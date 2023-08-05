# ../../../dm/saml2/pyxb/raw/authncontext_ppt.py
# -*- coding: utf-8 -*-
# PyXB bindings for NM:8a2c7cfd45dd53c9ca96a9164531618be8c8ccfb
# Generated 2012-06-30 20:34:07.152376 by PyXB version 1.1.4
# Namespace urn:oasis:names:tc:SAML:2.0:ac:classes:PasswordProtectedTransport

import pyxb
import pyxb.binding
import pyxb.binding.saxer
import StringIO
import pyxb.utils.utility
import pyxb.utils.domutils
import sys

# Unique identifier for bindings created at the same time
_GenerationUID = pyxb.utils.utility.UniqueIdentifier('urn:uuid:2c59a4e8-c2e2-11e1-9363-0025228242f2')

# Import bindings for namespaces imported into schema
import pyxb.binding.datatypes

Namespace = pyxb.namespace.NamespaceForURI(u'urn:oasis:names:tc:SAML:2.0:ac:classes:PasswordProtectedTransport', create_if_missing=True)
Namespace.configureCategories(['typeBinding', 'elementBinding'])
ModuleRecord = Namespace.lookupModuleRecordByUID(_GenerationUID, create_if_missing=True)
ModuleRecord._setModule(sys.modules[__name__])

def CreateFromDocument (xml_text, default_namespace=None, location_base=None):
    """Parse the given XML and use the document element to create a
    Python instance.
    
    @kw default_namespace The L{pyxb.Namespace} instance to use as the
    default namespace where there is no default namespace in scope.
    If unspecified or C{None}, the namespace of the module containing
    this function will be used.

    @keyword location_base: An object to be recorded as the base of all
    L{pyxb.utils.utility.Location} instances associated with events and
    objects handled by the parser.  You might pass the URI from which
    the document was obtained.
    """

    if pyxb.XMLStyle_saxer != pyxb._XMLStyle:
        dom = pyxb.utils.domutils.StringToDOM(xml_text)
        return CreateFromDOM(dom.documentElement)
    if default_namespace is None:
        default_namespace = Namespace.fallbackNamespace()
    saxer = pyxb.binding.saxer.make_parser(fallback_namespace=default_namespace, location_base=location_base)
    handler = saxer.getContentHandler()
    saxer.parse(StringIO.StringIO(xml_text))
    instance = handler.rootObject()
    return instance

def CreateFromDOM (node, default_namespace=None):
    """Create a Python instance from the given DOM node.
    The node tag must correspond to an element declaration in this module.

    @deprecated: Forcing use of DOM interface is unnecessary; use L{CreateFromDocument}."""
    if default_namespace is None:
        default_namespace = Namespace.fallbackNamespace()
    return pyxb.binding.basis.element.AnyCreateFromDOM(node, _fallback_namespace=default_namespace)


# Atomic SimpleTypeDefinition
class STD_ANON (pyxb.binding.datatypes.NMTOKEN, pyxb.binding.basis.enumeration_mixin):

    """An atomic simple type."""

    _ExpandedName = None
    _Documentation = None
STD_ANON._CF_enumeration = pyxb.binding.facets.CF_enumeration(value_datatype=STD_ANON, enum_prefix=None)
STD_ANON.primary = STD_ANON._CF_enumeration.addEnumeration(unicode_value=u'primary', tag=u'primary')
STD_ANON.secondary = STD_ANON._CF_enumeration.addEnumeration(unicode_value=u'secondary', tag=u'secondary')
STD_ANON._InitializeFacetMap(STD_ANON._CF_enumeration)

# Atomic SimpleTypeDefinition
class mediumType (pyxb.binding.datatypes.NMTOKEN, pyxb.binding.basis.enumeration_mixin):

    """An atomic simple type."""

    _ExpandedName = pyxb.namespace.ExpandedName(Namespace, u'mediumType')
    _Documentation = None
mediumType._CF_enumeration = pyxb.binding.facets.CF_enumeration(value_datatype=mediumType, enum_prefix=None)
mediumType.memory = mediumType._CF_enumeration.addEnumeration(unicode_value=u'memory', tag=u'memory')
mediumType.smartcard = mediumType._CF_enumeration.addEnumeration(unicode_value=u'smartcard', tag=u'smartcard')
mediumType.token = mediumType._CF_enumeration.addEnumeration(unicode_value=u'token', tag=u'token')
mediumType.MobileDevice = mediumType._CF_enumeration.addEnumeration(unicode_value=u'MobileDevice', tag=u'MobileDevice')
mediumType.MobileAuthCard = mediumType._CF_enumeration.addEnumeration(unicode_value=u'MobileAuthCard', tag=u'MobileAuthCard')
mediumType._InitializeFacetMap(mediumType._CF_enumeration)
Namespace.addCategoryObject('typeBinding', u'mediumType', mediumType)

# Atomic SimpleTypeDefinition
class STD_ANON_ (pyxb.binding.datatypes.NMTOKEN, pyxb.binding.basis.enumeration_mixin):

    """An atomic simple type."""

    _ExpandedName = None
    _Documentation = None
STD_ANON_._CF_enumeration = pyxb.binding.facets.CF_enumeration(value_datatype=STD_ANON_, enum_prefix=None)
STD_ANON_.principalchosen = STD_ANON_._CF_enumeration.addEnumeration(unicode_value=u'principalchosen', tag=u'principalchosen')
STD_ANON_.automatic = STD_ANON_._CF_enumeration.addEnumeration(unicode_value=u'automatic', tag=u'automatic')
STD_ANON_._InitializeFacetMap(STD_ANON_._CF_enumeration)

# Atomic SimpleTypeDefinition
class booleanType (pyxb.binding.datatypes.NMTOKEN, pyxb.binding.basis.enumeration_mixin):

    """An atomic simple type."""

    _ExpandedName = pyxb.namespace.ExpandedName(Namespace, u'booleanType')
    _Documentation = None
booleanType._CF_enumeration = pyxb.binding.facets.CF_enumeration(value_datatype=booleanType, enum_prefix=None)
booleanType.true = booleanType._CF_enumeration.addEnumeration(unicode_value=u'true', tag=u'true')
booleanType.false = booleanType._CF_enumeration.addEnumeration(unicode_value=u'false', tag=u'false')
booleanType._InitializeFacetMap(booleanType._CF_enumeration)
Namespace.addCategoryObject('typeBinding', u'booleanType', booleanType)

# Atomic SimpleTypeDefinition
class DeviceTypeType (pyxb.binding.datatypes.NMTOKEN, pyxb.binding.basis.enumeration_mixin):

    """An atomic simple type."""

    _ExpandedName = pyxb.namespace.ExpandedName(Namespace, u'DeviceTypeType')
    _Documentation = None
DeviceTypeType._CF_enumeration = pyxb.binding.facets.CF_enumeration(value_datatype=DeviceTypeType, enum_prefix=None)
DeviceTypeType.hardware = DeviceTypeType._CF_enumeration.addEnumeration(unicode_value=u'hardware', tag=u'hardware')
DeviceTypeType.software = DeviceTypeType._CF_enumeration.addEnumeration(unicode_value=u'software', tag=u'software')
DeviceTypeType._InitializeFacetMap(DeviceTypeType._CF_enumeration)
Namespace.addCategoryObject('typeBinding', u'DeviceTypeType', DeviceTypeType)

# Atomic SimpleTypeDefinition
class STD_ANON_2 (pyxb.binding.datatypes.integer):

    """An atomic simple type."""

    _ExpandedName = None
    _Documentation = None
STD_ANON_2._CF_minInclusive = pyxb.binding.facets.CF_minInclusive(value_datatype=STD_ANON_2, value=pyxb.binding.datatypes.integer(3L))
STD_ANON_2._InitializeFacetMap(STD_ANON_2._CF_minInclusive)

# Atomic SimpleTypeDefinition
class nymType (pyxb.binding.datatypes.NMTOKEN, pyxb.binding.basis.enumeration_mixin):

    """An atomic simple type."""

    _ExpandedName = pyxb.namespace.ExpandedName(Namespace, u'nymType')
    _Documentation = None
nymType._CF_enumeration = pyxb.binding.facets.CF_enumeration(value_datatype=nymType, enum_prefix=None)
nymType.anonymity = nymType._CF_enumeration.addEnumeration(unicode_value=u'anonymity', tag=u'anonymity')
nymType.verinymity = nymType._CF_enumeration.addEnumeration(unicode_value=u'verinymity', tag=u'verinymity')
nymType.pseudonymity = nymType._CF_enumeration.addEnumeration(unicode_value=u'pseudonymity', tag=u'pseudonymity')
nymType._InitializeFacetMap(nymType._CF_enumeration)
Namespace.addCategoryObject('typeBinding', u'nymType', nymType)

# Complex type ExtensionType with content type ELEMENT_ONLY
class ExtensionType (pyxb.binding.basis.complexTypeDefinition):
    _TypeDefinition = None
    _ContentTypeTag = pyxb.binding.basis.complexTypeDefinition._CT_ELEMENT_ONLY
    _Abstract = False
    _ExpandedName = pyxb.namespace.ExpandedName(Namespace, u'ExtensionType')
    # Base type is pyxb.binding.datatypes.anyType
    _HasWildcardElement = True

    _ElementMap = {
        
    }
    _AttributeMap = {
        
    }
Namespace.addCategoryObject('typeBinding', u'ExtensionType', ExtensionType)


# Complex type PublicKeyType with content type ELEMENT_ONLY
class PublicKeyType (pyxb.binding.basis.complexTypeDefinition):
    _TypeDefinition = None
    _ContentTypeTag = pyxb.binding.basis.complexTypeDefinition._CT_ELEMENT_ONLY
    _Abstract = False
    _ExpandedName = pyxb.namespace.ExpandedName(Namespace, u'PublicKeyType')
    # Base type is pyxb.binding.datatypes.anyType
    
    # Element {urn:oasis:names:tc:SAML:2.0:ac:classes:PasswordProtectedTransport}Extension uses Python identifier Extension
    __Extension = pyxb.binding.content.ElementUse(pyxb.namespace.ExpandedName(Namespace, u'Extension'), 'Extension', '__urnoasisnamestcSAML2_0acclassesPasswordProtectedTransport_PublicKeyType_urnoasisnamestcSAML2_0acclassesPasswordProtectedTransportExtension', True)

    
    Extension = property(__Extension.value, __Extension.set, None, None)

    
    # Attribute keyValidation uses Python identifier keyValidation
    __keyValidation = pyxb.binding.content.AttributeUse(pyxb.namespace.ExpandedName(None, u'keyValidation'), 'keyValidation', '__urnoasisnamestcSAML2_0acclassesPasswordProtectedTransport_PublicKeyType_keyValidation', pyxb.binding.datatypes.anySimpleType)
    
    keyValidation = property(__keyValidation.value, __keyValidation.set, None, None)


    _ElementMap = {
        __Extension.name() : __Extension
    }
    _AttributeMap = {
        __keyValidation.name() : __keyValidation
    }
Namespace.addCategoryObject('typeBinding', u'PublicKeyType', PublicKeyType)


# Complex type PasswordType with content type ELEMENT_ONLY
class PasswordType (pyxb.binding.basis.complexTypeDefinition):
    _TypeDefinition = None
    _ContentTypeTag = pyxb.binding.basis.complexTypeDefinition._CT_ELEMENT_ONLY
    _Abstract = False
    _ExpandedName = pyxb.namespace.ExpandedName(Namespace, u'PasswordType')
    # Base type is pyxb.binding.datatypes.anyType
    
    # Element {urn:oasis:names:tc:SAML:2.0:ac:classes:PasswordProtectedTransport}Alphabet uses Python identifier Alphabet
    __Alphabet = pyxb.binding.content.ElementUse(pyxb.namespace.ExpandedName(Namespace, u'Alphabet'), 'Alphabet', '__urnoasisnamestcSAML2_0acclassesPasswordProtectedTransport_PasswordType_urnoasisnamestcSAML2_0acclassesPasswordProtectedTransportAlphabet', False)

    
    Alphabet = property(__Alphabet.value, __Alphabet.set, None, None)

    
    # Element {urn:oasis:names:tc:SAML:2.0:ac:classes:PasswordProtectedTransport}Generation uses Python identifier Generation
    __Generation = pyxb.binding.content.ElementUse(pyxb.namespace.ExpandedName(Namespace, u'Generation'), 'Generation', '__urnoasisnamestcSAML2_0acclassesPasswordProtectedTransport_PasswordType_urnoasisnamestcSAML2_0acclassesPasswordProtectedTransportGeneration', False)

    
    Generation = property(__Generation.value, __Generation.set, None, u'\n        Indicates whether the password was chosen by the\n        Principal or auto-supplied by the Authentication Authority.\n        principalchosen - the Principal is allowed to choose\n        the value of the password. This is true even if\n        the initial password is chosen at random by the UA or\n        the IdP and the Principal is then free to change\n        the password.\n        automatic - the password is chosen by the UA or the\n        IdP to be cryptographically strong in some sense,\n        or to satisfy certain password rules, and that the\n        Principal is not free to change it or to choose a new password.\n      ')

    
    # Element {urn:oasis:names:tc:SAML:2.0:ac:classes:PasswordProtectedTransport}Extension uses Python identifier Extension
    __Extension = pyxb.binding.content.ElementUse(pyxb.namespace.ExpandedName(Namespace, u'Extension'), 'Extension', '__urnoasisnamestcSAML2_0acclassesPasswordProtectedTransport_PasswordType_urnoasisnamestcSAML2_0acclassesPasswordProtectedTransportExtension', True)

    
    Extension = property(__Extension.value, __Extension.set, None, None)

    
    # Element {urn:oasis:names:tc:SAML:2.0:ac:classes:PasswordProtectedTransport}Length uses Python identifier Length
    __Length = pyxb.binding.content.ElementUse(pyxb.namespace.ExpandedName(Namespace, u'Length'), 'Length', '__urnoasisnamestcSAML2_0acclassesPasswordProtectedTransport_PasswordType_urnoasisnamestcSAML2_0acclassesPasswordProtectedTransportLength', False)

    
    Length = property(__Length.value, __Length.set, None, u'\n        This element indicates the minimum and/or maximum\n        ASCII length of the password which is enforced (by the UA or the\n        IdP). In other words, this is the minimum and/or maximum number of\n        ASCII characters required to represent a valid password.\n        min - the minimum number of ASCII characters required\n        in a valid password, as enforced by the UA or the IdP.\n        max - the maximum number of ASCII characters required\n        in a valid password, as enforced by the UA or the IdP.\n      ')

    
    # Attribute ExternalVerification uses Python identifier ExternalVerification
    __ExternalVerification = pyxb.binding.content.AttributeUse(pyxb.namespace.ExpandedName(None, u'ExternalVerification'), 'ExternalVerification', '__urnoasisnamestcSAML2_0acclassesPasswordProtectedTransport_PasswordType_ExternalVerification', pyxb.binding.datatypes.anyURI)
    
    ExternalVerification = property(__ExternalVerification.value, __ExternalVerification.set, None, None)


    _ElementMap = {
        __Alphabet.name() : __Alphabet,
        __Generation.name() : __Generation,
        __Extension.name() : __Extension,
        __Length.name() : __Length
    }
    _AttributeMap = {
        __ExternalVerification.name() : __ExternalVerification
    }
Namespace.addCategoryObject('typeBinding', u'PasswordType', PasswordType)


# Complex type RestrictedPasswordType with content type ELEMENT_ONLY
class RestrictedPasswordType (PasswordType):
    _TypeDefinition = None
    _ContentTypeTag = pyxb.binding.basis.complexTypeDefinition._CT_ELEMENT_ONLY
    _Abstract = False
    _ExpandedName = pyxb.namespace.ExpandedName(Namespace, u'RestrictedPasswordType')
    # Base type is PasswordType
    
    # Element Generation ({urn:oasis:names:tc:SAML:2.0:ac:classes:PasswordProtectedTransport}Generation) inherited from {urn:oasis:names:tc:SAML:2.0:ac:classes:PasswordProtectedTransport}PasswordType
    
    # Element Extension ({urn:oasis:names:tc:SAML:2.0:ac:classes:PasswordProtectedTransport}Extension) inherited from {urn:oasis:names:tc:SAML:2.0:ac:classes:PasswordProtectedTransport}PasswordType
    
    # Element Length uses Python identifier Length_
    __Length_ = pyxb.binding.content.ElementUse(pyxb.namespace.ExpandedName(None, u'Length'), 'Length_', '__urnoasisnamestcSAML2_0acclassesPasswordProtectedTransport_RestrictedPasswordType_Length', False)

    
    Length_ = property(__Length_.value, __Length_.set, None, None)

    
    # Attribute ExternalVerification is restricted from parent
    
    # Attribute ExternalVerification uses Python identifier ExternalVerification
    __ExternalVerification = pyxb.binding.content.AttributeUse(pyxb.namespace.ExpandedName(None, u'ExternalVerification'), 'ExternalVerification', '__urnoasisnamestcSAML2_0acclassesPasswordProtectedTransport_PasswordType_ExternalVerification', pyxb.binding.datatypes.anyURI)
    
    ExternalVerification = property(__ExternalVerification.value, __ExternalVerification.set, None, None)


    _ElementMap = PasswordType._ElementMap.copy()
    _ElementMap.update({
        __Length_.name() : __Length_
    })
    _AttributeMap = PasswordType._AttributeMap.copy()
    _AttributeMap.update({
        __ExternalVerification.name() : __ExternalVerification
    })
Namespace.addCategoryObject('typeBinding', u'RestrictedPasswordType', RestrictedPasswordType)


# Complex type SharedSecretChallengeResponseType with content type ELEMENT_ONLY
class SharedSecretChallengeResponseType (pyxb.binding.basis.complexTypeDefinition):
    _TypeDefinition = None
    _ContentTypeTag = pyxb.binding.basis.complexTypeDefinition._CT_ELEMENT_ONLY
    _Abstract = False
    _ExpandedName = pyxb.namespace.ExpandedName(Namespace, u'SharedSecretChallengeResponseType')
    # Base type is pyxb.binding.datatypes.anyType
    
    # Element {urn:oasis:names:tc:SAML:2.0:ac:classes:PasswordProtectedTransport}Extension uses Python identifier Extension
    __Extension = pyxb.binding.content.ElementUse(pyxb.namespace.ExpandedName(Namespace, u'Extension'), 'Extension', '__urnoasisnamestcSAML2_0acclassesPasswordProtectedTransport_SharedSecretChallengeResponseType_urnoasisnamestcSAML2_0acclassesPasswordProtectedTransportExtension', True)

    
    Extension = property(__Extension.value, __Extension.set, None, None)

    
    # Attribute method uses Python identifier method
    __method = pyxb.binding.content.AttributeUse(pyxb.namespace.ExpandedName(None, u'method'), 'method', '__urnoasisnamestcSAML2_0acclassesPasswordProtectedTransport_SharedSecretChallengeResponseType_method', pyxb.binding.datatypes.anyURI)
    
    method = property(__method.value, __method.set, None, None)


    _ElementMap = {
        __Extension.name() : __Extension
    }
    _AttributeMap = {
        __method.name() : __method
    }
Namespace.addCategoryObject('typeBinding', u'SharedSecretChallengeResponseType', SharedSecretChallengeResponseType)


# Complex type ExtensionOnlyType with content type ELEMENT_ONLY
class ExtensionOnlyType (pyxb.binding.basis.complexTypeDefinition):
    _TypeDefinition = None
    _ContentTypeTag = pyxb.binding.basis.complexTypeDefinition._CT_ELEMENT_ONLY
    _Abstract = False
    _ExpandedName = pyxb.namespace.ExpandedName(Namespace, u'ExtensionOnlyType')
    # Base type is pyxb.binding.datatypes.anyType
    
    # Element {urn:oasis:names:tc:SAML:2.0:ac:classes:PasswordProtectedTransport}Extension uses Python identifier Extension
    __Extension = pyxb.binding.content.ElementUse(pyxb.namespace.ExpandedName(Namespace, u'Extension'), 'Extension', '__urnoasisnamestcSAML2_0acclassesPasswordProtectedTransport_ExtensionOnlyType_urnoasisnamestcSAML2_0acclassesPasswordProtectedTransportExtension', True)

    
    Extension = property(__Extension.value, __Extension.set, None, None)


    _ElementMap = {
        __Extension.name() : __Extension
    }
    _AttributeMap = {
        
    }
Namespace.addCategoryObject('typeBinding', u'ExtensionOnlyType', ExtensionOnlyType)


# Complex type GoverningAgreementRefType with content type EMPTY
class GoverningAgreementRefType (pyxb.binding.basis.complexTypeDefinition):
    _TypeDefinition = None
    _ContentTypeTag = pyxb.binding.basis.complexTypeDefinition._CT_EMPTY
    _Abstract = False
    _ExpandedName = pyxb.namespace.ExpandedName(Namespace, u'GoverningAgreementRefType')
    # Base type is pyxb.binding.datatypes.anyType
    
    # Attribute governingAgreementRef uses Python identifier governingAgreementRef
    __governingAgreementRef = pyxb.binding.content.AttributeUse(pyxb.namespace.ExpandedName(None, u'governingAgreementRef'), 'governingAgreementRef', '__urnoasisnamestcSAML2_0acclassesPasswordProtectedTransport_GoverningAgreementRefType_governingAgreementRef', pyxb.binding.datatypes.anyURI, required=True)
    
    governingAgreementRef = property(__governingAgreementRef.value, __governingAgreementRef.set, None, None)


    _ElementMap = {
        
    }
    _AttributeMap = {
        __governingAgreementRef.name() : __governingAgreementRef
    }
Namespace.addCategoryObject('typeBinding', u'GoverningAgreementRefType', GoverningAgreementRefType)


# Complex type CTD_ANON with content type EMPTY
class CTD_ANON (pyxb.binding.basis.complexTypeDefinition):
    _TypeDefinition = None
    _ContentTypeTag = pyxb.binding.basis.complexTypeDefinition._CT_EMPTY
    _Abstract = False
    _ExpandedName = None
    # Base type is pyxb.binding.datatypes.anyType
    
    # Attribute credentialLevel uses Python identifier credentialLevel
    __credentialLevel = pyxb.binding.content.AttributeUse(pyxb.namespace.ExpandedName(None, u'credentialLevel'), 'credentialLevel', '__urnoasisnamestcSAML2_0acclassesPasswordProtectedTransport_CTD_ANON_credentialLevel', STD_ANON)
    
    credentialLevel = property(__credentialLevel.value, __credentialLevel.set, None, None)


    _ElementMap = {
        
    }
    _AttributeMap = {
        __credentialLevel.name() : __credentialLevel
    }



# Complex type ActivationLimitSessionType with content type EMPTY
class ActivationLimitSessionType (pyxb.binding.basis.complexTypeDefinition):
    _TypeDefinition = None
    _ContentTypeTag = pyxb.binding.basis.complexTypeDefinition._CT_EMPTY
    _Abstract = False
    _ExpandedName = pyxb.namespace.ExpandedName(Namespace, u'ActivationLimitSessionType')
    # Base type is pyxb.binding.datatypes.anyType

    _ElementMap = {
        
    }
    _AttributeMap = {
        
    }
Namespace.addCategoryObject('typeBinding', u'ActivationLimitSessionType', ActivationLimitSessionType)


# Complex type ActivationPinType with content type ELEMENT_ONLY
class ActivationPinType (pyxb.binding.basis.complexTypeDefinition):
    _TypeDefinition = None
    _ContentTypeTag = pyxb.binding.basis.complexTypeDefinition._CT_ELEMENT_ONLY
    _Abstract = False
    _ExpandedName = pyxb.namespace.ExpandedName(Namespace, u'ActivationPinType')
    # Base type is pyxb.binding.datatypes.anyType
    
    # Element {urn:oasis:names:tc:SAML:2.0:ac:classes:PasswordProtectedTransport}Alphabet uses Python identifier Alphabet
    __Alphabet = pyxb.binding.content.ElementUse(pyxb.namespace.ExpandedName(Namespace, u'Alphabet'), 'Alphabet', '__urnoasisnamestcSAML2_0acclassesPasswordProtectedTransport_ActivationPinType_urnoasisnamestcSAML2_0acclassesPasswordProtectedTransportAlphabet', False)

    
    Alphabet = property(__Alphabet.value, __Alphabet.set, None, None)

    
    # Element {urn:oasis:names:tc:SAML:2.0:ac:classes:PasswordProtectedTransport}ActivationLimit uses Python identifier ActivationLimit
    __ActivationLimit = pyxb.binding.content.ElementUse(pyxb.namespace.ExpandedName(Namespace, u'ActivationLimit'), 'ActivationLimit', '__urnoasisnamestcSAML2_0acclassesPasswordProtectedTransport_ActivationPinType_urnoasisnamestcSAML2_0acclassesPasswordProtectedTransportActivationLimit', False)

    
    ActivationLimit = property(__ActivationLimit.value, __ActivationLimit.set, None, u'\n        This element indicates the length of time for which an\n        PIN-based authentication is valid.\n      ')

    
    # Element {urn:oasis:names:tc:SAML:2.0:ac:classes:PasswordProtectedTransport}Length uses Python identifier Length
    __Length = pyxb.binding.content.ElementUse(pyxb.namespace.ExpandedName(Namespace, u'Length'), 'Length', '__urnoasisnamestcSAML2_0acclassesPasswordProtectedTransport_ActivationPinType_urnoasisnamestcSAML2_0acclassesPasswordProtectedTransportLength', False)

    
    Length = property(__Length.value, __Length.set, None, u'\n        This element indicates the minimum and/or maximum\n        ASCII length of the password which is enforced (by the UA or the\n        IdP). In other words, this is the minimum and/or maximum number of\n        ASCII characters required to represent a valid password.\n        min - the minimum number of ASCII characters required\n        in a valid password, as enforced by the UA or the IdP.\n        max - the maximum number of ASCII characters required\n        in a valid password, as enforced by the UA or the IdP.\n      ')

    
    # Element {urn:oasis:names:tc:SAML:2.0:ac:classes:PasswordProtectedTransport}Extension uses Python identifier Extension
    __Extension = pyxb.binding.content.ElementUse(pyxb.namespace.ExpandedName(Namespace, u'Extension'), 'Extension', '__urnoasisnamestcSAML2_0acclassesPasswordProtectedTransport_ActivationPinType_urnoasisnamestcSAML2_0acclassesPasswordProtectedTransportExtension', True)

    
    Extension = property(__Extension.value, __Extension.set, None, None)

    
    # Element {urn:oasis:names:tc:SAML:2.0:ac:classes:PasswordProtectedTransport}Generation uses Python identifier Generation
    __Generation = pyxb.binding.content.ElementUse(pyxb.namespace.ExpandedName(Namespace, u'Generation'), 'Generation', '__urnoasisnamestcSAML2_0acclassesPasswordProtectedTransport_ActivationPinType_urnoasisnamestcSAML2_0acclassesPasswordProtectedTransportGeneration', False)

    
    Generation = property(__Generation.value, __Generation.set, None, u'\n        Indicates whether the password was chosen by the\n        Principal or auto-supplied by the Authentication Authority.\n        principalchosen - the Principal is allowed to choose\n        the value of the password. This is true even if\n        the initial password is chosen at random by the UA or\n        the IdP and the Principal is then free to change\n        the password.\n        automatic - the password is chosen by the UA or the\n        IdP to be cryptographically strong in some sense,\n        or to satisfy certain password rules, and that the\n        Principal is not free to change it or to choose a new password.\n      ')


    _ElementMap = {
        __Alphabet.name() : __Alphabet,
        __ActivationLimit.name() : __ActivationLimit,
        __Length.name() : __Length,
        __Extension.name() : __Extension,
        __Generation.name() : __Generation
    }
    _AttributeMap = {
        
    }
Namespace.addCategoryObject('typeBinding', u'ActivationPinType', ActivationPinType)


# Complex type KeyStorageType with content type EMPTY
class KeyStorageType (pyxb.binding.basis.complexTypeDefinition):
    _TypeDefinition = None
    _ContentTypeTag = pyxb.binding.basis.complexTypeDefinition._CT_EMPTY
    _Abstract = False
    _ExpandedName = pyxb.namespace.ExpandedName(Namespace, u'KeyStorageType')
    # Base type is pyxb.binding.datatypes.anyType
    
    # Attribute medium uses Python identifier medium
    __medium = pyxb.binding.content.AttributeUse(pyxb.namespace.ExpandedName(None, u'medium'), 'medium', '__urnoasisnamestcSAML2_0acclassesPasswordProtectedTransport_KeyStorageType_medium', mediumType, required=True)
    
    medium = property(__medium.value, __medium.set, None, None)


    _ElementMap = {
        
    }
    _AttributeMap = {
        __medium.name() : __medium
    }
Namespace.addCategoryObject('typeBinding', u'KeyStorageType', KeyStorageType)


# Complex type AuthnContextDeclarationBaseType with content type ELEMENT_ONLY
class AuthnContextDeclarationBaseType (pyxb.binding.basis.complexTypeDefinition):
    _TypeDefinition = None
    _ContentTypeTag = pyxb.binding.basis.complexTypeDefinition._CT_ELEMENT_ONLY
    _Abstract = False
    _ExpandedName = pyxb.namespace.ExpandedName(Namespace, u'AuthnContextDeclarationBaseType')
    # Base type is pyxb.binding.datatypes.anyType
    
    # Element {urn:oasis:names:tc:SAML:2.0:ac:classes:PasswordProtectedTransport}Identification uses Python identifier Identification
    __Identification = pyxb.binding.content.ElementUse(pyxb.namespace.ExpandedName(Namespace, u'Identification'), 'Identification', '__urnoasisnamestcSAML2_0acclassesPasswordProtectedTransport_AuthnContextDeclarationBaseType_urnoasisnamestcSAML2_0acclassesPasswordProtectedTransportIdentification', False)

    
    Identification = property(__Identification.value, __Identification.set, None, u'\n        Refers to those characteristics that describe the\n        processes and mechanisms\n        the Authentication Authority uses to initially create\n        an association between a Principal\n        and the identity (or name) by which the Principal will\n        be known\n      ')

    
    # Element {urn:oasis:names:tc:SAML:2.0:ac:classes:PasswordProtectedTransport}GoverningAgreements uses Python identifier GoverningAgreements
    __GoverningAgreements = pyxb.binding.content.ElementUse(pyxb.namespace.ExpandedName(Namespace, u'GoverningAgreements'), 'GoverningAgreements', '__urnoasisnamestcSAML2_0acclassesPasswordProtectedTransport_AuthnContextDeclarationBaseType_urnoasisnamestcSAML2_0acclassesPasswordProtectedTransportGoverningAgreements', False)

    
    GoverningAgreements = property(__GoverningAgreements.value, __GoverningAgreements.set, None, u'\n        Provides a mechanism for linking to external (likely\n        human readable) documents in which additional business agreements,\n        (e.g. liability constraints, obligations, etc) can be placed.\n      ')

    
    # Element {urn:oasis:names:tc:SAML:2.0:ac:classes:PasswordProtectedTransport}TechnicalProtection uses Python identifier TechnicalProtection
    __TechnicalProtection = pyxb.binding.content.ElementUse(pyxb.namespace.ExpandedName(Namespace, u'TechnicalProtection'), 'TechnicalProtection', '__urnoasisnamestcSAML2_0acclassesPasswordProtectedTransport_AuthnContextDeclarationBaseType_urnoasisnamestcSAML2_0acclassesPasswordProtectedTransportTechnicalProtection', False)

    
    TechnicalProtection = property(__TechnicalProtection.value, __TechnicalProtection.set, None, u"\n        Refers to those characterstics that describe how the\n        'secret' (the knowledge or possession\n        of which allows the Principal to authenticate to the\n        Authentication Authority) is kept secure\n      ")

    
    # Element {urn:oasis:names:tc:SAML:2.0:ac:classes:PasswordProtectedTransport}Extension uses Python identifier Extension
    __Extension = pyxb.binding.content.ElementUse(pyxb.namespace.ExpandedName(Namespace, u'Extension'), 'Extension', '__urnoasisnamestcSAML2_0acclassesPasswordProtectedTransport_AuthnContextDeclarationBaseType_urnoasisnamestcSAML2_0acclassesPasswordProtectedTransportExtension', True)

    
    Extension = property(__Extension.value, __Extension.set, None, None)

    
    # Element {urn:oasis:names:tc:SAML:2.0:ac:classes:PasswordProtectedTransport}OperationalProtection uses Python identifier OperationalProtection
    __OperationalProtection = pyxb.binding.content.ElementUse(pyxb.namespace.ExpandedName(Namespace, u'OperationalProtection'), 'OperationalProtection', '__urnoasisnamestcSAML2_0acclassesPasswordProtectedTransport_AuthnContextDeclarationBaseType_urnoasisnamestcSAML2_0acclassesPasswordProtectedTransportOperationalProtection', False)

    
    OperationalProtection = property(__OperationalProtection.value, __OperationalProtection.set, None, u'\n        Refers to those characteristics that describe\n        procedural security controls employed by the Authentication Authority.\n      ')

    
    # Element {urn:oasis:names:tc:SAML:2.0:ac:classes:PasswordProtectedTransport}AuthnMethod uses Python identifier AuthnMethod
    __AuthnMethod = pyxb.binding.content.ElementUse(pyxb.namespace.ExpandedName(Namespace, u'AuthnMethod'), 'AuthnMethod', '__urnoasisnamestcSAML2_0acclassesPasswordProtectedTransport_AuthnContextDeclarationBaseType_urnoasisnamestcSAML2_0acclassesPasswordProtectedTransportAuthnMethod', False)

    
    AuthnMethod = property(__AuthnMethod.value, __AuthnMethod.set, None, u'\n        Refers to those characteristics that define the\n        mechanisms by which the Principal authenticates to the Authentication\n        Authority.\n      ')

    
    # Attribute ID uses Python identifier ID
    __ID = pyxb.binding.content.AttributeUse(pyxb.namespace.ExpandedName(None, u'ID'), 'ID', '__urnoasisnamestcSAML2_0acclassesPasswordProtectedTransport_AuthnContextDeclarationBaseType_ID', pyxb.binding.datatypes.ID)
    
    ID = property(__ID.value, __ID.set, None, None)


    _ElementMap = {
        __Identification.name() : __Identification,
        __GoverningAgreements.name() : __GoverningAgreements,
        __TechnicalProtection.name() : __TechnicalProtection,
        __Extension.name() : __Extension,
        __OperationalProtection.name() : __OperationalProtection,
        __AuthnMethod.name() : __AuthnMethod
    }
    _AttributeMap = {
        __ID.name() : __ID
    }
Namespace.addCategoryObject('typeBinding', u'AuthnContextDeclarationBaseType', AuthnContextDeclarationBaseType)


# Complex type LengthType with content type EMPTY
class LengthType (pyxb.binding.basis.complexTypeDefinition):
    _TypeDefinition = None
    _ContentTypeTag = pyxb.binding.basis.complexTypeDefinition._CT_EMPTY
    _Abstract = False
    _ExpandedName = pyxb.namespace.ExpandedName(Namespace, u'LengthType')
    # Base type is pyxb.binding.datatypes.anyType
    
    # Attribute min uses Python identifier min
    __min = pyxb.binding.content.AttributeUse(pyxb.namespace.ExpandedName(None, u'min'), 'min', '__urnoasisnamestcSAML2_0acclassesPasswordProtectedTransport_LengthType_min', pyxb.binding.datatypes.integer, required=True)
    
    min = property(__min.value, __min.set, None, None)

    
    # Attribute max uses Python identifier max
    __max = pyxb.binding.content.AttributeUse(pyxb.namespace.ExpandedName(None, u'max'), 'max', '__urnoasisnamestcSAML2_0acclassesPasswordProtectedTransport_LengthType_max', pyxb.binding.datatypes.integer)
    
    max = property(__max.value, __max.set, None, None)


    _ElementMap = {
        
    }
    _AttributeMap = {
        __min.name() : __min,
        __max.name() : __max
    }
Namespace.addCategoryObject('typeBinding', u'LengthType', LengthType)


# Complex type AlphabetType with content type EMPTY
class AlphabetType (pyxb.binding.basis.complexTypeDefinition):
    _TypeDefinition = None
    _ContentTypeTag = pyxb.binding.basis.complexTypeDefinition._CT_EMPTY
    _Abstract = False
    _ExpandedName = pyxb.namespace.ExpandedName(Namespace, u'AlphabetType')
    # Base type is pyxb.binding.datatypes.anyType
    
    # Attribute excludedChars uses Python identifier excludedChars
    __excludedChars = pyxb.binding.content.AttributeUse(pyxb.namespace.ExpandedName(None, u'excludedChars'), 'excludedChars', '__urnoasisnamestcSAML2_0acclassesPasswordProtectedTransport_AlphabetType_excludedChars', pyxb.binding.datatypes.string)
    
    excludedChars = property(__excludedChars.value, __excludedChars.set, None, None)

    
    # Attribute case uses Python identifier case
    __case = pyxb.binding.content.AttributeUse(pyxb.namespace.ExpandedName(None, u'case'), 'case', '__urnoasisnamestcSAML2_0acclassesPasswordProtectedTransport_AlphabetType_case', pyxb.binding.datatypes.string)
    
    case = property(__case.value, __case.set, None, None)

    
    # Attribute requiredChars uses Python identifier requiredChars
    __requiredChars = pyxb.binding.content.AttributeUse(pyxb.namespace.ExpandedName(None, u'requiredChars'), 'requiredChars', '__urnoasisnamestcSAML2_0acclassesPasswordProtectedTransport_AlphabetType_requiredChars', pyxb.binding.datatypes.string, required=True)
    
    requiredChars = property(__requiredChars.value, __requiredChars.set, None, None)


    _ElementMap = {
        
    }
    _AttributeMap = {
        __excludedChars.name() : __excludedChars,
        __case.name() : __case,
        __requiredChars.name() : __requiredChars
    }
Namespace.addCategoryObject('typeBinding', u'AlphabetType', AlphabetType)


# Complex type CTD_ANON_ with content type EMPTY
class CTD_ANON_ (pyxb.binding.basis.complexTypeDefinition):
    _TypeDefinition = None
    _ContentTypeTag = pyxb.binding.basis.complexTypeDefinition._CT_EMPTY
    _Abstract = False
    _ExpandedName = None
    # Base type is pyxb.binding.datatypes.anyType
    
    # Attribute mechanism uses Python identifier mechanism
    __mechanism = pyxb.binding.content.AttributeUse(pyxb.namespace.ExpandedName(None, u'mechanism'), 'mechanism', '__urnoasisnamestcSAML2_0acclassesPasswordProtectedTransport_CTD_ANON__mechanism', STD_ANON_, required=True)
    
    mechanism = property(__mechanism.value, __mechanism.set, None, None)


    _ElementMap = {
        
    }
    _AttributeMap = {
        __mechanism.name() : __mechanism
    }



# Complex type ActivationLimitType with content type ELEMENT_ONLY
class ActivationLimitType (pyxb.binding.basis.complexTypeDefinition):
    _TypeDefinition = None
    _ContentTypeTag = pyxb.binding.basis.complexTypeDefinition._CT_ELEMENT_ONLY
    _Abstract = False
    _ExpandedName = pyxb.namespace.ExpandedName(Namespace, u'ActivationLimitType')
    # Base type is pyxb.binding.datatypes.anyType
    
    # Element {urn:oasis:names:tc:SAML:2.0:ac:classes:PasswordProtectedTransport}ActivationLimitDuration uses Python identifier ActivationLimitDuration
    __ActivationLimitDuration = pyxb.binding.content.ElementUse(pyxb.namespace.ExpandedName(Namespace, u'ActivationLimitDuration'), 'ActivationLimitDuration', '__urnoasisnamestcSAML2_0acclassesPasswordProtectedTransport_ActivationLimitType_urnoasisnamestcSAML2_0acclassesPasswordProtectedTransportActivationLimitDuration', False)

    
    ActivationLimitDuration = property(__ActivationLimitDuration.value, __ActivationLimitDuration.set, None, u'\n        This element indicates that the Key Activation Limit is\n        defined as a specific duration of time.\n      ')

    
    # Element {urn:oasis:names:tc:SAML:2.0:ac:classes:PasswordProtectedTransport}ActivationLimitUsages uses Python identifier ActivationLimitUsages
    __ActivationLimitUsages = pyxb.binding.content.ElementUse(pyxb.namespace.ExpandedName(Namespace, u'ActivationLimitUsages'), 'ActivationLimitUsages', '__urnoasisnamestcSAML2_0acclassesPasswordProtectedTransport_ActivationLimitType_urnoasisnamestcSAML2_0acclassesPasswordProtectedTransportActivationLimitUsages', False)

    
    ActivationLimitUsages = property(__ActivationLimitUsages.value, __ActivationLimitUsages.set, None, u'\n        This element indicates that the Key Activation Limit is\n        defined as a number of usages.\n      ')

    
    # Element {urn:oasis:names:tc:SAML:2.0:ac:classes:PasswordProtectedTransport}ActivationLimitSession uses Python identifier ActivationLimitSession
    __ActivationLimitSession = pyxb.binding.content.ElementUse(pyxb.namespace.ExpandedName(Namespace, u'ActivationLimitSession'), 'ActivationLimitSession', '__urnoasisnamestcSAML2_0acclassesPasswordProtectedTransport_ActivationLimitType_urnoasisnamestcSAML2_0acclassesPasswordProtectedTransportActivationLimitSession', False)

    
    ActivationLimitSession = property(__ActivationLimitSession.value, __ActivationLimitSession.set, None, u'\n        This element indicates that the Key Activation Limit is\n        the session.\n      ')


    _ElementMap = {
        __ActivationLimitDuration.name() : __ActivationLimitDuration,
        __ActivationLimitUsages.name() : __ActivationLimitUsages,
        __ActivationLimitSession.name() : __ActivationLimitSession
    }
    _AttributeMap = {
        
    }
Namespace.addCategoryObject('typeBinding', u'ActivationLimitType', ActivationLimitType)


# Complex type TimeSyncTokenType with content type EMPTY
class TimeSyncTokenType (pyxb.binding.basis.complexTypeDefinition):
    _TypeDefinition = None
    _ContentTypeTag = pyxb.binding.basis.complexTypeDefinition._CT_EMPTY
    _Abstract = False
    _ExpandedName = pyxb.namespace.ExpandedName(Namespace, u'TimeSyncTokenType')
    # Base type is pyxb.binding.datatypes.anyType
    
    # Attribute DeviceType uses Python identifier DeviceType
    __DeviceType = pyxb.binding.content.AttributeUse(pyxb.namespace.ExpandedName(None, u'DeviceType'), 'DeviceType', '__urnoasisnamestcSAML2_0acclassesPasswordProtectedTransport_TimeSyncTokenType_DeviceType', DeviceTypeType, required=True)
    
    DeviceType = property(__DeviceType.value, __DeviceType.set, None, None)

    
    # Attribute SeedLength uses Python identifier SeedLength
    __SeedLength = pyxb.binding.content.AttributeUse(pyxb.namespace.ExpandedName(None, u'SeedLength'), 'SeedLength', '__urnoasisnamestcSAML2_0acclassesPasswordProtectedTransport_TimeSyncTokenType_SeedLength', pyxb.binding.datatypes.integer, required=True)
    
    SeedLength = property(__SeedLength.value, __SeedLength.set, None, None)

    
    # Attribute DeviceInHand uses Python identifier DeviceInHand
    __DeviceInHand = pyxb.binding.content.AttributeUse(pyxb.namespace.ExpandedName(None, u'DeviceInHand'), 'DeviceInHand', '__urnoasisnamestcSAML2_0acclassesPasswordProtectedTransport_TimeSyncTokenType_DeviceInHand', booleanType, required=True)
    
    DeviceInHand = property(__DeviceInHand.value, __DeviceInHand.set, None, None)


    _ElementMap = {
        
    }
    _AttributeMap = {
        __DeviceType.name() : __DeviceType,
        __SeedLength.name() : __SeedLength,
        __DeviceInHand.name() : __DeviceInHand
    }
Namespace.addCategoryObject('typeBinding', u'TimeSyncTokenType', TimeSyncTokenType)


# Complex type ActivationLimitDurationType with content type EMPTY
class ActivationLimitDurationType (pyxb.binding.basis.complexTypeDefinition):
    _TypeDefinition = None
    _ContentTypeTag = pyxb.binding.basis.complexTypeDefinition._CT_EMPTY
    _Abstract = False
    _ExpandedName = pyxb.namespace.ExpandedName(Namespace, u'ActivationLimitDurationType')
    # Base type is pyxb.binding.datatypes.anyType
    
    # Attribute duration uses Python identifier duration
    __duration = pyxb.binding.content.AttributeUse(pyxb.namespace.ExpandedName(None, u'duration'), 'duration', '__urnoasisnamestcSAML2_0acclassesPasswordProtectedTransport_ActivationLimitDurationType_duration', pyxb.binding.datatypes.duration, required=True)
    
    duration = property(__duration.value, __duration.set, None, None)


    _ElementMap = {
        
    }
    _AttributeMap = {
        __duration.name() : __duration
    }
Namespace.addCategoryObject('typeBinding', u'ActivationLimitDurationType', ActivationLimitDurationType)


# Complex type ActivationLimitUsagesType with content type EMPTY
class ActivationLimitUsagesType (pyxb.binding.basis.complexTypeDefinition):
    _TypeDefinition = None
    _ContentTypeTag = pyxb.binding.basis.complexTypeDefinition._CT_EMPTY
    _Abstract = False
    _ExpandedName = pyxb.namespace.ExpandedName(Namespace, u'ActivationLimitUsagesType')
    # Base type is pyxb.binding.datatypes.anyType
    
    # Attribute number uses Python identifier number
    __number = pyxb.binding.content.AttributeUse(pyxb.namespace.ExpandedName(None, u'number'), 'number', '__urnoasisnamestcSAML2_0acclassesPasswordProtectedTransport_ActivationLimitUsagesType_number', pyxb.binding.datatypes.integer, required=True)
    
    number = property(__number.value, __number.set, None, None)


    _ElementMap = {
        
    }
    _AttributeMap = {
        __number.name() : __number
    }
Namespace.addCategoryObject('typeBinding', u'ActivationLimitUsagesType', ActivationLimitUsagesType)


# Complex type RestrictedLengthType with content type EMPTY
class RestrictedLengthType (LengthType):
    _TypeDefinition = None
    _ContentTypeTag = pyxb.binding.basis.complexTypeDefinition._CT_EMPTY
    _Abstract = False
    _ExpandedName = pyxb.namespace.ExpandedName(Namespace, u'RestrictedLengthType')
    # Base type is LengthType
    
    # Attribute min is restricted from parent
    
    # Attribute min uses Python identifier min
    __min = pyxb.binding.content.AttributeUse(pyxb.namespace.ExpandedName(None, u'min'), 'min', '__urnoasisnamestcSAML2_0acclassesPasswordProtectedTransport_LengthType_min', STD_ANON_2, required=True)
    
    min = property(__min.value, __min.set, None, None)

    
    # Attribute max is restricted from parent
    
    # Attribute max uses Python identifier max
    __max = pyxb.binding.content.AttributeUse(pyxb.namespace.ExpandedName(None, u'max'), 'max', '__urnoasisnamestcSAML2_0acclassesPasswordProtectedTransport_LengthType_max', pyxb.binding.datatypes.integer)
    
    max = property(__max.value, __max.set, None, None)


    _ElementMap = LengthType._ElementMap.copy()
    _ElementMap.update({
        
    })
    _AttributeMap = LengthType._AttributeMap.copy()
    _AttributeMap.update({
        __min.name() : __min,
        __max.name() : __max
    })
Namespace.addCategoryObject('typeBinding', u'RestrictedLengthType', RestrictedLengthType)


# Complex type ComplexAuthenticatorType with content type ELEMENT_ONLY
class ComplexAuthenticatorType (pyxb.binding.basis.complexTypeDefinition):
    _TypeDefinition = None
    _ContentTypeTag = pyxb.binding.basis.complexTypeDefinition._CT_ELEMENT_ONLY
    _Abstract = False
    _ExpandedName = pyxb.namespace.ExpandedName(Namespace, u'ComplexAuthenticatorType')
    # Base type is pyxb.binding.datatypes.anyType
    
    # Element {urn:oasis:names:tc:SAML:2.0:ac:classes:PasswordProtectedTransport}Extension uses Python identifier Extension
    __Extension = pyxb.binding.content.ElementUse(pyxb.namespace.ExpandedName(Namespace, u'Extension'), 'Extension', '__urnoasisnamestcSAML2_0acclassesPasswordProtectedTransport_ComplexAuthenticatorType_urnoasisnamestcSAML2_0acclassesPasswordProtectedTransportExtension', True)

    
    Extension = property(__Extension.value, __Extension.set, None, None)

    
    # Element {urn:oasis:names:tc:SAML:2.0:ac:classes:PasswordProtectedTransport}SubscriberLineNumber uses Python identifier SubscriberLineNumber
    __SubscriberLineNumber = pyxb.binding.content.ElementUse(pyxb.namespace.ExpandedName(Namespace, u'SubscriberLineNumber'), 'SubscriberLineNumber', '__urnoasisnamestcSAML2_0acclassesPasswordProtectedTransport_ComplexAuthenticatorType_urnoasisnamestcSAML2_0acclassesPasswordProtectedTransportSubscriberLineNumber', True)

    
    SubscriberLineNumber = property(__SubscriberLineNumber.value, __SubscriberLineNumber.set, None, None)

    
    # Element {urn:oasis:names:tc:SAML:2.0:ac:classes:PasswordProtectedTransport}IPAddress uses Python identifier IPAddress
    __IPAddress = pyxb.binding.content.ElementUse(pyxb.namespace.ExpandedName(Namespace, u'IPAddress'), 'IPAddress', '__urnoasisnamestcSAML2_0acclassesPasswordProtectedTransport_ComplexAuthenticatorType_urnoasisnamestcSAML2_0acclassesPasswordProtectedTransportIPAddress', True)

    
    IPAddress = property(__IPAddress.value, __IPAddress.set, None, u'\n        This element indicates that the Principal has been\n        authenticated through connection from a particular IP address.\n      ')

    
    # Element {urn:oasis:names:tc:SAML:2.0:ac:classes:PasswordProtectedTransport}ComplexAuthenticator uses Python identifier ComplexAuthenticator
    __ComplexAuthenticator = pyxb.binding.content.ElementUse(pyxb.namespace.ExpandedName(Namespace, u'ComplexAuthenticator'), 'ComplexAuthenticator', '__urnoasisnamestcSAML2_0acclassesPasswordProtectedTransport_ComplexAuthenticatorType_urnoasisnamestcSAML2_0acclassesPasswordProtectedTransportComplexAuthenticator', False)

    
    ComplexAuthenticator = property(__ComplexAuthenticator.value, __ComplexAuthenticator.set, None, u'\n        Supports Authenticators with nested combinations of\n        additional complexity.\n      ')

    
    # Element {urn:oasis:names:tc:SAML:2.0:ac:classes:PasswordProtectedTransport}ZeroKnowledge uses Python identifier ZeroKnowledge
    __ZeroKnowledge = pyxb.binding.content.ElementUse(pyxb.namespace.ExpandedName(Namespace, u'ZeroKnowledge'), 'ZeroKnowledge', '__urnoasisnamestcSAML2_0acclassesPasswordProtectedTransport_ComplexAuthenticatorType_urnoasisnamestcSAML2_0acclassesPasswordProtectedTransportZeroKnowledge', True)

    
    ZeroKnowledge = property(__ZeroKnowledge.value, __ZeroKnowledge.set, None, u'\n        This element indicates that the Principal has been\n        authenticated by a zero knowledge technique as specified in ISO/IEC\n        9798-5.\n      ')

    
    # Element {urn:oasis:names:tc:SAML:2.0:ac:classes:PasswordProtectedTransport}DigSig uses Python identifier DigSig
    __DigSig = pyxb.binding.content.ElementUse(pyxb.namespace.ExpandedName(Namespace, u'DigSig'), 'DigSig', '__urnoasisnamestcSAML2_0acclassesPasswordProtectedTransport_ComplexAuthenticatorType_urnoasisnamestcSAML2_0acclassesPasswordProtectedTransportDigSig', True)

    
    DigSig = property(__DigSig.value, __DigSig.set, None, u'\n        This element indicates that the Principal has been\n        authenticated by a mechanism which involves the Principal computing a\n        digital signature over at least challenge data provided by the IdP.\n      ')

    
    # Element {urn:oasis:names:tc:SAML:2.0:ac:classes:PasswordProtectedTransport}RestrictedPassword uses Python identifier RestrictedPassword
    __RestrictedPassword = pyxb.binding.content.ElementUse(pyxb.namespace.ExpandedName(Namespace, u'RestrictedPassword'), 'RestrictedPassword', '__urnoasisnamestcSAML2_0acclassesPasswordProtectedTransport_ComplexAuthenticatorType_urnoasisnamestcSAML2_0acclassesPasswordProtectedTransportRestrictedPassword', True)

    
    RestrictedPassword = property(__RestrictedPassword.value, __RestrictedPassword.set, None, None)

    
    # Element {urn:oasis:names:tc:SAML:2.0:ac:classes:PasswordProtectedTransport}UserSuffix uses Python identifier UserSuffix
    __UserSuffix = pyxb.binding.content.ElementUse(pyxb.namespace.ExpandedName(Namespace, u'UserSuffix'), 'UserSuffix', '__urnoasisnamestcSAML2_0acclassesPasswordProtectedTransport_ComplexAuthenticatorType_urnoasisnamestcSAML2_0acclassesPasswordProtectedTransportUserSuffix', True)

    
    UserSuffix = property(__UserSuffix.value, __UserSuffix.set, None, None)

    
    # Element {urn:oasis:names:tc:SAML:2.0:ac:classes:PasswordProtectedTransport}AsymmetricDecryption uses Python identifier AsymmetricDecryption
    __AsymmetricDecryption = pyxb.binding.content.ElementUse(pyxb.namespace.ExpandedName(Namespace, u'AsymmetricDecryption'), 'AsymmetricDecryption', '__urnoasisnamestcSAML2_0acclassesPasswordProtectedTransport_ComplexAuthenticatorType_urnoasisnamestcSAML2_0acclassesPasswordProtectedTransportAsymmetricDecryption', True)

    
    AsymmetricDecryption = property(__AsymmetricDecryption.value, __AsymmetricDecryption.set, None, u"\n        The local system has a private key but it is used\n        in decryption mode, rather than signature mode. For example, the\n        Authentication Authority generates a secret and encrypts it using the\n        local system's public key: the local system then proves it has\n        decrypted the secret.\n      ")

    
    # Element {urn:oasis:names:tc:SAML:2.0:ac:classes:PasswordProtectedTransport}SharedSecretChallengeResponse uses Python identifier SharedSecretChallengeResponse
    __SharedSecretChallengeResponse = pyxb.binding.content.ElementUse(pyxb.namespace.ExpandedName(Namespace, u'SharedSecretChallengeResponse'), 'SharedSecretChallengeResponse', '__urnoasisnamestcSAML2_0acclassesPasswordProtectedTransport_ComplexAuthenticatorType_urnoasisnamestcSAML2_0acclassesPasswordProtectedTransportSharedSecretChallengeResponse', True)

    
    SharedSecretChallengeResponse = property(__SharedSecretChallengeResponse.value, __SharedSecretChallengeResponse.set, None, None)

    
    # Element {urn:oasis:names:tc:SAML:2.0:ac:classes:PasswordProtectedTransport}Password uses Python identifier Password
    __Password = pyxb.binding.content.ElementUse(pyxb.namespace.ExpandedName(Namespace, u'Password'), 'Password', '__urnoasisnamestcSAML2_0acclassesPasswordProtectedTransport_ComplexAuthenticatorType_urnoasisnamestcSAML2_0acclassesPasswordProtectedTransportPassword', True)

    
    Password = property(__Password.value, __Password.set, None, u'\n        This element indicates that a password (or passphrase)\n        has been used to\n        authenticate the Principal to a remote system.\n      ')

    
    # Element {urn:oasis:names:tc:SAML:2.0:ac:classes:PasswordProtectedTransport}PreviousSession uses Python identifier PreviousSession
    __PreviousSession = pyxb.binding.content.ElementUse(pyxb.namespace.ExpandedName(Namespace, u'PreviousSession'), 'PreviousSession', '__urnoasisnamestcSAML2_0acclassesPasswordProtectedTransport_ComplexAuthenticatorType_urnoasisnamestcSAML2_0acclassesPasswordProtectedTransportPreviousSession', True)

    
    PreviousSession = property(__PreviousSession.value, __PreviousSession.set, None, u'\n        Indicates that the Principal has been strongly\n        authenticated in a previous session during which the IdP has set a\n        cookie in the UA. During the present session the Principal has only\n        been authenticated by the UA returning the cookie to the IdP.\n      ')

    
    # Element {urn:oasis:names:tc:SAML:2.0:ac:classes:PasswordProtectedTransport}AsymmetricKeyAgreement uses Python identifier AsymmetricKeyAgreement
    __AsymmetricKeyAgreement = pyxb.binding.content.ElementUse(pyxb.namespace.ExpandedName(Namespace, u'AsymmetricKeyAgreement'), 'AsymmetricKeyAgreement', '__urnoasisnamestcSAML2_0acclassesPasswordProtectedTransport_ComplexAuthenticatorType_urnoasisnamestcSAML2_0acclassesPasswordProtectedTransportAsymmetricKeyAgreement', True)

    
    AsymmetricKeyAgreement = property(__AsymmetricKeyAgreement.value, __AsymmetricKeyAgreement.set, None, u'\n        The local system has a private key and uses it for\n        shared secret key agreement with the Authentication Authority (e.g.\n        via Diffie Helman).\n      ')

    
    # Element {urn:oasis:names:tc:SAML:2.0:ac:classes:PasswordProtectedTransport}SharedSecretDynamicPlaintext uses Python identifier SharedSecretDynamicPlaintext
    __SharedSecretDynamicPlaintext = pyxb.binding.content.ElementUse(pyxb.namespace.ExpandedName(Namespace, u'SharedSecretDynamicPlaintext'), 'SharedSecretDynamicPlaintext', '__urnoasisnamestcSAML2_0acclassesPasswordProtectedTransport_ComplexAuthenticatorType_urnoasisnamestcSAML2_0acclassesPasswordProtectedTransportSharedSecretDynamicPlaintext', True)

    
    SharedSecretDynamicPlaintext = property(__SharedSecretDynamicPlaintext.value, __SharedSecretDynamicPlaintext.set, None, u'\n        The local system and Authentication Authority\n        share a secret key. The local system uses this to encrypt a\n        randomised string to pass to the Authentication Authority.\n      ')

    
    # Element {urn:oasis:names:tc:SAML:2.0:ac:classes:PasswordProtectedTransport}ResumeSession uses Python identifier ResumeSession
    __ResumeSession = pyxb.binding.content.ElementUse(pyxb.namespace.ExpandedName(Namespace, u'ResumeSession'), 'ResumeSession', '__urnoasisnamestcSAML2_0acclassesPasswordProtectedTransport_ComplexAuthenticatorType_urnoasisnamestcSAML2_0acclassesPasswordProtectedTransportResumeSession', True)

    
    ResumeSession = property(__ResumeSession.value, __ResumeSession.set, None, u'\n        Rather like PreviousSession but using stronger\n        security. A secret that was established in a previous session with\n        the Authentication Authority has been cached by the local system and\n        is now re-used (e.g. a Master Secret is used to derive new session\n        keys in TLS, SSL, WTLS).\n      ')


    _ElementMap = {
        __Extension.name() : __Extension,
        __SubscriberLineNumber.name() : __SubscriberLineNumber,
        __IPAddress.name() : __IPAddress,
        __ComplexAuthenticator.name() : __ComplexAuthenticator,
        __ZeroKnowledge.name() : __ZeroKnowledge,
        __DigSig.name() : __DigSig,
        __RestrictedPassword.name() : __RestrictedPassword,
        __UserSuffix.name() : __UserSuffix,
        __AsymmetricDecryption.name() : __AsymmetricDecryption,
        __SharedSecretChallengeResponse.name() : __SharedSecretChallengeResponse,
        __Password.name() : __Password,
        __PreviousSession.name() : __PreviousSession,
        __AsymmetricKeyAgreement.name() : __AsymmetricKeyAgreement,
        __SharedSecretDynamicPlaintext.name() : __SharedSecretDynamicPlaintext,
        __ResumeSession.name() : __ResumeSession
    }
    _AttributeMap = {
        
    }
Namespace.addCategoryObject('typeBinding', u'ComplexAuthenticatorType', ComplexAuthenticatorType)


# Complex type AuthenticatorTransportProtocolType with content type ELEMENT_ONLY
class AuthenticatorTransportProtocolType (pyxb.binding.basis.complexTypeDefinition):
    _TypeDefinition = None
    _ContentTypeTag = pyxb.binding.basis.complexTypeDefinition._CT_ELEMENT_ONLY
    _Abstract = False
    _ExpandedName = pyxb.namespace.ExpandedName(Namespace, u'AuthenticatorTransportProtocolType')
    # Base type is pyxb.binding.datatypes.anyType
    
    # Element {urn:oasis:names:tc:SAML:2.0:ac:classes:PasswordProtectedTransport}MobileNetworkRadioEncryption uses Python identifier MobileNetworkRadioEncryption
    __MobileNetworkRadioEncryption = pyxb.binding.content.ElementUse(pyxb.namespace.ExpandedName(Namespace, u'MobileNetworkRadioEncryption'), 'MobileNetworkRadioEncryption', '__urnoasisnamestcSAML2_0acclassesPasswordProtectedTransport_AuthenticatorTransportProtocolType_urnoasisnamestcSAML2_0acclassesPasswordProtectedTransportMobileNetworkRadioEncryption', False)

    
    MobileNetworkRadioEncryption = property(__MobileNetworkRadioEncryption.value, __MobileNetworkRadioEncryption.set, None, None)

    
    # Element {urn:oasis:names:tc:SAML:2.0:ac:classes:PasswordProtectedTransport}Extension uses Python identifier Extension
    __Extension = pyxb.binding.content.ElementUse(pyxb.namespace.ExpandedName(Namespace, u'Extension'), 'Extension', '__urnoasisnamestcSAML2_0acclassesPasswordProtectedTransport_AuthenticatorTransportProtocolType_urnoasisnamestcSAML2_0acclassesPasswordProtectedTransportExtension', True)

    
    Extension = property(__Extension.value, __Extension.set, None, None)

    
    # Element {urn:oasis:names:tc:SAML:2.0:ac:classes:PasswordProtectedTransport}MobileNetworkEndToEndEncryption uses Python identifier MobileNetworkEndToEndEncryption
    __MobileNetworkEndToEndEncryption = pyxb.binding.content.ElementUse(pyxb.namespace.ExpandedName(Namespace, u'MobileNetworkEndToEndEncryption'), 'MobileNetworkEndToEndEncryption', '__urnoasisnamestcSAML2_0acclassesPasswordProtectedTransport_AuthenticatorTransportProtocolType_urnoasisnamestcSAML2_0acclassesPasswordProtectedTransportMobileNetworkEndToEndEncryption', False)

    
    MobileNetworkEndToEndEncryption = property(__MobileNetworkEndToEndEncryption.value, __MobileNetworkEndToEndEncryption.set, None, None)

    
    # Element {urn:oasis:names:tc:SAML:2.0:ac:classes:PasswordProtectedTransport}SSL uses Python identifier SSL
    __SSL = pyxb.binding.content.ElementUse(pyxb.namespace.ExpandedName(Namespace, u'SSL'), 'SSL', '__urnoasisnamestcSAML2_0acclassesPasswordProtectedTransport_AuthenticatorTransportProtocolType_urnoasisnamestcSAML2_0acclassesPasswordProtectedTransportSSL', False)

    
    SSL = property(__SSL.value, __SSL.set, None, u'\n        This element indicates that the Authenticator has been\n        transmitted using a transport mechnanism protected by an SSL or TLS\n        session.\n      ')

    
    # Element {urn:oasis:names:tc:SAML:2.0:ac:classes:PasswordProtectedTransport}WTLS uses Python identifier WTLS
    __WTLS = pyxb.binding.content.ElementUse(pyxb.namespace.ExpandedName(Namespace, u'WTLS'), 'WTLS', '__urnoasisnamestcSAML2_0acclassesPasswordProtectedTransport_AuthenticatorTransportProtocolType_urnoasisnamestcSAML2_0acclassesPasswordProtectedTransportWTLS', False)

    
    WTLS = property(__WTLS.value, __WTLS.set, None, u'\n        This element indicates that the Authenticator has been\n        transmitted using a transport mechanism protected by a WTLS session.\n      ')

    
    # Element {urn:oasis:names:tc:SAML:2.0:ac:classes:PasswordProtectedTransport}IPSec uses Python identifier IPSec
    __IPSec = pyxb.binding.content.ElementUse(pyxb.namespace.ExpandedName(Namespace, u'IPSec'), 'IPSec', '__urnoasisnamestcSAML2_0acclassesPasswordProtectedTransport_AuthenticatorTransportProtocolType_urnoasisnamestcSAML2_0acclassesPasswordProtectedTransportIPSec', False)

    
    IPSec = property(__IPSec.value, __IPSec.set, None, u'\n        This element indicates that the Authenticator has been\n        transmitted using a transport mechanism protected by an IPSEC session.\n      ')

    
    # Element {urn:oasis:names:tc:SAML:2.0:ac:classes:PasswordProtectedTransport}MobileNetworkNoEncryption uses Python identifier MobileNetworkNoEncryption
    __MobileNetworkNoEncryption = pyxb.binding.content.ElementUse(pyxb.namespace.ExpandedName(Namespace, u'MobileNetworkNoEncryption'), 'MobileNetworkNoEncryption', '__urnoasisnamestcSAML2_0acclassesPasswordProtectedTransport_AuthenticatorTransportProtocolType_urnoasisnamestcSAML2_0acclassesPasswordProtectedTransportMobileNetworkNoEncryption', False)

    
    MobileNetworkNoEncryption = property(__MobileNetworkNoEncryption.value, __MobileNetworkNoEncryption.set, None, u'\n        This element indicates that the Authenticator has been\n        transmitted solely across a mobile network using no additional\n        security mechanism.\n      ')


    _ElementMap = {
        __MobileNetworkRadioEncryption.name() : __MobileNetworkRadioEncryption,
        __Extension.name() : __Extension,
        __MobileNetworkEndToEndEncryption.name() : __MobileNetworkEndToEndEncryption,
        __SSL.name() : __SSL,
        __WTLS.name() : __WTLS,
        __IPSec.name() : __IPSec,
        __MobileNetworkNoEncryption.name() : __MobileNetworkNoEncryption
    }
    _AttributeMap = {
        
    }
Namespace.addCategoryObject('typeBinding', u'AuthenticatorTransportProtocolType', AuthenticatorTransportProtocolType)


# Complex type OperationalProtectionType with content type ELEMENT_ONLY
class OperationalProtectionType (pyxb.binding.basis.complexTypeDefinition):
    _TypeDefinition = None
    _ContentTypeTag = pyxb.binding.basis.complexTypeDefinition._CT_ELEMENT_ONLY
    _Abstract = False
    _ExpandedName = pyxb.namespace.ExpandedName(Namespace, u'OperationalProtectionType')
    # Base type is pyxb.binding.datatypes.anyType
    
    # Element {urn:oasis:names:tc:SAML:2.0:ac:classes:PasswordProtectedTransport}DeactivationCallCenter uses Python identifier DeactivationCallCenter
    __DeactivationCallCenter = pyxb.binding.content.ElementUse(pyxb.namespace.ExpandedName(Namespace, u'DeactivationCallCenter'), 'DeactivationCallCenter', '__urnoasisnamestcSAML2_0acclassesPasswordProtectedTransport_OperationalProtectionType_urnoasisnamestcSAML2_0acclassesPasswordProtectedTransportDeactivationCallCenter', False)

    
    DeactivationCallCenter = property(__DeactivationCallCenter.value, __DeactivationCallCenter.set, None, None)

    
    # Element {urn:oasis:names:tc:SAML:2.0:ac:classes:PasswordProtectedTransport}Extension uses Python identifier Extension
    __Extension = pyxb.binding.content.ElementUse(pyxb.namespace.ExpandedName(Namespace, u'Extension'), 'Extension', '__urnoasisnamestcSAML2_0acclassesPasswordProtectedTransport_OperationalProtectionType_urnoasisnamestcSAML2_0acclassesPasswordProtectedTransportExtension', True)

    
    Extension = property(__Extension.value, __Extension.set, None, None)

    
    # Element {urn:oasis:names:tc:SAML:2.0:ac:classes:PasswordProtectedTransport}SecurityAudit uses Python identifier SecurityAudit
    __SecurityAudit = pyxb.binding.content.ElementUse(pyxb.namespace.ExpandedName(Namespace, u'SecurityAudit'), 'SecurityAudit', '__urnoasisnamestcSAML2_0acclassesPasswordProtectedTransport_OperationalProtectionType_urnoasisnamestcSAML2_0acclassesPasswordProtectedTransportSecurityAudit', False)

    
    SecurityAudit = property(__SecurityAudit.value, __SecurityAudit.set, None, None)


    _ElementMap = {
        __DeactivationCallCenter.name() : __DeactivationCallCenter,
        __Extension.name() : __Extension,
        __SecurityAudit.name() : __SecurityAudit
    }
    _AttributeMap = {
        
    }
Namespace.addCategoryObject('typeBinding', u'OperationalProtectionType', OperationalProtectionType)


# Complex type SecurityAuditType with content type ELEMENT_ONLY
class SecurityAuditType (pyxb.binding.basis.complexTypeDefinition):
    _TypeDefinition = None
    _ContentTypeTag = pyxb.binding.basis.complexTypeDefinition._CT_ELEMENT_ONLY
    _Abstract = False
    _ExpandedName = pyxb.namespace.ExpandedName(Namespace, u'SecurityAuditType')
    # Base type is pyxb.binding.datatypes.anyType
    
    # Element {urn:oasis:names:tc:SAML:2.0:ac:classes:PasswordProtectedTransport}Extension uses Python identifier Extension
    __Extension = pyxb.binding.content.ElementUse(pyxb.namespace.ExpandedName(Namespace, u'Extension'), 'Extension', '__urnoasisnamestcSAML2_0acclassesPasswordProtectedTransport_SecurityAuditType_urnoasisnamestcSAML2_0acclassesPasswordProtectedTransportExtension', True)

    
    Extension = property(__Extension.value, __Extension.set, None, None)

    
    # Element {urn:oasis:names:tc:SAML:2.0:ac:classes:PasswordProtectedTransport}SwitchAudit uses Python identifier SwitchAudit
    __SwitchAudit = pyxb.binding.content.ElementUse(pyxb.namespace.ExpandedName(Namespace, u'SwitchAudit'), 'SwitchAudit', '__urnoasisnamestcSAML2_0acclassesPasswordProtectedTransport_SecurityAuditType_urnoasisnamestcSAML2_0acclassesPasswordProtectedTransportSwitchAudit', False)

    
    SwitchAudit = property(__SwitchAudit.value, __SwitchAudit.set, None, None)


    _ElementMap = {
        __Extension.name() : __Extension,
        __SwitchAudit.name() : __SwitchAudit
    }
    _AttributeMap = {
        
    }
Namespace.addCategoryObject('typeBinding', u'SecurityAuditType', SecurityAuditType)


# Complex type GoverningAgreementsType with content type ELEMENT_ONLY
class GoverningAgreementsType (pyxb.binding.basis.complexTypeDefinition):
    _TypeDefinition = None
    _ContentTypeTag = pyxb.binding.basis.complexTypeDefinition._CT_ELEMENT_ONLY
    _Abstract = False
    _ExpandedName = pyxb.namespace.ExpandedName(Namespace, u'GoverningAgreementsType')
    # Base type is pyxb.binding.datatypes.anyType
    
    # Element {urn:oasis:names:tc:SAML:2.0:ac:classes:PasswordProtectedTransport}GoverningAgreementRef uses Python identifier GoverningAgreementRef
    __GoverningAgreementRef = pyxb.binding.content.ElementUse(pyxb.namespace.ExpandedName(Namespace, u'GoverningAgreementRef'), 'GoverningAgreementRef', '__urnoasisnamestcSAML2_0acclassesPasswordProtectedTransport_GoverningAgreementsType_urnoasisnamestcSAML2_0acclassesPasswordProtectedTransportGoverningAgreementRef', True)

    
    GoverningAgreementRef = property(__GoverningAgreementRef.value, __GoverningAgreementRef.set, None, None)


    _ElementMap = {
        __GoverningAgreementRef.name() : __GoverningAgreementRef
    }
    _AttributeMap = {
        
    }
Namespace.addCategoryObject('typeBinding', u'GoverningAgreementsType', GoverningAgreementsType)


# Complex type TokenType with content type ELEMENT_ONLY
class TokenType (pyxb.binding.basis.complexTypeDefinition):
    _TypeDefinition = None
    _ContentTypeTag = pyxb.binding.basis.complexTypeDefinition._CT_ELEMENT_ONLY
    _Abstract = False
    _ExpandedName = pyxb.namespace.ExpandedName(Namespace, u'TokenType')
    # Base type is pyxb.binding.datatypes.anyType
    
    # Element {urn:oasis:names:tc:SAML:2.0:ac:classes:PasswordProtectedTransport}Extension uses Python identifier Extension
    __Extension = pyxb.binding.content.ElementUse(pyxb.namespace.ExpandedName(Namespace, u'Extension'), 'Extension', '__urnoasisnamestcSAML2_0acclassesPasswordProtectedTransport_TokenType_urnoasisnamestcSAML2_0acclassesPasswordProtectedTransportExtension', True)

    
    Extension = property(__Extension.value, __Extension.set, None, None)

    
    # Element {urn:oasis:names:tc:SAML:2.0:ac:classes:PasswordProtectedTransport}TimeSyncToken uses Python identifier TimeSyncToken
    __TimeSyncToken = pyxb.binding.content.ElementUse(pyxb.namespace.ExpandedName(Namespace, u'TimeSyncToken'), 'TimeSyncToken', '__urnoasisnamestcSAML2_0acclassesPasswordProtectedTransport_TokenType_urnoasisnamestcSAML2_0acclassesPasswordProtectedTransportTimeSyncToken', False)

    
    TimeSyncToken = property(__TimeSyncToken.value, __TimeSyncToken.set, None, u'\n        This element indicates that a time synchronization\n        token is used to identify the Principal. hardware -\n        the time synchonization\n        token has been implemented in hardware. software - the\n        time synchronization\n        token has been implemented in software. SeedLength -\n        the length, in bits, of the\n        random seed used in the time synchronization token.\n      ')


    _ElementMap = {
        __Extension.name() : __Extension,
        __TimeSyncToken.name() : __TimeSyncToken
    }
    _AttributeMap = {
        
    }
Namespace.addCategoryObject('typeBinding', u'TokenType', TokenType)


# Complex type IdentificationType with content type ELEMENT_ONLY
class IdentificationType (pyxb.binding.basis.complexTypeDefinition):
    _TypeDefinition = None
    _ContentTypeTag = pyxb.binding.basis.complexTypeDefinition._CT_ELEMENT_ONLY
    _Abstract = False
    _ExpandedName = pyxb.namespace.ExpandedName(Namespace, u'IdentificationType')
    # Base type is pyxb.binding.datatypes.anyType
    
    # Element {urn:oasis:names:tc:SAML:2.0:ac:classes:PasswordProtectedTransport}Extension uses Python identifier Extension
    __Extension = pyxb.binding.content.ElementUse(pyxb.namespace.ExpandedName(Namespace, u'Extension'), 'Extension', '__urnoasisnamestcSAML2_0acclassesPasswordProtectedTransport_IdentificationType_urnoasisnamestcSAML2_0acclassesPasswordProtectedTransportExtension', True)

    
    Extension = property(__Extension.value, __Extension.set, None, None)

    
    # Element {urn:oasis:names:tc:SAML:2.0:ac:classes:PasswordProtectedTransport}WrittenConsent uses Python identifier WrittenConsent
    __WrittenConsent = pyxb.binding.content.ElementUse(pyxb.namespace.ExpandedName(Namespace, u'WrittenConsent'), 'WrittenConsent', '__urnoasisnamestcSAML2_0acclassesPasswordProtectedTransport_IdentificationType_urnoasisnamestcSAML2_0acclassesPasswordProtectedTransportWrittenConsent', False)

    
    WrittenConsent = property(__WrittenConsent.value, __WrittenConsent.set, None, None)

    
    # Element {urn:oasis:names:tc:SAML:2.0:ac:classes:PasswordProtectedTransport}GoverningAgreements uses Python identifier GoverningAgreements
    __GoverningAgreements = pyxb.binding.content.ElementUse(pyxb.namespace.ExpandedName(Namespace, u'GoverningAgreements'), 'GoverningAgreements', '__urnoasisnamestcSAML2_0acclassesPasswordProtectedTransport_IdentificationType_urnoasisnamestcSAML2_0acclassesPasswordProtectedTransportGoverningAgreements', False)

    
    GoverningAgreements = property(__GoverningAgreements.value, __GoverningAgreements.set, None, u'\n        Provides a mechanism for linking to external (likely\n        human readable) documents in which additional business agreements,\n        (e.g. liability constraints, obligations, etc) can be placed.\n      ')

    
    # Element {urn:oasis:names:tc:SAML:2.0:ac:classes:PasswordProtectedTransport}PhysicalVerification uses Python identifier PhysicalVerification
    __PhysicalVerification = pyxb.binding.content.ElementUse(pyxb.namespace.ExpandedName(Namespace, u'PhysicalVerification'), 'PhysicalVerification', '__urnoasisnamestcSAML2_0acclassesPasswordProtectedTransport_IdentificationType_urnoasisnamestcSAML2_0acclassesPasswordProtectedTransportPhysicalVerification', False)

    
    PhysicalVerification = property(__PhysicalVerification.value, __PhysicalVerification.set, None, u'\n        This element indicates that identification has been\n        performed in a physical\n        face-to-face meeting with the principal and not in an\n        online manner.\n      ')

    
    # Attribute nym uses Python identifier nym
    __nym = pyxb.binding.content.AttributeUse(pyxb.namespace.ExpandedName(None, u'nym'), 'nym', '__urnoasisnamestcSAML2_0acclassesPasswordProtectedTransport_IdentificationType_nym', nymType)
    
    nym = property(__nym.value, __nym.set, None, u'\n          This attribute indicates whether or not the\n          Identification mechanisms allow the actions of the Principal to be\n          linked to an actual end user.\n        ')


    _ElementMap = {
        __Extension.name() : __Extension,
        __WrittenConsent.name() : __WrittenConsent,
        __GoverningAgreements.name() : __GoverningAgreements,
        __PhysicalVerification.name() : __PhysicalVerification
    }
    _AttributeMap = {
        __nym.name() : __nym
    }
Namespace.addCategoryObject('typeBinding', u'IdentificationType', IdentificationType)


# Complex type PrivateKeyProtectionType with content type ELEMENT_ONLY
class PrivateKeyProtectionType (pyxb.binding.basis.complexTypeDefinition):
    _TypeDefinition = None
    _ContentTypeTag = pyxb.binding.basis.complexTypeDefinition._CT_ELEMENT_ONLY
    _Abstract = False
    _ExpandedName = pyxb.namespace.ExpandedName(Namespace, u'PrivateKeyProtectionType')
    # Base type is pyxb.binding.datatypes.anyType
    
    # Element {urn:oasis:names:tc:SAML:2.0:ac:classes:PasswordProtectedTransport}KeyActivation uses Python identifier KeyActivation
    __KeyActivation = pyxb.binding.content.ElementUse(pyxb.namespace.ExpandedName(Namespace, u'KeyActivation'), 'KeyActivation', '__urnoasisnamestcSAML2_0acclassesPasswordProtectedTransport_PrivateKeyProtectionType_urnoasisnamestcSAML2_0acclassesPasswordProtectedTransportKeyActivation', False)

    
    KeyActivation = property(__KeyActivation.value, __KeyActivation.set, None, u'The actions that must be performed\n        before the private key can be used. ')

    
    # Element {urn:oasis:names:tc:SAML:2.0:ac:classes:PasswordProtectedTransport}KeyStorage uses Python identifier KeyStorage
    __KeyStorage = pyxb.binding.content.ElementUse(pyxb.namespace.ExpandedName(Namespace, u'KeyStorage'), 'KeyStorage', '__urnoasisnamestcSAML2_0acclassesPasswordProtectedTransport_PrivateKeyProtectionType_urnoasisnamestcSAML2_0acclassesPasswordProtectedTransportKeyStorage', False)

    
    KeyStorage = property(__KeyStorage.value, __KeyStorage.set, None, u'\n        In which medium is the key stored.\n        memory - the key is stored in memory.\n        smartcard - the key is stored in a smartcard.\n        token - the key is stored in a hardware token.\n        MobileDevice - the key is stored in a mobile device.\n        MobileAuthCard - the key is stored in a mobile\n        authentication card.\n      ')

    
    # Element {urn:oasis:names:tc:SAML:2.0:ac:classes:PasswordProtectedTransport}KeySharing uses Python identifier KeySharing
    __KeySharing = pyxb.binding.content.ElementUse(pyxb.namespace.ExpandedName(Namespace, u'KeySharing'), 'KeySharing', '__urnoasisnamestcSAML2_0acclassesPasswordProtectedTransport_PrivateKeyProtectionType_urnoasisnamestcSAML2_0acclassesPasswordProtectedTransportKeySharing', False)

    
    KeySharing = property(__KeySharing.value, __KeySharing.set, None, u'Whether or not the private key is shared\n        with the certificate authority.')

    
    # Element {urn:oasis:names:tc:SAML:2.0:ac:classes:PasswordProtectedTransport}Extension uses Python identifier Extension
    __Extension = pyxb.binding.content.ElementUse(pyxb.namespace.ExpandedName(Namespace, u'Extension'), 'Extension', '__urnoasisnamestcSAML2_0acclassesPasswordProtectedTransport_PrivateKeyProtectionType_urnoasisnamestcSAML2_0acclassesPasswordProtectedTransportExtension', True)

    
    Extension = property(__Extension.value, __Extension.set, None, None)


    _ElementMap = {
        __KeyActivation.name() : __KeyActivation,
        __KeyStorage.name() : __KeyStorage,
        __KeySharing.name() : __KeySharing,
        __Extension.name() : __Extension
    }
    _AttributeMap = {
        
    }
Namespace.addCategoryObject('typeBinding', u'PrivateKeyProtectionType', PrivateKeyProtectionType)


# Complex type SecretKeyProtectionType with content type ELEMENT_ONLY
class SecretKeyProtectionType (pyxb.binding.basis.complexTypeDefinition):
    _TypeDefinition = None
    _ContentTypeTag = pyxb.binding.basis.complexTypeDefinition._CT_ELEMENT_ONLY
    _Abstract = False
    _ExpandedName = pyxb.namespace.ExpandedName(Namespace, u'SecretKeyProtectionType')
    # Base type is pyxb.binding.datatypes.anyType
    
    # Element {urn:oasis:names:tc:SAML:2.0:ac:classes:PasswordProtectedTransport}Extension uses Python identifier Extension
    __Extension = pyxb.binding.content.ElementUse(pyxb.namespace.ExpandedName(Namespace, u'Extension'), 'Extension', '__urnoasisnamestcSAML2_0acclassesPasswordProtectedTransport_SecretKeyProtectionType_urnoasisnamestcSAML2_0acclassesPasswordProtectedTransportExtension', True)

    
    Extension = property(__Extension.value, __Extension.set, None, None)

    
    # Element {urn:oasis:names:tc:SAML:2.0:ac:classes:PasswordProtectedTransport}KeyActivation uses Python identifier KeyActivation
    __KeyActivation = pyxb.binding.content.ElementUse(pyxb.namespace.ExpandedName(Namespace, u'KeyActivation'), 'KeyActivation', '__urnoasisnamestcSAML2_0acclassesPasswordProtectedTransport_SecretKeyProtectionType_urnoasisnamestcSAML2_0acclassesPasswordProtectedTransportKeyActivation', False)

    
    KeyActivation = property(__KeyActivation.value, __KeyActivation.set, None, u'The actions that must be performed\n        before the private key can be used. ')

    
    # Element {urn:oasis:names:tc:SAML:2.0:ac:classes:PasswordProtectedTransport}KeyStorage uses Python identifier KeyStorage
    __KeyStorage = pyxb.binding.content.ElementUse(pyxb.namespace.ExpandedName(Namespace, u'KeyStorage'), 'KeyStorage', '__urnoasisnamestcSAML2_0acclassesPasswordProtectedTransport_SecretKeyProtectionType_urnoasisnamestcSAML2_0acclassesPasswordProtectedTransportKeyStorage', False)

    
    KeyStorage = property(__KeyStorage.value, __KeyStorage.set, None, u'\n        In which medium is the key stored.\n        memory - the key is stored in memory.\n        smartcard - the key is stored in a smartcard.\n        token - the key is stored in a hardware token.\n        MobileDevice - the key is stored in a mobile device.\n        MobileAuthCard - the key is stored in a mobile\n        authentication card.\n      ')


    _ElementMap = {
        __Extension.name() : __Extension,
        __KeyActivation.name() : __KeyActivation,
        __KeyStorage.name() : __KeyStorage
    }
    _AttributeMap = {
        
    }
Namespace.addCategoryObject('typeBinding', u'SecretKeyProtectionType', SecretKeyProtectionType)


# Complex type TechnicalProtectionBaseType with content type ELEMENT_ONLY
class TechnicalProtectionBaseType (pyxb.binding.basis.complexTypeDefinition):
    _TypeDefinition = None
    _ContentTypeTag = pyxb.binding.basis.complexTypeDefinition._CT_ELEMENT_ONLY
    _Abstract = False
    _ExpandedName = pyxb.namespace.ExpandedName(Namespace, u'TechnicalProtectionBaseType')
    # Base type is pyxb.binding.datatypes.anyType
    
    # Element {urn:oasis:names:tc:SAML:2.0:ac:classes:PasswordProtectedTransport}Extension uses Python identifier Extension
    __Extension = pyxb.binding.content.ElementUse(pyxb.namespace.ExpandedName(Namespace, u'Extension'), 'Extension', '__urnoasisnamestcSAML2_0acclassesPasswordProtectedTransport_TechnicalProtectionBaseType_urnoasisnamestcSAML2_0acclassesPasswordProtectedTransportExtension', True)

    
    Extension = property(__Extension.value, __Extension.set, None, None)

    
    # Element {urn:oasis:names:tc:SAML:2.0:ac:classes:PasswordProtectedTransport}SecretKeyProtection uses Python identifier SecretKeyProtection
    __SecretKeyProtection = pyxb.binding.content.ElementUse(pyxb.namespace.ExpandedName(Namespace, u'SecretKeyProtection'), 'SecretKeyProtection', '__urnoasisnamestcSAML2_0acclassesPasswordProtectedTransport_TechnicalProtectionBaseType_urnoasisnamestcSAML2_0acclassesPasswordProtectedTransportSecretKeyProtection', False)

    
    SecretKeyProtection = property(__SecretKeyProtection.value, __SecretKeyProtection.set, None, u'\n        This element indicates the types and strengths of\n        facilities\n        of a UA used to protect a shared secret key from\n        unauthorized access and/or use.\n      ')

    
    # Element {urn:oasis:names:tc:SAML:2.0:ac:classes:PasswordProtectedTransport}PrivateKeyProtection uses Python identifier PrivateKeyProtection
    __PrivateKeyProtection = pyxb.binding.content.ElementUse(pyxb.namespace.ExpandedName(Namespace, u'PrivateKeyProtection'), 'PrivateKeyProtection', '__urnoasisnamestcSAML2_0acclassesPasswordProtectedTransport_TechnicalProtectionBaseType_urnoasisnamestcSAML2_0acclassesPasswordProtectedTransportPrivateKeyProtection', False)

    
    PrivateKeyProtection = property(__PrivateKeyProtection.value, __PrivateKeyProtection.set, None, u'\n        This element indicates the types and strengths of\n        facilities\n        of a UA used to protect a private key from\n        unauthorized access and/or use.\n      ')


    _ElementMap = {
        __Extension.name() : __Extension,
        __SecretKeyProtection.name() : __SecretKeyProtection,
        __PrivateKeyProtection.name() : __PrivateKeyProtection
    }
    _AttributeMap = {
        
    }
Namespace.addCategoryObject('typeBinding', u'TechnicalProtectionBaseType', TechnicalProtectionBaseType)


# Complex type KeyActivationType with content type ELEMENT_ONLY
class KeyActivationType (pyxb.binding.basis.complexTypeDefinition):
    _TypeDefinition = None
    _ContentTypeTag = pyxb.binding.basis.complexTypeDefinition._CT_ELEMENT_ONLY
    _Abstract = False
    _ExpandedName = pyxb.namespace.ExpandedName(Namespace, u'KeyActivationType')
    # Base type is pyxb.binding.datatypes.anyType
    
    # Element {urn:oasis:names:tc:SAML:2.0:ac:classes:PasswordProtectedTransport}Extension uses Python identifier Extension
    __Extension = pyxb.binding.content.ElementUse(pyxb.namespace.ExpandedName(Namespace, u'Extension'), 'Extension', '__urnoasisnamestcSAML2_0acclassesPasswordProtectedTransport_KeyActivationType_urnoasisnamestcSAML2_0acclassesPasswordProtectedTransportExtension', True)

    
    Extension = property(__Extension.value, __Extension.set, None, None)

    
    # Element {urn:oasis:names:tc:SAML:2.0:ac:classes:PasswordProtectedTransport}ActivationPin uses Python identifier ActivationPin
    __ActivationPin = pyxb.binding.content.ElementUse(pyxb.namespace.ExpandedName(Namespace, u'ActivationPin'), 'ActivationPin', '__urnoasisnamestcSAML2_0acclassesPasswordProtectedTransport_KeyActivationType_urnoasisnamestcSAML2_0acclassesPasswordProtectedTransportActivationPin', False)

    
    ActivationPin = property(__ActivationPin.value, __ActivationPin.set, None, u'\n        This element indicates that a Pin (Personal\n        Identification Number) has been used to authenticate the Principal to\n        some local system in order to activate a key.\n      ')


    _ElementMap = {
        __Extension.name() : __Extension,
        __ActivationPin.name() : __ActivationPin
    }
    _AttributeMap = {
        
    }
Namespace.addCategoryObject('typeBinding', u'KeyActivationType', KeyActivationType)


# Complex type KeySharingType with content type EMPTY
class KeySharingType (pyxb.binding.basis.complexTypeDefinition):
    _TypeDefinition = None
    _ContentTypeTag = pyxb.binding.basis.complexTypeDefinition._CT_EMPTY
    _Abstract = False
    _ExpandedName = pyxb.namespace.ExpandedName(Namespace, u'KeySharingType')
    # Base type is pyxb.binding.datatypes.anyType
    
    # Attribute sharing uses Python identifier sharing
    __sharing = pyxb.binding.content.AttributeUse(pyxb.namespace.ExpandedName(None, u'sharing'), 'sharing', '__urnoasisnamestcSAML2_0acclassesPasswordProtectedTransport_KeySharingType_sharing', pyxb.binding.datatypes.boolean, required=True)
    
    sharing = property(__sharing.value, __sharing.set, None, None)


    _ElementMap = {
        
    }
    _AttributeMap = {
        __sharing.name() : __sharing
    }
Namespace.addCategoryObject('typeBinding', u'KeySharingType', KeySharingType)


# Complex type PrincipalAuthenticationMechanismType with content type ELEMENT_ONLY
class PrincipalAuthenticationMechanismType (pyxb.binding.basis.complexTypeDefinition):
    _TypeDefinition = None
    _ContentTypeTag = pyxb.binding.basis.complexTypeDefinition._CT_ELEMENT_ONLY
    _Abstract = False
    _ExpandedName = pyxb.namespace.ExpandedName(Namespace, u'PrincipalAuthenticationMechanismType')
    # Base type is pyxb.binding.datatypes.anyType
    
    # Element {urn:oasis:names:tc:SAML:2.0:ac:classes:PasswordProtectedTransport}Extension uses Python identifier Extension
    __Extension = pyxb.binding.content.ElementUse(pyxb.namespace.ExpandedName(Namespace, u'Extension'), 'Extension', '__urnoasisnamestcSAML2_0acclassesPasswordProtectedTransport_PrincipalAuthenticationMechanismType_urnoasisnamestcSAML2_0acclassesPasswordProtectedTransportExtension', True)

    
    Extension = property(__Extension.value, __Extension.set, None, None)

    
    # Element {urn:oasis:names:tc:SAML:2.0:ac:classes:PasswordProtectedTransport}Token uses Python identifier Token
    __Token = pyxb.binding.content.ElementUse(pyxb.namespace.ExpandedName(Namespace, u'Token'), 'Token', '__urnoasisnamestcSAML2_0acclassesPasswordProtectedTransport_PrincipalAuthenticationMechanismType_urnoasisnamestcSAML2_0acclassesPasswordProtectedTransportToken', False)

    
    Token = property(__Token.value, __Token.set, None, u'\n        This element indicates that a hardware or software\n        token is used\n        as a method of identifying the Principal.\n      ')

    
    # Element {urn:oasis:names:tc:SAML:2.0:ac:classes:PasswordProtectedTransport}Smartcard uses Python identifier Smartcard
    __Smartcard = pyxb.binding.content.ElementUse(pyxb.namespace.ExpandedName(Namespace, u'Smartcard'), 'Smartcard', '__urnoasisnamestcSAML2_0acclassesPasswordProtectedTransport_PrincipalAuthenticationMechanismType_urnoasisnamestcSAML2_0acclassesPasswordProtectedTransportSmartcard', False)

    
    Smartcard = property(__Smartcard.value, __Smartcard.set, None, u'\n        This element indicates that a smartcard is used to\n        identity the Principal.\n      ')

    
    # Element {urn:oasis:names:tc:SAML:2.0:ac:classes:PasswordProtectedTransport}Password uses Python identifier Password
    __Password = pyxb.binding.content.ElementUse(pyxb.namespace.ExpandedName(Namespace, u'Password'), 'Password', '__urnoasisnamestcSAML2_0acclassesPasswordProtectedTransport_PrincipalAuthenticationMechanismType_urnoasisnamestcSAML2_0acclassesPasswordProtectedTransportPassword', False)

    
    Password = property(__Password.value, __Password.set, None, u'\n        This element indicates that a password (or passphrase)\n        has been used to\n        authenticate the Principal to a remote system.\n      ')

    
    # Element {urn:oasis:names:tc:SAML:2.0:ac:classes:PasswordProtectedTransport}ActivationPin uses Python identifier ActivationPin
    __ActivationPin = pyxb.binding.content.ElementUse(pyxb.namespace.ExpandedName(Namespace, u'ActivationPin'), 'ActivationPin', '__urnoasisnamestcSAML2_0acclassesPasswordProtectedTransport_PrincipalAuthenticationMechanismType_urnoasisnamestcSAML2_0acclassesPasswordProtectedTransportActivationPin', False)

    
    ActivationPin = property(__ActivationPin.value, __ActivationPin.set, None, u'\n        This element indicates that a Pin (Personal\n        Identification Number) has been used to authenticate the Principal to\n        some local system in order to activate a key.\n      ')

    
    # Element {urn:oasis:names:tc:SAML:2.0:ac:classes:PasswordProtectedTransport}RestrictedPassword uses Python identifier RestrictedPassword
    __RestrictedPassword = pyxb.binding.content.ElementUse(pyxb.namespace.ExpandedName(Namespace, u'RestrictedPassword'), 'RestrictedPassword', '__urnoasisnamestcSAML2_0acclassesPasswordProtectedTransport_PrincipalAuthenticationMechanismType_urnoasisnamestcSAML2_0acclassesPasswordProtectedTransportRestrictedPassword', False)

    
    RestrictedPassword = property(__RestrictedPassword.value, __RestrictedPassword.set, None, None)

    
    # Attribute preauth uses Python identifier preauth
    __preauth = pyxb.binding.content.AttributeUse(pyxb.namespace.ExpandedName(None, u'preauth'), 'preauth', '__urnoasisnamestcSAML2_0acclassesPasswordProtectedTransport_PrincipalAuthenticationMechanismType_preauth', pyxb.binding.datatypes.integer)
    
    preauth = property(__preauth.value, __preauth.set, None, None)


    _ElementMap = {
        __Extension.name() : __Extension,
        __Token.name() : __Token,
        __Smartcard.name() : __Smartcard,
        __Password.name() : __Password,
        __ActivationPin.name() : __ActivationPin,
        __RestrictedPassword.name() : __RestrictedPassword
    }
    _AttributeMap = {
        __preauth.name() : __preauth
    }
Namespace.addCategoryObject('typeBinding', u'PrincipalAuthenticationMechanismType', PrincipalAuthenticationMechanismType)


# Complex type AuthenticatorBaseType with content type ELEMENT_ONLY
class AuthenticatorBaseType (pyxb.binding.basis.complexTypeDefinition):
    _TypeDefinition = None
    _ContentTypeTag = pyxb.binding.basis.complexTypeDefinition._CT_ELEMENT_ONLY
    _Abstract = False
    _ExpandedName = pyxb.namespace.ExpandedName(Namespace, u'AuthenticatorBaseType')
    # Base type is pyxb.binding.datatypes.anyType
    
    # Element {urn:oasis:names:tc:SAML:2.0:ac:classes:PasswordProtectedTransport}RestrictedPassword uses Python identifier RestrictedPassword
    __RestrictedPassword = pyxb.binding.content.ElementUse(pyxb.namespace.ExpandedName(Namespace, u'RestrictedPassword'), 'RestrictedPassword', '__urnoasisnamestcSAML2_0acclassesPasswordProtectedTransport_AuthenticatorBaseType_urnoasisnamestcSAML2_0acclassesPasswordProtectedTransportRestrictedPassword', False)

    
    RestrictedPassword = property(__RestrictedPassword.value, __RestrictedPassword.set, None, None)


    _ElementMap = {
        __RestrictedPassword.name() : __RestrictedPassword
    }
    _AttributeMap = {
        
    }
Namespace.addCategoryObject('typeBinding', u'AuthenticatorBaseType', AuthenticatorBaseType)


# Complex type AuthnMethodBaseType with content type ELEMENT_ONLY
class AuthnMethodBaseType (pyxb.binding.basis.complexTypeDefinition):
    _TypeDefinition = None
    _ContentTypeTag = pyxb.binding.basis.complexTypeDefinition._CT_ELEMENT_ONLY
    _Abstract = False
    _ExpandedName = pyxb.namespace.ExpandedName(Namespace, u'AuthnMethodBaseType')
    # Base type is pyxb.binding.datatypes.anyType
    
    # Element {urn:oasis:names:tc:SAML:2.0:ac:classes:PasswordProtectedTransport}Authenticator uses Python identifier Authenticator
    __Authenticator = pyxb.binding.content.ElementUse(pyxb.namespace.ExpandedName(Namespace, u'Authenticator'), 'Authenticator', '__urnoasisnamestcSAML2_0acclassesPasswordProtectedTransport_AuthnMethodBaseType_urnoasisnamestcSAML2_0acclassesPasswordProtectedTransportAuthenticator', False)

    
    Authenticator = property(__Authenticator.value, __Authenticator.set, None, u"\n        The method applied to validate a principal's\n        authentication across a network\n      ")

    
    # Element {urn:oasis:names:tc:SAML:2.0:ac:classes:PasswordProtectedTransport}PrincipalAuthenticationMechanism uses Python identifier PrincipalAuthenticationMechanism
    __PrincipalAuthenticationMechanism = pyxb.binding.content.ElementUse(pyxb.namespace.ExpandedName(Namespace, u'PrincipalAuthenticationMechanism'), 'PrincipalAuthenticationMechanism', '__urnoasisnamestcSAML2_0acclassesPasswordProtectedTransport_AuthnMethodBaseType_urnoasisnamestcSAML2_0acclassesPasswordProtectedTransportPrincipalAuthenticationMechanism', False)

    
    PrincipalAuthenticationMechanism = property(__PrincipalAuthenticationMechanism.value, __PrincipalAuthenticationMechanism.set, None, u'\n        The method that a Principal employs to perform\n        authentication to local system components.\n      ')

    
    # Element {urn:oasis:names:tc:SAML:2.0:ac:classes:PasswordProtectedTransport}Extension uses Python identifier Extension
    __Extension = pyxb.binding.content.ElementUse(pyxb.namespace.ExpandedName(Namespace, u'Extension'), 'Extension', '__urnoasisnamestcSAML2_0acclassesPasswordProtectedTransport_AuthnMethodBaseType_urnoasisnamestcSAML2_0acclassesPasswordProtectedTransportExtension', True)

    
    Extension = property(__Extension.value, __Extension.set, None, None)

    
    # Element {urn:oasis:names:tc:SAML:2.0:ac:classes:PasswordProtectedTransport}AuthenticatorTransportProtocol uses Python identifier AuthenticatorTransportProtocol
    __AuthenticatorTransportProtocol = pyxb.binding.content.ElementUse(pyxb.namespace.ExpandedName(Namespace, u'AuthenticatorTransportProtocol'), 'AuthenticatorTransportProtocol', '__urnoasisnamestcSAML2_0acclassesPasswordProtectedTransport_AuthnMethodBaseType_urnoasisnamestcSAML2_0acclassesPasswordProtectedTransportAuthenticatorTransportProtocol', False)

    
    AuthenticatorTransportProtocol = property(__AuthenticatorTransportProtocol.value, __AuthenticatorTransportProtocol.set, None, u'\n        The protocol across which Authenticator information is\n        transferred to an Authentication Authority verifier.\n      ')


    _ElementMap = {
        __Authenticator.name() : __Authenticator,
        __PrincipalAuthenticationMechanism.name() : __PrincipalAuthenticationMechanism,
        __Extension.name() : __Extension,
        __AuthenticatorTransportProtocol.name() : __AuthenticatorTransportProtocol
    }
    _AttributeMap = {
        
    }
Namespace.addCategoryObject('typeBinding', u'AuthnMethodBaseType', AuthnMethodBaseType)


PhysicalVerification = pyxb.binding.basis.element(pyxb.namespace.ExpandedName(Namespace, u'PhysicalVerification'), CTD_ANON, documentation=u'\n        This element indicates that identification has been\n        performed in a physical\n        face-to-face meeting with the principal and not in an\n        online manner.\n      ')
Namespace.addCategoryObject('elementBinding', PhysicalVerification.name().localName(), PhysicalVerification)

ActivationLimitSession = pyxb.binding.basis.element(pyxb.namespace.ExpandedName(Namespace, u'ActivationLimitSession'), ActivationLimitSessionType, documentation=u'\n        This element indicates that the Key Activation Limit is\n        the session.\n      ')
Namespace.addCategoryObject('elementBinding', ActivationLimitSession.name().localName(), ActivationLimitSession)

WrittenConsent = pyxb.binding.basis.element(pyxb.namespace.ExpandedName(Namespace, u'WrittenConsent'), ExtensionOnlyType)
Namespace.addCategoryObject('elementBinding', WrittenConsent.name().localName(), WrittenConsent)

AuthenticationContextDeclaration = pyxb.binding.basis.element(pyxb.namespace.ExpandedName(Namespace, u'AuthenticationContextDeclaration'), AuthnContextDeclarationBaseType, documentation=u"\n        A particular assertion on an identity\n        provider's part with respect to the authentication\n        context associated with an authentication assertion.\n      ")
Namespace.addCategoryObject('elementBinding', AuthenticationContextDeclaration.name().localName(), AuthenticationContextDeclaration)

ActivationLimitDuration = pyxb.binding.basis.element(pyxb.namespace.ExpandedName(Namespace, u'ActivationLimitDuration'), ActivationLimitDurationType, documentation=u'\n        This element indicates that the Key Activation Limit is\n        defined as a specific duration of time.\n      ')
Namespace.addCategoryObject('elementBinding', ActivationLimitDuration.name().localName(), ActivationLimitDuration)

ActivationLimitUsages = pyxb.binding.basis.element(pyxb.namespace.ExpandedName(Namespace, u'ActivationLimitUsages'), ActivationLimitUsagesType, documentation=u'\n        This element indicates that the Key Activation Limit is\n        defined as a number of usages.\n      ')
Namespace.addCategoryObject('elementBinding', ActivationLimitUsages.name().localName(), ActivationLimitUsages)

RestrictedPassword = pyxb.binding.basis.element(pyxb.namespace.ExpandedName(Namespace, u'RestrictedPassword'), RestrictedPasswordType)
Namespace.addCategoryObject('elementBinding', RestrictedPassword.name().localName(), RestrictedPassword)

Alphabet = pyxb.binding.basis.element(pyxb.namespace.ExpandedName(Namespace, u'Alphabet'), AlphabetType)
Namespace.addCategoryObject('elementBinding', Alphabet.name().localName(), Alphabet)

DigSig = pyxb.binding.basis.element(pyxb.namespace.ExpandedName(Namespace, u'DigSig'), PublicKeyType, documentation=u'\n        This element indicates that the Principal has been\n        authenticated by a mechanism which involves the Principal computing a\n        digital signature over at least challenge data provided by the IdP.\n      ')
Namespace.addCategoryObject('elementBinding', DigSig.name().localName(), DigSig)

AsymmetricDecryption = pyxb.binding.basis.element(pyxb.namespace.ExpandedName(Namespace, u'AsymmetricDecryption'), PublicKeyType, documentation=u"\n        The local system has a private key but it is used\n        in decryption mode, rather than signature mode. For example, the\n        Authentication Authority generates a secret and encrypts it using the\n        local system's public key: the local system then proves it has\n        decrypted the secret.\n      ")
Namespace.addCategoryObject('elementBinding', AsymmetricDecryption.name().localName(), AsymmetricDecryption)

AsymmetricKeyAgreement = pyxb.binding.basis.element(pyxb.namespace.ExpandedName(Namespace, u'AsymmetricKeyAgreement'), PublicKeyType, documentation=u'\n        The local system has a private key and uses it for\n        shared secret key agreement with the Authentication Authority (e.g.\n        via Diffie Helman).\n      ')
Namespace.addCategoryObject('elementBinding', AsymmetricKeyAgreement.name().localName(), AsymmetricKeyAgreement)

IPAddress = pyxb.binding.basis.element(pyxb.namespace.ExpandedName(Namespace, u'IPAddress'), ExtensionOnlyType, documentation=u'\n        This element indicates that the Principal has been\n        authenticated through connection from a particular IP address.\n      ')
Namespace.addCategoryObject('elementBinding', IPAddress.name().localName(), IPAddress)

MobileNetworkEndToEndEncryption = pyxb.binding.basis.element(pyxb.namespace.ExpandedName(Namespace, u'MobileNetworkEndToEndEncryption'), ExtensionOnlyType)
Namespace.addCategoryObject('elementBinding', MobileNetworkEndToEndEncryption.name().localName(), MobileNetworkEndToEndEncryption)

SharedSecretDynamicPlaintext = pyxb.binding.basis.element(pyxb.namespace.ExpandedName(Namespace, u'SharedSecretDynamicPlaintext'), ExtensionOnlyType, documentation=u'\n        The local system and Authentication Authority\n        share a secret key. The local system uses this to encrypt a\n        randomised string to pass to the Authentication Authority.\n      ')
Namespace.addCategoryObject('elementBinding', SharedSecretDynamicPlaintext.name().localName(), SharedSecretDynamicPlaintext)

AuthenticatorTransportProtocol = pyxb.binding.basis.element(pyxb.namespace.ExpandedName(Namespace, u'AuthenticatorTransportProtocol'), AuthenticatorTransportProtocolType, documentation=u'\n        The protocol across which Authenticator information is\n        transferred to an Authentication Authority verifier.\n      ')
Namespace.addCategoryObject('elementBinding', AuthenticatorTransportProtocol.name().localName(), AuthenticatorTransportProtocol)

HTTP = pyxb.binding.basis.element(pyxb.namespace.ExpandedName(Namespace, u'HTTP'), ExtensionOnlyType, documentation=u'\n        This element indicates that the Authenticator has been\n        transmitted using bare HTTP utilizing no additional security\n        protocols.\n      ')
Namespace.addCategoryObject('elementBinding', HTTP.name().localName(), HTTP)

IPSec = pyxb.binding.basis.element(pyxb.namespace.ExpandedName(Namespace, u'IPSec'), ExtensionOnlyType, documentation=u'\n        This element indicates that the Authenticator has been\n        transmitted using a transport mechanism protected by an IPSEC session.\n      ')
Namespace.addCategoryObject('elementBinding', IPSec.name().localName(), IPSec)

WTLS = pyxb.binding.basis.element(pyxb.namespace.ExpandedName(Namespace, u'WTLS'), ExtensionOnlyType, documentation=u'\n        This element indicates that the Authenticator has been\n        transmitted using a transport mechanism protected by a WTLS session.\n      ')
Namespace.addCategoryObject('elementBinding', WTLS.name().localName(), WTLS)

MobileNetworkNoEncryption = pyxb.binding.basis.element(pyxb.namespace.ExpandedName(Namespace, u'MobileNetworkNoEncryption'), ExtensionOnlyType, documentation=u'\n        This element indicates that the Authenticator has been\n        transmitted solely across a mobile network using no additional\n        security mechanism.\n      ')
Namespace.addCategoryObject('elementBinding', MobileNetworkNoEncryption.name().localName(), MobileNetworkNoEncryption)

MobileNetworkRadioEncryption = pyxb.binding.basis.element(pyxb.namespace.ExpandedName(Namespace, u'MobileNetworkRadioEncryption'), ExtensionOnlyType)
Namespace.addCategoryObject('elementBinding', MobileNetworkRadioEncryption.name().localName(), MobileNetworkRadioEncryption)

SSL = pyxb.binding.basis.element(pyxb.namespace.ExpandedName(Namespace, u'SSL'), ExtensionOnlyType, documentation=u'\n        This element indicates that the Authenticator has been\n        transmitted using a transport mechnanism protected by an SSL or TLS\n        session.\n      ')
Namespace.addCategoryObject('elementBinding', SSL.name().localName(), SSL)

ISDN = pyxb.binding.basis.element(pyxb.namespace.ExpandedName(Namespace, u'ISDN'), ExtensionOnlyType)
Namespace.addCategoryObject('elementBinding', ISDN.name().localName(), ISDN)

PSTN = pyxb.binding.basis.element(pyxb.namespace.ExpandedName(Namespace, u'PSTN'), ExtensionOnlyType)
Namespace.addCategoryObject('elementBinding', PSTN.name().localName(), PSTN)

ADSL = pyxb.binding.basis.element(pyxb.namespace.ExpandedName(Namespace, u'ADSL'), ExtensionOnlyType)
Namespace.addCategoryObject('elementBinding', ADSL.name().localName(), ADSL)

OperationalProtection = pyxb.binding.basis.element(pyxb.namespace.ExpandedName(Namespace, u'OperationalProtection'), OperationalProtectionType, documentation=u'\n        Refers to those characteristics that describe\n        procedural security controls employed by the Authentication Authority.\n      ')
Namespace.addCategoryObject('elementBinding', OperationalProtection.name().localName(), OperationalProtection)

SwitchAudit = pyxb.binding.basis.element(pyxb.namespace.ExpandedName(Namespace, u'SwitchAudit'), ExtensionOnlyType)
Namespace.addCategoryObject('elementBinding', SwitchAudit.name().localName(), SwitchAudit)

SecurityAudit = pyxb.binding.basis.element(pyxb.namespace.ExpandedName(Namespace, u'SecurityAudit'), SecurityAuditType)
Namespace.addCategoryObject('elementBinding', SecurityAudit.name().localName(), SecurityAudit)

DeactivationCallCenter = pyxb.binding.basis.element(pyxb.namespace.ExpandedName(Namespace, u'DeactivationCallCenter'), ExtensionOnlyType)
Namespace.addCategoryObject('elementBinding', DeactivationCallCenter.name().localName(), DeactivationCallCenter)

GoverningAgreements = pyxb.binding.basis.element(pyxb.namespace.ExpandedName(Namespace, u'GoverningAgreements'), GoverningAgreementsType, documentation=u'\n        Provides a mechanism for linking to external (likely\n        human readable) documents in which additional business agreements,\n        (e.g. liability constraints, obligations, etc) can be placed.\n      ')
Namespace.addCategoryObject('elementBinding', GoverningAgreements.name().localName(), GoverningAgreements)

GoverningAgreementRef = pyxb.binding.basis.element(pyxb.namespace.ExpandedName(Namespace, u'GoverningAgreementRef'), GoverningAgreementRefType)
Namespace.addCategoryObject('elementBinding', GoverningAgreementRef.name().localName(), GoverningAgreementRef)

Identification = pyxb.binding.basis.element(pyxb.namespace.ExpandedName(Namespace, u'Identification'), IdentificationType, documentation=u'\n        Refers to those characteristics that describe the\n        processes and mechanisms\n        the Authentication Authority uses to initially create\n        an association between a Principal\n        and the identity (or name) by which the Principal will\n        be known\n      ')
Namespace.addCategoryObject('elementBinding', Identification.name().localName(), Identification)

TechnicalProtection = pyxb.binding.basis.element(pyxb.namespace.ExpandedName(Namespace, u'TechnicalProtection'), TechnicalProtectionBaseType, documentation=u"\n        Refers to those characterstics that describe how the\n        'secret' (the knowledge or possession\n        of which allows the Principal to authenticate to the\n        Authentication Authority) is kept secure\n      ")
Namespace.addCategoryObject('elementBinding', TechnicalProtection.name().localName(), TechnicalProtection)

UserSuffix = pyxb.binding.basis.element(pyxb.namespace.ExpandedName(Namespace, u'UserSuffix'), ExtensionOnlyType)
Namespace.addCategoryObject('elementBinding', UserSuffix.name().localName(), UserSuffix)

SecretKeyProtection = pyxb.binding.basis.element(pyxb.namespace.ExpandedName(Namespace, u'SecretKeyProtection'), SecretKeyProtectionType, documentation=u'\n        This element indicates the types and strengths of\n        facilities\n        of a UA used to protect a shared secret key from\n        unauthorized access and/or use.\n      ')
Namespace.addCategoryObject('elementBinding', SecretKeyProtection.name().localName(), SecretKeyProtection)

PrivateKeyProtection = pyxb.binding.basis.element(pyxb.namespace.ExpandedName(Namespace, u'PrivateKeyProtection'), PrivateKeyProtectionType, documentation=u'\n        This element indicates the types and strengths of\n        facilities\n        of a UA used to protect a private key from\n        unauthorized access and/or use.\n      ')
Namespace.addCategoryObject('elementBinding', PrivateKeyProtection.name().localName(), PrivateKeyProtection)

KeyActivation = pyxb.binding.basis.element(pyxb.namespace.ExpandedName(Namespace, u'KeyActivation'), KeyActivationType, documentation=u'The actions that must be performed\n        before the private key can be used. ')
Namespace.addCategoryObject('elementBinding', KeyActivation.name().localName(), KeyActivation)

KeySharing = pyxb.binding.basis.element(pyxb.namespace.ExpandedName(Namespace, u'KeySharing'), KeySharingType, documentation=u'Whether or not the private key is shared\n        with the certificate authority.')
Namespace.addCategoryObject('elementBinding', KeySharing.name().localName(), KeySharing)

KeyStorage = pyxb.binding.basis.element(pyxb.namespace.ExpandedName(Namespace, u'KeyStorage'), KeyStorageType, documentation=u'\n        In which medium is the key stored.\n        memory - the key is stored in memory.\n        smartcard - the key is stored in a smartcard.\n        token - the key is stored in a hardware token.\n        MobileDevice - the key is stored in a mobile device.\n        MobileAuthCard - the key is stored in a mobile\n        authentication card.\n      ')
Namespace.addCategoryObject('elementBinding', KeyStorage.name().localName(), KeyStorage)

SubscriberLineNumber = pyxb.binding.basis.element(pyxb.namespace.ExpandedName(Namespace, u'SubscriberLineNumber'), ExtensionOnlyType)
Namespace.addCategoryObject('elementBinding', SubscriberLineNumber.name().localName(), SubscriberLineNumber)

Password = pyxb.binding.basis.element(pyxb.namespace.ExpandedName(Namespace, u'Password'), PasswordType, documentation=u'\n        This element indicates that a password (or passphrase)\n        has been used to\n        authenticate the Principal to a remote system.\n      ')
Namespace.addCategoryObject('elementBinding', Password.name().localName(), Password)

ActivationPin = pyxb.binding.basis.element(pyxb.namespace.ExpandedName(Namespace, u'ActivationPin'), ActivationPinType, documentation=u'\n        This element indicates that a Pin (Personal\n        Identification Number) has been used to authenticate the Principal to\n        some local system in order to activate a key.\n      ')
Namespace.addCategoryObject('elementBinding', ActivationPin.name().localName(), ActivationPin)

Token = pyxb.binding.basis.element(pyxb.namespace.ExpandedName(Namespace, u'Token'), TokenType, documentation=u'\n        This element indicates that a hardware or software\n        token is used\n        as a method of identifying the Principal.\n      ')
Namespace.addCategoryObject('elementBinding', Token.name().localName(), Token)

TimeSyncToken = pyxb.binding.basis.element(pyxb.namespace.ExpandedName(Namespace, u'TimeSyncToken'), TimeSyncTokenType, documentation=u'\n        This element indicates that a time synchronization\n        token is used to identify the Principal. hardware -\n        the time synchonization\n        token has been implemented in hardware. software - the\n        time synchronization\n        token has been implemented in software. SeedLength -\n        the length, in bits, of the\n        random seed used in the time synchronization token.\n      ')
Namespace.addCategoryObject('elementBinding', TimeSyncToken.name().localName(), TimeSyncToken)

Smartcard = pyxb.binding.basis.element(pyxb.namespace.ExpandedName(Namespace, u'Smartcard'), ExtensionOnlyType, documentation=u'\n        This element indicates that a smartcard is used to\n        identity the Principal.\n      ')
Namespace.addCategoryObject('elementBinding', Smartcard.name().localName(), Smartcard)

Length = pyxb.binding.basis.element(pyxb.namespace.ExpandedName(Namespace, u'Length'), LengthType, documentation=u'\n        This element indicates the minimum and/or maximum\n        ASCII length of the password which is enforced (by the UA or the\n        IdP). In other words, this is the minimum and/or maximum number of\n        ASCII characters required to represent a valid password.\n        min - the minimum number of ASCII characters required\n        in a valid password, as enforced by the UA or the IdP.\n        max - the maximum number of ASCII characters required\n        in a valid password, as enforced by the UA or the IdP.\n      ')
Namespace.addCategoryObject('elementBinding', Length.name().localName(), Length)

ActivationLimit = pyxb.binding.basis.element(pyxb.namespace.ExpandedName(Namespace, u'ActivationLimit'), ActivationLimitType, documentation=u'\n        This element indicates the length of time for which an\n        PIN-based authentication is valid.\n      ')
Namespace.addCategoryObject('elementBinding', ActivationLimit.name().localName(), ActivationLimit)

Generation = pyxb.binding.basis.element(pyxb.namespace.ExpandedName(Namespace, u'Generation'), CTD_ANON_, documentation=u'\n        Indicates whether the password was chosen by the\n        Principal or auto-supplied by the Authentication Authority.\n        principalchosen - the Principal is allowed to choose\n        the value of the password. This is true even if\n        the initial password is chosen at random by the UA or\n        the IdP and the Principal is then free to change\n        the password.\n        automatic - the password is chosen by the UA or the\n        IdP to be cryptographically strong in some sense,\n        or to satisfy certain password rules, and that the\n        Principal is not free to change it or to choose a new password.\n      ')
Namespace.addCategoryObject('elementBinding', Generation.name().localName(), Generation)

AuthnMethod = pyxb.binding.basis.element(pyxb.namespace.ExpandedName(Namespace, u'AuthnMethod'), AuthnMethodBaseType, documentation=u'\n        Refers to those characteristics that define the\n        mechanisms by which the Principal authenticates to the Authentication\n        Authority.\n      ')
Namespace.addCategoryObject('elementBinding', AuthnMethod.name().localName(), AuthnMethod)

PrincipalAuthenticationMechanism = pyxb.binding.basis.element(pyxb.namespace.ExpandedName(Namespace, u'PrincipalAuthenticationMechanism'), PrincipalAuthenticationMechanismType, documentation=u'\n        The method that a Principal employs to perform\n        authentication to local system components.\n      ')
Namespace.addCategoryObject('elementBinding', PrincipalAuthenticationMechanism.name().localName(), PrincipalAuthenticationMechanism)

Authenticator = pyxb.binding.basis.element(pyxb.namespace.ExpandedName(Namespace, u'Authenticator'), AuthenticatorBaseType, documentation=u"\n        The method applied to validate a principal's\n        authentication across a network\n      ")
Namespace.addCategoryObject('elementBinding', Authenticator.name().localName(), Authenticator)

ComplexAuthenticator = pyxb.binding.basis.element(pyxb.namespace.ExpandedName(Namespace, u'ComplexAuthenticator'), ComplexAuthenticatorType, documentation=u'\n        Supports Authenticators with nested combinations of\n        additional complexity.\n      ')
Namespace.addCategoryObject('elementBinding', ComplexAuthenticator.name().localName(), ComplexAuthenticator)

PreviousSession = pyxb.binding.basis.element(pyxb.namespace.ExpandedName(Namespace, u'PreviousSession'), ExtensionOnlyType, documentation=u'\n        Indicates that the Principal has been strongly\n        authenticated in a previous session during which the IdP has set a\n        cookie in the UA. During the present session the Principal has only\n        been authenticated by the UA returning the cookie to the IdP.\n      ')
Namespace.addCategoryObject('elementBinding', PreviousSession.name().localName(), PreviousSession)

ResumeSession = pyxb.binding.basis.element(pyxb.namespace.ExpandedName(Namespace, u'ResumeSession'), ExtensionOnlyType, documentation=u'\n        Rather like PreviousSession but using stronger\n        security. A secret that was established in a previous session with\n        the Authentication Authority has been cached by the local system and\n        is now re-used (e.g. a Master Secret is used to derive new session\n        keys in TLS, SSL, WTLS).\n      ')
Namespace.addCategoryObject('elementBinding', ResumeSession.name().localName(), ResumeSession)

ZeroKnowledge = pyxb.binding.basis.element(pyxb.namespace.ExpandedName(Namespace, u'ZeroKnowledge'), ExtensionOnlyType, documentation=u'\n        This element indicates that the Principal has been\n        authenticated by a zero knowledge technique as specified in ISO/IEC\n        9798-5.\n      ')
Namespace.addCategoryObject('elementBinding', ZeroKnowledge.name().localName(), ZeroKnowledge)

SharedSecretChallengeResponse = pyxb.binding.basis.element(pyxb.namespace.ExpandedName(Namespace, u'SharedSecretChallengeResponse'), SharedSecretChallengeResponseType)
Namespace.addCategoryObject('elementBinding', SharedSecretChallengeResponse.name().localName(), SharedSecretChallengeResponse)

Extension = pyxb.binding.basis.element(pyxb.namespace.ExpandedName(Namespace, u'Extension'), ExtensionType)
Namespace.addCategoryObject('elementBinding', Extension.name().localName(), Extension)


ExtensionType._GroupModel = pyxb.binding.content.GroupSequence(
    pyxb.binding.content.ParticleModel(pyxb.binding.content.Wildcard(process_contents=pyxb.binding.content.Wildcard.PC_lax, namespace_constraint=(pyxb.binding.content.Wildcard.NC_not, u'urn:oasis:names:tc:SAML:2.0:ac:classes:PasswordProtectedTransport')), min_occurs=1, max_occurs=None)
    )
ExtensionType._ContentModel = pyxb.binding.content.ParticleModel(ExtensionType._GroupModel, min_occurs=1, max_occurs=1)



PublicKeyType._AddElement(pyxb.binding.basis.element(pyxb.namespace.ExpandedName(Namespace, u'Extension'), ExtensionType, scope=PublicKeyType))
PublicKeyType._GroupModel = pyxb.binding.content.GroupSequence(
    pyxb.binding.content.ParticleModel(PublicKeyType._UseForTag(pyxb.namespace.ExpandedName(Namespace, u'Extension')), min_occurs=0L, max_occurs=None)
    )
PublicKeyType._ContentModel = pyxb.binding.content.ParticleModel(PublicKeyType._GroupModel, min_occurs=1, max_occurs=1)



PasswordType._AddElement(pyxb.binding.basis.element(pyxb.namespace.ExpandedName(Namespace, u'Alphabet'), AlphabetType, scope=PasswordType))

PasswordType._AddElement(pyxb.binding.basis.element(pyxb.namespace.ExpandedName(Namespace, u'Generation'), CTD_ANON_, scope=PasswordType, documentation=u'\n        Indicates whether the password was chosen by the\n        Principal or auto-supplied by the Authentication Authority.\n        principalchosen - the Principal is allowed to choose\n        the value of the password. This is true even if\n        the initial password is chosen at random by the UA or\n        the IdP and the Principal is then free to change\n        the password.\n        automatic - the password is chosen by the UA or the\n        IdP to be cryptographically strong in some sense,\n        or to satisfy certain password rules, and that the\n        Principal is not free to change it or to choose a new password.\n      '))

PasswordType._AddElement(pyxb.binding.basis.element(pyxb.namespace.ExpandedName(Namespace, u'Extension'), ExtensionType, scope=PasswordType))

PasswordType._AddElement(pyxb.binding.basis.element(pyxb.namespace.ExpandedName(Namespace, u'Length'), LengthType, scope=PasswordType, documentation=u'\n        This element indicates the minimum and/or maximum\n        ASCII length of the password which is enforced (by the UA or the\n        IdP). In other words, this is the minimum and/or maximum number of\n        ASCII characters required to represent a valid password.\n        min - the minimum number of ASCII characters required\n        in a valid password, as enforced by the UA or the IdP.\n        max - the maximum number of ASCII characters required\n        in a valid password, as enforced by the UA or the IdP.\n      '))
PasswordType._GroupModel = pyxb.binding.content.GroupSequence(
    pyxb.binding.content.ParticleModel(PasswordType._UseForTag(pyxb.namespace.ExpandedName(Namespace, u'Length')), min_occurs=0L, max_occurs=1),
    pyxb.binding.content.ParticleModel(PasswordType._UseForTag(pyxb.namespace.ExpandedName(Namespace, u'Alphabet')), min_occurs=0L, max_occurs=1),
    pyxb.binding.content.ParticleModel(PasswordType._UseForTag(pyxb.namespace.ExpandedName(Namespace, u'Generation')), min_occurs=0L, max_occurs=1),
    pyxb.binding.content.ParticleModel(PasswordType._UseForTag(pyxb.namespace.ExpandedName(Namespace, u'Extension')), min_occurs=0L, max_occurs=None)
    )
PasswordType._ContentModel = pyxb.binding.content.ParticleModel(PasswordType._GroupModel, min_occurs=1, max_occurs=1)



RestrictedPasswordType._AddElement(pyxb.binding.basis.element(pyxb.namespace.ExpandedName(None, u'Length'), RestrictedLengthType, scope=RestrictedPasswordType))
RestrictedPasswordType._GroupModel = pyxb.binding.content.GroupSequence(
    pyxb.binding.content.ParticleModel(RestrictedPasswordType._UseForTag(pyxb.namespace.ExpandedName(None, u'Length')), min_occurs=1L, max_occurs=1),
    pyxb.binding.content.ParticleModel(RestrictedPasswordType._UseForTag(pyxb.namespace.ExpandedName(Namespace, u'Generation')), min_occurs=0L, max_occurs=1),
    pyxb.binding.content.ParticleModel(RestrictedPasswordType._UseForTag(pyxb.namespace.ExpandedName(Namespace, u'Extension')), min_occurs=0L, max_occurs=None)
    )
RestrictedPasswordType._ContentModel = pyxb.binding.content.ParticleModel(RestrictedPasswordType._GroupModel, min_occurs=1, max_occurs=1)



SharedSecretChallengeResponseType._AddElement(pyxb.binding.basis.element(pyxb.namespace.ExpandedName(Namespace, u'Extension'), ExtensionType, scope=SharedSecretChallengeResponseType))
SharedSecretChallengeResponseType._GroupModel = pyxb.binding.content.GroupSequence(
    pyxb.binding.content.ParticleModel(SharedSecretChallengeResponseType._UseForTag(pyxb.namespace.ExpandedName(Namespace, u'Extension')), min_occurs=0L, max_occurs=None)
    )
SharedSecretChallengeResponseType._ContentModel = pyxb.binding.content.ParticleModel(SharedSecretChallengeResponseType._GroupModel, min_occurs=1, max_occurs=1)



ExtensionOnlyType._AddElement(pyxb.binding.basis.element(pyxb.namespace.ExpandedName(Namespace, u'Extension'), ExtensionType, scope=ExtensionOnlyType))
ExtensionOnlyType._GroupModel = pyxb.binding.content.GroupSequence(
    pyxb.binding.content.ParticleModel(ExtensionOnlyType._UseForTag(pyxb.namespace.ExpandedName(Namespace, u'Extension')), min_occurs=0L, max_occurs=None)
    )
ExtensionOnlyType._ContentModel = pyxb.binding.content.ParticleModel(ExtensionOnlyType._GroupModel, min_occurs=1, max_occurs=1)



ActivationPinType._AddElement(pyxb.binding.basis.element(pyxb.namespace.ExpandedName(Namespace, u'Alphabet'), AlphabetType, scope=ActivationPinType))

ActivationPinType._AddElement(pyxb.binding.basis.element(pyxb.namespace.ExpandedName(Namespace, u'ActivationLimit'), ActivationLimitType, scope=ActivationPinType, documentation=u'\n        This element indicates the length of time for which an\n        PIN-based authentication is valid.\n      '))

ActivationPinType._AddElement(pyxb.binding.basis.element(pyxb.namespace.ExpandedName(Namespace, u'Length'), LengthType, scope=ActivationPinType, documentation=u'\n        This element indicates the minimum and/or maximum\n        ASCII length of the password which is enforced (by the UA or the\n        IdP). In other words, this is the minimum and/or maximum number of\n        ASCII characters required to represent a valid password.\n        min - the minimum number of ASCII characters required\n        in a valid password, as enforced by the UA or the IdP.\n        max - the maximum number of ASCII characters required\n        in a valid password, as enforced by the UA or the IdP.\n      '))

ActivationPinType._AddElement(pyxb.binding.basis.element(pyxb.namespace.ExpandedName(Namespace, u'Extension'), ExtensionType, scope=ActivationPinType))

ActivationPinType._AddElement(pyxb.binding.basis.element(pyxb.namespace.ExpandedName(Namespace, u'Generation'), CTD_ANON_, scope=ActivationPinType, documentation=u'\n        Indicates whether the password was chosen by the\n        Principal or auto-supplied by the Authentication Authority.\n        principalchosen - the Principal is allowed to choose\n        the value of the password. This is true even if\n        the initial password is chosen at random by the UA or\n        the IdP and the Principal is then free to change\n        the password.\n        automatic - the password is chosen by the UA or the\n        IdP to be cryptographically strong in some sense,\n        or to satisfy certain password rules, and that the\n        Principal is not free to change it or to choose a new password.\n      '))
ActivationPinType._GroupModel = pyxb.binding.content.GroupSequence(
    pyxb.binding.content.ParticleModel(ActivationPinType._UseForTag(pyxb.namespace.ExpandedName(Namespace, u'Length')), min_occurs=0L, max_occurs=1),
    pyxb.binding.content.ParticleModel(ActivationPinType._UseForTag(pyxb.namespace.ExpandedName(Namespace, u'Alphabet')), min_occurs=0L, max_occurs=1),
    pyxb.binding.content.ParticleModel(ActivationPinType._UseForTag(pyxb.namespace.ExpandedName(Namespace, u'Generation')), min_occurs=0L, max_occurs=1),
    pyxb.binding.content.ParticleModel(ActivationPinType._UseForTag(pyxb.namespace.ExpandedName(Namespace, u'ActivationLimit')), min_occurs=0L, max_occurs=1),
    pyxb.binding.content.ParticleModel(ActivationPinType._UseForTag(pyxb.namespace.ExpandedName(Namespace, u'Extension')), min_occurs=0L, max_occurs=None)
    )
ActivationPinType._ContentModel = pyxb.binding.content.ParticleModel(ActivationPinType._GroupModel, min_occurs=1, max_occurs=1)



AuthnContextDeclarationBaseType._AddElement(pyxb.binding.basis.element(pyxb.namespace.ExpandedName(Namespace, u'Identification'), IdentificationType, scope=AuthnContextDeclarationBaseType, documentation=u'\n        Refers to those characteristics that describe the\n        processes and mechanisms\n        the Authentication Authority uses to initially create\n        an association between a Principal\n        and the identity (or name) by which the Principal will\n        be known\n      '))

AuthnContextDeclarationBaseType._AddElement(pyxb.binding.basis.element(pyxb.namespace.ExpandedName(Namespace, u'GoverningAgreements'), GoverningAgreementsType, scope=AuthnContextDeclarationBaseType, documentation=u'\n        Provides a mechanism for linking to external (likely\n        human readable) documents in which additional business agreements,\n        (e.g. liability constraints, obligations, etc) can be placed.\n      '))

AuthnContextDeclarationBaseType._AddElement(pyxb.binding.basis.element(pyxb.namespace.ExpandedName(Namespace, u'TechnicalProtection'), TechnicalProtectionBaseType, scope=AuthnContextDeclarationBaseType, documentation=u"\n        Refers to those characterstics that describe how the\n        'secret' (the knowledge or possession\n        of which allows the Principal to authenticate to the\n        Authentication Authority) is kept secure\n      "))

AuthnContextDeclarationBaseType._AddElement(pyxb.binding.basis.element(pyxb.namespace.ExpandedName(Namespace, u'Extension'), ExtensionType, scope=AuthnContextDeclarationBaseType))

AuthnContextDeclarationBaseType._AddElement(pyxb.binding.basis.element(pyxb.namespace.ExpandedName(Namespace, u'OperationalProtection'), OperationalProtectionType, scope=AuthnContextDeclarationBaseType, documentation=u'\n        Refers to those characteristics that describe\n        procedural security controls employed by the Authentication Authority.\n      '))

AuthnContextDeclarationBaseType._AddElement(pyxb.binding.basis.element(pyxb.namespace.ExpandedName(Namespace, u'AuthnMethod'), AuthnMethodBaseType, scope=AuthnContextDeclarationBaseType, documentation=u'\n        Refers to those characteristics that define the\n        mechanisms by which the Principal authenticates to the Authentication\n        Authority.\n      '))
AuthnContextDeclarationBaseType._GroupModel = pyxb.binding.content.GroupSequence(
    pyxb.binding.content.ParticleModel(AuthnContextDeclarationBaseType._UseForTag(pyxb.namespace.ExpandedName(Namespace, u'Identification')), min_occurs=0L, max_occurs=1),
    pyxb.binding.content.ParticleModel(AuthnContextDeclarationBaseType._UseForTag(pyxb.namespace.ExpandedName(Namespace, u'TechnicalProtection')), min_occurs=0L, max_occurs=1),
    pyxb.binding.content.ParticleModel(AuthnContextDeclarationBaseType._UseForTag(pyxb.namespace.ExpandedName(Namespace, u'OperationalProtection')), min_occurs=0L, max_occurs=1),
    pyxb.binding.content.ParticleModel(AuthnContextDeclarationBaseType._UseForTag(pyxb.namespace.ExpandedName(Namespace, u'AuthnMethod')), min_occurs=1, max_occurs=1),
    pyxb.binding.content.ParticleModel(AuthnContextDeclarationBaseType._UseForTag(pyxb.namespace.ExpandedName(Namespace, u'GoverningAgreements')), min_occurs=0L, max_occurs=1),
    pyxb.binding.content.ParticleModel(AuthnContextDeclarationBaseType._UseForTag(pyxb.namespace.ExpandedName(Namespace, u'Extension')), min_occurs=0L, max_occurs=None)
    )
AuthnContextDeclarationBaseType._ContentModel = pyxb.binding.content.ParticleModel(AuthnContextDeclarationBaseType._GroupModel, min_occurs=1, max_occurs=1)



ActivationLimitType._AddElement(pyxb.binding.basis.element(pyxb.namespace.ExpandedName(Namespace, u'ActivationLimitDuration'), ActivationLimitDurationType, scope=ActivationLimitType, documentation=u'\n        This element indicates that the Key Activation Limit is\n        defined as a specific duration of time.\n      '))

ActivationLimitType._AddElement(pyxb.binding.basis.element(pyxb.namespace.ExpandedName(Namespace, u'ActivationLimitUsages'), ActivationLimitUsagesType, scope=ActivationLimitType, documentation=u'\n        This element indicates that the Key Activation Limit is\n        defined as a number of usages.\n      '))

ActivationLimitType._AddElement(pyxb.binding.basis.element(pyxb.namespace.ExpandedName(Namespace, u'ActivationLimitSession'), ActivationLimitSessionType, scope=ActivationLimitType, documentation=u'\n        This element indicates that the Key Activation Limit is\n        the session.\n      '))
ActivationLimitType._GroupModel = pyxb.binding.content.GroupChoice(
    pyxb.binding.content.ParticleModel(ActivationLimitType._UseForTag(pyxb.namespace.ExpandedName(Namespace, u'ActivationLimitDuration')), min_occurs=1, max_occurs=1),
    pyxb.binding.content.ParticleModel(ActivationLimitType._UseForTag(pyxb.namespace.ExpandedName(Namespace, u'ActivationLimitUsages')), min_occurs=1, max_occurs=1),
    pyxb.binding.content.ParticleModel(ActivationLimitType._UseForTag(pyxb.namespace.ExpandedName(Namespace, u'ActivationLimitSession')), min_occurs=1, max_occurs=1)
    )
ActivationLimitType._ContentModel = pyxb.binding.content.ParticleModel(ActivationLimitType._GroupModel, min_occurs=1, max_occurs=1)



ComplexAuthenticatorType._AddElement(pyxb.binding.basis.element(pyxb.namespace.ExpandedName(Namespace, u'Extension'), ExtensionType, scope=ComplexAuthenticatorType))

ComplexAuthenticatorType._AddElement(pyxb.binding.basis.element(pyxb.namespace.ExpandedName(Namespace, u'SubscriberLineNumber'), ExtensionOnlyType, scope=ComplexAuthenticatorType))

ComplexAuthenticatorType._AddElement(pyxb.binding.basis.element(pyxb.namespace.ExpandedName(Namespace, u'IPAddress'), ExtensionOnlyType, scope=ComplexAuthenticatorType, documentation=u'\n        This element indicates that the Principal has been\n        authenticated through connection from a particular IP address.\n      '))

ComplexAuthenticatorType._AddElement(pyxb.binding.basis.element(pyxb.namespace.ExpandedName(Namespace, u'ComplexAuthenticator'), ComplexAuthenticatorType, scope=ComplexAuthenticatorType, documentation=u'\n        Supports Authenticators with nested combinations of\n        additional complexity.\n      '))

ComplexAuthenticatorType._AddElement(pyxb.binding.basis.element(pyxb.namespace.ExpandedName(Namespace, u'ZeroKnowledge'), ExtensionOnlyType, scope=ComplexAuthenticatorType, documentation=u'\n        This element indicates that the Principal has been\n        authenticated by a zero knowledge technique as specified in ISO/IEC\n        9798-5.\n      '))

ComplexAuthenticatorType._AddElement(pyxb.binding.basis.element(pyxb.namespace.ExpandedName(Namespace, u'DigSig'), PublicKeyType, scope=ComplexAuthenticatorType, documentation=u'\n        This element indicates that the Principal has been\n        authenticated by a mechanism which involves the Principal computing a\n        digital signature over at least challenge data provided by the IdP.\n      '))

ComplexAuthenticatorType._AddElement(pyxb.binding.basis.element(pyxb.namespace.ExpandedName(Namespace, u'RestrictedPassword'), RestrictedPasswordType, scope=ComplexAuthenticatorType))

ComplexAuthenticatorType._AddElement(pyxb.binding.basis.element(pyxb.namespace.ExpandedName(Namespace, u'UserSuffix'), ExtensionOnlyType, scope=ComplexAuthenticatorType))

ComplexAuthenticatorType._AddElement(pyxb.binding.basis.element(pyxb.namespace.ExpandedName(Namespace, u'AsymmetricDecryption'), PublicKeyType, scope=ComplexAuthenticatorType, documentation=u"\n        The local system has a private key but it is used\n        in decryption mode, rather than signature mode. For example, the\n        Authentication Authority generates a secret and encrypts it using the\n        local system's public key: the local system then proves it has\n        decrypted the secret.\n      "))

ComplexAuthenticatorType._AddElement(pyxb.binding.basis.element(pyxb.namespace.ExpandedName(Namespace, u'SharedSecretChallengeResponse'), SharedSecretChallengeResponseType, scope=ComplexAuthenticatorType))

ComplexAuthenticatorType._AddElement(pyxb.binding.basis.element(pyxb.namespace.ExpandedName(Namespace, u'Password'), PasswordType, scope=ComplexAuthenticatorType, documentation=u'\n        This element indicates that a password (or passphrase)\n        has been used to\n        authenticate the Principal to a remote system.\n      '))

ComplexAuthenticatorType._AddElement(pyxb.binding.basis.element(pyxb.namespace.ExpandedName(Namespace, u'PreviousSession'), ExtensionOnlyType, scope=ComplexAuthenticatorType, documentation=u'\n        Indicates that the Principal has been strongly\n        authenticated in a previous session during which the IdP has set a\n        cookie in the UA. During the present session the Principal has only\n        been authenticated by the UA returning the cookie to the IdP.\n      '))

ComplexAuthenticatorType._AddElement(pyxb.binding.basis.element(pyxb.namespace.ExpandedName(Namespace, u'AsymmetricKeyAgreement'), PublicKeyType, scope=ComplexAuthenticatorType, documentation=u'\n        The local system has a private key and uses it for\n        shared secret key agreement with the Authentication Authority (e.g.\n        via Diffie Helman).\n      '))

ComplexAuthenticatorType._AddElement(pyxb.binding.basis.element(pyxb.namespace.ExpandedName(Namespace, u'SharedSecretDynamicPlaintext'), ExtensionOnlyType, scope=ComplexAuthenticatorType, documentation=u'\n        The local system and Authentication Authority\n        share a secret key. The local system uses this to encrypt a\n        randomised string to pass to the Authentication Authority.\n      '))

ComplexAuthenticatorType._AddElement(pyxb.binding.basis.element(pyxb.namespace.ExpandedName(Namespace, u'ResumeSession'), ExtensionOnlyType, scope=ComplexAuthenticatorType, documentation=u'\n        Rather like PreviousSession but using stronger\n        security. A secret that was established in a previous session with\n        the Authentication Authority has been cached by the local system and\n        is now re-used (e.g. a Master Secret is used to derive new session\n        keys in TLS, SSL, WTLS).\n      '))
ComplexAuthenticatorType._GroupModel_ = pyxb.binding.content.GroupChoice(
    pyxb.binding.content.ParticleModel(ComplexAuthenticatorType._UseForTag(pyxb.namespace.ExpandedName(Namespace, u'PreviousSession')), min_occurs=1, max_occurs=1),
    pyxb.binding.content.ParticleModel(ComplexAuthenticatorType._UseForTag(pyxb.namespace.ExpandedName(Namespace, u'ResumeSession')), min_occurs=1, max_occurs=1),
    pyxb.binding.content.ParticleModel(ComplexAuthenticatorType._UseForTag(pyxb.namespace.ExpandedName(Namespace, u'DigSig')), min_occurs=1, max_occurs=1),
    pyxb.binding.content.ParticleModel(ComplexAuthenticatorType._UseForTag(pyxb.namespace.ExpandedName(Namespace, u'Password')), min_occurs=1, max_occurs=1),
    pyxb.binding.content.ParticleModel(ComplexAuthenticatorType._UseForTag(pyxb.namespace.ExpandedName(Namespace, u'RestrictedPassword')), min_occurs=1, max_occurs=1),
    pyxb.binding.content.ParticleModel(ComplexAuthenticatorType._UseForTag(pyxb.namespace.ExpandedName(Namespace, u'ZeroKnowledge')), min_occurs=1, max_occurs=1),
    pyxb.binding.content.ParticleModel(ComplexAuthenticatorType._UseForTag(pyxb.namespace.ExpandedName(Namespace, u'SharedSecretChallengeResponse')), min_occurs=1, max_occurs=1),
    pyxb.binding.content.ParticleModel(ComplexAuthenticatorType._UseForTag(pyxb.namespace.ExpandedName(Namespace, u'SharedSecretDynamicPlaintext')), min_occurs=1, max_occurs=1),
    pyxb.binding.content.ParticleModel(ComplexAuthenticatorType._UseForTag(pyxb.namespace.ExpandedName(Namespace, u'IPAddress')), min_occurs=1, max_occurs=1),
    pyxb.binding.content.ParticleModel(ComplexAuthenticatorType._UseForTag(pyxb.namespace.ExpandedName(Namespace, u'AsymmetricDecryption')), min_occurs=1, max_occurs=1),
    pyxb.binding.content.ParticleModel(ComplexAuthenticatorType._UseForTag(pyxb.namespace.ExpandedName(Namespace, u'AsymmetricKeyAgreement')), min_occurs=1, max_occurs=1),
    pyxb.binding.content.ParticleModel(ComplexAuthenticatorType._UseForTag(pyxb.namespace.ExpandedName(Namespace, u'SubscriberLineNumber')), min_occurs=1, max_occurs=1),
    pyxb.binding.content.ParticleModel(ComplexAuthenticatorType._UseForTag(pyxb.namespace.ExpandedName(Namespace, u'UserSuffix')), min_occurs=1, max_occurs=1),
    pyxb.binding.content.ParticleModel(ComplexAuthenticatorType._UseForTag(pyxb.namespace.ExpandedName(Namespace, u'ComplexAuthenticator')), min_occurs=1, max_occurs=1)
    )
ComplexAuthenticatorType._GroupModel_2 = pyxb.binding.content.GroupSequence(
    pyxb.binding.content.ParticleModel(ComplexAuthenticatorType._UseForTag(pyxb.namespace.ExpandedName(Namespace, u'PreviousSession')), min_occurs=0L, max_occurs=1),
    pyxb.binding.content.ParticleModel(ComplexAuthenticatorType._UseForTag(pyxb.namespace.ExpandedName(Namespace, u'ResumeSession')), min_occurs=0L, max_occurs=1),
    pyxb.binding.content.ParticleModel(ComplexAuthenticatorType._UseForTag(pyxb.namespace.ExpandedName(Namespace, u'DigSig')), min_occurs=0L, max_occurs=1),
    pyxb.binding.content.ParticleModel(ComplexAuthenticatorType._UseForTag(pyxb.namespace.ExpandedName(Namespace, u'Password')), min_occurs=0L, max_occurs=1),
    pyxb.binding.content.ParticleModel(ComplexAuthenticatorType._UseForTag(pyxb.namespace.ExpandedName(Namespace, u'RestrictedPassword')), min_occurs=0L, max_occurs=1),
    pyxb.binding.content.ParticleModel(ComplexAuthenticatorType._UseForTag(pyxb.namespace.ExpandedName(Namespace, u'ZeroKnowledge')), min_occurs=0L, max_occurs=1),
    pyxb.binding.content.ParticleModel(ComplexAuthenticatorType._UseForTag(pyxb.namespace.ExpandedName(Namespace, u'SharedSecretChallengeResponse')), min_occurs=0L, max_occurs=1),
    pyxb.binding.content.ParticleModel(ComplexAuthenticatorType._UseForTag(pyxb.namespace.ExpandedName(Namespace, u'SharedSecretDynamicPlaintext')), min_occurs=0L, max_occurs=1),
    pyxb.binding.content.ParticleModel(ComplexAuthenticatorType._UseForTag(pyxb.namespace.ExpandedName(Namespace, u'IPAddress')), min_occurs=0L, max_occurs=1),
    pyxb.binding.content.ParticleModel(ComplexAuthenticatorType._UseForTag(pyxb.namespace.ExpandedName(Namespace, u'AsymmetricDecryption')), min_occurs=0L, max_occurs=1),
    pyxb.binding.content.ParticleModel(ComplexAuthenticatorType._UseForTag(pyxb.namespace.ExpandedName(Namespace, u'AsymmetricKeyAgreement')), min_occurs=0L, max_occurs=1),
    pyxb.binding.content.ParticleModel(ComplexAuthenticatorType._UseForTag(pyxb.namespace.ExpandedName(Namespace, u'SubscriberLineNumber')), min_occurs=0L, max_occurs=1),
    pyxb.binding.content.ParticleModel(ComplexAuthenticatorType._UseForTag(pyxb.namespace.ExpandedName(Namespace, u'UserSuffix')), min_occurs=0L, max_occurs=1),
    pyxb.binding.content.ParticleModel(ComplexAuthenticatorType._UseForTag(pyxb.namespace.ExpandedName(Namespace, u'Extension')), min_occurs=0L, max_occurs=None)
    )
ComplexAuthenticatorType._GroupModel = pyxb.binding.content.GroupSequence(
    pyxb.binding.content.ParticleModel(ComplexAuthenticatorType._GroupModel_, min_occurs=1, max_occurs=1),
    pyxb.binding.content.ParticleModel(ComplexAuthenticatorType._GroupModel_2, min_occurs=1, max_occurs=1)
    )
ComplexAuthenticatorType._ContentModel = pyxb.binding.content.ParticleModel(ComplexAuthenticatorType._GroupModel, min_occurs=1, max_occurs=1)



AuthenticatorTransportProtocolType._AddElement(pyxb.binding.basis.element(pyxb.namespace.ExpandedName(Namespace, u'MobileNetworkRadioEncryption'), ExtensionOnlyType, scope=AuthenticatorTransportProtocolType))

AuthenticatorTransportProtocolType._AddElement(pyxb.binding.basis.element(pyxb.namespace.ExpandedName(Namespace, u'Extension'), ExtensionType, scope=AuthenticatorTransportProtocolType))

AuthenticatorTransportProtocolType._AddElement(pyxb.binding.basis.element(pyxb.namespace.ExpandedName(Namespace, u'MobileNetworkEndToEndEncryption'), ExtensionOnlyType, scope=AuthenticatorTransportProtocolType))

AuthenticatorTransportProtocolType._AddElement(pyxb.binding.basis.element(pyxb.namespace.ExpandedName(Namespace, u'SSL'), ExtensionOnlyType, scope=AuthenticatorTransportProtocolType, documentation=u'\n        This element indicates that the Authenticator has been\n        transmitted using a transport mechnanism protected by an SSL or TLS\n        session.\n      '))

AuthenticatorTransportProtocolType._AddElement(pyxb.binding.basis.element(pyxb.namespace.ExpandedName(Namespace, u'WTLS'), ExtensionOnlyType, scope=AuthenticatorTransportProtocolType, documentation=u'\n        This element indicates that the Authenticator has been\n        transmitted using a transport mechanism protected by a WTLS session.\n      '))

AuthenticatorTransportProtocolType._AddElement(pyxb.binding.basis.element(pyxb.namespace.ExpandedName(Namespace, u'IPSec'), ExtensionOnlyType, scope=AuthenticatorTransportProtocolType, documentation=u'\n        This element indicates that the Authenticator has been\n        transmitted using a transport mechanism protected by an IPSEC session.\n      '))

AuthenticatorTransportProtocolType._AddElement(pyxb.binding.basis.element(pyxb.namespace.ExpandedName(Namespace, u'MobileNetworkNoEncryption'), ExtensionOnlyType, scope=AuthenticatorTransportProtocolType, documentation=u'\n        This element indicates that the Authenticator has been\n        transmitted solely across a mobile network using no additional\n        security mechanism.\n      '))
AuthenticatorTransportProtocolType._GroupModel_ = pyxb.binding.content.GroupChoice(
    pyxb.binding.content.ParticleModel(AuthenticatorTransportProtocolType._UseForTag(pyxb.namespace.ExpandedName(Namespace, u'SSL')), min_occurs=1, max_occurs=1),
    pyxb.binding.content.ParticleModel(AuthenticatorTransportProtocolType._UseForTag(pyxb.namespace.ExpandedName(Namespace, u'MobileNetworkNoEncryption')), min_occurs=1, max_occurs=1),
    pyxb.binding.content.ParticleModel(AuthenticatorTransportProtocolType._UseForTag(pyxb.namespace.ExpandedName(Namespace, u'MobileNetworkRadioEncryption')), min_occurs=1, max_occurs=1),
    pyxb.binding.content.ParticleModel(AuthenticatorTransportProtocolType._UseForTag(pyxb.namespace.ExpandedName(Namespace, u'MobileNetworkEndToEndEncryption')), min_occurs=1, max_occurs=1),
    pyxb.binding.content.ParticleModel(AuthenticatorTransportProtocolType._UseForTag(pyxb.namespace.ExpandedName(Namespace, u'WTLS')), min_occurs=1, max_occurs=1),
    pyxb.binding.content.ParticleModel(AuthenticatorTransportProtocolType._UseForTag(pyxb.namespace.ExpandedName(Namespace, u'IPSec')), min_occurs=1, max_occurs=1)
    )
AuthenticatorTransportProtocolType._GroupModel = pyxb.binding.content.GroupSequence(
    pyxb.binding.content.ParticleModel(AuthenticatorTransportProtocolType._GroupModel_, min_occurs=1, max_occurs=1),
    pyxb.binding.content.ParticleModel(AuthenticatorTransportProtocolType._UseForTag(pyxb.namespace.ExpandedName(Namespace, u'Extension')), min_occurs=0L, max_occurs=None)
    )
AuthenticatorTransportProtocolType._ContentModel = pyxb.binding.content.ParticleModel(AuthenticatorTransportProtocolType._GroupModel, min_occurs=1, max_occurs=1)



OperationalProtectionType._AddElement(pyxb.binding.basis.element(pyxb.namespace.ExpandedName(Namespace, u'DeactivationCallCenter'), ExtensionOnlyType, scope=OperationalProtectionType))

OperationalProtectionType._AddElement(pyxb.binding.basis.element(pyxb.namespace.ExpandedName(Namespace, u'Extension'), ExtensionType, scope=OperationalProtectionType))

OperationalProtectionType._AddElement(pyxb.binding.basis.element(pyxb.namespace.ExpandedName(Namespace, u'SecurityAudit'), SecurityAuditType, scope=OperationalProtectionType))
OperationalProtectionType._GroupModel = pyxb.binding.content.GroupSequence(
    pyxb.binding.content.ParticleModel(OperationalProtectionType._UseForTag(pyxb.namespace.ExpandedName(Namespace, u'SecurityAudit')), min_occurs=0L, max_occurs=1),
    pyxb.binding.content.ParticleModel(OperationalProtectionType._UseForTag(pyxb.namespace.ExpandedName(Namespace, u'DeactivationCallCenter')), min_occurs=0L, max_occurs=1),
    pyxb.binding.content.ParticleModel(OperationalProtectionType._UseForTag(pyxb.namespace.ExpandedName(Namespace, u'Extension')), min_occurs=0L, max_occurs=None)
    )
OperationalProtectionType._ContentModel = pyxb.binding.content.ParticleModel(OperationalProtectionType._GroupModel, min_occurs=1, max_occurs=1)



SecurityAuditType._AddElement(pyxb.binding.basis.element(pyxb.namespace.ExpandedName(Namespace, u'Extension'), ExtensionType, scope=SecurityAuditType))

SecurityAuditType._AddElement(pyxb.binding.basis.element(pyxb.namespace.ExpandedName(Namespace, u'SwitchAudit'), ExtensionOnlyType, scope=SecurityAuditType))
SecurityAuditType._GroupModel = pyxb.binding.content.GroupSequence(
    pyxb.binding.content.ParticleModel(SecurityAuditType._UseForTag(pyxb.namespace.ExpandedName(Namespace, u'SwitchAudit')), min_occurs=0L, max_occurs=1),
    pyxb.binding.content.ParticleModel(SecurityAuditType._UseForTag(pyxb.namespace.ExpandedName(Namespace, u'Extension')), min_occurs=0L, max_occurs=None)
    )
SecurityAuditType._ContentModel = pyxb.binding.content.ParticleModel(SecurityAuditType._GroupModel, min_occurs=1, max_occurs=1)



GoverningAgreementsType._AddElement(pyxb.binding.basis.element(pyxb.namespace.ExpandedName(Namespace, u'GoverningAgreementRef'), GoverningAgreementRefType, scope=GoverningAgreementsType))
GoverningAgreementsType._GroupModel = pyxb.binding.content.GroupSequence(
    pyxb.binding.content.ParticleModel(GoverningAgreementsType._UseForTag(pyxb.namespace.ExpandedName(Namespace, u'GoverningAgreementRef')), min_occurs=1, max_occurs=None)
    )
GoverningAgreementsType._ContentModel = pyxb.binding.content.ParticleModel(GoverningAgreementsType._GroupModel, min_occurs=1, max_occurs=1)



TokenType._AddElement(pyxb.binding.basis.element(pyxb.namespace.ExpandedName(Namespace, u'Extension'), ExtensionType, scope=TokenType))

TokenType._AddElement(pyxb.binding.basis.element(pyxb.namespace.ExpandedName(Namespace, u'TimeSyncToken'), TimeSyncTokenType, scope=TokenType, documentation=u'\n        This element indicates that a time synchronization\n        token is used to identify the Principal. hardware -\n        the time synchonization\n        token has been implemented in hardware. software - the\n        time synchronization\n        token has been implemented in software. SeedLength -\n        the length, in bits, of the\n        random seed used in the time synchronization token.\n      '))
TokenType._GroupModel = pyxb.binding.content.GroupSequence(
    pyxb.binding.content.ParticleModel(TokenType._UseForTag(pyxb.namespace.ExpandedName(Namespace, u'TimeSyncToken')), min_occurs=1, max_occurs=1),
    pyxb.binding.content.ParticleModel(TokenType._UseForTag(pyxb.namespace.ExpandedName(Namespace, u'Extension')), min_occurs=0L, max_occurs=None)
    )
TokenType._ContentModel = pyxb.binding.content.ParticleModel(TokenType._GroupModel, min_occurs=1, max_occurs=1)



IdentificationType._AddElement(pyxb.binding.basis.element(pyxb.namespace.ExpandedName(Namespace, u'Extension'), ExtensionType, scope=IdentificationType))

IdentificationType._AddElement(pyxb.binding.basis.element(pyxb.namespace.ExpandedName(Namespace, u'WrittenConsent'), ExtensionOnlyType, scope=IdentificationType))

IdentificationType._AddElement(pyxb.binding.basis.element(pyxb.namespace.ExpandedName(Namespace, u'GoverningAgreements'), GoverningAgreementsType, scope=IdentificationType, documentation=u'\n        Provides a mechanism for linking to external (likely\n        human readable) documents in which additional business agreements,\n        (e.g. liability constraints, obligations, etc) can be placed.\n      '))

IdentificationType._AddElement(pyxb.binding.basis.element(pyxb.namespace.ExpandedName(Namespace, u'PhysicalVerification'), CTD_ANON, scope=IdentificationType, documentation=u'\n        This element indicates that identification has been\n        performed in a physical\n        face-to-face meeting with the principal and not in an\n        online manner.\n      '))
IdentificationType._GroupModel = pyxb.binding.content.GroupSequence(
    pyxb.binding.content.ParticleModel(IdentificationType._UseForTag(pyxb.namespace.ExpandedName(Namespace, u'PhysicalVerification')), min_occurs=0L, max_occurs=1),
    pyxb.binding.content.ParticleModel(IdentificationType._UseForTag(pyxb.namespace.ExpandedName(Namespace, u'WrittenConsent')), min_occurs=0L, max_occurs=1),
    pyxb.binding.content.ParticleModel(IdentificationType._UseForTag(pyxb.namespace.ExpandedName(Namespace, u'GoverningAgreements')), min_occurs=0L, max_occurs=1),
    pyxb.binding.content.ParticleModel(IdentificationType._UseForTag(pyxb.namespace.ExpandedName(Namespace, u'Extension')), min_occurs=0L, max_occurs=None)
    )
IdentificationType._ContentModel = pyxb.binding.content.ParticleModel(IdentificationType._GroupModel, min_occurs=1, max_occurs=1)



PrivateKeyProtectionType._AddElement(pyxb.binding.basis.element(pyxb.namespace.ExpandedName(Namespace, u'KeyActivation'), KeyActivationType, scope=PrivateKeyProtectionType, documentation=u'The actions that must be performed\n        before the private key can be used. '))

PrivateKeyProtectionType._AddElement(pyxb.binding.basis.element(pyxb.namespace.ExpandedName(Namespace, u'KeyStorage'), KeyStorageType, scope=PrivateKeyProtectionType, documentation=u'\n        In which medium is the key stored.\n        memory - the key is stored in memory.\n        smartcard - the key is stored in a smartcard.\n        token - the key is stored in a hardware token.\n        MobileDevice - the key is stored in a mobile device.\n        MobileAuthCard - the key is stored in a mobile\n        authentication card.\n      '))

PrivateKeyProtectionType._AddElement(pyxb.binding.basis.element(pyxb.namespace.ExpandedName(Namespace, u'KeySharing'), KeySharingType, scope=PrivateKeyProtectionType, documentation=u'Whether or not the private key is shared\n        with the certificate authority.'))

PrivateKeyProtectionType._AddElement(pyxb.binding.basis.element(pyxb.namespace.ExpandedName(Namespace, u'Extension'), ExtensionType, scope=PrivateKeyProtectionType))
PrivateKeyProtectionType._GroupModel = pyxb.binding.content.GroupSequence(
    pyxb.binding.content.ParticleModel(PrivateKeyProtectionType._UseForTag(pyxb.namespace.ExpandedName(Namespace, u'KeyActivation')), min_occurs=0L, max_occurs=1),
    pyxb.binding.content.ParticleModel(PrivateKeyProtectionType._UseForTag(pyxb.namespace.ExpandedName(Namespace, u'KeyStorage')), min_occurs=0L, max_occurs=1),
    pyxb.binding.content.ParticleModel(PrivateKeyProtectionType._UseForTag(pyxb.namespace.ExpandedName(Namespace, u'KeySharing')), min_occurs=0L, max_occurs=1),
    pyxb.binding.content.ParticleModel(PrivateKeyProtectionType._UseForTag(pyxb.namespace.ExpandedName(Namespace, u'Extension')), min_occurs=0L, max_occurs=None)
    )
PrivateKeyProtectionType._ContentModel = pyxb.binding.content.ParticleModel(PrivateKeyProtectionType._GroupModel, min_occurs=1, max_occurs=1)



SecretKeyProtectionType._AddElement(pyxb.binding.basis.element(pyxb.namespace.ExpandedName(Namespace, u'Extension'), ExtensionType, scope=SecretKeyProtectionType))

SecretKeyProtectionType._AddElement(pyxb.binding.basis.element(pyxb.namespace.ExpandedName(Namespace, u'KeyActivation'), KeyActivationType, scope=SecretKeyProtectionType, documentation=u'The actions that must be performed\n        before the private key can be used. '))

SecretKeyProtectionType._AddElement(pyxb.binding.basis.element(pyxb.namespace.ExpandedName(Namespace, u'KeyStorage'), KeyStorageType, scope=SecretKeyProtectionType, documentation=u'\n        In which medium is the key stored.\n        memory - the key is stored in memory.\n        smartcard - the key is stored in a smartcard.\n        token - the key is stored in a hardware token.\n        MobileDevice - the key is stored in a mobile device.\n        MobileAuthCard - the key is stored in a mobile\n        authentication card.\n      '))
SecretKeyProtectionType._GroupModel = pyxb.binding.content.GroupSequence(
    pyxb.binding.content.ParticleModel(SecretKeyProtectionType._UseForTag(pyxb.namespace.ExpandedName(Namespace, u'KeyActivation')), min_occurs=0L, max_occurs=1),
    pyxb.binding.content.ParticleModel(SecretKeyProtectionType._UseForTag(pyxb.namespace.ExpandedName(Namespace, u'KeyStorage')), min_occurs=0L, max_occurs=1),
    pyxb.binding.content.ParticleModel(SecretKeyProtectionType._UseForTag(pyxb.namespace.ExpandedName(Namespace, u'Extension')), min_occurs=0L, max_occurs=None)
    )
SecretKeyProtectionType._ContentModel = pyxb.binding.content.ParticleModel(SecretKeyProtectionType._GroupModel, min_occurs=1, max_occurs=1)



TechnicalProtectionBaseType._AddElement(pyxb.binding.basis.element(pyxb.namespace.ExpandedName(Namespace, u'Extension'), ExtensionType, scope=TechnicalProtectionBaseType))

TechnicalProtectionBaseType._AddElement(pyxb.binding.basis.element(pyxb.namespace.ExpandedName(Namespace, u'SecretKeyProtection'), SecretKeyProtectionType, scope=TechnicalProtectionBaseType, documentation=u'\n        This element indicates the types and strengths of\n        facilities\n        of a UA used to protect a shared secret key from\n        unauthorized access and/or use.\n      '))

TechnicalProtectionBaseType._AddElement(pyxb.binding.basis.element(pyxb.namespace.ExpandedName(Namespace, u'PrivateKeyProtection'), PrivateKeyProtectionType, scope=TechnicalProtectionBaseType, documentation=u'\n        This element indicates the types and strengths of\n        facilities\n        of a UA used to protect a private key from\n        unauthorized access and/or use.\n      '))
TechnicalProtectionBaseType._GroupModel_ = pyxb.binding.content.GroupChoice(
    pyxb.binding.content.ParticleModel(TechnicalProtectionBaseType._UseForTag(pyxb.namespace.ExpandedName(Namespace, u'PrivateKeyProtection')), min_occurs=1, max_occurs=1),
    pyxb.binding.content.ParticleModel(TechnicalProtectionBaseType._UseForTag(pyxb.namespace.ExpandedName(Namespace, u'SecretKeyProtection')), min_occurs=1, max_occurs=1)
    )
TechnicalProtectionBaseType._GroupModel = pyxb.binding.content.GroupSequence(
    pyxb.binding.content.ParticleModel(TechnicalProtectionBaseType._GroupModel_, min_occurs=0L, max_occurs=1),
    pyxb.binding.content.ParticleModel(TechnicalProtectionBaseType._UseForTag(pyxb.namespace.ExpandedName(Namespace, u'Extension')), min_occurs=0L, max_occurs=None)
    )
TechnicalProtectionBaseType._ContentModel = pyxb.binding.content.ParticleModel(TechnicalProtectionBaseType._GroupModel, min_occurs=1, max_occurs=1)



KeyActivationType._AddElement(pyxb.binding.basis.element(pyxb.namespace.ExpandedName(Namespace, u'Extension'), ExtensionType, scope=KeyActivationType))

KeyActivationType._AddElement(pyxb.binding.basis.element(pyxb.namespace.ExpandedName(Namespace, u'ActivationPin'), ActivationPinType, scope=KeyActivationType, documentation=u'\n        This element indicates that a Pin (Personal\n        Identification Number) has been used to authenticate the Principal to\n        some local system in order to activate a key.\n      '))
KeyActivationType._GroupModel = pyxb.binding.content.GroupSequence(
    pyxb.binding.content.ParticleModel(KeyActivationType._UseForTag(pyxb.namespace.ExpandedName(Namespace, u'ActivationPin')), min_occurs=0L, max_occurs=1),
    pyxb.binding.content.ParticleModel(KeyActivationType._UseForTag(pyxb.namespace.ExpandedName(Namespace, u'Extension')), min_occurs=0L, max_occurs=None)
    )
KeyActivationType._ContentModel = pyxb.binding.content.ParticleModel(KeyActivationType._GroupModel, min_occurs=1, max_occurs=1)



PrincipalAuthenticationMechanismType._AddElement(pyxb.binding.basis.element(pyxb.namespace.ExpandedName(Namespace, u'Extension'), ExtensionType, scope=PrincipalAuthenticationMechanismType))

PrincipalAuthenticationMechanismType._AddElement(pyxb.binding.basis.element(pyxb.namespace.ExpandedName(Namespace, u'Token'), TokenType, scope=PrincipalAuthenticationMechanismType, documentation=u'\n        This element indicates that a hardware or software\n        token is used\n        as a method of identifying the Principal.\n      '))

PrincipalAuthenticationMechanismType._AddElement(pyxb.binding.basis.element(pyxb.namespace.ExpandedName(Namespace, u'Smartcard'), ExtensionOnlyType, scope=PrincipalAuthenticationMechanismType, documentation=u'\n        This element indicates that a smartcard is used to\n        identity the Principal.\n      '))

PrincipalAuthenticationMechanismType._AddElement(pyxb.binding.basis.element(pyxb.namespace.ExpandedName(Namespace, u'Password'), PasswordType, scope=PrincipalAuthenticationMechanismType, documentation=u'\n        This element indicates that a password (or passphrase)\n        has been used to\n        authenticate the Principal to a remote system.\n      '))

PrincipalAuthenticationMechanismType._AddElement(pyxb.binding.basis.element(pyxb.namespace.ExpandedName(Namespace, u'ActivationPin'), ActivationPinType, scope=PrincipalAuthenticationMechanismType, documentation=u'\n        This element indicates that a Pin (Personal\n        Identification Number) has been used to authenticate the Principal to\n        some local system in order to activate a key.\n      '))

PrincipalAuthenticationMechanismType._AddElement(pyxb.binding.basis.element(pyxb.namespace.ExpandedName(Namespace, u'RestrictedPassword'), RestrictedPasswordType, scope=PrincipalAuthenticationMechanismType))
PrincipalAuthenticationMechanismType._GroupModel = pyxb.binding.content.GroupSequence(
    pyxb.binding.content.ParticleModel(PrincipalAuthenticationMechanismType._UseForTag(pyxb.namespace.ExpandedName(Namespace, u'Password')), min_occurs=0L, max_occurs=1),
    pyxb.binding.content.ParticleModel(PrincipalAuthenticationMechanismType._UseForTag(pyxb.namespace.ExpandedName(Namespace, u'RestrictedPassword')), min_occurs=0L, max_occurs=1),
    pyxb.binding.content.ParticleModel(PrincipalAuthenticationMechanismType._UseForTag(pyxb.namespace.ExpandedName(Namespace, u'Token')), min_occurs=0L, max_occurs=1),
    pyxb.binding.content.ParticleModel(PrincipalAuthenticationMechanismType._UseForTag(pyxb.namespace.ExpandedName(Namespace, u'Smartcard')), min_occurs=0L, max_occurs=1),
    pyxb.binding.content.ParticleModel(PrincipalAuthenticationMechanismType._UseForTag(pyxb.namespace.ExpandedName(Namespace, u'ActivationPin')), min_occurs=0L, max_occurs=1),
    pyxb.binding.content.ParticleModel(PrincipalAuthenticationMechanismType._UseForTag(pyxb.namespace.ExpandedName(Namespace, u'Extension')), min_occurs=0L, max_occurs=None)
    )
PrincipalAuthenticationMechanismType._ContentModel = pyxb.binding.content.ParticleModel(PrincipalAuthenticationMechanismType._GroupModel, min_occurs=1, max_occurs=1)



AuthenticatorBaseType._AddElement(pyxb.binding.basis.element(pyxb.namespace.ExpandedName(Namespace, u'RestrictedPassword'), RestrictedPasswordType, scope=AuthenticatorBaseType))
AuthenticatorBaseType._GroupModel = pyxb.binding.content.GroupSequence(
    pyxb.binding.content.ParticleModel(AuthenticatorBaseType._UseForTag(pyxb.namespace.ExpandedName(Namespace, u'RestrictedPassword')), min_occurs=1, max_occurs=1)
    )
AuthenticatorBaseType._ContentModel = pyxb.binding.content.ParticleModel(AuthenticatorBaseType._GroupModel, min_occurs=1, max_occurs=1)



AuthnMethodBaseType._AddElement(pyxb.binding.basis.element(pyxb.namespace.ExpandedName(Namespace, u'Authenticator'), AuthenticatorBaseType, scope=AuthnMethodBaseType, documentation=u"\n        The method applied to validate a principal's\n        authentication across a network\n      "))

AuthnMethodBaseType._AddElement(pyxb.binding.basis.element(pyxb.namespace.ExpandedName(Namespace, u'PrincipalAuthenticationMechanism'), PrincipalAuthenticationMechanismType, scope=AuthnMethodBaseType, documentation=u'\n        The method that a Principal employs to perform\n        authentication to local system components.\n      '))

AuthnMethodBaseType._AddElement(pyxb.binding.basis.element(pyxb.namespace.ExpandedName(Namespace, u'Extension'), ExtensionType, scope=AuthnMethodBaseType))

AuthnMethodBaseType._AddElement(pyxb.binding.basis.element(pyxb.namespace.ExpandedName(Namespace, u'AuthenticatorTransportProtocol'), AuthenticatorTransportProtocolType, scope=AuthnMethodBaseType, documentation=u'\n        The protocol across which Authenticator information is\n        transferred to an Authentication Authority verifier.\n      '))
AuthnMethodBaseType._GroupModel = pyxb.binding.content.GroupSequence(
    pyxb.binding.content.ParticleModel(AuthnMethodBaseType._UseForTag(pyxb.namespace.ExpandedName(Namespace, u'PrincipalAuthenticationMechanism')), min_occurs=0L, max_occurs=1),
    pyxb.binding.content.ParticleModel(AuthnMethodBaseType._UseForTag(pyxb.namespace.ExpandedName(Namespace, u'Authenticator')), min_occurs=1, max_occurs=1),
    pyxb.binding.content.ParticleModel(AuthnMethodBaseType._UseForTag(pyxb.namespace.ExpandedName(Namespace, u'AuthenticatorTransportProtocol')), min_occurs=1, max_occurs=1),
    pyxb.binding.content.ParticleModel(AuthnMethodBaseType._UseForTag(pyxb.namespace.ExpandedName(Namespace, u'Extension')), min_occurs=0L, max_occurs=None)
    )
AuthnMethodBaseType._ContentModel = pyxb.binding.content.ParticleModel(AuthnMethodBaseType._GroupModel, min_occurs=1, max_occurs=1)
