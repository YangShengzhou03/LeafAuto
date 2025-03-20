from PyQt6 import QtWidgets, QtCore, QtGui

from Thread import AiWorkerThread
from common import log, get_resource_path


class AiAssistant(QtWidgets.QWidget):
    def __init__(self, wx, membership, parent=None):
        super().__init__(parent)
        self.parent = parent
        self.wx = wx
        self.Membership = membership
        self.ai_thread = None
        self.is_taking_over = False
        self.timer = QtCore.QTimer(self)
        self.timer.timeout.connect(self.update_timer)
        self.elapsed_time = 0

    def updateAiEditStatus(self):
        is_checked = self.parent.Global_takeover.isChecked()
        if is_checked:
            self.parent.takeOverReceiver_lineEdit.setText("全局Ai接管")
            self.parent.takeOverReceiver_lineEdit.setEnabled(False)
        else:
            self.parent.takeOverReceiver_lineEdit.setText("")
            self.parent.takeOverReceiver_lineEdit.setEnabled(True)

    def start_takeover(self):
        if self.is_taking_over:
            if self.ai_thread is not None:
                assert isinstance(self.ai_thread, AiWorkerThread)
                self.ai_thread.requestInterruption()
                self.ai_thread = None
            self.is_taking_over = False
            self.timer.stop()

        else:
            try:
                if not self.parent.takeOverReceiver_lineEdit.text():
                    QtWidgets.QMessageBox.warning(self, "接管联系人为空", "接管联系人为空，请先输入联系人")
                    return

                self.is_taking_over = True
                self.elapsed_time = 0
                self.ai_thread = AiWorkerThread(self, self.parent.takeOverReceiver_lineEdit.text(),
                                                model=self.parent.comboBox_AiLmodel.currentText(),
                                                role=self.parent.Characters_lineEdit.text())
                self.ai_thread.finished.connect(self.on_thread_finished)
                self.ai_thread.start()
                self.timer.start(1000)
                log("DEBUG", "Leaf Ai 接管启动")
                self.update_button_icon('resources/img/page3/page3_停止接管.svg')
                self.parent.label_7.setText(self.parent.label_7.text().replace('Leaf Ai接管 准备就绪', 'Leaf Ai 已为您接管'))
            except Exception as e:
                QtWidgets.QMessageBox.critical(self, "接管错误", f"接管开始时发生了一个错误{str(e)}")

    def on_thread_finished(self):
        log("INFO", "Leaf Ai 接管线程结束")
        self.is_taking_over = False
        self.timer.stop()
        self.update_button_icon('resources/img/page3/page3_开始接管.svg')
        self.parent.label_7.setText(self.parent.label_7.text().replace('Leaf Ai 已为您接管', 'Leaf Ai接管 准备就绪'))

    def update_timer(self):
        if self.is_taking_over:
            self.elapsed_time += 1
            minutes, seconds = divmod(self.elapsed_time, 60)
            hours, minutes = divmod(minutes, 60)
            time_str = f"{hours:02}:{minutes:02}:{seconds:02}"
            html = f"<html><head/><body><p align=\"center\"><span style=\" font-size:72pt;\">{time_str}</span></p></body></html>"
            self.parent.takeOverTime_label.setText(html)

            if self.Membership == 'Free':
                max_time = 60  # 1分钟
            elif self.Membership == 'Base':
                max_time = 60  # 1分钟
            elif self.Membership == 'AiVIP':
                max_time = 1800  # 30分钟
            else:
                max_time = float('inf')  # 不限时

            if self.elapsed_time >= max_time:
                self.is_taking_over = False
                self.timer.stop()
                if self.ai_thread is not None:
                    self.ai_thread.requestInterruption()
                    self.ai_thread = None
                self.update_button_icon('resources/img/page3/page3_开始接管.svg')
                self.parent.label_7.setText(self.parent.label_7.text().replace('Leaf Ai 已为您接管', 'Leaf Ai接管 准备就绪'))
                QtWidgets.QMessageBox.warning(self, "版本限制", "版本限制,接管终止,超级会员尊享无限接管")
        else:
            minutes, seconds = divmod(self.elapsed_time, 60)
            hours, minutes = divmod(minutes, 60)
            time_str = f"{hours:02}:{minutes:02}:{seconds:02}"
            html = f"<html><head/><body><p align=\"center\"><span style=\" font-size:88pt;\">{time_str}</span></p></body></html>"
            self.parent.takeOverTime_label.setText(html)

    def update_button_icon(self, icon_path):
        icon = QtGui.QIcon()
        icon.addPixmap(QtGui.QPixmap(get_resource_path(icon_path)), QtGui.QIcon.Mode.Normal, QtGui.QIcon.State.Off)
        self.parent.pushButton_takeover.setIcon(icon)
        self.parent.pushButton_takeover.setIconSize(QtCore.QSize(38, 38))
