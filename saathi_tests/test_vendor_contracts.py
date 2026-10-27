import asyncio
import base64
import json
import httpx
import pytest
from pydantic import SecretStr
from saathi.speech import fixture_audio
from saathi.vendor_speech import SarvamSTT, ElevenLabsSTT, SarvamTTS, ElevenLabsTTS


@pytest.mark.parametrize("kind", [SarvamSTT, ElevenLabsSTT])
@pytest.mark.parametrize("locale", ["en-IN", "hi-IN", "ta-IN"])
def test_vendor_stt_normalizes_without_network_or_fake_confidence(kind, locale):
    seen = []

    def reply(request):
        seen.append(request)
        return httpx.Response(
            200,
            json={
                "text": "synthetic transcript",
                "transcript": "synthetic transcript",
                "language_code": locale if kind is SarvamSTT else locale.split("-")[0],
                "language_probability": 0.99,
            },
        )

    client = kind(
        "explicit-model", SecretStr("synthetic"), transport=httpx.MockTransport(reply)
    )
    result = asyncio.run(client.transcribe(fixture_audio(locale), "audio/wav", locale))
    assert result.locale == locale and not result.mock and result.confidence is None
    assert b"explicit-model" in seen[0].content


@pytest.mark.parametrize("kind", [SarvamTTS, ElevenLabsTTS])
def test_vendor_tts_normalizes_and_live_default_is_denied(kind):
    audio = fixture_audio("en-IN")

    def reply(request):
        payload = json.loads(request.content)
        if kind is SarvamTTS:
            assert (
                payload["language_code"] == "en-IN"
                and payload["speech_sample_rate"] == 16000
            )
            assert "target_language_code" not in payload
        return (
            httpx.Response(200, json={"audios": [base64.b64encode(audio).decode()]})
            if kind is SarvamTTS
            else httpx.Response(
                200, content=b"synthetic mp3", headers={"content-type": "audio/mpeg"}
            )
        )

    client = kind(
        "explicit-model", SecretStr("synthetic"), transport=httpx.MockTransport(reply)
    )
    assert not asyncio.run(client.synthesize("hello", "en-IN", "configured_voice")).mock
    with pytest.raises(ValueError, match="disabled"):
        asyncio.run(
            kind("model", SecretStr("unused")).synthesize(
                "hello", "en-IN", "configured_voice"
            )
        )
