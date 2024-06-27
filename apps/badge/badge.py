"""
# badge.py: Refactored app for simpler loading in the launcher
# (For now layout + sizes of items is basically the same as the example.)
# Badge config format:
#   {
#       "heading": "company",
#       "name": "name",
#       "r1_title": "title 1",
#       "r1_text": "text 1",
#       "r2_title": "title 2",
#       "r2_text": "text 2",
#       "image": {
#           "file": "badge.jpg",  // no png sadly
#           "width": 135,  // pixels
#       }
#   }

# TODO:
#   - read /apps/badge/data for directories containing json configs
#   - let up/down cycle between displayed badge
#   - support multiple icons (?), toggled with A button or something
#   - support jpg or png icons
#   - parametrize-width of icon
"""

import badger_os
import jpegdec
import os
from badger2040 import Badger2040, HEIGHT, WIDTH, UPDATE_NORMAL, BUTTON_UP, BUTTON_DOWN
from ujson import load as load_json

from apps.app_base import AppBase

DATA_DIR = "/apps/badge/data"

BLACK = 0
WHITE = 15

# FIXME: read from data
# IMAGE_WIDTH = 104
# IMAGE_WIDTH = 128

# FIXME: get rid of field-specific globals constants
HEADING_HEIGHT = 30
DETAILS_HEIGHT = 20
NAME_HEIGHT = HEIGHT - HEADING_HEIGHT - (DETAILS_HEIGHT * 2) - 2
# TEXT_WIDTH = WIDTH - IMAGE_WIDTH - 1

HEADING_TEXT_SIZE = 0.6
DETAILS_TEXT_SIZE = 0.5

LEFT_PADDING = 5
NAME_PADDING = 20
DETAIL_SPACING = 10

# FIXME: list the json files
# BADGE_PATH = "/apps/badge/data/gknoy.json"


# ------------------------------
#      Utility functions
# ------------------------------


# Reduce the size of a string until it fits within a given width
def truncatestring(display, text: str, text_size: float, width: int):
    while True:
        length = display.measure_text(text, text_size)
        if length > 0 and length > width:
            text = text[:-1]
        else:
            text += ""
            return text


# ------------------------------
#      Drawing functions
# ------------------------------


def scale_font_to_fit_width(display, text: str, size: float, max_width: int):
    # Find the font size that lets text fit within a width
    # assumes that we've already done display.set_font(...)
    font_size = size if size >= 0.1 else 2.0
    text_width = display.measure_text(text, font_size)
    while text_width > max_width and font_size >= 0.1:
        font_size -= 0.01
        text_width = display.measure_text(text, font_size)
    return font_size


def render_text(
    display,  # picographics instance e.g. Badger2040().display
    text: str,
    x: int,
    y: int,
    width: int,
    text_size: float,
    color: int,
    font: str | None = None,
    scale_font=False,
    max_text_width=WIDTH,
):
    display.set_pen(color)  # Change this to 0 if a white background is used
    if font is not None:
        display.set_font(font)
    if scale_font:
        text_size = scale_font_to_fit_width(display, text, text_size, max_text_width)
    display.text(text, x, y, width, text_size)


def render_text_drop_shadow(
    display,  # picographics instance e.g. Badger2040().display
    text: str,
    x: int,
    y: int,
    width: int,
    text_size: float,
    fg: int,
    bg: int,
    font: str | None = None,
    scale_font=False,
    max_text_width=WIDTH,
    offsets: list[int] = None,
):
    if offsets is None:
        offsets = [1]
    for offset in offsets:
        render_text(
            display,
            text,
            x + offset,
            y + offset,
            width,
            text_size,
            bg,
            font,
            scale_font,
            max_text_width,
        )
    render_text(
        display, text, x, y, width, text_size, fg, font, scale_font, max_text_width
    )


# Draw the badge, including user text
# FIXME: parametrize with data
def draw_badge(
    display,
    jpeg,
    heading: str,
    name: str,
    r1_title: str,
    r1_text: str,
    r2_title: str,
    r2_text: str,
    image: dict,  # {file, width, dithered}
):
    display.set_pen(0)
    display.clear()

    assert type(image) is dict, "image != {file,width,dithered}"

    image_file = f"{DATA_DIR}/{image['file']}"
    image_width = int(image["width"])
    pre_dithered = image.get("dithered", False)

    text_width = WIDTH - image_width - 1

    # Draw badge image
    jpeg.open_file(image_file)
    jpeg.decode(
        WIDTH - image_width,  # align on right border
        0,  # y
        0,  # scale: 0, and then 2/4/8 are half/qtr/eighth
        pre_dithered,
    )

    # Draw a border around the image
    display.set_pen(0)
    display.line(WIDTH - image_width, 0, WIDTH - 1, 0)
    display.line(WIDTH - image_width, 0, WIDTH - image_width, HEIGHT - 1)
    display.line(WIDTH - image_width, HEIGHT - 1, WIDTH - 1, HEIGHT - 1)
    display.line(WIDTH - 1, 0, WIDTH - 1, HEIGHT - 1)

    # heading background
    display.set_pen(BLACK)
    display.rectangle(1, 1, text_width, HEADING_HEIGHT - 1)

    # Draw the heading
    render_text_drop_shadow(
        display=display,
        text=heading,
        x=LEFT_PADDING,
        y=(HEADING_HEIGHT // 2) + 1,
        width=WIDTH,
        text_size=HEADING_TEXT_SIZE,  # 0.6 !?
        fg=WHITE,
        bg=BLACK,
    )

    # Draw a white background behind the name
    display.set_pen(WHITE)
    display.rectangle(1, HEADING_HEIGHT + 1, text_width, NAME_HEIGHT)

    # Draw the name, scaling it based on the available width
    # name_size = scale_font_to_fit_width(display, name, 2.0, (TEXT_WIDTH - NAME_PADDING))
    # name_len = display.measure_text(name, DETAILS_TEXT_SIZE)
    render_text_drop_shadow(
        display=display,
        text=name,
        # FIXME: text centering
        x=NAME_PADDING,  # (TEXT_WIDTH - name_len) // 2,
        y=(NAME_HEIGHT // 2) + HEADING_HEIGHT + 1,
        width=WIDTH,
        text_size=2.0,
        fg=BLACK,
        bg=WHITE,
        font="sans",
        scale_font=True,
        max_text_width=(text_width - 2 * NAME_PADDING),
        offsets=[1, -1],
    )

    # Draw a white backgrounds behind the details
    display.set_pen(15)
    display.rectangle(1, HEIGHT - DETAILS_HEIGHT * 2, text_width, DETAILS_HEIGHT - 1)
    display.rectangle(1, HEIGHT - DETAILS_HEIGHT, text_width, DETAILS_HEIGHT - 1)

    # Draw the first detail row's title and text
    # display.set_pen(0)
    display.set_font("sans")
    d1_title_len = display.measure_text(r1_title, DETAILS_TEXT_SIZE)
    render_text_drop_shadow(
        display=display,
        text=r1_title,
        x=LEFT_PADDING,
        y=HEIGHT - ((DETAILS_HEIGHT * 3) // 2),
        width=WIDTH,
        text_size=DETAILS_TEXT_SIZE,
        fg=BLACK,
        bg=WHITE,
        font="sans",
        offsets=[1, -1],
    )
    render_text_drop_shadow(
        display=display,
        text=r1_text,
        x=5 + d1_title_len + DETAIL_SPACING,
        y=HEIGHT - ((DETAILS_HEIGHT * 3) // 2),
        width=WIDTH,
        text_size=DETAILS_TEXT_SIZE,
        fg=BLACK,
        bg=WHITE,
        font="sans",
        offsets=[1, -1],
    )

    # Draw the second detail row's title and text
    d2_title_len = display.measure_text(r2_title, DETAILS_TEXT_SIZE)
    render_text_drop_shadow(
        display=display,
        text=r2_title,
        x=LEFT_PADDING,
        y=HEIGHT - (DETAILS_HEIGHT // 2),
        width=WIDTH,
        text_size=DETAILS_TEXT_SIZE,
        fg=BLACK,
        bg=WHITE,
        font="sans",
        offsets=[1, -1],
    )
    render_text_drop_shadow(
        display=display,
        text=r2_text,
        x=LEFT_PADDING + d2_title_len + DETAIL_SPACING,
        y=HEIGHT - (DETAILS_HEIGHT // 2),
        width=WIDTH,
        text_size=DETAILS_TEXT_SIZE,
        fg=BLACK,
        bg=WHITE,
        font="sans",
        offsets=[1, -1],
    )

    display.update()


# ------------------------------
# reading options
# ------------------------------


def load_badge_configs():
    return [
        read_json(f"{DATA_DIR}/{fname}")
        for fname in os.listdir(DATA_DIR)
        if fname.endswith(".json")
    ]


def read_json(fname):
    with open(fname) as f:
        return load_json(f)


# ------------------------------
# Program setup
# ------------------------------

# Create a new Badger and set it to update NORMAL
display = Badger2040()
display.led(128)
display.set_update_speed(UPDATE_NORMAL)
display.set_thickness(2)

jpeg = jpegdec.JPEG(display.display)

state = {"index": 0}


# ------------------------------
#       Main program
# ------------------------------


def handle_buttons(state, display, jpeg, badge_configs):
    changed = False
    if display.pressed(BUTTON_DOWN):
        state["index"] = (state["index"] + 1) % len(badge_configs)
        print(f">>> DOWN: {state['index']}")
        changed = True

    if display.pressed(BUTTON_UP):
        state["index"] = (state["index"] - 1) % len(badge_configs)
        print(f">>> UP: {state['index']}")
        changed = True

    if changed:
        badger_os.state_save("badge", state)
        draw_badge(display, jpeg, **(badge_configs[state["index"]]))


class BadgeApp(AppBase):
    def __init__(self):
        self.name = "badge"
        self.label = "Badge"
        # self.icon = "/apps/badge/badge/icon.jpg"
        self.icon = "/examples/icon-badge.jpg"
        # badger_os uses this
        self.module_name = "/apps/badge/badge"


if __name__ == "/apps/badge/badge":
    # track state like image example

    badger_os.state_load("badge", state)
    badge_configs = load_badge_configs()
    draw_badge(display, jpeg, **(badge_configs[state["index"]]))

    while True:
        # Sometimes a button press or hold will keep the system
        # powered *through* HALT, so latch the power back on.
        display.keepalive()

        handle_buttons(state, display, jpeg, badge_configs)

        # If on battery, halt the Badger to save power, it will wake up if any of the front buttons are pressed
        display.halt()
