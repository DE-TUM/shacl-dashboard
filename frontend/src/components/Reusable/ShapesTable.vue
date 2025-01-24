<template>
  <div class="bg-white border border-gray-200 p-6 rounded-lg shadow-lg relative">
    <div class="flex justify-between items-center">
      <div class="flex items-center gap-4">
        <h2 class="text-2xl font-bold text-gray-700 mb-4">Property Shapes Overview</h2>
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
  
    <div>
      
      <!-- Property Shapes Table -->
        <table class="w-full border-collapse">
          <thead class="bg-gray-200">
            <tr>
              <th class="text-left px-4 py-2 border-b border-gray-300 text-gray-600 font-medium w-1/4">
                Property Shape Name
              </th>
              <th class="text-left px-4 py-2 border-b border-gray-300 text-gray-600 font-medium w-1/4">
                Number of Violations
              </th>
              <th class="text-left px-4 py-2 border-b border-gray-300 text-gray-600 font-medium w-1/4">
                Number of Constraints
              </th>
              <th class="text-left px-4 py-2 border-b border-gray-300 text-gray-600 font-medium w-1/4">
                Most Violated Constraint
              </th>
              <th class="text-left px-4 py-2 border-b border-gray-300 text-gray-600 font-medium w-1/4">
                
              </th>
            </tr>
          </thead><!-- Table Body with Items -->
            <tbody>
              <ShapesTablePropertyShape
              v-for="(shape, index) in tablesData"
              :key="index"
              :rowNumber="index + 1"
              :propertyShapeName="shape.propertyShapeName"
              :numberOfViolations="shape.numberOfViolations"
              :numberOfConstraints="shape.numberOfConstraints"
              :mostViolatedConstraint="shape.mostViolatedConstraint"
            />
            </tbody>
        </table>
    </div>
    
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
  import { ref, onMounted } from 'vue';
  import * as rdf from 'rdflib'; // Import rdflib.js
  import ShapeTableRow from './ShapeTableRow.vue'; // Import the ShapeTableRow component
  import ShapesTablePropertyShape from './ShapesTablePropertyShape.vue'; // Import the ShapeTableRow component
  import Filter from './Filter.vue';
  
  // Define table data and prefixes
  const tableData = ref([]);
  const tablesData = ref([]);
  const prefixes = ref({});
  
  const shapes = ref([]);

 // Data for Property Shapes
  const propertyShapes = ref([]);
  const expandedIndex = ref(null);

  // Load property shapes data from JSON file
  const loadPropertyShapes = async () => {
    try {
      // Fetch data from property-shapes.json
      const response = await fetch('./../reports/propertyShapes.json');
      if (response.ok) {
        const jsonData = await response.json();

        // Map the data to the required format
        tablesData.value = jsonData.map((shape) => ({
          propertyShapeName: shape.property_shape_name,
          numberOfViolations: shape.number_of_violations,
          numberOfConstraints: shape.number_of_constraints,
          mostViolatedConstraint: shape.most_violated_constraint,
        }));

        console.log("Loaded Property Shapes Data:", tablesData.value); // Debug log
      } else {
        console.error('Failed to fetch property-shapes.json. Response not OK.');
      }
    } catch (error) {
      console.error('Error fetching property-shapes.json:', error);
    }
  };

  // Fetch data when the component is mounted
  onMounted(async () => {
    await loadPropertyShapes();
  });

  // Toggle the visibility of details for a specific row
  const toggleDetails = (index) => {
  console.log('Toggling details for index:', index); // Debugging
  expandedIndex.value = expandedIndex.value === index ? null : index;
};

  // Fetch property shapes data on mount
  onMounted(async () => {
    await loadPropertyShapes();
  });
  /**
   * Load data from `example.json` and map it to the component's state.
   */
  const loadJsonData = async () => {
    try {
      const response = await fetch('./../reports/example.json');
      if (response.ok) {
        const jsonData = await response.json();

          
        // Extract prefixes **first**
        prefixes.value = jsonData["@prefixes"] || {}; 
        console.log("Loaded Prefixes:", prefixes.value);

        const violations = jsonData.violations;

        tableData.value = violations.map((violation, index) => {
          const details = Object.values(violation)[0].full_validation_details;
          const shapeDetails = Object.values(violation)[0].shape_details;

          console.log("Details:", details); // Debug log
          console.log("Shape Details:", shapeDetails); // Debug log

          return {
            focusNode: details.FocusNode,
            resultPath: details.ResultPath,
            value: details.Value,
            message: details.Message,
            propertyShape: details.PropertyShape,
            severity: details.Severity,
            targetClass: details.TargetClass || [], // Add fallback for missing values
            targetNode: details.TargetNode || [],
            targetSubjectsOf: details.TargetSubjectsOf || [],
            targetObjectsOf: details.TargetObjectsOf || [],
            nodeShape: details.NodeShape || "",
            constraintComponent: details.ConstraintComponent || "",
            shapes: {
              shape: shapeDetails.Shape || "",
              type: shapeDetails.Type || "",
              properties: shapeDetails.Properties || [],
              targetClass: shapeDetails.TargetClass || [],
            },
          };
        });

        console.log("Mapped Table Data:", tableData.value); // Debug log
      } else {
        console.error('Failed to load JSON data.');
      }
    } catch (error) {
      console.error('Error fetching JSON data:', error);
    }
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
    link.setAttribute("download", "ShapesOverview.csv");
    link.style.visibility = "hidden";

    document.body.appendChild(link);
    link.click();
    document.body.removeChild(link);
  } catch (error) {
    console.error("Error generating CSV file:", error);
    alert("Failed to generate CSV file.");
  }
};
  
  // Function to replace full URI with prefix
  const replacePrefix = (uri) => {
    for (const prefix in prefixes.value) {
      if (uri.startsWith(prefixes.value[prefix])) {
        return uri.replace(prefixes.value[prefix], `${prefix}:`);
      }
    }
    return uri; // If no prefix found, return the URI as is
  };

  const showFullPrefixes = ref(false); // State to track prefix expansion

  const formatURI = (uri) => {
  if (!uri) return uri; // Skip null or undefined values

  if (showFullPrefixes.value) {
    // Convert prefixed URI to full URI
    const [prefix, localName] = uri.split(":");
    if (prefixes.value[prefix]) {
      return `${prefixes.value[prefix]}${localName}`;
    }
    return uri; // Return as is if no match
  } else {
    // Convert full URI to prefixed form
    const matchedPrefix = Object.entries(prefixes.value).find(([_, namespace]) =>
      uri.startsWith(namespace)
    );
    if (matchedPrefix) {
      const [prefix, namespace] = matchedPrefix;
      return `${prefix}:${uri.replace(namespace, "")}`;
    }
    return uri; // Return as is if no match
  }
};

const showPrefixes = ref(false);

const togglePrefixes = () => {
  showPrefixes.value = !showPrefixes.value;
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
  
  th, td {
    padding: 12px;
  }
  
  tbody tr:hover {
    background-color: #f0f8ff;
  }
  
  tbody tr {
    cursor: pointer;
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
  