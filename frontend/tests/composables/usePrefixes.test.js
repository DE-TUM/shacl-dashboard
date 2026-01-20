import { describe, it, expect, beforeEach, vi, afterEach } from 'vitest';
import { usePrefixes } from '@/composables/usePrefixes';

// Mock the API
vi.mock('@/services/api.js', () => ({
  getValidationDetailsReport: vi.fn()
}));

// Mock logger
vi.mock('@/services/logger', () => ({
  logger: {
    error: vi.fn(),
    info: vi.fn(),
    warn: vi.fn()
  }
}));

import { getValidationDetailsReport } from '@/services/api.js';

describe('usePrefixes', () => {
  const mockPrefixes = {
    'sh': 'http://www.w3.org/ns/shacl#',
    'ex': 'http://example.org/',
    'foaf': 'http://xmlns.com/foaf/0.1/',
    'rdf': 'http://www.w3.org/1999/02/22-rdf-syntax-ns#',
    'xsd': 'http://www.w3.org/2001/XMLSchema#'
  };

  beforeEach(() => {
    vi.clearAllMocks();
    
    // Reset the singleton cache by reimporting
    vi.resetModules();
  });

  afterEach(() => {
    vi.clearAllMocks();
  });

  describe('loadPrefixes', () => {
    it('should load prefixes from API', async () => {
      getValidationDetailsReport.mockResolvedValue({
        '@prefixes': mockPrefixes
      });
      
      const { loadPrefixes, prefixes } = usePrefixes();
      
      const result = await loadPrefixes();
      
      expect(result).toEqual(mockPrefixes);
      expect(prefixes.value).toEqual(mockPrefixes);
      expect(getValidationDetailsReport).toHaveBeenCalledWith(1, 0);
    });

    it('should cache prefixes after first load', async () => {
      getValidationDetailsReport.mockResolvedValue({
        '@prefixes': mockPrefixes
      });
      
      const { loadPrefixes } = usePrefixes();
      
      await loadPrefixes();
      await loadPrefixes(); // Second call
      
      // API should only be called once due to caching
      expect(getValidationDetailsReport).toHaveBeenCalledTimes(1);
    });

    it('should share cache across multiple instances', async () => {
      getValidationDetailsReport.mockResolvedValue({
        '@prefixes': mockPrefixes
      });
      
      const instance1 = usePrefixes();
      const instance2 = usePrefixes();
      
      await instance1.loadPrefixes();
      const result = await instance2.loadPrefixes();
      
      // API should only be called once
      expect(getValidationDetailsReport).toHaveBeenCalledTimes(1);
      expect(result).toEqual(mockPrefixes);
    });

    it('should handle API errors gracefully', async () => {
      const error = new Error('API Error');
      getValidationDetailsReport.mockRejectedValue(error);
      
      const { loadPrefixes, prefixes, prefixesError } = usePrefixes();
      
      const result = await loadPrefixes();
      
      expect(result).toEqual({});
      expect(prefixes.value).toEqual({});
      expect(prefixesError.value).toBe(error);
    });

    it('should handle missing @prefixes in response', async () => {
      getValidationDetailsReport.mockResolvedValue({});
      
      const { loadPrefixes, prefixes } = usePrefixes();
      
      const result = await loadPrefixes();
      
      expect(result).toEqual({});
      expect(prefixes.value).toEqual({});
    });

    it('should update loading state correctly', async () => {
      getValidationDetailsReport.mockImplementation(() => 
        new Promise(resolve => setTimeout(() => resolve({ '@prefixes': mockPrefixes }), 100))
      );
      
      const { loadPrefixes, isLoadingPrefixes } = usePrefixes();
      
      expect(isLoadingPrefixes.value).toBe(false);
      
      const promise = loadPrefixes();
      expect(isLoadingPrefixes.value).toBe(true);
      
      await promise;
      expect(isLoadingPrefixes.value).toBe(false);
    });

    it('should wait for ongoing load if already loading', async () => {
      getValidationDetailsReport.mockImplementation(() => 
        new Promise(resolve => setTimeout(() => resolve({ '@prefixes': mockPrefixes }), 100))
      );
      
      const { loadPrefixes } = usePrefixes();
      
      // Start two loads simultaneously
      const promise1 = loadPrefixes();
      const promise2 = loadPrefixes();
      
      const [result1, result2] = await Promise.all([promise1, promise2]);
      
      expect(result1).toEqual(mockPrefixes);
      expect(result2).toEqual(mockPrefixes);
      // Should only call API once
      expect(getValidationDetailsReport).toHaveBeenCalledTimes(1);
    });
  });

  describe('formatURI', () => {
    beforeEach(async () => {
      getValidationDetailsReport.mockResolvedValue({
        '@prefixes': mockPrefixes
      });
      
      const { loadPrefixes } = usePrefixes();
      await loadPrefixes();
    });

    it('should format URI with matching prefix', () => {
      const { formatURI } = usePrefixes();
      
      const result = formatURI('http://www.w3.org/ns/shacl#minCount');
      expect(result).toBe('sh:minCount');
    });

    it('should format multiple URIs correctly', () => {
      const { formatURI } = usePrefixes();
      
      expect(formatURI('http://example.org/Person')).toBe('ex:Person');
      expect(formatURI('http://xmlns.com/foaf/0.1/name')).toBe('foaf:name');
      expect(formatURI('http://www.w3.org/2001/XMLSchema#string')).toBe('xsd:string');
    });

    it('should return original URI if no prefix matches', () => {
      const { formatURI } = usePrefixes();
      
      const uri = 'http://unknown.org/something';
      expect(formatURI(uri)).toBe(uri);
    });

    it('should handle URIs without protocol', () => {
      const { formatURI } = usePrefixes();
      
      const uri = 'notAUri';
      expect(formatURI(uri)).toBe(uri);
    });

    it('should return input if prefixes not loaded', () => {
      vi.resetModules();
      const { formatURI } = usePrefixes();
      
      const uri = 'http://www.w3.org/ns/shacl#minCount';
      expect(formatURI(uri)).toBe(uri);
    });

    it('should handle null input', () => {
      const { formatURI } = usePrefixes();
      
      expect(formatURI(null)).toBe(null);
    });

    it('should handle undefined input', () => {
      const { formatURI } = usePrefixes();
      
      expect(formatURI(undefined)).toBe(undefined);
    });

    it('should handle empty string', () => {
      const { formatURI } = usePrefixes();
      
      expect(formatURI('')).toBe('');
    });

    it('should handle non-string input', () => {
      const { formatURI } = usePrefixes();
      
      expect(formatURI(123)).toBe(123);
      expect(formatURI(true)).toBe(true);
      expect(formatURI({})).toEqual({});
    });

    it('should use longest matching namespace for nested namespaces', () => {
      getValidationDetailsReport.mockResolvedValue({
        '@prefixes': {
          'base': 'http://example.org/',
          'ext': 'http://example.org/extended/'
        }
      });
      
      const { loadPrefixes, formatURI } = usePrefixes();
      
      // Need to reload with new prefixes
      vi.resetModules();
      const freshInstance = usePrefixes();
      
      return freshInstance.loadPrefixes().then(() => {
        const result = freshInstance.formatURI('http://example.org/extended/Class');
        expect(result).toBe('ext:Class');
      });
    });

    it('should handle URIs with fragments', () => {
      const { formatURI } = usePrefixes();
      
      expect(formatURI('http://example.org/Class#id123')).toBe('ex:Class#id123');
    });

    it('should handle URIs with query parameters', () => {
      const { formatURI } = usePrefixes();
      
      expect(formatURI('http://example.org/Person?id=1')).toBe('ex:Person?id=1');
    });

    it('should preserve case in local part', () => {
      const { formatURI } = usePrefixes();
      
      expect(formatURI('http://example.org/PersonClass')).toBe('ex:PersonClass');
      expect(formatURI('http://example.org/personClass')).toBe('ex:personClass');
    });
  });

  describe('formatURI without loaded prefixes', () => {
    it('should return original URI when prefixes are not loaded', () => {
      // Create new instance without loading prefixes
      vi.resetModules();
      const { formatURI } = usePrefixes();
      
      const uri = 'http://www.w3.org/ns/shacl#minCount';
      expect(formatURI(uri)).toBe(uri);
    });
  });

  describe('state management', () => {
    it('should expose loading state', async () => {
      getValidationDetailsReport.mockResolvedValue({
        '@prefixes': mockPrefixes
      });
      
      const { isLoadingPrefixes } = usePrefixes();
      
      expect(isLoadingPrefixes.value).toBe(false);
    });

    it('should expose error state', () => {
      const { prefixesError } = usePrefixes();
      
      expect(prefixesError.value).toBe(null);
    });

    it('should expose prefixes ref', () => {
      const { prefixes } = usePrefixes();
      
      expect(prefixes.value).toBeDefined();
    });
  });

  describe('edge cases', () => {
    it('should handle very long URIs', async () => {
      getValidationDetailsReport.mockResolvedValue({
        '@prefixes': mockPrefixes
      });
      
      const { loadPrefixes, formatURI } = usePrefixes();
      await loadPrefixes();
      
      const longPath = 'a'.repeat(1000);
      const uri = `http://example.org/${longPath}`;
      
      expect(formatURI(uri)).toBe(`ex:${longPath}`);
    });

    it('should handle special characters in URIs', async () => {
      getValidationDetailsReport.mockResolvedValue({
        '@prefixes': mockPrefixes
      });
      
      const { loadPrefixes, formatURI } = usePrefixes();
      await loadPrefixes();
      
      expect(formatURI('http://example.org/Class%20With%20Spaces')).toBe('ex:Class%20With%20Spaces');
      expect(formatURI('http://example.org/class-with-dashes')).toBe('ex:class-with-dashes');
      expect(formatURI('http://example.org/class_with_underscores')).toBe('ex:class_with_underscores');
    });

    it('should handle URIs ending with namespace exactly', async () => {
      getValidationDetailsReport.mockResolvedValue({
        '@prefixes': mockPrefixes
      });
      
      const { loadPrefixes, formatURI } = usePrefixes();
      await loadPrefixes();
      
      // URI that equals the namespace exactly
      expect(formatURI('http://example.org/')).toBe('ex:');
    });

    it('should handle empty prefixes object', async () => {
      getValidationDetailsReport.mockResolvedValue({
        '@prefixes': {}
      });
      
      const { loadPrefixes, formatURI } = usePrefixes();
      await loadPrefixes();
      
      const uri = 'http://example.org/Something';
      expect(formatURI(uri)).toBe(uri);
    });
  });

  describe('real-world usage patterns', () => {
    it('should format SHACL constraint URIs', async () => {
      getValidationDetailsReport.mockResolvedValue({
        '@prefixes': mockPrefixes
      });
      
      const { loadPrefixes, formatURI } = usePrefixes();
      await loadPrefixes();
      
      expect(formatURI('http://www.w3.org/ns/shacl#minCount')).toBe('sh:minCount');
      expect(formatURI('http://www.w3.org/ns/shacl#maxCount')).toBe('sh:maxCount');
      expect(formatURI('http://www.w3.org/ns/shacl#datatype')).toBe('sh:datatype');
    });

    it('should format RDF type URIs', async () => {
      getValidationDetailsReport.mockResolvedValue({
        '@prefixes': mockPrefixes
      });
      
      const { loadPrefixes, formatURI } = usePrefixes();
      await loadPrefixes();
      
      expect(formatURI('http://www.w3.org/1999/02/22-rdf-syntax-ns#type')).toBe('rdf:type');
    });

    it('should format custom domain URIs', async () => {
      getValidationDetailsReport.mockResolvedValue({
        '@prefixes': mockPrefixes
      });
      
      const { loadPrefixes, formatURI } = usePrefixes();
      await loadPrefixes();
      
      expect(formatURI('http://example.org/Person')).toBe('ex:Person');
      expect(formatURI('http://example.org/hasName')).toBe('ex:hasName');
    });
  });
});
