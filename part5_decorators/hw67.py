from datetime import datetime, timezone
import functools
import json
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
    def __init__(self, message: object) -> None:
        super().__init__(message)
        self.func_name: str | None = None
        self.block_time: datetime | None = None


class CircuitBreaker:
    def __init__(
        self,
        critical_count: int = 5,
        time_to_recover: int = 30,
        triggers_on: type[Exception] = Exception,
    ):
        errors: list[Exception] = []

        if not isinstance(critical_count, int) or critical_count <= 0:
            errors.append(ValueError(INVALID_CRITICAL_COUNT))
        if not isinstance(time_to_recover, int) or time_to_recover <= 0:
            errors.append(ValueError(INVALID_RECOVERY_TIME))

        if errors:
            raise ExceptionGroup(VALIDATIONS_FAILED, errors)

        self.critical_count = critical_count
        self.time_to_recover = time_to_recover
        self.triggers_on = triggers_on

        self._fail_count: int = 0
        self._blocked_until: float | None = None

    def __call__(self, func: CallableWithMeta[P, R_co]) -> CallableWithMeta[P, R_co]:
        @functools.wraps(func)
        def wrapper(*args: P.args, **kwargs: P.kwargs) -> R_co:
            now_dt = datetime.now(timezone.utc)
            now = now_dt.timestamp()

            if self._blocked_until is not None:
                if now < self._blocked_until:
                    err = BreakerError(TOO_MUCH)
                    err.func_name = f"{func.__module__}.{func.__name__}"
                    err.block_time = datetime.fromtimestamp(
                        self._blocked_until, tz=timezone.utc
                    )
                    raise err
                else:
                    self._blocked_until = None
                    self._fail_count = 0

            try:
                result = func(*args, **kwargs)
                self._fail_count = 0
                return result

            except Exception as e:
                if not isinstance(e, self.triggers_on):
                    raise

                self._fail_count += 1

                if self._fail_count >= self.critical_count:
                    self._blocked_until = now + self.time_to_recover

                    err = BreakerError(TOO_MUCH)
                    err.func_name = f"{func.__module__}.{func.__name__}"
                    err.block_time = now_dt

                    raise err from e
                raise
        return wrapper


circuit_breaker = CircuitBreaker(5, 30, Exception)


@circuit_breaker
def get_comments(post_id: int) -> Any:
    """
    Получает комментарии к посту

    Args:
        post_id (int): Идентификатор поста

    Returns:
        list[dict[int | str]]: Список комментариев
    """
    response = urlopen(
        f"https://jsonplaceholder.typicode.com/comments?postId={post_id}"
    )
    return json.loads(response.read())


if __name__ == "__main__":
    comments = get_comments(1)