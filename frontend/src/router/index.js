/**
 * Router Configuration
 * 
 * Defines all routes for the SHACL Dashboard application.
 * Handles navigation between different views and components.
 * 
 * Routes include:
 * - Home (MainContent)
 * - Shape overview and detailed views
 * - Constraint overview and detailed views
 * - Focus Node overview and detailed views
 * - Property Path overview and detailed views
 * - About Us page
 * 
 * @dependencies
 * - vue-router
 * - Component imports from across the application
 * 
 * @returns {VueRouter} A configured Vue Router instance with history mode enabled
 * and all application routes defined, ready for integration with the Vue application.
 */
import { createRouter, createWebHistory } from "vue-router";

// Import components
import LandingPage from "@/components/LandingPage.vue"; // Your landing page component
import MainContent from "@/components/Layout/MainContent.vue"; // Home component

import ShapeOverview from "@/components/Overviews/ShapeOverview.vue";
import ShapeView from "@/components/Views/ShapeView.vue";
import ConstraintOverview from "@/components/Overviews/ConstraintOverview.vue";
import ConstraintView from "@/components/Views/ConstraintView.vue";
import FocusNodeOverview from "@/components/Overviews/FocusNodeOverview.vue";
import FocusNodeView from "@/components/Views/FocusNodeView.vue";
import PropertyPathOverview from "@/components/Overviews/PropertyPathOverview.vue";
import PropertyPathView from "@/components/Views/PropertyPathView.vue";
import AboutUs from "@/components/Overviews/AboutUs.vue";

const routes = [
  //{ path: "/", name: "LandingPage", component: LandingPage }, // Landing page route
  { path: "/", name: "Home", component: MainContent }, // Main content after landing page
  { path: "/shapes", name: "ShapeOverview", component: ShapeOverview },
  { path: "/shapes/:shapeId", name: "ShapeView", component: ShapeView },
  { path: "/constraints", name: "ConstraintOverview", component: ConstraintOverview },
  { path: "/constraints/:constraintId/:constraintName/:constraintViolations", name: "ConstraintView", component: ConstraintView },
  { path: "/focus-nodes", name: "FocusNodeOverview", component: FocusNodeOverview },
  { path: "/focus-nodes/:focusNodeId", name: "FocusNodeView", component: FocusNodeView },
  { path: "/property-paths", name: "PropertyPathOverview", component: PropertyPathOverview },
  { path: "/property-paths/:pathId", name: "PropertyPathView", component: PropertyPathView },
  { path: "/about-us", name: "AboutUs", component: AboutUs },
];

// Create the router instance
const router = createRouter({
  history: createWebHistory(),
  routes,
});

export default router;
