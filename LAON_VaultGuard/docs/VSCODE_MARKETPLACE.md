# VS Code Marketplace Deployment Plan — LAON VaultGuard

> v0.6 → v0.7 계획. VS Code Marketplace에 정식 배포.

## 현재 상태

- **소스 위치**: `LAON_VaultGuard/vscode-extension/`
- **설치 방식**: 수동 (Developer → Install Extension from Location)
- **컴파일**: `npm run compile` → `out/extension.js`

## 배포 단계

### 1. 패키지 보완 (v0.6)

| # | 항목 | 설명 |
|---|------|------|
| 1.1 | 아이콘 추가 | 128x128 PNG 아이콘. `images/icon.png` |
| 1.2 | 패키지 메타데이터 | publisher, repository, bugs URL |
| 1.3 | CHANGELOG.md | 버전별 변경 내역 |
| 1.4 | `.vscodeignore` 보강 | src/ 제외, out/ 포함 |
| 1.5 | 라이선스 파일 | LICENSE 파일 추가 (MIT) |
| 1.6 | `vsce package` 테스트 | 로컬에서 `.vsix` 생성 및 설치 테스트 |

### 2. CI/CD 파이프라인 (v0.6)

| # | 항목 | 설명 |
|---|------|------|
| 2.1 | GitHub Actions | `.github/workflows/vscode-publish.yml` |
| 2.2 | 자동 패키징 | PR → `vsce package` → artifact |
| 2.3 | 자동 배포 | main push → `vsce publish` |
| 2.4 | Personal Access Token | Azure DevOps PAT (Marketplace publish용) |

### 3. Marketplace 제출 (v0.7)

| # | 항목 | 설명 |
|---|------|------|
| 3.1 | `vsce publish` | `vsce publish -p $VSCE_TOKEN` |
| 3.2 | Marketplace 페이지 | 설명, 스크린샷, 기능 목록 |
| 3.3 | 태그/카테고리 | Linters, Security, Other |
| 3.4 | 버전 관리 | semver (`major.minor.patch`) |

### 4. 설치 경험 (v0.7)

| # | 항목 | 설명 |
|---|------|------|
| 4.1 | `ext install laon-vaultguard` | Marketplace 검색으로 설치 |
| 4.2 | 첫 실행 가이드 | LAON VaultGuard 미설치 시 안내 메시지 |
| 4.3 | 설정 가이드 | `npm run setup` 안내 |
| 4.4 | Quick Fix 제공 | 탐지된 시크릿에 대한 Quick Fix 액션 |

## GitHub Actions 워크플로우 프롬프트

아래 프롬프트를 Claude/DeepSeek에 입력하여 CI/CD 파이프라인 생성:

```
Create a GitHub Actions workflow (.github/workflows/vscode-publish.yml) for publishing
a VS Code extension to the Marketplace. Requirements:

1. Trigger: push to main branch (only when vscode-extension/ changes)
2. Steps:
   a. Checkout repo
   b. Setup Node.js 20
   c. cd vscode-extension && npm ci
   d. npm run compile
   e. npx vsce package
   f. npx vsce publish -p ${{ secrets.VSCE_TOKEN }}
3. Use marketplace publisher ID: gameworkerkim
4. Package name: laon-vaultguard

Also generate the vsce publish manual commands for local testing.
```

## vsce 설정 (`package.json` 보강)

```json
{
  "publisher": "gameworkerkim",
  "icon": "images/icon.png",
  "repository": {
    "type": "git",
    "url": "https://github.com/gameworkerkim/vibe-investing"
  },
  "bugs": {
    "url": "https://github.com/gameworkerkim/vibe-investing/issues"
  },
  "homepage": "https://github.com/gameworkerkim/vibe-investing/tree/main/LAON_VaultGuard/vscode-extension"
}
```

## 체크리스트

- [ ] 아이콘 생성 (128x128 PNG)
- [ ] `vsce` devDependency 추가
- [ ] `package.json` 메타데이터 보강
- [ ] `.vscodeignore` 보강
- [ ] 로컬 `vsce package` 성공
- [ ] `.vsix` 수동 설치 테스트
- [ ] Azure DevOps PAT 발급
- [ ] GitHub Actions Secret 등록 (`VSCE_TOKEN`)
- [ ] CI 파이프라인 테스트
- [ ] Marketplace 제출 및 심사
- [ ] Marketplace 페이지 최적화
