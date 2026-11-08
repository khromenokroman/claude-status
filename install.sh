#!/bin/bash
# Установка claude-status (запускать от пользователя, не root)

set -e

echo "Установка claude-status..."

# Пользовательские каталоги
USER_CONFIG="$HOME/.config/claude-status"
USER_EXTENSIONS="$HOME/.local/share/gnome-shell/extensions"
EXT_NAME="claude-status@panel.local"

# Каталог с файлами (относительно скрипта)
SCRIPT_DIR="$(cd "$(dirname "$0")" && pwd)"

# Создаём каталоги
mkdir -p "$USER_CONFIG"
mkdir -p "$USER_EXTENSIONS/$EXT_NAME"

# Копируем файлы
cp "$SCRIPT_DIR/claude_usage.py" "$USER_CONFIG/"
cp "$SCRIPT_DIR/gnome-extension/"* "$USER_EXTENSIONS/$EXT_NAME/"

# Права
chmod +x "$USER_CONFIG/claude_usage.py"

echo "Установлено:"
echo "  - $USER_CONFIG/claude_usage.py"
echo "  - $USER_EXTENSIONS/$EXT_NAME/"
echo ""
echo "Активируйте расширение:"
echo "  gnome-extensions enable $EXT_NAME"
echo "Перезапустите GNOME Shell (Wayland: перелогин, X11: Alt+F2 -> r)."
