# API Reference

## GET /api/status

Returns current scan status.

Response:

```json
{
  "open_findings": 3,
  "last_scan": "2026-06-07T12:00:00Z"
}
```

## GET /api/history

Returns historical findings.

## PUT /api/acknowledge/:id

Marks a finding as acknowledged.

## GET /dashboard

Serves dashboard UI.
