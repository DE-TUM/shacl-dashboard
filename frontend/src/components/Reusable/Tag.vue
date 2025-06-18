<template>
  <div class="tag-container border-2 rounded p-4 text-center shadow-sm">
    <h3 v-html="title"></h3>
    <p class="tag-ratio" v-if="isPercentage">{{ ratio }}%</p>
    <p class="tag-value" v-else>{{ singleValue }}</p>
  </div>
</template>

<script setup>
/**
 * Tag component
 *
 * Displays a labeled value or percentage in a card-like container.
 * Can show either a single value or calculate a percentage from two values.
 *
 * @example
 * // Single value usage:
 * // <Tag :data="[42]" title="Total Violations" />
 * 
 * // Percentage calculation:
 * // <Tag :data="[7, 10]" title="Validation Success Rate" />
 *
 * @prop {Array} data - Array with either [value] or [numerator, denominator]
 * @prop {String} title - The title/label for the tag
 *
 * @dependencies
 * - vue (Composition API)
 *
 * @style
 * - Bordered container with shadow and padding
 * - Title with descriptive text
 * - Value or percentage displayed prominently
 * - Color differentiation for values
 * 
 * @returns {HTMLElement} A card-style container with a title and either a single value
 * or a calculated percentage based on the provided data array, formatted with distinct
 * styling for the title and value/percentage.
 */
import { defineProps, computed } from 'vue';

// Define the props
const props = defineProps({
  data: {
    type: Array,
    required: true,
    validator(value) {
      return value.length === 1 || value.length === 2; // Support single-value or percentage calculation
    },
  },
  title: {
    type: String,
    required: true,
  },
});

// Determine if the data array has one or two values
const isPercentage = computed(() => props.data.length === 2);

// Compute the ratio for percentage calculation
const ratio = computed(() => {
  if (isPercentage.value) {
    const [value1, value2] = props.data;
    return value2 !== 0 ? ((value1 / value2) * 100).toFixed(2) : 'NaN'; // Calculate percentage or return 'NaN'
  }
  return null;
});

// Handle single-value display
const singleValue = computed(() => (props.data.length === 1 ? props.data[0] : null));
</script>

<style scoped>
.tag-container {
  display: flex;
  flex-direction: column;
  justify-content: center;
  align-items: center;
  background-color: #f9f9f9;
  border-color: #e0e0e0;
}

h3 {
  font-size: 1rem;
  font-weight: bold;
  color: #333;
  margin: 0 0 0.5rem 0;
  text-align: center;
}

.tag-ratio {
  font-size: 1.2rem;
  color: #1976D2;
  font-weight: bold;
}

.tag-value {
  font-size: 1.4rem;
  color: #444;
  font-weight: bold;
}
</style>
