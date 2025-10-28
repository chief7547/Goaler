"use client";

import { ReactNode, useEffect } from "react";
import { initMocks } from "../lib/initMocks";

interface ProvidersProps {
  children: ReactNode;
}

export const Providers: React.FC<ProvidersProps> = ({ children }) => {
  useEffect(() => {
    initMocks();
  }, []);

  return <>{children}</>;
};
