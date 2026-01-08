<template>
      <div class="chart-container">
        <canvas ref="chartCanvas"></canvas>
      </div>
  </template>
  
  <script setup>
/**
 * GaugeChart component
 *
 * Renders a gauge chart (speedometer-like) using Chart.js.
 * Displays a single value within a range with color-coded thresholds.
 *
 * @example
 * // Basic usage in a parent component template:
 * // <GaugeChart
 * //   :title="'Performance Score'"
 * //   :value="75"
 * //   :minValue="0"
 * //   :maxValue="100"
 * //   :thresholds="{ green: 75, yellow: 50, red: 25 }"
 * // />
 *
 * @prop {String} title - Title for the chart
 * @prop {Number} value - The value to display on the gauge
 * @prop {Number} minValue - Minimum value of the gauge range
 * @prop {Number} maxValue - Maximum value of the gauge range
 * @prop {Object} thresholds - Threshold values for color changes
 *
 * @dependencies
 * - vue (Composition API)
 * - chart.js
 *
 * @style
 * - Semi-circular gauge display
 * - Color-coded sections based on thresholds
 * - Clear indicator of current value position
 * 
 * @returns {HTMLElement} A canvas element containing a semi-circular gauge chart 
 * resembling a speedometer or dial, showing a needle pointing to the current value
 * position, with color-coded sections representing different threshold ranges.
 */
  import { ref, onMounted, watch, nextTick } from "vue";
  import { Chart, ArcElement, Tooltip } from "chart.js";
  
  Chart.register(ArcElement, Tooltip);
  
  const props = defineProps({
    value: {
      type: Number,
      required: true,
    },
    minValue: {
      type: Number,
      default: 0,
    },
    maxValue: {
      type: Number,
      default: 100,
    },
    thresholds: {
      type: Object,
      default: () => ({ green: 75, yellow: 50, red: 25 }),
    },
  });
  
  const chartCanvas = ref(null);
  let chartInstance = null;
  
  const createGaugeChart = async () => {
    await nextTick();
    if (!chartCanvas.value) return;
  
    if (chartInstance) {
      chartInstance.destroy();
    }
  
    const percentage = ((props.value - props.minValue) / (props.maxValue - props.minValue)) * 100;
  
    chartInstance = new Chart(chartCanvas.value, {
      type: "doughnut",
      data: {
        datasets: [
          {
            data: [percentage, 100 - percentage],
            backgroundColor: [
              percentage >= props.thresholds.green
                ? "rgba(67, 160, 71, 1)"
                : percentage >= props.thresholds.yellow
                ? "rgba(253, 216, 53, 1)"
                : "rgba(244, 67, 54, 1)",
              "rgba(229, 229, 229, 1)", // Gray background for remaining area
            ],
            borderWidth: 0,
          },
        ],
      },
      options: {
        rotation: -90,
        circumference: 180,
        cutout: "70%",
        plugins: {
          tooltip: { enabled: false },
          legend: { display: false },
        },
      },
      plugins: [
        {
          id: "centerText",
          beforeDraw(chart) {
            const { width } = chart;
            const { ctx } = chart;
            ctx.restore();
            const fontSize = (width / 5).toFixed(2);
            ctx.font = `bold ${fontSize}px 'Segoe UI'`;
            ctx.textAlign = "center";
            ctx.textBaseline = "top";
            ctx.fillStyle = "#333";
            const centerX = (chart.chartArea.left + chart.chartArea.right) / 2;
            const centerY = (chart.chartArea.top + chart.chartArea.bottom) / 2;
            ctx.fillText(`${Math.round(percentage)}%`, centerX, centerY);
            ctx.save();
          },
        },
      ],
    });
  };
  
  onMounted(async () => {
    await createGaugeChart();
  });
  
  watch(() => props.value, createGaugeChart);
  </script>
  
  <style scoped>
  .chart-card {
    background: transparent;
    border: 1px solid #e6e6e6;
    border-radius: 10px;
    padding: 0px 0px 0px 0px;
    box-shadow: 0 4px 12px rgba(0, 0, 0, 0.05);
    font-family: 'Roboto', sans-serif;
    transition: box-shadow 0.3s ease;
  }
  
  .chart-card:hover {
    box-shadow: 0 6px 16px rgba(0, 0, 0, 0.1);
  }
  
  .chart-container {
    height: 100px;
    width: 100%;
    margin-top: 0px;
  }
  
  .chart-container canvas {
    width: 100% !important;
    height: 100% !important;
  }
  </style>
