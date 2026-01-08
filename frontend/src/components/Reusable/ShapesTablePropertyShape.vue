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
            <table class="w-full border-collapse table-auto">
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
    </tr  v-if="showDetails">
  </template>
  
  <script setup>
/**
 * ShapesTablePropertyShape component
 *
 * Renders an expandable row for property shape information with associated validation results.
 * Shows property shape statistics with the ability to expand for detailed validation information.
 *
 * @example
 * // Basic usage in a parent component template:
 * // <ShapesTablePropertyShape
 * //   :rowNumber="1"
 * //   propertyShapeName="ex:nameShape"
 * //   :numberOfViolations="5"
 * //   :numberOfConstraints="3"
 * //   mostViolatedConstraint="sh:pattern"
 * // />
 *
 * @prop {Number} rowNumber - The sequential number for this row
 * @prop {String} propertyShapeName - The name of the property shape
 * @prop {Number} numberOfViolations - Count of violations for this property shape
 * @prop {Number} numberOfConstraints - Count of constraints in this property shape
 * @prop {String} mostViolatedConstraint - The most frequently violated constraint
 *
 * @dependencies
 * - vue (Composition API)
 * - ./ShapeTableRow.vue - For rendering detailed validation rows
 *
 * @style
 * - Interactive row with hover effects and expandable details.
 * - Nested table for displaying detailed violations.
 * - Triangle indicators showing expansion state.
 * 
 * @returns {HTMLElement} Two table rows: a main row showing property shape statistics, and
 * an expandable details row that appears when clicked, containing a nested table with
 * comprehensive validation results for the property shape including all affected triples.
 */
  import { defineProps, ref, onMounted } from 'vue';
  import ShapeTableRow from './ShapeTableRow.vue'; // Import the ShapeTableRow component

  const props = defineProps({
    rowNumber: Number,
    propertyShapeName: String,
    numberOfViolations: Number,
    numberOfConstraints: Number,
    mostViolatedConstraint: String,
    });
  
  // Define the props to receive data from the parent component
  const loadPropertyShapes = async () => {
    try {
        const response = await fetch('./../reports/example.json');
        if (response.ok) {
        const propertyShapesData = await response.json();

        // Map the JSON data into the desired structure
        tableData.value = propertyShapesData.map((shape) => ({
            propertyShapeName: shape.property_shape_name,
            numberOfViolations: shape.number_of_violations,
            numberOfConstraints: shape.number_of_constraints,
            mostViolatedConstraint: shape.most_violated_constraint,
        }));

        console.log("Mapped Property Shapes Data:", tableData.value); // Debug log
        } else {
        console.error('Failed to fetch property shapes data. Response not OK.');
        }
    } catch (error) {
        console.error('Error fetching property shapes data:', error);
    }
    };
  
  const showDetails = ref(false);
  
  // Toggle function for showing/hiding additional information
  const toggleDetails = (event) => {
    showDetails.value = !showDetails.value;
    event.stopPropagation(); // Prevent the row click from triggering the toggle
  };

  
  const tableData = ref([]);

  const loadJsonData = async () => {
    try {
      const response = await fetch('./../reports/result.json');
      if (response.ok) {
        const jsonData = await response.json();
        
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
