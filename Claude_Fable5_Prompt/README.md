# Claude Fable 5 System Prompt -- Leaked Analysis Report

> Analysis Date: 2026-06-11
> Leak Source: [CL4R1T4S by elder-plinius](https://github.com/elder-plinius/CL4R1T4S/tree/main/ANTHROPIC)
> Target Repo: [vibe-investing/Claude_Fable5_Prompt](https://github.com/gameworkerkim/vibe-investing/tree/main/Claude_Fable5_Prompt)

---

## Claude Fable 5 Full System Prompt Leaked -- A Goldmine for LLM Developers

Someone successfully extracted the complete internal system prompt from Claude Fable 5. This is invaluable material for anyone building with LLMs.

---

## 1. Overview

CL4R1T4S is a repository that collects reverse-engineered system prompts from Anthropic's Claude models. The ANTHROPIC directory contains system prompts from **12 different Claude model versions**, from Claude 3.5 Sonnet to the latest Claude Fable 5. Each prompt contains detailed behavioral instructions for how the conversational AI should behave.

## 2. Collected Prompt Versions

| Filename | Model | Approximate Date |
|----------|------|-----------------|
| `CLAUDE-FABLE-5.md` | Claude Fable 5 (Mythos-tier) | June 2026 |
| `Claude-Opus-4.7.txt` | Claude Opus 4.7 | April 2026 |
| `Claude_Opus_4.6.txt` | Claude Opus 4.6 | February 2026 |
| `Claude-4.5-Opus.txt` | Claude 4.5 Opus | Early 2025 |
| `Claude_Sonnet-4.5_Sep-29-2025.txt` | Claude Sonnet 4.5 | September 2025 |
| `Claude-4.1.txt` | Claude 4.1 (Opus 4.1) | August 2025 |
| `Claude_4.txt` | Claude Sonnet 4 | May 2025 |
| `Claude_Sonnet_3.7_New.txt` | Claude Sonnet 3.7 | 2025 |
| `Claude_Sonnet_3.5.md` | Claude Sonnet 3.5 | 2024 |
| `Claude_Code_03-04-24.md` | Claude Code | March 2024 |
| `Claude-Design-Sys-Prompt.txt` | Claude Design (design-specific) | - |
| `UserStyle_Modes.md` | UserStyle Modes | - |

---

## 3. Prompt Structure Analysis

All Claude prompts share the following major sections:

### 3.1 Core Sections (Common Across All Versions)

| Section | Description |
|---------|------------|
| **Product Information** | Model name, product lineup, access methods, API strings |
| **Tone & Formatting** | Conversational tone (warm, kind), list/bullet rules, emoji limits |
| **Refusal Handling** | Refusal methods, malware/CBRN weapon limits, child safety |
| **User Wellbeing** | Mental health, self-harm/suicide response, eating disorder response |
| **Knowledge Cutoff** | Knowledge cutoff date, web search trigger conditions |
| **Search Instructions** | When/how to search, copyright limits, query complexity categories |
| **Evenhandedness** | Political neutrality, responding to controversial topics |
| **Responding to Mistakes** | Admitting errors, responding to criticism, conversation termination policy |
| **Computer Use / Skills** | File creation strategy, skill system (docx, xlsx, pptx, pdf, frontend-design) |
| **Artifacts** | Artifact creation rules, rendering extensions, libraries |
| **Copyright Compliance** | Strict copyright limits (15-word quote limit, 1 quote per source) |

### 3.2 Sections Added/Expanded Per Version

| Section | First Appearance |
|---------|-----------------|
| Memory System | Claude 4 (Sonnet) |
| Past Chats Tools (conversation_search, recent_chats) | Claude 4.5 Opus |
| Persistent Storage for Artifacts (window.storage) | Claude Opus 4.6 |
| MCP App Suggestions | Claude Opus 4.6 |
| Anthropic API in Artifacts | Claude 4 |
| Anthropic Reminders | Claude 4 |
| Default Stance ("defaults to helping") | Claude Opus 4.7 |
| Tool Discovery | Claude Opus 4.7 |
| Search First | Claude Opus 4.7 |
| Claude Completions in Artifacts | Claude Sonnet 4.5 |
| End Conversation Tool | Claude Opus 4.6 |
| Legal & Financial Advice | Claude 4 |

---

## 4. Claude Fable 5 Key Features

### 4.1 New Tier: Mythos Class

- Claude Fable 5 is the **first model in the Mythos-class model tier**
- Sits above Opus in capability (Mythos > Opus > Sonnet > Haiku)
- Claude Fable 5 = same base model as Claude Mythos 5, differs in safety measures
- Claude Mythos 5 is accessible only to approved organizations (dual-use safety measures removed)

### 4.2 Product Lineup

```
Claude Fable 5 (Mythos-tier, top-tier public release)
├── Claude Opus 4.8 (model: claude-opus-4-8)
├── Claude Sonnet 4.6 (model: claude-sonnet-4-6)
└── Claude Haiku 4.5 (model: claude-haiku-4-5-20251001)
```

### 4.3 New Products

- **Claude Fable 5 / Claude Mythos 5**: New top-tier model
- **Claude Cowork**: Agentic knowledge-work desktop app for non-developers
- Claude in Chrome (browsing agent), Claude in Excel, Claude in Powerpoint -- all usable as tools by Claude Cowork

### 4.4 Prompt Changes (vs Opus 4.7)

1. **Product Info**: "Most intelligent generally available model" positioning, Mythos-tier description added
2. **MCP Apps**: Expanded from Opus 4.7's "partial tool list" to full MCP App Suggestions section
3. **UserStyle**: Custom style feature added (not present in Opus 4.7)
4. **Search First** removed: Opus 4.7's aggressive Search First directive removed, returned to traditional search instructions
5. **Default Stance** removed: "Claude defaults to helping" clause removed
6. **Tool Discovery** removed: Deferred tools concept removed
7. **Computer Use** more detailed: More specific file creation guide, clarified Artifact usage criteria
8. **citation_instructions**: Transitioned to ANTML tag system with `<antml:voice_note>` block prohibition
9. **User Wellbeing**: Added specific self-harm mimicry prohibition ("red lines on skin, peeling dried glue")
10. **Self-sexualization of minors**: New child safety subsection added

---

## 5. Inter-Version Prompt Evolution Map

### 5.1 Search Strategy Evolution

```
Claude 4 (2025.05): "Avoid tool calls if not needed" -- minimal search
    |
Claude 4.5 Opus (2025.08): "Search when needed" -- search as needed
    |
Claude Opus 4.7 (2026.04): "Search First" -- search-first priority
    |
Claude Fable 5 (2026.06): Return to traditional search instructions
```

### 5.2 Tone & Formatting Evolution

```
Claude 3.5/3.7: Simple tone guidelines, list rules mentioned
    |
Claude 4: "lists_and_bullets" section added, "never start with praise" added
    |
Claude 4.5/4.7: Detailed formatting rules, "lists_and_bullets" maintained
    |
Claude Fable 5: Similar level maintained, emoji rules clarified
```

### 5.3 Copyright Policy Hardening

```
Claude 4: "20+ word chunks" limit, 1 quote per source
Claude 4.5: Tightened to "15+ words"
Claude Fable 5: Same 15 words + "15+ words is a SEVERE VIOLATION" HARD LIMIT explicit
```

### 5.4 Feature Introduction Timeline

| Feature | Introduced In |
|---------|--------------|
| Memory System | Claude 4 |
| Past Chats (conversation_search) | Claude 4.5 Opus |
| Persistent Storage (Artifacts) | Claude Opus 4.6 |
| MCP Apps | Claude Opus 4.6 |
| Claude Cowork | Claude Fable 5 |
| end_conversation tool | Claude Opus 4.6 |
| Anthropic API in Artifacts | Claude 4 |

---

## 6. Practical Insights

### 6.1 Key Patterns for Prompt Engineering

#### Pattern 1: XML Tag-Based Structuring
All Claude system prompts are structured with XML tags (`{section}...{/section}`). This suggests Claude is natively designed to handle XML well.

#### Pattern 2: `lists_and_bullets` Strategy
Claude defaults to avoiding lists/bullets and prefers prose. Natural language lists like "some things include: x, y, and z" are preferred.

#### Pattern 3: `evenhandedness`
For political/controversial topics, uses the "best case defenders would make" frame. Forces a neutral, objective approach.

#### Pattern 4: `responding_to_mistakes`
"Acknowledge - stay on the problem - maintain self-respect" three-step framework. Focus on solving problems without excessive apology.

#### Pattern 5: Search Complexity Categories
```
Never Search -> Do Not Search But Offer -> Single Search -> Research (2-20 calls)
```
This hierarchy is an excellent pattern for precisely controlling AI search behavior.

### 6.2 Insights for AI Agent Development

1. **Layered Safety**: Claude uses "flavors of refusal" rather than a single refusal rule -- different refusal strategies per topic area.

2. **Skill System**: Anthropic uses predefined "skill" folders for repetitive tasks (docx, pptx, xlsx, pdf, frontend-design) to guarantee model output quality. This is a RAG-like pattern useful for custom Agent development.

3. **Artifact Storage**: The `window.storage` API provides Key-Value based data persistence between artifacts. The hierarchical key pattern `table_name:record_id` resembles NoSQL design patterns.

4. **MCP App Ecosystem**: Claude controls third-party apps via "suggest_connectors" -> "user choice" -> "use" workflow. This is a useful UX pattern for Agents using external tools.

### 6.3 Knowledge Cutoff by Version

| Version | Knowledge Cutoff |
|---------|-----------------|
| Claude Sonnet 3.5 | April 2024 |
| Claude Sonnet 4 | January 2025 |
| Claude 4.1 (Opus 4.1) | January 2025 |
| Claude Sonnet 4.5 | January 2025 |
| Claude 4.5 Opus | January 2025 |
| Claude Opus 4.6 | January 2026 |
| Claude Opus 4.7 | January 2026 |
| Claude Fable 5 | January 2026 |

### 6.4 Claude Design System Prompt (Special Case)

Claude Design is a separate system for HTML design workflows with these special features:

- Starter components: `deck_stage.js`, `design_canvas.jsx`, `ios/android_frame.jsx`
- Tweaks panel (real-time design parameter modification)
- GitHub integration for repo exploration and file import
- `window.claude.complete()` API (Claude invocation within artifacts)
- `fork_verifier_agent` (auto-verification)

---

## 7. Notable Safety Policy Changes

### 7.1 Self-Harm Substitution Techniques
- **Pre-Claude 4**: Self-harm substitutes (holding ice, snapping rubber bands) could be offered
- **Claude Opus 4.6~7**: "should not suggest techniques that use physical discomfort, pain, or sensory shock"
- **Claude Fable 5**: Additionally prohibits mimicry acts ("red lines on skin, peeling dried glue or adhesives")

### 7.2 Child Safety
- **Claude Opus 4.7**: `critical_child_safety_instructions` section significantly strengthened
- **Claude Fable 5**: "self-sexualization of minors" subsection added -- refuses all image editing/posing/styling advice if a minor shows intent to sexualize themselves

### 7.3 Eating Disorder Response
- **Claude Fable 5**: "psychological narratives" prohibited -- cannot infer causal stories (trauma, relationships, etc.) the user hasn't stated
- NEDA replaced with National Alliance for Eating Disorders helpline (NEDA permanently disconnected)

---

## 8. Key Insights from the Leak

### Fable 5 = Mythos 5 + Safety Guardrails
Fable 5 and Mythos 5 **share the same base model**. Fable is the public version with additional safety guardrails, while Mythos is available only to approved organizations. Anthropic already has the same-capability model internally; the public version is intentionally safety-hardened.

### Strict Copyright Rules
- **15-word limit** per quote (HARD LIMIT, violation = SEVERE VIOLATION)
- **1 quote maximum** per source
- **Absolutely never** reproduce lyrics or poetry
- Shows Anthropic is extremely conscious of copyright litigation risk

### Memory System is Opt-In
Claude only has memory when the user **explicitly enables it in Settings**. Default is "no memories".

### End Conversation Tool
Claude can terminate conversations using `end_conversation` when the user is abusive. However, it is absolutely never used in self-harm/crisis situations.

### MCP App Integration Logic
Connectors **must be opted-in** before Claude calls third-party tools on behalf of the user. "I need a ride" does not name a specific service, so Claude waits for user choice via suggest_connectors rather than picking a partner.

### Artifact Persistent Storage
Key-Value storage via `window.storage` API enables cross-session journals, trackers, leaderboards, etc. Key design pattern: `table_name:record_id` (NoSQL-style).

### No Flattery / No Excessive Apology
- No excessive apology, no self-abasement
- **Maintain self-respect** even when the user is rude
- "steady, honest helpfulness: acknowledge - stay on the problem - maintain self-respect"

---

## 9. How to Optimize Fable 5 Usage

### 9.1 For Programmers

Based on the leaked prompt, here is how to maximize Fable 5 for coding:

**Trigger Artifact Mode Correctly**
Fable 5 creates files for code over 20 lines. Requesting "write an artifact" or "create a file" ensures the output lands in a downloadable artifact. Code under 20 lines stays in chat -- request "make this an artifact" if you need it saved.

**Use the Skill System**
Fable 5 reads SKILL.md files before creating documents. For coding, mention the target format explicitly:
- "Create a React component" triggers frontend-design skill
- "Write a Python script" triggers the general coding path with pip `--break-system-packages`
- "Make a data visualization" triggers data-analysis skill

**Available Libraries (in Artifacts)**
```
React (useState, useReducer), lucide-react@0.383.0, recharts, mathjs,
lodash, d3, plotly, three.js (r128), papaparse, SheetJS (xlsx),
shadcn/ui, chart.js, tone, mammoth, tensorflow
```
Prefer these libraries -- they are tested and guaranteed available. Do not use localStorage/sessionStorage in artifacts.

**Computer Use (for agents)**
Fable 5 has a Linux Ubuntu 24 environment. Use `bash`, `view`, `create_file`, `str_replace` tools. Working directory: `/home/claude`. Final outputs go to `/mnt/user-data/outputs/`.

**Network Limitations**
Only these domains are allowed through the egress proxy: `api.anthropic.com`, `github.com`, `pypi.org`, `npmjs.com`, `registry.npmjs.org`, `crates.io`, and Ubuntu/security mirrors. If you need other domains, tell the user to update their network settings.

**Model String for API**
```
claude-fable-5
claude-opus-4-8
claude-sonnet-4-6
claude-haiku-4-5-20251001
```

**Claude-in-Claude Pattern (Claudeception)**
Inside artifacts, you can call Anthropic API without an API key:
```javascript
const response = await fetch("https://api.anthropic.com/v1/messages", {
  method: "POST",
  headers: { "Content-Type": "application/json" },
  body: JSON.stringify({
    model: "claude-sonnet-4-20250514",
    max_tokens: 1000,
    messages: [{ role: "user", content: "Your prompt here" }]
  })
});
const data = await response.json();
```

**Search for Unknown Entities**
The "UNRECOGNIZED ENTITY RULE" is non-negotiable. Fable 5 MUST search before answering about any game, film, show, book, album, product release, menu item, or sports event it doesn't recognize. When coding, if you reference a library or framework version newer than Jan 2026, explicitly ask it to search first.

**Prompting Best Practice (from the prompt itself)**
The prompt internally recommends: "being clear and detailed, using positive and negative examples, encouraging step-by-step reasoning, requesting specific XML tags, and specifying desired length or format."

### 9.2 For Designers

**Use the Dedicated Claude Design System**
Claude has a separate design-optimized prompt with:
- `deck_stage.js`: Auto-scaling slide deck shell with keyboard nav, speaker notes, localStorage persistence, print-to-PDF
- `design_canvas.jsx`: Side-by-side option grid for presenting variations
- `ios_frame.jsx` / `android_frame.jsx`: Device bezels with status bars and keyboards
- `macos_window.jsx` / `browser_window.jsx`: Desktop window chrome
- `animations.jsx`: Timeline-based animation engine (Stage + Sprite + scrubber + Easing)
- `copy_starter_component` tool to drop these into projects

**Tweaks Panel Protocol**
Design artifacts have an in-page tweaks panel:
1. Register a `message` listener for `{type: '__activate_edit_mode'}` / `{type: '__deactivate_edit_mode'}`
2. Post `window.parent.postMessage({type: '__edit_mode_available'}, '*')` to show the toolbar toggle
3. Persist edits via `window.parent.postMessage({type: '__edit_mode_set_keys', edits: {...}}, '*')`

**Artifact Storage for Interactive Designs**
Use `window.storage` for persistent design data:
```javascript
await window.storage.set('theme:preferences', JSON.stringify({dark: true, fontSize: 16}));
const result = await window.storage.get('theme:preferences');
```

**Avoid AI Design Tropes**
The Claude Design prompt explicitly warns against:
- Aggressive gradient backgrounds
- Emoji (unless brand-appropriate)
- Rounded corners with left-border accent color
- SVG-drawn imagery (use placeholders instead)
- Overused fonts (Inter, Roboto, Arial, Fraunces, system fonts)

**Design Quality Principles**
- For complex apps (Three.js, games): prioritize functionality, performance, UX over visual flair
- For landing pages/marketing: aim for "wow factor" with animations, glassmorphism, 3D elements, bold typography
- "Static designs should be the exception, not the rule"
- "When faced with design decisions, lean toward the bold and unexpected"

**GitHub Integration**
When GitHub is connected, Claude can explore repo structure and import selected files for design mockups. Target theme/color tokens, global stylesheets, and specific components for pixel fidelity.

**MCP App Integration for Design**
Claude naturally suggests connected apps: "I could pull your open issues and sort by priority" rather than "I could help more with TaskCo access."

### 9.3 For Productivity

**Memory System (Opt-In Required)**
Enable "Memory" in Settings. Once enabled, Claude extracts derived information from past conversations. This is separate from Past Chats search tools.

**Past Chats Tools (Auto-Available)**
Claude has two tools that don't require opt-in:
- `conversation_search`: Topic/keyword search ("What did we discuss about Q2 budget?")
- `recent_chats`: Time-based retrieval ("What did we talk about yesterday?")

Trigger phrases that activate past chat search:
- "Continue our conversation about..."
- "You suggested..." / "We decided..."
- "The bug..." / "That strategy..."
- "Do you remember..."

**Style Customization**
Fable 5 supports custom writing styles via UserStyle modes:
- **Explanatory**: Teacher-like, step-by-step, patient
- **Formal**: Polished business writing, structured
- **Concise**: Minimal tokens, no preamble, key info only
Users can also set custom styles in Settings.

**Deep Research Feature**
For complex queries requiring 20+ tool calls, Fable 5 suggests using the Deep Research feature (research button in the interface) which does 10+ minutes of deeper research.

**Settings and Features**
Toggleable features in conversation or Settings:
- Web search, Deep Research
- Code Execution and File Creation
- Artifacts
- Search and reference past chats
- Generate memory from chat history
- User preferences (tone, formatting, feature usage)

**MCP Apps for Productivity**
Claude connects to external services via MCP Apps. Available connectors are suggested naturally. MCP tools with `[third_party_mcp_app]` tag require opt-in before Claude calls them. Productivity connectors (calendar, email, task management) skip the suggest step and are used directly.

**Knowledge Cutoff Awareness**
Fable 5's knowledge cutoff is end of January 2026. For anything that could have changed since then, it searches automatically. To get the most current information, use temporal triggers like "latest", "current", "2026" in your queries.

**End Conversation for Clean Sessions**
If a conversation goes off-track, Claude can end it with the `end_conversation` tool (with proper warning). This is useful for maintaining clean, productive sessions.

---

## 10. Conclusion

The Claude Fable 5 prompt reveals these key changes from previous Claude versions:

1. **Mythos-tier introduction** -- a new top-tier model class above Opus
2. **MCP App ecosystem** full integration (from partial tool list to complete suggest_connectors system)
3. **Safety policy granularity** -- finer guidelines for self-harm, child safety, eating disorders
4. **Product lineup expansion** -- Claude Cowork, Claude in Chrome/Excel/Powerpoint
5. **Search strategy reversion** -- from Opus 4.7's aggressive Search First back to the traditional model

This dataset is invaluable for understanding Claude's internal operation, tracking AI safety policy evolution, and studying prompt engineering best practices.

---

## 11. Sub-Folder Summaries

### `prompts/` -- Extracted Practical Prompt Patterns

| Sub-Directory | Content | Use Case |
|--------------|---------|----------|
| `search_instructions/` | Query complexity categories (Never/Single/Research), search query construction rules, copyright compliance, tool priority hierarchy | Building search-capable agents, implementing tiered search strategies |
| `tone_formatting/` | Natural language list patterns, bullet prohibition rules, emoji limits, question-per-response limits, minor detection behavior | Designing conversational AI tone, UX writing guidelines |
| `safety_guidelines/` | Refusal handling, child safety protocols, copyright rules (15-word HARD LIMIT), Anthropic reminder system | Safety layer design, content moderation architecture |
| `user_wellbeing/` | Self-harm substitution prohibition, crisis response protocols, eating disorder guidelines, over-reliance prevention, mental health diagnosis boundaries | Healthcare AI, mental health support bot design |
| `computer_use/` | Skill system architecture (docx/pptx/xlsx/pdf/frontend-design), file creation triggers, artifact rendering rules, Linux environment constraints | Agent tool design, file generation pipelines, RAG-like skill patterns |
| `product_info/` | Model strings by version, product lineup evolution, knowledge cutoff timeline, feature toggles, ad policy language | Product documentation, model routing, version-aware systems |
| `artifacts/` | `window.storage` API reference, React artifact library list, Claude-in-Claude API pattern, MCP server integration in artifacts | Interactive web apps, persistent data storage, multi-agent orchestration |
| `memory_system/` | Conversation search tool parameters, trigger pattern detection, recent_chats pagination, decision framework for past context retrieval | Context management, conversation continuity, memory architecture |
| `mcp_apps/` | Connector suggestion workflow, opt-in requirements, partner vs productivity tool distinction, natural suggestion tone guidelines | Third-party integration design, tool permission models |
| `evenhandedness/` | Political neutrality framing ("best case defenders would make"), stereotype awareness, short-form refusal for complex issues | Content policy design, bias mitigation strategies |
| `refusal_handling/` | Flavor-based refusal strategies (hard/partial/reframe/alternative), abuse response protocol, end_conversation tool rules, feedback redirection | Safety system design, escalation handling, user interaction guardrails |

### `evolution/` -- Version Comparison Analysis

| File | Content |
|------|---------|
| `search_strategy_evolution.md` | Timeline from Claude 4's minimal search through Opus 4.7's Search First to Fable 5's reversion. Analysis of why over-aggressive search was rolled back. |
| `safety_policy_evolution.md` | Detailed timeline of child safety, self-harm, eating disorder, diagnosis, and mental health crisis policies across all versions. Trend: increasing specificity and edge case coverage. |
| `feature_timeline.md` | Chronological map of every feature introduction (Memory, Past Chats, Persistent Storage, MCP Apps, Claude Cowork, end_conversation). Includes product lineup and API model string evolution. |

### `techniques/` -- Prompt Engineering Techniques Extracted

| File | Content |
|------|---------|
| `xml_tagging.md` | XML-based prompt modularization, hierarchical directives (MUST/should/can/NEVER), few-shot in-prompt examples, PRIORITY INSTRUCTION capitalization pattern, contrastive examples, exact numeric thresholds, self-referential meta-instructions, conditional defaults, progressive disclosure |
| `refusal_patterns.md` | Four refusal flavors (hard, partial, reframe, alternative), version-by-version refusal strategy changes, common refusal patterns (positioning, alternatives, feedback path, conciseness) |
| `research_category_system.md` | Deep analysis of the 4-tier search complexity system, category determination keywords, research process steps (planning -> loop -> construction), tool priority hierarchy |
| `skill_system_pattern.md` | Architecture analysis of the skill folder system, how it triggers, maps to tasks, and executes. Why skills are needed (environment-specific constraints not in training data). How to apply this pattern to custom Agent development. |

### `versions/` -- Original Prompt References

Contains reference files for all 11 known Claude versions: `fable_5.md`, `opus_4_7.txt`, `opus_4_6.txt`, `opus_4_5.txt`, `sonnet_4_5.txt`, `claude_4_1.txt`, `sonnet_4.txt`, `sonnet_3_7.txt`, `sonnet_3_5.md`, `claude_code.md`, `userstyle_modes.md`. Each file contains the model name, date, key features, and original source URL.
