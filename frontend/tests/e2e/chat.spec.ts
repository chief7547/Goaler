import { expect, test } from '@playwright/test';

import { gotoDashboard, switchTheme } from './common';

test('Chat surface renders context and suggestions', async ({ page }) => {
  await gotoDashboard(page);
  await page.getByRole('link', { name: /챗/i }).click();

  await expect(page.getByRole('heading', { name: /코치와의 대화/i })).toBeVisible();
  await expect(page.getByText('어제 전리품을 기록했어요', { exact: false })).toBeVisible();
  await switchTheme(page, 'pro');
  await expect(page.locator('[data-theme="pro"]')).toBeVisible();
});
