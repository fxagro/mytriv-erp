/**
 * CRM Service for MyTriv ERP
 *
 * Provides CRM-specific operations and business logic for lead management.
 * Wraps the generic model service with CRM-specific functionality.
 */

import { apiClient } from './apiClient'
import { GenericModelService } from './genericModelService'
import { config } from '@/lib/config'
import type {
  ServiceResponse,
  ServiceListResponse,
  PaginatedResponse,
  Lead,
  ListOptions
} from '@/lib/types'

export class CRMService extends GenericModelService {
  private model = 'crm.lead'

  /**
   * List leads with CRM-specific filtering
   */
  async listLeads(options: CRMListOptions = {}): Promise<ServiceListResponse<Lead>> {
    try {
      // Build domain for CRM-specific filters
      const domain: any[] = []

      if (options.stageId) {
        domain.push(['stage_id', '=', options.stageId])
      }

      if (options.userId) {
        domain.push(['user_id', '=', options.userId])
      }

      if (options.priority !== undefined) {
        domain.push(['priority', '=', options.priority])
      }

      if (options.type) {
        domain.push(['type', '=', options.type])
      }

      if (options.expectedRevenueMin !== undefined) {
        domain.push(['expected_revenue', '>=', options.expectedRevenueMin])
      }

      if (options.expectedRevenueMax !== undefined) {
        domain.push(['expected_revenue', '<=', options.expectedRevenueMax])
      }

      if (options.probabilityMin !== undefined) {
        domain.push(['probability', '>=', options.probabilityMin])
      }

      if (options.probabilityMax !== undefined) {
        domain.push(['probability', '<=', options.probabilityMax])
      }

      if (options.deadlineBefore) {
        domain.push(['date_deadline', '<=', options.deadlineBefore])
      }

      if (options.deadlineAfter) {
        domain.push(['date_deadline', '>=', options.deadlineAfter])
      }

      const response = await apiClient.listLeads({
        ...options,
        domain: domain.length > 0 ? domain : options.domain,
      })

      return response
    } catch (error) {
      return {
        error: error instanceof Error ? error.message : 'Failed to list leads',
        success: false,
      }
    }
  }

  /**
   * Get lead by ID
   */
  async getLead(id: number): Promise<ServiceResponse<Lead>> {
    return this.get<Lead>(this.model, id)
  }

  /**
   * Create new lead
   */
  async createLead(data: CreateLeadData): Promise<ServiceResponse<Lead>> {
    return this.create<Lead>(this.model, data)
  }

  /**
   * Update lead
   */
  async updateLead(id: number, data: UpdateLeadData): Promise<ServiceResponse<Lead>> {
    return this.update<Lead>(this.model, id, data)
  }

  /**
   * Delete lead
   */
  async deleteLead(id: number): Promise<ServiceResponse<{ deleted_id: number; message: string }>> {
    return this.delete(this.model, id)
  }

  /**
   * Convert lead to opportunity
   */
  async convertToOpportunity(id: number, data: ConvertToOpportunityData = {}): Promise<ServiceResponse<Lead>> {
    try {
      const updateData = {
        type: 'opportunity' as const,
        ...data,
      }

      return this.update<Lead>(this.model, id, updateData)
    } catch (error) {
      return {
        error: error instanceof Error ? error.message : 'Failed to convert lead to opportunity',
        success: false,
      }
    }
  }

  /**
   * Get leads by stage
   */
  async getLeadsByStage(stageId: number): Promise<ServiceListResponse<Lead>> {
    return this.listLeads({
      stageId,
    })
  }

  /**
   * Get leads by assigned user
   */
  async getLeadsByUser(userId: number): Promise<ServiceListResponse<Lead>> {
    return this.listLeads({
      userId,
    })
  }

  /**
   * Get leads by priority
   */
  async getLeadsByPriority(priority: number): Promise<ServiceListResponse<Lead>> {
    return this.listLeads({
      priority,
    })
  }

  /**
   * Get high-priority leads (priority >= 2)
   */
  async getHighPriorityLeads(): Promise<ServiceListResponse<Lead>> {
    return this.listLeads({
      priorityMin: 2,
    })
  }

  /**
   * Get overdue leads (past deadline)
   */
  async getOverdueLeads(): Promise<ServiceListResponse<Lead>> {
    const today = new Date().toISOString().split('T')[0]
    return this.listLeads({
      deadlineBefore: today,
    })
  }

  /**
   * Get leads due soon (next 7 days)
   */
  async getLeadsDueSoon(days: number = 7): Promise<ServiceListResponse<Lead>> {
    const today = new Date()
    const futureDate = new Date()
    futureDate.setDate(today.getDate() + days)

    return this.listLeads({
      deadlineAfter: today.toISOString().split('T')[0],
      deadlineBefore: futureDate.toISOString().split('T')[0],
    })
  }

  /**
   * Search leads by name, email, or company
   */
  async searchLeads(query: string, options: CRMListOptions = {}): Promise<ServiceListResponse<Lead>> {
    return this.listLeads({
      ...options,
      search: query,
    })
  }

  /**
   * Get lead statistics
   */
  async getLeadStats(): Promise<ServiceResponse<LeadStats>> {
    try {
      const response = await this.listLeads({
        limit: 1000, // Get all for statistics
      })

      if (!response.success || !response.data) {
        return response as ServiceResponse<LeadStats>
      }

      const leads = response.data.items
      const total = leads.length

      // Count by type
      const leadsCount = leads.filter(lead => lead.type === 'lead').length
      const opportunitiesCount = leads.filter(lead => lead.type === 'opportunity').length

      // Count by stage
      const stageMap = new Map<number, number>()
      leads.forEach(lead => {
        const stageId = Array.isArray(lead.stage_id) ? lead.stage_id[0] : lead.stage_id
        if (stageId) {
          stageMap.set(stageId, (stageMap.get(stageId) || 0) + 1)
        }
      })

      const stageBreakdown = Array.from(stageMap.entries()).map(([id, count]) => ({
        id,
        count,
      }))

      // Count by priority
      const priorityMap = new Map<number, number>()
      leads.forEach(lead => {
        const priority = lead.priority || 0
        priorityMap.set(priority, (priorityMap.get(priority) || 0) + 1)
      })

      const priorityBreakdown = Array.from(priorityMap.entries()).map(([priority, count]) => ({
        priority,
        count,
      }))

      // Revenue statistics
      const leadsWithRevenue = leads.filter(lead => lead.expected_revenue && lead.expected_revenue > 0)
      const totalExpectedRevenue = leadsWithRevenue.reduce((sum, lead) => sum + (lead.expected_revenue || 0), 0)
      const averageRevenue = leadsWithRevenue.length > 0 ? totalExpectedRevenue / leadsWithRevenue.length : 0

      return {
        data: {
          total,
          leads: leadsCount,
          opportunities: opportunitiesCount,
          stageBreakdown,
          priorityBreakdown,
          totalExpectedRevenue,
          averageRevenue,
          conversionRate: total > 0 ? (opportunitiesCount / total) * 100 : 0,
        },
        success: true,
      }
    } catch (error) {
      return {
        error: error instanceof Error ? error.message : 'Failed to get lead statistics',
        success: false,
      }
    }
  }

  /**
   * Get leads pipeline (grouped by stage)
   */
  async getLeadsPipeline(): Promise<ServiceResponse<LeadPipeline[]>> {
    try {
      const response = await this.listLeads({
        limit: 1000, // Get all for pipeline
      })

      if (!response.success || !response.data) {
        return response as ServiceResponse<LeadPipeline[]>
      }

      const leads = response.data.items

      // Group leads by stage
      const pipelineMap = new Map<number, Lead[] & { stageName?: string }>()

      leads.forEach(lead => {
        const stageId = Array.isArray(lead.stage_id) ? lead.stage_id[0] : lead.stage_id
        if (stageId) {
          if (!pipelineMap.has(stageId)) {
            pipelineMap.set(stageId, [])
          }
          pipelineMap.get(stageId)!.push(lead)
        }
      })

      const pipeline = Array.from(pipelineMap.entries()).map(([stageId, stageLeads]) => ({
        stageId,
        stageName: Array.isArray(stageLeads[0]?.stage_id) ? stageLeads[0].stage_id[1] : 'Unknown Stage',
        leads: stageLeads,
        count: stageLeads.length,
        totalValue: stageLeads.reduce((sum, lead) => sum + (lead.expected_revenue || 0), 0),
      }))

      // Sort by stage sequence (if available)
      pipeline.sort((a, b) => a.stageId - b.stageId)

      return {
        data: pipeline,
        success: true,
      }
    } catch (error) {
      return {
        error: error instanceof Error ? error.message : 'Failed to get leads pipeline',
        success: false,
      }
    }
  }

  /**
   * Get recent activities for leads
   */
  async getRecentActivities(limit: number = 10): Promise<ServiceResponse<LeadActivity[]>> {
    try {
      // This would require a specific endpoint for activities
      // For now, return a placeholder response
      return {
        data: [],
        success: true,
        message: 'Recent activities endpoint not implemented yet',
      }
    } catch (error) {
      return {
        error: error instanceof Error ? error.message : 'Failed to get recent activities',
        success: false,
      }
    }
  }
}

// Type definitions for CRM service
export interface CRMListOptions extends ListOptions {
  stageId?: number
  userId?: number
  priority?: number
  priorityMin?: number
  priorityMax?: number
  type?: 'lead' | 'opportunity'
  expectedRevenueMin?: number
  expectedRevenueMax?: number
  probabilityMin?: number
  probabilityMax?: number
  deadlineBefore?: string
  deadlineAfter?: string
}

export interface CreateLeadData {
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
  description?: string
  contact_name?: string
  partner_id?: number
}

export interface UpdateLeadData extends Partial<CreateLeadData> {}

export interface ConvertToOpportunityData {
  expected_revenue?: number
  probability?: number
  date_deadline?: string
}

export interface LeadStats {
  total: number
  leads: number
  opportunities: number
  stageBreakdown: Array<{ id: number; count: number }>
  priorityBreakdown: Array<{ priority: number; count: number }>
  totalExpectedRevenue: number
  averageRevenue: number
  conversionRate: number
}

export interface LeadPipeline {
  stageId: number
  stageName: string
  leads: Lead[]
  count: number
  totalValue: number
}

export interface LeadActivity {
  id: number
  lead_id: number
  activity_type: string
  summary: string
  date: string
  user_id: number
}

// Create and export singleton instance
export const crmService = new CRMService()