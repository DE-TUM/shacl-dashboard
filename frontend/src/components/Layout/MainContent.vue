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

    <!-- Plots Section -->
    <!-- <div class="grid grid-cols-3 gap-6 mb-6">
      <BoxPlot
        title="Violation distribution over shapes"
        x-axis-label=""
        y-axis-label="Violations"
        :data="[1, 2, 2, 3, 4, 4, 4, 5, 5, 6, 7, 8, 9, 20]"
        class="card bg-white shadow-lg rounded-lg p-6"
      />
      <BoxPlot
        title="Violation distribution over paths"
        x-axis-label=""
        y-axis-label="Violations"
        :data="[1, 2, 2, 3, 4, 4, 4, 5, 5, 6, 7, 8, 9, 10]"
        class="card bg-white shadow-lg rounded-lg p-6"
      />
      <BoxPlot
        title="Violation distribution over focus nodes"
        x-axis-label=""
        y-axis-label="Violations"
        :data="[1, 2, 2, 3, 4, 4, 4, 5, 5, 6, 7, 8, 9, 50]"
        class="card bg-white shadow-lg rounded-lg p-6"
      />
    </div> -->
<!-- 
    <div class="grid grid-cols-3 gap-6 mb-6">
      <PieChart
        :title="'Violations per Shape'"
        :data="[72895, 83152, 80072, 39881, 14234, 7881, 86552, 98522, 79683, 13240]"
        :categories="['Shape A', 'Shape B', 'Shape C', 'Shape D', 'Shape E', 'Shape F', 'Shape G', 'Shape H', 'Shape I', 'Shape J']"
        class="card bg-white shadow-lg rounded-lg p-6"
      />
      <PieChart
        :title="'Violations per Path'"
        :data="[71491, 64036, 89818, 98656, 99242, 81159, 97923, 11101, 76166, 96080]"
        :categories="['Path A', 'Path B', 'Path C', 'Path D', 'Path E', 'Path F', 'Path G', 'Path H', 'Path I', 'Path J']"
        class="card bg-white shadow-lg rounded-lg p-6"
      />
      <PieChart
        :title="'Violations per Focus Node'"
        :data="[10496, 53213, 34641, 92937, 97444, 92112, 66890, 49144, 1061, 11078]"
        :categories="['Focus Node A', 'Focus Node B', 'Focus Node C', 'Focus Node D', 'Focus Node E', 'Focus Node F', 'Focus Node G', 'Focus Node H', 'Focus Node I', 'Focus Node J']"
        class="card bg-white shadow-lg rounded-lg p-6"
      />
    </div> -->
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
import { ref, onMounted } from "vue";
import HistogramChart from "./../Charts/HistogramChart.vue";
import PieChart from "./../Charts/PieChart.vue";
import Tag from "./../Reusable/Tag.vue";
import ViolationTable from "./../Reusable/ViolationTable.vue";
import * as api from "../../services/api.js";

// Store prefixes for URI formatting
const prefixes = ref({});

// Helper function to format URIs using prefixes
const formatUri = (uri) => {
  if (!uri || typeof uri !== "string") return "N/A";

  // Try to match with prefixes
  let matchedPrefix = null;
  let matchedNamespace = null;

  for (const [prefix, namespace] of Object.entries(prefixes.value)) {
    if (uri.startsWith(namespace) && (!matchedNamespace || namespace.length > matchedNamespace.length)) {
      matchedPrefix = prefix;
      matchedNamespace = namespace;
    }
  }

  if (matchedPrefix) {
    return `${matchedPrefix}:${uri.slice(matchedNamespace.length)}`;
  }

  // Fallback: extract local name after # or /
  const match = uri.match(/[#\/]([^#\/]+)$/);
  return match ? match[1] : uri;
};

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
    // First, fetch prefixes from validation details (just get 1 record to get prefixes quickly)
    const prefixData = await api.getValidationDetailsReport(1, 0);
    prefixes.value = prefixData["@prefixes"] || {};

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
      totalConstraints,
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
      api.getDistinctConstraintsCountInShapes(),
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
        value: `${distinctConstraintComponents.distinctConstraintComponentCount}/${totalConstraints.distinctConstraintsCount} (${formatPercentage(distinctConstraintComponents.distinctConstraintComponentCount, totalConstraints.distinctConstraintsCount)})`,
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
    console.error("Error loading homepage data:", error);
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
