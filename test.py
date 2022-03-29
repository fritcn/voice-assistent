import keyboard

def printing():
    print("Nice")

keyboard.add_hotkey("Ctrl+F", printing)
keyboard.wait()
