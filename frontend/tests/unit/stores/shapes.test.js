/**
 * Shapes Store Tests
 * 
 * Comprehensive tests for the shapes Pinia store
 */

import { describe, it, expect, beforeEach, vi } from 'vitest';
import { setActivePinia, createPinia } from 'pinia';
import { useShapesStore } from '@/stores/shapes';
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

describe('useShapesStore', () => {
  let store;

  beforeEach(() => {
    // Create a fresh pinia instance for each test
    setActivePinia(createPinia());
    store = useShapesStore();
    
    // Reset all mocks
    vi.clearAllMocks();
  });

  describe('Initial State', () => {
    it('should initialize with empty/default values', () => {
      expect(store.nodeShapes).toEqual([]);
      expect(store.totalNodeShapes).toBe(0);
      expect(store.nodeShapesWithViolations).toBe(0);
      expect(store.maxViolationsPerShape).toBe(0);
      expect(store.avgViolationsPerShape).toBe(0);
      expect(store.mostViolatedShape).toBeNull();
      expect(store.currentShape).toBeNull();
      expect(store.loading).toBe(false);
      expect(store.error).toBeNull();
    });

    it('should have correct cache timeout', () => {
      expect(store.cacheTimeout).toBe(5 * 60 * 1000); // 5 minutes
    });
  });

  describe('Getters', () => {
    describe('violationPercentage', () => {
      it('should return 0 when no shapes exist', () => {
        store.totalNodeShapes = 0;
        store.nodeShapesWithViolations = 0;
        expect(Number(store.violationPercentage)).toBe(0);
      });

      it('should calculate percentage correctly', () => {
        store.totalNodeShapes = 100;
        store.nodeShapesWithViolations = 25;
        expect(store.violationPercentage).toBe('25.0');
      });

      it('should handle decimal percentages', () => {
        store.totalNodeShapes = 100;
        store.nodeShapesWithViolations = 33;
        expect(store.violationPercentage).toBe('33.0');
      });
    });

    describe('isDataStale', () => {
      it('should return true when no data has been fetched', () => {
        expect(store.isDataStale).toBe(true);
      });

      it('should return false for fresh data', () => {
        store.lastFetchTime = Date.now();
        expect(store.isDataStale).toBe(false);
      });

      it('should return true for stale data', () => {
        store.lastFetchTime = Date.now() - (6 * 60 * 1000); // 6 minutes ago
        expect(store.isDataStale).toBe(true);
      });
    });

    describe('shapesSortedByViolations', () => {
      it('should sort shapes by violation count descending', () => {
        store.nodeShapes = [
          { name: 'Shape1', violations: 10 },
          { name: 'Shape2', violations: 50 },
          { name: 'Shape3', violations: 25 }
        ];

        const sorted = store.shapesSortedByViolations;
        expect(sorted[0].violations).toBe(50);
        expect(sorted[1].violations).toBe(25);
        expect(sorted[2].violations).toBe(10);
      });

      it('should handle shapes without violations', () => {
        store.nodeShapes = [
          { name: 'Shape1', violations: 10 },
          { name: 'Shape2' },
          { name: 'Shape3', violations: 0 }
        ];

        const sorted = store.shapesSortedByViolations;
        expect(sorted[0].violations).toBe(10);
      });
    });

    describe('shapesWithoutViolations', () => {
      it('should filter shapes with zero violations', () => {
        store.nodeShapes = [
          { name: 'Shape1', violations: 10 },
          { name: 'Shape2', violations: 0 },
          { name: 'Shape3' }
        ];

        const filtered = store.shapesWithoutViolations;
        expect(filtered.length).toBe(2);
        expect(filtered.map(s => s.name)).toEqual(['Shape2', 'Shape3']);
      });
    });

    describe('topViolatedShapes', () => {
      it('should return top N shapes', () => {
        store.nodeShapes = [
          { name: 'Shape1', violations: 100 },
          { name: 'Shape2', violations: 50 },
          { name: 'Shape3', violations: 75 },
          { name: 'Shape4', violations: 25 }
        ];

        const top2 = store.topViolatedShapes(2);
        expect(top2.length).toBe(2);
        expect(top2[0].violations).toBe(100);
        expect(top2[1].violations).toBe(75);
      });

      it('should default to 10 shapes', () => {
        store.nodeShapes = Array.from({ length: 15 }, (_, i) => ({
          name: `Shape${i}`,
          violations: i
        }));

        const top = store.topViolatedShapes();
        expect(top.length).toBe(10);
      });
    });
  });

  describe('Actions', () => {
    describe('loadOverview', () => {
      const mockOverviewData = {
        nodeShapeCount: 100,
        nodeShapesWithViolationsCount: 25,
        violationCount: 50,
        averageViolations: 2.5,
        nodeShape: 'MostViolatedShape',
        violations: 50
      };

      beforeEach(() => {
        api.getNodeShapesCountInGraph.mockResolvedValue({ nodeShapeCount: 100 });
        api.getNodeShapesWithViolationsCountOverview.mockResolvedValue({ nodeShapesWithViolationsCount: 25 });
        api.getMaxViolationsForNodeShape.mockResolvedValue({ violationCount: 50 });
        api.getAverageViolationsForNodeShapes.mockResolvedValue({ averageViolations: 2.5 });
        api.getMostViolatedNodeShape.mockResolvedValue({ nodeShape: 'MostViolatedShape', violations: 50 });
      });

      it('should load overview data successfully', async () => {
        await store.loadOverview();

        expect(store.totalNodeShapes).toBe(100);
        expect(store.nodeShapesWithViolations).toBe(25);
        expect(store.maxViolationsPerShape).toBe(50);
        expect(store.avgViolationsPerShape).toBe(2.5);
        expect(store.mostViolatedShape).toEqual({ nodeShape: 'MostViolatedShape', violations: 50 });
        expect(store.error).toBeNull();
        expect(store.lastFetchTime).toBeTruthy();
      });

      it('should set loading states correctly', async () => {
        const loadPromise = store.loadOverview();
        expect(store.overviewLoading).toBe(true);
        
        await loadPromise;
        expect(store.overviewLoading).toBe(false);
      });

      it('should use cache when data is fresh', async () => {
        // Load data first time
        await store.loadOverview();
        const firstFetchTime = store.lastFetchTime;
        
        // Set nodeShapes so cache check passes
        store.nodeShapes = [{ name: 'Shape1' }];
        vi.clearAllMocks();

        // Try to load again without force refresh
        await store.loadOverview(false);
        
        // API should not be called again
        expect(api.getNodeShapesCountInGraph).not.toHaveBeenCalled();
        expect(store.lastFetchTime).toBe(firstFetchTime);
      });

      it('should force refresh when requested', async () => {
        // Load data first time
        await store.loadOverview();
        vi.clearAllMocks();

        // Force refresh
        await store.loadOverview(true);
        
        // API should be called again
        expect(api.getNodeShapesCountInGraph).toHaveBeenCalled();
      });

      it('should handle API errors', async () => {
        const error = new Error('API Error');
        api.getNodeShapesCountInGraph.mockRejectedValue(error);

        await expect(store.loadOverview()).rejects.toThrow('API Error');
        expect(store.error).toBeTruthy();
        expect(store.overviewLoading).toBe(false);
      });

      it('should handle missing data gracefully', async () => {
        api.getNodeShapesCountInGraph.mockResolvedValue({});
        api.getNodeShapesWithViolationsCountOverview.mockResolvedValue({});
        api.getMaxViolationsForNodeShape.mockResolvedValue({});
        api.getAverageViolationsForNodeShapes.mockResolvedValue({});
        api.getMostViolatedNodeShape.mockResolvedValue({});

        await store.loadOverview();

        expect(store.totalNodeShapes).toBe(0);
        expect(store.nodeShapesWithViolations).toBe(0);
        expect(store.maxViolationsPerShape).toBe(0);
        expect(store.avgViolationsPerShape).toBe(0);
      });
    });

    describe('loadShapesTable', () => {
      it('should load shapes table data', async () => {
        const mockShapes = [
          { name: 'Shape1', violations: 10 },
          { name: 'Shape2', violations: 20 }
        ];
        api.getNodeShapeDetailsTable.mockResolvedValue({ nodeShapes: mockShapes });

        await store.loadShapesTable();

        expect(store.nodeShapes).toEqual(mockShapes);
        expect(store.loading).toBe(false);
        expect(store.error).toBeNull();
      });

      it('should handle empty table data', async () => {
        api.getNodeShapeDetailsTable.mockResolvedValue({ nodeShapes: [] });

        await store.loadShapesTable();

        expect(store.nodeShapes).toEqual([]);
      });

      it('should handle API errors', async () => {
        api.getNodeShapeDetailsTable.mockRejectedValue(new Error('Table load failed'));

        await expect(store.loadShapesTable()).rejects.toThrow();
        expect(store.error).toBeTruthy();
        expect(store.loading).toBe(false);
      });
    });

    describe('loadChartData', () => {
      beforeEach(() => {
        api.getViolationsDistribution.mockResolvedValue({ labels: [], datasets: [] });
        api.getCorrelationData.mockResolvedValue([]);
        api.getViolationsPerNodeShape.mockResolvedValue({ violationsPerNodeShape: [] });
      });

      it('should load chart data successfully', async () => {
        const mockHistogram = { labels: ['0-10', '10-20'], datasets: [{ data: [5, 3] }] };
        const mockCorrelation = [{ x: 1, y: 2 }];
        const mockViolations = { violationsPerNodeShape: [{ shape: 'A', count: 5 }] };

        api.getViolationsDistribution.mockResolvedValue(mockHistogram);
        api.getCorrelationData.mockResolvedValue(mockCorrelation);
        api.getViolationsPerNodeShape.mockResolvedValue(mockViolations);

        await store.loadChartData(10);

        expect(store.violationsDistribution).toEqual(mockHistogram);
        expect(store.correlationData).toEqual(mockCorrelation);
        expect(store.violationsPerShape).toEqual(mockViolations);
      });

      it('should pass bins parameter correctly', async () => {
        await store.loadChartData(20);
        expect(api.getViolationsDistribution).toHaveBeenCalledWith(20);
      });

      it('should handle errors', async () => {
        api.getViolationsDistribution.mockRejectedValue(new Error('Chart data error'));

        await expect(store.loadChartData()).rejects.toThrow();
        expect(store.error).toBeTruthy();
      });
    });

    describe('loadCompleteOverview', () => {
      beforeEach(() => {
        // Mock all required APIs
        api.getNodeShapesCountInGraph.mockResolvedValue({ nodeShapeCount: 100 });
        api.getNodeShapesWithViolationsCountOverview.mockResolvedValue({ nodeShapesWithViolationsCount: 25 });
        api.getMaxViolationsForNodeShape.mockResolvedValue({ violationCount: 50 });
        api.getAverageViolationsForNodeShapes.mockResolvedValue({ averageViolations: 2.5 });
        api.getMostViolatedNodeShape.mockResolvedValue({ nodeShape: 'Shape', violations: 50 });
        api.getNodeShapeDetailsTable.mockResolvedValue({ nodeShapes: [] });
        api.getViolationsDistribution.mockResolvedValue({ labels: [], datasets: [] });
        api.getCorrelationData.mockResolvedValue([]);
        api.getViolationsPerNodeShape.mockResolvedValue({ violationsPerNodeShape: [] });
      });

      it('should load all data in parallel', async () => {
        await store.loadCompleteOverview();

        expect(store.totalNodeShapes).toBe(100);
        expect(store.nodeShapes).toBeDefined();
        expect(store.violationsDistribution).toBeDefined();
      });

      it('should propagate errors', async () => {
        api.getNodeShapesCountInGraph.mockRejectedValue(new Error('Failed'));

        await expect(store.loadCompleteOverview()).rejects.toThrow();
      });
    });

    describe('loadShapeDetails', () => {
      const mockShapeUri = 'http://example.org/Shape1';

      beforeEach(() => {
        api.getViolationCountForNodeShape.mockResolvedValue({ violationCount: 10 });
        api.getViolatedFocusNodesCountForNodeShape.mockResolvedValue({ focusNodeCount: 5 });
        api.getPropertyPathsCountForNodeShape.mockResolvedValue({ pathCount: 3 });
        api.getConstraintCountForNodeShape.mockResolvedValue({ constraintCount: 7 });
        api.getShapeDefinition.mockResolvedValue({ definition: 'sh:NodeShape ...' });
      });

      it('should load shape details successfully', async () => {
        await store.loadShapeDetails(mockShapeUri);

        expect(store.currentShape).toBe(mockShapeUri);
        expect(store.currentShapeViolationCount).toBe(10);
        expect(store.currentShapeAffectedFocusNodes).toBe(5);
        expect(store.currentShapePropertyPathsCount).toBe(3);
        expect(store.currentShapeConstraintCount).toBe(7);
        expect(store.currentShapeDefinition).toBe('sh:NodeShape ...');
        expect(store.detailsLoading).toBe(false);
      });

      it('should handle API errors', async () => {
        api.getViolationCountForNodeShape.mockRejectedValue(new Error('Details failed'));

        await expect(store.loadShapeDetails(mockShapeUri)).rejects.toThrow();
        expect(store.error).toBeTruthy();
        expect(store.detailsLoading).toBe(false);
      });

      it('should handle missing data', async () => {
        api.getViolationCountForNodeShape.mockResolvedValue({});
        api.getViolatedFocusNodesCountForNodeShape.mockResolvedValue({});
        api.getPropertyPathsCountForNodeShape.mockResolvedValue({});
        api.getConstraintCountForNodeShape.mockResolvedValue({});
        api.getShapeDefinition.mockResolvedValue({});

        await store.loadShapeDetails(mockShapeUri);

        expect(store.currentShapeViolationCount).toBe(0);
        expect(store.currentShapeAffectedFocusNodes).toBe(0);
        expect(store.currentShapePropertyPathsCount).toBe(0);
        expect(store.currentShapeConstraintCount).toBe(0);
        expect(store.currentShapeDefinition).toBe('');
      });
    });

    describe('loadPropertyShapes', () => {
      const mockNodeShape = 'http://example.org/Shape1';

      it('should load property shapes with default pagination', async () => {
        const mockPropertyShapes = [
          { name: 'prop1', violations: 5 },
          { name: 'prop2', violations: 3 }
        ];
        api.getPropertyShapesForNodeShape.mockResolvedValue({ propertyShapes: mockPropertyShapes });

        const result = await store.loadPropertyShapes(mockNodeShape);

        expect(store.propertyShapes).toEqual(mockPropertyShapes);
        expect(store.propertyShapesLoading).toBe(false);
        expect(result.propertyShapes).toEqual(mockPropertyShapes);
        expect(api.getPropertyShapesForNodeShape).toHaveBeenCalledWith(mockNodeShape, 100, 0);
      });

      it('should support custom pagination', async () => {
        api.getPropertyShapesForNodeShape.mockResolvedValue({ propertyShapes: [] });

        await store.loadPropertyShapes(mockNodeShape, 50, 10);

        expect(api.getPropertyShapesForNodeShape).toHaveBeenCalledWith(mockNodeShape, 50, 10);
      });

      it('should handle errors', async () => {
        api.getPropertyShapesForNodeShape.mockRejectedValue(new Error('Load failed'));

        await expect(store.loadPropertyShapes(mockNodeShape)).rejects.toThrow();
        expect(store.error).toBeTruthy();
        expect(store.propertyShapesLoading).toBe(false);
      });
    });

    describe('clearShapeDetails', () => {
      it('should reset shape details to defaults', () => {
        // Set some data
        store.currentShape = 'http://example.org/Shape1';
        store.currentShapeDefinition = 'definition';
        store.currentShapeViolationCount = 10;
        store.currentShapeAffectedFocusNodes = 5;
        store.currentShapePropertyPathsCount = 3;
        store.currentShapeConstraintCount = 7;
        store.propertyShapes = [{ name: 'prop1' }];

        // Clear
        store.clearShapeDetails();

        expect(store.currentShape).toBeNull();
        expect(store.currentShapeDefinition).toBeNull();
        expect(store.currentShapeViolationCount).toBe(0);
        expect(store.currentShapeAffectedFocusNodes).toBe(0);
        expect(store.currentShapePropertyPathsCount).toBe(0);
        expect(store.currentShapeConstraintCount).toBe(0);
        expect(store.propertyShapes).toEqual([]);
      });
    });

    describe('resetStore', () => {
      it('should reset entire store to initial state', () => {
        // Modify state
        store.totalNodeShapes = 100;
        store.nodeShapes = [{ name: 'Shape1' }];
        store.loading = true;
        store.error = 'Some error';

        // Reset
        store.resetStore();

        expect(store.totalNodeShapes).toBe(0);
        expect(store.nodeShapes).toEqual([]);
        expect(store.loading).toBe(false);
        expect(store.error).toBeNull();
      });
    });
  });

  describe('Error Handling', () => {
    it('should clear previous errors on new requests', async () => {
      // Set an error
      store.error = 'Previous error';

      // Mock successful request
      api.getNodeShapeDetailsTable.mockResolvedValue({ nodeShapes: [] });

      await store.loadShapesTable();

      // During loading, error should be cleared
      expect(store.error).toBeNull();
    });

    it('should maintain loading state on error', async () => {
      api.getNodeShapeDetailsTable.mockRejectedValue(new Error('Failed'));

      try {
        await store.loadShapesTable();
      } catch (e) {
        // Error expected
      }

      expect(store.loading).toBe(false);
    });
  });

  describe('Cache Behavior', () => {
    it('should update lastFetchTime after successful load', async () => {
      api.getNodeShapesCountInGraph.mockResolvedValue({ nodeShapeCount: 100 });
      api.getNodeShapesWithViolationsCountOverview.mockResolvedValue({ nodeShapesWithViolationsCount: 25 });
      api.getMaxViolationsForNodeShape.mockResolvedValue({ violationCount: 50 });
      api.getAverageViolationsForNodeShapes.mockResolvedValue({ averageViolations: 2.5 });
      api.getMostViolatedNodeShape.mockResolvedValue({ nodeShape: 'Shape', violations: 50 });

      const beforeTime = Date.now();
      await store.loadOverview();
      const afterTime = Date.now();

      expect(store.lastFetchTime).toBeGreaterThanOrEqual(beforeTime);
      expect(store.lastFetchTime).toBeLessThanOrEqual(afterTime);
    });

    it('should not update cache time on error', async () => {
      api.getNodeShapesCountInGraph.mockRejectedValue(new Error('Failed'));

      const initialTime = store.lastFetchTime;

      try {
        await store.loadOverview();
      } catch (e) {
        // Expected error
      }

      expect(store.lastFetchTime).toBe(initialTime);
    });
  });
});
