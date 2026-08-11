"""线程安全的 LRU 缓存：避免重复打公共数据库 API，遵守限速。"""
from __future__ import annotations

import threading
import time
from collections import OrderedDict
from typing import Any, Callable, TypeVar

T = TypeVar("T")


class LRUCache:
    """简单的线程安全 LRU 缓存（内存）。"""

    def __init__(self, maxsize: int = 128, ttl_seconds: float = 3600.0) -> None:
        self._maxsize = maxsize
        self._ttl = ttl_seconds
        self._cache: OrderedDict[str, tuple[float, Any]] = OrderedDict()
        self._lock = threading.Lock()

    def get(self, key: str) -> Any | None:
        with self._lock:
            item = self._cache.get(key)
            if item is None:
                return None
            ts, value = item
            if self._ttl > 0 and time.monotonic() - ts > self._ttl:
                del self._cache[key]
                return None
            self._cache.move_to_end(key)
            return value

    def set(self, key: str, value: Any) -> None:
        with self._lock:
            self._cache[key] = (time.monotonic(), value)
            self._cache.move_to_end(key)
            while len(self._cache) > self._maxsize:
                self._cache.popitem(last=False)

    def clear(self) -> None:
        with self._lock:
            self._cache.clear()

    def __len__(self) -> int:
        with self._lock:
            return len(self._cache)


def cached(cache: LRUCache, key_fn: Callable[..., str]):
    """装饰器：为客户端方法加缓存（仅缓存 JSON 序列化安全的返回值）。"""

    def deco(fn: Callable[..., T]) -> Callable[..., T]:
        def wrapper(*args: Any, **kwargs: Any) -> T:
            key = key_fn(*args, **kwargs)
            hit = cache.get(key)
            if hit is not None:
                return hit
            value = fn(*args, **kwargs)
            cache.set(key, value)
            return value

        return wrapper

    return deco
