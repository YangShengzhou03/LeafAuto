import sys

from PyQt6 import QtWidgets, QtCore
from PyQt6.QtWidgets import QApplication

from MainWindow import MainWindow

"""
pyinstaller Application.spec
"""


def main():
    app = QtWidgets.QApplication(sys.argv)
    shared_memory = QtCore.QSharedMemory("LeafAuto_Server")
    if shared_memory.attach():
        sys.exit()

    if not shared_memory.create(1):
        sys.exit()

    window = MainWindow()
    window.setWindowTitle("枫叶信息自动化")
    window.move(100, 50)
    window.show()
    start_application()
    sys.exit(app.exec())


def start_application():
    try:
        app = QApplication(sys.argv)
        sys.exit(app.exec())
    except SystemExit:
        raise
    except Exception:
        sys.exit()


if __name__ == '__main__':
    main()
