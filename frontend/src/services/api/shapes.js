/**
 * Shapes API Module
 * 
 * API endpoints for SHACL shapes (node shapes and property shapes).
 * Handles shape details, statistics, and relationships.
 * 
 * @module services/api/shapes
 */

import { apiRequest, validateParams, validateNumeric } from './base';

/**
 * Get property shapes for a specific node shape
 * @param {string} nodeShape - Node shape URI
 * @param {number} [limit] - Optional limit for pagination
 * @param {number} [offset] - Optional offset for pagination
 * @returns {Promise<{nodeShape: string, propertyShapes: Array<{PropertyShapeName: string, NumViolations: number, NumConstraints: number, MostViolatedConstraint: string}>}>}
 */
export async function getPropertyShapesForNodeShape(nodeShape, limit, offset) {
  validateParams({ nodeShape }, ['nodeShape']);
  validateNumeric({ limit, offset }, ['limit', 'offset']);
  
  let url = `/overview/node-shape/property-shapes?node_shape=${encodeURIComponent(nodeShape)}`;
  if (limit !== undefined) url += `&limit=${limit}`;
  if (offset !== undefined) url += `&offset=${offset}`;
  return apiRequest(url);
}

/**
 * Get total number of node shapes in shapes graph
 * @param {string} [graphUri] - Optional shapes graph URI
 * @returns {Promise<{nodeShapeCount: number}>}
 */
export async function getNodeShapesCountInGraph(graphUri) {
  const params = graphUri ? `?graph_uri=${encodeURIComponent(graphUri)}` : '';
  return apiRequest(`/overview/shapes/graph/count${params}`);
}

/**
 * Get number of node shapes with violations
 * @param {string} [shapesGraphUri] - Optional shapes graph URI
 * @param {string} [validationReportUri] - Optional validation report URI
 * @returns {Promise<{nodeShapesWithViolationsCount: number}>}
 */
export async function getNodeShapesWithViolationsCountOverview(shapesGraphUri, validationReportUri) {
  let url = '/overview/shapes/violations/count';
  const params = new URLSearchParams();
  if (shapesGraphUri) params.append('shapes_graph_uri', shapesGraphUri);
  if (validationReportUri) params.append('validation_report_uri', validationReportUri);
  const queryString = params.toString();
  return apiRequest(queryString ? `${url}?${queryString}` : url);
}

/**
 * Get correlation data between constraints and violations
 * @returns {Promise<Array<{violation_entropy: number, num_violations: number, num_constraints: number}>>}
 */
export async function getCorrelationData() {
  return apiRequest('/overview/correlation');
}

/**
 * Get node shape details table
 * @param {number} [limit] - Optional limit for pagination
 * @param {number} [offset] - Optional offset for pagination
 * @returns {Promise<{nodeShapes: Array}>}
 */
export async function getNodeShapeDetailsTable(limit, offset) {
  validateNumeric({ limit, offset }, ['limit', 'offset']);
  
  let url = '/overview/shapes/details';
  const params = new URLSearchParams();
  if (limit !== undefined) params.append('limit', limit);
  if (offset !== undefined) params.append('offset', offset);
  const queryString = params.toString();
  return apiRequest(queryString ? `${url}?${queryString}` : url);
}

/**
 * Get property path count for a node shape
 * @param {string} nodeShape - Node shape URI
 * @returns {Promise<{nodeShape: string, propertyPathCount: number}>}
 */
export async function getPropertyPathsCountForNodeShape(nodeShape) {
  validateParams({ nodeShape }, ['nodeShape']);
  return apiRequest(`/shape_view/node-shape/property-paths/count?node_shape=${encodeURIComponent(nodeShape)}`);
}

/**
 * Get shape definition from shapes graph
 * @param {string} nodeShape - Node shape URI
 * @returns {Promise<{nodeShape: string, definition: string}>}
 */
export async function getShapeDefinition(nodeShape) {
  validateParams({ nodeShape }, ['nodeShape']);
  return apiRequest('/overview/shapes/graph/details', {
    method: 'POST',
    body: JSON.stringify({ node_shape_names: [nodeShape] })
  });
}
