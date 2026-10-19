#!/usr/bin/env python3
import argparse
import os
import subprocess
import sys
from pathlib import Path

import telebot
from dotenv import load_dotenv


ROOT = Path(__file__).resolve().parent
TELEGRAM_MESSAGE_LIMIT = 4096
load_dotenv(ROOT / ".env")


def configuration() -> tuple[str, set[int], int, int]:
    token = os.getenv("TELEGRAM_API_TOKEN")
    if not token:
        raise RuntimeError("TELEGRAM_API_TOKEN is required in .env")

    raw_ids = os.getenv("TELEGRAM_ALLOWED_USER_IDS", "")
    if not raw_ids.strip():
        raise RuntimeError("TELEGRAM_ALLOWED_USER_IDS must contain at least one Telegram user ID")
    try:
        allowed_ids = {int(value.strip()) for value in raw_ids.split(",") if value.strip()}
    except ValueError as error:
        raise RuntimeError("TELEGRAM_ALLOWED_USER_IDS must be comma-separated integers") from error
    if not allowed_ids:
        raise RuntimeError("TELEGRAM_ALLOWED_USER_IDS must contain at least one Telegram user ID")

    try:
        timeout = int(os.getenv("CLAUDE_TIMEOUT_SECONDS", "120"))
        max_length = int(os.getenv("MAX_MESSAGE_LENGTH", "4000"))
    except ValueError as error:
        raise RuntimeError("CLAUDE_TIMEOUT_SECONDS and MAX_MESSAGE_LENGTH must be integers") from error
    if timeout <= 0 or max_length <= 0:
        raise RuntimeError("CLAUDE_TIMEOUT_SECONDS and MAX_MESSAGE_LENGTH must be positive")
    return token, allowed_ids, timeout, max_length


def run_claude(prompt: str, timeout: int) -> str:
    try:
        result = subprocess.run(
            ["claude", "-p", "--no-session-persistence", prompt],
            cwd=ROOT,
            capture_output=True,
            text=True,
            timeout=timeout,
            check=False,
        )
    except FileNotFoundError:
        raise RuntimeError("Claude CLI was not found on PATH")
    except subprocess.TimeoutExpired:
        raise RuntimeError(f"Claude timed out after {timeout} seconds")
    if result.returncode != 0:
        detail = (result.stderr or result.stdout).strip()
        raise RuntimeError(f"Claude exited with code {result.returncode}: {detail[-1000:]}")
    return result.stdout.strip() or "בוצע (ללא פלט חזרה)."


def send_response(bot: telebot.TeleBot, chat_id: int, response: str) -> None:
    for start in range(0, len(response), TELEGRAM_MESSAGE_LIMIT):
        bot.send_message(chat_id, response[start:start + TELEGRAM_MESSAGE_LIMIT])


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--validate-config", action="store_true")
    args = parser.parse_args()
    try:
        token, allowed_ids, timeout, max_length = configuration()
    except RuntimeError as error:
        print(f"Configuration error: {error}", file=sys.stderr)
        return 2
    if args.validate_config:
        print("Telegram bridge configuration is valid.")
        return 0

    bot = telebot.TeleBot(token)

    @bot.message_handler(func=lambda message: True)
    def handle_message(message: telebot.types.Message) -> None:
        user_id = message.from_user.id if message.from_user else None
        if user_id not in allowed_ids:
            bot.reply_to(message, "Unauthorized.")
            return
        if len(message.text or "") > max_length:
            bot.reply_to(message, f"Message exceeds the {max_length}-character limit.")
            return
        bot.reply_to(message, "חושב...")
        try:
            response = run_claude(message.text or "", timeout)
        except RuntimeError as error:
            bot.send_message(message.chat.id, f"שגיאה מול קלוד:\n{error}")
            return
        send_response(bot, message.chat.id, response)

    bot.infinity_polling(skip_pending=True)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
