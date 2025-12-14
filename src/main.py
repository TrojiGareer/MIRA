import sys
import os
from PyQt6.QtWidgets import QApplication
from ui import MainWindow

def load_styles(app : QApplication):
    BASE_DIR = os.path.dirname(os.path.abspath(__file__))
    CSS_PATH = os.path.join(BASE_DIR, 'ui', 'style.css')

    try:
        with open(CSS_PATH, "r") as f:
            app.setStyleSheet(f.read())
        print(f"INFO: Successfully loaded styles from {CSS_PATH}")

    except FileNotFoundError:
        print(f"Warning: styles at {CSS_PATH} not found. Running without theme.")

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
