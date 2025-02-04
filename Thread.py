import ctypes
import os
import threading
from datetime import datetime

import requests
from PyQt6 import QtCore, QtMultimedia
from PyQt6.QtCore import QThread, pyqtSignal

from common import log, get_current_time, get_resource_path


class AiWorkerThread(QThread):
    pause_changed = pyqtSignal(bool)
    finished = pyqtSignal()

    def __init__(self, app_instance, receiver):
        super().__init__()
        self.app_instance = app_instance
        self.receiver = receiver
        self.stop_event = threading.Event()
        self.running = True

    def run(self):
        try:
            self.app_instance.wx.SendMsg(msg=" ", who=self.receiver)
        except Exception as e:
            log("ERROR", f"{str(e)}")
            self.app_instance.on_thread_finished()
            return

        while self.running and not self.stop_event.is_set():
            try:
                msgs = self.app_instance.wx.GetAllMessage()
                if msgs:
                    last_msg = msgs[-1]
                    if last_msg.type == "friend":
                        self.main(last_msg.content, self.receiver)
            except Exception as e:
                log("ERROR", f"{str(e)}")
                break
            finally:
                self.msleep(100)
            if self.stop_event.is_set():
                break
        self.app_instance.on_thread_finished()

    def requestInterruption(self):
        self.stop_event.set()

    def get_access_token(self):
        url = "https://aip.baidubce.com/oauth/2.0/token"
        params = {
            'grant_type': 'client_credentials',
            'client_id': 'eCB39lMiTbHXV0mTt1d6bBw7',
            'client_secret': 'WUbEO3XdMNJLTJKNQfFbMSQvtBVzRhvu'
        }
        response = requests.post(url, params=params)
        return response.json().get("access_token")

    def main(self, msg, who):
        access_token = self.get_access_token()
        url = f"https://aip.baidubce.com/rpc/2.0/ai_custom/v1/wenxinworkshop/chat/ernie-speed-128k?access_token={access_token}"
        payload = {
            "messages": [
                {"role": "user", "content": msg}
            ]
        }
        headers = {'Content-Type': 'application/json'}

        try:
            response = requests.post(url, json=payload, headers=headers)
            response.raise_for_status()
            json_result = response.json()
            if 'result' in json_result:
                self.app_instance.wx.SendMsg(msg=json_result['result'], who=who)
                log("INFO", f"Ai发送:{json_result['result']}")
            else:
                log("ERROR", f"{response.text}")
        except Exception as e:
            log("ERROR", f"{str(e)}")


class SplitWorkerThread(QThread):
    pause_changed = pyqtSignal(bool)
    finished = pyqtSignal()

    def __init__(self, app_instance, receiver, sentences):
        super().__init__()
        self.app_instance = app_instance
        self.receiver = receiver
        self.sentences = sentences
        self.stop_event = threading.Event()

    def run(self):
        log("WARNING", f"准备将 {len(self.sentences)} 条信息发给 {self.receiver}")

        for sentence in self.sentences:
            if self.stop_event.is_set():
                break

            try:
                log("INFO", f"发送 '{sentence}' 给 {self.receiver}")
                self.app_instance.wx.SendMsg(msg=sentence, who=self.receiver)
            except Exception as e:
                log("ERROR", f"{str(e)}")
                self.app_instance.is_sending = False
                self.app_instance.is_scheduled_task_active = False
                self.stop_event.set()
                break
        self.app_instance.on_thread_finished()

    def requestInterruption(self):
        self.stop_event.set()


class WorkerThread(QtCore.QThread):
    pause_changed = QtCore.pyqtSignal(bool)
    finished = QtCore.pyqtSignal()

    def __init__(self, app_instance):
        super().__init__()
        self.app_instance = app_instance
        self.is_paused = False
        self.interrupted = False
        self.prevent_sleep = False
        self.current_time = 'sys'

    def run(self):
        try:
            if self.prevent_sleep:
                ctypes.windll.kernel32.SetThreadExecutionState(0x80000002)

            while not self.interrupted:

                next_task = self.find_next_ready_task()
                if next_task is None:
                    ctypes.windll.kernel32.SetThreadExecutionState(0x80000000 | 0x00000001)
                    self.prevent_sleep = False
                    self.app_instance.on_thread_finished()
                    break
                task_time = datetime.strptime(next_task['time'], '%Y-%m-%dT%H:%M:%S')

                remaining_time = (task_time - get_current_time(self.current_time)).total_seconds()

                if remaining_time > 0:
                    self.msleep(int(remaining_time * 1000))

                try:
                    name = next_task['name']
                    info = next_task['info']

                    if os.path.isfile(info):
                        file_name = os.path.basename(info)
                        log("INFO", f"开始把文件 {file_name} 发给 {name}")
                        self.app_instance.wx.SendFiles(filepath=info, who=name)
                    elif info == 'Video_chat':
                        log("INFO", f"开始与 {name} 视频通话")
                        self.app_instance.wx.VideoCall(who=name)
                    else:
                        log("INFO", f"开始把 {info[:25] + '……' if len(info) > 25 else info} 发给 {name[:8]}")
                        self.app_instance.wx.SendMsg(msg=info, who=name)
                    log('DEBUG', f"成功把 {info[:25] + '……' if len(info) > 25 else info} 发给 {name[:8]} ")

                except Exception as e:
                    self.msleep(50)  # 有效阻止爆日志的问题
                    log("ERROR", f"{str(e)}")
                    self.app_instance.update_task_status(next_task, '出错')
                else:
                    self.app_instance.update_task_status(next_task, '成功')

                while not self.interrupted and self.is_paused:
                    self.msleep(50)
                if self.interrupted:
                    break
            if self.prevent_sleep:
                ctypes.windll.kernel32.SetThreadExecutionState(0x80000000 | 0x00000001)
                self.prevent_sleep = False
        except Exception as e:
            log("ERROR", f"{str(e)}")

    def find_next_ready_task(self):
        next_task = None
        min_time = None
        for task in self.app_instance.ready_tasks:
            try:
                task_time = QtCore.QDateTime.fromString(task['time'], QtCore.Qt.DateFormat.ISODate).toSecsSinceEpoch()
                if min_time is None or task_time < min_time:
                    min_time = task_time
                    next_task = task
            except Exception as e:
                log("ERROR", f"{str(e)}")
        return next_task

    def requestInterruption(self):
        self.interrupted = True


class ErrorSoundThread(QtCore.QThread):
    finished = QtCore.pyqtSignal()
    _has_run = False

    def __init__(self):
        super().__init__()
        if self._has_run:
            return
        self.sound_file = get_resource_path('resources/sound/error_sound.mp3')

    def run(self):
        try:
            if not os.path.exists(self.sound_file):
                return
            self._has_run = True
            audio_output = QtMultimedia.QAudioOutput()
            self.player = QtMultimedia.QMediaPlayer()
            self.player.setAudioOutput(audio_output)
            self.player.setSource(QtCore.QUrl.fromLocalFile(self.sound_file))
            self.player.mediaStatusChanged.connect(self._on_media_status_changed)
            self.player.play()

            loop = QtCore.QEventLoop()
            self.finished.connect(loop.quit)
            loop.exec()
        except Exception as e:
            log("ERROR", f"{str(e)}")

    def _on_media_status_changed(self, status):
        if status == QtMultimedia.QMediaPlayer.MediaStatus.EndOfMedia:
            self.finished.emit()
            if self.player:
                self.player.stop()
