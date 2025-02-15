import sys

from PyQt6 import QtWidgets, QtCore
from PyQt6.QtNetwork import QLocalServer, QLocalSocket

from MainWindow import MainWindow

"""
pyinstaller Application.spec
"""


# TODO 拆段发送的文本框夜间模式为全白

def bring_existing_to_front():
    socket = QLocalSocket()
    socket.connectToServer("LeafAuto_Server")
    if socket.waitForConnected(500):
        socket.write(b'bringToFront')
        socket.waitForBytesWritten(1000)
        socket.disconnectFromServer()
        socket.waitForDisconnected(1000)


def main():
    app = QtWidgets.QApplication(sys.argv)
    shared_memory = QtCore.QSharedMemory("LeafAuto_SharedMemory")

    if shared_memory.attach():
        bring_existing_to_front()
        sys.exit(0)

    if not shared_memory.create(1):
        sys.exit(1)

    local_server = QLocalServer()
    if local_server.listen("LeafAuto_Server"):
        def new_connection():
            socket = local_server.nextPendingConnection()
            if socket.waitForReadyRead(1000):
                data = socket.readAll().data()
                if data == b'bringToFront':
                    window.activateWindow()
                    window.raise_()
                    window.showNormal()

        local_server.newConnection.connect(new_connection)

    window = MainWindow()
    window.move(100, 50)
    window.show()
    sys.exit(app.exec())


if __name__ == '__main__':
    main()
