import argparse
import asyncio
import base64
import json
from pathlib import Path
from uuid import uuid4
from datetime import datetime, timedelta
from .config import Settings
from .channels import LocalChannel
from .db import Store
from .runtime import Runtime
from .speech import fixture_audio
from .outbox import drain_mock


async def demo(runtime, locale, voice=False, ambiguous=False):
    user = runtime.create_user(locale)
    channel = LocalChannel("test_cli")
    payload = {"external_id": uuid4().hex, "locale": locale}
    if voice:
        payload["audio_base64"] = base64.b64encode(fixture_audio(locale)).decode()
    else:
        payload["text"] = "Book dental cleaning in Chennai tomorrow"
    task = await runtime.handle(user, await channel.normalize_inbound(payload))
    if task["status"] != "PLANNED":
        return {
            "status": task["status"],
            "reply": task["payload"]["reply"],
            "mock": True,
        }
    preview = runtime.preview(
        user, task["id"], task["payload"]["slots"][0]["id"], task["version"]
    )
    print("MOCK ONLY: no real booking, speech recognition or external reminder.")
    print(json.dumps(preview["payload"]["preview"], ensure_ascii=False, indent=2))
    # This scripted path is an explicit synthetic approval event, never an LLM decision.
    runtime.mock_commit_timeout = ambiguous
    a = preview["payload"]["approval"]
    result = runtime.decide(user, a["id"], "approve", a["token"], preview["version"])
    if result["status"] == "RECONCILIATION_REQUIRED":
        result = runtime.reconcile(user, result["id"], result["version"])
    # Explicit time advance, mock delivery sink, no real-world message.
    delivery = drain_mock(
        runtime.store,
        user,
        now=datetime.fromisoformat(preview["payload"]["preview"]["starts_at"])
        + timedelta(days=1),
    )
    return {
        "task_id": result["id"],
        "status": result["status"],
        "receipt": result["payload"].get("receipt"),
        "profiles": result["profiles"],
        "delivery": delivery,
        "mock": True,
    }


def main():
    parser = argparse.ArgumentParser(
        description="Saathi Phase1 local mock demo; no live actions"
    )
    parser.add_argument("command", choices=["demo", "fixtures", "providers", "migrate"])
    parser.add_argument(
        "--locale", choices=["en-IN", "hi-IN", "ta-IN"], default="en-IN"
    )
    parser.add_argument(
        "--voice",
        action="store_true",
        help="Use an acoustic-token fixture, not actual ASR",
    )
    parser.add_argument("--simulate-timeout", action="store_true")
    parser.add_argument(
        "--approve-mock",
        action="store_true",
        help="Explicitly authorize the scripted mock booking",
    )
    args = parser.parse_args()
    settings = Settings.load()
    if args.command == "fixtures":
        folder = Path("artifacts/saathi-audio")
        folder.mkdir(parents=True, exist_ok=True)
        for locale in ["en-IN", "hi-IN", "ta-IN"]:
            (folder / f"{locale}.wav").write_bytes(fixture_audio(locale))
        print(
            "Wrote synthetic acoustic-token fixtures under artifacts/saathi-audio; not speech recordings."
        )
        return
    if args.command == "providers":
        from .providers import ProviderRouter

        print(json.dumps(ProviderRouter(settings.profiles()).snapshot(), indent=2))
        return
    store = Store(settings.database_url)
    try:
        if args.command == "migrate":
            print(
                "Saathi mock schema migrated; existing Home Agents data is untouched."
            )
        else:
            if not args.approve_mock:
                parser.error(
                    "demo requires --approve-mock: this consents only to the synthetic scripted scenario"
                )
            print(
                json.dumps(
                    asyncio.run(
                        demo(
                            Runtime(store, settings),
                            args.locale,
                            args.voice,
                            ambiguous=args.simulate_timeout,
                        )
                    ),
                    ensure_ascii=False,
                    indent=2,
                )
            )
    finally:
        store.engine.dispose()


if __name__ == "__main__":
    main()
