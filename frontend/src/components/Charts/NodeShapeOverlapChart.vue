<template>
    <div class="node-shape-overlap-chart">
      <canvas ref="nodeShapeCanvas"></canvas>
    </div>
</template>
  
  <script setup>
  import { onMounted, ref } from 'vue';
  import { Chart } from 'chart.js';
  
  const nodeShapeOverlapData = {
    labels: ['Node A', 'Node B', 'Node C', 'Node D'],
    datasets: [{
      label: 'Shape Overlap',
      data: [15, 30, 25, 10],  // Sample data: Overlap values for each node
      backgroundColor: 'rgba(75, 192, 192, 0.2)',
      borderColor: 'rgba(75, 192, 192, 1)',
      borderWidth: 1
    }]
  };
  
  const nodeShapeCanvas = ref(null);
  
  onMounted(() => {
    const ctx = nodeShapeCanvas.value.getContext('2d');
    new Chart(ctx, {
      type: 'line',
      data: nodeShapeOverlapData,
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
  .node-shape-overlap-chart {
    position: relative;
    width: 100%;
    height: 200px; /* Adjust height as needed */
  }
  </style>
  