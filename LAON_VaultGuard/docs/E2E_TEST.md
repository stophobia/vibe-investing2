# E2E 테스트 가이드 — LAON VaultGuard

> 🇰🇷 DeepSeek API 키로 실제 시크릿 탐지 End-to-End 테스트 가이드.
> 🇺🇸 End-to-End secret detection test guide using a real DeepSeek API key.
> 🇨🇳 使用真实 DeepSeek API 密钥的端到端密钥检测测试指南。

## 사전 준비

1. DeepSeek API 키 발급: https://platform.deepseek.com/api_keys
2. 약 $2 충전 (테스트 용도로 충분)

## 테스트 시나리오

### 시나리오 1: CLI 모드 — 로컬 레포 스캔

```bash
# 1. 키 설정
npm run setup
# → DeepSeek API Key: sk-your-real-key 입력

# 2. 테스트용 시크릿이 포함된 파일 생성
echo 'export AWS_ACCESS_KEY_ID=AKIAIOSFODNN7EXAMPLE' > /tmp/test-secret.txt
echo 'export AWS_SECRET_ACCESS_KEY=wJalrXUtnFEMI/K7MDENG/bPxRfiCYEXAMPLEKEY' >> /tmp/test-secret.txt

# 3. 테스트 레포 생성
mkdir -p /tmp/test-repo
cd /tmp/test-repo
git init
cp /tmp/test-secret.txt config.sh
git add config.sh
git commit -m "add config"

# 4. CLI 스캔 실행
cd LAON_VaultGuard
npx laon-vaultguard scan /tmp/test-repo
```

**예상 결과:**
```
🔍 1단계: git grep 키워드 필터링...
   → 1개 의심 라인 발견
🤖 2단계: LLM 문맥 분석 중...
   → 1개 LLM 응답 완료 (xxx tokens)

🔴 [CRITICAL] AWS — AWS Access Key ID
   파일: config.sh:1
   지문: AKIA…LE
   조치: 1) Rotate/revoke immediately...
```

### 시나리오 2: 서버 모드 — 웹 대시보드 + Telegram 알람

```bash
# 1. .env 설정 (DeepSeek 키 + Telegram)
DEEPSEEK_API_KEY=sk-your-real-key
LLM_PROVIDERS=deepseek
LLM_MODE=sequential
TELEGRAM_BOT_TOKEN=123:abc
TELEGRAM_CHAT_ID=-456

# 2. 서버 실행
npm run dev

# 3. 레포 등록
curl -X POST http://localhost:3101/api/repos \
  -H "Content-Type: application/json" \
  -d '{"name":"test-repo","type":"local","pathOrUrl":"/tmp/test-repo"}'

# 4. 수동 스캔
curl -X POST http://localhost:3101/api/scan/trigger

# 5. 대시보드 확인
open http://localhost:3101/dashboard
```

**예상 결과:**
- 대시보드에 finding 표시
- Telegram으로 알림 수신
- data/findings.json에 기록

### 시나리오 3: 실제 프로젝트 스캔

```bash
# vibe-investing 레포 등록 후 스캔
curl -X POST http://localhost:3101/api/repos \
  -H "Content-Type: application/json" \
  -d '{"name":"vibe-investing","type":"local","pathOrUrl":"/Users/dennis/Documents/GitHub/vibe-investing"}'

curl -X POST http://localhost:3101/api/scan/trigger
```

## 문제 해결

| 증상 | 원인 | 해결 |
|---|---|---|
| LLM auth failed | API 키 오타 | `npm run setup`으로 재설정 |
| LLM quota exceeded | 잔액 부족 | DeepSeek 콘솔에서 충전 |
| git grep 결과 없음 | 시크릿 없음 | 테스트 시크릿 파일 생성 |
| Telegram 알림 안 옴 | Bot Token/Chat ID 오류 | BotFather에서 재확인 |

## 자동화 CI 테스트 (추후)

```yaml
# .github/workflows/e2e-test.yml
- name: LAON VaultGuard E2E
  run: |
    mkdir /tmp/test-repo && cd /tmp/test-repo && git init
    echo 'API_KEY=sk-test123456789' > .env
    git add .env && git commit -m "test"
    cd LAON_VaultGuard
    npx laon-vaultguard scan /tmp/test-repo
  env:
    DEEPSEEK_API_KEY: ${{ secrets.DEEPSEEK_API_KEY }}
```
