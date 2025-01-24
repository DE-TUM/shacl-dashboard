// utils.js

/**
 * Calculate the Shannon entropy for a set of violations.
 * @param {Object} violationCounts - An object where keys are violation types, and values are their counts.
 * @returns {number} Shannon entropy value.
 */
export function calculateShannonEntropy(violationCounts) {
    // Sum of all violations
    const total = Object.values(violationCounts).reduce((sum, count) => sum + count, 0);
  
    // If there are no violations, entropy is 0
    if (total === 0) {
      return 0;
    }
  
    // Calculate probabilities for each violation type
    const probabilities = Object.values(violationCounts).map((count) => count / total);
  
    // Calculate Shannon entropy
    const entropy = probabilities.reduce((entropySum, p) => {
      return p > 0 ? entropySum - p * Math.log2(p) : entropySum;
    }, 0);
  
    return entropy;
  }
  