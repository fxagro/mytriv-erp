import apiClient from '@/lib/api';
import { Employee, ApiResponse, ApiError } from '@/lib/types';

// Re-export Employee type for convenience
export type { Employee } from '@/lib/types';

export class EmployeeService {
  /**
   * Get all employees from Odoo
   */
  static async getEmployees(params?: {
    limit?: number;
    offset?: number;
    domain?: any[];
    fields?: string[];
  }): Promise<Employee[]> {
    try {
      const queryParams = new URLSearchParams();

      if (params?.limit) queryParams.append('limit', params.limit.toString());
      if (params?.offset) queryParams.append('offset', params.offset.toString());
      if (params?.domain) queryParams.append('domain', JSON.stringify(params.domain));
      if (params?.fields) queryParams.append('fields', JSON.stringify(params.fields));

      const response = await apiClient.get<Employee[]>(
        `/v1/employees?${queryParams.toString()}`
      );

      return response.data || [];
    } catch (error: any) {
      console.error('Error fetching employees:', error);
      throw new ApiError(
        error.response?.data?.error || 'Failed to fetch employees',
        error.response?.status || 500
      );
    }
  }

  /**
   * Get a specific employee by ID
   */
  static async getEmployee(id: number): Promise<Employee> {
    try {
      const response = await apiClient.get<Employee>(
        `/v1/employees/${id}`
      );

      return response.data;
    } catch (error: any) {
      console.error(`Error fetching employee ${id}:`, error);
      throw new ApiError(
        error.response?.data?.error || 'Failed to fetch employee',
        error.response?.status || 500
      );
    }
  }

  /**
   * Create a new employee
   */
  static async createEmployee(employeeData: Omit<Employee, 'id'>): Promise<Employee> {
    try {
      const response = await apiClient.post<Employee>(
        '/v1/employees',
        employeeData
      );

      return response.data;
    } catch (error: any) {
      console.error('Error creating employee:', error);
      throw new ApiError(
        error.response?.data?.error || 'Failed to create employee',
        error.response?.status || 500
      );
    }
  }

  /**
   * Update an existing employee
   */
  static async updateEmployee(id: number, employeeData: Partial<Employee>): Promise<Employee> {
    try {
      const response = await apiClient.put<Employee>(
        `/v1/employees/${id}`,
        employeeData
      );

      return response.data;
    } catch (error: any) {
      console.error(`Error updating employee ${id}:`, error);
      throw new ApiError(
        error.response?.data?.error || 'Failed to update employee',
        error.response?.status || 500
      );
    }
  }

  /**
   * Delete an employee
   */
  static async deleteEmployee(id: number): Promise<void> {
    try {
      await apiClient.delete(`/v1/employees/${id}`);
    } catch (error: any) {
      console.error(`Error deleting employee ${id}:`, error);
      throw new ApiError(
        error.response?.data?.error || 'Failed to delete employee',
        error.response?.status || 500
      );
    }
  }

  /**
   * Search employees by name or email
   */
  static async searchEmployees(query: string): Promise<Employee[]> {
    try {
      const domain = [
        '|',
        ['name', 'ilike', query],
        ['work_email', 'ilike', query]
      ];

      return this.getEmployees({ domain, limit: 50 });
    } catch (error: any) {
      console.error('Error searching employees:', error);
      throw new ApiError(
        error.response?.data?.error || 'Failed to search employees',
        error.response?.status || 500
      );
    }
  }

  /**
   * Get employees by department
   */
  static async getEmployeesByDepartment(departmentId: number): Promise<Employee[]> {
    try {
      const domain = [['department_id', '=', departmentId]];
      return this.getEmployees({ domain, limit: 100 });
    } catch (error: any) {
      console.error(`Error fetching employees for department ${departmentId}:`, error);
      throw new ApiError(
        error.response?.data?.error || 'Failed to fetch department employees',
        error.response?.status || 500
      );
    }
  }
}

// Export a simple object-based API for easier usage
export const employeeService = {
  getEmployees: EmployeeService.getEmployees,
  getEmployee: EmployeeService.getEmployee,
  createEmployee: EmployeeService.createEmployee,
  updateEmployee: EmployeeService.updateEmployee,
  deleteEmployee: EmployeeService.deleteEmployee,
  searchEmployees: EmployeeService.searchEmployees,
  getEmployeesByDepartment: EmployeeService.getEmployeesByDepartment,
};