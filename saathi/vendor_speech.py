"""Vendor HTTP contract spikes. Runtime router does not enable these live clients."""

import base64
import re
import httpx
from pydantic import SecretStr
from .contracts import Transcript, AudioResult
from .speech import validate_audio


class SpeechVendor:
    def __init__(
        self, provider, model, key: SecretStr, *, transport=None, live_allowed=False
    ):
        if provider not in {"sarvam", "elevenlabs"} or not model:
            raise ValueError("Explicit speech provider and model are required.")
        self.provider, self.model, self.key = provider, model, key
        self.transport, self.live_allowed = transport, live_allowed

    async def request(self, path, **kwargs):
        if self.transport is None and not self.live_allowed:
            raise ValueError("Live speech is disabled; use a contract-test transport.")
        if not self.key.get_secret_value():
            raise ValueError("Speech credential unavailable.")
        origin, header = (
            ("https://api.sarvam.ai", "api-subscription-key")
            if self.provider == "sarvam"
            else ("https://api.elevenlabs.io", "xi-api-key")
        )
        try:
            async with httpx.AsyncClient(
                transport=self.transport, timeout=20, follow_redirects=False
            ) as client:
                response = await client.post(
                    origin + path,
                    headers={header: self.key.get_secret_value()},
                    **kwargs,
                )
                if response.status_code != 200 or len(response.content) > 500000:
                    raise ValueError(
                        "Speech provider unavailable or response outside limits."
                    )
                return response
        except httpx.HTTPError:
            raise ValueError(
                "Speech provider transport failed; retry or use text."
            ) from None


class SarvamSTT(SpeechVendor):
    def __init__(self, model, key, **kwargs):
        super().__init__("sarvam", model, key, **kwargs)

    async def transcribe(self, audio, mime, language_hint=None):
        validate_audio(audio, mime)
        response = await self.request(
            "/speech-to-text",
            files={"file": ("audio.wav", audio, mime)},
            data={"model": self.model, "language_code": language_hint or "unknown"},
        )
        try:
            data = response.json()
            return Transcript(
                text=data["transcript"], locale=data["language_code"], mock=False
            )
        except (KeyError, ValueError, TypeError):
            raise ValueError(
                "Invalid Sarvam transcript; unsupported locale or payload."
            ) from None


class ElevenLabsSTT(SpeechVendor):
    def __init__(self, model, key, **kwargs):
        super().__init__("elevenlabs", model, key, **kwargs)

    async def transcribe(self, audio, mime, language_hint=None):
        validate_audio(audio, mime)
        fields = {"model_id": self.model}
        if language_hint:
            fields["language_code"] = language_hint.split("-")[0]
        response = await self.request(
            "/v1/speech-to-text",
            files={"file": ("audio.wav", audio, mime)},
            data=fields,
        )
        try:
            data = response.json()
            return Transcript(
                text=data["text"],
                locale={"en": "en-IN", "hi": "hi-IN", "ta": "ta-IN"}[
                    data["language_code"]
                ],
                mock=False,
            )
        except (KeyError, ValueError, TypeError):
            raise ValueError(
                "Invalid ElevenLabs transcript; unsupported locale or payload."
            ) from None


class SarvamTTS(SpeechVendor):
    def __init__(self, model, key, **kwargs):
        super().__init__("sarvam", model, key, **kwargs)

    async def synthesize(self, text, language, voice=None):
        if (
            not voice
            or language not in {"en-IN", "hi-IN", "ta-IN"}
            or not 1 <= len(text) <= 2000
        ):
            raise ValueError(
                "Explicit supported locale, voice and bounded text required."
            )
        response = await self.request(
            "/text-to-speech",
            json={
                "text": text,
                "language_code": language,
                "model": self.model,
                "speaker": voice,
                "speech_sample_rate": 16000,
                "output_audio_codec": "wav",
            },
        )
        try:
            audio = response.json()["audios"][0]
            validate_audio(base64.b64decode(audio, validate=True), "audio/wav")
            return AudioResult(audio_base64=audio, mock=False)
        except (KeyError, IndexError, ValueError, TypeError):
            raise ValueError("Invalid or unsupported Sarvam audio result.") from None


class ElevenLabsTTS(SpeechVendor):
    def __init__(self, model, key, **kwargs):
        super().__init__("elevenlabs", model, key, **kwargs)

    async def synthesize(self, text, language, voice=None):
        if (
            not voice
            or not re.fullmatch(r"[A-Za-z0-9_-]{1,80}", voice)
            or language not in {"en-IN", "hi-IN", "ta-IN"}
            or not 1 <= len(text) <= 2000
        ):
            raise ValueError(
                "Explicit supported locale, safe voice ID and bounded text required."
            )
        response = await self.request(
            f"/v1/text-to-speech/{voice}",
            params={"output_format": "mp3_44100_128"},
            json={
                "text": text,
                "model_id": self.model,
                "language_code": language.split("-")[0],
            },
        )
        if (
            "audio/" not in response.headers.get("content-type", "")
            or not response.content
        ):
            raise ValueError("Invalid ElevenLabs audio response.")
        return AudioResult(
            audio_base64=base64.b64encode(response.content).decode(),
            mime="audio/mpeg",
            mock=False,
        )
