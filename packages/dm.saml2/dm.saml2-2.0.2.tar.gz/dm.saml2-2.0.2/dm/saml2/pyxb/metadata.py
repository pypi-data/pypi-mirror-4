# Copyright (C) 2010-2012 by Dr. Dieter Maurer <dieter@handshake.de>; see 'LICENSE.txt' for details
"""Elementary metadata support.

We have only limited support for signing: our signature mini-framework
requires that the keyname must be derived from the signed element. Not
all defined elements support this derivation. We support signing
based on ``entityID`` for elements that have this.

Due to this restriction, it is difficult to exchange signature protected
new signature key information. The new information would need to be signed
with the old key, which may not be easy for the signer. Probably,
we must extend our signing framework and look for certificates
provided in ``KeyInfo`` elements.
"""


from dm.saml2.uuid import uuid
from dm.saml2.util import enhance, Picklable
from dm.saml2.signature import Signable, add_signature_verification

from pyxb.bundles.saml20.metadata import *


class _StandardSaml2Initialization(object):
  """mixin class to provide standard initialization of 'ID'."""

  def __init__(self, *args, **kw):
    if 'ID' not in kw: kw['ID'] = '_' + uuid()
    super(_StandardSaml2Initialization, self).__init__(*args, **kw)


class _StandardSignable(Signable, _StandardSaml2Initialization):
  """mixin class to provide standard initialization and signability."""

  def S_GET_KEYNAME(self): return self.entityID


class _EntityDescriptorTypeExtension(_StandardSignable, Picklable): pass

enhance('EntityDescriptorType')


class _RoleDescriptorTypeExtension(object):
  """mixin class to provide standard initialization of ``protocolSupportEnumeration``."""
  def __init__(self, *args, **kw):
    pse = kw.get('protocolSupportEnumeration')
    proto = 'urn:oasis:names:tc:SAML:2.0:protocol'
    if pse is None: pse = kw['protocolSupportEnumeration'] = proto
    if proto not in pse: kw['protocolSupportEnumeration'] += ' ' + proto
    super(_RoleDescriptorTypeExtension, self).__init__(*args, **kw)
  
enhance('IDPSSODescriptorType', _RoleDescriptorTypeExtension)
enhance('SPSSODescriptorType', _RoleDescriptorTypeExtension)
enhance('AuthnAuthorityDescriptorType', _RoleDescriptorTypeExtension)
enhance('AttributeAuthorityDescriptorType', _RoleDescriptorTypeExtension)
enhance('PDPDescriptorType', _RoleDescriptorTypeExtension)


add_signature_verification()
