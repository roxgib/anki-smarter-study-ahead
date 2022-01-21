from aqt import mw
from aqt import gui_hooks
from aqt.utils import QAction, qconnect

from .study_ahead import *

study_ahead_all = QAction(f"Study Ahead All Decks", mw)
qconnect(study_ahead_all.triggered, on_study_ahead_all)
mw.form.menuTools.addAction(study_ahead_all)

gui_hooks.deck_browser_will_show_options_menu.append(on_show_options)

if __name__ == "__main__":
    print("This is an add-on for Anki. It is not intended to be run outside of Anki.")
