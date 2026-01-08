<template>
  <div class="focusnode-overview p-4">

    <!-- Tags Section -->
    <div class="grid grid-cols-4 gap-4 mb-4">
      <div
        v-for="(tag, index) in tags"
        :key="index"
        class="flex flex-row items-center bg-white rounded-lg shadow p-6 hover:shadow-md transition"
      >
        <div class="flex-grow">
          <h3 class="text-sm font-medium text-gray-600 mb-1">{{ tag.title }}</h3>
          <p class="text-3xl font-bold text-gray-800">{{ tag.value }}</p>
        </div>
        <div class="flex items-center justify-center bg-gray-200 rounded-full w-12 h-12">
          <!-- Replace with a relevant icon -->
          <font-awesome-icon :icon="['fas', 'chart-bar']" class="text-gray-600" />
        </div>
      </div>
    </div>

    <!-- Plots Section -->
    <div class="grid grid-cols-3 gap-4 mb-4">
      <HistogramChart
          :title="'Violations per Focus Node'"
          :xAxisLabel="'Number of Violations'"
          :yAxisLabel="'Frequency'"
          :data="histogramData"
        />
        <BarChart
          :title="'Shapes per Node'"
          :xAxisLabel="'Number of Shapes'"
          :yAxisLabel="'Frequency'"
          :data="barChartData"
        />
        <HistogramChart
          :title="'Property Path Violations per Node'"
          :xAxisLabel="'Number of Violations'"
          :yAxisLabel="'Frequency'"
          :data="histogramData"
        />
    </div>

    <!-- Table Section -->
    <div class="bg-white border border-gray-200 p-6 rounded-lg shadow-lg">
      <h2 class="text-2xl font-bold text-gray-700 mb-4">Focus Node Details</h2>
      <table class="w-full border-collapse">
        <thead class="bg-gray-200">
          <tr>
            <th class="text-left px-6 py-3 border-b border-gray-300 text-gray-600 font-medium">Focus Node</th>
            <th class="text-left px-6 py-3 border-b border-gray-300 text-gray-600 font-medium">Violations</th>
            <th class="text-left px-6 py-3 border-b border-gray-300 text-gray-600 font-medium">Shapes Applied</th>
            <th class="text-left px-6 py-3 border-b border-gray-300 text-gray-600 font-medium">Most Violated Property Path</th>
            <th class="text-left px-6 py-3 border-b border-gray-300 text-gray-600 font-medium">RDF Snippet</th>
            <th class="text-center px-6 py-3 border-b border-gray-300 text-gray-600 font-medium"></th>
          </tr>
        </thead>
        <tbody>
          <tr
            v-for="node in focusNodes"
            :key="node.id"
            class="even:bg-gray-50 hover:bg-blue-50 transition-colors"
            @click="goToFocusNodeView(node)"
          >
            <td class="px-6 py-4 border-b border-gray-300">{{ node.name }}</td>
            <td class="px-6 py-4 border-b border-gray-300">{{ node.violations }}</td>
            <td class="px-6 py-4 border-b border-gray-300">{{ node.shapesApplied }}</td>
            <td class="px-6 py-4 border-b border-gray-300">{{ node.mostViolatedPropertyPath }}</td>
            <td class="px-6 py-4 border-b border-gray-300">{{ node.rdfSnippet }}</td>
            <td class="px-6 py-4 border-b border-gray-300 text-center">
              <button class="text-blue-600 hover:text-blue-800">
                <font-awesome-icon icon="arrow-right" />
              </button>
            </td>
          </tr>
        </tbody>
      </table>
    </div>
  </div>
</template>

<script setup>
/**
 * FocusNodeOverview component
 *
 * Provides a comprehensive overview of focus nodes in the dataset.
 * Displays statistics, visualizations, and listings of focus nodes with their validation results.
 *
 * @example
 * // Basic usage in a parent component template:
 * // <FocusNodeOverview />
 *
 * @prop {Array} [focusNodes=[]] - List of focus nodes to display
 * @prop {Boolean} [showViolations=true] - Whether to show violation data
 * @prop {Boolean} [showCharts=true] - Whether to show visualization charts
 *
 * @dependencies
 * - vue (Composition API)
 * - ../Charts/PieChart.vue
 * - ../FocusNodeView/Metrics.vue
 *
 * @style
 * - Responsive layout with cards and data tables.
 * - Data visualization components for focus node statistics.
 * - Filterable and sortable focus node listings.
 * 
 * @returns {HTMLElement} A dashboard page displaying focus node statistics in summary cards at
 * the top, three visualizations (histograms and bar chart) in the middle, and a comprehensive
 * data table showing all focus nodes with their properties, violation counts, and RDF snippets.
 */
// Importing components
import HistogramChart from './../Charts/HistogramChart.vue';
import BarChart from './../Charts/BarChart.vue';
import { ref } from 'vue';
import { useRouter } from 'vue-router';

// Router navigation for focus node detail view
const router = useRouter();
const goToFocusNodeView = (node) => {
  router.push({ name: 'FocusNodeView', params: { focusNodeId: node.id } });
};

// Mock data for tags
const tags = [
  { title: "Total Focus Nodes", value: 50 },
  { title: "Nodes with Violations (%)", value: "60%" },
  { title: "Max Violations per Node", value: 25 },
  { title: "Avg Violations per Node", value: 5.2 },
];

// Mock data for charts
const histogramData = {
  labels: ['0-5', '6-10', '11-15', '16-20', '21-25'],
  datasets: [{ label: 'Number of Focus Nodes', data: [3, 2, 1, 0, 0], backgroundColor: '#42A5F5' }],
};
const barChartData = {
  labels: ['1 Shape', '2 Shapes', '3 Shapes', '4 Shapes'],
  datasets: [{ label: 'Shapes Applied per Node', data: [1, 2, 1, 0], backgroundColor: '#66BB6A' }],
};

// Mock data for table
const focusNodes = ref([
  { id: 1, name: 'Person', violations: 12, shapesApplied: 3, mostViolatedPropertyPath: 'author', rdfSnippet: '<Person rdf:ID="1"/>' },
  { id: 2, name: 'Book', violations: 8, shapesApplied: 2, mostViolatedPropertyPath: 'title', rdfSnippet: '<Book rdf:ID="2"/>' },
  { id: 3, name: 'Author', violations: 15, shapesApplied: 5, mostViolatedPropertyPath: 'writtenBy', rdfSnippet: '<Author rdf:ID="3"/>' },
]);
</script>

<style scoped>
.grid-cols-4 {
  grid-template-columns: repeat(4, 1fr);
}

tbody tr:hover {
  background-color: #f0f8ff;
}

.grid {
  grid-template-columns: repeat(auto-fit, minmax(200px, 1fr));
}

.shape-overview,
.focusnode-overview {
  display: flex;
  flex-direction: column;
  gap: 1rem;
}
</style>
