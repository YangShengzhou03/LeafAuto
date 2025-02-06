import random
from datetime import timedelta

from PyQt6 import QtWidgets, QtCore, QtGui
from PyQt6.QtCore import QRegularExpression
from PyQt6.QtGui import QRegularExpressionValidator

from System_info import get_motherboard_serial_number, write_key_value, read_key_value
from Ui_Activities import Ui_ActivitiesWindow
from common import get_resource_path, get_current_time, get_url


class ActivitiesWindow(QtWidgets.QMainWindow, Ui_ActivitiesWindow):
    def __init__(self):
        super().__init__()
        self.ui = Ui_ActivitiesWindow()
        self.ui.setupUi(self)
        self.setWindowTitle("等待激活枫叶")
        self.setWindowIcon(QtGui.QIcon(get_resource_path('resources/img/tray.ico')))
        self.setWindowFlags(
            self.windowFlags() | QtCore.Qt.WindowType.FramelessWindowHint | QtCore.Qt.WindowType.WindowStaysOnTopHint)
        self.setAttribute(QtCore.Qt.WidgetAttribute.WA_TranslucentBackground)
        self.identify = random.randint(100000, 999999)
        self.connect_signals()

    def connect_signals(self):
        self.ui.pushButton_close.clicked.connect(self.close)
        self.ui.pushButton_year.clicked.connect(self.year_vip)
        self.ui.pushButton_VIP.clicked.connect(self.super_vip)
        self.ui.pushButton_AiVIP.clicked.connect(self.ai_vip)
        self.ui.pushButton_Base.clicked.connect(self.base_vip)
        reg_exp = QRegularExpression(r'^[A-Za-z0-9]{0,8}$')
        validator = QRegularExpressionValidator(reg_exp, self.ui.lineEdit_code)
        self.ui.lineEdit_code.setValidator(validator)
        self.ui.lineEdit_code.returnPressed.connect(self.validate_activation)
        self.ui.pushButton_OK.clicked.connect(self.validate_activation)
        self.ui.lineEdit_code.textChanged.connect(lambda text: self.ui.lineEdit_code.setText(text.upper()))
        self.ui.label_identify.setText(str(self.identify))

    def super_vip(self):
        icon = QtGui.QIcon()
        icon.addPixmap(QtGui.QPixmap(get_resource_path('resources/img/activity/VIP-click.png')), QtGui.QIcon.Mode.Normal, QtGui.QIcon.State.Off)
        self.ui.pushButton_VIP.setIcon(icon)
        icon.addPixmap(QtGui.QPixmap(get_resource_path('resources/img/activity/year-unclick.png')), QtGui.QIcon.Mode.Normal, QtGui.QIcon.State.Off)
        self.ui.pushButton_year.setIcon(icon)
        icon.addPixmap(QtGui.QPixmap(get_resource_path('resources/img/activity/AiVIP-unclick.png')), QtGui.QIcon.Mode.Normal, QtGui.QIcon.State.Off)
        self.ui.pushButton_AiVIP.setIcon(icon)
        icon.addPixmap(QtGui.QPixmap(get_resource_path('resources/img/activity/Base-unclick.png')), QtGui.QIcon.Mode.Normal, QtGui.QIcon.State.Off)
        self.ui.pushButton_Base.setIcon(icon)
        icon.addPixmap(QtGui.QPixmap(get_resource_path('resources/img/activity/wp18.9.jpg')), QtGui.QIcon.Mode.Normal, QtGui.QIcon.State.Off)
        self.ui.pushButton_Wechat.setIcon(icon)
        icon2 = QtGui.QIcon()
        icon2.addPixmap(QtGui.QPixmap(get_resource_path('resources/img/activity/ap18.9.jpg')), QtGui.QIcon.Mode.Normal, QtGui.QIcon.State.Off)
        self.ui.pushButton_AliPay.setIcon(icon2)
        self.ui.label_prices.setText("18.90")


    def year_vip(self):
        icon = QtGui.QIcon()
        icon.addPixmap(QtGui.QPixmap(get_resource_path('resources/img/activity/VIP-unclick.png')), QtGui.QIcon.Mode.Normal, QtGui.QIcon.State.Off)
        self.ui.pushButton_VIP.setIcon(icon)
        icon.addPixmap(QtGui.QPixmap(get_resource_path('resources/img/activity/year-click.png')), QtGui.QIcon.Mode.Normal, QtGui.QIcon.State.Off)
        self.ui.pushButton_year.setIcon(icon)
        icon.addPixmap(QtGui.QPixmap(get_resource_path('resources/img/activity/AiVIP-unclick.png')), QtGui.QIcon.Mode.Normal, QtGui.QIcon.State.Off)
        self.ui.pushButton_AiVIP.setIcon(icon)
        icon.addPixmap(QtGui.QPixmap(get_resource_path('resources/img/activity/Base-unclick.png')), QtGui.QIcon.Mode.Normal, QtGui.QIcon.State.Off)
        self.ui.pushButton_Base.setIcon(icon)
        icon.addPixmap(QtGui.QPixmap(get_resource_path('resources/img/activity/wp99.jpg')), QtGui.QIcon.Mode.Normal, QtGui.QIcon.State.Off)
        self.ui.pushButton_Wechat.setIcon(icon)
        icon2 = QtGui.QIcon()
        icon2.addPixmap(QtGui.QPixmap(get_resource_path('resources/img/activity/ap99.jpg')), QtGui.QIcon.Mode.Normal, QtGui.QIcon.State.Off)
        self.ui.pushButton_AliPay.setIcon(icon2)
        self.ui.label_prices.setText("99.00")

    def ai_vip(self):
        icon = QtGui.QIcon()
        icon.addPixmap(QtGui.QPixmap(get_resource_path('resources/img/activity/VIP-unclick.png')), QtGui.QIcon.Mode.Normal, QtGui.QIcon.State.Off)
        self.ui.pushButton_VIP.setIcon(icon)
        icon.addPixmap(QtGui.QPixmap(get_resource_path('resources/img/activity/year-unclick.png')), QtGui.QIcon.Mode.Normal, QtGui.QIcon.State.Off)
        self.ui.pushButton_year.setIcon(icon)
        icon.addPixmap(QtGui.QPixmap(get_resource_path('resources/img/activity/AiVIP-click.png')), QtGui.QIcon.Mode.Normal, QtGui.QIcon.State.Off)
        self.ui.pushButton_AiVIP.setIcon(icon)
        icon.addPixmap(QtGui.QPixmap(get_resource_path('resources/img/activity/Base-unclick.png')), QtGui.QIcon.Mode.Normal, QtGui.QIcon.State.Off)
        self.ui.pushButton_Base.setIcon(icon)
        icon.addPixmap(QtGui.QPixmap(get_resource_path('resources/img/activity/wp17.9.jpg')), QtGui.QIcon.Mode.Normal, QtGui.QIcon.State.Off)
        self.ui.pushButton_Wechat.setIcon(icon)
        icon2 = QtGui.QIcon()
        icon2.addPixmap(QtGui.QPixmap(get_resource_path('resources/img/activity/ap17.9.jpg')), QtGui.QIcon.Mode.Normal, QtGui.QIcon.State.Off)
        self.ui.pushButton_AliPay.setIcon(icon2)
        self.ui.label_prices.setText("17.90")

    def base_vip(self):
        icon = QtGui.QIcon()
        icon.addPixmap(QtGui.QPixmap(get_resource_path('resources/img/activity/VIP-unclick.png')), QtGui.QIcon.Mode.Normal, QtGui.QIcon.State.Off)
        self.ui.pushButton_VIP.setIcon(icon)
        icon.addPixmap(QtGui.QPixmap(get_resource_path('resources/img/activity/year-unclick.png')), QtGui.QIcon.Mode.Normal, QtGui.QIcon.State.Off)
        self.ui.pushButton_year.setIcon(icon)
        icon.addPixmap(QtGui.QPixmap(get_resource_path('resources/img/activity/AiVIP-unclick.png')), QtGui.QIcon.Mode.Normal, QtGui.QIcon.State.Off)
        self.ui.pushButton_AiVIP.setIcon(icon)
        icon.addPixmap(QtGui.QPixmap(get_resource_path('resources/img/activity/Base-click.png')), QtGui.QIcon.Mode.Normal, QtGui.QIcon.State.Off)
        self.ui.pushButton_Base.setIcon(icon)
        icon.addPixmap(QtGui.QPixmap(get_resource_path('resources/img/activity/wp9.9.jpg')), QtGui.QIcon.Mode.Normal, QtGui.QIcon.State.Off)
        self.ui.pushButton_Wechat.setIcon(icon)
        icon2 = QtGui.QIcon()
        icon2.addPixmap(QtGui.QPixmap(get_resource_path('resources/img/activity/ap9.9.jpg')), QtGui.QIcon.Mode.Normal, QtGui.QIcon.State.Off)
        self.ui.pushButton_AliPay.setIcon(icon2)
        self.ui.label_prices.setText("9.90")

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
                expiration_time = (last_time + timedelta(days=7)).strftime('%Y-%m-%d %H:%M:%S')
            else:
                QtWidgets.QMessageBox.warning(self, "无效的激活秘钥", "请输入正确的激活秘钥，如已购买请在下方扫码领取")
                return
        else:
            QtWidgets.QMessageBox.warning(self, "无效的激活秘钥", "请输入正确的激活秘钥，如已购买请在下方扫码领取")
            return

        motherboard_sn = get_motherboard_serial_number()

        write_key_value('membership', membership)
        write_key_value('expiration_time', expiration_time)
        write_key_value('motherboardsn', motherboard_sn)

        if read_key_value('membership') != membership or \
           read_key_value('expiration_time') != expiration_time or \
           read_key_value('motherboardsn') != motherboard_sn:
           QtWidgets.QMessageBox.critical(self, "激活失败", "激活未能完成,请以管理员身份运行软件再次尝试")
        else:
            QtWidgets.QMessageBox.information(self, "激活成功", f"枫叶 {membership} 激活成功,有效期至{expiration_time}")
            QtWidgets.QApplication.quit()
