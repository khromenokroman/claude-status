#!/bin/bash
# Удаление claude-status (запускать от пользователя, не root)

set -e

echo "Удаление claude-status..."

# Пользовательские каталоги
USER_CONFIG="$HOME/.config/claude-status"
USER_EXTENSIONS="$HOME/.local/share/gnome-shell/extensions"
EXT_NAME="claude-status@panel.local"

# Отключаем расширение
gnome-extensions disable $EXT_NAME 2>/dev/null || true

# Удаляем файлы
rm -rf "$USER_CONFIG/claude-status"
rm -rf "$USER_EXTENSIONS/$EXT_NAME"

echo "Удалено."
