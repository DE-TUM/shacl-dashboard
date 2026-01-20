/**
 * Data Export Composable
 * 
 * Reusable data export functionality for generating and downloading CSV files.
 * Handles proper CSV formatting including escaping special characters.
 * 
 * @module useDataExport
 * @example
 * import { useDataExport } from '@/composables/useDataExport';
 * 
 * const { downloadCSV, downloadJSON } = useDataExport();
 * 
 * // Export table data
 * downloadCSV(tableData.value, 'MyReport.csv');
 */

import { logger } from '@/services/logger';
import { EXPORT } from '@/utils/constants';

/**
 * Create data export functionality
 * 
 * @returns {Object} Export methods
 */
export function useDataExport() {
  /**
   * Escape and format a value for CSV
   * @param {*} value - Value to format
   * @returns {string} Formatted CSV value
   */
  const formatCSVValue = (value) => {
    if (value === null || value === undefined) {
      return '';
    }
    
    if (typeof value === 'string') {
      // Escape double quotes by doubling them and wrap in quotes
      return `"${value.replace(/"/g, '""')}"`;
    }
    
    if (Array.isArray(value)) {
      // Join array values with semicolon
      return `"${value.join(EXPORT.CSV_ARRAY_SEPARATOR)}"`;
    }
    
    if (typeof value === 'object') {
      // Convert objects to JSON string
      return `"${JSON.stringify(value).replace(/"/g, '""')}"`;
    }
    
    return value;
  };

  /**
   * Convert array of objects to CSV string
   * @param {Array<Object>} data - Array of objects to convert
   * @returns {string} CSV formatted string
   */
  const dataToCSV = (data) => {
    if (!data || !data.length) {
      throw new Error('No data to export');
    }

    // Extract headers from first object
    const headers = Object.keys(data[0]).join(',');
    
    // Convert each row
    const rows = data.map((row) =>
      Object.values(row)
        .map(formatCSVValue)
        .join(',')
    );

    return [headers, ...rows].join('\n');
  };

  /**
   * Download data as CSV file
   * @param {Array<Object>} data - Array of objects to export
   * @param {string} [filename=EXPORT.DEFAULT_CSV_FILENAME] - Name of the file to download
   * @param {Object} [options] - Additional options
   * @param {boolean} [options.showAlert=true] - Show alert on success/failure
   * @returns {boolean} Success status
   */
  const downloadCSV = (data, filename = EXPORT.DEFAULT_CSV_FILENAME, options = {}) => {
    const { showAlert = true } = options;

    if (!data || !data.length) {
      if (showAlert) alert('No data available to export.');
      logger.warn('Attempted to export empty data');
      return false;
    }

    try {
      const csvContent = dataToCSV(data);
      const blob = new Blob([csvContent], { type: 'text/csv;charset=utf-8;' });
      const link = document.createElement('a');
      const url = URL.createObjectURL(blob);

      link.setAttribute('href', url);
      link.setAttribute('download', filename);
      link.style.visibility = 'hidden';

      document.body.appendChild(link);
      link.click();
      document.body.removeChild(link);

      // Clean up the URL object
      URL.revokeObjectURL(url);

      logger.info(`CSV exported successfully: ${filename}`);
      return true;
    } catch (error) {
      logger.error('Error generating CSV file:', error);
      if (showAlert) alert('Failed to generate CSV file.');
      return false;
    }
  };

  /**
   * Download data as JSON file
   * @param {*} data - Data to export (any JSON-serializable data)
   * @param {string} [filename=EXPORT.DEFAULT_JSON_FILENAME] - Name of the file to download
   * @param {Object} [options] - Additional options
   * @param {boolean} [options.showAlert=true] - Show alert on failure
   * @param {number} [options.indent=2] - JSON indentation
   * @returns {boolean} Success status
   */
  const downloadJSON = (data, filename = EXPORT.DEFAULT_JSON_FILENAME, options = {}) => {
    const { showAlert = true, indent = 2 } = options;

    if (!data) {
      if (showAlert) alert('No data available to export.');
      logger.warn('Attempted to export null/undefined data');
      return false;
    }

    try {
      const jsonContent = JSON.stringify(data, null, indent);
      const blob = new Blob([jsonContent], { type: 'application/json;charset=utf-8;' });
      const link = document.createElement('a');
      const url = URL.createObjectURL(blob);

      link.setAttribute('href', url);
      link.setAttribute('download', filename);
      link.style.visibility = 'hidden';

      document.body.appendChild(link);
      link.click();
      document.body.removeChild(link);

      // Clean up the URL object
      URL.revokeObjectURL(url);

      logger.info(`JSON exported successfully: ${filename}`);
      return true;
    } catch (error) {
      logger.error('Error generating JSON file:', error);
      if (showAlert) alert('Failed to generate JSON file.');
      return false;
    }
  };

  /**
   * Copy data to clipboard as CSV
   * @param {Array<Object>} data - Array of objects to copy
   * @returns {Promise<boolean>} Success status
   */
  const copyToClipboard = async (data) => {
    if (!data || !data.length) {
      logger.warn('No data to copy to clipboard');
      return false;
    }

    try {
      const csvContent = dataToCSV(data);
      await navigator.clipboard.writeText(csvContent);
      logger.info('Data copied to clipboard');
      return true;
    } catch (error) {
      logger.error('Error copying to clipboard:', error);
      return false;
    }
  };

  return {
    downloadCSV,
    downloadJSON,
    copyToClipboard,
    formatCSVValue,
    dataToCSV
  };
}

export default useDataExport;
