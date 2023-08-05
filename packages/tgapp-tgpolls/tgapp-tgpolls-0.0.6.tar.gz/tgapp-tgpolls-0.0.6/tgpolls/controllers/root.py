# -*- coding: utf-8 -*-
"""Main Controller"""

from tg import TGController, require, predicates
from tg import expose, flash, validate, session
from tg.i18n import ugettext as _
from tgext.datahelpers.utils import fail_with
from tgext.datahelpers.validators import validated_handler, SQLAEntityConverter
from tgext.pluggable import plug_redirect, call_partial

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
    @validate(dict(poll_uid=SQLAEntityConverter(Poll)),error_handler=fail_with(404))
    def vote(self, poll_uid, **kw):
        if 'poll_%s' % poll_uid.uid in session:
            return 'KO'

        for answer in poll_uid.answers:
            if str(answer.uid) in kw.get('votes[]', []):
                answer.votes += 1
                session['poll_%s' % poll_uid.uid] = '1'
                    
        session.save()
        return 'OK'

    @expose('tgpolls.templates.active')
    def active(self):
        active_polls = DBSession.query(Poll).filter(Poll.expiry > datetime.datetime.now()).all()
        return dict(active_polls=active_polls)

    @expose(content_type='text/html')
    def activebox(self):
        return call_partial('tgpolls.partials:active_polls')

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

    @require(predicates.in_group('managers'))
    @expose()
    def delete(self, poll_uid):
        poll = model.DBSession.query(Poll).filter_by(uid=poll_uid).first()
        if poll:
            model.DBSession.delete(poll)
            model.DBSession.flush()
            flash(_('Poll successfully deleted'))
        else:
            flash(_('Poll not found'))
        return plug_redirect('tgpolls', '/')
