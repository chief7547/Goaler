import { setupWorker } from "msw/browser";
import { handlers } from "./handlers";

export const worker = setupWorker(...handlers);

export async function startMocking() {
  if (typeof window === "undefined") {
    return;
  }
  await worker.start({ onUnhandledRequest: "bypass" });
}
