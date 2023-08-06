# -*- coding: utf-8 -*-
import hashlib
import sqlalchemy as sa
from ringo.lib.i18n import _ 
from ringo.model import Base
from ringo.model.base import BaseItem

ADMIN_ROLE = 'admin'
USER_ROLE = 'user'

# NM-Table definitions
nm_user_roles = sa.Table(
    'nm_user_roles', Base.metadata,
    sa.Column('uid', sa.Integer, sa.ForeignKey('users.id')),
    sa.Column('rid', sa.Integer, sa.ForeignKey('roles.id'))
    )

nm_usergroup_roles = sa.Table(
    'nm_usergroup_roles', Base.metadata,
    sa.Column('gid', sa.Integer, sa.ForeignKey('usergroups.id')),
    sa.Column('rid', sa.Integer, sa.ForeignKey('roles.id'))
    )

nm_user_usergroups = sa.Table(
    'nm_user_usergroups', Base.metadata,
    sa.Column('uid', sa.Integer, sa.ForeignKey('users.id')),
    sa.Column('gid', sa.Integer, sa.ForeignKey('usergroups.id'))
    )

class User(BaseItem, Base):
    """ The SQLAlchemy declarative model class for a user object. """
    __tablename__ = 'users'
    id = sa.Column(sa.types.Integer, primary_key=True, autoincrement=True)
    login = sa.Column(sa.types.VARCHAR(256), nullable=False)
    gid = sa.Column(sa.Integer, sa.ForeignKey('usergroups.id'))
    password = sa.Column(sa.types.VARCHAR(256), nullable=False)
    enabled = sa.Column(sa.types.BOOLEAN, default=True)
    roles = sa.orm.relationship("Role", secondary=nm_user_roles)

class UserGroup(BaseItem, Base):
    """ The SQLAlchemy declarative model class for a usergroup object. """
    __tablename__ = 'usergroups'
    id = sa.Column(sa.types.Integer, primary_key=True, autoincrement=True)
    name = sa.Column(sa.types.VARCHAR(256), nullable=False)
    roles = sa.orm.relationship("Role", secondary=nm_usergroup_roles)
    members = sa.orm.relationship("User", secondary=nm_user_usergroups)

class Role(BaseItem, Base):
    __tablename__ = 'roles'
    id = sa.Column(sa.types.Integer, primary_key=True, autoincrement=True)
    name = sa.Column(sa.types.VARCHAR(256), nullable=False)

def init_model(session):
    # Creating roles
    admin_role = Role()
    admin_role.name = ADMIN_ROLE
    session.add(admin_role)
    user_role = Role()
    user_role.name = USER_ROLE
    session.add(user_role)
    # Creating default admin user 
    admin_user = User()
    admin_user.login = 'admin' 
    m = hashlib.sha1()
    m.update('secret')
    admin_user.password = m.hexdigest()
    session.add(admin_user)
    # Creating groups
    admin_group = UserGroup()
    admin_group.name = _('Administration')
    admin_group.roles.append(admin_role)
    admin_group.members.append(admin_user)
    session.add(admin_group)
    user_group = UserGroup()
    user_group.name = _('Users')
    admin_group.roles.append(user_role)
    session.add(user_group)
