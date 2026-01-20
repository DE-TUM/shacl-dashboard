import { describe, it, expect, beforeEach } from 'vitest';
import { ref } from 'vue';
import { useTableFilters } from '@/composables/useTableFilters';

describe('useTableFilters', () => {
  let testData;

  beforeEach(() => {
    testData = ref([
      { id: 1, name: 'Alice', age: 25, status: 'active', city: 'New York' },
      { id: 2, name: 'Bob', age: 30, status: 'inactive', city: 'Los Angeles' },
      { id: 3, name: 'Charlie', age: 35, status: 'active', city: 'Chicago' },
      { id: 4, name: 'David', age: 28, status: 'pending', city: 'Houston' },
      { id: 5, name: 'Eve', age: 32, status: 'active', city: 'Phoenix' }
    ]);
  });

  describe('initialization', () => {
    it('should initialize with empty filters', () => {
      const { searchQuery, filteredData } = useTableFilters(testData);
      
      expect(searchQuery.value).toBe('');
      expect(filteredData.value).toEqual(testData.value);
    });

    it('should handle empty data', () => {
      const emptyData = ref([]);
      const { filteredData } = useTableFilters(emptyData);
      
      expect(filteredData.value).toEqual([]);
    });

    it('should handle null data', () => {
      const nullData = ref(null);
      const { filteredData } = useTableFilters(nullData);
      
      expect(filteredData.value).toEqual([]);
    });
  });

  describe('search functionality', () => {
    it('should filter by search query (case-insensitive by default)', () => {
      const { setSearchQuery, filteredData } = useTableFilters(testData);
      
      setSearchQuery('alice');
      expect(filteredData.value).toHaveLength(1);
      expect(filteredData.value[0].name).toBe('Alice');
    });

    it('should search across all fields by default', () => {
      const { setSearchQuery, filteredData } = useTableFilters(testData);
      
      setSearchQuery('New York');
      expect(filteredData.value).toHaveLength(1);
      expect(filteredData.value[0].city).toBe('New York');
      
      setSearchQuery('30');
      expect(filteredData.value).toHaveLength(1);
      expect(filteredData.value[0].age).toBe(30);
    });

    it('should search only in specified fields when searchFields provided', () => {
      const { setSearchQuery, filteredData } = useTableFilters(testData, {
        searchFields: ['name']
      });
      
      setSearchQuery('New York');
      expect(filteredData.value).toHaveLength(0); // City not in searchFields
      
      setSearchQuery('Bob');
      expect(filteredData.value).toHaveLength(1);
      expect(filteredData.value[0].name).toBe('Bob');
    });

    it('should support case-sensitive search when configured', () => {
      const { setSearchQuery, filteredData } = useTableFilters(testData, {
        caseSensitive: true
      });
      
      setSearchQuery('alice');
      expect(filteredData.value).toHaveLength(0);
      
      setSearchQuery('Alice');
      expect(filteredData.value).toHaveLength(1);
    });

    it('should return all data when search query is empty', () => {
      const { setSearchQuery, filteredData } = useTableFilters(testData);
      
      setSearchQuery('Alice');
      expect(filteredData.value).toHaveLength(1);
      
      setSearchQuery('');
      expect(filteredData.value).toHaveLength(5);
    });

    it('should handle partial matches', () => {
      const { setSearchQuery, filteredData } = useTableFilters(testData);
      
      setSearchQuery('ar');
      expect(filteredData.value).toHaveLength(1);
      expect(filteredData.value[0].name).toBe('Charlie');
    });
  });

  describe('field filters', () => {
    it('should filter by exact field value', () => {
      const { addFilter, filteredData } = useTableFilters(testData);
      
      addFilter('status', 'active');
      expect(filteredData.value).toHaveLength(3);
      expect(filteredData.value.every(item => item.status === 'active')).toBe(true);
    });

    it('should filter by multiple fields', () => {
      const { addFilter, filteredData } = useTableFilters(testData);
      
      addFilter('status', 'active');
      addFilter('city', 'New York');
      
      expect(filteredData.value).toHaveLength(1);
      expect(filteredData.value[0].name).toBe('Alice');
    });

    it('should handle range filters (min/max)', () => {
      const { addFilter, filteredData } = useTableFilters(testData);
      
      addFilter('age', { min: 30, max: 35 });
      
      expect(filteredData.value).toHaveLength(3);
      expect(filteredData.value.map(item => item.age)).toEqual([30, 35, 32]);
    });

    it('should handle range filter with only min', () => {
      const { addFilter, filteredData } = useTableFilters(testData);
      
      addFilter('age', { min: 32 });
      
      expect(filteredData.value).toHaveLength(2);
      expect(filteredData.value.every(item => item.age >= 32)).toBe(true);
    });

    it('should handle range filter with only max', () => {
      const { addFilter, filteredData } = useTableFilters(testData);
      
      addFilter('age', { max: 28 });
      
      expect(filteredData.value).toHaveLength(2);
      expect(filteredData.value.every(item => item.age <= 28)).toBe(true);
    });

    it('should handle array filters (value in array)', () => {
      const { addFilter, filteredData } = useTableFilters(testData);
      
      addFilter('status', ['active', 'pending']);
      
      expect(filteredData.value).toHaveLength(4);
      expect(filteredData.value.every(item => 
        ['active', 'pending'].includes(item.status)
      )).toBe(true);
    });

    it('should handle null/undefined values', () => {
      testData.value.push({ id: 6, name: 'Frank', age: null, status: 'active' });
      const { addFilter, filteredData } = useTableFilters(testData);
      
      addFilter('age', null);
      
      expect(filteredData.value).toHaveLength(1);
      expect(filteredData.value[0].name).toBe('Frank');
    });
  });

  describe('combined search and filters', () => {
    it('should apply both search and field filters', () => {
      const { setSearchQuery, addFilter, filteredData } = useTableFilters(testData);
      
      addFilter('status', 'active');
      setSearchQuery('i'); // Should match Alice and Charlie
      
      expect(filteredData.value).toHaveLength(2);
      expect(filteredData.value.map(item => item.name)).toEqual(['Alice', 'Charlie']);
    });

    it('should return empty when no items match all criteria', () => {
      const { setSearchQuery, addFilter, filteredData } = useTableFilters(testData);
      
      addFilter('status', 'active');
      setSearchQuery('Bob'); // Bob is inactive
      
      expect(filteredData.value).toHaveLength(0);
    });
  });

  describe('filter management', () => {
    it('should update existing filter', () => {
      const { addFilter, filteredData } = useTableFilters(testData);
      
      addFilter('status', 'active');
      expect(filteredData.value).toHaveLength(3);
      
      addFilter('status', 'inactive');
      expect(filteredData.value).toHaveLength(1);
    });

    it('should remove specific filter', () => {
      const { addFilter, removeFilter, filteredData } = useTableFilters(testData);
      
      addFilter('status', 'active');
      expect(filteredData.value).toHaveLength(3);
      
      removeFilter('status');
      expect(filteredData.value).toHaveLength(5);
    });

    it('should clear all filters', () => {
      const { setSearchQuery, addFilter, clearFilters, filteredData } = useTableFilters(testData);
      
      setSearchQuery('Alice');
      addFilter('status', 'active');
      expect(filteredData.value).toHaveLength(1);
      
      clearFilters();
      expect(filteredData.value).toHaveLength(5);
    });

    it('should clear only field filters, keeping search', () => {
      const { setSearchQuery, addFilter, clearFieldFilters, filteredData } = useTableFilters(testData);
      
      setSearchQuery('active');
      addFilter('age', { min: 30 });
      
      clearFieldFilters();
      
      // Search should still be active
      expect(filteredData.value).toHaveLength(3); // All with 'active' status
    });

    it('should set multiple filters at once', () => {
      const { setFilters, filteredData } = useTableFilters(testData);
      
      setFilters({
        status: 'active',
        city: 'Phoenix'
      });
      
      expect(filteredData.value).toHaveLength(1);
      expect(filteredData.value[0].name).toBe('Eve');
    });

    it('should check if specific filter is active', () => {
      const { addFilter, hasFilter } = useTableFilters(testData);
      
      expect(hasFilter('status')).toBe(false);
      
      addFilter('status', 'active');
      expect(hasFilter('status')).toBe(true);
    });
  });

  describe('active filter count', () => {
    it('should count active filters correctly', () => {
      const { setSearchQuery, addFilter, activeFilterCount } = useTableFilters(testData);
      
      expect(activeFilterCount.value).toBe(0);
      
      setSearchQuery('test');
      expect(activeFilterCount.value).toBe(1);
      
      addFilter('status', 'active');
      expect(activeFilterCount.value).toBe(2);
      
      addFilter('city', 'Chicago');
      expect(activeFilterCount.value).toBe(3);
    });

    it('should not count empty/null filters', () => {
      const { addFilter, activeFilterCount } = useTableFilters(testData);
      
      addFilter('status', '');
      addFilter('city', null);
      addFilter('age', undefined);
      
      expect(activeFilterCount.value).toBe(0);
    });
  });

  describe('data reactivity', () => {
    it('should update filtered results when data changes', () => {
      const { addFilter, filteredData } = useTableFilters(testData);
      
      addFilter('status', 'active');
      expect(filteredData.value).toHaveLength(3);
      
      // Add new active user
      testData.value.push({ id: 6, name: 'Frank', age: 40, status: 'active', city: 'Boston' });
      
      expect(filteredData.value).toHaveLength(4);
    });

    it('should handle data removal', () => {
      const { setSearchQuery, filteredData } = useTableFilters(testData);
      
      setSearchQuery('Alice');
      expect(filteredData.value).toHaveLength(1);
      
      // Remove Alice from data
      testData.value = testData.value.filter(item => item.name !== 'Alice');
      
      expect(filteredData.value).toHaveLength(0);
    });
  });

  describe('edge cases', () => {
    it('should handle filters on non-existent fields gracefully', () => {
      const { addFilter, filteredData } = useTableFilters(testData);
      
      addFilter('nonExistentField', 'value');
      
      // All items should be filtered out since the field doesn't exist
      expect(filteredData.value).toHaveLength(0);
    });

    it('should handle empty string filters', () => {
      const { addFilter, filteredData } = useTableFilters(testData);
      
      addFilter('status', '');
      
      // Empty string should be ignored
      expect(filteredData.value).toHaveLength(5);
    });

    it('should handle special characters in search', () => {
      testData.value[0].name = 'Alice (Admin)';
      const { setSearchQuery, filteredData } = useTableFilters(testData);
      
      setSearchQuery('(Admin)');
      
      expect(filteredData.value).toHaveLength(1);
    });

    it('should handle numeric string comparisons', () => {
      const { setSearchQuery, filteredData } = useTableFilters(testData);
      
      setSearchQuery('2'); // Should match id:2 and age:25, 28, 32
      
      expect(filteredData.value.length).toBeGreaterThan(0);
    });
  });
});
