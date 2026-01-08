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
/**
 * ConfirmationModal component
 *
 * Displays a modal dialog asking for user confirmation on important actions.
 * Provides yes/no options with appropriate styling.
 *
 * @example
 * // Basic usage in a parent component template:
 * // <ConfirmationModal ref="confirmModal" @confirmed="handleConfirm" @cancelled="handleCancel" />
 * //
 * // // In script:
 * // const confirmModal = ref(null);
 * // const showModal = () => {
 * //   confirmModal.value.show();
 * // }
 *
 * @emits {confirmed} - When the user confirms the action
 * @emits {cancelled} - When the user cancels the action
 *
 * @exposes {show} - Method to display the modal
 *
 * @dependencies
 * - vue (Composition API)
 * - vuetify - For dialog components (v-dialog, v-card)
 *
 * @style
 * - Persistent modal that requires user decision
 * - Clear action buttons with appropriate colors
 * - Centered content with limited width
 * 
 * @returns {HTMLElement} A modal dialog with "Are you sure, Sir?" title and Yes/No
 * buttons for confirming or canceling an action, designed to overlay the current page content
 * and require user interaction before proceeding.
 */

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
