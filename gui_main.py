"""Entry point for Antigravity Fixer — GUI (CustomTkinter desktop app)."""

from src.i18n import set_lang
from src.gui.app import AntigravityFixerApp


def main():
    set_lang("vi")
    app = AntigravityFixerApp()
    app.mainloop()


if __name__ == "__main__":
    main()
