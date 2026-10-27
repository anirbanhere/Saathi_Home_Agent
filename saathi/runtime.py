"""Bounded mock dental workflow. No live operation or provider credentials enter here."""

import asyncio
import base64
import copy
import hashlib
import logging
import secrets
from datetime import datetime, date, timedelta, timezone
from uuid import uuid4
from zoneinfo import ZoneInfo
from sqlalchemy import select, update, func
from .contracts import InboundMessage, ModelRequest, TaskPlan, Step, Action
from .db import schema as s
from .policy import Policy, digest, verify_token
from .providers import ProviderRouter
from .state import check_transition

log = logging.getLogger("saathi.events")


class DomainError(ValueError):
    def __init__(self, message, code="CONFLICT", status=409):
        super().__init__(message)
        self.code, self.status = code, status


class Runtime:
    def __init__(self, store, settings, clock=None):
        self.store, self.settings = store, settings
        self.clock = clock or (lambda: datetime.now(timezone.utc))
        self.policy = Policy()
        self.mock_commit_timeout = (
            False  # Test injection only; absent from HTTP/config/model inputs.
        )

    def now(self):
        return self.clock().astimezone(timezone.utc).isoformat()

    def create_user(self, locale):
        if locale not in {"en-IN", "hi-IN", "ta-IN"}:
            raise DomainError("Unsupported initial locale.", "UNSUPPORTED_LOCALE", 422)
        user = uuid4().hex
        with self.store.transaction() as c:
            c.execute(
                s.users.insert().values(id=user, locale=locale, created_at=self.now())
            )
        return user

    def _task(self, c, user, task_id):
        row = (
            c.execute(
                select(s.tasks)
                .where(s.tasks.c.id == task_id, s.tasks.c.user_id == user)
                .with_for_update()
            )
            .mappings()
            .first()
        )
        if not row:
            raise DomainError("Task not found.", "NOT_FOUND", 404)
        return copy.deepcopy(dict(row))

    def get(self, user, task_id):
        with self.store.transaction(user) as c:
            return self._task(c, user, task_id)

    def list_tasks(self, user):
        with self.store.transaction(user) as c:
            return [
                dict(row)
                for row in c.execute(
                    select(s.tasks)
                    .where(s.tasks.c.user_id == user)
                    .order_by(s.tasks.c.updated_at.desc())
                    .limit(100)
                ).mappings()
            ]

    def _audit(self, c, task, event):
        c.execute(
            s.audit.insert().values(
                id=uuid4().hex,
                user_id=task["user_id"],
                task_id=task["id"],
                event=event,
                at=self.now(),
            )
        )
        # IDs and event code only; no transcript, audio, preview token or internal reasoning.
        log.info("task_event", extra={"task_id": task["id"], "event_code": event})

    def _save(self, c, task, status):
        check_transition(task["status"], status)
        task["status"], task["version"], task["updated_at"] = (
            status,
            task["version"] + 1,
            self.now(),
        )
        c.execute(
            update(s.tasks)
            .where(s.tasks.c.id == task["id"])
            .values(
                status=status,
                version=task["version"],
                updated_at=task["updated_at"],
                payload=task["payload"],
            )
        )
        self._audit(c, task, status)
        return task

    def _version(self, task, version):
        if (
            isinstance(version, bool)
            or not isinstance(version, int)
            or task["version"] != version
        ):
            raise DomainError("Task changed; reload and review the current version.")

    def _slots(self, c, intent):
        result = []
        for hour in [10, 11]:
            start = datetime.fromisoformat(f"{intent.date}T{hour}:30:00+05:30")
            if start <= self.clock():
                continue
            slot_id = digest([intent.city, start.isoformat()])[:32]
            values = dict(
                id=slot_id, city=intent.city, starts_at=start.isoformat(), revision=1
            )
            if c.dialect.name == "postgresql":
                from sqlalchemy.dialects.postgresql import insert
            else:
                from sqlalchemy.dialects.sqlite import insert
            c.execute(
                insert(s.slots)
                .values(**values)
                .on_conflict_do_nothing(index_elements=[s.slots.c.id])
            )
            row = (
                c.execute(select(s.slots).where(s.slots.c.id == slot_id))
                .mappings()
                .one()
            )
            if row["booked_task"] is None:
                result.append(
                    {
                        "id": slot_id,
                        "city": row["city"],
                        "starts_at": row["starts_at"],
                        "timezone": "Asia/Kolkata",
                        "revision": row["revision"],
                        "clinic": "Saathi MOCK Dental Clinic",
                        "service": "dental_cleaning",
                        "amount_paise": 0,
                        "currency": "INR",
                        "mock": True,
                    }
                )
        return result

    async def handle(self, user_id, message: InboundMessage):
        fingerprint = digest(message.model_dump())
        with self.store.transaction(user_id) as c:
            if not c.scalar(select(s.users.c.id).where(s.users.c.id == user_id)):
                raise DomainError("Unknown mock principal.", "UNAUTHORIZED", 401)
            previous = (
                c.execute(
                    select(s.messages).where(
                        s.messages.c.user_id == user_id,
                        s.messages.c.channel == message.channel,
                        s.messages.c.external_id == message.external_id,
                    )
                )
                .mappings()
                .first()
            )
            if previous:
                if previous["fingerprint"] != fingerprint:
                    raise DomainError("Message ID has different contents.")
                return previous["response"]
            conversation = message.conversation_id
            if conversation:
                if not c.scalar(
                    select(s.conversations.c.id).where(
                        s.conversations.c.id == conversation,
                        s.conversations.c.user_id == user_id,
                        s.conversations.c.channel == message.channel,
                    )
                ):
                    raise DomainError("Conversation not found.", "NOT_FOUND", 404)
            else:
                conversation = uuid4().hex
                c.execute(
                    s.conversations.insert().values(
                        id=conversation, user_id=user_id, channel=message.channel
                    )
                )
            existing = (
                c.execute(
                    select(s.tasks)
                    .where(
                        s.tasks.c.conversation_id == conversation,
                        s.tasks.c.status == "CLARIFICATION_REQUIRED",
                    )
                    .with_for_update()
                )
                .mappings()
                .first()
            )
            if existing:
                task = copy.deepcopy(dict(existing))
            else:
                count = c.scalar(
                    select(func.count())
                    .select_from(s.tasks)
                    .where(s.tasks.c.user_id == user_id)
                )
                if count >= self.settings.max_tasks_per_user:
                    raise DomainError("Mock task budget reached.", "TASK_BUDGET", 429)
                task = dict(
                    id=uuid4().hex,
                    user_id=user_id,
                    conversation_id=conversation,
                    status="RECEIVED",
                    version=0,
                    locale=message.locale,
                    payload={"mock": True},
                    profiles=ProviderRouter(self.settings.profiles()).snapshot(),
                    updated_at=self.now(),
                )
                c.execute(s.tasks.insert().values(**task))
                self._audit(c, task, "RECEIVED")
            router = ProviderRouter(task["profiles"])
            text = message.text
            if message.audio_base64:
                try:
                    audio = base64.b64decode(message.audio_base64, validate=True)
                    transcript = await asyncio.wait_for(
                        router.stt.transcribe(audio, message.mime, message.locale),
                        router.profiles["stt"].timeout_seconds,
                    )
                    text = transcript.text
                    task["payload"]["transcript"] = {
                        "text": transcript.text,
                        "mock": transcript.mock,
                        "confidence": transcript.confidence,
                    }
                except ValueError:
                    raise DomainError(
                        "Mock audio fixture unavailable or invalid. Use text instead.",
                        "SPEECH_INPUT",
                        422,
                    ) from None
            self._save(c, task, "UNDERSTANDING")
            intent = await router.intent(
                ModelRequest(
                    text=text,
                    locale=message.locale,
                    context={
                        "today": self.clock()
                        .astimezone(ZoneInfo("Asia/Kolkata"))
                        .date()
                        .isoformat(),
                        "intent": task["payload"].get("intent", {}),
                    },
                )
            )
            task["payload"]["intent"] = intent.model_dump()
            missing = not intent.city or not intent.date
            if not missing:
                try:
                    requested = date.fromisoformat(intent.date)
                    today = self.clock().astimezone(ZoneInfo("Asia/Kolkata")).date()
                    if not today <= requested <= today + timedelta(days=90):
                        raise ValueError()
                except ValueError:
                    raise DomainError(
                        "Use a valid date within the next90 days; review the exact India date.",
                        "INVALID_DATE",
                        422,
                    ) from None
                self.policy.check("appointments.search", Action.READ, mock=True)
                task["payload"]["slots"] = self._slots(c, intent)
                plan = TaskPlan(
                    goal="Book one no-charge MOCK dental cleaning",
                    steps=[
                        Step(
                            tool=name,
                            action=action,
                            requires_approval=action == Action.BOOK,
                            prerequisite=(
                                None if i == 0 else list(self.policy.allowed)[i - 1]
                            ),
                            expected_output=output,
                        )
                        for i, ((name, action), output) in enumerate(
                            zip(
                                self.policy.allowed.items(),
                                [
                                    "mock_slot_options",
                                    "canonical_preview",
                                    "verified_mock_reference",
                                    "durable_reminder_intent",
                                ],
                            )
                        )
                    ],
                )
                task["payload"]["plan"] = plan.model_dump(mode="json")
                status = (
                    "PLANNED" if task["payload"]["slots"] else "REQUIRES_USER_ACTION"
                )
            else:
                status = "CLARIFICATION_REQUIRED"
            reply = await router.reply(
                ModelRequest(
                    text="",
                    locale=task["locale"],
                    context={"event": "clarify" if missing else "slots"},
                )
            )
            task["payload"]["reply"] = reply.text
            self._save(c, task, status)
            c.execute(
                s.messages.insert().values(
                    id=uuid4().hex,
                    user_id=user_id,
                    conversation_id=conversation,
                    channel=message.channel,
                    external_id=message.external_id,
                    fingerprint=fingerprint,
                    response=task,
                )
            )
            return task

    def preview(self, user, task_id, slot_id, version):
        with self.store.transaction(user) as c:
            task = self._task(c, user, task_id)
            self._version(task, version)
            if task["status"] not in {"PLANNED", "APPROVAL_PENDING"}:
                raise DomainError(
                    "Search or review a current slot before preparing a booking."
                )
            self.policy.check("appointments.prepare", Action.DRAFT, mock=True)
            slot = next(
                (slot for slot in task["payload"]["slots"] if slot["id"] == slot_id),
                None,
            )
            current = (
                c.execute(select(s.slots).where(s.slots.c.id == slot_id))
                .mappings()
                .first()
            )
            if (
                not slot
                or not current
                or current["booked_task"]
                or slot["revision"] != current["revision"]
                or datetime.fromisoformat(current["starts_at"]) <= self.clock()
            ):
                raise DomainError("Slot changed or expired; search again.")
            expires = (
                (self.clock() + timedelta(seconds=self.settings.approval_ttl_seconds))
                .astimezone(timezone.utc)
                .isoformat()
            )
            preview = {
                **slot,
                "task_id": task_id,
                "user_id": user,
                "version": version + 1,
                "expires_at": expires,
                "action": "BOOK",
                "cancellation_terms": "No real appointment. Demo commitment has no real cancellation/refund service.",
            }
            token, approval_id = secrets.token_urlsafe(32), uuid4().hex
            task["payload"]["preview"] = preview
            task["payload"]["approval"] = {
                "id": approval_id,
                "expires_at": expires,
                "preview_hash": digest(preview),
            }
            self._save(c, task, "APPROVAL_PENDING")
            c.execute(
                s.approvals.insert().values(
                    id=approval_id,
                    user_id=user,
                    task_id=task_id,
                    version=task["version"],
                    preview_hash=digest(preview),
                    token_hash=hashlib.sha256(token.encode()).hexdigest(),
                    expires_at=expires,
                )
            )
            # Raw nonce exists only in this response, not SQL, message history or audit logs.
            result = copy.deepcopy(task)
            result["payload"]["approval"]["token"] = token
            return result

    def decide(self, user, approval_id, decision, token, version):
        with self.store.transaction(user) as c:
            approval = (
                c.execute(
                    select(s.approvals)
                    .where(
                        s.approvals.c.id == approval_id, s.approvals.c.user_id == user
                    )
                    .with_for_update()
                )
                .mappings()
                .first()
            )
            if not approval or not verify_token(token, approval["token_hash"]):
                raise DomainError(
                    "Approval not found or token invalid.", "INVALID_APPROVAL", 403
                )
            task = self._task(c, user, approval["task_id"])
            if approval["decision"] is not None:
                if approval["decision"] == decision:
                    return task  # Same authorized request returns the prior effect, never executes again.
                raise DomainError("Approval already used.")
            self._version(task, version)
            if (
                task["status"] != "APPROVAL_PENDING"
                or approval["version"] != version
                or task["payload"]["approval"]["id"] != approval_id
            ):
                raise DomainError("Approval is stale; review again.")
            if datetime.fromisoformat(approval["expires_at"]) <= self.clock():
                raise DomainError("Approval expired; request a fresh preview.")
            if approval["preview_hash"] != digest(task["payload"]["preview"]):
                raise DomainError("Preview changed; new approval required.")
            if decision not in {"approve", "reject", "edit"}:
                raise DomainError(
                    "Choose approve, reject or edit.", "INVALID_DECISION", 422
                )
            c.execute(
                update(s.approvals)
                .where(s.approvals.c.id == approval_id)
                .values(decision=decision)
            )
            if decision in {"reject", "edit"}:
                task["payload"].pop("approval", None)
                task["payload"].pop("preview", None)
                return self._save(
                    c, task, "REJECTED" if decision == "reject" else "PLANNED"
                )
            self.policy.check(
                "appointments.book", Action.BOOK, mock=True, approved=True
            )
            slot = task["payload"]["preview"]
            if datetime.fromisoformat(slot["starts_at"]) <= self.clock():
                return self._save(c, task, "REQUIRES_USER_ACTION")
            changed = c.execute(
                update(s.slots)
                .where(
                    s.slots.c.id == slot["id"],
                    s.slots.c.booked_task.is_(None),
                    s.slots.c.revision == slot["revision"],
                )
                .values(booked_task=task["id"], revision=s.slots.c.revision + 1)
            )
            if changed.rowcount != 1:
                task["payload"][
                    "reply"
                ] = "Slot no longer available. Search and approve a new preview; no booking was created."
                return self._save(c, task, "REQUIRES_USER_ACTION")
            self._save(c, task, "APPROVED")
            self._save(c, task, "COMMITTING")
            operation_id = digest(
                [task["id"], "appointments.book", approval["version"]]
            )
            receipt = {
                "reference": "MOCK-BOOKING-" + operation_id[:16],
                "mock": True,
                "slot": slot["starts_at"],
                "clinic": slot["clinic"],
                "verified": True,
                "amount_paise": 0,
            }
            c.execute(
                s.operations.insert().values(
                    id=operation_id,
                    task_id=task["id"],
                    status="mock_confirmed",
                    reference=receipt["reference"],
                    receipt=receipt,
                )
            )
            if self.mock_commit_timeout:
                task["payload"][
                    "reply"
                ] = "MOCK provider response lost. Reconcile the saved operation; do not book again."
                return self._save(c, task, "RECONCILIATION_REQUIRED")
            return self._complete(c, task, receipt)

    def _complete(self, c, task, receipt):
        self._save(c, task, "VERIFYING")
        if not receipt.get("verified") or not receipt.get("reference", "").startswith(
            "MOCK-BOOKING-"
        ):
            raise DomainError("Mock receipt could not be verified.")
        task["payload"]["receipt"] = receipt
        task["payload"]["reply"] = {
            "en-IN": "MOCK booking confirmed. Reminder intent saved; no external notification or real appointment.",
            "hi-IN": "MOCK बुकिंग दर्ज हुई। रिमाइंडर केवल डेमो में सहेजा गया; असली संदेश नहीं भेजा गया।",
            "ta-IN": "MOCK முன்பதிவு பதிவாகியது. நினைவூட்டல் மாதிரி மட்டும்; உண்மையான செய்தி அனுப்பப்படவில்லை.",
        }[task["locale"]]
        due = datetime.fromisoformat(
            task["payload"]["preview"]["starts_at"]
        ) - timedelta(hours=1)
        c.execute(
            s.outbox.insert().values(
                id=uuid4().hex,
                user_id=task["user_id"],
                task_id=task["id"],
                dedupe_key=task["id"] + ":reminder",
                event="notification.scheduled",
                payload={"mock": True, "channel": "test_cli", "locale": task["locale"]},
                due_at=due.astimezone(timezone.utc).isoformat(),
                status="pending",
            )
        )
        return self._save(c, task, "COMPLETED")

    def reconcile(self, user, task_id, version):
        with self.store.transaction(user) as c:
            task = self._task(c, user, task_id)
            if task["status"] == "COMPLETED":
                return task
            self._version(task, version)
            if task["status"] != "RECONCILIATION_REQUIRED":
                raise DomainError("This task has no uncertain operation to reconcile.")
            receipt = c.scalar(
                select(s.operations.c.receipt).where(s.operations.c.task_id == task_id)
            )
            if not receipt:
                raise DomainError(
                    "No verified operation; manual reconciliation required."
                )
            return self._complete(c, task, receipt)

    def cancel(self, user, task_id, version):
        with self.store.transaction(user) as c:
            task = self._task(c, user, task_id)
            if task["status"] == "CANCELLED":
                return task
            self._version(task, version)
            if task["status"] in {
                "COMPLETED",
                "COMMITTING",
                "VERIFYING",
                "RECONCILIATION_REQUIRED",
            }:
                raise DomainError(
                    "Committed/uncertain operation needs provider cancellation or reconciliation; no cancellation was claimed."
                )
            task["payload"].pop("approval", None)
            task["payload"][
                "reply"
            ] = "Mock task cancelled before commitment. No booking or notification was sent."
            return self._save(c, task, "CANCELLED")
