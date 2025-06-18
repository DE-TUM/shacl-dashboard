/**
 * Chart Theme Configuration
 * 
 * Provides consistent theming for all charts in the application.
 * Extracts colors from CSS variables to ensure design system consistency.
 * 
 * @module chartTheme
 * 
 * @property {Object} colors - Main color palette for charts
 * @property {string} colors.primary - Primary color (True Blue)
 * @property {string} colors.secondary - Secondary color (Sapphire)
 * @property {string} colors.accent - Accent color (Yale Blue)
 * @property {string} colors.neutral - Neutral color (Cool Gray)
 * 
 * @property {Object} defaults - Default styling values for charts
 * @property {string} defaults.textColor - Default text color (Payne's Gray)
 * @property {string} defaults.gridlineColor - Color for grid lines (Cool Gray)
 * @property {string} defaults.legendColor - Color for legends (Oxford Blue 3)
 * @property {Object} defaults.fontSizes - Font size configuration for different elements
 * 
 * @property {Object} quadrantColors - Color scheme for quadrant-based visualizations
 * @property {Object} quadrantColors.lowLow - Colors for low-low quadrant (green)
 * @property {Object} quadrantColors.highLow - Colors for high-low quadrant (blue)
 * @property {Object} quadrantColors.lowHigh - Colors for low-high quadrant (yellow)
 * @property {Object} quadrantColors.highHigh - Colors for high-high quadrant (red)
 * 
 * @returns {Object} A configuration object containing standardized colors, sizes,
 * and settings for application charts, ensuring visual consistency across all data
 * visualizations by using values from the application's CSS variables.
 */
const rootStyles = getComputedStyle(document.documentElement);

export const chartTheme = {
  colors: {
    primary: rootStyles.getPropertyValue('--true-blue').trim(), // Primary color: True Blue
    secondary: rootStyles.getPropertyValue('--sapphire').trim(), // Secondary color: Sapphire
    accent: rootStyles.getPropertyValue('--yale-blue').trim(), // Accent color: Yale Blue
    neutral: rootStyles.getPropertyValue('--cool-gray').trim(), // Neutral color: Cool Gray
  },
  defaults: {
    textColor: rootStyles.getPropertyValue('--paynes-gray').trim(), // Text color: Payne's Gray
    gridlineColor: rootStyles.getPropertyValue('--cool-gray').trim(), // Gridline color: Slate Gray
    legendColor: rootStyles.getPropertyValue('--oxford-blue-3').trim(), // Legend color: Oxford Blue 3
    fontSizes: {
      legend: 12,
      tooltipTitle: 14,
      tooltipBody: 12,
      axisTitle: 14,
      ticks: 12,
    },
  },
  quadrantColors: {
    lowLow: { bg: 'rgba(102, 187, 106, 0.2)', border: 'rgba(102, 187, 106, 1)' },
    highLow: { bg: 'rgba(63, 81, 181, 0.2)', border: 'rgba(63, 81, 181, 1)' },
    lowHigh: { bg: 'rgba(255, 193, 7, 0.2)', border: 'rgba(255, 193, 7, 1)' },
    highHigh: { bg: 'rgba(244, 67, 54, 0.2)', border: 'rgba(244, 67, 54, 1)' },
  },
};
