/**
 * Application configuration for MyTriv ERP Frontend
 */

export const config = {
  // API Configuration
  api: {
    // Base URL for the Odoo backend API
    baseUrl: process.env.NEXT_PUBLIC_API_URL || 'http://localhost:8069',

    // API version
    version: 'v1',

    // Request timeout in milliseconds
    timeout: 30000,

    // Retry configuration
    retry: {
      attempts: 3,
      delay: 1000,
    },
  },

  // Authentication Configuration
  auth: {
    // Session cookie name
    sessionCookieName: 'session_id',

    // Token storage key (for token-based auth)
    tokenStorageKey: 'mytriv_token',

    // Auth type: 'cookie' or 'token'
    type: (process.env.NEXT_PUBLIC_AUTH_TYPE as 'cookie' | 'token') || 'cookie',

    // Login redirect path
    loginRedirect: '/dashboard',

    // Logout redirect path
    logoutRedirect: '/login',
  },

  // Mock Mode Configuration
  mock: {
    // Enable mock mode for development
    enabled: process.env.NEXT_PUBLIC_MOCK === '1',

    // Mock data delay (milliseconds)
    delay: 500,

    // Mock error rate (0-1)
    errorRate: 0,
  },

  // Pagination Configuration
  pagination: {
    // Default page size
    defaultLimit: 50,

    // Maximum page size
    maxLimit: 1000,

    // Page size options for UI
    sizeOptions: [10, 25, 50, 100, 500],
  },

  // UI Configuration
  ui: {
    // Application name
    appName: 'MyTriv ERP',

    // Company name
    companyName: 'MyTriv',

    // Default theme
    theme: 'light',

    // Animation duration
    animationDuration: 200,
  },

  // Module Configuration
  modules: {
    // Available modules and their endpoints
    hr: {
      name: 'Human Resources',
      endpoint: 'hr/employees',
      model: 'hr.employee',
      icon: 'Users',
      enabled: true,
    },
    crm: {
      name: 'Customer Relationship Management',
      endpoint: 'crm/leads',
      model: 'crm.lead',
      icon: 'Target',
      enabled: true,
    },
    sale: {
      name: 'Sales',
      endpoint: 'sale/orders',
      model: 'sale.order',
      icon: 'ShoppingCart',
      enabled: true,
    },
    project: {
      name: 'Project Management',
      endpoint: 'project/tasks',
      model: 'project.task',
      icon: 'FolderKanban',
      enabled: true,
    },
    account: {
      name: 'Accounting',
      endpoint: 'account/invoices',
      model: 'account.move',
      icon: 'Calculator',
      enabled: true,
    },
    stock: {
      name: 'Inventory',
      endpoint: 'stock/products',
      model: 'product.product',
      icon: 'Package',
      enabled: true,
    },
  },

  // Development Configuration
  development: {
    // Enable debug logging
    debug: process.env.NODE_ENV === 'development',

    // Enable error boundaries
    errorBoundaries: true,

    // Show mock mode indicator
    showMockIndicator: process.env.NEXT_PUBLIC_MOCK === '1',
  },
} as const

// Type exports for configuration
export type AppConfig = typeof config
export type ModuleConfig = typeof config.modules
export type ModuleKey = keyof typeof config.modules

/**
 * Get API base URL for making requests
 */
export function getApiBaseUrl(): string {
  return config.api.baseUrl
}

/**
 * Get full API URL for a specific endpoint
 */
export function getApiUrl(endpoint: string): string {
  const baseUrl = getApiBaseUrl()
  const cleanEndpoint = endpoint.startsWith('/') ? endpoint : `/${endpoint}`
  return `${baseUrl}/api/${config.api.version}${cleanEndpoint}`
}

/**
 * Check if a module is enabled
 */
export function isModuleEnabled(module: ModuleKey): boolean {
  return config.modules[module]?.enabled ?? false
}

/**
 * Get module configuration
 */
export function getModuleConfig(module: ModuleKey) {
  return config.modules[module]
}

/**
 * Check if mock mode is enabled
 */
export function isMockMode(): boolean {
  return config.mock.enabled
}

/**
 * Get all enabled modules
 */
export function getEnabledModules(): Array<{ key: ModuleKey; config: NonNullable<typeof config.modules[ModuleKey]> }> {
  return Object.entries(config.modules)
    .filter(([_, moduleConfig]) => moduleConfig.enabled)
    .map(([key, moduleConfig]) => ({
      key: key as ModuleKey,
      config: moduleConfig,
    }))
}