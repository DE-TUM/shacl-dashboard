<template>
  <div class="relative group inline-block z-50">
    <!-- Blue Circle with Question Mark -->
    <div class="w-6 h-6 bg-gray-500 text-white flex items-center justify-center rounded-full cursor-pointer">
      ?
    </div>
    <!-- Tooltip -->
    <div
      class="absolute hidden group-hover:block bg-gray-100 text-gray-800 text-sm p-2 rounded shadow-md w-64 mt-2 right-0 transform translate-x-full z-50"
    >
      {{ explanation }}
    </div>
  </div>
</template>

<script setup>
/**
 * ToggleQuestionMark component
 *
 * Renders a question mark icon with a hover tooltip for providing additional information.
 * Used to explain features or interface elements without cluttering the UI.
 *
 * @example
 * // Basic usage in a parent component template:
 * // <ToggleQuestionMark explanation="This field accepts a valid email address." />
 *
 * @prop {String} explanation - The tooltip text to display when hovering over the question mark
 *
 * @dependencies
 * - vue (Composition API)
 *
 * @style
 * - Round gray background with white question mark
 * - Tooltip appears on hover with readable text
 * - Z-index handling for proper layering
 * 
 * @returns {HTMLElement} A circular question mark icon with a hover-triggered tooltip
 * that displays the explanation text provided as a prop, positioned to the right of the icon.
 */
import { defineProps } from 'vue';

// Define props to allow customization of explanation text
defineProps({
  explanation: {
    type: String,
    required: true
  }
});
</script>

<style scoped>
/* Optional: Customize the tooltip's position and animation */
.group:hover .hidden {
  display: block;
}
</style>
