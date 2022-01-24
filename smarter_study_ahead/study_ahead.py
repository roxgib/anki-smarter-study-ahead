"""
Todo:
    - better handling of child decks
    - gui options
    - tests
"""

from aqt import mw
from aqt.utils import tooltip, showInfo



def underdue_ratio(card_id: int, mw=mw) -> float:
    card = mw.col.get_card(card_id)
    timeToday = mw.col.sched.today
    if card.due >= 0:
        due = card.due
    else:
        due = card.odue
    if due <= timeToday: return 0
    return (card.ivl / (due - timeToday))

def sort_cards():
    ids = mw.col.find_cards('deck:"Study Ahead" deck:filtered')
    ids = sorted(ids, key=lambda card_id: underdue_ratio(card_id, mw))
    cards = [mw.col.get_card(id) for id in ids]

    for i, card in enumerate(cards):
        card.due = int((-10000)+i)

    mw.col.update_cards(cards)

def create_filtered_deck(card_ids: list, deck_name: str) -> int:
    filter_string = '(' + ' OR '.join([f'cid:{id}' for id in card_ids]) + ') -is:due -is:learn -is:suspended -is:buried -rated:1'

    f_deck_id = mw.col.decks.new_filtered(deck_name)
    f_deck = mw.col.decks.current()

    f_deck['resched'] = True
    f_deck['delays'] = None
    f_deck['terms'] = [[filter_string, 10000, 6]]

    mw.col.decks.save(f_deck)
    mw.col.sched.rebuild_filtered_deck(f_deck_id)

    return f_deck_id

def find_eligible_cards(deck_ids: list[int], min_multiple: float = None) -> list[int]:
    config = mw.addonManager.getConfig(__name__)
    max_days_ahead = config['max_days_ahead']
    max_cards = config['max_cards']
    if min_multiple == None:
        min_multiple = config['min_multiple']

    deck_names = [mw.col.decks.get(deck_id)['name'] for deck_id in deck_ids]
    deck_string = ' OR '.join([f'deck:"{deck_name}"' for deck_name in deck_names])

    ids = mw.col.find_cards(f'({deck_string}) prop:due<={max_days_ahead} -is:due -is:learn -is:suspended -is:buried')
    ids = [id for id in sorted(ids, key = lambda card_id: underdue_ratio(card_id, mw), reverse=True) if (underdue_ratio(id) > min_multiple)]
    ids = [id for id in ids if mw.col.get_card(id).queue == 2][:max_cards]

    return ids

def study_ahead(deck_ids: list[int]) -> int:
    if len(deck_ids) == 1: # Enable tooltip on deck creation
        tt=True 
        min_multiple = None
    else: # Limit total cards accross all decks
        tt = False
        t_ids = find_eligible_cards(deck_ids)

        if (total_cards := len(t_ids)) == 0:
            showInfo(f"Couldn't find any suitable cards to study ahead.")
            return

        min_multiple = underdue_ratio(t_ids[-1])

    undo_entry = mw.col.add_custom_undo_entry(f'Create Study Ahead Deck')
    deck_count = 0

    for deck_id in deck_ids:
        _undo_entry = mw.col.add_custom_undo_entry(f'Create Study Ahead Deck')    
        
        deck_name = mw.col.decks.get(deck_id)['name']
        
        if (old_f_deck := mw.col.decks.id_for_name('Study Ahead::' + deck_name)) != None:
            mw.col.decks.remove([old_f_deck])

        ids = find_eligible_cards([deck_id], min_multiple)

        if tt: total_cards = len(ids)

        if len(ids) == 0: 
            if tt: 
                showInfo(f"Couldn't find any suitable cards to study ahead."); return
            else:
                continue

        create_filtered_deck(ids, 'Study Ahead::' + deck_name)

        deck_count += 1

        mw.col.merge_undo_entries(_undo_entry)

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

