from sqlalchemy import Table, ForeignKey, Column
from sqlalchemy.types import Unicode, Integer, DateTime
from sqlalchemy.orm import backref, relation

from tgpolls.model import DeclarativeBase
from tgext.pluggable import app_model, primary_key

class Poll(DeclarativeBase):
    __tablename__ = 'tgpolls_polls'

    uid = Column(Integer, autoincrement=True, primary_key=True)
    body = Column(Unicode(2048))
    expiry = Column(DateTime)

class PollAnswer(DeclarativeBase):
    __tablename__ = 'tgpolls_poll_answers'

    uid = Column(Integer, autoincrement=True, primary_key=True)
    text = Column(Unicode(255))
    votes = Column(Integer, default=0)

    poll_id = Column(Integer, ForeignKey(primary_key(Poll)), nullable=True, index=True)
    poll = relation(Poll, backref=backref('answers'), lazy='joined')

