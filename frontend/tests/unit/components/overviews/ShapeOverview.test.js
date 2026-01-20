/**
 * ShapeOverview Component Tests
 * 
 * Tests for the ShapeOverview component
 */

import { describe, it, expect, beforeEach, vi } from 'vitest';
import { mount } from '@vue/test-utils';
import { createPinia, setActivePinia } from 'pinia';
import ShapeOverview from '@/components/Overviews/ShapeOverview.vue';
import { useShapesStore } from '@/stores/shapes';

// Mock child components
vi.mock('@/components/Charts/HistogramChart.vue', () => ({
  default: {
    name: 'HistogramChart',
    template: '<div class="histogram-chart-mock"></div>',
    props: ['title', 'xAxisLabel', 'yAxisLabel', 'data', 'explanationText']
  }
}));

vi.mock('@/components/Charts/ScatterPlotChart.vue', () => ({
  default: {
    name: 'ScatterPlotChart',
    template: '<div class="scatter-plot-mock"></div>',
    props: ['title', 'xAxisLabel', 'yAxisLabel', 'data', 'showQuadrants', 'explanationText']
  }
}));

// Mock FontAwesome
vi.mock('@fortawesome/vue-fontawesome', () => ({
  FontAwesomeIcon: {
    name: 'FontAwesomeIcon',
    template: '<i class="fa-icon-mock"></i>',
    props: ['icon']
  }
}));

// Mock router
const mockRouter = {
  push: vi.fn()
};

vi.mock('vue-router', () => ({
  useRouter: () => mockRouter
}));

// Mock logger
vi.mock('@/services/logger', () => ({
  logger: {
    info: vi.fn(),
    error: vi.fn(),
    debug: vi.fn()
  }
}));

describe('ShapeOverview', () => {
  let wrapper;
  let store;
  let pinia;

  beforeEach(() => {
    pinia = createPinia();
    setActivePinia(pinia);
    store = useShapesStore();
    
    // Reset mocks
    vi.clearAllMocks();
    mockRouter.push.mockClear();
  });

  const createWrapper = (options = {}) => {
    return mount(ShapeOverview, {
      global: {
        plugins: [pinia],
        stubs: {
          FontAwesomeIcon: true,
          HistogramChart: true,
          ScatterPlotChart: true
        }
      },
      ...options
    });
  };

  describe('Loading State', () => {
    it('should display loading message when loading', () => {
      store.overviewLoading = true;
      store.loading = false;
      
      wrapper = createWrapper();
      
      expect(wrapper.text()).toContain('Loading shapes overview...');
      expect(wrapper.find('.text-gray-600').exists()).toBe(true);
    });

    it('should not display content when loading', () => {
      store.overviewLoading = true;
      
      wrapper = createWrapper();
      
      expect(wrapper.find('.grid').exists()).toBe(false);
      expect(wrapper.find('table').exists()).toBe(false);
    });
  });

  describe('Error State', () => {
    it('should display error message when there is an error', () => {
      store.loading = false;
      store.overviewLoading = false;
      store.error = 'Failed to load data';
      
      wrapper = createWrapper();
      
      expect(wrapper.text()).toContain('Failed to load data');
      expect(wrapper.find('.text-red-600').exists()).toBe(true);
    });

    it('should show retry button on error', () => {
      store.error = 'Network error';
      store.loading = false;
      store.overviewLoading = false;
      
      wrapper = createWrapper();
      
      const retryButton = wrapper.find('button');
      expect(retryButton.exists()).toBe(true);
      expect(retryButton.text()).toContain('Retry');
    });

    it('should call loadOverviewData when retry button is clicked', async () => {
      store.error = 'Network error';
      store.loading = false;
      store.overviewLoading = false;
      
      wrapper = createWrapper();
      
      const loadSpy = vi.spyOn(store, 'loadCompleteOverview').mockResolvedValue();
      
      await wrapper.find('button').trigger('click');
      
      expect(loadSpy).toHaveBeenCalled();
    });
  });

  describe('Tags/Statistics Display', () => {
    beforeEach(() => {
      store.totalNodeShapes = 100;
      store.nodeShapesWithViolations = 25;
      store.maxViolationsPerShape = 50;
      store.avgViolationsPerShape = 2.5;
      store.loading = false;
      store.overviewLoading = false;
      store.error = null;
      store.nodeShapes = [];
    });

    it('should display statistics cards', () => {
      wrapper = createWrapper();
      
      const cards = wrapper.findAll('.bg-white.rounded-lg.shadow');
      expect(cards.length).toBeGreaterThan(0);
    });

    it('should display correct statistics values', () => {
      wrapper = createWrapper();
      
      const text = wrapper.text();
      expect(text).toContain('100'); // Total shapes
      expect(text).toContain('25'); // Shapes with violations
    });
  });

  describe('Charts Display', () => {
    beforeEach(() => {
      store.loading = false;
      store.overviewLoading = false;
      store.error = null;
      store.nodeShapes = [];
      store.violationsDistribution = {
        labels: ['0-10', '10-20'],
        datasets: [{ data: [5, 3] }]
      };
      store.correlationData = [{ x: 1, y: 2 }];
    });

    it('should render histogram chart', () => {
      wrapper = createWrapper();
      
      const charts = wrapper.findAll('[class*="grid-cols-3"]');
      expect(charts.length).toBeGreaterThan(0);
    });

    it('should render multiple scatter plots', () => {
      wrapper = createWrapper();
      
      // Should have 2 scatter plots
      const text = wrapper.html();
      expect(text).toContain('Correlation Between Constraints and Violations');
      expect(text).toContain('Violation Diversity and Intensity');
    });
  });

  describe('Table Display', () => {
    beforeEach(() => {
      store.loading = false;
      store.overviewLoading = false;
      store.error = null;
      store.nodeShapes = [
        {
          id: 1,
          name: 'PersonShape',
          violations: 10,
          propertyShapes: 5,
          focusNodes: 20,
          propertyPaths: 3,
          mostViolatedConstraint: 'sh:minCount',
          violationToConstraintRatio: 2.0
        },
        {
          id: 2,
          name: 'AddressShape',
          violations: 5,
          propertyShapes: 3,
          focusNodes: 10,
          propertyPaths: 2,
          mostViolatedConstraint: 'sh:maxCount',
          violationToConstraintRatio: 1.7
        }
      ];
    });

    it('should render table with shape data', () => {
      wrapper = createWrapper();
      
      const table = wrapper.find('table');
      expect(table.exists()).toBe(true);
    });

    it('should display table headers', () => {
      wrapper = createWrapper();
      
      const headers = wrapper.findAll('th');
      expect(headers.length).toBeGreaterThan(0);
    });

    it('should display shape rows', () => {
      wrapper = createWrapper();
      
      const rows = wrapper.findAll('tbody tr');
      expect(rows.length).toBeGreaterThanOrEqual(1);
    });

    it('should display shape names', () => {
      wrapper = createWrapper();
      
      const text = wrapper.text();
      expect(text).toContain('PersonShape');
      expect(text).toContain('AddressShape');
    });

    it('should handle row click', async () => {
      wrapper = createWrapper();
      
      const firstRow = wrapper.find('tbody tr');
      await firstRow.trigger('click');
      
      expect(mockRouter.push).toHaveBeenCalled();
    });
  });

  describe('Pagination', () => {
    beforeEach(() => {
      store.loading = false;
      store.overviewLoading = false;
      store.error = null;
      
      // Create 25 shapes to test pagination (10 per page)
      store.nodeShapes = Array.from({ length: 25 }, (_, i) => ({
        id: i + 1,
        name: `Shape${i + 1}`,
        violations: i,
        propertyShapes: 2,
        focusNodes: 5,
        propertyPaths: 1,
        mostViolatedConstraint: 'sh:pattern',
        violationToConstraintRatio: 1.5
      }));
    });

    it('should show pagination controls', () => {
      wrapper = createWrapper();
      
      const buttons = wrapper.findAll('button');
      const prevButton = buttons.find(b => b.text().includes('Previous'));
      const nextButton = buttons.find(b => b.text().includes('Next'));
      
      expect(prevButton).toBeTruthy();
      expect(nextButton).toBeTruthy();
    });

    it('should display current page information', () => {
      wrapper = createWrapper();
      
      expect(wrapper.text()).toMatch(/Page \d+ of \d+/);
    });

    it('should disable previous button on first page', () => {
      wrapper = createWrapper();
      
      const buttons = wrapper.findAll('button');
      const prevButton = buttons.find(b => b.text().includes('Previous'));
      
      expect(prevButton.attributes('disabled')).toBeDefined();
    });

    it('should navigate to next page', async () => {
      wrapper = createWrapper();
      
      const buttons = wrapper.findAll('button');
      const nextButton = buttons.find(b => b.text().includes('Next'));
      
      await nextButton.trigger('click');
      
      expect(wrapper.text()).toContain('Page 2');
    });

    it('should navigate to previous page', async () => {
      wrapper = createWrapper();
      
      // Go to page 2 first
      const buttons = wrapper.findAll('button');
      const nextButton = buttons.find(b => b.text().includes('Next'));
      await nextButton.trigger('click');
      
      // Then go back to page 1
      const prevButton = buttons.find(b => b.text().includes('Previous'));
      await prevButton.trigger('click');
      
      expect(wrapper.text()).toContain('Page 1');
    });
  });

  describe('Sorting', () => {
    beforeEach(() => {
      store.loading = false;
      store.overviewLoading = false;
      store.error = null;
      store.nodeShapes = [
        {
          id: 1,
          name: 'ZShape',
          violations: 10,
          propertyShapes: 5,
          focusNodes: 20,
          propertyPaths: 3,
          mostViolatedConstraint: 'sh:minCount',
          violationToConstraintRatio: 2.0
        },
        {
          id: 2,
          name: 'AShape',
          violations: 5,
          propertyShapes: 3,
          focusNodes: 10,
          propertyPaths: 2,
          mostViolatedConstraint: 'sh:maxCount',
          violationToConstraintRatio: 1.7
        }
      ];
    });

    it('should have clickable column headers', () => {
      wrapper = createWrapper();
      
      const headers = wrapper.findAll('th');
      const clickableHeaders = headers.filter(h => h.classes().includes('cursor-pointer'));
      
      expect(clickableHeaders.length).toBeGreaterThan(0);
    });

    it('should sort column when header is clicked', async () => {
      wrapper = createWrapper();
      
      const headers = wrapper.findAll('th');
      const nameHeader = headers[0]; // First column is name
      
      await nameHeader.trigger('click');
      
      // Check that sort indicator appears
      expect(wrapper.html()).toMatch(/▲|▼/);
    });

    it('should toggle sort order on repeated clicks', async () => {
      wrapper = createWrapper();
      
      const headers = wrapper.findAll('th');
      const violationsHeader = headers[1]; // Violations column
      
      // First click - ascending
      await violationsHeader.trigger('click');
      expect(wrapper.html()).toContain('▲');
      
      // Second click - descending
      await violationsHeader.trigger('click');
      expect(wrapper.html()).toContain('▼');
    });
  });

  describe('Component Lifecycle', () => {
    it('should load data on mount', () => {
      const loadSpy = vi.spyOn(store, 'loadCompleteOverview').mockResolvedValue();
      
      wrapper = createWrapper();
      
      expect(loadSpy).toHaveBeenCalled();
    });

    it('should handle empty shapes array', () => {
      store.loading = false;
      store.overviewLoading = false;
      store.error = null;
      store.nodeShapes = [];
      
      wrapper = createWrapper();
      
      const rows = wrapper.findAll('tbody tr');
      expect(rows.length).toBe(0);
    });
  });

  describe('Responsive Behavior', () => {
    it('should render grid layouts', () => {
      store.loading = false;
      store.overviewLoading = false;
      store.error = null;
      store.nodeShapes = [];
      
      wrapper = createWrapper();
      
      const grids = wrapper.findAll('[class*="grid"]');
      expect(grids.length).toBeGreaterThan(0);
    });

    it('should apply proper CSS classes', () => {
      store.loading = false;
      store.overviewLoading = false;
      store.error = null;
      store.nodeShapes = [];
      
      wrapper = createWrapper();
      
      expect(wrapper.find('.shape-overview').exists()).toBe(true);
      expect(wrapper.find('.p-4').exists()).toBe(true);
    });
  });
});
