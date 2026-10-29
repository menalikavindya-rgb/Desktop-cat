import sys
import os
import math
import random
from PySide6.QtWidgets import QApplication, QWidget, QMenu
from PySide6.QtCore import Qt, QTimer, QUrl
from PySide6.QtGui import QPainter, QColor, QFont, QCursor
from PySide6.QtMultimedia import QSoundEffect

# These are only needed on Windows, to find the window you are using
if sys.platform == "win32":
    import ctypes
    from ctypes import wintypes

# ---------- Settings you can change ----------
PIXEL = 3             # size of one pixel on screen (3 = smaller cat, 5 = bigger cat)
WINDOW_W = 160
WINDOW_H = 140
SLEEP_AFTER = 70000   # the cat falls asleep after this many milliseconds with no petting
FOCUS_MINUTES = 0.5    # pomodoro focus time
BREAK_MINUTES = 0.5    # pomodoro break time

# ---------- What each letter means ----------
COLORS = {
    "K": QColor(60, 60, 60),      # dark outline
    "W": QColor(255, 255, 255),   # white fur
    "P": QColor(255, 190, 200),   # pink cheeks and ears
    "G": QColor(150, 150, 150),   # grey tail stripes
    "R": QColor(240, 90, 110),    # red heart
}

# ---------- Pose 1: awake, eyes open, tail leaning right (30 wide, 18 tall) ----------
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

# ---------- Pose 3 and 4: the same two poses with the tail leaning left (for the wag) ----------
CAT_AWAKE_B = list(CAT_AWAKE)
CAT_AWAKE_B[0] = "..K.......K...........KK......"
CAT_AWAKE_B[1] = ".KPK.....KPK.........KWWK....."
CAT_AWAKE_B[2] = "KWPWKKKKKWPWK.........KGGK...."
CAT_AWAKE_B[3] = "KWWWWWWWWWWWK.........KGGK...."
CAT_AWAKE_B[4] = "KWWWWWWWWWWWK..........KWWK..."
CAT_AWAKE_B[5] = "KWWKWWWWWKWWK..........KWWK..."
CAT_AWAKE_B[6] = "KWWKWWWWWKWWK...........KGGK.."
CAT_AWAKE_B[7] = "KPPWWKWKWWPPK...........KGGK.."

CAT_BLINK_B = list(CAT_AWAKE_B)
CAT_BLINK_B[5] = "KWWWWWWWWWWWK..........KWWK..."
CAT_BLINK_B[6] = "KWKKWWWWWKKWK...........KGGK.."

# ---------- Pose 5: sleeping (curled up like a loaf, eyes closed) ----------
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

# ---------- Finds the window you are using (Windows only) ----------
def find_active_window(my_hwnd, ratio):
    # Returns "me" if the cat itself is the active window,
    # None if there is no usable window, or (left, top, right) of the active window.
    if sys.platform != "win32":
        return None
    try:
        user32 = ctypes.windll.user32
        hwnd = user32.GetForegroundWindow()
        if hwnd == 0:
            return None
        if (hwnd & 0xFFFFFFFF) == (my_hwnd & 0xFFFFFFFF):
            return "me"
        # Ignore hidden, minimized and maximized windows
        if user32.IsWindowVisible(hwnd) == 0:
            return None
        if user32.IsIconic(hwnd) != 0 or user32.IsZoomed(hwnd) != 0:
            return None
        # Ignore the desktop and the taskbar
        name = ctypes.create_unicode_buffer(256)
        user32.GetClassNameW(hwnd, name, 256)
        if name.value in ("Progman", "WorkerW", "Shell_TrayWnd", "Shell_SecondaryTrayWnd"):
            return None
        rect = wintypes.RECT()
        user32.GetWindowRect(hwnd, ctypes.byref(rect))
        left = rect.left / ratio
        top = rect.top / ratio
        right = rect.right / ratio
        bottom = rect.bottom / ratio
        if right - left < 250 or bottom - top < 100:
            return None
        return (left, top, right)
    except Exception:
        return None

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

        # Step 5: sounds (purr.wav and meow.wav go in the same folder as cat.py)
        folder = os.path.dirname(__file__)
        self.purr = QSoundEffect()
        self.purr.setSource(QUrl.fromLocalFile(os.path.join(folder, "purr.wav")))
        self.purr.setLoopCount(-2)
        self.purr.setVolume(0.3)
        self.meow_path = os.path.join(folder, "meow.wav")
        self.meow = QSoundEffect()
        self.meow.setSource(QUrl.fromLocalFile(self.meow_path))
        self.meow.setVolume(0.7)

        # Step 6: where the cat can stand and walk
        screen = QApplication.primaryScreen().availableGeometry()
        self.floor_y = screen.bottom() - 130          # the floor is the bottom of the screen
        self.screen_min_x = screen.left()
        self.screen_max_x = screen.right() - WINDOW_W
        self.ground_y = self.floor_y                  # the height the cat stands at right now
        self.min_x = self.screen_min_x                # the cat can walk between these two
        self.max_x = self.screen_max_x
        self.move(screen.center().x() - WINDOW_W // 2, self.ground_y)

        # Step 7: jumping and falling
        self.in_air = False
        self.vy = 0                # up/down speed (negative = going up)
        self.air_target_x = None   # where the cat glides sideways while it is in the air

        # Step 8: wandering
        self.hovering = False
        self.walk_target_x = None
        self.flip = 1              # 1 = looking left, -1 = looking right
        self.wander_timer = QTimer()
        self.wander_timer.timeout.connect(self.choose_target)
        self.wander_timer.start(6000)

        # Step 9: chasing the mouse
        self.chasing = False
        self.pounce_wait = 0

        # Step 10: blinking (every 2 to 5 seconds, the eyes close for a moment)
        self.blinking = False
        self.blink_timer = QTimer()
        self.blink_timer.setSingleShot(True)
        self.blink_timer.timeout.connect(self.start_blink)
        self.blink_timer.start(3000)

        # Step 11: sleeping (falls asleep when nobody pets it for a while)
        self.sleeping = False
        self.sleep_timer = QTimer()
        self.sleep_timer.setSingleShot(True)
        self.sleep_timer.timeout.connect(self.go_to_sleep)
        self.sleep_timer.start(SLEEP_AFTER)

        # Step 12: sitting on the window you are using
        self.window_mode = True
        self.window_timer = QTimer()
        self.window_timer.timeout.connect(self.check_windows)
        self.window_timer.start(300)

        # Step 13: pomodoro (pomodoro is "none", "focus" or "break")
        self.pomodoro = "none"
        self.pomodoro_timer = QTimer()
        self.pomodoro_timer.setSingleShot(True)
        self.pomodoro_timer.timeout.connect(self.pomodoro_finished)

        # Step 14: speech bubble
        self.bubble_text = ""
        self.bubble_ticks = 0

    # ----- speech bubble -----
    def show_bubble(self, text):
        self.bubble_text = text
        self.bubble_ticks = 300    # about 5 seconds

    # ----- blinking -----
    def start_blink(self):
        self.blinking = True
        QTimer.singleShot(150, self.stop_blink)

    def stop_blink(self):
        self.blinking = False
        self.blink_timer.start(random.randint(2000, 5000))

    # ----- sleeping -----
    def go_to_sleep(self):
        # Timer ran out: only sleep if nobody is petting, dragging or playing with the cat
        if self.hovering or self.drag_offset is not None or self.chasing:
            self.sleep_timer.start(SLEEP_AFTER)
        else:
            self.fall_asleep()

    def fall_asleep(self):
        self.sleeping = True
        self.chasing = False
        self.walk_target_x = None
        self.velocity = -0.1

    def wake_up(self):
        # During a focus session the cat stays asleep
        if self.pomodoro == "focus":
            return
        if self.sleeping:
            self.sleeping = False
            self.velocity = 0.12   # a little stretch
        self.sleep_timer.start(SLEEP_AFTER)

    # ----- pomodoro -----
    def start_focus(self):
        self.pomodoro = "focus"
        self.pomodoro_timer.start(FOCUS_MINUTES * 60 * 1000)
        self.purr.stop()
        self.fall_asleep()
        self.show_bubble("Focus time. Shh!")

    def pomodoro_finished(self):
        if self.pomodoro == "focus":
            # Focus is over: the cat wakes up and meows
            self.pomodoro = "break"
            self.pomodoro_timer.start(BREAK_MINUTES * 60 * 1000)
            self.wake_up()
            self.play_meow()
            self.show_bubble("Break time! " + str(BREAK_MINUTES) + " min")
        elif self.pomodoro == "break":
            # Break is over
            self.pomodoro = "none"
            self.play_meow()
            self.show_bubble("Back to work!")

    def stop_pomodoro(self):
        self.pomodoro = "none"
        self.pomodoro_timer.stop()
        self.wake_up()

    def pomodoro_text(self):
        seconds_left = self.pomodoro_timer.remainingTime() // 1000
        minutes = seconds_left // 60
        seconds = seconds_left % 60
        if self.pomodoro == "focus":
            label = "Focus"
        else:
            label = "Break"
        return label + ": " + str(minutes) + ":" + str(seconds).zfill(2) + " left"

    def play_meow(self):
        if os.path.exists(self.meow_path):
            self.meow.play()
        else:
            QApplication.beep()

    # ----- chasing the mouse -----
    def start_chase(self):
        if self.pomodoro == "focus":
            return
        self.wake_up()
        self.walk_target_x = None
        self.chasing = True
        QTimer.singleShot(8000, self.stop_chase)

    def stop_chase(self):
        self.chasing = False

    def chase_step(self):
        cursor_x = QCursor.pos().x()
        cat_middle = self.x() + WINDOW_W // 2
        self.target = 1.0 + 0.05 * math.sin(self.tick * 0.5)

        # Look at the cursor
        if cursor_x < cat_middle:
            self.flip = 1
        else:
            self.flip = -1

        # Close enough: pounce! Otherwise run toward the cursor.
        if abs(cursor_x - cat_middle) < 40:
            if self.pounce_wait == 0:
                self.pounce()
        elif cursor_x > cat_middle:
            self.move(min(self.x() + 4, self.max_x), self.y())
        else:
            self.move(max(self.x() - 4, self.min_x), self.y())

    def pounce(self):
        self.in_air = True
        self.vy = -12
        self.air_target_x = None
        self.velocity = 0.15     # stretch while jumping
        self.pounce_wait = 50

    # ----- jumping and falling -----
    def fly(self):
        self.target = 1.0
        self.vy = self.vy + 1    # gravity
        x = self.x()
        y = self.y() + self.vy
        if self.air_target_x is not None:
            x = x + int((self.air_target_x - x) * 0.08)
        # Landing: only when falling and reaching the ground
        if self.vy > 0 and y >= self.ground_y:
            y = self.ground_y
            self.in_air = False
            self.velocity = -0.15    # squash when landing
            if self.air_target_x is not None:
                x = self.air_target_x
                self.air_target_x = None
        self.move(x, y)

    def jump_to_ground(self):
        self.in_air = True
        self.velocity = 0.15
        if self.y() > self.ground_y:
            # The ground is higher up: jump up to it
            height = self.y() - self.ground_y
            self.vy = -int(math.sqrt(2 * (height + 20)))
        elif self.y() < self.ground_y:
            # The ground is lower down: just fall
            self.vy = 0
        else:
            # Same height: a small hop
            self.vy = -6

    # ----- sitting on the active window -----
    def check_windows(self):
        # Don't move the cat while it is held or already jumping
        if self.drag_offset is not None or self.in_air:
            return

        new_ground = self.floor_y
        new_min = self.screen_min_x
        new_max = self.screen_max_x

        if self.window_mode:
            ratio = QApplication.primaryScreen().devicePixelRatio()
            found = find_active_window(int(self.winId()), ratio)
            if found == "me":
                return
            if found is not None:
                left, top, right = found
                if top >= 80:
                    new_ground = min(self.floor_y, int(top) - 130)
                    new_min = int(left) - 20
                    new_max = int(right) - WINDOW_W + 20

        x = self.x()
        x_inside = max(new_min, min(x, new_max))
        ground_changed = abs(new_ground - self.ground_y) > 3

        if ground_changed:
            self.ground_y = new_ground
        self.min_x = new_min
        self.max_x = new_max

        # The window changed or moved: jump to the new spot
        if ground_changed or x_inside != x:
            self.air_target_x = x_inside
            self.walk_target_x = None
            self.jump_to_ground()

    # ----- wandering -----
    def choose_target(self):
        if self.sleeping or self.chasing or self.in_air:
            return
        if self.drag_offset is None and not self.hovering:
            roll = random.random()
            if roll < 0.15:
                self.start_chase()      # 15%: chase the mouse (change to 0 to turn off)
            elif roll < 0.7:
                self.walk_target_x = random.randint(self.min_x, self.max_x)

    def walk_step(self):
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

    def update_spring(self):
        self.tick = self.tick + 1
        if self.bubble_ticks > 0:
            self.bubble_ticks = self.bubble_ticks - 1
        if self.pounce_wait > 0:
            self.pounce_wait = self.pounce_wait - 1

        # What is the cat doing right now?
        if self.in_air:
            self.fly()
        elif self.sleeping:
            # Breathing: the sleeping cat slowly gets a little bigger and smaller
            self.target = 1.0 + 0.03 * math.sin(self.tick * 0.06)
        elif self.chasing:
            self.chase_step()
        elif self.walk_target_x is not None:
            self.walk_step()
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
        if self.pomodoro == "focus":
            return              # no purring while you are focusing
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
            self.chasing = False
            self.in_air = False
            self.walk_target_x = None
            self.drag_offset = event.globalPosition().toPoint() - self.frameGeometry().topLeft()
            self.velocity = 0.12

    def mouseMoveEvent(self, event):
        if self.drag_offset is not None:
            self.move(event.globalPosition().toPoint() - self.drag_offset)

    def mouseReleaseEvent(self, event):
        self.drag_offset = None
        self.velocity = -0.1
        # Let go: the cat drops down to the ground
        self.air_target_x = max(self.min_x, min(self.x(), self.max_x))
        if self.y() >= self.ground_y:
            self.move(self.air_target_x, self.ground_y)
            self.air_target_x = None
        else:
            self.in_air = True
            self.vy = 0

    def contextMenuEvent(self, event):
        menu = QMenu(self)

        chase_action = menu.addAction("Chase my mouse")
        sleep_action = menu.addAction("Sleep now")
        window_action = menu.addAction("Sit on active window")
        window_action.setCheckable(True)
        window_action.setChecked(self.window_mode)
        if self.pomodoro == "focus":
            chase_action.setEnabled(False)
            sleep_action.setEnabled(False)

        menu.addSeparator()
        focus_action = None
        stop_action = None
        if self.pomodoro == "none":
            focus_action = menu.addAction("Start focus (" + str(FOCUS_MINUTES) + " min)")
        else:
            info_action = menu.addAction(self.pomodoro_text())
            info_action.setEnabled(False)
            stop_action = menu.addAction("Stop timer")

        menu.addSeparator()
        quit_action = menu.addAction("Quit")

        chosen = menu.exec(event.globalPos())
        if chosen is None:
            return
        if chosen == chase_action:
            self.start_chase()
        elif chosen == sleep_action:
            self.purr.stop()
            self.fall_asleep()
        elif chosen == window_action:
            self.window_mode = window_action.isChecked()
        elif chosen == focus_action:
            self.start_focus()
        elif chosen == stop_action:
            self.stop_pomodoro()
        elif chosen == quit_action:
            QApplication.quit()

    # ----- drawing -----
    def paintEvent(self, event):
        p = QPainter(self)
        # No smoothing, so the pixels stay sharp and square
        p.setRenderHint(QPainter.Antialiasing, False)
        p.setPen(Qt.NoPen)

        # The tail wags faster when the cat is happy (petting or chasing)
        if self.hovering or self.chasing:
            wag_speed = 10
        else:
            wag_speed = 40
        tail_left = (self.tick // wag_speed) % 2 == 1

        # Choose which picture to draw
        if self.sleeping:
            picture = CAT_SLEEP
        elif self.blinking and tail_left:
            picture = CAT_BLINK_B
        elif self.blinking:
            picture = CAT_BLINK
        elif tail_left:
            picture = CAT_AWAKE_B
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
            heart_y = int(34 + 4 * math.sin(self.tick * 0.1))
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
            p.drawText(head_x + 40 * self.flip, 52 + bob, "Z")

        # Speech bubble
        if self.bubble_ticks > 0:
            p.setPen(QColor(60, 60, 60))
            p.setBrush(QColor(255, 255, 255))
            p.drawRoundedRect(4, 4, WINDOW_W - 8, 24, 6, 6)
            p.setFont(QFont("Arial", 8, QFont.Bold))
            p.drawText(10, 20, self.bubble_text)

app = QApplication(sys.argv)
cat = Cat()
cat.show()
sys.exit(app.exec())