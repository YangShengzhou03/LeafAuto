import sys

from PyQt6 import QtWidgets, QtNetwork

from MainWindow import MainWindow

"""
pyinstaller Application.spec
"""


def bring_existing_to_front():
    socket = QtNetwork.QLocalSocket()
    socket.connectToServer("LeafAuto_Server")
    if socket.waitForConnected(500):
        socket.write(b'bringToFront')
        socket.waitForBytesWritten(1000)
        socket.disconnectFromServer()


def main():
    app = QtWidgets.QApplication(sys.argv)

    local_server = QtNetwork.QLocalServer()
    if not local_server.listen("LeafAuto_Server"):
        bring_existing_to_front()
        return

    def new_connection():
        socket = local_server.nextPendingConnection()
        if socket.waitForReadyRead(1000):
            if socket.readAll().data() == b'bringToFront':
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
