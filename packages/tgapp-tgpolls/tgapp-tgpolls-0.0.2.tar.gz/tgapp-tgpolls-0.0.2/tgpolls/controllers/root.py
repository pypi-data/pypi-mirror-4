# -*- coding: utf-8 -*-
"""Main Controller"""

from tg import TGController, require, predicates
from tg import expose, flash, validate, session
from tg.i18n import ugettext as _
from tgext.datahelpers.validators import validated_handler
from tgext.pluggable import plug_redirect


from tgpolls import model
from tgpolls.lib.forms import new_poll_form
from tgpolls.model import DBSession, Poll
import datetime

class RootController(TGController):
    @expose('tgpolls.templates.index')
    def index(self):
        polls = DBSession.query(Poll).order_by(Poll.uid.desc()).filter(Poll.expiry > datetime.datetime.now()).all()
        expired_polls = DBSession.query(Poll).filter(Poll.expiry < datetime.datetime.now()).all()
        return dict(polls=polls, expired_polls=expired_polls)

    @require(predicates.in_group('managers'))
    @expose('tgpolls.templates.poll.new')
    def new(self, **kw):
        return dict(form=new_poll_form)

    @expose()
    def vote(self, **kw):
        poll = DBSession.query(Poll).get(kw['poll_uid'])

        if 'poll_%s' % poll.uid in session:
            return 'KO'

        for answer in poll.answers:
            if str(answer.uid) in kw['votes[]']:
                answer.votes += 1;
                session['poll_%s' % poll.uid] = '1'

        session.save()
        return 'OK'

    @expose('tgpolls.templates.active')
    def active(self):
        active_polls = DBSession.query(Poll).filter(Poll.expiry > datetime.datetime.now()).all()
        return dict(active_polls=active_polls)

    @expose()
    @validate(new_poll_form,
              error_handler=validated_handler(new))
    @require(predicates.in_group('managers'))
    def save(self, **kw):
        new_poll = model.Poll(body=kw['body'], expiry=kw['expire'])
        model.DBSession.add(new_poll)
        model.DBSession.flush()

        for answer in kw['answers'].split('|'):
            new_answer = model.PollAnswer(text=answer, poll_id=new_poll.uid)
            model.DBSession.add(new_answer)

        model.DBSession.flush()

        flash(_('Poll successfully added'))
        return plug_redirect('tgpolls', '/')

