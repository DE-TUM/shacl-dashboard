/**
 * Sorting Composable
 * 
 * Reusable table sorting functionality with support for ascending/descending order.
 * Handles different data types (strings, numbers, dates) intelligently.
 * 
 * @module useSorting
 * @example
 * import { useSorting } from '@/composables/useSorting';
 * 
 * const myData = ref([...]);
 * const { sortedData, sortKey, sortOrder, sortBy, getSortIcon } = useSorting(myData);
 * 
 * // In template:
 * // <th @click="sortBy('name')">Name {{ getSortIcon('name') }}</th>
 */

import { ref, computed } from 'vue';

/**
 * Create sorting functionality for a data array
 * 
 * @param {Ref<Array>} data - Reactive array of data to sort
 * @param {Object} [options] - Configuration options
 * @param {string} [options.defaultSortKey=''] - Default field to sort by
 * @param {string} [options.defaultSortOrder='asc'] - Default sort order ('asc' or 'desc')
 * @param {Function} [options.customComparator] - Custom comparison function
 * @returns {Object} Sorting state and methods
 */
export function useSorting(data, options = {}) {
  const {
    defaultSortKey = '',
    defaultSortOrder = 'asc',
    customComparator = null
  } = options;

  const sortKey = ref(defaultSortKey);
  const sortOrder = ref(defaultSortOrder);

  /**
   * Default comparison function that handles multiple data types
   * @param {*} a - First value
   * @param {*} b - Second value
   * @returns {number} Comparison result (-1, 0, 1)
   */
  const defaultComparator = (a, b) => {
    // Handle null/undefined
    const valA = a ?? '';
    const valB = b ?? '';

    // If both are numbers, compare numerically
    if (typeof valA === 'number' && typeof valB === 'number') {
      return valA - valB;
    }

    // If both are dates, compare by time
    if (valA instanceof Date && valB instanceof Date) {
      return valA.getTime() - valB.getTime();
    }

    // Convert to string and use locale comparison with numeric support
    return valA.toString().localeCompare(
      valB.toString(),
      undefined,
      { numeric: true, sensitivity: 'base' }
    );
  };

  /**
   * Sorted data based on current sort key and order
   */
  const sortedData = computed(() => {
    if (!data.value || !sortKey.value) {
      return data.value || [];
    }

    const comparator = customComparator || defaultComparator;

    return [...data.value].sort((a, b) => {
      const valA = a[sortKey.value];
      const valB = b[sortKey.value];
      
      const result = comparator(valA, valB);
      return sortOrder.value === 'asc' ? result : -result;
    });
  });

  /**
   * Sort by a specific field (toggle order if already sorting by this field)
   * @param {string} field - Field name to sort by
   */
  const sortBy = (field) => {
    if (sortKey.value === field) {
      // Toggle sort order
      sortOrder.value = sortOrder.value === 'asc' ? 'desc' : 'asc';
    } else {
      // New field, default to ascending
      sortKey.value = field;
      sortOrder.value = 'asc';
    }
  };

  /**
   * Set sort parameters explicitly
   * @param {string} field - Field name to sort by
   * @param {string} order - Sort order ('asc' or 'desc')
   */
  const setSorting = (field, order = 'asc') => {
    sortKey.value = field;
    sortOrder.value = order;
  };

  /**
   * Clear sorting (reset to original order)
   */
  const clearSorting = () => {
    sortKey.value = '';
    sortOrder.value = 'asc';
  };

  /**
   * Get sort indicator icon for a specific field
   * @param {string} field - Field name
   * @returns {string} Unicode triangle icon or empty string
   */
  const getSortIcon = (field) => {
    if (sortKey.value !== field) return '';
    return sortOrder.value === 'asc' ? ' ▲' : ' ▼';
  };

  /**
   * Check if a field is currently being sorted
   * @param {string} field - Field name
   * @returns {boolean} True if this field is the active sort key
   */
  const isSortedBy = (field) => {
    return sortKey.value === field;
  };

  /**
   * Check if current sort is ascending
   * @returns {boolean} True if ascending order
   */
  const isAscending = () => {
    return sortOrder.value === 'asc';
  };

  /**
   * Check if current sort is descending
   * @returns {boolean} True if descending order
   */
  const isDescending = () => {
    return sortOrder.value === 'desc';
  };

  return {
    // State
    sortKey,
    sortOrder,
    
    // Computed
    sortedData,
    
    // Methods
    sortBy,
    setSorting,
    clearSorting,
    getSortIcon,
    isSortedBy,
    isAscending,
    isDescending
  };
}

export default useSorting;
