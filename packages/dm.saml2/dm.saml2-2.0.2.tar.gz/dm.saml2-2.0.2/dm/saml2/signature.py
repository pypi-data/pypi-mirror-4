# Copyright (C) 2010-2012 by Dr. Dieter Maurer <dieter@handshake.de>; see 'LICENSE.txt' for details
"""Signature (XML-DSIG) support."""

from util import get_frame_globals


class SignError(Exception):
  """an error during a signature request."""


class VerifyError(Exception):
  """an error during the verfication of a signature."""



class Signable(object):
  """Abstract mixin class supporting signing.

  Defines method ``request_signature`` which calls for signature
  creation in the ``toxml`` method.

  Note: requires ``Signable`` to be inherited before the ``pyxb`` base
  class defining ``toxml``.

  Class level configuration:

    S_ID_ATTRIBUTE
      attribute name used to determine the signature reference uri
      (default: ``'ID'``)

    S_SIGNATURE_ATTRIBUTE
      attribute name indicating the signature element to be used for signing
      (default: ``'Signature'``)

    S_GET_KEYNAME
      method to determine the keyname to used for signing.
  """

  S_ID_ATTRIBUTE = 'ID'
  S_SIGNATURE_ATTRIBUTE = 'Signature'
  S_GET_KEYNAME = None

  __signature_request = None


  def request_signature(self, keyname=None, context=None):
    """request signature in a following ``toxml``.

    *keyname* identifies the key to be used. If ``None``, it is
    determined by ``S_GET_KEYNAME``.

    *context* determines the signature context. If ``None``,
    ``default_sign_context`` is used.
    """

    self.__signature_request = _SignatureRequest(keyname, context)


  # this does not work -- must work at "DOM" level
  def _toDOM_csc(self, dom_support, parent):
    request = self.__signature_request
    if request is None:
      return super(Signable, self)._toDOM_csc(dom_support, parent)
    # prepare adding signature template
    sa = self.S_SIGNATURE_ATTRIBUTE
    s = getattr(self, sa)
    assert s is None, "signature attribute not None"
    # extend ``dom_support`` class, if necessary
    if not isinstance(dom_support, _BindingDOMSupportSignatureExtension):
      cls = dom_support.__class__
      dom_support.__class__ = type(cls)(
        cls.__name__,
        (_BindingDOMSupportSignatureExtension, cls),
        {}
        )
    dom_support.add_signature_request(request, self)
    try:
      # build the template
      from pyxb.bundles.wssplat.ds import Signature, SignedInfo, \
           CanonicalizationMethod, SignatureMethod, \
           Reference, Transforms, Transform, DigestMethod, DigestValue, \
           SignatureValue
      setattr(
        self, sa,
        Signature(
          SignedInfo(
            CanonicalizationMethod(Algorithm="http://www.w3.org/2001/10/xml-exc-c14n#"),
            SignatureMethod(Algorithm="http://www.w3.org/2000/09/xmldsig#rsa-sha1"),
            Reference(
              Transforms(
                Transform(Algorithm="http://www.w3.org/2000/09/xmldsig#enveloped-signature"),
                Transform(Algorithm="http://www.w3.org/2001/10/xml-exc-c14n#"),
                ),
              DigestMethod(Algorithm="http://www.w3.org/2000/09/xmldsig#sha1"),
              DigestValue(''),
              URI=u'#' + getattr(self, self.S_ID_ATTRIBUTE),
              ),
            ),
          SignatureValue(''),
          )
        )
      return super(Signable, self)._toDOM_csc(dom_support, parent)
    finally:
      setattr(self, sa, None) # restore signature attribute

  ###########################################################################
  # verification support
  #   SAML2 allows signatures on enclosing elements to verify its
  #   subelements as well. Even a transport verification can verify
  #   an object.
  # For the moment, we support signatures only by the issuing authority,
  #  identified by its keyname
  __verifying_keyname = None

  def set_signature_verification(self, keyname):
    """state that this object has been verified by *keyname*."""
    self.__verifying_keyname = keyname

  def verified_signature(self):
    """return true when this object has been verified."""
    return self.__verifying_keyname == self.S_GET_KEYNAME()



class _SignatureRequest(object):
  """auxiliary class to manage signature information."""

  def __init__(self, keyname, context):
    self._keyname = keyname
    self._context = context

  def sign(self, instance, doc):
    """return the signed serialization for *instance* in *doc*.

    *doc* is a `lxml` document containing *instance*,
    identified by its id.
    """

    keyname = self._keyname
    if keyname is None: keyname = instance.S_GET_KEYNAME()
    context = self._context
    if context is None: context = default_sign_context
    return context.sign(doc,
                        getattr(instance, instance.S_ID_ATTRIBUTE),
                        keyname
                        )


class SignatureContext(object):
  """encapsulates a signature (sign/verify) context.

  Note: Its instances are sensible. Avoid access from untrusted code!
  """

  def __init__(self, keys_manager=None):
    """initialize a signature context.

    *keys_manager* is currently a mapping from name to a sequence of keys.
    """
    if keys_manager is None: keys_manager = {}
    self.__keys_manager = keys_manager


  def add_key(self, key, name=None):
    """add xmlsec *key* to our context."""
    if name is None: name = key.name
    mngr = self.__keys_manager
    kl = mngr.get(name)
    if kl is None: kl = mngr[name] = []
    kl.append(key)


  def sign(self, doc, id, keyname):
    """sign element identified by *id* in *doc* (`lxml` etree) with the (first) key with *keyname*."""
    from dm.xmlsec.binding import dsig, DSigCtx, findNode, Error
    # will fail with ``IndexError`` when the id does not exist
    node = doc.xpath('//*[@ID="%s"]' % id)[0]
    node = findNode(node, dsig("Signature"))
    assert node is not None, "Missing signature element"
    sign_ctx = DSigCtx(None)
    sign_ctx.signKey = self.__keys_manager[keyname][0]
    try: sign_ctx.sign(node)
    except Error, e:
      raise SignError('signing failed', id, keyname, e)


  def verify(self, doc, id, keyname):
    """verify the node identified by *id* in *doc* using a key associated with *keyname*.

    Raise ``VerifyError``, when the verification fails.

    We only allow a single reference. Its uri must either be empty or
    refer to the element we are verifying.
    In addition, we only allow the standard transforms.
    """
    from dm.xmlsec.binding import findNode, dsig, DSigCtx, \
         TransformInclC14N, TransformExclC14N, TransformSha1, \
         TransformRsaSha1, TransformEnveloped, \
         VerificationError
    node = doc.xpath('//*[@ID="%s"]' % id)
    if len(node) != 1:
      raise VerifyError('id not unique or not found: %s %d' % (id, len(nodes)))
    node = node[0]
    sig = findNode(node, dsig("Signature"))
    # verify the reference.
    refs = sig.xpath('ds:SignedInfo/ds:Reference', namespaces=dsigns)
    if len(refs) != 1:
      raise VerifyError('only a single reference is allowed: %d' % len(refs))
    ref = refs[0]
    uris = ref.xpath('@URI')
    if not uris or uris[0] != '#' + id:
      raise VerifyError('reference uri does not refer to signature parent', id)
    # now verify the signature: try each key in turn
    for key in self.__keys_manager.get(keyname, ()):
      verify_ctx = DSigCtx(None)
      for t in (TransformInclC14N, TransformExclC14N, TransformSha1, TransformRsaSha1):
        verify_ctx.enableSignatureTransform(t)
      for t in (TransformInclC14N, TransformExclC14N, TransformSha1, TransformEnveloped):
        verify_ctx.enableReferenceTransform(t)
      verify_ctx.signKey = key
      try: verify_ctx.verify(sig)
      except VerificationError: pass
      else: return
    raise VerifyError('signature verification failed: %s %s' % (id, keyname))



class _BindingDOMSupportSignatureExtension(object):
  """mixin class to support signatures."""
  _signature_requests = None
  __document = None


  def add_signature_request(self, request, instance):
    """request signature for *instance* in upcoming ``finalize``."""
    sr = self._signature_requests
    if sr is None: sr = self._signature_requests = []
    sr.append((request, instance))


  def finalize(self):
    r = super(_BindingDOMSupportSignatureExtension, self).finalize()
    sr = self._signature_requests
    if sr is None: return r
    # perform all signature requests in reverse order
    from lxml.etree import parse, tostring
    from dm.xmlsec.binding import addIDs
    from StringIO import StringIO
    doc = self.document().toxml()
    doc_tree = parse(StringIO(doc))
    addIDs(doc_tree.getroot(), ['ID'])
    while sr:
      r, i = sr.pop()
      r.sign(i, doc_tree)
    signed_doc = tostring(doc_tree)
    # interestingly: I must use "xml.dom.mindom" for parsing
    #   ``pyxb.utils.domutils.StringToDOM`` does not work
    from xml.dom.minidom import parseString
    self.__document = parseString(signed_doc)
    
  def document(self):
    d = self.__document
    if d is not None: return d
    return super(_BindingDOMSupportSignatureExtension, self).document()


default_sign_context =  SignatureContext()


# Verification support
def verify_signatures(doc, val, keyname=None, context=None):
  """verify all signatures contained in *doc* and update *val*.

  *doc* is a string containing an XML document.
  *val* is its ``pyxb`` binding.

  *keyname*, if given, identifies the key that has verified the enclosing
  context, e.g. the transport.

  *context* is a signature context. Default: ``default_verify_context``

  The function recursively descends *val* and tries to verify
  the signature for each encountered ``Signable`` instance.
  A ``VerifyError`` is raised when the signature verification fails.
  """
  from lxml.etree import parse
  from StringIO import StringIO
  from dm.xmlsec.binding import addIDs

  def verify(node, keyname):
    """verify *node* and (recursively) its decendents."""
    if isinstance(node, Signable):
      # this object is signable
      if getattr(node, node.S_SIGNATURE_ATTRIBUTE) is not None:
        # has its own signature -- verify it
        keyname = node.S_GET_KEYNAME()
        context.verify(dp, getattr(node, node.S_ID_ATTRIBUTE), keyname)
      node.set_signature_verification(keyname)
    # recurse
    ss = getattr(node, '_symbolSet', None)
    if ss is None: return
    # node._symbolSet returns a map eu --> list(child)
    for cl in ss().values():
      for c in cl: verify(c, keyname)

  dp = parse(StringIO(doc))
  if context is None: context = default_verify_context
  addIDs(dp.getroot(), ['ID'])
  verify(val, keyname)


def add_signature_verification():
  """enhance caller globals with signature verification."""
  moddict = get_frame_globals(1)
  cfd = moddict['CreateFromDocument']

  def CreateFromDocument(xml_text, *args, **kw):
    """override to perform signature verification.

    *keyname* and *context* are keyword parameters used for signature
    verification (see ``dm.saml2.signature.verify_signatures``).
    Other arguments are passed on to the original function.
    The keyword parameter *suppress_verification* can suppress the
    verification.
    """
    keyname, context = kw.pop('keyname', None), kw.pop('context', None)
    suppress = kw.pop("suppress_verification", False)
    i = cfd(xml_text, *args, **kw)
    if not suppress: verify_signatures(xml_text, i, keyname, context)
    return i
  CreateFromDocument.signature_enhanced = True

  moddict['CreateFromDocument'] = CreateFromDocument


default_verify_context =  SignatureContext()

dsigns = dict(ds="http://www.w3.org/2000/09/xmldsig#")
