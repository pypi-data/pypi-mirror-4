## -*- coding: utf-8 -*-
import sqlalchemy as sa
from ringo.lib.i18n import _ 
from ringo.model import Base
from ringo.model.base import BaseItem
from ringo.model.meta import Meta 

class Item(BaseItem, Base):
    """ The SQLAlchemy declarative model class for a meta object. """
    MODUL_ID = 4
    __tablename__ = 'items'
    id = sa.Column(sa.types.Integer, primary_key=True, autoincrement=True)
    mid = sa.Column(sa.Integer, sa.ForeignKey('meta.id'))
    name = sa.Column(sa.types.VARCHAR(256))
    meta = sa.orm.relationship(Meta)

def init_model(session):
    item = Item()
    item.name = _('Test')
    session.add(item)
