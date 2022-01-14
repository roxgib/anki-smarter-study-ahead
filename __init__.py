"""
Todo:
    - Group filtered deck creation as one undo step
    - Order cards by dueness
    - Pick best for study ahead all decks
    - Better handling of child decks
"""

from aqt import mw
from aqt.utils import qconnect, QAction, tooltip
from aqt import gui_hooks

def create_filtered_deck(deck_id, tt = True) -> int:
    config = mw.addonManager.getConfig(__name__)
    max_days_ahead = config['max_days_ahead']
    max_cards = config['max_cards']
    max_multiple = config['max_multiple']

    deck = mw.col.decks.get(deck_id)

    deck_name = deck['name']
    timeToday = deck['timeToday'][0]

    if (old_f_deck := mw.col.decks.id_for_name('Study Ahead::' + deck_name)) != None:
        mw.col.decks.remove([old_f_deck])

    ids = list()

    for card_id in mw.col.find_cards(f'"deck:{deck_name}" prop:due<={max_days_ahead} -is:due -is:learn -is:suspended -is:buried'):
        card = mw.col.get_card(card_id)
        if (multiple := card.ivl / (card.due - timeToday)) > max_multiple:
            ids.append((card_id, multiple))

    if len(ids) == 0: 
        if tt: tooltip(f"Couldn't find any suitable cards to study ahead.")
        return

    ids = [k[0] for k in sorted(ids, key = lambda x: x[1])][:max_cards]

    filter_string = '(' + ' OR '.join([f'cid:{id}' for id in ids]) + ')' + ' -is:due -is:learn -is:suspended -is:buried -rated:1'

    f_deck_id = mw.col.decks.new_filtered('Study Ahead::' + deck_name)
    f_deck = mw.col.decks.current()

    f_deck['resched'] = True
    f_deck['delays'] = None
    f_deck['terms'] = [[filter_string, 10000, 6]]
    
    mw.col.decks.save(f_deck)
    mw.col.sched.rebuild_filtered_deck(f_deck_id)
    mw.reset()

    if tt: tooltip(f"Created filtered deck 'Study Ahead::{deck_name}' with {len(ids)} card{'' if (len(ids) == 1) else 's'}.")
    
    return f_deck_id

def on_reload_all() -> None:
    decklist = [mw.col.decks.id_for_name(deck.name[13:]) for deck in mw.col.decks.all_names_and_ids() if deck.name[:13] == 'Study Ahead::']
    count = len([id for id in [create_filtered_deck(id, tt=False) for id in decklist] if id != None])
    tooltip(f"Reloaded {count} deck{'' if count == 1 else 's'} for study ahead.")

def on_study_ahead_all() -> None:
    decklist = [deck.id for deck in mw.col.decks.all_names_and_ids() if '::' not in deck.name and not mw.col.decks.is_filtered(deck.id) and deck.name != 'Study Ahead']
    count = len([id for id in [create_filtered_deck(id, tt=False) for id in decklist] if id != None])
    tooltip(f"Created {count} deck{'' if count == 1 else 's'} for study ahead.")

study_ahead_all = QAction(f"Study Ahead All Decks", mw)
qconnect(study_ahead_all.triggered, on_study_ahead_all)
mw.form.menuTools.addAction(study_ahead_all)

def on_show_options(menu, deck_id) -> None:
    if (deck := mw.col.decks.get(deck_id))['name'][:11] != 'Study Ahead' and not mw.col.decks.is_filtered(deck_id):
        action = menu.addAction("Study Ahead")
        action.triggered.connect(lambda _, did=deck_id: create_filtered_deck(did))
    elif deck['name'] ==  'Study Ahead':
        action = menu.addAction("Reload All")
        action.triggered.connect(on_reload_all)
    elif deck['name'][:13] ==  'Study Ahead::':
        home_deck_id = mw.col.decks.id_for_name(deck['name'][13:])
        action = menu.addAction("Reload")
        action.triggered.connect(lambda _, did=home_deck_id: create_filtered_deck(did))

gui_hooks.deck_browser_will_show_options_menu.append(on_show_options)

if __name__ == "__main__":
    print("This is an add-on for Anki. It is not intended to be run outside of Anki.")