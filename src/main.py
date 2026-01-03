import sys
import os
import warnings

from PyQt6.QtWidgets import QApplication

from ui import MainWindow
from utils import (
    STYLESHEET_PATH,
)

# Silence protobuf deprecation
warnings.filterwarnings(
    "ignore",
    message="SymbolDatabase.GetPrototype\\(\\) is deprecated"
)

def load_styles(app : QApplication):
    try:
        with open(STYLESHEET_PATH, "r") as f:
            app.setStyleSheet(f.read())
        print(f"INFO: Successfully loaded styles from {STYLESHEET_PATH}")

    except FileNotFoundError:
        print(f"Warning: styles at {STYLESHEET_PATH} not found. Running without theme.")

    except Exception as e:
        print(f"Warning: failed to load styles due to an unexpected error: {e}")

def main():
    app = QApplication([])
    load_styles(app)
    
    window = MainWindow()
    window.show()
    sys.exit(app.exec())

if __name__ == "__main__":
    main()
