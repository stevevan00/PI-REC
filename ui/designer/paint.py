from PyQt5.QtGui import *
from PyQt5.QtWidgets import *
from PyQt5.QtCore import *

from PyQt5 import QtGui, QtWidgets, QtCore

from PyQt5.QtGui import QPainter, QBitmap, QPolygon, QPen, QBrush, QColor
from PyQt5.QtCore import Qt

from ui.designer.MainWindow import Ui_MainWindow
import os
import sys
import random
import types
import cv2
import numpy as np
try:
    # Include in try/except block if you're also targeting Mac/Linux
    from PyQt5.QtWinExtras import QtWin
    myappid = 'com.learnpyqt.minute-apps.paint'
    QtWin.setCurrentProcessExplicitAppUserModelID(myappid)    
except ImportError:
    pass


BRUSH_MULT = 3
SPRAY_PAINT_MULT = 5
SPRAY_PAINT_N = 100

COLORS = [
    '#000000', '#82817f', '#820300', '#868417', '#007e03', '#037e7b', '#040079',
    '#81067a', '#7f7e45', '#05403c', '#0a7cf6', '#093c7e', '#7e07f9', '#7c4002',

    '#ffffff', '#c1c1c1', '#f70406', '#fffd00', '#08fb01', '#0bf8ee', '#0000fa',
    '#b92fc2', '#fffc91', '#00fd83', '#87f9f9', '#8481c4', '#dc137d', '#fb803c',
]

FONT_SIZES = [7, 8, 9, 10, 11, 12, 13, 14, 18, 24, 36, 48, 64, 72, 96, 144, 288]

MODES = [
    'selectpoly', 'selectrect',
    'eraser','pen','ellipse',
    'dropper',
     'brush',
    # 'spray','line', 'rect',
    
]

CANVAS_DIMENSIONS = 176, 176

STAMPS = [
    './temp/color_domain.png',
    './temp/sketch.png',
    # ':/stamps/pie-cherry.png',
    # ':/stamps/pie-cherry2.png',
    # ':/stamps/pie-lemon.png',
    # ':/stamps/pie-moon.png',
    # ':/stamps/pie-pork.png',
    # ':/stamps/pie-pumpkin.png',
    # ':/stamps/pie-walnut.png',
]

SELECTION_PEN = QPen(QColor(Qt.white), 1, Qt.DashLine)
PREVIEW_PEN = QPen(QColor(Qt.white), 1, Qt.SolidLine)


def build_font(config):
    """
    Construct a complete font from the configuration options
    :param self:
    :param config:
    :return: QFont
    """
    font = config['font']
    font.setPointSize(config['fontsize'])
    font.setBold(config['bold'])
    font.setItalic(config['italic'])
    font.setUnderline(config['underline'])
    return font


class Canvas(QLabel):

    mode = 'rectangle'

    primary_color = QColor(Qt.black)
    secondary_color = None

    primary_color_updated = pyqtSignal(str)
    secondary_color_updated = pyqtSignal(str)

    # Store configuration settings, including pen width, fonts etc.
    config = {
        # Drawing options.
        'size': 1,
        'move_pixel': 5,
        'fill': False,
        # Font options.
        'font': QFont('Times'),
        'fontsize': 12,
        'bold': False,
        'italic': False,
        'underline': False,
    }

    active_color = None
    preview_pen = None

    timer_event = None
    select_shape = None
    current_stamp = None

    def initialize(self):
        self.background_color = QColor(self.secondary_color) if self.secondary_color else QColor(Qt.white)
        # self.eraser_color = QColor(self.secondary_color) if self.secondary_color else QColor(Qt.white)
        self.eraser_color = QColor(self.secondary_color) if self.secondary_color else QColor(Qt.black)
        self.eraser_color.setAlpha(100)
        # self.reset()

    def reset(self):
        # Create the pixmap for display.
        self.setPixmap(QPixmap(*CANVAS_DIMENSIONS))

        # Clear the canvas.
        self.pixmap().fill(self.background_color)

    def set_primary_color(self, hex):
        self.primary_color = QColor(hex)

    def set_secondary_color(self, hex):
        self.secondary_color = QColor(hex)

    def set_config(self, key, value):
        self.config[key] = value

    def set_mode(self, mode):
        # Clean up active timer animations.
        self.timer_cleanup()
        # Reset mode-specific vars (all)
        self.active_shape_fn = None
        self.active_shape_args = ()

        self.origin_pos = None

        self.current_pos = None
        self.last_pos = None

        self.history_pos = None
        self.last_history = []

        self.current_text = ""
        self.last_text = ""

        self.last_config = {}

        self.dash_offset = 0
        self.locked = False
        # Apply the mode
        self.mode = mode
        self.select_shape = None

    def reset_mode(self):
        self.set_mode(self.mode)

    def on_timer(self):
        if self.timer_event:
            self.timer_event()

    def timer_cleanup(self):
        if self.timer_event:
            # Stop the timer, then trigger cleanup.
            timer_event = self.timer_event
            self.timer_event = None
            timer_event(final=True)

    # Mouse events.

    def mousePressEvent(self, e):
        fn = getattr(self, "%s_mousePressEvent" % self.mode, None)
        if fn:
            return fn(e)

    def mouseMoveEvent(self, e):
        fn = getattr(self, "%s_mouseMoveEvent" % self.mode, None)
        if fn:
            return fn(e)

    def mouseReleaseEvent(self, e):
        fn = getattr(self, "%s_mouseReleaseEvent" % self.mode, None)
        if fn:
            return fn(e)

    def mouseDoubleClickEvent(self, e):
        fn = getattr(self, "%s_mouseDoubleClickEvent" % self.mode, None)
        if fn:
            return fn(e)

    # Generic events (shared by brush-like tools)

    def generic_mousePressEvent(self, e):
        self.last_pos = e.pos()

        if e.button() == Qt.LeftButton:
            self.active_color = self.primary_color
        else:
            self.active_color = self.secondary_color

    def generic_mouseReleaseEvent(self, e):
        self.last_pos = None

    # Mode-specific events.

    # Select polygon events

    def selectpoly_mousePressEvent(self, e):
        if not self.locked or e.button == Qt.RightButton:
            self.active_shape_fn = 'drawPolygon'
            self.preview_pen = SELECTION_PEN
            self.generic_poly_mousePressEvent(e)

    def selectpoly_timerEvent(self, final=False):
        self.generic_poly_timerEvent(final)

    def selectpoly_mouseMoveEvent(self, e):
        if not self.locked:
            self.generic_poly_mouseMoveEvent(e)

    def selectpoly_mouseDoubleClickEvent(self, e):
        self.current_pos = e.pos()
        self.locked = True

    def selectpoly_copy(self):
        """
        Copy a polygon region from the current image, returning it.

        Create a mask for the selected area, and use it to blank
        out non-selected regions. Then get the bounding rect of the
        selection and crop to produce the smallest possible image.

        :return: QPixmap of the copied region.
        """
        self.timer_cleanup()

        pixmap = self.pixmap().copy()
        bitmap = QBitmap(*CANVAS_DIMENSIONS)
        bitmap.clear()  # Starts with random data visible.

        p = QPainter(bitmap)
        # Construct a mask where the user selected area will be kept, 
        # the rest removed from the image is transparent.
        userpoly = QPolygon(self.history_pos + [self.current_pos])
        p.setPen(QPen(Qt.color1))
        p.setBrush(QBrush(Qt.color1))  # Solid color, Qt.color1 == bit on.
        p.drawPolygon(userpoly)
        p.end()

        # Set our created mask on the image.
        pixmap.setMask(bitmap)

        # Calculate the bounding rect and return a copy of that region.
        return pixmap.copy(userpoly.boundingRect())

    # Select rectangle events

    def selectrect_mousePressEvent(self, e):
        self.active_shape_fn = 'drawRect'
        self.preview_pen = SELECTION_PEN
        self.generic_shape_mousePressEvent(e)

    def selectrect_timerEvent(self, final=False):
        self.generic_shape_timerEvent(final)

    def selectrect_mouseMoveEvent(self, e):
        if not self.locked:
            self.current_pos = e.pos()

    def selectrect_mouseReleaseEvent(self, e):
        self.current_pos = e.pos()
        self.locked = True

    def selectrect_copy(self):
        """
        Copy a rectangle region of the current image, returning it.

        :return: QPixmap of the copied region.
        """
        # self.timer_cleanup()
        return self.pixmap().copy(QRect(self.origin_pos, self.current_pos))

    # Eraser events

    def eraser_mousePressEvent(self, e):
        self.generic_mousePressEvent(e)

    def eraser_mouseMoveEvent(self, e):
        if self.last_pos:
            p = QPainter(self.pixmap())
            p.setPen(QPen(self.eraser_color, 10, Qt.SolidLine, Qt.RoundCap, Qt.RoundJoin))
            p.drawLine(self.last_pos, e.pos())

            self.last_pos = e.pos()
            self.update()

    def eraser_mouseReleaseEvent(self, e):
        self.generic_mouseReleaseEvent(e)

    # Stamp (pie) events

    def stamp_mousePressEvent(self, e):
        p = QPainter(self.pixmap())
        stamp = self.current_stamp
        p.drawPixmap(e.x() - stamp.width() // 2, e.y() - stamp.height() // 2, stamp)
        self.update()

    # Pen events

    def pen_mousePressEvent(self, e):
        self.generic_mousePressEvent(e)

    def pen_mouseMoveEvent(self, e):
        if self.last_pos:
            p = QPainter(self.pixmap())
            p.setPen(QPen(self.active_color, self.config['size'], Qt.SolidLine, Qt.SquareCap, Qt.RoundJoin))
            p.drawLine(self.last_pos, e.pos())

            self.last_pos = e.pos()
            self.update()

    def pen_mouseReleaseEvent(self, e):
        self.generic_mouseReleaseEvent(e)

    # Brush events

    def brush_mousePressEvent(self, e):
        self.generic_mousePressEvent(e)

    def brush_mouseMoveEvent(self, e):
        if self.last_pos:
            p = QPainter(self.pixmap())
            p.setPen(QPen(self.active_color, self.config['size'] * BRUSH_MULT, Qt.SolidLine, Qt.RoundCap, Qt.RoundJoin))
            p.drawLine(self.last_pos, e.pos())

            self.last_pos = e.pos()
            self.update()

    def brush_mouseReleaseEvent(self, e):
        self.generic_mouseReleaseEvent(e)

    # Spray events

    def spray_mousePressEvent(self, e):
        self.generic_mousePressEvent(e)

    def spray_mouseMoveEvent(self, e):
        if self.last_pos:
            p = QPainter(self.pixmap())
            p.setPen(QPen(self.active_color, 1))

            for n in range(self.config['size'] * SPRAY_PAINT_N):
                xo = random.gauss(0, self.config['size'] * SPRAY_PAINT_MULT)
                yo = random.gauss(0, self.config['size'] * SPRAY_PAINT_MULT)
                p.drawPoint(e.x() + xo, e.y() + yo)

        self.update()

    def spray_mouseReleaseEvent(self, e):
        self.generic_mouseReleaseEvent(e)

    # Text events

    def keyPressEvent(self, event):
        if self.mode == 'selectrect':
            move = self.config['move_pixel']
            if event.key() == QtCore.Qt.Key_W:
                print('W Press')
                self.copy_to_clipboard(0, move * -1)
            elif event.key() == QtCore.Qt.Key_S:
                print('S Press')
                self.copy_to_clipboard(0, move)
            elif event.key() == QtCore.Qt.Key_A:
                print('A Press')
                self.copy_to_clipboard(move * -1, 0)
            elif event.key() == QtCore.Qt.Key_D:
                print('D Press')
                self.copy_to_clipboard(move, 0)
            elif event.key() == QtCore.Qt.Key_Q:
                self.set_mode('selectrect')
            
    def text_mousePressEvent(self, e):
        if e.button() == Qt.LeftButton and self.current_pos is None:
            self.current_pos = e.pos()
            self.current_text = ""
            self.timer_event = self.text_timerEvent

        elif e.button() == Qt.LeftButton:

            self.timer_cleanup()
            # Draw the text to the image
            p = QPainter(self.pixmap())
            p.setRenderHints(QPainter.Antialiasing)
            font = build_font(self.config)
            p.setFont(font)
            pen = QPen(self.primary_color, 1, Qt.SolidLine, Qt.RoundCap, Qt.RoundJoin)
            p.setPen(pen)
            p.drawText(self.current_pos, self.current_text)
            self.update()

            self.reset_mode()

        elif e.button() == Qt.RightButton and self.current_pos:
            self.reset_mode()

    def text_timerEvent(self, final=False):
        p = QPainter(self.pixmap())
        p.setCompositionMode(QPainter.RasterOp_SourceXorDestination)
        pen = PREVIEW_PEN
        p.setPen(pen)
        if self.last_text:
            font = build_font(self.last_config)
            p.setFont(font)
            p.drawText(self.current_pos, self.last_text)

        if not final:
            font = build_font(self.config)
            p.setFont(font)
            p.drawText(self.current_pos, self.current_text)

        self.last_text = self.current_text
        self.last_config = self.config.copy()
        self.update()

    # Fill events

    def fill_mousePressEvent(self, e):

        if e.button() == Qt.LeftButton:
            self.active_color = self.primary_color
        else:
            self.active_color = self.secondary_color

        image = self.pixmap().toImage()
        w, h = image.width(), image.height()
        x, y = e.x(), e.y()

        # Get our target color from origin.
        target_color = image.pixel(x,y)

        have_seen = set()
        queue = [(x, y)]

        def get_cardinal_points(have_seen, center_pos):
            points = []
            cx, cy = center_pos
            for x, y in [(1, 0), (0, 1), (-1, 0), (0, -1)]:
                xx, yy = cx + x, cy + y
                if (xx >= 0 and xx < w and
                    yy >= 0 and yy < h and
                    (xx, yy) not in have_seen):

                    points.append((xx, yy))
                    have_seen.add((xx, yy))

            return points

        # Now perform the search and fill.
        p = QPainter(self.pixmap())
        p.setPen(QPen(self.active_color))

        while queue:
            x, y = queue.pop()
            if image.pixel(x, y) == target_color:
                p.drawPoint(QPoint(x, y))
                queue.extend(get_cardinal_points(have_seen, (x, y)))

        self.update()

    # Dropper events

    def dropper_mousePressEvent(self, e):
        c = self.pixmap().toImage().pixel(e.pos())
        hex = QColor(c).name()

        if e.button() == Qt.LeftButton:
            self.set_primary_color(hex)
            self.primary_color_updated.emit(hex)  # Update UI.

        elif e.button() == Qt.RightButton:
            self.set_secondary_color(hex)
            self.secondary_color_updated.emit(hex)  # Update UI.

    # Generic shape events: Rectangle, Ellipse, Rounded-rect

    def generic_shape_mousePressEvent(self, e):
        self.origin_pos = e.pos()
        self.current_pos = e.pos()
        self.timer_event = self.generic_shape_timerEvent

    def generic_shape_timerEvent(self, final=False):
        p = QPainter(self.pixmap())
        p.setCompositionMode(QPainter.RasterOp_SourceXorDestination)
        pen = self.preview_pen
        pen.setDashOffset(self.dash_offset)
        p.setPen(pen)
        if self.last_pos:
            getattr(p, self.active_shape_fn)(QRect(self.origin_pos, self.last_pos), *self.active_shape_args)

        if not final:
            self.dash_offset -= 1
            pen.setDashOffset(self.dash_offset)
            p.setPen(pen)
            getattr(p, self.active_shape_fn)(QRect(self.origin_pos, self.current_pos), *self.active_shape_args)

        self.update()
        self.last_pos = self.current_pos

    def generic_shape_mouseMoveEvent(self, e):
        self.current_pos = e.pos()

    def generic_shape_mouseReleaseEvent(self, e):
        if self.last_pos:
            # Clear up indicator.
            self.timer_cleanup()

            p = QPainter(self.pixmap())
            # p.setPen(QPen(self.primary_color, self.config['size'], Qt.SolidLine, Qt.SquareCap, Qt.MiterJoin))
            p.setPen(QPen(QColor(Qt.white), self.config['size'], Qt.SolidLine, Qt.SquareCap, Qt.MiterJoin))

            if self.config['fill']:
                p.setBrush(QBrush(self.secondary_color))
            getattr(p, self.active_shape_fn)(QRect(self.origin_pos, e.pos()), *self.active_shape_args)
            self.update()

        self.reset_mode()

    # Line events

    def line_mousePressEvent(self, e):
        self.origin_pos = e.pos()
        self.current_pos = e.pos()
        self.preview_pen = PREVIEW_PEN
        self.timer_event = self.line_timerEvent

    def line_timerEvent(self, final=False):
        p = QPainter(self.pixmap())
        p.setCompositionMode(QPainter.RasterOp_SourceXorDestination)
        pen = self.preview_pen
        p.setPen(pen)
        if self.last_pos:
            p.drawLine(self.origin_pos, self.last_pos)

        if not final:
            p.drawLine(self.origin_pos, self.current_pos)

        self.update()
        self.last_pos = self.current_pos

    def line_mouseMoveEvent(self, e):
        self.current_pos = e.pos()

    def line_mouseReleaseEvent(self, e):
        if self.last_pos:
            # Clear up indicator.
            self.timer_cleanup()

            p = QPainter(self.pixmap())
            p.setPen(QPen(self.primary_color, self.config['size'], Qt.SolidLine, Qt.RoundCap, Qt.RoundJoin))

            p.drawLine(self.origin_pos, e.pos())
            self.update()

        self.reset_mode()

    # Generic poly events
    def generic_poly_mousePressEvent(self, e):
        if e.button() == Qt.LeftButton:
            if self.history_pos:
                self.history_pos.append(e.pos())
            else:
                self.history_pos = [e.pos()]
                self.current_pos = e.pos()
                self.timer_event = self.generic_poly_timerEvent

        elif e.button() == Qt.RightButton and self.history_pos:
            # Clean up, we're not drawing
            self.timer_cleanup()
            self.reset_mode()

    def generic_poly_timerEvent(self, final=False):
        p = QPainter(self.pixmap())
        p.setCompositionMode(QPainter.RasterOp_SourceXorDestination)
        pen = self.preview_pen
        pen.setDashOffset(self.dash_offset)
        p.setPen(pen)
        if self.last_history:
            getattr(p, self.active_shape_fn)(*self.last_history)

        if not final:
            self.dash_offset -= 1
            pen.setDashOffset(self.dash_offset)
            p.setPen(pen)
            getattr(p, self.active_shape_fn)(*self.history_pos + [self.current_pos])

        self.update()
        self.last_pos = self.current_pos
        self.last_history = self.history_pos + [self.current_pos]

    def generic_poly_mouseMoveEvent(self, e):
        self.current_pos = e.pos()

    def generic_poly_mouseDoubleClickEvent(self, e):
        self.timer_cleanup()
        p = QPainter(self.pixmap())
        p.setPen(QPen(self.primary_color, self.config['size'], Qt.SolidLine, Qt.RoundCap, Qt.RoundJoin))

        # Note the brush is ignored for polylines.
        if self.secondary_color:
            p.setBrush(QBrush(self.secondary_color))

        getattr(p, self.active_shape_fn)(*self.history_pos + [e.pos()])
        self.update()
        self.reset_mode()

    # Polyline events

    def polyline_mousePressEvent(self, e):
        self.active_shape_fn = 'drawPolyline'
        self.preview_pen = PREVIEW_PEN
        self.generic_poly_mousePressEvent(e)

    def polyline_timerEvent(self, final=False):
        self.generic_poly_timerEvent(final)

    def polyline_mouseMoveEvent(self, e):
        self.generic_poly_mouseMoveEvent(e)

    def polyline_mouseDoubleClickEvent(self, e):
        self.generic_poly_mouseDoubleClickEvent(e)

    # Rectangle events

    def rect_mousePressEvent(self, e):
        self.active_shape_fn = 'drawRect'
        self.active_shape_args = ()
        self.preview_pen = PREVIEW_PEN
        self.generic_shape_mousePressEvent(e)

    def rect_timerEvent(self, final=False):
        self.generic_shape_timerEvent(final)

    def rect_mouseMoveEvent(self, e):
        self.generic_shape_mouseMoveEvent(e)

    def rect_mouseReleaseEvent(self, e):
        self.generic_shape_mouseReleaseEvent(e)

    # Polygon events

    def polygon_mousePressEvent(self, e):
        self.active_shape_fn = 'drawPolygon'
        self.preview_pen = PREVIEW_PEN
        self.generic_poly_mousePressEvent(e)

    def polygon_timerEvent(self, final=False):
        self.generic_poly_timerEvent(final)

    def polygon_mouseMoveEvent(self, e):
        self.generic_poly_mouseMoveEvent(e)

    def polygon_mouseDoubleClickEvent(self, e):
        self.generic_poly_mouseDoubleClickEvent(e)

    # Ellipse events

    def ellipse_mousePressEvent(self, e):
        self.active_shape_fn = 'drawEllipse'
        self.active_shape_args = ()
        self.preview_pen = PREVIEW_PEN
        self.generic_shape_mousePressEvent(e)

    def ellipse_timerEvent(self, final=False):
        self.generic_shape_timerEvent(final)

    def ellipse_mouseMoveEvent(self, e):
        self.generic_shape_mouseMoveEvent(e)

    def ellipse_mouseReleaseEvent(self, e):
        self.generic_shape_mouseReleaseEvent(e)

    # Roundedrect events

    def roundrect_mousePressEvent(self, e):
        self.active_shape_fn = 'drawRoundedRect'
        self.active_shape_args = (25, 25)
        self.preview_pen = PREVIEW_PEN
        self.generic_shape_mousePressEvent(e)

    def roundrect_timerEvent(self, final=False):
        self.generic_shape_timerEvent(final)

    def roundrect_mouseMoveEvent(self, e):
        self.generic_shape_mouseMoveEvent(e)

    def roundrect_mouseReleaseEvent(self, e):
        self.generic_shape_mouseReleaseEvent(e)
        
    def copy_to_clipboard(self, move_x, move_y):
        # clipboard = QApplication.clipboard()

        if self.mode == 'selectrect' and self.locked:
            selectrect = self.selectrect_copy()
            # clipboard.setPixmap(selectrect)
            selectrect.save('./temp/sketch_crop.png', "PNG")
            sketch = cv2.imread('./temp/sketch.png')
            sketch_crop = cv2.imread('./temp/sketch_crop.png')
            x1, y1 = self.origin_pos.x(), self.origin_pos.y()
            x2, y2 = self.current_pos.x(), self.current_pos.y()
            w, h, c = sketch_crop.shape
            sketch_crop = sketch_crop[:(y2-y1), :(x2-x1)]
            
            w, h, c = sketch_crop.shape
            
            sketch[y1:y1+w, x1:x1+h] = np.zeros((w, h, c))
            if move_x > 0:
                new_x2 = x2+move_x if x2+move_x <= 176 else 176
                new_x1 = new_x2 - h
            elif move_x <= 0:
                new_x1 = x1+move_x if x1+move_x >= 0 else 0
                new_x2 = new_x1 + h
            else:
                new_x1, new_x2 = x1, x2
                
            if move_y > 0:
                new_y2 = y2+move_y if y2+move_y <= 176 else 176
                new_y1 = new_y2 - w
            elif move_y <= 0:
                new_y1 = y1+move_y if y1+move_y >= 0 else 0
                new_y2 = new_y1 + w 
            else:
                new_y1, new_y2 = y1, y2
                
            # new_y1, new_y2, new_x1, new_x2 = new_y1-1, new_y2-1, new_x1-1, new_x2-1
            sketch[new_y1:new_y2, new_x1:new_x2] = sketch_crop
            cv2.imwrite('./temp/sketch.png', sketch)
            self.setPixmap(QPixmap('./temp/sketch.png'))
            self.origin_pos.setX(new_x1)
            self.origin_pos.setY(new_y1)
            self.current_pos.setX(new_x2)
            self.current_pos.setY(new_y2)

class DesignerWindow(QMainWindow, Ui_MainWindow):

    _signal = QtCore.pyqtSignal(str)
    # mode == 0 -> sketch, 1 -> color
    def __init__(self,mode, *args, **kwargs):
        super(DesignerWindow, self).__init__(*args, **kwargs)
        self.setupUi(self)
        self.mode = mode
        self.path = None
        # Replace canvas placeholder from QtDesigner.
        self.verticalLayout_3.removeWidget(self.canvas)
        if self.mode == 0:
            self.label.setText('NOTE!\nFor Selection Only\nPress W: move up\nPress S: move down\nPress A: move left\nPress D: move right\nSelection will never stop until change button mode (left side) or Press Q')
        self.showSketch = False
        self.firstTime = True
        # self.verticalLayout_100 = QtWidgets.QVBoxLayout(self.horizontalLayout)
        # self.verticalLayout_100.setContentsMargins(0, 0, 0, 0)
        # self.verticalLayout_100.setObjectName("verticalLayout_100")
        self.canvas = Canvas()
        self.canvas.initialize()
        self.canvas.setMaximumHeight(176)
        self.canvas.setMaximumWidth(176)
        # We need to enable mouse tracking to follow the mouse without the button pressed.
        self.canvas.setMouseTracking(True)
        # Enable focus to capture key inputs.
        self.canvas.setFocusPolicy(Qt.StrongFocus)
        # self.canvas.setGeometry(QtCore.QRect(115, 0, 176,176))
        self.verticalLayout_3.insertWidget(0, self.canvas)
        # self.fileToolbar.hide()
        self.actionNewImage.setVisible(False)
        self.actionOpenImage.setVisible(False)
        self.menuBar.hide()

        # Setup the mode buttons
        mode_group = QButtonGroup(self)
        mode_group.setExclusive(True)

        for mode in MODES:
            btn = getattr(self, '%sButton' % mode)
            btn.pressed.connect(lambda mode=mode: self.canvas.set_mode(mode))
            mode_group.addButton(btn)

        # Setup the color selection buttons.
        self.primaryButton.pressed.connect(lambda: self.choose_color(self.set_primary_color))
        self.secondaryButton.pressed.connect(lambda: self.choose_color(self.set_secondary_color))

        # Initialize button colours.
        self.stampButton.hide()
        self.textButton.hide()
        self.lineButton.hide()
        self.polylineButton.hide()
        self.rectButton.hide()
        self.polygonButton.hide()
        self.roundrectButton.hide()
        self.fillButton.hide()
        self.sprayButton.hide()
        if self.mode == 0:
            for n, hex in enumerate(COLORS, 1):
                btn = getattr(self, 'colorButton_%d' % n)
                btn.hide()
            self.dropperButton.hide()
            self.brushButton.hide()
            self.stampnextButton.hide()
        elif self.mode == 1:
            self.selectpolyButton.hide()
            self.selectrectButton.hide()
            self.penButton.hide()
            self.eraserButton.hide()
            self.ellipseButton.hide()
            
            for n, hex in enumerate(COLORS, 1):
                btn = getattr(self, 'colorButton_%d' % n)
                btn.setStyleSheet('QPushButton { background-color: %s; }' % hex)
                btn.hex = hex  # For use in the event below

                def patch_mousePressEvent(self_, e):
                    if e.button() == Qt.LeftButton:
                        self.set_primary_color(self_.hex)

                    elif e.button() == Qt.RightButton:
                        self.set_secondary_color(self_.hex)

                btn.mousePressEvent = types.MethodType(patch_mousePressEvent, btn)

        # Setup up action signals
        # self.actionCopy.triggered.connect(self.copy_to_clipboard)

        # Initialize animation timer.
        self.timer = QTimer()
        self.timer.timeout.connect(self.canvas.on_timer)
        self.timer.setInterval(100)
        self.timer.start()

        # Setup to agree with Canvas.
        self.set_primary_color('#000000')
        self.set_secondary_color('#ffffff')

        # Signals for canvas-initiated color changes (dropper).
        self.canvas.primary_color_updated.connect(self.set_primary_color)
        self.canvas.secondary_color_updated.connect(self.set_secondary_color)

        # Setup the stamp state.
        self.current_stamp_n = -1
        # self.next_stamp()
        self.stampnextButton.pressed.connect(self.next_stamp)

        # Menu options
        self.actionNewImage.triggered.connect(self.canvas.initialize)
        # self.actionNewImage.triggered.connect(self.copy_to_clipboard)
        self.actionOpenImage.triggered.connect(self.open_file)
        self.actionSaveImage.triggered.connect(self.save_file)
        self.actionClearImage.triggered.connect(self.canvas.reset)
        self.actionInvertColors.triggered.connect(self.invert)
        self.actionFlipHorizontal.triggered.connect(self.flip_horizontal)
        self.actionFlipVertical.triggered.connect(self.flip_vertical)

        sizeicon = QLabel()
        sizeicon.setPixmap(QPixmap(':/icons/border-weight.png'))
        self.sizeselect = QSlider()
        # self.sizeselect.setRange(1,20)
        self.sizeselect.setRange(1,5)
        self.sizeselect.setOrientation(Qt.Horizontal)
        self.sizeselect.valueChanged.connect(lambda s: self.canvas.set_config('size', s))
        if self.mode == 1:
            self.drawingToolbar.addWidget(sizeicon)
            self.drawingToolbar.addWidget(self.sizeselect)

        # self.actionFillShapes.triggered.connect(lambda s: self.canvas.set_config('fill', s))
        # self.drawingToolbar.addAction(self.actionFillShapes)
        # self.actionFillShapes.setChecked(True)

        self.open_file_mode('./temp/sketch.png' if self.mode == 0 else './temp/color_domain.png')
        self.centralWidget.adjustSize()
        self.adjustSize()
        self.show()

    def choose_color(self, callback):
        dlg = QColorDialog()
        if dlg.exec():
            callback( dlg.selectedColor().name() )

    def set_primary_color(self, hex):
        self.canvas.set_primary_color(hex)
        self.primaryButton.setStyleSheet('QPushButton { background-color: %s; }' % hex)

    def set_secondary_color(self, hex):
        self.canvas.set_secondary_color(hex)
        self.secondaryButton.setStyleSheet('QPushButton { background-color: %s; }' % hex)

    def next_stamp(self):
        if self.showSketch:
            self.actionSaveImage.setEnabled(True)
            self.open_file_mode('./temp/color_domain.png')
        else:
            self.actionSaveImage.setEnabled(False)
            path = './temp/color_domain.png'
            pixmap = self.canvas.pixmap()
            pixmap.save(path, "PNG")
            color_domain = cv2.imread(path)
            edge = cv2.imread('./temp/sketch.png')
            img = self.concat_sketch_color(edge, color_domain)
            cv2.imwrite('./temp/color_domain_sketch.png', img)
            self.open_file_mode('./temp/color_domain_sketch.png')
        self.showSketch = not self.showSketch    
        
        self.current_stamp_n += 1
        if self.current_stamp_n >= len(STAMPS):
            self.current_stamp_n = 0

        pixmap = QPixmap(STAMPS[self.current_stamp_n])
        self.stampnextButton.setIcon(QIcon(pixmap))

        # self.canvas.current_stamp = pixmap
        
    def concat_sketch_color(self, edge, color, invert=True):
        img = cv2.addWeighted(color, 1, edge, 1, 0.0)
        if invert:
            r1, g1, b1 = 255, 255, 255 # Original value
            r2, g2, b2 = 0, 0, 0 # Value that we want to replace it with
            red, green, blue = img[:,:,0], img[:,:,1], img[:,:,2]
            mask = (red == r1) & (green == g1) & (blue == b1)
            img[:,:,:3][mask] = [r2, g2, b2]
        return img
 
    def copy_to_clipboard(self, move_x, move_y):
        # clipboard = QApplication.clipboard()

        if self.canvas.mode == 'selectrect' and self.canvas.locked:
            selectrect = self.canvas.selectrect_copy()
            # clipboard.setPixmap(selectrect)
            selectrect.save('./temp/sketch_crop.png', "PNG")
            sketch = cv2.imread('./temp/sketch.png')
            sketch_crop = cv2.imread('./temp/sketch_crop.png')
            x1, y1 = self.canvas.origin_pos.x(), self.canvas.origin_pos.y()
            x2, y2 = self.canvas.current_pos.x(), self.canvas.current_pos.y()
            # move_x = 5
            # move_y = -5
            print(sketch_crop.shape)
            w, h, c = sketch_crop.shape
            sketch[y1:y1+w, x1:x1+h] = np.zeros((w, h, c))
            
            if move_x > 0:
                new_x2 = x2+move_x if x2+move_x <= 176 else 176
                new_x1 = new_x2 - h
            else:
                new_x1 = x1+move_x if x1+move_x >= 0 else 0
                new_x2 = new_x1 + h
                
            if move_y > 0:
                new_y2 = y2+move_y if y2+move_y <= 176 else 176
                new_y1 = new_y2 - w
            else:
                new_y1 = y1+move_y if y1+move_y >= 0 else 0
                new_y2 = new_y1 + w
                
            sketch[new_y1:new_y2, new_x1:new_x2] = sketch_crop
            cv2.imwrite('./temp/sketch.png', sketch)
            self.open_file_mode('./temp/sketch.png')
            self.canvas.origin_pos.setX(new_x1)
            self.canvas.origin_pos.setY(new_y1)
            self.canvas.current_pos.setX(new_x2)
            self.canvas.current_pos.setY(new_y2)
            # print(self.origin_pos.x(), self.origin_pos.y(), self.current_pos.x(), self.current_pos.y() )
        
            
        # elif self.canvas.mode == 'selectpoly' and self.canvas.locked:
        #     clipboard.setPixmap(self.canvas.selectpoly_copy())

        # else:
        #     clipboard.setPixmap(self.canvas.pixmap())

    def open_file_mode(self, path):
        """
        Open image file for editing, scaling the smaller dimension and cropping the remainder.
        :return:
        """
        
        # path = './temp/sketch.png' if self.mode == 0 else './temp/color_domain_sketch.png'
        if path:
            pixmap = QPixmap()
            pixmap.load(path)

            # We need to crop down to the size of our canvas. Get the size of the loaded image.
            iw = pixmap.width()
            ih = pixmap.height()

            # Get the size of the space we're filling.
            cw, ch = CANVAS_DIMENSIONS

            if iw/cw < ih/ch:  # The height is relatively bigger than the width.
                pixmap = pixmap.scaledToWidth(cw)
                hoff = (pixmap.height() - ch) // 2
                pixmap = pixmap.copy(
                    QRect(QPoint(0, hoff), QPoint(cw, pixmap.height()-hoff))
                )

            elif iw/cw > ih/ch:  # The height is relatively bigger than the width.
                pixmap = pixmap.scaledToHeight(ch)
                woff = (pixmap.width() - cw) // 2
                pixmap = pixmap.copy(
                    QRect(QPoint(woff, 0), QPoint(pixmap.width()-woff, ch))
                )

            self.canvas.setPixmap(pixmap)

    def open_file(self):
        """
        Open image file for editing, scaling the smaller dimension and cropping the remainder.
        :return:
        """
        path, _ = QFileDialog.getOpenFileName(self, "Open file", "", "PNG image files (*.png); JPEG image files (*jpg); All files (*.*)")

        if path:
            pixmap = QPixmap()
            pixmap.load(path)

            # We need to crop down to the size of our canvas. Get the size of the loaded image.
            iw = pixmap.width()
            ih = pixmap.height()

            # Get the size of the space we're filling.
            cw, ch = CANVAS_DIMENSIONS

            if iw/cw < ih/ch:  # The height is relatively bigger than the width.
                pixmap = pixmap.scaledToWidth(cw)
                hoff = (pixmap.height() - ch) // 2
                pixmap = pixmap.copy(
                    QRect(QPoint(0, hoff), QPoint(cw, pixmap.height()-hoff))
                )

            elif iw/cw > ih/ch:  # The height is relatively bigger than the width.
                pixmap = pixmap.scaledToHeight(ch)
                woff = (pixmap.width() - cw) // 2
                pixmap = pixmap.copy(
                    QRect(QPoint(woff, 0), QPoint(pixmap.width()-woff, ch))
                )

            self.canvas.setPixmap(pixmap)

    def save_file(self):
        if self.canvas.locked:
            QMessageBox.information(self, "Canvas locked",
                    "Cannot save because your action on selection hadn't completed")
        else:
            self.path = './temp/designer_{}.png'.format('sketch' if self.mode == 0 else 'color_domain')
            pixmap = self.canvas.pixmap()
            pixmap.save(self.path, "PNG")
            self.close()

    def invert(self):
        img = QImage(self.canvas.pixmap())
        img.invertPixels()
        pixmap = QPixmap()
        pixmap.convertFromImage(img)
        self.canvas.setPixmap(pixmap)

    def flip_horizontal(self):
        pixmap = self.canvas.pixmap()
        self.canvas.setPixmap(pixmap.transformed(QTransform().scale(-1, 1)))

    def flip_vertical(self):
        pixmap = self.canvas.pixmap()
        self.canvas.setPixmap(pixmap.transformed(QTransform().scale(1, -1)))

    def closeEvent(self, event):
        if self.path:
            self._signal.emit(self.path)
        # self.close()
    
if __name__ == '__main__':

    app = QApplication(sys.argv)
    # app.setWindowIcon(QtGui.QIcon(':/icons/piecasso.ico'))
    window = DesignerWindow()
    app.exec_()