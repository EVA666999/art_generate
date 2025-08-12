#!/bin/bash

echo "========================================"
echo "  Обновление персонажей из файлов в БД"
echo "========================================"
echo

# Переходим в директорию скрипта
cd "$(dirname "$0")"

if [ -z "$1" ]; then
    echo "📋 Использование:"
    echo "  ./update.sh [имя_персонажа]"
    echo "  ./update.sh --list"
    echo
    echo "📝 Примеры:"
    echo "  ./update.sh anna"
    echo "  ./update.sh new_char"
    echo "  ./update.sh --list"
    echo
    read -p "Нажмите Enter для продолжения..."
    exit 1
fi

echo "🚀 Запускаем обновление персонажа..."
echo

python update_character.py "$@"

if [ $? -ne 0 ]; then
    echo
    echo "❌ Ошибка обновления персонажа"
    echo "🔍 Проверьте логи выше для деталей"
else
    echo
    echo "✅ Обновление завершено успешно"
fi

echo
read -p "Нажмите Enter для продолжения..."
