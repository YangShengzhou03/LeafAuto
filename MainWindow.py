import json
import os
import subprocess
import sys
from datetime import datetime, timedelta

from PyQt6 import QtWidgets, QtCore, QtGui
from PyQt6.QtCore import Qt
from PyQt6.QtGui import QAction
from PyQt6.QtWidgets import QCompleter, QListView
from wxauto import WeChat

import common
from ActivitiesWindow import ActivitiesWindow
from AiAssistant import AiAssistant
from AutoInfo import AutoInfo
from Reply import ReplyDialog
from SettingWindow import SettingWindow
from Split import Split
from System_info import read_key_value, ensure_config_file_exists, write_key_value
from Ui_MainWindow import Ui_MainWindow
from UpdateDialog import check_update
from common import get_resource_path, log, get_current_time, get_url

wx = None
current_version = 4.39


def reload_wx():
    global wx
    try:
        wx = WeChat(language=read_key_value('language'))
        MainWindow.wx = wx
    except Exception as e:
        if str(e) == "(1400, 'SetWindowPos', '无效的窗口句柄。')":
            log("ERROR", "微信未登录, 请登录微信后重启枫叶")
            return '微信未登录'
        else:
            log("ERROR", f"程序初始化出错, 错误原因:{e}")
            return '初始化错误'
    else:
        log("DEBUG", f"自动重载,{wx.nickname} 登录成功")
        return wx.nickname


class MainWindow(QtWidgets.QMainWindow, Ui_MainWindow):
    def __init__(self):
        super().__init__()
        global wx
        self.setupUi(self)
        self.ui = Ui_MainWindow()
        self.setWindowTitle("枫叶信息自动化系统")
        self.setWindowIcon(QtGui.QIcon(get_resource_path('resources/img/icon.ico')))
        common.main_window = self

        try:
            ensure_config_file_exists()
            self.language = read_key_value('language')
            self.Membership = read_key_value('membership')
            self.expiration_time = read_key_value('expiration_time')
            self.version = read_key_value('version')
            if float(self.version) < current_version:
                self.Version = write_key_value('version', str(current_version))
        except Exception as e:
            print(e)
            QtWidgets.QMessageBox.critical(self, "初始化失败", "首次启动,需连接网络并'以管理员身份运行")
            sys.exit()

        try:
            if self.language not in ['cn', 'cn_t', 'en']:
                self.language = 'cn'
            wx = WeChat(language=self.language)
        except Exception as e:
            if str(e) == "(1400, 'SetWindowPos', '无效的窗口句柄。')":
                log("ERROR", "微信未登录, 请登录微信后重启枫叶")
                self.userName_label.setText('微信未登录')
            else:
                log("ERROR", f"程序初始化出错, 错误原因:{e}")
                self.userName_label.setText('初始化错误')
        else:
            if wx and hasattr(wx, 'nickname'):
                log("DEBUG", f"初始化完成，{wx.nickname} 已登录，欢迎您!")
                self.userName_label.setText(wx.nickname)

        self.auto_info = AutoInfo(wx, self.Membership, self)
        self.split = Split(wx, self.Membership, self)
        self.ai_assistant = AiAssistant(wx, self.Membership, self)

        self.create_tray()

        self.setWindowFlags(QtCore.Qt.WindowType.FramelessWindowHint)
        self.setAttribute(QtCore.Qt.WidgetAttribute.WA_TranslucentBackground)
        self.mousePosition = None
        self.mousePressEvent = self._mouse_press_event
        self.mouseMoveEvent = self._mouse_move_event
        self.setAcceptDrops(True)

        self.connect_signals()
        self._update_ui_elements()
        self.apply_Membership_limits(self.Membership)
        if common.str_to_bool(read_key_value('auto_update')):
            check_update()
        if common.str_to_bool(read_key_value('serve_lock')):
            self.serve_lock()
        self.load_tasks_from_json()
        try:
            wx.GetSessionList()
            completer = QCompleter(wx.predict, self)
            completer.setFilterMode(Qt.MatchFlag.MatchContains)
            completer.setCompletionMode(QCompleter.CompletionMode.PopupCompletion)
            popup = completer.popup()
            if isinstance(popup, QListView):
                popup.setStyleSheet(common.load_stylesheet("completer_QListView.css"))
            self.receiver_lineEdit.setCompleter(completer)
        except Exception:
            pass

    def update_wx(self):
        global wx
        nick_name = reload_wx()
        self.userName_label.setText(nick_name)
        self.auto_info.wx = wx
        self.split.wx = wx
        self.ai_assistant.wx = wx

    def load_tasks_from_json(self):
        json_file_path = '_internal/tasks.json'
        if os.path.exists(json_file_path):
            with open(json_file_path, 'r', encoding='utf-8') as f:
                try:
                    loaded_tasks = json.load(f)
                    self.auto_info.ready_tasks.clear()
                    current_time = datetime.now()

                    membership_limit = 5 if self.Membership == 'Free' else (9999 if self.Membership == 'VIP' else 30)
                    remaining_slots = membership_limit - len(self.auto_info.ready_tasks)

                    for task in loaded_tasks:
                        if (all(key in task for key in ['time', 'name', 'info', 'frequency']) and
                                remaining_slots > 0):
                            task_time = datetime.fromisoformat(task['time'])

                            while task_time < current_time and task['frequency'] in ['每天', '工作日']:
                                task_time += timedelta(days=1)
                                if task['frequency'] == '工作日':
                                    while task_time.weekday() >= 5:
                                        task_time += timedelta(days=1)

                            widget_item = self.auto_info.create_widget(task_time.isoformat(), task['name'],
                                                                       task['info'], task['frequency'])
                            self.formLayout_3.addRow(widget_item)
                            self.auto_info.ready_tasks.append({
                                'time': task_time.isoformat(),
                                'name': task['name'],
                                'info': task['info'],
                                'frequency': task['frequency']
                            })
                            remaining_slots -= 1

                    if remaining_slots <= 0:
                        log("WARNING", f"当前已达到最大任务限制 {membership_limit}, 请升级会员")

                    self.auto_info.save_tasks_to_json()

                except json.JSONDecodeError:
                    log("ERROR", "无法解析JSON文件")
                    self.ready_tasks = []
                except Exception as e:
                    log("ERROR", f"其他错误: {str(e)}")
                    self.ready_tasks = []

    def on_vip_frame_clicked(self, event):
        if self.Membership != 'VIP':
            self.open_activities_window()
        else:
            common.author()

    def dragEnterEvent(self, event):
        if event.mimeData().hasUrls():
            event.acceptProposedAction()

    def dropEvent(self, event):
        try:
            urls = event.mimeData().urls()
            if not urls:
                return

            for url in urls:
                file_name = url.toLocalFile()
                if not file_name:
                    continue

                if os.path.isdir(file_name):
                    log('ERROR', '暂不支持发送文件夹，您可压缩后发送')
                    return

                if file_name.endswith('.csv'):
                    self.auto_info.load_configuration(filepath=file_name)
                else:
                    self.auto_info.openFileNameDialog(filepath=file_name)

            event.accept()
        except Exception:
            pass

    def _update_ui_elements(self):
        self.get_notice()
        self.dateTimeEdit.setDateTime(get_current_time('mix'))
        self.label_5.setText(self.expiration_time[:10])
        self.label_76.setText('LV.' + read_key_value('membership_class'))
        self.label_78.setText('ON' if common.str_to_bool(read_key_value('error_sound')) else 'OFF')
        self.label_80.setText(self.language.upper())
        self.label_82.setText('V' + self.version)
        self.log_textEdit.setReadOnly(True)

    def create_tray(self):
        self.tray_icon = QtWidgets.QSystemTrayIcon(self)
        self.tray_icon.setIcon(QtGui.QIcon(get_resource_path('resources/img/tray.ico')))

        menu = QtWidgets.QMenu(self)
        menu.setTitle("枫叶信息自动")
        menu.setStyleSheet(common.load_stylesheet("menu.setStyleSheet.css"))

        show_main_action = QAction("显示面板", self)
        show_main_action.triggered.connect(self.show_main_interface)
        menu.addAction(show_main_action)

        set_up_action = QAction("设置", self)
        set_up_action.triggered.connect(self.open_setting_window)
        menu.addAction(set_up_action)

        contact_feedback_action = QAction("帮助反馈", self)
        contact_feedback_action.triggered.connect(common.author)
        menu.addAction(contact_feedback_action)

        exit_action = QAction("退出枫叶", self)
        exit_action.triggered.connect(self.close_application)
        menu.addAction(exit_action)

        self.tray_icon.setContextMenu(menu)
        self.tray_icon.show()
        self.tray_icon.activated.connect(self.on_tray_icon_activated)

    def on_tray_icon_activated(self, reason):
        if reason == QtWidgets.QSystemTrayIcon.ActivationReason.Trigger:
            if self.isMinimized():
                self.showNormal()
                self.raise_()
                self.activateWindow()
            else:
                self.show()
                self.raise_()
                self.activateWindow()

    def apply_Membership_limits(self, membership: str):
        # Free\Base\AiVIP\VIP
        allow_icon = QtGui.QIcon()
        allow_icon.addPixmap(QtGui.QPixmap(get_resource_path('resources/img/page0/page0_允许白钩.svg')),
                             QtGui.QIcon.Mode.Normal,
                             QtGui.QIcon.State.Off)
        if membership == 'Free':
            small_member_image = get_resource_path('resources/img/小标/小标-免费试用版本.svg')
            retain_day = max(0, (datetime.strptime(self.expiration_time, '%Y-%m-%d %H:%M:%S') - get_current_time('mix'))
                             .days)
            if retain_day == 0:
                member_image = get_resource_path('resources/img/头标/头标-银色体验会员.svg')
                self.Free_pushButton.setText("免费试用已结束")
                self.open_activities_window()
            else:
                member_image = get_resource_path('resources/img/头标/头标-铂金体验会员.svg')
                self.Free_pushButton.setText("您正在免费试用中")
            self.welcome_label.setText(
                f"<html><head/><body><p><span style=\"font-size:16pt; font-weight:700; color:#ffffff;\">"
                f"试用还剩{retain_day}天 快充分利用吧(≧◡≦)</span></p></body></html>"
            )
            self.label_64.setText("12%")
            self.label_66.setText("6%")
            self.checkBox_Ai.setEnabled(False)
            self.checkBox_stopSleep.setEnabled(False)
            self.checkBox_period.setChecked(True)
            self.checkBox_comma.setChecked(True)
            self.checkBox_Space.setChecked(True)
        elif membership == 'Base':
            small_member_image = get_resource_path('resources/img/小标/小标-标准会员版本.svg')
            member_image = get_resource_path('resources/img/头标/头标-银色标准会员.svg')
            self.label_64.setText("74%")
            self.label_66.setText("24%")
            self.Free_pushButton.setText("正在使用标准版")
            self.label_68.setText("使用中")
            self.welcome_label.setText(
                f"<html><head/><body><p><span style=\"font-size:16pt; font-weight:700; color:#ffffff;\">"
                f"愿你充满动力 继续加油(⁎˃ᆺ˂)</span></p></body></html>"
            )
            self.checkBox_Ai.setChecked(True)
            self.checkBox_stopSleep.setChecked(True)
            self.base_pushButton.setEnabled(False)
            self.label_8.setText("已解锁 正在享用")
        elif membership == 'AiVIP':
            small_member_image = get_resource_path('resources/img/小标/小标-高级会员版本.svg')
            member_image = get_resource_path('resources/img/头标/头标-紫银高级会员.svg')
            self.label_64.setText("99%")
            self.label_66.setText("78%")
            self.Free_pushButton.setText("正在使用Ai+版")
            self.pushButton_29.setIcon(allow_icon)
            self.label_68.setText("使用中")
            self.label_69.setText("使用中")
            self.welcome_label.setText(
                f"<html><head/><body><p><span style=\"font-size:16pt; font-weight:700; color:#ffffff;\">"
                f"尊敬的会员 愿您再创佳绩(*´∀`*)</span></p></body></html>"
            )
            self.checkBox_Ai.setChecked(True)
            self.checkBox_stopSleep.setChecked(True)
            self.base_pushButton.setEnabled(False)
            self.Ai_pushButton.setEnabled(False)
            self.label_8.setText("已解锁 正在享用")
            self.label_85.setText("已解锁 正在享用")
        else:
            small_member_image = get_resource_path('resources/img/小标/小标-超级会员版本.svg')
            member_image = get_resource_path('resources/img/头标/头标-荣耀超级会员.svg')
            self.label_64.setText("99%")
            self.label_66.setText("99%")
            self.Free_pushButton.setText("正在使用超级至尊版")
            self.pushButton_29.setIcon(allow_icon)
            self.pushButton_30.setIcon(allow_icon)
            self.label_68.setText("使用中")
            self.label_69.setText("使用中")
            self.label_70.setText("使用中")
            self.welcome_label.setText(
                f"<html><head/><body><p><span style=\"font-size:16pt; font-weight:700; color:#ffffff;\">"
                f"尊贵的超级会员 欢迎您(◍•ᴗ•◍)</span></p></body></html>"
            )
            self.checkBox_Ai.setChecked(True)
            self.checkBox_stopSleep.setChecked(True)
            self.base_pushButton.setEnabled(False)
            self.Ai_pushButton.setEnabled(False)
            self.vip_pushButton.setEnabled(False)
            self.label_8.setText("已解锁 正在享用")
            self.label_85.setText("已解锁 正在享用")
            self.label_87.setText("已解锁 正在享用")
        self.vip_frame.setStyleSheet(
            f"image: url({member_image});\n"
            "background: transparent;\n"
            "border-radius:26px")
        self.version_frame.setStyleSheet("QFrame {\n"
                                         "padding: 8px;\n"
                                         f"image: url({small_member_image});\n"
                                         "background: qlineargradient(x1:0, y1:0, x2:0, y2:1,\n"
                                         "stop:0 rgba(155, 81, 45, 255),\n"
                                         "stop:1 rgba(175, 91, 55, 255));\n"
                                         "border: 0px solid red;\n"
                                         "border-radius: 10px;\n"
                                         "}")

    def connect_signals(self):
        self.setting_window = SettingWindow()
        self.activities_window = ActivitiesWindow()
        self.key_reply = ReplyDialog()
        self.file_pushButton.clicked.connect(self.auto_info.openFileNameDialog)
        self.video_pushButton_.clicked.connect(self.auto_info.video_chat)
        self.pushButton_save.clicked.connect(self.auto_info.save_configuration)
        self.pushButton_import.clicked.connect(self.auto_info.load_configuration)
        self.add_pushButton.clicked.connect(self.auto_info.add_list_item)
        self.message_lineEdit.returnPressed.connect(self.auto_info.add_list_item)
        self.receiver_lineEdit.returnPressed.connect(self.auto_info.add_list_item)

        self.close_pushButton.clicked.connect(self.head_close)
        self.maximize_pushButton.clicked.connect(self.toggle_maximize_restore)
        self.minimize_pushButton.clicked.connect(self.minimize_window)
        self.setup_pushButton.clicked.connect(self.open_setting_window)
        self.feedback_pushButton.clicked.connect(common.author)

        self.Free_pushButton.clicked.connect(common.author)
        self.base_pushButton.clicked.connect(self.open_activities_window)
        self.Ai_pushButton.clicked.connect(self.open_activities_window)
        self.vip_pushButton.clicked.connect(self.open_activities_window)

        self.start_pushButton.clicked.connect(self.auto_info.on_start_clicked)
        self.pushButton_split.clicked.connect(self.split.on_start_split_clicked)
        self.pushButton_startSplit.clicked.connect(self.split.on_start_send_clicked)
        self.pushButton_takeover.clicked.connect(self.ai_assistant.start_takeover)
        self.takeOverReceiver_lineEdit.returnPressed.connect(self.ai_assistant.start_takeover)
        self.Global_takeover.stateChanged.connect(self.ai_assistant.updateAiEditStatus)
        self.pushButton_addRule.clicked.connect(self.key_reply.show)

        checkboxes = [self.checkBox_Ai, self.checkBox_period, self.checkBox_comma, self.checkBox_Space]
        for checkbox in checkboxes:
            checkbox.clicked.connect(lambda checked, c=checkbox: self.handle_checkbox_click(c))

        self.vip_frame.mouseReleaseEvent = self.on_vip_frame_clicked

    def open_setting_window(self):
        try:
            write_key_value('admin_log', 'Test')
        except Exception:
            QtWidgets.QMessageBox.critical(self, "非管理员身份", "当前非管理员身份运行，设置可能无法保存")
        self.setting_window.show()
        self.setting_window.activateWindow()

    def open_activities_window(self):
        try:
            write_key_value('admin_log', 'Test')
        except Exception:
            QtWidgets.QMessageBox.critical(self, "非管理员身份", "当前非管理员身份运行，会员可能无法激活")
        self.activities_window.show()
        self.activities_window.activateWindow()

    def open_keyReply(self):
        self.key_reply.show()

    def handle_checkbox_click(self, checkbox):
        if checkbox.isChecked():
            if checkbox == self.checkBox_Ai:
                self.checkBox_period.setChecked(False)
                self.checkBox_comma.setChecked(False)
                self.checkBox_Space.setChecked(False)
            else:
                self.checkBox_Ai.setChecked(False)

    def minimize_window(self):
        self.showMinimized()

    def close_application(self):
        QtWidgets.QApplication.quit()

    def head_close(self):
        if common.str_to_bool(read_key_value('close_option')):
            self.hide_to_tray()
        else:
            QtWidgets.QApplication.quit()

    def hide_to_tray(self):
        self.hide()
        self.tray_icon.showMessage(
            "任务在后台继续执行",
            "枫叶已最小化到系统托盘",
            QtWidgets.QSystemTrayIcon.MessageIcon.Information,
            2000
        )

    def toggle_maximize_restore(self):
        if self.isMaximized():
            self.showNormal()
            self.resize(1289, 734)
            self.maximize_pushButton.setIcon(QtGui.QIcon(get_resource_path(
                'resources/img/窗口控制/窗口控制-最大化.svg')))
        else:
            self.showMaximized()
            self.maximize_pushButton.setIcon(QtGui.QIcon(get_resource_path('resources/img/窗口控制/窗口控制-还原.svg')))

    def _mouse_press_event(self, event):
        if event.button() == QtCore.Qt.MouseButton.LeftButton:
            self.mousePosition = event.globalPosition().toPoint() - self.frameGeometry().topLeft()
            event.accept()

    def _mouse_move_event(self, event):
        if self.mousePosition is not None and event.buttons() & QtCore.Qt.MouseButton.LeftButton:
            self.move(event.globalPosition().toPoint() - self.mousePosition)
            event.accept()

    def show_main_interface(self):
        if self.isMinimized():
            self.showNormal()
        else:
            self.show()
        self.raise_()
        self.activateWindow()

    def get_notice(self):
        try:
            Key, notice_content = get_url()
            if notice_content:
                self.textBrowser.setHtml(notice_content)
        except Exception:
            self.textBrowser.setHtml('<center><h2>欢迎使用LeafAuto</h2><h2>LeafAuto是我在2024'
                                     '年大二时写的练习程序，没想到居然这么多人爱用。希望大家多提宝贵意见，同时也希望大家会喜欢她。</h2'
                                     '></center>')

    def serve_lock(self):
        try:
            for i in range(10):
                cmd = r'%windir%\System32\tscon.exe {} /dest:console'.format(str(i))
                subprocess.run(cmd, shell=True, capture_output=True, text=True)
        except Exception as e:
            log("ERROR", f"阻止服务器锁屏失败: {str(e)}")
