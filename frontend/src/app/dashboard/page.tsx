/**
 * Dashboard Page
 *
 * Main dashboard showing overview statistics and recent activities.
 */

'use client'

import React, { useEffect, useState } from 'react'
import { CardStat, CardStatGrid } from '@/components/ui/card-stat'
import { Spinner } from '@/components/ui/spinner'
import { hrService } from '@/services/hrService'
import { crmService } from '@/services/crmService'
import { config } from '@/lib/config'
import type { EmployeeStats, LeadStats } from '@/lib/types'

export default function DashboardPage() {
  const [loading, setLoading] = useState(true)
  const [employeeStats, setEmployeeStats] = useState<EmployeeStats | null>(null)
  const [leadStats, setLeadStats] = useState<LeadStats | null>(null)
  const [error, setError] = useState('')

  useEffect(() => {
    loadDashboardData()
  }, [])

  const loadDashboardData = async () => {
    setLoading(true)
    setError('')

    try {
      const [hrResponse, crmResponse] = await Promise.all([
        hrService.getEmployeeStats(),
        crmService.getLeadStats(),
      ])

      if (hrResponse.success && hrResponse.data) {
        setEmployeeStats(hrResponse.data)
      }

      if (crmResponse.success && crmResponse.data) {
        setLeadStats(crmResponse.data)
      }
    } catch (err) {
      setError('Failed to load dashboard data')
    } finally {
      setLoading(false)
    }
  }

  if (loading) {
    return (
      <div className="p-6">
        <h1 className="text-2xl font-bold text-gray-900 mb-6">Dashboard</h1>
        <PageSpinner message="Loading dashboard data..." />
      </div>
    )
  }

  return (
    <div className="p-6">
      <div className="mb-6">
        <h1 className="text-2xl font-bold text-gray-900">Dashboard</h1>
        <p className="text-gray-600">Welcome to {config.ui.appName}</p>
      </div>

      {error && (
        <div className="mb-6 p-4 bg-red-50 border border-red-200 rounded-md">
          <p className="text-red-700">{error}</p>
        </div>
      )}

      {/* Statistics Cards */}
      <CardStatGrid columns={4} className="mb-8">
        <CardStat
          title="Total Employees"
          value={employeeStats?.total || 0}
          subtitle={`${employeeStats?.active || 0} active`}
          icon={<UsersIcon />}
          loading={loading}
        />
        <CardStat
          title="Total Leads"
          value={leadStats?.total || 0}
          subtitle={`${leadStats?.opportunities || 0} opportunities`}
          icon={<TargetIcon />}
          loading={loading}
        />
        <CardStat
          title="Conversion Rate"
          value={`${leadStats?.conversionRate?.toFixed(1) || '0'}%`}
          subtitle="Leads to opportunities"
          trend={{
            value: leadStats?.conversionRate || 0,
            label: 'vs last month',
            direction: (leadStats?.conversionRate || 0) > 5 ? 'up' : 'down',
          }}
          icon={<TrendingIcon />}
          loading={loading}
        />
        <CardStat
          title="Expected Revenue"
          value={`$${(leadStats?.totalExpectedRevenue || 0).toLocaleString()}`}
          subtitle={`Avg: $${(leadStats?.averageRevenue || 0).toLocaleString()}`}
          icon={<DollarIcon />}
          loading={loading}
        />
      </CardStatGrid>

      {/* Recent Activities Section */}
      <div className="grid grid-cols-1 lg:grid-cols-2 gap-6">
        <div className="bg-white rounded-lg border border-gray-200 p-6">
          <h2 className="text-lg font-medium text-gray-900 mb-4">Recent Employees</h2>
          <p className="text-gray-500">Employee list would go here</p>
        </div>

        <div className="bg-white rounded-lg border border-gray-200 p-6">
          <h2 className="text-lg font-medium text-gray-900 mb-4">Recent Leads</h2>
          <p className="text-gray-500">Lead list would go here</p>
        </div>
      </div>

      {config.mock.enabled && (
        <div className="mt-6 p-4 bg-blue-50 border border-blue-200 rounded-md">
          <p className="text-blue-700">
            <strong>Mock Mode:</strong> Dashboard is showing simulated data.
          </p>
        </div>
      )}
    </div>
  )
}

// Simple icon components (replace with proper icons later)
function UsersIcon() {
  return (
    <svg className="h-8 w-8 text-blue-600" fill="none" viewBox="0 0 24 24" stroke="currentColor">
      <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M12 4.354a4 4 0 110 5.292M15 21H3v-1a6 6 0 0112 0v1zm0 0h6v-1a6 6 0 00-9-5.197m13.5-9a2.5 2.5 0 11-5 0 2.5 2.5 0 015 0z" />
    </svg>
  )
}

function TargetIcon() {
  return (
    <svg className="h-8 w-8 text-green-600" fill="none" viewBox="0 0 24 24" stroke="currentColor">
      <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M9 12l2 2 4-4m6 2a9 9 0 11-18 0 9 9 0 0118 0z" />
    </svg>
  )
}

function TrendingIcon() {
  return (
    <svg className="h-8 w-8 text-purple-600" fill="none" viewBox="0 0 24 24" stroke="currentColor">
      <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M13 7h8m0 0v8m0-8l-8 8-4-4-6 6" />
    </svg>
  )
}

function DollarIcon() {
  return (
    <svg className="h-8 w-8 text-yellow-600" fill="none" viewBox="0 0 24 24" stroke="currentColor">
      <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M12 8c-1.657 0-3 .895-3 2s1.343 2 3 2 3 .895 3 2-1.343 2-3 2m0-8c1.11 0 2.08.402 2.599 1M12 8V7m0 1v8m0 0v1m0-1c-1.11 0-2.08-.402-2.599-1" />
    </svg>
  )
}

function PageSpinner({ message }: { message: string }) {
  return (
    <div className="flex flex-col items-center justify-center py-12">
      <Spinner size="lg" />
      <p className="mt-4 text-gray-600">{message}</p>
    </div>
  )
}