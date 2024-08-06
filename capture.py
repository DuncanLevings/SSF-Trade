import psutil
from pynput import keyboard
import win32gui # type: ignore
import win32process # type: ignore
import pyperclip
import time

target_application = "pathofexile.exe"

def is_application_active(application_name):
    hwnd = win32gui.GetForegroundWindow()
    _, pid = win32process.GetWindowThreadProcessId(hwnd)
    
    for process in psutil.process_iter(['pid', 'name']):
        if process.info['pid'] == pid:
            if process.info['name'].lower() == application_name.lower():
                return True
    return False

def on_press(key, queue):
    try:
        if key.char == '`':
            controller = keyboard.Controller()
            controller.press(keyboard.Key.ctrl_l)
            controller.press('c')
            controller.release('c')
            controller.release(keyboard.Key.ctrl_l)
            
            time.sleep(0.1)
            copied_content = pyperclip.paste()
            queue.put(copied_content)
    except AttributeError:
        pass

def key_listener(queue):
    def on_press_wrapper(key):
        on_press(key, queue)
    
    with keyboard.Listener(on_press=on_press_wrapper) as listener:
        listener.join()
