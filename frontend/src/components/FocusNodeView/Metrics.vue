<template>
  <div class="key-metrics grid grid-cols-4 gap-4">
    <!-- Shapes Involved -->
    <div class="metric-card bg-white shadow rounded p-4 flex items-center justify-between">
      <div class="flex items-center">
        <div class="icon bg-purple-100 text-purple-500 p-2 rounded-full mr-4">
          <svg xmlns="http://www.w3.org/2000/svg" class="h-6 w-6" fill="none" viewBox="0 0 24 24" stroke="currentColor">
            <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M4 4h16v16H4z" />
          </svg>
        </div>
        <div>
          <p class="text-lg font-semibold">Shapes Involved</p>
          <p class="text-2xl text-purple-500 font-bold">{{ shapesInvolved }}</p>
        </div>
      </div>
      <div class="sparkline">
        <sparkline-chart :data="[10, 12, 8, 14, 9]" color="purple" />
      </div>
    </div>

    <!-- Total Violations -->
    <div class="metric-card bg-white shadow rounded p-4 flex items-center justify-between">
      <div class="flex items-center">
        <div class="icon bg-red-100 text-red-500 p-2 rounded-full mr-4">
          <svg xmlns="http://www.w3.org/2000/svg" class="h-6 w-6" fill="none" viewBox="0 0 24 24" stroke="currentColor">
            <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M18.364 5.636a9 9 0 11-12.728 0M15 12h.01M9 12h.01M15 16h.01M9 16h.01M12 12.5l-3-3m0 0h6m-6 0l3 3" />
          </svg>
        </div>
        <div>
          <p class="text-lg font-semibold">Total Violations</p>
          <p class="text-2xl text-red-500 font-bold">{{ totalViolations }}</p>
        </div>
      </div>
      <div class="sparkline">
        <sparkline-chart :data="[5, 10, 7, 15, 12]" color="red" />
      </div>
    </div>

    <!-- Affected Property Paths -->
    <div class="metric-card bg-white shadow rounded p-4 flex items-center justify-between">
      <div class="flex items-center">
        <div class="icon bg-green-100 text-green-500 p-2 rounded-full mr-4">
          <svg xmlns="http://www.w3.org/2000/svg" class="h-6 w-6" fill="none" viewBox="0 0 24 24" stroke="currentColor">
            <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M7 20h10M7 8h10M12 4v16m-7 2a2 2 0 002-2m10 0a2 2 0 002-2M7 4a2 2 0 00-2-2m10 0a2 2 0 002-2m-9.334 0h9.668" />
          </svg>
        </div>
        <div>
          <p class="text-lg font-semibold">Property Paths</p>
          <p class="text-2xl text-green-500 font-bold">{{ affectedPropertyPaths }}</p>
        </div>
      </div>
      <div class="sparkline">
        <sparkline-chart :data="[3, 3, 5, 8, 7]" color="green" />
      </div>
    </div>

    <!-- Constraints Triggered -->
    <div class="metric-card bg-white shadow rounded p-4 flex items-center justify-between">
      <div class="flex items-center">
        <div class="icon bg-yellow-100 text-yellow-500 p-2 rounded-full mr-4">
          <svg xmlns="http://www.w3.org/2000/svg" class="h-6 w-6" fill="none" viewBox="0 0 24 24" stroke="currentColor">
            <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M3 7v6M7 3v10m8-4v6m4-4v6m-8-4h6m-6-4h10M3 11h6m-6-4h10M3 3h6m-6 4h10" />
          </svg>
        </div>
        <div>
          <p class="text-lg font-semibold">Constraints</p>
          <p class="text-2xl text-yellow-500 font-bold">{{ constraintsTriggered }}</p>
        </div>
      </div>
      <div class="sparkline">
        <sparkline-chart :data="[1, 2, 2, 4, 5]" color="yellow" />
      </div>
    </div>
  </div>
</template>

<script setup>
/**
 * Metrics component
 *
 * Displays key metrics about focus nodes in a dashboard format.
 * Shows information such as shapes involved, total violations, affected property paths,
 * and constraints triggered, each with a small sparkline chart.
 *
 * @example
 * // Basic usage in a parent component template:
 * // <Metrics />
 *
 * @prop {Number} [shapesInvolved=22] - Number of shapes involved with this focus node
 * @prop {Number} [totalViolations=12] - Total number of violations for this focus node
 * @prop {Number} [affectedPropertyPaths=9] - Number of property paths affected
 * @prop {Number} [constraintsTriggered=6] - Number of constraints triggered
 *
 * @dependencies
 * - vue (Composition API)
 * - ../Charts/SparklineChart.vue
 *
 * @style
 * - Grid layout with responsive card design.
 * - Cards with icons, titles, metric values, and sparkline charts.
 * - Color-coded icons and values for visual categorization.
 * 
 * @returns {HTMLElement} A grid of four metric cards displaying key statistics about a focus node,
 * each with an icon, title, numerical value, and mini sparkline chart. Cards show shapes involved,
 * total violations, property paths, and constraints triggered, each with distinct color coding.
 */
import SparklineChart from '../Charts/SparklineChart.vue'

const shapesInvolved = 22
const totalViolations = 12
const affectedPropertyPaths = 9
const constraintsTriggered = 6
</script>

<style scoped>
.key-metrics {
  display: grid;
  grid-template-columns: repeat(4, 1fr);
  gap: 1rem;
}

.metric-card {
  display: flex;
  align-items: center;
  justify-content: space-between;
  padding: 1rem;
  border-radius: 0.5rem;
  background-color: white;
  box-shadow: 0 4px 6px rgba(0, 0, 0, 0.1);
}

.icon {
  flex-shrink: 0;
}

.sparkline {
  width: 100px;
  height: 40px;
}
</style>
