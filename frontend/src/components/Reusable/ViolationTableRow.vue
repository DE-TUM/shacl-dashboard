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
    <td colspan="2" class="details-cell text-left align-top px-6 py-4 border-b border-gray-300 text-gray-800 font-medium cursor-pointer">
      <div>
        <div class="text-left text-xl font-semibold text-gray-700 mb-3">
          <strong>Full Validation Details:</strong>
        </div>
        <!-- Convert details list into a table -->
        <table class="w-full border-collapse">
          <tbody>
            <tr v-if="focusNode">
              <td class="font-bold pr-4">Focus Node:</td>
              <td>{{ focusNode }}</td>
            </tr>
            <tr v-if="resultPath">
              <td class="font-bold pr-4">Result Path:</td>
              <td>{{ resultPath }}</td>
            </tr>
            <tr v-if="value">
              <td class="font-bold pr-4">Value:</td>
              <td>{{ value }}</td>
            </tr>
            <tr v-if="message">
              <td class="font-bold pr-4">Message:</td>
              <td>{{ message }}</td>
            </tr>
            <tr v-if="propertyShape">
              <td class="font-bold pr-4">Property Shape:</td>
              <td>{{ propertyShape }}</td>
            </tr>
            <tr v-if="severity">
              <td class="font-bold pr-4">Severity:</td>
              <td>{{ severity }}</td>
            </tr>
            <tr v-if="targetClass && targetClass.length > 0">
              <td class="font-bold pr-4">Target Class:</td>
              <td>{{ targetClass }}</td>
            </tr>
            <tr v-if="targetNode && targetNode.length > 0">
              <td class="font-bold pr-4">Target Node:</td>
              <td>{{ targetNode }}</td>
            </tr>
            <tr v-if="targetSubjectsOf && targetSubjectsOf.length > 0">
              <td class="font-bold pr-4">Target Subjects of:</td>
              <td>{{ targetSubjectsOf }}</td>
            </tr>
            <tr v-if="targetObjectsOf && targetObjectsOf.length > 0">
              <td class="font-bold pr-4">Target Objects of:</td>
              <td>{{ targetObjectsOf }}</td>
            </tr>
            <tr v-if="nodeShape">
              <td class="font-bold pr-4">Node Shape:</td>
              <td>{{ nodeShape }}</td>
            </tr>
            <tr v-if="constraintComponent">
              <td class="font-bold pr-4">Constraint Component:</td>
              <td>{{ constraintComponent }}</td>
            </tr>
          </tbody>
        </table>
      </div>
    </td>
    <td colspan="2" class="details-cell text-right align-top px-6 py-4 border-b border-gray-300 text-gray-800 font-medium cursor-pointer">
      <div>
        <div class="text-left text-xl font-semibold text-gray-700 mb-3">
          <strong>Shape Details:</strong>
        </div>
          <p><strong>Shape:</strong> {{ shapes.shape || "None" }}</p>
          <p><strong>Type:</strong> {{ shapes.type || "None" }}</p>
          <div class="details-list">
            <!-- Iterate over the Properties array -->
            <div v-if="shapes.properties.length > 0">
              <strong>Property Shapes Details:</strong>
              <ul class="ml-6">
                <li v-for="(property, index) in shapes.properties" :key="index">
                  <p><strong>{{ property.predicate }}:</strong> 
                    <span v-if="Array.isArray(property.object)">
                      <ul>
                        <li v-for="(obj, idx) in property.object" :key="idx">{{ obj }}</li>
                      </ul>
                    </span>
                    <span v-else>&nbsp; {{ property.object }}</span>
                  </p>
                  <p class="my-2" />
                </li>
              </ul>
            </div>
            <p v-else>No properties available.</p>
            <p><strong>Target Class:</strong> {{ shapes.targetClass || "None" }}</p>
        </div> 
      </div>
    </td>
  </tr>
</template>

<script setup>
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

const toggleDetails = () => {
  showDetails.value = !showDetails.value;
};
</script>

<style scoped>
table {
  width: 100%;
  border-collapse: collapse; /* Ensures no extra spacing */
}

td,th {
  padding: 1px 1px; /* Reduce padding inside cells */
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
