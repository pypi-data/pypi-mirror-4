# safe implementation of eval, undoes repr
#
# Copyright 2011 aragost Trifork
#
# This software may be used and distributed according to the terms of
# the GNU General Public License version 2 or any later version.

def unrepr(s):
    """Parse a string produced by repr in simple cases.

    >>> unrepr("123")
    123
    >>> unrepr("'foo\\nbar'")
    'foo\\nbar'
    >>> unrepr("[]")
    []
    >>> unrepr("['foo', 'bar']")
    ['foo', 'bar']
    >>> unrepr("()")
    ()
    >>> unrepr("(1,)")
    (1,)
    >>> unrepr("('foo', 'bar')")
    ('foo', 'bar')
    >>> unrepr("['foo', 123, []]")
    ['foo', 123, []]
    >>> unrepr('True')
    True
    >>> unrepr('[True, False, None]')
    [True, False, None]
    """
    def skipspaces(s, i):
        while i < len(s) and s[i] == ' ':
            i += 1
        return i

    def advance(s, i, expected):
        if not s.startswith(expected, i):
            raise ValueError('expected %r, found %r at pos %d'
                             % (expected, s[i], i))
        return i + len(expected)

    def parse(s, i):
        if i >= len(s):
            raise ValueError('nothing left to parse')
        if s[i] == '[':
            return parselist(s, i)
        if s[i] == '(':
            return parsetuple(s, i)
        if s[i] == '"' or s[i] == "'":
            return parsestr(s, i)
        if s[i].isdigit():
            return parseint(s, i)
        if s.startswith('True', i):
            return True, i+4
        if s.startswith('False', i):
            return False, i+5
        if s.startswith('None', i):
            return None, i+4
        raise ValueError('cannot parse %r' % s)

    def parselist(s, i):
        result = []
        i += 1 # advance past [
        while i < len(s):
            i = skipspaces(s, i)
            if s[i] == ']':
                break
            elem, i = parse(s, i)
            result.append(elem)
            i = skipspaces(s, i)
            if s[i] == ']':
                break
            i = advance(s, i, ',')
        return result, i+1

    def parsetuple(s, i):
        result = []
        i += 1 # advance past (
        istuple = True
        while i < len(s):
            i = skipspaces(s, i)
            if s[i] == ')':
                break
            elem, i = parse(s, i)
            result.append(elem)
            i = skipspaces(s, i)
            if s[i] == ')':
                istuple = len(result) != 1
                break
            i = advance(s, i, ',')
        if istuple:
            result = tuple(result)
        else: # not really a tuple after all
            result = result[0]
        return result, i+1

    def parsestr(s, i):
        quote = s[i]
        j = i+1
        while j < len(s) and s[j] != quote:
            if s[j] == '\\':
                j += 2
            else:
                j += 1
        return s[i+1:j].decode('string-escape'), j+1

    def parseint(s, i):
        j = i+1
        while j < len(s) and s[j].isdigit():
            j += 1
        return int(s[i:j]), j

    s = s.strip()
    try:
        result, i = parse(s, 0)
    except ValueError, e:
        raise ValueError('parse error "%s" while parsing %s' % (e, s))

    if i < len(s):
        raise ValueError('could not parse %r' % s[i:])
    return result

if __name__ == "__main__":
    import doctest
    doctest.testmod(optionflags=doctest.REPORT_NDIFF)
