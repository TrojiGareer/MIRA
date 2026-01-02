from PyQt6.QtWidgets import QWidget
from .auto_control_panel_widget import Ui_widgetControlPanel

class ControlPanelWidget(QWidget, Ui_widgetControlPanel):
    def __init__(self, parent=None):
        super().__init__(parent)
        self.setupUi(self)
