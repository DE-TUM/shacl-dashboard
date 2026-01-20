/**
 * Constraints Store Tests
 * 
 * Comprehensive tests for the constraints Pinia store
 */

import { describe, it, expect, beforeEach, vi } from 'vitest';
import { setActivePinia, createPinia } from 'pinia';
import { useConstraintsStore } from '@/stores/constraints';
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

describe('useConstraintsStore', () => {
  let store;

  beforeEach(() => {
    setActivePinia(createPinia());
    store = useConstraintsStore();
    vi.clearAllMocks();
  });

  describe('Initial State', () => {
    it('should initialize with default values', () => {
      expect(store.mostFrequentConstraint).toBeNull();
      expect(store.distinctConstraintComponents).toBe(0);
      expect(store.distinctConstraintsInShapes).toBe(0);
      expect(store.violationsDistribution).toBeNull();
      expect(store.currentConstraintCount).toBe(0);
      expect(store.currentNodeShape).toBeNull();
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

    describe('mostFrequentConstraintName', () => {
      it('should return constraint name when set', () => {
        store.mostFrequentConstraint = {
          constraintComponent: 'sh:MinCountConstraint',
          occurrences: 50
        };
        expect(store.mostFrequentConstraintName).toBe('sh:MinCountConstraint');
      });

      it('should return N/A when no constraint set', () => {
        expect(store.mostFrequentConstraintName).toBe('N/A');
      });

      it('should handle null constraint', () => {
        store.mostFrequentConstraint = null;
        expect(store.mostFrequentConstraintName).toBe('N/A');
      });
    });

    describe('mostFrequentConstraintOccurrences', () => {
      it('should return occurrences when set', () => {
        store.mostFrequentConstraint = {
          constraintComponent: 'sh:MinCountConstraint',
          occurrences: 50
        };
        expect(store.mostFrequentConstraintOccurrences).toBe(50);
      });

      it('should return 0 when no constraint set', () => {
        expect(store.mostFrequentConstraintOccurrences).toBe(0);
      });
    });
  });

  describe('Actions', () => {
    describe('loadOverview', () => {
      beforeEach(() => {
        api.getMostFrequentConstraintComponent.mockResolvedValue({
          constraintComponent: 'sh:MinCountConstraint',
          occurrences: 50
        });
        api.getDistinctConstraintComponentsCount.mockResolvedValue({
          distinctConstraintComponentCount: 15
        });
        api.getDistinctConstraintsCountInShapes.mockResolvedValue({
          distinctConstraintsCount: 100
        });
      });

      it('should load overview data successfully', async () => {
        await store.loadOverview();

        expect(store.mostFrequentConstraint).toEqual({
          constraintComponent: 'sh:MinCountConstraint',
          occurrences: 50
        });
        expect(store.distinctConstraintComponents).toBe(15);
        expect(store.distinctConstraintsInShapes).toBe(100);
        expect(store.error).toBeNull();
        expect(store.lastFetchTime).toBeTruthy();
      });

      it('should set loading states correctly', async () => {
        const promise = store.loadOverview();
        expect(store.loading).toBe(true);

        await promise;
        expect(store.loading).toBe(false);
      });

      it('should use cache when data is fresh', async () => {
        await store.loadOverview();
        vi.clearAllMocks();

        await store.loadOverview(false);

        expect(api.getMostFrequentConstraintComponent).not.toHaveBeenCalled();
      });

      it('should force refresh when requested', async () => {
        await store.loadOverview();
        vi.clearAllMocks();

        await store.loadOverview(true);

        expect(api.getMostFrequentConstraintComponent).toHaveBeenCalled();
        expect(api.getDistinctConstraintComponentsCount).toHaveBeenCalled();
        expect(api.getDistinctConstraintsCountInShapes).toHaveBeenCalled();
      });

      it('should handle API errors', async () => {
        api.getMostFrequentConstraintComponent.mockRejectedValue(new Error('API Error'));

        await expect(store.loadOverview()).rejects.toThrow('API Error');
        expect(store.error).toBeTruthy();
        expect(store.loading).toBe(false);
      });

      it('should handle missing data gracefully', async () => {
        api.getMostFrequentConstraintComponent.mockResolvedValue({});
        api.getDistinctConstraintComponentsCount.mockResolvedValue({});
        api.getDistinctConstraintsCountInShapes.mockResolvedValue({});

        await store.loadOverview();

        expect(store.distinctConstraintComponents).toBe(0);
        expect(store.distinctConstraintsInShapes).toBe(0);
      });

      it('should clear previous errors', async () => {
        store.error = 'Previous error';

        await store.loadOverview();

        expect(store.error).toBeNull();
      });

      it('should load all data in parallel', async () => {
        const startTime = Date.now();
        await store.loadOverview();
        const duration = Date.now() - startTime;

        // Verify all APIs were called
        expect(api.getMostFrequentConstraintComponent).toHaveBeenCalled();
        expect(api.getDistinctConstraintComponentsCount).toHaveBeenCalled();
        expect(api.getDistinctConstraintsCountInShapes).toHaveBeenCalled();

        // Parallel execution should be fast (relative check)
        expect(duration).toBeLessThan(1000);
      });
    });

    describe('loadDistribution', () => {
      it('should load distribution data successfully', async () => {
        const mockDistribution = {
          labels: ['sh:MinCount', 'sh:MaxCount', 'sh:Pattern'],
          datasets: [{ data: [50, 30, 20] }]
        };
        api.getViolationsDistributionPerConstraintComponent.mockResolvedValue(mockDistribution);

        await store.loadDistribution();

        expect(store.violationsDistribution).toEqual(mockDistribution);
        expect(store.error).toBeNull();
      });

      it('should set loading states correctly', async () => {
        api.getViolationsDistributionPerConstraintComponent.mockResolvedValue({ labels: [], datasets: [] });

        const promise = store.loadDistribution();
        expect(store.distributionLoading).toBe(true);

        await promise;
        expect(store.distributionLoading).toBe(false);
      });

      it('should handle API errors', async () => {
        api.getViolationsDistributionPerConstraintComponent.mockRejectedValue(new Error('Distribution failed'));

        await expect(store.loadDistribution()).rejects.toThrow();
        expect(store.error).toBeTruthy();
        expect(store.distributionLoading).toBe(false);
      });

      it('should clear previous errors', async () => {
        store.error = 'Previous error';
        api.getViolationsDistributionPerConstraintComponent.mockResolvedValue({ labels: [], datasets: [] });

        await store.loadDistribution();

        expect(store.error).toBeNull();
      });

      it('should handle empty distribution data', async () => {
        api.getViolationsDistributionPerConstraintComponent.mockResolvedValue({
          labels: [],
          datasets: []
        });

        await store.loadDistribution();

        expect(store.violationsDistribution).toEqual({ labels: [], datasets: [] });
      });
    });

    describe('loadConstraintCountForShape', () => {
      const mockNodeShape = 'http://example.org/PersonShape';

      it('should load constraint count successfully', async () => {
        api.getConstraintCountForNodeShape.mockResolvedValue({ constraintCount: 25 });

        await store.loadConstraintCountForShape(mockNodeShape);

        expect(store.currentConstraintCount).toBe(25);
        expect(store.currentNodeShape).toBe(mockNodeShape);
        expect(store.error).toBeNull();
        expect(api.getConstraintCountForNodeShape).toHaveBeenCalledWith(mockNodeShape);
      });

      it('should set loading states correctly', async () => {
        api.getConstraintCountForNodeShape.mockResolvedValue({ constraintCount: 25 });

        const promise = store.loadConstraintCountForShape(mockNodeShape);
        expect(store.loading).toBe(true);

        await promise;
        expect(store.loading).toBe(false);
      });

      it('should handle API errors', async () => {
        api.getConstraintCountForNodeShape.mockRejectedValue(new Error('Count failed'));

        await expect(store.loadConstraintCountForShape(mockNodeShape)).rejects.toThrow();
        expect(store.error).toBeTruthy();
        expect(store.loading).toBe(false);
      });

      it('should handle missing count data', async () => {
        api.getConstraintCountForNodeShape.mockResolvedValue({});

        await store.loadConstraintCountForShape(mockNodeShape);

        expect(store.currentConstraintCount).toBe(0);
      });

      it('should update node shape even on error', async () => {
        api.getConstraintCountForNodeShape.mockRejectedValue(new Error('Failed'));

        try {
          await store.loadConstraintCountForShape(mockNodeShape);
        } catch (e) {
          // Expected
        }

        expect(store.currentNodeShape).toBe(mockNodeShape);
      });

      it('should handle different node shapes', async () => {
        api.getConstraintCountForNodeShape.mockResolvedValue({ constraintCount: 10 });
        await store.loadConstraintCountForShape('http://example.org/Shape1');
        expect(store.currentConstraintCount).toBe(10);

        api.getConstraintCountForNodeShape.mockResolvedValue({ constraintCount: 20 });
        await store.loadConstraintCountForShape('http://example.org/Shape2');
        expect(store.currentConstraintCount).toBe(20);
        expect(store.currentNodeShape).toBe('http://example.org/Shape2');
      });
    });

    describe('clearCurrent', () => {
      it('should clear current constraint data', () => {
        store.currentConstraintCount = 25;
        store.currentNodeShape = 'http://example.org/PersonShape';

        store.clearCurrent();

        expect(store.currentConstraintCount).toBe(0);
        expect(store.currentNodeShape).toBeNull();
      });

      it('should not affect other state', () => {
        store.currentConstraintCount = 25;
        store.currentNodeShape = 'http://example.org/PersonShape';
        store.distinctConstraintComponents = 15;
        store.mostFrequentConstraint = { constraintComponent: 'sh:MinCount', occurrences: 50 };

        store.clearCurrent();

        expect(store.distinctConstraintComponents).toBe(15);
        expect(store.mostFrequentConstraint).toEqual({ constraintComponent: 'sh:MinCount', occurrences: 50 });
      });
    });

    describe('resetStore', () => {
      it('should reset entire store to initial state', () => {
        // Modify state
        store.mostFrequentConstraint = { constraintComponent: 'sh:MinCount', occurrences: 50 };
        store.distinctConstraintComponents = 15;
        store.distinctConstraintsInShapes = 100;
        store.violationsDistribution = { labels: ['A'], datasets: [] };
        store.currentConstraintCount = 25;
        store.currentNodeShape = 'http://example.org/PersonShape';
        store.loading = true;
        store.error = 'Some error';

        // Reset
        store.resetStore();

        expect(store.mostFrequentConstraint).toBeNull();
        expect(store.distinctConstraintComponents).toBe(0);
        expect(store.distinctConstraintsInShapes).toBe(0);
        expect(store.violationsDistribution).toBeNull();
        expect(store.currentConstraintCount).toBe(0);
        expect(store.currentNodeShape).toBeNull();
        expect(store.loading).toBe(false);
        expect(store.error).toBeNull();
      });
    });
  });

  describe('Error Handling', () => {
    it('should clear previous errors on new requests', async () => {
      store.error = 'Previous error';
      api.getMostFrequentConstraintComponent.mockResolvedValue({ constraintComponent: 'sh:MinCount', occurrences: 50 });
      api.getDistinctConstraintComponentsCount.mockResolvedValue({ distinctConstraintComponentCount: 15 });
      api.getDistinctConstraintsCountInShapes.mockResolvedValue({ distinctConstraintsCount: 100 });

      await store.loadOverview();

      expect(store.error).toBeNull();
    });

    it('should maintain loading state on error', async () => {
      api.getMostFrequentConstraintComponent.mockRejectedValue(new Error('Failed'));

      try {
        await store.loadOverview();
      } catch (e) {
        // Expected
      }

      expect(store.loading).toBe(false);
    });

    it('should recover from error on subsequent successful request', async () => {
      // First request fails
      api.getMostFrequentConstraintComponent.mockRejectedValueOnce(new Error('Network error'));

      try {
        await store.loadOverview();
      } catch (e) {
        // Expected
      }

      expect(store.error).toBeTruthy();

      // Second request succeeds
      api.getMostFrequentConstraintComponent.mockResolvedValue({ constraintComponent: 'sh:MinCount', occurrences: 50 });
      api.getDistinctConstraintComponentsCount.mockResolvedValue({ distinctConstraintComponentCount: 15 });
      api.getDistinctConstraintsCountInShapes.mockResolvedValue({ distinctConstraintsCount: 100 });

      await store.loadOverview(true);

      expect(store.error).toBeNull();
      expect(store.distinctConstraintComponents).toBe(15);
    });
  });

  describe('Cache Behavior', () => {
    beforeEach(() => {
      api.getMostFrequentConstraintComponent.mockResolvedValue({ constraintComponent: 'sh:MinCount', occurrences: 50 });
      api.getDistinctConstraintComponentsCount.mockResolvedValue({ distinctConstraintComponentCount: 15 });
      api.getDistinctConstraintsCountInShapes.mockResolvedValue({ distinctConstraintsCount: 100 });
    });

    it('should update lastFetchTime after successful load', async () => {
      const beforeTime = Date.now();
      await store.loadOverview();
      const afterTime = Date.now();

      expect(store.lastFetchTime).toBeGreaterThanOrEqual(beforeTime);
      expect(store.lastFetchTime).toBeLessThanOrEqual(afterTime);
    });

    it('should not update cache time on error', async () => {
      api.getMostFrequentConstraintComponent.mockRejectedValue(new Error('Failed'));

      const initialTime = store.lastFetchTime;

      try {
        await store.loadOverview();
      } catch (e) {
        // Expected
      }

      expect(store.lastFetchTime).toBe(initialTime);
    });

    it('should respect cache when data is not stale', async () => {
      // First load
      await store.loadOverview();
      const firstData = store.mostFrequentConstraint;
      vi.clearAllMocks();

      // Change mock data
      api.getMostFrequentConstraintComponent.mockResolvedValue({ constraintComponent: 'sh:MaxCount', occurrences: 100 });

      // Second load without force refresh
      await store.loadOverview(false);

      // Should still have first data (cached)
      expect(store.mostFrequentConstraint).toEqual(firstData);
      expect(api.getMostFrequentConstraintComponent).not.toHaveBeenCalled();
    });

    it('should bypass cache with force refresh', async () => {
      // First load
      await store.loadOverview();
      vi.clearAllMocks();

      // Change mock data
      api.getMostFrequentConstraintComponent.mockResolvedValue({ constraintComponent: 'sh:MaxCount', occurrences: 100 });
      api.getDistinctConstraintComponentsCount.mockResolvedValue({ distinctConstraintComponentCount: 20 });
      api.getDistinctConstraintsCountInShapes.mockResolvedValue({ distinctConstraintsCount: 150 });

      // Second load with force refresh
      await store.loadOverview(true);

      // Should have new data
      expect(store.mostFrequentConstraint.constraintComponent).toBe('sh:MaxCount');
      expect(store.distinctConstraintComponents).toBe(20);
      expect(api.getMostFrequentConstraintComponent).toHaveBeenCalled();
    });
  });

  describe('Integration Scenarios', () => {
    it('should handle complete workflow: load overview -> distribution -> specific shape', async () => {
      // Load overview
      api.getMostFrequentConstraintComponent.mockResolvedValue({ constraintComponent: 'sh:MinCount', occurrences: 50 });
      api.getDistinctConstraintComponentsCount.mockResolvedValue({ distinctConstraintComponentCount: 15 });
      api.getDistinctConstraintsCountInShapes.mockResolvedValue({ distinctConstraintsCount: 100 });
      await store.loadOverview();

      expect(store.distinctConstraintComponents).toBe(15);

      // Load distribution
      api.getViolationsDistributionPerConstraintComponent.mockResolvedValue({ labels: ['A'], datasets: [] });
      await store.loadDistribution();

      expect(store.violationsDistribution).toBeDefined();

      // Load specific shape
      api.getConstraintCountForNodeShape.mockResolvedValue({ constraintCount: 25 });
      await store.loadConstraintCountForShape('http://example.org/PersonShape');

      expect(store.currentConstraintCount).toBe(25);

      // All data should be present
      expect(store.distinctConstraintComponents).toBe(15);
      expect(store.violationsDistribution).toBeDefined();
      expect(store.currentConstraintCount).toBe(25);
    });

    it('should handle clearing and reloading', async () => {
      // Load data
      api.getConstraintCountForNodeShape.mockResolvedValue({ constraintCount: 25 });
      await store.loadConstraintCountForShape('http://example.org/PersonShape');

      expect(store.currentConstraintCount).toBe(25);

      // Clear
      store.clearCurrent();
      expect(store.currentConstraintCount).toBe(0);

      // Reload
      api.getConstraintCountForNodeShape.mockResolvedValue({ constraintCount: 30 });
      await store.loadConstraintCountForShape('http://example.org/AddressShape');

      expect(store.currentConstraintCount).toBe(30);
      expect(store.currentNodeShape).toBe('http://example.org/AddressShape');
    });
  });
});
