# Copyright (C) 2010 by Dr. Dieter Maurer <dieter@handshake.de>; see 'LICENSE.txt' for details
"""Support for the http redirect binding.

The redirect binding allows to transport an SAML2 message
(request or response) via query string parameters in an HTTP ``GET``
request, usually used via an HTTP redirect.

Due to space considerations, the transported message usually
cannot contain a signature. The redirect binding supports
a restricted form of signature for the message's top level.
The implementation here provides the parameters for this signature
support but does not (yet) really implements signing and verification.
Such an implementation requires extension of ``PyXMLsec`` (the
Python binding to the xml security library) or a separate implementation
of the signing and verification algorithms.
"""

from zlib import compress, decompress
from urllib import urlencode
from cgi import parse_qs

from dm.saml2.pyxb.protocol import ResponseType


def encode(url, message, relay_state=None, context=None):
  """encode *message* and *relay_state* as query parameters for *url*; return the extended url.

  *message* is a ``PyXB`` binding object representing either a request or
  response.

  *relay_state* is a string, usually an opaque state handle obtained from
  a relay state manager. In cases, where an unsolicited response is
  sent, *relay_state* can indicate in some way a target.

  *context* is a signature context used for signing (not yet implmented).
  """

  # place of/for '?'
  url = str(url) # might be unicode
  qi = url.find('?')
  if qi < 0: qi = len(url)
  params = dict()
  if relay_state: params['RelayState'] = relay_state
  if message.Signature is not None:
    # Note: we must ensure ``message.Destination`` is set
    message.Destination = url[:qi]
    raise NotImplementedError("signature support not yet implemented")
  # hope ``compress`` really implements the deflate algorithm as of RFC1951
  msg = compress(message.toxml(root_only=True)).encode('base64')
  # remove whitespace
  msg = ''.join(msg.split())
  params[isinstance(message, ResponseType) and 'SAMLResponse' or 'SAMLRequest'] \
                             = msg
  qs = urlencode(params)
  if qi == len(url): url += '?' # '?' not yet present
  if qi != len(url)-1 and not url.endswith('&'): url += '&'
  url += urlencode(params)
  return url


def decode(url, context=None):
  """decode *url* and return pair *saml* and *relay_state*.

  *url* is the complete url, including the query string (necessary
  for signature verification).

  *context* is used for signature verification (not yet implemented).
  """
  params = parse_qs(url[url.index('?')+1:]) # maps param to list of values
  if 'Signature' in params:
    raise NotImplementedError('signature support not yet implemented')
  relay_state = params.get('RelayState')
  if relay_state is not None: relay_state = relay_state[0] # unlistify
  msg = (params.get('SAMLRequest') or params.get('SAMLResponse'))[0]
  return decompress(msg.decode("base64")), relay_state  

