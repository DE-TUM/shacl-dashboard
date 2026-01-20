/**
 * Composable for managing URI prefixes with caching
 * 
 * Fetches SHACL validation prefixes once and caches them for reuse across all components.
 * Provides utility functions for formatting URIs using the cached prefixes.
 * 
 * @module composables/usePrefixes
 * 
 * @example
 * // In a Vue component:
 * import { usePrefixes } from '@/composables/usePrefixes.js';
 * 
 * const { loadPrefixes, formatURI, prefixes } = usePrefixes();
 * 
 * // Load prefixes once (usually in onMounted or on app startup)
 * await loadPrefixes();
 * 
 * // Format URIs using cached prefixes
 * const formattedUri = formatURI('http://example.org/schema#Person');
 * // Returns: "ex:Person" (if ex prefix is defined)
 * 
 * @returns {Object} Composable object with:
 *   - prefixes: Ref<Object> - Cached prefixes object
 *   - isLoadingPrefixes: Ref<boolean> - Loading state
 *   - prefixesError: Ref<Error|null> - Error state
 *   - loadPrefixes: Function - Loads prefixes from API (with caching)
 *   - formatURI: Function - Formats a URI using cached prefixes
 */
import { ref } from 'vue';
import { getValidationDetailsReport } from '../services/api.js';
import { logger } from '@/services/logger';

// Singleton cache - shared across all component instances
const prefixesCache = ref(null);
const isLoading = ref(false);
const loadError = ref(null);

/**
 * Composable for managing URI prefixes with caching
 * Fetches prefixes once and reuses them across all components
 * 
 * @returns {Object} Prefixes management object
 */
export function usePrefixes() {
  /**
   * Format a URI using cached prefixes
   * Finds the longest matching namespace and replaces it with the prefix notation.
   * 
   * @param {string} uri - Full URI to format
   * @returns {string} Formatted URI with prefix (e.g., "ex:Person") or original URI if no match
   * 
   * @example
   * formatURI('http://www.w3.org/ns/shacl#minCount') // Returns: "sh:minCount"
   * formatURI('http://example.org/Person') // Returns: "ex:Person"
   * formatURI('notAUri') // Returns: "notAUri"
   */
  const formatURI = (uri) => {
    if (!uri || typeof uri !== "string" || !prefixesCache.value) return uri;

    let matchedPrefix = null;
    let matchedNamespace = null;

    // Find the longest matching namespace (for nested namespaces)
    for (const [prefix, namespace] of Object.entries(prefixesCache.value)) {
      if (uri.startsWith(namespace) && (!matchedNamespace || namespace.length > matchedNamespace.length)) {
        matchedPrefix = prefix;
        matchedNamespace = namespace;
      }
    }

    if (matchedPrefix) {
      return `${matchedPrefix}:${uri.slice(matchedNamespace.length)}`;
    }

    return uri;
  };

  /**
   * Load prefixes from API (only once, then cached)
   * Implements singleton pattern to avoid redundant API calls.
   * If already loaded, returns cached value immediately.
   * If currently loading, waits for the loading to complete.
   * 
   * @returns {Promise<Object>} Prefixes object (e.g., { "sh": "http://www.w3.org/ns/shacl#", ... })
   * 
   * @example
   * const prefixes = await loadPrefixes();
   * console.log(prefixes); // { "sh": "http://www.w3.org/ns/shacl#", "ex": "http://example.org/" }
   */
  const loadPrefixes = async () => {
    // Return cached prefixes if already loaded
    if (prefixesCache.value) {
      return prefixesCache.value;
    }

    // If already loading, wait for it to complete
    if (isLoading.value) {
      return new Promise((resolve) => {
        const checkLoaded = setInterval(() => {
          if (!isLoading.value) {
            clearInterval(checkLoaded);
            resolve(prefixesCache.value);
          }
        }, 50);
      });
    }

    isLoading.value = true;
    loadError.value = null;

    try {
      // Fetch validation details (only need 1 record to get prefixes)
      const prefixData = await getValidationDetailsReport(1, 0);
      prefixesCache.value = prefixData["@prefixes"] || {};
      return prefixesCache.value;
    } catch (error) {
      loadError.value = error;
      logger.error('Failed to load prefixes:', error);
      prefixesCache.value = {}; // Set empty object as fallback
      return {};
    } finally {
      isLoading.value = false;
    }
  };

  return {
    prefixes: prefixesCache,
    isLoadingPrefixes: isLoading,
    prefixesError: loadError,
    loadPrefixes,
    formatURI,
  };
}
