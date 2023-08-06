from pyramid.config import Configurator
from pyramid.authentication import AuthTktAuthenticationPolicy
from pyramid.authorization import ACLAuthorizationPolicy

from sqlalchemy import engine_from_config
from pyramid_beaker import session_factory_from_settings


import ringo.lib.helpers as helpers 
from ringo.lib.security import get_user
from ringo.model import (
    DBSession,
    Base,
    )

def add_renderer_globals(event):
    request = event['request']
    event['_'] = request.translate
    event['localizer'] = request.localizer
    event['h'] = helpers 

def setup_ringo(config):
    config.include(setup_ringo_handlers)
    config.include(setup_ringo_views)
    config.include(setup_ringo_assets)
    config.include(setup_ringo_routes)
    config.include(setup_ringo_security)
    config.include(setup_ringo_subscribers)

def setup_ringo_handlers(config):
    config.add_handler('auth', '/auth/{action}', handler="ringo.views.handlers.auth.AuthHandler")
    config.add_handler('item', '/item/{action}', handler="ringo.views.handlers.item.ItemHandler")

def setup_ringo_views(config):
    pass

def setup_ringo_assets(config):
    config.add_static_view('static', path='ringo:static', cache_max_age=3600)

def setup_ringo_routes(config):
    config.add_route('home', '/')
    config.add_route('about', '/about')
    config.add_route('contact', '/contact')
    config.add_route('login', '/auth/login')
    config.add_route('logout', '/auth/logout')

def setup_ringo_security(config):
    authn_policy = AuthTktAuthenticationPolicy('seekrit', hashalg='sha512')
    authz_policy = ACLAuthorizationPolicy()
    config.set_authentication_policy(authn_policy)
    config.set_authorization_policy(authz_policy)
    # Make the user object available as attribute "user" in the request. 
    # See http://docs.pylonsproject.org/projects/pyramid_cookbook/en/latest/auth/user_object.html
    config.set_request_property(get_user, 'user', reify=True)

def setup_ringo_subscribers(config):
    config.add_subscriber(add_renderer_globals,
                          'pyramid.events.BeforeRender')
    # I18n support. See
    # http://docs.pylonsproject.org/projects/pyramid_cookbook/en/latest/templates/mako_i18n.html
    config.add_subscriber('ringo.lib.i18n.add_localizer',
                          'pyramid.events.NewRequest')

def main(global_config, **settings):
    """ This function returns a Pyramid WSGI application.
    """
    engine = engine_from_config(settings, 'sqlalchemy.')
    DBSession.configure(bind=engine)
    Base.metadata.bind = engine
    config = Configurator(settings=settings)
    config.include('pyramid_handlers')
    config.include('pyramid_beaker')
    session_factory = session_factory_from_settings(settings)
    config.set_session_factory(session_factory)
    config.include(setup_ringo)
    config.scan()
    return config.make_wsgi_app()
