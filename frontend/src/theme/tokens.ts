export const colors = {
  background: {
    surface: {
      game: "#0B1026",
      pro: "#0F172A",
    },
    card: {
      game: "#161C3A",
      pro: "#111827",
    },
  },
  text: {
    primary: {
      game: "#E5E9FF",
      pro: "#F8FAFC",
    },
    secondary: {
      game: "#9AA4D6",
      pro: "#CBD5F5",
    },
  },
  primary: {
    game: "#6C5CE7",
    pro: "#2563EB",
  },
  success: {
    game: "#2CE5A7",
    pro: "#14B8A6",
  },
  warning: {
    game: "#FFB347",
    pro: "#F97316",
  },
  danger: {
    game: "#FF5C5C",
    pro: "#DC2626",
  },
  accent: {
    cyan: {
      game: "#00E0FF",
      pro: "#38BDF8",
    },
  },
  loot: {
    achievement: "#FFD166",
    insight: "#A6C665",
    emotion: "#C792EA",
  },
  chart: {
    line: {
      game: "#6C5CE7",
      pro: "#2563EB",
    },
  },
};

export const typography = {
  titleLg: {
    fontFamily: {
      game: '"Outfit", sans-serif',
      pro: '"Work Sans", sans-serif',
    },
    fontSize: "32px",
    lineHeight: "40px",
    fontWeight: 600,
  },
  titleMd: {
    fontFamily: {
      game: '"Outfit", sans-serif',
      pro: '"Work Sans", sans-serif',
    },
    fontSize: "24px",
    lineHeight: "32px",
    fontWeight: 600,
  },
  heading: {
    fontFamily: '"Inter", sans-serif',
    fontSize: "20px",
    lineHeight: "28px",
    fontWeight: 600,
  },
  body: {
    fontFamily: '"Inter", sans-serif',
    fontSize: "16px",
    lineHeight: "24px",
    fontWeight: 400,
  },
  small: {
    fontFamily: '"Inter", sans-serif',
    fontSize: "14px",
    lineHeight: "20px",
    fontWeight: 400,
  },
  caption: {
    fontFamily: '"Inter", sans-serif',
    fontSize: "12px",
    lineHeight: "16px",
    fontWeight: 400,
  },
};

export const spacing = {
  xs: 4,
  sm: 8,
  md: 12,
  lg: 16,
  xl: 24,
  xxl: 32,
  xxxl: 40,
  xxxxl: 48,
};

export const radius = {
  sm: 8,
  md: 16,
  lg: 24,
};

export const shadow = {
  card: {
    game: "0 24px 60px rgba(19, 21, 41, 0.55)",
    pro: "0 24px 48px rgba(8, 12, 24, 0.45)",
  },
  toast: "0 12px 32px rgba(0,0,0,0.4)",
};

export const glow = {
  success: "0 0 24px rgba(44, 229, 167, 0.45)",
  danger: "0 0 24px rgba(255, 92, 92, 0.55)",
};

export const elevation = {
  base: 0,
  shell: 20,
  modal: 40,
  fx: 50,
  toast: 60,
};

export const tokens = {
  colors,
  typography,
  spacing,
  radius,
  shadow,
  glow,
  elevation,
};

export type Tokens = typeof tokens;
