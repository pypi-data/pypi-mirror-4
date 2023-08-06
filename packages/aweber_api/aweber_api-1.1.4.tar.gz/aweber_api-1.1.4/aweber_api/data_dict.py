"""
This class is used to propagate changes to a parent item. This is
used for when an AWeberEntry has a dict item as on of the attributes
in _data.  When changes are made to an item in this data dict, __setattr__
gets called on the parent with the new state of the dict.
"""
class DataDict(object):

    def __init__(self, data, name, parent):
        self.parent = parent
        self.data = data
        self.name = name

    def __getitem__(self, key):
        return self.data[key]

    def __setitem__(self, key, value):
        self.data[key] = value
        self.parent.__setattr__(self.name, self.data)
