import { describe, it, expect, beforeEach } from 'vitest';
import { ref } from 'vue';
import { useSorting } from '@/composables/useSorting';

describe('useSorting', () => {
  let testData;

  beforeEach(() => {
    testData = ref([
      { id: 3, name: 'Charlie', age: 35, date: new Date('2020-03-15') },
      { id: 1, name: 'Alice', age: 25, date: new Date('2022-01-10') },
      { id: 2, name: 'Bob', age: 30, date: new Date('2021-06-20') },
      { id: 5, name: 'Eve', age: 28, date: new Date('2023-02-05') },
      { id: 4, name: 'David', age: 32, date: new Date('2019-11-30') }
    ]);
  });

  describe('initialization', () => {
    it('should initialize with no sorting', () => {
      const { sortKey, sortOrder, sortedData } = useSorting(testData);
      
      expect(sortKey.value).toBe('');
      expect(sortOrder.value).toBe('asc');
      expect(sortedData.value).toEqual(testData.value);
    });

    it('should initialize with default sort key', () => {
      const { sortKey, sortedData } = useSorting(testData, {
        defaultSortKey: 'name',
        defaultSortOrder: 'asc'
      });
      
      expect(sortKey.value).toBe('name');
      expect(sortedData.value[0].name).toBe('Alice');
      expect(sortedData.value[4].name).toBe('Eve');
    });

    it('should initialize with descending order', () => {
      const { sortOrder, sortedData } = useSorting(testData, {
        defaultSortKey: 'id',
        defaultSortOrder: 'desc'
      });
      
      expect(sortOrder.value).toBe('desc');
      expect(sortedData.value[0].id).toBe(5);
      expect(sortedData.value[4].id).toBe(1);
    });

    it('should handle empty data', () => {
      const emptyData = ref([]);
      const { sortedData } = useSorting(emptyData);
      
      expect(sortedData.value).toEqual([]);
    });

    it('should handle null data', () => {
      const nullData = ref(null);
      const { sortedData } = useSorting(nullData);
      
      expect(sortedData.value).toEqual([]);
    });
  });

  describe('sorting by different data types', () => {
    it('should sort numbers correctly', () => {
      const { sortBy, sortedData } = useSorting(testData);
      
      sortBy('age');
      
      expect(sortedData.value.map(item => item.age)).toEqual([25, 28, 30, 32, 35]);
    });

    it('should sort strings alphabetically', () => {
      const { sortBy, sortedData } = useSorting(testData);
      
      sortBy('name');
      
      expect(sortedData.value.map(item => item.name)).toEqual(['Alice', 'Bob', 'Charlie', 'David', 'Eve']);
    });

    it('should sort dates chronologically', () => {
      const { sortBy, sortedData } = useSorting(testData);
      
      sortBy('date');
      
      const years = sortedData.value.map(item => item.date.getFullYear());
      expect(years).toEqual([2019, 2020, 2021, 2022, 2023]);
    });

    it('should handle numeric strings', () => {
      const numericData = ref([
        { id: '10' },
        { id: '2' },
        { id: '1' },
        { id: '20' }
      ]);
      
      const { sortBy, sortedData } = useSorting(numericData);
      sortBy('id');
      
      // Should sort numerically, not alphabetically
      expect(sortedData.value.map(item => item.id)).toEqual(['1', '2', '10', '20']);
    });
  });

  describe('sort direction', () => {
    it('should sort ascending by default', () => {
      const { sortBy, sortedData, sortOrder } = useSorting(testData);
      
      sortBy('age');
      
      expect(sortOrder.value).toBe('asc');
      expect(sortedData.value[0].age).toBe(25);
      expect(sortedData.value[4].age).toBe(35);
    });

    it('should toggle to descending on second click', () => {
      const { sortBy, sortedData, sortOrder } = useSorting(testData);
      
      sortBy('age');
      sortBy('age'); // Second click
      
      expect(sortOrder.value).toBe('desc');
      expect(sortedData.value[0].age).toBe(35);
      expect(sortedData.value[4].age).toBe(25);
    });

    it('should toggle back to ascending on third click', () => {
      const { sortBy, sortedData, sortOrder } = useSorting(testData);
      
      sortBy('age');
      sortBy('age');
      sortBy('age'); // Third click
      
      expect(sortOrder.value).toBe('asc');
      expect(sortedData.value[0].age).toBe(25);
    });

    it('should reset to ascending when sorting by different field', () => {
      const { sortBy, sortOrder } = useSorting(testData);
      
      sortBy('age');
      sortBy('age'); // Now descending
      expect(sortOrder.value).toBe('desc');
      
      sortBy('name'); // Different field
      expect(sortOrder.value).toBe('asc');
    });
  });

  describe('sort methods', () => {
    it('should set sorting explicitly', () => {
      const { setSorting, sortKey, sortOrder, sortedData } = useSorting(testData);
      
      setSorting('age', 'desc');
      
      expect(sortKey.value).toBe('age');
      expect(sortOrder.value).toBe('desc');
      expect(sortedData.value[0].age).toBe(35);
    });

    it('should clear sorting', () => {
      const { sortBy, clearSorting, sortKey, sortOrder, sortedData } = useSorting(testData);
      
      sortBy('age');
      expect(sortKey.value).toBe('age');
      
      clearSorting();
      
      expect(sortKey.value).toBe('');
      expect(sortOrder.value).toBe('asc');
      expect(sortedData.value).toEqual(testData.value); // Back to original order
    });
  });

  describe('helper methods', () => {
    it('should return sort icon for current field', () => {
      const { sortBy, getSortIcon } = useSorting(testData);
      
      expect(getSortIcon('age')).toBe('');
      
      sortBy('age');
      expect(getSortIcon('age')).toBe(' ▲');
      
      sortBy('age'); // Toggle to desc
      expect(getSortIcon('age')).toBe(' ▼');
    });

    it('should return empty string for non-sorted fields', () => {
      const { sortBy, getSortIcon } = useSorting(testData);
      
      sortBy('age');
      expect(getSortIcon('name')).toBe('');
    });

    it('should check if field is currently sorted', () => {
      const { sortBy, isSortedBy } = useSorting(testData);
      
      expect(isSortedBy('age')).toBe(false);
      
      sortBy('age');
      expect(isSortedBy('age')).toBe(true);
      expect(isSortedBy('name')).toBe(false);
    });

    it('should check if sorting is ascending', () => {
      const { sortBy, isAscending } = useSorting(testData);
      
      sortBy('age');
      expect(isAscending()).toBe(true);
      
      sortBy('age'); // Toggle to desc
      expect(isAscending()).toBe(false);
    });

    it('should check if sorting is descending', () => {
      const { sortBy, isDescending } = useSorting(testData);
      
      sortBy('age');
      expect(isDescending()).toBe(false);
      
      sortBy('age'); // Toggle to desc
      expect(isDescending()).toBe(true);
    });
  });

  describe('custom comparator', () => {
    it('should use custom comparator when provided', () => {
      const customComparator = (a, b) => {
        // Custom logic: sort by absolute distance from 30
        return Math.abs(a - 30) - Math.abs(b - 30);
      };
      
      const { sortBy, sortedData } = useSorting(testData, { customComparator });
      
      sortBy('age');
      
      // Closest to 30 should be first
      expect(sortedData.value[0].age).toBe(30); // Exact match
      expect(sortedData.value[1].age).toBe(28); // 2 away
    });
  });

  describe('null and undefined handling', () => {
    it('should handle null values', () => {
      const dataWithNulls = ref([
        { id: 1, value: 10 },
        { id: 2, value: null },
        { id: 3, value: 5 },
        { id: 4, value: null }
      ]);
      
      const { sortBy, sortedData } = useSorting(dataWithNulls);
      sortBy('value');
      
      // Nulls should be sorted to the beginning (treated as empty strings)
      expect(sortedData.value[0].value).toBe(null);
      expect(sortedData.value[1].value).toBe(null);
      expect(sortedData.value[2].value).toBe(5);
      expect(sortedData.value[3].value).toBe(10);
    });

    it('should handle undefined values', () => {
      const dataWithUndefined = ref([
        { id: 1, value: 10 },
        { id: 2, value: undefined },
        { id: 3, value: 5 }
      ]);
      
      const { sortBy, sortedData } = useSorting(dataWithUndefined);
      sortBy('value');
      
      expect(sortedData.value[0].value).toBe(undefined);
      expect(sortedData.value[1].value).toBe(5);
      expect(sortedData.value[2].value).toBe(10);
    });
  });

  describe('data reactivity', () => {
    it('should update sorted data when source data changes', () => {
      const { sortBy, sortedData } = useSorting(testData);
      
      sortBy('age');
      expect(sortedData.value[0].age).toBe(25);
      
      // Add new youngest person
      testData.value.push({ id: 6, name: 'Frank', age: 20, date: new Date() });
      
      expect(sortedData.value[0].age).toBe(20);
      expect(sortedData.value).toHaveLength(6);
    });

    it('should maintain sort when data items are modified', () => {
      const { sortBy, sortedData } = useSorting(testData);
      
      sortBy('age');
      
      // Modify an item
      testData.value[0].age = 40;
      
      // Should re-sort
      expect(sortedData.value[sortedData.value.length - 1].age).toBe(40);
    });
  });

  describe('edge cases', () => {
    it('should handle single item', () => {
      const singleItem = ref([{ id: 1, name: 'Only' }]);
      const { sortBy, sortedData } = useSorting(singleItem);
      
      sortBy('name');
      
      expect(sortedData.value).toHaveLength(1);
      expect(sortedData.value[0].name).toBe('Only');
    });

    it('should handle duplicate values', () => {
      const duplicateData = ref([
        { id: 1, value: 10 },
        { id: 2, value: 10 },
        { id: 3, value: 10 }
      ]);
      
      const { sortBy, sortedData } = useSorting(duplicateData);
      sortBy('value');
      
      expect(sortedData.value).toHaveLength(3);
      expect(sortedData.value.every(item => item.value === 10)).toBe(true);
    });

    it('should handle mixed case strings', () => {
      const mixedCaseData = ref([
        { name: 'zebra' },
        { name: 'Apple' },
        { name: 'banana' },
        { name: 'Cherry' }
      ]);
      
      const { sortBy, sortedData } = useSorting(mixedCaseData);
      sortBy('name');
      
      // Should be case-insensitive
      expect(sortedData.value.map(item => item.name.toLowerCase())).toEqual([
        'apple', 'banana', 'cherry', 'zebra'
      ]);
    });

    it('should handle very long strings', () => {
      const longStringData = ref([
        { text: 'a'.repeat(1000) + 'z' },
        { text: 'a'.repeat(1000) + 'a' }
      ]);
      
      const { sortBy, sortedData } = useSorting(longStringData);
      sortBy('text');
      
      expect(sortedData.value[0].text.endsWith('a')).toBe(true);
      expect(sortedData.value[1].text.endsWith('z')).toBe(true);
    });

    it('should not mutate original data array', () => {
      const originalOrder = [...testData.value];
      const { sortBy } = useSorting(testData);
      
      sortBy('age');
      
      expect(testData.value).toEqual(originalOrder);
    });

    it('should handle sorting by non-existent field', () => {
      const { sortBy, sortedData } = useSorting(testData);
      
      sortBy('nonExistentField');
      
      // Should not throw, all values will be undefined and treated equally
      expect(sortedData.value).toHaveLength(testData.value.length);
    });
  });

  describe('performance', () => {
    it('should handle large datasets efficiently', () => {
      const largeData = ref(
        Array.from({ length: 10000 }, (_, i) => ({
          id: i,
          value: Math.random() * 1000,
          name: `Item ${i}`
        }))
      );
      
      const { sortBy, sortedData } = useSorting(largeData);
      
      const start = performance.now();
      sortBy('value');
      const duration = performance.now() - start;
      
      expect(sortedData.value).toHaveLength(10000);
      expect(duration).toBeLessThan(500); // Should sort 10k items in < 500ms
    });
  });
});
