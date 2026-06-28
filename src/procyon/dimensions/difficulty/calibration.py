from __future__ import annotations
from abc import ABC, abstractmethod
class DifficultyCalibrator(ABC):
    @abstractmethod
    def normalize(self, raw_metrics: dict[str, float], context: object | None = None) -> float: ...
