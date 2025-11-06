import { expect, test } from '@playwright/test';

import { gotoDashboard } from './common';

test('Settings allow toggling reduced motion', async ({ page }) => {
  await gotoDashboard(page);
  await page.getByRole('link', { name: /설정/i }).click();

  await expect(page.getByRole('heading', { name: /설정 & 알림 제어/i })).toBeVisible();

  const reducedToggle = page.getByRole('checkbox', { name: /Reduced Motion/i });
  await reducedToggle.check();
  await expect(reducedToggle).toBeChecked();
});
