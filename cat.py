import sys
import os
import math
import random
from PySide6.QtWidgets import QApplication, QWidget, QMenu
from PySide6.QtCore import Qt, QTimer, QPointF, QUrl
from PySide6.QtGui import QPainter, QColor, QPolygonF
from PySide6.QtMultimedia import QSoundEffect

class Cat(QWidget):
    def __init__(self):
        super().__init__()

        # Step 1: transparent, frameless, always-on-top window
        self.setWindowFlags(Qt.FramelessWindowHint | Qt.WindowStaysOnTopHint | Qt.Tool)
        self.setAttribute(Qt.WA_TranslucentBackground)
        self.resize(300, 300)

        # Step 2: spring values for the mochi squash and stretch
        self.scale_y = 1.0
        self.target = 1.0
        self.velocity = 0.0

        # Step 3: timer that runs the spring about 60 times per second
        self.timer = QTimer()
        self.timer.timeout.connect(self.update_spring)
        self.timer.start(16)

        # Step 4: dragging
        self.drag_offset = None

        # NEW Step 5: purr sound (loops while the mouse is on the cat)
        self.purr = QSoundEffect()
        purr_path = os.path.join(os.path.dirname(__file__), "purr.wav")
        self.purr.setSource(QUrl.fromLocalFile(purr_path))
        self.purr.setLoopCount(-2)
        self.purr.setVolume(0.5)

        # NEW Step 6: wandering
        self.hovering = False
        self.walk_target_x = None
        self.walk_time = 0
        self.wander_timer = QTimer()
        self.wander_timer.timeout.connect(self.choose_target)
        self.wander_timer.start(6000)   # every 6 seconds the cat may decide to walk

        # NEW Step 7: start on the bottom of the screen, just above the taskbar
        screen = QApplication.primaryScreen().availableGeometry()
        self.move(screen.center().x() - 150, screen.bottom() - 270)

    def choose_target(self):
        # 70% chance to walk somewhere new, if not being held or hovered
        if self.drag_offset is None and not self.hovering:
            if random.random() < 0.7:
                screen = QApplication.primaryScreen().availableGeometry()
                self.walk_target_x = random.randint(screen.left(), screen.right() - self.width())

    def update_spring(self):
        # Walking: move a little toward the target and bounce while walking
        if self.walk_target_x is not None:
            self.walk_time = self.walk_time + 1
            self.target = 1.0 + 0.05 * math.sin(self.walk_time * 0.3)
            x = self.x()
            if abs(self.walk_target_x - x) < 3:
                self.walk_target_x = None
            elif self.walk_target_x > x:
                self.move(x + 2, self.y())
            else:
                self.move(x - 2, self.y())
        else:
            self.target = 1.0

        # The mochi spring
        force = (self.target - self.scale_y) * 0.2
        self.velocity = (self.velocity + force) * 0.85
        self.scale_y = self.scale_y + self.velocity
        self.update()

    # Hover: squish, stop walking, start purring
    def enterEvent(self, event):
        self.hovering = True
        self.walk_target_x = None
        self.velocity = -0.08
        self.purr.play()

    # Mouse leaves: stop purring
    def leaveEvent(self, event):
        self.hovering = False
        self.purr.stop()

    # Click: stretch tall and start dragging
    def mousePressEvent(self, event):
        if event.button() == Qt.LeftButton:
            self.walk_target_x = None
            self.drag_offset = event.globalPosition().toPoint() - self.frameGeometry().topLeft()
            self.velocity = 0.12

    def mouseMoveEvent(self, event):
        if self.drag_offset is not None:
            self.move(event.globalPosition().toPoint() - self.drag_offset)

    def mouseReleaseEvent(self, event):
        self.drag_offset = None
        self.velocity = -0.1

    # NEW: right-click menu with Quit
    def contextMenuEvent(self, event):
        menu = QMenu(self)
        quit_action = menu.addAction("Quit")
        chosen = menu.exec(event.globalPos())
        if chosen == quit_action:
            QApplication.quit()

    def paintEvent(self, event):
        p = QPainter(self)
        p.setRenderHint(QPainter.Antialiasing)

        sy = self.scale_y
        sx = 1.0 / sy

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