/**
 * Pagination Composable
 * 
 * Reusable pagination logic for table components.
 * Provides reactive pagination state, computed values, and navigation methods.
 * 
 * @module usePagination
 * @example
 * import { usePagination } from '@/composables/usePagination';
 * 
 * const myData = ref([...]);
 * const { currentPage, totalPages, paginatedData, nextPage, prevPage, goToPage } = 
 *   usePagination(myData, 10);
 * 
 * // In template:
 * // <div v-for="item in paginatedData" :key="item.id">{{ item }}</div>
 * // <button @click="prevPage">Previous</button>
 * // <span>Page {{ currentPage }} of {{ totalPages }}</span>
 * // <button @click="nextPage">Next</button>
 */

import { ref, computed, watch } from 'vue';
import { PAGINATION } from '@/utils/constants';

/**
 * Create pagination functionality for a data array
 * 
 * @param {Ref<Array>} data - Reactive array of data to paginate
 * @param {number} [pageSize=PAGINATION.DEFAULT_PAGE_SIZE] - Number of items per page
 * @returns {Object} Pagination state and methods
 */
export function usePagination(data, pageSize = PAGINATION.DEFAULT_PAGE_SIZE) {
  const currentPage = ref(PAGINATION.DEFAULT_CURRENT_PAGE);
  const itemsPerPage = ref(pageSize);

  /**
   * Total number of pages based on data length and page size
   */
  const totalPages = computed(() => {
    return Math.ceil((data.value?.length || 0) / itemsPerPage.value);
  });

  /**
   * Current page's data slice
   */
  const paginatedData = computed(() => {
    if (!data.value) return [];
    const start = (currentPage.value - 1) * itemsPerPage.value;
    const end = start + itemsPerPage.value;
    return data.value.slice(start, end);
  });

  /**
   * Check if there's a previous page
   */
  const hasPrevPage = computed(() => currentPage.value > 1);

  /**
   * Check if there's a next page
   */
  const hasNextPage = computed(() => currentPage.value < totalPages.value);

  /**
   * Navigate to the previous page
   */
  const prevPage = () => {
    if (hasPrevPage.value) {
      currentPage.value--;
    }
  };

  /**
   * Navigate to the next page
   */
  const nextPage = () => {
    if (hasNextPage.value) {
      currentPage.value++;
    }
  };

  /**
   * Navigate to a specific page
   * @param {number} page - Page number to navigate to
   */
  const goToPage = (page) => {
    if (page >= 1 && page <= totalPages.value) {
      currentPage.value = page;
    }
  };

  /**
   * Reset to first page (useful when data changes)
   */
  const resetPage = () => {
    currentPage.value = 1;
  };

  /**
   * Update items per page
   * @param {number} newPageSize - New page size
   */
  const setPageSize = (newPageSize) => {
    itemsPerPage.value = newPageSize;
    // Reset to first page when page size changes
    resetPage();
  };

  /**
   * Get the starting row number for the current page
   * Useful for displaying row numbers in tables
   * @returns {number} Starting row number (1-indexed)
   */
  const getStartRowNumber = () => {
    return (currentPage.value - 1) * itemsPerPage.value + 1;
  };

  /**
   * Get the row number for a specific index on the current page
   * @param {number} index - Index within the current page (0-indexed)
   * @returns {number} Global row number (1-indexed)
   */
  const getRowNumber = (index) => {
    return (currentPage.value - 1) * itemsPerPage.value + index + 1;
  };

  // Watch for data changes and reset to first page if current page is out of bounds
  watch([data, totalPages], () => {
    if (currentPage.value > totalPages.value && totalPages.value > 0) {
      resetPage();
    }
  });

  return {
    // State
    currentPage,
    itemsPerPage,
    
    // Computed
    totalPages,
    paginatedData,
    hasPrevPage,
    hasNextPage,
    
    // Methods
    prevPage,
    nextPage,
    goToPage,
    resetPage,
    setPageSize,
    getStartRowNumber,
    getRowNumber
  };
}

export default usePagination;
