"""
MediStock Backend — Common Exceptions

Application-level exception classes for consistent error handling.
"""


class MediStockError(Exception):
    """Base exception for all MediStock application errors."""

    def __init__(self, message: str, code: str = "INTERNAL_ERROR"):
        self.message = message
        self.code = code
        super().__init__(self.message)


class NotFoundError(MediStockError):
    """Raised when a requested resource is not found."""

    def __init__(self, entity: str, identifier: str | int):
        super().__init__(
            message=f"{entity} with identifier '{identifier}' not found",
            code="NOT_FOUND",
        )


class DuplicateError(MediStockError):
    """Raised when a duplicate resource is detected."""

    def __init__(self, entity: str, field: str, value: str):
        super().__init__(
            message=f"{entity} with {field} '{value}' already exists",
            code="DUPLICATE",
        )


class InsufficientStockError(MediStockError):
    """Raised when stock is insufficient for an operation."""

    def __init__(self, batch_number: str, available: int, requested: int):
        super().__init__(
            message=(
                f"Batch {batch_number} has only {available} units available, "
                f"but {requested} were requested"
            ),
            code="INSUFFICIENT_STOCK",
        )


class ExpiredBatchError(MediStockError):
    """Raised when attempting to sell from an expired batch."""

    def __init__(self, batch_number: str, expiry_date: str):
        super().__init__(
            message=f"Batch {batch_number} expired on {expiry_date} and cannot be sold",
            code="EXPIRED_BATCH",
        )


class AuthenticationError(MediStockError):
    """Raised when authentication fails."""

    def __init__(self, message: str = "Invalid credentials"):
        super().__init__(message=message, code="AUTHENTICATION_FAILED")


class AuthorizationError(MediStockError):
    """Raised when a user lacks required permissions."""

    def __init__(self, message: str = "Insufficient permissions"):
        super().__init__(message=message, code="FORBIDDEN")


class BusinessRuleError(MediStockError):
    """Raised when a business rule is violated."""

    def __init__(self, message: str):
        super().__init__(message=message, code="BUSINESS_RULE_VIOLATION")
