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
        :data="normalizedHistogramData"
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


const shapeViolations = computed(() => [...shapeViolations2.value, ...zeroViolationShapes.value]);


const coveragePlotData = computed(() => ({
  datasets: [
    {
      label: "Shapes",
      data: shapeViolations.value.map((shape) => ({
        x: shape.constraints,
        y: shape.totalViolations / shape.constraints,
        label: shape.name,
        hasZeroViolations: shape.totalViolations === 0,
      }))
    },
  ],
}))


const scatterPlotData = computed(() => ({
  datasets: [
    {
      label: "Shapes",
      data: shapeViolations.value.map((shape) => ({
        x: calculateShannonEntropy(shape.violations),
        y: shape.totalViolations / shape.constraints,
        label: shape.name,
      }))
    },
  ],
}));


// Router for navigation
const router = useRouter();

// Mock data for tags
const tags = [
  { title: "Total Node Shapes", value: 50 },
  { title: "Node Shapes with Violations (%)", value: "40%" },
  { title: "Max Violations per Node Shape", value: 100 },
  { title: "Avg Violations per Node Shape", value: 12.5 },
];

const normalizedViolationBins = [0, 0.5, 1, 1.5, 2, 2.5, 3]; // Define bins for the histogram

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
  { label: "Shape Name", field: "name" },
  { label: "Violations", field: "violations" },
  { label: "Number of Property Shapes", field: "propertyShapes" },
  { label: "Focus Nodes Affected", field: "focusNodes" },
  { label: "Property Paths", field: "propertyPaths" },
  { label: "Most Violated Constraint", field: "mostViolatedConstraint" },
  { label: "Violation-to-Constraint Ratio", field: "violationToConstraintRatio" },
]);

const shapes = ref([
  { id: 1, name: "PersonShape", violations: 42, propertyPaths: 12, focusNodes: 8, mostViolatedConstraint: "MaxLength", propertyShapes: 5, violationToConstraintRatio: 3.5},
  { id: 2, name: "AddressShape", violations: 18, propertyPaths: 7, focusNodes: 5, mostViolatedConstraint: "Pattern", propertyShapes: 3, violationToConstraintRatio: 2.6},
  { id: 3, name: "OrganizationShape", violations: 8, propertyPaths: 5, focusNodes: 3, mostViolatedConstraint: "MinCount", propertyShapes: 4, violationToConstraintRatio: 1.6},
  { id: 4, name: "EventShape", violations: 25, propertyPaths: 10, focusNodes: 7, mostViolatedConstraint: "MaxExclusive", propertyShapes: 6, violationToConstraintRatio: 2.5 },
  { id: 5, name: "ProductShape", violations: 15, propertyPaths: 9, focusNodes: 6, mostViolatedConstraint: "NodeKind", propertyShapes: 2, violationToConstraintRatio: 2.1 },
]);

const currentPage = ref(1);
const pageSize = ref(5);
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
