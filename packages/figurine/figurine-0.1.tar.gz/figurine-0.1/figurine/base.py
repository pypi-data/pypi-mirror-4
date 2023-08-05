

class AttributeDict(dict):
    """
    Lexicon's AttributeDict
    https://github.com/bitprophet/lexicon/blob/master/lexicon/attribute_dict.py
    """

    def __getattr__(self, key):
        try:
            return self[key]
        except KeyError:
            # to conform with __getattr__ spec
            raise AttributeError(key)

    def __setattr__(self, key, value):
        if key.startswith('_'):
            object.__setattr__(self, key, value)
        else:
            self[key] = value

    def __delattr__(self, key):
        del self[key]


class FigurineType(type):
    """
    Allow both:

    f = Foo(id=1, name="lucy")

    and

    f = Foo()
    f.id = 1
    f.name = "Lucy"

    FigurineModel is the base for all of our models.
    Model def should look simple:

    class Foo(FigurineModel):
        def __init__(self):
            self.id = None
            self.name = "Lucy"

    Note, it does not look like we pass **kwargs, that's where
    this MetaClass comes in.

    It basically renames __init__ of the Model to __figurine_init__
    FigurineModel's __init__ will then always be called which 
    does take kwargs

    It will call __figurine_init__ in reverse MRO first in order 
    to build up the default values defined in the model.

    It will then, essentially, run a  dict.update() with the kwargs
    to apply the kwargs on top of the defaults.
    """
    def __new__(cls, name, bases, dct):
        if AttributeDict in bases:
            return type.__new__(cls, name, bases, dct)
        
        try:
            dct['__figurine_init__'] = dct['__init__']
            del dct['__init__']
        except KeyError:
            pass 
        
        return type.__new__(cls, name, bases, dct)

class FigurineModel(AttributeDict):

    __metaclass__ = FigurineType

    def __init__(self, *args, **kwargs):
        
        # why [:-4] ?
        # the last 4 items in the MRO will be:
        # 1) <class 'figurine.base.FigurineModel'>, 
        # 2) <class 'figurine.base.AttributeDict'>, 
        # 3) <type 'dict'>, 
        # 4) <type 'object'>
        # and we don't care about those for 
        # building up our model
        order = reversed(self.__class__.__mro__[:-4])
        map(lambda x: x.__figurine_init__(self), order)
        
        super(FigurineModel, self).__init__(**kwargs)