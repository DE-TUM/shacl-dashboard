/**
 * Constraints Store
 * 
 * Pinia store for managing SHACL constraint data,
 * including constraint components, counts, and distributions.
 * 
 * @module stores/constraints
 */

import { defineStore } from 'pinia';
import { logger } from '@/services/logger';
import {
  getMostFrequentConstraintComponent,
  getDistinctConstraintComponentsCount,
  getDistinctConstraintsCountInShapes,
  getViolationsDistributionPerConstraintComponent,
  getConstraintCountForNodeShape
} from '@/services/api';

export const useConstraintsStore = defineStore('constraints', {
  state: () => ({
    // Constraint statistics
    mostFrequentConstraint: null,
    distinctConstraintComponents: 0,
    distinctConstraintsInShapes: 0,
    
    // Distributions
    violationsDistribution: null,
    
    // Current constraint
    currentConstraintCount: 0,
    currentNodeShape: null,
    
    // Loading states
    loading: false,
    distributionLoading: false,
    
    // Error handling
    error: null,
    
    // Cache
    lastFetchTime: null,
    cacheTimeout: 5 * 60 * 1000 // 5 minutes
  }),

  getters: {
    /**
     * Check if data is stale
     */
    isDataStale: (state) => {
      if (!state.lastFetchTime) return true;
      return Date.now() - state.lastFetchTime > state.cacheTimeout;
    },

    /**
     * Get most frequent constraint name
     */
    mostFrequentConstraintName: (state) => {
      return state.mostFrequentConstraint?.constraintComponent || 'N/A';
    },

    /**
     * Get most frequent constraint occurrences
     */
    mostFrequentConstraintOccurrences: (state) => {
      return state.mostFrequentConstraint?.occurrences || 0;
    }
  },

  actions: {
    /**
     * Load constraint overview statistics
     */
    async loadOverview(forceRefresh = false) {
      if (!forceRefresh && !this.isDataStale && this.mostFrequentConstraint) {
        logger.debug('Using cached constraints overview');
        return;
      }

      this.loading = true;
      this.error = null;

      try {
        const [mostFrequent, distinctComponents, distinctInShapes] = await Promise.all([
          getMostFrequentConstraintComponent(),
          getDistinctConstraintComponentsCount(),
          getDistinctConstraintsCountInShapes()
        ]);

        this.mostFrequentConstraint = mostFrequent;
        this.distinctConstraintComponents = distinctComponents.distinctConstraintComponentCount || 0;
        this.distinctConstraintsInShapes = distinctInShapes.distinctConstraintsCount || 0;
        
        this.lastFetchTime = Date.now();
        logger.info('Constraints overview loaded successfully');
      } catch (error) {
        this.error = error.message || 'Failed to load constraints overview';
        logger.error('Error loading constraints overview:', error);
        throw error;
      } finally {
        this.loading = false;
      }
    },

    /**
     * Load violations distribution by constraint component
     */
    async loadDistribution() {
      this.distributionLoading = true;
      this.error = null;

      try {
        const data = await getViolationsDistributionPerConstraintComponent();
        this.violationsDistribution = data;
        logger.info('Constraint violations distribution loaded');
      } catch (error) {
        this.error = error.message || 'Failed to load constraint distribution';
        logger.error('Error loading constraint distribution:', error);
        throw error;
      } finally {
        this.distributionLoading = false;
      }
    },

    /**
     * Load constraint count for a specific node shape
     */
    async loadConstraintCountForShape(nodeShape) {
      this.loading = true;
      this.error = null;
      this.currentNodeShape = nodeShape;

      try {
        const data = await getConstraintCountForNodeShape(nodeShape);
        this.currentConstraintCount = data.constraintCount || 0;
        logger.info(`Constraint count for shape ${nodeShape}: ${this.currentConstraintCount}`);
      } catch (error) {
        this.error = error.message || 'Failed to load constraint count';
        logger.error('Error loading constraint count:', error);
        throw error;
      } finally {
        this.loading = false;
      }
    },

    /**
     * Clear current constraint data
     */
    clearCurrent() {
      this.currentConstraintCount = 0;
      this.currentNodeShape = null;
    },

    /**
     * Reset all state
     */
    resetStore() {
      this.$reset();
    }
  }
});
