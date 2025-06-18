/**
 * Main Application Entry Point
 * 
 * Initializes the Vue application with required plugins and global components.
 * Sets up Vuetify for UI components, Vue Router for navigation,
 * and Font Awesome for icons.
 * 
 * @dependencies
 * - vue - Core Vue 3 library
 * - vuetify - Material Design component framework
 * - vue-router - Official router for Vue.js
 * - @fortawesome - Icon library components
 * 
 * @returns {Vue} A mounted Vue 3 application instance with Vuetify and Vue Router,
 * and FontAwesome configured, ready to render the application on the #app DOM element.
 */
import './assets/main.css';

import { createApp } from 'vue';
import App from './App.vue';
import { createVuetify } from 'vuetify';
import 'vuetify/styles';
import * as components from 'vuetify/components';
import * as directives from 'vuetify/directives';

// Import the router
import router from './router';

// Import Font Awesome core
import { library } from '@fortawesome/fontawesome-svg-core';
import { faDownload } from "@fortawesome/free-solid-svg-icons";

// Import specific icons (solid, regular, or brands)
import { faArrowRight, faUser, faChartBar } from '@fortawesome/free-solid-svg-icons';

// Import the FontAwesomeIcon component
import { FontAwesomeIcon } from '@fortawesome/vue-fontawesome';

// Add icons to the library
library.add(faArrowRight, faUser, faChartBar, faDownload);

// Initialize Vuetify
const vuetify = createVuetify({
  components,
  directives,
});

// Create the Vue app
const app = createApp(App);

// Use Vuetify and the router
app.use(vuetify);
app.use(router);

// Register FontAwesomeIcon globally
app.component('font-awesome-icon', FontAwesomeIcon);

// Mount the app
app.mount('#app');
