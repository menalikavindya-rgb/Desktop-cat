import sys
import os
import math
import random
import time
from PySide6.QtWidgets import QApplication, QWidget, QMenu
from PySide6.QtCore import Qt, QTimer
from PySide6.QtGui import QPainter, QColor, QFont, QCursor

# Sound: pygame plays the purr and the meow (install it with:  py -3.12 -m pip install pygame)
os.environ["PYGAME_HIDE_SUPPORT_PROMPT"] = "1"
try:
    import pygame
except ImportError:
    pygame = None

# These are only needed on Windows, to find the window you are using
if sys.platform == "win32":
    import ctypes
    from ctypes import wintypes

def resource_path(name):
    base = getattr(sys, "_MEIPASS", os.path.dirname(os.path.abspath(__file__)))
    return os.path.join(base, name)

# ---------- Settings you can change ----------
PIXEL = 3             # size of one pixel on screen (3 = smaller cat, 5 = bigger cat)
WINDOW_W = 160
WINDOW_H = 140
SLEEP_AFTER = 70000   # the cat falls asleep after this many milliseconds with no petting
FOCUS_MINUTES = 25    # pomodoro focus time
BREAK_MINUTES = 5     # pomodoro break time

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

# ---------- Pose 6: yawning (eyes shut, big open mouth; only rows 5 to 9 change) ----------
CAT_YAWN = list(CAT_AWAKE)
CAT_YAWN[5] = "KWWWWWWWWWWWK...........KWWK.."
CAT_YAWN[6] = "KWKKWWWWWKKWK...........KGGK.."
CAT_YAWN[7] = "KPPWKKKKKWPPK...........KGGK.."
CAT_YAWN[8] = "KWWKKKKKKKWWKKKKKKKKKKKKKKKK.."
CAT_YAWN[9] = "KWWWKPPPKWWWKWWWWWWWWWWWK....."

# ---------- Pose 7: lying on its back with the paws up (used while rolling on the floor) ----------
CAT_BELLY = list(CAT_SLEEP)
CAT_BELLY[8] = ".KPK.....KPK......KKK..KKK...."
CAT_BELLY[9] = "KWPWKKKKKWPWK.....KPK..KPK...."
CAT_BELLY[10] = "KWWWWWWWWWWWK.....KWK..KWK...."

# ---------- A little butterfly (7 wide, 5 tall), two wing positions ----------
BUTTERFLY_OPEN = [
    "BB...BB",
    "BBB.BBB",
    "BBBKBBB",
    ".BBKBB.",
    "..BKB..",
]
BUTTERFLY_CLOSED = [
    "..K.K..",
    "..BKB..",
    "..BKB..",
    "..BKB..",
    "...K...",
]
BUTTERFLY_COLORS = {
    "B": QColor(120, 170, 255),   # blue wings
    "K": QColor(60, 60, 60),      # body
}

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

# ---------- The butterfly: its own tiny see-through window that flies around the screen ----------
class Butterfly(QWidget):
    def __init__(self):
        super().__init__()
        # WindowTransparentForInput lets your mouse clicks go straight through it
        self.setWindowFlags(Qt.FramelessWindowHint | Qt.WindowStaysOnTopHint | Qt.Tool | Qt.WindowTransparentForInput)
        self.setAttribute(Qt.WA_TranslucentBackground)
        self.setAttribute(Qt.WA_ShowWithoutActivating)
        self.resize(30, 24)
        self.wings_open = True

    def paintEvent(self, event):
        p = QPainter(self)
        p.setRenderHint(QPainter.Antialiasing, False)
        p.setPen(Qt.NoPen)
        if self.wings_open:
            picture = BUTTERFLY_OPEN
        else:
            picture = BUTTERFLY_CLOSED
        for row in range(len(picture)):
            for col in range(len(picture[row])):
                letter = picture[row][col]
                if letter != ".":
                    p.setBrush(BUTTERFLY_COLORS[letter])
                    p.drawRect(4 + col * 3, 4 + row * 3, 3, 3)

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
        self.purr_sound = None
        self.meow_sound = None
        self.purring = False
        self.last_sound_time = 0
        self.reset_sound()

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

        # Step 15: yawning
        self.yawning = False
        self.yawn_ticks = 0
        self.yawn_then_sleep = False

        # Step 16: rolling on the floor (sleep_pose is "loaf" or "belly")
        self.sleep_pose = "loaf"
        self.rolling = False
        self.roll_ticks = 0
        self.roll_dir = 1
        self.roll_start_flip = 1
        self.sleep_move_timer = QTimer()
        self.sleep_move_timer.setSingleShot(True)
        self.sleep_move_timer.timeout.connect(self.sleep_move)

        # Step 17: chasing a butterfly
        self.butterfly = Butterfly()
        self.chasing_butterfly = False
        self.butterfly_ticks = 0
        self.bf_x = 0              # the middle of the butterfly
        self.bf_dir = 1            # 1 = flying right, -1 = flying left

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
        busy = self.hovering or self.drag_offset is not None or self.chasing
        busy = busy or self.chasing_butterfly or self.yawning or self.rolling
        if busy:
            self.sleep_timer.start(SLEEP_AFTER)
        else:
            self.start_yawn(True)

    def fall_asleep(self):
        self.sleeping = True
        self.chasing = False
        self.stop_butterfly()
        self.yawning = False
        self.rolling = False
        self.sleep_pose = "loaf"
        self.walk_target_x = None
        self.velocity = -0.1
        # Once in a while the sleeping cat rolls over
        self.sleep_move_timer.start(random.randint(8000, 15000))

    def wake_up(self):
        # During a focus session the cat stays asleep
        if self.pomodoro == "focus":
            return
        self.yawning = False
        if self.rolling:
            self.rolling = False
            self.flip = self.roll_start_flip
        self.sleep_pose = "loaf"
        if self.sleeping:
            self.sleeping = False
            self.velocity = 0.12   # a little stretch
        self.sleep_timer.start(SLEEP_AFTER)

    # ----- yawning -----
    def start_yawn(self, then_sleep):
        if self.sleeping or self.yawning:
            return
        self.yawning = True
        self.yawn_ticks = 80               # about 1.3 seconds
        self.yawn_then_sleep = then_sleep
        self.chasing = False
        self.stop_butterfly()
        self.rolling = False
        self.walk_target_x = None
        self.stop_purr()

    def yawn_step(self):
        self.yawn_ticks = self.yawn_ticks - 1
        progress = 1.0 - self.yawn_ticks / 80
        # Stretch up while yawning, then relax
        self.target = 1.0 + 0.12 * math.sin(math.pi * progress)
        if self.yawn_ticks <= 0:
            self.yawning = False
            if self.yawn_then_sleep:
                self.fall_asleep()

    # ----- rolling on the floor -----
    def sleep_move(self):
        # Timer ran out: the sleeping cat rolls over
        if self.sleeping and not self.rolling and not self.in_air:
            self.start_roll()

    def start_roll(self):
        if self.rolling or self.in_air or self.yawning:
            return
        self.rolling = True
        self.roll_ticks = 60               # about 1 second
        self.roll_dir = random.choice([-1, 1])
        self.roll_start_flip = self.flip
        self.walk_target_x = None
        self.chasing = False
        self.stop_butterfly()

    def roll_step(self):
        self.target = 1.0
        self.roll_ticks = self.roll_ticks - 1
        segment = self.roll_ticks // 10    # counts 5, 4, 3, 2, 1, 0

        # Roll along the floor and turn around at the edges
        x = self.x() + self.roll_dir * 2
        if x < self.min_x or x > self.max_x:
            self.roll_dir = -self.roll_dir
            x = max(self.min_x, min(x, self.max_x))
        self.move(x, self.y())

        # Tumble: turn the other way every 10 ticks
        if segment % 2 == 1:
            self.flip = self.roll_start_flip
        else:
            self.flip = -self.roll_start_flip

        if self.roll_ticks <= 0:
            self.rolling = False
            self.flip = self.roll_start_flip
            if self.sleeping:
                # Switch between lying on the back and sleeping in a loaf
                if self.sleep_pose == "loaf":
                    self.sleep_pose = "belly"
                    self.sleep_move_timer.start(random.randint(4000, 8000))
                else:
                    self.sleep_pose = "loaf"
                    self.sleep_move_timer.start(random.randint(8000, 15000))

    # ----- pomodoro -----
    def start_focus(self):
        self.pomodoro = "focus"
        self.pomodoro_timer.start(FOCUS_MINUTES * 60 * 1000)
        self.stop_purr()
        self.start_yawn(True)
        if self.sleeping:
            self.sleep_pose = "loaf"
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

    # ----- sound -----
    def reset_sound(self):
        # Starts the sound system fresh and loads both sounds.
        # We do this again after a quiet while, because the computer's sound
        # device can go to sleep, and then the old connection stays silent.
        if pygame is None:
            return
        try:
            pygame.mixer.quit()
            pygame.mixer.init()
            purr_path = resource_path("purr.wav")
            meow_path = resource_path("meow.wav")
            if os.path.exists(purr_path):
                self.purr_sound = pygame.mixer.Sound(purr_path)
                self.purr_sound.set_volume(0.3)
            else:
                print("Cannot find the purr sound:", purr_path)
            if os.path.exists(meow_path):
                self.meow_sound = pygame.mixer.Sound(meow_path)
                self.meow_sound.set_volume(0.7)
            else:
                print("Cannot find the meow sound:", meow_path)
            self.purring = False
        except Exception as error:
            print("Could not start the sound:", error)
        self.last_sound_time = time.time()

    def refresh_sound_if_quiet(self):
        # If no sound was started for 20 seconds, start the sound system fresh
        if pygame is not None and time.time() - self.last_sound_time > 20:
            self.reset_sound()

    def start_purr(self):
        if pygame is None or self.purring:
            return
        self.refresh_sound_if_quiet()
        if self.purr_sound is not None:
            self.purr_sound.play(loops=-1)    # -1 = repeat until we stop it
            self.purring = True
            self.last_sound_time = time.time()

    def stop_purr(self):
        if self.purr_sound is not None and self.purring:
            self.purr_sound.stop()
        self.purring = False

    def play_meow(self):
        self.refresh_sound_if_quiet()
        if self.meow_sound is not None:
            self.meow_sound.play()
            self.last_sound_time = time.time()
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

    # ----- chasing a butterfly -----
    def start_butterfly(self):
        if self.pomodoro == "focus":
            return
        self.wake_up()
        self.chasing = False
        self.rolling = False
        self.yawning = False
        self.walk_target_x = None
        self.chasing_butterfly = True
        self.butterfly_ticks = 480          # the butterfly stays about 8 seconds

        # The butterfly appears to one side of the cat
        side = random.choice([-1, 1])
        cat_middle = self.x() + WINDOW_W // 2
        self.bf_x = cat_middle + side * 150
        self.bf_x = max(self.min_x + WINDOW_W // 2, min(self.bf_x, self.max_x + WINDOW_W // 2))
        self.bf_dir = random.choice([-1, 1])
        self.butterfly.move(int(self.bf_x) - 15, self.ground_y + 25)
        self.butterfly.show()

    def stop_butterfly(self):
        self.chasing_butterfly = False
        self.butterfly.hide()

    def move_butterfly(self):
        self.butterfly_ticks = self.butterfly_ticks - 1
        if self.butterfly_ticks <= 0:
            self.stop_butterfly()
            return

        # Fly sideways, and sometimes turn around
        self.bf_x = self.bf_x + self.bf_dir * 2.5
        if random.random() < 0.01:
            self.bf_dir = -self.bf_dir
        left_edge = self.min_x + WINDOW_W // 2
        right_edge = self.max_x + WINDOW_W // 2
        if self.bf_x < left_edge:
            self.bf_x = left_edge
            self.bf_dir = 1
        if self.bf_x > right_edge:
            self.bf_x = right_edge
            self.bf_dir = -1

        # Flap the wings and float up and down
        bf_y = self.ground_y + 25 + 15 * math.sin(self.tick * 0.08)
        self.butterfly.wings_open = (self.tick // 5) % 2 == 0
        self.butterfly.move(int(self.bf_x) - 15, int(bf_y))
        self.butterfly.update()

    def butterfly_chase_step(self):
        cat_middle = self.x() + WINDOW_W // 2
        self.target = 1.0 + 0.05 * math.sin(self.tick * 0.5)

        # Look at the butterfly
        if self.bf_x < cat_middle:
            self.flip = 1
        else:
            self.flip = -1

        # Close enough: jump! The butterfly flutters away. Otherwise run after it.
        if abs(self.bf_x - cat_middle) < 30:
            if self.pounce_wait == 0:
                self.pounce()
                self.bf_dir = random.choice([-1, 1])
                self.bf_x = self.bf_x + self.bf_dir * 50
        elif self.bf_x > cat_middle:
            self.move(min(self.x() + 3, self.max_x), self.y())
        else:
            self.move(max(self.x() - 3, self.min_x), self.y())

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
        busy = self.sleeping or self.chasing or self.chasing_butterfly
        busy = busy or self.yawning or self.rolling or self.in_air
        if busy:
            return
        if self.drag_offset is None and not self.hovering:
            roll = random.random()
            if roll < 0.10:
                self.start_chase()          # 10%: chase the mouse (change to 0 to turn off)
            elif roll < 0.20:
                self.start_butterfly()      # 10%: chase a butterfly (change to 0 to turn off)
            elif roll < 0.70:
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
        self.check_hover()
        if self.bubble_ticks > 0:
            self.bubble_ticks = self.bubble_ticks - 1
        if self.pounce_wait > 0:
            self.pounce_wait = self.pounce_wait - 1

        # The butterfly keeps flying, even while the cat is jumping
        if self.chasing_butterfly:
            self.move_butterfly()

        # What is the cat doing right now?
        if self.in_air:
            self.fly()
        elif self.yawning:
            self.yawn_step()
        elif self.rolling:
            self.roll_step()
        elif self.sleeping:
            # Breathing: the sleeping cat slowly gets a little bigger and smaller
            self.target = 1.0 + 0.03 * math.sin(self.tick * 0.06)
        elif self.chasing:
            self.chase_step()
        elif self.chasing_butterfly:
            self.butterfly_chase_step()
        elif self.walk_target_x is not None:
            self.walk_step()
        else:
            self.target = 1.0

        # The mochi spring
        force = (self.target - self.scale_y) * 0.2
        self.velocity = (self.velocity + force) * 0.85
        self.scale_y = self.scale_y + self.velocity
        self.update()

    # ----- hovering: we check where the mouse is 60 times per second -----
    def check_hover(self):
        pos = QCursor.pos()
        cat_left = self.x() + WINDOW_W // 2 - 15 * PIXEL
        cat_right = cat_left + 30 * PIXEL
        cat_bottom = self.y() + 130
        if self.sleeping:
            cat_top = cat_bottom - 11 * PIXEL     # the sleeping cat is lower
        else:
            cat_top = cat_bottom - 18 * PIXEL
        inside = cat_left <= pos.x() <= cat_right and cat_top <= pos.y() <= cat_bottom
        if inside and not self.hovering:
            self.start_hover()
        elif not inside and self.hovering:
            self.end_hover()

    def start_hover(self):
        self.hovering = True
        if self.pomodoro == "focus":
            return              # no purring while you are focusing
        self.wake_up()
        self.stop_butterfly()
        self.walk_target_x = None
        self.velocity = -0.08
        self.start_purr()

    def end_hover(self):
        self.hovering = False
        self.stop_purr()
        self.sleep_timer.start(SLEEP_AFTER)

    # ----- mouse clicks -----
    def mousePressEvent(self, event):
        if event.button() == Qt.LeftButton:
            self.wake_up()
            self.chasing = False
            self.stop_butterfly()
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

        meow_action = menu.addAction("Meow")
        chase_action = menu.addAction("Chase my mouse")
        butterfly_action = menu.addAction("Chase a butterfly")
        yawn_action = menu.addAction("Yawn")
        roll_action = menu.addAction("Roll on the floor")
        sleep_action = menu.addAction("Yawn and go to sleep")
        window_action = menu.addAction("Sit on active window")
        window_action.setCheckable(True)
        window_action.setChecked(self.window_mode)
        if self.pomodoro == "focus":
            chase_action.setEnabled(False)
            butterfly_action.setEnabled(False)
            yawn_action.setEnabled(False)
            sleep_action.setEnabled(False)
        if self.sleeping:
            yawn_action.setEnabled(False)
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
        if chosen == meow_action:
            self.play_meow()
        elif chosen == chase_action:
            self.start_chase()
        elif chosen == butterfly_action:
            self.start_butterfly()
        elif chosen == yawn_action:
            self.start_yawn(False)
        elif chosen == roll_action:
            self.start_roll()
        elif chosen == sleep_action:
            self.start_yawn(True)
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
        if self.hovering or self.chasing or self.chasing_butterfly:
            wag_speed = 10
        else:
            wag_speed = 40
        tail_left = (self.tick // wag_speed) % 2 == 1

        # Choose which picture to draw
        if self.rolling:
            # While rolling, switch between the loaf and the belly-up picture
            segment = self.roll_ticks // 10
            if self.sleep_pose == "loaf":
                first = CAT_SLEEP
                second = CAT_BELLY
            else:
                first = CAT_BELLY
                second = CAT_SLEEP
            if segment % 2 == 1:
                picture = first
            else:
                picture = second
        elif self.yawning:
            picture = CAT_YAWN
        elif self.sleeping and self.sleep_pose == "belly":
            picture = CAT_BELLY
        elif self.sleeping:
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