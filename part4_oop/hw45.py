from collections.abc import Callable
from dataclasses import dataclass, field
from typing import Any, TypeVar

from part4_oop.interfaces import Cache, HasCache, Policy, Storage

K = TypeVar("K")
V = TypeVar("V")


@dataclass
class DictStorage(Storage[K, V]):
    _data: dict[K, V] = field(default_factory=dict, init=False)

    def set(self, key: K, value: V) -> None:
        self._data[key] = value

    def get(self, key: K) -> V | None:
        return self._data.get(key)

    def exists(self, key: K) -> bool:
        return key in self._data

    def remove(self, key: K) -> None:
        self._data.pop(key, None)

    def clear(self) -> None:
        self._data.clear()


@dataclass
class FIFOPolicy(Policy[K]):
    capacity: int = 5
    _order: list[K] = field(default_factory=list, init=False)

    def register_access(self, key: K) -> None:
        if key not in self._order:
            self._order.append(key)

    def get_key_to_evict(self) -> K | None:
        if len(self._order) > self.capacity:
            return self._order[0]

        return None

    def remove_key(self, key: K) -> None:
        if key in self._order:
            self._order.remove(key)

    def clear(self) -> None:
        self._order.clear()

    @property
    def has_keys(self) -> bool:
        return bool(self._order)


@dataclass
class LRUPolicy(Policy[K]):
    capacity: int = 5
    _order: list[K] = field(default_factory=list, init=False)

    def register_access(self, key: K) -> None:
        if key in self._order:
            self._order.remove(key)

        self._order.append(key)

    def get_key_to_evict(self) -> K | None:
        if len(self._order) > self.capacity:
            return self._order[0]

        return None

    def remove_key(self, key: K) -> None:
        if key in self._order:
            self._order.remove(key)

    def clear(self) -> None:
        self._order.clear()

    @property
    def has_keys(self) -> bool:
        return bool(self._order)


@dataclass
class LFUPolicy(Policy[K]):
    capacity: int = 5
    _key_counter: dict[K, int] = field(default_factory=dict, init=False)

    def register_access(self, key: K) -> None:
        if key not in self._key_counter:
            self._key_counter[key] = 0
        self._key_counter[key] += 1

    def get_key_to_evict(self) -> K | None:
        if len(self._key_counter) >= self.capacity:
            last_key = list(self._key_counter)[-1]
            candidates = [k for k in list(self._key_counter) if k != last_key]
            if not candidates:
                return last_key
            min_count = min(self._key_counter[k] for k in candidates)
            for key in candidates:
                if self._key_counter[key] == min_count:
                    return key
            return None
        return None

    def remove_key(self, key: K) -> None:
        self._key_counter.pop(key, None)

    def clear(self) -> None:
        self._key_counter.clear()

    @property
    def has_keys(self) -> bool:
        return bool(self._key_counter)


@dataclass
class MIPTCache(Cache[K, V]):
    storage: Storage[K, V]
    policy: Policy[K]

    def set(self, key: K, value: V) -> None:
        self.storage.set(key, value)
        self.policy.register_access(key)
        evict_key = self.policy.get_key_to_evict()
        if evict_key is not None:
            self.storage.remove(evict_key)
            self.policy.remove_key(evict_key)

    def get(self, key: K) -> V | None:
        value = self.storage.get(key)
        if value is not None:
            self.policy.register_access(key)
        return value

    def exists(self, key: K) -> bool:
        exists = self.storage.exists(key)
        if exists:
            self.policy.register_access(key)
        return exists

    def remove(self, key: K) -> None:
        self.storage.remove(key)
        self.policy.remove_key(key)

    def clear(self) -> None:
        self.storage.clear()
        self.policy.clear()


class CachedProperty[V]:
    def __init__(self, func: Callable[..., V]) -> None:
        self.func = func
        self.key = ""

    def __set_name__(self, owner: type, name: str) -> None:
        self.key = f"{owner.__name__}.{name}"

    def __get__(self, instance: HasCache[Any, Any] | None, owner: type) -> V:
        if instance is None:
            return self  # type: ignore[return-value]
        cached_value = instance.cache.get(self.key)
        if cached_value is not None:
            return cached_value
        computed_value = self.func(instance)
        instance.cache.set(self.key, computed_value)
        return computed_value
