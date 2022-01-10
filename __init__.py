from aqt import mw
from aqt.utils import qconnect, tooltip
from aqt.qt import qconnect
from aqt.gui_hooks import deck_browser_will_show_options_menu

conf = mw.addonManager.getConfig(__name__)
num_days = conf['num_days']
num_cards = conf['num_cards']
max_multiple = conf['max_multiple']


def create_filtered_deck(deck_id) -> int:
    odeck = mw.col.decks.get(deck_id)
    deck_name = odeck['name']

    ids = mw.col.find_cards(f'deck:{deck_name} prop:due:')

    id_dues = list()

    for card_id in ids:
        card = mw.col.getCard(card_id)
        if card.ivl / card.due > max_multiple:
            id_dues.append((card_id, card.ivl / card.due))

    ids = [k[0] for k in sorted(id_dues, key = lambda x: x[1])]

    filter_string =  '"deck:' + str(deck_id) + '" ('
    filter_string += ' OR '.join([f"(prop:due<={i} prop:ivl>={i*max_multiple})" for i in range(1, num_days+1)])
    filter_string += ') -is:learn'

    f_deck_id = mw.col.decks.new_filtered('Study Ahead::' + deck_name)
    deck = mw.col.decks.current()

    deck['resched'] = True
    deck['delays'] = None
    deck['terms'] = [[filter_string, 10000, 6]]
    
    mw.col.decks.save(deck)
    mw.col.sched.rebuild_filtered_deck(f_deck_id)

    tooltip(f'Created filtered deck "Study Ahead::{deck_name}"')
    
    return f_deck_id

def on_study_ahead(menu, deck_id):
    action = menu.addAction("Study Ahead")
    action.triggered.connect(lambda _, did=deck_id: create_filtered_deck(did))

deck_browser_will_show_options_menu.append(on_study_ahead)