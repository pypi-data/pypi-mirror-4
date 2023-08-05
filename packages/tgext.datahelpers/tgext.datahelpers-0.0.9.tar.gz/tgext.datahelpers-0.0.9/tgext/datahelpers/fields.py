import tg, os, shutil, cgi, Image, json, tempfile
import sqlalchemy.types as types
import uuid as uuid_m
from tg.decorators import cached_property

class AttachedFile(object):
    def __init__(self, file, filename, uuid=None):
        self.uuid = uuid
        if not uuid:
            self.uuid = str(uuid_m.uuid1())

        self._file = file

        self.filename = unicode(filename)
        self.url = '/'.join([self.attachments_url, self.uuid, self.filename])
        self.local_path = os.path.join(self.attachment_dir, self.filename)

    @cached_property
    def file(self):
        if isinstance(self._file, basestring):
            self._file = open(self._file)
        return self._file

    @cached_property
    def attachments_url(self):
        return tg.config.get('attachments_url', '/attachments')

    @cached_property
    def attachment_dir(self):
        attachments_path = tg.config.get('attachments_path')
        if not attachments_path:
            attachments_path = os.path.join(tg.config['here'], tg.config['package'].__name__.lower(),
                                            'public', 'attachments')
        attachment_dir = os.path.join(attachments_path, self.uuid)
        return unicode(attachment_dir)

    def write(self):
        try:
            os.mkdir(self.attachment_dir)
        except Exception, e:
            pass

        if self.file.name != self.local_path:
            shutil.copyfileobj(self.file, open(self.local_path, 'w+'))
            self.file.seek(0)

    def unlink(self):
        shutil.rmtree(self.attachment_dir)

    def encode(self):
        return unicode(json.dumps({'file':self.local_path, 'filename':self.filename, 'uuid':self.uuid}))

    @classmethod
    def decode(cls, value):
        params = {}
        for key, value in json.loads(value).iteritems():
            params[str(key)] = value
        return cls(**params)

class Attachment(types.TypeDecorator):
    impl = types.Unicode

    def __init__(self, attachment_type=AttachedFile, *args, **kw):
        super(Attachment, self).__init__(*args, **kw)
        self.attachment_type = attachment_type

    def load_dialect_impl(self, dialect):
        return dialect.type_descriptor(types.VARCHAR(4096))

    def _create_attached_file(self, value):
        if isinstance(value, cgi.FieldStorage):
            filename = value.filename
            file = value.file
        elif isinstance(value, str):
            filename = 'attachment'
            file = tempfile.TemporaryFile()
            file.write(value)
            file.seek(0)
        else:
            filename = os.path.basename(value.name)
            file = value

        return self.attachment_type(file, filename)

    def process_bind_param(self, value, dialect):
        if isinstance(value, cgi.FieldStorage):
            if not bool(getattr(value, 'filename', None)):
                return None
        elif not value:
            return None

        if not isinstance(value, AttachedFile):
            value = self._create_attached_file(value)

        value.write()
        return value.encode()

    def process_result_value(self, value, dialect):
        if not value:
            return None

        return self.attachment_type.decode(value)

class AttachedImage(AttachedFile):
    thumbnail_size = (128, 128)
    thumbnail_format = 'png'

    def __init__(self, file, filename, uuid=None):
        super(AttachedImage, self).__init__(file, filename, uuid)
        
        thumb_filename = 'thumb.'+self.thumbnail_format.lower()
        self.thumb_local_path = os.path.join(self.attachment_dir, thumb_filename)
        self.thumb_url = '/'.join([self.attachments_url, self.uuid, thumb_filename])

    def write(self):
        super(AttachedImage, self).write()

        if self.file.name != self.local_path:
            self.file.seek(0)
            thumbnail = Image.open(self.file)
            thumbnail.thumbnail(self.thumbnail_size, Image.BILINEAR)
            thumbnail = thumbnail.convert('RGBA')
            thumbnail.format = self.thumbnail_format
            thumbnail.save(self.thumb_local_path)
