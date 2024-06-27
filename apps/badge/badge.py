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

import badger2040
import jpegdec

from apps.app_base import AppBase


# Global Constants
WIDTH = badger2040.WIDTH
HEIGHT = badger2040.HEIGHT

BLACK = 0
WHITE = 15

# FIXME: read from data
# IMAGE_WIDTH = 104
IMAGE_WIDTH = 128

# FIXME: get rid of field-specific globals constants
HEADING_HEIGHT = 30
DETAILS_HEIGHT = 20
NAME_HEIGHT = HEIGHT - HEADING_HEIGHT - (DETAILS_HEIGHT * 2) - 2
TEXT_WIDTH = WIDTH - IMAGE_WIDTH - 1

HEADING_TEXT_SIZE = 0.6
DETAILS_TEXT_SIZE = 0.5

LEFT_PADDING = 5
NAME_PADDING = 20
DETAIL_SPACING = 10

# FIXME: list the json files
BADGE_PATH = "/apps/badge/data/gknoy.json"


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


# def _scale2(display, text: str, size: float, max_width: int):
#     font_size = size if size >= 0.1 else 2.0
#     while True:
#         text_width = display.measure_text(text, font_size)
#         if text_width >= max_width and font_size >= 0.1:
#             font_size -= 0.01
#         else:
#             return font_size


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
    detail1_title: str,
    detail1_text: str,
    detail2_title: str,
    detail2_text: str,
    badge_image: str,  # todo: supportm multiple images?
):
    display.set_pen(0)
    display.clear()

    # Draw badge image
    jpeg.open_file(badge_image)
    jpeg.decode(WIDTH - IMAGE_WIDTH, 0)

    # Draw a border around the image
    display.set_pen(0)
    display.line(WIDTH - IMAGE_WIDTH, 0, WIDTH - 1, 0)
    display.line(WIDTH - IMAGE_WIDTH, 0, WIDTH - IMAGE_WIDTH, HEIGHT - 1)
    display.line(WIDTH - IMAGE_WIDTH, HEIGHT - 1, WIDTH - 1, HEIGHT - 1)
    display.line(WIDTH - 1, 0, WIDTH - 1, HEIGHT - 1)

    # heading background
    display.set_pen(BLACK)
    display.rectangle(1, 1, TEXT_WIDTH, HEADING_HEIGHT - 1)

    # Draw the company
    render_text_drop_shadow(
        display=display,
        text=heading,
        x=LEFT_PADDING,
        y=(HEADING_HEIGHT // 2) + 1,
        width=WIDTH,
        text_size=HEADING_TEXT_SIZE,  # 0.6 !?
        fg=BLACK,
        bg=WHITE,
    )
    # display.set_pen(15)  # Change this to 0 if a white background is used
    # display.set_font("serif")
    # display.text(
    #     company, LEFT_PADDING, (COMPANY_HEIGHT // 2) + 1, WIDTH, COMPANY_TEXT_SIZE
    # )

    # Draw a white background behind the name
    display.set_pen(WHITE)
    display.rectangle(1, HEADING_HEIGHT + 1, TEXT_WIDTH, NAME_HEIGHT)

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
        max_text_width=(TEXT_WIDTH - 2 * NAME_PADDING),
        offsets=[1, -1],
    )
    # display.set_pen(0)
    # display.set_font("sans")
    # name_size = 2.0  # A sensible starting scale

    # Draw a white backgrounds behind the details
    display.set_pen(15)
    display.rectangle(1, HEIGHT - DETAILS_HEIGHT * 2, TEXT_WIDTH, DETAILS_HEIGHT - 1)
    display.rectangle(1, HEIGHT - DETAILS_HEIGHT, TEXT_WIDTH, DETAILS_HEIGHT - 1)

    # Draw the first detail's title and text

    # display.set_pen(0)
    display.set_font("sans")
    d1_title_len = display.measure_text(detail1_title, DETAILS_TEXT_SIZE)
    render_text_drop_shadow(
        display=display,
        text=detail1_title,
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
        text=detail1_text,
        x=5 + d1_title_len + DETAIL_SPACING,
        y=HEIGHT - ((DETAILS_HEIGHT * 3) // 2),
        width=WIDTH,
        text_size=DETAILS_TEXT_SIZE,
        fg=BLACK,
        bg=WHITE,
        font="sans",
        offsets=[1, -1],
    )

    # Draw the second detail's title and text
    d2_title_len = display.measure_text(detail2_title, DETAILS_TEXT_SIZE)
    render_text_drop_shadow(
        display=display,
        text=detail2_title,
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
        text=detail2_text,
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
#        Program setup
# ------------------------------

# Create a new Badger and set it to update NORMAL
display = badger2040.Badger2040()
display.led(128)
display.set_update_speed(badger2040.UPDATE_NORMAL)
display.set_thickness(2)

jpeg = jpegdec.JPEG(display.display)

# FIXME READ/PICK JSON
# # Open the badge file
# try:
#     badge = open(BADGE_PATH, "r")
# except OSError:
#     with open(BADGE_PATH, "w") as f:
#         f.write(DEFAULT_TEXT)
#         f.flush()
#     badge = open(BADGE_PATH, "r")

# # Read in the next 6 lines
# heading = badge.readline()  # "mustelid inc"
# name = badge.readline()  # "H. Badger"
# detail1_title = badge.readline()  # "RP2040"
# detail1_text = badge.readline()  # "2MB Flash"
# detail2_title = badge.readline()  # "E ink"
# detail2_text = badge.readline()  # "296x128px"
# badge_image = badge.readline()  # /badges/badge.jpg

# # Truncate all of the text (except for the name as that is scaled)
# heading = truncatestring(heading, HEADING_TEXT_SIZE, TEXT_WIDTH)

# detail1_title = truncatestring(detail1_title, DETAILS_TEXT_SIZE, TEXT_WIDTH)
# detail1_text = truncatestring(
#     detail1_text,
#     DETAILS_TEXT_SIZE,
#     TEXT_WIDTH
#     - DETAIL_SPACING
#     - display.measure_text(detail1_title, DETAILS_TEXT_SIZE),
# )

# detail2_title = truncatestring(detail2_title, DETAILS_TEXT_SIZE, TEXT_WIDTH)
# detail2_text = truncatestring(
#     detail2_text,
#     DETAILS_TEXT_SIZE,
#     TEXT_WIDTH
#     - DETAIL_SPACING
#     - display.measure_text(detail2_title, DETAILS_TEXT_SIZE),
# )


# ------------------------------
#       Main program
# ------------------------------


class BadgeApp(AppBase):
    def __init__(self):
        self.name = "badge"
        self.label = "Badge"
        # self.icon = "/apps/badge/badge/icon.jpg"
        self.icon = "/examples/icon-badge.jpg"
        # badger_os uses this
        self.module_name = "/apps/badge/badge"


if __name__ == "/apps/badge/badge":
    draw_badge(
        # TODO: read config from a json file
        display=display,
        jpeg=jpeg,
        heading="Myriad Genetics",
        name="Gabriel Knoy",
        detail1_title="gknoy@myriad.com",
        detail1_text="",
        detail2_title="Data Review Engineering",
        detail2_text="",
        # badge_image="/apps/badge/data/portrait-128.jpg",
        # badge_image="/apps/badge/data/kelaan-portrait-135x128-bw2.jpg",
        badge_image="/apps/badge/data/gknoy-badge-128.jpg",
    )
    while True:
        # Sometimes a button press or hold will keep the system
        # powered *through* HALT, so latch the power back on.
        display.keepalive()

        # If on battery, halt the Badger to save power, it will wake up if any of the front buttons are pressed
        display.halt()
