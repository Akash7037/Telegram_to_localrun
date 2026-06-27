import json
import re
import os
from .config import Config
from .logger import logger

class IntentClassifier:
    def __init__(self):
        self.primary_llm_client = None
        self.fallback_llm_client = None
        self._init_llm_clients()

    def _init_llm_clients(self):
        # Initialize Primary LLM Client
        if Config.PRIMARY_LLM_PROVIDER == "google":
            import google.generativeai as genai
            genai.configure(api_key=Config.PRIMARY_LLM_API_KEY)
            self.primary_llm_client = genai
        elif Config.PRIMARY_LLM_PROVIDER == "openai":
            from openai import OpenAI
            self.primary_llm_client = OpenAI(api_key=Config.PRIMARY_LLM_API_KEY)
        elif Config.PRIMARY_LLM_PROVIDER == "anthropic":
            from anthropic import Anthropic
            self.primary_llm_client = Anthropic(api_key=Config.PRIMARY_LLM_API_KEY)
        elif Config.PRIMARY_LLM_PROVIDER == "openrouter":
            from openai import OpenAI # OpenRouter is OpenAI-compatible
            self.primary_llm_client = OpenAI(
                base_url="https://openrouter.ai/api/v1",
                api_key=Config.PRIMARY_LLM_API_KEY,
            )

        # Initialize Fallback LLM Client (if configured)
        if Config.FALLBACK_LLM_PROVIDER and Config.FALLBACK_LLM_API_KEY:
            if Config.FALLBACK_LLM_PROVIDER == "google":
                import google.generativeai as genai
                genai.configure(api_key=Config.FALLBACK_LLM_API_KEY)
                self.fallback_llm_client = genai
            elif Config.FALLBACK_LLM_PROVIDER == "openai":
                from openai import OpenAI
                self.fallback_llm_client = OpenAI(api_key=Config.FALLBACK_LLM_API_KEY)
            elif Config.FALLBACK_LLM_PROVIDER == "anthropic":
                from anthropic import Anthropic
                self.fallback_llm_client = Anthropic(api_key=Config.FALLBACK_LLM_API_KEY)
            elif Config.FALLBACK_LLM_PROVIDER == "openrouter":
                from openai import OpenAI # OpenRouter is OpenAI-compatible
                self.fallback_llm_client = OpenAI(
                    base_url="https://openrouter.ai/api/v1",
                    api_key=Config.FALLBACK_LLM_API_KEY,
                )

    def heuristic_check(self, text):
        """Cheap local check for casual messages."""
        casual_patterns = [
            r"^(hi|hello|hey|yo|greetings).*$",
            r"^(how are you|how\s*s it going|what\s*s up).*$",
            r"^(thanks|thank you|cool|nice|ok|okay).*$",
        ]
        text_lower = text.lower().strip()
        for pattern in casual_patterns:
            if re.match(pattern, text_lower):
                return {"type": "casual"}
        return None

    def _call_llm(self, client, provider, model, prompt):
        try:
            if provider == "google":
                model_instance = client.GenerativeModel(model)
                response = model_instance.generate_content(prompt)
                # Gemini API returns content in parts, join them
                return json.loads(response.text)
            elif provider == "openai" or provider == "openrouter":
                response = client.chat.completions.create(
                    model=model,
                    messages=[{"role": "user", "content": prompt}],
                    response_format={"type": "json_object"}
                )
                return json.loads(response.choices[0].message.content)
            elif provider == "anthropic":
                response = client.messages.create(
                    model=model,
                    max_tokens=1000,
                    messages=[{"role": "user", "content": prompt}]
                )
                return json.loads(response.content[0].text)
        except Exception as e:
            logger.error(f"{provider} LLM call failed with model {model}: {str(e)}")
            return None

    def llm_check(self, text):
        """Fallback to LLM for intent classification."""
        prompt = f"""
        Classify the following message from a user to their laptop assistant.
        Return a strict JSON object with:
        - "type": "command" or "casual"
        - "action": the action name if it's a command (open_browser_search, system_sleep, system_shutdown, lock_screen, open_app, close_app)
        - "params": a dictionary of parameters for the action (e.g., {{"query": "lofi music"}}, {{"app_name": "notepad"}})

        Message: "{text}"
        """
        
        # Try Primary LLM
        if self.primary_llm_client:
            logger.info(f"Attempting primary LLM ({Config.PRIMARY_LLM_PROVIDER}) for classification.")
            result = self._call_llm(
                self.primary_llm_client, 
                Config.PRIMARY_LLM_PROVIDER, 
                Config.PRIMARY_LLM_MODEL, 
                prompt
            )
            if result:
                return result
            logger.warning(f"Primary LLM ({Config.PRIMARY_LLM_PROVIDER}) failed. Trying fallback...")

        # Try Fallback LLM
        if self.fallback_llm_client:
            logger.info(f"Attempting fallback LLM ({Config.FALLBACK_LLM_PROVIDER}) for classification.")
            result = self._call_llm(
                self.fallback_llm_client, 
                Config.FALLBACK_LLM_PROVIDER, 
                Config.FALLBACK_LLM_MODEL, 
                prompt
            )
            if result:
                return result
            logger.warning(f"Fallback LLM ({Config.FALLBACK_LLM_PROVIDER}) also failed.")

        logger.error("Both primary and fallback LLMs failed. Defaulting to casual.")
        return {"type": "casual"}  # Default to casual on failure to avoid accidental commands

    def classify(self, text):
        # 1. Heuristic pass
        result = self.heuristic_check(text)
        if result:
            logger.info(f"Heuristic classified: {text} -> {result["type"]}")
            return result
        
        # 2. LLM fallback
        result = self.llm_check(text)
        logger.info(f"LLM classified: {text} -> {result.get("type")}")
        return result
