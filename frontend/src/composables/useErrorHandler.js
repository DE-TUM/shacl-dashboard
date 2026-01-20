/**
 * Error Handling Composable
 * 
 * Provides standardized error handling with user-facing feedback.
 * Ensures that API errors and other failures are communicated to users
 * instead of failing silently or only logging to console.
 * 
 * @module composables/useErrorHandler
 */

import { ref } from 'vue';
import { logger } from '@/services/logger';

/**
 * Error severity levels
 */
export const ERROR_SEVERITY = {
  INFO: 'info',
  WARNING: 'warning',
  ERROR: 'error',
  CRITICAL: 'critical'
};

/**
 * User-friendly error messages for common scenarios
 */
const ERROR_MESSAGES = {
  NETWORK: 'Unable to connect to the server. Please check your internet connection.',
  TIMEOUT: 'The request took too long to complete. Please try again.',
  NOT_FOUND: 'The requested data could not be found.',
  UNAUTHORIZED: 'You do not have permission to access this resource.',
  SERVER_ERROR: 'An unexpected server error occurred. Please try again later.',
  VALIDATION: 'The provided data is invalid. Please check your input.',
  UNKNOWN: 'An unexpected error occurred. Please try again.'
};

/**
 * Composable for error handling with user feedback
 * 
 * @returns {Object} Error handling utilities
 */
export function useErrorHandler() {
  const error = ref(null);
  const errorMessage = ref('');
  const errorSeverity = ref(ERROR_SEVERITY.ERROR);
  const showError = ref(false);

  /**
   * Parse error and generate user-friendly message
   * @param {Error|string} err - Error object or message
   * @returns {string} User-friendly error message
   */
  function parseErrorMessage(err) {
    if (typeof err === 'string') {
      return err;
    }

    if (err.message) {
      // Check for common error patterns
      if (err.message.includes('fetch') || err.message.includes('network')) {
        return ERROR_MESSAGES.NETWORK;
      }
      if (err.message.includes('timeout')) {
        return ERROR_MESSAGES.TIMEOUT;
      }
      if (err.message.includes('404') || err.message.includes('not found')) {
        return ERROR_MESSAGES.NOT_FOUND;
      }
      if (err.message.includes('401') || err.message.includes('403')) {
        return ERROR_MESSAGES.UNAUTHORIZED;
      }
      if (err.message.includes('500') || err.message.includes('502') || err.message.includes('503')) {
        return ERROR_MESSAGES.SERVER_ERROR;
      }
      if (err.message.includes('400') || err.message.includes('validation')) {
        return ERROR_MESSAGES.VALIDATION;
      }

      // Return the actual error message if it seems user-friendly
      if (err.message.length < 200 && !err.message.includes('stack')) {
        return err.message;
      }
    }

    return ERROR_MESSAGES.UNKNOWN;
  }

  /**
   * Handle error with user feedback and logging
   * @param {Error|string} err - Error to handle
   * @param {Object} options - Error handling options
   * @param {string} options.context - Context where error occurred
   * @param {string} options.severity - Error severity level
   * @param {string} options.customMessage - Custom user message
   * @param {boolean} options.silent - If true, don't show UI notification
   */
  function handleError(err, options = {}) {
    const {
      context = 'Application',
      severity = ERROR_SEVERITY.ERROR,
      customMessage = null,
      silent = false
    } = options;

    error.value = err;
    errorSeverity.value = severity;
    errorMessage.value = customMessage || parseErrorMessage(err);

    // Log error for debugging
    logger.error(`[${context}] ${errorMessage.value}`, err);

    // Show UI notification unless silent mode
    if (!silent) {
      showError.value = true;

      // Auto-dismiss after 5 seconds for non-critical errors
      if (severity !== ERROR_SEVERITY.CRITICAL) {
        setTimeout(() => {
          clearError();
        }, 5000);
      }
    }

    return errorMessage.value;
  }

  /**
   * Clear current error state
   */
  function clearError() {
    error.value = null;
    errorMessage.value = '';
    showError.value = false;
  }

  /**
   * Wrap an async function with error handling
   * @param {Function} fn - Async function to wrap
   * @param {Object} options - Error handling options
   * @returns {Function} Wrapped function
   */
  function withErrorHandling(fn, options = {}) {
    return async (...args) => {
      try {
        return await fn(...args);
      } catch (err) {
        handleError(err, options);
        throw err; // Re-throw so caller can handle if needed
      }
    };
  }

  /**
   * Execute async function with error handling
   * @param {Function} fn - Async function to execute
   * @param {Object} options - Error handling options
   * @returns {Promise} Result of function execution
   */
  async function tryAsync(fn, options = {}) {
    try {
      clearError();
      return await fn();
    } catch (err) {
      handleError(err, options);
      return null; // Return null on error
    }
  }

  return {
    // State
    error,
    errorMessage,
    errorSeverity,
    showError,

    // Methods
    handleError,
    clearError,
    withErrorHandling,
    tryAsync,

    // Constants
    ERROR_SEVERITY,
    ERROR_MESSAGES
  };
}
