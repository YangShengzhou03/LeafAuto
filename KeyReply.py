import json
from PyQt6 import QtCore, QtWidgets
from PyQt6.QtWidgets import QFileDialog
from UI_Reply import Ui_ReplyDialog
from common import log


class ReplyDialog(QtWidgets.QDialog):
    def __init__(self, parent=None):
        super().__init__(parent)
        self.ui = Ui_ReplyDialog()
        self.ui.setupUi(self)
        self.setWindowTitle("编辑Ai接管规则")
        self.setWindowFlags(QtCore.Qt.WindowType.FramelessWindowHint)
        self.setAttribute(QtCore.Qt.WidgetAttribute.WA_TranslucentBackground)
        self.ui.pushButton_download.clicked.connect(self.saveRulesToJsonAndClose)
        self.ui.file_pushButton.clicked.connect(lambda: self.choose_file_path(self.ui.Reply_lineEdit))
        self.ui.file_pushButton_2.clicked.connect(lambda: self.choose_file_path(self.ui.Reply_lineEdit_2))
        self.ui.file_pushButton_3.clicked.connect(lambda: self.choose_file_path(self.ui.Reply_lineEdit_3))
        self.ui.file_pushButton_4.clicked.connect(lambda: self.choose_file_path(self.ui.Reply_lineEdit_4))
        self.ui.file_pushButton_5.clicked.connect(lambda: self.choose_file_path(self.ui.Reply_lineEdit_5))

    def saveRulesToJson(self):
        rules = []

        def get_rule(rule_name_le, match_type_cb, keyword_le, reply_widget):
            rule_name = rule_name_le.text().strip()
            match_type = match_type_cb.currentText().strip()
            keyword = keyword_le.text().strip()
            reply_content = reply_widget.toPlainText().strip() if isinstance(reply_widget,
                                                                             QtWidgets.QTextEdit) else reply_widget.text().strip()

            if not rule_name or not match_type or not keyword or not reply_content:
                return None

            return {
                "rule_name": rule_name,
                "match_type": match_type,
                "keyword": keyword,
                "reply_content": reply_content
            }

        rules.append(get_rule(self.ui.RuleName_lineEdit, self.ui.KeyWord_comboBox, self.ui.KeyWord_lineEdit,
                              self.ui.Reply_lineEdit))
        rules.append(get_rule(self.ui.RuleName_lineEdit_2, self.ui.KeyWord_comboBox_2, self.ui.KeyWord_lineEdit_2,
                              self.ui.Reply_lineEdit_2))
        rules.append(get_rule(self.ui.RuleName_lineEdit_3, self.ui.KeyWord_comboBox_3, self.ui.KeyWord_lineEdit_3,
                              self.ui.Reply_lineEdit_3))
        rules.append(get_rule(self.ui.RuleName_lineEdit_4, self.ui.KeyWord_comboBox_4, self.ui.KeyWord_lineEdit_4,
                              self.ui.Reply_lineEdit_4))
        rules.append(get_rule(self.ui.RuleName_lineEdit_5, self.ui.KeyWord_comboBox_5, self.ui.KeyWord_lineEdit_5,
                              self.ui.Reply_lineEdit_5))

        valid_rules = [rule for rule in rules if rule is not None]

        try:
            with open('_internal/rules.json', 'w', encoding='utf-8') as f:
                json.dump(valid_rules, f, ensure_ascii=False, indent=4)
        except Exception:
            log('ERROR', '规则保存失败,可能是非管理员身份运行')

    def saveRulesToJsonAndClose(self):
        self.saveRulesToJson()
        self.close()

    def choose_file_path(self, line_edit):
        file_dialog = QFileDialog()
        file_path, _ = file_dialog.getOpenFileName(self, "选择文件", "", "All Files (*)")
        if file_path:
            line_edit.setText(file_path)
