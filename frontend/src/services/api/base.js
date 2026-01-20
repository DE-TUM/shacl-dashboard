/**
 * Base API Module
 * 
 * Provides core API functionality including base URL configuration
 * and the generic request handler used by all API modules.
 * 
 * @module services/api/base
 */

import { logger } from '../logger';

// Configure API base URL based on environment
export const API_BASE_URL = import.meta.env.PROD 
  ? `${window.location.origin}/api/v1`
  : 'http://localhost:80/api/v1';

/**
 * Validate required parameters
 * @param {Object} params - Parameters to validate
 * @param {Array<string>} requiredFields - List of required field names
 * @throws {Error} If validation fails
 */
export function validateParams(params, requiredFields) {
  for (const field of requiredFields) {
    const value = params[field];
    
    if (value === null || value === undefined) {
      throw new Error(`Missing required parameter: ${field}`);
    }
    
    if (typeof value === 'string' && value.trim() === '') {
      throw new Error(`Parameter '${field}' cannot be empty`);
    }
    
    if (typeof value === 'number' && (isNaN(value) || !isFinite(value))) {
      throw new Error(`Parameter '${field}' must be a valid number`);
    }
  }
}

/**
 * Validate numeric parameters
 * @param {Object} params - Parameters to validate
 * @param {Array<string>} numericFields - List of numeric field names
 * @throws {Error} If validation fails
 */
export function validateNumeric(params, numericFields) {
  for (const field of numericFields) {
    const value = params[field];
    
    if (value !== undefined && value !== null) {
      const num = Number(value);
      if (isNaN(num) || !isFinite(num)) {
        throw new Error(`Parameter '${field}' must be a valid number`);
      }
      if (num < 0) {
        throw new Error(`Parameter '${field}' must be non-negative`);
      }
    }
  }
}

/**
 * Generic API request handler with error handling
 * @param {string} endpoint - API endpoint path
 * @param {Object} options - Fetch options
 * @returns {Promise<any>} JSON response data
 * @throws {Error} API error with details
 */
export async function apiRequest(endpoint, options = {}) {
  // Validate endpoint
  if (!endpoint || typeof endpoint !== 'string') {
    throw new Error('Invalid API endpoint');
  }
  
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
    logger.apiError(endpoint, error);
    throw error;
  }
}
