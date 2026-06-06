# azure-news — (미사용) 뉴스 요약은 AIInvestor 앱에 통합됨

> **결정(2026-06-06)**: 가이드 §2.2 는 별도 Node 20 Functions 앱을 상정했으나,
> 이미 배포·운영 중인 **AIInvestor**(Python 3.11, Azure Functions v2) 앱에 Timer 함수로 **통합**한다.
> DeepSeek 클라이언트·Blob 저장·Key Vault 시크릿·배포 파이프라인을 모두 재사용하기 위함.
> 따라서 이 폴더에는 별도 구현을 두지 않는다(결정 기록용으로만 유지).

## 어디서 작업하나
- 구현 위치: `AIInvestor/` (별도 VS Code 프로젝트, github.com/gameworkerkim/vibe-investing/tree/main/AIInvestor)
- 작업 프롬프트: [`../docs/PROMPT-azure-news.md`](../docs/PROMPT-azure-news.md)

## 대시보드 repo 와의 유일한 합의 지점: ingest 계약
Azure 함수 → Cloudflare Pages Function `POST /api/ingest/news` 의 요청 형식·HMAC 서명 규약은
[`../docs/PROMPT-azure-news.md`](../docs/PROMPT-azure-news.md) 의 **§ingest 계약**에 단일 기준으로 정의되어 있다.
대시보드의 Pages Function `/api/ingest/news` 는 이 계약대로 검증/저장을 **이미 구현·테스트 완료**(`functions/api/ingest/news.ts` → `shared/ingest.ts`).
