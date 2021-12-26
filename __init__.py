from aqt import mw
from aqt.utils import qconnect, tooltip
from aqt.qt import qconnect, QAction
from aqt import gui_hooks

def filter_string(user_string, num_days, max_multiple=10):
    filter_string = user_string + ' ('
    filter_string.append(" OR ".join([f"(prop:due<={i} prop:ivl>={i*max_multiple})" for i in range(1, num_days+1)]))
    filter_string.append(') -is:learn')
    return filter_string

def create_filter():
    mw.col.sched.get_or_create_filtered_deck()

menuItem = QAction(f"Study Ahead", mw)
qconnect(menuItem.triggered, StudyAheadUI)
mw.form.menuTools.addAction(menuItem)