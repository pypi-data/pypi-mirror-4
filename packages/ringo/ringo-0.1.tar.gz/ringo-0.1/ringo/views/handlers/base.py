## -*- coding: utf-8 -*-
from pyramid.response import Response
from pyramid_handlers import action

class BaseHandler(object):

    def __init__(self, request):
        self.request = request

    def index(self):
        return self.overvierw()

    @action(renderer='/default/create.mako')
    def create(self):
        return {}

    @action(renderer='/default/list.mako')
    def overview(self):
        return {}

    @action(renderer='/default/read.mako')
    def read(self):
        return {}

    @action(renderer='/default/edit.mako')
    def edit(self):
        return {}

    # Dialogs
    def delete(self):
        return Response('Delete!')

    def erase(self):
        return Response('Erase!')

    def restore(self):
        return Response('Restore!')
