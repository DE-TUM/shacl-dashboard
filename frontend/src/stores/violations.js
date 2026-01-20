/**
 * Violations Store
 * 
 * Pinia store for managing SHACL validation violations data,
 * including violation reports, details, and distributions.
 * 
 * @module stores/violations
 */

import { defineStore } from 'pinia';
import { logger } from '@/services/logger';
import {
  getViolationsCount,
  getValidationDetailsReport,
  getViolationsDistributionPerShape,
  getViolationsDistributionPerPath,
  getViolationsDistributionPerFocusNode,
  getViolationsDistributionPerConstraintComponent
} from '@/services/api';

export const useViolationsStore = defineStore('violations', {
  state: () => ({
    // Violation counts
    totalViolations: 0,
    
    // Validation report
    validationReport: [],
    reportTotalCount: 0,
    reportCurrentPage: 1,
    reportItemsPerPage: 10,
    
    // Distributions
    distributionByShape: null,
    distributionByPath: null,
    distributionByFocusNode: null,
    distributionByConstraint: null,
    
    // Current violation details
    currentViolation: null,
    
    // Loading states
    loading: false,
    reportLoading: false,
    distributionsLoading: false,
    
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
     * Get total pages for validation report
     */
    reportTotalPages: (state) => {
      return Math.ceil(state.reportTotalCount / state.reportItemsPerPage);
    },

    /**
     * Check if there's a next page
     */
    hasNextPage: (state) => {
      return state.reportCurrentPage < Math.ceil(state.reportTotalCount / state.reportItemsPerPage);
    },

    /**
     * Check if there's a previous page
     */
    hasPrevPage: (state) => {
      return state.reportCurrentPage > 1;
    }
  },

  actions: {
    /**
     * Load total violations count
     */
    async loadViolationsCount(graphUri = null, forceRefresh = false) {
      if (!forceRefresh && !this.isDataStale && this.totalViolations > 0) {
        logger.debug('Using cached violations count');
        return;
      }

      this.loading = true;
      this.error = null;

      try {
        const data = await getViolationsCount(graphUri);
        this.totalViolations = data.violationCount || 0;
        this.lastFetchTime = Date.now();
        logger.info(`Total violations: ${this.totalViolations}`);
      } catch (error) {
        this.error = error.message || 'Failed to load violations count';
        logger.error('Error loading violations count:', error);
        throw error;
      } finally {
        this.loading = false;
      }
    },

    /**
     * Load validation details report with pagination
     */
    async loadValidationReport(limit = 10, offset = 0) {
      this.reportLoading = true;
      this.error = null;

      try {
        const data = await getValidationDetailsReport(limit, offset);
        this.validationReport = data.violations || [];
        this.reportTotalCount = data.total || 0;
        this.reportCurrentPage = Math.floor(offset / limit) + 1;
        this.reportItemsPerPage = limit;
        
        logger.info(`Loaded ${this.validationReport.length} violations`);
      } catch (error) {
        this.error = error.message || 'Failed to load validation report';
        logger.error('Error loading validation report:', error);
        throw error;
      } finally {
        this.reportLoading = false;
      }
    },

    /**
     * Load next page of validation report
     */
    async loadNextPage() {
      if (!this.hasNextPage) return;
      
      const offset = this.reportCurrentPage * this.reportItemsPerPage;
      await this.loadValidationReport(this.reportItemsPerPage, offset);
    },

    /**
     * Load previous page of validation report
     */
    async loadPrevPage() {
      if (!this.hasPrevPage) return;
      
      const offset = (this.reportCurrentPage - 2) * this.reportItemsPerPage;
      await this.loadValidationReport(this.reportItemsPerPage, offset);
    },

    /**
     * Load all violation distributions
     */
    async loadDistributions() {
      this.distributionsLoading = true;
      this.error = null;

      try {
        const [byShape, byPath, byFocusNode, byConstraint] = await Promise.all([
          getViolationsDistributionPerShape(),
          getViolationsDistributionPerPath(),
          getViolationsDistributionPerFocusNode(),
          getViolationsDistributionPerConstraintComponent()
        ]);

        this.distributionByShape = byShape;
        this.distributionByPath = byPath;
        this.distributionByFocusNode = byFocusNode;
        this.distributionByConstraint = byConstraint;

        logger.info('Violation distributions loaded successfully');
      } catch (error) {
        this.error = error.message || 'Failed to load distributions';
        logger.error('Error loading distributions:', error);
        throw error;
      } finally {
        this.distributionsLoading = false;
      }
    },

    /**
     * Clear current violation
     */
    clearCurrentViolation() {
      this.currentViolation = null;
    },

    /**
     * Reset pagination
     */
    resetPagination() {
      this.reportCurrentPage = 1;
      this.validationReport = [];
    },

    /**
     * Reset all state
     */
    resetStore() {
      this.$reset();
    }
  }
});
