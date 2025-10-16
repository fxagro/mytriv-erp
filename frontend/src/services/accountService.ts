/**
 * Accounting Service for MyTriv ERP
 */

import { GenericModelService } from './genericModelService'
import type { ServiceResponse, ServiceListResponse, AccountMove, ListOptions } from '@/lib/types'

export class AccountService extends GenericModelService {
  async listInvoices(options: ListOptions = {}): Promise<ServiceListResponse<AccountMove>> {
    return this.list<AccountMove>('account.move', options)
  }
}

export const accountService = new AccountService()