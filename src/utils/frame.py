import cv2
import numpy as np
from PyQt6.QtGui import QImage, QPixmap

def convert_cv_to_pixmap(frame: np.ndarray) -> QPixmap:
        """
        Converts an openCV frame (bgr) to a QPixmap(rgb) for better performance with the GUI

        :param frame: the frame to convert, in openCV format (bgr)

        :return QPixmap: the converted frame in QPixmap format
        """

        frame_rgb = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
        h, w, ch = frame_rgb.shape
        q_img = QImage(frame_rgb.data, w, h, ch * w, QImage.Format.Format_RGB888)
        
        return QPixmap.fromImage(q_img)