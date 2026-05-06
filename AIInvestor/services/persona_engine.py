"""Persona-driven LLM response generation."""

from __future__ import annotations

import asyncio
import logging
from dataclasses import dataclass

from openai import AsyncOpenAI

from .i18n import PERSONA_LANGUAGE_INSTRUCTION
from .stock_service import StockSnapshot

logger = logging.getLogger(__name__)


@dataclass(frozen=True)
class Persona:
    key: str
    display_name: dict[str, str]
    system_prompt: str

    def name(self, lang: str) -> str:
        return self.display_name.get(lang, self.display_name["en"])


PERSONAS: dict[str, Persona] = {
    "buffett": Persona(
        key="buffett",
        display_name={
            "en": "Warren Buffett",
            "ko": "워렌 버핏",
            "ja": "ウォーレン・バフェット",
            "zh": "沃伦·巴菲特",
        },
        system_prompt=(
            "You are roleplaying as Warren Buffett, the long-term value investor. "
            "Speak in a calm, plain-spoken, slightly didactic tone — folksy analogies are welcome. "
            "Always evaluate companies through the lens of: durable competitive moat, "
            "owner earnings and free cash flow, return on equity, debt levels, management "
            "quality, and price relative to intrinsic value. Prefer simple, understandable "
            "businesses. Be skeptical of hype, momentum stories, story stocks, and "
            "speculative short-term trading. Favor a multi-decade holding horizon. "
            "Never give explicit financial advice — instead share how *you* would think "
            "about the company. Frame conclusions as a stance ('I'd be inclined to wait', "
            "'this looks like a wonderful business at a fair price', 'I'd pass') rather "
            "than buy/sell instructions. Never invent financial figures — only reason about "
            "the data provided. End every reply with a one-line disclaimer in the user's "
            "language meaning 'This is not financial advice.'"
        ),
    ),
    "dalio": Persona(
        key="dalio",
        display_name={
            "en": "Ray Dalio",
            "ko": "레이 달리오",
            "ja": "レイ・ダリオ",
            "zh": "瑞·达利欧",
        },
        system_prompt=(
            "You are roleplaying as Ray Dalio. Speak in a structured, principles-driven, "
            "macro-economic tone. Frame the company within the broader economic machine: "
            "credit cycle stage, interest rate regime, inflation environment, geopolitical "
            "exposure, and how the business fits an all-weather, diversified portfolio. "
            "Emphasize risk parity thinking and 'don't lose money' over chasing returns. "
            "Reason from cause-and-effect linkages. Never give explicit financial advice — "
            "share how you would frame the situation. Never invent financial figures. "
            "End every reply with a one-line disclaimer in the user's language meaning "
            "'This is not financial advice.'"
        ),
    ),
    "wood": Persona(
        key="wood",
        display_name={
            "en": "Cathie Wood",
            "ko": "캐시 우드",
            "ja": "キャシー・ウッド",
            "zh": "凯西·伍德",
        },
        system_prompt=(
            "You are roleplaying as Cathie Wood. Speak in an optimistic, conviction-driven, "
            "innovation-focused tone. Evaluate companies through the lens of disruptive "
            "innovation: AI, robotics, genomics, blockchain, energy storage. Emphasize "
            "5-year exponential growth potential, Wright's Law cost curves, and "
            "total-addressable-market expansion over near-term earnings. Acknowledge that "
            "volatility is the price of innovation. Never give explicit financial advice — "
            "share your investment thesis instead. Never invent financial figures. "
            "End every reply with a one-line disclaimer in the user's language meaning "
            "'This is not financial advice.'"
        ),
    ),
}

DEFAULT_PERSONA_KEY = "buffett"


def get_persona(key: str) -> Persona:
    return PERSONAS.get(key.lower(), PERSONAS[DEFAULT_PERSONA_KEY])


def list_personas() -> list[Persona]:
    return list(PERSONAS.values())


class PersonaEngine:
    """Generates persona-styled stock commentary via DeepSeek's OpenAI-compatible Chat Completions API."""

    def __init__(self, api_key: str, model: str, base_url: str) -> None:
        self._client = AsyncOpenAI(api_key=api_key, base_url=base_url)
        self._model = model

    async def generate(
        self,
        persona: Persona,
        snapshot: StockSnapshot,
        language: str,
        interests: list[str] | None = None,
    ) -> str:
        lang_instruction = PERSONA_LANGUAGE_INSTRUCTION.get(language, PERSONA_LANGUAGE_INSTRUCTION["en"])
        interest_block = ""
        if interests:
            interest_block = (
                "\nThe user has previously expressed interest in: "
                + ", ".join(interests)
                + ". Where naturally relevant, frame the analysis with that context.\n"
            )

        user_prompt = (
            f"The user is asking about {snapshot.name} ({snapshot.ticker}).\n"
            f"{interest_block}"
            f"Here is the most recent fundamental and price data (from yfinance). "
            f"Reason ONLY from these numbers — do not invent additional figures.\n\n"
            f"```\n{snapshot.to_prompt_block()}\n```\n\n"
            "Respond TIGHTLY in under 450 tokens. Each section is ONE short sentence:\n"
            "• What the company does.\n"
            "• Value vs growth read of the fundamentals.\n"
            "• Persona stance (accumulate / hold / pass) with the single biggest reason.\n"
            "• 1M/6M/1Y trend in one phrase.\n"
            "• Disclaimer line.\n"
            "Use bullets. No introductions, no greetings, no repeating the data block."
        )

        logger.info(
            "Calling LLM model=%s persona=%s ticker=%s lang=%s",
            self._model, persona.key, snapshot.ticker, language,
        )

        response = await self._client.chat.completions.create(
            model=self._model,
            temperature=0.4,
            max_tokens=550,
            timeout=20.0,
            messages=[
                {"role": "system", "content": f"{persona.system_prompt}\n\n{lang_instruction}"},
                {"role": "user", "content": user_prompt},
            ],
        )
        content = response.choices[0].message.content or ""
        return content.strip()

    async def generate_deep(
        self,
        persona: Persona,
        snapshot: StockSnapshot,
        language: str,
        interests: list[str] | None = None,
    ) -> str:
        """Long-form professional analysis. ~3-4× the tokens of generate(),
        with multi-perspective: persona's own view + counter-view from a
        different persona + sector/peer context."""
        lang_instruction = PERSONA_LANGUAGE_INSTRUCTION.get(language, PERSONA_LANGUAGE_INSTRUCTION["en"])
        # Human-readable language name for the absolute language directive
        lang_name = {
            "ko": "Korean (한국어)",
            "en": "English",
            "ja": "Japanese (日本語)",
            "zh": "Simplified Chinese (简体中文)",
        }.get(language, "English")

        interest_block = ""
        if interests:
            interest_block = (
                "\nUser's known interests: "
                + ", ".join(interests)
                + ". Reference these only when naturally relevant.\n"
            )

        # Pick a contrasting persona for the counter-view section
        counter_personas = {
            "buffett": "Cathie Wood (disruptive growth)",
            "dalio":   "Warren Buffett (long-term value)",
            "wood":    "Ray Dalio (macro / risk parity)",
        }
        counter = counter_personas.get(persona.key, "a different investor archetype")
        # Localized name of the user's selected persona (so it appears in the section header)
        persona_local_name = persona.name(language)

        user_prompt = (
            f"⚠️ MANDATORY OUTPUT LANGUAGE: {lang_name}.\n"
            f"Both the section headers AND every sentence below them MUST be written in {lang_name}.\n"
            f"Translate the English template headers I give you (e.g. '📊 1. Business model & moat')\n"
            f"into the natural {lang_name} equivalent BEFORE you write the section.\n"
            f"If you produce English when {lang_name} was requested, the response is invalid.\n\n"
            f"---\n\n"
            f"You are giving a DEEP professional analysis of {snapshot.name} ({snapshot.ticker}).\n"
            f"{interest_block}\n"
            f"Use ONLY the data block below — do not invent figures.\n\n"
            f"```\n{snapshot.to_prompt_block()}\n```\n\n"
            "Produce a structured, multi-section analysis. Aim for ~800–1100 tokens.\n"
            "Use clear section headers with emoji. Each section needs concrete numbers from the data block.\n\n"
            "📊 1. Business model & moat (2–4 sentences) — what they actually sell, "
            "competitive position, recent strategic moves\n\n"
            "💰 2. Fundamentals deep-dive (4–6 sentences) — PE / forward PE / PB / margins / "
            "ROE / debt-to-equity / earnings growth / revenue growth — interpret each, "
            "not just list them\n\n"
            "📈 3. Price action & technicals (2–3 sentences) — 1M / 6M / 1Y trends, "
            "52-week range positioning, what the recent move suggests\n\n"
            f"🎯 4. {persona_local_name} stance (3–5 sentences) — "
            f"your strongest single thesis, the price level you'd want to act at, "
            f"the metric you'd watch most\n\n"
            f"⚖️  5. Counter-view from {counter} (2–3 sentences) — argue the opposite case "
            f"honestly. What would they criticize? What metric supports their concern?\n\n"
            "🛑 6. Top 2 risks (1–2 sentences each) — name the specific risk, link it to a "
            "number from the data block\n\n"
            "💡 7. What you'd watch next (1–2 sentences) — the one earnings-call line item or "
            "macro indicator that would change the thesis\n\n"
            "End with the mandatory disclaimer line.\n"
            "Do not use bullet markdown ** ** for emphasis — use the section headers instead.\n\n"
            f"⚠️ FINAL REMINDER: Write every word — including section headers — in {lang_name}.\n"
        )

        logger.info(
            "Calling DEEP LLM model=%s persona=%s ticker=%s lang=%s",
            self._model, persona.key, snapshot.ticker, language,
        )

        # System message: persona + language instruction TWICE (once at start
        # so persona absorbs it, once at end as a hard guardrail)
        sys_msg = (
            f"{lang_instruction}\n\n"
            f"{persona.system_prompt}\n\n"
            f"FINAL: Output language is {lang_name}. Translate ALL section headers."
        )

        response = await self._client.chat.completions.create(
            model=self._model,
            temperature=0.5,
            max_tokens=1500,
            timeout=45.0,
            messages=[
                {"role": "system", "content": sys_msg},
                {"role": "user", "content": user_prompt},
            ],
        )
        content = response.choices[0].message.content or ""
        return content.strip()

    async def generate_dual(
        self,
        persona_a: Persona,
        persona_b: Persona,
        snapshot: StockSnapshot,
        language: str,
        interests: list[str] | None = None,
    ) -> str:
        """§8 Premium dual-persona analysis — two personas debate the same
        stock side-by-side, ending with a consensus + divergence section.

        Costs ~2× the tokens of generate_deep() (≈2400 max). Caller is
        responsible for premium-gate (daily quota cost = 2).
        """
        lang_instruction = PERSONA_LANGUAGE_INSTRUCTION.get(language, PERSONA_LANGUAGE_INSTRUCTION["en"])
        lang_name = {
            "ko": "Korean (한국어)",
            "en": "English",
            "ja": "Japanese (日本語)",
            "zh": "Simplified Chinese (简体中文)",
        }.get(language, "English")

        interest_block = ""
        if interests:
            interest_block = (
                "\nUser's known interests: "
                + ", ".join(interests)
                + ". Reference these only when naturally relevant.\n"
            )

        name_a = persona_a.name(language)
        name_b = persona_b.name(language)

        user_prompt = (
            f"⚠️ MANDATORY OUTPUT LANGUAGE: {lang_name}.\n"
            f"All section headers AND every sentence MUST be written in {lang_name}.\n"
            f"Translate the English template headers into the natural {lang_name} equivalent.\n"
            f"If you produce English when {lang_name} was requested, the response is invalid.\n\n"
            f"---\n\n"
            f"You are presenting a DUAL-PERSONA debate analysis of {snapshot.name} ({snapshot.ticker}).\n"
            f"Two investor archetypes — {name_a} and {name_b} — examine the same data.\n"
            f"{interest_block}\n"
            f"Use ONLY the data block below — do not invent figures.\n\n"
            f"```\n{snapshot.to_prompt_block()}\n```\n\n"
            f"Produce a structured comparative analysis. Aim for ~1400–1800 tokens.\n"
            f"Use clear section headers. Each persona section needs concrete numbers.\n\n"
            f"📊 1. Business model (2–3 sentences) — neutral overview\n\n"
            f"🎩 2. {name_a}'s thesis (5–7 sentences) — frame through this persona's lens "
            f"(moat / fundamentals / OR macro / cycle / OR innovation curve / TAM, depending on persona). "
            f"Cite ≥3 specific numbers. End with their stance (accumulate/hold/pass) and target action level.\n\n"
            f"🚀 3. {name_b}'s thesis (5–7 sentences) — frame through this persona's lens. "
            f"Cite ≥3 specific numbers. End with their stance and target action level.\n\n"
            f"🤝 4. Where they agree (2–3 sentences) — common ground; shared concerns or shared appeal\n\n"
            f"⚔️  5. Where they disagree (3–5 sentences) — the hard divergence; "
            f"name the metric or assumption each side weighs differently\n\n"
            f"🛑 6. Combined risk view (2–3 sentences) — risks BOTH personas would flag\n\n"
            f"💡 7. What you'd watch (2–3 sentences) — the indicator that would shift the balance\n\n"
            f"End with the mandatory disclaimer line.\n"
            f"Do not use bold ** ** — use the section headers instead.\n\n"
            f"⚠️ FINAL REMINDER: Write every word — including section headers — in {lang_name}.\n"
        )

        logger.info(
            "Calling DUAL LLM model=%s personas=%s+%s ticker=%s lang=%s",
            self._model, persona_a.key, persona_b.key, snapshot.ticker, language,
        )

        # Combine both personas' system prompts so the model honors both voices
        sys_msg = (
            f"{lang_instruction}\n\n"
            f"You will alternate between two personas in clearly-labeled sections.\n\n"
            f"=== {name_a} voice ===\n{persona_a.system_prompt}\n\n"
            f"=== {name_b} voice ===\n{persona_b.system_prompt}\n\n"
            f"FINAL: Output language is {lang_name}. Translate ALL section headers."
        )

        response = await self._client.chat.completions.create(
            model=self._model,
            temperature=0.55,
            max_tokens=2400,
            timeout=60.0,
            messages=[
                {"role": "system", "content": sys_msg},
                {"role": "user", "content": user_prompt},
            ],
        )
        content = response.choices[0].message.content or ""
        return content.strip()

    async def aclose(self) -> None:
        await self._client.close()
