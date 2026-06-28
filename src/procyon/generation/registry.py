from __future__ import annotations
from dataclasses import dataclass, field
from typing import Generic, TypeVar
T = TypeVar("T")
@dataclass
class ComponentRegistry(Generic[T]):
    _items: dict[str, T] = field(default_factory=dict)
    def register(self, name: str, component: T) -> None: self._items[name] = component
    def get(self, name: str) -> T: return self._items[name]
    def available(self) -> list[str]: return sorted(self._items)
