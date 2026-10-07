"""AKM-DOS graphical boot entry point; Shell remains in main.py."""
from pathlib import Path


def main():
    try:
        from akm.gui.app import run
    except ModuleNotFoundError as exc:
        if exc.name and exc.name.startswith('PySide6'):
            print('Grafiksel başlangıç için PySide6 gerekli. pip install -r requirements-gui.txt')
            return 1
        raise
    return run(Path(__file__).resolve().parent)


if __name__ == '__main__':
    raise SystemExit(main())
