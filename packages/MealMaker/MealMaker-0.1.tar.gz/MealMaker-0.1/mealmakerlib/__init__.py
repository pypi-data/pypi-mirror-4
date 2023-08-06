#!/usr/bin/env python
# Copyright (c) 2010 Matt Harrison

import sys
import optparse

import meta

DEFAULT_MARKER = '# -'

def scrub_content(content, marker):
    """
    when you hit marker skip it (in_content = True) and up to and including the next marker.
    
    yields line,in_content for lines in content
    send in_content for st
    """
    in_marker = False

    for line in content:
        end = False
        if marker in line:
            if in_marker:
                end = True
            in_marker = not in_marker
        yield line, in_marker or end


def scrub_file(fin, fout, marker=DEFAULT_MARKER):
    r"""
    >>> import StringIO
    >>> fin = StringIO.StringIO('''foo
    ... bar
    ... # - junk
    ... baz
    ... # -
    ... biz
    ... # - jig
    ... ''')
    >>> fout = StringIO.StringIO('')
    >>> scrub_file(fin, fout)
    >>> print fout.getvalue()
    foo
    bar
    biz
    <BLANKLINE>

    """
    for line, in_marked in scrub_content(fin, marker):
        if not in_marked:
            fout.write(line)

def _test():
    import doctest
    doctest.testmod()
    
def main(prog_args):
    parser = optparse.OptionParser(version=meta.__version__, usage="mealmaker input [output]")
    parser.add_option('--marker', help="filter lines between marker(%s)"%DEFAULT_MARKER, default=DEFAULT_MARKER)
    opt, args = parser.parse_args(prog_args)

    if len(args) < 2:
        parser.print_help()
        return 1

    fin_name = args[1]
    fin = open(fin_name)

    if len(args) > 2:
        fout_name = args[2]
        fout = open(fout_name, 'w')
    else:
        fout = sys.stdout
    scrub_file(fin, fout, opt.marker)
if __name__ == '__main__':
    #_test()
    sys.exit(main(sys.argv))

