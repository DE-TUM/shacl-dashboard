<template>
  <v-dialog v-model="isVisible" max-width="400px" persistent>
    <v-card>
      <v-card-title class="headline">Are you sure, Sir?</v-card-title>
      <v-card-actions>
        <v-btn @click="cancel" color="grey">No</v-btn>
        <v-btn @click="confirm" color="red">Yes</v-btn>
      </v-card-actions>
    </v-card>
  </v-dialog>
</template>

<script setup>
import { ref } from 'vue';

// Local state to control modal visibility
const isVisible = ref(false);

// Emit events for confirmation or cancellation
const emit = defineEmits(['confirmed', 'cancelled']);

// Show modal
const show = () => {
  isVisible.value = true;
};

// Hide modal
const hide = () => {
  isVisible.value = false;
};

// Emit confirmed event
const confirm = () => {
  hide();
  emit('confirmed');
};

// Emit cancelled event
const cancel = () => {
  hide();
  emit('cancelled');
};

// Expose show function so parent can trigger the modal
defineExpose({ show });
</script>

<style scoped>
/* Custom style for dialog if needed */
</style>
