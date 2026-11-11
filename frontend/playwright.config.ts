import fs from 'node:fs';
import os from 'node:os';
import path from 'node:path';
import { chromium, defineConfig, devices } from '@playwright/test';

function resolveChromiumExecutable(): string | undefined {
  if (process.env.PLAYWRIGHT_CHROMIUM_EXECUTABLE_PATH) {
    return process.env.PLAYWRIGHT_CHROMIUM_EXECUTABLE_PATH;
  }
  const defaultPath = chromium.executablePath();
  if (fs.existsSync(defaultPath)) {
    return defaultPath;
  }
  const cacheRoot = path.join(os.homedir(), 'AppData', 'Local', 'ms-playwright');
  const candidate1248 = path.join(cacheRoot, 'chromium-1248', 'chrome-win64', 'chrome.exe');
  if (fs.existsSync(candidate1248)) {
    return candidate1248;
  }
  const systemChrome = 'C:\\Program Files\\Google\\Chrome\\Application\\chrome.exe';
  if (fs.existsSync(systemChrome)) {
    return systemChrome;
  }
  return undefined;
}

const executablePath = resolveChromiumExecutable();

export default defineConfig({
  testDir: './tests/e2e',
  fullyParallel: false,
  forbidOnly: !!process.env.CI,
  retries: process.env.CI ? 1 : 0,
  workers: 1,
  reporter: [['list'], ['html', { open: 'never' }]],
  use: {
    baseURL: process.env.PLAYWRIGHT_BASE_URL ?? 'http://localhost:5173',
    trace: 'retain-on-failure',
    screenshot: 'only-on-failure',
    locale: 'id-ID',
    timezoneId: 'Asia/Jakarta',
    ...(executablePath ? { launchOptions: { executablePath } } : {}),
  },
  projects: [
    {
      name: 'chromium-desktop',
      use: { ...devices['Desktop Chrome'], viewport: { width: 1440, height: 900 } },
    },
  ],
});
