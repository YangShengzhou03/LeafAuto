import random
from datetime import timedelta
from PyQt6 import QtWidgets, QtCore, QtGui
from PyQt6.QtCore import QRegularExpression, QUrl
from PyQt6.QtGui import QRegularExpressionValidator, QDesktopServices

from System_info import get_motherboard_serial_number, write_key_value, read_key_value
from Ui_Activities import Ui_ActivitiesWindow
from common import get_resource_path, get_current_time, get_url


class ActivitiesWindow(QtWidgets.QMainWindow, Ui_ActivitiesWindow):
    def __init__(self):
        super().__init__()
        self.ui = Ui_ActivitiesWindow()
        self.ui.setupUi(self)
        self.setWindowTitle("激活枫叶")
        self.setWindowIcon(QtGui.QIcon(get_resource_path('resources/img/tray.ico')))
        self.setWindowFlags(
            self.windowFlags() | QtCore.Qt.WindowType.FramelessWindowHint | QtCore.Qt.WindowType.WindowStaysOnTopHint)
        self.setAttribute(QtCore.Qt.WidgetAttribute.WA_TranslucentBackground)
        self.identify = random.randint(100000, 999999)
        self.current_selected_button = None
        self.connect_signals()
        self.year_vip()

    def connect_signals(self):
        self.ui.pushButton_close.clicked.connect(self.close)
        self.ui.pushButton_year.clicked.connect(self.year_vip)
        self.ui.pushButton_VIP.clicked.connect(self.super_vip)
        self.ui.pushButton_AiVIP.clicked.connect(self.ai_vip)
        self.ui.pushButton_Base.clicked.connect(self.base_vip)
        reg_exp = QRegularExpression(r'^[A-Za-z0-9]{0,12}$')
        validator = QRegularExpressionValidator(reg_exp, self.ui.lineEdit_code)
        self.ui.lineEdit_code.setValidator(validator)
        self.ui.lineEdit_code.returnPressed.connect(self.validate_activation)
        self.ui.pushButton_OK.clicked.connect(self.validate_activation)
        self.ui.lineEdit_code.textChanged.connect(lambda text: self.ui.lineEdit_code.setText(text.upper()))
        self.ui.label_identify.setText(str(self.identify))
        self.ui.pushButton_exchange.clicked.connect(self.QQ_code)
        self.ui.pushButton_check.clicked.connect(self.QQ_code)
        self.ui.pushButton_feedback.clicked.connect(self.QQ_code)
        self.ui.pushButton_privilege.clicked.connect(self.help)
        self.apply_default_styles()

    def QQ_code(self):
        icon = QtGui.QIcon()
        icon.addPixmap(QtGui.QPixmap(get_resource_path('resources/img/activity/QQ_Act.png')), QtGui.QIcon.Mode.Normal,
                       QtGui.QIcon.State.Off)
        self.ui.pushButton_Wechat.setIcon(icon)
        self.apply_default_styles()

    def apply_default_styles(self):
        default_style = """
QPushButton {
    margin-right: 3px;
    margin-bottom: 0px;
    color: rgb(255, 255, 255);
    border: 2px solid rgba(120, 120, 120, 60);
    border-radius: 8px;
    background: none;
    font-weight: bold;
    padding: 8px;
}

QPushButton:hover {
    border: 2px solid rgba(254, 81, 111, 120);
    background: qlineargradient(
        spread:pad,
        x1:0.5, y1:1, x2:0.5, y2:0,
        stop:0 rgba(0, 0, 0, 0),
        stop:1 rgba(255, 153, 170, 88)
    );
    transition: background 0.2s ease-in-out;
}

QPushButton:pressed {
    border: 2px solid rgba(254, 81, 111, 255);
    background: qlineargradient(
        spread:pad,
        x1:0.5, y1:1, x2:0.5, y2:0,
        stop:0 rgba(0, 0, 0, 0),
        stop:1 rgba(255, 153, 170, 88)
    );
    transition: background 0.1s ease-in-out;
}
"""
        for button in [self.ui.pushButton_VIP, self.ui.pushButton_year, self.ui.pushButton_AiVIP,
                       self.ui.pushButton_Base]:
            button.setStyleSheet(default_style)

    def update_button_style(self, button):
        active_style = """
QPushButton {
    margin-right: 3px;
    margin-bottom: 0px;
    color: rgb(255, 255, 255);
    border: 2px solid rgba(254, 81, 111, 120);
    border-radius: 8px;
    background: qlineargradient(
        spread:pad,
        x1:0.5, y1:1, x2:0.5, y2:0,
        stop:0 rgba(0, 0, 0, 0),
        stop:1 rgba(255, 153, 170, 88)
    );
    font-weight: bold;
    padding: 8px;
}

QPushButton:hover {
    border: 2px solid rgba(254, 81, 111, 120);
    background: qlineargradient(
        spread:pad,
        x1:0.5, y1:1, x2:0.5, y2:0,
        stop:0 rgba(0, 0, 0, 0),
        stop:1 rgba(255, 153, 170, 88)
    );
    transition: background 0.2s ease-in-out;
}

QPushButton:pressed {
    border: 2px solid rgba(254, 81, 111, 255);
    background: qlineargradient(
        spread:pad,
        x1:0.5, y1:1, x2:0.5, y2:0,
        stop:0 rgba(0, 0, 0, 0),
        stop:1 rgba(255, 153, 170, 88)
    );
    transition: background 0.1s ease-in-out;
}
"""

        self.apply_default_styles()
        button.setStyleSheet(active_style)
        self.current_selected_button = button

    def super_vip(self):
        icon = QtGui.QIcon()
        icon.addPixmap(QtGui.QPixmap(get_resource_path('resources/img/activity/wp18.9.jpg')), QtGui.QIcon.Mode.Normal, QtGui.QIcon.State.Off)
        self.ui.pushButton_Wechat.setIcon(icon)
        self.update_button_style(self.ui.pushButton_VIP)
        self.ui.label_prices.setText("18.90")
        self.ui.label_prices_2.setText("18.9")

    def year_vip(self):
        icon = QtGui.QIcon()
        icon.addPixmap(QtGui.QPixmap(get_resource_path('resources/img/activity/wp99.jpg')), QtGui.QIcon.Mode.Normal, QtGui.QIcon.State.Off)
        self.ui.pushButton_Wechat.setIcon(icon)
        self.update_button_style(self.ui.pushButton_year)
        self.ui.label_prices.setText("99.00")
        self.ui.label_prices_2.setText("99")

    def ai_vip(self):
        icon = QtGui.QIcon()
        icon.addPixmap(QtGui.QPixmap(get_resource_path('resources/img/activity/wp17.9.jpg')), QtGui.QIcon.Mode.Normal, QtGui.QIcon.State.Off)
        self.ui.pushButton_Wechat.setIcon(icon)
        self.update_button_style(self.ui.pushButton_AiVIP)
        self.ui.label_prices.setText("17.90")
        self.ui.label_prices_2.setText("17.9")

    def base_vip(self):
        icon = QtGui.QIcon()
        icon.addPixmap(QtGui.QPixmap(get_resource_path('resources/img/activity/wp9.9.jpg')), QtGui.QIcon.Mode.Normal, QtGui.QIcon.State.Off)
        self.ui.pushButton_Wechat.setIcon(icon)
        self.update_button_style(self.ui.pushButton_Base)
        self.ui.label_prices.setText("9.90")
        self.ui.label_prices_2.setText("9.9")

    def validate_activation(self):
        try:
            Key_value, _ = get_url()
        except Exception:
            Key_value = None

        input_password = self.ui.lineEdit_code.text()
        random_number = self.identify

        hex_base = hex(random_number + 1)[2:].upper()
        hex_ai_vip = hex(random_number + 2)[2:].upper()
        hex_vip = hex(random_number + 3)[2:].upper()
        hex_year_vip = hex(random_number + 4)[2:].upper()

        last_time = get_current_time('net')

        if input_password == hex_base:
            membership = 'Base'
            expiration_time = (last_time + timedelta(days=30)).strftime('%Y-%m-%d %H:%M:%S')
        elif input_password == hex_ai_vip:
            membership = 'AiVIP'
            expiration_time = (last_time + timedelta(days=30)).strftime('%Y-%m-%d %H:%M:%S')
        elif input_password == hex_vip:
            membership = 'VIP'
            expiration_time = (last_time + timedelta(days=30)).strftime('%Y-%m-%d %H:%M:%S')
        elif input_password == hex_year_vip:
            membership = 'VIP'
            expiration_time = (last_time + timedelta(days=365)).strftime('%Y-%m-%d %H:%M:%S')
        elif Key_value is not None:
            if input_password == Key_value:
                membership = 'VIP'
                expiration_time = (last_time + timedelta(days=30)).strftime('%Y-%m-%d %H:%M:%S')
            else:
                QtWidgets.QMessageBox.warning(self, "无效秘钥", "请输入正确的秘钥，如已购买请QQ扫码获取")
                return
        else:
            QtWidgets.QMessageBox.warning(self, "错误秘钥", "请输入正确的秘钥，如已购买请QQ扫获取")
            return

        motherboard_sn = get_motherboard_serial_number()

        write_key_value('membership', membership)
        write_key_value('expiration_time', expiration_time)
        write_key_value('motherboardsn', motherboard_sn)

        if read_key_value('membership') != membership or \
                read_key_value('expiration_time') != expiration_time or \
                read_key_value('motherboardsn') != motherboard_sn:
            QtWidgets.QMessageBox.critical(self, "激活失败", "激活出错,请以管理员身份运行软件")
        else:
            QtWidgets.QMessageBox.information(self, "激活成功", f"会员激活成功,有效期至{expiration_time}")
            QtWidgets.QApplication.quit()

    def help(self):
        QDesktopServices.openUrl(QUrl('https://blog.csdn.net/Yang_shengzhou/article/details/143782041'))
