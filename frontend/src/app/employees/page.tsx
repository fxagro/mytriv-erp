'use client';

import { useState, useEffect } from 'react';
import { Button } from '@/components/ui/button';
import { employeeService, Employee } from '@/services/employeeService';
import { ApiError } from '@/lib/types';

export default function EmployeesPage() {
  const [employees, setEmployees] = useState<Employee[]>([]);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);
  const [searchQuery, setSearchQuery] = useState('');

  // Fetch employees on component mount
  useEffect(() => {
    fetchEmployees();
  }, []);

  const fetchEmployees = async () => {
    try {
      setLoading(true);
      setError(null);
      const data = await employeeService.getEmployees({ limit: 20 });
      setEmployees(data);
    } catch (err) {
      console.error('Error fetching employees:', err);
      if (err instanceof ApiError) {
        setError(`API Error (${err.status}): ${err.message}`);
      } else {
        setError('Failed to fetch employees. Please check if the backend is running.');
      }
    } finally {
      setLoading(false);
    }
  };

  const handleSearch = async () => {
    if (!searchQuery.trim()) {
      fetchEmployees();
      return;
    }

    try {
      setLoading(true);
      setError(null);
      const data = await employeeService.searchEmployees(searchQuery);
      setEmployees(data);
    } catch (err) {
      console.error('Error searching employees:', err);
      if (err instanceof ApiError) {
        setError(`Search Error (${err.status}): ${err.message}`);
      } else {
        setError('Failed to search employees.');
      }
    } finally {
      setLoading(false);
    }
  };

  const createSampleEmployee = async () => {
    try {
      setError(null);
      const newEmployee = await employeeService.createEmployee({
        name: `Sample Employee ${Date.now()}`,
        work_email: `sample${Date.now()}@example.com`,
        active: true,
      });

      console.log('Created employee:', newEmployee);
      // Refresh the list
      fetchEmployees();
    } catch (err) {
      console.error('Error creating employee:', err);
      if (err instanceof ApiError) {
        setError(`Create Error (${err.status}): ${err.message}`);
      } else {
        setError('Failed to create employee.');
      }
    }
  };

  return (
    <div className="container mx-auto py-8 px-4">
      <div className="max-w-6xl mx-auto">
        <h1 className="text-3xl font-bold mb-8">Employee Management</h1>

        {/* API Status and Controls */}
        <div className="bg-card p-6 rounded-lg mb-8 border">
          <h2 className="text-xl font-semibold mb-4">API Integration Demo</h2>

          <div className="flex flex-wrap gap-4 mb-4">
            <Button onClick={fetchEmployees} disabled={loading}>
              {loading ? 'Loading...' : 'Refresh Employees'}
            </Button>

            <Button onClick={createSampleEmployee} variant="outline">
              Create Sample Employee
            </Button>
          </div>

          {/* Search */}
          <div className="flex gap-2">
            <input
              type="text"
              placeholder="Search employees by name or email..."
              value={searchQuery}
              onChange={(e) => setSearchQuery(e.target.value)}
              className="flex-1 px-3 py-2 border border-input rounded-md bg-background"
              onKeyPress={(e) => e.key === 'Enter' && handleSearch()}
            />
            <Button onClick={handleSearch} disabled={loading}>
              Search
            </Button>
          </div>

          {/* Error Display */}
          {error && (
            <div className="mt-4 p-3 bg-destructive/10 border border-destructive/20 rounded-md">
              <p className="text-destructive text-sm">{error}</p>
            </div>
          )}
        </div>

        {/* Employees List */}
        <div className="bg-card rounded-lg border">
          <div className="p-6 border-b">
            <h3 className="text-lg font-semibold">
              Employees ({employees.length})
            </h3>
          </div>

          {loading && (
            <div className="p-6 text-center">
              <p className="text-muted-foreground">Loading employees...</p>
            </div>
          )}

          {!loading && employees.length === 0 && (
            <div className="p-6 text-center">
              <p className="text-muted-foreground">No employees found.</p>
            </div>
          )}

          {employees.length > 0 && (
            <div className="divide-y">
              {employees.map((employee) => (
                <div key={employee.id} className="p-4 hover:bg-muted/50">
                  <div className="flex justify-between items-start">
                    <div className="flex-1">
                      <h4 className="font-medium">{employee.name}</h4>
                      {employee.work_email && (
                        <p className="text-sm text-muted-foreground">
                          {employee.work_email}
                        </p>
                      )}
                      {employee.work_phone && (
                        <p className="text-sm text-muted-foreground">
                          {employee.work_phone}
                        </p>
                      )}
                    </div>
                    <div className="flex items-center gap-2">
                      <span
                        className={`px-2 py-1 text-xs rounded-full ${
                          employee.active
                            ? 'bg-green-100 text-green-800'
                            : 'bg-gray-100 text-gray-800'
                        }`}
                      >
                        {employee.active ? 'Active' : 'Inactive'}
                      </span>
                    </div>
                  </div>
                </div>
              ))}
            </div>
          )}
        </div>

        {/* API Information */}
        <div className="mt-8 bg-muted/50 p-6 rounded-lg">
          <h3 className="text-lg font-semibold mb-4">API Information</h3>
          <div className="space-y-2 text-sm">
            <p><strong>API URL:</strong> {process.env.NEXT_PUBLIC_API_URL || 'http://localhost:8069/api'}</p>
            <p><strong>Status:</strong> {error ? 'Error' : loading ? 'Loading' : 'Connected'}</p>
            <p><strong>Sample Endpoint:</strong> <code>GET /api/v1/employees</code></p>
          </div>
        </div>
      </div>
    </div>
  );
}