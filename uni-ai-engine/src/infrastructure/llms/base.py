from abc import ABC, abstractmethod
from typing import Optional, AsyncGenerator


class ILLMService(ABC):
    @abstractmethod
    async def generate(
        self,
        system_prompt: str,
        user_prompt: str,
        temperature: float = 0.0,
        max_tokens: int = 1000
    ) -> Optional[str]:
        pass

    @abstractmethod
    def generate_stream(
        self,
        system_prompt: str,
        user_prompt: str,
        temperature: float = 0.0,
        max_tokens: int = 1000
    ) -> AsyncGenerator[str, None]:
        pass
