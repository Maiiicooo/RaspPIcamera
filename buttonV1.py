from picamera2 import Picamera2, Preview
from gpiozero import Button
import threading
import os
import time

# -----------------------------
# Camera setup
# -----------------------------
picam2 = Picamera2()

camera_config = picam2.create_preview_configuration(
    main={"size": (1920, 1080)}
)
picam2.configure(camera_config)
picam2.start_preview(Preview.QTGL, width=549, height=412)
picam2.start()

time.sleep(2)  # camera stabiliseren

# -----------------------------
# Map en teller setup
# -----------------------------
home_directory = os.path.expanduser("~")
images_directory = os.path.join(home_directory, "Desktop", "images")
os.makedirs(images_directory, exist_ok=True)

count_file = os.path.join(images_directory, "picture_count.txt")
if not os.path.exists(count_file):
    with open(count_file, "w") as f:
        f.write("0")

# -----------------------------
# Button setup
# -----------------------------
button = Button(16)
capture_lock = threading.Lock()

def capture():
    with capture_lock:
        # Teller lezen
        with open(count_file, "r") as f:
            number = int(f.read())

        number += 1
        filename = os.path.join(images_directory, f"pibz_{number}.jpg")

        # Foto opslaan
        picam2.capture_file(filename)
        print(f"Foto opgeslagen: {filename}")

        # Teller bijwerken
        with open(count_file, "w") as f:
            f.write(str(number))

# -----------------------------
# Button monitor thread
# -----------------------------
def button_monitor():
    while True:
        button.wait_for_press()
        capture()
        time.sleep(0.3)  # debounce

threading.Thread(target=button_monitor, daemon=True).start()

# -----------------------------
# Main loop
# -----------------------------
try:
    while True:
        time.sleep(1)
except KeyboardInterrupt:
    print("Afsluiten...")
    picam2.stop_preview()
    picam2.stop()
