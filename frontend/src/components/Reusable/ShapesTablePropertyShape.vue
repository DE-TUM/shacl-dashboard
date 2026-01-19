<template>
    <tr class="even:bg-gray-50 hover:bg-blue-50 transition-colors" @click="toggleDetails" >
      <!-- Display the row number in the first column -->
      <td class="text-left px-6 py-4 border-b border-gray-300 font-medium text-gray-800">{{ propertyShapeName }}</td> <!-- Row number column -->
  
      <!-- Display the RDF Triple in a single cell -->
      <td class="text-left px-6 py-4 border-b border-gray-300">{{ numberOfViolations }}</td>
      
      <!-- Error message column -->
      <td  class="text-left px-6 py-4 border-b border-gray-300">  {{ numberOfConstraints }} </td>
      
    
      <td class="text-left px-6 py-4 border-b border-gray-300">
        {{ mostViolatedConstraint }}
      </td>

      <td class="text-right px-6 py-4 border-b border-gray-300">
        <button @click.stop="toggleDetails" class="toggle-btn">
            <span v-if="showDetails" class="triangle-down"></span>
            <span v-else class="triangle-left"></span>
            </button>
      </td>
      
    </tr>
    <!-- Show additional information when clicked -->
    <tr v-if="showDetails">
        <td colspan="5" class="details-cell text-left align-top px-6 py-4 border-b border-gray-300 text-gray-800 font-medium cursor-pointer">
            <h3 class="text-xl font-semibold text-gray-700 mb-3">Validation Results:</h3>
            
            <!-- Show message if no violations -->
            <div v-if="!hasViolations" class="text-gray-500 italic py-4">
              No violations found for this property shape.
            </div>
            
            <!-- Show violations table if violations exist -->
            <table v-else class="w-full border-collapse table-auto">
                <!-- Table Header Row -->
                <thead class="bg-gray-200 w-full">
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
        
                <!-- Table Body with Items -->
                <tbody>
                <ShapeTableRow 
                    v-for="(item, index) in tableData"
                    :key="index"
                    :rowNumber="index + 1"
                    :focusNode="item.focusNode"
                    :resultPath="item.resultPath"
                    :value="item.value"
                    :message="item.message"
                    :propertyShape="item.propertyShape"
                    :severity="item.severity"
                    :targetClass="item.targetClass"
                    :targetNode="item.targetNode"
                    :targetSubjectsOf="item.targetSubjectsOf"
                    :targetObjectsOf="item.targetObjectsOf"
                    :nodeShape="item.nodeShape"
                    :constraintComponent="item.constraintComponent"
                    />
                </tbody>
            </table>
        </td>
    </tr>
  </template>
  
  <script setup>
  /**
   * Property Shape Table Component
   * 
   * Displays a row in the property shapes table with expandable violation details.
   * Each row shows summary statistics and can be expanded to show detailed violations.
   * 
   * @prop {string} propertyShapeName - Name/URI of the property shape
   * @prop {number} numberOfViolations - Total violations for this property shape
   * @prop {number} numberOfConstraints - Total constraints for this property shape
   * @prop {string} mostViolatedConstraint - Most frequently violated constraint
   * @prop {Array} violations - Array of detailed violation objects
   */
  import ShapeTableRow from './ShapeTableRow.vue';
  import { ref, computed, onMounted } from 'vue';

  // Define props
  const props = defineProps({
    propertyShapeName: {
      type: String,
      required: true
    },
    numberOfViolations: {
      type: Number,
      required: true
    },
    numberOfConstraints: {
      type: Number,
      required: true
    },
    mostViolatedConstraint: {
      type: String,
      required: true
    },
    violations: {
      type: Array,
      default: () => []
    }
  });

  const showDetails = ref(false);
  
  // Toggle function for showing/hiding additional information
  const toggleDetails = (event) => {
    showDetails.value = !showDetails.value;
    event.stopPropagation(); // Prevent the row click from triggering the toggle
  };

  // Map violations prop directly to table data
  const tableData = computed(() => {
    return props.violations.map((violation, index) => ({
      id: index + 1,
      focusNode: violation.focusNode,
      resultPath: violation.resultPath,
      value: violation.value,
      message: violation.message,
      propertyShape: violation.propertyShape,
      severity: violation.severity,
      targetClass: violation.targetClass || null,
      targetNode: violation.targetNode || null,
      targetSubjectsOf: violation.targetSubjectsOf || null,
      targetObjectsOf: violation.targetObjectsOf || null,
      nodeShape: violation.nodeShape || null,
      constraintComponent: violation.constraintComponent || null,
    }));
  });

  // Computed property to track if there are violations to display
  const hasViolations = computed(() => props.violations.length > 0);
  </script>
  
  <style scoped>
  td,th {
    padding: 12px;
  }
  
  div {
    text-align: left;
  }
  
  tr {
    cursor: pointer;
  }
  
  tr:hover {
    background-color: #f0f8ff;
  }
  
  /* Styling for the toggle button */
  .toggle-column {
    text-align: right;
  }
  
  .toggle-btn {
    background-color: transparent;
    border: none;
    font-size: 20px;
    cursor: pointer;
  }
  
  .toggle-btn:hover {
    color: #007bff;
  }
  
  /* Symbols for toggle: triangle left and down */
  .triangle-left {
    display: inline-block;
    width: 0;
    height: 0;
    border-top: 5px solid transparent;
    border-bottom: 5px solid transparent;
    border-right: 7px solid black; /* Left triangle */
  }
  
  .triangle-down {
    display: inline-block;
    width: 0;
    height: 0;
    border-left: 5px solid transparent;
    border-right: 5px solid transparent;
    border-top: 7px solid black; /* Downward triangle */
  }
  
  
  .details-cell {
    background-color: #f9fafb; /* Light gray background for better contrast */
    border-radius: 8px; /* Rounded corners for a smoother look */
  }
  
  .details-list p {
    font-size: 0.9rem;
    line-height: 1.5;
    color: #4a5568;
    margin-bottom: 8px;
  }
  
  .details-list strong {
    color: #2d3748; /* Darker text color for labels */
  }
  
  .shape-details {
    padding: 12px;
    font-size: 0.85rem;
    border-radius: 6px;
    white-space: pre-wrap;
    word-break: break-word;
  }
  
  .text-xl {
    font-size: 1.25rem; /* Slightly larger font for headings */
  }
  
  .font-semibold {
    font-weight: 600; /* Semi-bold for better emphasis */
  }
  
  .text-gray-700 {
    color: #4a5568; /* Darker text for better contrast */
  }
  
  .text-gray-800 {
    color: #2d3748; /* Even darker for important text */
  }
  
  .mb-3 {
    margin-bottom: 16px; /* Adds space after headings */
  }
  
  .cursor-pointer:hover {
    background-color: #f0f4f8; /* Subtle hover effect */
  }
  
  
  .details-list p {
    font-size: 0.9rem;
    line-height: 1.5;
    margin-bottom: 4px;
  }
  
  .details-list ul {
    padding-left: 1.5rem;
  }
  
  .details-list strong {
    color: #2d3748;
  }
  </style>
