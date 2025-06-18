<template>
  <div class="propertypath-view p-4">
    <button @click="goBack" class="bg-blue-500 text-white px-4 py-2 rounded mb-4">
      Back to Overview
    </button>

    <div class="header-section mb-6">
      <h1 class="text-2xl font-bold mb-2 text-primary">Property Path: {{ propertyPath }}</h1>
      <div class="header-content flex justify-between items-center bg-gray-100 p-4 rounded">
        <div>
          <p class="font-medium">Path Type:</p>
          <span class="text-green-500 font-semibold">{{ pathType }}</span>
        </div>
        <div>
          <p class="font-medium">
            Total Violations:
            <span class="text-red-500 font-bold">{{ totalViolations }}</span>
          </p>
        </div>
      </div>
    </div>

    <div class="main-content space-y-6">
      <div class="key-metrics grid grid-cols-4 gap-4">
        <Metrics />
      </div>

      <div class="plots-section grid grid-cols-3 gap-4">
        <div class="plot bg-gray-100 p-4 rounded">
          <h3 class="text-md font-medium">1. Violation Distribution</h3>
          <BarChart
            :title="'Violation Distribution'"
            :xAxisLabel="'Focus Nodes'"
            :yAxisLabel="'Number of Violations'"
            :data="violationDistributionData"
          />
        </div>
        <div class="plot bg-gray-100 p-4 rounded">
          <h3 class="text-md font-medium">2. Path Type Breakdown</h3>
          <BarChart
            :title="'Path Type Breakdown'"
            :xAxisLabel="'Property Path Types'"
            :yAxisLabel="'Violations'"
            :data="pathTypeData"
          />
        </div>
        <div class="plot bg-gray-100 p-4 rounded">
          <h3 class="text-md font-medium">3. Violation Examples</h3>
          <ViolationExamplesChart
            :title="'Example Violations'"
            :data="violationExamplesData"
          />
        </div>
      </div>
    </div>

    <div class="bottom-section bg-gray-100 p-4 rounded mt-6">
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
 * PropertyPathView component
 *
 * Detailed view for a specific SHACL property path.
 * Displays path information, metrics, visualizations, and associated violations.
 *
 * @example
 * // Basic usage in router view:
 * // <router-view /> with route to PropertyPathView with path ID parameter
 *
 * @dependencies
 * - vue (Composition API)
 * - vue-router - For navigation and route parameter access
 * - ../PropertyPathView/Metrics.vue
 * - ../Charts/BarChart.vue
 * - ../Charts/ViolationExamplesChart.vue
 *
 * @features
 * - Property path type and metadata display
 * - Key metrics dashboard
 * - Visualization charts for violation distribution and examples
 * - Comprehensive violations table
 *
 * @style
 * - Clean layout with distinct sections
 * - Color-coded information for visual differentiation
 * - Responsive grid system for metrics and charts
 * 
 * @returns {HTMLElement} A detailed dashboard page for property paths, containing a header with
 * back navigation and path metadata, key metrics in a card layout, three visualization charts
 * showing distribution data, and a comprehensive violations table listing all violations.
 */
import { ref, onMounted } from "vue";
import { useRoute, useRouter } from "vue-router";
import Metrics from "./../PropertyPathView/Metrics.vue";
import BarChart from './../Charts/BarChart.vue';
import ViolationExamplesChart from './../Charts/ViolationExamplesChart.vue';

const route = useRoute();
const router = useRouter();

const propertyPath = ref("");
const pathType = ref("");
const totalViolations = ref(0);

const violationDistributionData = ref({
  labels: ['Node 1', 'Node 2', 'Node 3'],
  datasets: [
    {
      label: 'Violations',
      data: [12, 5, 8],
      backgroundColor: ['rgba(255, 99, 132, 0.2)', 'rgba(54, 162, 235, 0.2)', 'rgba(75, 192, 192, 0.2)'],
      borderColor: ['rgba(255, 99, 132, 1)', 'rgba(54, 162, 235, 1)', 'rgba(75, 192, 192, 1)'],
      borderWidth: 1,
    },
  ],
});

const pathTypeData = ref({
  labels: ['Datatype Property', 'Object Property', 'Annotation Property'],
  datasets: [
    {
      label: 'Violations',
      data: [10, 20, 5],
      backgroundColor: ['rgba(255, 159, 64, 0.2)', 'rgba(153, 102, 255, 0.2)', 'rgba(255, 205, 86, 0.2)'],
      borderColor: ['rgba(255, 159, 64, 1)', 'rgba(153, 102, 255, 1)', 'rgba(255, 205, 86, 1)'],
      borderWidth: 1,
    },
  ],
});

const violationExamplesData = ref([
  { focusNode: "Node 1", message: "Missing value for foaf:age" },
  { focusNode: "Node 2", message: "Invalid datatype for foaf:name" },
]);

const violations = ref([
  { id: 1, focusNode: "http://example.com/123", propertyPath: "foaf:age", constraint: "sh:minCount", message: "Min count not met" },
  { id: 2, focusNode: "http://example.com/456", propertyPath: "foaf:name", constraint: "sh:datatype", message: "Invalid datatype" },
]);

onMounted(() => {
  const pathId = route.params.pathId;
  const pathData = {
    1: { path: "book:hasAuthor", type: "IRI", violations: 10 },
    2: { path: "book:hasTitle", type: "Literal", violations: 5 },
    3: { path: "book:publishedBy", type: "IRI", violations: 2 },
  }[pathId];

  if (pathData) {
    propertyPath.value = pathData.path;
    pathType.value = pathData.type;
    totalViolations.value = pathData.violations;
  }
});

const goBack = () => {
  router.push({ name: "PropertyPathOverview" });
};
</script>
