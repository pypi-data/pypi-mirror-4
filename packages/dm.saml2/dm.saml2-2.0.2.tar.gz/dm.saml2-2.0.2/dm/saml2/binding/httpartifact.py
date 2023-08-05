# Copyright (C) 2010 by Dr. Dieter Maurer <dieter@handshake.de>; see 'LICENSE.txt' for details
"""Support for the http artifact binding.

The artifact binding allows to transport a small reference to an
SAML2 message, called ``artifact`` via
via parameters in an HTTP ``GET`` or ``POST``
request.

The artifact can later be derefenced via the artifact resolution
protocol.

Artifact handling is supported by an ``ArtifactManager``,
defined in module ``util``.
"""
from dm.saml2.uuid import UUID

def encode(message, manager, relay_state=None):
  """encode *message* with help of *manager*; return a params dict.

  *message* is a ``PyXB`` binding of an SAML message.

  ``urllib.urlencode`` can be used to prepare the returned params
  for use as url parameters and the ``to_controls`` and ``to_form``
  functions in ``httppost`` to use them in a form.
  """
  params = {}
  if relay_state: params['RelayState'] = relay_state
  epi = manager.index
  EndpointIndex = chr(epi//256) + chr(epi % 256)
  TypeCode='\0x0\0x4'
  uuid = UUID(manager.store(message.toxml())).bytes + '\0\0\0\0'
  RemainingArtifact = manager.id + uuid
  artifact = (TypeCode + EndpointIndex + RemainingArtifact).encode('base64')
  # strip whitespace
  artifact = ''.join(artifact.split())
  params['SAMLart'] = artifact
  return params


def parse(params):
  """parse *params* into *SourceID*, *EndpointIndex*, *artifact* and *relay_state*.

  Used by artifact receiver to obtain the information necessary
  for artifact resolution.
  """
  relay_state = params.get('RelayState')
  artifact = params['SAMLart']
  return parse_artifact(artifact)[:2] + (artifact, relay_state)


def parse_artifact(artifact):
  """parse artifact into *SourceID*, *EndpointIndex* and *MessageHandle*."""
  artifact = artifact.decode('base64')
  if artifact[:2] != '\0x0\0x4':
    raise NotImplementedError('unsupported artifact type: %s' % artifact[:2])
  EndpointIndex = ord(artifact[2])*256 + ord(artifact[3])
  SourceID = artifact[4:24]
  MessageHandle = artifact[24:]
  return EndpointIndex, SourceID, MessageHandle


def resolve(artifact, manager):
  """resolve *artifact* into associated SAML2 message using *manager*.
  Note: the SAML2 message is returned as a document (string), not as
  its ``PyXB`` binding.

  Raise ``KeyError`` in case of resolution problems.
  The ``KeyError`` may be the subtype ``dm.saml2.binding.util.TimeoutError``
  to indicate that the artifact could be resolved but had timed out.
  """
  handle = parse_artifact(artifact)[2]
  uuid = UUID(bytes=handle[:16])
  return manager.retrieve(uuid)
