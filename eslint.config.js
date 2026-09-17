import js from '@eslint/js';
import globals from 'globals';

export default [
  { ignores: ['node_modules/**', '.venv/**'] },
  js.configs.recommended,
  {
    files: ['app/static/js/**/*.js'],
    languageOptions: { ecmaVersion: 2022, sourceType: 'module', globals: globals.browser },
    rules: {
      eqeqeq: 'error',
      'no-var': 'error',
      'prefer-const': 'error',
      'no-unused-vars': ['error', { argsIgnorePattern: '^_' }],
    },
  },
];
