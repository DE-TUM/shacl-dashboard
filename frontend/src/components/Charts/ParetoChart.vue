<template>
  <div class="chart-card">
    <div class="chart-header flex justify-between items-center">
      <h3 class="inline-flex items-center gap-2">
        {{ title }}
      </h3>
      <ToggleQuestionMark :explanation="explanationText" />
    </div>
    <div class="chart-container">
      <canvas ref="chartCanvas"></canvas>
    </div>
  </div>
</template>

<script setup>
/**
 * ParetoChart component
 *
 * Renders a Pareto chart using Chart.js.
 * Displays data in descending order of magnitude with a cumulative percentage line, with configurable title and axis labels.
 *
 * @example
 * // Basic usage in a parent component template:
 * // <ParetoChart
 * //   :data="paretoData"
 * //   title="Pareto Chart Example"
 * //   xAxisLabel="Categories"
 * //   yAxisLabel="Frequency"
 * // />
 *
 * @prop {Object} data - Chart.js data object for the Pareto chart (required)
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
import { ref, onMounted, watch } from "vue";
import { Chart, registerables } from "chart.js";
import { chartTheme } from "./../../assets/chartTheme"; // Ensure the path is correct
import ToggleQuestionMark from "../Reusable/ToggleQuestionMark.vue";

Chart.register(...registerables);

const props = defineProps({
  data: {
    type: Object,
    required: true,
  },
  title: {
    type: String,
    default: "Pareto Chart",
  },
});

const chartCanvas = ref(null);
let chartInstance = null;

const createParetoChart = () => {
  if (chartInstance) {
    chartInstance.destroy();
  }

  const cumulativeData = props.data.values
    .reduce((acc, value) => {
      acc.push(acc[acc.length - 1] + value);
      return acc;
    }, [0])
    .slice(1);

    const barData = {
  labels: props.data.labels,
  datasets: [
    {
      label: "Violations",
      data: props.data.values,
      type: "bar",
      backgroundColor: chartTheme.colors.primary,
      yAxisID: "y",
      borderRadius: 4,
      order: 2, // Render the bar dataset first (behind the line)
    },
    {
      label: "Cumulative Percentage",
      data: cumulativeData.map(
        (value) => (value / cumulativeData[cumulativeData.length - 1]) * 100
      ),
      type: "line",
      borderColor: chartTheme.colors.accent,
      borderWidth: 2,
      fill: true,
      yAxisID: "y1",
      tension: 0.4,
      order: 1, // Render the line dataset second (on top of the bars)
    },
  ],
};


  chartInstance = new Chart(chartCanvas.value, {
    type: "bar",
    data: barData,
    options: {
      responsive: true,
      maintainAspectRatio: false,  // Allow the chart to resize with the container
      scales: {
        y: {
          beginAtZero: true,
          position: "left",
          title: {
            display: true,
            text: "Violations",
            font: {
              size: chartTheme.defaults.fontSizes.axisTitle,
              weight: "500",
            },
            color: chartTheme.defaults.textColor,
          },
          grid: {
            color: chartTheme.defaults.gridlineColor,
          },
          ticks: {
            color: chartTheme.defaults.textColor,
            font: {
              size: chartTheme.defaults.fontSizes.ticks,
            },
          },
        },
        y1: {
          beginAtZero: true,
          position: "right",
          title: {
            display: true,
            text: "Cumulative Percentage",
            font: {
              size: chartTheme.defaults.fontSizes.axisTitle,
              weight: "500",
            },
            color: chartTheme.defaults.textColor,
          },
          grid: {
            drawOnChartArea: false,
          },
          ticks: {
            color: chartTheme.defaults.textColor,
            font: {
              size: chartTheme.defaults.fontSizes.ticks,
            },
          },
        },
      },
      plugins: {
        tooltip: {
          callbacks: {
            label: (context) =>
              context.dataset.type === "line"
                ? `${context.raw.toFixed(2)}%`
                : `Violations: ${context.raw}`,
          },
          backgroundColor: "#fff",
          borderColor: chartTheme.defaults.gridlineColor,
          borderWidth: 1,
          titleColor: chartTheme.defaults.textColor,
          bodyColor: chartTheme.defaults.textColor,
          displayColors: false,
          titleFont: {
            size: chartTheme.defaults.fontSizes.tooltipTitle,
            weight: "bold",
          },
          bodyFont: {
            size: chartTheme.defaults.fontSizes.tooltipBody,
          },
        },
        title: {
          display: false,
          text: props.title,
          font: {
            size: 20,
            weight: "600",
          },
          color: chartTheme.defaults.textColor,
        },
        legend: {
          labels: {
            color: chartTheme.defaults.legendColor,
            font: {
              size: chartTheme.defaults.fontSizes.legend,
            },
          },
        },
      },
    },
  });
};

onMounted(createParetoChart);
watch(() => props.data, createParetoChart);
</script>

<style scoped>
.chart-card {
  background: #ffffff;
  border: 1px solid #e6e6e6;
  border-radius: 12px;
  padding: 20px;
  box-shadow: 0 6px 16px rgba(0, 0, 0, 0.1);
  font-family: "Inter", sans-serif;
  transition: box-shadow 0.3s ease;
}

.chart-card:hover {
  box-shadow: 0 8px 24px rgba(0, 0, 0, 0.12);
}

.chart-header h3 {
  margin: 0;
  font-size: 22px;
  font-weight: 600;
  color: #333;
}

.chart-container {
  height: 300px; /* Same height as the second chart */
  width: 100%;
  margin-top: 20px;
}

.chart-container canvas {
  width: 100% !important;  /* Ensure canvas fills the container width */
  height: 100% !important; /* Ensure canvas fills the container height */
}
</style>
