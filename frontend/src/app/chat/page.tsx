export default function ChatPage() {
  return (
    <div className="space-y-4">
      <h1 className="text-2xl font-semibold" style={{ fontFamily: "var(--font-heading)" }}>
        챗 모듈 설계 진행 중
      </h1>
      <p className="text-sm text-[var(--text-secondary)]">
        `docs/FRONTEND_DESIGN.md` 4.2 절과 `docs/FRONTEND_API_CONTRACT.md`의 `/chat` 계약을 참고해
        UI·상태 구조를 준비해 두었습니다. 이후 작업자는 이 페이지에서 챗 로그, 추천 액션,
        컨텍스트 패널을 구현하면 됩니다.
      </p>
    </div>
  );
}
