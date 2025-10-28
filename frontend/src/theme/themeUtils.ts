import { colors, typography, spacing, radius, shadow, glow } from "./tokens";

export type ThemeVariant = "game" | "pro";

type CSSVariableMap = Record<string, string | number>;

const sharedVars: CSSVariableMap = {
  "--spacing-xs": `${spacing.xs}px`,
  "--spacing-sm": `${spacing.sm}px`,
  "--spacing-md": `${spacing.md}px`,
  "--spacing-lg": `${spacing.lg}px`,
  "--spacing-xl": `${spacing.xl}px`,
  "--radius-sm": `${radius.sm}px`,
  "--radius-md": `${radius.md}px`,
  "--radius-lg": `${radius.lg}px`,
  "--glow-success": glow.success,
  "--glow-danger": glow.danger,
  "--shadow-toast": shadow.toast,
};

const themeSpecific: Record<ThemeVariant, CSSVariableMap> = {
  game: {
    "--surface": colors.background.surface.game,
    "--card": colors.background.card.game,
    "--text-primary": colors.text.primary.game,
    "--text-secondary": colors.text.secondary.game,
    "--accent-primary": colors.primary.game,
    "--accent-success": colors.success.game,
    "--accent-warning": colors.warning.game,
    "--accent-danger": colors.danger.game,
    "--accent-cyan": colors.accent.cyan.game,
    "--shadow-card": shadow.card.game,
    "--font-title-lg": typography.titleLg.fontFamily.game,
    "--font-title-md": typography.titleMd.fontFamily.game,
  },
  pro: {
    "--surface": colors.background.surface.pro,
    "--card": colors.background.card.pro,
    "--text-primary": colors.text.primary.pro,
    "--text-secondary": colors.text.secondary.pro,
    "--accent-primary": colors.primary.pro,
    "--accent-success": colors.success.pro,
    "--accent-warning": colors.warning.pro,
    "--accent-danger": colors.danger.pro,
    "--accent-cyan": colors.accent.cyan.pro,
    "--shadow-card": shadow.card.pro,
    "--font-title-lg": typography.titleLg.fontFamily.pro,
    "--font-title-md": typography.titleMd.fontFamily.pro,
  },
};

export const getThemeVariables = (theme: ThemeVariant): CSSVariableMap => ({
  ...sharedVars,
  ...themeSpecific[theme],
  "--font-heading": typography.heading.fontFamily,
  "--font-body": typography.body.fontFamily,
  "--font-small": typography.small.fontFamily,
  "--font-caption": typography.caption.fontFamily,
  "--font-title-lg-size": typography.titleLg.fontSize,
  "--font-title-md-size": typography.titleMd.fontSize,
  "--font-heading-size": typography.heading.fontSize,
  "--font-body-size": typography.body.fontSize,
  "--font-small-size": typography.small.fontSize,
  "--font-caption-size": typography.caption.fontSize,
  "--font-title-lg-line": typography.titleLg.lineHeight,
  "--font-title-md-line": typography.titleMd.lineHeight,
  "--font-heading-line": typography.heading.lineHeight,
  "--font-body-line": typography.body.lineHeight,
  "--font-small-line": typography.small.lineHeight,
  "--font-caption-line": typography.caption.lineHeight,
  "--loot-achievement": colors.loot.achievement,
  "--loot-insight": colors.loot.insight,
  "--loot-emotion": colors.loot.emotion,
});

export const themeOptions: ThemeVariant[] = ["game", "pro"];
