<template>
  <Transition name="slide-down">
    <div
      v-if="show"
      class="error-notification"
      :class="[`severity-${severity}`]"
      role="alert"
      aria-live="assertive"
    >
      <div class="error-content">
        <div class="error-icon">
          <svg
            v-if="severity === 'error' || severity === 'critical'"
            xmlns="http://www.w3.org/2000/svg"
            viewBox="0 0 20 20"
            fill="currentColor"
            class="icon"
          >
            <path
              fill-rule="evenodd"
              d="M10 18a8 8 0 100-16 8 8 0 000 16zM8.707 7.293a1 1 0 00-1.414 1.414L8.586 10l-1.293 1.293a1 1 0 101.414 1.414L10 11.414l1.293 1.293a1 1 0 001.414-1.414L11.414 10l1.293-1.293a1 1 0 00-1.414-1.414L10 8.586 8.707 7.293z"
              clip-rule="evenodd"
            />
          </svg>
          <svg
            v-else-if="severity === 'warning'"
            xmlns="http://www.w3.org/2000/svg"
            viewBox="0 0 20 20"
            fill="currentColor"
            class="icon"
          >
            <path
              fill-rule="evenodd"
              d="M8.257 3.099c.765-1.36 2.722-1.36 3.486 0l5.58 9.92c.75 1.334-.213 2.98-1.742 2.98H4.42c-1.53 0-2.493-1.646-1.743-2.98l5.58-9.92zM11 13a1 1 0 11-2 0 1 1 0 012 0zm-1-8a1 1 0 00-1 1v3a1 1 0 002 0V6a1 1 0 00-1-1z"
              clip-rule="evenodd"
            />
          </svg>
          <svg
            v-else
            xmlns="http://www.w3.org/2000/svg"
            viewBox="0 0 20 20"
            fill="currentColor"
            class="icon"
          >
            <path
              fill-rule="evenodd"
              d="M18 10a8 8 0 11-16 0 8 8 0 0116 0zm-7-4a1 1 0 11-2 0 1 1 0 012 0zM9 9a1 1 0 000 2v3a1 1 0 001 1h1a1 1 0 100-2v-3a1 1 0 00-1-1H9z"
              clip-rule="evenodd"
            />
          </svg>
        </div>
        <div class="error-message">
          <p class="error-title">{{ title }}</p>
          <p class="error-description">{{ message }}</p>
        </div>
        <button
          class="error-close"
          @click="$emit('close')"
          aria-label="Close notification"
        >
          <svg
            xmlns="http://www.w3.org/2000/svg"
            viewBox="0 0 20 20"
            fill="currentColor"
            class="icon-close"
          >
            <path
              fill-rule="evenodd"
              d="M4.293 4.293a1 1 0 011.414 0L10 8.586l4.293-4.293a1 1 0 111.414 1.414L11.414 10l4.293 4.293a1 1 0 01-1.414 1.414L10 11.414l-4.293 4.293a1 1 0 01-1.414-1.414L8.586 10 4.293 5.707a1 1 0 010-1.414z"
              clip-rule="evenodd"
            />
          </svg>
        </button>
      </div>
    </div>
  </Transition>
</template>

<script setup>
/**
 * ErrorNotification Component
 * 
 * Global error notification component that displays user-facing error messages.
 * Supports different severity levels with appropriate styling and icons.
 * 
 * @component
 */
import { computed } from 'vue';

const props = defineProps({
  show: {
    type: Boolean,
    default: false
  },
  message: {
    type: String,
    required: true
  },
  severity: {
    type: String,
    default: 'error',
    validator: (value) => ['info', 'warning', 'error', 'critical'].includes(value)
  }
});

defineEmits(['close']);

const title = computed(() => {
  switch (props.severity) {
    case 'critical':
      return 'Critical Error';
    case 'error':
      return 'Error';
    case 'warning':
      return 'Warning';
    case 'info':
      return 'Information';
    default:
      return 'Notification';
  }
});
</script>

<style scoped>
.error-notification {
  position: fixed;
  top: 20px;
  right: 20px;
  z-index: 9999;
  max-width: 500px;
  min-width: 320px;
  background: white;
  border-radius: 8px;
  box-shadow: 0 10px 25px rgba(0, 0, 0, 0.1);
  overflow: hidden;
}

.error-content {
  display: flex;
  align-items: flex-start;
  padding: 16px;
  gap: 12px;
}

.error-icon {
  flex-shrink: 0;
}

.icon {
  width: 24px;
  height: 24px;
}

.error-message {
  flex: 1;
  min-width: 0;
}

.error-title {
  font-weight: 600;
  font-size: 14px;
  margin: 0 0 4px 0;
}

.error-description {
  font-size: 14px;
  margin: 0;
  line-height: 1.5;
}

.error-close {
  flex-shrink: 0;
  background: none;
  border: none;
  cursor: pointer;
  padding: 4px;
  border-radius: 4px;
  transition: background-color 0.2s;
}

.error-close:hover {
  background-color: rgba(0, 0, 0, 0.05);
}

.icon-close {
  width: 20px;
  height: 20px;
}

/* Severity-specific styles */
.severity-info {
  border-left: 4px solid var(--color-info, #3b82f6);
}

.severity-info .error-icon,
.severity-info .error-title {
  color: var(--color-info, #3b82f6);
}

.severity-warning {
  border-left: 4px solid var(--color-warning, #f59e0b);
}

.severity-warning .error-icon,
.severity-warning .error-title {
  color: var(--color-warning, #f59e0b);
}

.severity-error {
  border-left: 4px solid var(--color-error, #ef4444);
}

.severity-error .error-icon,
.severity-error .error-title {
  color: var(--color-error, #ef4444);
}

.severity-critical {
  border-left: 4px solid #dc2626;
  background-color: #fef2f2;
}

.severity-critical .error-icon,
.severity-critical .error-title {
  color: #dc2626;
}

/* Transitions */
.slide-down-enter-active,
.slide-down-leave-active {
  transition: all 0.3s ease;
}

.slide-down-enter-from {
  transform: translateY(-100%);
  opacity: 0;
}

.slide-down-leave-to {
  transform: translateY(-20px);
  opacity: 0;
}

@media (max-width: 640px) {
  .error-notification {
    left: 20px;
    right: 20px;
    max-width: none;
  }
}
</style>
