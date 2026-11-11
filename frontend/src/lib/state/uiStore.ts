import { create } from 'zustand';

export type ToastTone = 'success' | 'info' | 'warning' | 'danger';

export interface ToastMessage {
  readonly id: string;
  readonly title: string;
  readonly description?: string;
  readonly requestId?: string | null;
  readonly tone: ToastTone;
}

interface UiState {
  readonly mobileDrawerOpen: boolean;
  readonly sessionExpiredBanner: boolean;
  readonly toasts: readonly ToastMessage[];
  readonly pendingIdempotencyKeys: Readonly<Record<string, string>>;
  setMobileDrawerOpen: (open: boolean) => void;
  toggleMobileDrawer: () => void;
  setSessionExpiredBanner: (active: boolean) => void;
  pushToast: (toast: Omit<ToastMessage, 'id'>) => string;
  dismissToast: (id: string) => void;
  getOrCreateActionIdempotencyKey: (actionScope: string) => string;
  clearActionIdempotencyKey: (actionScope: string) => void;
  resetEphemeralState: () => void;
}

export function generateIdempotencyKey(): string {
  if (typeof crypto !== 'undefined' && typeof crypto.randomUUID === 'function') {
    return `idemp_${crypto.randomUUID().replace(/-/g, '')}`;
  }
  return `idemp_${Date.now().toString(36)}_${Math.random().toString(36).slice(2, 14)}`;
}

export const useUiStore = create<UiState>((set, get) => ({
  mobileDrawerOpen: false,
  sessionExpiredBanner: false,
  toasts: [],
  pendingIdempotencyKeys: {},

  setMobileDrawerOpen: (open) => set({ mobileDrawerOpen: open }),
  toggleMobileDrawer: () => set((s) => ({ mobileDrawerOpen: !s.mobileDrawerOpen })),
  setSessionExpiredBanner: (active) => set({ sessionExpiredBanner: active }),

  pushToast: (toast) => {
    const id = `toast_${Date.now()}_${Math.random().toString(36).slice(2, 7)}`;
    set((s) => ({
      toasts: [...s.toasts.slice(-3), { ...toast, id }],
    }));
    return id;
  },

  dismissToast: (id) =>
    set((s) => ({
      toasts: s.toasts.filter((item) => item.id !== id),
    })),

  getOrCreateActionIdempotencyKey: (actionScope) => {
    const existing = get().pendingIdempotencyKeys[actionScope];
    if (existing) {
      return existing;
    }
    const created = generateIdempotencyKey();
    set((s) => ({
      pendingIdempotencyKeys: {
        ...s.pendingIdempotencyKeys,
        [actionScope]: created,
      },
    }));
    return created;
  },

  clearActionIdempotencyKey: (actionScope) =>
    set((s) => {
      if (!(actionScope in s.pendingIdempotencyKeys)) {
        return s;
      }
      const next = { ...s.pendingIdempotencyKeys };
      delete next[actionScope];
      return { pendingIdempotencyKeys: next };
    }),

  resetEphemeralState: () =>
    set({
      mobileDrawerOpen: false,
      toasts: [],
      pendingIdempotencyKeys: {},
    }),
}));
