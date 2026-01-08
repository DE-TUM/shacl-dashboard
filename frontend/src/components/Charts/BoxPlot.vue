<template>
  <div class="chart-card">
    <div class="chart-header">
      <h3>{{ title }}</h3>
    </div>
    <div class="chart-container">
      <canvas ref="chartCanvas"></canvas>
    </div>
  </div>
</template>

<script setup>
/**
 * BoxPlot component
 *
 * Renders a box plot (box-and-whisker plot) using Chart.js.
 * Displays statistical distribution of data with quartiles, median, and outliers.
 *
 * @example
 * // Basic usage in a parent component template:
 * // <BoxPlot
 * //   :title="'Distribution of Scores'"
 * //   :xAxisLabel="'Categories'"
 * //   :yAxisLabel="'Scores'"
 * //   :data="[10, 20, 25, 30, 40, 50, 60]"
 * // />
 *
 * @prop {String} title - Title for the chart
 * @prop {String} xAxisLabel - Label for the x-axis
 * @prop {String} yAxisLabel - Label for the y-axis
 * @prop {Array} data - Array of numerical values to be visualized
 *
 * @dependencies
 * - vue (Composition API)
 * - chart.js
 * - chartjs-chart-box-and-violin-plot
 *
 * @style
 * - Responsive chart container
 * - Statistical visualization with quartile boxes and whiskers
 * - Outlier detection and display
 * 
 * @returns {HTMLElement} A canvas element containing the rendered box plot showing
 * data distribution with a box representing quartiles, a line for the median,
 * whiskers extending to minimum and maximum values, and dots for outliers.
 */
import { ref, watch, onMounted, onBeforeUnmount } from 'vue';
import { Chart } from 'chart.js/auto';
import { BoxPlotController, BoxAndWiskers } from '@sgratzl/chartjs-chart-boxplot';

// Register the necessary components from the BoxPlot plugin
Chart.register(BoxPlotController, BoxAndWiskers);

// Props
const props = defineProps({
  data: {
    type: Array,
    required: true,
    validator: (value) => Array.isArray(value) && value.every((item) => typeof item === 'number'),
  },
  title: {
    type: String,
    default: 'Boxplot',
  },
  xAxisLabel: {
    type: String,
    default: 'Categories',
  },
  yAxisLabel: {
    type: String,
    default: 'Values',
  },
});

const chartCanvas = ref(null);
let chart = null;

// Function to calculate boxplot statistics
const calculateStatistics = (data) => {
  const sortedData = [...data].sort((a, b) => a - b);
  const n = sortedData.length;
  const q1 = sortedData[Math.floor(n * 0.25)];
  const median = sortedData[Math.floor(n * 0.5)];
  const q3 = sortedData[Math.floor(n * 0.75)];
  const iqr = q3 - q1;
  const lowerWhisker = Math.max(...sortedData.filter((x) => x >= q1 - 1.5 * iqr));
  const upperWhisker = Math.min(...sortedData.filter((x) => x <= q3 + 1.5 * iqr));
  const outliers = sortedData.filter((x) => x < lowerWhisker || x > upperWhisker);

  return {
    min: lowerWhisker,
    q1,
    median,
    q3,
    max: upperWhisker,
    outliers,
  };
};

// Process data for the chart
const processData = (rawData) => {
  const stats = calculateStatistics(rawData);
  return [
    {
      label: props.title,
      data: [stats],
      backgroundColor: 'rgba(33, 150, 243, 0.2)', // Light blue fill
      borderColor: 'rgba(33, 150, 243, 1)', // Blue border
      borderWidth: 1.5,
      outlierColor: '#FF5252', // Red for outliers
      medianColor: '#FF9800', // Orange median line
      padding: 10,
    },
  ];
};

// Create the chart
const createChart = () => {
  const ctx = chartCanvas.value.getContext('2d');
  const minValue = Math.min(...props.data);
  const maxValue = Math.max(...props.data);
  const range = maxValue - minValue;
  const padding = range > 0 ? range * 0.05 : 1;

  chart = new Chart(ctx, {
    type: 'boxplot',
    data: {
      labels: [''], // No categories for single boxplot
      datasets: processData(props.data),
    },
    options: {
      responsive: true,
      maintainAspectRatio: false,  // Allow chart to stretch to the container size
      plugins: {
        legend: {
          display: false,
        },
        tooltip: {
          backgroundColor: '#fff',
          borderColor: '#ddd',
          borderWidth: 1,
          titleColor: '#333',
          bodyColor: '#555',
        },
        title: {
          display: false, // Already displayed in the card header
        },
      },
      scales: {
        x: {
          grid: {
            drawBorder: false,
            drawOnChartArea: false,
          },
          title: {
            display: true,
            text: props.xAxisLabel,
            color: '#555',
            font: {
              size: 14,
              weight: 'bold',
            },
          },
          ticks: {
            color: '#333',
          },
        },
        y: {
          grid: {
            color: '#eee', // Subtle gridlines
            drawBorder: false,
          },
          title: {
            display: true,
            text: props.yAxisLabel,
            color: '#555',
            font: {
              size: 14,
              weight: 'bold',
            },
          },
          ticks: {
            color: '#333',
          },
          beginAtZero: true,
          min: minValue - padding,
          max: maxValue + padding,
        },
      },
    },
  });
};

// Update chart when props change
const updateChart = () => {
  if (chart) {
    chart.data.datasets = processData(props.data);
    chart.options.scales.x.title.text = props.xAxisLabel;
    chart.options.scales.y.title.text = props.yAxisLabel;
    chart.update();
  }
};

// Watchers
watch(() => props.data, updateChart);
watch(() => props.xAxisLabel, updateChart);
watch(() => props.yAxisLabel, updateChart);

// Lifecycle hooks
onMounted(() => createChart());
onBeforeUnmount(() => chart && chart.destroy());
</script>

<style scoped>
.chart-card {
  background: #ffffff;
  border: 1px solid #e6e6e6;
  border-radius: 10px;
  padding: 20px;
  transition: box-shadow 0.3s ease;
  box-shadow: 0 2px 8px rgba(0, 0, 0, 0.05);
  font-family: 'Inter', sans-serif;
}

.chart-card:hover {
  box-shadow: 0 4px 20px rgba(0, 0, 0, 0.1);
}

.chart-header h3 {
  margin: 0;
  font-size: 20px;
  font-weight: 600;
  color: #333;
}

.chart-container {
  height: 300px; /* Set fixed height for chart */
}

.chart-container canvas {
  width: 100% !important;
  height: 100% !important; /* Ensure canvas takes full height */
}

</style>
