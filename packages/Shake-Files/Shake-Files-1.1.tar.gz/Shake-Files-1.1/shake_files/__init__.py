# -*- coding: utf-8 -*-
"""
# Shake-Files

Shake-Files allows your application to flexibly and efficiently handle file
uploads. 

You can create different sets of uploads - one for document attachments, one
for photos, etc. - and configure them to save tthe files in different places, 
creating the directories on demand, according to a pattern defined by you.


Copyright © 2010-2012 by Lúcuma labs (http://lucumalabs.com).  
MIT License. (http://www.opensource.org/licenses/mit-license.php)

"""
from __future__ import absolute_import
import errno
import os

try:
    from sqlalchemy.types import TypeDecorator, Text
    sqlalchemy_available = True
except ImportError:
    sqlalchemy_available = False

from werkzeug.exceptions import RequestEntityTooLarge, UnsupportedMediaType

from . import utils

__version__ = '1.1'


IMAGES = ('.jpg', '.jpeg', '.png', '.gif', '.bmp')

AUDIO = ('.wav', '.mp3', '.aac', '.ogg', '.oga', '.flac')

DOCUMENTS = ('.pdf', '.rtf', '.txt',
    '.odf', '.odp', '.ods', '.odg', '.ott', '.otp', '.ots', '.otg',
    '.pages', '.key', '.numbers', '.gnumeric', '.abw',
    '.doc', '.ppt', '.xls', '.vsd',
    '.docx', '.pptx', '.xlsx', '.vsx',
    )

DATA = ('.csv', '.json', '.xml', '.ini', '.plist', '.yaml', '.yml')

ARCHIVES = ('.zip', '.gz', '.bz2', '.tar', '.tgz', '.txz', '.7z')

DEFAULT = IMAGES + AUDIO + DOCUMENTS


class FileStorage(object):
    
    def __init__(self, base_path, base_url='/static/media/',
            upload_to='{yyyy}/{mm}/{dd}/', secret=False,
            prefix='', allowed=DEFAULT, denied=None, max_size=None):
        """
        Except for `base_path`, all of these parameters are optional,
        so only bother setting the ones relevant to your application.

        base_path
        :   Absolute path where the files will be stored. Example:
            `/var/www/example.com/media`.

            MEDIA_DIR = realpath(join(BASE_DIR, 'media'))

        base_url
        :   The base path used when building the file's URL. By default
            is `/static/media`.
            
            MEDIA_URL = '/media'

        upload_to
        :   A pattern used to build the upload path on the fly. 
            The wildcards avaliable are: 

                {yyyy},{yy}: Year
                {mm}, {m}: Month (0-padded or not)
                {ww}, {w}: Week number in the year (0-padded or not)
                {dd}, {d}: Day (0-padded or not)
                {hh}, {h}: Hours (0-padded or not)
                {nn}, {n}: Minutes (0-padded or not)
                {ss}, {s}: Seconds (0-padded or not)
                {a+}: Filename first letters
                {z+}: Filename last letters
                {r+}: Random letters and/or numbers
             
            Instead of a string, this can also be a callable.

        secret
        :   If True, instead of the original filename, a random one'll
             be used.

        prefix
        :   To avoid race-conditions between users uploading files with
            the same name at the same time. If `secret` is True, this
            will be ignored.

        allowed
        :   List of allowed file extensions. `None` to allow all
            of them. If the uploaded file doesn't have one of these
            extensions, an `UnsupportedMediaType` exception will be
            raised.
             
            Shake-Files come with some pre-defined extension lists:

            IMAGES = ('.jpg', '.jpeg', '.png', '.gif', '.bmp')

            AUDIO = ('.wav', '.mp3', '.aac', '.ogg', '.oga', '.flac')

            DOCUMENTS = ('.pdf', '.rtf', '.txt',
                '.odf', '.odp', '.ods', '.odg', '.ott', '.otp', '.ots', '.otg',
                '.pages', '.key', '.numbers', '.gnumeric', '.abw',
                '.doc', '.ppt', '.xls', '.vsd',
                '.docx', '.pptx', '.xlsx', '.vsx',
                )

            DATA = ('.csv', '.json', '.xml', '.ini', '.plist', '.yaml', '.yml')

            ARCHIVES = ('.zip', '.gz', '.bz2', '.tar', '.tgz', '.txz', '.7z')

            DEFAULT = IMAGES + AUDIO + DOCUMENTS

        denied
        :   List of forbidden extensions. Set to `None` to disable.
            If the uploaded file *does* have one of these extensions, a
            `UnsupportedMediaType` exception will be raised.

        max_size
        :   Maximum file size, in bytes, that file can have.
            Note: The `request` attribute `max_content_length`, if defined,
            has higher priority.
        
        """
        self.base_path = base_path.rstrip('/')
        self.base_url = base_url.rstrip('/')
        try:
            os.makedirs(os.path.realpath(base_path))
        except (OSError), e:
            if e.errno != errno.EEXIST:
                raise

        self.upload_to = upload_to
        self.secret = secret
        self.prefix = prefix
        self.allowed = allowed or []
        self.denied = denied or []
        self.max_size = max_size
    
    def __repr__(self):
        return '<%s "%s" secret=%s>' % (self.__class__.__name__,
            self.upload_to, self.secret)

    def save(self, filesto, upload_to=None, secret=None, prefix=None,
            allowed=None, denied=None, max_size=None):
        """
        Except for `filesto`, all of these parameters are optional, so only
        bother setting the ones relevant to *this upload*.

        filesto
        :   A `werkzeug.FileStorage`.
        
        upload_to
        :   A pattern used to build the upload path on the fly. 
            The wildcards avaliable are: 

                {yyyy},{yy}: Year
                {mm}, {m}: Month (0-padded or not)
                {ww}, {w}: Week number in the year (0-padded or not)
                {dd}, {d}: Day (0-padded or not)
                {hh}, {h}: Hours (0-padded or not)
                {nn}, {n}: Minutes (0-padded or not)
                {ss}, {s}: Seconds (0-padded or not)
                {a+}: Filename first letters
                {z+}: Filename last letters
                {r+}: Random letters and/or numbers
             
            Instead of a string, this can also be a callable.

        secret
        :   If True, instead of the original filename, a random one'll
             be used.

        prefix
        :   To avoid race-conditions between users uploading files with
            the same name at the same time. If `secret` is True, this
            will be ignored.

        allowed
        :   List of allowed file extensions. `None` to allow all
            of them. If the uploaded file doesn't have one of these
            extensions, an `UnsupportedMediaType` exception will be
            raised.
             
            Shake-Files come with some pre-defined extension lists:

            IMAGES = ('.jpg', '.jpeg', '.png', '.gif', '.bmp')

            AUDIO = ('.wav', '.mp3', '.aac', '.ogg', '.oga', '.flac')

            DOCUMENTS = ('.pdf', '.rtf', '.txt',
                '.odf', '.odp', '.ods', '.odg', '.ott', '.otp', '.ots', '.otg',
                '.pages', '.key', '.numbers', '.gnumeric', '.abw',
                '.doc', '.ppt', '.xls', '.vsd',
                '.docx', '.pptx', '.xlsx', '.vsx',
                )

            DATA = ('.csv', '.json', '.xml', '.ini', '.plist', '.yaml', '.yml')

            ARCHIVES = ('.zip', '.gz', '.bz2', '.tar', '.tgz', '.txz', '.7z')

            DEFAULT = IMAGES + AUDIO + DOCUMENTS

        denied
        :   List of forbidden extensions. Set to `None` to disable.
            If the uploaded file *does* have one of these extensions, a
            `UnsupportedMediaType` exception will be raised.

        max_size
        :   Maximum file size, in bytes, that file can have.
            Note: The attribute `max_content_length` defined in the
            `request` object has higher priority.
        
        """
        if not filesto:
            return None
        upload_to = upload_to or self.upload_to
        secret = secret or self.secret
        prefix = prefix or self.prefix
        original_filename = filesto.filename
        allowed = allowed or self.allowed
        denied = denied or self.denied

        self.validate(filesto, allowed, denied, max_size)

        tmplpath = upload_to
        if callable(tmplpath):
            tmplpath = tmplpath(original_filename)
        name, ext = os.path.splitext(original_filename)
        if secret:
            name = utils.get_random_filename()
        else:
            name = prefix + name
        filepath = utils.format_path(tmplpath, name)
        
        filename = utils.get_unique_filename(self.base_path, filepath, name,
            ext=ext)
        fullpath = utils.make_dirs(self.base_path, filepath)

        fullpath = os.path.join(fullpath, filename)
        filesto.save(fullpath)
        filesize = os.path.getsize(fullpath)
        
        # Post validation
        if max_size and filesize > max_size:
            try:
                os.remove(fullpath)
            except:
                pass
            raise RequestEntityTooLarge
        
        data = {
            'name': filename,
            'relpath': filepath,
            'size': filesize,
            'content_type': filesto.content_type,
            'remote_url': None,
        }
        return File(data, self.base_path, self.base_url)
    
    __call__ = save

    def validate(self, filesto, allowed=None, denied=None, max_size=None):
        max_size = max_size or self.max_size
        content_length = filesto.content_length
        if content_length == 0:
            filesto.seek(0, 2)
            content_length = filesto.tell()
            filesto.seek(0, 0)
        
        if max_size and content_length > max_size:
            raise RequestEntityTooLarge
        
        original_filename = filesto.filename
        name, ext = os.path.splitext(original_filename)
        ext = ext.lower()
        self.check_file_extension(ext, allowed, denied)
    
    def check_file_extension(self, ext, allowed=None, denied=None):
        allowed = allowed or self.allowed
        denied = denied or self.denied

        if allowed and not ext in allowed:
            raise UnsupportedMediaType()
        if denied and ext in denied:
            raise UnsupportedMediaType()


class File(object):
    """File data wrapper.
    """
    
    def __init__(self, data, base_path, base_url):
        data = data or {}
        self.name = data.get('name', u'')
        self.relpath = data.get('relpath', '').strip('/')
        self.size = data.get('size', u'')
        self.type = data.get('type', u'')
        self.remote_url = data.get('remote_url')

        self.width = data.get('width')
        self.height = data.get('height')
        
        self.base_path = base_path.rstrip('/')
        self.base_url = base_url.rstrip('/')
        
        self.is_image = self.type.startswith('image/')

        path = ''
        if self.relpath:
            path = os.path.join(self.base_path, self.relpath, self.name)
        self.path = path

        url = ''
        if self.remote_url:
            url = self.remote_url
        elif self.relpath:
            url = '%s/%s/%s' % (self.base_url, self.relpath, self.name)    
        self.url = url
    
    @property
    def __dict__(self):
        return self.to_dict()

    def __nonzero__(self):
        return bool(self.path)
    
    def __repr__(self):
        return repr(self.to_dict())
    
    def remove(self):
        try:
            os.remove(self.path)
        except OSError:
            pass
    
    def to_dict(self):
        """Serialize to a dictionary.
        """
        data = {
            'name': self.name,
            'relpath': self.relpath,
            'size': self.size,
            'type': self.type,
            'url': self.url,
            'remote_url': self.remote_url,
        }
        if self.width:
            data['width'] = self.width
        if self.height:
            data['height'] = self.height
        return data
    
    def to_json(self):
        """Serialize to JSON.
        """
        return utils.json.dumps(self.to_dict())


if sqlalchemy_available:
    class FileType(TypeDecorator):
        """Saves a File as a JSON-encoded string and reads it back as
        a File."""

        impl = Text
        filedata_class = File

        def __init__(self, base_path, base_url, default=None, **kwargs):
            """
            """
            self.base_path = base_path
            self.base_url = base_url
            self.default = default
            self.kwargs = kwargs
            TypeDecorator.__init__(self, **kwargs)
        
        def process_bind_param(self, value, dialect):
            if value is None:
                return None
            if hasattr(value, 'to_json'):
                return value.to_json()
            return utils.json.dumps(value)
        
        def process_result_value(self, value, dialect):
            if not value:
                if self.default:
                    return self.default
                return None
            data = utils.json.loads(value)
            return self.filedata_class(data, self.base_path, self.base_url)
        
        def copy(self):
            return self.__class__(self.base_path, self.base_url,
                default=self.default, **self.kwargs)

