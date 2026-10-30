"""Send keystrokes to Windows using SendInput (no extra libraries needed)."""
import ctypes
import struct
import threading
from ctypes import wintypes

KEYEVENTF_EXTENDEDKEY = 0x0001
KEYEVENTF_KEYUP = 0x0002
KEYEVENTF_UNICODE = 0x0004
INPUT_KEYBOARD = 1

ULONG_PTR = wintypes.WPARAM


class KEYBDINPUT(ctypes.Structure):
    _fields_ = [("wVk", wintypes.WORD), ("wScan", wintypes.WORD),
                ("dwFlags", wintypes.DWORD), ("time", wintypes.DWORD),
                ("dwExtraInfo", ULONG_PTR)]


class MOUSEINPUT(ctypes.Structure):
    _fields_ = [("dx", wintypes.LONG), ("dy", wintypes.LONG),
                ("mouseData", wintypes.DWORD), ("dwFlags", wintypes.DWORD),
                ("time", wintypes.DWORD), ("dwExtraInfo", ULONG_PTR)]


class _INPUTUNION(ctypes.Union):
    _fields_ = [("ki", KEYBDINPUT), ("mi", MOUSEINPUT)]


class INPUT(ctypes.Structure):
    _anonymous_ = ("u",)
    _fields_ = [("type", wintypes.DWORD), ("u", _INPUTUNION)]


user32 = ctypes.WinDLL("user32", use_last_error=True)
user32.SendInput.argtypes = (wintypes.UINT, ctypes.POINTER(INPUT), ctypes.c_int)
user32.SendInput.restype = wintypes.UINT
user32.VkKeyScanW.argtypes = (wintypes.WCHAR,)
user32.VkKeyScanW.restype = ctypes.c_short

_lock = threading.Lock()

# name -> (virtual key, extended?)
SPECIAL = {
    "enter": (0x0D, False), "backspace": (0x08, False), "tab": (0x09, False),
    "esc": (0x1B, False), "space": (0x20, False),
    "delete": (0x2E, True), "insert": (0x2D, True),
    "left": (0x25, True), "up": (0x26, True), "right": (0x27, True), "down": (0x28, True),
    "home": (0x24, True), "end": (0x23, True),
    "pageup": (0x21, True), "pagedown": (0x22, True),
}
for _i in range(1, 13):
    SPECIAL["f%d" % _i] = (0x6F + _i, False)

MODS = {"ctrl": (0x11, False), "alt": (0x12, False),
        "shift": (0x10, False), "win": (0x5B, True)}


def _key(vk=0, scan=0, flags=0):
    i = INPUT(type=INPUT_KEYBOARD)
    i.ki = KEYBDINPUT(vk, scan, flags, 0, 0)
    return i


def _send(items):
    if not items:
        return
    arr = (INPUT * len(items))(*items)
    user32.SendInput(len(items), arr, ctypes.sizeof(INPUT))


def _tap(vk, ext=False):
    f = KEYEVENTF_EXTENDEDKEY if ext else 0
    return [_key(vk, 0, f), _key(vk, 0, f | KEYEVENTF_KEYUP)]


def type_text(text, back=0):
    """Press Backspace `back` times, then type `text` (any Unicode)."""
    items = []
    for _ in range(max(0, min(int(back), 500))):
        items += _tap(0x08)
    for ch in text[:2000]:
        if ch == "\n":
            items += _tap(0x0D)
        elif ch == "\t":
            items += _tap(0x09)
        elif ch in ("\r", "\u200b"):
            continue
        else:
            for unit in struct.unpack("<%dH" % (len(ch.encode("utf-16-le")) // 2),
                                      ch.encode("utf-16-le")):
                items.append(_key(0, unit, KEYEVENTF_UNICODE))
                items.append(_key(0, unit, KEYEVENTF_UNICODE | KEYEVENTF_KEYUP))
    with _lock:
        _send(items)


def press_key(name, mods=()):
    """Press a named key (or a single character) while holding modifiers."""
    name = str(name)
    if name.lower() in SPECIAL:
        vk, ext = SPECIAL[name.lower()]
    elif len(name) == 1:
        res = user32.VkKeyScanW(name)
        if res == -1:
            type_text(name)
            return
        vk, ext = res & 0xFF, False
    else:
        return
    mod_list = [MODS[m] for m in mods if m in MODS]
    items = []
    for mvk, mext in mod_list:
        items.append(_key(mvk, 0, KEYEVENTF_EXTENDEDKEY if mext else 0))
    items += _tap(vk, ext)
    for mvk, mext in reversed(mod_list):
        items.append(_key(mvk, 0, KEYEVENTF_KEYUP | (KEYEVENTF_EXTENDEDKEY if mext else 0)))
    with _lock:
        _send(items)
