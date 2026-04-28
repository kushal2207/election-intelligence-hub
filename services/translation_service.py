import logging
from groq import Groq

logger = logging.getLogger(__name__)

# Map BCP-47 language codes to full language names the LLM understands
_LANGUAGE_NAMES: dict[str, str] = {
    "en": "English",
    "hi": "Hindi",
    "bn": "Bengali",
    "ta": "Tamil",
    "te": "Telugu",
    "mr": "Marathi",
    "gu": "Gujarati",
    "kn": "Kannada",
    "ml": "Malayalam",
    "pa": "Punjabi",
    "or": "Odia",
    "as": "Assamese",
    "ur": "Urdu",
}


class TranslationService:
    """
    Translates the final answer into the user's preferred language using Groq.
    Falls back to English if the target language is unsupported or the API call fails.
    """

    def __init__(self, api_key: str, model: str = "llama-3.3-70b-versatile"):
        self.client = Groq(api_key=api_key)
        self.model = model
        self.max_tokens = 2048

    async def translate(self, text: str, target_language_code: str) -> tuple[str, bool]:
        """
        Translate *text* into *target_language_code*.

        Returns:
            (translated_text, fallback_used)
            fallback_used is True when the English original was returned.
        """
        if target_language_code == "en":
            return text, False

        language_name = _LANGUAGE_NAMES.get(target_language_code)
        if not language_name:
            logger.warning(
                "Unsupported language code '%s'. Falling back to English.", target_language_code
            )
            return text, True

        system_prompt = (
            "You are a professional translator specialising in Indian languages and legal terminology. "
            "Translate the following text accurately into the requested language. "
            "Preserve proper nouns, article numbers, and act names in their original form. "
            "Return ONLY the translated text with no preamble."
        )

        user_message = f"Translate the following text into {language_name}:\n\n{text}"

        try:
            response = self.client.chat.completions.create(
                model=self.model,
                max_tokens=self.max_tokens,
                messages=[
                    {"role": "system", "content": system_prompt},
                    {"role": "user", "content": user_message},
                ],
            )
            return response.choices[0].message.content.strip(), False

        except Exception as exc:
            logger.error(
                "Translation API error for language '%s': %s. Falling back to English.",
                target_language_code,
                exc,
            )
            return text, True
