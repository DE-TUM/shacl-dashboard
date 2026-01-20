/**
 * Homepage API Module
 * 
 * API endpoints for the homepage/dashboard overview.
 * Provides aggregated statistics, counts, and distributions.
 * 
 * @module services/api/homepage
 */

import { apiRequest } from './base';

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
 * Get detailed validation report with violations
 * @param {number} [limit=10] - Maximum number of violations to return
 * @param {number} [offset=0] - Offset for pagination
 * @returns {Promise<Object>} Detailed validation report
 */
export async function getValidationDetailsReport(limit = 10, offset = 0) {
  return apiRequest(`/homepage/validation-details?limit=${limit}&offset=${offset}`);
}
