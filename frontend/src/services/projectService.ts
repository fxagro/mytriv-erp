/**
 * Project Service for MyTriv ERP
 */

import { GenericModelService } from './genericModelService'
import type { ServiceResponse, ServiceListResponse, Project, Task, ListOptions } from '@/lib/types'

export class ProjectService extends GenericModelService {
  async listProjects(options: ListOptions = {}): Promise<ServiceListResponse<Project>> {
    return this.list<Project>('project.project', options)
  }

  async listTasks(options: ListOptions = {}): Promise<ServiceListResponse<Task>> {
    return this.list<Task>('project.task', options)
  }
}

export const projectService = new ProjectService()