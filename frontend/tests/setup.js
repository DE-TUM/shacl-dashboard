import { config } from '@vue/test-utils';

// Mock global properties if needed
config.global.mocks = {
  $t: (key) => key, // Mock i18n if you use it
};

// Suppress Vue warnings during tests
config.global.config.warnHandler = () => null;
