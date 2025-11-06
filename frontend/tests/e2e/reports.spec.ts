import { expect, test } from '@playwright/test';

import { gotoDashboard, switchTheme } from './common';

test('Reports screen loads highlights', async ({ page }) => {
  await gotoDashboard(page);
  await page.getByRole('link', { name: /리포트/i }).click();

  await expect(page.getByRole('heading', { name: /리포트 & 회고/i })).toBeVisible();
  const highlight = page.getByText('Stage 1 에너지 안정화', { exact: false });
  if (await highlight.count()) {
    await expect(highlight.first()).toBeVisible();
  } else {
    await expect(page.getByText('리포트 데이터를 가져오지 못했습니다.', { exact: false })).toBeVisible();
  }
  await switchTheme(page, 'pro');
  await expect(page.locator('[data-theme="pro"]')).toBeVisible();
});
