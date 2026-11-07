#!/usr/bin/env python3
"""
Скрипт получения лимитов Claude Code из Anthropic API.

Читает OAuth-токен из ~/.claude/.credentials.json, ходит на
https://api.anthropic.com/api/oauth/usage и печатает JSON на stdout.

Формат вывода:
{
  "ok": true,
  "plan": "pro",
  "five_hour": {"utilization": 1.0, "resets_at": "2026-11-08T01:40:00+00:00"},
  "seven_day": {"utilization": 7.0, "resets_at": "2026-11-13T17:00:00+00:00"},
  "limits": [
    {"kind": "session", "percent": 1, "resets_at": "..."},
    {"kind": "weekly_all", "percent": 7, "resets_at": "..."}
  ]
}

При ошибке:
{
  "ok": false,
  "error": "описание ошибки"
}

Exit code: 0 при успехе, 1 при ошибке.
"""

import json
import sys
import time
import urllib.request
import urllib.error
from datetime import datetime, timezone
from pathlib import Path

CREDENTIALS_PATH = Path.home() / ".claude" / ".credentials.json"
USAGE_URL = "https://api.anthropic.com/api/oauth/usage"
BETA_HEADER = "oauth-2025-04-20"
TIMEOUT_SECONDS = 10


def eprint(*args):
    print(*args, file=sys.stderr)


def read_access_token():
    """Читает accessToken из ~/.claude/.credentials.json."""
    if not CREDENTIALS_PATH.exists():
        raise FileNotFoundError(f"Не найден файл: {CREDENTIALS_PATH}")
    with open(CREDENTIALS_PATH, "r", encoding="utf-8") as f:
        data = json.load(f)
    token = data.get("claudeAiOauth", {}).get("accessToken")
    if not token:
        raise KeyError("В credentials нет claudeAiOauth.accessToken")
    return token


def check_token_expiry():
    """Проверяет, не истёк ли accessToken. Возвращает True если валиден."""
    try:
        with open(CREDENTIALS_PATH, "r", encoding="utf-8") as f:
            data = json.load(f)
        oauth = data.get("claudeAiOauth", {})
        expires_at_ms = oauth.get("expiresAt")
        if expires_at_ms:
            expires_at = expires_at_ms / 1000.0
            if time.time() > expires_at:
                eprint("WARNING: accessToken истёк, попытка всё равно")
    except Exception:
        pass
    return True


def fetch_usage(token):
    """Выполняет GET /api/oauth/usage и возвращает разобранный JSON."""
    req = urllib.request.Request(
        USAGE_URL,
        headers={
            "Authorization": f"Bearer {token}",
            "anthropic-beta": BETA_HEADER,
            "Accept": "application/json, text/plain, */*",
            "Content-Type": "application/json",
            "User-Agent": "claude-code-usage-widget/1.0",
        },
        method="GET",
    )
    with urllib.request.urlopen(req, timeout=TIMEOUT_SECONDS) as resp:
        if resp.status != 200:
            raise RuntimeError(f"HTTP {resp.status}")
        return json.loads(resp.read().decode("utf-8"))


def parse_response(raw):
    """Преобразует сырой ответ API в компактный формат для виджета."""
    result = {
        "ok": True,
        "plan": None,
        "five_hour": None,
        "seven_day": None,
        "limits": [],
    }

    # plan из credentials
    try:
        with open(CREDENTIALS_PATH, "r", encoding="utf-8") as f:
            creds = json.load(f)
        result["plan"] = creds.get("claudeAiOauth", {}).get("subscriptionType")
    except Exception:
        pass

    # five_hour
    fh = raw.get("five_hour")
    if isinstance(fh, dict):
        result["five_hour"] = {
            "utilization": fh.get("utilization"),
            "resets_at": fh.get("resets_at"),
        }

    # seven_day
    sd = raw.get("seven_day")
    if isinstance(sd, dict):
        result["seven_day"] = {
            "utilization": sd.get("utilization"),
            "resets_at": sd.get("resets_at"),
        }

    # limits (массив)
    for lim in raw.get("limits", []):
        if isinstance(lim, dict):
            result["limits"].append({
                "kind": lim.get("kind"),
                "group": lim.get("group"),
                "percent": lim.get("percent"),
                "severity": lim.get("severity"),
                "resets_at": lim.get("resets_at"),
                "is_active": lim.get("is_active"),
            })

    return result


def main():
    try:
        token = read_access_token()
        check_token_expiry()
        raw = fetch_usage(token)
        result = parse_response(raw)
        json.dump(result, sys.stdout, ensure_ascii=False)
        print()
        sys.exit(0)
    except FileNotFoundError as e:
        eprint(str(e))
        json.dump({"ok": False, "error": str(e)}, sys.stdout, ensure_ascii=False)
        print()
        sys.exit(1)
    except KeyError as e:
        eprint(str(e))
        json.dump({"ok": False, "error": f"Ключ не найден: {e}"}, sys.stdout, ensure_ascii=False)
        print()
        sys.exit(1)
    except urllib.error.HTTPError as e:
        body = ""
        try:
            body = e.read().decode("utf-8", errors="replace")[:200]
        except Exception:
            pass
        eprint(f"HTTP {e.code}: {body}")
        json.dump({"ok": False, "error": f"HTTP {e.code}"}, sys.stdout, ensure_ascii=False)
        print()
        sys.exit(1)
    except urllib.error.URLError as e:
        eprint(f"Network error: {e.reason}")
        json.dump({"ok": False, "error": f"Сеть: {e.reason}"}, sys.stdout, ensure_ascii=False)
        print()
        sys.exit(1)
    except Exception as e:
        eprint(f"Unexpected: {e}")
        json.dump({"ok": False, "error": str(e)}, sys.stdout, ensure_ascii=False)
        print()
        sys.exit(1)


if __name__ == "__main__":
    main()
