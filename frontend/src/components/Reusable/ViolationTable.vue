<template>
  <div class="bg-white border border-gray-200 p-6 rounded-lg shadow-lg relative">
    <div class="flex justify-between items-center">
      <div class="flex items-center gap-4">
        <h1 class="text-2xl font-bold text-gray-700 mb-4">Validation Results</h1>
        <button
          @click="togglePrefixes"
          class="px-2 py-1 bg-gray-300 text-gray-700 rounded hover:bg-gray-400 text-sm mb-4"
        >
          {{ showPrefixes ? 'Hide Prefixes' : 'Show Prefixes' }}
        </button>


      </div>
      <div class="flex gap-4">
        <button
          @click="toggleFilterBox"
          class="px-4 py-2 bg-blue-500 text-white rounded hover:bg-blue-600 mb-4"
        >
          Filter
        </button>
        <button
          @click="downloadCSV"
          class="px-2 py-1 bg-gray-500 text-white rounded hover:bg-gray-600 mb-4 flex items-center gap-2"
        >
          <font-awesome-icon :icon="['fas', 'download']" />
          Download CSV
        </button>
      </div>
    </div>

    <!-- Filter Box -->
    <div
      v-if="isFilterBoxVisible"
      class="absolute bg-white p-6 border shadow-lg rounded-lg z-50"
      style="top: 4.4rem; right: 1.5rem;"
    >
      <Filter
        :filters="filters"
        @update:filters="applyFilters"
        @set-options="setDropdownOptions"
        @reset="resetAllFilters"
      />
      <button 
          @click="toggleFilterBox" 
          class="mt-4 px-4 py-2 text-white font-medium rounded-lg shadow-md transition-all duration-200 
                bg-gray-500 border border-gray-600 hover:bg-gray-600 hover:border-gray-700 hover:shadow-lg"
          style="width: 250px;"
        >
          Close
        </button>
    </div>

    <!-- Table to display combined details and messages -->
    <table class="w-full border-collapse">
      <thead class="bg-gray-200">
        <tr>
          <th class="text-left px-4 py-2 border-b border-gray-300 text-gray-600 font-medium w-20">
            ID
          </th>
          <th class="text-left px-4 py-2 border-b border-gray-300 text-gray-600 font-medium w-1/3">
            Violated Triple
          </th>
          <th class="text-left px-4 py-2 border-b border-gray-300 text-gray-600 font-medium w-1/3">
            Error Message
          </th>
          <th class="text-left px-4 py-2 border-b border-gray-300 text-gray-600 font-medium w-20">
          </th>
        </tr>
      </thead>
      <tbody>
        <ViolationTableRow
          v-for="(item, index) in paginatedData"
          :key="index"
          :rowNumber="(currentPage - 1) * itemsPerPage + index + 1"
          v-bind="item"
        />
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
    <!-- Prefix List -->
    <div v-if="showPrefixes" class="bg-gray-100 p-4 rounded-lg mt-4">
        <h2 class="text-lg font-semibold text-gray-700 mb-2">Loaded Prefixes</h2>
        <ul class="list-disc pl-6 text-gray-600">
          <li v-for="(namespace, prefix) in prefixes" :key="prefix">
            <strong class="text-gray-800">{{ prefix }}:</strong> {{ namespace }}
          </li>
        </ul>
      </div>
  </div>
</template>

<script setup>
import { ref, computed, onMounted } from 'vue';
import ViolationTableRow from './ViolationTableRow.vue';
import Filter from './Filter.vue';

const tableData = ref([]);
const prefixes = ref({});
const shapes = ref([]);
const allData = ref([]);
const showFullPrefixes = ref(false); // Reactive toggle state

const currentPage = ref(1);
const itemsPerPage = 10;

const totalPages = computed(() => Math.ceil(allData.value.length / itemsPerPage));
const paginatedData = computed(() => {
  const start = (currentPage.value - 1) * itemsPerPage;
  return allData.value.slice(start, start + itemsPerPage);
});

const showPrefixes = ref(false);

const togglePrefixes = () => {
  showPrefixes.value = !showPrefixes.value;
};

const prevPage = () => {
  if (currentPage.value > 1) currentPage.value--;
};

const nextPage = () => {
  if (currentPage.value < totalPages.value) currentPage.value++;
};

const loadJsonData = async () => {
  try {
    const response = await fetch('./../reports/result.json');
    if (!response.ok) {
      throw new Error("Failed to fetch JSON");
    }
    
    const jsonData = await response.json();
    prefixes.value = jsonData["@prefixes"] || {}; 
    console.log("Loaded Prefixes:", prefixes.value);

    if (Object.keys(prefixes.value).length === 0) {
      console.warn("No prefixes found! URIs will not be transformed.");
    }

    const violations = jsonData.violations;

    allData.value = violations.map((violation) => {
      const details = Object.values(violation)[0].full_validation_details;
      const shapeDetails = Object.values(violation)[0].shape_details;

      console.log("Before Formatting:", details);

      const formattedData = {
        focusNode: formatURI(details.FocusNode),
        resultPath: formatURI(details.ResultPath),
        value: formatURI(details.Value),
        message: details.Message,
        propertyShape: formatURI(details.PropertyShape),
        severity: formatURI(details.Severity),
        targetClass: formatURI(details.TargetClass),
        targetNode: formatURI(details.TargetNode),
        targetSubjectsOf: formatURI(details.TargetSubjectsOf),
        targetObjectsOf: formatURI(details.TargetObjectsOf),
        nodeShape: formatURI(details.NodeShape),
        constraintComponent: formatURI(details.ConstraintComponent),
        shapes: {
          shape: formatURI(shapeDetails.Shape || ""),
          type: formatURI(shapeDetails.Type || ""),
          properties: Array.isArray(shapeDetails.Properties)
            ? shapeDetails.Properties
            .filter(item => 
              item.Predicate !== "http://www.w3.org/1999/02/22-rdf-syntax-ns#type" &&
              item.Predicate !== "http://rdfs.org/ns/void#entities"
            ) 
            .map(item => ({
              predicate: item.Predicate === "http://www.w3.org/ns/shacl#path" 
                ? "Property Path" // Replace sh:path with Property Path
                : formatURI(item.Predicate), // Format other predicates
                object: Array.isArray(item.Object) 
                  ? item.Object.map(formatURI) // Handle array of objects
                  : formatURI(item.Object) // Handle single object value
              }))
            : [],
          targetClass: formatURI(shapeDetails.TargetClass) ,
        },
      };

      console.log("After Formatting:", formattedData);

      return formattedData;
    });

    tableData.value = [...allData.value];
    console.log("Final Processed Data:", tableData.value);
  } catch (error) {
    console.error('Error fetching JSON data:', error);
  }
};


const formatURI = (uri) => {
  if (!uri || typeof uri !== "string") return uri; // Ensure valid input

  console.log("Processing URI:", uri);

  let matchedPrefix = null;
  let matchedNamespace = null;

  for (const [prefix, namespace] of Object.entries(prefixes.value)) {
    if (uri.startsWith(namespace) && (!matchedNamespace || namespace.length > matchedNamespace.length)) {
      matchedPrefix = prefix;
      matchedNamespace = namespace;
    }
  }

  if (matchedPrefix) {
    const transformedURI = `${matchedPrefix}:${uri.slice(matchedNamespace.length)}`;
    console.log(`Transformed "${uri}" → "${transformedURI}"`);
    return transformedURI;
  }

  console.log(`No match for "${uri}". Returning original.`);
  return uri; // Return as is if no prefix match
};

// Fetch data on mount
onMounted(async () => {
  await loadJsonData();
});

const downloadCSV = () => {
  if (!tableData.value.length) {
    alert("No data available to export.");
    return;
  }

  try {
    const headers = Object.keys(tableData.value[0]).join(",");
    const rows = tableData.value.map((row) =>
      Object.values(row)
        .map((value) => {
          if (typeof value === "string") {
            return `"${value.replace(/"/g, '""')}"`;
          } else if (Array.isArray(value)) {
            return `"${value.join("; ")}"`;
          }
          return value;
        })
        .join(",")
    );

    const csvContent = [headers, ...rows].join("\n");
    const blob = new Blob([csvContent], { type: "text/csv;charset=utf-8;" });
    const link = document.createElement("a");
    const url = URL.createObjectURL(blob);

    link.setAttribute("href", url);
    link.setAttribute("download", "ValidationResults.csv");
    link.style.visibility = "hidden";

    document.body.appendChild(link);
    link.click();
    document.body.removeChild(link);
  } catch (error) {
    console.error("Error generating CSV file:", error);
    alert("Failed to generate CSV file.");
  }
};

const isFilterBoxVisible = ref(false);
const filters = ref({
  dropdown1: [],
  dropdown2: [],
  dropdown3: [],
  dropdown4: [],
  options1: [],
  options2: [],
  options3: [],
  options4: [],
});

const toggleFilterBox = () => {
  isFilterBoxVisible.value = !isFilterBoxVisible.value;
};

const applyFilters = (updatedFilters) => {
  filters.value = { ...updatedFilters };
};

const resetAllFilters = () => {
  for (let i = 1; i <= 4; i++) {
    filters.value[`dropdown${i}`] = [];
  }
};

const setDropdownOptions = (options) => {
  filters.value = { ...filters.value, ...options };
};

</script>

<style scoped>
.grid-cols-4 {
  grid-template-columns: repeat(4, 1fr);
}

table {
  table-layout: fixed; /* Enforce fixed layout for consistent column widths */
  width: 100%; /* Ensure the table spans the full container width */
}


th,
td {
  padding: 12px;
}

tbody tr:hover {
  background-color: #f0f8ff;
}

tbody tr {
  cursor: pointer;
}

button:focus {
  outline: none;
}

td {
  white-space: nowrap;
  overflow: hidden;
  text-overflow: ellipsis;
}

/* Allow wrapping for long text */
td.wrap {
  white-space: normal;
  word-break: break-word;
}
</style>
