"""FastAPI composition root, lifespan resource management, middleware, and base routes."""

from __future__ import annotations

import asyncio
import sys
from collections.abc import AsyncIterator
from contextlib import asynccontextmanager

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from app.core.config import Settings, get_settings
from app.core.database import build_async_engine, build_session_factory, dispose_database
from app.core.errors import register_exception_handlers
from app.core.health import router as health_router
from app.core.idempotency import SqlAlchemyIdempotencySlotAdapter
from app.core.logging import configure_logging, get_logger
from app.core.middleware import RequestContextAndAccessMiddleware
from app.core.observability import ObservabilityTracker
from app.core.redis import RedisClientManager
from app.modules.admin.application.use_cases import AdminGovernanceService
from app.modules.admin.infrastructure.observability_adapter import (
    CoreSystemObservabilityAdapter,
)
from app.modules.admin.infrastructure.repository import SqlAlchemyAdminRepository
from app.modules.admin.presentation.router import admin_governance_router
from app.modules.contracts.application.use_cases import ContractsService
from app.modules.contracts.infrastructure.repository import SqlAlchemyContractsRepository
from app.modules.contracts.presentation.router import contracts_router
from app.modules.files.application.use_cases import FilesService
from app.modules.files.infrastructure.repository import SqlAlchemyFilesRepository
from app.modules.files.infrastructure.storage import LocalEvidenceStorageAdapter
from app.modules.files.presentation.router import files_router
from app.modules.finance.application.use_cases import FinanceService
from app.modules.finance.infrastructure.repository import SqlAlchemyFinanceRepository
from app.modules.finance.presentation.router import invoices_router, payments_router
from app.modules.identity_access.application.use_cases import IdentityAccessService
from app.modules.identity_access.infrastructure.repository import SqlAlchemyIdentityRepository
from app.modules.identity_access.infrastructure.security_adapters import (
    Argon2PasswordHasher,
    HmacCsrfManager,
    RedisLoginRateLimiter,
    RedisSessionStore,
)
from app.modules.identity_access.presentation.router import admin_users_router, auth_router
from app.modules.logistics.application.use_cases import LogisticsService
from app.modules.logistics.infrastructure.repository import SqlAlchemyLogisticsRepository
from app.modules.logistics.presentation.router import logistics_router
from app.modules.master_data.application.use_cases import MasterDataService
from app.modules.master_data.infrastructure.cache_adapter import RedisPublicDirectoryInvalidator
from app.modules.master_data.infrastructure.repository import SqlAlchemyMasterDataRepository
from app.modules.master_data.presentation.router import master_data_router
from app.modules.mill_weighing.application.use_cases import MillWeighingService
from app.modules.mill_weighing.infrastructure.repository import SqlAlchemyMillWeighingRepository
from app.modules.mill_weighing.presentation.router import mill_weighing_router
from app.modules.pricing.application.use_cases import PricingService
from app.modules.pricing.infrastructure.cache_adapter import RedisPublicPricingInvalidator
from app.modules.pricing.infrastructure.repository import SqlAlchemyPricingRepository
from app.modules.pricing.presentation.router import pricing_router
from app.modules.public_portal.application.use_cases import PublicPortalService
from app.modules.public_portal.infrastructure.cache_adapter import RedisPublicPortalCache
from app.modules.public_portal.infrastructure.repository import SqlAlchemyPublicPortalRepository
from app.modules.public_portal.presentation.router import public_portal_router
from app.modules.reconciliation.application.use_cases import ReconciliationService
from app.modules.reconciliation.infrastructure.repository import (
    SqlAlchemyReconciliationRepository,
)
from app.modules.reconciliation.presentation.router import reconciliation_router
from app.modules.reporting.application.use_cases import ReportingService
from app.modules.reporting.infrastructure.cache_adapter import RedisReportingCache
from app.modules.reporting.infrastructure.repository import SqlAlchemyReportingRepository
from app.modules.reporting.presentation.router import reporting_router
from app.modules.tbs_receiving.application.use_cases import TbsReceivingService
from app.modules.tbs_receiving.infrastructure.repository import SqlAlchemyTbsReceivingRepository
from app.modules.tbs_receiving.presentation.router import tbs_receiving_router

# Psycopg 3 async requires SelectorEventLoop on Windows.
if sys.platform == "win32" and isinstance(
    asyncio.get_event_loop_policy(), asyncio.WindowsProactorEventLoopPolicy
):
    asyncio.set_event_loop_policy(asyncio.WindowsSelectorEventLoopPolicy())

logger = get_logger("app.main")


def create_app(
    *,
    settings: Settings | None = None,
    db_dsn_override: str | None = None,
    redis_url_override: str | None = None,
) -> FastAPI:
    """Construct configured FastAPI application instance via explicit composition root."""
    cfg = settings if settings is not None else get_settings()
    configure_logging(level=cfg.LOG_LEVEL, json_output=cfg.LOG_JSON)

    @asynccontextmanager
    async def lifespan(app_instance: FastAPI) -> AsyncIterator[None]:
        db_engine = build_async_engine(cfg, dsn_override=db_dsn_override)
        db_session_factory = build_session_factory(db_engine)
        redis_manager = RedisClientManager(cfg, url_override=redis_url_override)

        identity_repo = SqlAlchemyIdentityRepository(db_session_factory)
        identity_service = IdentityAccessService(
            repo=identity_repo,
            session_cache=RedisSessionStore(redis_manager),
            rate_limiter=RedisLoginRateLimiter(
                redis_manager,
                user_max_attempts=cfg.LOGIN_RATE_LIMIT_MAX_ATTEMPTS,
                ip_max_attempts=cfg.LOGIN_IP_RATE_LIMIT_MAX_ATTEMPTS,
                window_seconds=cfg.LOGIN_RATE_LIMIT_WINDOW_SECONDS,
            ),
            hasher=Argon2PasswordHasher(),
            csrf=HmacCsrfManager(cfg.SESSION_SECRET.get_secret_value()),
            session_ttl_seconds=cfg.SESSION_TTL_SECONDS,
        )

        app_instance.state.settings = cfg
        app_instance.state.db_engine = db_engine
        app_instance.state.db_session_factory = db_session_factory
        app_instance.state.redis_manager = redis_manager
        observability_tracker = ObservabilityTracker()
        app_instance.state.observability = observability_tracker
        app_instance.state.identity_service = identity_service
        app_instance.state.master_data_service = MasterDataService(
            repo=SqlAlchemyMasterDataRepository(db_session_factory),
            cache_invalidator=RedisPublicDirectoryInvalidator(redis_manager),
        )
        app_instance.state.pricing_service = PricingService(
            repo=SqlAlchemyPricingRepository(db_session_factory),
            cache_invalidator=RedisPublicPricingInvalidator(redis_manager),
        )
        app_instance.state.public_portal_service = PublicPortalService(
            repo=SqlAlchemyPublicPortalRepository(db_session_factory),
            cache=RedisPublicPortalCache(redis_manager),
        )
        app_instance.state.tbs_receiving_service = TbsReceivingService(
            repo=SqlAlchemyTbsReceivingRepository(db_session_factory),
            idempotency=SqlAlchemyIdempotencySlotAdapter(db_session_factory),
        )
        app_instance.state.contracts_service = ContractsService(
            repo=SqlAlchemyContractsRepository(db_session_factory),
            idempotency=SqlAlchemyIdempotencySlotAdapter(db_session_factory),
        )
        app_instance.state.logistics_service = LogisticsService(
            repo=SqlAlchemyLogisticsRepository(db_session_factory),
            idempotency=SqlAlchemyIdempotencySlotAdapter(db_session_factory),
        )
        app_instance.state.files_service = FilesService(
            repo=SqlAlchemyFilesRepository(db_session_factory),
            storage=LocalEvidenceStorageAdapter(cfg.FILE_STORAGE_DIR),
        )
        app_instance.state.mill_weighing_service = MillWeighingService(
            repo=SqlAlchemyMillWeighingRepository(db_session_factory),
            idempotency=SqlAlchemyIdempotencySlotAdapter(db_session_factory),
        )
        app_instance.state.reconciliation_service = ReconciliationService(
            repo=SqlAlchemyReconciliationRepository(db_session_factory),
            idempotency=SqlAlchemyIdempotencySlotAdapter(db_session_factory),
        )
        app_instance.state.finance_service = FinanceService(
            repo=SqlAlchemyFinanceRepository(db_session_factory),
            idempotency=SqlAlchemyIdempotencySlotAdapter(db_session_factory),
        )
        app_instance.state.reporting_service = ReportingService(
            repo=SqlAlchemyReportingRepository(db_session_factory),
            cache=RedisReportingCache(redis_manager),
        )
        app_instance.state.admin_governance_service = AdminGovernanceService(
            repo=SqlAlchemyAdminRepository(db_session_factory),
            observability=CoreSystemObservabilityAdapter(
                service_name=cfg.APP_NAME,
                db_engine=db_engine,
                redis_manager=redis_manager,
                tracker=observability_tracker,
            ),
        )
        logger.info("backend_startup_completed", extra={"structured": {"event": "app_startup"}})
        try:
            yield
        finally:
            await redis_manager.close()
            await dispose_database(db_engine)
            logger.info(
                "backend_shutdown_completed", extra={"structured": {"event": "app_shutdown"}}
            )

    application = FastAPI(
        title=cfg.APP_NAME,
        version=cfg.APP_VERSION,
        debug=cfg.APP_DEBUG,
        lifespan=lifespan,
    )

    application.add_middleware(
        CORSMiddleware,
        allow_origins=cfg.CORS_ALLOWED_ORIGINS,
        allow_credentials=True,
        allow_methods=["GET", "POST", "PUT", "PATCH", "DELETE", "OPTIONS"],
        allow_headers=["Content-Type", "X-CSRF-Token", "X-Request-ID", "Idempotency-Key"],
    )
    application.add_middleware(
        RequestContextAndAccessMiddleware,
        request_timeout_seconds=cfg.REQUEST_TIMEOUT_SECONDS,
    )
    register_exception_handlers(application)
    application.include_router(health_router)
    application.include_router(auth_router)
    application.include_router(admin_users_router)
    application.include_router(master_data_router)
    application.include_router(pricing_router)
    application.include_router(public_portal_router)
    application.include_router(tbs_receiving_router)
    application.include_router(contracts_router)
    application.include_router(logistics_router)
    application.include_router(files_router)
    application.include_router(mill_weighing_router)
    application.include_router(reconciliation_router)
    application.include_router(invoices_router)
    application.include_router(payments_router)
    application.include_router(reporting_router)
    application.include_router(admin_governance_router)

    return application


app = create_app()
