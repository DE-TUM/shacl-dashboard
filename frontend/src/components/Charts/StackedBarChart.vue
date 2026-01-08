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
  
  <script>
/**
 * StackedBarChart component
 *
 * Renders a stacked bar chart using Chart.js.
 * Displays multiple series of data stacked on top of each other, with configurable title and axis labels.
 *
 * @example
 * // Basic usage in a parent component template:
 * // <StackedBarChart
 * //   :data="stackedData"
 * //   title="Stacked Bar Chart Example"
 * //   xAxisLabel="Categories"
 * //   yAxisLabel="Values"
 * // />
 *
 * @prop {Object} data - Chart.js data object for the stacked bar chart (required)
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
  import { Chart, registerables } from "chart.js";
  
  Chart.register(...registerables);
  
  export default {
    name: "StackedBarChart",
    props: {
      title: {
        type: String,
        required: true,
      },
      data: {
        type: Object,
        required: true,
      },
      xAxisLabel: {
        type: String,
        required: false,
        default: "",
      },
      yAxisLabel: {
        type: String,
        required: false,
        default: "",
      },
    },
    mounted() {
      this.createChart();
    },
    methods: {
      createChart() {
        const ctx = this.$refs.chartCanvas.getContext("2d");
  
        new Chart(ctx, {
          type: "bar",
          data: this.data,
          options: {
            plugins: {
              title: {
                display: true,
                text: this.title,
                font: {
                  size: 20,
                  weight: '600',
                },
                color: '#333',
              },
              tooltip: {
                mode: "index",
                intersect: false,
                backgroundColor: "#fff",
                borderColor: "#ddd",
                borderWidth: 1,
                titleColor: "#333",
                bodyColor: "#555",
                displayColors: false,
              },
            },
            responsive: true,
            maintainAspectRatio: false,
            scales: {
              x: {
                stacked: true,
                title: {
                  display: !!this.xAxisLabel,
                  text: this.xAxisLabel,
                  color: '#555',
                  font: {
                    size: 14,
                    weight: '500',
                  },
                },
                ticks: {
                  color: '#333',
                },
              },
              y: {
                stacked: true,
                title: {
                  display: !!this.yAxisLabel,
                  text: this.yAxisLabel,
                  color: '#555',
                  font: {
                    size: 14,
                    weight: '500',
                  },
                },
                ticks: {
                  color: '#333',
                },
              },
            },
          },
        });
      },
    },
  };
  </script>
  
  <style scoped>
  .chart-card {
    background: #ffffff;
    border: 1px solid #e6e6e6;
    border-radius: 10px;
    padding: 20px;
    box-shadow: 0 4px 12px rgba(0, 0, 0, 0.05);
    font-family: 'Inter', sans-serif;
    transition: box-shadow 0.3s ease;
  }
  
  .chart-card:hover {
    box-shadow: 0 6px 16px rgba(0, 0, 0, 0.1);
  }
  
  .chart-header h3 {
    margin: 0;
    font-size: 20px;
    font-weight: 600;
    color: #333;
  }
  
  .chart-container {
    height: 400px;
    width: 100%;
    margin-top: 20px;
  }
  
  .chart-container canvas {
    width: 100% !important;
    height: 100% !important;
  }
  </style>
