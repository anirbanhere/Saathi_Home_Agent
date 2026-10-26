"""Authenticated RailRadar reports with explicit freshness and no fixture fallback."""
import copy
import hashlib
import json
import os
import re
import threading
from collections import OrderedDict, deque
from datetime import date, datetime, timedelta, timezone
from urllib.error import HTTPError, URLError
from urllib.request import HTTPRedirectHandler, Request, build_opener

from .errors import AppError

DOCS = "https://railradar.in/docs/live-train-status"
IST = timezone(timedelta(hours=5, minutes=30))
LABELS = {
    "en": ["Reported station", "Delay (min)", "Provider update", "Not reported", "Recent provider report", "Stale report", "Unverified/estimated report"],
    "ta": ["பதிவான நிலையம்", "தாமதம் (நிமிடம்)", "தகவல் புதுப்பிப்பு", "தகவல் இல்லை", "சமீபத்திய பதிவு", "பழைய பதிவு", "உறுதிப்படுத்தப்படாத/மதிப்பிடப்பட்ட பதிவு"],
    "ml": ["റിപ്പോർട്ട് ചെയ്ത സ്റ്റേഷൻ", "വൈകൽ (മിനിറ്റ്)", "വിവരം പുതുക്കിയത്", "വിവരം ലഭ്യമല്ല", "സമീപകാല റിപ്പോർട്ട്", "പഴയ റിപ്പോർട്ട്", "സ്ഥിരീകരിക്കാത്ത/കണക്കാക്കിയ റിപ്പോർട്ട്"],
    "kn": ["ವರದಿಯಾದ ನಿಲ್ದಾಣ", "ವಿಳಂಬ (ನಿಮಿಷ)", "ಮಾಹಿತಿ ನವೀಕರಣ", "ಮಾಹಿತಿ ಇಲ್ಲ", "ಇತ್ತೀಚಿನ ವರದಿ", "ಹಳೆಯ ವರದಿ", "ದೃಢೀಕರಿಸದ/ಅಂದಾಜು ವರದಿ"],
    "hi": ["रिपोर्ट किया गया स्टेशन", "देरी (मिनट)", "जानकारी अपडेट", "जानकारी नहीं मिली", "हाल की रिपोर्ट", "पुरानी रिपोर्ट", "अपुष्ट/अनुमानित रिपोर्ट"],
}
STATES = ["running", "not_started", "arrived", "completed", "cancelled", "rescheduled", "terminated", "unknown"]
STATE_TEXT = {
    "en": ["Running", "Not started", "Arrived", "Completed", "Cancelled", "Rescheduled", "Terminated", "Status unknown"],
    "ta": ["இயங்குகிறது", "புறப்படவில்லை", "வந்தடைந்தது", "பயணம் முடிந்தது", "ரத்து செய்யப்பட்டது", "நேரம் மாற்றப்பட்டது", "பயணம் நிறுத்தப்பட்டது", "நிலை தெரியவில்லை"],
    "ml": ["ഓടിക്കൊണ്ടിരിക്കുന്നു", "പുറപ്പെട്ടിട്ടില്ല", "എത്തിച്ചേർന്നു", "യാത്ര പൂർത്തിയായി", "റദ്ദാക്കി", "സമയം മാറ്റി", "യാത്ര അവസാനിപ്പിച്ചു", "സ്ഥിതി വ്യക്തമല്ല"],
    "kn": ["ಸಂಚರಿಸುತ್ತಿದೆ", "ಇನ್ನೂ ಹೊರಟಿಲ್ಲ", "ತಲುಪಿದೆ", "ಪ್ರಯಾಣ ಪೂರ್ಣಗೊಂಡಿದೆ", "ರದ್ದಾಗಿದೆ", "ಸಮಯ ಬದಲಾಗಿದೆ", "ಪ್ರಯಾಣ ನಿಲ್ಲಿಸಲಾಗಿದೆ", "ಸ್ಥಿತಿ ತಿಳಿದಿಲ್ಲ"],
    "hi": ["चल रही है", "अभी शुरू नहीं हुई", "पहुँच गई", "यात्रा पूरी हुई", "रद्द", "समय बदला", "यात्रा समाप्त", "स्थिति अज्ञात"],
}


def configuration():
    provider = os.environ.get("HOME_AGENT_TRAIN_PROVIDER", "fixture")
    return {"provider": provider, "configured": provider == "railradar" and bool(os.environ.get("RAILRADAR_API_KEY")),
            "mode": "provider" if provider == "railradar" else "fixture", "source": "RailRadar" if provider == "railradar" else "Local samples"}


class NoRedirect(HTTPRedirectHandler):
    def redirect_request(self, req, fp, code, msg, headers, newurl):
        raise AppError("Railway provider redirected. Request stopped.", 502, "TRAIN_PROVIDER_ERROR")


def fetch_report(number, journey_date, key):
    request = Request(f"https://api.railradar.in/v1/trains/{number}/live?date={journey_date}&haltsOnly=true",
                      headers={"Authorization": "Bearer " + key, "Accept": "application/json"})
    try:
        with build_opener(NoRedirect).open(request, timeout=18) as response:
            body = response.read(2_000_001)
        if len(body) > 2_000_000:
            raise ValueError()
        return json.loads(body)
    except HTTPError as error:
        failures = {
            401: (503, "TRAIN_AUTH_ERROR", "The railway API key was rejected. Check its activation and plan."),
            403: (503, "TRAIN_AUTH_ERROR", "The railway provider denied access for this key or plan."),
            404: (404, "TRAIN_NOT_FOUND", "No railway report was found for that train and journey start date. Check the date it departed its origin."),
            429: (429, "TRAIN_RATE_LIMITED", "The railway provider's request allowance is exhausted. Retry later."),
        }
        status, code, message = failures.get(error.code, (503, "TRAIN_PROVIDER_UNAVAILABLE", "The railway provider is temporarily unavailable. No live result was obtained."))
        raise AppError(message, status, code) from None
    except (URLError, OSError):
        raise AppError("The railway provider timed out or is unavailable. No live result was obtained.", 503, "TRAIN_PROVIDER_UNAVAILABLE") from None
    except (ValueError, UnicodeError):
        raise AppError("The railway provider returned invalid data.", 502, "TRAIN_INVALID_RESPONSE") from None


def bounded(value, maximum=160):
    if value is None:
        return None
    if not isinstance(value, str) or len(value) > maximum or any(ord(c) < 32 for c in value):
        raise AppError("The railway provider returned invalid text.", 502, "TRAIN_INVALID_RESPONSE")
    return value.strip() or None


def timestamp(value):
    if not isinstance(value, str):
        return None
    try:
        parsed = datetime.fromisoformat(value.replace("Z", "+00:00"))
        return parsed if parsed.tzinfo else None
    except ValueError:
        return None


def normalize(payload, number, journey_date, retrieved):
    if not isinstance(payload, dict) or payload.get("success") is not True or not isinstance(payload.get("data"), dict):
        raise AppError("No usable railway report was returned.", 502, "TRAIN_INVALID_RESPONSE")
    data = payload["data"]
    if data.get("trainNumber") != number or data.get("startDate") != journey_date:
        raise AppError("The railway report does not match the requested train and journey date.", 502, "TRAIN_RESPONSE_MISMATCH")
    location = data.get("currentLocation") or {}
    route, next_halt = data.get("route") or [], data.get("nextHalt") or {}
    if not isinstance(location, dict) or not isinstance(route, list) or not isinstance(next_halt, dict):
        raise AppError("The railway report has an invalid location.", 502, "TRAIN_INVALID_RESPONSE")
    code = bounded(location.get("stationCode"), 10)
    station = bounded(location.get("stationName"), 100)
    for stop in route:
        if isinstance(stop, dict) and code and stop.get("stationCode") == code:
            station = bounded(stop.get("stationName"), 100) or station
            break
    delay = data.get("delayMinutes")
    if delay is not None and (isinstance(delay, bool) or not isinstance(delay, (int, float)) or not -10080 <= delay <= 10080):
        raise AppError("The railway report has an invalid delay.", 502, "TRAIN_INVALID_RESPONSE")
    updated = timestamp(data.get("lastUpdatedAt"))
    status = bounded(data.get("status"), 40) or "unknown"
    if status not in {"running", "not_started", "arrived", "completed", "cancelled", "rescheduled", "terminated"}:
        status = "unknown"
    return {"train_number": number, "name": bounded(data.get("trainName")) or f"Train {number}",
            "requested_date": journey_date, "journey_start_date": journey_date,
            "source": "RailRadar — third-party running-status reports", "source_url": DOCS,
            "retrieved_at": retrieved.isoformat(), "provider_updated_at": updated.isoformat() if updated else None,
            "status": status, "reported_station": f"{station} ({code})" if station and code else station or code,
            "next_station": bounded(next_halt.get("stationName"), 100) or bounded(next_halt.get("stationCode"), 10),
            "delay_minutes": delay, "provider_claims_live": data.get("isLive") is True,
            "estimated": data.get("trackingMode") not in {None, "real-time"} or location.get("isActualPosition") is False,
            "position_notice": "Latest reported position; not guaranteed GPS location."}


class TrainFeed:
    def __init__(self, fetcher=fetch_report, clock=lambda: datetime.now(timezone.utc)):
        self.fetcher, self.clock = fetcher, clock
        self.lock, self.cache, self.requests = threading.Lock(), OrderedDict(), deque()

    def lookup(self, number, journey_date, language="en"):
        if not isinstance(number, str) or not re.fullmatch(r"\d{5}", number):
            raise AppError("Train number must have five digits.")
        try:
            parsed_date = date.fromisoformat(journey_date)
            if parsed_date.isoformat() != journey_date:
                raise ValueError()
        except (ValueError, TypeError):
            raise AppError("Use the journey start date in YYYY-MM-DD format.") from None
        now = self.clock()
        if parsed_date > now.astimezone(IST).date():
            raise AppError("Live status is unavailable for a future journey. Use the date the train departed its origin.")
        key = os.environ.get("RAILRADAR_API_KEY", "")
        if not key:
            raise AppError("Live train data is not connected yet. Configure the RailRadar API key on the server.", 503, "TRAIN_NOT_CONFIGURED")
        identifier = (hashlib.sha256(key.encode()).hexdigest(), number, journey_date)
        with self.lock:
            now = self.clock()
            cached = self.cache.get(identifier)
            cache_hit = cached is not None and (now-cached[0]).total_seconds() < 120
            if cache_hit:
                result = copy.deepcopy(cached[1])
                self.cache.move_to_end(identifier)
            else:
                while self.requests and (now-self.requests[0]).total_seconds() >= 60:
                    self.requests.popleft()
                if len(self.requests) >= 5:
                    raise AppError("The demo railway feed is busy. Retry in a minute.", 429, "TRAIN_RATE_LIMITED")
                self.requests.append(now)
                result = normalize(self.fetcher(number, journey_date, key), number, journey_date, self.clock())
                self.cache[identifier] = (self.clock(), copy.deepcopy(result))
                while len(self.cache) > 32:
                    self.cache.popitem(last=False)
        updated = timestamp(result["provider_updated_at"])
        age = (self.clock()-updated).total_seconds() if updated else None
        if age is not None and age > 900:
            mode = "stale"
        elif updated and -300 <= age <= 900 and result["provider_claims_live"] and not result["estimated"]:
            mode = "live"
        else:
            mode = "reported"
        labels = LABELS.get(language, LABELS["en"])
        result.update(mode=mode, cache_hit=cache_hit, update_age_seconds=round(age) if age is not None else None)
        quality = labels[4] if mode == "live" else labels[5] if mode == "stale" else labels[6]
        state = STATE_TEXT.get(language, STATE_TEXT["en"])[STATES.index(result["status"])]
        result["summary"] = (f"{result['name']} ({number}) · {state} · {quality}. {labels[0]}: {result['reported_station'] or labels[3]}. "
                             f"{labels[1]}: {result['delay_minutes'] if result['delay_minutes'] is not None else labels[3]}. "
                             f"{labels[2]}: {result['provider_updated_at'] or labels[3]}. RailRadar.")
        return result


DEFAULT_FEED = TrainFeed()
