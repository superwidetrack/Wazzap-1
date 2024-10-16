import os

def generate_structure(root_dir, output_file='project_structure.md'):
    with open(output_file, 'w') as f:
        f.write('# Обзор проекта\n\n')
        f.write('## Структура проекта\n\n')
        f.write('```\n')
        
        for dirpath, dirnames, filenames in os.walk(root_dir):
            level = dirpath.replace(root_dir, '').count(os.sep)
            indent = '    ' * level
            f.write(f'{indent}{os.path.basename(dirpath)}/\n')
            sub_indent = '    ' * (level + 1)
            
            for filename in filenames:
                f.write(f'{sub_indent}{filename}\n')
        
        f.write('```\n\n')
        
        f.write('## Содержимое файлов\n\n')
        
        for dirpath, dirnames, filenames in os.walk(root_dir):
            for filename in filenames:
                file_path = os.path.join(dirpath, filename)
                f.write(f'### {file_path}\n\n')
                f.write('```python\n')
                
                try:
                    with open(file_path, 'r') as file:
                        # Limit the number of lines to read for preview
                        for i, line in enumerate(file):
                            if i >= 10:
                                f.write('...\n')
                                break
                            f.write(line)
                except Exception as e:
                    f.write(f'Ошибка чтения файла: {e}\n')
                
                f.write('```\n\n')

if __name__ == '__main__':
    generate_structure('.').catch(error => {
    console.error('Error:', error);
    alert('Произошла ошибка при загрузке сообщений.');
});@wazzup_bp.route('/webhook', methods=['POST'])
def webhook():
    data = request.json
    message_handler.handle_incoming_message(data)  # Передача данных для обработки
    return jsonify({"status": "success"}), 200with app.app_context():
    db.init_app(app)
    init_db(app)import openai
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
