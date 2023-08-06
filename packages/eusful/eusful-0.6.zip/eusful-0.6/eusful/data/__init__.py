# EasyObject is a really simple way to store/display some structured data.
# Just three concepts: Atoms, Sequences (of EasyObjects), and Dictionaries (of Atoms to EasyObjects).
# Lists of Atoms are just Atoms; dictionaries of Atoms to Atoms are just Atoms too.
# Declare your types inheriting from EasyObject.  Declare their fields simply as one of the types.
#
# Example:
# class Example(EasyObject):
#   example_field = Atom
#   example_list = Sequence
#   example_dict = Dictionary
#
# Your type now automatically has a key-value constructor and a pretty printing __str__ method.
# All the fields will be initialized to the value you provide, or defaults of None, [], {} for Atoms,
# Sequences, Dictionaries respectively.
# The objects also print themselves, with a nice indentation.

class SimpleDataType(object):

  def __init__(self, default=None):
    self._default_func = default

  @property
  def DEFAULT(self):
    return self._default_func()

# Returning the default value from a function keeps the value from getting overwritten by mistake.
Atom = SimpleDataType(lambda: None)
Sequence = SimpleDataType(lambda: [])
Dictionary = SimpleDataType(lambda: {})

class EasyObject(object):
  
  def field_names(self):
    fns = []
    for field in dir(self.__class__):
      if getattr(self.__class__, field) in (Atom, Sequence):
        fns.append(field)
    return fns

  def __init__(self, **kwargs):
    for field_name in dir(self.__class__):
      field_type = getattr(self.__class__, field_name)
      if field_type in (Atom, Sequence, Dictionary):
        setattr(self, field_name, kwargs.get(field_name, field_type.DEFAULT))

  def __str__(self):
    return self.to_string()

  def to_string(self, indent=''):
    rv = '%s%s\n' % (indent, self.__class__.__name__)
    names_types = [(field_name, getattr(self.__class__, field_name)) for field_name in dir(self.__class__)]
    for field_name, field_type in names_types:
      if field_type is Atom:
        row = '%s  %s: %r\n' % (indent, field_name, getattr(self, field_name))
        rv += row
    for field_name, field_type in names_types:
      if field_type is Sequence:
        for inner in getattr(self, field_name):
          rv += inner.to_string(indent=indent+'  ')
    for field_name, field_type in names_types:
      if field_type is Dictionary:
        row = '%s  %s: {\n' % (indent, field_name)
        rv += row
        for key, inner in getattr(self, field_name).items():
          row = '%s    %s:\n' % (indent, key)
          rv += row
          rv += inner.to_string(indent=indent+'      ')
        row = '%s  }\n' % indent
        rv += row
    return rv
