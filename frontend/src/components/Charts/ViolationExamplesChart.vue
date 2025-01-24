<template>
    <div class="chart-container">
      <canvas ref="examplesChartCanvas"></canvas>
    </div>
</template>
  
<script setup>
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
  