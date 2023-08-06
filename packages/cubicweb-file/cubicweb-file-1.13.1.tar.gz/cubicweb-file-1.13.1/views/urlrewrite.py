from cubicweb.web.views.urlrewrite import SimpleReqRewriter, rgx


class FileReqRewriter(SimpleReqRewriter):
     rules = [
        (rgx('/file/(\d+)/raw(/.*)?'),
         dict(rql=r'Any X WHERE X eid \1', vid='download')),
     ]
