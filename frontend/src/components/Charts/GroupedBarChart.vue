<template>
    <div class="chart-container">
      <canvas ref="barChartCanvas"></canvas>
    </div>
  </template>
  
  <script setup>
  import { onMounted, ref } from 'vue';
  import { Chart } from 'chart.js';
  
  const props = defineProps({
    title: String,
    xAxisLabel: String,
    yAxisLabel: String,
    data: Object
  });
  
  const barChartCanvas = ref(null);
  
  onMounted(() => {
    new Chart(barChartCanvas.value, {
      type: 'bar',
      data: props.data,
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
            stacked: true,
            title: {
              display: true,
              text: props.xAxisLabel
            }
          },
          y: {
            stacked: true,
            title: {
              display: true,
              text: props.yAxisLabel
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
  