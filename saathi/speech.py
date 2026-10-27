"""Explicit acoustic-token fixtures, not real speech recognition or TTS quality."""

import base64
import hashlib
import io
import math
import struct
import wave
from .contracts import Transcript, AudioResult

FIXTURES = {
    "en-IN": "Book dental cleaning in Chennai this Saturday morning",
    "hi-IN": "चेन्नई में इस शनिवार सुबह दांतों की सफाई बुक करें",
    "ta-IN": "சென்னையில் இந்த சனிக்கிழமை காலை பல் சுத்தம் பதிவு செய்யவும்",
}


def fixture_audio(locale):
    if locale not in FIXTURES:
        raise ValueError("Unsupported fixture locale.")
    frequency = {"en-IN": 440, "hi-IN": 550, "ta-IN": 660}[locale]
    output = io.BytesIO()
    with wave.open(output, "wb") as wav:
        wav.setparams((1, 2, 16000, 0, "NONE", "not compressed"))
        wav.writeframes(
            b"".join(
                struct.pack(
                    "<h", int(1000 * math.sin(2 * math.pi * frequency * n / 16000))
                )
                for n in range(4000)
            )
        )
    return output.getvalue()


def validate_audio(audio, mime):
    if mime != "audio/wav" or not 44 <= len(audio) <= 32044:
        raise ValueError("Provide a mock WAV fixture under32KB.")
    try:
        with wave.open(io.BytesIO(audio)) as wav:
            if (
                wav.getnchannels() != 1
                or wav.getsampwidth() != 2
                or wav.getframerate() != 16000
                or wav.getnframes() > 16000
            ):
                raise ValueError("Unsupported WAV parameters.")
    except (wave.Error, EOFError):
        raise ValueError("Invalid WAV input.") from None


class MockSTT:
    async def transcribe(self, audio, mime, language_hint=None):
        validate_audio(audio, mime)
        for locale, text in FIXTURES.items():
            if (
                hashlib.sha256(audio).digest()
                == hashlib.sha256(fixture_audio(locale)).digest()
            ):
                if language_hint and language_hint != locale:
                    raise ValueError(
                        "Fixture language does not match the requested locale."
                    )
                return Transcript(text=text, locale=locale, mock=True)
        raise ValueError(
            "Mock STT recognizes only the published synthetic acoustic fixtures; type your request instead."
        )


class AlternateMockSTT(MockSTT):
    """Second independently selected contract implementation, same bounded fixtures."""


class MockTTS:
    async def synthesize(self, text, language, voice=None):
        if not text or len(text) > 4000:
            raise ValueError("Invalid TTS text length.")
        return AudioResult(
            audio_base64=base64.b64encode(fixture_audio(language)).decode(), mock=True
        )


class AlternateMockTTS(MockTTS):
    pass
