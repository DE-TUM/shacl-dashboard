<template>
  <div class="dropdown-container">
    <div class="dropdown-row">
      <template v-for="(_, index) in 4" :key="index">
        <DropDownMenu
          :model="filters[`dropdown${index + 1}`]"
          :items="filters[`options${index + 1}`]"
          :label="getLabel(index)"
          @update:model="value => updateDropdown(index + 1, value)"
        />
      </template>
      <button @click="saveSelection" class="save-button mt-4 px-4 py-2 bg-blue-500 text-white rounded hover:bg-blue-600">
        Save Selection
      </button>
      <button @click="resetFilters" class="reset-button mt-4 px-4 py-2 bg-gray-200 text-gray-500 rounded hover:bg-gray-400">
        Reset All Filters
      </button>
    </div>
  </div>
</template>

<script setup>
/**
 * Filter component
 *
 * Provides a multi-dropdown filtering interface for data tables.
 * Allows selection of filter values across multiple categories.
 *
 * @example
 * // Basic usage in a parent component template:
 * // <Filter 
 * //   :filters="filtersObject" 
 * //   @update:filters="handleFilterUpdate" 
 * //   @set-options="handleSetOptions" 
 * //   @reset="handleReset"
 * // />
 *
 * @prop {Object} filters - Object containing dropdown selections and options
 * 
 * @emits {update:filters} - When filters are updated
 * @emits {set-options} - When dropdown options are set
 * @emits {reset} - When filters are reset
 *
 * @dependencies
 * - vue (Composition API)
 * - ./DropDownMenu.vue - For dropdown selection components
 *
 * @style
 * - Vertical column layout with multiple dropdown menus
 * - Save and reset buttons with distinct styling
 * - Proper spacing for clear visual hierarchy
 * 
 * @returns {HTMLElement} A filtering interface with four dropdown menus for different filter categories
 * (Shapes, Focus Nodes, Property Paths, Constraint Components), plus Save Selection and Reset All
 * Filters buttons at the bottom.
 */
import { ref } from 'vue';
import DropDownMenu from './DropDownMenu.vue';

const props = defineProps({
  filters: {
    type: Object,
    required: true,
  },
});

const emit = defineEmits(['update:filters', 'set-options', 'reset']);

const labels = ['Shapes', 'Focus Nodes', 'Property Paths', 'Constraint Components'];

const getLabel = (index) => labels[index];

const updateDropdown = (index, value) => {
  props.filters[`dropdown${index}`] = value;
  emit('update:filters', { ...props.filters });
};

// Save the selected filters (updates parent state)
const saveSelection = () => {
  emit("update:filters", { ...tempFilters.value });
};


const resetFilters = () => {
  for (let i = 1; i <= 4; i++) {
    props.filters[`dropdown${i}`] = [];
  }
  emit('reset');
};
// Emit dropdown options to parent when component is mounted
const setOptions = () => {
  const options = {
    options1: ['Shape 1', 'Shape 2', 'Shape 3'],
    options2: ['Node 1', 'Node 2', 'Node 3'],
    options3: ['Path A', 'Path B', 'Path C'],
    options4: ['Constraint X', 'Constraint Y', 'Constraint Z'],
  };
  emit('set-options', options);
};

setOptions();
</script>
  
<style scoped>
.dropdown-container {
  display: flex;
  flex-direction: column;
  width: 100%;
}

.dropdown-row {
  display: flex;
  flex-direction: column;
  gap: 5px;
  width: 100%;
  align-items: center;
}

.v-select {
  width: 200px; /* Set a fixed width for the dropdowns */
}

.save-button {
  width: 250px;
  background-color: #0466C8;
  color: white;
  transition: 0.3s;
}

.save-button:hover {
  background-color: #0346A5;
}


.reset-button {
  width: 250px;
  margin-top: 10px;
  color: #4A4A4A;
  /* border-color: #4A4A4A; */
}

.v-btn.no-color-button {
  background-color: rgba(74, 74, 74, 0.05) !important;
  color: #383838 !important;
  font-size: 16px;
  height: 40px;
  margin: 0;
  padding: 0 16px;
  border: 1px solid #d0d0d0 !important;
  box-shadow: 0 1px 2px rgba(0, 0, 0, 0.05);
  transition: all 0.2s ease;
  width: 250px;
  margin-top: 10px;
  
}


.v-btn.no-color-button:hover {
  background-color: rgba(74, 74, 74, 0.1) !important;
  border-color: #b0b0b0 !important;
  box-shadow: 0 2px 4px rgba(0, 0, 0, 0.1);
}
</style>