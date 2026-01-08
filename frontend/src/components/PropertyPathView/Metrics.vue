<template>
  <div class="key-metrics grid grid-cols-4 gap-4">
    <!-- Shapes Using This Path -->
    <div class="metric-card bg-white shadow rounded p-4 flex items-center justify-between">
      <div class="flex items-center">
        <div class="icon bg-purple-100 text-purple-500 p-2 rounded-full mr-4">
          <svg xmlns="http://www.w3.org/2000/svg" class="h-6 w-6" fill="none" viewBox="0 0 24 24" stroke="currentColor">
            <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M4 4h16v16H4z" />
          </svg>
        </div>
        <div>
          <p class="text-lg font-semibold">Shapes Using This Path</p>
          <ul class="text-sm text-purple-500">
            <li v-for="shape in shapesUsingThisPath" :key="shape">{{ shape }}</li>
          </ul>
        </div>
      </div>
      <div class="sparkline">
        <sparkline-chart :data="[10, 12, 8, 14, 9]" color="purple" />
      </div>
    </div>

    <!-- Violations by Focus Node -->
    <div class="metric-card bg-white shadow rounded p-4 flex items-center justify-between">
      <div class="flex items-center">
        <div class="icon bg-red-100 text-red-500 p-2 rounded-full mr-4">
          <svg xmlns="http://www.w3.org/2000/svg" class="h-6 w-6" fill="none" viewBox="0 0 24 24" stroke="currentColor">
            <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M18.364 5.636a9 9 0 11-12.728 0M15 12h.01M9 12h.01M15 16h.01M9 16h.01M12 12.5l-3-3m0 0h6m-6 0l3 3" />
          </svg>
        </div>
        <div>
          <p class="text-lg font-semibold">Violations by Focus Node</p>
          <ul class="text-sm text-red-500">
            <li v-for="(count, node) in violationsByFocusNode" :key="node">{{ node }}: {{ count }}</li>
          </ul>
        </div>
      </div>
      <div class="sparkline">
        <sparkline-chart :data="[5, 10, 7, 15, 12]" color="red" />
      </div>
    </div>

    <!-- Constraint Components -->
    <div class="metric-card bg-white shadow rounded p-4 flex items-center justify-between">
      <div class="flex items-center">
        <div class="icon bg-yellow-100 text-yellow-500 p-2 rounded-full mr-4">
          <svg xmlns="http://www.w3.org/2000/svg" class="h-6 w-6" fill="none" viewBox="0 0 24 24" stroke="currentColor">
            <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M3 7v6M7 3v10m8-4v6m4-4v6m-8-4h6m-6-4h10M3 11h6m-6-4h10M3 3h6m-6 4h10" />
          </svg>
        </div>
        <div>
          <p class="text-lg font-semibold">Constraint Components</p>
          <ul class="text-sm text-yellow-500">
            <li v-for="constraint in constraintComponents" :key="constraint">{{ constraint }}</li>
          </ul>
        </div>
      </div>
      <div class="sparkline">
        <sparkline-chart :data="[1, 2, 2, 4, 5]" color="yellow" />
      </div>
    </div>

    <!-- Example Violations -->
    <div class="metric-card bg-white shadow rounded p-4 flex items-center justify-between">
      <div class="flex items-center">
        <div class="icon bg-blue-100 text-blue-500 p-2 rounded-full mr-4">
          <svg xmlns="http://www.w3.org/2000/svg" class="h-6 w-6" fill="none" viewBox="0 0 24 24" stroke="currentColor">
            <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M3 3h18v18H3z" />
          </svg>
        </div>
        <div>
          <p class="text-lg font-semibold">Example Violations</p>
          <ul class="text-sm text-blue-500">
            <li v-for="violation in exampleViolations" :key="violation">{{ violation }}</li>
          </ul>
        </div>
      </div>
      <div class="sparkline">
        <sparkline-chart :data="[3, 5, 8, 7, 6]" color="blue" />
      </div>
    </div>
  </div>
</template>

<script setup>
/**
 * Metrics component
 *
 * Displays key metrics about property paths in a dashboard format.
 * Shows information such as shapes using this path, violations by focus node,
 * constraint components, and example violations, each with a small sparkline chart.
 *
 * @example
 * // Basic usage in a parent component template:
 * // <Metrics />
 *
 * @prop {Array} [shapesUsingThisPath=['Shape 1', 'Shape 2', 'Shape 3']] - Shapes using this property path
 * @prop {Object} [violationsByFocusNode] - Object mapping focus nodes to violation counts
 * @prop {Array} [constraintComponents] - Array of constraint components related to this path
 * @prop {Array} [exampleViolations] - Examples of violations for this property path
 *
 * @dependencies
 * - vue (Composition API)
 * - ../Charts/SparklineChart.vue
 *
 * @style
 * - Grid layout with responsive card design.
 * - Cards with icons, titles, metric values, and sparkline charts.
 * - Color-coded icons and list items for visual categorization.
 * 
 * @returns {HTMLElement} A grid of four metric cards displaying property path information,
 * each with an icon, title, list of related data, and mini sparkline chart. Cards show shapes using
 * this path, violations by focus node, constraint components, and example violations with color coding.
 */
import SparklineChart from '../Charts/SparklineChart.vue'

// Props
const shapesUsingThisPath = ['Shape 1', 'Shape 2', 'Shape 3']
const violationsByFocusNode = {
  'Node A': 5,
  'Node B': 8,
  'Node C': 3
}
const constraintComponents = ['Constraint 1', 'Constraint 2', 'Constraint 3']
const exampleViolations = [
  'Missing value in property X',
  'Incorrect type for property Y',
  'Out-of-range value for property Z'
]
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
