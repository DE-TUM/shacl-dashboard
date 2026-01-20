/**
 * Shapes Store
 * 
 * Pinia store for managing SHACL shape data, including node shapes,
 * property shapes, and their associated violations.
 * 
 * @module stores/shapes
 */

import { defineStore } from 'pinia';
import { logger } from '@/services/logger';
import {
  getNodeShapesCount,
  getNodeShapesWithViolationsCount,
  getMostViolatedNodeShape,
  getViolationsPerNodeShape,
  getNodeShapeDetailsTable,
  getNodeShapesCountInGraph,
  getNodeShapesWithViolationsCountOverview,
  getMaxViolationsForNodeShape,
  getAverageViolationsForNodeShapes,
  getViolationsDistribution,
  getCorrelationData,
  getPropertyShapesForNodeShape,
  getViolationCountForNodeShape,
  getViolatedFocusNodesCountForNodeShape,
  getPropertyPathsCountForNodeShape,
  getConstraintCountForNodeShape,
  getViolationsPerConstraintTypeForPropertyShape,
  getShapeDefinition
} from '@/services/api';

export const useShapesStore = defineStore('shapes', {
  state: () => ({
    // Overview data
    nodeShapes: [],
    totalNodeShapes: 0,
    nodeShapesWithViolations: 0,
    maxViolationsPerShape: 0,
    avgViolationsPerShape: 0,
    mostViolatedShape: null,
    
    // Current shape details
    currentShape: null,
    currentShapeDefinition: null,
    currentShapeViolationCount: 0,
    currentShapeAffectedFocusNodes: 0,
    currentShapePropertyPathsCount: 0,
    currentShapeConstraintCount: 0,
    
    // Property shapes
    propertyShapes: [],
    propertyShapesLoading: false,
    
    // Chart data
    violationsDistribution: null,
    correlationData: null,
    violationsPerShape: null,
    
    // Loading states
    loading: false,
    overviewLoading: false,
    detailsLoading: false,
    
    // Error handling
    error: null,
    
    // Cache timestamps
    lastFetchTime: null,
    cacheTimeout: 5 * 60 * 1000 // 5 minutes
  }),

  getters: {
    /**
     * Get percentage of shapes with violations
     */
    violationPercentage: (state) => {
      if (state.totalNodeShapes === 0) return 0;
      return ((state.nodeShapesWithViolations / state.totalNodeShapes) * 100).toFixed(1);
    },

    /**
     * Check if overview data is stale
     */
    isDataStale: (state) => {
      if (!state.lastFetchTime) return true;
      return Date.now() - state.lastFetchTime > state.cacheTimeout;
    },

    /**
     * Get shapes sorted by violation count
     */
    shapesSortedByViolations: (state) => {
      return [...state.nodeShapes].sort((a, b) => 
        (b.violations || 0) - (a.violations || 0)
      );
    },

    /**
     * Get shapes with zero violations
     */
    shapesWithoutViolations: (state) => {
      return state.nodeShapes.filter(shape => !shape.violations || shape.violations === 0);
    },

    /**
     * Get top N most violated shapes
     */
    topViolatedShapes: (state) => (n = 10) => {
      return [...state.nodeShapes]
        .sort((a, b) => (b.violations || 0) - (a.violations || 0))
        .slice(0, n);
    }
  },

  actions: {
    /**
     * Load shape overview data (tags and statistics)
     */
    async loadOverview(forceRefresh = false) {
      // Use cache if available and not stale
      if (!forceRefresh && !this.isDataStale && this.nodeShapes.length > 0) {
        logger.debug('Using cached shapes overview data');
        return;
      }

      this.overviewLoading = true;
      this.error = null;

      try {
        // Load all overview data in parallel
        const [
          totalShapesData,
          shapesWithViolationsData,
          maxViolationsData,
          avgViolationsData,
          mostViolatedData
        ] = await Promise.all([
          getNodeShapesCountInGraph(),
          getNodeShapesWithViolationsCountOverview(),
          getMaxViolationsForNodeShape(),
          getAverageViolationsForNodeShapes(),
          getMostViolatedNodeShape()
        ]);

        // Update state
        this.totalNodeShapes = totalShapesData.nodeShapeCount || 0;
        this.nodeShapesWithViolations = shapesWithViolationsData.nodeShapesWithViolationsCount || 0;
        this.maxViolationsPerShape = maxViolationsData.violationCount || 0;
        this.avgViolationsPerShape = avgViolationsData.averageViolations || 0;
        this.mostViolatedShape = mostViolatedData;
        
        this.lastFetchTime = Date.now();
        logger.info('Shapes overview loaded successfully');
      } catch (error) {
        this.error = error.message || 'Failed to load shapes overview';
        logger.error('Error loading shapes overview:', error);
        throw error;
      } finally {
        this.overviewLoading = false;
      }
    },

    /**
     * Load detailed table data for shapes
     */
    async loadShapesTable() {
      this.loading = true;
      this.error = null;

      try {
        const tableData = await getNodeShapeDetailsTable();
        this.nodeShapes = tableData.nodeShapes || [];
        logger.info(`Loaded ${this.nodeShapes.length} shapes`);
      } catch (error) {
        this.error = error.message || 'Failed to load shapes table';
        logger.error('Error loading shapes table:', error);
        throw error;
      } finally {
        this.loading = false;
      }
    },

    /**
     * Load chart data (distributions and correlations)
     */
    async loadChartData(bins = 10) {
      this.loading = true;
      this.error = null;

      try {
        const [histogramData, correlationData, violationsData] = await Promise.all([
          getViolationsDistribution(bins),
          getCorrelationData(),
          getViolationsPerNodeShape()
        ]);

        this.violationsDistribution = histogramData;
        this.correlationData = correlationData;
        this.violationsPerShape = violationsData;
        
        logger.info('Shapes chart data loaded successfully');
      } catch (error) {
        this.error = error.message || 'Failed to load chart data';
        logger.error('Error loading chart data:', error);
        throw error;
      } finally {
        this.loading = false;
      }
    },

    /**
     * Load complete overview (overview + table + charts)
     */
    async loadCompleteOverview(forceRefresh = false) {
      try {
        await Promise.all([
          this.loadOverview(forceRefresh),
          this.loadShapesTable(),
          this.loadChartData()
        ]);
      } catch (error) {
        // Errors are already logged in individual methods
        throw error;
      }
    },

    /**
     * Load details for a specific shape
     */
    async loadShapeDetails(shapeUri) {
      this.detailsLoading = true;
      this.error = null;
      this.currentShape = shapeUri;

      try {
        // Load all shape details in parallel
        const [
          violationCountData,
          focusNodesData,
          pathsCountData,
          constraintCountData,
          definitionData
        ] = await Promise.all([
          getViolationCountForNodeShape(shapeUri),
          getViolatedFocusNodesCountForNodeShape(shapeUri),
          getPropertyPathsCountForNodeShape(shapeUri),
          getConstraintCountForNodeShape(shapeUri),
          getShapeDefinition(shapeUri)
        ]);

        this.currentShapeViolationCount = violationCountData.violationCount || 0;
        this.currentShapeAffectedFocusNodes = focusNodesData.focusNodeCount || 0;
        this.currentShapePropertyPathsCount = pathsCountData.pathCount || 0;
        this.currentShapeConstraintCount = constraintCountData.constraintCount || 0;
        this.currentShapeDefinition = definitionData.definition || '';

        logger.info(`Shape details loaded for: ${shapeUri}`);
      } catch (error) {
        this.error = error.message || 'Failed to load shape details';
        logger.error('Error loading shape details:', error);
        throw error;
      } finally {
        this.detailsLoading = false;
      }
    },

    /**
     * Load property shapes for a node shape
     */
    async loadPropertyShapes(nodeShape, limit = 100, offset = 0) {
      this.propertyShapesLoading = true;
      this.error = null;

      try {
        const data = await getPropertyShapesForNodeShape(nodeShape, limit, offset);
        this.propertyShapes = data.propertyShapes || [];
        logger.info(`Loaded ${this.propertyShapes.length} property shapes`);
        return data;
      } catch (error) {
        this.error = error.message || 'Failed to load property shapes';
        logger.error('Error loading property shapes:', error);
        throw error;
      } finally {
        this.propertyShapesLoading = false;
      }
    },

    /**
     * Clear current shape details
     */
    clearShapeDetails() {
      this.currentShape = null;
      this.currentShapeDefinition = null;
      this.currentShapeViolationCount = 0;
      this.currentShapeAffectedFocusNodes = 0;
      this.currentShapePropertyPathsCount = 0;
      this.currentShapeConstraintCount = 0;
      this.propertyShapes = [];
    },

    /**
     * Reset all state
     */
    resetStore() {
      this.$reset();
    }
  }
});
