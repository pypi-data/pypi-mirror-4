"""file/image gallery view

:organization: Logilab
:copyright: 2006-2012 LOGILAB S.A. (Paris, FRANCE), all rights reserved.
:contact: http://www.logilab.fr/ -- mailto:contact@logilab.fr
"""

__docformat__ = "restructuredtext en"
_ = unicode

from logilab.mtconverter import xml_escape
from logilab.common.decorators import monkeypatch

from cubicweb import typed_eid
from cubicweb.view import EntityView
from cubicweb.selectors import is_instance, has_mimetype, adaptable
from cubicweb.web.views import ajaxcontroller

class GalleryView(EntityView):
    __regid__ = 'gallery'
    __select__ = is_instance('File')

    currently_displayed = None

    def call(self):
        self._cw.add_js(('cubes.file.js', 'cubicweb.ajax.js'))
        self._cw.add_css('cubes.file.css')
        eid = typed_eid(self._cw.form.get('selected', self.cw_rset[0][0]))
        self.currently_displayed = eid
        for i in xrange(self.cw_rset.rowcount):
            self.cell_call(row=i, col=0)
        rset = self._cw.execute('Any X where X eid %(x)s', {'x': eid})
        self.w(u'<div id="imageholder">')
        self.wview('primary', rset, row=0, col=0, initargs={'is_primary':False})
        self.w(u'</div>')
        self.w(u'<div class="imagegallery">')
        self.w(u'</div>')

    def cell_call(self, row, col):
         entity = self.cw_rset.complete_entity(row, col)
         iimage = entity.cw_adapt_to('IImage')
         if iimage is not None:
             icon = xml_escape(iimage.download_url(small=1))
         else:
             icon = self._cw.uiprops['FILE_ICON']
         title = xml_escape(entity.dc_title())
         # .currently_displayed is None if we went directly to cell_call,
         # eg view called only for that entity, in which case we want
         # it to be considered as selected.
         if self.currently_displayed is None or entity.eid == self.currently_displayed:
             self.w(u'<a href="javascript:displayImg(%(eid)s)" title="%(title)s"><img id="img%(eid)s" '
                    u'class="selectedimg" alt="%(title)s" src="%(icon)s"/></a>'
               % {'eid':entity.eid, 'title':title,'icon':icon})
         else:
             self.w(u'<a href="javascript:displayImg(%(eid)s)" title="%(title)s"><img id="img%(eid)s" '
                    'alt="%(title)s" src="%(icon)s"/></a>'
               % {'eid':entity.eid, 'title':title,'icon':icon})


@ajaxcontroller.ajaxfunc(output_type='xhtml')
def js_get_image(self, eid):
    return self._cw.view('primary', self._cw.eid_rset(eid), row=0, col=0,
                         initargs={'is_primary': False})


class AlbumView(EntityView):
    __regid__ = 'album'
    __select__ = adaptable('IImage')

    def call(self, nbcol=5):
        self._cw.add_css('cubes.file.css')
        lines = [[]]
        for idx in xrange(self.cw_rset.rowcount):
            if len(lines[-1]) == nbcol:
                lines.append([])
            lines[-1].append(self._make_cell(idx, 0))
        while len(lines[-1]) != nbcol:
            lines[-1].append(u'&#160;')
        self.w(u'<table class="album">')
        for line in lines:
            self.w(u'<tr>')
            self.w(u''.join(u'<td>%s</td>' % cell for cell in line))
            self.w(u'</tr>')
        self.w(u'</table>')

    def _make_cell(self, row, col):
        entity = self.cw_rset.complete_entity(row, col)
        icon = xml_escape(entity.cw_adapt_to('IImage').download_url(small=1))
        title = xml_escape(entity.dc_title())
        return (u'<a href="%(url)s" title="%(title)s"><img alt="%(title)s" src="%(icon)s"/></a>'
                % {'url':xml_escape(entity.absolute_url()), 'title':title,'icon':icon})

    def cell_call(self, row, col):
        self.w(self._make_cell(row, col))


class ImageAdaptedView(AlbumView):
    __regid__ = 'sameetypelist'
    __select__ = has_mimetype('image/') & adaptable('IImage')
