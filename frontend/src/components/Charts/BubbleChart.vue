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
   * BubbleChart component
   *
   * Renders a bubble chart visualization using Chart.js.
   * Displays data points as bubbles with x, y coordinates and size (r) dimensions.
   *
   * @example
   * // Basic usage in a parent component template:
   * // <BubbleChart
   * //   :data="bubbleData"
   * //   :title="'Resource Allocation'"
   * //   :xAxisLabel="'Time (days)'"
   * //   :yAxisLabel="'Cost ($)'"
   * // />
   *
   * @prop {Object} data - Chart.js data object for bubble chart containing datasets with x, y, r values
   * @prop {String} [title=''] - Title displayed above the chart
   * @prop {String} [xAxisLabel=''] - Label for the x-axis
   * @prop {String} [yAxisLabel=''] - Label for the y-axis
   *
   * @dependencies
   * - vue (Composition API)
   * - chart.js - For rendering the bubble chart
   * - chartTheme - For consistent styling
   *
   * @style
   * - Responsive chart area with managed aspect ratio
   * - Consistent theme colors from chartTheme
   * - Proper padding and positioning
   * 
   * @returns {HTMLElement} A canvas element containing the rendered bubble chart where
   * each data point is represented as a bubble with position (x, y) and size (r),
   * making it suitable for displaying three-dimensional data in a two-dimensional space.
   */
  import { Chart, registerables } from 'chart.js';
  
  Chart.register(...registerables);
  
  export default {
    name: "BubblePlotChart",
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
        default: "X-Axis",
      },
      yAxisLabel: {
        type: String,
        default: "Y-Axis",
      },
    },
    mounted() {
      this.createChart();
    },
    methods: {
      createChart() {
        const ctx = this.$refs.chartCanvas.getContext("2d");
  
        new Chart(ctx, {
          type: "bubble",
          data: this.data,
          options: {
            plugins: {
              title: {
                display: true,
                text: this.title,
              },
              tooltip: {
                callbacks: {
                  label: (context) => {
                    const { x, y, r } = context.raw;
                    return `${context.raw.label}: (Constraints: ${x}, Violations: ${y}, Ratio: ${(r / 10).toFixed(
                      2
                    )})`;
                  },
                },
              },
            },
            scales: {
              x: {
                title: {
                  display: true,
                  text: this.xAxisLabel,
                },
                beginAtZero: true,
              },
              y: {
                title: {
                  display: true,
                  text: this.yAxisLabel,
                },
                beginAtZero: true,
              },
            },
            elements: {
              point: {
                backgroundColor: "rgba(75, 192, 192, 0.8)",
                borderColor: "rgba(75, 192, 192, 1)",
                borderWidth: 1,
              },
            },
            responsive: true,
            maintainAspectRatio: false,
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
  
  .chart-container {
    position: relative;
    height: 400px;
  }
  
  .chart-container canvas {
    max-height: 100%;
  }
  </style>
