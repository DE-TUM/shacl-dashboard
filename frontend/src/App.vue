<template>
  <v-app>
    <!-- Always Render the Main Layout -->
    <MainLayout />
    
    <!-- Global Error Notification -->
    <ErrorNotification
      :show="showError"
      :message="errorMessage"
      :severity="errorSeverity"
      @close="clearError"
    />
  </v-app>
</template>

<script setup>
import { provide } from 'vue';
import MainLayout from './components/Layout/MainLayout.vue';
import ErrorNotification from './components/Common/ErrorNotification.vue';
import { useErrorHandler } from './composables/useErrorHandler';

// Initialize global error handler
const {
  error,
  errorMessage,
  errorSeverity,
  showError,
  handleError,
  clearError
} = useErrorHandler();

// Provide error handler to all child components
provide('errorHandler', {
  handleError,
  clearError
});
</script>


<style scoped>
/* Ensure full height and width for responsive adjustments */
html, body, #app {
  height: 100%;
  width: 100%;
  margin: 0;
  padding: 0;
}

/* Ensure v-app takes up full height and width */
v-app {
  height: 100%;
  width: 100%;
  padding: 0;
  display: flex; /* Ensures flex layout works for full container size */
}

.v-application, .v-application-wrapper {
  width: 100vw;
  max-width: 100vw;
  min-height: 100vh;
}
</style>
