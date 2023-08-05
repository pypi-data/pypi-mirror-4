class nihil(object):
    def __getattribute__(self, method):
        return self

    def __call__(self, *args, **kwargs):
        return self

    def __bool__(self):
        return False
    __nonzero__=__bool__

    def __iter__(self):
        raise StopIteration
        yield

    def __repr__(self):
        return u"nihil()"

nihil = nihil()
