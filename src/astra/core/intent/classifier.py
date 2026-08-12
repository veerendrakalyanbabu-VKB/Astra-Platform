import re

from astra.core.intent.intents import *


APP_NAMES = (
    "chrome",
    "notepad",
    "calc",
    "calculator",
    "code",
    "vscode",
)


class Classifier:

    def __init__(self):
        self._plugin_rules = []

    def add_patterns(self, intent: str, patterns: tuple) -> None:
        self._plugin_rules.append((intent, patterns))

    def classify(self, text: str):

        for intent, patterns in self._plugin_rules:
            for pattern in patterns:
                if text == pattern or text.startswith(pattern):
                    return intent

        if text.startswith("create routine "):
            return CREATE_ROUTINE

        if text.startswith("delete routine "):
            return DELETE_ROUTINE

        if text.startswith("create profile "):
            return CREATE_PROFILE

        if text.startswith("switch profile ") or text.startswith("use profile "):
            return SWITCH_PROFILE

        if text in (
            "list profiles",
            "show profiles",
            "my profiles",
        ):
            return LIST_PROFILES

        if text in (
            "who am i",
            "whoami",
            "current profile",
            "which profile",
        ):
            return WHO_AM_I

        if text in (
            "list marketplace",
            "show marketplace",
            "plugin marketplace",
            "browse plugins",
        ):
            return LIST_MARKETPLACE

        if text.startswith("install plugin "):
            return INSTALL_PLUGIN

        if text in (
            "list schedules",
            "show schedules",
            "my schedules",
            "scheduled tasks",
        ):
            return LIST_SCHEDULES

        if text.startswith("schedule ") and " at " in text:
            return SCHEDULE_ROUTINE

        if text.startswith("activate ") and "workspace" in text:
            return ACTIVATE_WORKSPACE

        if text.endswith(" workspace") and text.split()[0] in ("coding", "focus", "chill"):
            return ACTIVATE_WORKSPACE

        if text.startswith("plan my ") or text.startswith("plan "):
            return RUN_GOAL

        if text in (
            "list routines",
            "show routines",
            "my routines",
            "list my routines",
        ):
            return LIST_ROUTINES

        if text in (
            "sync my memory",
            "sync memory",
            "cloud sync",
            "sync to cloud",
            "backup my memory",
        ) or text.startswith((
            "sync my ",
            "export memory",
        )):
            return SYNC_MEMORY

        if text in (
            "system info",
            "system information",
            "computer info",
            "show system info",
            "what is my system info",
        ):
            return SYSTEM_INFO

        if text in (
            "show clipboard",
            "get clipboard",
            "what is on my clipboard",
            "what's on my clipboard",
            "read clipboard",
        ):
            return GET_CLIPBOARD

        if text.startswith((
            "copy ",
            "copy to clipboard ",
        )):
            return COPY_CLIPBOARD

        if text in (
            "minimize all",
            "minimize all windows",
            "minimize windows",
            "show desktop",
        ):
            return MINIMIZE_ALL

        if text in (
            "list windows",
            "show windows",
            "show open windows",
        ):
            return LIST_WINDOWS

        if text.startswith("focus "):
            return FOCUS_WINDOW

        if text.startswith(("set volume ", "volume ")):
            return SET_VOLUME

        if text.startswith((
            "open folder ",
            "open my ",
        )) and any(word in text for word in ("downloads", "documents", "desktop", "folder")):
            return OPEN_FOLDER

        if text.startswith((
            "run my ",
            "organize my ",
            "execute ",
        )) or text in (
            "morning routine",
            "focus mode",
            "work start",
            "organize my morning routine",
            "run my morning routine",
        ):
            return RUN_GOAL

        if text.startswith("run ") and "protocol" in text:
            return RUN_PROTOCOL

        if text in (
            "industrial revolution",
            "run student protocol",
            "run startup protocol",
            "run revolution protocol",
            "student revolution",
            "startup revolution",
            "full revolution",
        ):
            return RUN_PROTOCOL

        if text.startswith("run "):
            target = text[4:].strip().split()[0] if text[4:].strip() else ""
            if target not in APP_NAMES:
                return RUN_GOAL

        if text in (
            "show roi",
            "roi report",
            "my roi",
            "hours saved",
            "value saved",
            "show value",
        ):
            return SHOW_ROI

        if text in (
            "start trial",
            "free trial",
            "start free trial",
            "start campus trial",
            "start startup trial",
        ) or (text.startswith("start ") and "trial" in text):
            return START_TRIAL

        if text.startswith((
            "open",
            "launch",
            "start",
            "run",
        )):
            return OPEN_APP

        if text.startswith((
            "remember",
            "memorize",
        )):
            return SAVE_MEMORY

        if text.startswith("save my ") or text.startswith("save that "):
            return SAVE_MEMORY

        if text.startswith((
            "what is my ",
            "what's my ",
            "whats my ",
            "tell me my ",
            "do you remember my ",
            "do you know my ",
            "recall my ",
            "what do you remember about my ",
        )):
            return RECALL_MEMORY

        if text.startswith((
            "recall ",
            "what do you know about ",
            "what do you remember about ",
        )):
            return RECALL_MEMORY

        if text.startswith((
            "calculate ",
            "compute ",
        )):
            return CALCULATE

        if re.match(r"^what is [\d\s+\-*/().]+$", text):
            return CALCULATE

        if text.startswith((
            "learn about ",
            "learn on ",
            "teach yourself ",
            "research and learn ",
            "study and learn ",
            "add knowledge ",
            "learn that ",
            "remember as knowledge ",
        )):
            return LEARN_TOPIC

        if text in (
            "show knowledge",
            "list knowledge",
            "knowledge graph",
            "what have you learned",
            "what topics do you know",
            "show learned topics",
            "list topics",
        ):
            return LIST_KNOWLEDGE

        if text.startswith((
            "tell me about ",
            "explain ",
            "how does ",
            "how do ",
        )):
            return ASK_KNOWLEDGE

        if text.startswith("what is ") and not text.startswith("what is my "):
            return ASK_KNOWLEDGE

        if text in (
            "show my memory",
            "show memory",
            "list memory",
            "list my memory",
            "what do you remember",
            "what do you know",
            "what do you know about me",
            "what do you remember about me",
            "show what you remember",
            "what have you stored",
            "whats in your memory",
            "what is in your memory",
        ) or text.startswith((
            "show all memory",
            "list all memory",
        )):
            return LIST_MEMORY

        if text in (
            "help",
            "commands",
            "what can you do",
            "what do you do",
            "show commands",
            "show help",
        ):
            return HELP

        if text in (
            "hey astra",
            "hi astra",
            "hello astra",
            "hey",
            "hi",
            "hello",
            "good morning",
            "good afternoon",
            "good evening",
            "good morning astra",
            "thanks",
            "thank you",
            "ty",
        ):
            return ASK_KNOWLEDGE

        if text.startswith((
            "delete ",
            "remove ",
            "erase ",
        )):
            return DELETE_FILE

        if text in (
            "shutdown",
            "shut down",
            "shutdown pc",
            "shut down pc",
            "power off",
            "turn off computer",
        ):
            return SHUTDOWN_PC

        if text.startswith((
            "format ",
        )):
            return FORMAT_DISK

        if (
            "time" in text
            or "clock" in text
            or "current time" in text
            or "what time" in text
        ):
            return GET_TIME

        if text in (
            "morning brief",
            "daily brief",
            "brief me",
            "morning report",
            "give me my brief",
        ):
            return MORNING_BRIEF

        if text in (
            "show plans",
            "show pricing",
            "pricing",
            "upgrade plan",
            "my plan",
        ):
            return SHOW_PLANS

        if text in (
            "show squad",
            "list agents",
            "my team",
            "agent squad",
            "who is on my team",
        ):
            return SHOW_SQUAD

        if text in (
            "revolution status",
            "automation index",
            "revolution progress",
            "show revolution",
        ):
            return REVOLUTION_STATUS

        if text.startswith("activate ") and "plan" in text:
            return ACTIVATE_PLAN

        if text.endswith(" mode") or text in (
            "startup mode",
            "student mode",
            "personal mode",
            "campus mode",
        ):
            return SET_MODE

        if text.startswith(("ask ", "tell ")):
            for agent in ("nova", "pilot", "mentor", "launch", "ledger", "core"):
                if text.startswith(f"ask {agent} ") or text.startswith(f"tell {agent} "):
                    return ASK_AGENT

        if text in (
            "voice settings",
            "show voice settings",
            "wake settings",
            "show wake settings",
        ):
            return SHOW_VOICE_SETTINGS

        if text.startswith("set assistant name to ") or text.startswith("rename assistant to "):
            return SET_ASSISTANT_NAME

        if text.startswith("set wake phrase to ") or text.startswith("add wake phrase "):
            return SET_WAKE_PHRASE

        if text in (
            "turn wake word on",
            "enable wake word",
            "wake word on",
        ):
            return TOGGLE_WAKE_WORD

        if text in (
            "turn wake word off",
            "disable wake word",
            "wake word off",
        ):
            return TOGGLE_WAKE_WORD

        if text in (
            "show weather",
            "what's the weather",
            "whats the weather",
            "weather today",
            "how is the weather",
        ):
            return SHOW_WEATHER

        if text in (
            "show calendar",
            "my calendar",
            "today's schedule",
            "todays schedule",
            "what is on my calendar",
        ):
            return SHOW_CALENDAR

        if text.startswith("connect calendar "):
            return CONNECT_CALENDAR

        if text.startswith("set city to ") or text.startswith("set location to "):
            return SET_CITY

        if text.startswith("focus timer") or text.startswith("start focus"):
            return FOCUS_TIMER

        if text in (
            "detect my location",
            "detect location",
            "where am i",
            "my location",
            "auto location",
        ):
            return DETECT_LOCATION

        return UNKNOWN
