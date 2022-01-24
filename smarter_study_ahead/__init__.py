from aqt import mw
from aqt import gui_hooks
from aqt.utils import QAction, qconnect

from .study_ahead import *

study_ahead_all = QAction(f"Study Ahead All Decks", mw)
qconnect(study_ahead_all.triggered, on_study_ahead_all)
mw.form.menuTools.addAction(study_ahead_all)

def on_show_options(menu, deck_id) -> None:
    if (deck := mw.col.decks.get(deck_id))['name'][:11] != 'Study Ahead' and not mw.col.decks.is_filtered(deck_id):
        action = menu.addAction('Study Ahead')
        action.triggered.connect(lambda _, did=deck_id: study_ahead([did]))
    elif deck['name'] ==  'Study Ahead':
        action = menu.addAction('Reload All')
        action.triggered.connect(on_reload_all)
    elif deck['name'][:13] ==  'Study Ahead::':
        home_deck_id = mw.col.decks.id_for_name(deck['name'][13:])
        action = menu.addAction('Reload')
        action.triggered.connect(lambda _, did=home_deck_id: study_ahead([did]))

gui_hooks.deck_browser_will_show_options_menu.append(on_show_options)

def add_tests():
    if mw.pm.name == 'addon_test':
        from .tests import run_tests
        test = QAction(f"Smarter Study Ahead Tests", mw)
        qconnect(test.triggered, run_tests)
        mw.form.menuTools.addAction(test)

gui_hooks.profile_did_open.append(add_tests)

if __name__ == "__main__":
    print("This is an add-on for Anki. It is not intended to be run outside of Anki.")