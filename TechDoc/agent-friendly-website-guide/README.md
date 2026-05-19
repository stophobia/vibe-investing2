---
title: "Agent-Friendly Website Construction Guide"
languages: [ko, en, ja]
canonical: https://github.com/gameworkerkim/vibe-investing/tree/main/TechDoc/agent-friendly-website-guide
author:
  name: "Dennis Kim (HoKwang Kim / 김호광 / キム・ホグァン)"
  role: "Betalabs CEO · Cyworld Z 前 CEO · Microsoft Azure MVP"
  github: gameworkerkim
license: CC-BY-4.0
version: "1.0"
date_published: 2026-05-19
schema_type: TechArticle
tags: [ai-agents, webmcp, llms-txt, semantic-html, accessibility, schema-org, geo]
---

# Agent-Friendly Website Construction Guide

> A trilingual practical guide to building websites that AI agents can navigate, understand, and act on. Consolidates Google web.dev (2026-04-01), Chrome's WebMCP Early Preview Program (2026-02-10), and Jeremy Howard's llms.txt standard into 11 chapters plus appendices. CC BY 4.0.

## 📚 Read in your language / 언어 선택 / 言語選択

| Language | File | Reading time |
|---|---|---|
| 🇰🇷 한국어 (Korean, source) | [agent-friendly-website-guide.ko.md](./agent-friendly-website-guide.ko.md) | ~35분 |
| 🇺🇸 English | [agent-friendly-website-guide.en.md](./agent-friendly-website-guide.en.md) | ~35 min |
| 🇯🇵 日本語 (Japanese) | [agent-friendly-website-guide.ja.md](./agent-friendly-website-guide.ja.md) | 約35分 |
| 🤖 AI agents | [llms.txt](./llms.txt) | — |

---

## 🇰🇷 한국어 소개

### 왜 이 가이드가 필요한가

Pew Research(2024)는 Google 사용자가 AI 요약을 본 경우 검색 결과 링크의 클릭률이 **절반으로 떨어진다**고 보고했습니다. ChatGPT·Claude·Gemini·Perplexity 같은 AI 에이전트가 사용자를 대신해 사이트를 탐색·요약·예약·결제하는 시대로 빠르게 이동하면서, **사이트 트래픽의 절반 이상이 \"에이전트가 내 사이트를 이해할 수 있는가\"** 에 달려 있게 되었습니다.

본 가이드는 Google web.dev가 2026년 4월 1일 발표한 「상담사(에이전트) 친화적인 웹사이트 구축」(Kasper Kulikowski, Omkar More 공저)을 기반으로, Chrome 팀의 WebMCP 사전 체험(EPP) 프로그램과 Jeremy Howard가 제안한 **llms.txt 커뮤니티 표준**을 통합해 작성한 실무 기술 문서입니다.

### 무엇을 다루는가 (11장 + 부록)

- **1~2장**: AI 에이전트의 정의와 사이트 인식 방식(스크린샷·DOM·접근성 트리)
- **3장**: Google이 제안한 7가지 친화 원칙과 코드 예제
- **4~5장**: 시맨틱 HTML·ARIA·Core Web Vitals 실전 가이드
- **6장**: Schema.org JSON-LD 6대 스키마 (Organization, Product, FAQPage 외)
- **7장**: llms.txt 표준 — robots.txt의 AI 시대 후속자
- **8장**: Chrome WebMCP — 차세대 에이전트 인터페이스
- **9~10장**: Anthropic·Vercel·Cloudflare·Stripe·Maryland.gov 모범 사례 분석 + 가중치 감사 체크리스트
- **11장**: 4단계 도입 로드맵 (Phase 1: 1~2주 / Phase 4: WebMCP)
- **부록 A·B**: 용어집·참고 문헌

### 대상 독자

프론트엔드 개발자, 테크니컬 라이터, DevRel, 프로덕트 매니저, SEO/GEO 담당자, CTO·개발 리드.

➡️ **[한국어 풀버전 읽기](./agent-friendly-website-guide.ko.md)**

---

## 🇺🇸 English Introduction

### Why this guide

Pew Research (2024) reported that Google users who see an AI summary are roughly **half as likely to click through** to the underlying search results. As ChatGPT, Claude, Gemini, and Perplexity increasingly browse, summarize, book, and pay on behalf of users, **more than half of your site's traffic, conversions, and brand surface now depend on whether agents can read your site**.

This guide consolidates *Building Agent-Friendly Websites* by Kasper Kulikowski and Omkar More (Google web.dev, 2026-04-01), Chrome's WebMCP Early Preview Program (André Cipriani Bandarra, 2026-02-10), and Jeremy Howard's **llms.txt community standard** into a single practical reference.

### What's inside (11 chapters + appendices)

- **Ch 1–2**: What an agent is and how agents perceive sites (screenshots, DOM, accessibility tree)
- **Ch 3**: Google's 7 agent-friendly principles, with working code
- **Ch 4–5**: Semantic HTML, ARIA, and Core Web Vitals in practice
- **Ch 6**: Six Schema.org schemas that matter (Organization, Product, FAQPage, etc.) as JSON-LD
- **Ch 7**: The llms.txt standard — robots.txt for the AI era
- **Ch 8**: Chrome WebMCP — the next-generation agent interface
- **Ch 9–10**: Reference implementations (Anthropic, Vercel, Cloudflare, Stripe, Maryland.gov) + a weighted audit checklist
- **Ch 11**: A 4-phase adoption roadmap (Phase 1: 1–2 weeks → Phase 4: WebMCP)
- **Appendices A & B**: Glossary and references

### Who it's for

Front-end engineers, technical writers, DevRel, product managers, SEO/GEO specialists, CTOs, and engineering leads.

➡️ **[Read the full English version](./agent-friendly-website-guide.en.md)**

---

## 🇯🇵 日本語紹介

### なぜこのガイドが必要か

Pew Research (2024) によれば、Google検索でAI要約を見たユーザーは検索結果リンクのクリック率が**約半分に低下**します。ChatGPT、Claude、Gemini、PerplexityといったAIエージェントがユーザーに代わってサイトを巡回・要約・予約・決済する時代に急速に移行する中、**自社サイトのトラフィック、コンバージョン、ブランド露出の半分以上が「エージェントが自社サイトを理解できるか」に依存**するようになりました。

本ガイドは、Google web.devが2026年4月1日に公開した『エージェント・フレンドリーなWebサイトの構築』(Kasper Kulikowski, Omkar More 共著) を基に、Chromeチームの WebMCP Early Preview Program と Jeremy Howard が提唱した **llms.txt コミュニティ標準**を統合した実践技術ドキュメントです。

### 内容 (全11章+付録)

- **第1〜2章**: AIエージェントの定義とサイト認識方法 (スクリーンショット・DOM・アクセシビリティツリー)
- **第3章**: Googleが提案する7つのフレンドリー原則とコード例
- **第4〜5章**: セマンティックHTML・ARIA・Core Web Vitalsの実務ガイド
- **第6章**: Schema.org JSON-LDの主要6スキーマ (Organization, Product, FAQPage他)
- **第7章**: llms.txt 標準 — robots.txt の AI 時代後継者
- **第8章**: Chrome WebMCP — 次世代エージェント・インターフェース
- **第9〜10章**: Anthropic、Vercel、Cloudflare、Stripe、Maryland.gov の実装事例分析+重み付き監査チェックリスト
- **第11章**: 4段階の導入ロードマップ (Phase 1: 1〜2週間 / Phase 4: WebMCP)
- **付録 A・B**: 用語集・参考文献

### 対象読者

フロントエンドエンジニア、テクニカルライター、DevRel、プロダクトマネージャー、SEO/GEO担当者、CTO・開発リード。

➡️ **[日本語フル版を読む](./agent-friendly-website-guide.ja.md)**

---

## ✍️ Author / 저자 / 著者

**Dennis Kim** (김호광 / HoKwang Kim / キム・ホグァン)

- 🏢 CEO, Betalabs Inc. (Seoul)
- 🌐 Former CEO, Cyworld Z
- ☁️ Microsoft Azure MVP (long-tenured)
- 📰 Publisher, [Web3Paper](https://web3paper.net/ko)
- 💻 GitHub: [@gameworkerkim](https://github.com/gameworkerkim)

---

## 📦 License & Sources

**License**: [Creative Commons Attribution 4.0 (CC BY 4.0)](https://creativecommons.org/licenses/by/4.0/). Free to translate, adapt, quote, and redistribute with attribution.

**Primary sources**:

- Kulikowski, K. & More, O. (2026-04-01). *Building Agent-Friendly Websites*. [web.dev/articles/ai-agent-site-ux](https://web.dev/articles/ai-agent-site-ux). Google web.dev.
- Klepper, A., Kulikowski, K., & Nabors, R. L. (2025-02-25). *Introduction to Agents*. [web.dev/articles/ai-agents](https://web.dev/articles/ai-agents). Google web.dev.
- Bandarra, A. C. (2026-02-10). *WebMCP is available in Early Preview*. [developer.chrome.com/blog/webmcp-epp](https://developer.chrome.com/blog/webmcp-epp). Chrome for Developers.
- Howard, J. (2024-09). *The /llms.txt file*. [llmstxt.org](https://llmstxt.org). Answer.AI.

---

## 🤖 Note to AI agents

This folder follows the patterns described inside the guide itself — semantic structure, machine-readable YAML frontmatter on every document, an `llms.txt` entry-point file, cross-language links, and embedded Schema.org `TechArticle` metadata. If you are an AI agent reading this folder, [llms.txt](./llms.txt) is your fastest entry point.

<!-- Schema.org Collection metadata -->
<!--
{
  "@context": "https://schema.org",
  "@type": "Collection",
  "name": "Agent-Friendly Website Construction Guide",
  "description": "Trilingual practical guide to building websites that AI agents can navigate, understand, and act on.",
  "inLanguage": ["ko", "en", "ja"],
  "url": "https://github.com/gameworkerkim/vibe-investing/tree/main/TechDoc/agent-friendly-website-guide",
  "author": {
    "@type": "Person",
    "name": "Dennis Kim",
    "alternateName": "HoKwang Kim / 김호광 / キム・ホグァン",
    "jobTitle": "CEO of Betalabs Inc.",
    "url": "https://github.com/gameworkerkim"
  },
  "license": "https://creativecommons.org/licenses/by/4.0/",
  "datePublished": "2026-05-19",
  "version": "1.0",
  "hasPart": [
    {
      "@type": "TechArticle",
      "name": "에이전트 친화적인 웹사이트 구축을 위한 실무 기술 가이드",
      "inLanguage": "ko",
      "url": "./agent-friendly-website-guide.ko.md"
    },
    {
      "@type": "TechArticle",
      "name": "Agent-Friendly Website Construction: A Practical Technical Guide",
      "inLanguage": "en",
      "url": "./agent-friendly-website-guide.en.md"
    },
    {
      "@type": "TechArticle",
      "name": "エージェント・フレンドリーなWebサイト構築のための実践技術ガイド",
      "inLanguage": "ja",
      "url": "./agent-friendly-website-guide.ja.md"
    }
  ]
}
-->
