import json
from PyQt6 import QtCore, QtWidgets, QtGui
from UI_Reply import Ui_ReplyDialog
from common import get_resource_path


class ReplyDialog(QtWidgets.QDialog):
    def __init__(self, parent=None):
        super().__init__(parent)
        self.ui = Ui_ReplyDialog()
        self.ui.setupUi(self)
        self.setWindowTitle("编辑Ai接管规则")
        self.setWindowIcon(QtGui.QIcon(get_resource_path('resources/img/tray.ico')))
        self.setWindowFlags(QtCore.Qt.WindowType.FramelessWindowHint)
        self.setAttribute(QtCore.Qt.WidgetAttribute.WA_TranslucentBackground)
        self.ui.pushButton_save.clicked.connect(self.saveRulesToJsonAndClose)
        self.ui.pushButton_add.clicked.connect(self.add_rule)
        self.ui.file_pushButton.clicked.connect(self.open_file)
        self.ui.pushButton_cancel.clicked.connect(self.close)
        self.rules = []
        self.loadRulesFromJson()
        self.displayRules()

    def open_file(self):
        file_path, _ = QtWidgets.QFileDialog.getOpenFileName(self, "选择文件", "", "All Files (*)")
        if file_path:
            self.ui.Reply_lineEdit.setText(file_path)

    def loadRulesFromJson(self):
        try:
            with open(get_resource_path('_internal/AutoReply_Rules.json'), 'r', encoding='utf-8') as file:
                self.rules = json.load(file)
        except FileNotFoundError:
            self.rules = []

    def saveRulesToJson(self):
        try:
            rules = []
            for i in range(self.ui.formLayout.count()):
                widget_item = self.ui.formLayout.itemAt(i).widget()
                if widget_item is not None and isinstance(widget_item, QtWidgets.QWidget):
                    rule_name = widget_item.findChild(QtWidgets.QLabel, "label_Name").text()
                    match_type = widget_item.findChild(QtWidgets.QLabel, "label_Rule").text()
                    keyword = widget_item.findChild(QtWidgets.QLabel, "label_KeyWord").text()
                    reply_content = widget_item.findChild(QtWidgets.QLabel, "label_Reply").text()
                    rules.append({
                        "rule_name": rule_name,
                        "match_type": match_type,
                        "keyword": keyword,
                        "reply_content": reply_content
                    })
            with open('_internal/AutoReply_Rules.json', 'w', encoding='utf-8') as file:
                json.dump(rules, file, ensure_ascii=False, indent=4)
        except Exception as e:
            QtWidgets.QMessageBox.critical(self, "保存失败", f"保存出错，{e}")

    def saveRulesToJsonAndClose(self):
        self.saveRulesToJson()
        self.close()

    def create_frame(self, rule_name, match_type, keyword, reply_content):
        RuleWidget_Item = QtWidgets.QWidget(parent=self.ui.scrollAreaWidgetContents)
        RuleWidget_Item.setMinimumSize(QtCore.QSize(760, 36))
        RuleWidget_Item.setMaximumSize(QtCore.QSize(760, 36))
        RuleWidget_Item.setStyleSheet("border-radius: 9px;\nbackground:rgba(255, 255, 255, 160);")
        RuleWidget_Item.setObjectName("RuleWidget_Item")

        horizontalLayout_18 = QtWidgets.QHBoxLayout(RuleWidget_Item)
        horizontalLayout_18.setContentsMargins(9, 4, 9, 4)
        horizontalLayout_18.setSpacing(6)
        horizontalLayout_18.setObjectName("horizontalLayout_18")

        label_Name = QtWidgets.QLabel(rule_name, parent=RuleWidget_Item)
        label_Name.setMinimumSize(QtCore.QSize(150, 0))
        label_Name.setMaximumSize(QtCore.QSize(150, 16777215))
        font = QtGui.QFont()
        font.setFamily("微软雅黑 Light")
        font.setPointSize(12)
        label_Name.setFont(font)
        label_Name.setStyleSheet("color:rgba(105, 27, 253, 180);\nbackground:rgba(0, 0, 0, 0);")
        label_Name.setObjectName("label_Name")
        horizontalLayout_18.addWidget(label_Name)

        label_Rule = QtWidgets.QLabel(match_type, parent=RuleWidget_Item)
        label_Rule.setMinimumSize(QtCore.QSize(50, 0))
        label_Rule.setMaximumSize(QtCore.QSize(50, 16777215))
        font = QtGui.QFont()
        font.setFamily("微软雅黑 Light")
        font.setPointSize(12)
        label_Rule.setFont(font)
        label_Rule.setStyleSheet("color:rgb(255, 255, 255);\nbackground:rgba(0, 0, 0, 0);")
        label_Rule.setObjectName("label_Rule")
        horizontalLayout_18.addWidget(label_Rule)

        label_KeyWord = QtWidgets.QLabel(keyword, parent=RuleWidget_Item)
        label_KeyWord.setMinimumSize(QtCore.QSize(200, 0))
        label_KeyWord.setMaximumSize(QtCore.QSize(200, 16777215))
        font = QtGui.QFont()
        font.setFamily("微软雅黑 Light")
        font.setPointSize(12)
        label_KeyWord.setFont(font)
        label_KeyWord.setStyleSheet("color:rgba(105, 27, 253, 180);\nbackground:rgba(0, 0, 0, 0);")
        label_KeyWord.setObjectName("label_KeyWord")
        horizontalLayout_18.addWidget(label_KeyWord)

        label_21 = QtWidgets.QLabel("回复内容", parent=RuleWidget_Item)
        label_21.setMinimumSize(QtCore.QSize(64, 0))
        label_21.setMaximumSize(QtCore.QSize(64, 16777215))
        font = QtGui.QFont()
        font.setFamily("微软雅黑 Light")
        font.setPointSize(12)
        label_21.setFont(font)
        label_21.setStyleSheet("color:rgb(255, 255, 255);\nbackground:rgba(0, 0, 0, 0);")
        label_21.setObjectName("label_21")
        horizontalLayout_18.addWidget(label_21)

        label_Reply = QtWidgets.QLabel(reply_content, parent=RuleWidget_Item)
        font = QtGui.QFont()
        font.setFamily("微软雅黑 Light")
        font.setPointSize(12)
        label_Reply.setFont(font)
        label_Reply.setStyleSheet("color:rgba(105, 27, 253, 180);\nbackground:rgba(0, 0, 0, 0);")
        label_Reply.setObjectName("label_Reply")
        horizontalLayout_18.addWidget(label_Reply)

        delete_button = QtWidgets.QPushButton("删除", parent=RuleWidget_Item)
        delete_button.setStyleSheet("""
            QPushButton {
                background-color: rgba(255, 0, 0, 180);
                border: none;
                border-radius: 6px;
                color: white;
                font-size: 12px;
                padding: 2px;
                width: 42px;
                height: 24px;
                min-width: 42px;
                max-width: 42px;
                min-height: 24px;
                max-height: 24px;
                transition: background-color 0.3s ease, transform 0.1s ease;
            }
            QPushButton:hover {
                background-color: rgba(255, 0, 0, 0.9);
                transform: scale(1.05);
            }
            QPushButton:pressed {
                background-color: rgba(200, 0, 0, 1);
                transform: scale(0.95);
                box-shadow: inset 0 0 5px rgba(0, 0, 0, 0.5);
            }
        """)
        delete_button.hide()
        delete_button.clicked.connect(lambda: self.remove_rule(RuleWidget_Item))
        horizontalLayout_18.addWidget(delete_button)

        RuleWidget_Item.enterEvent = lambda event: delete_button.show()
        RuleWidget_Item.leaveEvent = lambda event: delete_button.hide()

        return RuleWidget_Item

    def add_rule(self):
        rule_name = self.ui.RuleName_lineEdit.text()
        match_type = self.ui.Rule_comboBox.currentText()
        keyword = self.ui.KeyWord_lineEdit.text()
        reply_content = self.ui.Reply_lineEdit.text()
        if rule_name == "" or keyword == "" or reply_content == "":
            QtWidgets.QMessageBox.warning(self, "输入不完整", "您尚未完成所有必填项，请确保输入完整。")
            return
        existing_rule_names = [rule['rule_name'] for rule in self.rules]
        if rule_name in existing_rule_names:
            QtWidgets.QMessageBox.warning(self, "重复的规则名称", "规则名称已存在，请使用其他名称。")
            return
        widget_item = self.create_frame(rule_name, match_type, keyword, reply_content)
        self.ui.formLayout.addRow(widget_item)
        self.rules.append({
            "rule_name": rule_name,
            "match_type": match_type,
            "keyword": keyword,
            "reply_content": reply_content
        })

    def remove_rule(self, widget_item):
        widget_item.setParent(None)
        widget_item.deleteLater()

    def displayRules(self):
        for rule in self.rules:
            widget_item = self.create_frame(
                rule['rule_name'],
                rule['match_type'],
                rule['keyword'],
                rule['reply_content']
            )
            self.ui.formLayout.addRow(widget_item)
