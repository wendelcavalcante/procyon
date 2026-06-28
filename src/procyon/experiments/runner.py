from __future__ import annotations
from abc import ABC, abstractmethod
class ExperimentRunner(ABC):
    @abstractmethod
    def run(self) -> None: ...
