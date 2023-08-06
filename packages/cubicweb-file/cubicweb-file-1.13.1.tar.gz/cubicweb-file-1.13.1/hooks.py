"""File related hooks

:organization: Logilab
:copyright: 2003-2010 LOGILAB S.A. (Paris, FRANCE), all rights reserved.
:contact: http://www.logilab.fr/ -- mailto:contact@logilab.fr
"""
__docformat__ = "restructuredtext en"


from cubicweb import ValidationError
from cubicweb.server import hook
from cubicweb.sobjects.notification import ContentAddedView
from cubicweb.selectors import is_instance


class UpdateFileHook(hook.Hook):
    """a file has been updated, check data_format/data_encoding consistency
    """
    __regid__ = 'updatefilehook'
    __select__ = hook.Hook.__select__ & is_instance('File')
    events = ('before_add_entity', 'before_update_entity',)
    order = -1 # should be run before other hooks
    def __call__(self):
        if 'data' in self.entity.cw_edited:
            self.entity.set_format_and_encoding()
            maxsize = self._cw.vreg.config['image-max-size']
            if maxsize and self.entity.data_format.startswith('image/'):
                iimage = self.entity.cw_adapt_to('IImage')
                self.entity.cw_edited['data'] = iimage.thumbnail(shadow=False,
                                                                 size=maxsize)


class FileAddedView(ContentAddedView):
    """get notified from new files"""
    __select__ = is_instance('File')
    content_attr = 'description'
