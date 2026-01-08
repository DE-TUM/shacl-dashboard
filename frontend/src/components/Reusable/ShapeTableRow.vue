<template>
  <tr class="even:bg-gray-50 hover:bg-blue-50 transition-colors" @click="toggleDetails" >
    <!-- Display the row number in the first column -->
    <td  class="text-left px-6 py-4 border-b border-gray-300">{{ rowNumber }}</td> <!-- Row number column -->

    <!-- Display the RDF Triple in a single cell -->
    <td class="text-left px-6 py-4 border-b border-gray-300">
      <span>{{ focusNode }}</span>
      <span>&nbsp;&nbsp;&nbsp;</span>
      <span>{{ resultPath }}</span>
      <span>&nbsp;&nbsp;&nbsp;</span>
      <span>{{ value }}</span>
    </td>
    
    <!-- Error message column -->
    <td  class="text-left px-6 py-4 border-b border-gray-300">  
      {{ message }} 
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
    <td colspan="4" class="details-cell text-left align-top px-6 py-4 border-b border-gray-300 bg-gray-100 rounded-md">
      <div>
        <div class="text-left text-xl font-semibold text-gray-700 mb-3">
          <strong>Full Validation Details:</strong>
        </div>
        <table class="w-full border-collapse">
          <tbody>
            <tr v-if="focusNode">
              <td class="font-bold pr-4">Focus Node:</td>
              <td class="text-gray-700">{{ focusNode }}</td>
            </tr>
            <tr v-if="resultPath">
              <td class="font-bold pr-4">Result Path:</td>
              <td class="text-gray-700">{{ resultPath }}</td>
            </tr>
            <tr v-if="value">
              <td class="font-bold pr-4">Value:</td>
              <td class="text-gray-700">{{ value }}</td>
            </tr>
            <tr v-if="message">
              <td class="font-bold pr-4">Message:</td>
              <td class="text-gray-700">{{ message }}</td>
            </tr>
            <tr v-if="propertyShape">
              <td class="font-bold pr-4">Property Shape:</td>
              <td class="text-gray-700">{{ propertyShape }}</td>
            </tr>
            <tr v-if="severity">
              <td class="font-bold pr-4">Severity:</td>
              <td class="text-gray-700">{{ severity }}</td>
            </tr>
            <tr v-if="targetClass && targetClass.length">
              <td class="font-bold pr-4">Target Class:</td>
              <td class="text-gray-700">{{ targetClass }}</td>
            </tr>
            <tr v-if="targetNode && targetNode.length">
              <td class="font-bold pr-4">Target Node:</td>
              <td class="text-gray-700">{{ targetNode }}</td>
            </tr>
            <tr v-if="targetSubjectsOf && targetSubjectsOf.length">
              <td class="font-bold pr-4">Target Subjects of:</td>
              <td class="text-gray-700">{{ targetSubjectsOf }}</td>
            </tr>
            <tr v-if="targetObjectsOf && targetObjectsOf.length">
              <td class="font-bold pr-4">Target Objects of:</td>
              <td class="text-gray-700">{{ targetObjectsOf }}</td>
            </tr>
            <tr v-if="nodeShape">
              <td class="font-bold pr-4">Node Shape:</td>
              <td class="text-gray-700">{{ nodeShape }}</td>
            </tr>
            <tr v-if="constraintComponent">
              <td class="font-bold pr-4">Constraint Component:</td>
              <td class="text-gray-700">{{ constraintComponent }}</td>
            </tr>
          </tbody>
        </table>
      </div>
    </td>
  </tr>
</template>

<script setup>
/**
 * ShapeTableRow component
 *
 * Renders an expandable row for SHACL shape details.
 * Shows basic shape info with the ability to expand for detailed validation information.
 *
 * @example
 * // Basic usage in a parent component template:
 * // <ShapeTableRow
 * //   :rowNumber="1"
 * //   focusNode="ex:Person1"
 * //   resultPath="ex:name"
 * //   value="John Doe"
 * //   message="Value does not match pattern"
 * // />
 *
 * @prop {Number} rowNumber - The sequential number for this row
 * @prop {String} focusNode - The focus node URI
 * @prop {String} resultPath - The property path
 * @prop {String|Number} value - The value
 * @prop {String} message - The validation message
 * @prop {String} propertyShape - The property shape URI
 * @prop {String} severity - The severity level
 * @prop {Object} shapes - Object containing shape details
 * @prop {String|Array} targetClass - The target class of the shape
 * @prop {String|Array} targetNode - The target node of the shape
 * @prop {String|Array} targetSubjectsOf - The target subjects of the shape
 * @prop {String|Array} targetObjectsOf - The target objects of the shape
 * @prop {String} nodeShape - The node shape URI
 * @prop {String} constraintComponent - The constraint component URI
 *
 * @dependencies
 * - vue (Composition API)
 *
 * @style
 * - Interactive row with hover effects and expandable details.
 * - Color-coded content with clear typography.
 * - Triangle indicators showing expansion state.
 * 
 * @returns {HTMLElement} Two table rows: a main row showing summary shape information, and
 * an expandable details row that appears when clicked, displaying comprehensive validation
 * details in a structured table format with consistent styling and indentation.
 */
import { defineProps, ref } from 'vue';

// Define the props to receive data from the parent component
const props = defineProps({
  rowNumber: Number,
  focusNode: String,
  resultPath: String,
  value: [String, Number],
  message: String,
  propertyShape: String,
  severity: String,
  shapes: Object,
  targetClass: [String, Array],
  targetNode: [String, Array],
  targetSubjectsOf: [String, Array],
  targetObjectsOf: [String, Array],
  nodeShape: String,
  constraintComponent: String,
});

const showDetails = ref(false);

// Toggle function for showing/hiding additional information
const toggleDetails = (event) => {
  showDetails.value = !showDetails.value;
  event.stopPropagation(); // Prevent the row click from triggering the toggle
};
</script>

<style scoped>
/* 📌 8️⃣ Table Enhancements */
table {
  width: 100%;
  border-collapse: collapse;
}

/* 📌 9️⃣ Reduced Padding for Compact View */
td, th {
  padding: 4px 8px;
}

/* 📌 1️⃣0️⃣ Toggle Button Styling */
.toggle-btn {
  background-color: transparent;
  border: none;
  font-size: 18px;
  cursor: pointer;
}

.toggle-btn:hover {
  color: #007bff;
}

/* 📌 1️⃣1️⃣ Triangle Icons for Expansion */
.triangle-left {
  display: inline-block;
  width: 0;
  height: 0;
  border-top: 5px solid transparent;
  border-bottom: 5px solid transparent;
  border-right: 7px solid black;
}

.triangle-down {
  display: inline-block;
  width: 0;
  height: 0;
  border-left: 5px solid transparent;
  border-right: 5px solid transparent;
  border-top: 7px solid black;
}

/* 📌 1️⃣2️⃣ Improved Details Section Styling */
.details-cell {
  background-color: #f9fafb;
  border-radius: 8px;
  padding: 12px;
}

/* 📌 1️⃣3️⃣ Better Readability for Expanded Content */
.text-gray-700 {
  color: #4a5568;
}

.font-bold {
  font-weight: 600;
}
</style>
