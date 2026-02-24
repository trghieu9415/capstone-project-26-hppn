from abc import ABC, abstractmethod
from typing import Optional, AsyncGenerator


class ILLMService(ABC):
    @abstractmethod
    async def generate(
        self, system_prompt: str, user_prompt: str, temperature: float = 0.0
    ) -> Optional[str]:
        pass

    @abstractmethod
    async def generate_stream(
        self, system_prompt: str, user_prompt: str, temperature: float = 0.0
    ) -> AsyncGenerator[str, None]:
        pass
