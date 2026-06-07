# LAON VaultGuard — VS Code Extension

> Real-time secret detection in VS Code. LLM-powered multi-provider cross-validation.

## Features

- **Real-time highlighting** — suspect secrets underlined with dashed red border as you type
- **Problems panel integration** — detected secrets shown in VS Code's Problems panel (masked fingerprints only)
- **Scan on save** — automatically scans file when you save (configurable)
- **Status bar indicator** — shows `LAON: clean` or `LAON: N` with warning count
- **Deep LLM scan** — `Ctrl+Shift+P → LAON VaultGuard: Scan Workspace` runs full multi-LLM pipeline
- **Context menu** — right-click any file → Scan Current File for Secrets

## Configuration

| Setting | Default | Description |
|---|---|---|
| `laon-vaultguard.enabled` | `true` | Enable/disable extension |
| `laon-vaultguard.scanOnSave` | `true` | Scan file on save |
| `laon-vaultguard.scanOnOpen` | `false` | Scan file when opened |
| `laon-vaultguard.severity` | `medium` | Minimum severity: critical, high, medium, all |

## Requirements

- LAON VaultGuard v0.5+ installed (`cd LAON_VaultGuard && npm install`)
- Storage engine: **SQLite** (WAL, ACID) or **JSON** (legacy) — both supported
- At least one LLM provider configured (DeepSeek, Claude, OpenAI, or Ollama)
- For deep scan: `npm run setup` completed

## Detected Patterns

| Pattern | Example |
|---|---|
| AWS Access Key | `AKIA...` |
| GitHub Token | `ghp_...` |
| OpenAI/LLM Key | `sk-...` |
| JWT Token | `eyJ...` |
| Private Key | `-----BEGIN PRIVATE KEY-----` |
| DB Connection String | `mongodb://user:pass@host` |
| Hardcoded Password | `password = "..."` |
| Naver Cloud Key | `NCP_ACCESS_KEY=...` |

## Commands

- `LAON VaultGuard: Scan Workspace` — Deep LLM scan of entire workspace
- `LAON VaultGuard: Scan Current File` — Quick regex scan of active file
- `LAON VaultGuard: Clear Secret Warnings` — Remove all diagnostics

## Security

This extension never sends your code to external services without your consent.
- **Regex scanning** runs entirely locally, no network calls
- **Deep LLM scan** uses your configured LAON VaultGuard providers
- **All fingerprints are masked** — `AKIA****7Q` instead of full key
- **Differential Privacy** is enabled by default in LAON VaultGuard
