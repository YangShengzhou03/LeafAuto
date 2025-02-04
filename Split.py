import re

from PyQt6 import QtWidgets

from Thread import SplitWorkerThread
from common import log


class Split(QtWidgets.QWidget):
    def __init__(self, wx, membership, parent=None):
        super().__init__(parent)
        self.parent = parent
        self.wx = wx
        self.Membership = membership
        self.prepared_sentences = []
        self.is_sending = False
        self.split_thread = None

    def on_start_split_clicked(self):
        if not any([
            self.parent.checkBox_Ai.isChecked(),
            self.parent.checkBox_period.isChecked(),
            self.parent.checkBox_comma.isChecked(),
            self.parent.checkBox_Space.isChecked()
        ]):
            log("WARNING", "请至少选择一种拆句规则,作为句子分隔符")
            return

        message = self.parent.textEdit_2.toPlainText().strip()
        delimiters = []

        if self.parent.checkBox_comma.isChecked():
            delimiters.extend(['，', ','])
        if self.parent.checkBox_Space.isChecked():
            delimiters.append(' ')
        if self.parent.checkBox_period.isChecked():
            delimiters.extend(['。', '.'])
        if self.parent.checkBox_Ai.isChecked():
            smart_delimiters = [
                '。', '.', '？', '?', '！', '!', '，', ',', '；', ';', '：', ':',
                '（', '）', '【', '】', '［', '］', '【', '】', '〈', '〉', '《', '》', '『', '』',
                '、', '，', '。', '！', '？', '；', '：', '——', '…', '……', '-',
                '·', '—', '“', '”', '‘', '’', '`', '\'', '"', '"',
                ' ', '/', '｜', '│',
                '+', '-', '*', '/', '%', '=', '#', '@', '&', '^', '_', '~', '\\', '|',
                '[', ']', '{', '}', '<', '>',
            ]
            delimiters.extend(smart_delimiters)

        self.prepared_sentences = self.split_message(message, delimiters)

    def on_start_send_clicked(self):
        if self.is_sending:
            self.is_sending = False
            self.parent.pushButton_startSplit.setText("发送句子")
            if self.split_thread is not None:
                self.split_thread.requestInterruption()
                self.split_thread = None
        else:
            receiver = self.parent.SplitReceiver_lineEdit.text().strip()
            sentences = self.prepared_sentences

            if not receiver:
                log("WARNING", "句子接收者为空,请输入有效的接收者")
                return

            self.is_sending = True

            self.parent.pushButton_startSplit.setText("停止发送")

            self.split_thread = SplitWorkerThread(self, receiver, sentences)
            self.split_thread.finished.connect(self.on_thread_finished)
            self.split_thread.start()

    def on_thread_finished(self):
        log("DEBUG", "段落拆句发送任务执行完成")
        self.is_sending = False
        self.parent.pushButton_startSplit.setText("发送句子")

    def split_message(self, message, delimiters):
        delimiter_pattern = '|'.join(map(re.escape, delimiters))
        sentences = re.split(delimiter_pattern, message)
        return [s.strip() for s in sentences if s.strip()]