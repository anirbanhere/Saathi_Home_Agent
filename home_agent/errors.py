"""Validation and public error semantics shared by HTTP and MCP."""
import math
from decimal import Decimal, InvalidOperation


class AppError(Exception):
    def __init__(self, message: str, status: int = 422, code: str = "VALIDATION_ERROR"):
        super().__init__(message)
        self.status = status
        self.code = code


def text(value, name: str, maximum: int = 200, allow_empty: bool = False) -> str:
    if not isinstance(value, str) or len(value) > maximum or (not value.strip() and not allow_empty):
        raise AppError(f"{name} must be text between 1 and {maximum} characters.")
    return value.strip()


def number(value, name: str, minimum: float = 0, maximum: float = 1_000_000) -> float:
    if isinstance(value, bool):
        raise AppError(f"{name} must be a number.")
    try:
        result = float(Decimal(str(value)))
    except (InvalidOperation, ValueError, TypeError, OverflowError):
        raise AppError(f"{name} must be a number.") from None
    if not math.isfinite(result) or not minimum <= result <= maximum:
        raise AppError(f"{name} must be between {minimum} and {maximum}.")
    return result
