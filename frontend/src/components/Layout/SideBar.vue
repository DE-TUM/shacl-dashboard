<template>
  <div 
    class="sidebar" 
    @mouseenter="isExpanded = true" 
    @mouseleave="isExpanded = false"
  >
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
            <span v-if="isExpanded" class="menu-text">{{ item.label }}</span>
          </div>
        </router-link>
      </li>

      <!-- Logout button -->
      <!-- <li @click="handleLogout" class="logout-item">
        <FontAwesomeIcon :icon="faPowerOff" class="menu-icon" />
        <span v-if="isExpanded" class="menu-text">Log out</span>
      </li> -->
    </ul>

    <!-- Confirmation Modal -->
    <ConfirmationModal ref="confirmationModal" @confirmed="logoutConfirmed" @cancelled="handleCancel" />
  </div>
</template>

<script setup>
/**
 * SideBar component
 *
 * Side navigation component that provides secondary navigation.
 * Typically includes links to different sections or views of the application.
 *
 * @example
 * // Basic usage in a parent component template:
 * // <SideBar />
 *
 * @prop {Array} [menuItems=[]] - Items to display in the sidebar menu
 * @prop {Boolean} [collapsed=false] - Whether the sidebar is in collapsed state
 * @prop {Boolean} [showToggle=true] - Whether to show collapse/expand toggle
 *
 * @dependencies
 * - vue (Composition API)
 * - vue-router (for navigation)
 *
 * @style
 * - Vertical navigation panel with fixed or flexible width.
 * - Contains styling for navigation links and nested menus.
 * - Often includes collapsible functionality for responsive design.
 * 
 * @returns {HTMLElement} A collapsible sidebar navigation menu that expands on hover,
 * featuring menu items with icons and text labels for different application views,
 * highlighting the currently active item and providing smooth transitions between states.
 */
import { ref, defineProps, watch } from 'vue';
import { FontAwesomeIcon } from '@fortawesome/vue-fontawesome';
import { faHome, faShapes, faProjectDiagram, faRoute, faPuzzlePiece, faPowerOff, faInfo } from '@fortawesome/free-solid-svg-icons';
import ConfirmationModal from './../Reusable/ConfirmationModal.vue';

const emit = defineEmits(['updateView', 'sidebarWidthChanged']);
const confirmationModal = ref(null);
const activeView = ref('Home');
const isExpanded = ref(false);
const sidebarWidth = ref(60);

const menuItems = [
  { name: 'Home', label: 'Home', icon: faHome, route: '/' },
  { name: 'Shape View', label: 'Shapes', icon: faShapes, route: '/shapes' },
  { name: 'About Us', label: 'About Us', icon: faInfo, route: '/about-us' }
];

// const menuItems = [
//   { name: 'Home', label: 'Home', icon: faHome, route: '/' },
//   { name: 'Shape View', label: 'Shapes', icon: faShapes, route: '/shapes' },
//   { name: 'Focus Node View', label: 'Focus Nodes', icon: faProjectDiagram, route: '/focus-nodes' },
//   { name: 'Property Path View', label: 'Property Paths', icon: faRoute, route: '/property-paths' },
//   { name: 'Constraint View', label: 'Constraints', icon: faPuzzlePiece, route: '/constraints' },
//   { name: 'About Us', label: 'About Us', icon: faInfo, route: '/about-us' }
// ];


const buttonClicked = (viewName, navigate) => {
  activeView.value = viewName;
  emit('updateView', viewName);
  navigate();
};

const handleLogout = () => {
  confirmationModal.value.show();
};

const logoutConfirmed = () => {
  emit('updateView', 'LandingPage');
};

watch(isExpanded, (newValue) => {
  sidebarWidth.value = newValue ? 250 : 60;
  emit('sidebarWidthChanged', sidebarWidth.value);
});
</script>

<style scoped>
.sidebar {
  position: fixed;
  width: v-bind(sidebarWidth + 'px');
  height: 100vh;
  background-color: #ffffff;
  border-right: 1px solid #ddd;
  box-shadow: 0 4px 6px rgba(0, 0, 0, 0.1);
  display: flex;
  flex-direction: column;
  padding: 20px 0;
  overflow-y: auto;
  z-index: 50;
  transition: width 0.3s ease-in-out;
}

.menu-list {
  list-style: none;
  padding: 0;
  margin: 0;
  width: 100%;
  display: flex;
  flex-direction: column;
  min-height: 100%;
}

.menu-item {
  display: flex;
  align-items: center;
  width: 100%;
  padding: 10px 20px;
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

.menu-text {
  font-size: 16px;
  text-align: left;
}

.logout-item {
  cursor: pointer;
  display: flex;
  align-items: center;
  width: 100%;
  padding: 10px 20px;
  font-size: 16px;
  color: #828282;
}

.logout-item:hover {
  background-color: #efefef;
  color: #020202;
}
</style>
