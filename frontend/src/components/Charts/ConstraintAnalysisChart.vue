<template>
    <div class="constraint-analysis-chart">
      <canvas ref="constraintCanvas" > </canvas>
    </div>
  </template>
  
  <script setup>
  import { onMounted, ref } from 'vue';
  import { Chart } from 'chart.js';
  
  const constraintAnalysisData = {
    labels: ['Constraint 1', 'Constraint 2', 'Constraint 3'],
    datasets: [{
      label: 'Violations per Constraint',
      data: [10, 20, 15],
      backgroundColor: 'rgba(255, 99, 132, 0.2)',
      borderColor: 'rgba(255, 99, 132, 1)',
      borderWidth: 1
    }]
  };
  
  const constraintCanvas = ref(null);
  
  onMounted(() => {
    const ctx = constraintCanvas.value.getContext('2d');
    new Chart(ctx, {
      type: 'bar',
      data: constraintAnalysisData,
      options: {
        responsive: true,
        scales: {
          y: {
            beginAtZero: true
          }
        }
      }
    });
  });
  </script>
  
  <style scoped>
  .constraint-analysis-chart {
    position: relative;
    width: 100%;
    height: 300px; /* Adjust height as needed */
  }
  </style>
  