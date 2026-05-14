import functools
import json
from datetime import UTC, datetime, timedelta
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
    def __init__(
        self,
        func_name: str,
        block_time: datetime | None,
        source_exception: Exception | None = None,
    ) -> None:
        super().__init__(TOO_MUCH)
        self.func_name = func_name
        self.block_time = block_time
        if source_exception is not None:
            self.__cause__ = source_exception


class CircuitBreaker:
    def __init__(
        self,
        critical_count: int = 5,
        time_to_recover: int = 30,
        triggers_on: type[Exception] = Exception,
    ) -> None:
        errors: list[ValueError] = []

        if critical_count <= 0:
            errors.append(ValueError(INVALID_CRITICAL_COUNT))

        if time_to_recover <= 0:
            errors.append(ValueError(INVALID_RECOVERY_TIME))

        if errors:
            raise ExceptionGroup(VALIDATIONS_FAILED, errors)

        self._critical_count = critical_count
        self._time_to_recover = time_to_recover
        self._triggers_on = triggers_on

        self._failure_count = 0
        self._block_time: datetime | None = None

    def __call__(self, func: CallableWithMeta[P, R_co]) -> CallableWithMeta[P, R_co]:
        @functools.wraps(func)
        def wrapper(*args: P.args, **kwargs: P.kwargs) -> R_co:
            self._check_blocked(func)
            return self._execute_func(func, *args, **kwargs)

        return wrapper

    def _check_blocked(self, func: CallableWithMeta[P, R_co]) -> None:
        if self._is_blocked():
            raise BreakerError(
                func_name=f"{func.__module__}.{func.__name__}",
                block_time=self._block_time,
                source_exception=None,
            )

    def _is_blocked(self) -> bool:
        if self._block_time is None:
            return False

        if datetime.now(UTC) > self._block_time + timedelta(seconds=self._time_to_recover):
            self._block_time = None
            self._failure_count = 0
            return False

        return True

    def _handle_error(self, exception: Exception, func: CallableWithMeta[P, R_co]) -> None:
        self._failure_count += 1
        if self._failure_count >= self._critical_count:
            self._block_time = datetime.now(UTC)
            self._failure_count = 0
            raise BreakerError(
                func_name=f"{func.__module__}.{func.__name__}",
                block_time=self._block_time,
                source_exception=exception,
            ) from exception
        raise exception

    def _execute_func(self, func: CallableWithMeta[P, R_co], *args: P.args, **kwargs: P.kwargs) -> R_co:
        try:
            result = func(*args, **kwargs)
        except self._triggers_on as e:
            self._handle_error(e, func)
            raise
        else:
            self._failure_count = 0
            return result


circuit_breaker = CircuitBreaker(5, 30, Exception)


def get_comments(post_id: int) -> Any:
    response = urlopen(f"https://jsonplaceholder.typicode.com/comments?postId={post_id}")
    return json.loads(response.read())


if __name__ == "__main__":
    comments = get_comments(1)
