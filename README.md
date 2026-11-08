# claude-status

Виджет для панели GNOME Shell, показывающий использование лимитов Claude Code
(окна 5 часов и 7 дней).

Подходит для Debian 13 / GNOME Shell 48.

## Состав

- `claude_usage.py` - Python-скрипт, запрашивает лимиты у Anthropic API
  и печатает JSON на stdout.
- `gnome-extension/` - расширение GNOME Shell (ESM, GNOME Shell 48+).
- `whatsnew.txt` - журнал изменений.

## Как работает

1. Python-скрипт читает OAuth-токен из `~/.claude/.credentials.json`
   (ключ `claudeAiOauth.accessToken`).
2. Выполняет `GET https://api.anthropic.com/api/oauth/usage`
   с заголовком `anthropic-beta: oauth-2025-04-20`.
3. Расширение запускает скрипт раз в 5 минут через
   `GLib.spawn_async` (не блокирует UI) и обновляет индикатор.

В панели отображается `5ч: 5% | 7д: 8%`. При клике раскрывается меню
с деталями по обоим окнам, временем до сброса, тарифом и ссылкой
на страницу лимитов в браузере.

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

- Wayland: выйдите из сессии и войдите снова.
- X11: `Alt+F2` -> `r` -> Enter.

## Использование

- В верхней панели, между часами и индикатором языка, появляется
  строка вида `5ч: 5% | 7д: 8%`.
- При клике раскрывается меню:
  - `5ч окно: 5%, сброс через 4ч 30м`
  - `7д окно: 8%, сброс через 3д 4ч`
  - `Обновлено: 09:55:48`
  - `Тариф: pro`
  - `Автообновление: каждые 5 мин`
  - `Открыть страницу лимитов` (переход в браузер)

При ошибке (rate limit, нет сети) на панели остаются последние
успешные данные.

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
- GNOME Shell 48+
- Установленный и авторизованный `claude` CLI
