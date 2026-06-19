import sys 
from PySide6.QtWidgets import QApplication, QLabel 
if __name__ == "__main__": 
    app = QApplication(sys.argv) 
    w = QLabel("Hello from frozen EXE!") 
    w.show() 
    sys.exit(app.exec()) 
