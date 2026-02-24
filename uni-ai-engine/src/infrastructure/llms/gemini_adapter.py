import google.generativeai as genai
from typing import Optional, Generator
from .base import ILLMService


class GeminiAdapter(ILLMService):
    def __init__(self, api_key: str, model_name: str = "gemini-1.5-flash"):
        genai.configure(api_key=api_key)
        self.model_name = model_name

    def _get_model(self, system_prompt: str, temperature: float):
        generation_config = genai.GenerationConfig(
            temperature=temperature,
            top_p=0.95,
            top_k=64,
        )

        return genai.GenerativeModel(
            model_name=self.model_name,
            generation_config=generation_config,
            system_instruction=system_prompt,
        )

    def generate(
        self, system_prompt: str, user_prompt: str, temperature: float = 0.0
    ) -> Optional[str]:
        try:
            model = self._get_model(system_prompt, temperature)
            response = model.generate_content(user_prompt)

            return response.text
        except Exception as e:
            print(f"[Error] Lỗi khi gọi Gemini API (Generate): {e}")
            return None

    def generate_stream(
        self, system_prompt: str, user_prompt: str, temperature: float = 0.0
    ) -> Generator[str, None, None]:
        try:
            model = self._get_model(system_prompt, temperature)
            response = model.generate_content(user_prompt, stream=True)

            for chunk in response:
                if chunk.text:
                    yield chunk.text
        except Exception as e:
            print(f"[Error] Lỗi khi gọi Gemini API (Stream): {e}")
            yield f"[Lỗi hệ thống: Không thể kết nối tới LLM - {str(e)}]"
