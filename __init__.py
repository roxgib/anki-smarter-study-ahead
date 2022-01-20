"""
Todo:
    - better handling of child decks
    - gui options
"""

from aqt import mw
from aqt.utils import qconnect, QAction, tooltip
from aqt import gui_hooks

def underdue_ratio(card_id, mw=mw):
    card = mw.col.get_card(card_id)
    timeToday = mw.col.decks.get(card.did)['timeToday'][0]
    return card.ivl / (card.due - timeToday)

def sort_cards():
    ids = mw.col.find_cards('deck:"Study Ahead" deck:filtered')
    ids = sorted(ids, key=lambda card_id: underdue_ratio(card_id, mw))
    cards = [mw.col.get_card(id) for id in ids]
    
    for i, card in enumerate(cards):

        card.due = int((-10000)+i)

    mw.col.update_cards(cards)

def create_filtered_deck(card_ids, deck_name):
    filter_string = '(' + ' OR '.join([f'cid:{id}' for id in card_ids]) + ') -is:due -is:learn -is:suspended -is:buried -rated:1'

    f_deck_id = mw.col.decks.new_filtered(deck_name)
    f_deck = mw.col.decks.current()

    f_deck['resched'] = True
    f_deck['delays'] = None
    f_deck['terms'] = [[filter_string, 10000, 6]]
    
    mw.col.decks.save(f_deck)
    mw.col.sched.rebuild_filtered_deck(f_deck_id)

    return f_deck_id

def study_ahead(deck_ids: list) -> int:
    config = mw.addonManager.getConfig(__name__)
    max_days_ahead = config['max_days_ahead']
    max_cards = config['max_cards']
    min_multiple = config['min_multiple']

    if len(deck_ids) == 1: # Enable tooltip on deck creation
        tt=True 
    else: # Limit total cards accross all decks
        tt = False
        deck_names = [mw.col.decks.get(deck_id)['name'] for deck_id in deck_ids]
        deck_string = ' OR '.join([f'deck:"{deck_name}"' for deck_name in deck_names])
        t_ids = mw.col.find_cards(f'({deck_string}) prop:due<={max_days_ahead} -is:due -is:learn -is:suspended -is:buried')
        t_ids = [id for id in sorted(t_ids, key = lambda card_id: underdue_ratio(card_id, mw), reverse=True) if (underdue_ratio(id) > min_multiple)]
        t_ids = t_ids[:max_cards]

        if (total_cards := len(t_ids)) == 0:
            tooltip(f"Couldn't find any suitable cards to study ahead.")
            return

        if underdue_ratio(t_ids[-1]) > min_multiple:
            min_multiple = underdue_ratio(t_ids[-1])

    deck_count = 0

    undo_entry = mw.col.add_custom_undo_entry(f'Create Study Ahead Deck')    

    for deck_id in deck_ids:
        deck_name = mw.col.decks.get(deck_id)['name']
        
        if (old_f_deck := mw.col.decks.id_for_name('Study Ahead::' + deck_name)) != None:
            mw.col.decks.remove([old_f_deck])

        ids = mw.col.find_cards(f'deck:"{deck_name}" prop:due<={max_days_ahead} -is:due -is:learn -is:suspended -is:buried')
        ids = [id for id in sorted(ids, key = lambda card_id: underdue_ratio(card_id, mw)) if (underdue_ratio(id) >= min_multiple)]
        ids = ids[:max_cards]

        if tt: total_cards = len(ids)

        if len(ids) == 0: 
            if tt: tooltip(f"Couldn't find any suitable cards to study ahead."); return
            continue

        create_filtered_deck(ids, 'Study Ahead::' + deck_name)

        deck_count += 1

    if tt: tooltip(f"Created filtered deck 'Study Ahead::{deck_name}' with {len(ids)} card{'' if (len(ids) == 1) else 's'}.")

    sort_cards()

    mw.col.merge_undo_entries(undo_entry)

    mw.reset()

    return total_cards

def on_reload_all() -> None:
    undo_entry = mw.col.add_custom_undo_entry(f'Reload All Study Ahead Decks')
    decklist = [mw.col.decks.id_for_name(deck.name[13:]) for deck in mw.col.decks.all_names_and_ids() if deck.name[:13] == 'Study Ahead::']
    decklist = [id for id in decklist if id != None]
    mw.col.decks.remove([mw.col.decks.id_for_name('Study Ahead')])
    count = study_ahead(decklist)
    if count == None: return
    tooltip(f"Reloaded decks for study ahead with a total of {count} card{'' if count == 1 else 's'}.")
    mw.col.merge_undo_entries(undo_entry)

def on_study_ahead_all() -> None:
    undo_entry = mw.col.add_custom_undo_entry(f'Study Ahead All Decks')
    try:
        mw.col.decks.remove([mw.col.decks.id_for_name('Study Ahead')])
    except:
        pass
    deck_list = [deck.id for deck in mw.col.decks.all_names_and_ids() if '::' not in deck.name and not mw.col.decks.is_filtered(deck.id) and deck.name != 'Study Ahead']
    count = study_ahead([deck for deck in deck_list if deck != None])
    if count == None: return
    tooltip(f"Created {count} deck{'' if count == 1 else 's'} for study ahead.")
    mw.col.merge_undo_entries(undo_entry)

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

if __name__ == "__main__":
    print("This is an add-on for Anki. It is not intended to be run outside of Anki.")