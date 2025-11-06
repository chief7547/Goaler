import { expect, test } from '@playwright/test';

import { emulateReducedMotion, gotoDashboard, switchTheme } from './common';

test.describe('Dashboard experience', () => {
  test('shows hero card and quest checklist', async ({ page, project }) => {
    await gotoDashboard(page);
    if (project.name.includes('reduced-motion')) {
      await emulateReducedMotion(page);
    }

    await expect(page.getByText('체크리스트', { exact: false }).first()).toBeVisible();
    await expect(page.getByRole('heading', { name: '오늘의 추천 퀘스트' })).toBeVisible();
  });

  test('professional theme changes visual tokens', async ({ page }) => {
    await gotoDashboard(page);
    await switchTheme(page, 'pro');
    await expect(page.locator('[data-theme="pro"]').first()).toBeVisible();
  });
});
