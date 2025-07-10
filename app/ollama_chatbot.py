import os
import json
import ollama

class OllamaChatbot:
    def __init__(self, model='llama3.2:1b'):
        self.model = model
        self.history_file = 'conversation_history.json'
        self.conversation_history = []
        self.load_history()

    def load_history(self):
        if os.path.exists(self.history_file):
            with open(self.history_file, 'r') as f:
                try:
                    self.conversation_history = json.load(f)
                except json.JSONDecodeError:
                    self.conversation_history = []

    def save_history(self):
        with open(self.history_file, 'w') as f:
            json.dump(self.conversation_history, f, indent=2)

    def chat(self, user_prompt: str) -> str:
        self.conversation_history.append({'role': 'user', 'content': user_prompt})

        response = ollama.chat(
            model=self.model,
            messages=self.conversation_history
        )

        reply = response['message']['content'].strip()

        self.conversation_history.append({'role': 'assistant', 'content': reply})
        self.save_history()

        return reply
