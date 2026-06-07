# API Reference — LAON VaultGuard

Base URL: `http://localhost:3101`

## Scan & Status

### GET /api/status

현재 스캔 상태와 미해결 finding 수.

```json
{
  "open_findings": 3,
  "last_scan": "2026-06-07T12:00:00Z",
  "next_scan": "2026-06-07T18:00:00Z",
  "total_scans": 42,
  "registered_repos": 5
}
```

### POST /api/scan/trigger

수동으로 전체 스캔 트리거. 스케줄과 무관하게 즉시 실행.

Response: `{ "scan_id": "uuid", "status": "started" }`

### GET /api/scan/:id

특정 스캔 실행 상태 조회.

```json
{
  "id": "uuid",
  "status": "running|completed|failed",
  "started_at": "2026-06-07T12:00:00Z",
  "completed_at": null,
  "findings_count": 0
}
```

## Findings

### GET /api/findings?severity=critical&acknowledged=false

탐지된 finding 목록 조회. 쿼리 파라미터 필터링 지원.

| 파라미터 | 설명 |
|---|---|
| `severity` | critical, high, medium, info |
| `acknowledged` | true, false |
| `repo_id` | 특정 레포만 |
| `limit` | 기본 50 |
| `offset` | 페이지네이션 |

```json
{
  "total": 3,
  "findings": [
    {
      "id": 1,
      "scan_id": "uuid",
      "repo_name": "my-project",
      "file_path": "src/config.ts",
      "line": 42,
      "provider": "AWS",
      "secret_type": "AWS Access Key ID",
      "masked_fingerprint": "AKIA…7Q",
      "confidence": "high",
      "severity": "critical",
      "acknowledged": false,
      "detected_at": "2026-06-07T12:00:00Z",
      "llm_sources": ["openai", "deepseek"],
      "remediation": "1) Rotate at AWS IAM console...",
      "evidence_note": "AKIA prefix + high entropy + aws_access_key_id identifier"
    }
  ]
}
```

### PUT /api/findings/:id/acknowledge

Finding 확인 처리. Body: `{ "note": "Rotated key" }`

### GET /api/findings/:id

단일 finding 상세 조회.

## Repositories

### GET /api/repos

등록된 모니터링 레포 목록.

```json
{
  "repos": [
    {
      "id": 1,
      "name": "my-project",
      "type": "github",
      "path_or_url": "https://github.com/user/repo",
      "last_scan": "2026-06-07T12:00:00Z",
      "findings_total": 0,
      "findings_open": 0
    }
  ]
}
```

### POST /api/repos

신규 레포 등록.

Request:
```json
{
  "name": "my-project",
  "type": "github|gitlab|local",
  "path_or_url": "https://github.com/user/repo",
  "branch": "main",
  "cron_override": null
}
```

### DELETE /api/repos/:id

레포 삭제 (연관 findings는 유지).

## Dashboard

### GET /dashboard

정적 대시보드 UI 반환.

### GET /api/events

SSE (Server-Sent Events) 스트림. 대시보드 실시간 업데이트.

이벤트 타입:
- `scan:started` — 스캔 시작
- `scan:completed` — 스캔 완료 (요약 데이터)
- `finding:new` — 새 finding 발견
- `finding:acknowledged` — 확인 처리됨

## Health

### GET /api/health

서버 상태 + LLM 연결 확인.

```json
{
  "status": "ok",
  "uptime": 3600,
  "llm_providers": {
    "openai": "connected",
    "deepseek": "connected",
    "minimax": "disconnected"
  },
  "db_size_bytes": 40960,
  "version": "0.1.0"
}
```
