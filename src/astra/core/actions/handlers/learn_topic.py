"""Teach Astra new topics — local save or LLM-assisted research."""

import re
from typing import Dict, Optional

from astra.core.intent.intents import LEARN_TOPIC
from astra.core.actions.handlers.base import ActionHandler
from astra.core.actions.result import ActionResult

LEARN_PREFIXES = (
    "learn about ",
    "learn on ",
    "teach yourself ",
    "research and learn about ",
    "research and learn ",
    "study and learn ",
    "add knowledge about ",
    "add knowledge on ",
    "learn that ",
    "remember as knowledge ",
)


class LearnTopicHandler(ActionHandler):

    def __init__(self, knowledge_engine, llm_responder=None):
        self.knowledge = knowledge_engine
        self.llm = llm_responder

    def can_handle(self, action: str) -> bool:
        return action == LEARN_TOPIC

    def execute(self, parameters: Dict) -> ActionResult:
        topic = (parameters.get("topic") or "").strip()
        content = (parameters.get("content") or "").strip()
        raw = (parameters.get("raw") or "").strip()

        if not topic and not content and raw:
            topic, content = self._parse_raw(raw)

        if not topic and content:
            topic = self._topic_from_content(content)

        if not content and topic:
            if self.llm and self.llm.enabled:
                content = self._research_with_llm(topic)
            else:
                return ActionResult(
                    success=False,
                    message=(
                        f"I need an LLM key to research '{topic}' automatically. "
                        "Add ANTHROPIC_API_KEY to .env, or say: "
                        f"learn that <facts> about {topic}"
                    ),
                    error="LLM_REQUIRED",
                )

        if not topic or not content:
            return ActionResult(
                success=False,
                message="Tell me what to learn — e.g. 'learn about Kubernetes' or "
                "'learn that pods are the smallest deployable unit in Kubernetes'.",
                error="EMPTY_LEARN",
            )

        entry = self.knowledge.add_entry(topic=topic, content=content)
        total = self.knowledge.topic_count()

        return ActionResult(
            success=True,
            message=(
                f"Neural core updated — learned topic '{entry['topic']}' "
                f"({total} topics in knowledge graph). Ask me about it anytime."
            ),
            data={"topic": entry["topic"], "source": entry.get("source", "user"), "total": total},
        )

    def _parse_raw(self, raw: str) -> tuple:
        text = raw.strip().lower()
        for prefix in LEARN_PREFIXES:
            if text.startswith(prefix):
                body = raw.strip()[len(prefix):].strip()
                if prefix == "learn that ":
                    return self._topic_from_content(body), body
                return body, ""
        return raw.strip(), ""

    def _topic_from_content(self, content: str) -> str:
        words = re.findall(r"[a-zA-Z0-9]+", content.lower())
        if not words:
            return "general"
        if len(words) <= 3:
            return "_".join(words[:3])
        return "_".join(words[:2])

    def _research_with_llm(self, topic: str) -> Optional[str]:
        prompt = (
            f"Teach Astra about: {topic}\n\n"
            "Write 2-3 concise paragraphs of factual knowledge Astra should remember. "
            "No markdown headers. Under 180 words. Focus on durable facts, not fluff."
        )
        answer = self.llm.respond(prompt)
        return answer.strip() if answer else None
