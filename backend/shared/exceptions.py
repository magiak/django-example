class DomainError(Exception):
    """Base exception for domain-level errors."""

    def __init__(self, message: str, code: str = "domain_error") -> None:
        self.message = message
        self.code = code
        super().__init__(message)


class NotFoundError(DomainError):
    """Raised when a domain entity is not found."""

    def __init__(self, entity: str, identifier: str) -> None:
        super().__init__(
            message=f"{entity} with id '{identifier}' not found",
            code="not_found",
        )


class InvalidTransitionError(DomainError):
    """Raised when an invalid state transition is attempted."""

    def __init__(self, entity: str, current_state: str, target_state: str) -> None:
        super().__init__(
            message=f"Cannot transition {entity} from '{current_state}' to '{target_state}'",
            code="invalid_transition",
        )
