import sqlalchemy as sa
from ringo.model import Base
from ringo.lib.i18n import _ 
from ringo.model.base import BaseItem

class Module(BaseItem, Base):
    """ The SQLAlchemy declarative model class for a Model object. """
    __tablename__ = 'modules'
    id = sa.Column(sa.types.Integer, primary_key=True, autoincrement=True)
    name = sa.Column(sa.types.VARCHAR(256), nullable=False)
    name_plural = sa.Column(sa.types.VARCHAR(256))
    render_str = sa.Column(sa.types.VARCHAR(256))
    parent = sa.Column(sa.types.VARCHAR(256))
    controller = sa.Column(sa.types.VARCHAR(256))
    show = sa.Column(sa.types.BOOLEAN, default=True)
    enabled = sa.Column(sa.types.BOOLEAN, default=True)

def init_model(session):
    # User Modul
    user_modul = Module()
    user_modul.name = _('User') 
    user_modul.name_plural = _('Users') 
    user_modul.controller = 'users_admin' 
    session.add(user_modul)
    # Usergroup Modul
    usergroup_modul = Module()
    usergroup_modul.name = _('Usergroup') 
    usergroup_modul.name_plural = _('Usergroups') 
    usergroup_modul.controller = 'usergroups_admin' 
    session.add(usergroup_modul)
    # Role Modul
    role_modul = Module()
    role_modul.name = _('Role') 
    role_modul.name_plural = _('Roles') 
    role_modul.controller = 'roles_admin' 
    # Item Modul
    role_modul = Module()
    role_modul.name = _('Item') 
    role_modul.name_plural = _('Items') 
    role_modul.controller = 'item' 
    session.add(role_modul)
