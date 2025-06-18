<template>
  <div class="dropdown-container">
    <v-select
      ref="selectRef"
      v-model="model"
      :items="items"
      :label="label"
      density="compact"
      class="dropdown-field"
      hide-details
      multiple
      chips
      :chip-props="{ size: 'x-small' }" 
      :menu-props="{ closeOnContentClick: false }"
    />
  </div>
</template>

<script setup>
/**
 * DropDownMenu component
 *
 * Renders a multi-select dropdown menu with chips for selected items.
 * Used for filtering and selection interfaces.
 *
 * @example
 * // Basic usage in a parent component template:
 * // <DropDownMenu
 * //   :model="selectedItems"
 * //   :items="availableItems"
 * //   label="Select Options"
 * //   @update:model="handleUpdate"
 * // />
 *
 * @prop {Array} model - Array of currently selected items
 * @prop {Array} items - Array of available items to select from
 * @prop {String} label - Label text for the dropdown
 *
 * @emits {update:model} - When selection changes
 *
 * @dependencies
 * - vue (Composition API)
 * - vuetify - For v-select component
 *
 * @style
 * - Compact dropdown with small chips for selected items
 * - Consistent height and margin for UI alignment
 * - Small chip size for space efficiency
 * 
 * @returns {HTMLElement} A Vuetify select component configured for multi-select functionality
 * with chips representing selected items, supporting both dropdown item selection and
 * deselection via chip removal.
 */
import { ref, watch } from "vue";

const props = defineProps({
  model: {
    type: Array,
    default: () => [],
  },
  items: {
    type: Array,
    required: true,
  },
  label: {
    type: String,
    required: true,
  },
});

const emit = defineEmits(["update:model"]);
const model = ref([...props.model]); // Store selected options

// Sync model with parent when it changes
watch(
  () => props.model,
  (newValue) => {
    model.value = [...newValue];
  },
  { deep: true }
);
</script>

<style scoped>
.dropdown-field {
  height: 50px;
  margin: 5px;
}

/* Reduce chip size */
::v-deep(.v-chip) {
  font-size: 10px !important;
  height: 18px !important;
  padding: 2px 4px !important;
}
</style>
