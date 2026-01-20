<template>
  <div class="shape-overview p-4">
    <!-- Loading State -->
    <div v-if="loading" class="text-center py-20">
      <p class="text-gray-600 text-lg">Loading shapes overview...</p>
    </div>

    <!-- Error State -->
    <div v-else-if="error" class="text-center py-20">
      <p class="text-red-600 text-lg">{{ error }}</p>
      <button 
        @click="loadOverviewData" 
        class="mt-4 px-6 py-3 bg-blue-500 text-white rounded hover:bg-blue-600"
        aria-label="Retry loading shapes overview data"
      >
        Retry
      </button>
    </div>

    <!-- Main Content -->
    <div v-else>
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
      </div>
    </div>

    <!-- Plots Section -->
    <div class="grid grid-cols-3 gap-4 mb-4">
      <HistogramChart
        :title="'Distribution of Violations per Constraint'"
        :xAxisLabel="'Number of Violations per Constraint'"
        :yAxisLabel="'Number of Node Shapes'"
        :data="normalizedHistogramViolationData"
        :explanationText="'This scatter plot shows how violations correlate with the number of constraints 1.'"
      />
      <ScatterPlotChart
        :title="'Correlation Between Constraints and Violations'"
        :xAxisLabel="'Number of Constraints'"
        :yAxisLabel="'Violations / Constraint'"
        :data="coveragePlotData"
        :showQuadrants="true"
        :explanationText="'This scatter plot shows how violations correlate with the number of constraints 1.'"
      />
      <ScatterPlotChart
        :title="'Violation Diversity and Intensity'"
        :xAxisLabel="'Entropy of Constraint Violations'"
        :yAxisLabel="'Violations / Constraints'"
        :data="scatterPlotData"
        :showQuadrants="true"
        :explanationText="'This scatter plot shows how violations correlate with the number of constraints 2.'"

      />
    </div>

    <!-- Table Section -->
    <div class="bg-white border border-gray-200 p-6 rounded-lg shadow-lg">
      <h2 class="text-2xl font-bold text-gray-700 mb-4">Shape Details</h2>
      <table class="w-full border-collapse">
        <thead class="bg-gray-200">
          <tr>
            <th 
              v-for="(column, index) in columns" 
              :key="index" 
              class="text-left px-6 py-3 border-b border-gray-300 text-gray-600 font-medium cursor-pointer"
              @click="sortColumn(column)">
              {{ column.label }}
              <span class="sort-indicator" >
                {{ sortKey === column.field ? (sortOrder === 'asc' ? ' ▲' : ' ▼') : '' }}
              </span>
            </th>
            <th class="text-center px-6 py-3 border-b border-gray-300 text-gray-600 font-medium"></th>
          </tr>
        </thead>
        <tbody>
          <tr 
            v-for="shape in sortedPaginatedData" 
            :key="shape.id" 
            class="even:bg-gray-50 hover:bg-blue-50 transition-colors"
            @click="goToShape(shape)">
            <td class="px-6 py-4 border-b border-gray-300">{{ shape.name }}</td>
            <td class="px-6 py-4 border-b border-gray-300">{{ shape.violations }}</td>
            <td class="px-6 py-4 border-b border-gray-300">{{ shape.propertyShapes }}</td>
            <td class="px-6 py-4 border-b border-gray-300">{{ shape.focusNodes }}</td>
            <td class="px-6 py-4 border-b border-gray-300">{{ shape.propertyPaths }}</td>
            <td class="px-6 py-4 border-b border-gray-300">{{ shape.mostViolatedConstraint }}</td>
            <td class="px-6 py-4 border-b border-gray-300">{{ shape.violationToConstraintRatio }}</td>
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
          class="px-4 py-2 bg-gray-200 text-gray-600 rounded hover:bg-gray-300 disabled:opacity-50">
          Previous
        </button>
        <span class="text-gray-700">Page {{ currentPage }} of {{ totalPages }}</span>
        <button
          :disabled="currentPage === totalPages"
          @click="nextPage"
          class="px-4 py-2 bg-gray-200 text-gray-600 rounded hover:bg-gray-300 disabled:opacity-50">
          Next
        </button>
      </div>
    </div>
    </div>
  </div>
</template>


<script setup>
/**
 * ShapeOverview component
 *
 * Provides a comprehensive overview of SHACL shapes in the dataset.
 * Displays statistics, visualizations, and listings of shapes with their constraints and validation results.
 *
 * @example
 * // Basic usage in a parent component template:
 * // <ShapeOverview />
 *
 * @prop {Array} [shapes=[]] - List of shapes to display
 * @prop {Boolean} [showViolations=true] - Whether to show violation data
 * @prop {Boolean} [showCharts=true] - Whether to show visualization charts
 *
 * @dependencies
 * - vue (Composition API)
 * - ../Charts/PieChart.vue
 * - ../Charts/GroupedBarChart.vue
 *
 * @style
 * - Responsive layout with cards and data tables.
 * - Data visualization components for shape statistics.
 * - Filterable and sortable shape listings with expandable details.
 * 
 * @returns {HTMLElement} A dashboard page showing shape statistics in summary cards at the top,
 * three data visualizations (histogram and scatter plots) in the middle, and a sortable, paginated 
 * data table listing all node shapes with their metrics and violation details at the bottom.
 */
// Importing components
import HistogramChart from './../Charts/HistogramChart.vue';
import ScatterPlotChart from './../Charts/ScatterPlotChart.vue';
import { ref, computed, onMounted } from 'vue';
import { logger } from '@/services/logger';
import { useRouter } from 'vue-router';
import { calculateShannonEntropy } from "./../../utils/utils";
import { useShapesStore } from '@/stores/shapes';
import { usePrefixes } from '../../composables/usePrefixes.js';

// Initialize stores
const shapesStore = useShapesStore();

// State
const loading = computed(() => shapesStore.overviewLoading);
const error = computed(() => shapesStore.error);

// Use prefixes composable for URI formatting
const { loadPrefixes, formatURI } = usePrefixes();

// Router for navigation
const router = useRouter();

// Tags data - computed from store
const tags = computed(() => [
  { title: "Total Node Shapes", value: shapesStore.totalNodeShapes },
  { title: "Node Shapes with Violations (%)", value: `${shapesStore.violationPercentage}%` },
  { title: "Max Violations per Node Shape", value: shapesStore.maxViolationsPerShape },
  { title: "Avg Violations per Node Shape", value: shapesStore.avgViolationsPerShape },
]);

// Chart data - computed from store
const normalizedHistogramViolationData = computed(() => shapesStore.violationsDistribution || { labels: [], datasets: [] });

const coveragePlotData = computed(() => {
  if (!shapesStore.correlationData) {
    return { datasets: [{ label: "Shapes", data: [] }] };
  }
  return {
    datasets: [{
      label: "Shapes",
      data: shapesStore.correlationData.map(item => ({
        x: item.num_constraints,
        y: item.num_constraints > 0 ? item.num_violations / item.num_constraints : 0,
        label: "",
        hasZeroViolations: item.num_violations === 0
      }))
    }]
  };
});

const scatterPlotData = computed(() => {
  if (!shapesStore.correlationData) {
    return { datasets: [{ label: "Shapes", data: [] }] };
  }
  return {
    datasets: [{
      label: "Shapes",
      data: shapesStore.correlationData.map(item => ({
        x: item.violation_entropy,
        y: item.num_constraints > 0 ? item.num_violations / item.num_constraints : 0,
        label: ""
      }))
    }]
  };
});

const columns = ref([
  { label: "Node Shape Name", field: "name" },
  { label: "Violations", field: "violations" },
  { label: "Number of Property Shapes", field: "propertyShapes" },
  { label: "Focus Nodes Affected", field: "focusNodes" },
  { label: "Property Paths", field: "propertyPaths" },
  { label: "Most Violated Constraint Component", field: "mostViolatedConstraint" },
  { label: "Violation-to-Constraint Ratio", field: "violationToConstraintRatio" },
]);

// Table data - computed from store with formatted URIs
const shapes = computed(() => {
  return (shapesStore.nodeShapes || []).map(shape => ({
    ...shape,
    originalName: shape.name,  // Keep full URI for navigation
    name: formatURI(shape.name),  // Display prefixed version
    mostViolatedConstraint: formatURI(shape.mostViolatedConstraint)
  }));
});

// Load all overview data from store
const loadOverviewData = async () => {
  try {
    // Load prefixes (cached after first call)
    await loadPrefixes();

    // Load all data from store (store handles API calls and caching)
    await shapesStore.loadOverview();
    await shapesStore.loadChartData();
    await shapesStore.loadShapesTable();

  } catch (err) {
    logger.error('Error loading overview data:', err);
  }
};

// Replace with composables
import { usePagination } from '@/composables/usePagination';
import { useSorting } from '@/composables/useSorting';

const { currentPage, totalPages, paginatedData, prevPage, nextPage } = usePagination(shapes, 10);
const { sortKey, sortOrder, sortedData, sortBy } = useSorting(paginatedData);

// Use sortedData instead of sortedPaginatedData
const sortedPaginatedData = sortedData;

// Sorting wrapper for column clicks
const sortColumn = (column) => {
  sortBy(column.field);
};

// Use originalName (full URI) for navigation, not the prefixed name
const goToShape = (shape) => {
  // URL-encode the shape URI to handle special characters and slashes
  const encodedShapeId = encodeURIComponent(shape.originalName);
  router.push({ name: "ShapeView", params: { shapeId: encodedShapeId } });
};

// Load data on mount
onMounted(() => {
  loadOverviewData();
});
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

.shape-overview {
  display: flex;
  flex-direction: column;
  gap: 1rem;
}

.sort-indicator {
  font-size: 0.8em; /* Makes the triangle smaller */
  margin-left: 5px;
  opacity: 0.8; /* Optional: makes it slightly faded */
}
</style>
