import {
  createRootRoute,
  createRoute,
  createRouter,
  redirect,
  type AnyRoute,
  type RouterHistory,
} from '@tanstack/react-router';
import type { ReactNode } from 'react';
import {
  CANONICAL_ROUTES,
  hasAnyRole,
  type AuthenticatedUser,
  type CanonicalRouteMeta,
} from '@/lib/auth/permissions';
import { fetchCurrentUser } from '@/lib/auth/session';
import { appQueryClient } from '@/lib/query/queryClient';
import { queryKeys } from '@/lib/query/queryKeys';
import {
  ForbiddenRoleView,
  LoadingFallback,
  NotFoundView,
  RootLayout,
} from './RouterShellViews';
import { resolveInternalPage, resolvePublicOrAuthPage } from './routePageRegistry';

const rootRoute = createRootRoute({
  component: RootLayout,
  notFoundComponent: NotFoundView,
});

async function resolveSessionUser(): Promise<AuthenticatedUser | null> {
  return appQueryClient.ensureQueryData({
    queryKey: queryKeys.auth.me(),
    queryFn: fetchCurrentUser,
    staleTime: 10_000,
  });
}

function makeProtectedWrapper(meta: CanonicalRouteMeta): () => ReactNode {
  const InternalComponent = resolveInternalPage(meta.path);
  return function ProtectedRouteView() {
    const cachedUser = appQueryClient.getQueryData<AuthenticatedUser | null>(queryKeys.auth.me());
    if (!cachedUser || !hasAnyRole(cachedUser, meta.allowedRoles)) {
      return <ForbiddenRoleView user={cachedUser ?? null} />;
    }
    return <InternalComponent user={cachedUser} />;
  };
}

function buildCanonicalRoute(meta: CanonicalRouteMeta): AnyRoute {
  if (meta.access === 'internal') {
    return createRoute({
      getParentRoute: () => rootRoute,
      path: meta.path,
      beforeLoad: async ({ location }) => {
        const user = await resolveSessionUser();
        if (!user) {
          throw redirect({
            to: '/login',
            search: { next: location.pathname },
          });
        }
      },
      component: makeProtectedWrapper(meta),
    });
  }

  const PublicOrAuthComponent = resolvePublicOrAuthPage(meta.path);
  return createRoute({
    getParentRoute: () => rootRoute,
    path: meta.path,
    component: () => <PublicOrAuthComponent />,
  });
}

const canonicalChildRoutes = CANONICAL_ROUTES.map(buildCanonicalRoute);
const routeTree = rootRoute.addChildren(canonicalChildRoutes);

export function createAppRouter(history?: RouterHistory) {
  return createRouter({
    routeTree,
    history,
    defaultPreload: 'intent',
    defaultPendingComponent: LoadingFallback,
    defaultNotFoundComponent: NotFoundView,
  });
}

export const appRouter = createAppRouter();

declare module '@tanstack/react-router' {
  interface Register {
    router: typeof appRouter;
  }
}
