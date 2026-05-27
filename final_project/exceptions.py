class ProjectError(Exception):
    def __init__(self, message: str, context: dict[str, str] | None = None) -> None:
        super().__init__(message)
        self.context = context


class ExternalServiceError(ProjectError):
    pass


class TokenError(ExternalServiceError):
    pass


class LLMServiceError(ExternalServiceError):
    pass


class ModelError(ExternalServiceError):
    pass
