"use client";

import clsx from "clsx";
import Link from "next/link";
import { usePathname } from "next/navigation";
import { ReactNode } from "react";
import { availableThemes, useThemeVariant } from "../theme/ThemeProvider";

const navItems = [
  { href: "/", label: "대시보드" },
  { href: "/chat", label: "챗" },
  { href: "/goals", label: "목표" },
  { href: "/reports", label: "리포트" },
  { href: "/settings", label: "설정" },
];

interface AppShellProps {
  children: ReactNode;
}

export const AppShell: React.FC<AppShellProps> = ({ children }) => {
  const pathname = usePathname();
  const { theme, setTheme } = useThemeVariant();

  return (
    <div className="md:flex">
        <aside className="hidden min-h-screen w-64 flex-shrink-0 flex-col justify-between border-r border-white/10 bg-black/20 px-6 py-8 md:flex">
          <div className="space-y-8">
            <div>
              <p className="text-xs uppercase tracking-[0.4em] text-[var(--accent-cyan)]">Goaler</p>
              <h1 className="mt-3 text-2xl font-semibold" style={{ fontFamily: "var(--font-title-md)" }}>
                현실을 게임처럼
              </h1>
              <p className="mt-2 text-sm text-[var(--text-secondary)]">
                오늘의 보스전에 대비하세요.
              </p>
            </div>
            <nav className="space-y-2">
              {navItems.map((item) => {
                const isActive = pathname === item.href || (item.href !== "/" && pathname.startsWith(item.href));
                return (
                  <Link
                    key={item.href}
                    href={item.href}
                    className={clsx(
                      "flex items-center justify-between rounded-xl px-3 py-2 text-sm transition-colors",
                      isActive
                        ? "bg-[var(--accent-primary)] text-[var(--surface)]"
                        : "text-[var(--text-secondary)] hover:bg-white/5 hover:text-[var(--text-primary)]"
                    )}
                  >
                    {item.label}
                    {isActive && (
                      <span className="text-xs font-semibold uppercase text-white/80">ON</span>
                    )}
                  </Link>
                );
              })}
            </nav>
          </div>
          <div className="space-y-3 rounded-2xl bg-white/5 p-4 text-sm text-[var(--text-secondary)]">
            <p className="text-[var(--text-primary)]">테마</p>
            <div className="flex items-center gap-2">
              {availableThemes.map((option) => (
                <button
                  key={option}
                  type="button"
                  onClick={() => setTheme(option)}
                  className={clsx(
                    "flex-1 rounded-lg border px-3 py-2 text-xs font-semibold uppercase tracking-[0.2em]",
                    theme === option
                      ? "border-[var(--accent-primary)] bg-[var(--accent-primary)] text-[var(--surface)]"
                      : "border-white/10 text-[var(--text-secondary)] hover:border-white/30"
                  )}
                >
                  {option === "game" ? "GAME" : "PRO"}
                </button>
              ))}
            </div>
            <p className="text-xs leading-5">
              Game은 몰입감 있는 네온 연출, Pro는 조용한 데이터 강조 버전입니다.
            </p>
          </div>
        </aside>
        <div className="relative flex min-h-screen flex-1 flex-col">
          <header className="flex items-center justify-between border-b border-white/10 px-6 py-4 backdrop-blur md:hidden">
            <h1 className="text-lg font-semibold">Goaler</h1>
            <div className="flex items-center gap-2 text-xs">
              <span className="rounded-full bg-[var(--accent-primary)] px-3 py-1 text-[var(--surface)]">
                Stage 1 · Energy
              </span>
            </div>
          </header>
          <main className="flex-1 overflow-y-auto px-4 py-6 pb-24 md:px-10 md:pb-10">
            {children}
          </main>
          <nav className="fixed bottom-0 left-0 right-0 z-30 flex items-center justify-around border-t border-white/10 bg-black/40 px-4 py-3 text-xs font-medium uppercase tracking-[0.3em] backdrop-blur md:hidden">
            {navItems.map((item) => {
              const isActive = pathname === item.href || (item.href !== "/" && pathname.startsWith(item.href));
              return (
                <Link
                  key={item.href}
                  href={item.href}
                  className={clsx(
                    "rounded-full px-3 py-2",
                    isActive
                      ? "bg-[var(--accent-primary)] text-[var(--surface)]"
                      : "text-[var(--text-secondary)]"
                  )}
                >
                  {item.label}
                </Link>
              );
            })}
          </nav>
        </div>
    </div>
  );
};
