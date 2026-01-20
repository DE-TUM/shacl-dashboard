/**
 * Violations Store Tests
 * 
 * Comprehensive tests for the violations Pinia store
 */

import { describe, it, expect, beforeEach, vi } from 'vitest';
import { setActivePinia, createPinia } from 'pinia';
import { useViolationsStore } from '@/stores/violations';
import * as api from '@/services/api';

// Mock the API module
vi.mock('@/services/api');

// Mock logger
vi.mock('@/services/logger', () => ({
  logger: {
    info: vi.fn(),
    error: vi.fn(),
    debug: vi.fn(),
    warn: vi.fn()
  }
}));

describe('useViolationsStore', () => {
  let store;

  beforeEach(() => {
    setActivePinia(createPinia());
    store = useViolationsStore();
    vi.clearAllMocks();
  });

  describe('Initial State', () => {
    it('should initialize with default values', () => {
      expect(store.totalViolations).toBe(0);
      expect(store.validationReport).toEqual([]);
      expect(store.reportTotalCount).toBe(0);
      expect(store.reportCurrentPage).toBe(1);
      expect(store.reportItemsPerPage).toBe(10);
      expect(store.distributionByShape).toBeNull();
      expect(store.currentViolation).toBeNull();
      expect(store.loading).toBe(false);
      expect(store.error).toBeNull();
    });

    it('should have correct cache timeout', () => {
      expect(store.cacheTimeout).toBe(5 * 60 * 1000);
    });
  });

  describe('Getters', () => {
    describe('isDataStale', () => {
      it('should return true when no data fetched', () => {
        expect(store.isDataStale).toBe(true);
      });

      it('should return false for fresh data', () => {
        store.lastFetchTime = Date.now();
        expect(store.isDataStale).toBe(false);
      });

      it('should return true for stale data', () => {
        store.lastFetchTime = Date.now() - (6 * 60 * 1000);
        expect(store.isDataStale).toBe(true);
      });
    });

    describe('reportTotalPages', () => {
      it('should calculate total pages correctly', () => {
        store.reportTotalCount = 100;
        store.reportItemsPerPage = 10;
        expect(store.reportTotalPages).toBe(10);
      });

      it('should round up for partial pages', () => {
        store.reportTotalCount = 95;
        store.reportItemsPerPage = 10;
        expect(store.reportTotalPages).toBe(10);
      });

      it('should return 0 for no items', () => {
        store.reportTotalCount = 0;
        store.reportItemsPerPage = 10;
        expect(store.reportTotalPages).toBe(0);
      });
    });

    describe('hasNextPage', () => {
      it('should return true when next page exists', () => {
        store.reportTotalCount = 100;
        store.reportItemsPerPage = 10;
        store.reportCurrentPage = 5;
        expect(store.hasNextPage).toBe(true);
      });

      it('should return false on last page', () => {
        store.reportTotalCount = 100;
        store.reportItemsPerPage = 10;
        store.reportCurrentPage = 10;
        expect(store.hasNextPage).toBe(false);
      });
    });

    describe('hasPrevPage', () => {
      it('should return true when on page > 1', () => {
        store.reportCurrentPage = 2;
        expect(store.hasPrevPage).toBe(true);
      });

      it('should return false on first page', () => {
        store.reportCurrentPage = 1;
        expect(store.hasPrevPage).toBe(false);
      });
    });
  });

  describe('Actions', () => {
    describe('loadViolationsCount', () => {
      it('should load violations count successfully', async () => {
        api.getViolationsCount.mockResolvedValue({ violationCount: 150 });

        await store.loadViolationsCount();

        expect(store.totalViolations).toBe(150);
        expect(store.error).toBeNull();
        expect(store.lastFetchTime).toBeTruthy();
        expect(api.getViolationsCount).toHaveBeenCalledWith(null);
      });

      it('should pass graphUri parameter', async () => {
        api.getViolationsCount.mockResolvedValue({ violationCount: 150 });

        await store.loadViolationsCount('http://example.org/graph');

        expect(api.getViolationsCount).toHaveBeenCalledWith('http://example.org/graph');
      });

      it('should use cache when data is fresh', async () => {
        api.getViolationsCount.mockResolvedValue({ violationCount: 150 });
        
        await store.loadViolationsCount();
        vi.clearAllMocks();

        await store.loadViolationsCount(null, false);

        expect(api.getViolationsCount).not.toHaveBeenCalled();
      });

      it('should force refresh when requested', async () => {
        api.getViolationsCount.mockResolvedValue({ violationCount: 150 });
        
        await store.loadViolationsCount();
        vi.clearAllMocks();

        await store.loadViolationsCount(null, true);

        expect(api.getViolationsCount).toHaveBeenCalled();
      });

      it('should handle API errors', async () => {
        api.getViolationsCount.mockRejectedValue(new Error('API Error'));

        await expect(store.loadViolationsCount()).rejects.toThrow('API Error');
        expect(store.error).toBeTruthy();
        expect(store.loading).toBe(false);
      });

      it('should handle missing data', async () => {
        api.getViolationsCount.mockResolvedValue({});

        await store.loadViolationsCount();

        expect(store.totalViolations).toBe(0);
      });

      it('should set loading states correctly', async () => {
        api.getViolationsCount.mockResolvedValue({ violationCount: 150 });
        
        const promise = store.loadViolationsCount();
        expect(store.loading).toBe(true);
        
        await promise;
        expect(store.loading).toBe(false);
      });
    });

    describe('loadValidationReport', () => {
      it('should load validation report with default pagination', async () => {
        const mockViolations = [
          { id: 1, message: 'Violation 1' },
          { id: 2, message: 'Violation 2' }
        ];
        api.getValidationDetailsReport.mockResolvedValue({
          violations: mockViolations,
          total: 100
        });

        await store.loadValidationReport();

        expect(store.validationReport).toEqual(mockViolations);
        expect(store.reportTotalCount).toBe(100);
        expect(store.reportCurrentPage).toBe(1);
        expect(store.reportItemsPerPage).toBe(10);
        expect(api.getValidationDetailsReport).toHaveBeenCalledWith(10, 0);
      });

      it('should support custom pagination', async () => {
        api.getValidationDetailsReport.mockResolvedValue({
          violations: [],
          total: 100
        });

        await store.loadValidationReport(25, 50);

        expect(api.getValidationDetailsReport).toHaveBeenCalledWith(25, 50);
        expect(store.reportCurrentPage).toBe(3); // offset 50 / limit 25 + 1
        expect(store.reportItemsPerPage).toBe(25);
      });

      it('should handle empty results', async () => {
        api.getValidationDetailsReport.mockResolvedValue({
          violations: [],
          total: 0
        });

        await store.loadValidationReport();

        expect(store.validationReport).toEqual([]);
        expect(store.reportTotalCount).toBe(0);
      });

      it('should handle API errors', async () => {
        api.getValidationDetailsReport.mockRejectedValue(new Error('Report failed'));

        await expect(store.loadValidationReport()).rejects.toThrow();
        expect(store.error).toBeTruthy();
        expect(store.reportLoading).toBe(false);
      });

      it('should clear previous errors', async () => {
        store.error = 'Previous error';
        api.getValidationDetailsReport.mockResolvedValue({ violations: [], total: 0 });

        await store.loadValidationReport();

        expect(store.error).toBeNull();
      });
    });

    describe('loadNextPage', () => {
      beforeEach(() => {
        api.getValidationDetailsReport.mockResolvedValue({ violations: [], total: 100 });
      });

      it('should load next page', async () => {
        store.reportCurrentPage = 2;
        store.reportItemsPerPage = 10;
        store.reportTotalCount = 100;

        await store.loadNextPage();

        expect(api.getValidationDetailsReport).toHaveBeenCalledWith(10, 20);
      });

      it('should not load if on last page', async () => {
        store.reportCurrentPage = 10;
        store.reportItemsPerPage = 10;
        store.reportTotalCount = 100;

        await store.loadNextPage();

        expect(api.getValidationDetailsReport).not.toHaveBeenCalled();
      });
    });

    describe('loadPrevPage', () => {
      beforeEach(() => {
        api.getValidationDetailsReport.mockResolvedValue({ violations: [], total: 100 });
      });

      it('should load previous page', async () => {
        store.reportCurrentPage = 3;
        store.reportItemsPerPage = 10;

        await store.loadPrevPage();

        expect(api.getValidationDetailsReport).toHaveBeenCalledWith(10, 10);
      });

      it('should not load if on first page', async () => {
        store.reportCurrentPage = 1;
        store.reportItemsPerPage = 10;

        await store.loadPrevPage();

        expect(api.getValidationDetailsReport).not.toHaveBeenCalled();
      });
    });

    describe('loadDistributions', () => {
      beforeEach(() => {
        api.getViolationsDistributionPerShape.mockResolvedValue({ labels: ['A'], datasets: [] });
        api.getViolationsDistributionPerPath.mockResolvedValue({ labels: ['P'], datasets: [] });
        api.getViolationsDistributionPerFocusNode.mockResolvedValue({ labels: ['F'], datasets: [] });
        api.getViolationsDistributionPerConstraintComponent.mockResolvedValue({ labels: ['C'], datasets: [] });
      });

      it('should load all distributions in parallel', async () => {
        await store.loadDistributions();

        expect(store.distributionByShape).toBeDefined();
        expect(store.distributionByPath).toBeDefined();
        expect(store.distributionByFocusNode).toBeDefined();
        expect(store.distributionByConstraint).toBeDefined();
        expect(store.error).toBeNull();
      });

      it('should set loading states correctly', async () => {
        const promise = store.loadDistributions();
        expect(store.distributionsLoading).toBe(true);

        await promise;
        expect(store.distributionsLoading).toBe(false);
      });

      it('should handle API errors', async () => {
        api.getViolationsDistributionPerShape.mockRejectedValue(new Error('Distribution failed'));

        await expect(store.loadDistributions()).rejects.toThrow();
        expect(store.error).toBeTruthy();
        expect(store.distributionsLoading).toBe(false);
      });
    });

    // Note: loadViolationDetails tests skipped - getViolationDetails API function doesn't exist yet

    describe('clearCurrentViolation', () => {
      it('should clear current violation', () => {
        store.currentViolation = { id: 'v1', message: 'Test' };

        store.clearCurrentViolation();

        expect(store.currentViolation).toBeNull();
      });
    });

    describe('resetPagination', () => {
      it('should reset pagination to defaults', () => {
        store.reportCurrentPage = 5;
        store.validationReport = [{ id: 1 }];

        store.resetPagination();

        expect(store.reportCurrentPage).toBe(1);
        expect(store.validationReport).toEqual([]);
      });
    });

    describe('resetStore', () => {
      it('should reset entire store to initial state', () => {
        store.totalViolations = 150;
        store.validationReport = [{ id: 1 }];
        store.reportCurrentPage = 5;
        store.error = 'Some error';

        store.resetStore();

        expect(store.totalViolations).toBe(0);
        expect(store.validationReport).toEqual([]);
        expect(store.reportCurrentPage).toBe(1);
        expect(store.error).toBeNull();
      });
    });
  });

  describe('Pagination Logic', () => {
    beforeEach(() => {
      api.getValidationDetailsReport.mockResolvedValue({ violations: [], total: 100 });
      store.reportItemsPerPage = 10;
      store.reportTotalCount = 100;
    });

    it('should correctly navigate through pages', async () => {
      // Start on page 1
      expect(store.reportCurrentPage).toBe(1);
      expect(store.hasNextPage).toBe(true);
      expect(store.hasPrevPage).toBe(false);

      // Go to page 2
      await store.loadNextPage();
      expect(store.reportCurrentPage).toBe(2);
      expect(store.hasNextPage).toBe(true);
      expect(store.hasPrevPage).toBe(true);

      // Go back to page 1
      await store.loadPrevPage();
      expect(store.reportCurrentPage).toBe(1);
      expect(store.hasPrevPage).toBe(false);
    });

    it('should handle boundary conditions', async () => {
      // Jump to last page
      await store.loadValidationReport(10, 90);
      expect(store.reportCurrentPage).toBe(10);
      expect(store.hasNextPage).toBe(false);
      expect(store.hasPrevPage).toBe(true);

      // Try to go next (should not call API)
      vi.clearAllMocks();
      await store.loadNextPage();
      expect(api.getValidationDetailsReport).not.toHaveBeenCalled();

      // Go back
      await store.loadPrevPage();
      expect(store.reportCurrentPage).toBe(9);
    });
  });

  describe('Error Recovery', () => {
    it('should recover from error on subsequent successful request', async () => {
      // First request fails
      api.getViolationsCount.mockRejectedValueOnce(new Error('Network error'));
      
      try {
        await store.loadViolationsCount();
      } catch (e) {
        // Expected
      }
      
      expect(store.error).toBeTruthy();

      // Second request succeeds
      api.getViolationsCount.mockResolvedValue({ violationCount: 150 });
      await store.loadViolationsCount(null, true);

      expect(store.error).toBeNull();
      expect(store.totalViolations).toBe(150);
    });
  });

  describe('Cache Behavior', () => {
    it('should update lastFetchTime after successful load', async () => {
      api.getViolationsCount.mockResolvedValue({ violationCount: 150 });

      const beforeTime = Date.now();
      await store.loadViolationsCount();
      const afterTime = Date.now();

      expect(store.lastFetchTime).toBeGreaterThanOrEqual(beforeTime);
      expect(store.lastFetchTime).toBeLessThanOrEqual(afterTime);
    });

    it('should not update cache time on error', async () => {
      api.getViolationsCount.mockRejectedValue(new Error('Failed'));

      const initialTime = store.lastFetchTime;

      try {
        await store.loadViolationsCount();
      } catch (e) {
        // Expected
      }

      expect(store.lastFetchTime).toBe(initialTime);
    });
  });
});
