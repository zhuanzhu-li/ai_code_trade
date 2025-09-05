const js = require('@eslint/js')
const typescript = require('@typescript-eslint/eslint-plugin')
const typescriptParser = require('@typescript-eslint/parser')
const vue = require('eslint-plugin-vue')
const vueParser = require('vue-eslint-parser')

module.exports = [
  js.configs.recommended,
  {
    files: ['**/*.{js,ts,vue}'],
    languageOptions: {
      parser: vueParser,
      parserOptions: {
        parser: typescriptParser,
        ecmaVersion: 'latest',
        sourceType: 'module'
      },
      globals: {
        console: 'readonly',
        process: 'readonly',
        global: 'readonly',
        window: 'readonly',
        document: 'readonly',
        localStorage: 'readonly',
        URL: 'readonly',
        __dirname: 'readonly',
        module: 'readonly',
        require: 'readonly'
      }
    },
    plugins: {
      '@typescript-eslint': typescript,
      vue
    },
    rules: {
      ...typescript.configs.recommended.rules,
      ...vue.configs['vue3-recommended'].rules,
      '@typescript-eslint/no-unused-vars': ['error', { argsIgnorePattern: '^_' }],
      '@typescript-eslint/no-explicit-any': 'warn',
      '@typescript-eslint/no-require-imports': 'off',
      'no-useless-catch': 'warn',
      'no-useless-escape': 'warn',
      'vue/multi-word-component-names': 'off',
      'vue/no-v-html': 'off'
    }
  },
  {
    ignores: ['node_modules/**', 'dist/**', 'coverage/**', 'eslint.config.js']
  }
]
