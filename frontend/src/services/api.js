/**
 * API Service Module
 * 
 * Centralized API communication layer for the SHACL Dashboard frontend.
 * Handles all HTTP requests to the Flask backend API endpoints.
 * 
 * Base URL Configuration:
 * - Development: Defaults to http://localhost:80 (Flask backend)
 * - Production: Uses window.location.origin (same server)
 * 
 * @module services/api
 */

// Configure API base URL based on environment
const API_BASE_URL = import.meta.env.PROD 
  ? window.location.origin 
  : 'http://localhost:80';

/**
 * Generic API request handler with error handling
 * @param {string} endpoint - API endpoint path
 * @param {Object} options - Fetch options
 * @returns {Promise<any>} JSON response data
 * @throws {Error} API error with details
 */
async function apiRequest(endpoint, options = {}) {
  try {
    const response = await fetch(`${API_BASE_URL}${endpoint}`, {
      headers: {
        'Content-Type': 'application/json',
        ...options.headers,
      },
      ...options,
    });

    if (!response.ok) {
      const errorData = await response.json().catch(() => ({}));
      throw new Error(errorData.error || `API request failed: ${response.status}`);
    }

    return await response.json();
  } catch (error) {
    console.error(`API Error [${endpoint}]:`, error);
    throw error;
  }
}

// ============================================================================
// Homepage API Endpoints
// ============================================================================

/**
 * Get total number of violations in validation report
 * @param {string} [graphUri] - Optional validation report URI
 * @returns {Promise<{violationCount: number}>}
 */
export async function getViolationsCount(graphUri) {
  const params = graphUri ? `?graph_uri=${encodeURIComponent(graphUri)}` : '';
  return apiRequest(`/homepage/violations/report/count${params}`);
}

/**
 * Get number of node shapes with violations
 * @returns {Promise<{nodeShapesWithViolationsCount: number}>}
 */
export async function getNodeShapesWithViolationsCount() {
  return apiRequest('/homepage/shapes/violations/count');
}

/**
 * Get total number of node shapes in shapes graph
 * @returns {Promise<{nodeShapeCount: number}>}
 */
export async function getNodeShapesCount() {
  return apiRequest('/homepage/nodeshapes/count');
}

/**
 * Get number of unique paths in shapes graph
 * @returns {Promise<{uniquePathsCount: number}>}
 */
export async function getPathsCountInGraph() {
  return apiRequest('/homepage/shapes/graph/paths/count');
}

/**
 * Get number of paths with violations
 * @returns {Promise<{pathsWithViolationsCount: number}>}
 */
export async function getPathsWithViolationsCount() {
  return apiRequest('/homepage/validation-report/paths/violations/count');
}

/**
 * Get number of focus nodes in validation report
 * @returns {Promise<{focusNodesCount: number}>}
 */
export async function getFocusNodesCount() {
  return apiRequest('/homepage/validation-report/focus-nodes/count');
}

/**
 * Get most violated node shape
 * @returns {Promise<{nodeShape: string, violations: number}>}
 */
export async function getMostViolatedNodeShape() {
  return apiRequest('/homepage/violations/most-violated-node-shape');
}

/**
 * Get most violated path
 * @returns {Promise<{path: string, violations: number}>}
 */
export async function getMostViolatedPath() {
  return apiRequest('/homepage/violations/most-violated-path');
}

/**
 * Get most violated focus node
 * @returns {Promise<{focusNode: string, violations: number}>}
 */
export async function getMostViolatedFocusNode() {
  return apiRequest('/homepage/violations/most-violated-focus-node');
}

/**
 * Get most frequent constraint component
 * @returns {Promise<{constraintComponent: string, occurrences: number}>}
 */
export async function getMostFrequentConstraintComponent() {
  return apiRequest('/homepage/violations/most-frequent-constraint-component');
}

/**
 * Get count of distinct constraint components
 * @returns {Promise<{distinctConstraintComponentCount: number}>}
 */
export async function getDistinctConstraintComponentsCount() {
  return apiRequest('/homepage/violations/distinct-constraint-components/count');
}

/**
 * Get count of distinct constraints in shapes graph
 * @returns {Promise<{distinctConstraintsCount: number}>}
 */
export async function getDistinctConstraintsCountInShapes() {
  return apiRequest('/homepage/shapes/distinct-constraints/count');
}

/**
 * Get distribution of violations per node shape (histogram data)
 * @returns {Promise<{labels: string[], datasets: Array}>}
 */
export async function getViolationsDistributionPerShape() {
  return apiRequest('/homepage/violations/distribution/shape');
}

/**
 * Get distribution of violations per path (histogram data)
 * @returns {Promise<{labels: string[], datasets: Array}>}
 */
export async function getViolationsDistributionPerPath() {
  return apiRequest('/homepage/violations/distribution/path');
}

/**
 * Get distribution of violations per focus node (histogram data)
 * @returns {Promise<{labels: string[], datasets: Array}>}
 */
export async function getViolationsDistributionPerFocusNode() {
  return apiRequest('/homepage/violations/distribution/focus-node');
}

/**
 * Get distribution of violations per constraint component (histogram data)
 * @returns {Promise<{labels: string[], datasets: Array}>}
 */
export async function getViolationsDistributionPerConstraintComponent() {
  return apiRequest('/homepage/violations/distribution-per-constraint-component');
}

/**
 * Get detailed validation report with violations
 * @param {number} [limit=10] - Maximum number of violations to return
 * @param {number} [offset=0] - Offset for pagination
 * @returns {Promise<Object>} Detailed validation report
 */
export async function getValidationDetailsReport(limit = 10, offset = 0) {
  return apiRequest(`/homepage/validation-details?limit=${limit}&offset=${offset}`);
}

/**
 * Get violations per node shape (list)
 * @returns {Promise<{violationsPerNodeShape: Array<{NodeShapeName: string, NumViolations: number}>}>}
 */
export async function getViolationsPerNodeShape() {
  return apiRequest('/homepage/shapes/violations');
}

/**
 * Get violations per path (list)
 * @returns {Promise<{violationsPerPath: Array<{PathName: string, NumViolations: number}>}>}
 */
export async function getViolationsPerPath() {
  return apiRequest('/homepage/validation-report/paths/violations');
}

/**
 * Get violations per focus node (list)
 * @returns {Promise<{violationsPerFocusNode: Array<{FocusNodeName: string, NumViolations: number}>}>}
 */
export async function getViolationsPerFocusNode() {
  return apiRequest('/homepage/validation-report/focus-nodes/violations');
}
