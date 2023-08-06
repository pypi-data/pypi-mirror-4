#!/usr/bin/python
#coding=utf-8

import sys
import time

from os import path

root = path.abspath(path.pardir)
if root not in sys.path:
    sys.path.append(root)


__version__ = '0.1.0'
__author__ = 'Daniel Black <danielblack@danielblack.name>'
__depends__ = ['PyQt4', ]


from PyQt4.QtGui import QApplication
from PyQt4.QtGui import QBrush
from PyQt4.QtGui import QLabel
from PyQt4.QtGui import QPainter
from PyQt4.QtGui import QPen
from PyQt4.QtGui import QPixmap
from PyQt4.QtGui import QMessageBox
from PyQt4.QtGui import QWidget

from PyQt4.QtCore import Qt
from PyQt4.QtCore import QPoint
from PyQt4.QtCore import QRect
from PyQt4.QtCore import QString
from PyQt4.QtCore import pyqtSignal

import settings


class CutterWindow(QWidget):
    '''
    Main cutter window
    '''

    # Default scale ratio of the display of paint label
    SCALE_RATIO = 0.9


    def __init__(self, parent=None):
        super(CutterWindow, self).__init__(parent)
        self.shot = self.get_shot()
        self.shot_label = ShotLabel(self.shot, self)
        self.init_window()
        self.init_connect()

    def init_connect(self):
        self.shot_label.error_signal.connect(self.error_slot)
        self.shot_label.succ_signal.connect(self.succ_slot)

    def init_window(self):
        '''
        Initialize the cutter window without the title pane
        '''
        self.setWindowFlags(Qt.FramelessWindowHint)
        #self.setWindowOpacity(0.5)
        self.showMaximized()

        self.adjust_label()
        
    def adjust_label(self):
        desktop = QApplication.desktop()
        rect = desktop.screenGeometry()
        self.shot_label.move(
                rect.width() * (1 - self.SCALE_RATIO) / 2.0,
                rect.height() * (1 - self.SCALE_RATIO) / 2.0,
        )

    def error_slot(self, error):
        '''
        General error slot
        '''
        QMessageBox.warning(self, QString("Error"), 
                error.message)
        self.close()

    def succ_slot(self):
        self.close()


    def get_shot(self):
        '''
        Get the scaled window
        '''
        return self._get_full_shot()

    @staticmethod
    def _get_full_shot():
        '''
        Get the full screen shot for the current screen
        '''
        desktop = QApplication.desktop().winId()
        return QPixmap.grabWindow(desktop)



class ShotLabel(QLabel):
    '''
    Label for displaying the screen shot
    '''
    
    succ_signal = pyqtSignal()
    error_signal = pyqtSignal(Exception, name='error_signal')

    def __init__(self, shot, parent=None):
        super(ShotLabel, self).__init__(parent)
        self.full_shot = shot
        self.shot = self._scale_pixmap(shot, CutterWindow.SCALE_RATIO)
        self._fill_shot()
        self.x1 = self.y1 = None
        self.x2 = self.y2 = None
        self.tracing = False

    def paintEvent(self, event):
        '''
        Paint the selected rectangle if possible
        '''
        painter = QPainter(self)
        painter.setPen(QPen(Qt.white, 2, Qt.SolidLine, Qt.RoundCap))

        painter.drawPixmap(0, 0, self.shot)
        if self.x1:
            painter.drawLine(self.x1, self.y1, self.x1, self.y2)
            painter.drawLine(self.x1, self.y1, self.x2, self.y1)
            painter.drawLine(self.x1, self.y2, self.x2, self.y2)
            painter.drawLine(self.x2, self.y2, self.x2, self.y1)
            p = QPoint(self.x2, self.y2)
            s = QString("%d x %d" % 
                    (abs(self.x1 - self.x2), abs(self.y1 - self.y2)))
            painter.drawText(p, s)
        
        
    def mouseMoveEvent(self, event):
        '''
        Track the mouse when it is pressed and moving
        then update the label
        '''
        x, y = event.x(), event.y()
        if not self.tracing:
            self.x1, self.y1 = x, y
            self.tracing = True
        if self.x1 is None:
            self.x1, self.x2 = x, y
        self.x2, self.y2 = x, y
        self.update()

    def mouseReleaseEvent(self, event):
        self.tracing = False

    def mouseDoubleClickEvent(self, event):
        '''
        If mouse is in the selected area,
        save the shortcut
        '''
        if self._in_selected_range(event.x(), event.y()):
        # Mouse click in the selected area
            try:
                self.save_shot(self._get_sub_shot())
            except IOError as e:
                self.emit(SIGNAL(e))
            else:
                self.succ_signal.emit()
        else:
        # Mouse click out the selected range
            self.x1, self.y1 = None, None


    def save_shot(self, shot):
        '''
        Save the pixmap to the default path,
        the file name is using the timestamp
        '''
        save_path = path.join(settings.DEFAULT_PATH, 
                str(int(time.time())) + ".png")
        succ = shot.save(save_path, "PNG", settings.QUALITY)
        if not succ:
            raise IOError(u"Error to save file to %s" % save_path)
        

    def _in_selected_range(self, x, y):
        '''
        Determine the click point in the selected range or not
        '''
        if not self.x1:
            return False
        min_x, max_x = min(self.x1, self.x2), max(self.x1, self.x2)
        min_y, max_y = min(self.y1, self.y2), max(self.y1, self.y2)
        if x in range(min_x, max_x) and y in range(min_y, max_y):
            return True
        return False

    def _get_sub_shot(self):
        '''
        Get the cutted original shot
        '''
        return self.full_shot.copy(
                min(self.x1, self.x2) / CutterWindow.SCALE_RATIO ,
                min(self.y1, self.y2) / CutterWindow.SCALE_RATIO,
                abs(self.x1 - self.x2) / CutterWindow.SCALE_RATIO,
                abs(self.y1 - self.y2) / CutterWindow.SCALE_RATIO,
        )

    def _fill_shot(self):
        '''
        Fill up the label with the screen shot
        Auto adjust the size to the custom screen length-width ratio
        '''
        self.setPixmap(self.shot)

    @staticmethod
    def _scale_pixmap(shot, ratio):
        '''
        Static method for scaling the pixmap
        '''
        assert(ratio <= 1)

        # get the desktop size rectangle
        desktop = QApplication.desktop()
        rect = desktop.screenGeometry()

        # Adjust the size of the pixmap
        return shot.scaled(
                rect.width() * ratio,
                rect.height() * ratio,
                transformMode = Qt.SmoothTransformation,
        )
        

def start_window():
    '''
    Set up the window
    '''
    app = QApplication(sys.argv)
    window = CutterWindow()
    window.show()
    sys.exit(app.exec_())

if __name__ == '__main__':
    start_window()
