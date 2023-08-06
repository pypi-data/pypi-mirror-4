import sys
from os import listdir, path as osp

from cubicweb import Binary


def fsimport(cw, fspaths, parenteid=None, mapfolders=True, bfss=False,
             fsencoding=sys.stdout.encoding or 'utf-8', quiet=False):
    cw.set_cnxset()
    assert bfss, 'not implemented'
    if bfss:
        cw.transaction_data['fs_importing'] = True
    if parenteid is not None:
        parent = cw.execute('Any X WHERE X eid %(x)s', {'x': parenteid}).get_entity(0, 0)
    else:
        parent = None
    # XXX what if not bfss?
    alreadyimported = set(x.getvalue() for x, in cw.execute(
        'Any fspath(D) WHERE X data D, X is File'))
    for fspath in fspaths:
        fspath = osp.abspath(osp.normpath(fspath))
        if osp.isdir(fspath):
            import_directory(cw, fspath, parent, mapfolders, bfss, fsencoding,
                             quiet, _alreadyimported=alreadyimported)
        else:
            import_file(cw, fspath, parent, bfss, fsencoding, quiet,
                        _alreadyimported=alreadyimported)


def import_directory(cw, directory, parent=None, mapfolders=True, bfss=False,
                     fsencoding=sys.stdout.encoding or 'utf-8', quiet=False,
                     _indent='', _alreadyimported=()):
    # getting directory content will check it's validity, do it before creating
    # any Folder entity
    dirfiles = listdir(directory)
    # XXX what if not bfss
    if mapfolders:
        parent = folder_entity(cw, directory, parent=parent, fsencoding=fsencoding)
    if not quiet:
        print _indent + '** importing directory', directory
    for fname in dirfiles:
        fspath = osp.join(directory, fname)
        if osp.isdir(fspath):
            import_directory(cw, fspath, parent, mapfolders, bfss, fsencoding,
                             quiet, _indent=_indent + '  ',
                             _alreadyimported=_alreadyimported)
        else:
            import_file(cw, fspath, parent, bfss, fsencoding, quiet,
                        _indent=_indent + '  ',
                        _alreadyimported=_alreadyimported)


def import_file(cw, fspath, parent=None, bfss=False,
                fsencoding=sys.stdout.encoding or 'utf-8', quiet=False,
                _indent='', _alreadyimported=()):
    fname = osp.basename(fspath)
    if isinstance(fname, str):
        fname = unicode(fname, fsencoding)
    if fspath in _alreadyimported:
        if not quiet:
            print _indent + '  skipping already imported', fname
        return
    if not quiet:
        print _indent + '  importing', fname
    if bfss:
        efile = cw.create_entity('File', data_name=fname,
                                 data=Binary(fspath))
    else:
        stream = open(fspath, 'rb')
        efile = cw.create_entity('File', data_name=fname,
                                 data=Binary(stream.read()))
        stream.close()
    _alreadyimported.add(fspath)
    if parent is not None:
        efile.set_relations(filed_under=parent)


def folder_entity(cw, directory, parent=None, fsencoding='utf-8'):
    if isinstance(directory, str):
        directory = unicode(directory, fsencoding)
    if parent is None:
        rset = cw.execute('Folder X WHERE X name %(name)s', {'name': directory})
    else:
        rset = cw.execute('Folder X WHERE X name %(name)s, X filed_under P, P eid %(p)s',
                          {'name': osp.dirname(directory), 'p': parent.eid})
    if rset:
        return rset.get_entity(0, 0)
    # create the folder
    if parent is None:
        return cw.create_entity('Folder', name=directory)
    return cw.create_entity('Folder', name=directory, filed_under=parent)
