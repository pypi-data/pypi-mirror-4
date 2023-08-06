# EasyObject is a really simple way to store/display some structured data.
# Just two concepts, Atoms and Sequences (of EasyObjects).  (Sequences of Atoms are just Atoms.)
# Declare your types ineriting from EasyObject.  Declare their fields simply as either of the two types.
#
# Example:
# class Example(EasyObject):
#   example_field = Atom
#   example_list = Sequence
#
# Your type now automatically has a key-value constructor and a pretty printing __str__ method.
# All the fields will be initialized to the value you provide, or None for Atoms or empty lists for Sequences.
# The objects also print themselves, with a nice indentation.

Atom = object()
Sequence = object()

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
      if field_type in (Atom, Sequence):
        default_value = (None if field_type is Atom else list())
        setattr(self, field_name, kwargs.get(field_name, default_value))

  def __str__(self):
    return self.to_string()

  def to_string(self, indent=''):
    cls = self.__class__
    rv = '%s%s\n' % (indent, self.__class__.__name__)
    for field_name in dir(self.__class__):
      field_type = getattr(self.__class__, field_name)
      if field_type is Atom:
        row = '%s  %s: %r\n' % (indent, field_name, getattr(self, field_name))
        rv += row
    for field_name in dir(self.__class__):
      field_type = getattr(self.__class__, field_name)
      if field_type is Sequence:
        for inner in getattr(self, field_name):
          rv += inner.to_string(indent=indent+'  ')
    return rv
