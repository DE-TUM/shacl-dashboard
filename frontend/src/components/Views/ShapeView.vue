<template>
  <div class="shape-view p-4">
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
      <!-- Scatter Plot -->
      <ScatterPlotChart
          :title="'Violation Impact vs. Complexity'"
          :xAxisLabel="'Number of Constraints'"
          :yAxisLabel="'Number of Violations'"
          :data="scatterPlotData"
          :explanationText="'This scatter plot shows how violations correlate with the number of constraints4.'"
        />

      <!-- Heatmap -->
      <HeatmapChart
          :title="'Violation Heatmap'"
          :xAxisLabel="'Constraint Types'"
          :yAxisLabel="'Property Shapes'"
          :data="heatmapData"
          :explanationText="'This scatter plot shows how violations correlate with the number of constraints 1.'"
        />

      <!-- Pareto Chart -->
      <ParetoChart
          :title="'Contribution of Property Shapes'"
          :xAxisLabel="'Property Shapes'"
          :yAxisLabel="'Cumulative Violations'"
          :data="paretoData"
          :explanationText="'This scatter plot shows how violations correlate with the number of constraints 1.'"
        />
    </div>

    <!-- Violations Table -->
    <ShapesTable class="bg-white shadow rounded-lg p-6 mt-8" />
  </div>
</template>

<script setup>
import { ref, onMounted } from "vue";
import { useRoute, useRouter } from "vue-router";
import ScatterPlotChart from "./../Charts/ScatterPlotChart.vue";
import HeatmapChart from "./../Charts/HeatmapChart.vue";
import ParetoChart from "./../Charts/ParetoChart.vue";
import ShapesTable from "./../Reusable/ShapesTable.vue";
import GaugeChart from "./../Charts/GaugeChart.vue";
import { FontAwesomeIcon } from "@fortawesome/vue-fontawesome";

const route = useRoute();
const router = useRouter();

const shapeName = ref("");
const shapeDefinition = ref("");
const totalViolations = ref(42);
const affectedFocusNodes = ref(15);
const affectedPropertyPaths = ref(8);
const constraintsTriggered = ref(5);
const healthScore = ref(70);
const showDefinition = ref(false);

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

const heatmapData = ref({
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

const paretoData = ref({
  labels: ["Property Shape 1", "Property Shape 2", "Property Shape 3"],
  values: [20, 30, 50],
});

const metrics = ref([
  { id: "violations", label: "Total Violations", value: totalViolations, titleMaxViolated: "", maxViolated: ""},
  { id: "focus-nodes", label: "Focus Nodes", value: affectedFocusNodes, titleMaxViolated: "Most Focus Node", maxViolated: "dbpedia:PGA_Tour"},
  { id: "property-paths", label: "Property Paths", value: affectedPropertyPaths, titleMaxViolated: "Most Property Path", maxViolated: " rdf:type"},
  { id: "constraints", label: "Constraints Triggered", value: constraintsTriggered, titleMaxViolated: "Most triggered Constrain", maxViolated: "sh:in"},
]);

const toggleDefinition = () => {
  showDefinition.value = !showDefinition.value;
};

onMounted(() => {
  const shapeId = route.params.shapeId;
  const shapes = {
    1: {
      name: "PersonShape",
      definition: `@prefix sh: <http://www.w3.org/ns/shacl#> . 
                    @prefix xsd: <http://www.w3.org/2001/XMLSchema#> .
                    @prefix foaf: <http://xmlns.com/foaf/0.1/> .
                    @prefix ex: <http://example.org/> .

                    ex:AgeShape
                        a sh:NodeShape ;
                        sh:targetClass foaf:Person ;  
                        sh:property [
                            sh:path foaf:age ;        
                            sh:datatype xsd:integer ; 
                            sh:minInclusive 0 ;       
                            sh:message "Age must be a non-negative integer." ;
                        ] .`,
      violations: 42,
    },
    2: {
      name: "AddressShape",
      definition: "PREFIX ex: <http://example.org/> ...",
      violations: 18,
    },
  };
  const shape = shapes[shapeId];

  if (shape) {
    shapeName.value = shape.name;
    shapeDefinition.value = shape.definition;
    totalViolations.value = shape.violations;
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
