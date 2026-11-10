"""Security infrastructure adapters: Argon2id hasher, Redis sessions & rate limit, HMAC CSRF."""

from __future__ import annotations

import asyncio
import hashlib
import hmac
import json
import secrets
from typing import Any
from uuid import UUID

from argon2 import PasswordHasher
from argon2.exceptions import InvalidHashError, VerificationError, VerifyMismatchError
from redis.exceptions import RedisError

from app.core.exceptions import AppError, ErrorCode
from app.core.logging import get_logger
from app.core.redis import RedisClientManager
from app.core.security import constant_time_equals

logger = get_logger("app.identity_access.security_adapters")


class Argon2PasswordHasher:
    """OWASP-aligned Argon2id password hasher executing safely off the async event loop."""

    def __init__(self) -> None:
        self._hasher = PasswordHasher(time_cost=2, memory_cost=19456, parallelism=1)
        # Precompute deterministic dummy hash once so unknown-user timing stays balanced.
        self._dummy_hash = self._hasher.hash("dummy-timing-guard-placeholder-secret")

    async def hash_password(self, raw_password: str) -> str:
        return await asyncio.to_thread(self._hasher.hash, raw_password)

    async def verify_password(self, raw_password: str, encoded_hash: str) -> bool:
        def _verify() -> bool:
            try:
                return bool(self._hasher.verify(encoded_hash, raw_password))
            except (VerifyMismatchError, VerificationError, InvalidHashError):
                return False

        return await asyncio.to_thread(_verify)

    async def verify_dummy(self, raw_password: str) -> None:
        await self.verify_password(raw_password, self._dummy_hash)


class RedisSessionStore:
    """Fail-closed Redis active session registry paired with PostgreSQL auth_sessions."""

    _PREFIX = "sess:"

    def __init__(self, redis_manager: RedisClientManager) -> None:
        self._redis = redis_manager

    def _key(self, token_hash: str) -> str:
        return f"{self._PREFIX}{token_hash}"

    async def ping_required(self, operation_name: str) -> None:
        await self._redis.require_security_operation(operation_name)

    async def store_session(
        self,
        *,
        token_hash: str,
        user_id: UUID,
        session_id: UUID,
        ttl_seconds: int,
    ) -> None:
        client = await self._redis.require_security_operation("session_store")
        payload = json.dumps({"user_id": str(user_id), "session_id": str(session_id)})
        try:
            await client.set(self._key(token_hash), payload, ex=ttl_seconds)
        except RedisError as exc:
            logger.error(
                "redis_session_write_failed",
                extra={
                    "structured": {"event": "security_fail_closed", "error": exc.__class__.__name__}
                },
            )
            raise AppError(ErrorCode.SYS_DEPENDENCY_UNAVAILABLE) from exc

    async def is_session_present(self, token_hash: str) -> bool:
        client = await self._redis.require_security_operation("session_verify")
        try:
            exists = await client.exists(self._key(token_hash))
            return bool(exists)
        except RedisError as exc:
            logger.error(
                "redis_session_read_failed",
                extra={
                    "structured": {"event": "security_fail_closed", "error": exc.__class__.__name__}
                },
            )
            raise AppError(ErrorCode.SYS_DEPENDENCY_UNAVAILABLE) from exc

    async def delete_session(self, token_hash: str) -> None:
        await self._redis.invalidate_keys(self._key(token_hash))

    async def delete_sessions(self, token_hashes: list[str]) -> None:
        keys = [self._key(h) for h in token_hashes if h]
        if keys:
            await self._redis.invalidate_keys(*keys)


class RedisLoginRateLimiter:
    """Fail-closed sliding/fixed-window Redis anti-brute-force rate limiter for /login."""

    def __init__(
        self,
        redis_manager: RedisClientManager,
        *,
        user_max_attempts: int,
        ip_max_attempts: int,
        window_seconds: int,
    ) -> None:
        self._redis = redis_manager
        self._user_max = user_max_attempts
        self._ip_max = ip_max_attempts
        self._window = window_seconds

    @staticmethod
    def _ip_key(client_ip: str) -> str:
        return f"rl:login:ip:{client_ip}"

    @staticmethod
    def _user_key(client_ip: str, username: str) -> str:
        return f"rl:login:user:{client_ip}:{username.lower()}"

    async def check_allowed(self, *, client_ip: str, username: str) -> None:
        client = await self._redis.require_security_operation("login_rate_limit")
        user_key = self._user_key(client_ip, username)
        ip_key = self._ip_key(client_ip)
        try:
            async with client.pipeline(transaction=False) as pipe:
                pipe.get(user_key)
                pipe.get(ip_key)
                pipe.ttl(user_key)
                pipe.ttl(ip_key)
                results: list[Any] = await pipe.execute()
            user_count = int(results[0] or 0)
            ip_count = int(results[1] or 0)
            user_ttl = max(int(results[2] or 0), 1)
            ip_ttl = max(int(results[3] or 0), 1)
        except RedisError as exc:
            raise AppError(ErrorCode.SYS_DEPENDENCY_UNAVAILABLE) from exc

        if user_count >= self._user_max or ip_count >= self._ip_max:
            retry_after = user_ttl if user_count >= self._user_max else ip_ttl
            logger.warning(
                "login_rate_limit_blocked",
                extra={
                    "structured": {
                        "event": "auth_rate_limited",
                        "client_ip": client_ip,
                        "username": username,
                        "retry_after_seconds": retry_after,
                    }
                },
            )
            raise AppError(
                ErrorCode.AUTH_TOO_MANY_REQUESTS,
                details={"retry_after_seconds": retry_after},
                headers={"Retry-After": str(retry_after)},
            )

    async def record_failure(self, *, client_ip: str, username: str) -> None:
        client = await self._redis.require_security_operation("login_rate_limit_record")
        user_key = self._user_key(client_ip, username)
        ip_key = self._ip_key(client_ip)
        try:
            async with client.pipeline(transaction=True) as pipe:
                pipe.incr(user_key)
                pipe.expire(user_key, self._window, nx=True)
                pipe.incr(ip_key)
                pipe.expire(ip_key, self._window, nx=True)
                await pipe.execute()
        except RedisError as exc:
            raise AppError(ErrorCode.SYS_DEPENDENCY_UNAVAILABLE) from exc

    async def clear_failures(self, *, client_ip: str, username: str) -> None:
        await self._redis.invalidate_keys(self._user_key(client_ip, username))


class HmacCsrfManager:
    """Stateless HMAC-SHA256 CSRF token issuer bound strictly to active server session IDs."""

    def __init__(self, secret: str) -> None:
        self._key = secret.encode("utf-8")

    def _sign(self, payload: str) -> str:
        return hmac.new(self._key, payload.encode("utf-8"), hashlib.sha256).hexdigest()

    def issue_for_session(self, session_id: UUID) -> str:
        nonce = secrets.token_hex(12)
        sig = self._sign(f"s1:{session_id}:{nonce}")
        return f"s1.{nonce}.{sig}"

    def issue_pre_auth(self) -> str:
        nonce = secrets.token_hex(12)
        sig = self._sign(f"p1:{nonce}")
        return f"p1.{nonce}.{sig}"

    def verify_for_session(self, token: str | None, session_id: UUID) -> bool:
        if not token:
            return False
        parts = token.strip().split(".")
        if len(parts) != 3 or parts[0] != "s1":
            return False
        _, nonce, provided_sig = parts
        if len(nonce) < 8:
            return False
        expected_sig = self._sign(f"s1:{session_id}:{nonce}")
        return constant_time_equals(expected_sig, provided_sig)
