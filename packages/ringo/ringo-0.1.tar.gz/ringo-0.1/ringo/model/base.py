## -*- coding: utf-8 -*-
from ringo.model.meta import Meta 

class BaseItem(object):
    MODUL_ID = None

    def __init__(self):
        if self.MODUL_ID is not None:
            self.meta = Meta()
            self.meta.mid = self.MODUL_ID
