// Common types for API responses and data models

export interface ApiResponse<T> {
  model?: string;
  records?: T[];
  record?: T;
  count?: number;
  error?: string;
}

export interface Employee {
  id: number;
  name: string;
  work_email?: string;
  work_phone?: string;
  department_id?: number;
  job_title?: string;
  active?: boolean;
  create_date?: string;
  write_date?: string;
}

export interface Department {
  id: number;
  name: string;
  manager_id?: number;
  active?: boolean;
}

export class ApiError extends Error {
  constructor(message: string, public status?: number, public details?: any) {
    super(message);
    this.name = 'ApiError';
  }
}

export interface ApiErrorResponse {
  message: string;
  status?: number;
  details?: any;
}