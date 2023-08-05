import re

from formalize.core import Undefined, ErrorList

def dict2list(structure, base, fillgaps, maxsize):
    """
    >>> dict2list({1: 'x', 2: 'y', 4: 'z', 5: { 1: 'a', 2: 'b' }}, 1, True, 1000)
    ['x', 'y', Undefined, 'z', {1: 'a', 2: 'b'}]
    """
    l = sorted(structure.items())
    if len(l) == 0:
        return []
    keys, values = zip(*l)
    if not fillgaps:
        return values
    last_index = keys[-1]
    if last_index - base + 1 > maxsize:
        raise Exception("List size too large (requested size is %d)" % (last_index - base + 1))
    return [ structure.get(index, Undefined) for index in range(base, last_index + 1) ]


class Unpacker(object):
    """
    Return an unpacked hierarchy of lists and dictionaries given a flattened
    data structure, typically one resulting from an HTML form submission.

        >>> data = {
        ...     'person#0.name': 'eric',
        ...     'person#0.occupation#0' : 'ordinary schoolboy',
        ...     'person#0.occupation#1' : 'superhero',
        ...     'person#1.name': 'mr benn',
        ...     'person#1.occupation#0' : 'businessman',
        ...     'person#1.occupation#1' : 'astronaut',
        ...     'person#1.occupation#2' : 'balloonist',
        ... }
        >>> unpacker = Unpacker()
        >>> unpacker(data) == {
        ...     'person' : [
        ...         {'name': 'eric', 'occupation': ['ordinary schoolboy', 'superhero']},
        ...         {'name': 'mr benn', 'occupation': ['businessman', 'astronaut', 'balloonist']}
        ...     ],
        ... }
        True
    """

    def __init__(
        self,
        list_separator='#',
        dict_separator='.',
        list_base=0,
        list_maxsize=1000,
        list_fillgaps=True
    ):
        self.list_separator = list_separator
        self.dict_separator = dict_separator
        self.list_base = list_base
        self.list_maxsize = list_maxsize
        self.list_fillgaps = list_fillgaps

    def __call__(self, data):

        # Hold the unpacked data structure as we build it up
        unpacked = {}

        # Initially construct lists as dicts keyed on integers, as we won't get
        # the keys through in numerical order and there may be missing keys.
        lists = []

        for item in data:

            current = unpacked
            context = {None: unpacked}, None
            path = self.dict_separator + item
            path = re.split('(%s|%s)' % (re.escape(self.dict_separator), re.escape(self.list_separator)), path)[1:]

            while path:
                separator = path.pop(0)
                if separator == self.dict_separator:
                    current = context[0].setdefault(context[1], {})
                    key = path.pop(0)
                elif separator == self.list_separator:
                    new = {}
                    current = context[0].setdefault(context[1], new)
                    if current is new:
                        lists.append(context)
                    key = int(path.pop(0))
                context = current, key

            context[0][context[1]] = data[item]

        self.convert_lists(lists)
        return unpacked

    def convert_lists(self, lists):
        for parent, key in lists:
            parent[key] = dict2list(
                parent[key], self.list_base, self.list_fillgaps, self.list_maxsize
            )

    def repack_errors(self, errors, prefix=''):
        """
        Given a nested error list (from a ValidationError), return a flattened
        list with the same keys as would have been unpacked from the form
        submission.

        Synopsis::

            >>> v = Unpacker(list_separator='-', dict_separator='$', list_base=0)
            >>> v.repack_errors([
            ...     ('person', ErrorList([
            ...         (1, ErrorList([
            ...                 ('name', 'Value expected'),
            ...                 ('question', ErrorList([
            ...                     (3, 'Answer was incorrect')
            ...                 ]))
            ...         ]))
            ...     ]))
            ... ])
            [('person-1$name', 'Value expected'), ('person-1$question-3', 'Answer was incorrect')]

        """
        packed = []
        for name, error in errors:
            if isinstance(name, int):
                name = "%s%s%d" % (prefix, self.list_separator, name + self.list_base)
            else:
                name = "%s%s%s" % (prefix, self.dict_separator, name)

            if isinstance(error, ErrorList):
                packed.extend(self.repack_errors(error, name))
            else:
                packed.append((name[1:], error))
        return packed

default_unpacker = Unpacker()
