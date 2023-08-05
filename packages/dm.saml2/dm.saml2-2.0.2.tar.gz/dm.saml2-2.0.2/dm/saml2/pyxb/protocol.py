from pyxb.bundles.saml20.protocol import *

from dm.saml2.signature import add_signature_verification
from dm.saml2.util import enhance, Picklable

from assertion import _StandardSignable



class _RequestAbstractTypeExtension(_StandardSignable, Picklable):
  """A mix in class to provide extensions for ``RequestAbstractType``."""

class _ResponseTypeExtension(_StandardSignable):
  """A mix in class to provide extensions for ``StatusResponseType``."""

  PREFIX = "urn:oasis:names:tc:SAML:2.0:status:"

  def set_status(self, code, message=None, detail=None):
    """set the ``Status`` element.

    *code* is either a string or a sequence of strings or a ``StatusCodeType``
    instance. It specifies
    the content of the nested ``StatusCode`` elements. If a
    string does not contain ``:``, then *PREFIX* is prepended.

    *message* is a string and specifies the ``StatusMessage``.

    *detail* must be a ``StatusDetailType`` instance.
    """
    if not isinstance(code, StatusCodeType):
      if isinstance(code, (str, unicode)): code = code,
      code, css = None, code
      for cs in css:
        if ':' not in cs: cs = self.PREFIX + cs
        c = StatusCode(Value=cs)
        if code is None: parent = code = c
        else: parent.StatusCode = c; parent = c
    # ``code`` is not a ``StatusCodeType`` instance
    self.Status = Status(code, message, detail)

  def set_success(self):
    """set success status."""
    self.set_status('Success')

  def set_exception(self, exc):
    """set a status for *exc*.

    *exc* is an unexpected exception and therefore classified as
    responder failure. Exceptions due to client failures should
    not be handled by this method.
    """
    msg = '%s: %s' % (exc.__class__.__name__, str(exc))
    self.set_status('Responder', msg)

##  # first level status codes
##  Success
##  Requester
##  Responder
##  VersionMismatch

##  # second level status codes
##  AuthnFailed
##  InvalidAttrNameOrValue
##  UnkownAttrProfile
##  InvalidNameIDPolicy
##  NoAuthnContext
##  NoAvailableIDP
##  NoPassive
##  PartialLogout
##  # there are more, but we do not expect we will use them

enhance('StatusResponseType', _ResponseTypeExtension)
enhance('ResponseType')

# assertion request and assertion query
enhance('AssertionIDRequestType', _RequestAbstractTypeExtension)
enhance('AuthnQueryType', _RequestAbstractTypeExtension)
enhance('AttributeQueryType', _RequestAbstractTypeExtension)
enhance('AuthzDecisionQueryType', _RequestAbstractTypeExtension)

# authentication request
enhance('AuthnRequestType', _RequestAbstractTypeExtension)

# artifact resolution
enhance('ArtifactResolveType', _RequestAbstractTypeExtension)
enhance('ArtifactResponseType', _ResponseTypeExtension)

# name id management
enhance('ManageNameIDRequestType', _RequestAbstractTypeExtension)

# single logout
enhance('LogoutRequestType', _RequestAbstractTypeExtension)

# name id mapping
enhance('NameIDMappingRequestType', _RequestAbstractTypeExtension)
enhance('NameIDMappingResponseType', _ResponseTypeExtension)



add_signature_verification()

