import { defineConfig, devices } from '@playwright/test';

const baseURL = 'http://127.0.0.1:3000';

export default defineConfig({
  timeout: 60_000,
  testDir: './tests/e2e',
  outputDir: './tests/e2e-output',
  use: {
    baseURL,
    trace: 'retain-on-failure',
    screenshot: 'only-on-failure',
    video: 'retain-on-failure',
  },
  projects: [
    {
      name: 'chromium',
      use: devices['Desktop Chrome'],
    },
    {
      name: 'chromium-reduced-motion',
      use: {
        ...devices['Desktop Chrome'],
        colorScheme: 'dark',
      },
    },
  ],
  webServer: {
    command: 'NEXT_PUBLIC_API_MOCKING=enabled npm run dev -- --hostname 127.0.0.1 --port 3000',
    url: baseURL,
    reuseExistingServer: !process.env.CI,
    cwd: __dirname,
    stdout: 'pipe',
    stderr: 'pipe',
  },
});
