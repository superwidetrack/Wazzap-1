#!/bin/bash

# Функция для рекурсивного переименования директорий
rename_directories() {
    find . -depth -type d -name "*wazzap*" | while read -r dir; do
        newdir=$(echo "$dir" | sed 's/wazzap/wazzup/g')
        echo "Переименование директории: $dir -> $newdir"
        mv "$dir" "$newdir"
    done
}

# Функция для переименования файлов
rename_files() {
    find . -type f -name "*wazzap*" | while read -r file; do
        newfile=$(echo "$file" | sed 's/wazzap/wazzup/g')
        echo "Переименование файла: $file -> $newfile"
        mv "$file" "$newfile"
    done
}

# Функция для замены содержимого в файлах
replace_content() {
    find . -type f \( -name "*.py" -o -name "*.html" -o -name "*.js" -o -name "*.md" \) -print0 | xargs -0 sed -i 's/wazzap/wazzup/g'
    echo "Замена содержимого в файлах завершена."
}

# Выполнение функций
rename_directories
rename_files
replace_content

echo "Замена 'wazzap' на 'wazzup' завершена."
