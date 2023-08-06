# -*- coding: utf-8 -*-
import sqlalchemy as sa
from ringo.lib.i18n import _ 
from ringo.model import Base

class Meta(Base):
    """ The SQLAlchemy declarative model class for a meta object. """
    __tablename__ = 'meta'
    id = sa.Column(sa.types.Integer, primary_key=True, autoincrement=True)
    uid = sa.Column(sa.Integer, sa.ForeignKey('users.id'))
    gid = sa.Column(sa.Integer, sa.ForeignKey('usergroups.id'))
    mid = sa.Column(sa.Integer, sa.ForeignKey('modules.id'))
    sid = sa.Column(sa.Integer, sa.ForeignKey('status.id'))

def init_model(session):
    pass
