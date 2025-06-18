<template>
  <div class="search-container">
    <!-- Search input field -->
    <v-text-field
      v-model="inputValue"
      label="Search"
      density="compact"
      class="search-field"
      hide-details
    />
    <v-btn @click="searchText" class="no-color-button" density="compact">
      Go
    </v-btn>
  </div>
</template>

<script setup>
/**
 * Search component
 *
 * Provides a search input field with a submit button.
 * Used for searching within datasets or content.
 *
 * @example
 * // Basic usage in a parent component template:
 * // <Search />
 *
 * @dependencies
 * - vue (Composition API)
 * - vuetify - For UI components (v-text-field, v-btn)
 *
 * @emits
 * - No events emitted directly (internal handling)
 *
 * @style
 * - Horizontal layout with search field and button
 * - Responsive sizing with maximum width constraint
 * - Button styling with hover effects
 * 
 * @returns {HTMLElement} A search interface with a Vuetify text field for input
 * and a "Go" button, styled with consistent heights and transitions for interactive elements.
 */

import { ref } from 'vue';

// Reactive variable for the search field
const inputValue = ref('');
</script>

<style scoped>
/* Container for the search field and button */
.search-container {
  display: flex;
  justify-content: center;
  align-items: stretch;
  gap: 10px;
  height: 40px;
}

/* Style for the search input */
.search-field {
  flex-grow: 1; /* Allow the input field to take up available space */
  max-width: 200px; /* Set a maximum width for the search field */
  width: 100%; /* Make sure it can take full available space */
}

/* Style for the 'Go' button */
.v-btn.no-color-button {
  background-color: rgba(74, 74, 74, 0.05) !important;
  color: #383838 !important;
  font-size: 16px;
  height: 100%;
  margin: 0;
  padding: 0 16px;
  border: 1px solid #d0d0d0 !important;
  box-shadow: 0 1px 2px rgba(0, 0, 0, 0.05);
  transition: all 0.2s ease;
}

.v-btn.no-color-button:hover {
  background-color: rgba(74, 74, 74, 0.1) !important;
  border-color: #b0b0b0 !important;
  box-shadow: 0 2px 4px rgba(0, 0, 0, 0.1);
}

:deep(.v-field) {
  height: 100%;
}
</style>
