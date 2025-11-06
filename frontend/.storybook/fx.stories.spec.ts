import { test, expect } from '@storybook/test-runner';

import type { StoryId } from '@storybook/test-runner';

const stories: StoryId[] = [
  'fxlayer-examples--stage-upgrade',
  'fxlayer-examples--quest-complete',
  'fxlayer-examples--energy-warning-reduced',
  'fxlayer-examples--professional-theme',
];

test.describe('FxLayer visual regression', () => {
  for (const id of stories) {
    test(id, async ({ page, storybook }) => {
      await storybook.goto(id);

      // Give animations time to render initial state
      await page.waitForTimeout(400);

      // Storybook interactions should respect reduced motion state when provided
      const frame = page.frameLocator('iframe[data-testid="storybook-preview-iframe"]');
      const fxLayer = frame.locator('.fx-layer');
      await expect(fxLayer).toHaveScreenshot(`${id}.png`, { animations: 'disabled', maxDiffPixelRatio: 0.05 });
    });
  }
});
