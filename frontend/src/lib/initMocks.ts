export async function initMocks() {
  if (typeof window === "undefined") {
    return;
  }

  if (process.env.NEXT_PUBLIC_API_MOCKING !== "enabled") {
    return;
  }

  const { startMocking } = await import("../mocks/browser");
  await startMocking();
}
