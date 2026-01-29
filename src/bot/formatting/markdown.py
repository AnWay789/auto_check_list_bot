"""Утилиты форматирования сообщений Telegram."""

from __future__ import annotations


def escape_markdown(text: str) -> str:
    """Экранирует специальные символы Markdown (parse_mode='Markdown')."""
    special_chars = [
        "*",
        "_",
        "[",
        "]",
        "(",
        ")",
        "~",
        "`",
        ">",
        "#",
        "+",
        "-",
        "=",
        "|",
        "{",
        "}",
        ".",
        "!",
    ]
    for ch in special_chars:
        text = text.replace(ch, f"\\{ch}")
    return text

