"""hglist extension - enhanced file listing

This extension adds a new :hg:`list`/:hg:`ls` command that works in a
similar way to the UNIX ls command, but rather than listing the content
of the current directory, lists the files in a Mercurial repository."""
from mercurial import commands, templatefilters
from hglist.list_files import list_files
from hglist.filters import lsdate, lssize, lsmode

list_cmd = (list_files,
            [('r', 'rev', '', 'revision to list', 'REV'),
             ('a', 'all', False, 'include files whose names begin with a dot'),
             ('F', 'flags', False, 'show executable/directory/symlink state'),
             ('s', 'sort', 'name', 'set sort order', 'SORTORDER'),
             ('l', 'long', False, 'list in long format'),
             ('H', 'human', False, 'use human-readable sizes'),
             ('S', 'subrepos', False, 'enable subrepository support (hg only)'),
             ('', 'dumb', False, 'disable smart name sort'),
             ('', 'recursive', False, 'recurse into directories'),
             ('', 'style', None, 'display using template map file', 'STYLE'),
             ('', 'template', '', 'display with template', 'TEMPLATE'),
             ('', 'columns', '', 'set column alignment', 'ALIGNMENT')],
            '[options] [FILE ...]')

cmdtable = {
    'list|ls': list_cmd,
    }

testedwith = '2.4'
buglink = 'http://alastairs-place.net/projects/hglist/'

def extsetup(ui):
    templatefilters.filters['lsdate'] = lsdate
    templatefilters.filters['lssize'] = lssize
    templatefilters.filters['lsmode'] = lsmode
