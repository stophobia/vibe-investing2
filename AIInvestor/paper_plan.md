# Research Data Collection Plan
## Empirical Validation of Semantic Edge Caching for Repetitive LLM Queries

**Companion Document for**: *Semantic Edge Caching for Repetitive LLM Queries*
**Author**: HoKwang Kim
**Target Venue**: IEEE Transactions on Cloud Computing
**Document Version**: 1.0 (English) — 2026-05-05
**Companion Architecture Document**: `jeunggwon-architecture-v3.0-ko.md` (Korean)

---

## Abstract

This document specifies the data collection methodology for empirically validating the hypotheses presented in *"Semantic Edge Caching for Repetitive LLM Queries"*. Where the original paper relies primarily on simulation, this companion plan describes how a deployed production chatbot ("Jeunggwon Chatbot") serves as a real-world data collection platform across two channels (Telegram and mobile native apps) under a low-cost serverless architecture on Microsoft Azure. The plan covers: (1) mapping of the paper's five core hypotheses to measurable signals, (2) anonymization and consent protocols satisfying Korean Personal Information Protection Act and GDPR, (3) Azure Cosmos DB schema with automatic time-to-live policies, (4) channel-stratified statistical analysis methods, and (5) ethics review preparation including IRB exemption justification.

**Keywords**: Semantic Caching, LLM Inference, CDN-inspired Architecture, Empirical Validation, Anonymized Telemetry, Multi-channel Data Collection

---

## Table of Contents

1. [Background and Motivation](#1-background-and-motivation)
2. [Hypothesis Mapping](#2-hypothesis-mapping)
3. [System Architecture for Data Collection](#3-system-architecture-for-data-collection)
4. [Data Schema and Cosmos DB Containers](#4-data-schema-and-cosmos-db-containers)
5. [Anonymization Protocol](#5-anonymization-protocol)
6. [Informed Consent Workflow](#6-informed-consent-workflow)
7. [Multi-Channel Comparative Analysis](#7-multi-channel-comparative-analysis)
8. [Statistical Analysis Methods](#8-statistical-analysis-methods)
9. [Cost Impact](#9-cost-impact)
10. [Ethics Review and IRB Preparation](#10-ethics-review-and-irb-preparation)
11. [Timeline Aligned with Paper Submission](#11-timeline-aligned-with-paper-submission)
12. [Threats to Validity](#12-threats-to-validity)
13. [Reproducibility and Open Data](#13-reproducibility-and-open-data)

---

## 1. Background and Motivation

### 1.1 Gap in the Original Paper

The original manuscript proposes a CDN-inspired semantic edge caching architecture that reduces redundant LLM inference. Its central claim is that human queries follow repetitive statistical patterns, enabling high cache hit rates with consequent reductions in latency, energy consumption, and GPU workload. However, the original results in Sections 11–14 (Cache Hit Rate, GPU Workload Reduction, Cost Reduction, Energy Impact) rely on simulation rather than measurements from a deployed system serving real users.

This data collection plan addresses that gap. We deploy a production chatbot serving Korean retail investors across two channels and collect anonymized query telemetry continuously, producing a dataset that allows the simulation results to be either confirmed or refined with empirical evidence.

### 1.2 Why a Financial Chatbot

Financial-domain chatbots are well suited to validate the Query Repetition Hypothesis for three reasons:

1. **Strong temporal structure**: Market opening and closing hours impose predictable query bursts (e.g., U.S. market open at 22:30 KST creates a wave of queries about NASDAQ-listed equities), providing natural ground truth for the time-clustering claim in Section 7 (Predictive Cache Warming).
2. **Bounded vocabulary**: A finite number of tickers, sectors, and indices constrains the semantic space, making the Zipf-like popularity distribution claim in Section 4 (Statistical Model of Query Popularity) easier to test.
3. **Persona-stratified queries**: The chatbot offers eight distinct investor personas, each attracting users with different question styles. This provides a natural experimental factor for measuring how persona choice affects cache hit rates.

### 1.3 Why Two Channels (Telegram + Mobile)

Single-channel data is at risk of channel-specific bias. By collecting from both Telegram (command-driven, short queries) and native mobile apps (natural language, longer queries), we strengthen external validity. Channel comparison itself becomes a novel contribution beyond the original paper's scope.

---

## 2. Hypothesis Mapping

The paper presents five testable claims. Each is mapped below to a measurable signal collected by the production system.

| Paper Section | Claim | Measurement in Production System |
|---|---|---|
| §3 Query Repetition Hypothesis | Human queries follow repetitive statistical patterns. | Repetition rate per command, per ticker, per time-of-day in `query_stats` container; deduplication ratio over rolling windows. |
| §4 Statistical Model of Query Popularity | Query popularity follows a power-law (Zipf) distribution. | Daily aggregation in `research_popularity_daily` container; goodness-of-fit test against Zipf with maximum-likelihood estimation of the exponent. |
| §6 Semantic Cache Pipeline | Embedding-based ANN search can identify semantically equivalent queries above a similarity threshold. | Cosine similarity distribution stored in `research_cache_events`; correlation between similarity score and downstream user feedback (thumbs up/down). |
| §7 Predictive Cache Warming | Trending signals enable proactive cache population. | Pre-warming triggered 30 minutes before market-open clusters; comparison of hit rates with vs. without pre-warming. |
| §11–14 Hit Rate / GPU / Cost / Energy | 60–90% cache hit rates yield proportional savings in GPU load, dollar cost, and energy. | Direct measurement: hit rate from `research_cache_events`, dollar cost from DeepSeek API billing, GPU/energy via published per-token energy figures. |

**Auxiliary hypothesis introduced by this plan**:

| Plan-introduced Hypothesis | Measurement |
|---|---|
| H6 (Channel-clustered queries) | Telegram and mobile users exhibit distinguishable query distributions. Tested via Kolmogorov–Smirnov on length, command distribution, and time-of-day distributions. |
| H7 (Time-clustered queries) | Queries arriving in the same KST hour form semantic clusters in embedding space. Tested via silhouette score on K-means clustering of hourly embeddings. |

---

## 3. System Architecture for Data Collection

### 3.1 Production Stack (Summary)

| Component | Choice | Reason |
|---|---|---|
| Compute | Azure Functions (Flex Consumption) | Pay-per-request serverless, no idle cost. |
| Cache | Azure CDN + Blob Storage | Mature CDN inspiration aligns with paper's framing. |
| Vector Store | Azure Cosmos DB with DiskANN vector index | Single-system telemetry plus ANN queries for §6 validation. |
| LLM Provider | DeepSeek V4-Pro / V4-Flash | Cost-efficient, transparent token pricing for §13 cost reduction analysis. |
| Embedding | Azure OpenAI `text-embedding-3-small` (1536-d) | Stable, low-cost, separate from LLM inference cost. |
| Channels | Telegram bot + iOS/Android native apps (React Native + Expo) | Two-channel coverage as discussed in §1.3. |
| Identity | SHA-256 with rotated salt in Azure Key Vault | One-way anonymization per §5. |

### 3.2 Telemetry Plane vs. Production Plane

The system runs two logical planes sharing the same Azure Functions backend:

- **Production plane**: Serves user queries, returns LLM/cache responses. Latency budget is strict.
- **Telemetry plane**: Asynchronously persists anonymized signals to Cosmos DB. Failures are non-blocking; telemetry loss does not degrade user experience.

A producer–consumer pattern using Azure Storage Queues ensures the production plane is never blocked by Cosmos DB write latency. Telemetry messages enqueue with a TTL of 24 hours; if the consumer cannot drain the queue within that window, the messages expire silently rather than backing up indefinitely.

### 3.3 Sampling Strategy

For high-volume periods (estimated peak: 1,000 queries per minute during U.S. market open), full collection is feasible because telemetry write costs are dominated by Cosmos DB request units rather than network. We collect 100% of:

- Cache events (hit/miss flag, similarity score)
- Latency observations (server-side, network-side from mobile clients)
- Query metadata (length, command, channel, KST hour)

We collect 100% of embeddings, since the embedding has already been computed for cache lookup and storing it costs only Cosmos DB write RU (no additional LLM call).

We collect raw query text only from users who explicitly opted in (see §6).

---

## 4. Data Schema and Cosmos DB Containers

Four research-dedicated containers are added to the existing `jeunggwon` database. Each has a default time-to-live (TTL) policy that automatically deletes records, simplifying compliance and reducing storage cost (the storage cost reduction itself is a separate finding for §13).

### 4.1 `research_query_embeddings`

Purpose: Validate §6 (Semantic Cache Pipeline) and H7 (Time-clustered queries).

```json
{
  "id": "<uuid>",
  "anon_user_id": "<sha256-16-hex>",
  "embedding": [/* 1536 float32 */],
  "query_length_chars": 27,
  "query_text_optional": null,
  "channel": "telegram | mobile_ios | mobile_android",
  "timestamp": "2026-05-05T22:31:14.523Z",
  "kst_hour": 7,
  "kst_weekday": "Tuesday",
  "date": "2026-05-05",
  "ttl": 7776000
}
```

- `query_text_optional` is populated only with explicit consent.
- Partition key: `/date` (one partition per UTC day, simplifying TTL and time-window queries).
- TTL: 90 days (7,776,000 seconds).
- Vector index: DiskANN on `embedding` for ANN queries over the most recent 90 days.

### 4.2 `research_cache_events`

Purpose: Validate §11 (Cache Hit Rate Results) and the §6 similarity-threshold claim.

```json
{
  "id": "<uuid>",
  "anon_user_id": "<sha256-16-hex>",
  "cache_hit": true,
  "similarity_score": 0.962,
  "model_fallback": null,
  "channel": "telegram",
  "timestamp": "...",
  "date": "2026-05-05",
  "ttl": 7776000
}
```

- `similarity_score` is null on cache miss; `model_fallback` is null on cache hit.
- Partition key: `/date`. TTL: 90 days.

### 4.3 `research_latency`

Purpose: Validate §9 (Latency Analysis).

```json
{
  "id": "<uuid>",
  "anon_user_id": "<sha256-16-hex>",
  "latency_ms_total": 412,
  "latency_ms_server": 318,
  "latency_ms_network": 94,
  "cache_hit": true,
  "model_used": "cache | deepseek-v4-flash | deepseek-v4-pro",
  "channel": "mobile_ios",
  "timestamp": "...",
  "date": "2026-05-05",
  "ttl": 7776000
}
```

- For Telegram, only `latency_ms_total` (server-side) is available.
- For mobile clients, network-side latency is measured client-side and uploaded with the next telemetry beacon, then merged server-side using `anon_user_id` and request ID correlation within a 60-second window.
- Partition key: `/date`. TTL: 90 days.

### 4.4 `research_popularity_daily`

Purpose: Validate §4 (Statistical Model of Query Popularity).

```json
{
  "id": "2026-05-05",
  "date": "2026-05-05",
  "command_distribution": {
    "/btc": 4823,
    "/us": 3104,
    "/summary": 1872
  },
  "ticker_distribution": {
    "NVDA": 2104,
    "TSLA": 1876,
    "005930": 1502
  },
  "natural_language_top_50": [
    {"normalized_query": "...", "count": 412}
  ],
  "ttl": 31536000
}
```

- Partition key: `/date`. TTL: 365 days (1 year) — enables year-over-year analysis without retaining individual records.
- This container is *aggregated*, not per-event. The aggregation runs nightly via a scheduled Azure Function over the previous day's `research_query_embeddings`.

### 4.5 Container Initialization

```python
async def create_research_containers(db):
    """Idempotent container creation with TTL and vector indexing."""
    await db.create_container_if_not_exists(
        id="research_query_embeddings",
        partition_key=PartitionKey(path="/date"),
        default_ttl=7_776_000,  # 90 days
        indexing_policy={
            "indexingMode": "consistent",
            "vectorIndexes": [{"path": "/embedding", "type": "diskANN"}]
        }
    )
    await db.create_container_if_not_exists(
        id="research_cache_events",
        partition_key=PartitionKey(path="/date"),
        default_ttl=7_776_000
    )
    await db.create_container_if_not_exists(
        id="research_latency",
        partition_key=PartitionKey(path="/date"),
        default_ttl=7_776_000
    )
    await db.create_container_if_not_exists(
        id="research_popularity_daily",
        partition_key=PartitionKey(path="/date"),
        default_ttl=31_536_000  # 365 days
    )
```

---

## 5. Anonymization Protocol

### 5.1 Identity Hashing

User identifiers from each channel (Telegram user ID, mobile device install ID) are converted to a 64-character hex string truncated to 16 characters using SHA-256 with a server-side salt:

```
anon_user_id = sha256(salt + ":" + raw_user_id)[0:16]
```

The salt is stored in Azure Key Vault and is **not** logged anywhere. The salt is rotated every 90 days, which means that a user appearing before and after the rotation receives a different `anon_user_id`. This is intentional: it prevents long-term re-identification while still allowing short-term session analysis (within a 90-day rotation window).

### 5.2 What Is Stored vs. What Is Not Stored

| Stored | Not stored |
|---|---|
| Anonymous user hash | Raw Telegram/device ID |
| Embedding (1536-d float vector) | User name, profile photo, phone number |
| Query length (character count) | Query text (unless explicit consent) |
| Channel, KST hour, weekday, date | IP address, geolocation, user-agent |
| Cache hit flag, similarity score | Account creation date, payment info |
| Latency in milliseconds | Cookie or session token |

### 5.3 Re-identification Risk Assessment

Re-identification of an individual from the stored data would require:

1. Access to both the database and the Key Vault salt (separate access controls).
2. Knowledge of when a specific user issued a specific query.
3. The ability to enumerate all `raw_user_id` candidates and compare hashes.

In a population of an estimated 10,000 active Telegram users plus an unknown number of mobile installs, the search space is large enough that linkage attacks are infeasible without access to the Key Vault salt. The salt rotation further reduces persistence of any link.

The embedding itself does not contain identifying information beyond the semantic content of the (potentially sensitive) query. For users who have opted in to query-text storage, we apply an additional safeguard: queries containing personally identifiable patterns (Korean resident registration numbers, credit card patterns, full email addresses) are detected via regex and replaced with `[REDACTED]` before storage.

### 5.4 Right to Erasure

Although individual events cannot be linked to a specific user without the salt, users may request blanket erasure of all data potentially associated with their account by contacting `privacy@jeunggwon.com`. On request, we accept the user's current Telegram ID or device install ID, compute the corresponding `anon_user_id` under the active salt, and delete all records matching that hash within 7 days. Records issued under previously rotated salts cannot be deleted by hash matching but will expire automatically via TTL.

---

## 6. Informed Consent Workflow

### 6.1 Two-Tier Consent

| Tier | Default | Data collected |
|---|---|---|
| Operational tier | Opt-out only (data necessary for service operation) | `anon_user_id`, channel, command, embedding, cache event, latency, KST hour |
| Research-extended tier | Opt-in only | All of the above plus raw query text |

The operational tier covers data the system must collect to function at all (caching itself requires embeddings; billing requires per-call accounting). Users may opt out by declining to use the service. The research-extended tier covers raw query text and is collected only after a clear, separate consent event.

### 6.2 Consent Message (Excerpted, English Translation of Korean Original)

> **Research Data Collection Notice**
>
> This bot collects anonymized data to support a research study on LLM caching efficiency, intended for submission to IEEE Transactions on Cloud Computing.
>
> **Always collected (required for service operation, cannot be opted out)**:
> - Time of query, channel (Telegram/mobile), command type
> - Response latency, cache hit/miss flag
> - Query length and semantic embedding (cannot be reversed to original text)
>
> **Collected only with your consent**:
> - Raw query text (including persona, tickers, free-form natural language)
>
> All data is anonymized via one-way hash; raw identifiers are never stored. Records are automatically deleted after 90 days to one year depending on category. Research outputs are released only as academic papers; no individual is identifiable.
>
> [I consent to all data collection — most helpful for the research]
> [Operational data only — default]
> [View full data policy]

### 6.3 Consent Storage

Consent events are stored in the `users` container with `research_consent` and `research_consent_at` fields. The `research_consent` flag is checked at every query before deciding whether to populate `query_text_optional`. Users may revoke consent via `/research_revoke`, after which `query_text_optional` is removed from all records associated with their `anon_user_id`.

### 6.4 First-Response Notice

Independent of consent, every user receives a one-time notice immediately after their first response, regardless of channel. This notice is described in the architecture document §5.6 and contains four points: (1) AI may produce errors, (2) data is used to improve service and research, (3) personal information is anonymized and not stored in identifiable form, (4) responses are not financial advice. The notice is shown exactly once per user lifetime, tracked via a flag in the `users` container.

---

## 7. Multi-Channel Comparative Analysis

Channel-stratified analysis is a primary contribution beyond the original paper. We hypothesize that Telegram and mobile users exhibit distinct query patterns due to interface affordances:

| Dimension | Telegram (expected) | Mobile (expected) |
|---|---|---|
| Median query length | Short (commands like `/btc`) | Longer (natural language) |
| Time-of-day skew | Commute hours and lunch breaks | Higher late-night share |
| Cache hit rate | Higher (repeated commands compress vocabulary) | Lower (natural language disperses queries) |
| Server-side latency | Pure backend time | Same backend time but with longer end-to-end latency due to network |
| Persona preference | To be measured | To be measured |
| Follow-up rate | Lower (single-shot) | Higher (conversational) |

For each dimension, we test whether channels are statistically distinguishable using:

- **Length distribution**: Two-sample Kolmogorov–Smirnov test.
- **Time-of-day distribution**: Chi-square test on hourly histograms.
- **Hit rate**: Two-proportion z-test.
- **Latency**: Mann–Whitney U test (latency is heavy-tailed; t-test inappropriate).
- **Persona preference**: Chi-square test of independence between channel and persona.
- **Follow-up rate**: Two-proportion z-test on the proportion of users issuing a second query within 60 seconds.

If channel differences are statistically significant (p < 0.01 with Bonferroni correction across dimensions), the original paper's results are conditional on channel mix. We will report channel-stratified hit rates and present an overall figure only with explicit weighting.

---

## 8. Statistical Analysis Methods

### 8.1 Cache Hit Rate (§11 of the paper)

Aggregated nightly:

```sql
SELECT
  c.channel,
  c.date,
  COUNT(1) AS total,
  SUM(c.cache_hit ? 1 : 0) AS hits,
  SUM(c.cache_hit ? 1 : 0) * 1.0 / COUNT(1) AS hit_rate
FROM c
WHERE c.date >= '2026-05-01'
GROUP BY c.channel, c.date
```

We report rolling 7-day mean and 95% confidence intervals via the Wilson score interval.

### 8.2 Zipf Fit for Query Popularity (§4)

For each daily aggregation in `research_popularity_daily`:

1. Sort queries by frequency descending.
2. Fit `frequency(rank) = C * rank^(-s)` via maximum-likelihood estimation of `s`.
3. Test goodness of fit with the Kolmogorov–Smirnov statistic.
4. Report median `s` across days and the proportion of days where the Zipf fit is not rejected at α = 0.05.

The original paper claims `s ≈ 1.0` for human queries; we report whether this is observed in the financial chatbot domain.

### 8.3 Time Clustering (H7, supports §7)

Daily K-means clustering on a sample of 10,000 embeddings stratified by KST hour:

1. Reduce dimensionality from 1536 to 50 via PCA.
2. Cluster with K=24 (one cluster per hour as the working hypothesis).
3. Compute silhouette score.
4. Compute confusion matrix between cluster assignment and KST hour.
5. Visualize via UMAP projection to 2D, colored by KST hour.

If the confusion matrix shows strong diagonal structure (i.e., clusters align with hours of day), H7 is supported, providing direct evidence for §7's predictive warming.

### 8.4 Pre-warming Effectiveness

Run a controlled comparison: in the live system, alternate days with pre-warming enabled vs. disabled (assignment fixed at midnight UTC). Compare hit rates between the two conditions for queries arriving in the first 30 minutes after market opens. The treatment effect is estimated via the difference in hit rates with bootstrap confidence intervals.

This is technically a quasi-experiment (not randomized at the user level), but the alternation pattern controls for day-of-week and longer-term trends.

### 8.5 Cost and Energy (§13–14)

Cost per query: derived from DeepSeek API billing (input + output tokens × per-token rate, with cache-hit discount applied). Aggregated to monthly cost. The counterfactual "cost without caching" is estimated by applying full inference cost to every query in the dataset.

Energy: per-token energy estimates from published benchmarks (e.g., for similar model-size GPU inference) multiplied by token count. We report total kWh saved and the equivalent carbon savings under a published grid emission factor.

---

## 9. Cost Impact

The data collection layer is designed to add minimal cost on top of operational expenses.

| Item | Estimated monthly cost (at 3,000 DAU baseline) |
|---|---|
| Cosmos DB serverless: 4 additional containers with TTL | $3–5 |
| Embedding storage (1.5 KB × 300,000 events) | ~450 MB → Blob $0.01 |
| Embedding dimensionality: stored at full 1536 dimensions | (already computed for caching, no extra LLM cost) |
| Mobile push notifications (Azure Notification Hubs free tier) | $0 (within free tier of 1M pushes/month) |
| Apple Developer Program | $99/year ≈ $8.25/month |
| Google Play Console | $25 one-time |
| **Total monthly add-on** | **approximately $12–16** |

Channel expansion plus research data collection together add less than $20 per month in the operational baseline scenario, well within the project's low-cost operating principle.

---

## 10. Ethics Review and IRB Preparation

### 10.1 Applicable Regulatory Framework

| Jurisdiction | Regulation | Applicability |
|---|---|---|
| Korea | Personal Information Protection Act (PIPA) | Primary applicability (Korean-headquartered service, primarily Korean users). |
| Korea | Bioethics and Safety Act (with IRB oversight) | Applicable if the research is classified as human subjects research. The hashed-only nature and absence of intervention may qualify for exemption. |
| EU | GDPR | Applicable to any EU user of the mobile app. Storage minimization, right to erasure, and lawful basis (consent for opt-in tier; legitimate interest for operational tier) are addressed in §5–6. |
| US | Common Rule | Not applicable for non-US-based research, but we follow the substantive requirements where relevant. |

### 10.2 IRB Exemption Argument

We will request IRB review with a request for exemption under the following arguments:

1. **No intervention or interaction beyond service use**: Research data is observational telemetry from users who voluntarily engage with a publicly available service.
2. **No identifiable private information**: Operational-tier data is anonymized at collection. The research-extended tier uses opt-in consent and stores text only after PII redaction.
3. **Standard data protection**: Records are stored encrypted at rest in Azure Cosmos DB, access-controlled via RBAC, and automatically deleted via TTL.
4. **Minimal risk**: The research presents no greater than minimal risk to subjects, as defined by the Common Rule and analogous Korean regulations.

If exemption is denied, we will pursue full IRB review with the same materials, expected to add 2–3 months to the timeline.

### 10.3 Data Sharing Plan

If the paper is accepted:

- **Aggregated statistics** (hourly hit rates, Zipf parameters per day) will be published as supplementary material.
- **De-identified per-event data** (without raw query text, with `anon_user_id` re-hashed under a publication-specific salt) may be released on a controlled-access basis through the IEEE Dataport service, requiring institutional approval to download.
- **Raw query text data** will not be publicly released. It is accessible only to the research team and only for the duration of the analysis.

### 10.4 Data Retention Beyond Project End

When the data collection phase ends (anticipated 12 months from launch), the operational TTL continues to function and within 1 year all per-event records will have been deleted. The aggregated daily popularity records (`research_popularity_daily`) persist for 365 days from creation but contain no individual-level information.

---

## 11. Timeline Aligned with Paper Submission

The architecture document defines product development phases with no time estimates by design. For research purposes, we set targets relative to paper submission milestones.

| Milestone | Trigger | Activity |
|---|---|---|
| M1: Telemetry plane operational | Architecture Phase v2.5-A complete | Cosmos containers created, anonymization in production, consent UI live. |
| M2: Telegram-only data accumulation | M1 + 30 days | First 30 days of telemetry from Telegram users. Sufficient to draft preliminary analysis tables. |
| M3: Mobile launch | Architecture Phase 22b complete | Cross-channel data collection begins. |
| M4: Multi-channel data sufficient | M3 + 60 days | Sufficient mobile sample size (target: 10,000+ events) for channel comparison. |
| M5: Statistical analysis complete | M4 + 30 days | Sections §11–14 of the manuscript revised with empirical figures; new H6 (channel) and H7 (time) results added. |
| M6: Paper resubmission | M5 + 14 days | Updated manuscript submitted to IEEE Transactions on Cloud Computing. |

The total timeline from M1 to M6 is approximately 4 months at minimum, assuming continuous data collection and no IRB delays.

---

## 12. Threats to Validity

We follow Wohlin et al.'s classification.

### 12.1 Internal Validity

- **Pre-warming as quasi-experiment**: Day-level alternation is not a randomized user-level experiment. Confounding by day-of-week effects is partially controlled but not eliminated.
- **Salt rotation effect**: A 90-day salt rotation creates artificial discontinuities in any longitudinal analysis. We address this by limiting longitudinal claims to within-window effects.

### 12.2 External Validity

- **Domain specificity**: Findings are from a financial chatbot. Generalization to other LLM domains (general assistant, customer support, coding help) is not directly supported.
- **Language specificity**: Primarily Korean queries. Multi-language generalization is not claimed.
- **Channel mix**: Findings are conditional on the Telegram + mobile mix. Web-only or voice-only systems may differ.

### 12.3 Construct Validity

- **Cache hit definition**: Defined as cosine similarity above 0.93. This threshold is empirical, not theoretically derived. Sensitivity analysis at thresholds 0.90, 0.93, 0.95 will be reported.
- **Latency measurement**: Server-side latency excludes cold start time of Azure Functions. We separately report cold-start frequency and impact.

### 12.4 Conclusion Validity

- **Multiple testing**: Many statistical tests are performed (channel × dimension × time window). Bonferroni correction is applied where appropriate; for exploratory analysis, false discovery rate (Benjamini–Hochberg) is used instead.

---

## 13. Reproducibility and Open Data

To support reproducibility:

1. **Code**: The data collection code (Cosmos schema, anonymization, consent flow) is available in the project's GitHub repository under MIT license. The architecture document provides the full operational context.
2. **Aggregated statistics**: Daily hit rate, Zipf parameters, and channel comparison statistics will be published as a CSV companion to the paper.
3. **Analysis scripts**: Python notebooks for the statistical analyses described in §8 will be released in the same repository under MIT license.
4. **Replication**: Other researchers running similar production chatbots in different domains may adapt the schema in §4 directly. We provide a `cosmos_setup.py` script that creates the four containers with appropriate TTL and indexing.
5. **Pre-registration**: The hypotheses H6 and H7 introduced in this plan are pre-registered prior to data collection. The pre-registration is timestamped via a public Git commit on the project repository.

---

## Appendix A: Glossary

| Term | Definition |
|---|---|
| Cache hit | A query whose embedding has cosine similarity ≥ 0.93 with at least one cached embedding from the past hour. |
| Cold start | First invocation of an Azure Functions instance after scale-to-zero, which adds 1–3 seconds latency. |
| Embedding | A 1536-dimensional float vector produced by Azure OpenAI's text-embedding-3-small model. |
| KST | Korea Standard Time (UTC+9). All temporal analyses use KST unless noted. |
| Operational tier | Data collected without explicit opt-in, necessary for service operation. |
| Research-extended tier | Data collected only with explicit opt-in, including raw query text. |
| Salt rotation | Replacement of the SHA-256 salt every 90 days, breaking long-term linkability. |
| TTL | Time-to-live; Cosmos DB feature for automatic record deletion after a specified age. |

## Appendix B: Cross-Reference to Architecture Document

| This document | Architecture document (Korean, v3.0) |
|---|---|
| §3 System Architecture | §1–4 (overview, stack, project structure) |
| §4 Cosmos containers | §12 (Cosmos DB TTL strategy) |
| §5 Anonymization | §19 (Security and monitoring) |
| §6 Consent | §5.6 (First-response notice) |
| §7 Channel comparison | §22 (placeholder pointing to this document) |
| §9 Cost | §18 (4-tier DAU cost simulation) |

---

**End of Document**

*For corrections, suggestions, or replication inquiries, please open an issue on the project's GitHub repository.*
