<template>
  <div class="constraint-overview p-4">
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
        <div class="flex items-center justify-center bg-gray-200 rounded-full w-12 h-12">
          <!-- Replace with a relevant icon -->
          <font-awesome-icon :icon="['fas', 'chart-bar']" class="text-gray-600" />
        </div>
      </div>
    </div>

    <!-- Plots Section -->
    <div class="grid grid-cols-3 gap-4 mb-4">
      <BarChart
        :title="'Violations by Constraint Type'"
        :xAxisLabel="'Constraint Types'"
        :yAxisLabel="'Number of Violations'"
        :data="violationsByConstraintType"
      />

      <!-- Usage Distribution -->
      <PieChart
        :title="'Usage Distribution'"
        :data="usageDistributionData"
        :categories="usageLabels"
      />

      <!-- Violation Distribution by Constraint Component -->
      <HistogramChart
        :title="'Violation Distribution by Constraint Component'"
        :xAxisLabel="'Violation Count'"
        :yAxisLabel="'Number of Constraint Components'"
        :data="histogramData"
      />

    </div>

    <!-- Generate Tables for Each Category -->
    <div v-for="category in uniqueCategories" :key="category" class="category-section mb-4">

      <div class="bg-white border border-gray-200 p-6 rounded-lg shadow-lg">
        <h2 class="text-2xl font-bold text-gray-700 mb-4">{{ category }}</h2>
        <table class="w-full border-collapse table-fixed">
          <thead class="bg-gray-200">
            <tr>
              <th class="text-left px-6 py-3 border-b border-gray-300 text-gray-600 font-medium w-1/4">
                Constraint Name
              </th>
              <th class="text-left px-6 py-3 border-b border-gray-300 text-gray-600 font-medium w-1/3">
                Description
              </th>
              <th class="text-left px-6 py-3 border-b border-gray-300 text-gray-600 font-medium w-1/6">
                Severity
              </th>
              <th class="text-left px-6 py-3 border-b border-gray-300 text-gray-600 font-medium w-1/6">
                Number of Violations
              </th>
              <th class="text-center px-6 py-3 border-b border-gray-300 text-gray-600 font-medium w-1/12"></th>
            </tr>
          </thead>
          <tbody>
            <tr
              v-for="constraint in constraintsByCategory(category)"
              :key="constraint.id"
              class="even:bg-gray-50 hover:bg-blue-50 transition-colors"
              @click="goToConstraintView(constraint)"
            >
              <td class="px-6 py-4 border-b border-gray-300">{{ constraint.name }}</td>
              <td class="px-6 py-4 border-b border-gray-300">{{ constraint.description }}</td>
              <td class="px-6 py-4 border-b border-gray-300">{{ constraint.severity }}</td>
              <td class="px-6 py-4 border-b border-gray-300">{{ constraint.violations }}</td>
              <td class="px-6 py-4 border-b border-gray-300 text-center">
                <button class="text-blue-600 hover:text-blue-800">
                  <font-awesome-icon icon="arrow-right" />
                </button>
              </td>
            </tr>
          </tbody>
        </table>
      </div>
    </div>
  </div>
</template>

<script setup>
/**
 * ConstraintOverview component
 *
 * Provides a comprehensive overview of SHACL constraints in the dataset.
 * Displays statistics, visualizations, and listings of constraints with their usage and violations.
 *
 * @example
 * // Basic usage in a parent component template:
 * // <ConstraintOverview />
 *
 * @prop {Array} [constraints=[]] - List of constraints to display
 * @prop {Boolean} [showViolations=true] - Whether to show violation data
 * @prop {Boolean} [showCharts=true] - Whether to show visualization charts
 *
 * @dependencies
 * - vue (Composition API)
 * - ../Charts/GroupedBarChart.vue
 * - ../ConstraintView/Metrics.vue
 *
 * @style
 * - Responsive layout with cards and data tables.
 * - Data visualization components for constraint statistics.
 * - Filterable and sortable constraint listings.
 * 
 * @returns {HTMLElement} A dashboard page showing constraint statistics in summary cards at the 
 * top, data visualizations in the middle (bar chart, pie chart, and histogram), and a categorized 
 * table listing all constraints with their properties and violation counts at the bottom.
 */
// Importing components
import BarChart from './../Charts/BarChart.vue';
import PieChart from './../Charts/PieChart.vue';
import HistogramChart from './../Charts/HistogramChart.vue';
import { ref, computed } from 'vue';
import { useRouter } from 'vue-router';

// Router for navigation
const router = useRouter();

// Full constraints data
const constraints = ref([
  { id: 1, name: 'sh:class', description: 'Ensures that the value is an instance of a specified class.', violations: 3 },
  { id: 2, name: 'sh:datatype', description: 'Ensures that the value is of a specified datatype.', violations: 2 },
  { id: 3, name: 'sh:nodeKind', description: 'Ensures that the value is of a specified node kind (e.g., literal, blank node, IRI).', violations: 1 },
  { id: 4, name: 'sh:minCount', description: 'Specifies the minimum number of values allowed for a property.', violations: 5 },
  { id: 5, name: 'sh:maxCount', description: 'Specifies the maximum number of values allowed for a property.', violations: 4 },
  { id: 6, name: 'sh:minExclusive', description: 'Specifies the minimum exclusive value allowed for a property.', violations: 2 },
  { id: 7, name: 'sh:minInclusive', description: 'Specifies the minimum inclusive value allowed for a property.', violations: 3 },
  { id: 8, name: 'sh:maxExclusive', description: 'Specifies the maximum exclusive value allowed for a property.', violations: 1 },
  { id: 9, name: 'sh:maxInclusive', description: 'Specifies the maximum inclusive value allowed for a property.', violations: 0 },
  { id: 10, name: 'sh:minLength', description: 'Specifies the minimum length of a string value.', violations: 6 },
  { id: 11, name: 'sh:maxLength', description: 'Specifies the maximum length of a string value.', violations: 4 },
  { id: 12, name: 'sh:pattern', description: 'Specifies a regular expression pattern that the string value must match.', violations: 2 },
  { id: 13, name: 'sh:languageIn', description: 'Specifies a set of allowed language tags for a string value.', violations: 0 },
  { id: 14, name: 'sh:uniqueLang', description: 'Ensures that all language tags in a set of string values are unique.', violations: 1 },
  { id: 15, name: 'sh:equals', description: 'Ensures that the value of one property equals the value of another property.', violations: 3 },
  { id: 16, name: 'sh:disjoint', description: 'Ensures that the values of two properties are disjoint sets.', violations: 5 },
  { id: 17, name: 'sh:lessThan', description: 'Ensures that the value of one property is less than the value of another property.', violations: 2 },
  { id: 18, name: 'sh:lessThanOrEqual', description: 'Ensures that the value of one property is less than or equal to the value of another property.', violations: 4 },
  { id: 19, name: 'sh:not', description: 'Specifies that a property must not have a value that satisfies a given shape.', violations: 0 },
  { id: 20, name: 'sh:and', description: 'Specifies that a property must have a value that satisfies all of a set of given shapes.', violations: 1 },
  { id: 21, name: 'sh:or', description: 'Specifies that a property must have a value that satisfies at least one of a set of given shapes.', violations: 2 },
  { id: 22, name: 'sh:xone', description: 'Specifies that a property must have a value that satisfies exactly one of a set of given shapes.', violations: 3 },
  { id: 23, name: 'sh:node', description: 'Specifies that a property must have a value that satisfies a given shape.', violations: 1 },
  { id: 24, name: 'sh:property', description: 'Specifies that a property must have a value that satisfies a given shape, and allows additional properties to be specified.', violations: 0 },
  { id: 25, name: 'sh:qualifiedValueShape', description: 'Specifies that a property must have a value that satisfies a given shape, and allows additional constraints to be specified.', violations: 2 },
  { id: 26, name: 'sh:qualifiedMinCount', description: 'Specifies the minimum number of values that a property must have, and allows additional constraints to be specified.', violations: 4 },
  { id: 27, name: 'sh:qualifiedMaxCount', description: 'Specifies the maximum number of values that a property must have, and allows additional constraints to be specified.', violations: 3 },
  { id: 28, name: 'sh:closed', description: 'Specifies that a node must not have any properties other than those specified in a given set.', violations: 0 },
  { id: 29, name: 'sh:ignoredProperties', description: 'Specifies a set of properties that are ignored during validation.', violations: 2 },
  { id: 30, name: 'sh:hasValue', description: 'Specifies that a property must have a specific value.', violations: 4 },
  { id: 31, name: 'sh:in', description: 'Specifies that a property must have a value that is in a given set of values.', violations: 5 },
]);


// Tags for summary
const tags = ref([
  { title: 'Total Constraint Types', value: constraints.value.length },
  { title: 'Constraints with Violations', value: `${constraints.value.filter(c => c.violations > 0).length} (${Math.round((constraints.value.filter(c => c.violations > 0).length / constraints.value.length) * 100)}%)` },
  { title: 'Most Violated Constraint Type', value: 'sh:minCount' },
  { title: 'Average Violations per Constraint', value: (constraints.value.reduce((sum, c) => sum + c.violations, 0) / constraints.value.length).toFixed(2) },
]);

// Helper function to categorize constraints dynamically
const categorizeConstraint = (constraint) => {
  if (constraint.name.includes('sh:class') || constraint.name.includes('sh:datatype') || constraint.name.includes('sh:nodeKind')) {
    return 'Value Type Constraint Components';
  }
  if (constraint.name.includes('sh:minCount') || constraint.name.includes('sh:maxCount')) {
    return 'Cardinality Constraint Components';
  }
  if (constraint.name.includes('sh:minExclusive') || constraint.name.includes('sh:minInclusive') || constraint.name.includes('sh:maxExclusive')) {
    return 'Value Range Constraint Components';
  }
  if (constraint.name.includes('sh:minLength') || constraint.name.includes('sh:maxLength')) {
    return 'String-based Constraint Components';
  }
  if (constraint.name.includes('sh:equals') || constraint.name.includes('sh:disjoint')) {
    return 'Property Pair Constraint Components';
  }
  if (constraint.name.includes('sh:not') || constraint.name.includes('sh:and') || constraint.name.includes('sh:or') || constraint.name.includes('sh:xone')) {
    return 'Logical Constraint Components';
  }
  if (constraint.name.includes('sh:node') || constraint.name.includes('sh:property')) {
    return 'Shape-based Constraint Components';
  }
  return 'Other Constraint Components';
};

// Categorize constraints
const constraintsWithCategory = constraints.value.map(constraint => ({
  ...constraint,
  category: categorizeConstraint(constraint),
}));

// Unique categories
const uniqueCategories = [...new Set(constraintsWithCategory.map(c => c.category))];

// Get constraints by category
const constraintsByCategory = category =>
  constraintsWithCategory.filter(constraint => constraint.category === category);

// Charts data
const violationsByConstraintType = {
  labels: constraints.value.map(constraint => constraint.name),
  datasets: [
    {
      label: 'Number of Violations',
      data: constraints.value.map(constraint => constraint.violations),
      backgroundColor: '#FF5252',
    },
  ],
};

const histogramData = {
  labels: ['0-5', '6-10', '11-15', '16-20', '21-25'], // Violation count ranges
  datasets: [
    {
      label: 'Constraint Component', 
      data: [8, 12, 5, 7, 3], // Mock data representing the number of constraint components in each violation range
      backgroundColor: '#66BB6A', // Green color for the bars
    },
  ],
};

const usageDistributionData = computed(() => constraints.value.map(c => c.violations));
const usageLabels = computed(() => constraints.value.map(c => c.name));

// Navigation
const goToConstraintView = (constraint) => {
  router.push({ 
    name: 'ConstraintView', 
    params: { 
      constraintId: constraint.id, 
      constraintName: constraint.name, 
      constraintViolations: constraint.violations
    } 
  });
};
</script>

<style scoped>
.category-section {
  margin-bottom: 30px;
}

.table-container {
  background-color: white;
  border-radius: 8px;
  padding: 20px;
  margin-bottom: 20px;
}

.table-fixed {
  table-layout: fixed;
}

th,
td {
  padding: 12px;
}

th.w-1\/4,
td.w-1\/4 {
  width: 25%;
}

th.w-1\/3,
td.w-1\/3 {
  width: 33.33%;
}

th.w-1\/6,
td.w-1\/6 {
  width: 16.67%;
}

th.w-1\/12,
td.w-1\/12 {
  width: 8.33%;
}

tbody tr:hover {
  background-color: #f0f8ff;
}

tbody tr {
  cursor: pointer;
}


.constraint-overview {
    display: flex;
    flex-direction: column;
    gap: 1rem; /* Match the spacing between sections */
}

.grid {
    grid-template-columns: repeat(auto-fit, minmax(200px, 1fr));
    gap: 1rem; /* Match the spacing for plots */
}

.grid-cols-3 {
    gap: 1rem; /* Match the gap in PropertyPathOverview */
}

.grid-cols-4 {
    grid-template-columns: repeat(4, 1fr);

}

.category-section {
    margin-bottom: 1.5rem; /* Ensure uniform spacing for tables */
}


.table-container {
    margin-bottom: 1.5rem; /* Consistent spacing for tables */
    padding: 1rem;
}
</style>
