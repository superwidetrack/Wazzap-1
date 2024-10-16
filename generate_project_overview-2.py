import os
from pathlib import Path
import mimetypes
import argparse
import logging
import stat

def escape_markdown(text):
    """Экранирует специальные символы для корректного отображения в Markdown."""
    return text.replace('`', '\\`').replace('*', '\\*').replace('_', '\\_')

def is_text_file(file_path):
    """Определяет, является ли файл текстовым на основе его MIME-типа."""
    mime_type, _ = mimetypes.guess_type(file_path)
    if mime_type is None:
        return False
    return mime_type.startswith('text')

def get_file_permissions(file_path):
    """Возвращает строковое представление прав доступа к файлу."""
    st = os.stat(file_path)
    mode = st.st_mode
    permissions = []
    for who in ['USR', 'GRP', 'OTH']:
        for what in ['R', 'W', 'X']:
            if mode & getattr(stat, f'S_I{what}{who}'):
                permissions.append(what.lower())
            else:
                permissions.append('-')
    return ''.join(permissions)

def generate_folder_description(folder_path):
    """
    Генерирует описание папки.
    В текущей реализации описание автоматически создается на основе имени папки.
    При необходимости можно расширить функциональность для более детальных описаний.
    """
    # Пример простого описания. Можно доработать для более информативных описаний.
    description = f"**{folder_path.name}/** - Описание папки не предоставлено."
    return description

def generate_file_content(file_path, max_file_size=100000):
    """Генерирует содержимое файла в формате Markdown."""
    try:
        file_size = file_path.stat().st_size
        if file_size > max_file_size:
            return f"**Файл слишком большой для отображения (>{max_file_size} байт).**\n\n"
        elif file_size == 0:
            return "**Файл пуст.**\n\n"

        try:
            with open(file_path, 'r', encoding='utf-8') as f:
                content = f.read()

            if not content.strip():
                return "**Файл содержит только пробельные символы.**\n\n"

            content = escape_markdown(content)
            lang = {
                '.py': 'python',
                '.js': 'javascript',
                '.html': 'html',
                '.css': 'css',
                '.json': 'json',
                '.env': 'dotenv',
                '.gitignore': 'gitignore',
                '.md': 'markdown',
                'Dockerfile': 'dockerfile',
                'Makefile': 'makefile'
            }.get(file_path.suffix or file_path.name, '')
            return f"```{lang}\n{content}\n```\n\n"
        except UnicodeDecodeError:
            # Попробуем прочитать файл в бинарном режиме
            with open(file_path, 'rb') as f:
                content = f.read()
            return f"**Ошибка: файл содержит не-UTF-8 символы. Первые 100 байт (hex):**\n```\n{content[:100].hex()}\n```\n\n"
        except PermissionError:
            return f"**Ошибка: нет прав доступа для чтения файла.**\n\n"
    except Exception as e:
        return f"**Ошибка при чтении файла:** {str(e)}\n\n"

def generate_markdown_recursive(project_dir, output_file, main_files=None, exclude_dirs=None, exclude_files=None, max_file_size=100000):
    if main_files is None:
        main_files = ['README.md', 'main.py', 'app.py', 'index.js', 'Dockerfile', 'Makefile']
    if exclude_dirs is None:
        exclude_dirs = ['__pycache__', 'venv', '.venv', 'node_modules', 'pypoetry', 'replit']
    if exclude_files is None:
        exclude_files = ['PROJECT_OVERVIEW.md']

    logging.warning(f"Начало генерации обзора проекта: {project_dir}")

    try:
        with open(output_file, 'w', encoding='utf-8') as md:
            md.write(f"# Обзор проекта: `{project_dir.name}`\n\n")

            # Рекурсивный обход всех папок
            for root, dirs, files in os.walk(project_dir):
                # Исключаем директории
                dirs[:] = [d for d in dirs if d not in exclude_dirs]
                current_path = Path(root)
                relative_path = current_path.relative_to(project_dir)
                indent_level = len(relative_path.parts)
                indent = '    ' * indent_level
                folder_name = current_path.name
                md.write(f"{indent}- **{folder_name}/**\n")

                # Добавление описания папки
                description = generate_folder_description(current_path)
                md.write(f"{indent}    {description}\n")

                # Обработка файлов в текущей папке
                for file in sorted(files):
                    if file in exclude_files:
                        continue
                    file_path = current_path / file
                    if not file_path.is_symlink():
                        md.write(f"{indent}    - `{file}`\n")

                        # Проверяем, является ли файл основным
                        if file_path.suffix in [Path(f).suffix for f in main_files] or file_path.name in main_files:
                            relative_file_path = file_path.relative_to(project_dir)
                            md.write(f"\n{indent}    ### `{relative_file_path}`\n\n")
                            try:
                                file_size = file_path.stat().st_size
                            except Exception as e:

