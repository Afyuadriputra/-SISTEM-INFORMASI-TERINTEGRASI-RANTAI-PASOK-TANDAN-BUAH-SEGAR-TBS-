import { adminReportsHandlers } from './handlers/adminReportsHandlers';
import { authHandlers } from './handlers/authHandlers';
import { financeHandlers } from './handlers/financeHandlers';
import { logisticsHandlers } from './handlers/logisticsHandlers';
import { masterDataHandlers } from './handlers/masterDataHandlers';
import { pricingHandlers } from './handlers/pricingHandlers';
import { publicHandlers } from './handlers/publicHandlers';
import { receivingHandlers } from './handlers/receivingHandlers';
import { reconciliationHandlers } from './handlers/reconciliationHandlers';

export const handlers = [
  ...publicHandlers,
  ...authHandlers,
  ...masterDataHandlers,
  ...pricingHandlers,
  ...receivingHandlers,
  ...logisticsHandlers,
  ...reconciliationHandlers,
  ...financeHandlers,
  ...adminReportsHandlers,
];
