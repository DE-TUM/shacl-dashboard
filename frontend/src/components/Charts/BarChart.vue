<template>
  <div class="chart-card">
    <div class="chart-header">
      <h3>{{ title }}</h3>
    </div>
    <div class="chart-body">
      <canvas ref="chartCanvas"></canvas>
    </div>
  </div>
</template>

<script setup>
/**
 * BarChart component.
 *
 * Renders a customizable bar chart using Chart.js, with configurable title, axis labels, and data.
 * Applies a theme from the local chartTheme asset.
 *
 * @component
 * @example
 * // Basic usage in a parent component template:
 * // <BarChart
 * //   :data="{
 * //     labels: ['A', 'B', 'C'],
 * //     datasets: [{ label: 'My Data', data: [10, 20, 30] }]
 * //   }"
 * //   title="My Bar Chart"
 * //   xAxisLabel="Categories"
 * //   yAxisLabel="Values"
 * // />
 *
 * @prop {Object} data - Chart.js data object with `labels` (array) and `datasets` (array) (required)
 * @prop {string} [title='Bar Chart'] - Title displayed above the chart
 * @prop {string} [xAxisLabel='X Axis'] - Label for the x-axis
 * @prop {string} [yAxisLabel='Y Axis'] - Label for the y-axis
 *
 * @dependencies
 * - vue (Composition API)
 * - chart.js
 * - chartTheme (local asset)
 *
 * @style
 * - Card-style container with subtle shadow and rounded corners.
 * - Responsive chart area with fixed height.
 */

import { ref, onMounted, watch } from 'vue';
import { Chart } from 'chart.js';
import { chartTheme } from './../../assets/chartTheme'; // Ensure the path to your chartTheme file is correct

// Props
const props = defineProps({
  title: {
    type: String,
    default: 'Bar Chart',
  },
  xAxisLabel: {
    type: String,
    default: 'X Axis',
  },
  yAxisLabel: {
    type: String,
    default: 'Y Axis',
  },
  data: {
    type: Object,
    required: true,
    validator(value) {
      return value.labels && value.datasets;
    },
  },
});

// References
const chartCanvas = ref(null);
let chartInstance = null;

// Create Chart Function
const createChart = () => {
  if (chartInstance) {
    chartInstance.destroy();
  }

  const ctx = chartCanvas.value.getContext('2d');
  const annotations = props.showQuadrants ? getQuadrantAnnotations() : {};

  chartInstance = new Chart(ctx, {
    type: 'bar', // Change this to 'bar' if it's a bar chart
    data: {
      ...props.data,
      datasets: props.data.datasets.map((dataset) => ({
        ...dataset,
        backgroundColor: chartTheme.colors.primary, // Bar fill color
        borderColor: chartTheme.colors.secondary, // Bar border color
        borderWidth: 1,
      })),
    },
    options: {
      responsive: true,
      maintainAspectRatio: false,
      plugins: {
        legend: {
          display: true,
          position: 'top',
          labels: {
            color: chartTheme.defaults.legendColor,
            font: {
              size: chartTheme.defaults.fontSizes.legend,
            },
          },
        },
        tooltip: {
          backgroundColor: '#ffffff',
          titleColor: chartTheme.defaults.textColor,
          bodyColor: chartTheme.defaults.textColor,
          borderColor: chartTheme.defaults.gridlineColor,
          borderWidth: 1,
          titleFont: {
            size: chartTheme.defaults.fontSizes.tooltipTitle,
            weight: 'bold',
          },
          bodyFont: {
            size: chartTheme.defaults.fontSizes.tooltipBody,
          },
        },
        annotation: {
          annotations: annotations,
        },
      },
      scales: {
        x: {
          title: {
            display: true,
            text: props.xAxisLabel,
            color: chartTheme.defaults.textColor,
            font: {
              size: chartTheme.defaults.fontSizes.axisTitle,
              weight: 'bold',
            },
          },
          ticks: {
            color: chartTheme.defaults.textColor,
            font: {
              size: chartTheme.defaults.fontSizes.ticks,
            },
          },
        },
        y: {
          title: {
            display: true,
            text: props.yAxisLabel,
            color: chartTheme.defaults.textColor,
            font: {
              size: chartTheme.defaults.fontSizes.axisTitle,
              weight: 'bold',
            },
          },
          ticks: {
            color: chartTheme.defaults.textColor,
            font: {
              size: chartTheme.defaults.fontSizes.ticks,
            },
          },
        },
      },
    },
  });
};

// Lifecycle Hooks
onMounted(() => {
  createChart();
});

watch(
  () => props.data,
  () => {
    createChart();
  },
  { deep: true }
);
</script>

<style scoped>
.chart-card {
  background: #ffffff;
  border: 1px solid #e6e6e6;
  border-radius: 8px;
  padding: 24px;
  transition: box-shadow 0.2s ease;
  box-shadow: 0 2px 8px rgba(0, 0, 0, 0.05);
}

.chart-card:hover {
  box-shadow: 0 4px 16px rgba(0, 0, 0, 0.1);
}

.chart-header h3 {
  margin: 0 0 16px;
  font-size: 18px;
  font-weight: 600;
  color: #222;
}

.chart-body {
  position: relative;
  height: 300px; /* Increased height for a cleaner appearance */
}

.chart-body canvas {
  max-height: 100%;
}
</style>
