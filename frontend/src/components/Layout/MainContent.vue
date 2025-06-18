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
import { ref } from "vue";
import HistogramChart from "./../Charts/HistogramChart.vue";
import PieChart from "./../Charts/PieChart.vue";
import Tag from "./../Reusable/Tag.vue";
import ViolationTable from "./../Reusable/ViolationTable.vue";

const tags = [
  { title: "Total Violations", value: "27392", titleMaxViolated: "", maxViolated: "" },
  { title: "Violated Node Shapes", value: "27/30 (90%)", titleMaxViolated: "Most Violated Node Shape", maxViolated: "shs:StadiumShape"},
  { title: "Violated Paths", value: " 30/255 (11.76%)", titleMaxViolated: "Most Violated Path", maxViolated: "rdf:type" },
  { title: "Violated Focus Nodes", value: "1388", titleMaxViolated: "Most Violated Focus Node", maxViolated: "dbr:Steve_Davis" },
  { title: "Violated Constraint Components", value: "4/5 (80%)", titleMaxViolated: "Most Violated Constraint Component", maxViolated: "sh:InConstraintComponent" },
];

const shapeHistogramData = ref({
  labels: ["0-237", "238-475", "476-713", "714-951", "952-1189", "1190-1427", "1428-1665", "1666-1903", "1904-2141", "2142-2379"],
  datasets: [
    {
      label: "Violations",
      data: [5, 2, 4, 6, 5, 2, 2, 1, 1, 2],
      backgroundColor: "rgba(154, 188, 228)", // Light blue with transparency
      borderColor: "rgba(154, 188, 228)", // Solid blue border
      borderWidth: 1, // Optional: sets the border width of bars
    },
  ],
});


const pathHistogramData = ref({
  labels: ["0-2586", "2587-5173", "5174-7760", "7761-10347", "10348-12934", "12935-15521", "15522-18108", "18109-20695", "20696-23282", "23283-25869"],
  datasets: [
    {
      label: "Violations",
      data: [29, 0, 0, 0, 0, 0, 0, 0, 0, 1],
      backgroundColor: "rgba(94, 148, 212, 1)", // Light blue with transparency
      borderColor: "rgba(94, 148, 212, 1)", // Solid blue border
      borderWidth: 1, // Optional: sets the border width of bars
    },
  ],
});

const focusNodeHistogramData = ref({
  labels: ["0-10", "11-21", "22-32", "33-43", "44-54", "55-65", "66-76", "77-87", "88-98", "99-109"],
  datasets: [
    {
      label: "Violations",
      data: [268, 609, 378, 81, 21, 14, 10, 4, 1, 2],
      backgroundColor: "rgba(22, 93, 177, 1)", // Light blue with transparency
      borderColor: "rgba(22, 93, 177, 1)", // Solid blue border
      borderWidth: 1, // Optional: sets the border width of bars
    },
  ],
});

const constraintComponentHistogramData = ref({
  labels: ["0-2586", "2587-5173", "5174-7760", "7761-10347", "10348-12934", "12935-15521", "15522-18108", "18109-20695", "20696-23282", "23283-25869"],
  datasets: [
    {
      label: "Violations",
      data: [4, 0, 0, 0, 0, 0, 0, 0, 0, 1],
      backgroundColor: "rgba(10, 45, 87)", // Light blue with transparency
      borderColor: "rgba(10, 45, 87)", // Solid blue border
      borderWidth: 1, // Optional: sets the border width of bars
    },
  ],
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
