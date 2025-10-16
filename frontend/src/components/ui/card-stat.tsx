/**
 * CardStat Component
 *
 * Displays a statistic card with title, value, and optional trend indicator.
 */

import React from 'react'
import { cn } from '@/lib/utils'

interface CardStatProps {
  title: string
  value: string | number
  subtitle?: string
  trend?: {
    value: number
    label: string
    direction: 'up' | 'down' | 'neutral'
  }
  icon?: React.ReactNode
  className?: string
  loading?: boolean
}

const trendColors = {
  up: 'text-green-600 bg-green-50',
  down: 'text-red-600 bg-red-50',
  neutral: 'text-gray-600 bg-gray-50',
}

const trendIcons = {
  up: '↗',
  down: '↘',
  neutral: '→',
}

export function CardStat({
  title,
  value,
  subtitle,
  trend,
  icon,
  className,
  loading = false
}: CardStatProps) {
  if (loading) {
    return (
      <div className={cn(
        'bg-white rounded-lg border border-gray-200 p-6 animate-pulse',
        className
      )}>
        <div className="flex items-center justify-between">
          <div className="space-y-2">
            <div className="h-4 bg-gray-200 rounded w-24"></div>
            <div className="h-8 bg-gray-200 rounded w-16"></div>
            <div className="h-3 bg-gray-200 rounded w-20"></div>
          </div>
          <div className="h-8 w-8 bg-gray-200 rounded"></div>
        </div>
      </div>
    )
  }

  return (
    <div className={cn(
      'bg-white rounded-lg border border-gray-200 p-6 hover:shadow-md transition-shadow',
      className
    )}>
      <div className="flex items-center justify-between">
        <div className="space-y-1">
          <p className="text-sm font-medium text-gray-600">{title}</p>
          <p className="text-2xl font-bold text-gray-900">{value}</p>
          {subtitle && (
            <p className="text-sm text-gray-500">{subtitle}</p>
          )}
        </div>
        {icon && (
          <div className="flex-shrink-0">
            {icon}
          </div>
        )}
      </div>

      {trend && (
        <div className="mt-4 flex items-center space-x-2">
          <span className={cn(
            'inline-flex items-center px-2 py-1 rounded-full text-xs font-medium',
            trendColors[trend.direction]
          )}>
            <span className="mr-1">{trendIcons[trend.direction]}</span>
            {trend.value}%
          </span>
          <span className="text-sm text-gray-500">{trend.label}</span>
        </div>
      )}
    </div>
  )
}

// Grid layout component for multiple stats
interface CardStatGridProps {
  children: React.ReactNode
  columns?: 1 | 2 | 3 | 4
  className?: string
}

export function CardStatGrid({ children, columns = 3, className }: CardStatGridProps) {
  const gridCols = {
    1: 'grid-cols-1',
    2: 'grid-cols-1 md:grid-cols-2',
    3: 'grid-cols-1 md:grid-cols-2 lg:grid-cols-3',
    4: 'grid-cols-1 md:grid-cols-2 lg:grid-cols-4',
  }

  return (
    <div className={cn(
      'grid gap-6',
      gridCols[columns],
      className
    )}>
      {children}
    </div>
  )
}