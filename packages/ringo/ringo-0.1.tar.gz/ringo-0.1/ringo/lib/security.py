## -*- coding: utf-8 -*-
import logging
from pyramid.security import unauthenticated_userid
from sqlalchemy.orm.exc import NoResultFound

from ringo.model import DBSession
from ringo.model.user import User

log = logging.getLogger(__name__)

def get_user(request):
    userid = unauthenticated_userid(request)
    if userid is not None:
        session = DBSession 
        try:
            user = session.query(User).filter_by(id=userid).one()
            return user
        except NoResultFound:
            pass
    return None

def get_groups(userid, request):
    user = request.user
    if user is not None:
        return [ group.name for group in request.user.groups ]
    return None

def login(username, password):
    session = DBSession()
    try:
        user = session.query(User).filter_by(login=username, password=password).one()
        return user
    except NoResultFound:
        return None
