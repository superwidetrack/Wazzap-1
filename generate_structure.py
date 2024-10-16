    import os

    def generate_structure(root_dir, output_file='project_structure.md'):
        # Список файлов, над которыми вы работаете
        active_files = [
            'main.py',
            'api_wazzup/routes.py',
            'api_openai/routes.py',
            'database/database.py',
            'handlers/message_handler.py',
            'templates/index.html',
            'config/config.py',
            'README.md'
        ]

        with open(output_file, 'w') as f:
            f.write('# Обзор активных файлов проекта\n\n')
            f.write('## Структура проекта\n\n')
            f.write('```\n')

            for file_path in active_files:
                f.write(f'{file_path}\n')

            f.write('```\n\n')

            f.write('## Содержимое файлов\n\n')

            for file_path in active_files:
                full_path = os.path.join(root_dir, file_path)
                f.write(f'### {file_path}\n\n')
                f.write('```python\n')

                try:
                    with open(full_path, 'r') as file:
                        # Ограничиваем количество строк для предварительного просмотра
                        for i, line in enumerate(file):
                            if i >= 10:
                                f.write('...\n')
                                break
                            f.write(line)
                except Exception as e:
                    f.write(f'Ошибка чтения файла: {e}\n')

                f.write('```\n\n')

    if __name__ == '__main__':
        generate_structure('.')