/**
 * API Client for MyTriv ERP Backend Communication
 *
 * Handles HTTP requests to Odoo backend with proper authentication,
 * error handling, and mock mode support.
 */

import axios, { AxiosInstance, AxiosRequestConfig, AxiosResponse } from 'axios'
import { config } from '@/lib/config'
import { getApiUrl } from '@/lib/config'
import { safeGetStorage, safeSetStorage, safeRemoveStorage, mockDelay, mockError } from '@/lib/utils'
import { isMockMode } from '@/lib/config'
import type {
  ApiResponse,
  ServiceResponse,
  RequestConfig,
  LoginCredentials,
  AuthResponse,
  User,
  PaginatedResponse,
  ModelRecord,
  ListOptions
} from '@/lib/types'

class ApiClient {
  private client: AxiosInstance
  private sessionId: string | null = null

  constructor() {
    this.client = axios.create({
      baseURL: config.api.baseUrl,
      timeout: config.api.timeout,
      headers: {
        'Content-Type': 'application/json',
      },
    })

    // Initialize session from storage
    this.loadSession()

    // Setup request interceptors
    this.setupRequestInterceptors()

    // Setup response interceptors
    this.setupResponseInterceptors()
  }

  /**
   * Setup request interceptors for authentication and common headers
   */
  private setupRequestInterceptors() {
    this.client.interceptors.request.use(
      (config) => {
        // Add authentication headers
        if (config.auth !== false) {
          if (config.auth?.type === 'token') {
            const token = safeGetStorage(config.auth.tokenStorageKey)
            if (token) {
              config.headers.Authorization = `Bearer ${token}`
            }
          } else {
            // Cookie-based authentication
            if (this.sessionId) {
              config.headers.Cookie = `session_id=${this.sessionId}`
            }
          }
        }

        // Add common headers
        config.headers['X-Requested-With'] = 'XMLHttpRequest'

        return config
      },
      (error) => {
        return Promise.reject(this.transformError(error))
      }
    )
  }

  /**
   * Setup response interceptors for error handling and session management
   */
  private setupResponseInterceptors() {
    this.client.interceptors.response.use(
      (response: AxiosResponse) => {
        // Handle successful responses
        if (response.headers['set-cookie']) {
          this.extractSessionFromCookie(response.headers['set-cookie'])
        }

        return response
      },
      (error) => {
        // Handle authentication errors
        if (error.response?.status === 401) {
          this.clearSession()
        }

        return Promise.reject(this.transformError(error))
      }
    )
  }

  /**
   * Transform axios errors to application errors
   */
  private transformError(error: any): Error {
    if (error.response) {
      // Server responded with error status
      const message = error.response.data?.error || error.response.data?.message || error.message
      const appError = new Error(message)
      appError.name = 'ApiError'
      ;(appError as any).status = error.response.status
      ;(appError as any).data = error.response.data
      return appError
    } else if (error.request) {
      // Network error
      const networkError = new Error('Network error - please check your connection')
      networkError.name = 'NetworkError'
      return networkError
    } else {
      // Other error
      return error
    }
  }

  /**
   * Extract session ID from Set-Cookie header
   */
  private extractSessionFromCookie(cookies: string[]): void {
    for (const cookie of cookies) {
      if (cookie.includes('session_id=')) {
        const match = cookie.match(/session_id=([^;]+)/)
        if (match) {
          this.sessionId = match[1]
          safeSetStorage(config.auth.sessionCookieName, this.sessionId)
          break
        }
      }
    }
  }

  /**
   * Load session from storage
   */
  private loadSession(): void {
    this.sessionId = safeGetStorage(config.auth.sessionCookieName)
  }

  /**
   * Clear session data
   */
  private clearSession(): void {
    this.sessionId = null
    safeRemoveStorage(config.auth.sessionCookieName)
  }

  /**
   * Make HTTP GET request
   */
  async get<T = any>(url: string, config: RequestConfig = {}): Promise<ServiceResponse<T>> {
    try {
      if (isMockMode()) {
        await mockDelay()
      }

      const response: AxiosResponse<ApiResponse<T>> = await this.client.get(url, {
        ...config,
        params: {
          ...config.params,
        },
      })

      const data = mockError(response.data)

      return {
        data: data.data,
        success: true,
        message: data.message,
      }
    } catch (error) {
      return {
        error: error instanceof Error ? error.message : 'Unknown error',
        success: false,
      }
    }
  }

  /**
   * Make HTTP POST request
   */
  async post<T = any>(
    url: string,
    data?: any,
    requestConfig: RequestConfig = {}
  ): Promise<ServiceResponse<T>> {
    try {
      if (isMockMode()) {
        await mockDelay()
      }

      const response: AxiosResponse<ApiResponse<T>> = await this.client.post(url, data, requestConfig)

      const responseData = mockError(response.data)

      return {
        data: responseData.data,
        success: true,
        message: responseData.message,
      }
    } catch (error) {
      return {
        error: error instanceof Error ? error.message : 'Unknown error',
        success: false,
      }
    }
  }

  /**
   * Make HTTP PUT request
   */
  async put<T = any>(
    url: string,
    data?: any,
    requestConfig: RequestConfig = {}
  ): Promise<ServiceResponse<T>> {
    try {
      if (isMockMode()) {
        await mockDelay()
      }

      const response: AxiosResponse<ApiResponse<T>> = await this.client.put(url, data, requestConfig)

      const responseData = mockError(response.data)

      return {
        data: responseData.data,
        success: true,
        message: responseData.message,
      }
    } catch (error) {
      return {
        error: error instanceof Error ? error.message : 'Unknown error',
        success: false,
      }
    }
  }

  /**
   * Make HTTP DELETE request
   */
  async delete<T = any>(url: string, config: RequestConfig = {}): Promise<ServiceResponse<T>> {
    try {
      if (isMockMode()) {
        await mockDelay()
      }

      const response: AxiosResponse<ApiResponse<T>> = await this.client.delete(url, config)

      const data = mockError(response.data)

      return {
        data: data.data,
        success: true,
        message: data.message,
      }
    } catch (error) {
      return {
        error: error instanceof Error ? error.message : 'Unknown error',
        success: false,
      }
    }
  }

  // Authentication methods

  /**
   * Login user
   */
  async login(credentials: LoginCredentials): Promise<ServiceResponse<AuthResponse>> {
    return this.post<AuthResponse>('/api/v1/auth/login', credentials)
  }

  /**
   * Logout user
   */
  async logout(): Promise<ServiceResponse<void>> {
    const response = await this.post<void>('/api/v1/auth/logout')
    if (response.success) {
      this.clearSession()
    }
    return response
  }

  /**
   * Get current user info
   */
  async getCurrentUser(): Promise<ServiceResponse<User>> {
    return this.get<User>('/api/v1/auth/me')
  }

  /**
   * Check if user is authenticated
   */
  async checkAuth(): Promise<ServiceResponse<{ authenticated: boolean; user?: User }>> {
    return this.get<{ authenticated: boolean; user?: User }>('/api/v1/auth/session')
  }

  // Generic model methods

  /**
   * List records from any model
   */
  async listRecords<T extends ModelRecord>(
    model: string,
    options: ListOptions = {}
  ): Promise<ServiceResponse<PaginatedResponse<T>>> {
    const params = {
      limit: options.limit || config.pagination.defaultLimit,
      offset: options.offset || 0,
      search: options.search,
      domain: options.domain ? JSON.stringify(options.domain) : undefined,
      fields: options.fields?.join(','),
    }

    return this.get<PaginatedResponse<T>>(`/api/v1/models/${model}`, { params })
  }

  /**
   * Get a specific record by ID
   */
  async getRecord<T extends ModelRecord>(
    model: string,
    id: number,
    fields?: string[]
  ): Promise<ServiceResponse<T>> {
    const params = fields ? { fields: fields.join(',') } : {}
    return this.get<T>(`/api/v1/models/${model}/${id}`, { params })
  }

  /**
   * Create a new record
   */
  async createRecord<T extends ModelRecord>(
    model: string,
    data: Partial<T>
  ): Promise<ServiceResponse<T>> {
    return this.post<T>(`/api/v1/models/${model}`, data)
  }

  /**
   * Update an existing record
   */
  async updateRecord<T extends ModelRecord>(
    model: string,
    id: number,
    data: Partial<T>
  ): Promise<ServiceResponse<T>> {
    return this.put<T>(`/api/v1/models/${model}/${id}`, data)
  }

  /**
   * Delete a record
   */
  async deleteRecord(
    model: string,
    id: number
  ): Promise<ServiceResponse<{ deleted_id: number; message: string }>> {
    return this.delete<{ deleted_id: number; message: string }>(`/api/v1/models/${model}/${id}`)
  }

  // Module-specific methods

  /**
   * List HR employees
   */
  async listEmployees(options: ListOptions = {}): Promise<ServiceResponse<PaginatedResponse<any>>> {
    const params = {
      limit: options.limit || config.pagination.defaultLimit,
      offset: options.offset || 0,
      search: options.search,
      department_id: options.domain?.find((d: any) => d[0] === 'department_id')?.[2],
      active: options.domain?.find((d: any) => d[0] === 'active')?.[2]?.toString(),
    }

    return this.get<PaginatedResponse<any>>('/api/v1/hr/employees', { params })
  }

  /**
   * Get HR employee by ID
   */
  async getEmployee(id: number): Promise<ServiceResponse<any>> {
    return this.get<any>(`/api/v1/hr/employees/${id}`)
  }

  /**
   * Create HR employee
   */
  async createEmployee(data: any): Promise<ServiceResponse<any>> {
    return this.post<any>('/api/v1/hr/employees', data)
  }

  /**
   * Update HR employee
   */
  async updateEmployee(id: number, data: any): Promise<ServiceResponse<any>> {
    return this.put<any>(`/api/v1/hr/employees/${id}`, data)
  }

  /**
   * Delete HR employee
   */
  async deleteEmployee(id: number): Promise<ServiceResponse<{ deleted_id: number; message: string }>> {
    return this.delete<{ deleted_id: number; message: string }>(`/api/v1/hr/employees/${id}`)
  }

  /**
   * List CRM leads
   */
  async listLeads(options: ListOptions = {}): Promise<ServiceResponse<PaginatedResponse<any>>> {
    const params = {
      limit: options.limit || config.pagination.defaultLimit,
      offset: options.offset || 0,
      search: options.search,
      stage_id: options.domain?.find((d: any) => d[0] === 'stage_id')?.[2],
      user_id: options.domain?.find((d: any) => d[0] === 'user_id')?.[2],
      priority: options.domain?.find((d: any) => d[0] === 'priority')?.[2],
      type: options.domain?.find((d: any) => d[0] === 'type')?.[2],
    }

    return this.get<PaginatedResponse<any>>('/api/v1/crm/leads', { params })
  }

  /**
   * Get CRM lead by ID
   */
  async getLead(id: number): Promise<ServiceResponse<any>> {
    return this.get<any>(`/api/v1/crm/leads/${id}`)
  }

  /**
   * Create CRM lead
   */
  async createLead(data: any): Promise<ServiceResponse<any>> {
    return this.post<any>('/api/v1/crm/leads', data)
  }

  /**
   * Update CRM lead
   */
  async updateLead(id: number, data: any): Promise<ServiceResponse<any>> {
    return this.put<any>(`/api/v1/crm/leads/${id}`, data)
  }

  /**
   * Delete CRM lead
   */
  async deleteLead(id: number): Promise<ServiceResponse<{ deleted_id: number; message: string }>> {
    return this.delete<{ deleted_id: number; message: string }>(`/api/v1/crm/leads/${id}`)
  }

  // Utility methods

  /**
   * Check if client is authenticated
   */
  isAuthenticated(): boolean {
    return this.sessionId !== null
  }

  /**
   * Get current session ID
   */
  getSessionId(): string | null {
    return this.sessionId
  }

  /**
   * Set session ID manually
   */
  setSessionId(sessionId: string): void {
    this.sessionId = sessionId
    safeSetStorage(config.auth.sessionCookieName, sessionId)
  }

  /**
   * Clear authentication
   */
  clearAuth(): void {
    this.clearSession()
  }
}

// Create and export singleton instance
export const apiClient = new ApiClient()

// Export class for testing or custom instances
export { ApiClient }