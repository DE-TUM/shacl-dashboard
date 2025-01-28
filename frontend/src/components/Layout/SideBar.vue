<template>
  <div class="sidebar">
    <ul class="menu-list">
      <li v-for="item in menuItems" :key="item.name">
        <router-link 
          :to="item.route"
          custom
          v-slot="{ navigate }"
        >
          <div
            @click="buttonClicked(item.name, navigate)"
            :class="{ active: activeView === item.name }"
            class="menu-item"
          >
            <FontAwesomeIcon 
              :icon="item.icon" 
              class="menu-icon" 
              :class="{ 'active-icon': activeView === item.name }" 
            />
            <span class="menu-text">{{ item.label }}</span>
          </div>
        </router-link>
      </li>

      <!-- Logout button -->
      <li @click="handleLogout" class="logout-item">
        <FontAwesomeIcon :icon="faPowerOff" class="menu-icon" />
        <span class="menu-text">Log out</span>
      </li>
    </ul>

    <!-- Confirmation Modal -->
    <ConfirmationModal ref="confirmationModal" @confirmed="logoutConfirmed" @cancelled="handleCancel" />

  </div>
</template>

<script setup>
import { ref } from 'vue';
import { FontAwesomeIcon } from '@fortawesome/vue-fontawesome';
import { faHome, faShapes, faProjectDiagram, faRoute, faPuzzlePiece, faPowerOff, faInfo } from '@fortawesome/free-solid-svg-icons';
import ConfirmationModal from './../Reusable/ConfirmationModal.vue';

const emit = defineEmits(['updateView']);
const confirmationModal = ref(null); // Reference to the modal
const activeView = ref('Home');
const showModal = ref(false);

const menuItems = [
  { name: 'Home', label: 'Home', icon: faHome, route: '/home' },
  { name: 'Shape View', label: 'Shapes', icon: faShapes, route: '/shapes' },
  { name: 'Focus Node View', label: 'Focus Nodes', icon: faProjectDiagram, route: '/focus-nodes' },
  { name: 'Property Path View', label: 'Property Paths', icon: faRoute, route: '/property-paths' },
  { name: 'Constraint View', label: 'Constraints', icon: faPuzzlePiece, route: '/constraints' },
  { name: 'About Us', label: 'About Us', icon: faInfo, route: '/about-us' }
];

const buttonClicked = (viewName, navigate) => {
  activeView.value = viewName;
  emit('updateView', viewName);
  navigate(); // Execute the router-link navigation
};

const handleLogout = () => {
  confirmationModal.value.show(); // Call the show function to display the modal
};

const logoutConfirmed = () => {
  emit('updateView', 'LandingPage');
  showModal.value = false;
};
</script>

<style scoped>
/* Sidebar Styling */
.sidebar {
  position: fixed;
  width: 250px;
  height: 100vh;
  background-color: #ffffff;
  border-right: 1px solid #ddd;
  box-shadow: 0 4px 6px rgba(0, 0, 0, 0.1);
  display: flex;
  flex-direction: column;
  padding: 20px 0;
  overflow-y: auto; 
  z-index: 50;/* Add this to ensure scrolling works if needed */
}

.confirmation-modal {
  position: fixed;
  z-index: 1000; /* Ensure it's above other elements */
  top: 0;
  left: 0;
  width: 100%;
  height: 100%;
  background-color: rgba(0, 0, 0, 0.5);
  display: flex;
  justify-content: center;
  align-items: center;
}

.profile-container {
  display: flex;
  justify-content: center;
  align-items: center;
  margin-bottom: 20px; /* Space between photo and menu */
}

.profile-photo {
  width: 100px; /* Adjust size as needed */
  height: 100px;
  border-radius: 50%; /* This makes the photo circular */
  object-fit: cover; /* Ensures the photo fits nicely within the circle */
  border: 2px solid #ddd; /* Optional: Add a border around the circle */
  box-shadow: 0 4px 6px rgba(0, 0, 0, 0.1); /* Optional: Add a subtle shadow */
}

.profile-text {
  font-weight: 800;
  color: black;
  display: inline-block;
  text-decoration: none; /* Removes underline on the link */
}

.profile-link:hover {
  background-color: #fff !important;
}

.profile-text:hover {
  background-color: #afafaf !important;
}

.menu-list {
  list-style: none;
  padding: 0;
  margin: 0;
  width: 100%;
  display: flex;
  flex-direction: column;
  min-height: 100%; /* Change height to min-height */
}
.menu-item {
  display: flex;
  align-items: center;
  width: 100%;
  padding: 10px 40px;
  font-size: 16px;
  color: #828282;
  cursor: pointer;
  transition: background-color 0.3s, color 0.3s;
}

.menu-item.active {
  color: #020202;
}

.menu-item:hover {
  background-color: #efefef;
  color: #020202;
}

.menu-icon {
  margin-right: 10px;
  font-size: 20px;
  transition: color 0.3s;
}

.menu-icon.active-icon {
  color: rgb(24, 103, 192);
}

.menu-text {
  font-size: 16px;
  text-align: left;
}

.logout-item {
  /* margin-top: auto; */
  cursor: pointer;
  display: flex;
  align-items: center;
  width: 100%;
  padding: 10px 40px;
  font-size: 16px;
  color: #828282;
  /* border-top: 1px solid #ddd; */
}

.logout-item:hover {
  background-color: #efefef;
  color: #020202;
}
</style>