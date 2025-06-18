<template>
  <div class="propertypath-overview p-4">
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
          <font-awesome-icon :icon="['fas', 'chart-bar']" class="text-gray-600" />
        </div>
      </div>
    </div>

    <!-- Plots Section -->
    <div class="grid grid-cols-3 gap-4 mb-4">
      <HistogramChart
          :title="'Property Path Depth Distribution'"
          :xAxisLabel="'Depth Level'"
          :yAxisLabel="'Frequency'"
          :data="histogramData"
        />
        <BarChart
          :title="'Path Type Distribution'"
          :xAxisLabel="'Path Types'"
          :yAxisLabel="'Occurrences'"
          :data="barChartData"
        />
        <HorizontalBoxPlotChart
          :title="'Path Usage Distribution'"
          :xAxisLabel="'Usage Frequency'"
          :yAxisLabel="'Paths'"
          :data="boxPlotData"
        />
    </div>

    <!-- Table Section -->
    <div class="bg-white border border-gray-200 p-6 rounded-lg shadow-lg">
      <h2 class="text-2xl font-bold text-gray-700 mb-4">Property Path Details</h2>
      <table class="w-full border-collapse">
        <thead class="bg-gray-200">
          <tr>
            <th class="text-left px-6 py-3 border-b border-gray-300 text-gray-600 font-medium">Property Path</th>
            <th class="text-left px-6 py-3 border-b border-gray-300 text-gray-600 font-medium">Path Type</th>
            <th class="text-left px-6 py-3 border-b border-gray-300 text-gray-600 font-medium">Description</th>
            <th class="text-center px-6 py-3 border-b border-gray-300 text-gray-600 font-medium"></th>
          </tr>
        </thead>
        <tbody>
          <tr
            v-for="propertyPath in propertyPaths"
            :key="propertyPath.id"
            class="even:bg-gray-50 hover:bg-blue-50 transition-colors"
            @click="goToPropertyPath(propertyPath)"
          >
            <td class="px-6 py-4 border-b border-gray-300">{{ propertyPath.path }}</td>
            <td class="px-6 py-4 border-b border-gray-300">{{ propertyPath.type }}</td>
            <td class="px-6 py-4 border-b border-gray-300">{{ propertyPath.description }}</td>
            <td class="px-6 py-4 border-b border-gray-300 text-center">
              <button class="text-blue-600 hover:text-blue-800">
                <font-awesome-icon icon="arrow-right" />
              </button>
            </td>
          </tr>
        </tbody>
      </table>

      <div class="flex justify-between items-center mt-4">
        <button
          :disabled="currentPage === 1"
          @click="prevPage"
          class="px-4 py-2 bg-gray-200 text-gray-600 rounded hover:bg-gray-300 disabled:opacity-50"
        >
          Previous
        </button>
        <span class="text-gray-700">Page {{ currentPage }} of {{ totalPages }}</span>
        <button
          :disabled="currentPage === totalPages"
          @click="nextPage"
          class="px-4 py-2 bg-gray-200 text-gray-600 rounded hover:bg-gray-300 disabled:opacity-50"
        >
          Next
        </button>
      </div>
    </div>
  </div>
</template>

<script setup>
/**
 * PropertyPathOverview component
 *
 * Provides a comprehensive overview of property paths in the dataset.
 * Displays statistics, visualizations, and listings of property paths with usage and validation results.
 *
 * @example
 * // Basic usage in a parent component template:
 * // <PropertyPathOverview />
 *
 * @prop {Array} [propertyPaths=[]] - List of property paths to display
 * @prop {Boolean} [showViolations=true] - Whether to show violation data
 * @prop {Boolean} [showCharts=true] - Whether to show visualization charts
 *
 * @dependencies
 * - vue (Composition API)
 * - ../Charts/StackedBarChart.vue
 *
 * @style
 * - Responsive layout with cards and data tables.
 * - Data visualization components for property path statistics.
 * - Filterable and sortable property path listings.
 * 
 * @returns {HTMLElement} A dashboard page showing property path statistics in summary cards at 
 * the top, three data visualizations (histogram, bar chart, and box plot) in the middle, and a
 * paginated data table listing all property paths with their types and descriptions at the bottom.
 */
// Importing components
import HistogramChart from './../Charts/HistogramChart.vue';
import BarChart from './../Charts/BarChart.vue';
import HorizontalBoxPlotChart from './../Charts/HorizontalBoxPlotChart.vue';
import { ref, computed } from 'vue';
import { useRouter } from 'vue-router';

// Router for navigation
const router = useRouter();

// Mock data for tags
const tags = [
  { title: "Total Property Paths", value: 50 },
  { title: "Paths with Descriptions (%)", value: "60%" },
  { title: "Max Path Depth per Property", value: 100 },
  { title: "Avg Path Depth per Property", value: 2 },
];

// Mock data for charts
const histogramData = {
  labels: ['1-2', '3-4', '5-6', '7-8'],
  datasets: [
    {
      label: 'Property Paths',
      data: [10, 15, 20, 5],
      backgroundColor: '#66BB6A',
    },
  ],
};
const barChartData = {
  labels: ['IRI', 'Literal', 'Blank Node'],
  datasets: [
    {
      label: 'Path Type Occurrences',
      data: [25, 15, 10],
      backgroundColor: ['#42A5F5', '#66BB6A', '#FF5252'],
    },
  ],
};
const boxPlotData = [1, 2, 3, 4, 5, 6, 7, 8, 9, 10];

// Mock data for the table
const propertyPaths = ref([
  { id: 1, path: "book:hasAuthor", type: "IRI", description: "Indicates the author of a book." },
  { id: 2, path: "book:hasTitle", type: "Literal", description: "Indicates the title of a book." },
  { id: 3, path: "book:publishedBy", type: "IRI", description: "Indicates the publisher of the book." },
]);

// Pagination logic
const currentPage = ref(1);
const pageSize = ref(5);
const totalPages = computed(() => Math.ceil(propertyPaths.value.length / pageSize.value));

const paginatedData = computed(() => {
  const start = (currentPage.value - 1) * pageSize.value;
  return propertyPaths.value.slice(start, start + pageSize.value);
});

const prevPage = () => {
  if (currentPage.value > 1) currentPage.value--;
};

const nextPage = () => {
  if (currentPage.value < totalPages.value) currentPage.value++;
};

const goToPropertyPath = (propertyPath) => {
  router.push({ name: 'PropertyPathView', params: { pathId: propertyPath.id } });
};
</script>

<style scoped>
.grid-cols-4 {
  grid-template-columns: repeat(4, 1fr);
}

th, td {
  padding: 12px;
}

tbody tr:hover {
  background-color: #f0f8ff;
}

tbody tr {
  cursor: pointer;
}

.grid {
  grid-template-columns: repeat(auto-fit, minmax(200px, 1fr));
}

.chart-container {
  height: 100%;
  width: 100%;
  background: white;
  border-radius: 8px;
  padding: 10px;
}

.propertypath-overview {
  display: flex;
  flex-direction: column;
  gap: 1rem;
}
</style>
