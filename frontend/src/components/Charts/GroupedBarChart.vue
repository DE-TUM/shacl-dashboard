<template>
    <div class="chart-container">
      <canvas ref="barChartCanvas"></canvas>
    </div>
  </template>
  
  <script setup>
/**
 * GroupedBarChart component
 *
 * Renders a grouped bar chart using Chart.js.
 * Displays multiple datasets grouped by categories, with configurable title and axis labels.
 *
 * @example
 * // Basic usage in a parent component template:
 * // <GroupedBarChart
 * //   :data="chartData"
 * //   title="Grouped Bar Chart Example"
 * //   xAxisLabel="Categories"
 * //   yAxisLabel="Values"
 * // />
 *
 * @prop {Object} data - Chart.js data object for grouped bar chart (required)
 * @prop {string} [title=''] - Title displayed above the chart
 * @prop {string} [xAxisLabel=''] - Label for the x-axis
 * @prop {string} [yAxisLabel=''] - Label for the y-axis
 *
 * @dependencies
 * - vue (Composition API)
 * - chart.js
 *
 * @style
 * - Responsive chart area with fixed height.
 * - Container for the chart with relative positioning.
 * 
 * @returns {HTMLElement} A canvas element containing the rendered grouped bar chart with
 * multiple data series displayed as adjacent bars grouped by categories.
 */
  import { onMounted, ref } from 'vue';
  import { Chart } from 'chart.js';
  
  const props = defineProps({
    title: String,
    xAxisLabel: String,
    yAxisLabel: String,
    data: Object
  });
  
  const barChartCanvas = ref(null);
  
  onMounted(() => {
    new Chart(barChartCanvas.value, {
      type: 'bar',
      data: props.data,
      options: {
        responsive: true,
        plugins: {
          title: {
            display: true,
            text: props.title
          },
          tooltip: {
            enabled: true
          }
        },
        scales: {
          x: {
            stacked: true,
            title: {
              display: true,
              text: props.xAxisLabel
            }
          },
          y: {
            stacked: true,
            title: {
              display: true,
              text: props.yAxisLabel
            }
          }
        }
      }
    });
  });
  </script>
  
  <style scoped>
  .chart-container {
    position: relative;
    height: 200px;
  }
  </style>
