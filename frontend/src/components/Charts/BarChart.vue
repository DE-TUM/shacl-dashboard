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
