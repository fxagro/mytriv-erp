/**
 * Spinner Component
 *
 * Displays a loading spinner with customizable size and appearance.
 */

import React from 'react'
import { cn } from '@/lib/utils'

interface SpinnerProps {
  size?: 'sm' | 'md' | 'lg' | 'xl'
  className?: string
  color?: 'primary' | 'secondary' | 'white'
}

const sizeClasses = {
  sm: 'w-4 h-4',
  md: 'w-6 h-6',
  lg: 'w-8 h-8',
  xl: 'w-12 h-12',
}

const colorClasses = {
  primary: 'text-blue-600',
  secondary: 'text-gray-600',
  white: 'text-white',
}

export function Spinner({ size = 'md', className, color = 'primary' }: SpinnerProps) {
  return (
    <div
      className={cn(
        'animate-spin rounded-full border-2 border-gray-300 border-t-current',
        sizeClasses[size],
        colorClasses[color],
        className
      )}
      role="status"
      aria-label="Loading"
    >
      <span className="sr-only">Loading...</span>
    </div>
  )
}

// Full page spinner component
interface PageSpinnerProps {
  message?: string
  className?: string
}

export function PageSpinner({ message = 'Loading...', className }: PageSpinnerProps) {
  return (
    <div className={cn(
      'flex flex-col items-center justify-center min-h-[200px] space-y-4',
      className
    )}>
      <Spinner size="lg" />
      <p className="text-sm text-gray-600">{message}</p>
    </div>
  )
}

// Inline spinner for buttons and small spaces
interface InlineSpinnerProps {
  message?: string
  className?: string
}

export function InlineSpinner({ message, className }: InlineSpinnerProps) {
  return (
    <div className={cn(
      'flex items-center space-x-2',
      className
    )}>
      <Spinner size="sm" />
      {message && <span className="text-sm text-gray-600">{message}</span>}
    </div>
  )
}