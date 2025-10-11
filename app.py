"""
Main application file for the Goaler conversational agent.
This file contains the main conversation loop that interacts with the user and the Gemini API.
"""

import os
import uuid
import google.generativeai as genai
from dotenv import load_dotenv

from core.agent import GoalSettingAgent
from core.llm_prompt import SYSTEM_PROMPT

def run_conversation():
    """Runs the main conversational loop."""
    print("--- Goaler 초기화 중... ---")
    load_dotenv()

    # 1. API 키 설정 확인
    api_key = os.getenv("GOOGLE_GEMINI_API_KEY")
    if not api_key:
        print("오류: GOOGLE_GEMINI_API_KEY 환경 변수를 찾을 수 없습니다.")
        return

    genai.configure(api_key=api_key)

    # 2. 우리 시스템의 핵심 에이전트와 LLM 모델 준비
    agent = GoalSettingAgent()
    
    # LLM에게 우리가 정의한 함수(Tool)들을 알려줌
    model = genai.GenerativeModel(
        model_name='gemini-1.5-flash',
        system_instruction=SYSTEM_PROMPT,
        tools=[agent.create_goal, agent.add_metric, agent.set_motivation, agent.finalize_goal]
    )

    # 3. 대화 시작
    # enable_automatic_function_calling=True 옵션이 핵심입니다.
    # 이 옵션 덕분에 LLM이 함수를 호출해야겠다고 판단하면, 라이브러리가 자동으로 해당 함수를 실행해 줍니다.
    chat = model.start_chat(enable_automatic_function_calling=True)
    
    # 각 대화를 구별하기 위한 고유 ID 생성
    conversation_id = f"conv_{uuid.uuid4()}"
    
    print("--- Goaler 준비 완료. 대화를 시작하세요. (종료하려면 'exit' 입력) ---")

    # 4. 대화 루프
    while True:
        user_input = input("> ")
        if user_input.lower() == 'exit':
            print("대화를 종료합니다.")
            break

        # 사용자 입력을 LLM에게 전송
        response = chat.send_message({
            "role": "user",
            "parts": [{
                "text": f"[CONVERSATION_ID: {conversation_id}] {user_input}"
            }]
        })

        # 최종 답변 출력 (함수 호출 과정은 라이브러리가 자동으로 처리)
        print(f"Goaler: {response.text}")

if __name__ == "__main__":
    run_conversation()
