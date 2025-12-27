from picamera2 import Picamera2, Preview
import time
from datetime import datetime
from gpiozero import Button
import threading
import os

# -----------------------------
# Camera setup (MAIN THREAD)
# -----------------------------
picam2 = Picamera2()

camera_config = picam2.create_preview_configuration(
    main={"size": (1920, 1080)}
)
picam2.configure(camera_config)

picam2.start_preview(Preview.QTGL, width=549, height=412)
picam2.start()

time.sleep(2)  # camera laten stabiliseren

# -----------------------------
# Button setup
# -----------------------------
button = Button(16)

capture_in_progress = False

# -----------------------------
# Zorg dat picture_count.txt bestaat
# -----------------------------
if not os.path.exists("picture_count.txt"):
    with open("picture_count.txt", "w") as f:
        f.write("0")

# -----------------------------
# Capture function (NO THREAD)
# -----------------------------
def capture():
    global capture_in_progress

    with open("picture_count.txt", "r") as file:
        number = int(file.read())

    number += 1

    home_directory = os.path.expanduser("~")
    images_directory = os.path.join(home_directory, "Desktop", "images")
    os.makedirs(images_directory, exist_ok=True)

    filename = os.path.join(images_directory, f"pibz_{number}.jpg")
    metadata = picam2.capture_file(filename)

    with open("picture_count.txt", "w") as file:
        file.write(str(number))

    print(f"Foto opgeslagen: {filename}")
    print(metadata)

    capture_in_progress = False

# -----------------------------
# Button monitor (THREAD OK)
# -----------------------------
def button_monitor():
    global capture_in_progress
    while True:
        if button.is_pressed and not capture_in_progress:
            capture_in_progress = True
            capture()
            time.sleep(0.5)  # debounce

# -----------------------------
# Start button thread
# -----------------------------
button_thread = threading.Thread(target=button_monitor, daemon=True)
button_thread.start()

# -----------------------------
# Main loop (blijft draaien)
# -----------------------------
try:
    while True:
        time.sleep(1)
except KeyboardInterrupt:
    print("Afsluiten...")
    picam2.stop_preview()
    picam2.stop()
