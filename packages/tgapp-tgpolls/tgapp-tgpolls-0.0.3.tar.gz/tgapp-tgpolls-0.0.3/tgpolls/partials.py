from tg import expose
from tgpolls import model
from datetime import datetime

@expose('tgpolls.templates.poll_partial')
def poll_partial(poll):
    return dict(poll=poll)

@expose('tgpolls.templates.active_partial')
def active_polls():
    active_polls = model.DBSession.query(model.Poll).filter(model.Poll.expiry > datetime.now()).all()
    return dict(active_polls=active_polls)
