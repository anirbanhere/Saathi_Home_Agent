import asyncio
import re
from datetime import date, timedelta
from .contracts import BookingIntent, ModelRequest, ModelResponse, Profile
from .speech import MockSTT, AlternateMockSTT, MockTTS, AlternateMockTTS


class MockModel:
    async def structured_generate(self, request, schema):
        text = request.text.casefold()
        city = (
            "Chennai"
            if any(s in text for s in ["chennai", "चेन्नई", "சென்னை", "சென்னையில்"])
            else "Bengaluru" if "bengaluru" in text else None
        )
        match = re.search(r"\b(\d{4}-\d{2}-\d{2})\b", text)
        when = match.group(1) if match else None
        today = date.fromisoformat(request.context["today"])
        if when is None and any(
            s in text for s in ["saturday", "शनिवार", "சனிக்கிழமை"]
        ):
            when = (today + timedelta(days=(5 - today.weekday()) % 7)).isoformat()
        if when is None and any(s in text for s in ["tomorrow", "कल", "நாளை"]):
            when = (today + timedelta(days=1)).isoformat()
        previous = request.context.get("intent", {})
        return schema.model_validate(
            {
                **previous,
                **({"city": city} if city else {}),
                **({"date": when} if when else {}),
            }
        )

    async def generate(self, request):
        code = request.context.get("event", "clarify")
        replies = {
            "en-IN": {
                "clarify": "Please provide the city (Chennai or Bengaluru) and exact appointment date (YYYY-MM-DD).",
                "slots": "Choose one of the MOCK clinic slots. Review the exact date and India time before approving.",
                "completed": "MOCK booking confirmed in the demo clinic. No real appointment or reminder message was sent.",
            },
            "hi-IN": {
                "clarify": "शहर (चेन्नई या Bengaluru) और तारीख YYYY-MM-DD में बताएं।",
                "slots": "डेमो क्लिनिक का समय चुनें। पुष्टि से पहले तारीख और भारतीय समय जांचें।",
                "completed": "डेमो क्लिनिक में MOCK बुकिंग दर्ज है। असली अपॉइंटमेंट या संदेश नहीं भेजा गया।",
            },
            "ta-IN": {
                "clarify": "நகரம் (Chennai அல்லது Bengaluru), தேதி YYYY-MM-DD கொடுக்கவும்.",
                "slots": "மாதிரி கிளினிக் நேரத்தைத் தேர்ந்தெடுக்கவும். தேதி மற்றும் இந்திய நேரத்தைச் சரிபார்க்கவும்.",
                "completed": "MOCK முன்பதிவு மாதிரி கிளினிக்கில் பதிவாகியுள்ளது. உண்மையான முன்பதிவோ செய்தியோ அனுப்பப்படவில்லை.",
            },
        }
        return ModelResponse(
            text=replies[request.locale].get(
                code, "MOCK task updated. See the saved status and details."
            )
        )


class AlternateMockModel(MockModel):
    async def structured_generate(self, request, schema):
        # Deliberately returns a fresh validated instance through the same contract.
        result = await super().structured_generate(request, schema)
        return schema.model_validate(result.model_dump())


class ProviderRouter:
    def __init__(self, profiles):
        if set(profiles) != {"reasoning", "conversation", "stt", "tts"}:
            raise ValueError("Configure exactly four independent provider roles.")
        self.profiles = {r: Profile.model_validate(p) for r, p in profiles.items()}
        if any(p.provider not in {"mock", "mock_alt"} for p in self.profiles.values()):
            raise ValueError(
                "Phase1 runtime allows only mock/mock_alt. Live vendor adapters require separate acceptance."
            )
        for role, p in self.profiles.items():
            factory = (
                {"stt": AlternateMockSTT, "tts": AlternateMockTTS}.get(
                    role, AlternateMockModel
                )
                if p.provider == "mock_alt"
                else {"stt": MockSTT, "tts": MockTTS}.get(role, MockModel)
            )
            setattr(self, role, factory())

    def snapshot(self):
        return {r: p.model_dump() for r, p in self.profiles.items()}

    async def intent(self, request):
        return await asyncio.wait_for(
            self.reasoning.structured_generate(request, BookingIntent),
            self.profiles["reasoning"].timeout_seconds,
        )

    async def reply(self, request):
        return await asyncio.wait_for(
            self.conversation.generate(request),
            self.profiles["conversation"].timeout_seconds,
        )
