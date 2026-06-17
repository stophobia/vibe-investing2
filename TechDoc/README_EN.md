# TechDoc

> Technical documents evaluating and curating recently trending technologies by [Dennis Kim (@gameworkerkim)](https://github.com/gameworkerkim) -- covering serverless, cloud cost optimization, AI/LLM, and developer infrastructure.
>
> Korean version: [README.md](README.md)

---

## NEW

| Document | Description |
|---|---|
| [AI Coding Workflow Guide](effective_LLM/AI%20coding%20workflow%20claude%20code%20cursor%20chatgpt.md) | Practical AI coding workflow strategies using Claude Code, Cursor, ChatGPT -- tool selection, parallel usage, context management, cost optimization |
| [Open Code Review Guide](LLM/Open%20code%20review%20guide.md) | In-depth review of Open Code CLI -- DeepSeek V4 Pro integration, setup, optimization, command reference, tool comparison |
| [Supabase Complete Guide](OpenSource_Firebase/SuperBase_guide.md) | Open-source Firebase alternative -- PostgreSQL, Auth, Storage, Realtime, Edge Functions, Vercel integration |

---

## Table of Contents

- [Serverless & SaaS Free Tier](#serverless--saas-free-tier)
- [Cloud Cost Reduction](#cloud-cost-reduction)
- [AI / LLM](#ai--llm)
- [AI Coding Assistants](#ai-coding-assistants)
- [AI Agent & Website Standards](#ai-agent--website-standards)
- [Developer Tools & Other](#developer-tools--other)

---

## Serverless & SaaS Free Tier

Documents evaluating and comparing serverless platforms and SaaS services with free tier offerings -- practical guides for developers and startups looking to minimize infrastructure costs.

| Document | Description | Last Updated |
|---|---|---|
| [Cloudflare Free Tier Guide](CloudFlare/Cloudflare%20free%20tier%20guide.md) | Comprehensive guide to Cloudflare's free tier services including Workers, Pages, D1, R2, KV, and security features. | 2026-05-12 |
| [Oracle Cloud Free Tier Guide](OracleCloud/02.%20Oracle%20Cloud%20Free%20Tier%20Guide.md) | Korean-language guide to Oracle Cloud's Always Free Tier resources: ARM VMs, Compute, databases, networking. | 2026-05-09 |
| [Neon Review](Neon/Neon_review.md) | Evaluation of Neon.tech -- serverless PostgreSQL with branching, free tier limits, pricing, and performance analysis. | 2026-06-09 |
| [Turso Guide](SQLite_%20Turso/Turso_guide.md) | Guide to Turso -- distributed SQLite at the edge with generous free tier, covering setup, replication, and use cases. | 2026-06-09 |
| [Upstash Guide](Serverless_Redis/upstash_guide.md) | Evaluation and comparison guide for Upstash -- serverless Redis/Kafka with per-request pricing and free tier analysis. | 2026-06-09 |
| [Vercel Analysis](vercel/vercel_analysis.md) | In-depth analysis of Vercel's platform: pricing tiers, edge functions, limits, and cost-effectiveness for different workloads. | 2026-06-09 |
| [Global Free CDN Guide](github_cdn/Global%20free%20cdn%20guide.md) | Guide to leveraging free global CDNs including jsDelivr, GitHub's raw content CDN, and alternatives for static asset delivery. | 2026-06-12 |
| [GitHub CDN](github_cdn/github_cdn.md) | Technical deep-dive on using GitHub repositories as a free CDN with jsDelivr integration. | 2026-06-10 |
| [Free Email Guide](FreeEmail/FreeEmail_guide.md) | Comparison of 8 free transactional email services (Resend, Brevo, Mailgun, MailerSend, Amazon SES, Mailtrap, SendGrid, Postmark) with Vercel + Next.js recommendations. | 2026-06-14 |
| [Supabase Complete Guide](OpenSource_Firebase/SuperBase_guide.md) | Open-source Firebase alternative guide -- PostgreSQL, Auth, Storage, Realtime, Edge Functions, Vercel integration, pricing analysis. | 2026-06-14 |

## Cloud Cost Reduction

Documents focused on reducing cloud infrastructure spending -- targeted at technical decision makers and executives.

| Document | Description | Last Updated |
|---|---|---|
| [AWS Cost Reduction for CEO](AWS/Aws%20cost%20reduction%20for%20ceo.md) | Executive-level guide to AWS cost reduction strategies: reserved instances, savings plans, rightsizing, and architectural optimizations. | 2026-05-30 |

## AI / LLM

Documents covering large language models -- token optimization, local deployment, security, and knowledge management.

| Document | Description | Last Updated |
|---|---|---|
| [Caveman RTK Token Optimization](LLM/Caveman%20rtk%20token%20optimization.md) | Token optimization techniques for LLM interactions -- reducing cost and latency through prompt engineering and context management. | 2026-06-13 |
| [Quivr Guide](LLM/Quivr_guide.md) | Guide to Quivr -- an open-source second brain / knowledge management platform powered by LLMs, covering setup and usage. | 2026-06-13 |
| [Secret Scanning LLM Harness Prompt](LLM_Security/Secret%20scanning%20llm%20harness%20prompt.md) | Prompt harness design for using LLMs to scan codebases for secrets, API keys, and credentials with false-positive mitigation. | 2026-06-06 |
| [Ollama Install Guide](Local_LLM/Ollama_Install_Guilde.md) | Step-by-step installation guide for Ollama -- running local LLMs (Llama, Mistral, etc.) on personal hardware. | 2026-05-xx |
| [Headroom Complete Guide](Headroom/Headroom%20complete%20guide.md) | AI agent context compression tool -- 60-95% token savings. SmartCrusher, CodeCompressor, CacheAligner engines. Works with DeepSeek V4 Pro, Open Code, and any OpenAI/Anthropic-compatible tool. | 2026-06-12 |
| [Open Code Review Guide](LLM/Open%20code%20review%20guide.md) | In-depth review of Open Code CLI tool -- DeepSeek V4 Pro integration, installation, setup optimization, command reference, comparison with other coding tools. | 2026-06-15 |

## AI Coding Assistants

Documents comparing and guiding AI coding assistants, pricing, and integration with development environments.

| Document | Description | Last Updated |
|---|---|---|
| [MiniMax Coding Guide (KO/EN)](MiniMax%20Coding%20Guide/) | Practical guide to using MiniMax as an AI coding assistant -- VS Code integration, agent workflows, and price/performance comparison against DeepSeek, Anthropic, and OpenAI. | 2026-06-04 |
| [Visual Studio C# LLM Guide (KO/EN)](MiniMax%20Coding%20Guide/visual-studio-csharp-llm-guide.en.md) | Verified recommendations for C# coding AI assistants in Visual Studio + how to connect DeepSeek and other LLMs. | 2026-06-04 |
| [AI Coding Workflow Guide](effective_LLM/AI%20coding%20workflow%20claude%20code%20cursor%20chatgpt.md) | Practical AI coding workflow strategies using Claude Code, Cursor, ChatGPT -- tool selection, parallel usage, context management, cost optimization. | 2026-06-16 |

## AI Agent & Website Standards

Documents covering the emerging standard of building websites that AI agents can navigate, understand, and act on.

| Document | Description | Last Updated |
|---|---|---|
| [Agent-Friendly Website Guide (KO/EN/JA)](agent-friendly-website-guide/) | Trilingual guide (11 chapters + appendices) consolidating Google web.dev (2026-04), Chrome WebMCP EPP, and Jeremy Howard's llms.txt standard. Covers semantic HTML, ARIA, Schema.org JSON-LD, llms.txt, and WebMCP. CC BY 4.0. | 2026-05-19 |

## Developer Tools & Other

| Document | Description | Last Updated |
|---|---|---|
| [Bigfive Getting Started](Bigfive/Bigfive%20getting%20started.md) | Getting started guide for the Bigfive personality assessment framework -- a web-based tool implementing the Big Five personality traits model. | 2026-05-27 |

---

## Recently Updated

Documents added or significantly revised recently, ordered by commit date (newest first):

| Date | Document | Action |
|---|---|---|
| 2026-06-16 | [AI Coding Workflow Guide](effective_LLM/AI%20coding%20workflow%20claude%20code%20cursor%20chatgpt.md) | AI coding tool strategies |
| 2026-06-15 | [Open Code Review Guide](LLM/Open%20code%20review%20guide.md) | AI coding CLI deep review |
| 2026-06-14 | [Supabase Complete Guide](OpenSource_Firebase/SuperBase_guide.md) | Open-source Firebase alternative |
| 2026-06-14 | [Free Email Guide](FreeEmail/FreeEmail_guide.md) | Free email SaaS comparison |
| 2026-06-13 | [Caveman RTK Token Optimization](LLM/Caveman%20rtk%20token%20optimization.md) | LLM token savings |
| 2026-06-13 | [Quivr Guide](LLM/Quivr_guide.md) | AI as your personal assistant |
| 2026-06-12 | [Headroom Complete Guide](Headroom/Headroom%20complete%20guide.md) | LLM token compression tool |
| 2026-06-12 | [Global Free CDN Guide](github_cdn/Global%20free%20cdn%20guide.md) | Free CDN guide |
| 2026-06-10 | [GitHub CDN](github_cdn/github_cdn.md) | Updated with jsDelivr |
| 2026-06-09 | [Upstash Guide](Serverless_Redis/upstash_guide.md) | Free Redis SaaS |
| 2026-06-09 | [Turso Guide](SQLite_%20Turso/Turso_guide.md) | SQLite edge computing |
| 2026-06-09 | [Neon Review](Neon/Neon_review.md) | SaaS DB free tier |
| 2026-06-09 | [Vercel Analysis](vercel/vercel_analysis.md) | Free SaaS web server |
| 2026-06-07 | [Ollama Install Guide](Local_LLM/Ollama_Install_Guilde.md) | Local LLM install guide |
| 2026-06-07 | [Agent-Friendly Website Guide](agent-friendly-website-guide/) | AI agent-friendly web guide |
| 2026-06-06 | [Secret Scanning LLM Harness Prompt](LLM_Security/Secret%20scanning%20llm%20harness%20prompt.md) | LLM security |
| 2026-06-04 | [MiniMax Coding Guide + VS C# LLM Guide](MiniMax%20Coding%20Guide/) | AI coding assistant comparison |
| 2026-05-30 | [AWS Cost Reduction for CEO](AWS/Aws%20cost%20reduction%20for%20ceo.md) | Cost reduction |
| 2026-05-27 | [Bigfive Getting Started](Bigfive/Bigfive%20getting%20started.md) | Bigfive guide |
| 2026-05-12 | [Cloudflare Free Tier Guide](CloudFlare/Cloudflare%20free%20tier%20guide.md) | Cloudflare free tier usage |
| 2026-05-09 | [Oracle Cloud Free Tier Guide](OracleCloud/02.%20Oracle%20Cloud%20Free%20Tier%20Guide.md) | Oracle Cloud free tier usage |

---

## Note to AI Agents

This directory follows semantic structure where possible. For the fastest machine-readable entry point, see [llms.txt](llms.txt). Subdirectories with their own `llms.txt` files (e.g. `agent-friendly-website-guide/`) provide additional structured indexing.

## License

Unless otherwise noted in individual documents, documents authored by Dennis Kim are shared as reference materials. The `agent-friendly-website-guide/` is licensed under CC BY 4.0.
