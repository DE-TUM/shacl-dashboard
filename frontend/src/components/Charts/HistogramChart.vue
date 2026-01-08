<template>
  <div class="chart-card ">
    <div class="chart-header flex justify-between items-center">
      <h3 class="inline-flex items-center gap-2" v-html="title"></h3>
      <ToggleQuestionMark :explanation="explanationText" />
    </div>
    <div class="chart-body w-full ">
      <canvas ref="histogramCanvas"></canvas>
    </div>
  </div>
</template>

<script setup>
/**
 * HistogramChart component
 *
 * Renders a histogram chart using Chart.js.
 * Displays the distribution of a dataset as bars, with configurable title and axis labels.
 *
 * @example
 * // Basic usage in a parent component template:
 * // <HistogramChart
 * //   :data="histogramData"
 * //   title="Histogram Example"
 * //   xAxisLabel="Bins"
 * //   yAxisLabel="Frequency"
 * // />
 *
 * @prop {Object} data - Chart.js data object for the histogram (required)
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
import { onMounted, ref } from 'vue';
import { Chart } from 'chart.js';
import { chartTheme } from './../../assets/chartTheme'; // Ensure the path to your chartTheme file is correct
import ToggleQuestionMark from "../Reusable/ToggleQuestionMark.vue";

const props = defineProps({
  title: {
    type: String,
    default: 'Histogram',
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

const histogramCanvas = ref(null);

onMounted(() => {
  // Apply global defaults for Chart.js using chartTheme
  Chart.defaults.color = chartTheme.defaults.textColor;
  Chart.defaults.borderColor = chartTheme.defaults.gridlineColor;
  Chart.defaults.plugins.legend.labels.color = chartTheme.defaults.legendColor;

  new Chart(histogramCanvas.value, {
    type: 'bar',
    data: {
      ...props.data,
      datasets: props.data.datasets.map((dataset) => ({
        ...dataset,
        backgroundColor: dataset.backgroundColor || chartTheme.colors.primary, 
        borderColor: dataset.borderColor || chartTheme.colors.secondary,
        borderWidth: 1, // Border width
      })),
    },
    options: {
      responsive: true,
      maintainAspectRatio: false,
      plugins: {
        legend: {
          display: true,
          labels: {
            color: chartTheme.defaults.legendColor,
            font: {
              size: chartTheme.defaults.fontSizes.title,
            },
          },
        },
        tooltip: {
          enabled: true,
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
      },
      scales: {
        x: {
          grid: {
            display: false,
          },
          title: {
            display: true,
            text: props.xAxisLabel,
            color: chartTheme.defaults.textColor,
            font: {
              size: chartTheme.defaults.fontSizes.axisTitle,
              weight: '600',
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
          grid: {
            color: chartTheme.defaults.gridlineColor,
            drawBorder: false,
          },
          title: {
            display: true,
            text: props.yAxisLabel,
            color: chartTheme.defaults.textColor,
            font: {
              size: chartTheme.defaults.fontSizes.axisTitle,
              weight: '600',
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
});
</script>

<style scoped>
.chart-card {
  background: #ffffff;
  border: 1px solid #e6e6e6;
  border-radius: 8px;
  padding: 24px;
  transition: box-shadow 0.2s ease, transform 0.2s ease;
  box-shadow: 0 2px 8px rgba(0, 0, 0, 0.05);
}

.chart-card:hover {
  box-shadow: 0 4px 16px rgba(0, 0, 0, 0.1);
  /* transform: translateY(-2px); */
}

.chart-header h3 {
  margin: 0 0 16px;
  font-size: 18px; /* Consistent font size */
  font-weight: 600; /* Bold font weight for emphasis */
  color: #222222; /* Darker color for better contrast */
  line-height: 1.4; /* Better readability */
}

.chart-body {
  position: relative;
  height: 300px; /* Ensure sufficient height for the chart */
}

.chart-body canvas {
  max-height: 100%; /* Prevent canvas from exceeding container */
}
</style>
