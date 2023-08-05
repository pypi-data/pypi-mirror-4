# -*- coding:utf-8 -*-
__all__=('max_upload_size', 'content_type_check', 'virus_check')

import logging

from django.conf import settings
from django.core.exceptions import ValidationError
from django.template.defaultfilters import filesizeformat
from django.utils.translation import ugettext
from django.utils.translation import ugettext_lazy as _

log = logging.Logger(__name__)

try:
    import pyclamd
    scan_file = lambda x:[0]

    try:
        clam_socket = pyclamd.ClamdUnixSocket()
        clam_socket.ping()
        scan_file = clam_socket.scan_file
    except pyclamd.ConnectionError:
        pass
except ImportError:
    log.warn(ugettext('Please, install clamav and pyclamd if you want virus checking for user uploaded files.'))

try:
    import magic
    m = magic.open(magic.MAGIC_MIME);m.load()
    guess_type = m.file
except ImportError:
    import mimetypes
    guess_type = lambda x:mimetypes.guess_type(x)[0]
    log.warn(ugettext('Please, install python-magic package for better mimetype discovery support.'))

def max_upload_size(max_size):
    """
    Validator that ensures the maximum size of a file.
    """
    def _max_upload_size(file, max_size):
        if file.size>max_size:
            error_msg = 'Please keep filesize under %(max_filesize)s. Current filesize %(cur_filesize)s.'
            raise ValidationError(ugettext(error_msg) % {
                'max_filesize':filesizeformat(max_size),
                'cur_filesize':filesizeformat(file.size)
            })
    return lambda value: _max_upload_size(value, max_size)

def virus_check(file):
    '''
    Validator that checks if a uploaded file is infected. It uses pyclamav to do so.
    It requires that uploadhandler MemoryFileUploadHandler is not installed.
    '''
    if hasattr(file, 'temporary_file_path'):
        scan_result = scan_file(file.temporary_file_path)

        # TODO: logging needed
        if scan_result is not None:
            log.info('Attachment %s is unsafe.' % file.name)
            raise ValidationError(ugettext('File is considered unsafe. Upload aborted.'))
        else:
            log.info('Attachment %s is safe.' % file.name)
    else: log.warn(ugettext('Please, make sure clamav and pyclamd are installed. Virus check not performed.'))

def content_type_check(content_types):
    """
    Makes sure a the uploaded file is of a certain type. If python-magic is installed,
    mimetype guessing is done using it. Otherwise, mimetypes module is used.
    It requires that uploadhandler MemoryFileUploadHandler is not installed.
    """
    def _content_type_check(file, content_types):
        if hasattr(file, 'temporary_file_path'):
            content_type = guess_type(file.temporary_file_path)
            if content_type not in content_types:
                raise ValidationError(_('Filetype not supported.'))
        else: log.warn(ugettext('Please, make sure clamav and pyclamav are installed. Virus check not performed.'))
    return lambda value: _content_type_check(value, content_types)
