import sys
from PySide6.QtWidgets import QApplication, QWidget
from PySide6.QtCore import Qt, QTimer, QPointF
from PySide6.QtGui import QPainter, QColor, QPolygonF

class Cat(QWidget):
    def __init__(self):
        super().__init__()

        # Step 1: transparent, frameless, always-on-top window
        self.setWindowFlags(Qt.FramelessWindowHint | Qt.WindowStaysOnTopHint | Qt.Tool)
        self.setAttribute(Qt.WA_TranslucentBackground)
        self.resize(300, 300)

        # Step 2: spring values for the mochi squash and stretch
        self.scale_y = 1.0      # current height scale
        self.target = 1.0       # the size it wants to return to
        self.velocity = 0.0     # how fast the size is changing

        # Step 3: timer that runs the spring about 60 times per second
        self.timer = QTimer()
        self.timer.timeout.connect(self.update_spring)
        self.timer.start(16)

        # Step 4: dragging
        self.drag_offset = None

    def update_spring(self):
        force = (self.target - self.scale_y) * 0.2
        self.velocity = (self.velocity + force) * 0.85
        self.scale_y = self.scale_y + self.velocity
        self.update()

    # Hover: squish a little
    def enterEvent(self, event):
        self.velocity = -0.08

    # Click: stretch tall and start dragging
    def mousePressEvent(self, event):
        if event.button() == Qt.LeftButton:
            self.drag_offset = event.globalPosition().toPoint() - self.frameGeometry().topLeft()
            self.velocity = 0.12

    def mouseMoveEvent(self, event):
        if self.drag_offset is not None:
            self.move(event.globalPosition().toPoint() - self.drag_offset)

    def mouseReleaseEvent(self, event):
        self.drag_offset = None
        self.velocity = -0.1   # plop

    def paintEvent(self, event):
        p = QPainter(self)
        p.setRenderHint(QPainter.Antialiasing)

        # Keep volume: taller means thinner, shorter means wider
        sy = self.scale_y
        sx = 1.0 / sy

        # Move the origin to the cat's "feet", then squash and stretch from there
        p.translate(150, 270)
        p.scale(sx, sy)

        orange = QColor(240, 170, 90)
        p.setPen(Qt.NoPen)
        p.setBrush(orange)

        # Fat body
        p.drawEllipse(QPointF(0, -80), 110, 80)

        # Ears
        p.drawPolygon(QPolygonF([QPointF(-70, -130), QPointF(-45, -190), QPointF(-20, -135)]))
        p.drawPolygon(QPolygonF([QPointF(70, -130), QPointF(45, -190), QPointF(20, -135)]))

        # Eyes
        p.setBrush(QColor(40, 40, 40))
        p.drawEllipse(QPointF(-35, -95), 9, 12)
        p.drawEllipse(QPointF(35, -95), 9, 12)

        # Nose
        p.setBrush(QColor(230, 120, 130))
        p.drawEllipse(QPointF(0, -70), 7, 5)

app = QApplication(sys.argv)
cat = Cat()
cat.show()
sys.exit(app.exec())