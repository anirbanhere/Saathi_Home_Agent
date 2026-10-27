import hashlib
from .contracts import InboundMessage, DeliveryReceipt


class LocalChannel:
    def __init__(self, name):
        if name not in {"web_chat", "test_cli"}:
            raise ValueError("Only local mock web/CLI channels are enabled.")
        self.name = name

    async def normalize_inbound(self, payload):
        return InboundMessage.model_validate({**payload, "channel": self.name})

    async def send_message(self, message):
        # Deterministic receipt for local display, never a third-party delivery claim.
        digest = hashlib.sha256(message.model_dump_json().encode()).hexdigest()[:20]
        return DeliveryReceipt(
            reference="MOCK-DELIVERY-" + digest, status="mock_delivered"
        )

    async def send_approval(self, message):
        return await self.send_message(message)
