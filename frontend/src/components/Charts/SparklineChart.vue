<template>
  <div class="sparkline-container">
    <Line :data="chartData" :options="chartOptions" />
  </div>
</template>

<script setup>
/**
 * SparklineChart component
 *
 * Renders a compact sparkline chart using Chart.js.
 * Displays a simple, word-sized graphic to show the trend of a data series, with minimal visual elements.
 *
 * @example
 * // Basic usage in a parent component template:
 * // <SparklineChart
 * //   :data="sparklineData"
 * // />
 *
 * @prop {Object} data - Chart.js data object for the sparkline chart (required)
 *
 * @dependencies
 * - vue (Composition API)
 * - chart.js
 *
 * @style
 * - Compact, inline chart area with minimal height.
 * - No grid lines, axes, or labels to maintain simplicity.
 */
import { computed } from 'vue'
import { Line } from 'vue-chartjs'
import {
  Chart as ChartJS,
  Title,
  Tooltip,
  Legend,
  LineElement,
  PointElement,
  LinearScale,
  CategoryScale,
} from 'chart.js'

ChartJS.register(
  Title,
  Tooltip,
  Legend,
  LineElement,
  PointElement,
  LinearScale,
  CategoryScale
)

const props = defineProps({
  data: {
    type: Array,
    required: true
  },
  color: {
    type: String,
    default: '#42b983'
  }
})

const chartData = computed(() => ({
  labels: props.data.map((_, index) => index + 1),
  datasets: [{
    data: props.data,
    borderColor: props.color,
    borderWidth: 2,
    tension: 0.3,
    fill: false,
    pointRadius: 0
  }]
}))

const chartOptions = computed(() => ({
  responsive: true,
  maintainAspectRatio: false,
  plugins: {
    legend: {
      display: false
    },
    tooltip: {
      enabled: false
    }
  },
  scales: {
    x: {
      display: false
    },
    y: {
      display: false
    }
  }
}))
</script>

<style scoped>
.sparkline-container {
  height: 40px;
  width: 100px;
  position: relative;
}
</style>