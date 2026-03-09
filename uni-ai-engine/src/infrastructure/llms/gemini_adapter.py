import google.generativeai as genai
from google.generativeai.types import GenerationConfig
from typing import Optional, AsyncGenerator

from infrastructure.llms.base import ILLMService
from configs.settings import settings
from utils.logger import app_logger


class GeminiAdapter(ILLMService):
    def __init__(
        self,
        api_key: str = settings.GEMINI_API_KEY,
        model_name: str = settings.GEMINI_MODEL_NAME
    ):
        # Cấu hình API key cho toàn bộ module genai
        genai.configure(api_key=api_key)
        self.model_name = model_name
        app_logger.info(f"Đã khởi tạo GeminiAdapter với model: {self.model_name}")

    # INTERNAL METHOD
    def _create_model(self, system_prompt: str, temperature: float, max_tokens: int):
        config = GenerationConfig(
            temperature=temperature,
            max_output_tokens=max_tokens,
        )
        return genai.GenerativeModel(
            model_name=self.model_name,
            system_instruction=system_prompt,
            generation_config=config
        )

    # INTERFACE IMPLEMENTATION
    async def generate(
        self,
        system_prompt: str,
        user_prompt: str,
        temperature: float = 0.0,
        max_tokens: int = 1000
    ) -> Optional[str]:

        if not user_prompt or not user_prompt.strip():
            return None

        try:
            model = self._create_model(system_prompt, temperature, max_tokens)
            response = await model.generate_content_async(user_prompt)
            return response.text

        except Exception as e:
            app_logger.error(f"Lỗi khi gọi Gemini API (Generate): {e}")
            return None

    async def generate_stream(
        self,
        system_prompt: str,
        user_prompt: str,
        temperature: float = 0.0,
        max_tokens: int = 1000
    ) -> AsyncGenerator[str, None]:

        if not user_prompt or not user_prompt.strip():
            yield ""
            return

        try:
            model = self._create_model(system_prompt, temperature, max_tokens)
            response = await model.generate_content_async(user_prompt, stream=True)
            async for chunk in response:
                if chunk.text:
                    yield chunk.text

        except Exception as e:
            app_logger.error(f"Lỗi khi gọi Gemini API (Stream): {e}")
            yield f"\n[Hệ thống AI đang gặp sự cố gián đoạn, vui lòng thử lại sau. Lỗi: {e}]"
