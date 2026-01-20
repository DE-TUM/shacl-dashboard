# Frontend Tests

This directory contains unit tests for the SHACL Dashboard frontend application.

## Running Tests

```bash
# Run all tests
npm run test

# Run tests in watch mode (recommended for development)
npm run test -- --watch

# Run tests with UI
npm run test:ui

# Run tests with coverage report
npm run test:coverage
```

## Test Structure

```
tests/
├── setup.js                    # Test configuration and global setup
├── composables/               # Tests for Vue composables
│   ├── usePagination.test.js
│   ├── useTableFilters.test.js
│   ├── useDataExport.test.js
│   ├── useSorting.test.js
│   └── usePrefixes.test.js
├── components/                # Tests for Vue components (to be added)
└── stores/                    # Tests for Pinia stores (to be added)
```

## Testing Guidelines

### Composables

All composables in `src/composables/` should have corresponding test files:

- Test all public methods and computed properties
- Test edge cases (null, undefined, empty arrays)
- Test reactivity (data changes should update computed values)
- Test error handling
- Aim for >70% code coverage

### Components

Component tests should cover:

- Rendering with different props
- User interactions (clicks, inputs)
- Emitted events
- Conditional rendering
- Integration with composables and stores

### Stores

Store tests should verify:

- Initial state
- Mutations/actions
- Getters
- API integration (with mocked API calls)
- Error states

## Writing Tests

### Example Test Structure

```javascript
import { describe, it, expect, beforeEach } from 'vitest';
import { ref } from 'vue';
import { useMyComposable } from '@/composables/useMyComposable';

describe('useMyComposable', () => {
  let testData;

  beforeEach(() => {
    // Setup test data
    testData = ref([...]);
  });

  describe('feature group', () => {
    it('should do something specific', () => {
      const { result } = useMyComposable(testData);
      
      expect(result.value).toBe(expectedValue);
    });
  });
});
```

### Best Practices

1. **Descriptive test names**: Use clear, descriptive names that explain what is being tested
2. **Arrange-Act-Assert**: Structure tests with clear setup, execution, and assertion phases
3. **Test behavior, not implementation**: Focus on what the code does, not how it does it
4. **Mock external dependencies**: Use `vi.mock()` for API calls, third-party libraries, etc.
5. **One assertion per test**: Keep tests focused and easy to debug
6. **Test edge cases**: null, undefined, empty arrays, large datasets, etc.

## Coverage Goals

| Category | Current | Target |
|----------|---------|--------|
| Composables | ~90% | 70%+ ✅ |
| Components | 0% | 70%+ |
| Stores | 0% | 70%+ |
| Overall | ~15% | 70%+ |

## Continuous Integration

Tests run automatically on:
- Push to `main` or `develop` branches
- Pull requests to `main` or `develop`

The CI pipeline will fail if:
- Any test fails
- Code coverage drops below 70% (future requirement)

## Troubleshooting

### Tests not finding modules

Make sure the `@` alias is correctly configured in `vitest.config.js`:

```javascript
resolve: {
  alias: {
    '@': fileURLToPath(new URL('./src', import.meta.url))
  }
}
```

### Mock not working

Ensure mocks are defined before importing the module under test:

```javascript
vi.mock('@/services/api', () => ({
  getValidationDetailsReport: vi.fn()
}));

import { usePrefixes } from '@/composables/usePrefixes';
```

### JSDOM errors

Some tests may require DOM APIs. Ensure `environment: 'jsdom'` is set in `vitest.config.js`.

## Resources

- [Vitest Documentation](https://vitest.dev/)
- [Vue Test Utils](https://test-utils.vuejs.org/)
- [Testing Library](https://testing-library.com/)
