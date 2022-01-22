from aqt import mw
from aqt import gui_hooks
from aqt.utils import QAction, qconnect

from .study_ahead import *

study_ahead_all = QAction(f"Study Ahead All Decks", mw)
qconnect(study_ahead_all.triggered, on_study_ahead_all)
mw.form.menuTools.addAction(study_ahead_all)

def add_tests():
    if mw.pm.name == 'addon_test':
        from .tests import run_tests
        test = QAction(f"Smarter Study Ahead Tests", mw)
        qconnect(test.triggered, run_tests)
        mw.form.menuTools.addAction(test)

gui_hooks.deck_browser_will_show_options_menu.append(on_show_options)
gui_hooks.profile_did_open.append(add_tests)

if __name__ == "__main__":
    print("This is an add-on for Anki. It is not intended to be run outside of Anki.")