"use client";

import {
  createContext,
  useContext,
  useMemo,
  useState,
  type ReactNode,
  type CSSProperties,
} from "react";
import { getThemeVariables, themeOptions, type ThemeVariant } from "./themeUtils";

interface ThemeContextValue {
  theme: ThemeVariant;
  setTheme: (next: ThemeVariant) => void;
}

const ThemeContext = createContext<ThemeContextValue | null>(null);

interface ThemeProviderProps {
  children: ReactNode;
  initialTheme?: ThemeVariant;
}

export const ThemeProvider: React.FC<ThemeProviderProps> = ({
  children,
  initialTheme = "game",
}) => {
  const [theme, setTheme] = useState<ThemeVariant>(initialTheme);

  const value = useMemo(() => ({ theme, setTheme }), [theme]);
  const themeVars = useMemo(() => getThemeVariables(theme), [theme]);

  return (
    <ThemeContext.Provider value={value}>
      <div
        style={themeVars as CSSProperties}
        data-theme={theme}
        className="min-h-screen bg-[var(--surface)] text-[var(--text-primary)]"
      >
        {children}
      </div>
    </ThemeContext.Provider>
  );
};

export const useThemeVariant = () => {
  const context = useContext(ThemeContext);
  if (!context) {
    throw new Error("useThemeVariant must be used within ThemeProvider");
  }
  return context;
};

export const availableThemes = themeOptions;
