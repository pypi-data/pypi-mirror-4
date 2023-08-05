from mercurial import util, templater, hg, error

import fnmatch, os, os.path, time, datetime, posixpath, re

from itertools import izip

_TOKEN_RE = re.compile(r'(?:\d+|\w+|[^\d\w\s]+)')

def smartcmp(a, b):
    """Compare two filenames by breaking them up into tokens and comparing
    the tokens.  Integer tokens are compared by value, not by character.
    If two strings are token-wise equal, they are then compared by character
    instead."""
    for atoken, btoken in izip(_TOKEN_RE.finditer(a),
                               _TOKEN_RE.finditer(b)):
        atok = atoken.group(0)
        btok = btoken.group(0)

        if atok[0] in '0123456789' \
               and btok[0] in '0123456789':
            ret = cmp(int(atok), int(btok))
        else:
            ret = cmp(atok, btok)
        
        if ret:
            return ret

    return cmp(a, b)

def walk(ui, repo, ctx, subrepos, match, sort, dumb, prefix=None, depth=1):
    """Walk the specified context of the specified repository, calling
    the match function and yielding

       (kind, namepieces, ctxname, repopath, repo, ctx)

    tuples for each item the match function returns True for."""

    # First do things at the base level
    prev_dir = None
    for name in ctx:
        ns = name.split('/')
        
        if prefix:
            if ns[:len(prefix)] != prefix:
                continue

            ns = ns[len(prefix):]

        if len(ns) != depth:
            continue

        if not match(ns):
            continue

        yield 'file', ns, name, '', repo, ctx

    # Next, do directories at this level

    # Cope with sorting
    reverse = False
    for s in sort:
        if s == '-name':
            reverse = True
            break
        elif s == 'name' or s == '+name':
            break

    files = [(f, f, '', repo, ctx) for f in ctx]

    if subrepos:
        # Recursively search for subrepositories
        stack = [('', ctx)]
        while stack:
            base, spctx = stack.pop()
            
            for subpath, info in spctx.substate.iteritems():
                if info[2] != 'hg':
                    ui.warn('cannot examine non-mercurial subrepository %s'
                            % posixpath.join(base, subpath))
                    continue

                subrepo = hg.repository(ui,
                                        os.path.join(repo.root, base, subpath),
                                        create=False)

                subctx = subrepo[info[1]]
                newbase = posixpath.join(base, subpath)
                files += [(posixpath.join(newbase, f), f,
                           newbase, subrepo, subctx)
                          for f in subctx]

                stack.append((newbase, subctx))

    # Sort the names piecewise
    def fcmp(x,y):
        xs = x[0].split('/')
        ys = y[0].split('/')

        for xn,yn in izip(xs[:-1], ys[:-1]):
            if not dumb:
                ret = smartcmp(xn, yn)
            else:
                ret = cmp(xn, yn)
            if reverse:
                ret = -ret
            if ret:
                return ret

        ret = cmp(len(xs), len(ys))

        if ret:
            return ret

        if not dumb:
            ret = smartcmp(xs[-1], ys[-1])
        else:
            ret = cmp(xs[-1], ys[-1])
        if reverse:
            ret = -ret
        return ret
    
    files.sort(cmp=fcmp)

    prev_dir = None
    prev_inner = None
    prev_real_depth = 0
    for name, ctxname, subpath, subrepo, context in files:
        ns = name.split('/')

        if prefix:
            if ns[:len(prefix)] != prefix:
                continue

            ns = ns[len(prefix):]

        if len(ns) <= depth:
            continue

        if not match(ns):
            continue

        if depth == 0:
            # depth = 0 means we're in recursive mode
            if len(ns) > 1:
                if len(ns) > prev_real_depth:
                    yield 'innerdir', ns[:-1], ctxname, subpath, subrepo, None
                    prev_dir = None
                prev_real_depth = len(ns)

                this_dir = ns[-2]
                if this_dir != prev_dir:
                    yield 'dir', ns[:-1], ctxname, subpath, subrepo, None
                    prev_dir = this_dir
            
            yield 'file', ns, ctxname, subpath, subrepo, context
            continue

        this_dir = '/'.join(ns[:depth])
        if this_dir != prev_dir:
            yield 'dir', ns[:depth], ctxname, subpath, subrepo, None
            prev_dir = this_dir
            prev_inner = None

        if len(ns) == depth + 1:
            yield 'file', ns, ctxname, subpath, subrepo, context
        else:
            this_inner = ns[depth]
            if this_inner != prev_inner:
                yield 'innerdir', ns[:depth + 1], ctxname, subpath, subrepo, None
                prev_inner = this_inner
            
def list_files(ui, repo, *args, **opts):
    """list files and related information

    For each name given that is a file of a type other than a directory,
    displays its name as well as any requested, associated information.
    For each name given that is a directory, displays the names of files
    within that directory, as well as any requested, associated information.

    If no names are given, the contents of the working directory are
    displayed.

    N.B. the :hg:`list` command *only displays items that are checked in
    to the repository*.  It specifically *does not* display items that are
    merely present in the working directory, even if you have used :hg:`add`
    on them.

    Use the -s/--sort option to change the sort order for the files; the
    argument is a comma-separated list of any of the following items:

      :name:    the name of the file
      :rev:     the last revision at which the file was changed
      :date:    the date of the last revision at which the file was changed
      :author:  the name of the user who last changed the file
      :user:    the short name of the user who last changed the file
      :size:    the size of the file
      :subrepo: the name of the subrepository

    Each item may optionally be preceded by a '+' or a '-' character to
    control sort direction.

    If the -l/--long option is given, the following information is displayed
    for each file:

      - file flags
      - short user (pass -v to change to full username)
      - size of the file (pass -H to view in human-readable form)
      - revision of last change (in rev:node format)
      - date of last change
      - file name

    Additionally, if you use the -S option to recurse into subrepositories,
    a column will be inserted before the revision column naming the
    subrepository.  Subrepository recursion only works for Mercurial
    subrepositories; foreign subrepositories are not supported.

    If the -F/--flags option is specified, an '@', '*', or '/' character
    will be appended to the name to indicate symbolic links, executable files,
    subrepositories and directories respectively.

    You can also customise the output using the --template argument; this
    uses the same template system as :hg:`log`; the following keywords are
    defined:

      :name:    the name of the file
      :mode:    the UNIX mode of the file
      :size:    the size of the file, in bytes
      :kind:    an '@', '*', or '/' character depending on the type of
                the file
      :subrepo: if this file is in a subrepository, the path within the outer
                repository
      :rev:     the last revision at which the file was changed
      :node:    the changeset ID for that revision
      :date:    the date of the last revision at which the file was changed
      :author:  the name of the user who last changed the file
      :branch:  the branch of the last revision at which the file was changed
      :desc:    the description of that revision

    If you pass the --columns switch as well as the --template switch,
    you can obtain column-aligned output.  The --columns switch takes a
    string, each character of which corresponds to a column in the output.
    An 'l' character left-justifies within the column, while an 'r'
    right-justifies and a 'c' character will center within the column.
    Any other character will cause right-justification.

    If you are using the --columns switch, your template should use '\0'
    characters (i.e. NULs) to separate the columns.  If you have more
    columns than the number of alignment specifications, the extra
    columns will be left-justified by default.  A trailing left-aligned
    column will not be padded."""

    rev = opts['rev']
    ctx = repo[rev]
    all = opts['all']
    flags = opts['flags']
    sort = [s.lower().strip() for s in opts['sort'].split(',')]
    template = opts['template']
    style = opts['style']
    should_format = ui.formatted()
    long_format = opts['long']
    human = opts['human']
    subrepos = opts['subrepos']
    recursive = opts['recursive']
    dumb = opts['dumb']
    align_columns = opts['columns']
    file_buffer = []

    # Work out where to get our template from
    if not (style or template):
        template = ui.config('ui', 'listtemplate')
        if template:
            try:
                template = templater.parsestring(template)
            except SyntaxError:
                template = templater.parsestring(template, quoted=False)
        else:
            style = util.expandpath(ui.config('ui', 'style', ''))
    elif template:
        try:
            template = templater.parsestring(template, quoted=False)
        except SyntaxError, e:
            raise util.Abort('bad template: %s' % e.args[0])
    
    mapfile = None
    if style and not template:
        mapfile = style
        if not os.path.split(mapfile)[0]:
            mapname = (templater.templatepath('map-cmdline.' + mapfile)
                       or templater.templatepath(mapfile))
            if mapname:
                mapfile = mapname

    if style or template:
        should_format = False
        long_format = True
    elif long_format:
        if ui.verbose:
            template = ['{mode|lsmode}\0{author}']
        else:
            template = ['{mode|lsmode}\0{author|user}']
        align_columns = ['ll']
        
        if human:
            template.append('{size|lssize}')
        else:
            template.append('{size}')
        align_columns.append('r')
        
        if subrepos:
            template.append('{subrepo}')
            align_columns.append('l')
            
        if ui.debugflag:
            template.append('{rev}:{node}')
        else:
            template.append('{rev}:{node|short}')
        align_columns.append('r')
        
        if ui.verbose:
            template.append('{date|isodate}')
        else:
            template.append('{date|lsdate}')
        align_columns.append('l')
        
        if flags:
            template.append('{name}{kind}')
        else:
            template.append('{name}')
        align_columns.append('l')
        
        template = '\0'.join(template)
        align_columns = ''.join(align_columns)

    formatter = None
    if style or template:
        formatter = templater.templater(mapfile)
        if template:
            formatter.cache['file'] = template

        tmplmodes = [
            (True, None),
            (ui.verbose, 'verbose'),
            (ui.quiet, 'quiet'),
            (ui.debugflag, 'debug'),
        ]

        for mode, postfix in tmplmodes:
            cur = postfix and ('file_%s' % postfix) or 'file'
            if mode and cur in formatter:
                template_name = cur
    
    # Find the path relative to the repository root
    cwd = os.getcwd()
    relpath = os.path.relpath(cwd, repo.root)
    prefix = relpath.replace(os.path.sep, '/')

    if prefix == '.':
        prefix = None
    else:
        prefix = prefix.split('/')
    
    def list_dir(name, subpath, subrepo):
        file_buffer.append((name, subpath, subrepo, None))

    def list_file(name, subpath, subrepo, fctx):
        file_buffer.append((name, subpath, subrepo, fctx))

    def file_kind(fctx, subpath):
        if not flags:
            return ''
        if not fctx:
            return '/'
        kind = ''
        ctxflags = fctx.flags()
        if 'l' in ctxflags:
            kind = '@'
        elif 'x' in ctxflags:
            kind = '*'
        return kind

    def cmp_buf(x,y):
        xname, xsp, xsr, xctx = x
        yname, ysp, ysr, yctx = y
        for s in sort:
            invert = False
            if s.startswith('-'):
                invert = True
                s = s[1:]
            elif s.startswith('+'):
                s = s[1:]

            ret = 0
            if s == 'name':
                if not dumb:
                    ret = smartcmp(xname, yname)
                else:
                    ret = cmp(xname, yname)
            elif xctx is None or yctx is None:
                if xctx is None and yctx is None:
                    ret = 0
                elif xctx is None:
                    ret = -1
                elif yctx is None:
                    ret = +1
            elif s == 'rev':
                ret = cmp(xctx.linkrev(), yctx.linkrev())
            elif s == 'size':
                ret = cmp(xctx.size(), yctx.size())
            elif s == 'subrepo':
                ret = cmp(xsp, ysp)
            else:
                xcctx = xsr[xctx.linkrev()]
                ycctx = ysr[yctx.linkrev()]

                if s == 'author':
                    ret = cmp(xcctx.user(), ycctx.user())
                elif s == 'user':
                    ret = cmp(ui.shortuser(xcctx.user()),
                              ui.shortuser(ycctx.user()))
                elif s == 'date':
                    ret = cmp(xcctx.date(), ycctx.date())

            if invert:
                ret = -ret
                
            if ret != 0:
                break

        return ret
    
    def flush_buffer():
        if not file_buffer:
            return

        file_buffer.sort(cmp=cmp_buf)

        do_long = not should_format or long_format
        if not do_long:
            w = ui.termwidth()
            ml = max([len(n) for n,sp,sr,f in file_buffer])
            if flags:
                ml += 1
            ml = (((ml + 1) + 7) & ~7) - 1
            if ml > w / 2 - 2:
                do_long = True
                
        if do_long:
            outbuf = []
            for name, subpath, subrepo, fctx in file_buffer:
                kind = file_kind(fctx, subpath)
                
                if formatter:
                    mode = 0o100644
                    
                    if not fctx:
                        mode = 0o040755
                    else:
                        ctxflags = fctx.flags()
                        if 'l' in ctxflags:
                            mode = 0o120755
                        if 'x' in ctxflags:
                            mode = mode | 0o0111

                    if not fctx:
                        user = 'nobody'
                        date = (0, 0)
                        size = 0
                        rev = -1
                        node = 'f'*40
                        desc = ''
                        branch = ''
                    else:
                        size = fctx.size()
                        rev = fctx.linkrev()
                        cctx = subrepo[rev]
                        user = cctx.user()
                        date = cctx.date()
                        node = cctx.hex()
                        desc = cctx.description()
                        branch = cctx.branch()

                    info = { 'name': name,
                             'kind': kind,
                             'mode': mode,
                             'author': user,
                             'date': date,
                             'size': size,
                             'rev': rev,
                             'node': node,
                             'subrepo': subpath,
                             'desc': desc,
                             'branch': branch }

                    try:
                        fmt = templater.stringify(formatter(template_name,
                                                            **info))
                    except error.ParseError, e:
                        raise util.Abort('bad template - at character %s: %s'
                                         % (e.args[1], e.args[0]))
                    
                    if align_columns:
                        outbuf.append(fmt.split('\0'))
                    else:
                        ui.write(fmt)
                else:
                    ui.write('%s%s\n' % (name, kind))

            del file_buffer[:]

            if align_columns and outbuf:
                colwidths = [len(n) for n in outbuf[0]]
                for line in outbuf:
                    colwidths = [max(colwidths[n], len(line[n]))
                                 for n in xrange(0, len(colwidths))]

                fmtstr = []
                for ncol in xrange(0, len(colwidths)):
                    if ncol >= len(align_columns):
                        alignment = 'l'
                    else:
                        alignment = align_columns[ncol]
                    width = colwidths[ncol]
                    
                    if alignment == 'l':
                        # Trailing 'l' columns are not padded
                        if ncol == len(colwidths) - 1:
                            fmtstr.append('{{{0}}}'.format(ncol))
                        else:
                            fmtstr.append('{{{0}:<{1}}}'.format(ncol, width))
                    elif alignment == 'c':
                        fmtstr.append('{{{0}:^{1}}}'.format(ncol, width))
                    else:
                        fmtstr.append('{{{0}:>{1}}}'.format(ncol, width))

                fmtstr = ' '.join(fmtstr) + '\n'
                
                for line in outbuf:
                    ui.write(fmtstr.format(*line))
                    
            return
        
        per_line = w / (ml + 1)
        ml = w / per_line
        count = len(file_buffer)
        rows = (count + per_line - 1) / per_line
        columns = range(0, count, rows)
        
        for n in xrange(0, rows):
            line = []
            for c in columns:
                if c + n >= count:
                    break
                name,sp,sr,fctx = file_buffer[c + n]
                kind = file_kind(fctx, sp)
                line.append('%-*s' % (ml, name + kind))

            ui.write(''.join(line))
            ui.write('\n')

        del file_buffer[:]

    # The recursive case
    if recursive:
        first = True
        if not args:
            args = [None]
        else:
            for pattern in args:
                if len(pattern.split('/')) != 1:
                    raise util.Abort('when in recursive mode, patterns '
                                     'cannot contain \'/\' characters')
        
        for pattern in args:
            if pattern is None:
                ps = []
            else:
                ps = pattern.split('/')

            def match(ns):
                if not all and ns[-1].startswith('.'):
                    return False
                if pattern is None:
                    return True
                if not fnmatch.fnmatch(ns[-1], pattern):
                    return False
                return True

            for kind, ns, name, rpath, rpo, ctxt in walk (ui, repo, ctx,
                                                          subrepos, match,
                                                          sort, dumb, prefix, 0):
                if kind == 'file':
                    if should_format:
                        list_file(ns[-1], rpath, rpo, ctxt[name])
                    else:
                        list_file('/'.join(ns), rpath, rpo, ctxt[name])
                    first = False
                elif should_format and kind == 'dir':
                    if not first:
                        flush_buffer()
                        ui.write('\n')
                    ui.write('%s:\n' % '/'.join(ns))
                    first = False
                elif kind == 'innerdir':
                    if should_format:
                        list_dir(ns[-1], rpath, rpo)
                    else:
                        list_dir('/'.join(ns), rpath, rpo)
                    first = False

        flush_buffer()
        return

    # The pattern match case
    if len(args):
        first = True
        for pattern in args:
            ps = pattern.split('/')

            def match(ns):
                if not all and ns[-1].startswith('.'):
                    return False
                for n, p in izip(ns, ps):
                    if not fnmatch.fnmatch(n, p):
                        return False
                return True

            for kind, ns, name, rpath, rpo, ctxt in walk (ui, repo, ctx,
                                                          subrepos, match,
                                                          sort, dumb, prefix,
                                                          len(ps)):
                if kind == 'file':
                    if not should_format or len(ps) > 1 and len(ns) == len(ps):
                        list_file('/'.join(ns), rpath, rpo, ctxt[name])
                    else:
                        list_file(ns[-1], rpath, rpo, ctxt[name])
                    first = False
                elif should_format and kind == 'dir':
                    if not first:
                        flush_buffer()
                        ui.write('\n')
                    ui.write('%s:\n' % '/'.join(ns))
                    first = False
                elif kind == 'innerdir':
                    if should_format:
                        list_dir(ns[-1], rpath, rpo)
                    else:
                        list_dir('/'.join(ns), rpath, rpo)
                    first = False

        flush_buffer()
        return

    # Neither recursive, nor pattern match
    prev_dir = None
    for name in ctx:
        ns = name.split('/')

        if prefix:
            if ns[:len(prefix)] != prefix:
                continue

            ns = ns[len(prefix):]

        if not all and ns[0].startswith('.'):
            continue
            
        if len(ns) == 1:
            list_file('/'.join(ns), '', repo, ctx[name])
        elif len(ns) > 1:
            this_dir = ns[0]
            if this_dir != prev_dir:
                list_dir(this_dir, '', repo)
                prev_dir = this_dir
    
    if subrepos:
        for name in ctx.substate:
            ns = name.split('/')

            if prefix:
                if ns[:len(prefix)] != prefix:
                    continue

                ns = ns[len(prefix):]

            if not all and ns[0].startswith('.'):
                continue
        
            list_dir(ns[0], '', None)

    flush_buffer()
