import os
import sys
from datetime import datetime

import requests
from PyQt6 import QtGui
from PyQt6.QtCore import Qt
from PyQt6.QtGui import QPixmap, QIcon
from PyQt6.QtWidgets import QDialog, QVBoxLayout, QLabel, QPushButton, QWidget
from bs4 import BeautifulSoup

main_window = None


def str_to_bool(value):
    """Convert a string representation of truth to true (True) or false (False)."""
    return value.lower() == 'true' if isinstance(value, str) else bool(value)


def get_current_time(mode='sys'):
    url = 'https://www.beijing-time.org/t/time.asp'
    headers = {
        "user-agent": "Mozilla/5.0 (Windows NT 10.0; WOW64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/80.0.3987.87 Safari/537.36 SE 2.X MetaSr 1.0"
    }

    def _fetch_network_time():
        try:
            response = requests.get(url=url, headers=headers, timeout=5)
            response.raise_for_status()

            js_vars = {}
            for line in response.text.splitlines():
                if '=' in line and not line.startswith('//') and not line.strip().startswith('function'):
                    parts = line.split('=', 1)
                    if len(parts) == 2:
                        key, value = parts
                        js_vars[key.strip()] = value.strip().strip(';').replace('"', '')

            required_keys = ['nyear', 'nmonth', 'nday', 'nwday', 'nhrs', 'nmin', 'nsec']
            if all(key in js_vars for key in required_keys):
                time_str = f"{js_vars['nyear']}-{int(js_vars['nmonth']):02d}-{int(js_vars['nday']):02d} {int(js_vars['nhrs']):02d}:{int(js_vars['nmin']):02d}:{int(js_vars['nsec']):02d}"
                network_time = datetime.strptime(time_str, '%Y-%m-%d %H:%M:%S')
                return network_time
            else:
                raise ValueError("Incomplete time information")

        except Exception:
            return None

    if mode == 'net':
        return _fetch_network_time()
    elif mode == 'sys':
        return datetime.now()
    elif mode == 'mix':
        network_time = _fetch_network_time()
        return network_time if network_time is not None else datetime.now()
    else:
        raise ValueError("Invalid mode specified")


def log(level, message):
    timestamp = get_current_time('mix').strftime("%m-%d %H:%M:%S")
    colors = {
        "INFO": "#691bfd",
        "WARNING": "#FFA500",
        "ERROR": "#FF0000",
        "DEBUG": "#00CC33"
    }
    color = colors.get(level, "#00CC33")
    formatted_message = f'<span style="color:{color}">[{timestamp}]: {message}</span>'
    main_window.log_textEdit.append(formatted_message)


def load_stylesheet(filename):
    script_dir = os.path.dirname(os.path.realpath(__file__))
    file_path = os.path.join(script_dir, 'resources', 'stylesheet', filename)

    try:
        with open(file_path, 'r', encoding='utf-8') as file:
            return file.read()
    except FileNotFoundError:
        return f"文件 {filename} 未找到。"


def get_resource_path(relative_path):
    try:
        base_path = sys._MEIPASS
    except Exception:
        base_path = os.path.abspath(".")
    return os.path.join(base_path, relative_path).replace(os.sep, '/')


def author():
    dialog = QDialog()
    dialog.setWindowTitle("联系开发者")
    dialog.setWindowIcon(QtGui.QIcon(get_resource_path('resources/img/tray.ico')))
    dialog.setWindowFlags(dialog.windowFlags() | Qt.WindowType.FramelessWindowHint)
    dialog.setAttribute(Qt.WidgetAttribute.WA_TranslucentBackground)
    dialog.setFixedSize(320, 450)

    container = QWidget(dialog)
    container.setStyleSheet(load_stylesheet("author.dialog.setStyleSheet.css"))
    container.setGeometry(0, 0, dialog.width(), dialog.height())

    layout = QVBoxLayout(container)

    qr_code_label = QLabel(container)
    resource_path = get_resource_path("resources/img/activity/QQ_Card.png")
    pixmap = QPixmap(resource_path)
    qr_code_label.setPixmap(pixmap)
    qr_code_label.setAlignment(Qt.AlignmentFlag.AlignCenter)

    confirm_button = QPushButton("手机QQ扫码·联系开发者", container)
    confirm_button.clicked.connect(dialog.accept)
    layout.addWidget(qr_code_label)
    layout.addWidget(confirm_button)

    close_button = QPushButton(container)
    close_button.setIcon(QIcon(get_resource_path("resources/img/窗口控制/窗口控制-关闭.svg")))
    close_button.setFixedSize(28, 28)
    close_button.move(container.width() - close_button.width() - 12, 6)
    close_button.clicked.connect(dialog.reject)
    close_button.setAttribute(Qt.WidgetAttribute.WA_TranslucentBackground)
    close_button.setStyleSheet(load_stylesheet("close_button.setStyleSheet.css"))

    dialog.exec()


def get_url():
    url = 'https://www.cnblogs.com/YangShengzhou/p/18611081'
    try:
        response = requests.get(url)
        response.raise_for_status()
        soup = BeautifulSoup(response.text, 'html.parser')
        post_body = soup.find('div', class_='postBody')

        if not post_body:
            return

        blog_content = post_body.get_text().strip()
        content_parts = blog_content.split('==')

        Key, update_content, notice_content = content_parts

        return Key, notice_content

    except Exception:
        return
