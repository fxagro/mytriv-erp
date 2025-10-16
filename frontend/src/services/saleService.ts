/**
 * Sales Service for MyTriv ERP
 *
 * Provides sales-specific operations and business logic for order management.
 */

import { GenericModelService } from './genericModelService'
import type { ServiceResponse, ServiceListResponse, SaleOrder, ListOptions } from '@/lib/types'

export class SaleService extends GenericModelService {
  private model = 'sale.order'

  async listOrders(options: ListOptions = {}): Promise<ServiceListResponse<SaleOrder>> {
    return this.list<SaleOrder>(this.model, options)
  }

  async getOrder(id: number): Promise<ServiceResponse<SaleOrder>> {
    return this.get<SaleOrder>(this.model, id)
  }

  async createOrder(data: any): Promise<ServiceResponse<SaleOrder>> {
    return this.create<SaleOrder>(this.model, data)
  }

  async updateOrder(id: number, data: any): Promise<ServiceResponse<SaleOrder>> {
    return this.update<SaleOrder>(this.model, id, data)
  }

  async deleteOrder(id: number): Promise<ServiceResponse<{ deleted_id: number; message: string }>> {
    return this.delete(this.model, id)
  }
}

export const saleService = new SaleService()