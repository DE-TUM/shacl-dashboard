/**
 * Application Constants
 * 
 * Centralized constants for magic numbers, configuration values,
 * and application-wide settings.
 * 
 * @module constants
 */

/**
 * Sidebar configuration
 */
export const SIDEBAR = {
  COLLAPSED_WIDTH: 60,
  EXPANDED_WIDTH: 250,
  TRANSITION_DURATION: '0.3s'
};

/**
 * Pagination defaults
 */
export const PAGINATION = {
  DEFAULT_PAGE_SIZE: 10,
  DEFAULT_CURRENT_PAGE: 1,
  PAGE_SIZE_OPTIONS: [5, 10, 25, 50, 100]
};

/**
 * Table configuration
 */
export const TABLE = {
  MIN_COLUMN_WIDTH: 100,
  MAX_COLUMN_WIDTH: 500,
  DEFAULT_SORT_ORDER: 'asc'
};

/**
 * Chart dimensions
 */
export const CHART = {
  DEFAULT_HEIGHT: 400,
  DEFAULT_WIDTH: 600,
  MIN_HEIGHT: 200,
  MAX_HEIGHT: 800
};

/**
 * API configuration
 */
export const API = {
  TIMEOUT: 30000, // 30 seconds
  RETRY_ATTEMPTS: 3,
  RETRY_DELAY: 1000 // 1 second
};

/**
 * Data export settings
 */
export const EXPORT = {
  CSV_DELIMITER: ',',
  CSV_ARRAY_SEPARATOR: '; ',
  DEFAULT_CSV_FILENAME: 'export.csv',
  DEFAULT_JSON_FILENAME: 'export.json'
};

/**
 * UI timing
 */
export const TIMING = {
  DEBOUNCE_DELAY: 300,
  TOOLTIP_DELAY: 500,
  NOTIFICATION_DURATION: 3000,
  ANIMATION_DURATION: 200
};

/**
 * Color scheme (can be used before CSS variables are implemented)
 */
export const COLORS = {
  PRIMARY: '#3b82f6',
  SECONDARY: '#6b7280',
  SUCCESS: '#10b981',
  WARNING: '#f59e0b',
  ERROR: '#ef4444',
  INFO: '#3b82f6'
};

/**
 * Validation limits
 */
export const VALIDATION = {
  MAX_SEARCH_LENGTH: 200,
  MIN_PASSWORD_LENGTH: 8,
  MAX_FILE_SIZE: 10 * 1024 * 1024, // 10MB
  ALLOWED_FILE_TYPES: ['csv', 'json', 'xml', 'ttl']
};

/**
 * Local storage keys
 */
export const STORAGE_KEYS = {
  USER_PREFERENCES: 'shacl_user_preferences',
  THEME: 'shacl_theme',
  LAST_VIEW: 'shacl_last_view',
  PREFIXES: 'shacl_prefixes'
};

/**
 * Route names (for type-safe routing)
 */
export const ROUTES = {
  HOME: 'Home',
  SHAPES: 'ShapeOverview',
  SHAPE_DETAIL: 'ShapeView',
  CONSTRAINTS: 'ConstraintOverview',
  CONSTRAINT_DETAIL: 'ConstraintView',
  FOCUS_NODES: 'FocusNodeOverview',
  FOCUS_NODE_DETAIL: 'FocusNodeView',
  PROPERTY_PATHS: 'PropertyPathOverview',
  PROPERTY_PATH_DETAIL: 'PropertyPathView',
  ABOUT: 'AboutUs'
};

export default {
  SIDEBAR,
  PAGINATION,
  TABLE,
  CHART,
  API,
  EXPORT,
  TIMING,
  COLORS,
  VALIDATION,
  STORAGE_KEYS,
  ROUTES
};
