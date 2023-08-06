## -*- coding: utf-8 -*-
import magic
import logging
import pkg_resources

log = logging.getLogger(__name__)

mimes = {'pdf': ['application/pdf', 'application/x-pdf', 'application/acrobat', 
         'applications/vnd.pdf', 'text/pdf', 'text/x-pdf'],
         'jpg': ['image/jpeg', 'image/jpg', 'image/jp_', 'application/jpg', 
         'application/x-jpg', 'image/pjpeg', 'image/pipeg', 
         'image/vnd.swiftview-jpeg', 'image/x-xbitmap'],
         'png': ['image/png', 'application/png', 'application/x-png'],
         'xml': ['txt/xml', 'application/xml'],
         'txt': ['text/plain'],
         'tiff': ['image/tiff']}

mimes_icons = {'pdf': '/images/icons/16x16/mimetypes/pdf.png',
               'jpg': '/images/icons/16x16/mimetypes/jpg.png',
               'png': '/images/icons/16x16/mimetypes/png.png',
               'xml': '/images/icons/16x16/mimetypes/text-generic.png',
               'txt': '/images/icons/16x16/mimetypes/text-generic.png',
               'tiff': '/images/icons/16x16/mimetypes/tiff.png'}

def get_mime_suffix(mime):
    '''Will return the suffix for the given mimetype. If the mimetype is
    unknown or can not be matched an an empty string as suffix is returned'''
    for key, value in mimes.iteritems():
        if mime in value: return key
    log.info('File suffix for mime %s not found -> return empty string' % mime)
    return ""

def get_mime_icon(mime):
    '''Will return the path to a small icon for the given mime. The icon
    depends on the mimetypes filesuffix. If the mimetype is unknown or can not
    be matched None is returned as icon path.'''
    suffix = get_mime_suffix(mime)
    return mimes_icons.get(suffix)

def get_mime_type(data, mime=True):
    '''Return the mimetype string for a given str buffer'''
    return magic.from_buffer(data, mime)

def get_package_version(pkg):
    """Returns the version number of the given package name"""
    return pkg_resources.get_distribution(pkg).version
