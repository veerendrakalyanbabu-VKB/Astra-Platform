import os
import re

from astra.core.intent.parser import Parser
from astra.core.intent.classifier import Classifier
from astra.core.intent.context_resolver import ContextResolver
from astra.core.intent.nlu_enhancer import NaturalLanguageEnhancer
from astra.core.intent.llm_classifier import LLMClassifier
from astra.core.intent.models import IntentResult
from astra.core.intent.intents import (
    OPEN_APP,
    SAVE_MEMORY,
    RECALL_MEMORY,
    LIST_MEMORY,
    GET_TIME,
    ASK_KNOWLEDGE,
    CALCULATE,
    HELP,
    DELETE_FILE,
    SHUTDOWN_PC,
    FORMAT_DISK,
    RUN_GOAL,
    SYNC_MEMORY,
    COPY_CLIPBOARD,
    GET_CLIPBOARD,
    SYSTEM_INFO,
    OPEN_FOLDER,
    CREATE_ROUTINE,
    DELETE_ROUTINE,
    LIST_ROUTINES,
    LIST_SCHEDULES,
    FOCUS_WINDOW,
    SET_VOLUME,
    MINIMIZE_ALL,
    SCHEDULE_ROUTINE,
    ACTIVATE_WORKSPACE,
    LIST_WINDOWS,
    LIST_PROFILES,
    CREATE_PROFILE,
    SWITCH_PROFILE,
    WHO_AM_I,
    LIST_MARKETPLACE,
    INSTALL_PLUGIN,
    MORNING_BRIEF,
    ASK_AGENT,
    SET_MODE,
    SHOW_PLANS,
    SHOW_SQUAD,
    ACTIVATE_PLAN,
    REVOLUTION_STATUS,
    RUN_PROTOCOL,
    SHOW_ROI,
    START_TRIAL,
    SHOW_VOICE_SETTINGS,
    SET_ASSISTANT_NAME,
    SET_WAKE_PHRASE,
    TOGGLE_WAKE_WORD,
    SHOW_WEATHER,
    SHOW_CALENDAR,
    CONNECT_CALENDAR,
    SET_CITY,
    FOCUS_TIMER,
    DETECT_LOCATION,
    UNKNOWN,
)


class IntentEngine:

    SAVE_PREFIXES = ("remember", "memorize", "save my", "save that")

    RECALL_PREFIXES = (
        "what is my ",
        "what's my ",
        "whats my ",
        "tell me my ",
        "do you remember my ",
        "do you know my ",
        "recall my ",
        "what do you remember about my ",
        "recall ",
        "what do you know about ",
        "what do you remember about ",
    )

    KNOWLEDGE_PREFIXES = (
        "tell me about ",
        "explain ",
        "how does ",
        "how do ",
        "what is ",
    )

    DELETE_PREFIXES = ("delete ", "remove ", "erase ")

    CALCULATE_PREFIXES = ("calculate ", "compute ")

    def __init__(self, context_engine=None, llm_enabled: bool = None):

        self.parser = Parser()
        self.classifier = Classifier()
        self.context_resolver = ContextResolver()
        self.nlu = NaturalLanguageEnhancer()
        self.llm = LLMClassifier(enabled=llm_enabled)
        self.context = context_engine

    def register_patterns(self, intent: str, patterns: tuple) -> None:
        self.classifier.add_patterns(intent, patterns)

    def process(self, text: str) -> IntentResult:

        normalized = self.parser.normalize(text)

        if self.context:
            resolved = self.context_resolver.resolve(normalized, self.context)

            if resolved:
                return IntentResult(
                    intent=resolved["intent"],
                    entities=resolved["entities"],
                    confidence=resolved["confidence"],
                )

        intent = self.classifier.classify(normalized)

        if intent != UNKNOWN:
            entities = self._extract_entities(intent, normalized)
            return IntentResult(intent=intent, entities=entities, confidence=1.0)

        enhanced = self.nlu.enhance(normalized)

        if enhanced:
            return enhanced

        if self.llm.enabled:
            llm_result = self.llm.classify(text)

            if llm_result:
                return llm_result

        return IntentResult(intent=UNKNOWN, entities={}, confidence=0.0)

    def _extract_entities(self, intent: str, normalized: str) -> dict:

        if intent == OPEN_APP:
            words = normalized.split()
            if len(words) >= 2:
                return {"application": " ".join(words[1:])}
            return {}

        if intent == SAVE_MEMORY:
            memory_text = normalized

            for prefix in self.SAVE_PREFIXES:
                if memory_text.startswith(prefix):
                    memory_text = memory_text[len(prefix):].strip()
                    break

            return {"text": memory_text}

        if intent == RECALL_MEMORY:
            query = normalized

            for prefix in self.RECALL_PREFIXES:
                if query.startswith(prefix):
                    query = query[len(prefix):].strip()
                    break

            query = re.sub(r"[^\w\s]", "", query).strip()
            return {"query": query}

        if intent == ASK_KNOWLEDGE:
            query = normalized

            greeting_queries = {
                "hey astra", "hi astra", "hello astra", "hey", "hi", "hello",
                "good morning", "good afternoon", "good evening",
                "good morning astra", "thanks", "thank you", "ty",
            }
            if normalized in greeting_queries:
                return {"query": "greeting"}

            for prefix in self.KNOWLEDGE_PREFIXES:
                if query.startswith(prefix):
                    query = query[len(prefix):].strip()
                    break

            return {"query": query}

        if intent == CALCULATE:
            expression = normalized

            for prefix in self.CALCULATE_PREFIXES:
                if expression.startswith(prefix):
                    expression = expression[len(prefix):].strip()
                    break

            if expression.startswith("what is "):
                expression = expression[len("what is "):].strip()

            expression = (
                expression
                .replace("times", "*")
                .replace("multiplied by", "*")
                .replace("divided by", "/")
                .replace("plus", "+")
                .replace("minus", "-")
            )

            return {"expression": expression.strip()}

        if intent == DELETE_FILE:
            target = normalized

            for prefix in self.DELETE_PREFIXES:
                if target.startswith(prefix):
                    target = target[len(prefix):].strip()
                    break

            return {"target": target}

        if intent == FORMAT_DISK:
            drive = "C:"
            match = re.search(r"drive\s+(\w)", normalized)

            if match:
                drive = f"{match.group(1).upper()}:"

            return {"drive": drive}

        if intent == RUN_GOAL:
            goal = normalized

            for prefix in (
                "organize my ",
                "run my ",
                "run ",
                "start ",
                "execute ",
                "plan my ",
                "plan ",
            ):
                if goal.startswith(prefix):
                    goal = goal[len(prefix):].strip()
                    break

            goal = goal.replace(" routine", "").strip()
            return {"goal": goal or normalized}

        if intent == COPY_CLIPBOARD:
            text = normalized

            for prefix in ("copy to clipboard ", "copy "):
                if text.startswith(prefix):
                    text = text[len(prefix):].strip()
                    break

            return {"text": text}

        if intent == OPEN_FOLDER:
            folder = normalized

            for prefix in ("open folder ", "open my ", "open "):
                if folder.startswith(prefix):
                    folder = folder[len(prefix):].strip()
                    break

            folder = folder.replace(" folder", "").strip()
            return {"folder": folder}

        if intent == CREATE_ROUTINE:
            body = normalized[len("create routine "):].strip()
            if ":" in body:
                key, steps = body.split(":", 1)
                return {"key": key.strip(), "steps": steps.strip()}
            return {"key": body, "steps": ""}

        if intent == DELETE_ROUTINE:
            key = normalized[len("delete routine "):].strip()
            return {"key": key}

        if intent == SCHEDULE_ROUTINE:
            match = re.search(r"schedule\s+(.+?)\s+at\s+(.+)", normalized)
            if match:
                target = match.group(1).strip().replace(" ", "_")
                return {"routine": target, "time": match.group(2).strip()}
            return {"routine": "", "time": "08:00"}

        if intent == ACTIVATE_WORKSPACE:
            workspace = normalized.replace("activate ", "").replace(" workspace", "").strip()
            return {"workspace": workspace}

        if intent == CREATE_PROFILE:
            name = normalized.replace("create profile ", "", 1).strip()
            return {"name": name}

        if intent == SWITCH_PROFILE:
            for prefix in ("switch profile ", "use profile "):
                if normalized.startswith(prefix):
                    return {"profile": normalized[len(prefix):].strip()}
            return {"profile": ""}

        if intent == INSTALL_PLUGIN:
            plugin = normalized.replace("install plugin ", "", 1).strip()
            return {"plugin": plugin}

        if intent == ASK_AGENT:
            body = normalized
            for prefix in ("ask ", "tell "):
                if body.startswith(prefix):
                    body = body[len(prefix):].strip()
                    break
            for agent in ("nova", "pilot", "mentor", "launch", "ledger", "core"):
                if body.startswith(agent + " "):
                    return {
                        "agent": agent,
                        "query": body[len(agent):].strip(),
                    }
            return {"agent": "core", "query": body}

        if intent == SET_MODE:
            mode = normalized.replace(" mode", "").strip()
            if mode == "campus":
                mode = "student"
            return {"mode": mode}

        if intent == ACTIVATE_PLAN:
            tier = "campus"
            if "startup" in normalized:
                tier = "startup"
            elif "enterprise" in normalized:
                tier = "enterprise"
            elif "cosmic" in normalized or "free" in normalized:
                tier = "cosmic"
            return {"tier": tier}

        if intent == RUN_PROTOCOL:
            protocol = "revolution"
            if "student" in normalized:
                protocol = "student"
            elif "startup" in normalized:
                protocol = "startup"
            return {"protocol": protocol}

        if intent == START_TRIAL:
            tier = "campus"
            if "startup" in normalized:
                tier = "startup"
            return {"tier": tier}

        if intent == SET_ASSISTANT_NAME:
            for prefix in ("set assistant name to ", "rename assistant to "):
                if normalized.startswith(prefix):
                    return {"name": normalized[len(prefix):].strip()}
            return {"name": ""}

        if intent == SET_WAKE_PHRASE:
            for prefix in ("set wake phrase to ", "add wake phrase "):
                if normalized.startswith(prefix):
                    return {"phrase": normalized[len(prefix):].strip(), "mode": "chat"}
            return {"phrase": "", "mode": "chat"}

        if intent == TOGGLE_WAKE_WORD:
            enabled = normalized not in (
                "turn wake word off",
                "disable wake word",
                "wake word off",
            )
            return {"enabled": enabled}

        if intent == CONNECT_CALENDAR:
            url = normalized.replace("connect calendar ", "", 1).strip()
            return {"url": url}

        if intent == SET_CITY:
            for prefix in ("set city to ", "set location to "):
                if normalized.startswith(prefix):
                    return {"city": normalized[len(prefix):].strip()}
            return {"city": ""}

        if intent == FOCUS_TIMER:
            match = re.search(r"(\d+)", normalized)
            return {"minutes": int(match.group(1)) if match else 25}

        if intent == REVOLUTION_STATUS:
            return {}

        if intent == FOCUS_WINDOW:
            app = normalized[len("focus "):].strip()
            return {"application": app}

        if intent == SET_VOLUME:
            match = re.search(r"(\d+)", normalized)
            level = int(match.group(1)) if match else 50
            return {"level": level}

        if intent in (
            GET_TIME,
            LIST_MEMORY,
            HELP,
            SHUTDOWN_PC,
            SYNC_MEMORY,
            GET_CLIPBOARD,
            SYSTEM_INFO,
            LIST_ROUTINES,
            LIST_SCHEDULES,
            MINIMIZE_ALL,
            LIST_WINDOWS,
            LIST_PROFILES,
            WHO_AM_I,
            LIST_MARKETPLACE,
            MORNING_BRIEF,
            SHOW_PLANS,
            SHOW_SQUAD,
            REVOLUTION_STATUS,
            RUN_PROTOCOL,
            SHOW_ROI,
            START_TRIAL,
            SHOW_VOICE_SETTINGS,
            SHOW_WEATHER,
            SHOW_CALENDAR,
            DETECT_LOCATION,
        ):
            return {}

        return {}
