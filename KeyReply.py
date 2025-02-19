import json
from PyQt6 import QtCore, QtWidgets, QtGui
from PyQt6.QtWidgets import QFileDialog
from UI_Reply import Ui_ReplyDialog
from common import log, get_resource_path


class ReplyDialog(QtWidgets.QDialog):
    def __init__(self, parent=None):
        super().__init__(parent)
        self.ui = Ui_ReplyDialog()
        self.ui.setupUi(self)
        self.setWindowTitle("编辑Ai接管规则")
        self.setWindowIcon(QtGui.QIcon(get_resource_path('resources/img/tray.ico')))
        self.setWindowFlags(QtCore.Qt.WindowType.FramelessWindowHint)
        self.setAttribute(QtCore.Qt.WidgetAttribute.WA_TranslucentBackground)

        self.ui.pushButton_download.clicked.connect(self.saveRulesToJsonAndClose)
        self.ui.file_pushButton_1.clicked.connect(lambda: self.choose_file_path(self.ui.Reply_lineEdit_1))
        self.ui.file_pushButton_2.clicked.connect(lambda: self.choose_file_path(self.ui.Reply_lineEdit_2))
        self.ui.file_pushButton_3.clicked.connect(lambda: self.choose_file_path(self.ui.Reply_lineEdit_3))

        self.ui.pushButton_1.clicked.connect(lambda: self.clear_fields(1))
        self.ui.pushButton_2.clicked.connect(lambda: self.clear_fields(2))
        self.ui.pushButton_3.clicked.connect(lambda: self.clear_fields(3))

        self.load_rules_from_json()

    def load_rules_from_json(self):
        try:
            with open('_internal/rules.json', 'r', encoding='utf-8') as f:
                rules = json.load(f)
                self.fill_ui_with_rules(rules)
        except FileNotFoundError:
            pass
        except Exception as e:
            log('ERROR', f'加载规则失败: {str(e)}')

    def fill_ui_with_rules(self, rules):
        for i in range(1, 4):
            rule_name_le = getattr(self.ui, f'RuleName_lineEdit_{i}', None)
            match_type_cb = getattr(self.ui, f'KeyWord_comboBox_{i}', None)
            keyword_le = getattr(self.ui, f'KeyWord_lineEdit_{i}', None)
            reply_widget = getattr(self.ui, f'Reply_lineEdit_{i}', None)

            if i <= len(rules) and all([rule_name_le, match_type_cb, keyword_le, reply_widget]):
                rule = rules[i - 1]
                rule_name_le.setText(rule.get('rule_name', ''))
                match_type_cb.setCurrentText(rule.get('match_type', ''))
                keyword_le.setText(rule.get('keyword', ''))
                reply_widget.setText(rule.get('reply_content', ''))
            else:
                if all([rule_name_le, match_type_cb, keyword_le, reply_widget]):
                    rule_name_le.clear()
                    match_type_cb.setCurrentIndex(0)
                    keyword_le.clear()
                    reply_widget.clear()

    def saveRulesToJson(self):
        rules = []

        def get_rule(index):
            rule_name_le = getattr(self.ui, f'RuleName_lineEdit_{index}', None)
            match_type_cb = getattr(self.ui, f'KeyWord_comboBox_{index}', None)
            keyword_le = getattr(self.ui, f'KeyWord_lineEdit_{index}', None)
            reply_widget = getattr(self.ui, f'Reply_lineEdit_{index}', None)

            if all([rule_name_le, match_type_cb, keyword_le, reply_widget]):
                rule_name = rule_name_le.text().strip()
                match_type = match_type_cb.currentText().strip()
                keyword = keyword_le.text().strip()
                reply_content = reply_widget.toPlainText().strip() if isinstance(reply_widget,
                                                                                 QtWidgets.QTextEdit) else reply_widget.text().strip()
                if rule_name and match_type and keyword and reply_content:
                    return {"rule_name": rule_name, "match_type": match_type, "keyword": keyword,
                            "reply_content": reply_content}
            return None

        rules.extend(filter(None, [get_rule(i) for i in range(1, 4)]))

        try:
            with open('_internal/rules.json', 'w', encoding='utf-8') as f:
                json.dump(rules, f, ensure_ascii=False, indent=4)
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

    def clear_fields(self, index):
        rule_name_le = getattr(self.ui, f'RuleName_lineEdit_{index}', None)
        match_type_cb = getattr(self.ui, f'KeyWord_comboBox_{index}', None)
        keyword_le = getattr(self.ui, f'KeyWord_lineEdit_{index}', None)
        reply_widget = getattr(self.ui, f'Reply_lineEdit_{index}', None)

        if all([rule_name_le, match_type_cb, keyword_le, reply_widget]):
            rule_name_le.clear()
            match_type_cb.setCurrentIndex(0)
            keyword_le.clear()
            reply_widget.clear()