export const queryKeys = {
  health: {
    all: ['health'] as const,
    live: () => [...queryKeys.health.all, 'live'] as const,
    ready: () => [...queryKeys.health.all, 'ready'] as const,
  },
  public: {
    all: ['public'] as const,
    prices: (filters?: Record<string, unknown>) =>
      [...queryKeys.public.all, 'prices', filters ?? {}] as const,
    priceDetail: (id: string) => [...queryKeys.public.all, 'price-detail', id] as const,
    disbunPrices: (filters?: Record<string, unknown>) =>
      [...queryKeys.public.all, 'disbun-prices', filters ?? {}] as const,
    mills: (filters?: Record<string, unknown>) =>
      [...queryKeys.public.all, 'mills', filters ?? {}] as const,
    millDetail: (id: string) => [...queryKeys.public.all, 'mill-detail', id] as const,
    profile: () => [...queryKeys.public.all, 'profile'] as const,
    notices: () => [...queryKeys.public.all, 'notices'] as const,
  },
  auth: {
    all: ['auth'] as const,
    me: () => [...queryKeys.auth.all, 'me'] as const,
  },
  masterData: {
    all: ['master-data'] as const,
    cooperatives: (filters?: Record<string, unknown>) =>
      [...queryKeys.masterData.all, 'cooperatives', filters ?? {}] as const,
    farmers: (filters?: Record<string, unknown>) =>
      [...queryKeys.masterData.all, 'farmers', filters ?? {}] as const,
    farmerDetail: (id: string) => [...queryKeys.masterData.all, 'farmer', id] as const,
    farms: (filters?: Record<string, unknown>) =>
      [...queryKeys.masterData.all, 'farms', filters ?? {}] as const,
    millCompanies: () => [...queryKeys.masterData.all, 'mill-companies'] as const,
    mills: (filters?: Record<string, unknown>) =>
      [...queryKeys.masterData.all, 'mills', filters ?? {}] as const,
    millDetail: (id: string) => [...queryKeys.masterData.all, 'mill', id] as const,
    vehicles: (filters?: Record<string, unknown>) =>
      [...queryKeys.masterData.all, 'vehicles', filters ?? {}] as const,
    drivers: (filters?: Record<string, unknown>) =>
      [...queryKeys.masterData.all, 'drivers', filters ?? {}] as const,
  },
  pricing: {
    all: ['pricing'] as const,
    referenceMeta: () => [...queryKeys.pricing.all, 'reference-meta'] as const,
    list: (filters?: Record<string, unknown>) =>
      [...queryKeys.pricing.all, 'list', filters ?? {}] as const,
    detail: (id: string) => [...queryKeys.pricing.all, 'detail', id] as const,
  },
  receipts: {
    all: ['receipts'] as const,
    list: (filters?: Record<string, unknown>) =>
      [...queryKeys.receipts.all, 'list', filters ?? {}] as const,
    detail: (id: string) => [...queryKeys.receipts.all, 'detail', id] as const,
  },
  contracts: {
    all: ['contracts'] as const,
    list: (filters?: Record<string, unknown>) =>
      [...queryKeys.contracts.all, 'list', filters ?? {}] as const,
    detail: (id: string) => [...queryKeys.contracts.all, 'detail', id] as const,
    quota: (id: string) => [...queryKeys.contracts.all, 'quota', id] as const,
  },
  deliveryOrders: {
    all: ['delivery-orders'] as const,
    list: (filters?: Record<string, unknown>) =>
      [...queryKeys.deliveryOrders.all, 'list', filters ?? {}] as const,
    detail: (id: string) => [...queryKeys.deliveryOrders.all, 'detail', id] as const,
  },
  millTickets: {
    all: ['mill-tickets'] as const,
    list: (filters?: Record<string, unknown>) =>
      [...queryKeys.millTickets.all, 'list', filters ?? {}] as const,
    detail: (id: string) => [...queryKeys.millTickets.all, 'detail', id] as const,
  },
  reconciliations: {
    all: ['reconciliations'] as const,
    list: (filters?: Record<string, unknown>) =>
      [...queryKeys.reconciliations.all, 'list', filters ?? {}] as const,
    detail: (id: string) => [...queryKeys.reconciliations.all, 'detail', id] as const,
  },
  finance: {
    all: ['finance'] as const,
    invoices: (filters?: Record<string, unknown>) =>
      [...queryKeys.finance.all, 'invoices', filters ?? {}] as const,
    invoiceDetail: (id: string) => [...queryKeys.finance.all, 'invoice', id] as const,
    payments: (filters?: Record<string, unknown>) =>
      [...queryKeys.finance.all, 'payments', filters ?? {}] as const,
  },
  reports: {
    all: ['reports'] as const,
    overview: (filters?: Record<string, unknown>) =>
      [...queryKeys.reports.all, 'overview', filters ?? {}] as const,
    supply: (filters?: Record<string, unknown>) =>
      [...queryKeys.reports.all, 'supply', filters ?? {}] as const,
    reconciliation: (filters?: Record<string, unknown>) =>
      [...queryKeys.reports.all, 'reconciliation', filters ?? {}] as const,
    finance: (filters?: Record<string, unknown>) =>
      [...queryKeys.reports.all, 'finance', filters ?? {}] as const,
  },
  admin: {
    all: ['admin'] as const,
    users: (filters?: Record<string, unknown>) =>
      [...queryKeys.admin.all, 'users', filters ?? {}] as const,
    ruleVersions: (filters?: Record<string, unknown>) =>
      [...queryKeys.admin.all, 'rule-versions', filters ?? {}] as const,
    auditEvents: (filters?: Record<string, unknown>) =>
      [...queryKeys.admin.all, 'audit-events', filters ?? {}] as const,
    systemHealth: () => [...queryKeys.admin.all, 'system-health'] as const,
  },
} as const;
