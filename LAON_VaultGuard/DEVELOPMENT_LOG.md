# DEVELOPMENT LOG — LAON VaultGuard

> macOS · Node.js/TypeScript · LLM 기반 시크릿 탐지 감사 도구

## 2026-06-07 — v0.1 프로젝트 초기화

### 완료
- [x] 프로젝트 디렉토리 구조 생성
- [x] `package.json` — deps 정의 (express, simple-git, openai, node-cron, @octokit/rest, dotenv)
- [x] `tsconfig.json` — ES2022, bundler module resolution
- [x] `.env.example` — LLM 키, 알람 채널, 스캔 설정 템플릿
- [x] `.gitignore` — node_modules, dist, data, .env, *.db
- [x] `docs/Architecture.md` — 전체 아키텍처 문서 (개선 제안 반영)
- [x] `docs/API.md` — REST API 풀 스펙 (11개 엔드포인트)
- [x] `docs/Database.md` — 파일 기반 JSON 저장소 스키마
- [x] `docs/LLM_Prompt.md` — 시크릿 탐지 LLM 프롬프트 연동 가이드
- [x] `src/types.ts` — 공통 타입 정의
- [x] `src/config.ts` — dotenv + 환경변수 검증
- [x] `src/db.ts` — 파일 기반 JSON 저장소 (repos, findings, scans, audit log)
- [x] `src/git-monitor.ts` — simple-git + Octokit, diff 파싱, GitHub compareCommits 증분
- [x] `src/candidate-filter.ts` — git grep 1차 키워드 필터 (20+ 패턴)
- [x] `src/llm-harness.ts` — 멀티 LLM 호출 (parallel/sequential/majority), fallback 체인, 비용 산정
- [x] `src/sse.ts` — SSE 이벤트 버스
- [x] `src/scan-runner.ts` — 단일 레포 스캔 파이프라인 (git → grep → LLM → save → alert)
- [x] `src/scheduler.ts` — node-cron + 초기 구동 스캔 + 수동 트리거
- [x] `src/alert-engine.ts` — Telegram Bot API 알람
- [x] `src/routes/api.ts` — REST API (repos, findings, scan, acknowledge, dashboard)
- [x] `src/index.ts` — Express 서버 진입점 (+ SSE, CORS, graceful shutdown)
- [x] `public/index.html` + `dashboard.js` — 대시보드 UI (SSE 실시간, 필터, acknowledge)
- [x] `npm install` → 정상
- [x] `npm run build` → 정상 (esbuild, 2.0MB)
- [x] `npm run typecheck` → 정상 (tsc --noEmit)

### 설계 결정
- **macOS 전용** — v0.1은 macOS만 공식 지원
- **파일 기반 스토리지** — `data/` 아래 JSON 파일로 관리, v0.2에서 SQLite 확장 예정
- **LLM fallback 체인** — sequential 모드에서 provider 실패 시 자동 다음 provider 전환
- **GitHub 증분 스캔** — Octokit `compareCommitsWithBasehead`로 전체 클론 방지
- **LLM 비용 로깅** — audit_log에 토큰 사용량 기록
- **대시보드 인증** — v0.1은 localhost 전용

### 다음 작업 (v0.1 마무리)
1. [ ] `.env` 설정 후 실제 구동 테스트
2. [ ] 로컬 레포 등록 → 수동 스캔 → 대시보드 확인
3. [ ] Telegram 알람 연동 검증
4. [ ] GitHub 원격 레포 연동 검증
5. [ ] 오류 처리 보강 (네트워크 타임아웃, git grep 실패 등)

### v0.2 계획
1. [ ] SQLite 마이그레이션 (better-sqlite3)
2. [ ] 대시보드 인증
3. [ ] Slack 알람
4. [ ] 이메일 요약 리포트
