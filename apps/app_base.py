"""
# utils to let us describe icon + module logic for apps
"""

# constants from from launcher
FONT_SIZE = 2
WIDTH = 296


class AppBase:
    def __init__(self, name, label, icon, module_name):
        # predefine
        self.name = name
        self.label = label
        self.icon = icon  # full path+ext
        self.module_name = module_name
        self.jpeg = None
        self.font_size = FONT_SIZE

    def render_icon(self, display, jpeg, x):
        """
        # refactored magic from launcher's render()
        #
        #   display: badger display instance
        #   jpeg: already initialized jpegdec.JPEG instance
        #   x: ofset to render at (one of 3 cols)
        """
        # render app icon
        jpeg.open_file(self.icon)
        jpeg.decode(x - 26, 30)

        # render app label text
        display.set_pen(0)
        w = display.measure_text(self.name, FONT_SIZE)
        display.text(self.name, int(x - (w / 2)), 16 + 80, WIDTH, FONT_SIZE)


class Example(AppBase):
    EXAMPLE_DIR = "/examples"

    @classmethod
    def from_name(cls, name):
        icon_name_fragment = name.replace("_", "-")
        # png doesn't work anyway
        icon = f"{cls.EXAMPLE_DIR}/icon-{icon_name_fragment}.jpg"
        label = name.replace("_", " ")
        module_name = f"{cls.EXAMPLE_DIR}/{name}"
        return cls(name=name, label=label, icon=icon, module_name=module_name)
