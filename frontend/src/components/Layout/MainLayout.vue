<script setup>
import { ref, onMounted } from 'vue';
import SideBar from './SideBar.vue'; // Import the SideBar component

const isMobile = ref(false); // Track screen size for responsiveness
const activeView = ref("Home"); // Track the currently selected view
const emit = defineEmits(['updateView']);

const handleViewUpdate = (view) => {
  // Emit the selected view to the parent to update the content dynamically
  activeView.value = view;
  emit('updateView', view);
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
      <v-col style="padding: 0; margin: 0; max-width: 300px;">
        <SideBar @updateView="handleViewUpdate" />
      </v-col>

      <!-- Main Content fills remaining space -->
      <v-col style="padding: 0px 20px; flex: 1;">
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
