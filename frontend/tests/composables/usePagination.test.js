import { describe, it, expect, beforeEach } from 'vitest';
import { ref } from 'vue';
import { usePagination } from '@/composables/usePagination';

describe('usePagination', () => {
  let testData;

  beforeEach(() => {
    // Create test data with 25 items
    testData = ref(
      Array.from({ length: 25 }, (_, i) => ({
        id: i + 1,
        name: `Item ${i + 1}`
      }))
    );
  });

  describe('initialization', () => {
    it('should initialize with default page size', () => {
      const { currentPage, itemsPerPage, totalPages } = usePagination(testData);
      
      expect(currentPage.value).toBe(1);
      expect(itemsPerPage.value).toBe(10); // Default from constants
      expect(totalPages.value).toBe(3); // 25 items / 10 per page
    });

    it('should initialize with custom page size', () => {
      const { itemsPerPage, totalPages } = usePagination(testData, 5);
      
      expect(itemsPerPage.value).toBe(5);
      expect(totalPages.value).toBe(5); // 25 items / 5 per page
    });

    it('should handle empty data', () => {
      const emptyData = ref([]);
      const { totalPages, paginatedData } = usePagination(emptyData);
      
      expect(totalPages.value).toBe(0);
      expect(paginatedData.value).toEqual([]);
    });

    it('should handle null data', () => {
      const nullData = ref(null);
      const { totalPages, paginatedData } = usePagination(nullData);
      
      expect(totalPages.value).toBe(0);
      expect(paginatedData.value).toEqual([]);
    });
  });

  describe('paginatedData', () => {
    it('should return correct data for first page', () => {
      const { paginatedData } = usePagination(testData, 10);
      
      expect(paginatedData.value).toHaveLength(10);
      expect(paginatedData.value[0].id).toBe(1);
      expect(paginatedData.value[9].id).toBe(10);
    });

    it('should return correct data for middle page', () => {
      const { paginatedData, goToPage } = usePagination(testData, 10);
      
      goToPage(2);
      
      expect(paginatedData.value).toHaveLength(10);
      expect(paginatedData.value[0].id).toBe(11);
      expect(paginatedData.value[9].id).toBe(20);
    });

    it('should return correct data for last page with partial items', () => {
      const { paginatedData, goToPage } = usePagination(testData, 10);
      
      goToPage(3);
      
      expect(paginatedData.value).toHaveLength(5); // Only 5 items on last page
      expect(paginatedData.value[0].id).toBe(21);
      expect(paginatedData.value[4].id).toBe(25);
    });
  });

  describe('navigation', () => {
    it('should navigate to next page', () => {
      const { currentPage, nextPage } = usePagination(testData);
      
      expect(currentPage.value).toBe(1);
      nextPage();
      expect(currentPage.value).toBe(2);
    });

    it('should navigate to previous page', () => {
      const { currentPage, goToPage, prevPage } = usePagination(testData);
      
      goToPage(2);
      expect(currentPage.value).toBe(2);
      prevPage();
      expect(currentPage.value).toBe(1);
    });

    it('should not go before first page', () => {
      const { currentPage, prevPage } = usePagination(testData);
      
      expect(currentPage.value).toBe(1);
      prevPage();
      expect(currentPage.value).toBe(1); // Should stay at 1
    });

    it('should not go beyond last page', () => {
      const { currentPage, totalPages, nextPage } = usePagination(testData, 10);
      
      // Go to last page
      while (currentPage.value < totalPages.value) {
        nextPage();
      }
      
      expect(currentPage.value).toBe(3);
      nextPage();
      expect(currentPage.value).toBe(3); // Should stay at last page
    });

    it('should go to specific page', () => {
      const { currentPage, goToPage } = usePagination(testData);
      
      goToPage(2);
      expect(currentPage.value).toBe(2);
    });

    it('should not go to invalid page number', () => {
      const { currentPage, goToPage } = usePagination(testData);
      
      goToPage(0); // Invalid
      expect(currentPage.value).toBe(1);
      
      goToPage(10); // Beyond total pages
      expect(currentPage.value).toBe(1);
    });
  });

  describe('page state checks', () => {
    it('should correctly indicate previous page availability', () => {
      const { hasPrevPage, nextPage } = usePagination(testData);
      
      expect(hasPrevPage.value).toBe(false); // First page
      nextPage();
      expect(hasPrevPage.value).toBe(true); // Second page
    });

    it('should correctly indicate next page availability', () => {
      const { hasNextPage, goToPage } = usePagination(testData, 10);
      
      expect(hasNextPage.value).toBe(true); // First page, more pages exist
      goToPage(3); // Last page
      expect(hasNextPage.value).toBe(false);
    });
  });

  describe('page size changes', () => {
    it('should update page size', () => {
      const { itemsPerPage, setPageSize } = usePagination(testData, 10);
      
      expect(itemsPerPage.value).toBe(10);
      setPageSize(20);
      expect(itemsPerPage.value).toBe(20);
    });

    it('should reset to first page when page size changes', () => {
      const { currentPage, goToPage, setPageSize } = usePagination(testData, 10);
      
      goToPage(2);
      expect(currentPage.value).toBe(2);
      
      setPageSize(5);
      expect(currentPage.value).toBe(1);
    });

    it('should recalculate total pages when page size changes', () => {
      const { totalPages, setPageSize } = usePagination(testData, 10);
      
      expect(totalPages.value).toBe(3);
      setPageSize(5);
      expect(totalPages.value).toBe(5);
    });
  });

  describe('reset functionality', () => {
    it('should reset to first page', () => {
      const { currentPage, goToPage, resetPage } = usePagination(testData);
      
      goToPage(3);
      expect(currentPage.value).toBe(3);
      
      resetPage();
      expect(currentPage.value).toBe(1);
    });
  });

  describe('row number utilities', () => {
    it('should calculate correct start row number', () => {
      const { getStartRowNumber, goToPage } = usePagination(testData, 10);
      
      expect(getStartRowNumber()).toBe(1); // First page
      
      goToPage(2);
      expect(getStartRowNumber()).toBe(11); // Second page
      
      goToPage(3);
      expect(getStartRowNumber()).toBe(21); // Third page
    });

    it('should calculate correct row number for index', () => {
      const { getRowNumber, goToPage } = usePagination(testData, 10);
      
      expect(getRowNumber(0)).toBe(1); // First item on first page
      expect(getRowNumber(9)).toBe(10); // Last item on first page
      
      goToPage(2);
      expect(getRowNumber(0)).toBe(11); // First item on second page
      expect(getRowNumber(5)).toBe(16); // Middle item on second page
    });
  });

  describe('data reactivity', () => {
    it('should update when data changes', () => {
      const { paginatedData, totalPages } = usePagination(testData, 10);
      
      expect(totalPages.value).toBe(3);
      expect(paginatedData.value).toHaveLength(10);
      
      // Change data
      testData.value = testData.value.slice(0, 15);
      
      expect(totalPages.value).toBe(2);
      expect(paginatedData.value).toHaveLength(10);
    });

    it('should reset to first page if current page becomes out of bounds', () => {
      const { currentPage, goToPage } = usePagination(testData, 10);
      
      goToPage(3); // Last page
      expect(currentPage.value).toBe(3);
      
      // Reduce data so page 3 no longer exists
      testData.value = testData.value.slice(0, 15);
      
      expect(currentPage.value).toBe(1);
    });
  });

  describe('edge cases', () => {
    it('should handle data length exactly divisible by page size', () => {
      const exactData = ref(Array.from({ length: 20 }, (_, i) => ({ id: i + 1 })));
      const { totalPages, paginatedData, goToPage } = usePagination(exactData, 10);
      
      expect(totalPages.value).toBe(2);
      
      goToPage(2);
      expect(paginatedData.value).toHaveLength(10);
    });

    it('should handle single item', () => {
      const singleItem = ref([{ id: 1, name: 'Only' }]);
      const { totalPages, paginatedData } = usePagination(singleItem, 10);
      
      expect(totalPages.value).toBe(1);
      expect(paginatedData.value).toHaveLength(1);
    });

    it('should handle page size larger than data length', () => {
      const smallData = ref([{ id: 1 }, { id: 2 }, { id: 3 }]);
      const { totalPages, paginatedData } = usePagination(smallData, 10);
      
      expect(totalPages.value).toBe(1);
      expect(paginatedData.value).toHaveLength(3);
    });
  });
});
