/**
 * API Service Module (Legacy Entry Point)
 * 
 * This file maintains backward compatibility by re-exporting all functions
 * from the modular API structure in services/api/*.
 * 
 * New code should import directly from the modular structure:
 * - import { getViolationsCount } from '@/services/api/homepage'
 * - import { getPropertyShapesForNodeShape } from '@/services/api/shapes'
 * - import { getViolationsDistribution } from '@/services/api/violations'
 * - import { getConstraintCountForNodeShape } from '@/services/api/constraints'
 * 
 * @module services/api
 * @deprecated Use modular imports from services/api/* instead
 */

// Re-export everything from the modular API structure
export * from './api/index';
