"""
# utils to let us describe icon + module logic for apps
"""


class AppBase:
    def __init__(self, name, icon):
        self.name = name
        self.icon = f"icon-{name}.png"

    def render_icon(self, display):
        pass


class Example(AppBase):
    # derive name + icon from name
    def __init__(self, name):
        self.name = name
        self.icon = f"icon-{name}.png"

    # TODO: invoke the named example from /examples/
