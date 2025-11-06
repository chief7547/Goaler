# Playwright E2E Tests

## Prerequisites
- API 서버가 `/api/v1` 경로로 동작 중이어야 합니다. 로컬 개발에서는 `GOALER_ACTIVE_USER_ID=demo-user python api.py`를 먼저 실행하세요.
- Next.js 앱은 `npm run dev` 또는 `npm run build && npm run start`로 띄워야 합니다.

## 실행 방법
```bash
cd frontend
npm install
npx playwright install --with-deps chromium
npm run dev # 다른 터미널에서 실행 중이라면 생략
PLAYWRIGHT_BASE_URL=http://localhost:3000 npx playwright test
```

### Reduced Motion & Theme 시나리오
Playwright 프로젝트는 `chromium`과 `chromium-reduced-motion` 두 가지가 포함되어 있습니다. 
- Reduced Motion 모드는 자동으로 `emulateMedia({ reducedMotion: 'reduce' })` 설정을 사용해 대체 연출을 검증합니다.
- Professional 테마 전환은 테스트 내에서 앱의 테마 토글 버튼을 클릭해 확인합니다.

## CI 연동
`npm run test:stories`와 함께 `npx playwright test`를 실행하도록 하고, 실패 시 `frontend/tests/e2e-output/`의 스크린샷/비디오를 아티팩트로 업로드하세요.
