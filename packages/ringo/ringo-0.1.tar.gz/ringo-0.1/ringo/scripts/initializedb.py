import os
import sys
import transaction

from sqlalchemy import engine_from_config

from pyramid.paster import (
    get_appsettings,
    setup_logging,
    )

from ringo.model import DBSession, Base
from ringo.model.module import init_model as init_modules_model
from ringo.model.user import init_model as init_user_model
from ringo.model.status import init_model as init_status_model
from ringo.model.meta import init_model as init_meta_model
from ringo.model.item import init_model as init_item_model

def usage(argv):
    cmd = os.path.basename(argv[0])
    print('usage: %s <config_uri>\n'
          '(example: "%s development.ini")' % (cmd, cmd))
    sys.exit(1)

def main(argv=sys.argv):
    if len(argv) != 2:
        usage(argv)
    config_uri = argv[1]
    setup_logging(config_uri)
    settings = get_appsettings(config_uri)
    engine = engine_from_config(settings, 'sqlalchemy.')
    DBSession.configure(bind=engine)
    Base.metadata.create_all(engine)
    with transaction.manager:
        # Initialise the ringo model
        init_status_model(DBSession)
        init_meta_model(DBSession)
        init_user_model(DBSession)
        init_modules_model(DBSession)
        init_item_model(DBSession)
