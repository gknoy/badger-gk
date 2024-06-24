"""
# Customized launcher for badger2040
#
# TODO:
# - Keep able to run default /examples/*
# - Add custom apps to run from /apps/
"""

import gc
import os
import time
import math
import badger2040
import badger_os
import jpegdec

# Note: example code implies png support but importing this fails
# import pngdec


# TODO: dynamically get all apps in apps/ instead of importing them directly :-/
from apps.badge.badge import BadgeApp
from apps.app_base import Example


# CUSTOM_APPS = [badge_app]
APP_DIR = "/apps"
EXAMPLE_DIR = "/examples"
FONT_SIZE = 2

changed = False
exited_to_launcher = False
woken_by_button = (
    badger2040.woken_by_button()
)  # Must be done before we clear_pressed_to_wake


if badger2040.pressed_to_wake(badger2040.BUTTON_A) and badger2040.pressed_to_wake(
    badger2040.BUTTON_C
):
    # Pressing A and C together at start quits app
    exited_to_launcher = badger_os.state_clear_running()
    badger2040.reset_pressed_to_wake()
else:
    # Otherwise restore previously running app
    badger_os.state_launch()


display = badger2040.Badger2040()
display.set_font("bitmap8")
display.led(128)

# png = pngdec.PNG(display.display)
jpeg = jpegdec.JPEG(display.display)

state = {"page": 0, "running": "launcher"}

badger_os.state_load("launcher", state)

# FIXME: use these when populating list of apps/icons
app_names = []  # FIXME
# app_names = [app.name for app in CUSTOM_APPS]
examples = [x[:-3] for x in os.listdir(EXAMPLE_DIR) if x.endswith(".py")]
example_apps = [Example.from_name(name) for name in examples]
all_apps = [BadgeApp()] + example_apps

# Approximate center lines for buttons A, B and C
centers = (41, 147, 253)

MAX_PAGE = math.ceil((len(app_names) + len(examples)) / 3)

WIDTH = 296


def map_value(input, in_min, in_max, out_min, out_max):
    return (((input - in_min) * (out_max - out_min)) / (in_max - in_min)) + out_min


def draw_disk_usage(x):
    _, f_used, _ = badger_os.get_disk_usage()

    display.set_pen(15)
    display.image(
        bytearray(
            (
                0b00000000,
                0b00111100,
                0b00111100,
                0b00111100,
                0b00111000,
                0b00000000,
                0b00000000,
                0b00000001,
            )
        ),
        8,
        8,
        x,
        4,
    )
    display.rectangle(x + 10, 3, 80, 10)
    display.set_pen(0)
    display.rectangle(x + 11, 4, 78, 8)
    display.set_pen(15)
    display.rectangle(x + 12, 5, int(76 / 100.0 * f_used), 6)
    display.text("{:.2f}%".format(f_used), x + 91, 4, WIDTH, 1.0)


def render_icon(icon, label, display, jpeg, x):
    """
    # prototyping reusable icon rendering
    # (todo: refactor to use App)
    """
    # render app icon
    jpeg.open_file(icon)
    jpeg.decode(x - 26, 30)

    # render app label text
    display.set_pen(0)
    w = display.measure_text(label, FONT_SIZE)
    display.text(label, int(x - (w / 2)), 16 + 80, WIDTH, FONT_SIZE)


def render():
    display.set_pen(15)
    display.clear()
    display.set_pen(0)

    # max_icons = min(3, len(examples[(state["page"] * 3) :]))
    max_icons = min(3, len(all_apps[(state["page"] * 3) :]))

    # FIXME: loop over apps and call app.render_icon(...)
    for i in range(max_icons):
        x = centers[i]
        # app = example_apps[i + (state["page"] * 3)]
        app = all_apps[i + (state["page"] * 3)]

        try:
            app.render_icon(display, jpeg, x)
            # decorate label so we know it's working
            # render_icon(icon, f"^{label}", display, jpeg, x)
        except (RuntimeError, Exception) as e:
            print(f">>> Using fallback rendering for {app.name}")
            print(f"    --> {e}")
            # label = examples[i + (state["page"] * 3)]
            # icon_label = label.replace("_", "-")
            # # png doesn't work anyway
            # icon = f"{EXAMPLE_DIR}/icon-{icon_label}.jpg"
            # label = label.replace("_", " ")
            label = app.label
            icon = app.icon
            try:
                # lib.open_file(f"{icon}.{ext}")
                jpeg.open_file(icon)
                jpeg.decode(x - 26, 30)
            except (OSError, RuntimeError) as e:
                print(f"  -> {e}")
            display.set_pen(0)
            label = f"!{label}"
            w = display.measure_text(label, FONT_SIZE)
            display.text(label, int(x - (w / 2)), 16 + 80, WIDTH, FONT_SIZE)

    for i in range(MAX_PAGE):
        x = 286
        y = int((128 / 2) - (MAX_PAGE * 10 / 2) + (i * 10))
        display.set_pen(0)
        display.rectangle(x, y, 8, 8)
        if state["page"] != i:
            display.set_pen(15)
            display.rectangle(x + 1, y + 1, 6, 6)

    display.set_pen(0)
    display.rectangle(0, 0, WIDTH, 16)
    draw_disk_usage(90)
    display.set_pen(15)
    display.text("badgerOS", 4, 4, WIDTH, 1.0)

    display.update()


def wait_for_user_to_release_buttons():
    while display.pressed_any():
        time.sleep(0.01)


def launch_app(index):
    wait_for_user_to_release_buttons()

    # change from list of example filenames
    # to list of App objects, using app.module_name instead of "file"
    # file = examples[(state["page"] * 3) + index]
    # file = f"{EXAMPLE_DIR}/{file}"
    # print(f">>> launching {file}")

    app = all_apps[(state["page"] * 3) + index]
    file = app.module_name
    print(f">>> launching {file}")

    for k in locals().keys():
        if k not in ("gc", "file", "badger_os"):
            del locals()[k]

    gc.collect()

    badger_os.launch(file)


def button(pin):
    global changed
    changed = True

    if pin == badger2040.BUTTON_A:
        launch_app(0)
    if pin == badger2040.BUTTON_B:
        launch_app(1)
    if pin == badger2040.BUTTON_C:
        launch_app(2)
    if pin == badger2040.BUTTON_UP:
        state["page"] = (state["page"] - 1) % MAX_PAGE
        render()
    if pin == badger2040.BUTTON_DOWN:
        state["page"] = (state["page"] + 1) % MAX_PAGE
        render()


if exited_to_launcher or not woken_by_button:
    wait_for_user_to_release_buttons()
    display.set_update_speed(badger2040.UPDATE_MEDIUM)
    render()

display.set_update_speed(badger2040.UPDATE_FAST)

while True:
    # Sometimes a button press or hold will keep the system
    # powered *through* HALT, so latch the power back on.
    display.keepalive()

    if display.pressed(badger2040.BUTTON_A):
        button(badger2040.BUTTON_A)
    if display.pressed(badger2040.BUTTON_B):
        button(badger2040.BUTTON_B)
    if display.pressed(badger2040.BUTTON_C):
        button(badger2040.BUTTON_C)

    if display.pressed(badger2040.BUTTON_UP):
        button(badger2040.BUTTON_UP)
    if display.pressed(badger2040.BUTTON_DOWN):
        button(badger2040.BUTTON_DOWN)

    if changed:
        badger_os.state_save("launcher", state)
        changed = False

    display.halt()
