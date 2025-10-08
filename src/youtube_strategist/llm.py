"""Ollama LLM wrapper for local model inference."""

import ollama
from typing import Optional, Dict, Any
import json
import logging

logger = logging.getLogger(__name__)

class OllamaLLM:
    """Wrapper for Ollama local LLM inference."""

    def __init__(
        self,
        model: str = "mistral:7b",
        temperature: float = 0.7,
        max_tokens: int = 2000
    ):
        self.model = model
        self.temperature = temperature
        self.max_tokens = max_tokens
        self._ensure_model_available()

    def _ensure_model_available(self):
        """Check if model is available, pull if not."""
        try:
            ollama.show(self.model)
            logger.info(f"Model {self.model} is available")
        except Exception:
            logger.info(f"Pulling model {self.model}...")
            ollama.pull(self.model)
            logger.info(f"Model {self.model} pulled successfully")

    def generate(
        self,
        prompt: str,
        system_prompt: Optional[str] = None,
        json_mode: bool = False
    ) -> str:
        """Generate text from prompt."""
        messages = []

        if system_prompt:
            messages.append({"role": "system", "content": system_prompt})

        messages.append({"role": "user", "content": prompt})

        try:
            response = ollama.chat(
                model=self.model,
                messages=messages,
                options={
                    "temperature": self.temperature,
                    "num_predict": self.max_tokens,
                },
                format="json" if json_mode else ""
            )

            content = response['message']['content']
            logger.debug(f"Generated response: {content[:100]}...")
            return content

        except Exception as e:
            logger.error(f"Error generating with Ollama: {e}")
            raise

    def generate_structured(
        self,
        prompt: str,
        system_prompt: Optional[str] = None,
        schema: Optional[Dict[str, Any]] = None
    ) -> Dict[str, Any]:
        """Generate structured JSON output."""
        json_prompt = prompt
        if schema:
            json_prompt += f"\n\nReturn ONLY valid JSON matching this schema:\n{json.dumps(schema, indent=2)}"

        response = self.generate(
            prompt=json_prompt,
            system_prompt=system_prompt,
            json_mode=True
        )

        try:
            return json.loads(response)
        except json.JSONDecodeError as e:
            logger.error(f"Failed to parse JSON response: {response}")
            # Try to extract JSON from markdown code blocks
            if "```json" in response:
                json_str = response.split("```json")[1].split("```")[0].strip()
                return json.loads(json_str)
            elif "```" in response:
                json_str = response.split("```")[1].split("```")[0].strip()
                return json.loads(json_str)
            raise e
