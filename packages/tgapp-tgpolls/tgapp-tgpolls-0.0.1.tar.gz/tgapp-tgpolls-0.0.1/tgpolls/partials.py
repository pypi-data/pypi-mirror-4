from tg import expose

@expose('tgpolls.templates.poll_partial')
def poll_partial(poll):
    return dict(poll=poll)