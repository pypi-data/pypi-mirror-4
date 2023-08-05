# Copyright (C) 2010 by Dr. Dieter Maurer <dieter@handshake.de>; see 'LICENSE.txt' for details
"""Utilities"""
from time import time

from dm.saml2.uuid import uuid

class Store(object):
  """class to implement storage of objects under ids.

  Instances of this class are used to manage relay states and
  artifacts. They use a mapping store for the actual storage.

  Artifact management stores pairs consisting of a timestamp (a float)
  and an XML document. Relay state management stores whatever the
  application stores. The used mapping store must be able to store
  accordingly.
  """
  def __init__(self, mapping_store):
    self._store = mapping_store

  def store(self, obj):
    """store *obj* and return an id to retrieve it later."""
    id = self._makeid()
    self._store[id] = obj
    return id

  def retrieve(self, id):
    """retrieve the object stored under *id* and delete."""
    obj = self._store[id]
    del self._store[id]
    return obj

  @staticmethod
  def _makeid():
    """auxiliary method to generate ids."""
    return uuid()


class UnmanagedError(Exception):
  """exception indicating that the object is not managed."""


class RelayStateManager(object):
  """manages relay states.

  delegates storage to a ``Store`` instance.
  """

  PREFIX = 'rs:' # indicates a managed relay state

  def __init__(self, store):
    self._store = store

  def store(self, state):
    return self.PREFIX + self._store.store(state)

  def retrieve(self, id):
    p = self.PREFIX
    if not id.startswith(p): raise UnmanagedError(id)
    return self._store.retrieve(id[len(p):])


class TimeoutError(KeyError):
  """exception indicating that the value timed out."""


class ArtifactManager(object):
  """manages artifacts.

  stores XML documents for a limited time.
  """
  VALID_SECONDS = 300

  id = None # associated ``SourceID``
  index = 0 # assiciated ``EndpointIndex``

  def __init__(self, store, id, index=0, valid_seconds=None):
    """*id* specifies the ``SourceID``, it should be the SHA-1 hash of the entity name,
    *index* specifies the ``EndpointIndex`` (an integer).
    *valid_seconds* specifies how long artifacts can be resolved.

    *store* must be able to store pairs float, string.
    """
    self._store = store
    assert len(id) == 20 # may compute the SHA-1 hash ourselves
    self.id = id; self.index = index
    self._valid = valid_seconds > 0 or self.VALID_SECONDS

  def store(self, doc):
    return self._store.store((time(), obj))

  def retrieve(self, id):
    ts, obj = self._store.retrieve(id)
    if time() - ts > self._valid: raise TimeoutError(id, ts)
    return obj



