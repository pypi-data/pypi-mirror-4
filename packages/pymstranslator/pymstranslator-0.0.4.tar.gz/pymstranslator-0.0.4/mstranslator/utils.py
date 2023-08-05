class Constant(object):
    """Object that gets initialized with preset attributes"""
    def __init__(self, **kwargs):
        for k in kwargs:
            setattr(self, k, kwargs[k])

