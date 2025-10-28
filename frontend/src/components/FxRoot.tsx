"use client";

import { ReactNode } from "react";
import { FxProvider } from "./FxContext";
import { FxLayer } from "./FxLayer";

interface FxRootProps {
  children: ReactNode;
  reducedMotion?: boolean;
}

export const FxRoot: React.FC<FxRootProps> = ({ children, reducedMotion = false }) => {
  return (
    <FxProvider reducedMotion={reducedMotion}>
      <div className="relative min-h-screen">
        <FxLayer />
        {children}
      </div>
    </FxProvider>
  );
};
