# Database Schema — LAON VaultGuard (macOS v0.1)

> **v0.1**: 파일 기반 JSON 저장소. `data/` 디렉토리 아래 구조화된 파일로 관리.
> v0.2+에서 SQLite로 점진적 마이그레이션 예정.

## 저장소 경로

기본: `./data/` (`.env`의 `DB_PATH`로 변경 가능)

```
data/
├── repos.json          ← 모니터링 레포 목록 (Repository[])
├── findings.json       ← 탐지된 시크릿 건 (Finding[])
├── scans/              ← 스캔 실행 기록 (개별 JSON 파일)
│   ├── {uuid}.json
│   └── ...
└── logs/               ← 감사 로그 (일별 파일)
    ├── 2026-06-07.log
    └── ...
```

## 엔티티

### Repository (`repos.json`)

```typescript
interface Repository {
  id: string;            // UUID
  name: string;          // 표시명
  type: "local" | "github" | "gitlab";
  pathOrUrl: string;     // 로컬 경로 or 원격 URL
  branch: string;        // 기본 "main"
  enabled: boolean;      // false=일시중지
  cronOverride: string | null;
  lastScan: string | null; // ISO datetime
  createdAt: string;     // ISO datetime
}
```

### ScanRun (`scans/{id}.json`)

```typescript
interface ScanRun {
  id: string;            // UUID
  repoId: string;
  status: "running" | "completed" | "failed";
  trigger: "scheduled" | "manual";
  startedAt: string;
  completedAt: string | null;
  filesScanned: number;
  findingsCritical: number;
  findingsHigh: number;
  findingsMedium: number;
  findingsInfo: number;
  llmProvidersUsed: string[];
  errorMessage: string | null;
}
```

### Finding (`findings.json`)

```typescript
interface Finding {
  id: string;            // F-{uuid8}
  scanId: string;
  repoId: string;
  filePath: string;
  line: number | null;
  provider: "AWS" | "Azure" | "GCP" | "KTCloud" | "NCP" | "Generic";
  secretType: string;    // 예: "AWS Access Key ID"
  maskedFingerprint: string;  // 예: "AKIA…7Q"
  confidence: "high" | "medium" | "low";
  severity: "critical" | "high" | "medium" | "info";
  isPlaceholder: boolean;
  evidenceNote: string;
  remediation: string;
  acknowledged: boolean;
  acknowledgedAt: string | null;
  acknowledgedNote: string | null;
  detectedAt: string;    // ISO datetime
  llmSources: string[];  // 응답한 LLM provider 목록
}
```

### Audit Log (`logs/{YYYY-MM-DD}.log`)

각 라인은 JSON 객체:

```json
{"timestamp":"2026-06-07T12:00:00.000Z","event":"scan_started","severity":"info","message":"...","metadata":{}}
```

이벤트 종류: `scan_started`, `scan_completed`, `finding_detected`, `alert_sent`, `repo_added`, `repo_removed`, `finding_acknowledged`, `error`

## 쿼리 성능 고려 (v0.1 한계)

- `findings.json` 단일 파일 읽기/쓰기 → findings 수백 건 이하에서 정상 동작
- 수천 건 이상 누적 시 성능 저하 → v0.2에서 SQLite로 이전
- 현재는 `acknowledged` 된 finding을 90일 이상 보관 시 수동 정리 권장

## SQLite 마이그레이션 계획 (v0.2)

- `data/repos.json` → `repositories` 테이블
- `data/findings.json` → `findings` 테이블
- `data/scans/*.json` → `scan_runs` 테이블
- `data/logs/*.log` → `audit_log` 테이블
- 마이그레이션 스크립트: `npm run migrate` → 기존 JSON → SQLite 변환
