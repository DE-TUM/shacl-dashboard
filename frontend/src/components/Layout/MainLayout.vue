<script setup>
/**
 * MainLayout component
 *
 * Root layout component that structures the overall application layout.
 * Typically includes navigation, sidebar, and main content areas.
 *
 * @example
 * // Basic usage in a parent component template:
 * // <MainLayout>
 * //   <template #sidebar>
 * //     <SideBar />
 * //   </template>
 * //   <template #content>
 * //     <MainContent />
 * //   </template>
 * // </MainLayout>
 *
 * @slot sidebar - Content for the sidebar area
 * @slot navigation - Content for the navigation area
 * @slot content - Main content area
 * @slot footer - Footer content area
 *
 * @dependencies
 * - vue (Composition API)
 *
 * @style
 * - CSS grid or flexbox layout for positioning main application sections.
 * - Responsive design that adjusts for different screen sizes.
 * - Contains basic structure styling for the application layout.
 * 
 * @returns {HTMLElement} The primary application layout structure with a top app bar displaying
 * the application title, a collapsible sidebar on the left for navigation, and a main content
 * area on the right that displays the current route's view.
 */
import { ref, onMounted } from 'vue';
import SideBar from './SideBar.vue'; // Import the SideBar component

const isMobile = ref(false); // Track screen size for responsiveness
const activeView = ref("Home"); // Track the currently selected view
const sidebarWidth = ref(60); // Default collapsed sidebar width
const emit = defineEmits(['updateView']);

const handleViewUpdate = (view) => {
  // Emit the selected view to the parent to update the content dynamically
  activeView.value = view;
  emit('updateView', view);
};

const updateSidebarWidth = (width) => {
  sidebarWidth.value = width;
};

// Watch window resize to toggle between mobile and desktop
onMounted(() => {
  const handleResize = () => {
    isMobile.value = window.innerWidth <= 600; // Adjust breakpoint as needed
  };

  window.addEventListener("resize", handleResize);
  handleResize(); // Initial check
});
</script>

<template>
  <!-- Top App Bar -->
  <v-app-bar app color="primary" dark>
    <v-toolbar-title class="text-center" style="width: 100%;">SHACL Dashboard</v-toolbar-title>
  </v-app-bar>

  <!-- Main Content Area -->
  <v-main style="height: calc(100vh - 64px); display: flex; margin-top: 64px; padding: 0;">
    <v-row no-gutters style="width: 100%; height: 100%;">
      <!-- Sidebar with auto width -->
      <v-col :style="{ padding: '0', margin: '0', maxWidth: sidebarWidth + 'px' }">
        <SideBar @updateView="handleViewUpdate" @sidebarWidthChanged="updateSidebarWidth" />
      </v-col>

      <!-- Main Content fills remaining space -->
      <v-col :style="{ padding: '0px 20px', flex: '1', width: `calc(100% - ${sidebarWidth}px)` }">
        <!-- Router View -->
        <router-view class="mt-4" />
      </v-col>
    </v-row>
  </v-main>
</template>

<style scoped>
.v-main {
  display: flex;
  flex-direction: row;
  height: 100%;
  width: 100%;
  overflow-y: auto;
  padding: 0;
  background-color: #efefef !important;
}

.v-row {
  display: flex;
  width: 100%;
  height: 100%;
}

.v-col {
  display: flex;
  flex-direction: column;
}

@media (max-width: 768px) {
  .v-main {
    flex-direction: column;
  }

  .v-col {
    padding-left: 10px;
  }
}
</style>
