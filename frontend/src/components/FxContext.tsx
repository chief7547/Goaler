"use client";

import { ReactNode, useEffect } from "react";
import { useFxStore, FxPayload } from "../stores/fxStore";

export const FxProvider: React.FC<{ children: ReactNode; reducedMotion?: boolean }>
  = ({ children, reducedMotion = false }) => {
  const setReducedMotion = useFxStore((state) => state.setReducedMotion);

  useEffect(() => {
    setReducedMotion(reducedMotion);
  }, [reducedMotion, setReducedMotion]);

  return <>{children}</>;
};

export const useFxLayer = () => {
  const queue = useFxStore((state) => state.queue);
  const popFx = useFxStore((state) => state.popFx);

  return {
    queue,
    popFx,
  };
};

export const triggerFx = (payload: FxPayload) => {
  useFxStore.getState().pushFx(payload);
};
