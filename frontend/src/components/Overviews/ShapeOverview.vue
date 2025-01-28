<template>
  <div class="shape-overview p-4">
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
</template>


<script setup>
// Importing components
import HistogramChart from './../Charts/HistogramChart.vue';
import ScatterPlotChart from './../Charts/ScatterPlotChart.vue';
import { ref, computed } from 'vue';
import { useRouter } from 'vue-router';
import { calculateShannonEntropy } from "./../../utils/utils"; // Assume you have this utility function

const shapeViolations2 = ref([
  { name: "PersonShape", violations: { "sh:minCount": 20, "sh:datatype": 10 }, totalViolations: 30, constraints: 10 },
  { name: "AddressShape", violations: { "sh:pattern": 5, "sh:datatype": 15, "sh:maxCount": 10 }, totalViolations: 30, constraints: 8 },
  { name: "OrganizationShape", violations: { "sh:minCount": 25 }, totalViolations: 25, constraints: 5 },
  { name: "EventShape", violations: { "sh:pattern": 10, "sh:minCount": 15, "sh:maxCount": 5 }, totalViolations: 30, constraints: 12 },
  { name: "ProductShape", violations: { "sh:datatype": 20, "sh:pattern": 10 }, totalViolations: 30, constraints: 9 },
  { name: "LocationShape", violations: { "sh:maxCount": 8, "sh:nodeKind": 5 }, totalViolations: 13, constraints: 7 },
  { name: "BuildingShape", violations: { "sh:minCount": 12, "sh:pattern": 8 }, totalViolations: 20, constraints: 8 },
  { name: "VehicleShape", violations: { "sh:datatype": 14, "sh:maxCount": 6 }, totalViolations: 20, constraints: 6 },
  { name: "CityShape", violations: { "sh:pattern": 10, "sh:minCount": 5, "sh:maxExclusive": 10 }, totalViolations: 25, constraints: 10 },
  { name: "CountryShape", violations: { "sh:minCount": 18, "sh:datatype": 12 }, totalViolations: 30, constraints: 9 },
  { name: "SchoolShape", violations: { "sh:pattern": 15, "sh:datatype": 10 }, totalViolations: 25, constraints: 7 },
  { name: "HospitalShape", violations: { "sh:minCount": 12, "sh:maxCount": 8 }, totalViolations: 20, constraints: 6 },
  { name: "AirportShape", violations: { "sh:nodeKind": 7, "sh:maxExclusive": 10 }, totalViolations: 17, constraints: 8 },
  { name: "UniversityShape", violations: { "sh:datatype": 25, "sh:pattern": 15 }, totalViolations: 40, constraints: 12 },
  { name: "LibraryShape", violations: { "sh:minCount": 10, "sh:datatype": 10 }, totalViolations: 20, constraints: 7 },
  { name: "ParkShape", violations: { "sh:pattern": 8, "sh:maxCount": 7 }, totalViolations: 15, constraints: 5 },
  { name: "MuseumShape", violations: { "sh:minCount": 15, "sh:nodeKind": 10 }, totalViolations: 25, constraints: 10 },
  { name: "BridgeShape", violations: { "sh:pattern": 12, "sh:datatype": 8 }, totalViolations: 20, constraints: 6 },
  { name: "RiverShape", violations: { "sh:minCount": 8, "sh:maxExclusive": 6 }, totalViolations: 14, constraints: 8 },
  { name: "StreetShape", violations: { "sh:nodeKind": 10, "sh:pattern": 5 }, totalViolations: 15, constraints: 6 },
  { name: "EmployeeShape", violations: { "sh:minCount": 2,  }, totalViolations: 5, constraints: 10 },
  { name: "DepartmentShape", violations: { "sh:datatype": 3 }, totalViolations: 3, constraints: 8 },
  { name: "ProjectShape", violations: { "sh:maxCount": 1 }, totalViolations: 1, constraints: 12 },
  { name: "TaskShape", violations: { "sh:pattern": 2 }, totalViolations: 4, constraints: 7 },
  { name: "TeamShape", violations: { "sh:nodeKind": 3 }, totalViolations: 3, constraints: 15 }
]);

const zeroViolationShapes = ref([
  { name: "CustomerShape", violations: {}, totalViolations: 0, constraints: 8 },
  { name: "OrderShape", violations: {}, totalViolations: 0, constraints: 6 },
  { name: "InvoiceShape", violations: {}, totalViolations: 0, constraints: 10 },
  { name: "ReceiptShape", violations: {}, totalViolations: 0, constraints: 7 },
  { name: "PaymentShape", violations: {}, totalViolations: 0, constraints: 9 },
  { name: "AccountShape", violations: {}, totalViolations: 0, constraints: 5 },
  { name: "VendorShape", violations: {}, totalViolations: 0, constraints: 6 },
  { name: "SupplierShape", violations: {}, totalViolations: 0, constraints: 8 },
  { name: "WarehouseShape", violations: {}, totalViolations: 0, constraints: 12 },
  { name: "InventoryShape", violations: {}, totalViolations: 0, constraints: 10 },
  { name: "LogisticsShape", violations: {}, totalViolations: 0, constraints: 11 },
  { name: "ShipmentShape", violations: {}, totalViolations: 0, constraints: 6 },
  { name: "RegionShape", violations: {}, totalViolations: 0, constraints: 9 },
  { name: "SectorShape", violations: {}, totalViolations: 0, constraints: 7 },
  { name: "DistrictShape", violations: {}, totalViolations: 0, constraints: 10 }
]);

const realViolations = ref([
{'violation_entropy': 0.39, 'num_violations': 729, 'num_constraints': 22}, 
{'violation_entropy': 0.0, 'num_violations': 718, 'num_constraints': 8}, 
{'violation_entropy': 0.18, 'num_violations': 1896, 'num_constraints': 65}, 
{'violation_entropy': 0.7, 'num_violations': 830, 'num_constraints': 25}, 
{'violation_entropy': 0.13, 'num_violations': 1203, 'num_constraints': 22}, 
{'violation_entropy': 0.0, 'num_violations': 1045, 'num_constraints': 17}, 
{'violation_entropy': 0.82, 'num_violations': 576, 'num_constraints': 25}, 
{'violation_entropy': 0.22, 'num_violations': 1283, 'num_constraints': 23}, 
{'violation_entropy': 0.4, 'num_violations': 384, 'num_constraints': 24}, 
{'violation_entropy': 0.2, 'num_violations': 1165, 'num_constraints': 27}, 
{'violation_entropy': 0.5, 'num_violations': 892, 'num_constraints': 55}, 
{'violation_entropy': 0.63, 'num_violations': 387, 'num_constraints': 24}, 
{'violation_entropy': 0.0, 'num_violations': 0, 'num_constraints': 16}, 
{'violation_entropy': 0.13, 'num_violations': 656, 'num_constraints': 15}, 
{'violation_entropy': 0.14, 'num_violations': 732, 'num_constraints': 22}, 
{'violation_entropy': 0.0, 'num_violations': 642, 'num_constraints': 21}, 
{'violation_entropy': 0.49, 'num_violations': 1452, 'num_constraints': 58}, 
{'violation_entropy': 0.04, 'num_violations': 997, 'num_constraints': 48}, 
{'violation_entropy': 0.45, 'num_violations': 1507, 'num_constraints': 75}, 
{'violation_entropy': 0.55, 'num_violations': 1086, 'num_constraints': 63}, 
{'violation_entropy': 0.18, 'num_violations': 968, 'num_constraints': 40}, 
{'violation_entropy': 0.24, 'num_violations': 1941, 'num_constraints': 38}, 
{'violation_entropy': 0.0, 'num_violations': 0, 'num_constraints': 22}, 
{'violation_entropy': 0.43, 'num_violations': 34, 'num_constraints': 19}, 
{'violation_entropy': 0.0, 'num_violations': 41, 'num_constraints': 20}, 
{'violation_entropy': 0.4, 'num_violations': 2379, 'num_constraints': 49}, 
{'violation_entropy': 0.29, 'num_violations': 2241, 'num_constraints': 29}, 
{'violation_entropy': 0.23, 'num_violations': 949, 'num_constraints': 24}, 
{'violation_entropy': 0.0, 'num_violations': 0, 'num_constraints': 39}, 
{'violation_entropy': 0.02, 'num_violations': 659, 'num_constraints': 32}])


const shapeViolations = computed(() => [...shapeViolations2.value, ...zeroViolationShapes.value]);


const coveragePlotData = computed(() => ({
  datasets: [
    {
      label: "Shapes",
      data: realViolations.value.map((shape) => ({
        x: shape.num_constraints,
        y: shape.num_violations / shape.num_constraints,
        label: "",
        hasZeroViolations: shape.num_violations === 0,
      }))
    },
  ],
}))


const scatterPlotData = computed(() => ({
  datasets: [
    {
      label: "Shapes",
      data: realViolations.value.map((shape) => ({
        x: shape.violation_entropy,
        y: shape.num_violations / shape.num_constraints,
        label: "",
      }))
    },
  ],
}));


// Router for navigation
const router = useRouter();

// Mock data for tags
const tags = [
  { title: "Total Node Shapes", value: 30 },
  { title: "Node Shapes with Violations (%)", value: "90%" },
  { title: "Max Violations per Node Shape", value: 2379 },
  { title: "Avg Violations per Node Shape", value: 913.07 },
];

const normalizedViolationBins = [0, 0.5, 1, 1.5, 2, 2.5, 3]; // Define bins for the histogram


const normalizedHistogramViolationData = ref({
  labels: ["0-8", "9-17", "18-26", "27-35", "36-44", "45-53", "54-62", "63-71", "72-80", "81-89"],
  datasets: [
    {
      label: "Violations",
      data: [5, 4, 6, 5, 3, 2, 3, 0, 1, 1],
      borderWidth: 1, // Optional: sets the border width of bars
    },
  ],
});



const normalizedHistogramData = {
  labels: normalizedViolationBins.map((bin, index) =>
    index < normalizedViolationBins.length - 1
      ? `${bin} - ${normalizedViolationBins[index + 1]}`
      : `${bin}+`
  ),
  datasets: [
    {
      label: "Normalized Violations",
      data: normalizedViolationBins.map((bin, index) => {
        const lowerBound = bin;
        const upperBound = normalizedViolationBins[index + 1] || Infinity;

        return shapeViolations.value.filter(
          (shape) =>
            shape.totalViolations / shape.constraints >= lowerBound &&
            shape.totalViolations / shape.constraints < upperBound
        ).length;
      })
    },
  ],
};

const columns = ref([
  { label: "Node Shape Name", field: "name" },
  { label: "Violations", field: "violations" },
  { label: "Number of Property Shapes", field: "propertyShapes" },
  { label: "Focus Nodes Affected", field: "focusNodes" },
  { label: "Property Paths", field: "propertyPaths" },
  { label: "Most Violated Constraint Component", field: "mostViolatedConstraint" },
  { label: "Violation-to-Constraint Ratio", field: "violationToConstraintRatio" },
]);

const shapes = ref([
  {'id': 26, 'name': 'shs:StadiumShape', 'violations': 2379, 'propertyPaths': 30, 'focusNodes': 118, 'mostViolatedConstraint': 'sh:InConstraintComponent', 'propertyShapes': 30, 'violationToConstraintRatio': 793.0}, 
  {'id': 1, 'name': 'shs:AmphibianShape', 'violations': 729, 'propertyPaths': 14, 'focusNodes': 50, 'mostViolatedConstraint': 'sh:InConstraintComponent', 'propertyShapes': 14, 'violationToConstraintRatio': 364.5},
  {'id': 2, 'name': 'shs:ComicStripShape', 'violations': 718, 'propertyPaths': 6, 'focusNodes': 42, 'mostViolatedConstraint': 'sh:InConstraintComponent', 'propertyShapes': 6, 'violationToConstraintRatio': 718.0}, 
  {'id': 3, 'name': 'shs:CongressmanShape', 'violations': 1896, 'propertyPaths': 48, 'focusNodes': 51, 'mostViolatedConstraint': 'sh:InConstraintComponent', 'propertyShapes': 48, 'violationToConstraintRatio': 948.0},
  {'id': 4, 'name': 'shs:ConiferShape', 'violations': 830, 'propertyPaths': 15, 'focusNodes': 50, 'mostViolatedConstraint': 'sh:InConstraintComponent', 'propertyShapes': 15, 'violationToConstraintRatio': 415.0}, 
  {'id': 5, 'name': 'shs:CricketTeamShape', 'violations': 1203, 'propertyPaths': 16, 'focusNodes': 53, 'mostViolatedConstraint': 'sh:InConstraintComponent', 'propertyShapes': 16, 'violationToConstraintRatio': 601.5},
  {'id': 7, 'name': 'shs:FernShape', 'violations': 576, 'propertyPaths': 15, 'focusNodes': 50, 'mostViolatedConstraint': 'sh:InConstraintComponent', 'propertyShapes': 15, 'violationToConstraintRatio': 288.0}, 
  {'id': 8, 'name': 'shs:FootballMatchShape', 'violations': 1283, 'propertyPaths': 16, 'focusNodes': 86, 'mostViolatedConstraint': 'sh:InConstraintComponent', 'propertyShapes': 16, 'violationToConstraintRatio': 427.67}, 
  {'id': 9, 'name': 'shs:GolfLeagueShape', 'violations': 384, 'propertyPaths': 12, 'focusNodes': 17, 'mostViolatedConstraint': 'sh:InConstraintComponent', 'propertyShapes': 12, 'violationToConstraintRatio': 192.0},
  {'id': 10, 'name': 'shs:HockeyTeamShape', 'violations': 1165, 'propertyPaths': 19, 'focusNodes': 53, 'mostViolatedConstraint': 'sh:InConstraintComponent', 'propertyShapes': 19, 'violationToConstraintRatio': 388.33}
]);

const shapes2 = ref([
  {'id': 11, 'name': 'shs:HospitalShape', 'violations': 892, 'propertyPaths': 34, 'focusNodes': 63, 'mostViolatedConstraint': 'sh:InConstraintComponent', 'propertyShapes': 34, 'violationToConstraintRatio': 446.0},
  {'id': 12, 'name': 'shs:MossShape', 'violations': 387, 'propertyPaths': 15, 'focusNodes': 51, 'mostViolatedConstraint': 'sh:InConstraintComponent', 'propertyShapes': 15, 'violationToConstraintRatio': 129.0},
  {'id': 13, 'name': 'shs:NetballPlayerShape', 'violations': 0, 'propertyPaths': 12, 'focusNodes': 0, 'mostViolatedConstraint': '', 'propertyShapes': 12, 'violationToConstraintRatio': 0.0}, 
  {'id': 14, 'name': 'shs:RacecourseShape', 'violations': 656, 'propertyPaths': 10, 'focusNodes': 32, 'mostViolatedConstraint': 'sh:InConstraintComponent', 'propertyShapes': 10, 'violationToConstraintRatio': 328.0}, 
  {'id': 15, 'name': 'shs:RadioHostShape', 'violations': 732, 'propertyPaths': 14, 'focusNodes': 21, 'mostViolatedConstraint': 'sh:InConstraintComponent', 'propertyShapes': 14, 'violationToConstraintRatio': 366.0}, 
  {'id': 16, 'name': 'shs:RoadJunctionShape', 'violations': 642, 'propertyPaths': 15, 'focusNodes': 49, 'mostViolatedConstraint': 'sh:InConstraintComponent', 'propertyShapes': 15, 'violationToConstraintRatio': 642.0}, 
  {'id': 17, 'name': 'shs:RoadShape', 'violations': 1452, 'propertyPaths': 40, 'focusNodes': 89, 'mostViolatedConstraint': 'sh:InConstraintComponent', 'propertyShapes': 40, 'violationToConstraintRatio': 484.0}, 
  {'id': 18, 'name': 'shs:SeaShape', 'violations': 997, 'propertyPaths': 29, 'focusNodes': 51, 'mostViolatedConstraint': 'sh:InConstraintComponent', 'propertyShapes': 29, 'violationToConstraintRatio': 498.5}, 
  {'id': 19, 'name': 'shs:ShipShape', 'violations': 1507, 'propertyPaths': 44, 'focusNodes': 75, 'mostViolatedConstraint': 'sh:InConstraintComponent', 'propertyShapes': 44, 'violationToConstraintRatio': 376.75}, 
  {'id': 20, 'name': 'shs:ShoppingMallShape', 'violations': 1086, 'propertyPaths': 38, 'focusNodes': 53, 'mostViolatedConstraint': 'sh:InConstraintComponent', 'propertyShapes': 38, 'violationToConstraintRatio': 543.0}
])

const shapes3 = ref([
{'id': 21, 'name': 'shs:SnookerChampShape', 'violations': 968, 'propertyPaths': 22, 'focusNodes': 31, 'mostViolatedConstraint': 'sh:InConstraintComponent', 'propertyShapes': 22, 'violationToConstraintRatio': 484.0}, 
{'id': 22, 'name': 'shs:SnookerPlayerShape', 'violations': 1941, 'propertyPaths': 21, 'focusNodes': 80, 'mostViolatedConstraint': 'sh:InConstraintComponent', 'propertyShapes': 21, 'violationToConstraintRatio': 647.0}, 
{'id': 23, 'name': 'shs:SnookerWorldRankingShape', 'violations': 0, 'propertyPaths': 9, 'focusNodes': 0, 'mostViolatedConstraint': '', 'propertyShapes': 9, 'violationToConstraintRatio': 0.0}, 
{'id': 24, 'name': 'shs:SoftballLeagueShape', 'violations': 34, 'propertyPaths': 10, 'focusNodes': 2, 'mostViolatedConstraint': 'sh:InConstraintComponent', 'propertyShapes': 10, 'violationToConstraintRatio': 17.0}, 
{'id': 25, 'name': 'shs:SpeedwayLeagueShape', 'violations': 41, 'propertyPaths': 10, 'focusNodes': 2, 'mostViolatedConstraint': 'sh:InConstraintComponent', 'propertyShapes': 10, 'violationToConstraintRatio': 41.0}, 
{'id': 6, 'name': 'shs:DartsPlayerShape', 'violations': 1045, 'propertyPaths': 11, 'focusNodes': 50, 'mostViolatedConstraint': 'sh:InConstraintComponent', 'propertyShapes': 11, 'violationToConstraintRatio': 1045.0},  
{'id': 27, 'name': 'shs:SumoWrestlerShape', 'violations': 2241, 'propertyPaths': 17, 'focusNodes': 89, 'mostViolatedConstraint': 'sh:InConstraintComponent', 'propertyShapes': 17, 'violationToConstraintRatio': 1120.5}, 
{'id': 28, 'name': 'shs:TennisTournamentShape', 'violations': 949, 'propertyPaths': 17, 'focusNodes': 73, 'mostViolatedConstraint': 'sh:InConstraintComponent', 'propertyShapes': 17, 'violationToConstraintRatio': 316.33}, 
{'id': 29, 'name': 'shs:TenureShape', 'violations': 0, 'propertyPaths': 32, 'focusNodes': 0, 'mostViolatedConstraint': '', 'propertyShapes': 32, 'violationToConstraintRatio': 0.0}, 
{'id': 30, 'name': 'shs:TunnelShape', 'violations': 659, 'propertyPaths': 20, 'focusNodes': 41, 'mostViolatedConstraint': 'sh:InConstraintComponent', 'propertyShapes': 20, 'violationToConstraintRatio': 329.5}

])
const currentPage = ref(1);
const pageSize = ref(10);
const totalPages = computed(() => Math.ceil(shapes.value.length / pageSize.value));

const paginatedData = computed(() => {
  const start = (currentPage.value - 1) * pageSize.value;
  return shapes.value.slice(start, start + pageSize.value);
});

const sortedPaginatedData = computed(() => {
  const data = paginatedData.value;
  if (sortKey.value) {
    return [...data].sort((a, b) => {
      const result = a[sortKey.value].toString().localeCompare(b[sortKey.value].toString(), undefined, { numeric: true });
      return sortOrder.value === "asc" ? result : -result;
    });
  }
  return data;
});

const prevPage = () => {
  if (currentPage.value > 1) currentPage.value--;
};

const nextPage = () => {
  if (currentPage.value < totalPages.value) currentPage.value++;
};

const goToShape = (shape) => {
  router.push({ name: "ShapeView", params: { shapeId: shape.id } });
};

const sortKey = ref("");
const sortOrder = ref("asc");

const sortColumn = (column) => {
  if (sortKey.value === column.field) {
    sortOrder.value = sortOrder.value === "asc" ? "desc" : "asc";
  } else {
    sortKey.value = column.field;
    sortOrder.value = "asc";
  }
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
