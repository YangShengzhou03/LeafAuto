from PyQt6 import QtWidgets, QtGui


class CenteredComboBox(QtWidgets.QComboBox):
    def __init__(self, parent=None):
        super().__init__(parent)
        self.setEditable(False)
        fixed_width = 80
        self.setMinimumWidth(fixed_width)
        self.setMaximumWidth(fixed_width)
        self.setFixedWidth(fixed_width)
        self.setStyleSheet("""
            QComboBox {
                color: #000000;
                background-color: #FFFFFF;
                border: none;
                border-radius: none;
                padding: 1px 2px;
                font-size: 10pt;
                text-align: center;
            }
            QComboBox::drop-down {
                subcontrol-origin: padding;
                subcontrol-position: top right;
                width: 18px;
                border-left-width: 1px;
                border-left-color: #CCCCCC;
                border-left-style: solid;
                border-top-right-radius: 4px;
                border-bottom-right-radius: 4px;
            }
            QComboBox::down-arrow {
                image: url(:/images/down_arrow.png);
                width: 12px;
                height: 12px;
            }
            QComboBox QAbstractItemView {
                background-color: #FFFFFF;
                selection-background-color: #E0E0E0;
                selection-color: #000000;
                border: none;
                border-radius: 0px;
            }
            QComboBox QAbstractItemView::item {
                padding: 4px;
                min-height: 12px;
                text-align: center;
            }
        """)

    def paintEvent(self, event):
        painter = QtWidgets.QStylePainter(self)
        option = QtWidgets.QStyleOptionComboBox()
        self.initStyleOption(option)
        text = self.currentText()
        font = QtGui.QFont("微软雅黑 Light", 10)
        painter.setFont(font)
        metrics = QtGui.QFontMetrics(font)
        rect = self.rect()
        text_width = metrics.horizontalAdvance(text)
        text_height = metrics.height()
        x = (rect.width() - text_width) // 2
        y = (rect.height() + text_height) // 2
        painter.setPen(QtGui.QColor("#ffffff"))
        painter.drawText(x, y, text)
