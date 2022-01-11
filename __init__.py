"""
Todo:
    - delete old filtered deck
    - run for all decks
    - 

"""


from aqt import mw
from aqt.utils import qconnect, tooltip
from aqt.qt import qconnect

import aqt.gui_hooks

conf = mw.addonManager.getConfig(__name__)
max_days_ahead = conf['max_days_ahead']
max_cards = conf['max_cards']
max_multiple = conf['max_multiple']

def create_filtered_deck(deck_id) -> int:
    odeck = mw.col.decks.get(deck_id)
    deck_name = odeck['name']

    ids = mw.col.find_cards(f'deck:{deck_name} prop:due<={max_days_ahead} -is:due -is:learning -is:suspended -is:buried')

    id_dues = list()

    for card_id in ids:
        card = mw.col.getCard(card_id)
        if card.ivl / card.due > max_multiple:
            id_dues.append((card_id, card.ivl / card.due))

    ids = [k[0] for k in sorted(id_dues, key = lambda x: x[1])][:max_cards]

    filter_string = ' OR '.join([f'cid:{id}' for id in ids]) + ' -is:due -is:learning -is:suspended -is:buried -rated:1'

    f_deck_id = mw.col.decks.new_filtered('Study Ahead::' + deck_name)
    deck = mw.col.decks.current()

    deck['resched'] = True
    deck['delays'] = None
    deck['terms'] = [[filter_string, 10000, 6]]
    
    mw.col.decks.save(deck)
    mw.col.sched.rebuild_filtered_deck(f_deck_id)

    tooltip(f'Created filtered deck "Study Ahead::{deck_name}" with {len(ids)} cards.')
    
    return f_deck_id

def on_study_ahead(menu, deck_id) -> None:
    action = menu.addAction("Study Ahead")
    action.triggered.connect(lambda _, did=deck_id: create_filtered_deck(did))

aqt.gui_hooks.deck_browser_will_show_options_menu.append(on_study_ahead)