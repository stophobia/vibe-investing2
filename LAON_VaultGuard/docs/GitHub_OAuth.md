# GitHub App OAuth 연동 가이드 — LAON VaultGuard

> 🇰🇷 대시보드에서 GitHub 계정을 연동해 원격 레포지토리를 바로 등록하는 방법.
> 🇺🇸 How to connect your GitHub account from the dashboard to instantly register remote repos.
> 🇨🇳 从仪表板连接 GitHub 账户以直接注册远程仓库。

## 1. GitHub OAuth App 생성

1. https://github.com/settings/developers → **New OAuth App**
2. 설정:
   - **Application name**: `LAON VaultGuard (local)`
   - **Homepage URL**: `http://localhost:3101`
   - **Authorization callback URL**: `http://localhost:3101/api/oauth/github/callback`
3. **Register application** → **Generate a new client secret**
4. Client ID와 Client Secret 복사

## 2. .env 설정

```bash
GITHUB_CLIENT_ID=Iv1.xxxxxxxxxxxx
GITHUB_CLIENT_SECRET=xxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxx
GITHUB_REDIRECT_URI=http://localhost:3101/api/oauth/github/callback
```

## 3. 사용 방법

1. `npm run dev` 실행
2. 대시보드 접속 → **🔗 GitHub** 버튼 클릭
3. **GitHub 연동** 버튼 → GitHub 로그인 → 권한 승인
4. 연동 완료 후 내 레포지토리 목록이 표시됨
5. **+ 등록** 버튼으로 모니터링할 레포 선택

## 4. 작동 방식

```
대시보드                              GitHub
  │                                     │
  ├─ GET /api/oauth/github ────────────→│  OAuth 인증 페이지
  │                                     │
  │←─ callback?code=xxx ───────────────┤  사용자 승인
  │                                     │
  ├─ POST /login/oauth/access_token ──→│  code → token 교환
  │                                     │
  ├─ GET /user ───────────────────────→│  사용자 정보 조회
  │                                     │
  ├─ 토큰 저장 (data/oauth.json)        │
  │                                     │
  ├─ GET /user/repos ─────────────────→│  레포 목록 조회
  │                                     │
  └─ 레포 등록 + 주기적 스캔            │
```

## 5. 권한 (Scopes)

- `repo` — private 레포지토리 포함 접근 (스캔용)
- `read:user` — 사용자 정보 조회

## 6. 보안

- OAuth 토큰은 `data/oauth.json`에 저장 (`.gitignore` 대상)
- 토큰은 로컬에서만 사용, 외부 전송 없음
- 언제든지 대시보드에서 **연동 해제** 가능
- GitHub 측에서도 Settings → Applications → Revoke 가능

## 7. 문제 해결

| 증상 | 원인 | 해결 |
|---|---|---|
| redirect_uri_mismatch | callback URL 불일치 | GitHub App 설정과 `.env`의 값이 정확히 일치하는지 확인 |
| 401 Unauthorized | client_secret 오류 | `.env`에서 재확인 후 서버 재시작 |
| 레포 목록이 안 뜸 | 토큰 만료 | 연동 해제 후 재연동 |
| Organization 레포가 안 보임 | OAuth App 권한 | Organization이 Third-party access를 허용했는지 확인 |
