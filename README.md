# claude-status

Виджет для панели GNOME Shell, показывающий остаток лимитов Claude Code
(окна 5 часов и 7 дней).

Подходит для Debian 13 / GNOME Shell 48.

## Состав

- `claude_usage.py` - Python-скрипт, запрашивает лимиты у Anthropic API
  и печатает JSON на stdout.
- `gnome-extension/` - расширение GNOME Shell (ESM, GNOME Shell 45+).
- `whatsnew.txt` - журнал изменений.

## Как работает

1. Python-скрипт читает OAuth-токен из `~/.claude/.credentials.json`
   (ключ `claudeAiOauth.accessToken`).
2. Выполняет `GET https://api.anthropic.com/api/oauth/usage`
   с заголовком `anthropic-beta: oauth-2025-04-20`.
3. Расширение запускает скрипт раз в 60 секунд через
   `GLib.spawn_command_line_sync` и обновляет индикатор.

В панели отображается процент недельного окна. При клике раскрывается
меню с двумя окнами (5ч / 7д) и временем до сброса.

## Установка

### 1. Python-скрипт

Скопируйте `claude_usage.py` в пользовательский каталог настроек:

```bash
mkdir -p ~/.config/claude-status
cp claude_usage.py ~/.config/claude-status/
chmod +x ~/.config/claude-status/claude_usage.py
```

### 2. GNOME-расширение

Скопируйте папку `gnome-extension/` в каталог расширений:

```bash
cp -r gnome-extension ~/.local/share/gnome-shell/extensions/claude-status@panel.local
```

### 3. Активация

```bash
gnome-extensions enable claude-status@panel.local
```

Если расширение не подхватилось, перезапустите GNOME Shell:

- Wayland: `Alt+F2` -> `r` не работает; выйдите из сессии и войдите снова.
- X11: `Alt+F2` -> `r` -> Enter.

Или перезагрузите GNOME Shell через `gnome-extensions` в режиме восстановления.

## Использование

- В верхней панели, рядом с часами, появляется процент недельного лимита
  (например `7%`).
- При наведении - tooltip с деталями по обоим окнам.
- При клике - меню с строками:
  - `5ч окно: 1%, сброс через 1ч 2м`
  - `7д окно: 7%, сброс через 4ч 30м`
  - Активный лимит с подсветкой по severity.

## Токен

Токен берётся из `~/.claude/.credentials.json`, который создаётся
автоматически при первой авторизации `claude` (команда `claude` в
терминале, вход через браузер).

Если токен истёк, расширение покажет «Ошибка» в меню. Для обновления
запустите `claude` в терминале ещё раз.

## Снятие

```bash
gnome-extensions disable claude-status@panel.local
rm -rf ~/.local/share/gnome-shell/extensions/claude-status@panel.local
rm -rf ~/.config/claude-status
```

## Требования

- Python 3.8+ (только stdlib, без зависимостей)
- GNOME Shell 45+ (проверено на 48)
- Установленный и авторизованный `claude` CLI
