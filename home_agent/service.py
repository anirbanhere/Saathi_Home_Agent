"""Deterministic domain tools. Transactions and approvals are independent of the model."""
import csv
import hashlib
import io
import json
import re
from datetime import date, datetime, timedelta, timezone
from pathlib import Path
from uuid import uuid4

from .catalog import ALIASES, RECIPES, TRAINS
from .errors import AppError, number, text
from .languages import LANGUAGES, detect_language, say
from .store import Store, now

DEFAULT_DB = Path(__file__).resolve().parent.parent / "data" / "home-agent.sqlite3"
HOUSEHOLD_TOOLS = {"inventory_list", "recipe_plan", "dish_suggestions"}
TOOL_ARGS = {
    "train_status": {"train_number", "date", "language"},
    "bill_preview": {"account", "language"},
    "booking_preview": {"origin", "destination", "date", "language"},
    "recipe_plan": {"recipe", "servings", "less_spicy", "language"},
    "dish_suggestions": {"language"}, "inventory_list": {"language"},
}


def valid_date(value) -> str:
    value = text(value, "date", 10)
    if not re.fullmatch(r"\d{4}-\d{2}-\d{2}", value):
        raise AppError("Use a valid date in YYYY-MM-DD format.")
    try:
        return date.fromisoformat(value).isoformat()
    except ValueError:
        raise AppError("Use a valid date in YYYY-MM-DD format.") from None


def normalize_item(name, quantity, unit):
    name = text(name, "item name", 60).lower()
    if not re.fullmatch(r"[\w -]+", name):
        raise AppError("Item names may contain letters, numbers, spaces and hyphens.")
    name = ALIASES.get(name, name)
    unit = text(unit, "unit", 10).lower()
    quantity = number(quantity, "quantity")
    if unit in {"kg", "l"}:
        quantity *= 1000
        unit = {"kg": "g", "l": "ml"}[unit]
    if unit not in {"g", "ml", "pcs"}:
        raise AppError("Supported units are g, kg, ml, l and pcs.")
    if quantity > 1_000_000:
        raise AppError("Quantity exceeds the demo limit.")
    return name, round(quantity, 4), unit


class HomeAgent:
    def __init__(self, path=DEFAULT_DB):
        self.store = Store(Path(path))

    @staticmethod
    def _actor(actor):
        if not isinstance(actor, str) or actor not in {"owner", "cook"}:
            raise AppError("Unknown household role.", 403, "FORBIDDEN")

    @staticmethod
    def _task_access(task, actor):
        HomeAgent._actor(actor)
        if actor != "owner" and task["kind"] not in HOUSEHOLD_TOOLS:
            raise AppError("This task is only available to the household owner.", 403, "FORBIDDEN")

    def task(self, task_id, actor="owner"):
        with self.store.transaction() as db:
            task = self.store.decode(db.execute("SELECT * FROM tasks WHERE id=?", (task_id,)).fetchone())
            self._task_access(task, actor)
            return task

    def snapshot(self, actor="owner", session="demo", limit=50):
        self._actor(actor)
        with self.store.transaction() as db:
            inventory = [dict(r) for r in db.execute("SELECT * FROM inventory ORDER BY name")]
            rows = db.execute("SELECT * FROM tasks ORDER BY rowid DESC LIMIT 200").fetchall()
            tasks = [self.store.decode(r) for r in rows if actor == "owner" or r["kind"] in HOUSEHOLD_TOOLS][:limit]
            events = [dict(r) for r in db.execute("SELECT * FROM inventory_events ORDER BY rowid DESC LIMIT 30")]
            messages = [dict(r) for r in db.execute(
                "SELECT language,user_text,response,created_at FROM messages WHERE session=? ORDER BY id DESC LIMIT 40", (session,))]
            for message in messages:
                message["response"] = json.loads(message["response"])
            payments = db.execute("SELECT COUNT(*) FROM tasks WHERE kind='bill_preview' AND status='succeeded'").fetchone()[0]
            return {"inventory": inventory, "tasks": tasks, "events": events, "messages": list(reversed(messages)),
                    "recipes": [{"id": key, "name": recipe["name"], "time_minutes": recipe["time_minutes"]}
                                for key, recipe in RECIPES.items()],
                    "metrics": {"sandbox_payments": payments if actor == "owner" else 0,
                                "inventory_items": len(inventory), "tasks": len(tasks)},
                    "mode": "offline", "languages": LANGUAGES}

    def tool(self, name, args, actor="owner"):
        self._actor(actor)
        if not isinstance(name, str) or name not in TOOL_ARGS:
            raise AppError("Unknown or prohibited tool.", 403, "TOOL_NOT_ALLOWED")
        if not isinstance(args, dict) or set(args) - TOOL_ARGS[name]:
            raise AppError("Unexpected tool arguments.")
        if actor == "cook" and name not in HOUSEHOLD_TOOLS:
            raise AppError("The cook may only access recipes and inventory.", 403, "FORBIDDEN")
        language = args.get("language", "en")
        if not isinstance(language, str) or language not in LANGUAGES:
            raise AppError("Unsupported language.")
        with self.store.transaction() as db:
            return self._tool(db, name, args, actor, language)

    def _tool(self, db, name, args, actor, language, session="", task_id=None):
        status = "succeeded"
        if name == "train_status":
            train_number = text(args.get("train_number"), "train number", 5)
            if not re.fullmatch(r"\d{5}", train_number):
                raise AppError("Train number must have exactly five digits.")
            travel_date = valid_date(args.get("date"))
            train = TRAINS.get(train_number)
            result = {"mode": "fixture", "source": "Local demonstration fixture; never a live train feed",
                      "requested_date": travel_date, "retrieved_at": now(), "train_number": train_number}
            if train:
                result.update(train)
                result["summary"] = say(language, "train_result", name=train["name"], delay=train["sample_delay_minutes"],
                                        station=train["sample_station"], date=travel_date)
            else:
                status = "failed"
                result["summary"] = say(language, "train_missing")
        elif name == "bill_preview":
            account = text(args.get("account"), "demo account", 40).upper()
            if not re.fullmatch(r"DEMO-[A-Z0-9-]{1,30}", account):
                raise AppError("Only DEMO- accounts are accepted. Example: DEMO-1042.")
            result = {"mode": "sandbox", "biller": "Demo Electricity", "account": account,
                      "amount_paise": 84500, "currency": "INR", "source": "Local bill simulator",
                      "summary": say(language, "bill_ready", account=account, amount="845.00")}
            status = "awaiting_approval"
        elif name == "booking_preview":
            origin = text(args.get("origin"), "origin", 80)
            destination = text(args.get("destination"), "destination", 80)
            if origin.casefold() == destination.casefold():
                raise AppError("Origin and destination must differ.")
            travel_date = valid_date(args.get("date"))
            result = {"mode": "sandbox", "origin": origin, "destination": destination, "date": travel_date,
                      "amount_paise": 65000, "currency": "INR", "source": "Local booking simulator; no actual availability checked",
                      "summary": say(language, "booking_ready", origin=origin, destination=destination,
                                     date=travel_date, amount="650.00")}
            status = "awaiting_approval"
        elif name == "recipe_plan":
            key = text(args.get("recipe"), "recipe", 60)
            if key not in RECIPES:
                raise AppError("Choose tomato-rice, dal or upma.")
            servings = number(args.get("servings", 2), "servings", 1, 12)
            if servings != int(servings):
                raise AppError("Servings must be a whole number.")
            less_spicy = args.get("less_spicy", False)
            if not isinstance(less_spicy, bool):
                raise AppError("less_spicy must be true or false.")
            recipe = RECIPES[key]
            inventory = {r["name"]: dict(r) for r in db.execute("SELECT * FROM inventory")}
            ingredients = []
            for item, quantity, unit in recipe["ingredients"]:
                needed = quantity * servings / recipe["servings"]
                if item == "chilli" and less_spicy:
                    needed /= 2
                needed = round(needed, 2)
                available = inventory.get(item, {}).get("quantity", 0)
                ingredients.append({"name": item, "quantity": needed, "unit": unit,
                                    "available": available, "missing": max(0, needed - available)})
            steps = list(recipe["steps"])
            if less_spicy:
                steps.insert(0, "Use less chilli: the ingredient list already has half the usual chilli. Taste before adding more.")
            if key == "upma":
                steps[3 + int(less_spicy)] = f"Add about {round(400 * servings / 2)} ml water and salt. Bring to a boil."
            result = {"mode": "curated", "source": "Curated demo recipe, not extracted from a video",
                      "recipe": key, "name": recipe["name"], "servings": int(servings), "estimated": True,
                      "time_minutes": recipe["time_minutes"], "ingredients": ingredients, "steps": steps,
                      "steps_language": "en", "less_spicy": less_spicy,
                      "summary": say(language, "recipe_ready", name=recipe["name"], servings=int(servings))}
            status = "planned"
        elif name == "dish_suggestions":
            inventory = {r["name"]: r["quantity"] for r in db.execute("SELECT * FROM inventory")}
            recent = {json.loads(r[0]).get("recipe") for r in db.execute(
                "SELECT result FROM tasks WHERE kind='recipe_plan' AND status='succeeded' ORDER BY rowid DESC LIMIT 3")}
            options = []
            for key, recipe in RECIPES.items():
                missing = [{"name": item, "quantity": round(qty - inventory.get(item, 0), 2), "unit": unit}
                           for item, qty, unit in recipe["ingredients"] if inventory.get(item, 0) < qty]
                options.append({"id": key, "name": recipe["name"], "missing": missing,
                                "recently_cooked": key in recent, "time_minutes": recipe["time_minutes"]})
            options.sort(key=lambda option: (len(option["missing"]), option["recently_cooked"], option["time_minutes"]))
            result = {"mode": "inventory", "options": options, "summary": say(language, "suggestions")}
        else:
            result = {"mode": "inventory", "items": [dict(r) for r in db.execute("SELECT * FROM inventory ORDER BY name")],
                      "summary": say(language, "inventory")}
        return self.store.save_task(db, name, actor, {**args, "language": language}, result, status, session, task_id)

    def approve(self, task_id, actor="owner"):
        self._actor(actor)
        if actor != "owner":
            raise AppError("Only the owner can approve transactions.", 403, "FORBIDDEN")
        with self.store.transaction() as db:
            task = self.store.decode(db.execute("SELECT * FROM tasks WHERE id=?", (task_id,)).fetchone())
            if task["kind"] not in {"bill_preview", "booking_preview"}:
                raise AppError("This task cannot be approved.", 409, "INVALID_STATE")
            if task["status"] == "succeeded":
                return task
            if task["status"] != "awaiting_approval":
                raise AppError("Task is no longer awaiting approval.", 409, "INVALID_STATE")
            result = {**task["result"], "receipt": "SANDBOX-" + task["id"][:12].upper(),
                      "approved_at": now(), "approved_by": actor, "executed_at": now()}
            result["summary"] = say(task["args"].get("language", "en"), "completed", receipt=result["receipt"])
            return self.store.save_task(db, task["kind"], task["actor"], task["args"], result,
                                        "succeeded", task["session"], task["id"])

    def cancel(self, task_id, actor="owner"):
        with self.store.transaction() as db:
            task = self.store.decode(db.execute("SELECT * FROM tasks WHERE id=?", (task_id,)).fetchone())
            self._task_access(task, actor)
            if task["status"] not in {"needs_input", "awaiting_approval", "planned", "cancelled"}:
                raise AppError("Completed tasks cannot be cancelled.", 409, "INVALID_STATE")
            result = {**task["result"], "summary": say(task["args"].get("language", "en"), "cancelled")}
            return self.store.save_task(db, task["kind"], task["actor"], task["args"], result, "cancelled", task["session"], task_id)

    def import_receipt(self, content, receipt_id, actor="owner"):
        self._actor(actor)
        content = text(content, "receipt text", 10000)
        receipt_id = text(receipt_id, "receipt reference", 100)
        fingerprint = hashlib.sha256(content.encode()).hexdigest()
        rows = list(csv.reader(io.StringIO(content)))
        if not rows or len(rows) > 100:
            raise AppError("Provide between 1 and 100 CSV lines: item, quantity, unit.")
        items = []
        for row in rows:
            if len(row) != 3:
                raise AppError("Each receipt line must be item, quantity, unit. Example: Rice,1,kg")
            item = normalize_item(*row)
            if item[1] <= 0:
                raise AppError("Purchase quantities must be positive.")
            items.append(item)
        with self.store.transaction() as db:
            previous = db.execute("SELECT * FROM receipts WHERE id=?", (receipt_id,)).fetchone()
            if previous:
                if previous["fingerprint"] != fingerprint:
                    raise AppError("That receipt reference already has different contents.", 409, "CONFLICT")
                return json.loads(previous["result"])
            result = {"receipt_id": receipt_id, "items": [], "source": "User-reviewed grocery text; no OCR performed"}
            for index, (name, quantity, unit) in enumerate(items):
                self.store.stock_event(db, f"receipt:{receipt_id}:{index}", name, quantity, unit, "Purchase " + receipt_id)
                result["items"].append({"name": name, "quantity": quantity, "unit": unit})
            db.execute("INSERT INTO receipts VALUES (?, ?, ?)", (receipt_id, fingerprint, json.dumps(result)))
            return result

    def correct_stock(self, name, quantity, unit, reference, actor="owner"):
        self._actor(actor)
        name, quantity, unit = normalize_item(name, quantity, unit)
        reference = text(reference, "correction reference", 100)
        with self.store.transaction() as db:
            previous = db.execute("SELECT * FROM stock_corrections WHERE id=?", (reference,)).fetchone()
            if previous:
                if (previous["name"], previous["quantity"], previous["unit"]) != (name, quantity, unit):
                    raise AppError("Correction reference already used with different contents.", 409, "CONFLICT")
                return json.loads(previous["result"])
            current = db.execute("SELECT * FROM inventory WHERE name=?", (name,)).fetchone()
            if current and current["unit"] != unit:
                raise AppError("Correction must use the item's existing unit.")
            self.store.stock_event(db, "correction:" + reference, name, quantity - (current["quantity"] if current else 0),
                                   unit, "Manual stock correction")
            result = dict(db.execute("SELECT * FROM inventory WHERE name=?", (name,)).fetchone())
            db.execute("INSERT INTO stock_corrections VALUES (?, ?, ?, ?, ?)",
                       (reference, name, quantity, unit, json.dumps(result)))
            return result

    def complete_meal(self, task_id, actor="owner"):
        self._actor(actor)
        with self.store.transaction() as db:
            task = self.store.decode(db.execute("SELECT * FROM tasks WHERE id=?", (task_id,)).fetchone())
            if task["kind"] != "recipe_plan":
                raise AppError("Only a recipe plan can be marked cooked.")
            if task["status"] == "succeeded":
                return task
            if task["status"] != "planned":
                raise AppError("Recipe is no longer planned.", 409, "INVALID_STATE")
            for item in task["result"]["ingredients"]:
                self.store.stock_event(db, f"meal:{task_id}:{item['name']}", item["name"], -item["quantity"], item["unit"],
                                       "Estimated usage: " + task["result"]["name"], estimated=True)
            result = {**task["result"], "meal_id": task_id, "completed_at": now(),
                      "summary": say(task["args"].get("language", "en"), "meal_done")}
            return self.store.save_task(db, task["kind"], task["actor"], task["args"], result, "succeeded", task["session"], task_id)

    def message(self, content, language="en", session="demo", request_id=None):
        content = text(content, "message", 4000)
        session = text(session, "session", 100)
        request_id = text(request_id or uuid4().hex, "request id", 100)
        if not isinstance(language, str) or language not in LANGUAGES:
            raise AppError("Unsupported language.")
        if language == "en":
            language = detect_language(content, language)
        fingerprint = hashlib.sha256((content + "\0" + language).encode()).hexdigest()
        with self.store.transaction() as db:
            previous = db.execute("SELECT * FROM messages WHERE session=? AND request_id=?", (session, request_id)).fetchone()
            if previous:
                if previous["fingerprint"] != fingerprint:
                    raise AppError("Message reference already used with different contents.", 409, "CONFLICT")
                return json.loads(previous["response"])
            lower = content.casefold()
            task = None
            train_number = re.search(r"(?<!\d)\d{5}(?!\d)", content)
            date_match = re.search(r"\d{4}-\d{2}-\d{2}", content)
            travel_date = date_match.group() if date_match else None
            today = datetime.now(timezone(timedelta(hours=5, minutes=30))).date()
            if any(word in lower for word in ["tomorrow", "naalai", "naale", "நாளை", "നാളെ", "ನಾಳೆ"]):
                travel_date = (today + timedelta(days=1)).isoformat()
            elif any(word in lower for word in ["today", "இன்று", "ഇന്ന്", "ಇಂದು", "आज"]):
                travel_date = today.isoformat()
            # Hindi 'kal' can mean yesterday or tomorrow: deliberately ask for an explicit date.
            pending_row = db.execute("SELECT * FROM tasks WHERE session=? AND status='needs_input' ORDER BY rowid DESC LIMIT 1", (session,)).fetchone()
            intent = None
            if any(word in lower for word in ["bill", "electric", "கட்டணம்", "ബിൽ", "ಬಿಲ್", "बिल"]):
                intent = "bill_preview"
            elif any(word in lower for word in ["book", "ticket", "முன்பதிவு", "ടിക്കറ്റ്", "ಟಿಕೆಟ್", "टिकट"]):
                reply = say(language, "booking_prompt")
                intent = "booking_help"
            elif train_number or any(word in lower for word in ["train", "rail", "ரயில்", "ട്രെയിൻ", "ರೈಲು", "ट्रेन"]):
                intent = "train_status"
            elif any(word in lower for word in ["suggest", "சமைக்கலாம்", "നിർദേശ", "ಸಲಹೆ", "सुझाव"]):
                intent = "dish_suggestions"
            elif any(word in lower for word in ["inventory", "stock", "இருப்பு", "സ്റ്റോക്ക്", "ದಾಸ್ತಾನು", "स्टॉक"]):
                intent = "inventory_list"
            elif any(word in lower for word in ["cook", "rice", "dal", "upma", "சமை", "சாதம்", "പാചകം", "ಅಡುಗೆ", "बना", "खाना"]):
                intent = "recipe_plan"
            elif pending_row:
                intent = pending_row["kind"]
            pending = self.store.decode(pending_row) if pending_row and pending_row["kind"] == intent else None
            args = dict(pending["args"]) if pending else {}
            args["language"] = language
            if intent == "train_status":
                if train_number:
                    args["train_number"] = train_number.group()
                if travel_date:
                    args["date"] = valid_date(travel_date)
                if not args.get("train_number") or not args.get("date"):
                    reply = say(language, "train_prompt")
                    task = self.store.save_task(db, intent, "owner", args, {"summary": reply, "mode": "fixture"},
                                                "needs_input", session, pending["id"] if pending else None)
                else:
                    task = self._tool(db, intent, args, "owner", language, session, pending["id"] if pending else None)
            elif intent == "bill_preview":
                account = re.search(r"DEMO-[A-Z0-9-]{1,30}", content.upper())
                if not account:
                    reply = say(language, "bill_prompt")
                    task = self.store.save_task(db, intent, "owner", args, {"summary": reply, "mode": "sandbox"},
                                                "needs_input", session, pending["id"] if pending else None)
                else:
                    args["account"] = account.group()
                    task = self._tool(db, intent, args, "owner", language, session, pending["id"] if pending else None)
            elif intent == "recipe_plan":
                key = None
                for recipe_key, words in [
                    ("upma", ["upma", "உப்புமா", "ഉപ്പുമാവ്", "ಉಪ್ಪಿಟ್ಟು", "उपमा"]),
                    ("dal", ["dal", "பருப்பு", "പരിപ്പ്", "ಬೇಳೆ", "दाल"]),
                    ("tomato-rice", ["tomato", "தக்காளி", "തക്കാളി", "ಟೊಮೆಟೊ", "टमाटर"]),
                ]:
                    if any(word in lower for word in words):
                        key = recipe_key
                        break
                servings = re.search(r"(?:for|பேர்|പേർ|ಜನ|लोग)\s*(\d{1,2})", lower)
                args.update(servings=int(servings.group(1)) if servings else args.get("servings", 2),
                            less_spicy=args.get("less_spicy", False) or any(word in lower for word in ["less", "mild", "காரம் குறை", "എരിവ് കുറ", "ಖಾರ ಕಡಿಮೆ", "कम तीखा"]))
                if key:
                    args["recipe"] = key
                    task = self._tool(db, intent, args, "owner", language, session, pending["id"] if pending else None)
                else:
                    reply = say(language, "recipe_prompt")
                    task = self.store.save_task(db, intent, "owner", args, {"summary": reply, "mode": "curated"},
                                                "needs_input", session, pending["id"] if pending else None)
            elif intent in {"dish_suggestions", "inventory_list"}:
                task = self._tool(db, intent, args, "owner", language, session)
            elif intent != "booking_help":
                reply = say(language, "help")
            if task:
                reply = task["result"]["summary"]
            response = {"reply": reply, "language": language, "task": task, "mode": "offline",
                        "notice": "Limited phrase matching and templates; no live LLM or service call."}
            db.execute("INSERT INTO messages(session,request_id,fingerprint,language,user_text,response,created_at) VALUES (?,?,?,?,?,?,?)",
                       (session, request_id, fingerprint, language, content, json.dumps(response), now()))
            return response
