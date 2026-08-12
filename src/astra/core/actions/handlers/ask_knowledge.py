from typing import Dict

from astra.core.intent.intents import ASK_KNOWLEDGE
from astra.core.actions.handlers.base import ActionHandler
from astra.core.actions.result import ActionResult


class AskKnowledgeHandler(ActionHandler):

    def __init__(self, knowledge_engine, llm_responder=None):
        self.knowledge = knowledge_engine
        self.llm = llm_responder

    def can_handle(self, action: str) -> bool:
        return action == ASK_KNOWLEDGE

    def execute(self, parameters: Dict) -> ActionResult:
        query = parameters.get("query", "").strip()

        if not query:
            return ActionResult(
                success=False,
                message="What would you like to know?",
                error="EMPTY_QUERY",
            )

        answer = self.knowledge.best_match(query)

        if answer is None and self.llm and self.llm.enabled:
            llm_answer = self.llm.respond(query)
            if llm_answer:
                return ActionResult(
                    success=True,
                    message=llm_answer,
                    data={"query": query, "source": "llm"},
                )

        if answer is None:
            topics = ", ".join(self.knowledge.list_topics())
            return ActionResult(
                success=False,
                message=f"I don't have knowledge about that. Try: {topics}",
                error="NOT_FOUND",
            )

        return ActionResult(
            success=True,
            message=answer,
            data={"query": query, "source": "local"},
        )
