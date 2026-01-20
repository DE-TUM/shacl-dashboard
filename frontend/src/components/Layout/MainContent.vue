<template>
  <div class="main-content p-4">
    <!-- Tags Section -->
    <div class="grid gap-6 mb-6"
     style="grid-template-columns: minmax(150px, 0.2fr) 1fr 1fr 1fr 1fr;">
     <div
  v-for="(tag, index) in tags"
  :key="index"
  class="card flex flex-col sm:flex-row items-center justify-center text-center bg-white shadow rounded-lg p-6 hover:shadow-md transition"
>
  <div class="flex-grow flex flex-col items-center text-center">
    <h3 class="text-xs sm:text-sm md:text-base font-medium text-gray-500 mb-1">
      {{ tag.title }}
    </h3>
    <p class="font-bold text-[18px] text-gray-800">
      {{ tag.value }}
    </p>
      <!-- Added spacing here -->
    <div class="h-4 sm:h-5"></div> <!-- Spacer div for consistent spacing -->
    <h3 class="text-xs sm:text-sm md:text-base font-medium text-gray-500 mb-1">
      {{ tag.titleMaxViolated }}
    </h3>
    <p class="font-bold text-[18px]" :style="{ color: 'rgb(227,114,34)' }">
      {{ tag.maxViolated }}
    </p>
  </div>
</div>
</div>

<!-- Histograms Section -->
<div class="grid grid-cols-4 gap-4 mb-4 w-full max-w-full overflow-hidden transition">
      <!-- Histogram for Violations per Shape -->
      <HistogramChart
        :title="`<span style='color: rgba(154, 188, 228);; font-weight: bold;'>Violations per Node Shape</span>`"
        titleAlign="center"
        :xAxisLabel="'Number of Violations (Bins)'"
        :yAxisLabel="'Frequency'"
        :data="shapeHistogramData"
      />

      <!-- Histogram for Violations per Path -->
      <HistogramChart
        :title="`<span style='color: rgba(94, 148, 212, 1);; font-weight: bold;'>Violations per Path</span>`"
        :xAxisLabel="'Number of Violations (Bins)'"
        :yAxisLabel="'Frequency'"
        :data="pathHistogramData"
      />

      <!-- Histogram for Violations per Focus Node -->
      <HistogramChart
        :title="`<span style='color: rgba(22, 93, 177, 1);; font-weight: bold;'>Violations per Focus Node</span>`"
        :xAxisLabel="'Number of Violations (Bins)'"
        :yAxisLabel="'Frequency'"
        :data="focusNodeHistogramData"
      />

      <HistogramChart
        :title="`<span style='color: rgba(10, 45, 87);; font-weight: bold;'>Violations per Constraint Component</span>`"
        :xAxisLabel="'Number of Violations (Bins)'"
        :yAxisLabel="'Frequency'"
        :data="constraintComponentHistogramData"
      />
    </div>

    <!-- Table Section -->
    <ViolationTable class="card bg-white shadow-lg rounded-lg p-6 w-full max-w-full overflow-hidden" style="grid-column: span 3;" />
  </div>
</template>

<script setup>
/**
 * MainContent component
 *
 * Main content area of the application that displays the primary content.
 * Typically renders the currently active route's component.
 *
 * @example
 * // Basic usage in a parent component template:
 * // <MainContent />
 *
 * @prop {Boolean} [fullWidth=false] - Whether the content should take full width
 * @prop {String} [padding='p-6'] - CSS padding class for the content
 *
 * @dependencies
 * - vue (Composition API)
 * - vue-router (for route content)
 *
 * @style
 * - Responsive container for the main application content.
 * - Adjusts to accommodate sidebar and navigation components.
 * - Contains padding and layout styling for content areas.
 * 
 * @returns {HTMLElement} A dashboard layout featuring a statistics section with key metrics
 * at the top, a visualization section with multiple histograms in the middle, and a 
 * comprehensive data table showing validation details at the bottom.
 */
import { ref, computed, onMounted } from "vue";
import HistogramChart from "./../Charts/HistogramChart.vue";
import PieChart from "./../Charts/PieChart.vue";
import Tag from "./../Reusable/Tag.vue";
import ViolationTable from "./../Reusable/ViolationTable.vue";
import { useViolationsStore } from '@/stores/violations';
import { usePrefixes } from '../../composables/usePrefixes.js';
import { logger } from '@/services/logger';
import * as api from '@/services/api';

// Use stores
const violationsStore = useViolationsStore();

// Use prefixes composable for URI formatting
const { loadPrefixes, formatURI: formatUri } = usePrefixes();

// Helper function to calculate percentage
const formatPercentage = (part, total) => {
  if (total === 0) return "0%";
  return `${((part / total) * 100).toFixed(2)}%`;
};

// Reactive data for tags and histograms
const tags = ref([
  { title: "Total Violations", value: "Loading...", titleMaxViolated: "", maxViolated: "" },
  { title: "Violated Node Shapes", value: "Loading...", titleMaxViolated: "Most Violated Node Shape", maxViolated: "Loading..." },
  { title: "Violated Paths", value: "Loading...", titleMaxViolated: "Most Violated Path", maxViolated: "Loading..." },
  { title: "Violated Focus Nodes", value: "Loading...", titleMaxViolated: "Most Violated Focus Node", maxViolated: "Loading..." },
  { title: "Violated Constraint Components", value: "Loading...", titleMaxViolated: "Most Violated Constraint Component", maxViolated: "Loading..." },
]);

const shapeHistogramData = ref({
  labels: [],
  datasets: [
    {
      label: "Violations",
      data: [],
      backgroundColor: "rgba(154, 188, 228)",
      borderColor: "rgba(154, 188, 228)",
      borderWidth: 1,
    },
  ],
});

const pathHistogramData = ref({
  labels: [],
  datasets: [
    {
      label: "Violations",
      data: [],
      backgroundColor: "rgba(94, 148, 212, 1)",
      borderColor: "rgba(94, 148, 212, 1)",
      borderWidth: 1,
    },
  ],
});

const focusNodeHistogramData = ref({
  labels: [],
  datasets: [
    {
      label: "Violations",
      data: [],
      backgroundColor: "rgba(22, 93, 177, 1)",
      borderColor: "rgba(22, 93, 177, 1)",
      borderWidth: 1,
    },
  ],
});

const constraintComponentHistogramData = ref({
  labels: [],
  datasets: [
    {
      label: "Violations",
      data: [],
      backgroundColor: "rgba(10, 45, 87)",
      borderColor: "rgba(10, 45, 87)",
      borderWidth: 1,
    },
  ],
});

// Load data from API on component mount
onMounted(async () => {
  try {
    // Load prefixes (cached after first call)
    await loadPrefixes();

    // Fetch all statistics in parallel
    const [
      violationsCount,
      nodeShapesWithViolations,
      totalNodeShapes,
      pathsWithViolations,
      totalPaths,
      focusNodesCount,
      mostViolatedShape,
      mostViolatedPath,
      mostViolatedFocusNode,
      distinctConstraintComponents,
      mostFrequentConstraint,
      shapeDistribution,
      pathDistribution,
      focusNodeDistribution,
      constraintDistribution,
    ] = await Promise.all([
      api.getViolationsCount(),
      api.getNodeShapesWithViolationsCount(),
      api.getNodeShapesCount(),
      api.getPathsWithViolationsCount(),
      api.getPathsCountInGraph(),
      api.getFocusNodesCount(),
      api.getMostViolatedNodeShape(),
      api.getMostViolatedPath(),
      api.getMostViolatedFocusNode(),
      api.getDistinctConstraintComponentsCount(),
      api.getMostFrequentConstraintComponent(),
      api.getViolationsDistributionPerShape(),
      api.getViolationsDistributionPerPath(),
      api.getViolationsDistributionPerFocusNode(),
      api.getViolationsDistributionPerConstraintComponent(),
    ]);

    // Update tags with fetched data
    tags.value = [
      {
        title: "Total Violations",
        value: violationsCount.violationCount.toString(),
        titleMaxViolated: "",
        maxViolated: "",
      },
      {
        title: "Violated Node Shapes",
        value: `${nodeShapesWithViolations.nodeShapesWithViolationsCount}/${totalNodeShapes.nodeShapeCount} (${formatPercentage(nodeShapesWithViolations.nodeShapesWithViolationsCount, totalNodeShapes.nodeShapeCount)})`,
        titleMaxViolated: "Most Violated Node Shape",
        maxViolated: formatUri(mostViolatedShape.nodeShape),
      },
      {
        title: "Violated Paths",
        value: `${pathsWithViolations.pathsWithViolationsCount}/${totalPaths.uniquePathsCount} (${formatPercentage(pathsWithViolations.pathsWithViolationsCount, totalPaths.uniquePathsCount)})`,
        titleMaxViolated: "Most Violated Path",
        maxViolated: formatUri(mostViolatedPath.path),
      },
      {
        title: "Violated Focus Nodes",
        value: focusNodesCount.focusNodesCount.toString(),
        titleMaxViolated: "Most Violated Focus Node",
        maxViolated: formatUri(mostViolatedFocusNode.focusNode),
      },
      {
        title: "Violated Constraint Components",
        value: distinctConstraintComponents.distinctConstraintComponentCount.toString(),
        titleMaxViolated: "Most Violated Constraint Component",
        maxViolated: formatUri(mostFrequentConstraint.constraintComponent),
      },
    ];

    // Update histogram data with proper styling
    shapeHistogramData.value = {
      ...shapeDistribution,
      datasets: shapeDistribution.datasets.map(dataset => ({
        ...dataset,
        backgroundColor: "rgba(154, 188, 228)",
        borderColor: "rgba(154, 188, 228)",
        borderWidth: 1,
      }))
    };
    
    pathHistogramData.value = {
      ...pathDistribution,
      datasets: pathDistribution.datasets.map(dataset => ({
        ...dataset,
        backgroundColor: "rgba(94, 148, 212, 1)",
        borderColor: "rgba(94, 148, 212, 1)",
        borderWidth: 1,
      }))
    };
    
    focusNodeHistogramData.value = {
      ...focusNodeDistribution,
      datasets: focusNodeDistribution.datasets.map(dataset => ({
        ...dataset,
        backgroundColor: "rgba(22, 93, 177, 1)",
        borderColor: "rgba(22, 93, 177, 1)",
        borderWidth: 1,
      }))
    };
    
    constraintComponentHistogramData.value = {
      ...constraintDistribution,
      datasets: constraintDistribution.datasets.map(dataset => ({
        ...dataset,
        backgroundColor: "rgba(10, 45, 87)",
        borderColor: "rgba(10, 45, 87)",
        borderWidth: 1,
      }))
    };
    
  } catch (error) {
    logger.error("Error loading homepage data:", error);
    // Set error state in tags
    tags.value = tags.value.map(tag => ({
      ...tag,
      value: tag.value === "Loading..." ? "Error" : tag.value,
      maxViolated: tag.maxViolated === "Loading..." ? "Error" : tag.maxViolated,
    }));
  }
});

</script>

<style scoped>
.main-content {
  display: flex;
  flex-direction: column;
  gap: 1.5rem;
}

.grid {
  grid-template-columns: repeat(auto-fit, minmax(200px, 1fr));
}

.grid-cols-3 {
  grid-template-columns: repeat(3, 1fr);
  gap: 1.5rem;
}

.card {
  transition: box-shadow 0.2s ease-in-out;
}

.card:hover {
  box-shadow: 0 10px 15px rgba(0, 0, 0, 0.1);
}

</style>
