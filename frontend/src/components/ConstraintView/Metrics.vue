<template>
    <div class="key-metrics grid grid-cols-4 gap-4">
      <!-- Shapes Using This Constraint -->
      <div class="metric-card bg-white shadow rounded p-4 flex items-center justify-between">
        <div class="flex items-center">
          <div class="icon bg-purple-100 text-purple-500 p-2 rounded-full mr-4">
            <svg xmlns="http://www.w3.org/2000/svg" class="h-6 w-6" fill="none" viewBox="0 0 24 24" stroke="currentColor">
              <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M4 4h16v16H4z" />
            </svg>
          </div>
          <div>
            <p class="text-lg font-semibold">Shapes Using This Constraint</p>
            <p class="text-2xl text-purple-500 font-bold">{{ shapesUsingConstraint }}</p>
          </div>
        </div>
      </div>
  
      <!-- Violation Breakdown -->
      <div class="metric-card bg-white shadow rounded p-4 flex items-center justify-between">
        <div class="flex items-center">
          <div class="icon bg-red-100 text-red-500 p-2 rounded-full mr-4">
            <svg xmlns="http://www.w3.org/2000/svg" class="h-6 w-6" fill="none" viewBox="0 0 24 24" stroke="currentColor">
              <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M18.364 5.636a9 9 0 11-12.728 0M15 12h.01M9 12h.01M15 16h.01M9 16h.01M12 12.5l-3-3m0 0h6m-6 0l3 3" />
            </svg>
          </div>
          <div>
            <p class="text-lg font-semibold">Violation Breakdown</p>
            <p class="text-2xl text-red-500 font-bold">{{ violationBreakdown }}</p>
          </div>
        </div>
      </div>
  
      <!-- Common Issues -->
      <div class="metric-card bg-white shadow rounded p-4 flex items-center justify-between">
        <div class="flex items-center">
          <div class="icon bg-green-100 text-green-500 p-2 rounded-full mr-4">
            <svg xmlns="http://www.w3.org/2000/svg" class="h-6 w-6" fill="none" viewBox="0 0 24 24" stroke="currentColor">
              <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M9 5v14l11-7-11-7z" />
            </svg>
          </div>
          <div>
            <p class="text-lg font-semibold">Common Issues</p>
            <p class="text-sm text-green-500">Missing data, incorrect data type, invalid URIs</p>
          </div>
        </div>
      </div>
    </div>
  </template>
  
  <script setup>
/**
 * Metrics component
 *
 * Displays key metrics about constraints in a dashboard format.
 * Shows information such as shapes using the constraint, violation breakdowns, and common issues.
 *
 * @example
 * // Basic usage in a parent component template:
 * // <Metrics />
 *
 * @prop {Number} [shapesUsingConstraint=5] - Number of shapes using this constraint
 * @prop {Number} [violationBreakdown=10] - Number of violations for this constraint
 *
 * @dependencies
 * - vue (Composition API)
 *
 * @style
 * - Grid layout with responsive card design.
 * - Cards with icons, titles, and metric values.
 * - Color-coded icons and values for visual categorization.
 * 
 * @returns {HTMLElement} A grid of three metric cards showing key constraint statistics:
 * shapes using this constraint (with count), violation breakdown (with count), and 
 * common issues (with text descriptions). Each card features an icon and descriptive text.
 */
  import { ref } from 'vue';
  
  const shapesUsingConstraint = ref(5); // This can be dynamic based on actual data
  const violationBreakdown = ref(10);  // This can be dynamic as well
  </script>
  
  <style scoped>
  .metric-card {
    border: 1px solid #e5e7eb;
  }
  .icon {
    width: 48px;
    height: 48px;
  }
  </style>
