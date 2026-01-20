/**
 * Table Filters Composable
 * 
 * Reusable table filtering functionality with support for text search,
 * field-specific filters, and range filters.
 * 
 * @module useTableFilters
 * @example
 * import { useTableFilters } from '@/composables/useTableFilters';
 * 
 * const myData = ref([...]);
 * const { filteredData, searchQuery, setSearchQuery, addFilter, removeFilter, clearFilters } = 
 *   useTableFilters(myData);
 * 
 * // Add filters
 * addFilter('status', 'active');
 * addFilter('age', { min: 18, max: 65 });
 * 
 * // Set search query
 * setSearchQuery('john');
 */

import { ref, computed } from 'vue';

/**
 * Create filtering functionality for a data array
 * 
 * @param {Ref<Array>} data - Reactive array of data to filter
 * @param {Object} [options] - Configuration options
 * @param {Array<string>} [options.searchFields] - Fields to search in (empty = all fields)
 * @param {boolean} [options.caseSensitive=false] - Case-sensitive search
 * @returns {Object} Filtering state and methods
 */
export function useTableFilters(data, options = {}) {
  const {
    searchFields = [],
    caseSensitive = false
  } = options;

  const searchQuery = ref('');
  const filters = ref({});

  /**
   * Check if a value matches the search query
   * @param {*} value - Value to check
   * @param {string} query - Search query
   * @returns {boolean} True if matches
   */
  const matchesSearch = (value, query) => {
    if (!query) return true;
    if (value === null || value === undefined) return false;

    const valueStr = caseSensitive 
      ? String(value) 
      : String(value).toLowerCase();
    const queryStr = caseSensitive 
      ? query 
      : query.toLowerCase();

    return valueStr.includes(queryStr);
  };

  /**
   * Check if an item matches a specific filter
   * @param {*} itemValue - Value from the item
   * @param {*} filterValue - Filter criteria
   * @returns {boolean} True if matches
   */
  const matchesFilter = (itemValue, filterValue) => {
    // Handle null/undefined
    if (itemValue === null || itemValue === undefined) {
      return filterValue === null || filterValue === undefined;
    }

    // Handle range filters (object with min/max)
    if (typeof filterValue === 'object' && !Array.isArray(filterValue)) {
      const { min, max } = filterValue;
      const numValue = Number(itemValue);
      
      if (min !== undefined && numValue < min) return false;
      if (max !== undefined && numValue > max) return false;
      return true;
    }

    // Handle array filters (value must be in array)
    if (Array.isArray(filterValue)) {
      return filterValue.includes(itemValue);
    }

    // Exact match for other types
    return itemValue === filterValue;
  };

  /**
   * Check if an item matches the search query
   * @param {Object} item - Data item to check
   * @returns {boolean} True if matches
   */
  const matchesSearchQuery = (item) => {
    if (!searchQuery.value) return true;

    // If searchFields specified, only search those fields
    const fieldsToSearch = searchFields.length > 0 
      ? searchFields 
      : Object.keys(item);

    return fieldsToSearch.some(field => 
      matchesSearch(item[field], searchQuery.value)
    );
  };

  /**
   * Check if an item matches all active filters
   * @param {Object} item - Data item to check
   * @returns {boolean} True if matches all filters
   */
  const matchesAllFilters = (item) => {
    return Object.entries(filters.value).every(([field, filterValue]) => {
      // Skip if filter is not set or empty
      if (filterValue === '' || filterValue === null || filterValue === undefined) {
        return true;
      }

      return matchesFilter(item[field], filterValue);
    });
  };

  /**
   * Filtered data based on search query and filters
   */
  const filteredData = computed(() => {
    if (!data.value) return [];

    return data.value.filter(item => 
      matchesSearchQuery(item) && matchesAllFilters(item)
    );
  });

  /**
   * Number of active filters
   */
  const activeFilterCount = computed(() => {
    return Object.values(filters.value).filter(v => 
      v !== '' && v !== null && v !== undefined
    ).length + (searchQuery.value ? 1 : 0);
  });

  /**
   * Set search query
   * @param {string} query - Search text
   */
  const setSearchQuery = (query) => {
    searchQuery.value = query;
  };

  /**
   * Add or update a filter
   * @param {string} field - Field name to filter
   * @param {*} value - Filter value
   */
  const addFilter = (field, value) => {
    filters.value[field] = value;
  };

  /**
   * Remove a specific filter
   * @param {string} field - Field name
   */
  const removeFilter = (field) => {
    delete filters.value[field];
  };

  /**
   * Clear all filters (including search)
   */
  const clearFilters = () => {
    searchQuery.value = '';
    filters.value = {};
  };

  /**
   * Clear only field filters (keep search)
   */
  const clearFieldFilters = () => {
    filters.value = {};
  };

  /**
   * Set multiple filters at once
   * @param {Object} newFilters - Object with field-value pairs
   */
  const setFilters = (newFilters) => {
    filters.value = { ...newFilters };
  };

  /**
   * Check if a specific filter is active
   * @param {string} field - Field name
   * @returns {boolean} True if filter is set
   */
  const hasFilter = (field) => {
    const value = filters.value[field];
    return value !== '' && value !== null && value !== undefined;
  };

  /**
   * Get filter value for a specific field
   * @param {string} field - Field name
   * @returns {*} Filter value or undefined
   */
  const getFilter = (field) => {
    return filters.value[field];
  };

  return {
    // State
    searchQuery,
    filters,
    
    // Computed
    filteredData,
    activeFilterCount,
    
    // Methods
    setSearchQuery,
    addFilter,
    removeFilter,
    clearFilters,
    clearFieldFilters,
    setFilters,
    hasFilter,
    getFilter
  };
}

export default useTableFilters;
