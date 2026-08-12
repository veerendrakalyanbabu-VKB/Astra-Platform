from astra.core.intent.intents import UNKNOWN
from astra.core.pipeline.result import PipelineResult
from astra.core.pipeline.compound import split_compound_command
from astra.core.observability.metrics import TimedOperation
from astra.core.planner.plan import Plan


class PipelineOrchestrator:

    def __init__(
        self,
        intent_engine,
        planner,
        reasoning_engine,
        executor,
        context_engine,
        permission_manager=None,
        safety_engine=None,
        learning_engine=None,
        session_manager=None,
        audit_logger=None,
        event_bus=None,
        metrics=None,
        logger=None,
        llm_responder=None,
        memory_manager=None,
        tier_manager=None,
        usage_tracker=None,
        revolution_engine=None,
        roi_engine=None,
    ):
        self.intent_engine = intent_engine
        self.planner = planner
        self.reasoning = reasoning_engine
        self.executor = executor
        self.context = context_engine
        self.permissions = permission_manager
        self.safety = safety_engine
        self.learning = learning_engine
        self.session = session_manager
        self.audit = audit_logger
        self.event_bus = event_bus
        self.metrics = metrics
        self.logger = logger
        self.llm_responder = llm_responder
        self.memory_manager = memory_manager
        self.tier_manager = tier_manager
        self.usage_tracker = usage_tracker
        self.revolution_engine = revolution_engine
        self.roi_engine = roi_engine

    def process(self, user_input: str) -> PipelineResult:

        if self.metrics:
            self.metrics.increment("pipeline.requests")

        parts = split_compound_command(user_input)

        if len(parts) > 1:
            intents = [self.intent_engine.process(part) for part in parts]

            if all(item.intent != UNKNOWN for item in intents):
                return self._process_compound(user_input, parts)

        return self._process_single(user_input)

    def _process_compound(self, user_input: str, parts: list) -> PipelineResult:

        messages = []
        last_result = None
        all_success = True

        for part in parts:
            last_result = self._process_single(part)

            if last_result.message:
                messages.append(last_result.message)

            if not last_result.executed and not last_result.blocked:
                all_success = False

            if last_result.needs_confirmation or last_result.blocked:
                last_result.message = " | ".join(messages)
                return last_result

        combined = PipelineResult(
            input=user_input,
            intent=last_result.intent,
            executed=all_success,
            message=" Then ".join(messages),
        )

        self.context.remember_conversation("User", user_input)
        self.context.remember_conversation("Astra", combined.message)
        self._persist_session()

        return combined

    def _process_single(self, user_input: str) -> PipelineResult:

        with TimedOperation(self.metrics, "pipeline.total") if self.metrics else _noop_context():

            intent = self.intent_engine.process(user_input)

            tier_id = self.tier_manager.tier_id if self.tier_manager else "cosmic"
            if self.usage_tracker:
                allowed, limit_msg = self.usage_tracker.check_allowed(
                    tier_id, intent.intent
                )
                if not allowed:
                    result = PipelineResult(
                        input=user_input,
                        intent=intent,
                        executed=False,
                        message=limit_msg,
                    )
                    self._update_context(user_input, intent, result)
                    self._record_learning(user_input, intent, result)
                    return result

            self._emit("intent.classified", {
                "input": user_input,
                "intent": intent.intent,
                "confidence": intent.confidence,
            })

            if self.logger:
                self.logger.info(
                    f"Intent classified: {intent.intent} (confidence={intent.confidence})"
                )

            if intent.intent == UNKNOWN:
                conversational = self._try_conversational_answer(user_input)

                if conversational:
                    result = PipelineResult(
                        input=user_input,
                        intent=intent,
                        executed=True,
                        message=conversational,
                    )
                    self._update_context(user_input, intent, result)
                    self._record_learning(user_input, intent, result)
                    return result

                result = PipelineResult(
                    input=user_input,
                    intent=intent,
                    executed=False,
                    message=(
                        "I'm not sure how to do that yet. Try asking naturally — "
                        "like \"what time is it\", \"show my memory\", or \"help me plan my morning\"."
                    ),
                )
                self._update_context(user_input, intent, result)
                self._record_learning(user_input, intent, result)
                return result

            plan = self.planner.create_plan(intent)

            self._emit("plan.created", {
                "action": plan.action,
                "parameters": plan.parameters,
            })

            if self.logger:
                self.logger.info(f"Plan created: {plan.action}")

            reasoning = self.reasoning.think(plan)
            decision = reasoning["decision"]["decision"]

            if self.safety:
                safety_result = self.safety.evaluate(plan, decision)

                if safety_result["decision"] != decision or safety_result["message"]:
                    decision = safety_result["decision"]
                    reasoning["decision"]["decision"] = decision

                    if safety_result["message"]:
                        reasoning["decision"]["message"] = safety_result["message"]

            self._emit("decision.made", {
                "action": plan.action,
                "decision": decision,
                "risk": reasoning["analysis"]["risk"],
            })

            if self.logger:
                risk = reasoning["analysis"]["risk"]
                self.logger.info(f"Reasoning decision: {decision} (risk={risk})")

            if decision == "BLOCK":
                if self.audit:
                    self.audit.log_block(plan.action, reasoning["decision"]["message"])

                result = PipelineResult(
                    input=user_input,
                    intent=intent,
                    plan=plan,
                    reasoning=reasoning,
                    executed=False,
                    blocked=True,
                    message=reasoning["decision"]["message"],
                )
                self._update_context(user_input, intent, result)
                self._record_learning(user_input, intent, result)
                return result

            if decision == "CONFIRM":
                if self.permissions:
                    self.permissions.request_confirmation(plan, reasoning)

                result = PipelineResult(
                    input=user_input,
                    intent=intent,
                    plan=plan,
                    reasoning=reasoning,
                    executed=False,
                    needs_confirmation=True,
                    message=reasoning["decision"]["message"],
                )
                return result

            return self._execute(user_input, intent, plan, reasoning)

    def execute_approved_plan(self, user_input: str = "confirmed") -> PipelineResult:

        if not self.permissions or not self.permissions.has_pending():
            return PipelineResult(
                input=user_input,
                intent=self.intent_engine.process(""),
                executed=False,
                message="Nothing to confirm.",
            )

        plan = self.permissions.pending_plan
        reasoning = self.permissions.pending_reasoning
        self.permissions.approve()

        if self.audit:
            self.audit.log_confirm(plan.action, approved=True)

        from astra.core.intent.models import IntentResult

        intent = IntentResult(
            intent=plan.action,
            entities=plan.parameters,
            confidence=1.0,
        )

        return self._execute(user_input, intent, plan, reasoning)

    def cancel_pending(self, user_input: str = "cancelled") -> PipelineResult:

        action = "UNKNOWN"

        if self.permissions and self.permissions.pending_plan:
            action = self.permissions.pending_plan.action

            if self.audit:
                self.audit.log_confirm(action, approved=False)

        if self.permissions:
            self.permissions.deny()

        result = PipelineResult(
            input=user_input,
            intent=self.intent_engine.process(user_input),
            executed=False,
            message="Action cancelled.",
        )
        self._update_context(user_input, result.intent, result)
        return result

    def _execute(self, user_input, intent, plan, reasoning) -> PipelineResult:

        if plan.is_multi_step:
            return self._execute_steps(user_input, intent, plan, reasoning)

        with TimedOperation(self.metrics, "pipeline.execute") if self.metrics else _noop_context():

            action_result = self.executor.execute(plan)

            if self.safety and action_result.success:
                self.safety.record_execution(plan.action)

            if self.audit:
                self.audit.log_execute(plan.action, action_result.success)

            self._emit("action.completed", {
                "action": plan.action,
                "success": action_result.success,
                "message": action_result.message,
            })

            result = PipelineResult(
                input=user_input,
                intent=intent,
                plan=plan,
                reasoning=reasoning,
                action_result=action_result,
                executed=action_result.success,
                message=action_result.message,
            )

            self._update_context(user_input, intent, result)
            self._record_learning(user_input, intent, result)
            return result

    def _execute_steps(self, user_input, intent, plan, reasoning) -> PipelineResult:

        title = plan.parameters.get("title", plan.parameters.get("goal", "routine"))
        messages = [f"Running {title}:"]
        all_success = True
        last_action_result = None

        for index, step in enumerate(plan.steps, start=1):
            step_plan = Plan(step.action, step.parameters)
            action_result = self.executor.execute(step_plan)
            last_action_result = action_result

            self._emit("goal.step.completed", {
                "goal": plan.parameters.get("goal"),
                "step": index,
                "action": step.action,
                "success": action_result.success,
            })

            if self.audit:
                self.audit.log_execute(step.action, action_result.success)

            messages.append(f"  Step {index}: {action_result.message}")

            if not action_result.success:
                all_success = False
                break

        combined_message = "\n".join(messages)

        result = PipelineResult(
            input=user_input,
            intent=intent,
            plan=plan,
            reasoning=reasoning,
            action_result=last_action_result,
            executed=all_success,
            message=combined_message,
        )

        self._update_context(user_input, intent, result)
        self._record_learning(user_input, intent, result)
        return result

    def _emit(self, event_type: str, payload: dict) -> None:
        if self.event_bus:
            self.event_bus.publish(event_type, payload)

    def _update_context(self, user_input, intent, result):

        self.context.remember_conversation("User", user_input)

        if result.message and not result.needs_confirmation:
            self.context.remember_conversation("Astra", result.message)

        self.context.remember_command(user_input)
        self.context.update_state("last_intent", intent.intent)

        if result.executed:
            self.context.update_state("last_action", intent.intent)

            if self.usage_tracker and self.tier_manager:
                self.usage_tracker.record(self.tier_manager.tier_id, intent.intent)

            if intent.intent == "OPEN_APP":
                application = intent.entities.get("application")

                if application:
                    self.context.update_state("last_application", application)

                elif result.action_result and result.action_result.data:
                    app = result.action_result.data.get("application")
                    if app:
                        self.context.update_state("last_application", app)

        self._persist_session()

    def _persist_session(self) -> None:
        if self.session:
            self.session.save(self.context)

    def _record_learning(self, user_input, intent, result) -> None:
        if self.revolution_engine:
            self.revolution_engine.record_command(result.executed, intent.intent)

        if self.roi_engine:
            self.roi_engine.record(result.executed, intent.intent)

        if self.learning:
            self.learning.record(
                user_input,
                intent.intent,
                result.executed,
                result.message,
            )

    def _try_conversational_answer(self, user_input: str) -> str | None:
        from astra.core.knowledge.local_responder import local_conversational_reply

        offline = local_conversational_reply(user_input)
        if offline:
            return offline

        if not self.llm_responder or not self.llm_responder.enabled:
            return None

        memory_entries = {}
        if self.memory_manager:
            memory_entries = self.memory_manager.list_all()

        conversation = self.context.conversation.all() if self.context else []

        return self.llm_responder.respond(user_input, memory_entries, conversation)


class _noop_context:
    def __enter__(self):
        return self

    def __exit__(self, exc_type, exc_val, exc_tb):
        return False
