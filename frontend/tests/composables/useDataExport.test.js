import { describe, it, expect, beforeEach, vi } from 'vitest';
import { useDataExport } from '@/composables/useDataExport';

// Mock logger
vi.mock('@/services/logger', () => ({
  logger: {
    info: vi.fn(),
    warn: vi.fn(),
    error: vi.fn()
  }
}));

describe('useDataExport', () => {
  let testData;
  let createObjectURLSpy;
  let revokeObjectURLSpy;

  beforeEach(() => {
    testData = [
      { id: 1, name: 'Alice', age: 25, city: 'New York' },
      { id: 2, name: 'Bob', age: 30, city: 'Los Angeles' },
      { id: 3, name: 'Charlie', age: 35, city: 'Chicago' }
    ];

    // Mock URL.createObjectURL and revokeObjectURL
    createObjectURLSpy = vi.spyOn(URL, 'createObjectURL').mockReturnValue('blob:mock-url');
    revokeObjectURLSpy = vi.spyOn(URL, 'revokeObjectURL').mockImplementation(() => {});

    // Mock DOM methods
    global.Blob = vi.fn((content, options) => ({ content, options }));
    global.alert = vi.fn();
    
    // Mock document methods
    const mockLink = {
      setAttribute: vi.fn(),
      click: vi.fn(),
      style: {}
    };
    vi.spyOn(document, 'createElement').mockReturnValue(mockLink);
    vi.spyOn(document.body, 'appendChild').mockImplementation(() => {});
    vi.spyOn(document.body, 'removeChild').mockImplementation(() => {});
  });

  describe('formatCSVValue', () => {
    it('should format string values with quotes', () => {
      const { formatCSVValue } = useDataExport();
      
      expect(formatCSVValue('hello')).toBe('"hello"');
    });

    it('should escape double quotes in strings', () => {
      const { formatCSVValue } = useDataExport();
      
      expect(formatCSVValue('hello "world"')).toBe('"hello ""world"""');
    });

    it('should handle null and undefined', () => {
      const { formatCSVValue } = useDataExport();
      
      expect(formatCSVValue(null)).toBe('');
      expect(formatCSVValue(undefined)).toBe('');
    });

    it('should handle numbers', () => {
      const { formatCSVValue } = useDataExport();
      
      expect(formatCSVValue(42)).toBe(42);
      expect(formatCSVValue(3.14)).toBe(3.14);
    });

    it('should handle arrays by joining with separator', () => {
      const { formatCSVValue } = useDataExport();
      
      expect(formatCSVValue(['a', 'b', 'c'])).toBe('"a; b; c"');
    });

    it('should handle objects by converting to JSON', () => {
      const { formatCSVValue } = useDataExport();
      
      const result = formatCSVValue({ key: 'value' });
      expect(result).toBe('"{""key"":""value""}"');
    });

    it('should handle booleans', () => {
      const { formatCSVValue } = useDataExport();
      
      expect(formatCSVValue(true)).toBe(true);
      expect(formatCSVValue(false)).toBe(false);
    });
  });

  describe('dataToCSV', () => {
    it('should convert array of objects to CSV string', () => {
      const { dataToCSV } = useDataExport();
      
      const csv = dataToCSV(testData);
      const lines = csv.split('\n');
      
      expect(lines[0]).toBe('id,name,age,city');
      expect(lines).toHaveLength(4); // Header + 3 data rows
    });

    it('should handle values with commas', () => {
      const { dataToCSV } = useDataExport();
      const data = [{ name: 'Last, First', value: 100 }];
      
      const csv = dataToCSV(data);
      expect(csv).toContain('"Last, First"');
    });

    it('should throw error for empty data', () => {
      const { dataToCSV } = useDataExport();
      
      expect(() => dataToCSV([])).toThrow('No data to export');
      expect(() => dataToCSV(null)).toThrow('No data to export');
    });

    it('should handle complex nested data', () => {
      const { dataToCSV } = useDataExport();
      const complexData = [
        { id: 1, tags: ['tag1', 'tag2'], meta: { created: '2024-01-01' } }
      ];
      
      const csv = dataToCSV(complexData);
      expect(csv).toContain('id,tags,meta');
      expect(csv).toContain('"tag1; tag2"');
    });
  });

  describe('downloadCSV', () => {
    it('should download CSV file successfully', () => {
      const { downloadCSV } = useDataExport();
      
      const result = downloadCSV(testData, 'test.csv');
      
      expect(result).toBe(true);
      expect(createObjectURLSpy).toHaveBeenCalled();
      expect(revokeObjectURLSpy).toHaveBeenCalled();
    });

    it('should use default filename if not provided', () => {
      const { downloadCSV } = useDataExport();
      
      const mockLink = document.createElement('a');
      downloadCSV(testData);
      
      expect(mockLink.setAttribute).toHaveBeenCalledWith('download', expect.stringContaining('.csv'));
    });

    it('should return false and show alert for empty data', () => {
      const { downloadCSV } = useDataExport();
      
      const result = downloadCSV([]);
      
      expect(result).toBe(false);
      expect(global.alert).toHaveBeenCalledWith('No data available to export.');
    });

    it('should not show alert when showAlert is false', () => {
      const { downloadCSV } = useDataExport();
      
      downloadCSV([], 'test.csv', { showAlert: false });
      
      expect(global.alert).not.toHaveBeenCalled();
    });

    it('should handle download errors gracefully', () => {
      const { downloadCSV } = useDataExport();
      
      // Make dataToCSV throw an error
      const badData = [{ id: 1 }];
      badData[0] = null; // This will cause an error when trying to get keys
      
      const result = downloadCSV([null], 'test.csv');
      
      expect(result).toBe(false);
    });

    it('should create proper Blob with correct MIME type', () => {
      const { downloadCSV } = useDataExport();
      
      downloadCSV(testData, 'test.csv');
      
      expect(global.Blob).toHaveBeenCalledWith(
        expect.any(Array),
        expect.objectContaining({ type: 'text/csv;charset=utf-8;' })
      );
    });
  });

  describe('downloadJSON', () => {
    it('should download JSON file successfully', () => {
      const { downloadJSON } = useDataExport();
      
      const result = downloadJSON(testData, 'test.json');
      
      expect(result).toBe(true);
      expect(createObjectURLSpy).toHaveBeenCalled();
      expect(revokeObjectURLSpy).toHaveBeenCalled();
    });

    it('should use default filename if not provided', () => {
      const { downloadJSON } = useDataExport();
      
      const mockLink = document.createElement('a');
      downloadJSON(testData);
      
      expect(mockLink.setAttribute).toHaveBeenCalledWith('download', expect.stringContaining('.json'));
    });

    it('should format JSON with indentation', () => {
      const { downloadJSON } = useDataExport();
      
      downloadJSON(testData, 'test.json', { indent: 4 });
      
      expect(global.Blob).toHaveBeenCalledWith(
        expect.arrayContaining([expect.stringContaining('    ')]),
        expect.any(Object)
      );
    });

    it('should return false for null data', () => {
      const { downloadJSON } = useDataExport();
      
      const result = downloadJSON(null);
      
      expect(result).toBe(false);
      expect(global.alert).toHaveBeenCalled();
    });

    it('should handle any JSON-serializable data', () => {
      const { downloadJSON } = useDataExport();
      
      const complexData = {
        users: testData,
        metadata: { total: 3, page: 1 }
      };
      
      const result = downloadJSON(complexData, 'test.json');
      
      expect(result).toBe(true);
    });

    it('should create proper Blob with correct MIME type', () => {
      const { downloadJSON } = useDataExport();
      
      downloadJSON(testData, 'test.json');
      
      expect(global.Blob).toHaveBeenCalledWith(
        expect.any(Array),
        expect.objectContaining({ type: 'application/json;charset=utf-8;' })
      );
    });
  });

  describe('copyToClipboard', () => {
    it('should copy CSV data to clipboard', async () => {
      const { copyToClipboard } = useDataExport();
      
      // Mock clipboard API
      global.navigator.clipboard = {
        writeText: vi.fn().mockResolvedValue(undefined)
      };
      
      const result = await copyToClipboard(testData);
      
      expect(result).toBe(true);
      expect(navigator.clipboard.writeText).toHaveBeenCalledWith(
        expect.stringContaining('id,name,age,city')
      );
    });

    it('should return false for empty data', async () => {
      const { copyToClipboard } = useDataExport();
      
      const result = await copyToClipboard([]);
      
      expect(result).toBe(false);
    });

    it('should handle clipboard errors', async () => {
      const { copyToClipboard } = useDataExport();
      
      // Mock clipboard API to throw error
      global.navigator.clipboard = {
        writeText: vi.fn().mockRejectedValue(new Error('Clipboard error'))
      };
      
      const result = await copyToClipboard(testData);
      
      expect(result).toBe(false);
    });
  });

  describe('edge cases', () => {
    it('should handle data with special characters', () => {
      const { dataToCSV } = useDataExport();
      const specialData = [
        { text: 'Line\nBreak', quote: 'He said "Hi"', comma: 'a,b,c' }
      ];
      
      const csv = dataToCSV(specialData);
      
      expect(csv).toContain('Line\nBreak');
      expect(csv).toContain('""Hi""');
    });

    it('should handle empty strings in data', () => {
      const { dataToCSV } = useDataExport();
      const data = [{ name: '', value: 0 }];
      
      const csv = dataToCSV(data);
      
      expect(csv).toContain('name,value');
      expect(csv).toContain('"",0');
    });

    it('should handle mixed data types in same column', () => {
      const { dataToCSV } = useDataExport();
      const mixedData = [
        { value: 'text' },
        { value: 123 },
        { value: null },
        { value: true }
      ];
      
      expect(() => dataToCSV(mixedData)).not.toThrow();
    });

    it('should handle objects with different keys', () => {
      const { dataToCSV } = useDataExport();
      const data = [
        { id: 1, name: 'Alice' },
        { id: 2, age: 30 } // Missing 'name', has 'age'
      ];
      
      const csv = dataToCSV(data);
      const lines = csv.split('\n');
      
      // Headers from first object
      expect(lines[0]).toBe('id,name');
      expect(lines).toHaveLength(3);
    });
  });
});
