import type { Metadata } from "next";
import { Geist, Geist_Mono } from "next/font/google";
import "./globals.css";
import { ThemeProvider } from "../theme/ThemeProvider";
import { FxRoot } from "../components/FxRoot";
import { AppShell } from "../components/AppShell";
import { Providers } from "./providers";

const geistSans = Geist({
  variable: "--font-geist-sans",
  subsets: ["latin"],
});

const geistMono = Geist_Mono({
  variable: "--font-geist-mono",
  subsets: ["latin"],
});

export const metadata: Metadata = {
  title: "Goaler 대시보드",
  description: "현실을 게임처럼 운영하는 생산성 코치",
};

export default function RootLayout({
  children,
}: Readonly<{
  children: React.ReactNode;
}>) {
  return (
    <html lang="ko">
      <body
        className={`${geistSans.variable} ${geistMono.variable} antialiased`}
      >
        <Providers>
          <ThemeProvider>
            <FxRoot>
              <AppShell>{children}</AppShell>
            </FxRoot>
          </ThemeProvider>
        </Providers>
      </body>
    </html>
  );
}
