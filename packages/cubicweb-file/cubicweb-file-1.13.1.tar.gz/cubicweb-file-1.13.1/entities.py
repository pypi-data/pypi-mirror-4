"""entity classes for File entities

:organization: Logilab
:copyright: 2003-2011 LOGILAB S.A. (Paris, FRANCE), all rights reserved.
:contact: http://www.logilab.fr/ -- mailto:contact@logilab.fr
"""
__docformat__ = "restructuredtext en"

from os.path import join

from logilab.mtconverter import guess_mimetype_and_encoding
from logilab.common.deprecation import deprecated

from cubicweb import Binary
from cubicweb.entities import AnyEntity, fetch_config, adapters
from cubicweb.view import EntityAdapter
from cubicweb.selectors import is_instance, has_mimetype

from cubes.file.uilib import dropShadow

class File(AnyEntity):
    """customized class for File entities"""
    __regid__ = 'File'
    fetch_attrs, cw_fetch_order = fetch_config(['data_name', 'title'])

    def set_format_and_encoding(self):
        """try to set format and encoding according to known values (filename,
        file content, format, encoding).

        This method must be called in a before_[add|update]_entity hook else it
        won't have any effect.
        """
        assert 'data' in self.cw_edited, "missing mandatory attribute data"
        if self.cw_edited.get('data'):
            if hasattr(self.data, 'filename'):
                self.cw_edited['data_name'] = self.data.filename
        else:
            self.cw_edited['data_format'] = None
            self.cw_edited['data_encoding'] = None
            self.cw_edited['data_name'] = None
            return
        if 'data_format' in self.cw_edited:
            format = self.cw_edited.get('data_format')
        else:
            format = None
        if 'data_encoding' in self.cw_edited:
            encoding = self.cw_edited.get('data_encoding')
        else:
            encoding = None
        if not (format and encoding):
            format, encoding = guess_mimetype_and_encoding(
                data=self.cw_edited.get('data'),
                # use get and not get_value since data has changed, we only want
                # to consider explicitly specified values, not old ones
                filename=self.cw_edited.get('data_name'),
                format=format, encoding=encoding,
                fallbackencoding=self._cw.encoding)
            if format:
                self.cw_edited['data_format'] = unicode(format)
            if encoding:
                self.cw_edited['data_encoding'] = unicode(encoding)

    def dc_title(self):
        if self.title:
            return '%s (%s)' % (self.title, self.data_name)
        return self.data_name

    def size(self):
        rql = "Any LENGTH(D) WHERE X eid %(x)s, X data D"
        return self._cw.execute(rql, {'x': self.eid})[0][0]

    def read(self, size=-1):
        return self.data.read(size)

    def seek(self, pos, *args, **kwargs):
        return self.data.seek(pos, *args, **kwargs)

    def tell(self):
        return self.data.tell()

    def icon_url(self):
        config = self._cw.vreg.config
        for rid in (self.data_format.replace('/', '_', 1),
                    self.data_format.split('/', 1)[0],
                    'default'):
            iconfile = rid + '.ico'
            rpath, iconfile = config.locate_resource(join('icons', iconfile))
            if rpath is not None:
                return self._cw.data_url(iconfile)

    @deprecated('[file 1.9] use entity.cw_adapt_to("IDownloadable").download_url() instead')
    def download_url(self):
        return self.cw_adapt_to('IDownloadable').download_url()
    @deprecated('[file 1.9] use entity.cw_adapt_to("IDownloadable").download_content_type() instead')
    def download_content_type(self):
        return self.cw_adapt_to('IDownloadable').download_content_type()
    @deprecated('[file 1.9] use entity.cw_adapt_to("IDownloadable").download_encoding() instead')
    def download_encoding(self):
        return self.cw_adapt_to('IDownloadable').download_encoding()
    @deprecated('[file 1.9] use entity.cw_adapt_to("IDownloadable").download_file_name() instead')
    def download_file_name(self):
        return self.cw_adapt_to('IDownloadable').download_file_name()
    @deprecated('[file 1.9] use entity.cw_adapt_to("IDownloadable").download_data() instead')
    def download_data(self):
        return self.cw_adapt_to('IDownloadable').download_data()

    @property
    @deprecated('[file 1.6] use entity.data_name instead')
    def name(self):
        return self.data_name


from PIL.Image import open as pilopen
from PIL.Image import ANTIALIAS


class FileIDownloadableAdapter(adapters.IDownloadableAdapter):
    __select__ = is_instance('File')

    # IDownloadable
    def download_url(self, **kwargs):
        # include filename in download url for nicer url
        name = self._cw.url_quote(self.download_file_name())
        path = '%s/raw/%s' % (self.entity.rest_path(), name)
        return self._cw.build_url(path, **kwargs)
    def download_content_type(self):
        return self.entity.data_format
    def download_encoding(self):
        return self.entity.data_encoding
    def download_file_name(self):
        return self.entity.data_name
    def download_data(self):
        if self.download_content_type().startswith('image/') and \
               'small' in getattr(self._cw, 'form', ()): # Session has not .form
            # have to consume force param to avoid infinite recursion
            self._cw.form.pop('small')
            shadow = not self._cw.form.pop('noshadow', None)
            iimage = self.entity.cw_adapt_to('IImage')
            return iimage.thumbnail(shadow=shadow).getvalue()
        return self.entity.data.getvalue()


class IImageAdapter(EntityAdapter):
    __regid__ = 'IImage'
    __select__ = has_mimetype('image/')
    def __init__(self, *args, **kwargs):
        super(IImageAdapter, self).__init__(*args, **kwargs)
        idownloadable = self.entity.cw_adapt_to('IDownloadable')
        for meth in ('download_url', 'download_content_type',
                     'download_encoding', 'download_file_name',
                     'download_data'):
            setattr(self, meth, getattr(idownloadable, meth))

    def thumbnail(self, shadow=True, size=None):
        if size is None:
            size = self._cw.vreg.config['image-thumb-size']
        size = tuple(int(s) for s in size.split('x'))
        idownloadable = self.entity.cw_adapt_to('IDownloadable')
        data = idownloadable.download_data()
        pilimg = pilopen(Binary(data))
        if shadow:
            pilimg.draft("RGB", pilimg.size)
            pilimg = pilimg.convert("RGB")
            pilimg.thumbnail(size, ANTIALIAS)
            pilimg = dropShadow(pilimg)
        else:
            pilimg.thumbnail(size, ANTIALIAS)
        fmt = idownloadable.download_content_type().split('/', 1)[1]
        stream = Binary()
        pilimg.save(stream, fmt)
        stream.seek(0)
        stream.filename = idownloadable.download_file_name()
        return stream

Image = object # XXX
