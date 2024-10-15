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

def generate_directory_structure(project_dir, exclude_dirs=None, exclude_files=None):
    """
    Генерирует структуру директорий и файлов в формате Markdown.
    Исключает указанные директории и файлы.
    """
    lines = []
    for root, dirs, files in os.walk(project_dir):
        # Исключаем только директории из списка exclude_dirs
        dirs[:] = [d for d in dirs if d not in exclude_dirs]
        level = len(Path(root).relative_to(project_dir).parts)
        indent = '    ' * level
        folder_name = Path(root).name
        lines.append(f"{indent}- **{folder_name}/**")
        sub_indent = '    ' * (level + 1)
        for f in sorted(files):
            if f not in exclude_files:
                file_path = Path(root) / f
                if not file_path.is_symlink():
                    lines.append(f"{sub_indent}- {f}")
    return '\n'.join(lines)

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

def generate_markdown(project_dir, output_file, max_file_size=100000, extensions=None, include_files=None, exclude_dirs=None, exclude_files=None):
    if extensions is None:
        extensions = ['.py', '.js', '.html', '.css', '.json', '.md']
    if include_files is None:
        include_files = ['.env', '.gitignore', 'Dockerfile', 'Makefile']
    if exclude_dirs is None:
        exclude_dirs = ['__pycache__', 'venv', '.venv', 'node_modules', 'pypoetry', 'replit']  # Добавлено 'replit'
    if exclude_files is None:
        exclude_files = ['PROJECT_OVERVIEW.md']

    logging.warning(f"Начало генерации обзора проекта: {project_dir}")

    try:
        with open(output_file, 'w', encoding='utf-8') as md:
            md.write(f"# Обзор проекта: `{project_dir.name}`\n\n")
            md.write("## Структура проекта\n\n")
            directory_structure = generate_directory_structure(project_dir, exclude_dirs, exclude_files)
            md.write(f"```\n{directory_structure}\n```\n\n")

            md.write("## Содержимое файлов\n\n")
            for root, dirs, files in os.walk(project_dir):
                dirs[:] = [d for d in dirs if d not in exclude_dirs]
                for file in sorted(files):
                    if file not in exclude_files:
                        file_path = Path(root) / file
                        if file_path.suffix in extensions or file_path.name in include_files:
                            relative_path = file_path.relative_to(project_dir)
                            md.write(f"### `{relative_path}`\n\n")
                            file_size = file_path.stat().st_size
                            md.write(f"Размер файла: {file_size} байт\n\n")
                            md.write(f"MIME-тип: {mimetypes.guess_type(file_path)[0]}\n\n")
                            md.write(f"Права доступа: {get_file_permissions(file_path)}\n\n")
                            md.write(generate_file_content(file_path, max_file_size))

        logging.warning(f"Markdown-файл с обзором проекта создан: {output_file}")
    except Exception as e:
        logging.error(f"Ошибка при открытии файла для записи: {e}")

if __name__ == "__main__":
    logging.basicConfig(
        filename='generate_project_overview.log',
        level=logging.WARNING,  # Изменено с INFO на WARNING
        format='%(asctime)s - %(levelname)s - %(message)s'
    )

    parser = argparse.ArgumentParser(description="Генерация обзора проекта в Markdown.")
    parser.add_argument('--project_dir', type=str, default=str(Path(__file__).parent.resolve()), help='Путь к директории проекта.')
    parser.add_argument('--output_file', type=str, default='PROJECT_OVERVIEW.md', help='Имя выходного Markdown-файла.')
    parser.add_argument('--max_file_size', type=int, default=100000, help='Максимальный размер файла в байтах для отображения.')
    parser.add_argument('--extensions', type=str, nargs='+', default=['.py', '.js', '.html', '.css', '.json', '.md'], help='Список расширений файлов для обработки.')
    parser.add_argument('--include_files', type=str, nargs='+', default=['.env', '.gitignore', 'Dockerfile', 'Makefile'], help='Список файлов для включения независимо от расширения.')
    parser.add_argument('--exclude_dirs', type=str, nargs='+', default=['__pycache__', 'venv', '.venv', 'node_modules', 'pypoetry', 'replit'], help='Список директорий для исключения из обхода.')  # Добавлено 'replit'
    parser.add_argument('--exclude_files', type=str, nargs='+', default=['PROJECT_OVERVIEW.md'], help='Список файлов для исключения из обработки.')
    args = parser.parse_args()

    project_directory = Path(args.project_dir).resolve()
    output_markdown = project_directory / args.output_file
    generate_markdown(
        project_dir=project_directory,
        output_file=output_markdown,
        max_file_size=args.max_file_size,
        extensions=args.extensions,
        include_files=args.include_files,
        exclude_dirs=args.exclude_dirs,
        exclude_files=args.exclude_files
    )
