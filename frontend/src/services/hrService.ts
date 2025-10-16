/**
 * HR Service for MyTriv ERP
 *
 * Provides HR-specific operations and business logic for employee management.
 * Wraps the generic model service with HR-specific functionality.
 */

import { apiClient } from './apiClient'
import { GenericModelService } from './genericModelService'
import { config } from '@/lib/config'
import type {
  ServiceResponse,
  ServiceListResponse,
  PaginatedResponse,
  Employee,
  ListOptions
} from '@/lib/types'

export class HRService extends GenericModelService {
  private model = 'hr.employee'

  /**
   * List employees with HR-specific filtering
   */
  async listEmployees(options: HRListOptions = {}): Promise<ServiceListResponse<Employee>> {
    try {
      // Build domain for HR-specific filters
      const domain: any[] = []

      if (options.departmentId) {
        domain.push(['department_id', '=', options.departmentId])
      }

      if (options.active !== undefined) {
        domain.push(['active', '=', options.active])
      }

      if (options.managerId) {
        domain.push(['parent_id', '=', options.managerId])
      }

      if (options.jobTitle) {
        domain.push(['job_title', 'ilike', options.jobTitle])
      }

      if (options.workEmail) {
        domain.push(['work_email', 'ilike', options.workEmail])
      }

      const response = await apiClient.listEmployees({
        ...options,
        domain: domain.length > 0 ? domain : options.domain,
      })

      return response
    } catch (error) {
      return {
        error: error instanceof Error ? error.message : 'Failed to list employees',
        success: false,
      }
    }
  }

  /**
   * Get employee by ID
   */
  async getEmployee(id: number): Promise<ServiceResponse<Employee>> {
    return this.get<Employee>(this.model, id)
  }

  /**
   * Create new employee
   */
  async createEmployee(data: CreateEmployeeData): Promise<ServiceResponse<Employee>> {
    return this.create<Employee>(this.model, data)
  }

  /**
   * Update employee
   */
  async updateEmployee(id: number, data: UpdateEmployeeData): Promise<ServiceResponse<Employee>> {
    return this.update<Employee>(this.model, id, data)
  }

  /**
   * Delete employee
   */
  async deleteEmployee(id: number): Promise<ServiceResponse<{ deleted_id: number; message: string }>> {
    return this.delete(this.model, id)
  }

  /**
   * Get employees by department
   */
  async getEmployeesByDepartment(departmentId: number): Promise<ServiceListResponse<Employee>> {
    return this.listEmployees({
      departmentId,
      active: true,
    })
  }

  /**
   * Get employee hierarchy (managers and their reports)
   */
  async getEmployeeHierarchy(): Promise<ServiceResponse<EmployeeHierarchy[]>> {
    try {
      const response = await this.listEmployees({
        active: true,
        limit: 1000, // Get all for hierarchy
      })

      if (!response.success || !response.data) {
        return response as ServiceResponse<EmployeeHierarchy[]>
      }

      // Build hierarchy structure
      const employeeMap = new Map<number, Employee & { reports: Employee[] }>()
      const rootEmployees: (Employee & { reports: Employee[] })[] = []

      // First pass: create employee map
      response.data.items.forEach(emp => {
        employeeMap.set(emp.id, { ...emp, reports: [] })
      })

      // Second pass: build hierarchy
      response.data.items.forEach(emp => {
        const employeeWithReports = employeeMap.get(emp.id)!
        const managerId = Array.isArray(emp.parent_id) ? emp.parent_id[0] : emp.parent_id

        if (managerId && employeeMap.has(managerId)) {
          const manager = employeeMap.get(managerId)!
          manager.reports.push(employeeWithReports)
        } else {
          rootEmployees.push(employeeWithReports)
        }
      })

      return {
        data: rootEmployees,
        success: true,
      }
    } catch (error) {
      return {
        error: error instanceof Error ? error.message : 'Failed to get employee hierarchy',
        success: false,
      }
    }
  }

  /**
   * Search employees by name, email, or job title
   */
  async searchEmployees(query: string, options: HRListOptions = {}): Promise<ServiceListResponse<Employee>> {
    return this.listEmployees({
      ...options,
      search: query,
    })
  }

  /**
   * Get employee statistics
   */
  async getEmployeeStats(): Promise<ServiceResponse<EmployeeStats>> {
    try {
      const response = await this.listEmployees({
        limit: 1000, // Get all for statistics
      })

      if (!response.success || !response.data) {
        return response as ServiceResponse<EmployeeStats>
      }

      const employees = response.data.items
      const total = employees.length
      const active = employees.filter(emp => emp.active).length
      const inactive = total - active

      // Department breakdown
      const departmentMap = new Map<number, number>()
      employees.forEach(emp => {
        const deptId = Array.isArray(emp.department_id) ? emp.department_id[0] : emp.department_id
        if (deptId) {
          departmentMap.set(deptId, (departmentMap.get(deptId) || 0) + 1)
        }
      })

      const departments = Array.from(departmentMap.entries()).map(([id, count]) => ({
        id,
        count,
      }))

      // Gender breakdown
      const genderMap = new Map<string, number>()
      employees.forEach(emp => {
        const gender = emp.gender || 'unspecified'
        genderMap.set(gender, (genderMap.get(gender) || 0) + 1)
      })

      const genderBreakdown = Array.from(genderMap.entries()).map(([gender, count]) => ({
        gender,
        count,
      }))

      return {
        data: {
          total,
          active,
          inactive,
          departments,
          genderBreakdown,
        },
        success: true,
      }
    } catch (error) {
      return {
        error: error instanceof Error ? error.message : 'Failed to get employee statistics',
        success: false,
      }
    }
  }

  /**
   * Get upcoming employee birthdays
   */
  async getUpcomingBirthdays(days: number = 30): Promise<ServiceResponse<Employee[]>> {
    try {
      const response = await this.listEmployees({
        active: true,
        limit: 1000,
      })

      if (!response.success || !response.data) {
        return response as ServiceResponse<Employee[]>
      }

      const today = new Date()
      const futureDate = new Date()
      futureDate.setDate(today.getDate() + days)

      const upcomingBirthdays = response.data.items.filter(emp => {
        if (!emp.birthday) return false

        const birthday = new Date(emp.birthday)
        const thisYearBirthday = new Date(today.getFullYear(), birthday.getMonth(), birthday.getDate())

        // If birthday already passed this year, check next year
        if (thisYearBirthday < today) {
          thisYearBirthday.setFullYear(today.getFullYear() + 1)
        }

        return thisYearBirthday <= futureDate
      })

      return {
        data: upcomingBirthdays,
        success: true,
      }
    } catch (error) {
      return {
        error: error instanceof Error ? error.message : 'Failed to get upcoming birthdays',
        success: false,
      }
    }
  }

  /**
   * Get employees by work location
   */
  async getEmployeesByLocation(locationId: number): Promise<ServiceListResponse<Employee>> {
    try {
      const response = await this.listEmployees({
        active: true,
        limit: 1000,
      })

      if (!response.success || !response.data) {
        return response
      }

      const employeesAtLocation = response.data.items.filter(emp =>
        (Array.isArray(emp.work_location_id) ? emp.work_location_id[0] : emp.work_location_id) === locationId
      )

      return {
        data: {
          items: employeesAtLocation,
          total: employeesAtLocation.length,
          limit: employeesAtLocation.length,
          offset: 0,
        },
        success: true,
      }
    } catch (error) {
      return {
        error: error instanceof Error ? error.message : 'Failed to get employees by location',
        success: false,
      }
    }
  }
}

// Type definitions for HR service
export interface HRListOptions extends ListOptions {
  departmentId?: number
  managerId?: number
  jobTitle?: string
  workEmail?: string
  active?: boolean
}

export interface CreateEmployeeData {
  name: string
  job_title?: string
  work_email?: string
  work_phone?: string
  mobile_phone?: string
  department_id?: number
  parent_id?: number
  coach_id?: number
  active?: boolean
  gender?: string
  birthday?: string
  place_of_birth?: string
  country_of_birth?: number
  marital?: string
  address_home_id?: number
  work_location_id?: number
}

export interface UpdateEmployeeData extends Partial<CreateEmployeeData> {}

export interface EmployeeHierarchy extends Employee {
  reports: Employee[]
}

export interface EmployeeStats {
  total: number
  active: number
  inactive: number
  departments: Array<{ id: number; count: number }>
  genderBreakdown: Array<{ gender: string; count: number }>
}

// Create and export singleton instance
export const hrService = new HRService()