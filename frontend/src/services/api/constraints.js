/**
 * Constraints API Module
 * 
 * API endpoints for SHACL constraints.
 * Handles constraint counts, types, and statistics.
 * 
 * @module services/api/constraints
 */

import { apiRequest } from './base';

/**
 * Get constraint count for a node shape
 * @param {string} nodeShape - Node shape URI
 * @returns {Promise<{nodeShape: string, constraintCount: number}>}
 */
export async function getConstraintCountForNodeShape(nodeShape) {
  return apiRequest(`/shape_view/node-shape/constraints/count?node_shape=${encodeURIComponent(nodeShape)}`);
}

/**
 * Get constraints count for property shapes in a node shape
 * @param {string} nodeShapeName - Node shape name/URI
 * @returns {Promise<{nodeShape: string, propertyShapesConstraints: Array}>}
 */
export async function getConstraintsCountForPropertyShapes(nodeShapeName) {
  return apiRequest(`/shape_view/property-shapes/constraints/count?nodeshape_name=${encodeURIComponent(nodeShapeName)}`);
}
