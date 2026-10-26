"""The same JSON-schema tool contracts are used by Muse and Hermes MCP."""
from .service import HOUSEHOLD_TOOLS

LANGUAGE = {"type": "string", "enum": ["en", "ta", "ml", "kn", "hi"]}
SCHEMAS = {
    "checkout_handoff": ("Save an UNVERIFIED bill-payment or food-order draft for manual handoff to a public merchant website. No login, payment or order is executed. Use only the user's stated details; ask for the merchant URL or missing critical fields. Never invent totals, addresses, account numbers or receipts. This task cannot be approved to execute in this demo.",
                         {"kind": {"type": "string", "enum": ["bill", "food"]}, "merchant_url": {"type": "string", "maxLength": 2000}, "details": {"type": "string", "maxLength": 1000}}, ["kind", "merchant_url", "details"]),
    "train_status": ("Get a train's running-status report from the server-configured railway provider, or explicitly labeled fixtures in offline development. Ask for a five-digit train number and its journey start date (departure from origin), YYYY-MM-DD. Inspect mode, provider_updated_at and source: only mode=live is a recent provider report; stale/reported data must not be called live. A provider failure is never a successful status.",
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
