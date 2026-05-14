import json
from datetime import UTC, datetime, timedelta
from functools import wraps
from typing import Any, ParamSpec, Protocol, TypeVar
from urllib.request import urlopen

INVALID_CRITICAL_COUNT = "Breaker count must be positive integer!"
INVALID_RECOVERY_TIME = "Breaker recovery time must be positive integer!"
VALIDATIONS_FAILED = "Invalid decorator args."
TOO_MUCH = "Too much requests, just wait."


P = ParamSpec("P")
R_co = TypeVar("R_co", covariant=True)


class CallableWithMeta(Protocol[P, R_co]):
    __name__: str
    __module__: str

    def __call__(self, *args: P.args, **kwargs: P.kwargs) -> R_co: ...


class BreakerError(Exception):
    def __init__(self, func_name: str, block_time: datetime | None) -> None:
        super().__init__(TOO_MUCH)
        self.func_name = func_name
        self.block_time = block_time


class CircuitBreaker:
    def __init__(
        self,
        critical_count: int = 5,
        time_to_recover: int = 30,
        triggers_on: type[Exception] = Exception,
    ) -> None:
        self._validate_args(critical_count, time_to_recover)

        self.critical_count = critical_count
        self.time_to_recover = time_to_recover
        self.triggers_on = triggers_on

        self._fails = 0
        self._blocked_until: datetime | None = None

    @staticmethod
    def _validate_positive_int(value: int, message: str) -> ValueError | None:
        if isinstance(value, bool) or value <= 0:
            return ValueError(message)
        return None

    def _validate_args(self, critical_count: int, time_to_recover: int) -> None:
        errors = [
            error
            for error in (
                self._validate_positive_int(
                    critical_count,
                    INVALID_CRITICAL_COUNT,
                ),
                self._validate_positive_int(
                    time_to_recover,
                    INVALID_RECOVERY_TIME,
                ),
            )
            if error is not None
        ]
        if errors:
            raise ExceptionGroup(VALIDATIONS_FAILED, errors)

    def _func_name(self, func: CallableWithMeta[P, R_co]) -> str:
        return f"{func.__module__}.{func.__name__}"

    def _is_blocked(self) -> bool:
        blocked_until = self._blocked_until

        if blocked_until is None:
            return False

        return datetime.now(UTC) < blocked_until

    def _raise_blocked(self, func: CallableWithMeta[P, R_co]) -> None:
        raise BreakerError(func_name=self._func_name(func), block_time=self._blocked_until)

    def _activate_breaker(self, func: CallableWithMeta[P, R_co], source_error: Exception) -> None:
        block_time = datetime.now(UTC) + timedelta(seconds=self.time_to_recover)
        self._blocked_until = block_time

        error = BreakerError(func_name=self._func_name(func), block_time=block_time)
        raise error from source_error

    def _handle_exception(self, func: CallableWithMeta[P, R_co], error: Exception) -> None:
        if not isinstance(error, self.triggers_on):
            raise error

        self._fails += 1

        if self._fails >= self.critical_count:
            self._activate_breaker(func, error)

        raise error

    def __call__(self, func: CallableWithMeta[P, R_co]) -> CallableWithMeta[P, R_co]:
        @wraps(func)
        def wrapper(*args: P.args, **kwargs: P.kwargs) -> R_co:
            if self._is_blocked():
                self._raise_blocked(func)

            try:
                result = func(*args, **kwargs)
            except Exception as error:
                self._handle_exception(func, error)
                raise

            self._fails = 0
            return result

        return wrapper


circuit_breaker = CircuitBreaker(5, 30, Exception)


def get_comments(post_id: int) -> Any:
    response = urlopen(f"https://jsonplaceholder.typicode.com/comments?postId={post_id}")
    return json.loads(response.read())


if __name__ == "__main__":
    comments = get_comments(1)
