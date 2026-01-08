<script setup>
/**
 * Navigation component
 *
 * Top navigation bar of the application.
 * Typically includes logo, main navigation links, and user controls.
 *
 * @example
 * // Basic usage in a parent component template:
 * // <Navigation />
 *
 * @prop {String} [title='SHACL Dashboard'] - Application title to display
 * @prop {Array} [navItems=[]] - Navigation items to display
 * @prop {Boolean} [showUserMenu=true] - Whether to show user menu controls
 *
 * @dependencies
 * - vue (Composition API)
 * - vue-router (for navigation)
 *
 * @style
 * - Full-width navigation bar with responsive design.
 * - Contains styling for navigation links, dropdowns, and user controls.
 * - Typically has contrasting background color for visual separation.
 * 
 * @returns {HTMLElement} A vertical navigation menu consisting of a list of router-linked
 * buttons for different application views (Home, Shapes View, and Log out), styled with
 * blue backgrounds and consistent spacing.
 */
const emit = defineEmits(['updateView']);

const buttonClicked = (viewName) => {
  emit('updateView', viewName); // Emit the selected view to the parent
};
</script>

<template>
  <v-list class="button-list">
    <v-list-item>
      <router-link :to="'/home'" @click.native="buttonClicked('Home')">
        <v-btn text class="button-text-wrap blue-btn">Home</v-btn>
      </router-link>
    </v-list-item>
    <v-list-item>
      <router-link :to="'/shapes'" @click.native="buttonClicked('Shape View')">
        <v-btn text class="button-text-wrap blue-btn">Shapes View</v-btn>
      </router-link>
    </v-list-item>
    <!-- <v-list-item>
      <router-link :to="'/focus-nodes'" @click.native="buttonClicked('Focus Node View')">
        <v-btn text class="button-text-wrap blue-btn">Focus Nodes View</v-btn>
      </router-link>
    </v-list-item>
    <v-list-item>
      <router-link :to="'/property-paths'" @click.native="buttonClicked('Property Path View')">
        <v-btn text class="button-text-wrap blue-btn">Property Paths View</v-btn>
      </router-link>
    </v-list-item>
    <v-list-item>
      <router-link :to="'/constraints'" @click.native="buttonClicked('Constraint View')">
        <v-btn text class="button-text-wrap blue-btn">Constraints View</v-btn>
      </router-link>
    </v-list-item> -->

    <v-list-item>
      <router-link :to="'/'" @click.native="buttonClicked('LandingPage')">
        <v-btn text class="button-text-wrap blue-btn">Log out</v-btn>
      </router-link>
    </v-list-item>
  </v-list>
</template>

<style scoped>
/* Button List Styling */
.button-list {
  display: flex;
  flex-direction: column; /* Arrange buttons vertically */
  justify-content: flex-start; /* Align buttons to the top */
  align-items: center; /* Center align buttons horizontally */
  height: 100%;
  padding: 20px 0;
  margin: 0;
}

.button-text-wrap {
  white-space: normal;
  text-align: center;
  display: inline-block;
  word-wrap: break-word;
  width: 200px;
  min-width: 200px;
  max-width: 200px;
  padding: 10px 20px;
  color: white;
  background-color: #1976D2;
  border-radius: 4px;
  transition: background-color 0.3s ease;
}

.button-text-wrap:hover {
  background-color: #1565C0;
}
</style>
