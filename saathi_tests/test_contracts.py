import asyncio
import pytest
from pydantic import ValidationError

from saathi.contracts import InboundMessage, Profile, Transcript
from saathi.config import Settings
from saathi.providers import ProviderRouter
from saathi.speech import fixture_audio


def test_extra_identity_fields_and_unsupported_locale_are_rejected():
    with pytest.raises(ValidationError):
        InboundMessage(external_id="one", text="book", user_id="forged")
    with pytest.raises(ValidationError):
        InboundMessage(external_id="one", text="book", locale="ml-IN")


def test_each_provider_role_swaps_independently_and_roundtrips_profiles():
    original = Settings()
    for role in ["reasoning", "conversation", "stt", "tts"]:
        settings = original.model_copy(deep=True)
        setattr(settings, role, Profile(provider="mock_alt", model="alternate-v1"))
        router = ProviderRouter(settings.profiles())
        assert router.profiles[role].provider == "mock_alt"
        assert all(
            p.provider == "mock" for r, p in router.profiles.items() if r != role
        )
        assert ProviderRouter(router.snapshot()).snapshot() == router.snapshot()


@pytest.mark.parametrize("locale", ["en-IN", "hi-IN", "ta-IN"])
@pytest.mark.parametrize("provider", ["mock", "mock_alt"])
def test_audio_fixtures_have_explicit_mock_transcripts(locale, provider):
    router = ProviderRouter(
        {**Settings().profiles(), "stt": Profile(provider=provider, model="fixture")}
    )
    transcript = asyncio.run(
        router.stt.transcribe(fixture_audio(locale), "audio/wav", locale)
    )
    assert isinstance(transcript, Transcript)
    assert transcript.locale == locale and transcript.mock
    assert (
        transcript.confidence is None
    )  # A lookup must not pretend calibrated ASR confidence.
    with pytest.raises(ValueError):
        asyncio.run(router.stt.transcribe(b"not audio", "audio/wav", locale))


def test_live_flags_do_not_enable_unapproved_runtime_and_unknown_provider_fails():
    with pytest.raises(ValueError):
        Settings(live_actions_enabled=True)
    with pytest.raises(ValueError):
        Settings(whatsapp_production_eligible=True)
    with pytest.raises(ValueError):
        ProviderRouter(
            {
                **Settings().profiles(),
                "reasoning": Profile(provider="unapproved", model="x"),
            }
        )
