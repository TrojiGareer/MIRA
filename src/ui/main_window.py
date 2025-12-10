from PyQt6.QtWidgets import QMainWindow
from PyQt6.uic.load_ui import loadUiType
import os

BASE_DIR = os.path.dirname(os.path.abspath(__file__))
UI_PATH = os.path.join(BASE_DIR, 'main_window.ui')

# The UI is dynamically loaded
try:
    Ui_MainWindow, QtBaseClass = loadUiType(UI_PATH)
except FileNotFoundError:
    print(f"ERROR: UI file not found at {UI_PATH}. Check path and file name.")

    # Use generic QMainWindow if UI file is missing to prevent crash
    class Ui_MainWindow:
        def setupUi(self, MainWindow): pass
    QtBaseClass = QMainWindow


"""
The main application window, inheriting structure from the UI file.
The LSP can identify the two superclasses of MainWindow as nonexisting but they are created at runtime
"""
class MainWindow(QtBaseClass, Ui_MainWindow):
    def __init__(self):
        super().__init__()
        
        # Use the loaded UI file
        self.setupUi(self)
        
        self.setWindowTitle("M.I.R.A. – Motion Interpretation Remote Assistant")
        
        self._initialize_components()

    """
    Initializes custom logic and connects the UI to the backend(camera, model, etc.)
    """
    def _initialize_components(self):
        # All widgets defined in the .ui file are now attributes of self due to self.setupUi(self)
        # Widgets' names, custom properties are gotten from the .ui files for connecting
        
        print("INFO: UI structure loaded from Qt Designer.")
