/**
 * Violations API Module
 * 
 * API endpoints for SHACL validation violations.
 * Handles violation distributions, details, and per-entity violations.
 * 
 * @module services/api/violations
 */

import { apiRequest } from './base';

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

/**
 * Get violation count for a specific node shape
 * @param {string} nodeShapeName - Node shape name/URI
 * @returns {Promise<{nodeShape: string, violationCount: number}>}
 */
export async function getViolationCountForNodeShape(nodeShapeName) {
  return apiRequest(`/shape_view/violations/node-shape/count?nodeshape_name=${encodeURIComponent(nodeShapeName)}`);
}

/**
 * Get count of violated focus nodes for a node shape
 * @param {string} nodeShape - Node shape URI
 * @returns {Promise<{nodeShape: string, violatedFocusNodesCount: number}>}
 */
export async function getViolatedFocusNodesCountForNodeShape(nodeShape) {
  return apiRequest(`/shape_view/violations/node-shape/focus-nodes/count?node_shape=${encodeURIComponent(nodeShape)}`);
}

/**
 * Get violations per constraint type for property shapes in a node shape
 * @param {string} nodeShape - Node shape URI
 * @returns {Promise<{nodeShape: string, propertyShapes: Array}>}
 */
export async function getViolationsPerConstraintTypeForPropertyShape(nodeShape) {
  return apiRequest(`/shape_view/violations/property-shapes/constraint-types?node_shape=${encodeURIComponent(nodeShape)}`);
}

/**
 * Get node shape with detailed violations for all property shapes
 * @param {string} nodeShape - Node shape URI
 * @param {number} [limitViolations] - Limit violations per property shape
 * @param {number} [offsetViolations] - Offset for violations
 * @returns {Promise<{nodeShape: string, propertyShapes: Array}>}
 */
export async function getNodeShapeWithViolations(nodeShape, limitViolations, offsetViolations) {
  let url = `/shape_view/node-shape/violations-detailed?node_shape=${encodeURIComponent(nodeShape)}`;
  if (limitViolations !== undefined) url += `&limit_violations=${limitViolations}`;
  if (offsetViolations !== undefined) url += `&offset_violations=${offsetViolations}`;
  return apiRequest(url);
}

/**
 * Get maximum violations for any node shape
 * @returns {Promise<{nodeShape: string, violationCount: number}>}
 */
export async function getMaxViolationsForNodeShape() {
  return apiRequest('/overview/violations/max');
}

/**
 * Get average violations across node shapes
 * @returns {Promise<{averageViolations: number}>}
 */
export async function getAverageViolationsForNodeShapes() {
  return apiRequest('/overview/violations/average');
}

/**
 * Get distribution of violations per constraint (histogram data)
 * @param {number} [numBins=10] - Number of bins for histogram
 * @returns {Promise<{labels: string[], datasets: Array}>}
 */
export async function getViolationsDistribution(numBins = 10) {
  return apiRequest(`/overview/violations-distribution?num_bins=${numBins}`);
}
