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
 * ShannonScatterPlotChart component
 *
 * Renders a scatter plot chart using Chart.js specialized for Shannon entropy visualization.
 * Displays entropy-related data points in a scatter plot format, with configurable title and axis labels.
 *
 * @example
 * // Basic usage in a parent component template:
 * // <ShannonScatterPlotChart
 * //   :data="shannonData"
 * //   title="Shannon Entropy Scatter Plot"
 * //   xAxisLabel="Dataset Size"
 * //   yAxisLabel="Entropy Value"
 * // />
 *
 * @prop {Object} data - Chart.js data object for the Shannon scatter plot (required)
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
 */
import { ref, onMounted, watch } from 'vue';
import { Chart, registerables } from 'chart.js';
import annotationPlugin from 'chartjs-plugin-annotation';
import { chartTheme } from './../../assets/chartTheme'; // Ensure the path to your chartTheme file is correct

Chart.register(...registerables, annotationPlugin);

// Props
const props = defineProps({
  title: {
    type: String,
    default: 'Scatter Plot',
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
      return (
        value.datasets &&
        value.datasets.every((dataset) => Array.isArray(dataset.data) && dataset.data.every((point) => 'x' in point && 'y' in point))
      );
    },
  },
  showQuadrants: {
    type: Boolean,
    default: false,
  },
  quadrants: {
    type: Object,
    default: () => ({
      lowLow: 'Minimal Issues',
      lowHigh: 'High-Level Issues',
      highHigh: 'Complex Problems',
      highLow: 'Rare Cases',
    }),
  },
});

// References
const chartCanvas = ref(null);
let chartInstance = null;

// Helper to calculate axis limits
const calculateAxisLimits = () => {
  const xValues = props.data.datasets.flatMap((dataset) => dataset.data.map((point) => point.x));
  const yValues = props.data.datasets.flatMap((dataset) => dataset.data.map((point) => point.y));

  const xMin = Math.min(...xValues);
  const xMax = Math.max(...xValues);
  const yMin = Math.min(...yValues);
  const yMax = Math.max(...yValues);

  // Add padding
  const paddingFactor = 0.1;
  const xPadding = (xMax - xMin) * paddingFactor;
  const yPadding = (yMax - yMin) * paddingFactor;

  return {
    xMin: xMin - xPadding,
    xMax: xMax + xPadding,
    yMin: yMin - yPadding,
    yMax: yMax + yPadding,
    xMid: (xMin + xMax) / 2,
    yMid: (yMin + yMax) / 2,
  };
};

// Quadrant annotations
const getQuadrantAnnotations = () => {
  const { xMin, xMax, yMin, yMax, xMid, yMid } = calculateAxisLimits();

  return {
    box1: {
      type: 'box',
      xMin: xMin,
      xMax: xMid,
      yMin: yMin,
      yMax: yMid,
      backgroundColor: chartTheme.quadrantColors.lowLow.bg,
      borderColor: chartTheme.quadrantColors.lowLow.border,
      borderWidth: 1,
      label: {
        display: true,
        content: props.quadrants.lowLow,
        position: 'center',
      },
    },
    box2: {
      type: 'box',
      xMin: xMid,
      xMax: xMax,
      yMin: yMin,
      yMax: yMid,
      backgroundColor: chartTheme.quadrantColors.highLow.bg,
      borderColor: chartTheme.quadrantColors.highLow.border,
      borderWidth: 1,
      label: {
        display: true,
        content: props.quadrants.highLow,
        position: 'center',
      },
    },
    box3: {
      type: 'box',
      xMin: xMin,
      xMax: xMid,
      yMin: yMid,
      yMax: yMax,
      backgroundColor: chartTheme.quadrantColors.lowHigh.bg,
      borderColor: chartTheme.quadrantColors.lowHigh.border,
      borderWidth: 1,
      label: {
        display: true,
        content: props.quadrants.lowHigh,
        position: 'center',
      },
    },
    box4: {
      type: 'box',
      xMin: xMid,
      xMax: xMax,
      yMin: yMid,
      yMax: yMax,
      backgroundColor: chartTheme.quadrantColors.highHigh.bg,
      borderColor: chartTheme.quadrantColors.highHigh.border,
      borderWidth: 1,
      label: {
        display: true,
        content: props.quadrants.highHigh,
        position: 'center',
      },
    },
  };
};

// Create Chart Function
const createChart = () => {
  if (chartInstance) {
    chartInstance.destroy();
  }

  const ctx = chartCanvas.value.getContext('2d');
  const annotations = props.showQuadrants ? getQuadrantAnnotations() : {};

  chartInstance = new Chart(ctx, {
    type: 'scatter',
    data: props.data,
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

watch(
  () => props.showQuadrants,
  () => {
    createChart();
  },
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
  width: 100%;
}

.chart-body canvas {
  width: 100% !important;
  height: 100% !important;
}
</style>
