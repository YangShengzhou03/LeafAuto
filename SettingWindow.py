import os
import re
import sys

from PyQt6 import QtWidgets, QtCore, QtGui
from PyQt6.QtCore import QUrl
from PyQt6.QtGui import QDesktopServices
from PyQt6.QtWidgets import QInputDialog, QMessageBox

import UpdateDialog
from System_info import write_key_value, read_key_value
from Thread import ErrorSoundThread
from Ui_SettingWindow import Ui_SettingWindow
from common import str_to_bool, log, get_resource_path


class SettingWindow(QtWidgets.QMainWindow, Ui_SettingWindow):
    language_map = {'cn': '简体中文', 'cn_t': '繁体中文', 'en': 'English'}
    reverse_language_map = {v: k for k, v in language_map.items()}

    def __init__(self):
        super().__init__()
        self.ui = Ui_SettingWindow()
        self.ui.setupUi(self)
        self.setWindowTitle("设置枫叶")
        self.setWindowIcon(QtGui.QIcon(get_resource_path('resources/img/icon.ico')))
        self.setWindowFlags(QtCore.Qt.WindowType.FramelessWindowHint)
        self.setAttribute(QtCore.Qt.WidgetAttribute.WA_TranslucentBackground)

        self.error_sound_thread = ErrorSoundThread()

        self.ui.checkBox_Email.clicked.connect(self.select_email)

        self.ui.pushButton_exit_setting.clicked.connect(self.save_close)
        self.ui.pushButton_test_sound.clicked.connect(self.toggle_audio)
        self.ui.pushButton_check_updata.clicked.connect(self.check_update)
        self.ui.pushButton_clean.clicked.connect(self.clean_date)
        self.ui.pushButton_help.clicked.connect(self.help)

        membership = read_key_value('membership')
        if membership == 'VIP':
            pass
        elif membership == 'AiVIP':
            self.ui.checkBox_Email.setEnabled(False)
        else:
            self.ui.checkBox_net_time.setEnabled(False)
            self.ui.checkBox_Email.setEnabled(False)
            # self.ui.checkBox_sever.setChecked(False)

        self.setting_init()
        self.ui.comboBox_errorAudio.currentIndexChanged.connect(self.update_selected_sound)

    def clean_date(self):
        file1 = '_internal/AutoReply_Rules.json'
        file2 = '_internal/tasks.json'
        files_to_clean = [file1, file2]
        cleaned_any = False
        for file in files_to_clean:
            if os.path.exists(file):
                os.remove(file)
                cleaned_any = True
        if not cleaned_any:
            QtWidgets.QMessageBox.warning(self, "无需清理", "已经很干净了，无需清理。")
        else:
            QtWidgets.QMessageBox.information(self, "清理完成", "数据已清理，即将重启以完成。")
            sys.exit(0)

    def select_email(self, state):
        if state:
            email = self.show_input_dialog()
            if email is not None:
                write_key_value('email', str(email))
            else:
                self.ui.checkBox_Email.setChecked(False)
        else:
            self.ui.checkBox_Email.setChecked(False)

    def show_input_dialog(self):
        email, ok = QInputDialog.getText(self, '输入邮箱', '请输入用于接收出错信息的邮箱:')
        if ok and email:
            if re.match(r"[^@]+@[^@]+\.[^@]+", email):
                return email
            else:
                QMessageBox.warning(self, "错误", "邮箱格式无效,请输入正确的邮箱")
                return None
        return None

    def help(self):
        QDesktopServices.openUrl(QUrl('https://blog.csdn.net/Yang_shengzhou/article/details/143782041'))

    def check_update(self):
        if UpdateDialog.check_update() == 0:
            QtWidgets.QMessageBox.information(self, "已经是最新版本", "当前运行的已经是最新版本")

    def toggle_audio(self):
        if not hasattr(self, 'selected_audio_file'):
            log('ERROR', '未选择音频文件')
            return
        self.error_sound_thread.update_sound_file(self.selected_audio_file)
        self.error_sound_thread.play_test()

    def setting_init(self):
        for key, checkbox in [
            ('error_email', self.ui.checkBox_Email),
            ('error_sound', self.ui.checkBox_sound),
            ('net_time', self.ui.checkBox_net_time),
            ('auto_update', self.ui.checkBox_updata),
            ('serve_lock', self.ui.checkBox_sever),
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

        self.audio_files = {
            0: get_resource_path('resources/sound/error_sound_1.mp3'),
            1: get_resource_path('resources/sound/error_sound_2.mp3'),
            2: get_resource_path('resources/sound/error_sound_3.mp3'),
            3: get_resource_path('resources/sound/error_sound_4.mp3'),
            4: get_resource_path('resources/sound/error_sound_5.mp3')
        }

        selected_index_str = read_key_value('selected_audio_index')
        selected_index = int(selected_index_str) if selected_index_str is not None else 0

        self.ui.comboBox_errorAudio.blockSignals(True)
        self.ui.comboBox_errorAudio.clear()
        for i in range(5):
            self.ui.comboBox_errorAudio.addItem(f"提示音{i + 1}")
        self.ui.comboBox_errorAudio.blockSignals(False)

        if 0 <= selected_index < len(self.audio_files):
            self.ui.comboBox_errorAudio.setCurrentIndex(selected_index)
            self.update_selected_sound(selected_index)
        else:
            log('ERROR', f'无效的索引: {selected_index}')
            self.ui.comboBox_errorAudio.setCurrentIndex(0)
            self.update_selected_sound(0)

    def save_close(self):
        try:
            if self.error_sound_thread._is_playing:
                self.error_sound_thread.stop_playback()
            for key, checkbox in [
                ('error_email', self.ui.checkBox_Email),
                ('error_sound', self.ui.checkBox_sound),
                ('net_time', self.ui.checkBox_net_time),
                ('auto_update', self.ui.checkBox_updata),
                ('serve_lock', self.ui.checkBox_sever),
                ('close_option', self.ui.checkBox_close_option)
            ]:
                write_key_value(key, str(checkbox.isChecked()))
            write_key_value('add_timestep', str(self.ui.spinBox_timestep.value()))
            selected_language = self.ui.comboBox_language.currentText()
            language_code = self.reverse_language_map.get(selected_language, 'cn')
            write_key_value('language', language_code)
            write_key_value('selected_audio_index', str(self.ui.comboBox_errorAudio.currentIndex()))
        except Exception as e:
            log('ERROR', f'设置保存失败，请用管理员身份运行软件。')
        else:
            log('DEBUG', '设置保存成功，部分功能需重启生效')
            QtWidgets.QMessageBox.information(self, "设置保存成功", "设置保存成功，部分功能需重启生效")
        self.close()

    def update_selected_sound(self, index):
        if index < 0 or index >= len(self.audio_files):
            log('ERROR', f'报错音频索引无效: {index}')
            return
        if self.error_sound_thread._is_playing:
            self.error_sound_thread.stop_playback()
        self.selected_audio_file = self.audio_files[index]
