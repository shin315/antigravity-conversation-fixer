"""Entry point for Antigravity Fixer — TUI (Rich terminal UI)."""

import argparse
import sys

from src.i18n import set_lang
from src.tui.app import run


def main():
    parser = argparse.ArgumentParser(
        description="Antigravity Fixer — Terminal UI"
    )
    parser.add_argument(
        "--lang",
        choices=["vi", "en"],
        default="vi",
        help="Language: vi (Vietnamese, default) or en (English)",
    )
    args = parser.parse_args()

    set_lang(args.lang)
    run()


if __name__ == "__main__":
    main()
