# coding: utf-8

instance = None


class Bread(object):

    def __init__(self, *a, **kw):
        import ipdb; ipdb.set_trace()
        print instance

    def set_instance(self, v):
        instance = v
