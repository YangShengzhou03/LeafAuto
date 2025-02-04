import csv
import json
import os
import time
from datetime import datetime, timedelta

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
        widget_item.setStyleSheet("background-color: rgb(255, 255, 255); border-radius:18px;")
        widget_item.setObjectName("widget_item")

        horizontal_layout = QtWidgets.QHBoxLayout(widget_item)
        horizontal_layout.setContentsMargins(12, 2, 12, 2)
        horizontal_layout.setSpacing(6)

        widget_image = QtWidgets.QWidget(parent=widget_item)
        widget_image.setMinimumSize(QtCore.QSize(36, 36))
        widget_image.setMaximumSize(QtCore.QSize(36, 36))
        widget_image.setStyleSheet(f"image: url({get_resource_path('resources/img/page1/page1_发送就绪.svg')});")
        widget_image.setObjectName("widget_image")
        horizontal_layout.addWidget(widget_image)

        vertical_layout = QtWidgets.QVBoxLayout()
        vertical_layout.setContentsMargins(6, 6, 6, 6)
        vertical_layout.setSpacing(0)

        horizontal_layout_top = QtWidgets.QHBoxLayout()
        horizontal_layout_top.setContentsMargins(12, 6, 12, 3)
        horizontal_layout_top.setSpacing(12)

        receiver_label = QtWidgets.QLabel(name_text, parent=widget_item)
        font_receiver = QtGui.QFont()
        font_receiver.setPointSize(12)
        receiver_label.setFont(font_receiver)
        receiver_label.setObjectName("receiver_label")
        horizontal_layout_top.addWidget(receiver_label)

        time_label = QtWidgets.QLabel(time_text, parent=widget_item)
        font_time = QtGui.QFont()
        font_time.setPointSize(10)
        time_label.setFont(font_time)
        time_label.setStyleSheet("color: rgb(169, 169, 169);")
        time_label.setAlignment(
            QtCore.Qt.AlignmentFlag.AlignRight | QtCore.Qt.AlignmentFlag.AlignTrailing | QtCore.Qt.AlignmentFlag.AlignVCenter)
        time_label.setObjectName("time_label")
        horizontal_layout_top.addWidget(time_label)

        label_one_time = QtWidgets.QLabel(frequency, parent=widget_item)
        font_one_time = QtGui.QFont()
        font_one_time.setPointSize(10)
        label_one_time.setFont(font_one_time)
        label_one_time.setStyleSheet("color: rgb(105, 27, 253); text-align: center; background:rgba(0, 0, 0, 0);")
        label_one_time.setAlignment(
            QtCore.Qt.AlignmentFlag.AlignCenter)
        label_one_time.setObjectName("label_Frequency")
        horizontal_layout_top.addWidget(label_one_time)

        vertical_layout.addLayout(horizontal_layout_top)

        horizontal_layout_bottom = QtWidgets.QHBoxLayout()
        horizontal_layout_bottom.setContentsMargins(12, 6, 12, 3)

        message_label = QtWidgets.QLabel(info_text, parent=widget_item)
        font_message = QtGui.QFont()
        font_message.setPointSize(10)
        message_label.setFont(font_message)
        message_label.setStyleSheet("color: rgb(169, 169, 169);")
        message_label.setObjectName("message_label")
        horizontal_layout_bottom.addWidget(message_label)
        vertical_layout.addLayout(horizontal_layout_bottom)

        delete_button = QtWidgets.QPushButton("删除", parent=widget_item)
        delete_button.setFixedSize(50, 25)
        delete_button.setStyleSheet(
            "QPushButton { background-color: transparent; color: red; } QPushButton:hover { background-color: rgba("
            "255, 0, 0, 0.1); }"
        )
        delete_button.clicked.connect(lambda checked, t=time_text, n=name_text, i=info_text: self.remove_task(t, n, i))
        delete_button.setVisible(False)

        horizontal_layout_bottom.addWidget(delete_button)

        widget_item.enterEvent = lambda event, btn=delete_button: btn.setVisible(True)
        widget_item.leaveEvent = lambda event, btn=delete_button: btn.setVisible(False)

        horizontal_layout.addLayout(vertical_layout)
        widget_item.task = {'time': time_text, 'name': name_text, 'info': info_text, 'frequency': frequency}
        return widget_item

    def remove_task(self, time_text, name_text, info_text):
        for task in self.ready_tasks:
            if task['time'] == time_text and task['name'] == name_text and task['info'] == info_text:
                self.ready_tasks.remove(task)
                log('WARNING', f'已删除任务 {info_text[:35] + "……" if len(info_text) > 30 else info_text}')
                break
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
                        widget_image = widget_item.findChild(QtWidgets.QWidget, "widget_image")
                        if widget_image:
                            if status == '成功':
                                icon_path_key = 'page1_发送成功.svg'
                            else:
                                icon_path_key = 'page1_发送失败.svg'
                                self.play_error_sound()
                            new_icon_path = get_resource_path(f'resources/img/page1/{icon_path_key}')
                            widget_image.setStyleSheet(f"image: url({new_icon_path});")

                        next_time = datetime.fromisoformat(task['time'])

                        if task['frequency'] == '每天':
                            next_time += timedelta(days=1)
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
                with open(file_name, mode='w', newline='', encoding='ansi') as file:
                    writer = csv.writer(file)
                    writer.writerow(['Time', 'Name', 'Info', 'Frequency'])
                    for task in self.ready_tasks:
                        writer.writerow([task['time'], task['name'], task['info'], task['frequency']])
                log("DEBUG", f"任务文件已保存至{file_name}")
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
                        valid_tasks.append(row)

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

    def play_error_sound(self):
        if str_to_bool(read_key_value('error_sound')):
            self.error_sound_thread.start()
