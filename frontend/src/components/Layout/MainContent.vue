<template>
  <div class="main-content p-4">
    <!-- Tags Section -->
    <div class="grid grid-cols-4 gap-6 mb-6">
      <div
        v-for="(tag, index) in tags"
        :key="index"
        class="card flex flex-row items-center bg-white shadow rounded-lg p-6 hover:shadow-md transition"
      >
        <div class="flex-grow">
          <h3 class="text-sm font-medium text-gray-500 mb-1">{{ tag.title }}</h3>
          <p class="text-3xl font-bold text-gray-800">{{ tag.value }}</p>
        </div>
        <div>
          <h3 class="text-sm font-medium text-gray-500 mb-1">{{ tag.titleMaxViolated }}</h3>
          <p class="text-xl font-medium" :style="{ color: 'rgb(227,114,34)' }">{{ tag.maxViolated }}</p>
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
<div class="grid grid-cols-3 gap-4 mb-4">
      <!-- Histogram for Violations per Shape -->
      <HistogramChart
        :title="`Distribution of <span style='color: rgba(94, 148, 212, 1);; font-weight: bold;'>Violations per Shape</span>`"
        :xAxisLabel="'Number of Violations (Bins)'"
        :yAxisLabel="'Frequency'"
        :data="shapeHistogramData"
      />

      <!-- Histogram for Violations per Path -->
      <HistogramChart
        :title="`Distribution of <span style='color: rgba(22, 93, 177, 1);; font-weight: bold;'>Violations per Path</span>`"
        :xAxisLabel="'Number of Violations (Bins)'"
        :yAxisLabel="'Frequency'"
        :data="pathHistogramData"
      />

      <!-- Histogram for Violations per Focus Node -->
      <HistogramChart
        :title="`Distribution of <span style='color: rgba(10, 45, 87);; font-weight: bold;'>Violations per Focus Node</span>`"
        :xAxisLabel="'Number of Violations (Bins)'"
        :yAxisLabel="'Frequency'"
        :data="focusNodeHistogramData"
      />
    </div>

    <!-- Table Section -->
    <ViolationTable class="card bg-white shadow-lg rounded-lg p-6" style="grid-column: span 3;" />
  </div>
</template>

<script setup>
import { ref } from "vue";
import HistogramChart from "./../Charts/HistogramChart.vue";
import PieChart from "./../Charts/PieChart.vue";
import Tag from "./../Reusable/Tag.vue";
import ViolationTable from "./../Reusable/ViolationTable.vue";

const tags = [
  { title: "Violations", value: "5432", titleMaxViolated: "", maxViolated: "" },
  { title: "Violated Shapes", value: "54/200 (27%)", titleMaxViolated: "Most Violated Shape", maxViolated: "shs:TennisTournamentShape"},
  { title: "Violated Paths", value: " 75/500 (15%)", titleMaxViolated: "Most Violated Path", maxViolated: "rdf:type" },
  { title: "Violated Focus Nodes", value: "150", titleMaxViolated: "Most Violated Focus Node", maxViolated: "db:PGA_Tour" },
];

const shapeHistogramData = ref({
  labels: ["0-5", "5-10", "10-15", "15-20", "20-25", "25-30", "30-35", "35-40", "40-45", "45-50"],
  datasets: [
    {
      label: "Violations",
      data: [2, 5, 8, 10, 12, 7, 6, 4, 3, 2],
      backgroundColor: "rgba(94, 148, 212, 1)", // Light blue with transparency
      borderColor: "rgba(94, 148, 212, 1)", // Solid blue border
      borderWidth: 1, // Optional: sets the border width of bars
    },
  ],
});

const pathHistogramData = ref({
  labels: ["0-5", "5-10", "10-15", "15-20", "20-25", "25-30", "30-35", "35-40", "40-45", "45-50"],
  datasets: [
    {
      label: "Violations",
      data: [1, 3, 5, 8, 9, 6, 5, 4, 2, 1],
      backgroundColor: "rgba(22, 93, 177, 1)", // Light blue with transparency
      borderColor: "rgba(22, 93, 177, 1)", // Solid blue border
      borderWidth: 1, // Optional: sets the border width of bars
    },
  ],
});

const focusNodeHistogramData = ref({
  labels: ["0-5", "5-10", "10-15", "15-20", "20-25", "25-30", "30-35", "35-40", "40-45", "45-50"],
  datasets: [
    {
      label: "Violations",
      data: [3, 6, 10, 9, 8, 5, 4, 3, 2, 1],
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
