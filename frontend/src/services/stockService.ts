/**
 * Inventory/Stock Service for MyTriv ERP
 */

import { GenericModelService } from './genericModelService'
import type { ServiceResponse, ServiceListResponse, Product, ListOptions } from '@/lib/types'

export class StockService extends GenericModelService {
  async listProducts(options: ListOptions = {}): Promise<ServiceListResponse<Product>> {
    return this.list<Product>('product.product', options)
  }
}

export const stockService = new StockService()