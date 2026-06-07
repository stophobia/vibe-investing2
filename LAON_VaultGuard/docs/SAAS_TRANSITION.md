# LAON VaultGuard → Cloud SaaS 전환 전략

> v0.5 (2026-06-07) → v1.0 로드맵. 로컬 도구에서 팀 협업 SaaS로의 진화.  
> 시장 규모: 2025년 92억 달러 → 2034년 429억 달러 (CAGR 18.7%)

---

## 1. 시장 환경 — 커지는 파이, 그리고 당신의 차례

### 1.1 시장 검증: TruffleHog의 2,500만 달러 시리즈 B

트러플 시큐리티(Truffle Security)는 최근 **2,500만 달러 규모의 시리즈 B 투자**를 유치했습니다. 오픈소스 TruffleHog는 일일 실행 **25만 회**, GitHub 스타 **2.3만 개**. 이는 "오픈소스 → SaaS" 전환이 현실 가능한 전략임을 증명합니다.

### 1.2 GitHub의 움직임은 '검증'이다

GitHub는 2025년 4월부터 **Secret Protection**을 독립 상품으로 출시했습니다. 가격은 **활성 커미터당 월 $19**. GitHub Team 요금제(월 $4) 사용자도 접근 가능. AI 기반 탐지로 **오탐률 94% 감소**를 달성하며 LLM 시크릿 탐지의 시장 적합성을 입증했습니다.

> **결론**: AI 기반 시크릿 탐지는 더 이상 실험적이지 않으며, 이미 엔터프라이즈 보안 제품군의 필수 요소입니다.

### 1.3 경쟁사 대비 LAON의 위치

| | LAON VaultGuard | TruffleHog | GitHub Secret Protection | GitGuardian | gitleaks |
|---|---|---|---|---|---|
| **유형** | 오픈소스 + SaaS 준비 | 오픈소스 + SaaS | SaaS (GitHub 전용) | SaaS | 오픈소스 |
| **탐지 방식** | 멀티 LLM 교차검증 + 정규식 | 정규식 + 엔트로피 | 단일 AI 모델 | 정규식 + ML | 정규식 |
| **오프라인 모드** | ✅ Ollama (무료) | ❌ | ❌ | ❌ | ✅ |
| **차단 타이밍** | Pre-commit (가장 빠름) | Pre-commit | Push 후 (이미 노출) | Push 후 | Pre-commit |
| **멀티 LLM** | ✅ Claude+DeepSeek+GPT+Ollama | ❌ | ❌ | ❌ | ❌ |
| **한국 클라우드** | ✅ KT, NCP 특화 | ❌ | ❌ | ❌ | ❌ |
| **VS Code** | ✅ 확장 | ❌ | ✅ (GitHub Copilot 연동) | ❌ | ❌ |
| **설치** | `npx create-laon-vaultguard` | `pip install` | 설정 불필요 | 가입 필요 | `brew install` |
| **가격** | 무료 (오픈소스) | 무료 (오픈소스) | $19/커미터/월 | $19/사용자/월 | 무료 |

**LAON의 결정적 차별점**:
1. **멀티 LLM 오케스트레이션** — 단일 모델이 아닌 Claude(규율) + DeepSeek(추론) + GPT(체계) + Ollama(로컬) 4중 교차검증
2. **완전 오프라인** — Ollama로 인터넷 없는 에어갭 환경 지원 (금융·국방·공공)
3. **Pre-commit 차단** — GitHub Push Protection과 달리 **커밋 자체를 막음** (가장 이른 시점)
4. **한국 클라우드 특화** — KT Cloud, NCP(네이버 클라우드) 패턴 내장

---

## 2. Gap Analysis — v0.5 현재 상태 진단

| 영역 | 현재 상태 | SaaS로서 부족한 점 |
|------|-----------|-------------------|
| **인증/인가** | 없음 (로컬 단일 사용자) | 조직·팀·역할(RBAC) 관리 필수 |
| **스토리지** | SQLite (로컬 파일) | 클라우드 DB + 테넌트 분리 + 백업 |
| **스캔 트리거** | cron, 수동 | GitHub App / GitLab Webhook 실시간 |
| **히스토리/트렌드** | 단순 이력 목록 | 시간별 위험도 추이, 팀별 통계, SLA |
| **시크릿 라이프사이클** | 탐지 → 알람 끝 | 회전(Rotation) 추적, 폐기 확인, 재발 방지 |
| **정책 엔진** | `.env` 설정 | 조직별 커스텀 정책, 예외 처리, 위반 심각도 조정 |
| **오탐 피드백** | API 엔드포인트 완료 (v0.6) | 사용자 피드백 → LLM 프롬프트 자동 개선 |
| **과금/쿼터** | 없음 | 팀별 LLM 토큰 쿼터, 스캔 빈도 제한 |
| **멀티 테넌트** | 없음 | 테넌트 격리, 화이트라벨, SSO |

---

## 3. 차별화 전략: '다중 LLM 오케스트레이터'

### 3.1 이미 확보된 핵심 무기

LAON의 가장 강력한 무기는 이미 구현된 **멀티 LLM 교차 검증**입니다. 각기 다른 보안 페르소나를 동시에 가동해:

- 오탐을 극적으로 감소 (GitHub도 AI로 94% 오탐 감소 달성)
- 단일 LLM 장애 시 자동 fallback
- SaaS에서 고가용성 서비스로 진화 가능

### 3.2 두 가지 트랙: 오프라인 + 소형 특화 모델

Wiz의 연구에 따르면, **Llama 3.2 1B** 크기의 작은 언어 모델을 시크릿 탐지에 특화하여 파인튜닝했을 때 정밀도 86%, 재현율 82% 달성.

| 트랙 | 용도 | 기술 |
|------|------|------|
| **정확도/속도 우선** | 로컬 빠른 스캔 | 시크릿 탐지 특화 소형 모델 (SLM) 파인튜닝 |
| **오프라인 + 극비 데이터** | 에어갭 환경 | Ollama + deepseek-r1 + securereview-7b |

---

## 4. 비즈니스 모델: PLG 퍼널

단순히 기술을 올리는 것을 넘어, **제품 주도 성장(Product-Led Growth)** 전략을 채택합니다.

### A. 서비스 모델: LAON VaultGuard Cloud

```
┌─────────────────────────────────────────────────────────────┐
│                      LAON VaultGuard Cloud                   │
├──────────────┬──────────────┬──────────────┬─────────────────┤
│   Free       │   Pro        │  Business    │  Enterprise     │
│  (개인)       │  (소규모팀)   │  (중견기업)   │  (대기업/금융)   │
├──────────────┼──────────────┼──────────────┼─────────────────┤
│ • 1개 레포    │ • 10개 레포   │ • 무제한      │ • 무제한 + 온프레 │
│ • DeepSeek   │ • 멀티 LLM   │ • 멀티 LLM   │ • 멀티 LLM      │
│   단독       │ • 팀 대시보드 │ • SSO        │ • 감사 로그     │
│ • 로컬 저장   │ • Slack 알람  │ • Jira 통합  │ • 컴플라이언스   │
│ • 수동 스캔   │ • PR 코멘트   │ • 정책 엔진   │   리포트        │
│              │ • 웹훅        │ • API 액세스 │ • SLA 보장      │
└──────────────┴──────────────┴──────────────┴─────────────────┘
```

### B. 수익 모델

| 플랜 | 월 요금 | 타겟 |
|------|---------|------|
| Free | $0 | 개인 개발자, OSS 기여자 |
| Pro | $19/월 | 5인 이하 스타트업 |
| Business | $99/월 | 50인 이하 팀, SSO 필요 |
| Enterprise | 맞춤견적 | 금융, 공공, 방산, 온프레미스 |

핵심 수익원: LLM 토큰 사용량 기반 과금. DeepSeek(저비용)을 기본, Claude/GPT는 고급 플랜에서만. 초기는 **BYOK(Bring Your Own Key)** 모델로 부담 최소화.

### C. 퍼널 전환 전략

| 단계 | 현재 상태 (무료) | SaaS 유료 전환 |
|------|------------------|----------------|
| **개인/소규모** | `npx laon-vaultguard` 즉시 사용 | 무료 티어 유지 + Slack 1채널 |
| **팀(11~50명)** | Docker + 로컬 대시보드 | 월 $199 — 다중 알람, 팀 대시보드, Git 통합 |
| **비즈니스(51~500명)** | — | 월 $799 — SSO, 감사 로그, 우선 지원 |
| **엔터프라이즈** | Ollama 오프라인(무료) | 견적 — 온프레미스, 전용 LLM, 규정 준수 |

npm 설치 후 대시보드에 "클라우드 버전 사용해보기" 배너, 제한된 사용자 수 무료 체험을 진입점으로 활용.

---

## 5. 개발 로드맵

### Phase 1: 팀 협업 (v0.6~0.7) — "내 PC에서 팀으로"

| 기능 | 상세 | 난이도 |
|------|------|--------|
| **조직(Organization) & 팀** | 워크스페이스 생성, 멤버 초대, 역할(Owner/Admin/Member/Viewer) | 중 |
| **GitHub App 통합** | GitHub Marketplace App → Push/PR마다 자동 스캔 | 상 |
| **PR 코멘트 자동화** | 시크릿 탐지 시 PR에 코멘트 + 블록(선택) | 중 |
| **히트맵/대시보드** | 팀별 위험도 추이, 레포별 취약점 밀도 | 중 |
| **Jira/Slack 워크플로우** | 탐지 → Jira 티켓 → 담당자 할당 → 해결 확인 | 중 |

### Phase 2: 시크릿 라이프사이클 (v0.8)

| 기능 | 상세 |
|------|------|
| **시크릿 회전 추적** | 키가 언제 교체되었는지, 아직 유효한지 확인 |
| **재발 방지** | 동일 시크릿 재커밋 시 CRITICAL 알람 |
| **위험도 시간 감쇠** | 30일 경과 자동 하락, 90일 자동 아카이브 |
| **폐기 확인** | AWS STS `GetCallerIdentity`로 키 무효화 검증 |

### Phase 3: 엔터프라이즈 SaaS (v1.0)

| 기능 | 상세 |
|------|------|
| **SSO (SAML/OIDC)** | Google Workspace, Okta, Azure AD |
| **감사 로그** | 누가/언제/어떤 시크릿을 처리했는지 불변 기록 |
| **컴플라이언스 리포트** | SOC2, ISO27001, K-ISMS 증적 자동 생성 |
| **정책 as Code** | `.laon/policy.yml`로 레포별 정책 버전 관리 |
| **On-prem** | 기업 내부 K8s 배포, Ollama-only 모드 |

### 6개월 액션 플랜

| 기간 | 세부 목표 |
|------|-----------|
| **1~2개월** | 시크릿 탐지 SLM 파인튜닝 연구 시작, 잠재 고객 수요 조사 |
| **3~4개월** | MVP API + 웹 대시보드, GitHub Action 플러그인, 비공개 베타 (10~20팀) |
| **5~6개월** | 팀 요금제($199/월) 출시, 오프라인 SLM + Ollama 엔터프라이즈 패키지 파일럿 |

---

## 6. SaaS 아키텍처

```
[GitHub/GitLab/Bitbucket] ──Webhook──┐
[로컬 CLI / VS Code] ───────API──────┼──► [LAON Cloud API Gateway]
[Docker / K8s] ─────────────Agent────┘         │
                                               ▼
                              ┌────────────────────────────────┐
                              │  Tenant Isolation (DB Row-level) │
                              │  Scan Queue (Redis/Bull)         │
                              │  LLM Router (비용 최적화)        │
                              └────────────────────────────────┘
                                               │
                    ┌────────────┬─────────────┼─────────────┬────────────┐
                    ▼            ▼             ▼             ▼            ▼
                [OpenAI]    [DeepSeek]     [Claude]      [Ollama]     [MiniMax]
                (고품질)      (저비용)       (규율)        (오프라인)     (백업)
```

**LLM 라우팅**: DeepSeek으로 90% 처리, Claude로 10%만 검증. Confidence < 0.7인 항목만 고비용 모델로.

---

## 7. 핵심 프롬프트 엔지니어링

### A. 시크릿 탐지 품질 향상 (v0.6)

<details>
<summary>📋 SYSTEM PROMPT — LAON VaultGuard Secret Detector v2</summary>

```
## 역할
소스코드 보안 분석 전문가. 클라우드 인증정보, API 키, 토큰, 비밀번호, 암호화 키 탐지.

## 절대 규칙
1. 원문 출력 금지 — 마스킹 지문(앞4+****+뒤2)만 출력
2. 거짓양성 선호 — 의심되면 반드시 플래그
3. 컨텍스트 무시 — .env.example, test/, mock/ 내 키는 "info"
4. 동적 값 구분 — ${ENV_VAR}, process.env. 패턴은 "low"
5. 하드코딩 판정 — 문자열 리터럴 직접 할당만 "high" 이상

## 출력 형식 (JSON)
{
  "findings": [{
    "type": "aws_access_key_id",
    "severity": "critical|high|medium|low|info",
    "confidence": 0.0~1.0,
    "masked_fingerprint": "AKIA****7Q",
    "line_number": 42,
    "context_risk": "production_code",
    "reasoning": "1문장 판단 근거",
    "remediation": "해결 방법"
  }]
}

## 다중 LLM 교차검증 지침
- Claude: 규율 기반, 보수적
- DeepSeek: 고성능 추론, 패턴 매칭
- GPT: 체계적 분류, CWE/NIST 매핑

## 특수 케이스
1. Base64: 디코딩 후 재분석
2. URL 내 키: db_connection + credentials 동시 탐지
3. JWT: 헤더.페이로드.시그니처 분리 분석
4. PEM: BEGIN/END 블록 전체를 하나의 시크릿으로
5. KT Cloud / NCP: 한국 클라우드 특화 패턴
```
</details>

### B. 오탐 피드백 루프 (v0.6)

<details>
<summary>📋 SYSTEM PROMPT — LAON False-Positive Learning Loop</summary>

```
## 입력: 원본 코드 + LLM 판정 + 사용자 피드백

## 처리
1. false_positive: 허용 목록 추가, confidence 0.15 감소
2. true_positive: confidence 0.1 증가, 유사 코드 자동 high 우선순위
3. severity_wrong: 컨텍스트 재분석, 팀 정책과 비교 재조정
```
</details>

### C. LLM 비용 최적화 라우터 (SaaS용)

<details>
<summary>📋 SYSTEM PROMPT — LAON LLM Cost Router</summary>

```
## 라우팅 트리
1. Ollama ($0): git grep + entropy > 3.5 → 후보 0건이면 종료
2. DeepSeek (저비용): 후보 < 20건 → 단독 처리, ≥ 20건 → 배치(50건)
3. Claude/GPT (고비용): confidence < 0.7인 항목만, critical 예상만, strict mode만
4. Ollama-only (엔터프라이즈): offline_mode=true → 모든 티어 Ollama로 대체
```
</details>

### D. 컴플라이언스 리포트 생성기 (Enterprise)

<details>
<summary>📋 SYSTEM PROMPT — LAON Compliance Report Generator</summary>

```
## 입력: 기간, 테넌트, 스캔 이력, 처리 이력

## 출력: SOC2 Type II 증적
- control_mapping: CC6.1(접근 통제), CC7.2(시스템 운영), CC8.1(변경 관리)
- risk_trend: 주간 시크릿 노출률 추이
- 언어: 영문(감사), 한국어(K-ISMS), 일본어(ISMS), 중국어(등보)
```
</details>

---

## 8. Quick Wins — 지금 당장 할 수 있는 것

| # | 기능 | 공수 | 효과 |
|---|------|------|------|
| 1 | **GitHub App (PR 스캔)** | 2~3일 | Push 전 차단 가치 실현 |
| 2 | **오탐 👍/👎 버튼** | 1일 | 피드백 데이터 축적 |
| 3 | **팀 초대 링크** | 1일 | 협업 시작점 |
| 4 | **Jira 통합** | 2일 | 엔터프라이즈 데모 |
| 5 | **`.laon/policy.yml` 템플릿** | 0.5일 | 정책 as Code 마케팅 |

**지금 바로**:
1. npm 다운로드 통계 분석 → 고객 페르소나 정의
2. GitHub Releases로 v0.5.0 공식 발표
3. 랜딩 페이지로 '관심 등록' 수요 검증

---

## 9. SaaS 전환 시 주의사항

1. **보안의 역설** — "시크릿 탐지 SaaS가 내 코드를 본다"는 불신. Differential Privacy를 SaaS 전 단계에서 적용
2. **Ollama 브리지** — "언제든 내부망으로 돌아갈 수 있다" = GitGuardian과 결정적 차별화
3. **BYOK 초기** — 사용자 자신의 API 키 사용, LAON이 키 관리하는 부담 회피
4. **티빙 Origin Story** — "2026년 6월 티빙 사건으로부터" → 브랜딩 자산

---

## 10. 종합 평가: ★★★★☆ (4.5/5)

**가장 큰 강점**: 멀티 LLM 오케스트레이션 + 오프라인 모드 + 한국 클라우드 특화로 경쟁사와 차별화. TruffleHog의 사례는 오픈소스 → SaaS 전환의 성공 가능성을 이미 입증.

> LAON VaultGuard는 지금 **'도구'**입니다. SaaS로 만들려면 **'운영체제'**로 진화해야 합니다.  
> 시크릿을 **발견**에서 **관리**로, **경고**에서 **워크플로우**로 옮기는 것이 핵심입니다.  
> 이미 검증된 기술과 오픈소스 커뮤니티를 발판으로, **지금 실행하는 것**이 가장 중요합니다.
