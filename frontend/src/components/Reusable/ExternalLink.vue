<!-- ExternalLink.vue -->
<template>
    <a
      :href="href"
      :aria-label="ariaLabel"
      target="_blank"
      rel="noopener noreferrer"
    >
      <slot></slot>
    </a>
  </template>
  
  <script setup>
/**
 * ExternalLink component
 *
 * Renders an anchor tag that safely opens links in a new tab.
 * Includes proper security attributes and accessibility features.
 *
 * @example
 * // Basic usage in a parent component template:
 * // <ExternalLink href="https://example.com" aria-label="Visit Example">
 * //   Example Website
 * // </ExternalLink>
 *
 * @prop {String} href - The URL to link to
 * @prop {String} ariaLabel - Accessible label describing the link
 *
 * @slots
 * - default - Content to display as the link text
 *
 * @dependencies
 * - vue (Composition API)
 *
 * @security
 * - Uses rel="noopener noreferrer" to prevent security vulnerabilities
 * - Opens in new tab with target="_blank" to preserve user context
 * 
 * @returns {HTMLElement} A standard anchor tag (<a>) that opens the specified URL in a new tab,
 * with security attributes and accessibility features properly configured, and displays the
 * slot content as the link text.
 */
  defineProps({
    href: {
      type: String,
      required: true,
    },
    ariaLabel: {
      type: String,
      required: true,
    },
  });
  </script>
