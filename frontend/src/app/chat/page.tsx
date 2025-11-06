import { ChatPageContent } from "../../components/chat/ChatPageContent";

export default function ChatPage() {
  return (
    <div className="space-y-6">
      <header className="space-y-2">
        <h1 className="text-2xl font-semibold" style={{ fontFamily: "var(--font-heading)" }}>
          코치와의 대화
        </h1>
        <p className="text-sm text-[var(--text-secondary)]">
          진행 상황을 공유하면 코치가 목표, 퀘스트, 전리품 계획을 실시간으로 조정합니다.
        </p>
      </header>
      <ChatPageContent />
    </div>
  );
}
