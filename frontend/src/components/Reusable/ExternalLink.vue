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
  