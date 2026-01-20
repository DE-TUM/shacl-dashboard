/**
 * UI Constants
 * 
 * Centralized configuration for UI-related magic numbers.
 * This ensures consistency across the application and makes it easier to adjust values.
 * 
 * @module constants/ui
 */

/**
 * Sidebar dimension constants
 */
export const SIDEBAR = {
  /** Width when sidebar is collapsed (px) */
  COLLAPSED: 60,
  /** Width when sidebar is expanded (px) */
  EXPANDED: 250
};

/**
 * Pagination constants
 */
export const PAGINATION = {
  /** Default number of items per page */
  DEFAULT_PAGE_SIZE: 10,
  /** Page size options for user selection */
  PAGE_SIZE_OPTIONS: [5, 10, 20, 50, 100]
};

/**
 * Responsive breakpoint constants (px)
 */
export const BREAKPOINTS = {
  /** Mobile breakpoint */
  MOBILE: 600,
  /** Tablet breakpoint */
  TABLET: 768,
  /** Desktop breakpoint */
  DESKTOP: 1024,
  /** Large desktop breakpoint */
  LARGE_DESKTOP: 1440
};

/**
 * Layout constants
 */
export const LAYOUT = {
  /** Top app bar height (px) */
  APP_BAR_HEIGHT: 64,
  /** Standard spacing unit (px) */
  SPACING_UNIT: 8,
  /** Card padding (px) */
  CARD_PADDING: 16
};

/**
 * Chart constants
 */
export const CHART = {
  /** Default chart height (px) */
  DEFAULT_HEIGHT: 400,
  /** Minimum chart height (px) */
  MIN_HEIGHT: 200,
  /** Animation duration (ms) */
  ANIMATION_DURATION: 750
};
