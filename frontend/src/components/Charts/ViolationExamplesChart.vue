<template>
    <div class="chart-container">
      <canvas ref="examplesChartCanvas"></canvas>
    </div>
</template>
  
<script setup>
/**
 * ViolationExamplesChart component
 *
 * Renders a chart visualizing SHACL validation violation examples using Chart.js.
 * Displays data about validation violations in a graphical format, with configurable title and axis labels.
 *
 * @example
 * // Basic usage in a parent component template:
 * // <ViolationExamplesChart
 * //   :data="violationData"
 * //   title="Validation Violations"
 * //   xAxisLabel="Violation Types"
 * //   yAxisLabel="Count"
 * // />
 *
 * @prop {Object} data - Chart.js data object for the violation examples chart (required)
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
  
  const props = defineProps({
    title: String,
    data: Array
  });
  
  const examplesChartCanvas = ref(null);
  
  onMounted(() => {
    const labels = props.data.map(example => example.focusNode);
    const data = props.data.map(example => example.message.length);
  
    new Chart(examplesChartCanvas.value, {
      type: 'bar',
      data: {
        labels: labels,
        datasets: [
          {
            label: 'Violation Example Length',
            data: data,
            backgroundColor: 'rgba(255, 99, 132, 0.2)',
            borderColor: 'rgba(255, 99, 132, 1)',
            borderWidth: 1
          }
        ]
      },
      options: {
        responsive: true,
        plugins: {
          title: {
            display: true,
            text: props.title
          },
          tooltip: {
            enabled: true
          }
        },
        scales: {
          x: {
            title: {
              display: true,
              text: 'Focus Node'
            }
          },
          y: {
            title: {
              display: true,
              text: 'Message Length'
            }
          }
        }
      }
    });
  });
  </script>
  
  <style scoped>
  .chart-container {
    position: relative;
    height: 200px;
  }
  </style>
