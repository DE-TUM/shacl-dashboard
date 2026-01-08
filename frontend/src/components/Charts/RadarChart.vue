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
  
  <script>
/**
 * RadarChart component
 *
 * Renders a radar chart using Chart.js.
 * Displays multivariate data as a two-dimensional chart of multiple quantitative variables, with configurable title.
 *
 * @example
 * // Basic usage in a parent component template:
 * // <RadarChart
 * //   :data="radarData"
 * //   title="Radar Chart Example"
 * // />
 *
 * @prop {Object} data - Chart.js data object for the radar chart (required)
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
  import { defineComponent, onMounted, ref, watch } from "vue";
  import { Chart } from "chart.js";
  
  export default defineComponent({
    name: "RadarChart",
    props: {
      title: {
        type: String,
        default: "Radar Chart",
      },
      labels: {
        type: Array,
        required: true,
      },
      data: {
        type: Array,
        required: true,
      },
    },
    setup(props) {
      const chartCanvas = ref(null);
      let chartInstance = null;
  
      const createChart = () => {
        if (chartInstance) {
          chartInstance.destroy();
        }
  
        chartInstance = new Chart(chartCanvas.value, {
          type: "radar",
          data: {
            labels: props.labels,
            datasets: [
              {
                label: props.title,
                data: props.data,
                backgroundColor: "rgba(54, 162, 235, 0.2)",
                borderColor: "rgba(54, 162, 235, 1)",
                borderWidth: 2,
              },
            ],
          },
          options: {
            responsive: true,
            plugins: {
              title: {
                display: true,
                text: props.title,
              },
            },
            scales: {
              r: {
                angleLines: {
                  display: true,
                },
                suggestedMin: 0,
                suggestedMax: Math.max(...props.data) + 5, // Dynamic scaling
              },
            },
          },
        });
      };
  
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
  
      return {
        chartCanvas,
      };
    },
  });
  </script>
  
  <style scoped>
  .chart-card {
    background: white;
    border-radius: 12px;
    box-shadow: 0 4px 12px rgba(0, 0, 0, 0.05);
    padding: 20px;
    transition: box-shadow 0.3s ease;
  }
  
  .chart-card:hover {
    box-shadow: 0 6px 16px rgba(0, 0, 0, 0.1);
  }
  
  .chart-header h3 {
    margin: 0 0 10px;
    font-size: 16px;
    font-weight: 600;
    color: #333;
  }
  
  .chart-body {
    position: relative;
    height: 250px;
  }
  </style>