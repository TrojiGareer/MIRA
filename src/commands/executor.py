import pyautogui
import platform

pyautogui.FAILSAFE = False
pyautogui.PAUSE = 0

class Executor:
    def __init__(self):
        self.screen_w, self.screen_h = pyautogui.size()
        self.os_name = platform.system()

    def move_mouse(self, x_ratio: float, y_ratio: float):
        """Moves mouse to x,y coordinates (0.0 to 1.0)"""
        screen_x = max(0, min(int(x_ratio * self.screen_w), self.screen_w - 1))
        screen_y = max(0, min(int(y_ratio * self.screen_h), self.screen_h - 1))
        pyautogui.moveTo(screen_x, screen_y)

    def left_click(self):
        pyautogui.click(button='left')

    def right_click(self):
        pyautogui.click(button='right')

    def start_drag(self):
        pyautogui.mouseDown(button='left')

    def stop_drag(self):
        pyautogui.mouseUp(button='left')

    def scroll(self, distance):
        """
        Scrolls the page.
        distance: positive for UP, negative for DOWN
        """
        scroll_amount = int(distance * 500) 
        pyautogui.scroll(scroll_amount)

    def change_volume(self, direction: str):
        if direction == 'up':
            pyautogui.press('volumeup')
        elif direction == 'down':
            pyautogui.press('volumedown')

    def switch_window(self):
        """
        Opens Windows Task View (Win + Tab).
        This allows the user to see ALL windows and select one with the mouse gesture.
        """
        pyautogui.hotkey('win', 'tab')