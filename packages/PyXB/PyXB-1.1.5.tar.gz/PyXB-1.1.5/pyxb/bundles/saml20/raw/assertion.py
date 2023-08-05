# ./pyxb/bundles/saml20/raw/assertion.py
# -*- coding: utf-8 -*-
# PyXB bindings for NM:c67eab1e6d7826a8e79aaf9536d1cb355237afad
# Generated 2012-11-01 15:13:39.801230 by PyXB version 1.1.5
# Namespace urn:oasis:names:tc:SAML:2.0:assertion

import pyxb
import pyxb.binding
import pyxb.binding.saxer
import StringIO
import pyxb.utils.utility
import pyxb.utils.domutils
import sys

# Unique identifier for bindings created at the same time
_GenerationUID = pyxb.utils.utility.UniqueIdentifier('urn:uuid:a02d8576-2460-11e2-a26e-c8600024e903')

# Import bindings for namespaces imported into schema
import pyxb.binding.datatypes
import pyxb.bundles.wssplat.xenc
import pyxb.bundles.wssplat.ds

Namespace = pyxb.namespace.NamespaceForURI(u'urn:oasis:names:tc:SAML:2.0:assertion', create_if_missing=True)
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


# Atomic simple type: {urn:oasis:names:tc:SAML:2.0:assertion}DecisionType
class DecisionType (pyxb.binding.datatypes.string, pyxb.binding.basis.enumeration_mixin):

    """An atomic simple type."""

    _ExpandedName = pyxb.namespace.ExpandedName(Namespace, u'DecisionType')
    _DefinitionLocation = pyxb.utils.utility.Location('/tmp/pyxbdist.RHB65sy/PyXB-1.1.5/pyxb/bundles/saml20/schemas/assertion.xsd', 236, 4)
    _Documentation = None
DecisionType._CF_enumeration = pyxb.binding.facets.CF_enumeration(value_datatype=DecisionType, enum_prefix=None)
DecisionType.Permit = DecisionType._CF_enumeration.addEnumeration(unicode_value=u'Permit', tag=u'Permit')
DecisionType.Deny = DecisionType._CF_enumeration.addEnumeration(unicode_value=u'Deny', tag=u'Deny')
DecisionType.Indeterminate = DecisionType._CF_enumeration.addEnumeration(unicode_value=u'Indeterminate', tag=u'Indeterminate')
DecisionType._InitializeFacetMap(DecisionType._CF_enumeration)
Namespace.addCategoryObject('typeBinding', u'DecisionType', DecisionType)

# Complex type {urn:oasis:names:tc:SAML:2.0:assertion}ConditionAbstractType with content type EMPTY
class ConditionAbstractType (pyxb.binding.basis.complexTypeDefinition):
    _TypeDefinition = None
    _ContentTypeTag = pyxb.binding.basis.complexTypeDefinition._CT_EMPTY
    _Abstract = True
    _ExpandedName = pyxb.namespace.ExpandedName(Namespace, u'ConditionAbstractType')
    _DefinitionLocation = pyxb.utils.utility.Location('/tmp/pyxbdist.RHB65sy/PyXB-1.1.5/pyxb/bundles/saml20/schemas/assertion.xsd', 139, 4)
    # Base type is pyxb.binding.datatypes.anyType

    _ElementMap = {
        
    }
    _AttributeMap = {
        
    }
Namespace.addCategoryObject('typeBinding', u'ConditionAbstractType', ConditionAbstractType)


# Complex type {urn:oasis:names:tc:SAML:2.0:assertion}AudienceRestrictionType with content type ELEMENT_ONLY
class AudienceRestrictionType (ConditionAbstractType):
    _TypeDefinition = None
    _ContentTypeTag = pyxb.binding.basis.complexTypeDefinition._CT_ELEMENT_ONLY
    _Abstract = False
    _ExpandedName = pyxb.namespace.ExpandedName(Namespace, u'AudienceRestrictionType')
    _DefinitionLocation = pyxb.utils.utility.Location('/tmp/pyxbdist.RHB65sy/PyXB-1.1.5/pyxb/bundles/saml20/schemas/assertion.xsd', 141, 4)
    # Base type is ConditionAbstractType
    
    # Element {urn:oasis:names:tc:SAML:2.0:assertion}Audience uses Python identifier Audience
    __Audience = pyxb.binding.content.ElementUse(pyxb.namespace.ExpandedName(Namespace, u'Audience'), 'Audience', '__urnoasisnamestcSAML2_0assertion_AudienceRestrictionType_urnoasisnamestcSAML2_0assertionAudience', True)
    __Audience._DeclarationLocation = pyxb.utils.utility.Location('/tmp/pyxbdist.RHB65sy/PyXB-1.1.5/pyxb/bundles/saml20/schemas/assertion.xsd', 150, 4)
    __Audience._UseLocation = pyxb.utils.utility.Location('/tmp/pyxbdist.RHB65sy/PyXB-1.1.5/pyxb/bundles/saml20/schemas/assertion.xsd', 144, 16)

    
    Audience = property(__Audience.value, __Audience.set, None, None)


    _ElementMap = ConditionAbstractType._ElementMap.copy()
    _ElementMap.update({
        __Audience.name() : __Audience
    })
    _AttributeMap = ConditionAbstractType._AttributeMap.copy()
    _AttributeMap.update({
        
    })
Namespace.addCategoryObject('typeBinding', u'AudienceRestrictionType', AudienceRestrictionType)


# Complex type {urn:oasis:names:tc:SAML:2.0:assertion}NameIDType with content type SIMPLE
class NameIDType (pyxb.binding.basis.complexTypeDefinition):
    _TypeDefinition = pyxb.binding.datatypes.string
    _ContentTypeTag = pyxb.binding.basis.complexTypeDefinition._CT_SIMPLE
    _Abstract = False
    _ExpandedName = pyxb.namespace.ExpandedName(Namespace, u'NameIDType')
    _DefinitionLocation = pyxb.utils.utility.Location('/tmp/pyxbdist.RHB65sy/PyXB-1.1.5/pyxb/bundles/saml20/schemas/assertion.xsd', 38, 4)
    # Base type is pyxb.binding.datatypes.string
    
    # Attribute SPProvidedID uses Python identifier SPProvidedID
    __SPProvidedID = pyxb.binding.content.AttributeUse(pyxb.namespace.ExpandedName(None, u'SPProvidedID'), 'SPProvidedID', '__urnoasisnamestcSAML2_0assertion_NameIDType_SPProvidedID', pyxb.binding.datatypes.string)
    __SPProvidedID._DeclarationLocation = pyxb.utils.utility.Location('/tmp/pyxbdist.RHB65sy/PyXB-1.1.5/pyxb/bundles/saml20/schemas/assertion.xsd', 43, 16)
    __SPProvidedID._UseLocation = pyxb.utils.utility.Location('/tmp/pyxbdist.RHB65sy/PyXB-1.1.5/pyxb/bundles/saml20/schemas/assertion.xsd', 43, 16)
    
    SPProvidedID = property(__SPProvidedID.value, __SPProvidedID.set, None, None)

    
    # Attribute Format uses Python identifier Format
    __Format = pyxb.binding.content.AttributeUse(pyxb.namespace.ExpandedName(None, u'Format'), 'Format', '__urnoasisnamestcSAML2_0assertion_NameIDType_Format', pyxb.binding.datatypes.anyURI)
    __Format._DeclarationLocation = pyxb.utils.utility.Location('/tmp/pyxbdist.RHB65sy/PyXB-1.1.5/pyxb/bundles/saml20/schemas/assertion.xsd', 42, 16)
    __Format._UseLocation = pyxb.utils.utility.Location('/tmp/pyxbdist.RHB65sy/PyXB-1.1.5/pyxb/bundles/saml20/schemas/assertion.xsd', 42, 16)
    
    Format = property(__Format.value, __Format.set, None, None)

    
    # Attribute SPNameQualifier uses Python identifier SPNameQualifier
    __SPNameQualifier = pyxb.binding.content.AttributeUse(pyxb.namespace.ExpandedName(None, u'SPNameQualifier'), 'SPNameQualifier', '__urnoasisnamestcSAML2_0assertion_NameIDType_SPNameQualifier', pyxb.binding.datatypes.string)
    __SPNameQualifier._DeclarationLocation = pyxb.utils.utility.Location('/tmp/pyxbdist.RHB65sy/PyXB-1.1.5/pyxb/bundles/saml20/schemas/assertion.xsd', 31, 8)
    __SPNameQualifier._UseLocation = pyxb.utils.utility.Location('/tmp/pyxbdist.RHB65sy/PyXB-1.1.5/pyxb/bundles/saml20/schemas/assertion.xsd', 31, 8)
    
    SPNameQualifier = property(__SPNameQualifier.value, __SPNameQualifier.set, None, None)

    
    # Attribute NameQualifier uses Python identifier NameQualifier
    __NameQualifier = pyxb.binding.content.AttributeUse(pyxb.namespace.ExpandedName(None, u'NameQualifier'), 'NameQualifier', '__urnoasisnamestcSAML2_0assertion_NameIDType_NameQualifier', pyxb.binding.datatypes.string)
    __NameQualifier._DeclarationLocation = pyxb.utils.utility.Location('/tmp/pyxbdist.RHB65sy/PyXB-1.1.5/pyxb/bundles/saml20/schemas/assertion.xsd', 30, 8)
    __NameQualifier._UseLocation = pyxb.utils.utility.Location('/tmp/pyxbdist.RHB65sy/PyXB-1.1.5/pyxb/bundles/saml20/schemas/assertion.xsd', 30, 8)
    
    NameQualifier = property(__NameQualifier.value, __NameQualifier.set, None, None)


    _ElementMap = {
        
    }
    _AttributeMap = {
        __SPProvidedID.name() : __SPProvidedID,
        __Format.name() : __Format,
        __SPNameQualifier.name() : __SPNameQualifier,
        __NameQualifier.name() : __NameQualifier
    }
Namespace.addCategoryObject('typeBinding', u'NameIDType', NameIDType)


# Complex type {urn:oasis:names:tc:SAML:2.0:assertion}EncryptedElementType with content type ELEMENT_ONLY
class EncryptedElementType (pyxb.binding.basis.complexTypeDefinition):
    _TypeDefinition = None
    _ContentTypeTag = pyxb.binding.basis.complexTypeDefinition._CT_ELEMENT_ONLY
    _Abstract = False
    _ExpandedName = pyxb.namespace.ExpandedName(Namespace, u'EncryptedElementType')
    _DefinitionLocation = pyxb.utils.utility.Location('/tmp/pyxbdist.RHB65sy/PyXB-1.1.5/pyxb/bundles/saml20/schemas/assertion.xsd', 47, 4)
    # Base type is pyxb.binding.datatypes.anyType
    
    # Element {http://www.w3.org/2001/04/xmlenc#}EncryptedData uses Python identifier EncryptedData
    __EncryptedData = pyxb.binding.content.ElementUse(pyxb.namespace.ExpandedName(pyxb.namespace.NamespaceForURI(u'http://www.w3.org/2001/04/xmlenc#'), u'EncryptedData'), 'EncryptedData', '__urnoasisnamestcSAML2_0assertion_EncryptedElementType_httpwww_w3_org200104xmlencEncryptedData', False)
    __EncryptedData._DeclarationLocation = pyxb.utils.utility.Location('/tmp/pyxbdist.RHB65sy/PyXB-1.1.5/pyxb/bundles/wssplat/schemas/xenc.xsd', 72, 2)
    __EncryptedData._UseLocation = pyxb.utils.utility.Location('/tmp/pyxbdist.RHB65sy/PyXB-1.1.5/pyxb/bundles/saml20/schemas/assertion.xsd', 48, 8)

    
    EncryptedData = property(__EncryptedData.value, __EncryptedData.set, None, None)

    
    # Element {http://www.w3.org/2001/04/xmlenc#}EncryptedKey uses Python identifier EncryptedKey
    __EncryptedKey = pyxb.binding.content.ElementUse(pyxb.namespace.ExpandedName(pyxb.namespace.NamespaceForURI(u'http://www.w3.org/2001/04/xmlenc#'), u'EncryptedKey'), 'EncryptedKey', '__urnoasisnamestcSAML2_0assertion_EncryptedElementType_httpwww_w3_org200104xmlencEncryptedKey', True)
    __EncryptedKey._DeclarationLocation = pyxb.utils.utility.Location('/tmp/pyxbdist.RHB65sy/PyXB-1.1.5/pyxb/bundles/wssplat/schemas/xenc.xsd', 82, 2)
    __EncryptedKey._UseLocation = pyxb.utils.utility.Location('/tmp/pyxbdist.RHB65sy/PyXB-1.1.5/pyxb/bundles/saml20/schemas/assertion.xsd', 48, 8)

    
    EncryptedKey = property(__EncryptedKey.value, __EncryptedKey.set, None, None)


    _ElementMap = {
        __EncryptedData.name() : __EncryptedData,
        __EncryptedKey.name() : __EncryptedKey
    }
    _AttributeMap = {
        
    }
Namespace.addCategoryObject('typeBinding', u'EncryptedElementType', EncryptedElementType)


# Complex type {urn:oasis:names:tc:SAML:2.0:assertion}StatementAbstractType with content type EMPTY
class StatementAbstractType (pyxb.binding.basis.complexTypeDefinition):
    _TypeDefinition = None
    _ContentTypeTag = pyxb.binding.basis.complexTypeDefinition._CT_EMPTY
    _Abstract = True
    _ExpandedName = pyxb.namespace.ExpandedName(Namespace, u'StatementAbstractType')
    _DefinitionLocation = pyxb.utils.utility.Location('/tmp/pyxbdist.RHB65sy/PyXB-1.1.5/pyxb/bundles/saml20/schemas/assertion.xsd', 180, 4)
    # Base type is pyxb.binding.datatypes.anyType

    _ElementMap = {
        
    }
    _AttributeMap = {
        
    }
Namespace.addCategoryObject('typeBinding', u'StatementAbstractType', StatementAbstractType)


# Complex type {urn:oasis:names:tc:SAML:2.0:assertion}AuthnContextType with content type ELEMENT_ONLY
class AuthnContextType (pyxb.binding.basis.complexTypeDefinition):
    _TypeDefinition = None
    _ContentTypeTag = pyxb.binding.basis.complexTypeDefinition._CT_ELEMENT_ONLY
    _Abstract = False
    _ExpandedName = pyxb.namespace.ExpandedName(Namespace, u'AuthnContextType')
    _DefinitionLocation = pyxb.utils.utility.Location('/tmp/pyxbdist.RHB65sy/PyXB-1.1.5/pyxb/bundles/saml20/schemas/assertion.xsd', 201, 4)
    # Base type is pyxb.binding.datatypes.anyType
    
    # Element {urn:oasis:names:tc:SAML:2.0:assertion}AuthnContextDeclRef uses Python identifier AuthnContextDeclRef
    __AuthnContextDeclRef = pyxb.binding.content.ElementUse(pyxb.namespace.ExpandedName(Namespace, u'AuthnContextDeclRef'), 'AuthnContextDeclRef', '__urnoasisnamestcSAML2_0assertion_AuthnContextType_urnoasisnamestcSAML2_0assertionAuthnContextDeclRef', False)
    __AuthnContextDeclRef._DeclarationLocation = pyxb.utils.utility.Location('/tmp/pyxbdist.RHB65sy/PyXB-1.1.5/pyxb/bundles/saml20/schemas/assertion.xsd', 220, 4)
    __AuthnContextDeclRef._UseLocation = pyxb.utils.utility.Location('/tmp/pyxbdist.RHB65sy/PyXB-1.1.5/pyxb/bundles/saml20/schemas/assertion.xsd', 202, 8)

    
    AuthnContextDeclRef = property(__AuthnContextDeclRef.value, __AuthnContextDeclRef.set, None, None)

    
    # Element {urn:oasis:names:tc:SAML:2.0:assertion}AuthenticatingAuthority uses Python identifier AuthenticatingAuthority
    __AuthenticatingAuthority = pyxb.binding.content.ElementUse(pyxb.namespace.ExpandedName(Namespace, u'AuthenticatingAuthority'), 'AuthenticatingAuthority', '__urnoasisnamestcSAML2_0assertion_AuthnContextType_urnoasisnamestcSAML2_0assertionAuthenticatingAuthority', True)
    __AuthenticatingAuthority._DeclarationLocation = pyxb.utils.utility.Location('/tmp/pyxbdist.RHB65sy/PyXB-1.1.5/pyxb/bundles/saml20/schemas/assertion.xsd', 222, 4)
    __AuthenticatingAuthority._UseLocation = pyxb.utils.utility.Location('/tmp/pyxbdist.RHB65sy/PyXB-1.1.5/pyxb/bundles/saml20/schemas/assertion.xsd', 202, 8)

    
    AuthenticatingAuthority = property(__AuthenticatingAuthority.value, __AuthenticatingAuthority.set, None, None)

    
    # Element {urn:oasis:names:tc:SAML:2.0:assertion}AuthnContextDecl uses Python identifier AuthnContextDecl
    __AuthnContextDecl = pyxb.binding.content.ElementUse(pyxb.namespace.ExpandedName(Namespace, u'AuthnContextDecl'), 'AuthnContextDecl', '__urnoasisnamestcSAML2_0assertion_AuthnContextType_urnoasisnamestcSAML2_0assertionAuthnContextDecl', False)
    __AuthnContextDecl._DeclarationLocation = pyxb.utils.utility.Location('/tmp/pyxbdist.RHB65sy/PyXB-1.1.5/pyxb/bundles/saml20/schemas/assertion.xsd', 221, 4)
    __AuthnContextDecl._UseLocation = pyxb.utils.utility.Location('/tmp/pyxbdist.RHB65sy/PyXB-1.1.5/pyxb/bundles/saml20/schemas/assertion.xsd', 202, 8)

    
    AuthnContextDecl = property(__AuthnContextDecl.value, __AuthnContextDecl.set, None, None)

    
    # Element {urn:oasis:names:tc:SAML:2.0:assertion}AuthnContextClassRef uses Python identifier AuthnContextClassRef
    __AuthnContextClassRef = pyxb.binding.content.ElementUse(pyxb.namespace.ExpandedName(Namespace, u'AuthnContextClassRef'), 'AuthnContextClassRef', '__urnoasisnamestcSAML2_0assertion_AuthnContextType_urnoasisnamestcSAML2_0assertionAuthnContextClassRef', False)
    __AuthnContextClassRef._DeclarationLocation = pyxb.utils.utility.Location('/tmp/pyxbdist.RHB65sy/PyXB-1.1.5/pyxb/bundles/saml20/schemas/assertion.xsd', 219, 4)
    __AuthnContextClassRef._UseLocation = pyxb.utils.utility.Location('/tmp/pyxbdist.RHB65sy/PyXB-1.1.5/pyxb/bundles/saml20/schemas/assertion.xsd', 202, 8)

    
    AuthnContextClassRef = property(__AuthnContextClassRef.value, __AuthnContextClassRef.set, None, None)


    _ElementMap = {
        __AuthnContextDeclRef.name() : __AuthnContextDeclRef,
        __AuthenticatingAuthority.name() : __AuthenticatingAuthority,
        __AuthnContextDecl.name() : __AuthnContextDecl,
        __AuthnContextClassRef.name() : __AuthnContextClassRef
    }
    _AttributeMap = {
        
    }
Namespace.addCategoryObject('typeBinding', u'AuthnContextType', AuthnContextType)


# Complex type {urn:oasis:names:tc:SAML:2.0:assertion}AttributeType with content type ELEMENT_ONLY
class AttributeType (pyxb.binding.basis.complexTypeDefinition):
    _TypeDefinition = None
    _ContentTypeTag = pyxb.binding.basis.complexTypeDefinition._CT_ELEMENT_ONLY
    _Abstract = False
    _ExpandedName = pyxb.namespace.ExpandedName(Namespace, u'AttributeType')
    _DefinitionLocation = pyxb.utils.utility.Location('/tmp/pyxbdist.RHB65sy/PyXB-1.1.5/pyxb/bundles/saml20/schemas/assertion.xsd', 272, 4)
    # Base type is pyxb.binding.datatypes.anyType
    
    # Element {urn:oasis:names:tc:SAML:2.0:assertion}AttributeValue uses Python identifier AttributeValue
    __AttributeValue = pyxb.binding.content.ElementUse(pyxb.namespace.ExpandedName(Namespace, u'AttributeValue'), 'AttributeValue', '__urnoasisnamestcSAML2_0assertion_AttributeType_urnoasisnamestcSAML2_0assertionAttributeValue', True)
    __AttributeValue._DeclarationLocation = pyxb.utils.utility.Location('/tmp/pyxbdist.RHB65sy/PyXB-1.1.5/pyxb/bundles/saml20/schemas/assertion.xsd', 281, 4)
    __AttributeValue._UseLocation = pyxb.utils.utility.Location('/tmp/pyxbdist.RHB65sy/PyXB-1.1.5/pyxb/bundles/saml20/schemas/assertion.xsd', 273, 8)

    
    AttributeValue = property(__AttributeValue.value, __AttributeValue.set, None, None)

    
    # Attribute NameFormat uses Python identifier NameFormat
    __NameFormat = pyxb.binding.content.AttributeUse(pyxb.namespace.ExpandedName(None, u'NameFormat'), 'NameFormat', '__urnoasisnamestcSAML2_0assertion_AttributeType_NameFormat', pyxb.binding.datatypes.anyURI)
    __NameFormat._DeclarationLocation = pyxb.utils.utility.Location('/tmp/pyxbdist.RHB65sy/PyXB-1.1.5/pyxb/bundles/saml20/schemas/assertion.xsd', 277, 8)
    __NameFormat._UseLocation = pyxb.utils.utility.Location('/tmp/pyxbdist.RHB65sy/PyXB-1.1.5/pyxb/bundles/saml20/schemas/assertion.xsd', 277, 8)
    
    NameFormat = property(__NameFormat.value, __NameFormat.set, None, None)

    
    # Attribute FriendlyName uses Python identifier FriendlyName
    __FriendlyName = pyxb.binding.content.AttributeUse(pyxb.namespace.ExpandedName(None, u'FriendlyName'), 'FriendlyName', '__urnoasisnamestcSAML2_0assertion_AttributeType_FriendlyName', pyxb.binding.datatypes.string)
    __FriendlyName._DeclarationLocation = pyxb.utils.utility.Location('/tmp/pyxbdist.RHB65sy/PyXB-1.1.5/pyxb/bundles/saml20/schemas/assertion.xsd', 278, 8)
    __FriendlyName._UseLocation = pyxb.utils.utility.Location('/tmp/pyxbdist.RHB65sy/PyXB-1.1.5/pyxb/bundles/saml20/schemas/assertion.xsd', 278, 8)
    
    FriendlyName = property(__FriendlyName.value, __FriendlyName.set, None, None)

    
    # Attribute Name uses Python identifier Name
    __Name = pyxb.binding.content.AttributeUse(pyxb.namespace.ExpandedName(None, u'Name'), 'Name', '__urnoasisnamestcSAML2_0assertion_AttributeType_Name', pyxb.binding.datatypes.string, required=True)
    __Name._DeclarationLocation = pyxb.utils.utility.Location('/tmp/pyxbdist.RHB65sy/PyXB-1.1.5/pyxb/bundles/saml20/schemas/assertion.xsd', 276, 8)
    __Name._UseLocation = pyxb.utils.utility.Location('/tmp/pyxbdist.RHB65sy/PyXB-1.1.5/pyxb/bundles/saml20/schemas/assertion.xsd', 276, 8)
    
    Name = property(__Name.value, __Name.set, None, None)

    _AttributeWildcard = pyxb.binding.content.Wildcard(process_contents=pyxb.binding.content.Wildcard.PC_lax, namespace_constraint=(pyxb.binding.content.Wildcard.NC_not, u'urn:oasis:names:tc:SAML:2.0:assertion'))

    _ElementMap = {
        __AttributeValue.name() : __AttributeValue
    }
    _AttributeMap = {
        __NameFormat.name() : __NameFormat,
        __FriendlyName.name() : __FriendlyName,
        __Name.name() : __Name
    }
Namespace.addCategoryObject('typeBinding', u'AttributeType', AttributeType)


# Complex type {urn:oasis:names:tc:SAML:2.0:assertion}EvidenceType with content type ELEMENT_ONLY
class EvidenceType (pyxb.binding.basis.complexTypeDefinition):
    _TypeDefinition = None
    _ContentTypeTag = pyxb.binding.basis.complexTypeDefinition._CT_ELEMENT_ONLY
    _Abstract = False
    _ExpandedName = pyxb.namespace.ExpandedName(Namespace, u'EvidenceType')
    _DefinitionLocation = pyxb.utils.utility.Location('/tmp/pyxbdist.RHB65sy/PyXB-1.1.5/pyxb/bundles/saml20/schemas/assertion.xsd', 252, 4)
    # Base type is pyxb.binding.datatypes.anyType
    
    # Element {urn:oasis:names:tc:SAML:2.0:assertion}Assertion uses Python identifier Assertion
    __Assertion = pyxb.binding.content.ElementUse(pyxb.namespace.ExpandedName(Namespace, u'Assertion'), 'Assertion', '__urnoasisnamestcSAML2_0assertion_EvidenceType_urnoasisnamestcSAML2_0assertionAssertion', True)
    __Assertion._DeclarationLocation = pyxb.utils.utility.Location('/tmp/pyxbdist.RHB65sy/PyXB-1.1.5/pyxb/bundles/saml20/schemas/assertion.xsd', 57, 4)
    __Assertion._UseLocation = pyxb.utils.utility.Location('/tmp/pyxbdist.RHB65sy/PyXB-1.1.5/pyxb/bundles/saml20/schemas/assertion.xsd', 253, 8)

    
    Assertion = property(__Assertion.value, __Assertion.set, None, None)

    
    # Element {urn:oasis:names:tc:SAML:2.0:assertion}AssertionURIRef uses Python identifier AssertionURIRef
    __AssertionURIRef = pyxb.binding.content.ElementUse(pyxb.namespace.ExpandedName(Namespace, u'AssertionURIRef'), 'AssertionURIRef', '__urnoasisnamestcSAML2_0assertion_EvidenceType_urnoasisnamestcSAML2_0assertionAssertionURIRef', True)
    __AssertionURIRef._DeclarationLocation = pyxb.utils.utility.Location('/tmp/pyxbdist.RHB65sy/PyXB-1.1.5/pyxb/bundles/saml20/schemas/assertion.xsd', 56, 4)
    __AssertionURIRef._UseLocation = pyxb.utils.utility.Location('/tmp/pyxbdist.RHB65sy/PyXB-1.1.5/pyxb/bundles/saml20/schemas/assertion.xsd', 253, 8)

    
    AssertionURIRef = property(__AssertionURIRef.value, __AssertionURIRef.set, None, None)

    
    # Element {urn:oasis:names:tc:SAML:2.0:assertion}EncryptedAssertion uses Python identifier EncryptedAssertion
    __EncryptedAssertion = pyxb.binding.content.ElementUse(pyxb.namespace.ExpandedName(Namespace, u'EncryptedAssertion'), 'EncryptedAssertion', '__urnoasisnamestcSAML2_0assertion_EvidenceType_urnoasisnamestcSAML2_0assertionEncryptedAssertion', True)
    __EncryptedAssertion._DeclarationLocation = pyxb.utils.utility.Location('/tmp/pyxbdist.RHB65sy/PyXB-1.1.5/pyxb/bundles/saml20/schemas/assertion.xsd', 178, 4)
    __EncryptedAssertion._UseLocation = pyxb.utils.utility.Location('/tmp/pyxbdist.RHB65sy/PyXB-1.1.5/pyxb/bundles/saml20/schemas/assertion.xsd', 253, 8)

    
    EncryptedAssertion = property(__EncryptedAssertion.value, __EncryptedAssertion.set, None, None)

    
    # Element {urn:oasis:names:tc:SAML:2.0:assertion}AssertionIDRef uses Python identifier AssertionIDRef
    __AssertionIDRef = pyxb.binding.content.ElementUse(pyxb.namespace.ExpandedName(Namespace, u'AssertionIDRef'), 'AssertionIDRef', '__urnoasisnamestcSAML2_0assertion_EvidenceType_urnoasisnamestcSAML2_0assertionAssertionIDRef', True)
    __AssertionIDRef._DeclarationLocation = pyxb.utils.utility.Location('/tmp/pyxbdist.RHB65sy/PyXB-1.1.5/pyxb/bundles/saml20/schemas/assertion.xsd', 55, 4)
    __AssertionIDRef._UseLocation = pyxb.utils.utility.Location('/tmp/pyxbdist.RHB65sy/PyXB-1.1.5/pyxb/bundles/saml20/schemas/assertion.xsd', 253, 8)

    
    AssertionIDRef = property(__AssertionIDRef.value, __AssertionIDRef.set, None, None)


    _ElementMap = {
        __Assertion.name() : __Assertion,
        __AssertionURIRef.name() : __AssertionURIRef,
        __EncryptedAssertion.name() : __EncryptedAssertion,
        __AssertionIDRef.name() : __AssertionIDRef
    }
    _AttributeMap = {
        
    }
Namespace.addCategoryObject('typeBinding', u'EvidenceType', EvidenceType)


# Complex type {urn:oasis:names:tc:SAML:2.0:assertion}AuthnStatementType with content type ELEMENT_ONLY
class AuthnStatementType (StatementAbstractType):
    _TypeDefinition = None
    _ContentTypeTag = pyxb.binding.basis.complexTypeDefinition._CT_ELEMENT_ONLY
    _Abstract = False
    _ExpandedName = pyxb.namespace.ExpandedName(Namespace, u'AuthnStatementType')
    _DefinitionLocation = pyxb.utils.utility.Location('/tmp/pyxbdist.RHB65sy/PyXB-1.1.5/pyxb/bundles/saml20/schemas/assertion.xsd', 182, 4)
    # Base type is StatementAbstractType
    
    # Element {urn:oasis:names:tc:SAML:2.0:assertion}AuthnContext uses Python identifier AuthnContext
    __AuthnContext = pyxb.binding.content.ElementUse(pyxb.namespace.ExpandedName(Namespace, u'AuthnContext'), 'AuthnContext', '__urnoasisnamestcSAML2_0assertion_AuthnStatementType_urnoasisnamestcSAML2_0assertionAuthnContext', False)
    __AuthnContext._DeclarationLocation = pyxb.utils.utility.Location('/tmp/pyxbdist.RHB65sy/PyXB-1.1.5/pyxb/bundles/saml20/schemas/assertion.xsd', 200, 4)
    __AuthnContext._UseLocation = pyxb.utils.utility.Location('/tmp/pyxbdist.RHB65sy/PyXB-1.1.5/pyxb/bundles/saml20/schemas/assertion.xsd', 185, 16)

    
    AuthnContext = property(__AuthnContext.value, __AuthnContext.set, None, None)

    
    # Element {urn:oasis:names:tc:SAML:2.0:assertion}SubjectLocality uses Python identifier SubjectLocality
    __SubjectLocality = pyxb.binding.content.ElementUse(pyxb.namespace.ExpandedName(Namespace, u'SubjectLocality'), 'SubjectLocality', '__urnoasisnamestcSAML2_0assertion_AuthnStatementType_urnoasisnamestcSAML2_0assertionSubjectLocality', False)
    __SubjectLocality._DeclarationLocation = pyxb.utils.utility.Location('/tmp/pyxbdist.RHB65sy/PyXB-1.1.5/pyxb/bundles/saml20/schemas/assertion.xsd', 195, 4)
    __SubjectLocality._UseLocation = pyxb.utils.utility.Location('/tmp/pyxbdist.RHB65sy/PyXB-1.1.5/pyxb/bundles/saml20/schemas/assertion.xsd', 185, 16)

    
    SubjectLocality = property(__SubjectLocality.value, __SubjectLocality.set, None, None)

    
    # Attribute SessionNotOnOrAfter uses Python identifier SessionNotOnOrAfter
    __SessionNotOnOrAfter = pyxb.binding.content.AttributeUse(pyxb.namespace.ExpandedName(None, u'SessionNotOnOrAfter'), 'SessionNotOnOrAfter', '__urnoasisnamestcSAML2_0assertion_AuthnStatementType_SessionNotOnOrAfter', pyxb.binding.datatypes.dateTime)
    __SessionNotOnOrAfter._DeclarationLocation = pyxb.utils.utility.Location('/tmp/pyxbdist.RHB65sy/PyXB-1.1.5/pyxb/bundles/saml20/schemas/assertion.xsd', 191, 16)
    __SessionNotOnOrAfter._UseLocation = pyxb.utils.utility.Location('/tmp/pyxbdist.RHB65sy/PyXB-1.1.5/pyxb/bundles/saml20/schemas/assertion.xsd', 191, 16)
    
    SessionNotOnOrAfter = property(__SessionNotOnOrAfter.value, __SessionNotOnOrAfter.set, None, None)

    
    # Attribute AuthnInstant uses Python identifier AuthnInstant
    __AuthnInstant = pyxb.binding.content.AttributeUse(pyxb.namespace.ExpandedName(None, u'AuthnInstant'), 'AuthnInstant', '__urnoasisnamestcSAML2_0assertion_AuthnStatementType_AuthnInstant', pyxb.binding.datatypes.dateTime, required=True)
    __AuthnInstant._DeclarationLocation = pyxb.utils.utility.Location('/tmp/pyxbdist.RHB65sy/PyXB-1.1.5/pyxb/bundles/saml20/schemas/assertion.xsd', 189, 16)
    __AuthnInstant._UseLocation = pyxb.utils.utility.Location('/tmp/pyxbdist.RHB65sy/PyXB-1.1.5/pyxb/bundles/saml20/schemas/assertion.xsd', 189, 16)
    
    AuthnInstant = property(__AuthnInstant.value, __AuthnInstant.set, None, None)

    
    # Attribute SessionIndex uses Python identifier SessionIndex
    __SessionIndex = pyxb.binding.content.AttributeUse(pyxb.namespace.ExpandedName(None, u'SessionIndex'), 'SessionIndex', '__urnoasisnamestcSAML2_0assertion_AuthnStatementType_SessionIndex', pyxb.binding.datatypes.string)
    __SessionIndex._DeclarationLocation = pyxb.utils.utility.Location('/tmp/pyxbdist.RHB65sy/PyXB-1.1.5/pyxb/bundles/saml20/schemas/assertion.xsd', 190, 16)
    __SessionIndex._UseLocation = pyxb.utils.utility.Location('/tmp/pyxbdist.RHB65sy/PyXB-1.1.5/pyxb/bundles/saml20/schemas/assertion.xsd', 190, 16)
    
    SessionIndex = property(__SessionIndex.value, __SessionIndex.set, None, None)


    _ElementMap = StatementAbstractType._ElementMap.copy()
    _ElementMap.update({
        __AuthnContext.name() : __AuthnContext,
        __SubjectLocality.name() : __SubjectLocality
    })
    _AttributeMap = StatementAbstractType._AttributeMap.copy()
    _AttributeMap.update({
        __SessionNotOnOrAfter.name() : __SessionNotOnOrAfter,
        __AuthnInstant.name() : __AuthnInstant,
        __SessionIndex.name() : __SessionIndex
    })
Namespace.addCategoryObject('typeBinding', u'AuthnStatementType', AuthnStatementType)


# Complex type {urn:oasis:names:tc:SAML:2.0:assertion}AuthzDecisionStatementType with content type ELEMENT_ONLY
class AuthzDecisionStatementType (StatementAbstractType):
    _TypeDefinition = None
    _ContentTypeTag = pyxb.binding.basis.complexTypeDefinition._CT_ELEMENT_ONLY
    _Abstract = False
    _ExpandedName = pyxb.namespace.ExpandedName(Namespace, u'AuthzDecisionStatementType')
    _DefinitionLocation = pyxb.utils.utility.Location('/tmp/pyxbdist.RHB65sy/PyXB-1.1.5/pyxb/bundles/saml20/schemas/assertion.xsd', 224, 4)
    # Base type is StatementAbstractType
    
    # Element {urn:oasis:names:tc:SAML:2.0:assertion}Evidence uses Python identifier Evidence
    __Evidence = pyxb.binding.content.ElementUse(pyxb.namespace.ExpandedName(Namespace, u'Evidence'), 'Evidence', '__urnoasisnamestcSAML2_0assertion_AuthzDecisionStatementType_urnoasisnamestcSAML2_0assertionEvidence', False)
    __Evidence._DeclarationLocation = pyxb.utils.utility.Location('/tmp/pyxbdist.RHB65sy/PyXB-1.1.5/pyxb/bundles/saml20/schemas/assertion.xsd', 251, 4)
    __Evidence._UseLocation = pyxb.utils.utility.Location('/tmp/pyxbdist.RHB65sy/PyXB-1.1.5/pyxb/bundles/saml20/schemas/assertion.xsd', 227, 16)

    
    Evidence = property(__Evidence.value, __Evidence.set, None, None)

    
    # Element {urn:oasis:names:tc:SAML:2.0:assertion}Action uses Python identifier Action
    __Action = pyxb.binding.content.ElementUse(pyxb.namespace.ExpandedName(Namespace, u'Action'), 'Action', '__urnoasisnamestcSAML2_0assertion_AuthzDecisionStatementType_urnoasisnamestcSAML2_0assertionAction', True)
    __Action._DeclarationLocation = pyxb.utils.utility.Location('/tmp/pyxbdist.RHB65sy/PyXB-1.1.5/pyxb/bundles/saml20/schemas/assertion.xsd', 243, 4)
    __Action._UseLocation = pyxb.utils.utility.Location('/tmp/pyxbdist.RHB65sy/PyXB-1.1.5/pyxb/bundles/saml20/schemas/assertion.xsd', 227, 16)

    
    Action = property(__Action.value, __Action.set, None, None)

    
    # Attribute Decision uses Python identifier Decision
    __Decision = pyxb.binding.content.AttributeUse(pyxb.namespace.ExpandedName(None, u'Decision'), 'Decision', '__urnoasisnamestcSAML2_0assertion_AuthzDecisionStatementType_Decision', DecisionType, required=True)
    __Decision._DeclarationLocation = pyxb.utils.utility.Location('/tmp/pyxbdist.RHB65sy/PyXB-1.1.5/pyxb/bundles/saml20/schemas/assertion.xsd', 232, 16)
    __Decision._UseLocation = pyxb.utils.utility.Location('/tmp/pyxbdist.RHB65sy/PyXB-1.1.5/pyxb/bundles/saml20/schemas/assertion.xsd', 232, 16)
    
    Decision = property(__Decision.value, __Decision.set, None, None)

    
    # Attribute Resource uses Python identifier Resource
    __Resource = pyxb.binding.content.AttributeUse(pyxb.namespace.ExpandedName(None, u'Resource'), 'Resource', '__urnoasisnamestcSAML2_0assertion_AuthzDecisionStatementType_Resource', pyxb.binding.datatypes.anyURI, required=True)
    __Resource._DeclarationLocation = pyxb.utils.utility.Location('/tmp/pyxbdist.RHB65sy/PyXB-1.1.5/pyxb/bundles/saml20/schemas/assertion.xsd', 231, 16)
    __Resource._UseLocation = pyxb.utils.utility.Location('/tmp/pyxbdist.RHB65sy/PyXB-1.1.5/pyxb/bundles/saml20/schemas/assertion.xsd', 231, 16)
    
    Resource = property(__Resource.value, __Resource.set, None, None)


    _ElementMap = StatementAbstractType._ElementMap.copy()
    _ElementMap.update({
        __Evidence.name() : __Evidence,
        __Action.name() : __Action
    })
    _AttributeMap = StatementAbstractType._AttributeMap.copy()
    _AttributeMap.update({
        __Decision.name() : __Decision,
        __Resource.name() : __Resource
    })
Namespace.addCategoryObject('typeBinding', u'AuthzDecisionStatementType', AuthzDecisionStatementType)


# Complex type {urn:oasis:names:tc:SAML:2.0:assertion}SubjectType with content type ELEMENT_ONLY
class SubjectType (pyxb.binding.basis.complexTypeDefinition):
    _TypeDefinition = None
    _ContentTypeTag = pyxb.binding.basis.complexTypeDefinition._CT_ELEMENT_ONLY
    _Abstract = False
    _ExpandedName = pyxb.namespace.ExpandedName(Namespace, u'SubjectType')
    _DefinitionLocation = pyxb.utils.utility.Location('/tmp/pyxbdist.RHB65sy/PyXB-1.1.5/pyxb/bundles/saml20/schemas/assertion.xsd', 77, 4)
    # Base type is pyxb.binding.datatypes.anyType
    
    # Element {urn:oasis:names:tc:SAML:2.0:assertion}NameID uses Python identifier NameID
    __NameID = pyxb.binding.content.ElementUse(pyxb.namespace.ExpandedName(Namespace, u'NameID'), 'NameID', '__urnoasisnamestcSAML2_0assertion_SubjectType_urnoasisnamestcSAML2_0assertionNameID', False)
    __NameID._DeclarationLocation = pyxb.utils.utility.Location('/tmp/pyxbdist.RHB65sy/PyXB-1.1.5/pyxb/bundles/saml20/schemas/assertion.xsd', 37, 4)
    __NameID._UseLocation = pyxb.utils.utility.Location('/tmp/pyxbdist.RHB65sy/PyXB-1.1.5/pyxb/bundles/saml20/schemas/assertion.xsd', 78, 8)

    
    NameID = property(__NameID.value, __NameID.set, None, None)

    
    # Element {urn:oasis:names:tc:SAML:2.0:assertion}SubjectConfirmation uses Python identifier SubjectConfirmation
    __SubjectConfirmation = pyxb.binding.content.ElementUse(pyxb.namespace.ExpandedName(Namespace, u'SubjectConfirmation'), 'SubjectConfirmation', '__urnoasisnamestcSAML2_0assertion_SubjectType_urnoasisnamestcSAML2_0assertionSubjectConfirmation', True)
    __SubjectConfirmation._DeclarationLocation = pyxb.utils.utility.Location('/tmp/pyxbdist.RHB65sy/PyXB-1.1.5/pyxb/bundles/saml20/schemas/assertion.xsd', 90, 4)
    __SubjectConfirmation._UseLocation = pyxb.utils.utility.Location('/tmp/pyxbdist.RHB65sy/PyXB-1.1.5/pyxb/bundles/saml20/schemas/assertion.xsd', 78, 8)

    
    SubjectConfirmation = property(__SubjectConfirmation.value, __SubjectConfirmation.set, None, None)

    
    # Element {urn:oasis:names:tc:SAML:2.0:assertion}EncryptedID uses Python identifier EncryptedID
    __EncryptedID = pyxb.binding.content.ElementUse(pyxb.namespace.ExpandedName(Namespace, u'EncryptedID'), 'EncryptedID', '__urnoasisnamestcSAML2_0assertion_SubjectType_urnoasisnamestcSAML2_0assertionEncryptedID', False)
    __EncryptedID._DeclarationLocation = pyxb.utils.utility.Location('/tmp/pyxbdist.RHB65sy/PyXB-1.1.5/pyxb/bundles/saml20/schemas/assertion.xsd', 53, 4)
    __EncryptedID._UseLocation = pyxb.utils.utility.Location('/tmp/pyxbdist.RHB65sy/PyXB-1.1.5/pyxb/bundles/saml20/schemas/assertion.xsd', 78, 8)

    
    EncryptedID = property(__EncryptedID.value, __EncryptedID.set, None, None)

    
    # Element {urn:oasis:names:tc:SAML:2.0:assertion}BaseID uses Python identifier BaseID
    __BaseID = pyxb.binding.content.ElementUse(pyxb.namespace.ExpandedName(Namespace, u'BaseID'), 'BaseID', '__urnoasisnamestcSAML2_0assertion_SubjectType_urnoasisnamestcSAML2_0assertionBaseID', False)
    __BaseID._DeclarationLocation = pyxb.utils.utility.Location('/tmp/pyxbdist.RHB65sy/PyXB-1.1.5/pyxb/bundles/saml20/schemas/assertion.xsd', 33, 4)
    __BaseID._UseLocation = pyxb.utils.utility.Location('/tmp/pyxbdist.RHB65sy/PyXB-1.1.5/pyxb/bundles/saml20/schemas/assertion.xsd', 78, 8)

    
    BaseID = property(__BaseID.value, __BaseID.set, None, None)


    _ElementMap = {
        __NameID.name() : __NameID,
        __SubjectConfirmation.name() : __SubjectConfirmation,
        __EncryptedID.name() : __EncryptedID,
        __BaseID.name() : __BaseID
    }
    _AttributeMap = {
        
    }
Namespace.addCategoryObject('typeBinding', u'SubjectType', SubjectType)


# Complex type {urn:oasis:names:tc:SAML:2.0:assertion}SubjectConfirmationType with content type ELEMENT_ONLY
class SubjectConfirmationType (pyxb.binding.basis.complexTypeDefinition):
    _TypeDefinition = None
    _ContentTypeTag = pyxb.binding.basis.complexTypeDefinition._CT_ELEMENT_ONLY
    _Abstract = False
    _ExpandedName = pyxb.namespace.ExpandedName(Namespace, u'SubjectConfirmationType')
    _DefinitionLocation = pyxb.utils.utility.Location('/tmp/pyxbdist.RHB65sy/PyXB-1.1.5/pyxb/bundles/saml20/schemas/assertion.xsd', 91, 4)
    # Base type is pyxb.binding.datatypes.anyType
    
    # Element {urn:oasis:names:tc:SAML:2.0:assertion}BaseID uses Python identifier BaseID
    __BaseID = pyxb.binding.content.ElementUse(pyxb.namespace.ExpandedName(Namespace, u'BaseID'), 'BaseID', '__urnoasisnamestcSAML2_0assertion_SubjectConfirmationType_urnoasisnamestcSAML2_0assertionBaseID', False)
    __BaseID._DeclarationLocation = pyxb.utils.utility.Location('/tmp/pyxbdist.RHB65sy/PyXB-1.1.5/pyxb/bundles/saml20/schemas/assertion.xsd', 33, 4)
    __BaseID._UseLocation = pyxb.utils.utility.Location('/tmp/pyxbdist.RHB65sy/PyXB-1.1.5/pyxb/bundles/saml20/schemas/assertion.xsd', 92, 8)

    
    BaseID = property(__BaseID.value, __BaseID.set, None, None)

    
    # Element {urn:oasis:names:tc:SAML:2.0:assertion}EncryptedID uses Python identifier EncryptedID
    __EncryptedID = pyxb.binding.content.ElementUse(pyxb.namespace.ExpandedName(Namespace, u'EncryptedID'), 'EncryptedID', '__urnoasisnamestcSAML2_0assertion_SubjectConfirmationType_urnoasisnamestcSAML2_0assertionEncryptedID', False)
    __EncryptedID._DeclarationLocation = pyxb.utils.utility.Location('/tmp/pyxbdist.RHB65sy/PyXB-1.1.5/pyxb/bundles/saml20/schemas/assertion.xsd', 53, 4)
    __EncryptedID._UseLocation = pyxb.utils.utility.Location('/tmp/pyxbdist.RHB65sy/PyXB-1.1.5/pyxb/bundles/saml20/schemas/assertion.xsd', 92, 8)

    
    EncryptedID = property(__EncryptedID.value, __EncryptedID.set, None, None)

    
    # Element {urn:oasis:names:tc:SAML:2.0:assertion}SubjectConfirmationData uses Python identifier SubjectConfirmationData
    __SubjectConfirmationData = pyxb.binding.content.ElementUse(pyxb.namespace.ExpandedName(Namespace, u'SubjectConfirmationData'), 'SubjectConfirmationData', '__urnoasisnamestcSAML2_0assertion_SubjectConfirmationType_urnoasisnamestcSAML2_0assertionSubjectConfirmationData', False)
    __SubjectConfirmationData._DeclarationLocation = pyxb.utils.utility.Location('/tmp/pyxbdist.RHB65sy/PyXB-1.1.5/pyxb/bundles/saml20/schemas/assertion.xsd', 102, 4)
    __SubjectConfirmationData._UseLocation = pyxb.utils.utility.Location('/tmp/pyxbdist.RHB65sy/PyXB-1.1.5/pyxb/bundles/saml20/schemas/assertion.xsd', 92, 8)

    
    SubjectConfirmationData = property(__SubjectConfirmationData.value, __SubjectConfirmationData.set, None, None)

    
    # Element {urn:oasis:names:tc:SAML:2.0:assertion}NameID uses Python identifier NameID
    __NameID = pyxb.binding.content.ElementUse(pyxb.namespace.ExpandedName(Namespace, u'NameID'), 'NameID', '__urnoasisnamestcSAML2_0assertion_SubjectConfirmationType_urnoasisnamestcSAML2_0assertionNameID', False)
    __NameID._DeclarationLocation = pyxb.utils.utility.Location('/tmp/pyxbdist.RHB65sy/PyXB-1.1.5/pyxb/bundles/saml20/schemas/assertion.xsd', 37, 4)
    __NameID._UseLocation = pyxb.utils.utility.Location('/tmp/pyxbdist.RHB65sy/PyXB-1.1.5/pyxb/bundles/saml20/schemas/assertion.xsd', 92, 8)

    
    NameID = property(__NameID.value, __NameID.set, None, None)

    
    # Attribute Method uses Python identifier Method
    __Method = pyxb.binding.content.AttributeUse(pyxb.namespace.ExpandedName(None, u'Method'), 'Method', '__urnoasisnamestcSAML2_0assertion_SubjectConfirmationType_Method', pyxb.binding.datatypes.anyURI, required=True)
    __Method._DeclarationLocation = pyxb.utils.utility.Location('/tmp/pyxbdist.RHB65sy/PyXB-1.1.5/pyxb/bundles/saml20/schemas/assertion.xsd', 100, 8)
    __Method._UseLocation = pyxb.utils.utility.Location('/tmp/pyxbdist.RHB65sy/PyXB-1.1.5/pyxb/bundles/saml20/schemas/assertion.xsd', 100, 8)
    
    Method = property(__Method.value, __Method.set, None, None)


    _ElementMap = {
        __BaseID.name() : __BaseID,
        __EncryptedID.name() : __EncryptedID,
        __SubjectConfirmationData.name() : __SubjectConfirmationData,
        __NameID.name() : __NameID
    }
    _AttributeMap = {
        __Method.name() : __Method
    }
Namespace.addCategoryObject('typeBinding', u'SubjectConfirmationType', SubjectConfirmationType)


# Complex type {urn:oasis:names:tc:SAML:2.0:assertion}AssertionType with content type ELEMENT_ONLY
class AssertionType (pyxb.binding.basis.complexTypeDefinition):
    _TypeDefinition = None
    _ContentTypeTag = pyxb.binding.basis.complexTypeDefinition._CT_ELEMENT_ONLY
    _Abstract = False
    _ExpandedName = pyxb.namespace.ExpandedName(Namespace, u'AssertionType')
    _DefinitionLocation = pyxb.utils.utility.Location('/tmp/pyxbdist.RHB65sy/PyXB-1.1.5/pyxb/bundles/saml20/schemas/assertion.xsd', 58, 4)
    # Base type is pyxb.binding.datatypes.anyType
    
    # Element {urn:oasis:names:tc:SAML:2.0:assertion}Issuer uses Python identifier Issuer
    __Issuer = pyxb.binding.content.ElementUse(pyxb.namespace.ExpandedName(Namespace, u'Issuer'), 'Issuer', '__urnoasisnamestcSAML2_0assertion_AssertionType_urnoasisnamestcSAML2_0assertionIssuer', False)
    __Issuer._DeclarationLocation = pyxb.utils.utility.Location('/tmp/pyxbdist.RHB65sy/PyXB-1.1.5/pyxb/bundles/saml20/schemas/assertion.xsd', 54, 4)
    __Issuer._UseLocation = pyxb.utils.utility.Location('/tmp/pyxbdist.RHB65sy/PyXB-1.1.5/pyxb/bundles/saml20/schemas/assertion.xsd', 59, 8)

    
    Issuer = property(__Issuer.value, __Issuer.set, None, None)

    
    # Element {http://www.w3.org/2000/09/xmldsig#}Signature uses Python identifier Signature
    __Signature = pyxb.binding.content.ElementUse(pyxb.namespace.ExpandedName(pyxb.namespace.NamespaceForURI(u'http://www.w3.org/2000/09/xmldsig#'), u'Signature'), 'Signature', '__urnoasisnamestcSAML2_0assertion_AssertionType_httpwww_w3_org200009xmldsigSignature', False)
    __Signature._DeclarationLocation = pyxb.utils.utility.Location('/tmp/pyxbdist.RHB65sy/PyXB-1.1.5/pyxb/bundles/wssplat/schemas/ds.xsd', 43, 0)
    __Signature._UseLocation = pyxb.utils.utility.Location('/tmp/pyxbdist.RHB65sy/PyXB-1.1.5/pyxb/bundles/saml20/schemas/assertion.xsd', 59, 8)

    
    Signature = property(__Signature.value, __Signature.set, None, None)

    
    # Element {urn:oasis:names:tc:SAML:2.0:assertion}Conditions uses Python identifier Conditions
    __Conditions = pyxb.binding.content.ElementUse(pyxb.namespace.ExpandedName(Namespace, u'Conditions'), 'Conditions', '__urnoasisnamestcSAML2_0assertion_AssertionType_urnoasisnamestcSAML2_0assertionConditions', False)
    __Conditions._DeclarationLocation = pyxb.utils.utility.Location('/tmp/pyxbdist.RHB65sy/PyXB-1.1.5/pyxb/bundles/saml20/schemas/assertion.xsd', 127, 4)
    __Conditions._UseLocation = pyxb.utils.utility.Location('/tmp/pyxbdist.RHB65sy/PyXB-1.1.5/pyxb/bundles/saml20/schemas/assertion.xsd', 59, 8)

    
    Conditions = property(__Conditions.value, __Conditions.set, None, None)

    
    # Element {urn:oasis:names:tc:SAML:2.0:assertion}Statement uses Python identifier Statement
    __Statement = pyxb.binding.content.ElementUse(pyxb.namespace.ExpandedName(Namespace, u'Statement'), 'Statement', '__urnoasisnamestcSAML2_0assertion_AssertionType_urnoasisnamestcSAML2_0assertionStatement', True)
    __Statement._DeclarationLocation = pyxb.utils.utility.Location('/tmp/pyxbdist.RHB65sy/PyXB-1.1.5/pyxb/bundles/saml20/schemas/assertion.xsd', 179, 4)
    __Statement._UseLocation = pyxb.utils.utility.Location('/tmp/pyxbdist.RHB65sy/PyXB-1.1.5/pyxb/bundles/saml20/schemas/assertion.xsd', 59, 8)

    
    Statement = property(__Statement.value, __Statement.set, None, None)

    
    # Element {urn:oasis:names:tc:SAML:2.0:assertion}AttributeStatement uses Python identifier AttributeStatement
    __AttributeStatement = pyxb.binding.content.ElementUse(pyxb.namespace.ExpandedName(Namespace, u'AttributeStatement'), 'AttributeStatement', '__urnoasisnamestcSAML2_0assertion_AssertionType_urnoasisnamestcSAML2_0assertionAttributeStatement', True)
    __AttributeStatement._DeclarationLocation = pyxb.utils.utility.Location('/tmp/pyxbdist.RHB65sy/PyXB-1.1.5/pyxb/bundles/saml20/schemas/assertion.xsd', 260, 4)
    __AttributeStatement._UseLocation = pyxb.utils.utility.Location('/tmp/pyxbdist.RHB65sy/PyXB-1.1.5/pyxb/bundles/saml20/schemas/assertion.xsd', 59, 8)

    
    AttributeStatement = property(__AttributeStatement.value, __AttributeStatement.set, None, None)

    
    # Element {urn:oasis:names:tc:SAML:2.0:assertion}Advice uses Python identifier Advice
    __Advice = pyxb.binding.content.ElementUse(pyxb.namespace.ExpandedName(Namespace, u'Advice'), 'Advice', '__urnoasisnamestcSAML2_0assertion_AssertionType_urnoasisnamestcSAML2_0assertionAdvice', False)
    __Advice._DeclarationLocation = pyxb.utils.utility.Location('/tmp/pyxbdist.RHB65sy/PyXB-1.1.5/pyxb/bundles/saml20/schemas/assertion.xsd', 168, 4)
    __Advice._UseLocation = pyxb.utils.utility.Location('/tmp/pyxbdist.RHB65sy/PyXB-1.1.5/pyxb/bundles/saml20/schemas/assertion.xsd', 59, 8)

    
    Advice = property(__Advice.value, __Advice.set, None, None)

    
    # Element {urn:oasis:names:tc:SAML:2.0:assertion}AuthnStatement uses Python identifier AuthnStatement
    __AuthnStatement = pyxb.binding.content.ElementUse(pyxb.namespace.ExpandedName(Namespace, u'AuthnStatement'), 'AuthnStatement', '__urnoasisnamestcSAML2_0assertion_AssertionType_urnoasisnamestcSAML2_0assertionAuthnStatement', True)
    __AuthnStatement._DeclarationLocation = pyxb.utils.utility.Location('/tmp/pyxbdist.RHB65sy/PyXB-1.1.5/pyxb/bundles/saml20/schemas/assertion.xsd', 181, 4)
    __AuthnStatement._UseLocation = pyxb.utils.utility.Location('/tmp/pyxbdist.RHB65sy/PyXB-1.1.5/pyxb/bundles/saml20/schemas/assertion.xsd', 59, 8)

    
    AuthnStatement = property(__AuthnStatement.value, __AuthnStatement.set, None, None)

    
    # Element {urn:oasis:names:tc:SAML:2.0:assertion}Subject uses Python identifier Subject
    __Subject = pyxb.binding.content.ElementUse(pyxb.namespace.ExpandedName(Namespace, u'Subject'), 'Subject', '__urnoasisnamestcSAML2_0assertion_AssertionType_urnoasisnamestcSAML2_0assertionSubject', False)
    __Subject._DeclarationLocation = pyxb.utils.utility.Location('/tmp/pyxbdist.RHB65sy/PyXB-1.1.5/pyxb/bundles/saml20/schemas/assertion.xsd', 76, 4)
    __Subject._UseLocation = pyxb.utils.utility.Location('/tmp/pyxbdist.RHB65sy/PyXB-1.1.5/pyxb/bundles/saml20/schemas/assertion.xsd', 59, 8)

    
    Subject = property(__Subject.value, __Subject.set, None, None)

    
    # Element {urn:oasis:names:tc:SAML:2.0:assertion}AuthzDecisionStatement uses Python identifier AuthzDecisionStatement
    __AuthzDecisionStatement = pyxb.binding.content.ElementUse(pyxb.namespace.ExpandedName(Namespace, u'AuthzDecisionStatement'), 'AuthzDecisionStatement', '__urnoasisnamestcSAML2_0assertion_AssertionType_urnoasisnamestcSAML2_0assertionAuthzDecisionStatement', True)
    __AuthzDecisionStatement._DeclarationLocation = pyxb.utils.utility.Location('/tmp/pyxbdist.RHB65sy/PyXB-1.1.5/pyxb/bundles/saml20/schemas/assertion.xsd', 223, 4)
    __AuthzDecisionStatement._UseLocation = pyxb.utils.utility.Location('/tmp/pyxbdist.RHB65sy/PyXB-1.1.5/pyxb/bundles/saml20/schemas/assertion.xsd', 59, 8)

    
    AuthzDecisionStatement = property(__AuthzDecisionStatement.value, __AuthzDecisionStatement.set, None, None)

    
    # Attribute Version uses Python identifier Version
    __Version = pyxb.binding.content.AttributeUse(pyxb.namespace.ExpandedName(None, u'Version'), 'Version', '__urnoasisnamestcSAML2_0assertion_AssertionType_Version', pyxb.binding.datatypes.string, required=True)
    __Version._DeclarationLocation = pyxb.utils.utility.Location('/tmp/pyxbdist.RHB65sy/PyXB-1.1.5/pyxb/bundles/saml20/schemas/assertion.xsd', 72, 8)
    __Version._UseLocation = pyxb.utils.utility.Location('/tmp/pyxbdist.RHB65sy/PyXB-1.1.5/pyxb/bundles/saml20/schemas/assertion.xsd', 72, 8)
    
    Version = property(__Version.value, __Version.set, None, None)

    
    # Attribute ID uses Python identifier ID
    __ID = pyxb.binding.content.AttributeUse(pyxb.namespace.ExpandedName(None, u'ID'), 'ID', '__urnoasisnamestcSAML2_0assertion_AssertionType_ID', pyxb.binding.datatypes.ID, required=True)
    __ID._DeclarationLocation = pyxb.utils.utility.Location('/tmp/pyxbdist.RHB65sy/PyXB-1.1.5/pyxb/bundles/saml20/schemas/assertion.xsd', 73, 8)
    __ID._UseLocation = pyxb.utils.utility.Location('/tmp/pyxbdist.RHB65sy/PyXB-1.1.5/pyxb/bundles/saml20/schemas/assertion.xsd', 73, 8)
    
    ID = property(__ID.value, __ID.set, None, None)

    
    # Attribute IssueInstant uses Python identifier IssueInstant
    __IssueInstant = pyxb.binding.content.AttributeUse(pyxb.namespace.ExpandedName(None, u'IssueInstant'), 'IssueInstant', '__urnoasisnamestcSAML2_0assertion_AssertionType_IssueInstant', pyxb.binding.datatypes.dateTime, required=True)
    __IssueInstant._DeclarationLocation = pyxb.utils.utility.Location('/tmp/pyxbdist.RHB65sy/PyXB-1.1.5/pyxb/bundles/saml20/schemas/assertion.xsd', 74, 8)
    __IssueInstant._UseLocation = pyxb.utils.utility.Location('/tmp/pyxbdist.RHB65sy/PyXB-1.1.5/pyxb/bundles/saml20/schemas/assertion.xsd', 74, 8)
    
    IssueInstant = property(__IssueInstant.value, __IssueInstant.set, None, None)


    _ElementMap = {
        __Issuer.name() : __Issuer,
        __Signature.name() : __Signature,
        __Conditions.name() : __Conditions,
        __Statement.name() : __Statement,
        __AttributeStatement.name() : __AttributeStatement,
        __Advice.name() : __Advice,
        __AuthnStatement.name() : __AuthnStatement,
        __Subject.name() : __Subject,
        __AuthzDecisionStatement.name() : __AuthzDecisionStatement
    }
    _AttributeMap = {
        __Version.name() : __Version,
        __ID.name() : __ID,
        __IssueInstant.name() : __IssueInstant
    }
Namespace.addCategoryObject('typeBinding', u'AssertionType', AssertionType)


# Complex type {urn:oasis:names:tc:SAML:2.0:assertion}ActionType with content type SIMPLE
class ActionType (pyxb.binding.basis.complexTypeDefinition):
    _TypeDefinition = pyxb.binding.datatypes.string
    _ContentTypeTag = pyxb.binding.basis.complexTypeDefinition._CT_SIMPLE
    _Abstract = False
    _ExpandedName = pyxb.namespace.ExpandedName(Namespace, u'ActionType')
    _DefinitionLocation = pyxb.utils.utility.Location('/tmp/pyxbdist.RHB65sy/PyXB-1.1.5/pyxb/bundles/saml20/schemas/assertion.xsd', 244, 4)
    # Base type is pyxb.binding.datatypes.string
    
    # Attribute Namespace uses Python identifier Namespace
    __Namespace = pyxb.binding.content.AttributeUse(pyxb.namespace.ExpandedName(None, u'Namespace'), 'Namespace', '__urnoasisnamestcSAML2_0assertion_ActionType_Namespace', pyxb.binding.datatypes.anyURI, required=True)
    __Namespace._DeclarationLocation = pyxb.utils.utility.Location('/tmp/pyxbdist.RHB65sy/PyXB-1.1.5/pyxb/bundles/saml20/schemas/assertion.xsd', 247, 16)
    __Namespace._UseLocation = pyxb.utils.utility.Location('/tmp/pyxbdist.RHB65sy/PyXB-1.1.5/pyxb/bundles/saml20/schemas/assertion.xsd', 247, 16)
    
    Namespace = property(__Namespace.value, __Namespace.set, None, None)


    _ElementMap = {
        
    }
    _AttributeMap = {
        __Namespace.name() : __Namespace
    }
Namespace.addCategoryObject('typeBinding', u'ActionType', ActionType)


# Complex type {urn:oasis:names:tc:SAML:2.0:assertion}SubjectConfirmationDataType with content type MIXED
class SubjectConfirmationDataType (pyxb.binding.basis.complexTypeDefinition):
    _TypeDefinition = None
    _ContentTypeTag = pyxb.binding.basis.complexTypeDefinition._CT_MIXED
    _Abstract = False
    _ExpandedName = pyxb.namespace.ExpandedName(Namespace, u'SubjectConfirmationDataType')
    _DefinitionLocation = pyxb.utils.utility.Location('/tmp/pyxbdist.RHB65sy/PyXB-1.1.5/pyxb/bundles/saml20/schemas/assertion.xsd', 103, 4)
    # Base type is pyxb.binding.datatypes.anyType
    
    # Attribute Address uses Python identifier Address
    __Address = pyxb.binding.content.AttributeUse(pyxb.namespace.ExpandedName(None, u'Address'), 'Address', '__urnoasisnamestcSAML2_0assertion_SubjectConfirmationDataType_Address', pyxb.binding.datatypes.string)
    __Address._DeclarationLocation = pyxb.utils.utility.Location('/tmp/pyxbdist.RHB65sy/PyXB-1.1.5/pyxb/bundles/saml20/schemas/assertion.xsd', 113, 16)
    __Address._UseLocation = pyxb.utils.utility.Location('/tmp/pyxbdist.RHB65sy/PyXB-1.1.5/pyxb/bundles/saml20/schemas/assertion.xsd', 113, 16)
    
    Address = property(__Address.value, __Address.set, None, None)

    
    # Attribute NotBefore uses Python identifier NotBefore
    __NotBefore = pyxb.binding.content.AttributeUse(pyxb.namespace.ExpandedName(None, u'NotBefore'), 'NotBefore', '__urnoasisnamestcSAML2_0assertion_SubjectConfirmationDataType_NotBefore', pyxb.binding.datatypes.dateTime)
    __NotBefore._DeclarationLocation = pyxb.utils.utility.Location('/tmp/pyxbdist.RHB65sy/PyXB-1.1.5/pyxb/bundles/saml20/schemas/assertion.xsd', 109, 16)
    __NotBefore._UseLocation = pyxb.utils.utility.Location('/tmp/pyxbdist.RHB65sy/PyXB-1.1.5/pyxb/bundles/saml20/schemas/assertion.xsd', 109, 16)
    
    NotBefore = property(__NotBefore.value, __NotBefore.set, None, None)

    
    # Attribute Recipient uses Python identifier Recipient
    __Recipient = pyxb.binding.content.AttributeUse(pyxb.namespace.ExpandedName(None, u'Recipient'), 'Recipient', '__urnoasisnamestcSAML2_0assertion_SubjectConfirmationDataType_Recipient', pyxb.binding.datatypes.anyURI)
    __Recipient._DeclarationLocation = pyxb.utils.utility.Location('/tmp/pyxbdist.RHB65sy/PyXB-1.1.5/pyxb/bundles/saml20/schemas/assertion.xsd', 111, 16)
    __Recipient._UseLocation = pyxb.utils.utility.Location('/tmp/pyxbdist.RHB65sy/PyXB-1.1.5/pyxb/bundles/saml20/schemas/assertion.xsd', 111, 16)
    
    Recipient = property(__Recipient.value, __Recipient.set, None, None)

    
    # Attribute InResponseTo uses Python identifier InResponseTo
    __InResponseTo = pyxb.binding.content.AttributeUse(pyxb.namespace.ExpandedName(None, u'InResponseTo'), 'InResponseTo', '__urnoasisnamestcSAML2_0assertion_SubjectConfirmationDataType_InResponseTo', pyxb.binding.datatypes.NCName)
    __InResponseTo._DeclarationLocation = pyxb.utils.utility.Location('/tmp/pyxbdist.RHB65sy/PyXB-1.1.5/pyxb/bundles/saml20/schemas/assertion.xsd', 112, 16)
    __InResponseTo._UseLocation = pyxb.utils.utility.Location('/tmp/pyxbdist.RHB65sy/PyXB-1.1.5/pyxb/bundles/saml20/schemas/assertion.xsd', 112, 16)
    
    InResponseTo = property(__InResponseTo.value, __InResponseTo.set, None, None)

    
    # Attribute NotOnOrAfter uses Python identifier NotOnOrAfter
    __NotOnOrAfter = pyxb.binding.content.AttributeUse(pyxb.namespace.ExpandedName(None, u'NotOnOrAfter'), 'NotOnOrAfter', '__urnoasisnamestcSAML2_0assertion_SubjectConfirmationDataType_NotOnOrAfter', pyxb.binding.datatypes.dateTime)
    __NotOnOrAfter._DeclarationLocation = pyxb.utils.utility.Location('/tmp/pyxbdist.RHB65sy/PyXB-1.1.5/pyxb/bundles/saml20/schemas/assertion.xsd', 110, 16)
    __NotOnOrAfter._UseLocation = pyxb.utils.utility.Location('/tmp/pyxbdist.RHB65sy/PyXB-1.1.5/pyxb/bundles/saml20/schemas/assertion.xsd', 110, 16)
    
    NotOnOrAfter = property(__NotOnOrAfter.value, __NotOnOrAfter.set, None, None)

    _AttributeWildcard = pyxb.binding.content.Wildcard(process_contents=pyxb.binding.content.Wildcard.PC_lax, namespace_constraint=(pyxb.binding.content.Wildcard.NC_not, u'urn:oasis:names:tc:SAML:2.0:assertion'))
    _HasWildcardElement = True

    _ElementMap = {
        
    }
    _AttributeMap = {
        __Address.name() : __Address,
        __NotBefore.name() : __NotBefore,
        __Recipient.name() : __Recipient,
        __InResponseTo.name() : __InResponseTo,
        __NotOnOrAfter.name() : __NotOnOrAfter
    }
Namespace.addCategoryObject('typeBinding', u'SubjectConfirmationDataType', SubjectConfirmationDataType)


# Complex type {urn:oasis:names:tc:SAML:2.0:assertion}SubjectLocalityType with content type EMPTY
class SubjectLocalityType (pyxb.binding.basis.complexTypeDefinition):
    _TypeDefinition = None
    _ContentTypeTag = pyxb.binding.basis.complexTypeDefinition._CT_EMPTY
    _Abstract = False
    _ExpandedName = pyxb.namespace.ExpandedName(Namespace, u'SubjectLocalityType')
    _DefinitionLocation = pyxb.utils.utility.Location('/tmp/pyxbdist.RHB65sy/PyXB-1.1.5/pyxb/bundles/saml20/schemas/assertion.xsd', 196, 4)
    # Base type is pyxb.binding.datatypes.anyType
    
    # Attribute DNSName uses Python identifier DNSName
    __DNSName = pyxb.binding.content.AttributeUse(pyxb.namespace.ExpandedName(None, u'DNSName'), 'DNSName', '__urnoasisnamestcSAML2_0assertion_SubjectLocalityType_DNSName', pyxb.binding.datatypes.string)
    __DNSName._DeclarationLocation = pyxb.utils.utility.Location('/tmp/pyxbdist.RHB65sy/PyXB-1.1.5/pyxb/bundles/saml20/schemas/assertion.xsd', 198, 8)
    __DNSName._UseLocation = pyxb.utils.utility.Location('/tmp/pyxbdist.RHB65sy/PyXB-1.1.5/pyxb/bundles/saml20/schemas/assertion.xsd', 198, 8)
    
    DNSName = property(__DNSName.value, __DNSName.set, None, None)

    
    # Attribute Address uses Python identifier Address
    __Address = pyxb.binding.content.AttributeUse(pyxb.namespace.ExpandedName(None, u'Address'), 'Address', '__urnoasisnamestcSAML2_0assertion_SubjectLocalityType_Address', pyxb.binding.datatypes.string)
    __Address._DeclarationLocation = pyxb.utils.utility.Location('/tmp/pyxbdist.RHB65sy/PyXB-1.1.5/pyxb/bundles/saml20/schemas/assertion.xsd', 197, 8)
    __Address._UseLocation = pyxb.utils.utility.Location('/tmp/pyxbdist.RHB65sy/PyXB-1.1.5/pyxb/bundles/saml20/schemas/assertion.xsd', 197, 8)
    
    Address = property(__Address.value, __Address.set, None, None)


    _ElementMap = {
        
    }
    _AttributeMap = {
        __DNSName.name() : __DNSName,
        __Address.name() : __Address
    }
Namespace.addCategoryObject('typeBinding', u'SubjectLocalityType', SubjectLocalityType)


# Complex type {urn:oasis:names:tc:SAML:2.0:assertion}ConditionsType with content type ELEMENT_ONLY
class ConditionsType (pyxb.binding.basis.complexTypeDefinition):
    _TypeDefinition = None
    _ContentTypeTag = pyxb.binding.basis.complexTypeDefinition._CT_ELEMENT_ONLY
    _Abstract = False
    _ExpandedName = pyxb.namespace.ExpandedName(Namespace, u'ConditionsType')
    _DefinitionLocation = pyxb.utils.utility.Location('/tmp/pyxbdist.RHB65sy/PyXB-1.1.5/pyxb/bundles/saml20/schemas/assertion.xsd', 128, 4)
    # Base type is pyxb.binding.datatypes.anyType
    
    # Element {urn:oasis:names:tc:SAML:2.0:assertion}ProxyRestriction uses Python identifier ProxyRestriction
    __ProxyRestriction = pyxb.binding.content.ElementUse(pyxb.namespace.ExpandedName(Namespace, u'ProxyRestriction'), 'ProxyRestriction', '__urnoasisnamestcSAML2_0assertion_ConditionsType_urnoasisnamestcSAML2_0assertionProxyRestriction', True)
    __ProxyRestriction._DeclarationLocation = pyxb.utils.utility.Location('/tmp/pyxbdist.RHB65sy/PyXB-1.1.5/pyxb/bundles/saml20/schemas/assertion.xsd', 157, 4)
    __ProxyRestriction._UseLocation = pyxb.utils.utility.Location('/tmp/pyxbdist.RHB65sy/PyXB-1.1.5/pyxb/bundles/saml20/schemas/assertion.xsd', 129, 8)

    
    ProxyRestriction = property(__ProxyRestriction.value, __ProxyRestriction.set, None, None)

    
    # Element {urn:oasis:names:tc:SAML:2.0:assertion}OneTimeUse uses Python identifier OneTimeUse
    __OneTimeUse = pyxb.binding.content.ElementUse(pyxb.namespace.ExpandedName(Namespace, u'OneTimeUse'), 'OneTimeUse', '__urnoasisnamestcSAML2_0assertion_ConditionsType_urnoasisnamestcSAML2_0assertionOneTimeUse', True)
    __OneTimeUse._DeclarationLocation = pyxb.utils.utility.Location('/tmp/pyxbdist.RHB65sy/PyXB-1.1.5/pyxb/bundles/saml20/schemas/assertion.xsd', 151, 4)
    __OneTimeUse._UseLocation = pyxb.utils.utility.Location('/tmp/pyxbdist.RHB65sy/PyXB-1.1.5/pyxb/bundles/saml20/schemas/assertion.xsd', 129, 8)

    
    OneTimeUse = property(__OneTimeUse.value, __OneTimeUse.set, None, None)

    
    # Element {urn:oasis:names:tc:SAML:2.0:assertion}AudienceRestriction uses Python identifier AudienceRestriction
    __AudienceRestriction = pyxb.binding.content.ElementUse(pyxb.namespace.ExpandedName(Namespace, u'AudienceRestriction'), 'AudienceRestriction', '__urnoasisnamestcSAML2_0assertion_ConditionsType_urnoasisnamestcSAML2_0assertionAudienceRestriction', True)
    __AudienceRestriction._DeclarationLocation = pyxb.utils.utility.Location('/tmp/pyxbdist.RHB65sy/PyXB-1.1.5/pyxb/bundles/saml20/schemas/assertion.xsd', 140, 4)
    __AudienceRestriction._UseLocation = pyxb.utils.utility.Location('/tmp/pyxbdist.RHB65sy/PyXB-1.1.5/pyxb/bundles/saml20/schemas/assertion.xsd', 129, 8)

    
    AudienceRestriction = property(__AudienceRestriction.value, __AudienceRestriction.set, None, None)

    
    # Element {urn:oasis:names:tc:SAML:2.0:assertion}Condition uses Python identifier Condition
    __Condition = pyxb.binding.content.ElementUse(pyxb.namespace.ExpandedName(Namespace, u'Condition'), 'Condition', '__urnoasisnamestcSAML2_0assertion_ConditionsType_urnoasisnamestcSAML2_0assertionCondition', True)
    __Condition._DeclarationLocation = pyxb.utils.utility.Location('/tmp/pyxbdist.RHB65sy/PyXB-1.1.5/pyxb/bundles/saml20/schemas/assertion.xsd', 138, 4)
    __Condition._UseLocation = pyxb.utils.utility.Location('/tmp/pyxbdist.RHB65sy/PyXB-1.1.5/pyxb/bundles/saml20/schemas/assertion.xsd', 129, 8)

    
    Condition = property(__Condition.value, __Condition.set, None, None)

    
    # Attribute NotOnOrAfter uses Python identifier NotOnOrAfter
    __NotOnOrAfter = pyxb.binding.content.AttributeUse(pyxb.namespace.ExpandedName(None, u'NotOnOrAfter'), 'NotOnOrAfter', '__urnoasisnamestcSAML2_0assertion_ConditionsType_NotOnOrAfter', pyxb.binding.datatypes.dateTime)
    __NotOnOrAfter._DeclarationLocation = pyxb.utils.utility.Location('/tmp/pyxbdist.RHB65sy/PyXB-1.1.5/pyxb/bundles/saml20/schemas/assertion.xsd', 136, 8)
    __NotOnOrAfter._UseLocation = pyxb.utils.utility.Location('/tmp/pyxbdist.RHB65sy/PyXB-1.1.5/pyxb/bundles/saml20/schemas/assertion.xsd', 136, 8)
    
    NotOnOrAfter = property(__NotOnOrAfter.value, __NotOnOrAfter.set, None, None)

    
    # Attribute NotBefore uses Python identifier NotBefore
    __NotBefore = pyxb.binding.content.AttributeUse(pyxb.namespace.ExpandedName(None, u'NotBefore'), 'NotBefore', '__urnoasisnamestcSAML2_0assertion_ConditionsType_NotBefore', pyxb.binding.datatypes.dateTime)
    __NotBefore._DeclarationLocation = pyxb.utils.utility.Location('/tmp/pyxbdist.RHB65sy/PyXB-1.1.5/pyxb/bundles/saml20/schemas/assertion.xsd', 135, 8)
    __NotBefore._UseLocation = pyxb.utils.utility.Location('/tmp/pyxbdist.RHB65sy/PyXB-1.1.5/pyxb/bundles/saml20/schemas/assertion.xsd', 135, 8)
    
    NotBefore = property(__NotBefore.value, __NotBefore.set, None, None)


    _ElementMap = {
        __ProxyRestriction.name() : __ProxyRestriction,
        __OneTimeUse.name() : __OneTimeUse,
        __AudienceRestriction.name() : __AudienceRestriction,
        __Condition.name() : __Condition
    }
    _AttributeMap = {
        __NotOnOrAfter.name() : __NotOnOrAfter,
        __NotBefore.name() : __NotBefore
    }
Namespace.addCategoryObject('typeBinding', u'ConditionsType', ConditionsType)


# Complex type {urn:oasis:names:tc:SAML:2.0:assertion}ProxyRestrictionType with content type ELEMENT_ONLY
class ProxyRestrictionType (ConditionAbstractType):
    _TypeDefinition = None
    _ContentTypeTag = pyxb.binding.basis.complexTypeDefinition._CT_ELEMENT_ONLY
    _Abstract = False
    _ExpandedName = pyxb.namespace.ExpandedName(Namespace, u'ProxyRestrictionType')
    _DefinitionLocation = pyxb.utils.utility.Location('/tmp/pyxbdist.RHB65sy/PyXB-1.1.5/pyxb/bundles/saml20/schemas/assertion.xsd', 158, 4)
    # Base type is ConditionAbstractType
    
    # Element {urn:oasis:names:tc:SAML:2.0:assertion}Audience uses Python identifier Audience
    __Audience = pyxb.binding.content.ElementUse(pyxb.namespace.ExpandedName(Namespace, u'Audience'), 'Audience', '__urnoasisnamestcSAML2_0assertion_ProxyRestrictionType_urnoasisnamestcSAML2_0assertionAudience', True)
    __Audience._DeclarationLocation = pyxb.utils.utility.Location('/tmp/pyxbdist.RHB65sy/PyXB-1.1.5/pyxb/bundles/saml20/schemas/assertion.xsd', 150, 4)
    __Audience._UseLocation = pyxb.utils.utility.Location('/tmp/pyxbdist.RHB65sy/PyXB-1.1.5/pyxb/bundles/saml20/schemas/assertion.xsd', 161, 12)

    
    Audience = property(__Audience.value, __Audience.set, None, None)

    
    # Attribute Count uses Python identifier Count
    __Count = pyxb.binding.content.AttributeUse(pyxb.namespace.ExpandedName(None, u'Count'), 'Count', '__urnoasisnamestcSAML2_0assertion_ProxyRestrictionType_Count', pyxb.binding.datatypes.nonNegativeInteger)
    __Count._DeclarationLocation = pyxb.utils.utility.Location('/tmp/pyxbdist.RHB65sy/PyXB-1.1.5/pyxb/bundles/saml20/schemas/assertion.xsd', 164, 12)
    __Count._UseLocation = pyxb.utils.utility.Location('/tmp/pyxbdist.RHB65sy/PyXB-1.1.5/pyxb/bundles/saml20/schemas/assertion.xsd', 164, 12)
    
    Count = property(__Count.value, __Count.set, None, None)


    _ElementMap = ConditionAbstractType._ElementMap.copy()
    _ElementMap.update({
        __Audience.name() : __Audience
    })
    _AttributeMap = ConditionAbstractType._AttributeMap.copy()
    _AttributeMap.update({
        __Count.name() : __Count
    })
Namespace.addCategoryObject('typeBinding', u'ProxyRestrictionType', ProxyRestrictionType)


# Complex type {urn:oasis:names:tc:SAML:2.0:assertion}KeyInfoConfirmationDataType with content type ELEMENT_ONLY
class KeyInfoConfirmationDataType (SubjectConfirmationDataType):
    _TypeDefinition = None
    _ContentTypeTag = pyxb.binding.basis.complexTypeDefinition._CT_ELEMENT_ONLY
    _Abstract = False
    _ExpandedName = pyxb.namespace.ExpandedName(Namespace, u'KeyInfoConfirmationDataType')
    _DefinitionLocation = pyxb.utils.utility.Location('/tmp/pyxbdist.RHB65sy/PyXB-1.1.5/pyxb/bundles/saml20/schemas/assertion.xsd', 118, 4)
    # Base type is SubjectConfirmationDataType
    
    # Element {http://www.w3.org/2000/09/xmldsig#}KeyInfo uses Python identifier KeyInfo
    __KeyInfo = pyxb.binding.content.ElementUse(pyxb.namespace.ExpandedName(pyxb.namespace.NamespaceForURI(u'http://www.w3.org/2000/09/xmldsig#'), u'KeyInfo'), 'KeyInfo', '__urnoasisnamestcSAML2_0assertion_KeyInfoConfirmationDataType_httpwww_w3_org200009xmldsigKeyInfo', True)
    __KeyInfo._DeclarationLocation = pyxb.utils.utility.Location('/tmp/pyxbdist.RHB65sy/PyXB-1.1.5/pyxb/bundles/wssplat/schemas/ds.xsd', 144, 0)
    __KeyInfo._UseLocation = pyxb.utils.utility.Location('/tmp/pyxbdist.RHB65sy/PyXB-1.1.5/pyxb/bundles/saml20/schemas/assertion.xsd', 121, 16)

    
    KeyInfo = property(__KeyInfo.value, __KeyInfo.set, None, None)

    
    # Attribute Address inherited from {urn:oasis:names:tc:SAML:2.0:assertion}SubjectConfirmationDataType
    
    # Attribute Recipient inherited from {urn:oasis:names:tc:SAML:2.0:assertion}SubjectConfirmationDataType
    
    # Attribute NotBefore inherited from {urn:oasis:names:tc:SAML:2.0:assertion}SubjectConfirmationDataType
    
    # Attribute NotOnOrAfter inherited from {urn:oasis:names:tc:SAML:2.0:assertion}SubjectConfirmationDataType
    
    # Attribute InResponseTo inherited from {urn:oasis:names:tc:SAML:2.0:assertion}SubjectConfirmationDataType

    _ElementMap = SubjectConfirmationDataType._ElementMap.copy()
    _ElementMap.update({
        __KeyInfo.name() : __KeyInfo
    })
    _AttributeMap = SubjectConfirmationDataType._AttributeMap.copy()
    _AttributeMap.update({
        
    })
Namespace.addCategoryObject('typeBinding', u'KeyInfoConfirmationDataType', KeyInfoConfirmationDataType)


# Complex type {urn:oasis:names:tc:SAML:2.0:assertion}AttributeStatementType with content type ELEMENT_ONLY
class AttributeStatementType (StatementAbstractType):
    _TypeDefinition = None
    _ContentTypeTag = pyxb.binding.basis.complexTypeDefinition._CT_ELEMENT_ONLY
    _Abstract = False
    _ExpandedName = pyxb.namespace.ExpandedName(Namespace, u'AttributeStatementType')
    _DefinitionLocation = pyxb.utils.utility.Location('/tmp/pyxbdist.RHB65sy/PyXB-1.1.5/pyxb/bundles/saml20/schemas/assertion.xsd', 261, 4)
    # Base type is StatementAbstractType
    
    # Element {urn:oasis:names:tc:SAML:2.0:assertion}EncryptedAttribute uses Python identifier EncryptedAttribute
    __EncryptedAttribute = pyxb.binding.content.ElementUse(pyxb.namespace.ExpandedName(Namespace, u'EncryptedAttribute'), 'EncryptedAttribute', '__urnoasisnamestcSAML2_0assertion_AttributeStatementType_urnoasisnamestcSAML2_0assertionEncryptedAttribute', True)
    __EncryptedAttribute._DeclarationLocation = pyxb.utils.utility.Location('/tmp/pyxbdist.RHB65sy/PyXB-1.1.5/pyxb/bundles/saml20/schemas/assertion.xsd', 282, 4)
    __EncryptedAttribute._UseLocation = pyxb.utils.utility.Location('/tmp/pyxbdist.RHB65sy/PyXB-1.1.5/pyxb/bundles/saml20/schemas/assertion.xsd', 264, 16)

    
    EncryptedAttribute = property(__EncryptedAttribute.value, __EncryptedAttribute.set, None, None)

    
    # Element {urn:oasis:names:tc:SAML:2.0:assertion}Attribute uses Python identifier Attribute
    __Attribute = pyxb.binding.content.ElementUse(pyxb.namespace.ExpandedName(Namespace, u'Attribute'), 'Attribute', '__urnoasisnamestcSAML2_0assertion_AttributeStatementType_urnoasisnamestcSAML2_0assertionAttribute', True)
    __Attribute._DeclarationLocation = pyxb.utils.utility.Location('/tmp/pyxbdist.RHB65sy/PyXB-1.1.5/pyxb/bundles/saml20/schemas/assertion.xsd', 271, 4)
    __Attribute._UseLocation = pyxb.utils.utility.Location('/tmp/pyxbdist.RHB65sy/PyXB-1.1.5/pyxb/bundles/saml20/schemas/assertion.xsd', 264, 16)

    
    Attribute = property(__Attribute.value, __Attribute.set, None, None)


    _ElementMap = StatementAbstractType._ElementMap.copy()
    _ElementMap.update({
        __EncryptedAttribute.name() : __EncryptedAttribute,
        __Attribute.name() : __Attribute
    })
    _AttributeMap = StatementAbstractType._AttributeMap.copy()
    _AttributeMap.update({
        
    })
Namespace.addCategoryObject('typeBinding', u'AttributeStatementType', AttributeStatementType)


# Complex type {urn:oasis:names:tc:SAML:2.0:assertion}OneTimeUseType with content type EMPTY
class OneTimeUseType (ConditionAbstractType):
    _TypeDefinition = None
    _ContentTypeTag = pyxb.binding.basis.complexTypeDefinition._CT_EMPTY
    _Abstract = False
    _ExpandedName = pyxb.namespace.ExpandedName(Namespace, u'OneTimeUseType')
    _DefinitionLocation = pyxb.utils.utility.Location('/tmp/pyxbdist.RHB65sy/PyXB-1.1.5/pyxb/bundles/saml20/schemas/assertion.xsd', 152, 4)
    # Base type is ConditionAbstractType

    _ElementMap = ConditionAbstractType._ElementMap.copy()
    _ElementMap.update({
        
    })
    _AttributeMap = ConditionAbstractType._AttributeMap.copy()
    _AttributeMap.update({
        
    })
Namespace.addCategoryObject('typeBinding', u'OneTimeUseType', OneTimeUseType)


# Complex type {urn:oasis:names:tc:SAML:2.0:assertion}BaseIDAbstractType with content type EMPTY
class BaseIDAbstractType (pyxb.binding.basis.complexTypeDefinition):
    _TypeDefinition = None
    _ContentTypeTag = pyxb.binding.basis.complexTypeDefinition._CT_EMPTY
    _Abstract = True
    _ExpandedName = pyxb.namespace.ExpandedName(Namespace, u'BaseIDAbstractType')
    _DefinitionLocation = pyxb.utils.utility.Location('/tmp/pyxbdist.RHB65sy/PyXB-1.1.5/pyxb/bundles/saml20/schemas/assertion.xsd', 34, 4)
    # Base type is pyxb.binding.datatypes.anyType
    
    # Attribute SPNameQualifier uses Python identifier SPNameQualifier
    __SPNameQualifier = pyxb.binding.content.AttributeUse(pyxb.namespace.ExpandedName(None, u'SPNameQualifier'), 'SPNameQualifier', '__urnoasisnamestcSAML2_0assertion_BaseIDAbstractType_SPNameQualifier', pyxb.binding.datatypes.string)
    __SPNameQualifier._DeclarationLocation = pyxb.utils.utility.Location('/tmp/pyxbdist.RHB65sy/PyXB-1.1.5/pyxb/bundles/saml20/schemas/assertion.xsd', 31, 8)
    __SPNameQualifier._UseLocation = pyxb.utils.utility.Location('/tmp/pyxbdist.RHB65sy/PyXB-1.1.5/pyxb/bundles/saml20/schemas/assertion.xsd', 31, 8)
    
    SPNameQualifier = property(__SPNameQualifier.value, __SPNameQualifier.set, None, None)

    
    # Attribute NameQualifier uses Python identifier NameQualifier
    __NameQualifier = pyxb.binding.content.AttributeUse(pyxb.namespace.ExpandedName(None, u'NameQualifier'), 'NameQualifier', '__urnoasisnamestcSAML2_0assertion_BaseIDAbstractType_NameQualifier', pyxb.binding.datatypes.string)
    __NameQualifier._DeclarationLocation = pyxb.utils.utility.Location('/tmp/pyxbdist.RHB65sy/PyXB-1.1.5/pyxb/bundles/saml20/schemas/assertion.xsd', 30, 8)
    __NameQualifier._UseLocation = pyxb.utils.utility.Location('/tmp/pyxbdist.RHB65sy/PyXB-1.1.5/pyxb/bundles/saml20/schemas/assertion.xsd', 30, 8)
    
    NameQualifier = property(__NameQualifier.value, __NameQualifier.set, None, None)


    _ElementMap = {
        
    }
    _AttributeMap = {
        __SPNameQualifier.name() : __SPNameQualifier,
        __NameQualifier.name() : __NameQualifier
    }
Namespace.addCategoryObject('typeBinding', u'BaseIDAbstractType', BaseIDAbstractType)


# Complex type {urn:oasis:names:tc:SAML:2.0:assertion}AdviceType with content type ELEMENT_ONLY
class AdviceType (pyxb.binding.basis.complexTypeDefinition):
    _TypeDefinition = None
    _ContentTypeTag = pyxb.binding.basis.complexTypeDefinition._CT_ELEMENT_ONLY
    _Abstract = False
    _ExpandedName = pyxb.namespace.ExpandedName(Namespace, u'AdviceType')
    _DefinitionLocation = pyxb.utils.utility.Location('/tmp/pyxbdist.RHB65sy/PyXB-1.1.5/pyxb/bundles/saml20/schemas/assertion.xsd', 169, 4)
    # Base type is pyxb.binding.datatypes.anyType
    
    # Element {urn:oasis:names:tc:SAML:2.0:assertion}AssertionURIRef uses Python identifier AssertionURIRef
    __AssertionURIRef = pyxb.binding.content.ElementUse(pyxb.namespace.ExpandedName(Namespace, u'AssertionURIRef'), 'AssertionURIRef', '__urnoasisnamestcSAML2_0assertion_AdviceType_urnoasisnamestcSAML2_0assertionAssertionURIRef', True)
    __AssertionURIRef._DeclarationLocation = pyxb.utils.utility.Location('/tmp/pyxbdist.RHB65sy/PyXB-1.1.5/pyxb/bundles/saml20/schemas/assertion.xsd', 56, 4)
    __AssertionURIRef._UseLocation = pyxb.utils.utility.Location('/tmp/pyxbdist.RHB65sy/PyXB-1.1.5/pyxb/bundles/saml20/schemas/assertion.xsd', 170, 8)

    
    AssertionURIRef = property(__AssertionURIRef.value, __AssertionURIRef.set, None, None)

    
    # Element {urn:oasis:names:tc:SAML:2.0:assertion}AssertionIDRef uses Python identifier AssertionIDRef
    __AssertionIDRef = pyxb.binding.content.ElementUse(pyxb.namespace.ExpandedName(Namespace, u'AssertionIDRef'), 'AssertionIDRef', '__urnoasisnamestcSAML2_0assertion_AdviceType_urnoasisnamestcSAML2_0assertionAssertionIDRef', True)
    __AssertionIDRef._DeclarationLocation = pyxb.utils.utility.Location('/tmp/pyxbdist.RHB65sy/PyXB-1.1.5/pyxb/bundles/saml20/schemas/assertion.xsd', 55, 4)
    __AssertionIDRef._UseLocation = pyxb.utils.utility.Location('/tmp/pyxbdist.RHB65sy/PyXB-1.1.5/pyxb/bundles/saml20/schemas/assertion.xsd', 170, 8)

    
    AssertionIDRef = property(__AssertionIDRef.value, __AssertionIDRef.set, None, None)

    
    # Element {urn:oasis:names:tc:SAML:2.0:assertion}EncryptedAssertion uses Python identifier EncryptedAssertion
    __EncryptedAssertion = pyxb.binding.content.ElementUse(pyxb.namespace.ExpandedName(Namespace, u'EncryptedAssertion'), 'EncryptedAssertion', '__urnoasisnamestcSAML2_0assertion_AdviceType_urnoasisnamestcSAML2_0assertionEncryptedAssertion', True)
    __EncryptedAssertion._DeclarationLocation = pyxb.utils.utility.Location('/tmp/pyxbdist.RHB65sy/PyXB-1.1.5/pyxb/bundles/saml20/schemas/assertion.xsd', 178, 4)
    __EncryptedAssertion._UseLocation = pyxb.utils.utility.Location('/tmp/pyxbdist.RHB65sy/PyXB-1.1.5/pyxb/bundles/saml20/schemas/assertion.xsd', 170, 8)

    
    EncryptedAssertion = property(__EncryptedAssertion.value, __EncryptedAssertion.set, None, None)

    
    # Element {urn:oasis:names:tc:SAML:2.0:assertion}Assertion uses Python identifier Assertion
    __Assertion = pyxb.binding.content.ElementUse(pyxb.namespace.ExpandedName(Namespace, u'Assertion'), 'Assertion', '__urnoasisnamestcSAML2_0assertion_AdviceType_urnoasisnamestcSAML2_0assertionAssertion', True)
    __Assertion._DeclarationLocation = pyxb.utils.utility.Location('/tmp/pyxbdist.RHB65sy/PyXB-1.1.5/pyxb/bundles/saml20/schemas/assertion.xsd', 57, 4)
    __Assertion._UseLocation = pyxb.utils.utility.Location('/tmp/pyxbdist.RHB65sy/PyXB-1.1.5/pyxb/bundles/saml20/schemas/assertion.xsd', 170, 8)

    
    Assertion = property(__Assertion.value, __Assertion.set, None, None)

    _HasWildcardElement = True

    _ElementMap = {
        __AssertionURIRef.name() : __AssertionURIRef,
        __AssertionIDRef.name() : __AssertionIDRef,
        __EncryptedAssertion.name() : __EncryptedAssertion,
        __Assertion.name() : __Assertion
    }
    _AttributeMap = {
        
    }
Namespace.addCategoryObject('typeBinding', u'AdviceType', AdviceType)


AudienceRestriction = pyxb.binding.basis.element(pyxb.namespace.ExpandedName(Namespace, u'AudienceRestriction'), AudienceRestrictionType)
Namespace.addCategoryObject('elementBinding', AudienceRestriction.name().localName(), AudienceRestriction)

AuthnContextDecl = pyxb.binding.basis.element(pyxb.namespace.ExpandedName(Namespace, u'AuthnContextDecl'), pyxb.binding.datatypes.anyType)
Namespace.addCategoryObject('elementBinding', AuthnContextDecl.name().localName(), AuthnContextDecl)

AuthnContextClassRef = pyxb.binding.basis.element(pyxb.namespace.ExpandedName(Namespace, u'AuthnContextClassRef'), pyxb.binding.datatypes.anyURI)
Namespace.addCategoryObject('elementBinding', AuthnContextClassRef.name().localName(), AuthnContextClassRef)

AuthnContextDeclRef = pyxb.binding.basis.element(pyxb.namespace.ExpandedName(Namespace, u'AuthnContextDeclRef'), pyxb.binding.datatypes.anyURI)
Namespace.addCategoryObject('elementBinding', AuthnContextDeclRef.name().localName(), AuthnContextDeclRef)

AuthnContext = pyxb.binding.basis.element(pyxb.namespace.ExpandedName(Namespace, u'AuthnContext'), AuthnContextType)
Namespace.addCategoryObject('elementBinding', AuthnContext.name().localName(), AuthnContext)

Attribute = pyxb.binding.basis.element(pyxb.namespace.ExpandedName(Namespace, u'Attribute'), AttributeType)
Namespace.addCategoryObject('elementBinding', Attribute.name().localName(), Attribute)

Evidence = pyxb.binding.basis.element(pyxb.namespace.ExpandedName(Namespace, u'Evidence'), EvidenceType)
Namespace.addCategoryObject('elementBinding', Evidence.name().localName(), Evidence)

AuthzDecisionStatement = pyxb.binding.basis.element(pyxb.namespace.ExpandedName(Namespace, u'AuthzDecisionStatement'), AuthzDecisionStatementType)
Namespace.addCategoryObject('elementBinding', AuthzDecisionStatement.name().localName(), AuthzDecisionStatement)

AuthnStatement = pyxb.binding.basis.element(pyxb.namespace.ExpandedName(Namespace, u'AuthnStatement'), AuthnStatementType)
Namespace.addCategoryObject('elementBinding', AuthnStatement.name().localName(), AuthnStatement)

SubjectConfirmation = pyxb.binding.basis.element(pyxb.namespace.ExpandedName(Namespace, u'SubjectConfirmation'), SubjectConfirmationType)
Namespace.addCategoryObject('elementBinding', SubjectConfirmation.name().localName(), SubjectConfirmation)

Action = pyxb.binding.basis.element(pyxb.namespace.ExpandedName(Namespace, u'Action'), ActionType)
Namespace.addCategoryObject('elementBinding', Action.name().localName(), Action)

SubjectLocality = pyxb.binding.basis.element(pyxb.namespace.ExpandedName(Namespace, u'SubjectLocality'), SubjectLocalityType)
Namespace.addCategoryObject('elementBinding', SubjectLocality.name().localName(), SubjectLocality)

Statement = pyxb.binding.basis.element(pyxb.namespace.ExpandedName(Namespace, u'Statement'), StatementAbstractType)
Namespace.addCategoryObject('elementBinding', Statement.name().localName(), Statement)

NameID = pyxb.binding.basis.element(pyxb.namespace.ExpandedName(Namespace, u'NameID'), NameIDType)
Namespace.addCategoryObject('elementBinding', NameID.name().localName(), NameID)

Issuer = pyxb.binding.basis.element(pyxb.namespace.ExpandedName(Namespace, u'Issuer'), NameIDType)
Namespace.addCategoryObject('elementBinding', Issuer.name().localName(), Issuer)

Subject = pyxb.binding.basis.element(pyxb.namespace.ExpandedName(Namespace, u'Subject'), SubjectType)
Namespace.addCategoryObject('elementBinding', Subject.name().localName(), Subject)

AssertionIDRef = pyxb.binding.basis.element(pyxb.namespace.ExpandedName(Namespace, u'AssertionIDRef'), pyxb.binding.datatypes.NCName)
Namespace.addCategoryObject('elementBinding', AssertionIDRef.name().localName(), AssertionIDRef)

EncryptedAssertion = pyxb.binding.basis.element(pyxb.namespace.ExpandedName(Namespace, u'EncryptedAssertion'), EncryptedElementType)
Namespace.addCategoryObject('elementBinding', EncryptedAssertion.name().localName(), EncryptedAssertion)

AssertionURIRef = pyxb.binding.basis.element(pyxb.namespace.ExpandedName(Namespace, u'AssertionURIRef'), pyxb.binding.datatypes.anyURI)
Namespace.addCategoryObject('elementBinding', AssertionURIRef.name().localName(), AssertionURIRef)

EncryptedAttribute = pyxb.binding.basis.element(pyxb.namespace.ExpandedName(Namespace, u'EncryptedAttribute'), EncryptedElementType)
Namespace.addCategoryObject('elementBinding', EncryptedAttribute.name().localName(), EncryptedAttribute)

AttributeStatement = pyxb.binding.basis.element(pyxb.namespace.ExpandedName(Namespace, u'AttributeStatement'), AttributeStatementType)
Namespace.addCategoryObject('elementBinding', AttributeStatement.name().localName(), AttributeStatement)

ProxyRestriction = pyxb.binding.basis.element(pyxb.namespace.ExpandedName(Namespace, u'ProxyRestriction'), ProxyRestrictionType)
Namespace.addCategoryObject('elementBinding', ProxyRestriction.name().localName(), ProxyRestriction)

OneTimeUse = pyxb.binding.basis.element(pyxb.namespace.ExpandedName(Namespace, u'OneTimeUse'), OneTimeUseType)
Namespace.addCategoryObject('elementBinding', OneTimeUse.name().localName(), OneTimeUse)

Conditions = pyxb.binding.basis.element(pyxb.namespace.ExpandedName(Namespace, u'Conditions'), ConditionsType)
Namespace.addCategoryObject('elementBinding', Conditions.name().localName(), Conditions)

EncryptedID = pyxb.binding.basis.element(pyxb.namespace.ExpandedName(Namespace, u'EncryptedID'), EncryptedElementType)
Namespace.addCategoryObject('elementBinding', EncryptedID.name().localName(), EncryptedID)

Audience = pyxb.binding.basis.element(pyxb.namespace.ExpandedName(Namespace, u'Audience'), pyxb.binding.datatypes.anyURI)
Namespace.addCategoryObject('elementBinding', Audience.name().localName(), Audience)

BaseID = pyxb.binding.basis.element(pyxb.namespace.ExpandedName(Namespace, u'BaseID'), BaseIDAbstractType)
Namespace.addCategoryObject('elementBinding', BaseID.name().localName(), BaseID)

AttributeValue = pyxb.binding.basis.element(pyxb.namespace.ExpandedName(Namespace, u'AttributeValue'), pyxb.binding.datatypes.anyType, nillable=pyxb.binding.datatypes.boolean(1))
Namespace.addCategoryObject('elementBinding', AttributeValue.name().localName(), AttributeValue)

Assertion = pyxb.binding.basis.element(pyxb.namespace.ExpandedName(Namespace, u'Assertion'), AssertionType)
Namespace.addCategoryObject('elementBinding', Assertion.name().localName(), Assertion)

Advice = pyxb.binding.basis.element(pyxb.namespace.ExpandedName(Namespace, u'Advice'), AdviceType)
Namespace.addCategoryObject('elementBinding', Advice.name().localName(), Advice)

SubjectConfirmationData = pyxb.binding.basis.element(pyxb.namespace.ExpandedName(Namespace, u'SubjectConfirmationData'), SubjectConfirmationDataType)
Namespace.addCategoryObject('elementBinding', SubjectConfirmationData.name().localName(), SubjectConfirmationData)

Condition = pyxb.binding.basis.element(pyxb.namespace.ExpandedName(Namespace, u'Condition'), ConditionAbstractType)
Namespace.addCategoryObject('elementBinding', Condition.name().localName(), Condition)

AuthenticatingAuthority = pyxb.binding.basis.element(pyxb.namespace.ExpandedName(Namespace, u'AuthenticatingAuthority'), pyxb.binding.datatypes.anyURI)
Namespace.addCategoryObject('elementBinding', AuthenticatingAuthority.name().localName(), AuthenticatingAuthority)



AudienceRestrictionType._AddElement(pyxb.binding.basis.element(pyxb.namespace.ExpandedName(Namespace, u'Audience'), pyxb.binding.datatypes.anyURI, scope=AudienceRestrictionType))
AudienceRestrictionType._GroupModel = pyxb.binding.content.GroupSequence(
    pyxb.binding.content.ParticleModel(AudienceRestrictionType._UseForTag(pyxb.namespace.ExpandedName(Namespace, u'Audience')), min_occurs=1, max_occurs=None)
    )
AudienceRestrictionType._ContentModel = pyxb.binding.content.ParticleModel(AudienceRestrictionType._GroupModel, min_occurs=1, max_occurs=1)



EncryptedElementType._AddElement(pyxb.binding.basis.element(pyxb.namespace.ExpandedName(pyxb.namespace.NamespaceForURI(u'http://www.w3.org/2001/04/xmlenc#'), u'EncryptedData'), pyxb.bundles.wssplat.xenc.EncryptedDataType, scope=EncryptedElementType))

EncryptedElementType._AddElement(pyxb.binding.basis.element(pyxb.namespace.ExpandedName(pyxb.namespace.NamespaceForURI(u'http://www.w3.org/2001/04/xmlenc#'), u'EncryptedKey'), pyxb.bundles.wssplat.xenc.EncryptedKeyType, scope=EncryptedElementType))
EncryptedElementType._GroupModel = pyxb.binding.content.GroupSequence(
    pyxb.binding.content.ParticleModel(EncryptedElementType._UseForTag(pyxb.namespace.ExpandedName(pyxb.namespace.NamespaceForURI(u'http://www.w3.org/2001/04/xmlenc#'), u'EncryptedData')), min_occurs=1, max_occurs=1),
    pyxb.binding.content.ParticleModel(EncryptedElementType._UseForTag(pyxb.namespace.ExpandedName(pyxb.namespace.NamespaceForURI(u'http://www.w3.org/2001/04/xmlenc#'), u'EncryptedKey')), min_occurs=0L, max_occurs=None)
    )
EncryptedElementType._ContentModel = pyxb.binding.content.ParticleModel(EncryptedElementType._GroupModel, min_occurs=1, max_occurs=1)



AuthnContextType._AddElement(pyxb.binding.basis.element(pyxb.namespace.ExpandedName(Namespace, u'AuthnContextDeclRef'), pyxb.binding.datatypes.anyURI, scope=AuthnContextType))

AuthnContextType._AddElement(pyxb.binding.basis.element(pyxb.namespace.ExpandedName(Namespace, u'AuthenticatingAuthority'), pyxb.binding.datatypes.anyURI, scope=AuthnContextType))

AuthnContextType._AddElement(pyxb.binding.basis.element(pyxb.namespace.ExpandedName(Namespace, u'AuthnContextDecl'), pyxb.binding.datatypes.anyType, scope=AuthnContextType))

AuthnContextType._AddElement(pyxb.binding.basis.element(pyxb.namespace.ExpandedName(Namespace, u'AuthnContextClassRef'), pyxb.binding.datatypes.anyURI, scope=AuthnContextType))
AuthnContextType._GroupModel_3 = pyxb.binding.content.GroupChoice(
    pyxb.binding.content.ParticleModel(AuthnContextType._UseForTag(pyxb.namespace.ExpandedName(Namespace, u'AuthnContextDecl')), min_occurs=1, max_occurs=1),
    pyxb.binding.content.ParticleModel(AuthnContextType._UseForTag(pyxb.namespace.ExpandedName(Namespace, u'AuthnContextDeclRef')), min_occurs=1, max_occurs=1)
    )
AuthnContextType._GroupModel_2 = pyxb.binding.content.GroupSequence(
    pyxb.binding.content.ParticleModel(AuthnContextType._UseForTag(pyxb.namespace.ExpandedName(Namespace, u'AuthnContextClassRef')), min_occurs=1, max_occurs=1),
    pyxb.binding.content.ParticleModel(AuthnContextType._GroupModel_3, min_occurs=0L, max_occurs=1)
    )
AuthnContextType._GroupModel_4 = pyxb.binding.content.GroupChoice(
    pyxb.binding.content.ParticleModel(AuthnContextType._UseForTag(pyxb.namespace.ExpandedName(Namespace, u'AuthnContextDecl')), min_occurs=1, max_occurs=1),
    pyxb.binding.content.ParticleModel(AuthnContextType._UseForTag(pyxb.namespace.ExpandedName(Namespace, u'AuthnContextDeclRef')), min_occurs=1, max_occurs=1)
    )
AuthnContextType._GroupModel_ = pyxb.binding.content.GroupChoice(
    pyxb.binding.content.ParticleModel(AuthnContextType._GroupModel_2, min_occurs=1, max_occurs=1),
    pyxb.binding.content.ParticleModel(AuthnContextType._GroupModel_4, min_occurs=1, max_occurs=1)
    )
AuthnContextType._GroupModel = pyxb.binding.content.GroupSequence(
    pyxb.binding.content.ParticleModel(AuthnContextType._GroupModel_, min_occurs=1, max_occurs=1),
    pyxb.binding.content.ParticleModel(AuthnContextType._UseForTag(pyxb.namespace.ExpandedName(Namespace, u'AuthenticatingAuthority')), min_occurs=0L, max_occurs=None)
    )
AuthnContextType._ContentModel = pyxb.binding.content.ParticleModel(AuthnContextType._GroupModel, min_occurs=1, max_occurs=1)



AttributeType._AddElement(pyxb.binding.basis.element(pyxb.namespace.ExpandedName(Namespace, u'AttributeValue'), pyxb.binding.datatypes.anyType, nillable=pyxb.binding.datatypes.boolean(1), scope=AttributeType))
AttributeType._GroupModel = pyxb.binding.content.GroupSequence(
    pyxb.binding.content.ParticleModel(AttributeType._UseForTag(pyxb.namespace.ExpandedName(Namespace, u'AttributeValue')), min_occurs=0L, max_occurs=None)
    )
AttributeType._ContentModel = pyxb.binding.content.ParticleModel(AttributeType._GroupModel, min_occurs=1, max_occurs=1)



EvidenceType._AddElement(pyxb.binding.basis.element(pyxb.namespace.ExpandedName(Namespace, u'Assertion'), AssertionType, scope=EvidenceType))

EvidenceType._AddElement(pyxb.binding.basis.element(pyxb.namespace.ExpandedName(Namespace, u'AssertionURIRef'), pyxb.binding.datatypes.anyURI, scope=EvidenceType))

EvidenceType._AddElement(pyxb.binding.basis.element(pyxb.namespace.ExpandedName(Namespace, u'EncryptedAssertion'), EncryptedElementType, scope=EvidenceType))

EvidenceType._AddElement(pyxb.binding.basis.element(pyxb.namespace.ExpandedName(Namespace, u'AssertionIDRef'), pyxb.binding.datatypes.NCName, scope=EvidenceType))
EvidenceType._GroupModel = pyxb.binding.content.GroupChoice(
    pyxb.binding.content.ParticleModel(EvidenceType._UseForTag(pyxb.namespace.ExpandedName(Namespace, u'AssertionIDRef')), min_occurs=1, max_occurs=1),
    pyxb.binding.content.ParticleModel(EvidenceType._UseForTag(pyxb.namespace.ExpandedName(Namespace, u'AssertionURIRef')), min_occurs=1, max_occurs=1),
    pyxb.binding.content.ParticleModel(EvidenceType._UseForTag(pyxb.namespace.ExpandedName(Namespace, u'Assertion')), min_occurs=1, max_occurs=1),
    pyxb.binding.content.ParticleModel(EvidenceType._UseForTag(pyxb.namespace.ExpandedName(Namespace, u'EncryptedAssertion')), min_occurs=1, max_occurs=1)
    )
EvidenceType._ContentModel = pyxb.binding.content.ParticleModel(EvidenceType._GroupModel, min_occurs=1, max_occurs=None)



AuthnStatementType._AddElement(pyxb.binding.basis.element(pyxb.namespace.ExpandedName(Namespace, u'AuthnContext'), AuthnContextType, scope=AuthnStatementType))

AuthnStatementType._AddElement(pyxb.binding.basis.element(pyxb.namespace.ExpandedName(Namespace, u'SubjectLocality'), SubjectLocalityType, scope=AuthnStatementType))
AuthnStatementType._GroupModel = pyxb.binding.content.GroupSequence(
    pyxb.binding.content.ParticleModel(AuthnStatementType._UseForTag(pyxb.namespace.ExpandedName(Namespace, u'SubjectLocality')), min_occurs=0L, max_occurs=1),
    pyxb.binding.content.ParticleModel(AuthnStatementType._UseForTag(pyxb.namespace.ExpandedName(Namespace, u'AuthnContext')), min_occurs=1, max_occurs=1)
    )
AuthnStatementType._ContentModel = pyxb.binding.content.ParticleModel(AuthnStatementType._GroupModel, min_occurs=1, max_occurs=1)



AuthzDecisionStatementType._AddElement(pyxb.binding.basis.element(pyxb.namespace.ExpandedName(Namespace, u'Evidence'), EvidenceType, scope=AuthzDecisionStatementType))

AuthzDecisionStatementType._AddElement(pyxb.binding.basis.element(pyxb.namespace.ExpandedName(Namespace, u'Action'), ActionType, scope=AuthzDecisionStatementType))
AuthzDecisionStatementType._GroupModel = pyxb.binding.content.GroupSequence(
    pyxb.binding.content.ParticleModel(AuthzDecisionStatementType._UseForTag(pyxb.namespace.ExpandedName(Namespace, u'Action')), min_occurs=1, max_occurs=None),
    pyxb.binding.content.ParticleModel(AuthzDecisionStatementType._UseForTag(pyxb.namespace.ExpandedName(Namespace, u'Evidence')), min_occurs=0L, max_occurs=1)
    )
AuthzDecisionStatementType._ContentModel = pyxb.binding.content.ParticleModel(AuthzDecisionStatementType._GroupModel, min_occurs=1, max_occurs=1)



SubjectType._AddElement(pyxb.binding.basis.element(pyxb.namespace.ExpandedName(Namespace, u'NameID'), NameIDType, scope=SubjectType))

SubjectType._AddElement(pyxb.binding.basis.element(pyxb.namespace.ExpandedName(Namespace, u'SubjectConfirmation'), SubjectConfirmationType, scope=SubjectType))

SubjectType._AddElement(pyxb.binding.basis.element(pyxb.namespace.ExpandedName(Namespace, u'EncryptedID'), EncryptedElementType, scope=SubjectType))

SubjectType._AddElement(pyxb.binding.basis.element(pyxb.namespace.ExpandedName(Namespace, u'BaseID'), BaseIDAbstractType, scope=SubjectType))
SubjectType._GroupModel_2 = pyxb.binding.content.GroupChoice(
    pyxb.binding.content.ParticleModel(SubjectType._UseForTag(pyxb.namespace.ExpandedName(Namespace, u'BaseID')), min_occurs=1, max_occurs=1),
    pyxb.binding.content.ParticleModel(SubjectType._UseForTag(pyxb.namespace.ExpandedName(Namespace, u'NameID')), min_occurs=1, max_occurs=1),
    pyxb.binding.content.ParticleModel(SubjectType._UseForTag(pyxb.namespace.ExpandedName(Namespace, u'EncryptedID')), min_occurs=1, max_occurs=1)
    )
SubjectType._GroupModel_ = pyxb.binding.content.GroupSequence(
    pyxb.binding.content.ParticleModel(SubjectType._GroupModel_2, min_occurs=1, max_occurs=1),
    pyxb.binding.content.ParticleModel(SubjectType._UseForTag(pyxb.namespace.ExpandedName(Namespace, u'SubjectConfirmation')), min_occurs=0L, max_occurs=None)
    )
SubjectType._GroupModel = pyxb.binding.content.GroupChoice(
    pyxb.binding.content.ParticleModel(SubjectType._GroupModel_, min_occurs=1, max_occurs=1),
    pyxb.binding.content.ParticleModel(SubjectType._UseForTag(pyxb.namespace.ExpandedName(Namespace, u'SubjectConfirmation')), min_occurs=1, max_occurs=None)
    )
SubjectType._ContentModel = pyxb.binding.content.ParticleModel(SubjectType._GroupModel, min_occurs=1, max_occurs=1)



SubjectConfirmationType._AddElement(pyxb.binding.basis.element(pyxb.namespace.ExpandedName(Namespace, u'BaseID'), BaseIDAbstractType, scope=SubjectConfirmationType))

SubjectConfirmationType._AddElement(pyxb.binding.basis.element(pyxb.namespace.ExpandedName(Namespace, u'EncryptedID'), EncryptedElementType, scope=SubjectConfirmationType))

SubjectConfirmationType._AddElement(pyxb.binding.basis.element(pyxb.namespace.ExpandedName(Namespace, u'SubjectConfirmationData'), SubjectConfirmationDataType, scope=SubjectConfirmationType))

SubjectConfirmationType._AddElement(pyxb.binding.basis.element(pyxb.namespace.ExpandedName(Namespace, u'NameID'), NameIDType, scope=SubjectConfirmationType))
SubjectConfirmationType._GroupModel_ = pyxb.binding.content.GroupChoice(
    pyxb.binding.content.ParticleModel(SubjectConfirmationType._UseForTag(pyxb.namespace.ExpandedName(Namespace, u'BaseID')), min_occurs=1, max_occurs=1),
    pyxb.binding.content.ParticleModel(SubjectConfirmationType._UseForTag(pyxb.namespace.ExpandedName(Namespace, u'NameID')), min_occurs=1, max_occurs=1),
    pyxb.binding.content.ParticleModel(SubjectConfirmationType._UseForTag(pyxb.namespace.ExpandedName(Namespace, u'EncryptedID')), min_occurs=1, max_occurs=1)
    )
SubjectConfirmationType._GroupModel = pyxb.binding.content.GroupSequence(
    pyxb.binding.content.ParticleModel(SubjectConfirmationType._GroupModel_, min_occurs=0L, max_occurs=1),
    pyxb.binding.content.ParticleModel(SubjectConfirmationType._UseForTag(pyxb.namespace.ExpandedName(Namespace, u'SubjectConfirmationData')), min_occurs=0L, max_occurs=1)
    )
SubjectConfirmationType._ContentModel = pyxb.binding.content.ParticleModel(SubjectConfirmationType._GroupModel, min_occurs=1, max_occurs=1)



AssertionType._AddElement(pyxb.binding.basis.element(pyxb.namespace.ExpandedName(Namespace, u'Issuer'), NameIDType, scope=AssertionType))

AssertionType._AddElement(pyxb.binding.basis.element(pyxb.namespace.ExpandedName(pyxb.namespace.NamespaceForURI(u'http://www.w3.org/2000/09/xmldsig#'), u'Signature'), pyxb.bundles.wssplat.ds.SignatureType, scope=AssertionType))

AssertionType._AddElement(pyxb.binding.basis.element(pyxb.namespace.ExpandedName(Namespace, u'Conditions'), ConditionsType, scope=AssertionType))

AssertionType._AddElement(pyxb.binding.basis.element(pyxb.namespace.ExpandedName(Namespace, u'Statement'), StatementAbstractType, scope=AssertionType))

AssertionType._AddElement(pyxb.binding.basis.element(pyxb.namespace.ExpandedName(Namespace, u'AttributeStatement'), AttributeStatementType, scope=AssertionType))

AssertionType._AddElement(pyxb.binding.basis.element(pyxb.namespace.ExpandedName(Namespace, u'Advice'), AdviceType, scope=AssertionType))

AssertionType._AddElement(pyxb.binding.basis.element(pyxb.namespace.ExpandedName(Namespace, u'AuthnStatement'), AuthnStatementType, scope=AssertionType))

AssertionType._AddElement(pyxb.binding.basis.element(pyxb.namespace.ExpandedName(Namespace, u'Subject'), SubjectType, scope=AssertionType))

AssertionType._AddElement(pyxb.binding.basis.element(pyxb.namespace.ExpandedName(Namespace, u'AuthzDecisionStatement'), AuthzDecisionStatementType, scope=AssertionType))
AssertionType._GroupModel_ = pyxb.binding.content.GroupChoice(
    pyxb.binding.content.ParticleModel(AssertionType._UseForTag(pyxb.namespace.ExpandedName(Namespace, u'Statement')), min_occurs=1, max_occurs=1),
    pyxb.binding.content.ParticleModel(AssertionType._UseForTag(pyxb.namespace.ExpandedName(Namespace, u'AuthnStatement')), min_occurs=1, max_occurs=1),
    pyxb.binding.content.ParticleModel(AssertionType._UseForTag(pyxb.namespace.ExpandedName(Namespace, u'AuthzDecisionStatement')), min_occurs=1, max_occurs=1),
    pyxb.binding.content.ParticleModel(AssertionType._UseForTag(pyxb.namespace.ExpandedName(Namespace, u'AttributeStatement')), min_occurs=1, max_occurs=1)
    )
AssertionType._GroupModel = pyxb.binding.content.GroupSequence(
    pyxb.binding.content.ParticleModel(AssertionType._UseForTag(pyxb.namespace.ExpandedName(Namespace, u'Issuer')), min_occurs=1, max_occurs=1),
    pyxb.binding.content.ParticleModel(AssertionType._UseForTag(pyxb.namespace.ExpandedName(pyxb.namespace.NamespaceForURI(u'http://www.w3.org/2000/09/xmldsig#'), u'Signature')), min_occurs=0L, max_occurs=1),
    pyxb.binding.content.ParticleModel(AssertionType._UseForTag(pyxb.namespace.ExpandedName(Namespace, u'Subject')), min_occurs=0L, max_occurs=1),
    pyxb.binding.content.ParticleModel(AssertionType._UseForTag(pyxb.namespace.ExpandedName(Namespace, u'Conditions')), min_occurs=0L, max_occurs=1),
    pyxb.binding.content.ParticleModel(AssertionType._UseForTag(pyxb.namespace.ExpandedName(Namespace, u'Advice')), min_occurs=0L, max_occurs=1),
    pyxb.binding.content.ParticleModel(AssertionType._GroupModel_, min_occurs=0L, max_occurs=None)
    )
AssertionType._ContentModel = pyxb.binding.content.ParticleModel(AssertionType._GroupModel, min_occurs=1, max_occurs=1)


SubjectConfirmationDataType._GroupModel = pyxb.binding.content.GroupSequence(
    pyxb.binding.content.ParticleModel(pyxb.binding.content.Wildcard(process_contents=pyxb.binding.content.Wildcard.PC_lax, namespace_constraint=pyxb.binding.content.Wildcard.NC_any), min_occurs=0L, max_occurs=None)
    )
SubjectConfirmationDataType._ContentModel = pyxb.binding.content.ParticleModel(SubjectConfirmationDataType._GroupModel, min_occurs=1, max_occurs=1)



ConditionsType._AddElement(pyxb.binding.basis.element(pyxb.namespace.ExpandedName(Namespace, u'ProxyRestriction'), ProxyRestrictionType, scope=ConditionsType))

ConditionsType._AddElement(pyxb.binding.basis.element(pyxb.namespace.ExpandedName(Namespace, u'OneTimeUse'), OneTimeUseType, scope=ConditionsType))

ConditionsType._AddElement(pyxb.binding.basis.element(pyxb.namespace.ExpandedName(Namespace, u'AudienceRestriction'), AudienceRestrictionType, scope=ConditionsType))

ConditionsType._AddElement(pyxb.binding.basis.element(pyxb.namespace.ExpandedName(Namespace, u'Condition'), ConditionAbstractType, scope=ConditionsType))
ConditionsType._GroupModel = pyxb.binding.content.GroupChoice(
    pyxb.binding.content.ParticleModel(ConditionsType._UseForTag(pyxb.namespace.ExpandedName(Namespace, u'Condition')), min_occurs=1, max_occurs=1),
    pyxb.binding.content.ParticleModel(ConditionsType._UseForTag(pyxb.namespace.ExpandedName(Namespace, u'AudienceRestriction')), min_occurs=1, max_occurs=1),
    pyxb.binding.content.ParticleModel(ConditionsType._UseForTag(pyxb.namespace.ExpandedName(Namespace, u'OneTimeUse')), min_occurs=1, max_occurs=1),
    pyxb.binding.content.ParticleModel(ConditionsType._UseForTag(pyxb.namespace.ExpandedName(Namespace, u'ProxyRestriction')), min_occurs=1, max_occurs=1)
    )
ConditionsType._ContentModel = pyxb.binding.content.ParticleModel(ConditionsType._GroupModel, min_occurs=0L, max_occurs=None)



ProxyRestrictionType._AddElement(pyxb.binding.basis.element(pyxb.namespace.ExpandedName(Namespace, u'Audience'), pyxb.binding.datatypes.anyURI, scope=ProxyRestrictionType))
ProxyRestrictionType._GroupModel = pyxb.binding.content.GroupSequence(
    pyxb.binding.content.ParticleModel(ProxyRestrictionType._UseForTag(pyxb.namespace.ExpandedName(Namespace, u'Audience')), min_occurs=0L, max_occurs=None)
    )
ProxyRestrictionType._ContentModel = pyxb.binding.content.ParticleModel(ProxyRestrictionType._GroupModel, min_occurs=1, max_occurs=1)



KeyInfoConfirmationDataType._AddElement(pyxb.binding.basis.element(pyxb.namespace.ExpandedName(pyxb.namespace.NamespaceForURI(u'http://www.w3.org/2000/09/xmldsig#'), u'KeyInfo'), pyxb.bundles.wssplat.ds.KeyInfoType, scope=KeyInfoConfirmationDataType))
KeyInfoConfirmationDataType._GroupModel = pyxb.binding.content.GroupSequence(
    pyxb.binding.content.ParticleModel(KeyInfoConfirmationDataType._UseForTag(pyxb.namespace.ExpandedName(pyxb.namespace.NamespaceForURI(u'http://www.w3.org/2000/09/xmldsig#'), u'KeyInfo')), min_occurs=1, max_occurs=None)
    )
KeyInfoConfirmationDataType._ContentModel = pyxb.binding.content.ParticleModel(KeyInfoConfirmationDataType._GroupModel, min_occurs=1, max_occurs=1)



AttributeStatementType._AddElement(pyxb.binding.basis.element(pyxb.namespace.ExpandedName(Namespace, u'EncryptedAttribute'), EncryptedElementType, scope=AttributeStatementType))

AttributeStatementType._AddElement(pyxb.binding.basis.element(pyxb.namespace.ExpandedName(Namespace, u'Attribute'), AttributeType, scope=AttributeStatementType))
AttributeStatementType._GroupModel = pyxb.binding.content.GroupChoice(
    pyxb.binding.content.ParticleModel(AttributeStatementType._UseForTag(pyxb.namespace.ExpandedName(Namespace, u'Attribute')), min_occurs=1, max_occurs=1),
    pyxb.binding.content.ParticleModel(AttributeStatementType._UseForTag(pyxb.namespace.ExpandedName(Namespace, u'EncryptedAttribute')), min_occurs=1, max_occurs=1)
    )
AttributeStatementType._ContentModel = pyxb.binding.content.ParticleModel(AttributeStatementType._GroupModel, min_occurs=1, max_occurs=None)



AdviceType._AddElement(pyxb.binding.basis.element(pyxb.namespace.ExpandedName(Namespace, u'AssertionURIRef'), pyxb.binding.datatypes.anyURI, scope=AdviceType))

AdviceType._AddElement(pyxb.binding.basis.element(pyxb.namespace.ExpandedName(Namespace, u'AssertionIDRef'), pyxb.binding.datatypes.NCName, scope=AdviceType))

AdviceType._AddElement(pyxb.binding.basis.element(pyxb.namespace.ExpandedName(Namespace, u'EncryptedAssertion'), EncryptedElementType, scope=AdviceType))

AdviceType._AddElement(pyxb.binding.basis.element(pyxb.namespace.ExpandedName(Namespace, u'Assertion'), AssertionType, scope=AdviceType))
AdviceType._GroupModel = pyxb.binding.content.GroupChoice(
    pyxb.binding.content.ParticleModel(AdviceType._UseForTag(pyxb.namespace.ExpandedName(Namespace, u'AssertionIDRef')), min_occurs=1, max_occurs=1),
    pyxb.binding.content.ParticleModel(AdviceType._UseForTag(pyxb.namespace.ExpandedName(Namespace, u'AssertionURIRef')), min_occurs=1, max_occurs=1),
    pyxb.binding.content.ParticleModel(AdviceType._UseForTag(pyxb.namespace.ExpandedName(Namespace, u'Assertion')), min_occurs=1, max_occurs=1),
    pyxb.binding.content.ParticleModel(AdviceType._UseForTag(pyxb.namespace.ExpandedName(Namespace, u'EncryptedAssertion')), min_occurs=1, max_occurs=1),
    pyxb.binding.content.ParticleModel(pyxb.binding.content.Wildcard(process_contents=pyxb.binding.content.Wildcard.PC_lax, namespace_constraint=(pyxb.binding.content.Wildcard.NC_not, u'urn:oasis:names:tc:SAML:2.0:assertion')), min_occurs=1, max_occurs=1)
    )
AdviceType._ContentModel = pyxb.binding.content.ParticleModel(AdviceType._GroupModel, min_occurs=0L, max_occurs=None)
