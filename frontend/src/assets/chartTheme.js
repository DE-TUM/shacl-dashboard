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
