import { expect, type Page } from '@playwright/test';

export async function gotoDashboard(page: Page) {
  await page.goto('/');
  await page.waitForLoadState('networkidle');
  await expect(page.locator('main')).toBeVisible();
}

export async function emulateReducedMotion(page: Page) {
  await page.emulateMedia({ reducedMotion: 'reduce' });
}

export async function switchTheme(page: Page, theme: 'game' | 'pro') {
  const toggle = page.getByRole('button', { name: new RegExp(theme, 'i') });
  if (await toggle.isVisible()) {
    await toggle.click();
  }
}
