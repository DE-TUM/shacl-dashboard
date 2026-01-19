<template>
  <div class="shape-view p-4">
    <!-- Loading State -->
    <div v-if="loading" class="text-center py-20">
      <p class="text-gray-600 text-lg">Loading shape details...</p>
    </div>

    <!-- Error State -->
    <div v-else-if="error" class="text-center py-20">
      <p class="text-red-600 text-lg">{{ error }}</p>
      <button @click="loadShapeData(route.params.shapeId)" class="mt-4 px-6 py-3 bg-blue-500 text-white rounded hover:bg-blue-600">
        Retry
      </button>
    </div>

    <!-- Main Content -->
    <div v-else>
    <!-- Header Section with Horizontal Bar -->
    <div class="header-section bg-gray-100 p-4 rounded mb-6 shadow flex items-center justify-between">
  <!-- Left: Breadcrumb Button -->
  <div class="breadcrumbs">
    <button 
      @click="goShapeOverview" 
      class="px-2 py-1 bg-blue-500 text-white rounded hover:bg-blue-600 flex items-center gap-2"
    >
      Back to Shape Overview
    </button>
  </div>

  <!-- Center: Title and Toggle Definition -->
  <div class="flex flex-col items-center flex-grow text-center">
    <h1 class="text-2xl font-semibold text-gray-800">NodeShape: {{ shapeName }}</h1>
    <div class="text-blue-600 text-sm cursor-pointer mt-1" @click="toggleDefinition">
      <span v-if="showDefinition">Hide Definition</span>
      <span v-else>Show Definition</span>
    </div>
  </div>

  <!-- Right: Placeholder for Balance -->
  <div class="w-[120px]"></div>
</div>
      <!-- Gauge Chart -->
      <!-- div class="gauge-chart">
        < <GaugeChart
          :title="'Node Shape Health'"
          :value="healthScore"
          :minValue="0"
          :maxValue="100"
          :thresholds="{ green: 75, yellow: 50, red: 25 }"
        /> -->
      <!--/div>

        <!-- Collapsible Shape Definition -->
        <transition name="fade">
          <div v-if="showDefinition" class="bg-gray-50 p-4 rounded mb-4 shadow">
            <p class="font-medium text-lg mb-2">Shape Definition:</p>
            <code
              class="text-sm bg-gray-50 text-gray-700 p-2 rounded block"
              style="white-space: pre-wrap;"
            >
              {{ shapeDefinition }}
            </code>
          </div>
        </transition>


    <!-- Key Statistics Section -->
    <div class="statistics-section grid grid-cols-4 gap-4 mb-8">
      <div
        v-for="metric in metrics"
        :key="metric.id"
        class="stat-card flex flex-row items-center bg-white rounded-lg shadow p-6 hover:shadow-md transition"
      >
        <div class="flex-grow">
          <h3 class="text-sm font-medium text-gray-600 mb-1">{{ metric.label }}</h3>
          <p class="text-3xl font-bold text-gray-800">{{ metric.value }}</p>
        </div>
        <div>
          <h3 class="text-sm font-medium text-gray-500 mb-1">{{ metric.titleMaxViolated }}</h3>
          <p class="text-xl font-medium" :style="{ color: 'rgb(227,114,34)' }">{{ metric.maxViolated }}</p>
        </div>
      </div>
    </div>


    <!-- Plots Section -->
    <div class="grid grid-cols-3 gap-4 mb-4">
      <!-- Heatmap -->
      <HeatmapChart
          :title="'Violation Heatmap'"
          :xAxisLabel="'Constraint Components'"
          :yAxisLabel="'Property Shapes'"
          :data="heatmapData26"
          :explanationText="'This scatter plot shows how violations correlate with the number of constraints 1.'"
          class="col-span-2"
        />

      <!-- Pareto Chart -->
      <ParetoChart
          :title="'Contribution of Property Shapes'"
          :xAxisLabel="'Property Shapes'"
          :yAxisLabel="'Cumulative Violations'"
          :data="paretoData"
          :explanationText="'This scatter plot shows how violations correlate with the number of constraints 1.'"
          class="col-span-1"
        />
    </div>

    <!-- Violations Table -->
    <ShapesTable :nodeShape="shapeId" class="bg-white shadow rounded-lg p-6 mt-8" />
    </div>
  </div>
</template>

<script setup>
/**
 * ShapeView component
 *
 * Detailed view for a specific SHACL node shape.
 * Displays shape information, metrics, visualizations, and associated validation results.
 *
 * @example
 * // Basic usage in router view:
 * // <router-view /> with route to ShapeView with shape ID parameter
 *
 * @dependencies
 * - vue (Composition API)
 * - vue-router - For navigation and route parameter access
 * - ../Charts/ScatterPlotChart.vue
 * - ../Charts/HeatmapChart.vue
 * - ../Charts/ParetoChart.vue
 * - ../Reusable/ShapesTable.vue
 * - ../Charts/GaugeChart.vue
 * - @fortawesome/vue-fontawesome
 *
 * @features
 * - Shape definition display with toggle
 * - Key metrics dashboard
 * - Multiple visualization charts for constraint violations
 * - Property shape details with associated violations
 *
 * @style
 * - Clean, organized section layout with consistent spacing
 * - Responsive grid system for metrics and visualizations
 * - Interactive elements with hover effects
 * 
 * @returns {HTMLElement} A detailed dashboard page containing a header with back navigation
 * and shape definition, metrics cards showing violation statistics, visualization charts 
 * (heatmap and pareto), and a property shapes table with detailed violation information.
 */
import { ref, onMounted, computed } from "vue";
import { useRoute, useRouter } from "vue-router";
import ScatterPlotChart from "./../Charts/ScatterPlotChart.vue";
import HeatmapChart from "./../Charts/HeatmapChart.vue";
import ParetoChart from "./../Charts/ParetoChart.vue";
import ShapesTable from "./../Reusable/ShapesTable.vue";
import GaugeChart from "./../Charts/GaugeChart.vue";
import { FontAwesomeIcon } from "@fortawesome/vue-fontawesome";
import {
  getViolationCountForNodeShape,
  getViolatedFocusNodesCountForNodeShape,
  getPropertyPathsCountForNodeShape,
  getConstraintCountForNodeShape,
  getViolationsPerConstraintTypeForPropertyShape,
  getShapeDefinition
} from '../../services/api.js';
import { usePrefixes } from '../../composables/usePrefixes.js';

const route = useRoute();
const router = useRouter();

const shapeId = ref(""); // Store the full URI from route
const shapeName = ref(""); // Store the formatted display name
const shapeDefinition = ref("");
const totalViolations = ref(0);
const affectedFocusNodes = ref(0);
const loading = ref(false);
const error = ref(null);

// Use prefixes composable for URI formatting
const { loadPrefixes, formatURI } = usePrefixes();

const affectedPropertyPaths = ref(0);
const constraintsTriggered = ref(0);
const healthScore = ref(70);
const showDefinition = ref(false);

// Refs for "most violated" metrics
const mostViolatedFocusNode = ref("");
const mostViolatedPropertyPath = ref("");
const mostTriggeredConstraint = ref("");

const scatterPlotData = ref({
  datasets: [
    {
      label: "Property Shapes",
      data: [
        { x: 3, y: 3.33, label: "Property Shape 1", hasZeroViolations: false },
        { x: 5, y: 3, label: "Property Shape 2", hasZeroViolations: false },
        { x: 7, y: 3.57, label: "Property Shape 3", hasZeroViolations: false },
        { x: 4, y: 0, label: "Property Shape 4", hasZeroViolations: true },
      ]
    },
  ],
});

const heatmapDatas = ref({
  properties: ["Property Shape 1", "Property Shape 2", "Property Shape 3", "Property Shape 4", "Property Shape 1", "Property Shape 2", "Property Shape 3", "Property Shape 4"],
  constraints: ["sh:minCount", "sh:maxCount", "sh:datatype", "sh:minCount", "sh:maxCount", "sh:datatype"],
  violations: [
    [3, 0, 0, 3, 0, 0],
    [0, 0.5, 0, 3, 0, 0],
    [2, 0, 1, 3, 0, 0],
    [2, 1, 1, 3, 0, 0],
    [3, 0, 0, 3, 0, 0],
    [0, 0.5, 0, 3, 0, 0],
    [2, 0, 1, 3, 0, 0],
    [2, 1, 1, 3, 0, 0],
  ],
});

const heatmapData26 = ref([

  ]);


const paretoData = ref({
  labels: ["Property Shape 1", "Property Shape 2", "Property Shape 3"],
  values: [20, 30, 50],
});

const metrics = computed(() => [
  { id: "violations", label: "Total Violations", value: totalViolations.value, titleMaxViolated: "", maxViolated: ""},
  { id: "focus-nodes", label: "Focus Nodes", value: affectedFocusNodes.value, titleMaxViolated: "Most Violated Focus Node", maxViolated: mostViolatedFocusNode.value},
  { id: "property-paths", label: "Property Paths", value: affectedPropertyPaths.value, titleMaxViolated: "Most Violated Property Path", maxViolated: mostViolatedPropertyPath.value},
  { id: "constraints", label: "Constraints Triggered", value: constraintsTriggered.value, titleMaxViolated: "Most Triggered Constraint", maxViolated: mostTriggeredConstraint.value},
]);

const toggleDefinition = () => {
  showDefinition.value = !showDefinition.value;
};

// Load shape data from API
const loadShapeData = async (shapeId) => {
  loading.value = true;
  error.value = null;

  try {
    // Load prefixes (cached after first call)
    await loadPrefixes();

    // Fetch all data in parallel
    const [
      violationsData,
      focusNodesData,
      propertyPathsData,
      constraintsData,
      violationsPerConstraintData,
      definitionData
    ] = await Promise.all([
      getViolationCountForNodeShape(shapeId),
      getViolatedFocusNodesCountForNodeShape(shapeId),
      getPropertyPathsCountForNodeShape(shapeId),
      getConstraintCountForNodeShape(shapeId),
      getViolationsPerConstraintTypeForPropertyShape(shapeId),
      getShapeDefinition(shapeId).catch(() => null)
    ]);

    // Update refs with API data - format the shapeName with prefix
    shapeName.value = formatURI(shapeId);
    totalViolations.value = violationsData.violationCount || 0;
    affectedFocusNodes.value = focusNodesData.violatedFocusNodesCount || 0;
    affectedPropertyPaths.value = propertyPathsData.propertyPathCount || 0;
    constraintsTriggered.value = constraintsData.constraintCount || 0;
    
    // Process definition data - backend returns shape data keyed by shape URI
    if (definitionData && definitionData[shapeId]) {
      const shapeData = definitionData[shapeId];
      shapeDefinition.value = JSON.stringify(shapeData, null, 2);
    } else {
      shapeDefinition.value = "Definition not available";
    }

    // Update heatmap data with formatted URIs and calculate "most" metrics
    if (violationsPerConstraintData.propertyShapes) {
      heatmapData26.value = violationsPerConstraintData.propertyShapes.map(ps => ({
        PropertyShape: formatURI(ps.PropertyShape),
        Constraints: ps.Constraints.map(c => ({
          Constraint: formatURI(c.Constraint),
          Violations: c.Violations
        }))
      }));

      // Calculate most violated property path (property shape with most violations)
      let maxPropertyViolations = 0;
      let maxPropertyShape = "";
      violationsPerConstraintData.propertyShapes.forEach(ps => {
        const totalViolations = ps.Constraints.reduce((sum, c) => sum + c.Violations, 0);
        if (totalViolations > maxPropertyViolations) {
          maxPropertyViolations = totalViolations;
          maxPropertyShape = ps.PropertyShape;
        }
      });
      mostViolatedPropertyPath.value = maxPropertyShape ? formatURI(maxPropertyShape) : "None";

      // Calculate most triggered constraint (constraint with most violations across all property shapes)
      const constraintViolations = {};
      violationsPerConstraintData.propertyShapes.forEach(ps => {
        ps.Constraints.forEach(c => {
          constraintViolations[c.Constraint] = (constraintViolations[c.Constraint] || 0) + c.Violations;
        });
      });
      
      let maxConstraintViolations = 0;
      let maxConstraint = "";
      Object.entries(constraintViolations).forEach(([constraint, violations]) => {
        if (violations > maxConstraintViolations) {
          maxConstraintViolations = violations;
          maxConstraint = constraint;
        }
      });
      mostTriggeredConstraint.value = maxConstraint ? formatURI(maxConstraint) : "None";

      // For most violated focus node, set to N/A (requires separate backend endpoint)
      mostViolatedFocusNode.value = "N/A";

      // Calculate Pareto data (top 3 property shapes by violation count)
      const propertyShapeViolations = violationsPerConstraintData.propertyShapes.map(ps => ({
        name: formatURI(ps.PropertyShape),
        totalViolations: ps.Constraints.reduce((sum, c) => sum + c.Violations, 0)
      }));

      // Sort by violations (descending) and take top 3
      const top3 = propertyShapeViolations
        .sort((a, b) => b.totalViolations - a.totalViolations)
        .slice(0, 3);

      // Update paretoData
      paretoData.value = {
        labels: top3.map(ps => ps.name),
        values: top3.map(ps => ps.totalViolations)
      };
    } else {
      // No data available
      mostViolatedPropertyPath.value = "None";
      mostTriggeredConstraint.value = "None";
      mostViolatedFocusNode.value = "N/A";
      
      // Fallback if no data
      paretoData.value = {
        labels: [],
        values: []
      };
    }

  } catch (err) {
    console.error('Error loading shape data:', err);
    error.value = 'Failed to load shape data. Please try again.';
  } finally {
    loading.value = false;
  }
};

onMounted(() => {
  // Decode the shapeId from URL encoding
  const encodedShapeId = route.params.shapeId;
  const decodedShapeId = decodeURIComponent(encodedShapeId);
  
  if (decodedShapeId) {
    shapeId.value = decodedShapeId; // Store in ref for template access
    loadShapeData(decodedShapeId);
  } else {
    error.value = "No shape ID provided";
  }
});

const goBack = () => {
  router.push({ name: "ShapeOverview" });
};

const goShapeOverview = () => {
  router.push({ name: "ShapeOverview" });
};
</script>

<style scoped>
.shape-view {
  width: 100%;
  margin: 0 auto;
}

.header-section {
  display: flex;
  flex-direction: row;
  align-items: center;
  justify-content: space-between;
  padding: 0.75rem 1.25rem; /* Reduced padding */
  background-color: #ffffff;
  border-radius: 0.5rem;
  box-shadow: 0 4px 6px rgba(0, 0, 0, 0.1);
  gap: 2rem; /* Increased gap between elements */
  min-height: 4rem; /* Set minimum height */
}

.breadcrumb {
  gap: 0.5rem; /* Tighter breadcrumb spacing */
}

.stat-card {
  display: flex;
  align-items: center;
  padding: 1rem;
  border-radius: 0.5rem;
  background-color: white;
  box-shadow: 0 4px 6px rgba(0, 0, 0, 0.1);
  transition: box-shadow 0.3s ease;
}

.stat-card:hover {
  box-shadow: 0 6px 10px rgba(0, 0, 0, 0.15);
}

.gauge-chart {
  display: flex;
  justify-content: center;
  align-items: center;
  padding: 0; /* Remove padding */
  background-color: transparent;
  max-width: 150px; /* Limit width */
}

.icon {
  flex-shrink: 0;
  padding: 0.5rem;
  border-radius: 50%;
  background-color: rgba(229, 229, 229, 1);
}

/* .plots-section {
  display: grid;
  grid-template-columns: repeat(3, 1fr);
  gap: 1.5rem;
} */

.plot {
  padding: 1rem;
  border-radius: 0.5rem;
  background-color: white;
  box-shadow: 0 4px 6px rgba(0, 0, 0, 0.1);
}

/* Adjust title spacing */
h1.text-2xl {
  margin: 0;
  line-height: 1.2;
}
</style>
