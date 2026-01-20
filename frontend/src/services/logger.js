/**
 * Logging Service
 * 
 * Provides environment-based logging with different log levels.
 * In production, only errors are logged. In development, all levels are logged.
 * 
 * @module logger
 */

const LOG_LEVELS = {
  DEBUG: 0,
  INFO: 1,
  WARN: 2,
  ERROR: 3,
  NONE: 4
};

// Set log level based on environment
const currentLogLevel = import.meta.env.MODE === 'production' 
  ? LOG_LEVELS.ERROR 
  : LOG_LEVELS.DEBUG;

/**
 * Internal logging function
 * @param {number} level - Log level
 * @param {string} method - Console method to use
 * @param {...any} args - Arguments to log
 */
function log(level, method, ...args) {
  if (level >= currentLogLevel) {
    console[method](...args);
  }
}

/**
 * Logger instance with different log levels
 */
export const logger = {
  /**
   * Log debug information (development only)
   * @param {...any} args - Arguments to log
   */
  debug(...args) {
    log(LOG_LEVELS.DEBUG, 'debug', '[DEBUG]', ...args);
  },

  /**
   * Log informational messages
   * @param {...any} args - Arguments to log
   */
  info(...args) {
    log(LOG_LEVELS.INFO, 'info', '[INFO]', ...args);
  },

  /**
   * Log warnings
   * @param {...any} args - Arguments to log
   */
  warn(...args) {
    log(LOG_LEVELS.WARN, 'warn', '[WARN]', ...args);
  },

  /**
   * Log errors
   * @param {...any} args - Arguments to log
   */
  error(...args) {
    log(LOG_LEVELS.ERROR, 'error', '[ERROR]', ...args);
  },

  /**
   * Log API errors with structured format
   * @param {string} endpoint - API endpoint that failed
   * @param {Error} error - Error object
   */
  apiError(endpoint, error) {
    this.error(`API Error [${endpoint}]:`, error.message || error);
  }
};

export default logger;
