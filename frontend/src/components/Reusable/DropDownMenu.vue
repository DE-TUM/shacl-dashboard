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
