/**
 * CRM Leads Page
 *
 * Customer relationship management leads interface.
 */

'use client'

import React, { useState, useEffect } from 'react'
import { Table } from '@/components/ui/table'
import { Spinner } from '@/components/ui/spinner'
import { crmService } from '@/services/crmService'
import { config } from '@/lib/config'
import type { Lead, TableColumn } from '@/lib/types'

export default function LeadsPage() {
  const [leads, setLeads] = useState<Lead[]>([])
  const [loading, setLoading] = useState(true)
  const [error, setError] = useState('')
  const [search, setSearch] = useState('')

  useEffect(() => {
    loadLeads()
  }, [])

  const loadLeads = async () => {
    setLoading(true)
    try {
      const response = await crmService.listLeads({
        limit: 100,
        search: search || undefined,
      })

      if (response.success && response.data) {
        setLeads(response.data.items)
      } else {
        setError(response.error || 'Failed to load leads')
      }
    } catch (err) {
      setError('An unexpected error occurred')
    } finally {
      setLoading(false)
    }
  }

  const columns: TableColumn<Lead>[] = [
    {
      key: 'name',
      label: 'Name',
      sortable: true,
    },
    {
      key: 'partner_name',
      label: 'Company',
    },
    {
      key: 'email_from',
      label: 'Email',
    },
    {
      key: 'phone',
      label: 'Phone',
    },
    {
      key: 'stage_id',
      label: 'Stage',
      render: (value) => Array.isArray(value) ? value[1] : value,
    },
    {
      key: 'expected_revenue',
      label: 'Expected Revenue',
      render: (value) => value ? `$${value.toLocaleString()}` : '-',
    },
    {
      key: 'priority',
      label: 'Priority',
      render: (value) => {
        const priorities = { 0: 'Very Low', 1: 'Low', 2: 'Medium', 3: 'High' }
        return priorities[value as keyof typeof priorities] || 'Unknown'
      },
    },
    {
      key: 'type',
      label: 'Type',
      render: (value) => value === 'opportunity' ? 'Opportunity' : 'Lead',
    },
  ]

  return (
    <div className="p-6">
      <div className="mb-6">
        <h1 className="text-2xl font-bold text-gray-900">CRM Leads</h1>
        <p className="text-gray-600">Manage customer leads and opportunities</p>
      </div>

      {/* Search and Actions */}
      <div className="mb-6 flex justify-between items-center">
        <input
          type="text"
          placeholder="Search leads..."
          className="px-4 py-2 border border-gray-300 rounded-md"
          value={search}
          onChange={(e) => setSearch(e.target.value)}
        />
        <button className="px-4 py-2 bg-green-600 text-white rounded-md">
          Add Lead
        </button>
      </div>

      {error && (
        <div className="mb-6 p-4 bg-red-50 border border-red-200 rounded-md">
          <p className="text-red-700">{error}</p>
        </div>
      )}

      {/* Leads Table */}
      <Table
        data={leads}
        columns={columns}
        loading={loading}
        actions={[
          {
            label: 'Edit',
            onClick: (lead) => console.log('Edit', lead),
          },
          {
            label: 'Convert',
            onClick: (lead) => console.log('Convert', lead),
          },
          {
            label: 'Delete',
            onClick: (lead) => console.log('Delete', lead),
            variant: 'danger',
          },
        ]}
      />

      {config.mock.enabled && (
        <div className="mt-6 p-4 bg-blue-50 border border-blue-200 rounded-md">
          <p className="text-blue-700">
            <strong>Mock Mode:</strong> Lead data is simulated.
          </p>
        </div>
      )}
    </div>
  )
}