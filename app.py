"""Application entry point for Preflight."""

from gui.main_window import PreflightApp


def main() -> None:
    app = PreflightApp()
    app.mainloop()


if __name__ == "__main__":
    main()

