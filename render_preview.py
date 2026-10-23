import sys, os
from PyQt6.QtWidgets import QApplication
from PyQt6.QtCore import QTimer
import ui

app = QApplication.instance() or QApplication(sys.argv)
win = ui.MainWindow(face_path="")
win.resize(1280, 720)
win.show()

# Let it process events and paint
for _ in range(15):
    app.processEvents()

pixmap = win.grab()
out_path = r"C:\Users\ahmad\Desktop\Mark-LIV-main\ui_preview.png"
pixmap.save(out_path)
print("Saved preview to:", out_path)
win.close()
