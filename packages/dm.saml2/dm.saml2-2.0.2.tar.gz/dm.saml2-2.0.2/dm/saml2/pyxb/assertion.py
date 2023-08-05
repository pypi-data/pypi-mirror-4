from datetime import datetime

from pyxb.bundles.saml20.assertion import *
from dm.saml2.signature import Signable, add_signature_verification
from dm.saml2.uuid import uuid
from dm.saml2.util import enhance, Picklable


class _StandardSaml2Initialization(object):
  """mixin class to provide standard initialization of 'ID', 'Version' and 'IssueInstant."""

  def __init__(self, *args, **kw):
    if 'Version' not in kw: kw['Version'] = '2.0'
    # Note: an id must start with a char
    if 'ID' not in kw: kw['ID'] = '_' + uuid()
    if 'IssueInstant' not in kw: kw['IssueInstant'] = datetime.utcnow()
    super(_StandardSaml2Initialization, self).__init__(*args, **kw)


class _StandardSignable(Signable, _StandardSaml2Initialization):
  """mixin class to provide standard initialization and signability."""

  def S_GET_KEYNAME(self): return self.Issuer.value()


class _AssertionTypeExtension(_StandardSignable, Picklable):
  """Application generated ``Assertion``."""

  def is_valid(self, context=None):
    cs = self.Conditions
    return cs is None or cs.is_valid(context)


enhance('AssertionType')

class ConditionsCheckContext(object):
  """Base class used for condition validity checks.

  Supports the standard condition types.
  """
  #  handling the `Condition` extension point
  #   override as necessary to handle your conditions
  def is_condition_valid(self, condition): return False

  # audience restriction
  # must be overridden by derived classes
  def audience_id(self): return None
  def belongs_to_audience(self, audience):
    return audience == self.audience_id()

  # one time use
  def set_one_time_use(self):
    raise NotImplementedError("we do not support `OneTimeUse`")

  def set_proxy_restriction(self, restriction):
    raise NotImplementedError("we do not support `ProxyRestriction`")


class _ConditionsTypeExtension(object):
  """give it a ``is_valid`` method.

  Concrete implementations likely will need some (potentially) global context.
  """

  def is_valid(self, context=None):
    # according to 2.5.1.1 we should implement a three-value logic
    #  (invalid, valid, indeterminate) -- we fail to do so.
    now = datetime.utcnow()
    cv = self.NotBefore
    if cv is not None and now < cv: return False
    cv = self.NotOnOrAfter
    if cv is not None and now >= cv: return False
    for c in self.Condition:
      if not c.is_valid(context): return False
    for c in self.AudienceRestriction:
      if not c.is_valid(context): return False
    for c in self.OneTimeUse:
      if not c.is_valid(context): return False
    for c in self.ProxyRestriction: pass
    return True

enhance('ConditionsType')


class _ConditionAbstractTypeExtension(object):
  def is_valid(self, context):
    return context is not None and context.is_condition_valid(self)

enhance("ConditionAbstractType")


class _AudienceRestrictionTypeExtension(object):
  def is_valid(self, context):
    if context is None: return False
    for a in self.Audience:
      if context.belongs_to_audience(a): return True
    return False

enhance("AudienceRestrictionType")


class _OneTimeUseTypeExtension(object):
  def is_valid(self, context):
    if context is None: context = ConditionsCheckContext()
    context.set_one_time_use()
    return True

enhance("OneTimeUseType")


class _ProxyRestrictionTypeExtension(object):
  def is_valid(self, context):
    if context is None: context = ConditionsCheckContext()
    context.set_proxy_restriction(self)
    return True

enhance("ProxyRestrictionType")




add_signature_verification()
