# Copyright (C) 2010-2012 by Dr. Dieter Maurer <dieter@handshake.de>; see 'LICENSE.txt' for details
"""Utilities"""
from sys import _getframe, modules

def get_frame_globals(level):
  """the globals at frame level *level* above us."""
  fr = _getframe(level + 1)
  return fr.f_globals


def enhance(name, extension=None):
  r"""look up *name* in the callers globals and enhance it by *extension*.

  If *extension* is not specified, it is looked up in the callers
  globals under ``_``\ *name*\ ``Extension``.

  The enhanced object is supposed to behave similar to a class.
  Enhancement happens by defining a new class with *extension*
  as first ``__bases__`` element.
  """
  mdict = get_frame_globals(1)
  if extension is None: extension = mdict['_%sExtension' % name]
  base = mdict[name]
  ec = mdict[name] = type(base)(name, (extension, base) + base.__bases__, {})
  ec.__module__ = mdict["__name__"] # ensure picklability
  base._SetSupersedingClass(ec)


class Picklable(object):
  """Mixin class to implement pickling via XML serialization.

  Note: PyXB objects should be picklable by itself, but apparently
  some literals (at least `dateTime`) have problems.

  Note: Our pickling is not completely faithfull. We loose signature
  verification information (but this could be fixed, if necessary).
  """
  def __getstate__(self): return self.toxml(root_only=True)
  def __setstate__(self, state):
    mod = modules[self.__class__.__module__]
    cfd = mod.CreateFromDocument
    if getattr(cfd, "signature_enhanced", False):
      obj = cfd(state, suppress_verification=True)
    else: obj = cfd(state)
    self.__dict__.update(obj.__dict__) # quite brutal


# Auxiliary functions to better access PyXB objects.
def children(obj, none_ok=False):
  """the children of *obj* as sequence of `ElementUse`, value pairs.

  If *none_ok*, all children are reported; otherwise, only children
  with a value different from None.
  """
  return [(eu, eu.value(obj))
          for eu in obj._ElementMap.values()
          if none_ok or eu.value(obj) is not None
          ]

def child_items(obj, none_ok=False):
  """the children of *obj* as sequence of attr, value pairs."""
  return [(eu.id(), value) for (eu, value) in children(obj, none_ok)]

def child_values(obj, none_ok=False):
  """the children of *obj* as sequence of values."""
  return [ci[1] for ci in children(obj, none_ok)]

def child_ids(obj, none_ok=False):
  """the children of *obj* as sequence of ids."""
  return [ci[0].id() for ci in children(obj, none_ok)]



##############################################################################
## Authentication class support

SAML_CLASS_PREFIX = "urn:oasis:names:tc:SAML:2.0:ac:classes:"

def normalize_class(c):
  """normalize authentication context class reference *c*."""
  if ":" not in c: c = SAML_CLASS_PREFIX + c
  return c

# the authentication classes supported so far
SAML_CLASSES = (
  normalize_class("Password"),
  normalize_class("PasswordProtectedTransport"),
  )

SAML_CLASS_STRENGTH = {
  normalize_class("Password") : 100,
  normalize_class("PasswordProtectedTransport") : 200,
  }

def compare_classes(c1, c2):
  """compare the strength of classes *c1* and *c2*.

  return None if this is impossible; otherwise, -1, 0 or 1.
  """
  if c1 == c2: return 0
  if c1 not in SAML_CLASS_STRENGTH or c2 not in SAML_CLASS_STRENGTH: return
  return cmp(SAML_CLASS_STRENGTH[c1], SAML_CLASS_STRENGTH[c2])



##############################################################################
## Name id support
NAMEID_FORMAT_PREFIX = "urn:oasis:names:tc:SAML:2.0:nameid-format:"

def normalize_nameid_format(nidf):
  """normalize nameid format *nidf*."""
  if ":" not in nidf: nidf = NAMEID_FORMAT_PREFIX + nidf
  return nidf

NAMEID_FORMATS = (
  normalize_nameid_format("emailAddress"),
  normalize_nameid_format("X509SubjectName"),
  normalize_nameid_format("WindowsDomainQualifiedName"),
  normalize_nameid_format("kerberos"),
  normalize_nameid_format("entity"),
  normalize_nameid_format("persistent"),
  normalize_nameid_format("transient"),
  # moved to the end of the list, to give more specific formats better exposure
  normalize_nameid_format("unspecified"),
  # not a first class nameid format -- usuably only as part of `NameIDPolicy`
  #normalize_nameid_format("encrypted"),
  )


##############################################################################
## attribute support

ATTRNAME_FORMAT_PREFIX = "urn:oasis:names:tc:SAML:2.0:attrname-format:"

def normalize_attrname_format(anf):
  """normalize attribute name format *anf*."""
  if ":" not in anf: anf = ATTRNAME_FORMAT_PREFIX + anf
  return anf

ATTRNAME_FORMATS = (
  normalize_attrname_format("unspecified"),
  normalize_attrname_format("uri"),
  normalize_attrname_format("basic"),
  )


##############################################################################
## XML-schema basic type conversion

# impossible due to local/global import confusion
#import pyxb.binding.datatypes as xs
xs = __import__("pyxb.binding.datatypes", {}, {}, ["__name__"])

XSCHEMA_BASE_TYPES = (
  "anyURI", "base64Binary", "boolean", "date", "dateTime", "double",
  "duration", "float", "int", "string",
  )

def xs_convert_to_xml(ty, value, element=None):
  """convert Python *value* to XML using base type *ty*.

  If *element* put into such an element -- otherwise return the
  PyXB basic binding of *value* corresponding to *ty*.

  If *value* is a list or tuple, convert its elements and return
  a list.
  """
  if value is None: return element is not None and element() or None
  if isinstance(value, (list, tuple)):
    # Note: we assume to have only one sequence level
    return [xs_convert_to_xml(ty, v, element) for v in value]
  return getattr(xs, ty)(value, _element=element)

def xs_convert_from_xml(xml, is_seq=False):
  """convert *xml* to Python.

  *xml* is the PyXB binding of an element with simple content.

  As XML-Schema often uses lists to represent optional values,
  *is_seq* controls whether the result should be a list or
  whether the convertion should try to convert to a single value
  (`None`, if the list is empty; the first component if the list has
  a single value).
  """
  if xml is None: return
  if is_seq:
    # *xml* must be a sequence, too; crash, if this is not the case
    return [xs_convert_from_xml(e) for e in xml]
  if isinstance(xml, (list, tuple)):
    if not xml: return
    if len(xml) == 1: return xs_convert_from_xml(xml[0])
    raise TypeError("cannot convert list to single value")
  # most PyXB types are perfect Python values -- only a few types require conversion
  if isinstance(xml, xs.dateTime): return pyxb_to_datetime(xml)
  # some types may still be missing
  return xml



##############################################################################
## Wrapper

class Printer(object):
  """Wrapper to print a PyXB object."""

  def __init__(self, obj): self._obj = obj

  def __str__(self): return self._obj.toxml(root_only=True)
  __repr__ = __str__



##############################################################################
## Workaround for PyXB weaknesses

def pyxb_to_datetime(pdt):
  """PyXB datetime values are not picklable -- convert to "normal" `datetime`."""
  if pdt is None: return
  from datetime import datetime
  return datetime(pdt.year, pdt.month, pdt.day, pdt.hour, pdt.minute, pdt.second, pdt.microsecond)
