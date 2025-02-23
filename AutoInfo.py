import csv
import json
import os
import re
import smtplib
import time
from datetime import datetime, timedelta
from email.header import Header
from email.mime.text import MIMEText

from PyQt6 import QtWidgets, QtCore, QtGui

from System_info import read_key_value
from Thread import WorkerThread, ErrorSoundThread
from common import get_resource_path, log, str_to_bool


class AutoInfo(QtWidgets.QWidget):
    def __init__(self, wx, membership, parent=None):
        super().__init__(parent)
        self.parent = parent
        self.wx = wx
        self.Membership = membership
        self.ready_tasks = []
        self.completed_tasks = []
        self.is_executing = False
        self.worker_thread = None
        self.error_sound_thread = ErrorSoundThread()
        self.audio_files = {
            0: get_resource_path('resources/sound/error_sound_1.mp3'),
            1: get_resource_path('resources/sound/error_sound_2.mp3'),
            2: get_resource_path('resources/sound/error_sound_3.mp3'),
            3: get_resource_path('resources/sound/error_sound_4.mp3'),
            4: get_resource_path('resources/sound/error_sound_5.mp3')
        }

    def openFileNameDialog(self, filepath=None):
        if filepath:
            self.parent.message_lineEdit.setText(str(filepath))
            return

        file_filters = (
            "所有文件 (*);;"
            "图像文件 (*.bmp *.gif *.jpg *.jpeg *.png *.svg *.tiff);;"
            "文档文件 (*.doc *.docx *.pdf *.txt *.odt);;"
            "电子表格 (*.xls *.xlsx *.ods);;"
            "演示文稿 (*.ppt *.pptx *.odp);;"
            "音频文件 (*.mp3 *.wav *.flac *.aac);;"
            "视频文件 (*.mp4 *.avi *.mkv *.mov);;"
            "压缩文件 (*.zip *.rar *.tar *.gz *.bz2)"
        )

        options = QtWidgets.QFileDialog.Option.ReadOnly
        fileName, _ = QtWidgets.QFileDialog.getOpenFileName(
            None,
            "选择要发送的文件",
            "",
            file_filters,
            options=options
        )

        if fileName:
            self.parent.message_lineEdit.setText(fileName)

    def video_chat(self):
        self.parent.message_lineEdit.setText('Video_chat')

    def save_tasks_to_json(self):
        try:
            with open('_internal/tasks.json', 'w', encoding='utf-8') as f:
                json.dump(self.ready_tasks, f, ensure_ascii=False, indent=4)
        except Exception:
            log("ERROR", "非管理员身份运行软件,未能将操作保存")

    def add_list_item(self):
        time_text, name_text, info_text, frequency = self.get_input_values()

        if not all([time_text, name_text, info_text]):
            log("WARNING", "请先输入有效内容和接收人再添加任务")
            return

        if self.Membership == 'Free' and len(self.ready_tasks) >= 5:
            log("WARNING", "试用版最多添加5个任务，请升级版本")
            QtWidgets.QMessageBox.warning(self, "试用版限制", "试用版最多添加5个任务，请升级版本")
            return
        elif self.Membership == 'Base' and len(self.ready_tasks) >= 30:
            log("WARNING", "基础版最多添加30个任务,升级Ai版无限制")
            QtWidgets.QMessageBox.warning(self, "标准版限制", "标准版最多添加30个任务，请升级版本")
            return

        widget_item = self.create_widget(time_text, name_text, info_text, frequency)
        self.parent.formLayout_3.addRow(widget_item)
        self.ready_tasks.append({'time': time_text, 'name': name_text, 'info': info_text, 'frequency': frequency})
        log('INFO',
            f'已添加 {time_text[-8:]} 把 {info_text[:25] + "……" if len(info_text) > 25 else info_text} 发给 {name_text[:8]} ')

        self.parent.dateTimeEdit.setDateTime(
            datetime.fromisoformat(time_text) + timedelta(minutes=int(read_key_value('add_timestep'))))

        self.save_tasks_to_json()

    def create_widget(self, time_text, name_text, info_text, frequency):
        widget_item = QtWidgets.QWidget(parent=self.parent.scrollAreaWidgetContents_3)
        widget_item.setMinimumSize(QtCore.QSize(360, 70))
        widget_item.setMaximumSize(QtCore.QSize(360, 70))
        widget_item.setStyleSheet("background-color: rgb(255, 255, 255);\nborder-radius:18px")
        widget_item.setObjectName("widget_item")

        horizontalLayout_76 = QtWidgets.QHBoxLayout(widget_item)
        horizontalLayout_76.setContentsMargins(12, 2, 12, 2)
        horizontalLayout_76.setSpacing(6)
        horizontalLayout_76.setObjectName("horizontalLayout_76")

        widget_54 = QtWidgets.QWidget(parent=widget_item)
        widget_54.setMinimumSize(QtCore.QSize(36, 36))
        widget_54.setMaximumSize(QtCore.QSize(36, 36))
        widget_54.setStyleSheet(f"image: url({get_resource_path('resources/img/page1/page1_发送就绪.svg')});")
        widget_54.setObjectName("widget_54")
        horizontalLayout_76.addWidget(widget_54)

        verticalLayout_64 = QtWidgets.QVBoxLayout()
        verticalLayout_64.setContentsMargins(6, 6, 6, 6)
        verticalLayout_64.setSpacing(0)
        verticalLayout_64.setObjectName("verticalLayout_64")

        horizontalLayout_77 = QtWidgets.QHBoxLayout()
        horizontalLayout_77.setContentsMargins(0, 0, 0, 0)
        horizontalLayout_77.setSpacing(4)
        horizontalLayout_77.setObjectName("horizontalLayout_77")

        receiver_label = QtWidgets.QLabel(name_text, parent=widget_item)
        font = QtGui.QFont()
        font.setFamily("微软雅黑 Light")
        font.setPointSize(12)
        receiver_label.setFont(font)
        receiver_label.setStyleSheet("color:rgb(0, 0, 0);")
        receiver_label.setObjectName("receiver_label")
        horizontalLayout_77.addWidget(receiver_label)

        time_label = QtWidgets.QLabel(time_text, parent=widget_item)
        font = QtGui.QFont()
        font.setPointSize(10)
        time_label.setFont(font)
        time_label.setStyleSheet("color: rgb(169, 169, 169);")
        time_label.setAlignment(
            QtCore.Qt.AlignmentFlag.AlignRight | QtCore.Qt.AlignmentFlag.AlignTrailing | QtCore.Qt.AlignmentFlag.AlignVCenter)
        time_label.setObjectName("time_label")
        horizontalLayout_77.addWidget(time_label)

        label_2 = QtWidgets.QLabel(frequency, parent=widget_item)
        label_2.setStyleSheet("color:rgb(105, 27, 253);\ntext-align: center;\nbackground:rgba(0, 0, 0, 0);")
        label_2.setObjectName("label_2")
        horizontalLayout_77.addWidget(label_2)

        horizontalLayout_77.setStretch(0, 1)
        verticalLayout_64.addLayout(horizontalLayout_77)

        horizontalLayout_7 = QtWidgets.QHBoxLayout()
        horizontalLayout_7.setContentsMargins(0, 6, 12, 3)
        horizontalLayout_7.setObjectName("horizontalLayout_7")

        message_label = QtWidgets.QLabel(info_text, parent=widget_item)
        font = QtGui.QFont()
        font.setPointSize(10)
        message_label.setFont(font)
        message_label.setStyleSheet("color: rgb(169, 169, 169);")
        message_label.setObjectName("message_label")
        horizontalLayout_7.addWidget(message_label)
        delete_button = QtWidgets.QPushButton("删除", parent=widget_item)
        delete_button.setFixedSize(50, 25)
        delete_button.setStyleSheet(
            "QPushButton { background-color: transparent; color: red; } QPushButton:hover { background-color: rgba(255, 0, 0, 0.1); }"
        )
        delete_button.clicked.connect(lambda checked, t=time_text, n=name_text, i=info_text: self.remove_task(t, n, i))
        delete_button.setVisible(False)

        horizontalLayout_7.addWidget(delete_button)

        widget_item.enterEvent = lambda event, btn=delete_button: btn.setVisible(True)
        widget_item.leaveEvent = lambda event, btn=delete_button: btn.setVisible(False)

        verticalLayout_64.addLayout(horizontalLayout_7)
        horizontalLayout_76.addLayout(verticalLayout_64)
        widget_item.task = {'time': time_text, 'name': name_text, 'info': info_text, 'frequency': frequency}
        return widget_item

    def remove_task(self, time_text, name_text, info_text):
        if self.error_sound_thread._is_playing:
            self.error_sound_thread.stop_playback()
        for task in self.ready_tasks:
            if task['time'] == time_text and task['name'] == name_text and task['info'] == info_text:
                self.ready_tasks.remove(task)
                log('WARNING', f'已删除任务 {info_text[:35] + "……" if len(info_text) > 30 else info_text}')
                break
        if not self.ready_tasks:
            self.is_executing = False
            self.parent.start_pushButton.setText("开始执行")
            if self.worker_thread is not None:
                self.worker_thread.requestInterruption()
                self.worker_thread = None
        self.update_ui()
        self.save_tasks_to_json()

    def update_ui(self):
        self.clear_layout(self.parent.formLayout_3)
        for task in self.ready_tasks:
            widget = self.create_widget(task['time'], task['name'], task['info'], task['frequency'])
            self.parent.formLayout_3.addRow(widget)

    def get_input_values(self):
        name_text = self.parent.receiver_lineEdit.text()
        info_text = self.parent.message_lineEdit.text()
        time_text = self.parent.dateTimeEdit.dateTime().toString(QtCore.Qt.DateFormat.ISODate)
        frequency = self.parent.comboBox_Frequency.currentText()
        return time_text, name_text, info_text, frequency

    def on_start_clicked(self):
        if self.is_executing:
            self.is_executing = False
            self.parent.start_pushButton.setText("开始执行")
            if self.worker_thread is not None:
                self.worker_thread.requestInterruption()
                self.worker_thread = None
            if self.error_sound_thread._is_playing:
                self.error_sound_thread.stop_playback()
        else:
            if not self.ready_tasks:
                log("WARNING", "任务列表为空，请先添加任务至任务列表")
            else:
                self.is_executing = True
                self.parent.start_pushButton.setText("停止执行")
                self.worker_thread = WorkerThread(self)
                self.worker_thread.prevent_sleep = self.parent.checkBox_stopSleep.isChecked()
                self.worker_thread.current_time = 'mix' if str_to_bool(read_key_value('net_time')) else 'sys'
                self.worker_thread.finished.connect(self.on_thread_finished)
                self.worker_thread.start()

    def clear_layout(self, layout):
        while layout.count():
            child = layout.takeAt(0)
            if child.widget():
                child.widget().deleteLater()

    def update_task_status(self, task, status):
        if task in self.ready_tasks:
            task_index = self.ready_tasks.index(task)
            self.ready_tasks[task_index]['status'] = status
            self.completed_tasks.append(self.ready_tasks.pop(task_index))
            for i in range(self.parent.formLayout_3.count()):
                item = self.parent.formLayout_3.itemAt(i)
                if item and item.widget():
                    widget_item = item.widget()
                    if hasattr(widget_item, 'task') and all(
                            widget_item.task[key] == task[key] for key in ['time', 'name', 'info', 'frequency']):
                        widget_image = widget_item.findChild(QtWidgets.QWidget, "widget_54")
                        if widget_image:
                            if status == '成功':
                                icon_path_key = 'page1_发送成功.svg'
                            else:
                                icon_path_key = 'page1_发送失败.svg'
                                self.play_error_sound()
                                self.send_error_email(task)
                            new_icon_path = get_resource_path(f'resources/img/page1/{icon_path_key}')
                            widget_image.setStyleSheet(f"image: url({new_icon_path});")

                        next_time = datetime.fromisoformat(task['time'])

                        if task['frequency'] == '每天':
                            next_time += timedelta(days=1)
                            self.add_next_task(next_time.isoformat(), task['name'], task['info'], task['frequency'])
                        elif task['frequency'] == '每周':
                            next_time += timedelta(days=7)
                            self.add_next_task(next_time.isoformat(), task['name'], task['info'], task['frequency'])
                        elif task['frequency'] == '工作日':
                            while True:
                                next_time += timedelta(days=1)
                                if next_time.weekday() < 5:
                                    break
                            self.add_next_task(next_time.isoformat(), task['name'], task['info'], task['frequency'])
                        self.save_tasks_to_json()
                        break

    def add_next_task(self, time_text, name_text, info_text, frequency):
        widget_item = self.create_widget(time_text, name_text, info_text, frequency)
        self.parent.formLayout_3.addRow(widget_item)
        self.ready_tasks.append({'time': time_text, 'name': name_text, 'info': info_text, 'frequency': frequency})
        log('INFO',
            f'自动添加 {time_text} 把 {info_text[:25] + "……" if len(info_text) > 25 else info_text} 发给 {name_text[:8]}')
        self.save_tasks_to_json()

    def on_thread_finished(self):
        log("DEBUG", "所有任务执行完毕")
        self.is_executing = False
        self.parent.start_pushButton.setText("开始执行")
        if self.parent.checkBox_Shutdown.isChecked():
            self.shutdown_computer()

    def shutdown_computer(self):
        for i in range(10, 0, -1):
            log("WARNING", f"电脑在 {i} 秒后自动关机")
            time.sleep(1)
        log("DEBUG", "正在关机中...")
        os.system('shutdown /s /t 0')

    def save_configuration(self):
        try:
            if not self.ready_tasks:
                log("WARNING", "当前任务列表为空,没有任务可供保存")
                return
            documents_dir = os.path.expanduser("~/Documents")
            file_name, _ = QtWidgets.QFileDialog.getSaveFileName(
                self, "保存任务计划", os.path.join(documents_dir, "LeafAuto自动计划"), "枫叶任务文件(*.csv);;All Files (*)"
            )
            if file_name:
                try:
                    with open(file_name, mode='w', newline='', encoding='ansi') as file:
                        writer = csv.writer(file)
                        writer.writerow(['Time', 'Name', 'Info', 'Frequency'])
                        for task in self.ready_tasks:
                            writer.writerow([task['time'], task['name'], task['info'], task['frequency']])
                    log("DEBUG", f"任务文件已保存至{file_name}")
                except UnicodeEncodeError:
                    with open(file_name, mode='w', newline='', encoding='utf-8') as file:
                        writer = csv.writer(file)
                        writer.writerow(['Time', 'Name', 'Info', 'Frequency'])
                        for task in self.ready_tasks:
                            writer.writerow([task['time'], task['name'], task['info'], task['frequency']])
                    log("DEBUG", f"因有特殊字符,已用UTF-8编码保存至{file_name}")
        except Exception as e:
            log("ERROR", f"任务保存失败,{e}")

    def load_configuration(self, filepath=None):
        documents_dir = os.path.expanduser("~/Documents")
        if not filepath:
            file_name, _ = QtWidgets.QFileDialog.getOpenFileName(
                self, "导入任务计划", documents_dir, "枫叶任务文件(*.csv);;All Files (*)"
            )
        else:
            file_name = filepath
        if file_name:
            try:
                with open(file_name, mode='r', newline='', encoding='ansi') as file:
                    reader = csv.DictReader(file)
                    new_tasks = [row for row in reader]
            except UnicodeDecodeError:
                try:
                    with open(file_name, mode='r', newline='', encoding='utf-8') as file:
                        reader = csv.DictReader(file)
                        new_tasks = [row for row in reader]
                except UnicodeDecodeError:
                    log("ERROR", f"文件 {file_name} 编码不正确，无法读取")
                    QtWidgets.QMessageBox.warning(self, "编码错误", "文件编码不正确，无法读取")
                    return

            valid_tasks = []
            for index, row in enumerate(new_tasks):
                if all(key in row for key in ['Time', 'Name', 'Info', 'Frequency']):
                    if row['Time'] and row['Name'] and row['Info']:
                        if re.match(r"^\d{4}-\d{2}-\d{2}T\d{2}:\d{2}:\d{2}$", row['Time']):
                            try:
                                datetime.strptime(row['Time'], "%Y-%m-%dT%H:%M:%S")
                                valid_tasks.append(row)
                            except ValueError:
                                log("WARNING",
                                    f"任务 {index + 1} 的时间 '{row['Time']}' 格式不正确或值无效，已跳过此任务")
                        else:
                            log("WARNING", f"任务 {index + 1} 的时间 '{row['Time']}' 格式不正确或值无效，已跳过此任务")
            if not valid_tasks:
                log('ERROR', '任务文件中有错误数据,导入出错')
                return
            total_tasks = len(self.ready_tasks) + len(valid_tasks)
            if (self.Membership == 'Free' and total_tasks > 5) or (self.Membership == 'Base' and total_tasks > 30):
                Membership_limit = 5 if self.Membership == 'Free' else 30
                remaining_slots = Membership_limit - len(self.ready_tasks)
                if remaining_slots > 0:
                    log("WARNING", f"当前版本剩余{remaining_slots}个任务槽,只导入前{remaining_slots}个任务")
                    valid_tasks = valid_tasks[:remaining_slots]
                else:
                    log("WARNING", f"当前版本已达到最大任务数限制,请升级会员")
                    return
            for row in valid_tasks:
                widget = self.create_widget(row['Time'], row['Name'], row['Info'], row['Frequency'])
                self.parent.formLayout_3.addRow(widget)
                self.ready_tasks.append({
                    'time': row['Time'],
                    'name': row['Name'],
                    'info': row['Info'],
                    'frequency': row['Frequency']
                })
            log("DEBUG", f"计划已从 {file_name} 导入")
            self.save_tasks_to_json()

    def play_error_sound(self):
        if str_to_bool(read_key_value('error_sound')):
            try:
                selected_audio_index = int(read_key_value('selected_audio_index'))
            except Exception:
                selected_audio_index = 0
            if selected_audio_index in self.audio_files:
                self.selected_audio_file = self.audio_files[selected_audio_index]
            else:
                log("ERROR", f"音频播放失败{selected_audio_index}")
                return
            self.error_sound_thread.update_sound_file(self.selected_audio_file)
            self.error_sound_thread.start()

    def send_error_email(self, task):
        if str_to_bool(read_key_value('error_email')):
            try:
                sender_email = '3555844679@qq.com'
                receiver_email = read_key_value('email')
                smtp_server = 'smtp.qq.com'
                smtp_port = 465

                username = '3555844679@qq.com'
                password = 'xtibpzrdwnppchhi'

                # 改进后的邮件主题和正文
                subject = f"【枫叶提醒】您于{task['time']}发送给{task['name']}的信息出错了"
                body = (
                    f"尊敬的用户朋友：\n\n您好！感谢您一直以来对枫叶信息服务保障团队的支持与信任。\n\n我们非常遗憾地通知您，在【{task['time']}】尝试将您的【{task['info']}】信息发送给【{task['name']}】时，由于系统遇到了未知的技术故障，导致此次信息未能成功送达。\n"
                    "\n我们深知这一情况可能给您带来的不便，对此我们深表歉意。为了帮助您尽快解决问题，我们建议您可以首先检查所填写的信息是否准确无误，接收者是否与实际备注完全一致。\n"
                    "\n如果您确认所有信息均正确无误，但仍无法成功发送，请不要犹豫，随时联系我们的客户服务团队。您可以通过联系开发者或者发送电子邮件至我们的邮箱来获取进一步的帮助和支持。\n"
                    "\n同时，我们也鼓励您通过访问我们的官方网站或下载最新的应用程序来了解更多信息和自助解决指南。我们不断努力改进我们的服务和技术，以确保为每一位用户提供最佳的使用体验。\n"
                    "\n最后，对于此次事件给您带来的任何不便，我们再次表示深深的歉意，并感谢您的耐心等待和理解。请相信我们会全力以赴解决此问题，并持续提升我们的服务质量。\n"
                    "\n祝您拥有美好的一天！\n——枫叶信息服务保障团队"
                )

                receiver_name = '尊贵的枫叶用户朋友'

                message = MIMEText(body, 'plain', 'utf-8')
                message['From'] = 'LeafAuto <3555844679@qq.com>'
                message['To'] = f"{Header(receiver_name, 'utf-8')} <{receiver_email}>"
                message['Subject'] = Header(subject, 'utf-8')

                server = smtplib.SMTP_SSL(smtp_server, smtp_port)
                server.login(username, password)
                server.sendmail(sender_email, [receiver_email], message.as_string())
            except Exception as e:
                log("ERROR", "邮件发送失败")
            finally:
                server.quit()
