# -*- coding: utf-8 -*-:
# Copyright (C) 2011,2012  Torsten Irländer <torsten@irlaender.de>
#
# This file is part of ringo. 

import logging
import hashlib
import magic
import StringIO
import xml.parsers.expat
import re
from datetime import timedelta
from xml.etree.ElementTree import XML

from formencode import Schema
from formencode.validators import FancyValidator, Invalid, FieldsMatch, String, Int, FormValidator
from formencode.compound import All
from ringo.lib.helpers import mimes

log = logging.getLogger(__name__)

class BaseFormValidator(Schema):
    allow_extra_fields = True
    filter_extra_fields = True

class FileName(FormValidator):
    """Validator which will set the filename to the name of the uploaded file
    if no optional filename is given."""
    def __init__(self, x, y, *args, **kw):
        """x ist name of the optional filename, y is the payload field"""
        super(FileName, self).__init__(*args,**kw)
        self.fieldname = x
        self.datafield = y

    def validate_python(self, field_dict, state):
        if not field_dict.get(self.fieldname):
            field_dict[self.fieldname] = ".".join(field_dict[self.datafield].filename.split('.')[0:-1])
        return field_dict

class FileValidator(FancyValidator):
    def _to_python(self, value, state):
        allowed_mimes = []
        for ft in self.allowed_filetypes:
            allowed_mimes.extend(mimes.get(ft, []))

        payload = value.file.read(self.max)
        mime = magic.from_buffer(payload, mime=True)
        # rewind so that the application can access the content
        value.file.seek(0)
        if mime not in allowed_mimes:
            log.error('Mimetype check failed for "%s" -> not found in allowed mimetypes' % mime)
            raise Invalid(u"Only the following types of files are allowed: %s " % ", ".join(self.allowed_filetypes), value, state)
        if len(payload) == self.max:
            log.error('Len check failed with len "%s"' % len(payload))
            raise Invalid(u"The file is too big (> %s Bytes)" % self.max, value, state)

        return value

class XMLImportFileValidator(FancyValidator):
    def _to_python(self, value, state):
        allowed_mimes = mimes.get('xml', [])
        payload = value.file.read(self.max)
        mime = magic.from_buffer(payload, mime=True)
        # rewind so that the application can access the content
        value.file.seek(0)
        if mime not in allowed_mimes:
            log.error('Mimetype check failed for "%s" -> not found in allowed mimetypes' % mime)
            raise Invalid(u"Only the following types of files are allowed: %s " % ", ".join(self.allowed_filetypes), value, state)
        if len(payload) == self.max:
            log.error('Len check failed with len "%s"' % len(payload))
            raise Invalid(u"The file is too big (> %s Bytes)" % self.max, value, state)
        # Check if the data is well formed, and build xmldom
        try:
            parser = xml.parsers.expat.ParserCreate()
            parser.ParseFile(StringIO.StringIO(payload))
            xmldom = XML(payload)
        except Exception, e:
            raise Invalid(u"The file is not well formed: %s" % e, value, state)
        return xmldom

class Md5(FancyValidator):
    def _to_python(self, value, state):
        m = hashlib.md5()
        m.update(value)
        return m.hexdigest()

class Sha1(FancyValidator):
    def _to_python(self, value, state):
        m = hashlib.sha1()
        m.update(value)
        return m.hexdigest()

class SearchExpression(FancyValidator):
    def _to_python(self, value, state):
        try:
            re.compile(value)
            return value
        except Exception, e:
            raise Invalid(u"Building regular expression for search failed: %s" % e.message, value, state)

class TimeValidator(FancyValidator):
    """Converts a given string representation of a timedelta (HH:MM:SS) to an
    int value of the total amount of seconds"""
    def _to_python(self, value, state):
        try:
            # Check if this is a timedelta string
            m = re.compile("^[0-9]+:[0-5]\d:[0-5]\d$")
            if m.match(value):
                h,m,s = value.split(':')
                td = timedelta(seconds=int(s), minutes=int(m), hours=int(h))
                return int(td.total_seconds())
            raise Exception(value)
        except Exception, e:
            raise Invalid(u"The time is not well formed (HH:MM:SS): %s" % e, value, state)

class LoginFormValidator(BaseFormValidator):
    username = String(not_empty=True)
    password = String(not_empty=True)

class SearchFormValidator(BaseFormValidator):
    search = SearchExpression()
    search_field = String()

class EditUserFormValidator(BaseFormValidator):
    password = All(validators=[Sha1(not_empyt=True), String(min=8)])
    retype_password = Sha1()
    chained_validators = [FieldsMatch('password', 'retype_password')]

class ImportXMLFormValidator(BaseFormValidator):
    importdata = XMLImportFileValidator(max=10000)


