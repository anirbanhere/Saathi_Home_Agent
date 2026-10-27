import json
import logging


class EventFormatter(logging.Formatter):
    def format(self, record):
        return json.dumps(
            {
                "event": "transaction_transition_proposed",
                "state": getattr(record, "event_code", "unknown"),
                "task_id": getattr(record, "task_id", ""),
                "mock": True,
            }
        )


def configure_logging():
    logger = logging.getLogger("saathi.events")
    if not logger.handlers:
        handler = logging.StreamHandler()
        handler.setFormatter(EventFormatter())
        logger.addHandler(handler)
    logger.setLevel(logging.INFO)
    logger.propagate = False
