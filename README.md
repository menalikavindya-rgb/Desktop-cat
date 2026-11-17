# Desktop Cat 🐱

A pixel-art desktop pet for Windows. A soft, squishy cat lives on your screen: it purrs when you pet it, chases your mouse and butterflies, yawns, rolls around, falls asleep, sits on top of the window you're using, and can act as a Pomodoro timer.

Built with **Python**, **PySide6 (Qt)** and **pygame**. The cat is drawn entirely in code from a small grid of letters, so there are no sprite sheets and you can redraw it yourself.



## Features

- **Mochi animation:** the cat squashes and stretches like a soft rice cake when it lands, jumps, or is picked up
- **Purrs when you pet it:** hover the mouse over the cat to hear it purr and see a floating heart; the tail wags faster when it's happy
- **Wanders around:** walks along the bottom of your screen, blinks, and turns to face the direction it walks
- **Chases your mouse:** runs toward your cursor and pounces on it
- **Chases butterflies:** a small butterfly flutters out for a few seconds and the cat runs after it
- **Yawns before bed:** stretches and yawns, then curls up in a loaf with floating *z z Z*
- **Rolls on the floor:** while sleeping, it now and then rolls over onto its back and later rolls back into a loaf
- **Sits on your active window:** hops onto the top edge of the window you're using and walks along it
- **Pomodoro buddy:** sleeps while you focus, then wakes up and meows when it's break time
- **Drag and drop:** pick the cat up and let go; it falls with gravity and squashes when it lands

## Requirements

- Windows 10 or 11
- Python 3.12
- [PySide6](https://pypi.org/project/PySide6/) (the `PySide6-Essentials` package is enough)
- [pygame](https://pypi.org/project/pygame/) (for the purr and meow sounds)

## Installation

1. Clone this repository:

   ```
   git clone https://github.com/<your-username>/<your-repo>.git
   cd <your-repo>
   ```

2. Install the requirements:

   ```
   py -3.12 -m pip install -r requirements.txt
   ```

3. Add two sound files in the same folder as `cat.py`:

   - `purr.wav`: a short looping purr (about 3 to 5 seconds works well)
   - `meow.wav`: a short meow

   They must be standard **16-bit PCM WAV** files. Without them, the cat still runs silently, and the break-time meow falls back to the Windows beep.

4. Run it:

   ```
   py -3.12 cat.py
   ```

## How to use

| Action | What happens |
|---|---|
| Hover the mouse over the cat | Purrs, shows a heart, wags its tail |
| Click and drag | Picks the cat up; it falls when you let go |
| Right-click | Opens the menu below |

### Right-click menu

| Item | What it does |
|---|---|
| Meow | Plays the meow sound (handy for testing audio) |
| Chase my mouse | The cat runs after your cursor for about 8 seconds |
| Chase a butterfly | A butterfly appears and the cat chases it |
| Yawn | The cat yawns and stays awake |
| Roll on the floor | The cat rolls along the floor |
| Yawn and go to sleep | The cat yawns, then falls asleep |
| Sit on active window | Turns the window-sitting behavior on or off |
| Start focus (25 min) | Starts a Pomodoro session; the cat sleeps until the break |
| Quit | Closes the cat |

During a focus session the cat stays asleep and doesn't purr, so it won't distract you. When the focus time ends, it wakes up, meows, and a speech bubble says it's break time.

## Customization

Settings are at the top of `cat.py`:

| Setting | Meaning | Default |
|---|---|---|
| `PIXEL` | Size of one pixel on screen (3 = small, 5 = large) | `3` |
| `SLEEP_AFTER` | Milliseconds without petting before the cat yawns and sleeps | `70000` |
| `FOCUS_MINUTES` | Pomodoro focus length | `25` |
| `BREAK_MINUTES` | Pomodoro break length | `5` |

If you raise `PIXEL` above 5, also raise `WINDOW_W` and `WINDOW_H` so the cat isn't cut off.

### Redrawing the cat

Each pose is a list of text rows, and every letter is one colored square:

| Letter | Color |
|---|---|
| `K` | Dark outline |
| `W` | White fur |
| `P` | Pink (cheeks, ears, tongue) |
| `G` | Grey (tail stripes) |
| `R` | Red (heart) |
| `.` | Empty (see-through) |

Change a letter and that pixel changes. Every row in a pose must stay exactly **30 characters** wide, or the picture will look crooked. To make a differently colored cat, edit the colors in the `COLORS` dictionary (for example, change the `W` color for an orange or black cat).

## Building an .exe

If you'd rather double-click than run Python each time:

```
py -3.12 -m pip install pyinstaller
py -3.12 -m PyInstaller --noconsole --onefile --add-data "purr.wav;." --add-data "meow.wav;." cat.py
```

The finished program appears in the `dist` folder. With `--noconsole` you won't see error messages, so run `python cat.py` first if something isn't working.

## How it works

- **Window:** a frameless, transparent, always-on-top Qt window that only shows the cat
- **Drawing:** `QPainter` draws each pixel square from the letter grids; scaling the whole picture gives the squash and stretch
- **Mochi spring:** the cat's height is pulled toward a target value with a little bounce, and one small spring drives all the soft movement
- **Hover detection:** the mouse position is checked 60 times per second, so hovering works reliably
- **Window sitting:** the Windows API (through `ctypes`) finds the active window's position, and the cat jumps onto its top edge
- **Sound:** `pygame` plays the purr and meow; the sound system restarts itself after a quiet spell so audio keeps working if the sound device goes to sleep
- **Butterfly:** a second tiny transparent window that mouse clicks pass through

## Troubleshooting

- **`ModuleNotFoundError: No module named 'PySide6'`:** you installed the packages into a different Python than the one running the cat. Use `py -3.12 -m pip install ...` and `py -3.12 cat.py` so both use the same Python.
- **No sound:** check that `purr.wav` and `meow.wav` are next to `cat.py` and are real 16-bit PCM WAV files (not renamed MP3s). The terminal prints `Cannot find the purr sound` or `Could not start the sound` if something is wrong. Right-click the cat and choose **Meow** to test.
- **The cat sits at the wrong height on a window:** Windows display scaling can shift positions slightly. Turn off **Sit on active window** in the menu if it bothers you.

## Limitations

- Windows only: the window-sitting feature uses the Windows API
- Works on the main monitor only
- Maximized, minimized, and very small windows are ignored, so the cat stays at the bottom of the screen



