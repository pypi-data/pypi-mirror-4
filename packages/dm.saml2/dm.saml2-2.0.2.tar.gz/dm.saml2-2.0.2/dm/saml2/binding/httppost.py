# Copyright (C) 2010 by Dr. Dieter Maurer <dieter@handshake.de>; see 'LICENSE.txt' for details
"""Support for the http post binding.

The post binding allows to transport an SAML2 message
(request or response) via parameters in an HTTP ``POST``
request, usually used via an HTML form submission, either explicitely
or automatically via Javascript.
"""
from cgi import escape

from dm.saml2.pyxb.protocol import ResponseType


def encode(message, relay_state=None):
  """encode *message* and *relay_state*, returning a dict of parameters.

  *message* is a ``PyXB`` binding for an SAML request or response.
  """
  params = dict()
  if relay_state is not None: params['RelayState'] = relay_state
  params[isinstance(message, ResponseType) and 'SAMLResponse' or 'SAMLRequest'] = \
                             message.toxml().encode('base64')
  return params


def as_controls(params):
  """encode *params* (a dict) a hidden form controls (an XHTML fragment)."""
  cl = []
  for pn, pv in params.iteritems():
    cl.append('<input name="%s" type="hidden" value="%s" />'
              % (escape(pn, True), escape(pv, True))
              )
  return ''.join(cl)


def as_form(params, action, submit=None, name=None):
  """encode *params* (a dict) as a simple form (an XHTML fragment).

  *action* (an URL) specifies the form action. 

  *submit* specifies the submit button label. It usually will be a
  unicode value. In this case, the result will be unicode as well.

  *name* can be used to give the form a name.
  """
  name = name and 'name="%s"' % escape(name, True) or ''
  sv = submit and 'value="%s"' % escape(submit, True) or ''
  return (
    '<form %s action="%s" method="POST">%s<input type="submit" %s /></form>'
    % (name, action, as_controls(params), sv)
    )


def decode(params):
  """decode (dict) *params* into a pair *saml*, *relay_state*.

  ``decode`` is (almost) the inverse of ``encode`` (it returns
  an saml document rather than a `PyXB` object.
  """
  return ((params.get('SAMLRequest') or params.get('SAMLResponse'))
          .decode('base64'),
          params.get('RelayState')
          )



