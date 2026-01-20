/**
 * Pinia Stores Index
 * 
 * Central export point for all Pinia stores.
 * Allows for cleaner imports throughout the application.
 * 
 * @module stores
 * @example
 * import { useShapesStore, useViolationsStore } from '@/stores';
 */

export { useShapesStore } from './shapes';
export { useViolationsStore } from './violations';
export { useConstraintsStore } from './constraints';
