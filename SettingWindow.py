from PyQt6 import QtWidgets, QtCore, QtGui
from PyQt6.QtCore import QUrl
from PyQt6.QtGui import QDesktopServices

import UpdateDialog
from System_info import write_key_value, read_key_value
from Thread import ErrorSoundThread
from Ui_SettingWindow import Ui_SettingWindow
from common import str_to_bool, log, get_resource_path


class SettingWindow(QtWidgets.QMainWindow, Ui_SettingWindow):
    language_map = {
        'cn': '简体中文',
        'cn_t': '繁体中文',
        'en': 'English'
    }
    reverse_language_map = {v: k for k, v in language_map.items()}

    def __init__(self):
        super().__init__()
        self.ui = Ui_SettingWindow()
        self.ui.setupUi(self)
        self.setWindowTitle("设置枫叶")
        self.setWindowIcon(QtGui.QIcon(get_resource_path('resources/img/icon.ico')))
        self.setWindowFlags(QtCore.Qt.WindowType.FramelessWindowHint)
        self.setAttribute(QtCore.Qt.WidgetAttribute.WA_TranslucentBackground)
        self.setting_init()
        self.error_sound_thread = ErrorSoundThread()
        self.ui.pushButton_exit_setting.clicked.connect(self.save_close)
        self.ui.pushButton_test_sound.clicked.connect(self.play_test)
        self.ui.pushButton_check_updata.clicked.connect(self.check_update)
        self.ui.pushButton_help.clicked.connect(self.help)
        if read_key_value('membership') == 'Free':
            self.ui.checkBox_net_time.setEnabled(False)

    def help(self):
        QDesktopServices.openUrl(QUrl('https://blog.csdn.net/Yang_shengzhou/article/details/143782041'))

    def check_update(self):
        if UpdateDialog.check_update() == 0:
            QtWidgets.QMessageBox.information(self, "已经是最新版本", "当前运行的已经是最新版本")

    def play_test(self):
        self.error_sound_thread.start()

    def setting_init(self):
        for key, checkbox in [
            ('error_sound', self.ui.checkBox_sound),
            ('net_time', self.ui.checkBox_net_time),
            ('auto_update', self.ui.checkBox_updata),
            ('close_option', self.ui.checkBox_close_option)
        ]:
            checkbox.setChecked(str_to_bool(read_key_value(key)))

        language_code = read_key_value('language')
        language_name = self.language_map.get(language_code, '简体中文')
        index = self.ui.comboBox_language.findText(language_name)
        if index >= 0:
            self.ui.comboBox_language.setCurrentIndex(index)
        self.ui.label_version.setText('V' + read_key_value('version'))
        self.ui.spinBox_timestep.setValue(int(read_key_value('add_timestep')))

    def save_close(self):
        try:
            for key, checkbox in [
                ('error_sound', self.ui.checkBox_sound),
                ('net_time', self.ui.checkBox_net_time),
                ('auto_update', self.ui.checkBox_updata),
                ('close_option', self.ui.checkBox_close_option)
            ]:
                write_key_value(key, str(checkbox.isChecked()))
            write_key_value('add_timestep', str(self.ui.spinBox_timestep.value()))
            selected_language = self.ui.comboBox_language.currentText()
            language_code = self.reverse_language_map.get(selected_language, 'cn')
            write_key_value('language', language_code)
        except Exception as e:
            log('ERROR', f'设置保存失败{e}')
        else:
            log('DEBUG', '设置保存成功，部分功能需重启生效')
            QtWidgets.QMessageBox.information(self, "设置保存成功", "设置保存成功，部分功能需重启生效")
        self.close()
