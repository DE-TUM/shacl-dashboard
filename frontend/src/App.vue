<template>
  <v-app>
    <!-- Always Render the Main Layout -->
    <MainLayout />
  </v-app>
</template>

<script setup>
import { ref } from 'vue';
import MainLayout from './components/Layout/MainLayout.vue';
import LandingPage from './components/LandingPage.vue'; // Make sure you import the LandingPage component
import { useRouter } from 'vue-router';

// Router for navigation
const router = useRouter();
// State to track if the user is on the landing page
const isLandingPage = ref(true);

// Function to switch to the main layout
const handleEnterClick = () => {
  router.push({ name: "Home" }); 
  isLandingPage.value = false; // Switch to main layout when ENTER is clicked
};

const handleViewUpdate = (view) => {
  // Emit the selected view to the parent to update the content dynamically
  if (view === 'LandingPage') {
    isLandingPage.value = true; // Switch to landing page when Log out is clicked
  }
};
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
  padding: 0 !important;
  display: flex; /* Ensures flex layout works for full container size */

}

.v-application, .v-application-wrapper {
  width: 100vw !important;
  max-width: 100vw !important;
  min-height: 100vh;
}



</style>
