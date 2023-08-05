# Copyright (C) 2010-2012 by Dr. Dieter Maurer <dieter@handshake.de>; see 'LICENSE.txt' for details
"""Metadata support.

For most SAML2 operations metadata describing important aspects
of a set of SAML2 authorities is vital.

This module defines base classes to manage and access SAML2 related
metadata.

At its center is the ``MetadataRepository``. It behaves like
a container for entity references, called ``Entity``.
Each entity reference corresponds to an SAML2 authority and
knows how to obtain metadata relevant for this authority.
Thus, the entity reference encapsulates the necessary configuration
to access its authorities metadata.

A ``MetadataRepository`` can be asked for current metadata for
its known authorities; access can be either via entity id or its SHA-1
hash (used by SAML2 for some purposes).

Metadata for a specific entity is described by the class
``EntityMetadata``. This class can handle multiple metadata sets
for a single entity valid for different time ranges. This
complexity was mainly introduced to facilitate "key rollover".
The class knows how to fetch new metadata (via use of ``Entity``)
and can continue to use outdated metadata when this fails.

For efficiency reasons, ``MetadataRepository`` uses an externally
controllable store, used by ``EntityMetadata`` for its
storage needs. It must be able to store arbitrary mappings
from ``unicode`` to picklable objects. If this store is persistent,
metadata might be retained across process lifetimes (depends
on other requirements as well).
"""
from logging import getLogger
from datetime import datetime, timedelta
from urllib2 import urlopen


logger = getLogger(__name__)


class MetadataFetchError(Exception):
  """Exception to report the failure fetching metadata.

  Its constructor expects two arguments, the entity id
  and an exception.
  """
  def __repr__(self):
    id, exc = self.args
    return 'MetadataFetchError for %s: %s' % (id, exc)

  __str__ = __repr__


class EntityBase(object):
  """abstract entity reference base class.

  Encapsulates the relevant configuration data to identify
  an SAML2 authority and access its current metadata description.
  """

  id = None # entity id, definied in ``__init__``

  # "dm.saml2" assumes specific keys (rather than certificate chains founded
  #   in a set of trusted certificates with subsequent subject verification)
  #   for its verifications.
  #   Usually, such keys would be made known via metadata exchange.
  #   This obviously poses a chicken egg problem when signatures
  #   must be verified for a metadata exchange itself.
  #   The following attribute allows to suppress the signature check
  suppress_verification = True

  def __init__(self, id, *args, **kw):
    # id's are hashed; thus, they should be bytes (not unicode)
    super(EntityBase, self).__init__(*args, **kw)
    self.id = str(id)

  def get_metadata(self):
    """fetch metadata for this entity (as Python object)."""

    from dm.saml2.pyxb.metadata import CreateFromDocument
    # Note: the unrestricted "try: ... except: ..." is nasty
    #  but there are too many potential exceptions that
    #  an enumeration would be difficult
    try:
      return CreateFromDocument(
        self.get_metadata_document(),
        suppress_verification=self.suppress_verification,
        )
    except Exception, e:
      logger.exception('failed to get metadata for %s', self.id)
      raise MetadataFetchError(self.id, e)

  def get_metadata_document(self):
    """fetch metadata for this entity (as XML document)."""
    raise NotImplementedError('``get_metadata_document`` must be implemended by derived classes')


class EntityByUrl(EntityBase):
  """Entity reference obtaining metadata from a well known internet url.

  This is a simple class. We might want significantly more transport control,
  e.g. proxy, authentication, ...
  """

  def __init__(self, id, url, *args, **kw):
    super(EntityByUrl, self).__init__(id, *args, **kw)
    self.url = url

  def get_metadata_document(self):
    return urlopen(self.url).read()



class EntityMetadata(object):
  """Entity proxy providing access to the entities metadata.

  The class manages a sequence of metadata sets -- essentially
  to facilitate key rollover.

  The class automatically tries to fetch new metadata when
  existing metadata lost its validity. However, it is ready
  to continue to use outdated metadata when fetching a new one fails.

  Under normal conditions, it maintains a single metadata set.
  However, ``fetch_metadata`` can be used, to fetch a current metadata set,
  even when there are valid ones. This may facilitate key rollover.

  The class uses an externally provided *store* (a mapping) to
  store its metadata.
  """
  # to be overridden by derived classes (to facilitate persistency)
  SEQUENCE_CLASS = list


  def __init__(self, entity, store, default_validity):
    self.entity, self.store, self.default_validity = entity, store, default_validity
    self.id = entity.id


  def _get_metadata_sets(self, exc=False):
    """the currently known metadata sets;

    *exc* requests an exception when no set is available.
    """
    store = self.store; eid = self.id
    modified = False
    sets = store.get(eid)
    if sets is None:
      sets = self.SEQUENCE_CLASS(); modified = True
    # find sets no longer valid
    #  Note: sets is a sequence, ordered by "most recent" first
    now = datetime.now()
    invalid = [] # list of indexes for no longer valid entries
    for i, s in enumerate(sets):
      if now > s.validUntil: invalid.append(i)
    if len(invalid) == len(sets) or not len(sets):
      # no valid sets -- try to fetch a new one
      s = self._fetch(exc)
      if s is not None: sets[:] = (s,)
      else:
        # try to keep the most recent one
        sets = sets[:1]
      modified = True
    elif len(invalid):
      # invalidate no longer valid entries
      invalid.reverse()
      for i in invalid: del sets[i]
      modified = True

    # support for ZODB persistency
    if modified: store[eid] = sets
    return modified, sets

  def get_metadata_sets(self, exc=False):
    return self._get_metadata_sets(exc)[1]


  def get_recent_metadata(self):
    # can be optimized
    return self.get_metadata_sets(True)[0]


  def fetch_metadata(self, clear_old=False):
    """fetch a new metadata set.

    Without explicit calls of this method, we have at most 1 set
    as we fetch a new set only when all others became invalid.

    The method would be called when an entity reports changes
    to its metadata.

    Without *clear_old*, certificates defined by older sets
    will still be used (to facilitate key rollover).
    """
    sets = self.get_metadata_sets()
    sets.insert(0, self._fetch())
    if clear_old: del sets[1:]
    self.store[self.id] = sets


  def clear_metadata(self):
    """delete the stored metadata."""
    self.store[self.id] = self.SEQUENCE_CLASS()


  def get_role_descriptor(self, role,
                          protocol='urn:oasis:names:tc:SAML:2.0:protocol'
                          ):
    """the (first) role descriptor supporting *role* and *protocol*, or ``None``.

    According to the spec, their should be at most one such descriptor.

    Roles are represented by short strings: ``idpsso`` (identity provider),
    ``spsso`` (service provider), ``authn`` (authentication authority),
    ``attribute`` (attribute authority) and ``pdp`` (policy decision
    point).
    """
    return select_role_descriptor(self.get_recent_metadata(),
                                  role, protocol
                                  )

  def get_role_certificates(self, role,
                            use=None,
                            protocol='urn:oasis:names:tc:SAML:2.0:protocol'
                            ):
    """select all certificates used by *role*.

    To facilitate key rollover, older metadata sets are used as well
    to determine keys.

    See ``get_role_descriptor`` for the coding of *roles*.
    """
    certs = []
    for s in self.get_metadata_sets():
      select_role_certificates(select_role_descriptor(s, role, protocol),
                               use, certs
                               )
    return certs

  def _fetch(self, exc=True):
    """fetch current metadata.

    If *exc*, raise exceptions when the metadata cannot be fetched;
    otherwise, return ``None``.
    """
    eid = self.id
    try: s = self.entity.get_metadata()
    except MetadataFetchError:
      if exc: raise
      return
    else:
      # fetch successfull
      if eid != s.entityID:
        # looks like metadata describing someone else
        if not exc: return
        raise MetadataFetchError(
          eid,
          ValueError('entityID mismatch: %s != %s' % (eid, s.entityID))
          )
      # we do not check that metadata is authentic

      # the standard requires that either ``validUntil`` or ``cacheDuration``
      #   is defined -- but not all SAML2 entities follow the standard
      #   normalize to always provide ``validUntil``
      if s.validUntil is None:
        cd = s.cacheDuration or self.default_validity
        s.validUntil = datetime.now() + cd
    return s


role2element = dict(
  idpsso='IDPSSODescriptor',
  spsso='SPSSODescriptor',
  authn='AuthnAuthorityDescriptor',
  ap='AttributeAuthorityDescriptor',
  pdp='PDPDescriptor',
  )

def select_role_descriptor(md, role, protocol):
  """select the first descriptor from metadata *md* supporting *role* and *protocol*.

  See ``EntityMetadata.get_role_descriptor`` for further details.
  """
  for r in getattr(md, role2element[role]):
    if protocol in r.protocolSupportEnumeration: return r


def select_role_certificates(rd, use, certs):
  """extend *certs* (a list) by certificates used by role descriptor *rd*.

  Note: *rd* may be ``None``.
  """
  if rd is None: return
  for kd in rd.KeyDescriptor:
    if use is None or kd.use is None or use == kd.use:
      ki = kd.KeyInfo
      for x509 in getattr(ki, 'X509Data', ()):
        cert = getattr(x509, 'X509Certificate', None)
        if cert is not None:
          # `cert` contains a certificate chain. We use only the first one
          certs.append(cert[0])


class MetadataRepository(object):
  """``Entity`` container managing a set of entity references.

  Provides access to ``EntityMetadata``, either by id or by its SHA-1 hash.
  """

  # can be overridden by derived classes -- e.g. to provide persistency
  INTERNAL_STORAGE_CLASS = dict
  METADATA_STORAGE_CLASS = dict
  METADATA_CLASS = EntityMetadata

  default_validity = timedelta(10, 0, 0) # 10 days

  def __init__(self, default_validity=None):
    self._entities = self.INTERNAL_STORAGE_CLASS()
    self._metadata = self.INTERNAL_STORAGE_CLASS()
    self._metadata_storage = self.METADATA_STORAGE_CLASS()
    if default_validity is not None: self.default_validity = default_validity
  

  def add_entity(self, entity):
    """add new *entity*."""
    ents = self._entities; eid = entity.id
    if eid in ents: raise ValueError('entity already managed: %s' % id)
    self._entities[eid] = entity
    self._entities = self._entities # to facilitate ZODB persistency

  def list_entities(self):
    # Note: when entities are modified, it might become necessary
    #  to invalidate the associated metadata
    return self._entities.values() # should we sort them?

  def get_entity(self, id, default=None):
    """the entity *id* or *default*."""
    return self._entities.get(id, default)

  def del_entity(self, eid):
    """delete entity identified by *eid* (if present)."""
    if eid in self._entities: del self._entities[eid]
    if eid in self._metadata: del self._metadata[eid]

  def metadata_by_id(self, eid):
    md = self._metadata.get(eid)
    if md is None:
      md = self._metadata[eid] = self.METADATA_CLASS(
        self._entities[eid], self._metadata_storage, self.default_validity
        )
      self._metadata = self._metadata # to facilitate ZODB persistency
    return md


  def metadata_by_hash(self, sha_hash):
    h2id = self._get_hash2id()
    if sha_hash not in h2id: h2id = self._get_hash2id(True)
    return metadata_by_id(h2id[sha_hash])


  _hash2id = None

  def _get_hash2id(self, rebuild=False):
    h2id = self._hash2id
    if h2id is None or rebuild:
      from sha import sha
      h2id = self._hash2id = dict((sha(eid), eid) for eid in self._entities)
    return h2id
