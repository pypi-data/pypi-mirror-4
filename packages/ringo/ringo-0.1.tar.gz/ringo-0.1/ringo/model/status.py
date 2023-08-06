# -*- coding: utf-8 -*-
import sqlalchemy as sa
from ringo.lib.i18n import _ 
from ringo.model import Base

class Status(Base):
    """ The SQLAlchemy declarative model class for a meta object. """
    __tablename__ = 'status'
    id = sa.Column(sa.types.Integer, primary_key=True, autoincrement=True)
    name = sa.Column(sa.types.VARCHAR(256))

def init_model(session):
    status_item = Status()
    status_item.name = _('Trash')
    session.add(status_item)
