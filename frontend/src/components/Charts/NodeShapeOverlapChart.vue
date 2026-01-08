<template>
    <div class="node-shape-overlap-chart">
      <canvas ref="nodeShapeCanvas"></canvas>
    </div>
</template>
  
  <script setup>
/**
 * NodeShapeOverlapChart component
 *
 * Renders a chart visualizing the overlap between node shapes using Chart.js.
 * Displays the intersection or overlap of different node shapes, with configurable title and axis labels.
 *
 * @example
 * // Basic usage in a parent component template:
 * // <NodeShapeOverlapChart
 * //   :data="overlapData"
 * //   title="Node Shape Overlap Example"
 * //   xAxisLabel="Node Shapes"
 * //   yAxisLabel="Overlap Count"
 * // />
 *
 * @prop {Object} data - Chart.js data object for the overlap chart (required)
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
