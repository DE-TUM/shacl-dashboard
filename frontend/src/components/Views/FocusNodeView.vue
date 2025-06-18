<template>
  <div class="focus-node-view p-4">
    <!-- Back Button Section -->
    <button @click="goBack" class="bg-blue-500 text-white px-4 py-2 rounded mb-4">
      Back to Overview
    </button>

    <!-- Header Section -->
    <div class="header-section mb-6">
      <h1 class="text-2xl font-bold mb-2 text-primary">Focus Node: {{ focusNodeURI }}</h1>
      <div class="header-content flex justify-between items-center bg-gray-100 p-4 rounded">
        <div>
          <p class="font-medium">RDF Snippet Preview:</p>
          <code class="text-sm bg-gray-200 p-1 rounded">{{ rdfSnippet }}</code>
        </div>
        <div>
          <p class="font-medium">Total Violations: <span class="text-red-500 font-bold">{{ totalViolations }}</span></p>
        </div>
      </div>
    </div>

    <!-- Main Content Section -->
    <div class="main-content space-y-6">
      <!-- Key Metrics Section -->
      <div class="key-metrics grid grid-cols-4 gap-4">
        <Metrics />
      </div>

      <!-- Plots Section -->
      <div class="plots-section grid grid-cols-3 gap-4">
        <div class="plot bg-gray-100 p-4 rounded">
          <h3 class="text-md font-medium">1. Violation Heatmap</h3>
          <ConstraintAnalysisChart :data="constraintAnalysisData" />
        </div>
        <div class="plot bg-gray-100 p-4 rounded">
          <h3 class="text-md font-medium">2. Constraint Analysis</h3>
          <ConstraintAnalysisChart :data="constraintAnalysisData" />
        </div>
        <div class="plot bg-gray-100 p-4 rounded">
          <h3 class="text-md font-medium">3. Node-Shape Overlap</h3>
          <NodeShapeOverlapChart :data="nodeShapeOverlapData" />
        </div>
      </div>
    </div>

    <!-- Violations List Section -->
    <div class="violations-section bg-gray-100 p-4 rounded mt-6">
      <h2 class="text-lg font-semibold mb-4">List of Violations</h2>
      <table class="table-auto w-full text-left border-collapse border border-gray-300">
        <thead class="bg-gray-200">
          <tr>
            <th class="border border-gray-300 px-4 py-2">Focus Node</th>
            <th class="border border-gray-300 px-4 py-2">Property Path</th>
            <th class="border border-gray-300 px-4 py-2">Constraint</th>
            <th class="border border-gray-300 px-4 py-2">Message</th>
          </tr>
        </thead>
        <tbody>
          <tr v-for="violation in violations" :key="violation.id" class="hover:bg-gray-50">
            <td class="border border-gray-300 px-4 py-2">{{ violation.focusNode }}</td>
            <td class="border border-gray-300 px-4 py-2">{{ violation.propertyPath }}</td>
            <td class="border border-gray-300 px-4 py-2">{{ violation.constraint }}</td>
            <td class="border border-gray-300 px-4 py-2">{{ violation.message }}</td>
          </tr>
        </tbody>
      </table>
    </div>
  </div>
</template>

<script setup>
/**
 * FocusNodeView component
 *
 * Detailed view for a specific focus node with SHACL validation results.
 * Displays node information, RDF snippet, metrics, visualizations, and associated violations.
 *
 * @example
 * // Basic usage in router view:
 * // <router-view /> with route to FocusNodeView with node ID parameter
 *
 * @dependencies
 * - vue (Composition API)
 * - vue-router - For navigation
 * - ../Charts/ConstraintAnalysisChart.vue
 * - ../Charts/NodeShapeOverlapChart.vue
 * - ../FocusNodeView/Metrics.vue
 *
 * @features
 * - Focus node URI and RDF snippet display
 * - Key metrics dashboard with violation counts
 * - Visualization charts for constraint analysis and node-shape overlap
 * - Violations table with detailed error information
 *
 * @style
 * - Clean, organized layout with distinct sections
 * - Consistent spacing and typography
 * - Responsive grid system for metrics and visualizations
 * 
 * @returns {HTMLElement} A detailed dashboard page for a focus node, featuring a header with
 * back navigation and node metadata including an RDF snippet, metrics cards showing validation
 * statistics, visualization charts for constraint analysis, and a violations table.
 */
import { ref } from 'vue';
import { useRouter } from 'vue-router';
import ConstraintAnalysisChart from './../Charts/ConstraintAnalysisChart.vue';
import NodeShapeOverlapChart from './../Charts/NodeShapeOverlapChart.vue';
import Metrics from './../FocusNodeView/Metrics.vue';

const router = useRouter();

// Mock Data (replace with real data or props later)
const focusNodeURI = ref("http://example.com/123");
const rdfSnippet = ref("<http://example.com/123> rdf:type ex:Person; ex:age 30;");
const totalViolations = ref(12);
const violations = ref([
  { id: 1, focusNode: "http://example.com/123", propertyPath: "ex:age", constraint: "sh:minCount", message: "Min count not met" },
  { id: 2, focusNode: "http://example.com/123", propertyPath: "ex:name", constraint: "sh:datatype", message: "Invalid datatype" }
]);

// Go back to the overview page
const goBack = () => {
  router.push({ name: "FocusNodeOverview" }); // Make sure the route name matches your route configuration
};
</script>

<style scoped>
.focus-node-view {
  width: 100%;
  max-width: 1200px;
  margin: 0 auto;
}

.header-section {
  border-bottom: 1px solid #e5e7eb;
}

.key-metrics,
.plots-section {
  display: grid;
}

.key-metrics {
  grid-template-columns: repeat(4, 1fr);
}

.plots-section {
  grid-template-columns: repeat(3, 1fr);
}

.plot-placeholder {
  display: flex;
  align-items: center;
  justify-content: center;
  color: #6b7280;
  font-size: 0.875rem;
}
</style>
