import json
import re
from .config import Config
from .logger import logger

class IntentClassifier:
    def __init__(self):
        self.llm_client = self._init_llm_client()

    def _init_llm_client(self):
        if Config.LLM_PROVIDER == "openai":
            from openai import OpenAI
            return OpenAI(api_key=Config.LLM_API_KEY)
        elif Config.LLM_PROVIDER == "anthropic":
            from anthropic import Anthropic
            return Anthropic(api_key=Config.LLM_API_KEY)
        return None

    def heuristic_check(self, text):
        """Cheap local check for casual messages."""
        casual_patterns = [
            r"^(hi|hello|hey|yo|greetings).*$",
            r"^(how are you|how's it going|what's up).*$",
            r"^(thanks|thank you|cool|nice|ok|okay).*$",
        ]
        text_lower = text.lower().strip()
        for pattern in casual_patterns:
            if re.match(pattern, text_lower):
                return {"type": "casual"}
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
        
        try:
            if Config.LLM_PROVIDER == "openai":
                response = self.llm_client.chat.completions.create(
                    model=Config.LLM_MODEL,
                    messages=[{"role": "user", "content": prompt}],
                    response_format={"type": "json_object"}
                )
                return json.loads(response.choices[0].message.content)
            elif Config.LLM_PROVIDER == "anthropic":
                response = self.llm_client.messages.create(
                    model=Config.LLM_MODEL,
                    max_tokens=1000,
                    messages=[{"role": "user", "content": prompt}]
                )
                # Anthropic doesn't support response_format="json_object" yet in the same way, 
                # so we might need to parse the text.
                return json.loads(response.content[0].text)
        except Exception as e:
            logger.error(f"LLM classification failed: {str(e)}")
            return {"type": "casual"}  # Default to casual on failure to avoid accidental commands

    def classify(self, text):
        # 1. Heuristic pass
        result = self.heuristic_check(text)
        if result:
            logger.info(f"Heuristic classified: {text} -> {result['type']}")
            return result
        
        # 2. LLM fallback
        result = self.llm_check(text)
        logger.info(f"LLM classified: {text} -> {result.get('type')}")
        return result
