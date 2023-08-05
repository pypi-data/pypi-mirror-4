import datetime

def lsdate(d):
    """:lsdate: Format a date in the style of ls"""
    if not d:
        return ''
    
    t, tz = d

    the_date = datetime.datetime.utcfromtimestamp(t)
    now = datetime.datetime.utcnow()

    the_months = the_date.year * 12 + the_date.month
    now_months = now.year * 12 + now.month

    if abs(now_months - the_months) >= 6:
        return the_date.strftime('%b %d  %Y')
    
    return the_date.strftime('%b %d %H:%M')

def lssize(s):
    """:lssize: Format a size in the style of ls -h"""
    if s < 1000:
        return '%sB' % s

    endings = ('K', 'M', 'G', 'T', 'P')
    for e in endings:
        s = s / 1024.0
        f = '%.1f%s' % (s, e)
        if len(f) <= 4:
            return f
        f = '%.0f%s' % (s, e)
        if len(f) <= 4:
            return f

    raise ValueError('size too large to format')

_LSKIND = '?pc?d?b?-?l?s???'
_SRWX = ['---', '--x', '-w-', '-wx', 'r--', 'r-x', 'rw-', 'rwx',
         '--S', '--s', '-wS', '-ws', 'r-S', 'r-s', 'rwS', 'rws']
_TRWX = ['---', '--x', '-w-', '-wx', 'r--', 'r-x', 'rw-', 'rwx',
         '--T', '--t', '-wT', '-wt', 'r-T', 'r-t', 'rwT', 'rwt']

def lsmode(m):
    """:lsmode: Format a mode value in the style of ls"""
    kind = (m >> 12) & 0o17
    flags = [_LSKIND[kind],
             _SRWX[((m & 0o4000) >> 8) | (m & 0o0700) >> 6],
             _SRWX[((m & 0o2000) >> 7) | (m & 0o0070) >> 3],
             _TRWX[((m & 0o1000) >> 6) | (m & 0o0007)]]
    return ''.join(flags)
