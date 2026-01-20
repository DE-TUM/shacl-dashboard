/**
 * API Services Index
 * 
 * Central export point for all API modules.
 * Re-exports all functions from domain-specific modules to maintain
 * backward compatibility with existing imports.
 * 
 * @module services/api
 */

// Export base utilities
export { API_BASE_URL, apiRequest } from './base';

// Export homepage/dashboard endpoints
export {
  getViolationsCount,
  getNodeShapesWithViolationsCount,
  getNodeShapesCount,
  getPathsCountInGraph,
  getPathsWithViolationsCount,
  getFocusNodesCount,
  getMostViolatedNodeShape,
  getMostViolatedPath,
  getMostViolatedFocusNode,
  getMostFrequentConstraintComponent,
  getDistinctConstraintComponentsCount,
  getDistinctConstraintsCountInShapes,
  getValidationDetailsReport
} from './homepage';

// Export violations endpoints
export {
  getViolationsDistributionPerShape,
  getViolationsDistributionPerPath,
  getViolationsDistributionPerFocusNode,
  getViolationsDistributionPerConstraintComponent,
  getViolationsPerNodeShape,
  getViolationsPerPath,
  getViolationsPerFocusNode,
  getViolationCountForNodeShape,
  getViolatedFocusNodesCountForNodeShape,
  getViolationsPerConstraintTypeForPropertyShape,
  getNodeShapeWithViolations,
  getMaxViolationsForNodeShape,
  getAverageViolationsForNodeShapes,
  getViolationsDistribution
} from './violations';

// Export shapes endpoints
export {
  getPropertyShapesForNodeShape,
  getNodeShapesCountInGraph,
  getNodeShapesWithViolationsCountOverview,
  getCorrelationData,
  getNodeShapeDetailsTable,
  getPropertyPathsCountForNodeShape,
  getShapeDefinition
} from './shapes';

// Export constraints endpoints
export {
  getConstraintCountForNodeShape,
  getConstraintsCountForPropertyShapes
} from './constraints';
