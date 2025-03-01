import requests
from PyQt6 import QtWidgets, QtCore
from PyQt6.QtCore import QUrl
from PyQt6.QtGui import QDesktopServices
from bs4 import BeautifulSoup

from System_info import read_key_value
from UI_UpdateDialog import Ui_UpdateDialog


def check_update():
    url = 'https://www.cnblogs.com/YangShengzhou/p/18611081'
    try:
        response = requests.get(url, timeout=3)
        response.raise_for_status()
        soup = BeautifulSoup(response.text, 'html.parser')
        title_element = soup.find('a', class_='postTitle2')
        post_body = soup.find('div', class_='postBody')
        if not title_element or not post_body:
            return 1
        title = title_element.text.strip()
        blog_content = post_body.get_text().strip()
        title_parts = title.split('==')
        content_parts = blog_content.split('==')
        if len(title_parts) != 3:
            return 1
        title_str, latest_version_str, update_link = title_parts
        key, update_content, information = content_parts
        lastlyVersion = float(latest_version_str.strip())
        lastlyVersionUrl = update_link.strip()
        current_version = float(read_key_value('version'))
        if lastlyVersion > current_version:
            if int(lastlyVersion) == int(current_version):
                necessary = False
            else:
                necessary = True
            dialog = UpdateDialog(url=lastlyVersionUrl, title=title_str, content=update_content, necessary=necessary)
            dialog.exec_()
        else:
            return 0
    except Exception:
        return 1


class UpdateDialog(QtWidgets.QDialog):
    def __init__(self, parent=None, url=None, title=None, content=None, necessary=False):
        super(UpdateDialog, self).__init__(parent)
        self.ui = Ui_UpdateDialog()
        self.ui.setupUi(self)
        self.setWindowFlags(QtCore.Qt.WindowType.FramelessWindowHint)
        self.setAttribute(QtCore.Qt.WidgetAttribute.WA_TranslucentBackground)
        self.dialogTitle = title
        self.lastlyVersionUrl = url
        self.content = content
        self.necessary = necessary
        if necessary:
            self.ui.pushButton_cancel.hide()
        self.ui.label_title.setText(self.dialogTitle)
        self.ui.label_content.setText(self.content)
        self.ui.pushButton_cancel.clicked.connect(self.reject)
        self.ui.pushButton_download.clicked.connect(self.accept_download)

    def accept_download(self):
        QDesktopServices.openUrl(QUrl(self.lastlyVersionUrl))
        exit(0)
