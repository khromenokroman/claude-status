#!/bin/bash
# Сборка .deb пакета claude-status

set -e

cd "$(dirname "$0")"
PROJECT_ROOT="$(pwd)"
VERSION="1.1.0"
PKG_NAME="claude-status"
BUILD_DIR="/tmp/${PKG_NAME}-build"

echo "Сборка ${PKG_NAME}_${VERSION}..."

# Очистка
rm -rf "$BUILD_DIR"
mkdir -p "$BUILD_DIR"

# Структура пакета
PKG_DIR="$BUILD_DIR/${PKG_NAME}_${VERSION}_${PKG_NAME}"
mkdir -p "$PKG_DIR/DEBIAN"
mkdir -p "$PKG_DIR/usr/share/${PKG_NAME}/gnome-extension"

# Копируем файлы
cp "$PROJECT_ROOT/claude_usage.py" "$PKG_DIR/usr/share/${PKG_NAME}/"
cp "$PROJECT_ROOT/gnome-extension/"* "$PKG_DIR/usr/share/${PKG_NAME}/gnome-extension/"

# Права
chmod +x "$PKG_DIR/usr/share/${PKG_NAME}/claude_usage.py"

# Копируем DEBIAN-скрипты
cp "$PROJECT_ROOT/debian/postinst" "$PKG_DIR/DEBIAN/postinst"
cp "$PROJECT_ROOT/debian/preinst" "$PKG_DIR/DEBIAN/preinst"
chmod +x "$PKG_DIR/DEBIAN/postinst" "$PKG_DIR/DEBIAN/preinst"

# Создаём control
cat > "$PKG_DIR/DEBIAN/control" << 'CONTROLEOF'
Package: claude-status
Version: 1.1.0
Architecture: all
Maintainer: Roma Khromenok <roma55592@yandex.ru>
Installed-Size: 50
Depends: gnome-shell (>= 48.0), python3
Section: utils
Priority: optional
Description: GNOME Shell extension showing Claude Code usage limits
 Claude Code Limits Indicator (claude-status) is a GNOME Shell extension
 that displays the usage of Claude Code API rate limits (5-hour and
 7-day windows) in the top panel.
 It shows a percentage indicator next to the clock and language
 selector. Clicking the indicator opens a menu with details:
   - 5-hour window usage with countdown to reset
   - 7-day window usage with countdown to reset
   - Last update time
   - Current plan (Pro/Free)
   - Link to open the usage page in browser
 The extension uses an OAuth token from ~/.claude/.credentials.json
 (created automatically by the `claude` CLI) and queries the
 Anthropic API every 5 minutes.
Homepage: https://github.com/khromenokroman/claude-status
CONTROLEOF

# Сборка
cd "$BUILD_DIR"
dpkg-deb --build "$PKG_DIR" "${PKG_NAME}_${VERSION}_all.deb"

# Копируем в проект
cp "${PKG_NAME}_${VERSION}_all.deb" "$PROJECT_ROOT/"

echo ""
echo "Готово: $PROJECT_ROOT/${PKG_NAME}_${VERSION}_all.deb"
echo ""
echo "Установка:"
echo "  sudo dpkg -i ${PKG_NAME}_${VERSION}_all.deb"
echo ""
echo "Удаление:"
echo "  sudo dpkg -r ${PKG_NAME}"
