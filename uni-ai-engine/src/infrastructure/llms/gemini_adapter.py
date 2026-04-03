from google import genai
from typing import AsyncGenerator
from google.genai import types
from infrastructure.llms.base import ILLMService
from configs.settings import settings
from utils.loggers.app_logger import app_logger


class GeminiService(ILLMService):
    def __init__(
        self,
        api_key: str = settings.GEMINI_API_KEY,
        model_name: str = settings.GEMINI_MODEL_NAME
    ):
        self.client = genai.Client(api_key=api_key)
        self.model_name = model_name
        app_logger.info(
            f"Đã khởi tạo GeminiService (GenAI SDK) với model: {self.model_name}")
        app_logger.info(f"api_key: {api_key[:5]}...{api_key[-5:]}")

    async def generate_stream(
        self,
        system_prompt: str,
        user_prompt: str,
        temperature: float = 0.0,
        max_tokens: int = 2000
    ) -> AsyncGenerator[str, None]:

        if not user_prompt or not user_prompt.strip():
            yield ""
            return

        try:
            config = types.GenerateContentConfig(
                system_instruction=system_prompt,
                temperature=temperature,
                max_output_tokens=max_tokens,
            )

            stream = await self.client.aio.models.generate_content_stream(
                model=self.model_name,
                contents=user_prompt,
                config=config
            )

            async for chunk in stream:
                if chunk.text:
                    yield chunk.text

        except Exception as e:
            app_logger.error(f"Lỗi khi gọi Gemini API (Stream): {e}")
            yield f"\n[Lỗi kết nối AI: {e}]"

    async def generate(self, system_prompt, user_prompt, temperature=0.0,
                       max_tokens=1000):
        try:
            config = types.GenerateContentConfig(
                system_instruction=system_prompt,
                temperature=temperature,
                max_output_tokens=max_tokens,
            )

            response = await self.client.aio.models.generate_content(
                model=self.model_name,
                contents=user_prompt,
                config=config
            )

            return response.text
        except Exception as e:
            app_logger.error(f"Lỗi Generate: {e}")
            return None
