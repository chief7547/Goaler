"use client";

import { ReactNode, useEffect, useState } from "react";
import { QueryClient, QueryClientProvider } from "@tanstack/react-query";
import { initMocks } from "../lib/initMocks";

interface ProvidersProps {
  children: ReactNode;
}

export const Providers: React.FC<ProvidersProps> = ({ children }) => {
  const [queryClient] = useState(() => new QueryClient());
  useEffect(() => {
    initMocks();
  }, []);

  return <QueryClientProvider client={queryClient}>{children}</QueryClientProvider>;
};
