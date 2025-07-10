import config
import google.generativeai as genai

class GeminiClient:
    def __init__(self, model: str = "gemini-2.5-flash"):
        """
        Initializes the Gemini client with a specific model.
        """
        genai.configure(api_key=config.GEMINI_API_KEY)
        self.model = genai.GenerativeModel(model)

    def chat(self, prompt: str) -> str:
        """
        Sends a prompt to Gemini and returns the response text if available.
        """
        response = self.model.generate_content(prompt)

        try:
            if response.candidates and response.candidates[0].content.parts:
                return response.text.strip()
            else:
                return "[Empty response or blocked by safety filter]"
        except Exception as e:
            print("Gemini error:", e)
            return "[Error generating content]"

