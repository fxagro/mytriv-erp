/**
 * Generic Model Service for MyTriv ERP
 *
 * Provides a high-level abstraction for working with any Odoo model
 * through the REST API. Handles common operations like CRUD with
 * proper error handling and type safety.
 */

import { apiClient } from './apiClient'
import { config } from '@/lib/config'
import { retryWithBackoff, buildQueryString } from '@/lib/utils'
import type {
  ServiceResponse,
  ServiceListResponse,
  PaginatedResponse,
  ModelRecord,
  ListOptions
} from '@/lib/types'

export class GenericModelService {
  /**
   * List records from any Odoo model
   */
  async list<T extends ModelRecord>(
    model: string,
    options: ListOptions = {}
  ): Promise<ServiceListResponse<T>> {
    try {
      // Use retry logic for reliability
      const response = await retryWithBackoff(
        () => apiClient.listRecords<T>(model, options),
        config.api.retry.attempts,
        config.api.retry.delay
      )

      return response
    } catch (error) {
      return {
        error: error instanceof Error ? error.message : 'Failed to list records',
        success: false,
      }
    }
  }

  /**
   * Get a specific record by ID
   */
  async get<T extends ModelRecord>(
    model: string,
    id: number,
    fields?: string[]
  ): Promise<ServiceResponse<T>> {
    try {
      // Use retry logic for reliability
      const response = await retryWithBackoff(
        () => apiClient.getRecord<T>(model, id, fields),
        config.api.retry.attempts,
        config.api.retry.delay
      )

      return response
    } catch (error) {
      return {
        error: error instanceof Error ? error.message : 'Failed to get record',
        success: false,
      }
    }
  }

  /**
   * Create a new record
   */
  async create<T extends ModelRecord>(
    model: string,
    data: Partial<T>
  ): Promise<ServiceResponse<T>> {
    try {
      // Use retry logic for reliability
      const response = await retryWithBackoff(
        () => apiClient.createRecord<T>(model, data),
        config.api.retry.attempts,
        config.api.retry.delay
      )

      return response
    } catch (error) {
      return {
        error: error instanceof Error ? error.message : 'Failed to create record',
        success: false,
      }
    }
  }

  /**
   * Update an existing record
   */
  async update<T extends ModelRecord>(
    model: string,
    id: number,
    data: Partial<T>
  ): Promise<ServiceResponse<T>> {
    try {
      // Use retry logic for reliability
      const response = await retryWithBackoff(
        () => apiClient.updateRecord<T>(model, id, data),
        config.api.retry.attempts,
        config.api.retry.delay
      )

      return response
    } catch (error) {
      return {
        error: error instanceof Error ? error.message : 'Failed to update record',
        success: false,
      }
    }
  }

  /**
   * Delete a record
   */
  async delete(
    model: string,
    id: number
  ): Promise<ServiceResponse<{ deleted_id: number; message: string }>> {
    try {
      // Use retry logic for reliability
      const response = await retryWithBackoff(
        () => apiClient.deleteRecord(model, id),
        config.api.retry.attempts,
        config.api.retry.delay
      )

      return response
    } catch (error) {
      return {
        error: error instanceof Error ? error.message : 'Failed to delete record',
        success: false,
      }
    }
  }

  /**
   * Search records with advanced options
   */
  async search<T extends ModelRecord>(
    model: string,
    searchQuery: string,
    options: Omit<ListOptions, 'search'> = {}
  ): Promise<ServiceListResponse<T>> {
    return this.list<T>(model, {
      ...options,
      search: searchQuery,
    })
  }

  /**
   * Get records with pagination
   */
  async getPage<T extends ModelRecord>(
    model: string,
    page: number = 1,
    pageSize: number = config.pagination.defaultLimit,
    options: Omit<ListOptions, 'limit' | 'offset'> = {}
  ): Promise<ServiceListResponse<T>> {
    const offset = (page - 1) * pageSize

    return this.list<T>(model, {
      ...options,
      limit: pageSize,
      offset,
    })
  }

  /**
   * Count total records matching criteria
   */
  async count(model: string, options: Pick<ListOptions, 'search' | 'domain'> = {}): Promise<ServiceResponse<number>> {
    try {
      const response = await this.list(model, {
        ...options,
        limit: 1,
        fields: ['id'], // Only fetch ID field for counting
      })

      if (response.success && response.data) {
        return {
          data: response.data.total,
          success: true,
        }
      }

      return response as ServiceResponse<number>
    } catch (error) {
      return {
        error: error instanceof Error ? error.message : 'Failed to count records',
        success: false,
      }
    }
  }

  /**
   * Bulk create records
   */
  async bulkCreate<T extends ModelRecord>(
    model: string,
    records: Partial<T>[]
  ): Promise<ServiceResponse<T[]>> {
    try {
      const results = await Promise.allSettled(
        records.map(record => this.create<T>(model, record))
      )

      const successful: T[] = []
      const errors: string[] = []

      results.forEach((result, index) => {
        if (result.status === 'fulfilled' && result.value.success && result.value.data) {
          successful.push(result.value.data)
        } else {
          const error = result.status === 'fulfilled' ? result.value.error : 'Unknown error'
          errors.push(`Record ${index + 1}: ${error}`)
        }
      })

      return {
        data: successful,
        success: errors.length === 0,
        message: errors.length > 0 ? `Some records failed: ${errors.join(', ')}` : undefined,
      }
    } catch (error) {
      return {
        error: error instanceof Error ? error.message : 'Failed to bulk create records',
        success: false,
      }
    }
  }

  /**
   * Bulk update records
   */
  async bulkUpdate<T extends ModelRecord>(
    model: string,
    updates: Array<{ id: number; data: Partial<T> }>
  ): Promise<ServiceResponse<T[]>> {
    try {
      const results = await Promise.allSettled(
        updates.map(update => this.update<T>(model, update.id, update.data))
      )

      const successful: T[] = []
      const errors: string[] = []

      results.forEach((result, index) => {
        if (result.status === 'fulfilled' && result.value.success && result.value.data) {
          successful.push(result.value.data)
        } else {
          const error = result.status === 'fulfilled' ? result.value.error : 'Unknown error'
          errors.push(`Record ${updates[index].id}: ${error}`)
        }
      })

      return {
        data: successful,
        success: errors.length === 0,
        message: errors.length > 0 ? `Some records failed: ${errors.join(', ')}` : undefined,
      }
    } catch (error) {
      return {
        error: error instanceof Error ? error.message : 'Failed to bulk update records',
        success: false,
      }
    }
  }

  /**
   * Bulk delete records
   */
  async bulkDelete(
    model: string,
    ids: number[]
  ): Promise<ServiceResponse<{ deleted_ids: number[]; errors: string[] }>> {
    try {
      const results = await Promise.allSettled(
        ids.map(id => this.delete(model, id))
      )

      const deletedIds: number[] = []
      const errors: string[] = []

      results.forEach((result, index) => {
        if (result.status === 'fulfilled' && result.value.success) {
          deletedIds.push(ids[index])
        } else {
          const error = result.status === 'fulfilled' ? result.value.error : 'Unknown error'
          errors.push(`Record ${ids[index]}: ${error}`)
        }
      })

      return {
        data: {
          deleted_ids: deletedIds,
          errors,
        },
        success: errors.length === 0,
        message: errors.length > 0 ? `Some deletions failed: ${errors.join(', ')}` : undefined,
      }
    } catch (error) {
      return {
        error: error instanceof Error ? error.message : 'Failed to bulk delete records',
        success: false,
      }
    }
  }

  /**
   * Check if a model exists (useful for graceful degradation)
   */
  async modelExists(model: string): Promise<boolean> {
    try {
      const response = await this.count(model)
      return response.success
    } catch {
      return false
    }
  }

  /**
   * Get model fields information (if supported by backend)
   */
  async getModelFields(model: string): Promise<ServiceResponse<any[]>> {
    try {
      // This would require a backend endpoint to expose model fields
      // For now, return a placeholder response
      return {
        data: [],
        success: true,
        message: 'Model fields endpoint not implemented yet',
      }
    } catch (error) {
      return {
        error: error instanceof Error ? error.message : 'Failed to get model fields',
        success: false,
      }
    }
  }

  /**
   * Export records to CSV format (client-side)
   */
  async exportToCSV<T extends ModelRecord>(
    model: string,
    records: T[],
    fields?: string[]
  ): Promise<ServiceResponse<string>> {
    try {
      if (records.length === 0) {
        return {
          error: 'No records to export',
          success: false,
        }
      }

      // Determine fields to export
      const exportFields = fields || Object.keys(records[0])

      // Create CSV header
      const header = exportFields.join(',')

      // Create CSV rows
      const rows = records.map(record =>
        exportFields.map(field => {
          const value = (record as any)[field]
          // Handle values that might contain commas or quotes
          if (typeof value === 'string' && (value.includes(',') || value.includes('"'))) {
            return `"${value.replace(/"/g, '""')}"`
          }
          return value || ''
        }).join(',')
      )

      const csv = [header, ...rows].join('\n')

      return {
        data: csv,
        success: true,
      }
    } catch (error) {
      return {
        error: error instanceof Error ? error.message : 'Failed to export records',
        success: false,
      }
    }
  }

  /**
   * Get records with infinite scroll support
   */
  async getInfiniteScroll<T extends ModelRecord>(
    model: string,
    options: Omit<ListOptions, 'offset'> & {
      cursor?: number
      pageSize?: number
    } = {}
  ): Promise<ServiceResponse<{
    records: T[]
    nextCursor?: number
    hasMore: boolean
  }>> {
    try {
      const pageSize = options.pageSize || config.pagination.defaultLimit
      const offset = options.cursor ? (options.cursor - 1) * pageSize : 0

      const response = await this.list<T>(model, {
        ...options,
        limit: pageSize + 1, // Get one extra to check if there are more
        offset,
      })

      if (!response.success || !response.data) {
        return response as ServiceResponse<{
          records: T[]
          nextCursor?: number
          hasMore: boolean
        }>
      }

      const { items, total } = response.data
      const hasMore = items.length > pageSize
      const records = hasMore ? items.slice(0, -1) : items
      const nextCursor = hasMore ? Math.floor(offset / pageSize) + 2 : undefined

      return {
        data: {
          records,
          nextCursor,
          hasMore,
        },
        success: true,
      }
    } catch (error) {
      return {
        error: error instanceof Error ? error.message : 'Failed to get records for infinite scroll',
        success: false,
      }
    }
  }
}

// Create and export singleton instance
export const genericModelService = new GenericModelService()