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
        if self.prevent_sleep:
            ctypes.windll.kernel32.SetThreadExecutionState(0x80000002)

        while not self.interrupted:
            if self.interrupted:
                break

            next_task = self.find_next_ready_task()
            if next_task is None:
                ctypes.windll.kernel32.SetThreadExecutionState(0x80000000 | 0x00000001)
                self.prevent_sleep = False
                self.app_instance.on_thread_finished()
                break

            task_time = datetime.strptime(next_task['time'], '%Y-%m-%dT%H:%M:%S')
            remaining_time = (task_time - get_current_time(self.current_time)).total_seconds()

            if remaining_time > 0:
                if self.interrupted:
                    break
                self.msleep(int(remaining_time * 1000))

            if self.interrupted:
                break

            name = next_task['name']
            info = next_task['info']

            if self.interrupted:
                break

            if os.path.isfile(info):
                file_name = os.path.basename(info)
                log("INFO", f"开始把文件 {file_name} 发给 {name}")
                if self.interrupted:
                    break
                self.app_instance.wx.SendFiles(filepath=info, who=name)
            elif info == 'Video_chat':
                log("INFO", f"开始与 {name} 视频通话")
                if self.interrupted:
                    break
                self.app_instance.wx.VideoCall(who=name)
            else:
                log("INFO", f"开始把 {info[:25] + '……' if len(info) > 25 else info} 发给 {name[:8]}")
                if self.interrupted:
                    break
                self.app_instance.wx.SendMsg(msg=info, who=name)

            if self.interrupted:
                break

            log("DEBUG", f"成功把 {info[:25] + '……' if len(info) > 25 else info} 发给 {name[:8]} ")
            self.app_instance.update_task_status(next_task, '成功')

            while not self.interrupted and self.is_paused:
                self.msleep(50)
            if self.interrupted:
                break

        if self.prevent_sleep:
            ctypes.windll.kernel32.SetThreadExecutionState(0x80000000 | 0x00000001)
            self.prevent_sleep = False

    def find_next_ready_task(self):
        next_task = None
        min_time = None
        for task in self.app_instance.ready_tasks:
            try:
                task_time = QtCore.QDateTime.fromString(task['time'], "yyyy-MM-ddTHH:mm:ss").toSecsSinceEpoch()
                if min_time is None or task_time < min_time:
                    min_time = task_time
                    next_task = task
            except Exception as e:
                log("ERROR", f"{str(e)}")
        return next_task

    def requestInterruption(self):
        self.interrupted = True


import os
from PyQt6 import QtCore, QtMultimedia

class ErrorSoundThread(QtCore.QThread):
    finished = QtCore.pyqtSignal()
    _is_playing = False

    def __init__(self):
        super().__init__()
        self.sound_file = None
        self.player = None

    def update_sound_file(self, sound_file_path):
        self.sound_file = sound_file_path

    def run(self):
        if not self.sound_file or not os.path.exists(self.sound_file) or self._is_playing:
            return
        self._is_playing = True
        audio_output = QtMultimedia.QAudioOutput()
        self.player = QtMultimedia.QMediaPlayer()
        self.player.setAudioOutput(audio_output)
        self.player.setSource(QtCore.QUrl.fromLocalFile(self.sound_file))
        self.player.mediaStatusChanged.connect(self._on_media_status_changed)
        self.player.play()
        loop = QtCore.QEventLoop()
        self.finished.connect(loop.quit)
        loop.exec()

    def _on_media_status_changed(self, status):
        if status == QtMultimedia.QMediaPlayer.MediaStatus.EndOfMedia:
            self.finished.emit()
            if self.player:
                self.player.stop()
                self._is_playing = False

    def stop_playback(self):
        if self.player and self._is_playing:
            self.player.stop()
            self._is_playing = False
            self.finished.emit()

    def play_test(self):
        if self._is_playing:
            self.stop_playback()
        else:
            self.start()
