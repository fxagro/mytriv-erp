/**
 * TypeScript type definitions for MyTriv ERP Frontend
 */

import React from 'react'

// Base API Response Types
export interface ApiResponse<T = any> {
  success: boolean
  data?: T
  error?: string
  message?: string
}

export interface PaginatedResponse<T> {
  items: T[]
  total: number
  limit: number
  offset: number
  model?: string
  endpoint?: string
}

export interface ListOptions {
  limit?: number
  offset?: number
  search?: string
  domain?: any[]
  fields?: string[]
  sort?: string
  order?: 'ASC' | 'DESC'
}

// Authentication Types
export interface LoginCredentials {
  login: string
  password: string
  db?: string
}

export interface AuthResponse {
  user: User
  session_id: string
  message: string
  success: boolean
}

export interface User {
  id: number
  name: string
  login: string
  partner_id?: number
  company_id?: number
  company_name?: string
  partner?: Partner
  groups?: string[]
  active?: boolean
  last_login?: string
}

export interface Partner {
  id: number
  name: string
  email?: string
}

// Generic Model Types
export interface ModelRecord {
  id: number
  [key: string]: any
}

export interface ModelField {
  name: string
  type: string
  required?: boolean
  readonly?: boolean
  selection?: [string, string][]
}

// HR Module Types
export interface Employee extends ModelRecord {
  name: string
  job_title?: string
  work_email?: string
  work_phone?: string
  mobile_phone?: string
  department_id?: [number, string] | number
  parent_id?: [number, string] | number
  coach_id?: [number, string] | number
  active?: boolean
  gender?: string
  birthday?: string
  place_of_birth?: string
  country_of_birth?: [number, string] | number
  marital?: string
  spouse_complete_name?: string
  spouse_birthdate?: string
  children?: number
  emergency_contact?: string
  emergency_phone?: string
  address_home_id?: [number, string] | number
  work_location_id?: [number, string] | number
}

export interface Department extends ModelRecord {
  name: string
  parent_id?: number
  manager_id?: number
  active?: boolean
}

// CRM Module Types
export interface Lead extends ModelRecord {
  name: string
  partner_name?: string
  email_from?: string
  phone?: string
  mobile?: string
  street?: string
  city?: string
  country_id?: number
  stage_id?: number
  user_id?: number
  team_id?: number
  priority?: number
  type?: 'lead' | 'opportunity'
  expected_revenue?: number
  probability?: number
  date_deadline?: string
  activity_summary?: string
  next_activity_id?: number
  title_action?: string
  date_action?: string
  active?: boolean
  description?: string
  contact_name?: string
  partner_id?: number
  company_currency?: number
  campaign_id?: number
  source_id?: number
  medium_id?: number
}

export interface Stage extends ModelRecord {
  name: string
  sequence?: number
  fold?: boolean
  active?: boolean
}

// Sales Module Types
export interface SaleOrder extends ModelRecord {
  name: string
  partner_id?: number
  partner_shipping_id?: number
  partner_invoice_id?: number
  user_id?: number
  team_id?: number
  state?: string
  date_order?: string
  validity_date?: string
  require_signature?: boolean
  require_payment?: boolean
  create_date?: string
  confirmation_date?: string
  amount_total?: number
  amount_tax?: number
  currency_id?: number
  order_line?: SaleOrderLine[]
}

export interface SaleOrderLine extends ModelRecord {
  order_id?: number
  product_id?: number
  name?: string
  product_uom_qty?: number
  price_unit?: number
  tax_id?: number[]
  discount?: number
}

// Project Module Types
export interface Project extends ModelRecord {
  name: string
  user_id?: number
  partner_id?: number
  stage_id?: number
  date_start?: string
  date?: string
  description?: string
  active?: boolean
}

export interface Task extends ModelRecord {
  name: string
  project_id?: number
  user_id?: number
  stage_id?: number
  description?: string
  date_deadline?: string
  date_assign?: string
  active?: boolean
}

// Accounting Module Types
export interface AccountMove extends ModelRecord {
  name?: string
  partner_id?: number
  date?: string
  state?: string
  move_type?: string
  amount_total?: number
  amount_residual?: number
  currency_id?: number
  journal_id?: number
  payment_state?: string
  invoice_date?: string
  invoice_date_due?: string
}

export interface Journal extends ModelRecord {
  name: string
  code?: string
  type?: string
  active?: boolean
}

// Inventory Module Types
export interface Product extends ModelRecord {
  name: string
  default_code?: string
  barcode?: string
  type?: 'product' | 'service' | 'consu'
  categ_id?: number
  list_price?: number
  standard_price?: number
  uom_id?: number
  uom_po_id?: number
  active?: boolean
  description?: string
  description_sale?: string
  tracking?: 'none' | 'lot' | 'serial'
}

export interface ProductCategory extends ModelRecord {
  name: string
  parent_id?: number
  active?: boolean
}

// Service Layer Types
export interface ServiceResponse<T> {
  data?: T
  error?: string
  message?: string
  success: boolean
}

export interface ServiceListResponse<T> extends ServiceResponse<PaginatedResponse<T>> {}

// Form Types
export interface FormField {
  name: string
  label: string
  type: 'text' | 'email' | 'password' | 'number' | 'date' | 'select' | 'textarea' | 'checkbox'
  required?: boolean
  placeholder?: string
  options?: Array<{ value: any; label: string }>
  validation?: {
    min?: number
    max?: number
    pattern?: string
  }
}

export interface FormConfig {
  fields: FormField[]
  submitLabel?: string
  cancelLabel?: string
  layout?: 'horizontal' | 'vertical'
}

// UI Component Types
export interface TableColumn<T> {
  key: keyof T | string
  label: string
  sortable?: boolean
  width?: string
  render?: (value: any, record: T) => React.ReactNode
}

export interface TableProps<T> {
  data: T[]
  columns: TableColumn<T>[]
  loading?: boolean
  pagination?: {
    total: number
    current: number
    pageSize: number
    onChange: (page: number, pageSize: number) => void
  }
  onRowClick?: (record: T) => void
  actions?: Array<{
    label: string
    onClick: (record: T) => void
    variant?: 'primary' | 'secondary' | 'danger'
  }>
}

export interface ModalProps {
  open: boolean
  onClose: () => void
  title?: string
  children: React.ReactNode
  size?: 'sm' | 'md' | 'lg' | 'xl'
  footer?: React.ReactNode
}

// Error Types
export interface AppError {
  code: string
  message: string
  details?: any
  stack?: string
}

// Mock Data Types
export interface MockConfig {
  enabled: boolean
  delay: number
  errorRate: number
}

// Utility Types
export type DeepPartial<T> = {
  [P in keyof T]?: T[P] extends object ? DeepPartial<T[P]> : T[P]
}

export type Optional<T, K extends keyof T> = Omit<T, K> & Partial<Pick<T, K>>

export type RequiredFields<T, K extends keyof T> = T & Required<Pick<T, K>>

// API Client Types
export interface RequestConfig {
  timeout?: number
  retries?: number
  headers?: Record<string, string>
  params?: Record<string, any>
}

export interface ApiClient {
  get<T>(url: string, config?: RequestConfig): Promise<ServiceResponse<T>>
  post<T>(url: string, data?: any, config?: RequestConfig): Promise<ServiceResponse<T>>
  put<T>(url: string, data?: any, config?: RequestConfig): Promise<ServiceResponse<T>>
  delete<T>(url: string, config?: RequestConfig): Promise<ServiceResponse<T>>
}

// Context Types
export interface AuthContextType {
  user: User | null
  login: (credentials: LoginCredentials) => Promise<void>
  logout: () => Promise<void>
  isLoading: boolean
  isAuthenticated: boolean
}

export interface ApiContextType {
  client: ApiClient
  mockMode: boolean
}

// Hook Types
export interface UseApiOptions {
  enabled?: boolean
  refetchOnWindowFocus?: boolean
  staleTime?: number
}

export interface UseInfiniteQueryOptions extends UseApiOptions {
  getNextPageParam?: (lastPage: any, pages: any[]) => any
  getPreviousPageParam?: (firstPage: any, pages: any[]) => any
}