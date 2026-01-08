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
 * PieChart component
 *
 * Renders a pie chart using Chart.js.
 * Displays data as proportional segments of a circle, with configurable title.
 *
 * @example
 * // Basic usage in a parent component template:
 * // <PieChart
 * //   :data="pieData"
 * //   title="Pie Chart Example"
 * // />
 *
 * @prop {Object} data - Chart.js data object for the pie chart (required)
 * @prop {string} [title=''] - Title displayed above the chart
 *
 * @dependencies
 * - vue (Composition API)
 * - chart.js
 *
 * @style
 * - Responsive chart area with fixed height.
 * - Container for the chart with relative positioning.
 */
import { ref, watch, onMounted, onBeforeUnmount, nextTick } from 'vue';
import { Chart } from 'chart.js/auto';
import { chartTheme } from './../../assets/chartTheme'; // Import the chart theme

// Define the props
const props = defineProps({
  data: {
    type: Array,
    required: true,
    validator: (value) => Array.isArray(value) && value.every((item) => typeof item === 'number'),
  },
  title: {
    type: String,
    default: 'Pie Chart',
  },
  categories: {
    type: Array,
    required: true,
    validator: (value) =>
      Array.isArray(value) && value.every((item) => typeof item === 'string' && item.trim().length > 0),
  },
});

// Reference for the chart canvas element
const chartCanvas = ref(null);
let chart = null;

// Function to process the input data and return chart dataset
const processData = (rawData, categoryNames) => {
  const numCategories = categoryNames.length;
  const dataLength = rawData.length;
  const categoryCount = Math.min(numCategories, dataLength);

  const sortedData = [...rawData].sort((a, b) => b - a);
  const top7Data = sortedData.slice(0, 7);
  const othersData = sortedData.slice(7);

  const othersSum = othersData.reduce((sum, value) => sum + value, 0);

  const individualLabels = categoryNames.slice(0, 7);
  const othersLabel = ['Others'];

  return {
    individualData: top7Data,
    othersData: othersSum,
    individualLabels,
    othersLabel,
  };
};

// Function to create the chart
const createChart = () => {
  const ctx = chartCanvas.value.getContext('2d');

  const { individualData, othersData, individualLabels, othersLabel } = processData(props.data, props.categories);

  const themeColors = [
    chartTheme.colors.primary,
    chartTheme.colors.secondary,
    chartTheme.colors.accent,
    chartTheme.colors.neutral,
    'rgba(102, 187, 106, 0.6)', // Additional color for overflow
    'rgba(63, 81, 181, 0.6)',  // Additional color
    'rgba(255, 193, 7, 0.6)',  // Additional color
    'rgba(244, 67, 54, 0.6)',  // Additional color
  ];

  chart = new Chart(ctx, {
    type: 'pie',
    data: {
      labels: [...individualLabels, ...othersLabel],
      datasets: [
        {
          label: props.title,
          data: [...individualData, othersData],
          backgroundColor: themeColors.slice(0, individualLabels.length + 1), // Use theme colors
          borderColor: 'rgba(255, 255, 255, 1)',
          borderWidth: 2,
        },
      ],
    },
    options: {
      responsive: true,
      maintainAspectRatio: false,
      layout: {
        padding: {
          top: 30,
          right: 50,
          bottom: 10,
          left: 10,
        },
      },
      plugins: {
        legend: {
          display: true,
          position: 'right', // Move the legend to the right side
          labels: {
            boxWidth: 20,
            padding: 10,
          },
        },
      },
    },
  });
};

// Function to update the chart when props change
const updateChart = () => {
  if (chart) {
    const { individualData, othersData, individualLabels, othersLabel } = processData(props.data, props.categories);

    chart.data.datasets[0].data = [...individualData, othersData];
    chart.data.labels = [...individualLabels, ...othersLabel];
    chart.options.plugins.title.text = props.title;
    chart.update();
  }
};

// Watch for changes in props and update chart accordingly
watch(() => props.data, updateChart);
watch(() => props.title, updateChart);
watch(() => props.categories, updateChart);

// Lifecycle hooks
onMounted(() => {
  nextTick(() => {
    createChart();
  });

  window.addEventListener('resize', handleResize);
});

const handleResize = () => {
  if (chart) {
    chart.resize();
  }
};

onBeforeUnmount(() => {
  if (chart) {
    chart.destroy();
  }

  window.removeEventListener('resize', handleResize);
});

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
