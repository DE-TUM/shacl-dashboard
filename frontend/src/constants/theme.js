/**
 * Theme Constants
 * 
 * Centralized color palette and theme configuration.
 * These should be synchronized with CSS variables in the main stylesheet.
 * 
 * @module constants/theme
 */

/**
 * Primary color palette
 */
export const COLORS = {
  /** Primary brand color (orange) */
  PRIMARY: 'rgb(227, 114, 34)',
  PRIMARY_HEX: '#E37222',
  
  /** Gray scale */
  GRAY_50: '#f9fafb',
  GRAY_100: '#f3f4f6',
  GRAY_200: '#e5e7eb',
  GRAY_300: '#d1d5db',
  GRAY_400: '#9ca3af',
  GRAY_500: '#6b7280',
  GRAY_600: '#4b5563',
  GRAY_700: '#374151',
  GRAY_800: '#1f2937',
  GRAY_900: '#111827',
  
  /** Semantic colors */
  SUCCESS: '#10b981',
  WARNING: '#f59e0b',
  ERROR: '#ef4444',
  INFO: '#3b82f6',
  
  /** Background colors */
  BACKGROUND_LIGHT: '#ffffff',
  BACKGROUND_GRAY: '#efefef',
  BACKGROUND_BLUE: '#f0f8ff',
  
  /** Text colors */
  TEXT_PRIMARY: '#111827',
  TEXT_SECONDARY: '#6b7280',
  TEXT_TERTIARY: '#9ca3af',
  
  /** Border colors */
  BORDER_LIGHT: '#e5e7eb',
  BORDER_DEFAULT: '#d1d5db',
  BORDER_DARK: '#9ca3af',
  
  /** Component-specific */
  LINK: '#007bff',
  TAG_BACKGROUND: '#f9f9f9',
  TAG_BORDER: '#e0e0e0',
  TAG_BLUE: '#1976D2'
};

/**
 * CSS Custom Properties
 * Use these in inline styles when needed
 */
export const CSS_VARS = {
  '--color-primary': COLORS.PRIMARY,
  '--color-gray-50': COLORS.GRAY_50,
  '--color-gray-100': COLORS.GRAY_100,
  '--color-gray-200': COLORS.GRAY_200,
  '--color-gray-300': COLORS.GRAY_300,
  '--color-gray-400': COLORS.GRAY_400,
  '--color-gray-500': COLORS.GRAY_500,
  '--color-gray-600': COLORS.GRAY_600,
  '--color-gray-700': COLORS.GRAY_700,
  '--color-gray-800': COLORS.GRAY_800,
  '--color-gray-900': COLORS.GRAY_900,
  '--color-success': COLORS.SUCCESS,
  '--color-warning': COLORS.WARNING,
  '--color-error': COLORS.ERROR,
  '--color-info': COLORS.INFO,
  '--color-background-light': COLORS.BACKGROUND_LIGHT,
  '--color-background-gray': COLORS.BACKGROUND_GRAY,
  '--color-background-blue': COLORS.BACKGROUND_BLUE,
  '--color-text-primary': COLORS.TEXT_PRIMARY,
  '--color-text-secondary': COLORS.TEXT_SECONDARY,
  '--color-border': COLORS.BORDER_DEFAULT
};

/**
 * Z-index layers
 */
export const Z_INDEX = {
  DROPDOWN: 1000,
  STICKY: 1020,
  FIXED: 1030,
  MODAL_BACKDROP: 1040,
  MODAL: 1050,
  POPOVER: 1060,
  TOOLTIP: 1070
};
