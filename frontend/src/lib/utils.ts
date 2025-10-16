/**
 * Utility functions for MyTriv ERP Frontend
 */

import { type ClassValue, clsx } from 'clsx'
import { twMerge } from 'tailwind-merge'
import { config } from './config'
import type { ModelRecord, PaginatedResponse, ListOptions } from './types'

/**
 * Merge Tailwind CSS classes with proper precedence
 */
export function cn(...inputs: ClassValue[]) {
  return twMerge(clsx(inputs))
}

/**
 * Format currency values
 */
export function formatCurrency(
  amount: number,
  currency: string = 'USD',
  locale: string = 'en-US'
): string {
  return new Intl.NumberFormat(locale, {
    style: 'currency',
    currency: currency,
  }).format(amount)
}

/**
 * Format date values
 */
export function formatDate(
  date: string | Date,
  options?: Intl.DateTimeFormatOptions
): string {
  const defaultOptions: Intl.DateTimeFormatOptions = {
    year: 'numeric',
    month: 'short',
    day: 'numeric',
  }

  return new Intl.DateTimeFormat('en-US', { ...defaultOptions, ...options }).format(
    new Date(date)
  )
}

/**
 * Format date and time values
 */
export function formatDateTime(
  date: string | Date,
  options?: Intl.DateTimeFormatOptions
): string {
  const defaultOptions: Intl.DateTimeFormatOptions = {
    year: 'numeric',
    month: 'short',
    day: 'numeric',
    hour: '2-digit',
    minute: '2-digit',
  }

  return new Intl.DateTimeFormat('en-US', { ...defaultOptions, ...options }).format(
    new Date(date)
  )
}

/**
 * Format relative time (e.g., "2 hours ago")
 */
export function formatRelativeTime(date: string | Date): string {
  const now = new Date()
  const targetDate = new Date(date)
  const diffInSeconds = Math.floor((now.getTime() - targetDate.getTime()) / 1000)

  const intervals = [
    { label: 'year', seconds: 31536000 },
    { label: 'month', seconds: 2592000 },
    { label: 'day', seconds: 86400 },
    { label: 'hour', seconds: 3600 },
    { label: 'minute', seconds: 60 },
    { label: 'second', seconds: 1 },
  ]

  for (const interval of intervals) {
    const count = Math.floor(diffInSeconds / interval.seconds)
    if (count >= 1) {
      return `${count} ${interval.label}${count !== 1 ? 's' : ''} ago`
    }
  }

  return 'just now'
}

/**
 * Truncate text to specified length
 */
export function truncateText(text: string, maxLength: number): string {
  if (text.length <= maxLength) return text
  return text.slice(0, maxLength).trim() + '...'
}

/**
 * Generate initials from name
 */
export function getInitials(name: string): string {
  return name
    .split(' ')
    .map(word => word.charAt(0).toUpperCase())
    .slice(0, 2)
    .join('')
}

/**
 * Debounce function for search inputs
 */
export function debounce<T extends (...args: any[]) => any>(
  func: T,
  wait: number
): (...args: Parameters<T>) => void {
  let timeout: NodeJS.Timeout

  return (...args: Parameters<T>) => {
    clearTimeout(timeout)
    timeout = setTimeout(() => func(...args), wait)
  }
}

/**
 * Sleep utility for async operations
 */
export function sleep(ms: number): Promise<void> {
  return new Promise(resolve => setTimeout(resolve, ms))
}

/**
 * Generate random ID for mock data
 */
export function generateId(): number {
  return Math.floor(Math.random() * 1000000)
}

/**
 * Validate email format
 */
export function isValidEmail(email: string): boolean {
  const emailRegex = /^[^\s@]+@[^\s@]+\.[^\s@]+$/
  return emailRegex.test(email)
}

/**
 * Validate phone number format
 */
export function isValidPhone(phone: string): boolean {
  const phoneRegex = /^[\+]?[1-9][\d]{0,15}$/
  return phoneRegex.test(phone.replace(/[\s\-\(\)]/g, ''))
}

/**
 * Build query string from object
 */
export function buildQueryString(params: Record<string, any>): string {
  const searchParams = new URLSearchParams()

  Object.entries(params).forEach(([key, value]) => {
    if (value !== null && value !== undefined && value !== '') {
      searchParams.append(key, String(value))
    }
  })

  return searchParams.toString()
}

/**
 * Parse query string to object
 */
export function parseQueryString(queryString: string): Record<string, any> {
  const searchParams = new URLSearchParams(queryString)
  const params: Record<string, any> = {}

  searchParams.forEach((value, key) => {
    // Try to parse as number
    if (/^\d+$/.test(value)) {
      params[key] = parseInt(value, 10)
    } else if (/^\d+\.\d+$/.test(value)) {
      params[key] = parseFloat(value)
    } else if (value === 'true') {
      params[key] = true
    } else if (value === 'false') {
      params[key] = false
    } else {
      params[key] = value
    }
  })

  return params
}

/**
 * Deep clone an object
 */
export function deepClone<T>(obj: T): T {
  if (obj === null || typeof obj !== 'object') return obj
  if (obj instanceof Date) return new Date(obj.getTime()) as any
  if (Array.isArray(obj)) return obj.map(item => deepClone(item)) as any

  const cloned = {} as T
  Object.keys(obj).forEach(key => {
    cloned[key] = deepClone(obj[key])
  })

  return cloned
}

/**
 * Check if value is empty (null, undefined, empty string, empty array, empty object)
 */
export function isEmpty(value: any): boolean {
  if (value === null || value === undefined) return true
  if (typeof value === 'string' && value.trim() === '') return true
  if (Array.isArray(value) && value.length === 0) return true
  if (typeof value === 'object' && Object.keys(value).length === 0) return true
  return false
}

/**
 * Get nested object property by path
 */
export function get(obj: any, path: string, defaultValue?: any): any {
  const keys = path.split('.')
  let result = obj

  for (const key of keys) {
    if (result === null || result === undefined) return defaultValue
    result = result[key]
  }

  return result !== undefined ? result : defaultValue
}

/**
 * Set nested object property by path
 */
export function set(obj: any, path: string, value: any): any {
  const keys = path.split('.')
  const lastKey = keys.pop()!
  let current = obj

  for (const key of keys) {
    if (!(key in current) || typeof current[key] !== 'object' || current[key] === null) {
      current[key] = {}
    }
    current = current[key]
  }

  current[lastKey] = value
  return obj
}

/**
 * Format file size in bytes to human readable format
 */
export function formatFileSize(bytes: number): string {
  if (bytes === 0) return '0 Bytes'

  const k = 1024
  const sizes = ['Bytes', 'KB', 'MB', 'GB', 'TB']
  const i = Math.floor(Math.log(bytes) / Math.log(k))

  return parseFloat((bytes / Math.pow(k, i)).toFixed(2)) + ' ' + sizes[i]
}

/**
 * Generate pagination info
 */
export function getPaginationInfo<T>(
  response: PaginatedResponse<T>,
  currentPage: number = 1
): {
  currentPage: number
  totalPages: number
  hasNextPage: boolean
  hasPrevPage: boolean
  startItem: number
  endItem: number
} {
  const { total, limit, offset } = response
  const totalPages = Math.ceil(total / limit)
  const hasNextPage = offset + limit < total
  const hasPrevPage = offset > 0
  const startItem = offset + 1
  const endItem = Math.min(offset + limit, total)

  return {
    currentPage,
    totalPages,
    hasNextPage,
    hasPrevPage,
    startItem,
    endItem,
  }
}

/**
 * Calculate pagination offset from page number
 */
export function getOffset(page: number, limit: number): number {
  return (page - 1) * limit
}

/**
 * Get page number from offset
 */
export function getPage(offset: number, limit: number): number {
  return Math.floor(offset / limit) + 1
}

/**
 * Sanitize HTML content (basic)
 */
export function sanitizeHtml(text: string): string {
  return text
    .replace(/&/g, '&')
    .replace(/</g, '<')
    .replace(/>/g, '>')
    .replace(/"/g, '"')
    .replace(/'/g, '&#x27;')
}

/**
 * Generate mock delay for development
 */
export async function mockDelay(): Promise<void> {
  if (config.mock.enabled) {
    await sleep(config.mock.delay)
  }
}

/**
 * Simulate random errors for testing
 */
export function mockError<T>(data: T): T {
  if (config.mock.enabled && Math.random() < config.mock.errorRate) {
    throw new Error('Mock error for testing')
  }
  return data
}

/**
 * Create mock pagination response
 */
export function createMockPagination<T extends ModelRecord>(
  items: T[],
  options: Partial<ListOptions> = {}
): PaginatedResponse<T> {
  const limit = options.limit || config.pagination.defaultLimit
  const offset = options.offset || 0

  return {
    items: items.slice(offset, offset + limit),
    total: items.length,
    limit,
    offset,
    model: options.search ? 'mock.model' : undefined,
  }
}

/**
 * Retry async operation with exponential backoff
 */
export async function retryWithBackoff<T>(
  operation: () => Promise<T>,
  maxRetries: number = 3,
  baseDelay: number = 1000
): Promise<T> {
  let lastError: Error

  for (let attempt = 0; attempt <= maxRetries; attempt++) {
    try {
      return await operation()
    } catch (error) {
      lastError = error as Error

      if (attempt === maxRetries) {
        throw lastError
      }

      const delay = baseDelay * Math.pow(2, attempt)
      await sleep(delay)
    }
  }

  throw lastError!
}

/**
 * Check if running in browser environment
 */
export function isBrowser(): boolean {
  return typeof window !== 'undefined'
}

/**
 * Local storage helpers with error handling
 */
export function safeGetStorage(key: string): string | null {
  if (!isBrowser()) return null

  try {
    return localStorage.getItem(key)
  } catch {
    return null
  }
}

export function safeSetStorage(key: string, value: string): boolean {
  if (!isBrowser()) return false

  try {
    localStorage.setItem(key, value)
    return true
  } catch {
    return false
  }
}

export function safeRemoveStorage(key: string): boolean {
  if (!isBrowser()) return false

  try {
    localStorage.removeItem(key)
    return true
  } catch {
    return false
  }
}