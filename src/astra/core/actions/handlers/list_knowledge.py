from typing import Dict

from astra.core.intent.intents import LIST_KNOWLEDGE
from astra.core.actions.handlers.base import ActionHandler
from astra.core.actions.result import ActionResult


class ListKnowledgeHandler(ActionHandler):

    def __init__(self, knowledge_engine):
        self.knowledge = knowledge_engine

    def can_handle(self, action: str) -> bool:
        return action == LIST_KNOWLEDGE

    def execute(self, parameters: Dict) -> ActionResult:
        topics = self.knowledge.list_topics()
        learned = self.knowledge.list_learned_topics()
        total = len(topics)

        if not topics:
            return ActionResult(
                success=True,
                message="Knowledge graph is empty. Say 'learn about quantum computing' to grow the core.",
            )

        lines = [f"Knowledge graph — {total} topics ({len(learned)} learned by you/Astra):"]
        for entry in self.knowledge.list_entries():
            tag = "· learned" if entry.get("source") == "learned" else "· core"
            preview = (entry.get("content") or "")[:72].replace("\n", " ")
            lines.append(f"  • {entry['topic']} {tag} — {preview}…")

        return ActionResult(
            success=True,
            message="\n".join(lines),
            data={"topics": topics, "learned": learned, "total": total},
        )
