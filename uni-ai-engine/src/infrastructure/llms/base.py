from abc import ABC, abstractmethod
from typing import Optional


class ILLMService(ABC):
    @abstractmethod
    def generate(
        self, system_prompt: str, user_prompt: str, temperature: float = 0.0
    ) -> Optional[str]:
        pass

    @abstractmethod
    def generate_stream(
        self, system_prompt: str, user_prompt: str, temperature: float = 0.0
    ):
        pass
