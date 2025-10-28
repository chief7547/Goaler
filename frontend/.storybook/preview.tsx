import type { Preview } from "@storybook/nextjs-vite";
import { FxRoot } from "../src/components/FxRoot";
import { ThemeProvider, availableThemes } from "../src/theme/ThemeProvider";

const preview: Preview = {
  globalTypes: {
    theme: {
      name: "Theme",
      description: "게임/프로 변환",
      defaultValue: "game",
      toolbar: {
        icon: "mirror",
        items: availableThemes.map((value) => ({ value, title: value.toUpperCase() })),
        showName: true,
      },
    },
    reducedMotion: {
      name: "Reduced Motion",
      description: "모션 축소 모드 토글",
      defaultValue: "off",
      toolbar: {
        icon: "contrast",
        items: [
          { value: "off", title: "Motion On" },
          { value: "on", title: "Motion Reduced" },
        ],
      },
    },
  },
  decorators: [
    (Story, context) => (
      <ThemeProvider initialTheme={context.globals.theme as (typeof availableThemes)[number]}>
        <FxRoot reducedMotion={context.globals.reducedMotion === "on"}>
          <div style={{ minHeight: "100vh", padding: "32px", background: "var(--surface)" }}>
            <Story />
          </div>
        </FxRoot>
      </ThemeProvider>
    ),
  ],
  parameters: {
    controls: {
      matchers: {
        color: /(background|color)$/i,
        date: /Date$/i,
      },
    },
    a11y: {
      test: "todo",
    },
  },
};

export default preview;
