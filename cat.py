import sys
import os
import math
import random
from PySide6.QtWidgets import QApplication, QWidget, QMenu
from PySide6.QtCore import Qt, QTimer, QUrl
from PySide6.QtGui import QPainter, QColor, QFont
from PySide6.QtMultimedia import QSoundEffect

# ---------- Settings you can change ----------
PIXEL = 3            # size of one pixel on screen (3 = smaller cat, 5 = bigger cat)
WINDOW_W = 160
WINDOW_H = 140
SLEEP_AFTER = 20000  # the cat falls asleep after this many milliseconds with no petting

# ---------- What each letter means ----------
COLORS = {
    "K": QColor(60, 60, 60),      # dark outline
    "W": QColor(255, 255, 255),   # white fur
    "P": QColor(255, 190, 200),   # pink cheeks and ears
    "G": QColor(150, 150, 150),   # grey tail stripes
    "R": QColor(240, 90, 110),    # red heart
}

# ---------- Pose 1: awake, eyes open (30 wide, 18 tall) ----------
CAT_AWAKE = [
    "..K.......K................KK.",
    ".KPK.....KPK..............KWWK",
    "KWPWKKKKKWPWK............KGGK.",
    "KWWWWWWWWWWWK............KGGK.",
    "KWWWWWWWWWWWK...........KWWK..",
    "KWWKWWWWWKWWK...........KWWK..",
    "KWWKWWWWWKWWK...........KGGK..",
    "KPPWWKWKWWPPK...........KGGK..",
    "KWWWWWKWWWWWKKKKKKKKKKKKKKKK..",
    "KWWWWWWWWWWWKWWWWWWWWWWWK.....",
    "KKKKKKKKKKKKKWWWWWWWWWWWK.....",
    "..KWWWWWWWWWWWWWWWWWWWWWK.....",
    "..KWWWWWWWWWWWWWWWWWWWWWK.....",
    "..KWWWWWWWWWWWWWWWWWWWWWK.....",
    "..KWWWWWWKKKKKKKKKWWWWWWK.....",
    "..KWWWWWWK.......KWWWWWWK.....",
    "..KWWKKWWK.......KWWKKWWK.....",
    "..KKKKKKKK.......KKKKKKKK.....",
]

# ---------- Pose 2: blinking (same as awake, only rows 5 and 6 change) ----------
CAT_BLINK = list(CAT_AWAKE)
CAT_BLINK[5] = "KWWWWWWWWWWWK...........KWWK.."
CAT_BLINK[6] = "KWKKWWWWWKKWK...........KGGK.."

# ---------- Pose 3: sleeping (curled up like a loaf, eyes closed) ----------
CAT_SLEEP = [
    "..............................",
    "..............................",
    "..............................",
    "..............................",
    "..............................",
    "..............................",
    "..............................",
    "..K.......K...................",
    ".KPK.....KPK..................",
    "KWPWKKKKKWPWK.................",
    "KWWWWWWWWWWWK.................",
    "KWWWWWWWWWWWK..KKKKKKKKKKKK...",
    "KWWWWWWWWWWWKKKWWWWWWWWWWWKK..",
    "KWKKWWWWWKKWKWWWWWWWWWWWWWWWK.",
    "KPPWWKWKWWPPKWWWWWWWWWWWWWWWK.",
    "KWWWWWKWWWWWKWWWWWWWWWWWWWWWK.",
    "KWWWWWWWWWWWKWWWWWWWWWWWWWWWK.",
    "KKKKKKKKKKKKKKKKKKKKKKKKKKKKK.",
]

# ---------- A little heart that floats up while you pet the cat ----------
HEART = [
    ".RR.RR.",
    "RRRRRRR",
    "RRRRRRR",
    ".RRRRR.",
    "..RRR..",
    "...R...",
]

class Cat(QWidget):
    def __init__(self):
        super().__init__()

        # Step 1: transparent, frameless, always-on-top window
        self.setWindowFlags(Qt.FramelessWindowHint | Qt.WindowStaysOnTopHint | Qt.Tool)
        self.setAttribute(Qt.WA_TranslucentBackground)
        self.resize(WINDOW_W, WINDOW_H)

        # Step 2: spring values for the mochi squash and stretch
        self.scale_y = 1.0
        self.target = 1.0
        self.velocity = 0.0

        # Step 3: timer that runs the animation about 60 times per second
        self.tick = 0
        self.timer = QTimer()
        self.timer.timeout.connect(self.update_spring)
        self.timer.start(16)

        # Step 4: dragging
        self.drag_offset = None

        # Step 5: purr sound (loops while the mouse is on the cat)
        self.purr = QSoundEffect()
        purr_path = os.path.join(os.path.dirname(__file__), "purr.wav")
        self.purr.setSource(QUrl.fromLocalFile(purr_path))
        self.purr.setLoopCount(-2)
        self.purr.setVolume(0.5)

        # Step 6: wandering
        self.hovering = False
        self.walk_target_x = None
        self.flip = 1          # 1 = looking left, -1 = looking right
        self.wander_timer = QTimer()
        self.wander_timer.timeout.connect(self.choose_target)
        self.wander_timer.start(6000)

        # Step 7: blinking (every 2 to 5 seconds, the eyes close for a moment)
        self.blinking = False
        self.blink_timer = QTimer()
        self.blink_timer.setSingleShot(True)
        self.blink_timer.timeout.connect(self.start_blink)
        self.blink_timer.start(3000)

        # Step 8: sleeping (falls asleep when nobody pets it for a while)
        self.sleeping = False
        self.sleep_timer = QTimer()
        self.sleep_timer.setSingleShot(True)
        self.sleep_timer.timeout.connect(self.go_to_sleep)
        self.sleep_timer.start(SLEEP_AFTER)

        # Step 9: start at the bottom of the screen, just above the taskbar
        screen = QApplication.primaryScreen().availableGeometry()
        self.move(screen.center().x() - WINDOW_W // 2, screen.bottom() - 130)

    # ----- blinking -----
    def start_blink(self):
        self.blinking = True
        QTimer.singleShot(150, self.stop_blink)

    def stop_blink(self):
        self.blinking = False
        self.blink_timer.start(random.randint(2000, 5000))

    # ----- sleeping -----
    def go_to_sleep(self):
        # Timer ran out: only sleep if nobody is petting or dragging the cat
        if self.hovering or self.drag_offset is not None:
            self.sleep_timer.start(SLEEP_AFTER)
        else:
            self.fall_asleep()

    def fall_asleep(self):
        self.sleeping = True
        self.walk_target_x = None
        self.velocity = -0.1

    def wake_up(self):
        if self.sleeping:
            self.sleeping = False
            self.velocity = 0.12   # a little stretch
        self.sleep_timer.start(SLEEP_AFTER)

    # ----- wandering -----
    def choose_target(self):
        if self.sleeping:
            return
        if self.drag_offset is None and not self.hovering:
            if random.random() < 0.7:
                screen = QApplication.primaryScreen().availableGeometry()
                self.walk_target_x = random.randint(screen.left(), screen.right() - self.width())

    def update_spring(self):
        self.tick = self.tick + 1

        if self.sleeping:
            # Breathing: the sleeping cat slowly gets a little bigger and smaller
            self.target = 1.0 + 0.03 * math.sin(self.tick * 0.06)
        elif self.walk_target_x is not None:
            # Walking: move a little toward the target and bounce
            self.target = 1.0 + 0.05 * math.sin(self.tick * 0.3)
            x = self.x()
            if abs(self.walk_target_x - x) < 3:
                self.walk_target_x = None
            elif self.walk_target_x > x:
                self.flip = -1
                self.move(x + 2, self.y())
            else:
                self.flip = 1
                self.move(x - 2, self.y())
        else:
            self.target = 1.0

        # The mochi spring
        force = (self.target - self.scale_y) * 0.2
        self.velocity = (self.velocity + force) * 0.85
        self.scale_y = self.scale_y + self.velocity
        self.update()

    # ----- mouse -----
    def enterEvent(self, event):
        self.hovering = True
        self.wake_up()
        self.walk_target_x = None
        self.velocity = -0.08
        self.purr.play()

    def leaveEvent(self, event):
        self.hovering = False
        self.purr.stop()
        self.sleep_timer.start(SLEEP_AFTER)

    def mousePressEvent(self, event):
        if event.button() == Qt.LeftButton:
            self.wake_up()
            self.walk_target_x = None
            self.drag_offset = event.globalPosition().toPoint() - self.frameGeometry().topLeft()
            self.velocity = 0.12

    def mouseMoveEvent(self, event):
        if self.drag_offset is not None:
            self.move(event.globalPosition().toPoint() - self.drag_offset)

    def mouseReleaseEvent(self, event):
        self.drag_offset = None
        self.velocity = -0.1

    def contextMenuEvent(self, event):
        menu = QMenu(self)
        sleep_action = menu.addAction("Sleep now")
        quit_action = menu.addAction("Quit")
        chosen = menu.exec(event.globalPos())
        if chosen == sleep_action:
            self.purr.stop()
            self.fall_asleep()
        elif chosen == quit_action:
            QApplication.quit()

    # ----- drawing -----
    def paintEvent(self, event):
        p = QPainter(self)
        # No smoothing, so the pixels stay sharp and square
        p.setRenderHint(QPainter.Antialiasing, False)
        p.setPen(Qt.NoPen)

        # Choose which picture to draw
        if self.sleeping:
            picture = CAT_SLEEP
        elif self.blinking:
            picture = CAT_BLINK
        else:
            picture = CAT_AWAKE

        sy = self.scale_y
        sx = 1.0 / sy

        # Draw the cat. save() and restore() keep the squash from affecting the extras below.
        p.save()
        # Origin at the cat's feet (bottom middle). The flip turns the cat to face the other way.
        p.translate(WINDOW_W / 2, 130)
        p.scale(sx * self.flip, sy)
        for row in range(len(picture)):
            for col in range(len(picture[row])):
                letter = picture[row][col]
                if letter != ".":
                    p.setBrush(COLORS[letter])
                    x = (col - 15) * PIXEL
                    y = (row - 18) * PIXEL
                    p.drawRect(x, y, PIXEL, PIXEL)
        p.restore()

        # Where the middle of the cat's head is on the screen
        head_x = int(WINDOW_W / 2 - 9 * PIXEL * self.flip)

        # Floating heart while the mouse is on the cat
        if self.hovering and not self.sleeping:
            heart_y = int(30 + 4 * math.sin(self.tick * 0.1))
            p.setBrush(COLORS["R"])
            for row in range(len(HEART)):
                for col in range(len(HEART[row])):
                    if HEART[row][col] == "R":
                        p.drawRect(head_x - 10 + col * 3, heart_y + row * 3, 3, 3)

        # Floating z z Z while sleeping
        if self.sleeping:
            bob = int(3 * math.sin(self.tick * 0.05))
            p.setPen(QColor(90, 90, 130))
            p.setFont(QFont("Arial", 10, QFont.Bold))
            p.drawText(head_x + 16 * self.flip, 78 + bob, "z")
            p.setFont(QFont("Arial", 13, QFont.Bold))
            p.drawText(head_x + 28 * self.flip, 64 + bob, "z")
            p.setFont(QFont("Arial", 16, QFont.Bold))
            p.drawText(head_x + 40 * self.flip, 48 + bob, "Z")

app = QApplication(sys.argv)
cat = Cat()
cat.show()
sys.exit(app.exec())