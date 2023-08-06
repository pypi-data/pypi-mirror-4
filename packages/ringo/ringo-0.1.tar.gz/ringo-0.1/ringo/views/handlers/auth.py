import logging
import hashlib

from pyramid.security import remember, forget, unauthenticated_userid
from pyramid.httpexceptions import HTTPFound
from pyramid_simpleform import Form
from pyramid_simpleform.renderers import FormRenderer
from pyramid_handlers import action

from ringo.lib.validators import LoginFormValidator 
from ringo.lib.security import login 
from ringo.handlers.base import BaseHandler

log = logging.getLogger(__name__)

class AuthHandler(BaseHandler):

    @action(renderer="/auth/login.mako")
    def login(self):
        target_page = self.request.params.get('next') or self.request.route_url('home')
        form = Form(self.request, schema=LoginFormValidator)
        if form.validate():
            username = form.data.get('username')
            password = form.data.get('password')
            m = hashlib.sha1()
            m.update(password)
            user = login(username, m.hexdigest())
            if user:
                self.request.session.flash('alert-success;Login succeeded :)')
                log.info('Login successfull for user %s' % username)
                headers = remember(self.request, user.id, max_age='86400')
                return HTTPFound(location=target_page, headers=headers)
            else:
                self.request.session.flash('alert-error;Login failed! Username or password was wrong.')
        else:
            self.request.session.flash('alert-info;Please enter your username and password to login.')
        return dict(form=FormRenderer(form))

    def logout(self):
        target_page = self.request.route_url('home')
        headers = forget(self.request)
        return HTTPFound(location=target_page, headers=headers)

