# -*- coding: utf-8 -*-


class GroupIterator(object):
    """
    Instance of GroupIterator can be iterated over by groups of
    'objects', each of size 'group_size'.
    """
    def __init__(self, objects, group_size):
        self.objects = list(objects)
        self.group_size = group_size

    def __nonzero__(self):
        return bool(self.objects)

    def __iter__(self):
        pos = 0
        size = len(self.objects)
        group_size = self.group_size
        while pos < size:
            yield self.objects[pos:pos + group_size]
            pos += group_size
