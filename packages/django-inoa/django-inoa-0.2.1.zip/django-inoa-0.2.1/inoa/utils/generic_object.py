# -*- coding: utf-8 -*-

class GenericObject(object):
    """
    An object class that behaves similarly to JavaScript's objects:
    each named parameter in the constructor becomes an attribute in the instance.
    
    Examples:
    x = GenericObject(mydict)
    y = GenericObject(**{'name': 'Howard', 'count': 5})
    y.count ==> 5
    """
    def __init__(self, **entries): 
        self.__dict__.update(entries)
