# BACKTEST LOG — 2026-06-07 v0.6

```

══════════════════════════════════
  LAON VaultGuard v0.5 Backtest
══════════════════════════════════

── 1. Config ──
  ✅ PORT default = 3101
  ✅ HOST is set
  ✅ LLM_MODE is valid
  ✅ storageEngine exists
  ✅ scan timeout > 0
  ✅ cache enabled by default
  ✅ validateConfig is a function

── 2. Differential Privacy ──
  ✅ masks AWS key (AKIA...)
  ✅ masks GitHub token (ghp_)
  ✅ masks OpenAI key (sk-)
  ✅ masks JWT token
  ✅ masks private key block
  ✅ masks hardcoded password
  ✅ masks DB connection string
  ✅ masks NCP access key
  ✅ does not mask non-secrets
  ✅ summarizeMasking returns correct stats

── 3. Storage — SQLite ──
  ✅ DATA_DIR exists
  ✅ DB_PATH file created
  ✅ addRepo returns valid repo
  ✅ listRepos includes test repo
  ✅ getRepo finds by id
  ✅ updateRepoLastScan sets timestamp
  ✅ saveFindings persists
  ✅ listFindings returns with filter
  ✅ acknowledgeFinding updates
  ✅ unacknowledgeFinding reverts
  ✅ addFindingComment appends
  ✅ countOpenFindings returns count
  ✅ saveScanRun persists
  ✅ getLatestScan returns most recent
  ✅ getScanCount > 0
  ✅ getScanHistory returns entries
  ✅ getAlertConfig returns defaults
  ✅ updateAlertConfig persists
  ✅ readJson returns fallback for missing file
  ✅ writeJson + readJson round-trip

── 3b. Storage — JSON (legacy) ──
  ✅ JSON addRepo/listRepos
  ✅ JSON removeRepo
  ✅ removeRepo cleans up

── 4. SARIF Export ──
  ✅ No open findings to export.
  ✅ generates valid SARIF v2.1.0
  ✅ severity mapping: critical → error
  ✅ severity mapping: medium → warning
  ✅ SARIF output is valid JSON

── 5. Prometheus Metrics ──
  ✅ metrics returns text/plain
  ✅ metrics includes counter
  ✅ metrics includes gauge
  ✅ metrics includes histogram
  ✅ metrics format is valid Prometheus

── 6. Candidate Filter ──
  ✅ grep pattern includes AKIA
  ✅ grep pattern includes ghp_
  ✅ grep pattern includes sk-
  ✅ grep pattern is valid regex

── 7. Version ──
  ✅ package.json version = 0.5.0

══════════════════════════════════
  Results: 54 passed, 0 failed, 0 skipped
══════════════════════════════════
  ✅ All 54 tests passed.
```
