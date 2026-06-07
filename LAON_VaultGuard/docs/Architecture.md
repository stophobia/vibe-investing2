# Architecture

## High-Level Flow

```text
Config
  ↓
Scheduler
  ↓
Git Monitor
  ↓
Diff Extraction
  ↓
LLM Harness
  ↓
Result Analysis
  ↓
Database
  ↓
Alert Modules
  ↓
Dashboard
```

## Components

### Scheduler
Periodic repository scanning.

### Git Monitor
Collects local and remote repository changes.

### LLM Harness
Analyzes diffs for exposed secrets.

### Alert Engine
Slack, Telegram, Email, Dashboard.

### Dashboard
Real-time monitoring and remediation tracking.
