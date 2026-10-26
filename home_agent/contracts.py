"""The same JSON-schema tool contracts are used by Muse and Hermes MCP."""
from .service import HOUSEHOLD_TOOLS

LANGUAGE = {"type": "string", "enum": ["en", "ta", "ml", "kn", "hi"]}
SCHEMAS = {
    "train_status": ("Look up a LOCAL FIXTURE, never live train status. Supported samples: 12627, 12623, 12658. Ask for train number and explicit YYYY-MM-DD date first.",
                     {"train_number": {"type": "string", "pattern": "^[0-9]{5}$"}, "date": {"type": "string", "format": "date"}}, ["train_number", "date"]),
    "bill_preview": ("Prepare a SANDBOX electricity bill for a DEMO- account. Does not pay. Human approval in the local console is required to execute.",
                     {"account": {"type": "string", "pattern": "^DEMO-[A-Z0-9-]+$"}}, ["account"]),
    "booking_preview": ("Prepare a SANDBOX journey quote. No actual availability is checked. Human approval in the local console is required; no real tickets are issued.",
                        {"origin": {"type": "string", "maxLength": 80}, "destination": {"type": "string", "maxLength": 80},
                         "date": {"type": "string", "format": "date"}}, ["origin", "destination", "date"]),
    "recipe_plan": ("Plan a curated demo recipe against actual local inventory. Quantities are estimates. Does not consume stock; no video has been processed.",
                    {"recipe": {"type": "string", "enum": ["tomato-rice", "dal", "upma"]},
                     "servings": {"type": "integer", "minimum": 1, "maximum": 12}, "less_spicy": {"type": "boolean"}}, ["recipe"]),
    "dish_suggestions": ("Suggest curated dishes based on local inventory and recent meal history. Does not change stock.", {}, []),
    "inventory_list": ("Read the shared kitchen inventory. Opening quantities and meal consumption are estimates.", {}, []),
}


def tool_schemas(actor="owner"):
    result = []
    for name, (description, properties, required) in SCHEMAS.items():
        if actor == "cook" and name not in HOUSEHOLD_TOOLS:
            continue
        result.append({"name": name, "description": description,
                       "inputSchema": {"type": "object", "properties": {**properties, "language": LANGUAGE},
                                       "required": required, "additionalProperties": False}})
    return result
