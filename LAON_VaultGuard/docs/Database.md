# Database Design

## repositories

Stores monitored repositories.

| Field | Type |
|---------|---------|
| id | INTEGER |
| name | TEXT |
| type | TEXT |
| path_or_url | TEXT |

## scan_results

Stores secret findings.

| Field | Type |
|---------|---------|
| id | INTEGER |
| repo_id | INTEGER |
| file_path | TEXT |
| secret_type | TEXT |
| risk_level | TEXT |

## alert_config

Notification configuration.

## audit_log

System audit history.
