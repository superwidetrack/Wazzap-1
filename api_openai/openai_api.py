import openai
from config import Config

class OpenAIAssistant:
    def __init__(self):
        self.api_key = Config.OPENAI_API_KEY
        self.assistant_id = Config.OPENAI_ASSISTANT_ID
        openai.api_key = self.api_key

    def create_thread(self):
        thread = openai.beta.threads.create()
        return thread.id

    def add_message_to_thread(self, thread_id, message):
        openai.beta.threads.messages.create(
            thread_id=thread_id,
            role="user",
            content=message
        )

    def run_assistant(self, thread_id):
        run = openai.beta.threads.runs.create(
            thread_id=thread_id,
            assistant_id=self.assistant_id
        )
        while run.status != 'completed':
            run = openai.beta.threads.runs.retrieve(thread_id=thread_id, run_id=run.id)

        messages = openai.beta.threads.messages.list(thread_id=thread_id)
        return messages.data[0].content[0].text.value
