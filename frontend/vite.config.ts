import { defineConfig } from 'vite'
import react from '@vitejs/plugin-react'
import { configDefaults } from 'vitest/config';

// https://vitejs.dev/config/
export default defineConfig({
  plugins: [react()],
  test: {
    ...configDefaults,
    environment: 'jsdom',
    globals: true,
    setupFiles: './src/setupTests.ts', // 必要に応じて設定ファイルを指定
    coverage: {
      provider: 'v8',
      reporter: ['text', 'json', 'html'],
      exclude: [
        'src/main.tsx',  // main.tsxをカバレッジレポートから除外する(main.tsxはテスト対象外)
        'eslint.config.js',
        'vite.config.ts',
        'node_modules/**'
      ],
    },
  },
})
