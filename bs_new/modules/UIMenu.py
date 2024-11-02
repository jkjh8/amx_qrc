# ---------------------------------------------------------------------------- #
from modules.lib_tp import *


# ---------------------------------------------------------------------------- #
class UIMenu:
    def __init__(self, device):
        self.device = device
        self.selected_menu = 0
        self.setup()

    def set_page(self, pagename):
        tp_set_page(self.device, pagename)

    def show_popup(self, popupname):
        self.selected_menu = int(popupname)
        tp_show_popup(self.device, popupname)

    def hide_all_popup(self):
        self.selected_menu = 0
        tp_hide_all_popup(self.device)

    def update_menu_feedback(self):
        for idx in range(1, 5):
            tp_set_button(self.device, 1, idx + 10, self.selected_menu == idx)

    def select_menu(self, evt, idx_menu):
        if evt.value:
            self.selected_menu = int(idx_menu)
            self.show_popup("{0:0>3d}".format(idx_menu))
            self.update_menu_feedback()

    def close_menu(self, evt):
        if evt.value:
            self.hide_all_popup()
            self.update_menu_feedback()

    def setup(self):
        for idx in range(1, 5):
            tp_add_watcher(self.device, 1, idx + 10, lambda evt, idx=int(idx): self.select_menu(evt, int(idx)))

        tp_add_watcher(self.device, 1, 100, self.close_menu)

        for idx in range(1, 5):
            tp_set_button(self.device, 1, idx + 10, False)


# ---------------------------------------------------------------------------- #
