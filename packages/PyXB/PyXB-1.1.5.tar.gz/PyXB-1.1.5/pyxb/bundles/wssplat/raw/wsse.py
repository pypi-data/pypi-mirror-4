# ./pyxb/bundles/wssplat/raw/wsse.py
# -*- coding: utf-8 -*-
# PyXB bindings for NM:533be3d902dc7f54d5027ddd5917639d584e9d38
# Generated 2012-11-01 15:13:36.615182 by PyXB version 1.1.5
# Namespace http://docs.oasis-open.org/wss/2004/01/oasis-200401-wss-wssecurity-secext-1.0.xsd

import pyxb
import pyxb.binding
import pyxb.binding.saxer
import StringIO
import pyxb.utils.utility
import pyxb.utils.domutils
import sys

# Unique identifier for bindings created at the same time
_GenerationUID = pyxb.utils.utility.UniqueIdentifier('urn:uuid:9e4cf2b4-2460-11e2-9ce5-c8600024e903')

# Import bindings for namespaces imported into schema
import pyxb.binding.datatypes

Namespace = pyxb.namespace.NamespaceForURI(u'http://docs.oasis-open.org/wss/2004/01/oasis-200401-wss-wssecurity-secext-1.0.xsd', create_if_missing=True)
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


# List simple type: {http://docs.oasis-open.org/wss/2004/01/oasis-200401-wss-wssecurity-secext-1.0.xsd}tUsage
# superclasses pyxb.binding.datatypes.anySimpleType
class tUsage (pyxb.binding.basis.STD_list):

    """Typedef to allow a list of usages (as URIs)."""

    _ExpandedName = pyxb.namespace.ExpandedName(Namespace, u'tUsage')
    _DefinitionLocation = pyxb.utils.utility.Location('/tmp/pyxbdist.RHB65sy/PyXB-1.1.5/pyxb/bundles/wssplat/schemas/wsse.xsd', 76, 1)
    _Documentation = u'Typedef to allow a list of usages (as URIs).'

    _ItemType = pyxb.binding.datatypes.anyURI
tUsage._InitializeFacetMap()
Namespace.addCategoryObject('typeBinding', u'tUsage', tUsage)

# Atomic simple type: {http://docs.oasis-open.org/wss/2004/01/oasis-200401-wss-wssecurity-secext-1.0.xsd}FaultcodeEnum
class FaultcodeEnum (pyxb.binding.datatypes.QName, pyxb.binding.basis.enumeration_mixin):

    """An atomic simple type."""

    _ExpandedName = pyxb.namespace.ExpandedName(Namespace, u'FaultcodeEnum')
    _DefinitionLocation = pyxb.utils.utility.Location('/tmp/pyxbdist.RHB65sy/PyXB-1.1.5/pyxb/bundles/wssplat/schemas/wsse.xsd', 184, 1)
    _Documentation = None
FaultcodeEnum._CF_enumeration = pyxb.binding.facets.CF_enumeration(value_datatype=FaultcodeEnum, enum_prefix=None)
FaultcodeEnum.wsseUnsupportedSecurityToken = FaultcodeEnum._CF_enumeration.addEnumeration(unicode_value=u'wsse:UnsupportedSecurityToken', tag=u'wsseUnsupportedSecurityToken')
FaultcodeEnum.wsseUnsupportedAlgorithm = FaultcodeEnum._CF_enumeration.addEnumeration(unicode_value=u'wsse:UnsupportedAlgorithm', tag=u'wsseUnsupportedAlgorithm')
FaultcodeEnum.wsseInvalidSecurity = FaultcodeEnum._CF_enumeration.addEnumeration(unicode_value=u'wsse:InvalidSecurity', tag=u'wsseInvalidSecurity')
FaultcodeEnum.wsseInvalidSecurityToken = FaultcodeEnum._CF_enumeration.addEnumeration(unicode_value=u'wsse:InvalidSecurityToken', tag=u'wsseInvalidSecurityToken')
FaultcodeEnum.wsseFailedAuthentication = FaultcodeEnum._CF_enumeration.addEnumeration(unicode_value=u'wsse:FailedAuthentication', tag=u'wsseFailedAuthentication')
FaultcodeEnum.wsseFailedCheck = FaultcodeEnum._CF_enumeration.addEnumeration(unicode_value=u'wsse:FailedCheck', tag=u'wsseFailedCheck')
FaultcodeEnum.wsseSecurityTokenUnavailable = FaultcodeEnum._CF_enumeration.addEnumeration(unicode_value=u'wsse:SecurityTokenUnavailable', tag=u'wsseSecurityTokenUnavailable')
FaultcodeEnum._InitializeFacetMap(FaultcodeEnum._CF_enumeration)
Namespace.addCategoryObject('typeBinding', u'FaultcodeEnum', FaultcodeEnum)

# Complex type {http://docs.oasis-open.org/wss/2004/01/oasis-200401-wss-wssecurity-secext-1.0.xsd}AttributedString with content type SIMPLE
class AttributedString (pyxb.binding.basis.complexTypeDefinition):
    _TypeDefinition = pyxb.binding.datatypes.string
    _ContentTypeTag = pyxb.binding.basis.complexTypeDefinition._CT_SIMPLE
    _Abstract = False
    _ExpandedName = pyxb.namespace.ExpandedName(Namespace, u'AttributedString')
    _DefinitionLocation = pyxb.utils.utility.Location('/tmp/pyxbdist.RHB65sy/PyXB-1.1.5/pyxb/bundles/wssplat/schemas/wsse.xsd', 14, 1)
    # Base type is pyxb.binding.datatypes.string
    
    # Attribute {http://docs.oasis-open.org/wss/2004/01/oasis-200401-wss-wssecurity-utility-1.0.xsd}Id uses Python identifier Id
    __Id = pyxb.binding.content.AttributeUse(pyxb.namespace.ExpandedName(pyxb.namespace.NamespaceForURI(u'http://docs.oasis-open.org/wss/2004/01/oasis-200401-wss-wssecurity-utility-1.0.xsd'), u'Id'), 'Id', '__httpdocs_oasis_open_orgwss200401oasis_200401_wss_wssecurity_secext_1_0_xsd_AttributedString_httpdocs_oasis_open_orgwss200401oasis_200401_wss_wssecurity_utility_1_0_xsdId', pyxb.binding.datatypes.ID)
    __Id._DeclarationLocation = pyxb.utils.utility.Location('/tmp/pyxbdist.RHB65sy/PyXB-1.1.5/pyxb/bundles/wssplat/schemas/wsu.xsd', 28, 1)
    __Id._UseLocation = pyxb.utils.utility.Location('/tmp/pyxbdist.RHB65sy/PyXB-1.1.5/pyxb/bundles/wssplat/schemas/wsse.xsd', 20, 4)
    
    Id = property(__Id.value, __Id.set, None, u'\nThis global attribute supports annotating arbitrary elements with an ID.\n          ')

    _AttributeWildcard = pyxb.binding.content.Wildcard(process_contents=pyxb.binding.content.Wildcard.PC_lax, namespace_constraint=(pyxb.binding.content.Wildcard.NC_not, u'http://docs.oasis-open.org/wss/2004/01/oasis-200401-wss-wssecurity-secext-1.0.xsd'))

    _ElementMap = {
        
    }
    _AttributeMap = {
        __Id.name() : __Id
    }
Namespace.addCategoryObject('typeBinding', u'AttributedString', AttributedString)


# Complex type {http://docs.oasis-open.org/wss/2004/01/oasis-200401-wss-wssecurity-secext-1.0.xsd}EncodedString with content type SIMPLE
class EncodedString (AttributedString):
    _TypeDefinition = pyxb.binding.datatypes.string
    _ContentTypeTag = pyxb.binding.basis.complexTypeDefinition._CT_SIMPLE
    _Abstract = False
    _ExpandedName = pyxb.namespace.ExpandedName(Namespace, u'EncodedString')
    _DefinitionLocation = pyxb.utils.utility.Location('/tmp/pyxbdist.RHB65sy/PyXB-1.1.5/pyxb/bundles/wssplat/schemas/wsse.xsd', 35, 1)
    # Base type is AttributedString
    
    # Attribute EncodingType uses Python identifier EncodingType
    __EncodingType = pyxb.binding.content.AttributeUse(pyxb.namespace.ExpandedName(None, u'EncodingType'), 'EncodingType', '__httpdocs_oasis_open_orgwss200401oasis_200401_wss_wssecurity_secext_1_0_xsd_EncodedString_EncodingType', pyxb.binding.datatypes.anyURI)
    __EncodingType._DeclarationLocation = pyxb.utils.utility.Location('/tmp/pyxbdist.RHB65sy/PyXB-1.1.5/pyxb/bundles/wssplat/schemas/wsse.xsd', 41, 4)
    __EncodingType._UseLocation = pyxb.utils.utility.Location('/tmp/pyxbdist.RHB65sy/PyXB-1.1.5/pyxb/bundles/wssplat/schemas/wsse.xsd', 41, 4)
    
    EncodingType = property(__EncodingType.value, __EncodingType.set, None, None)

    
    # Attribute Id inherited from {http://docs.oasis-open.org/wss/2004/01/oasis-200401-wss-wssecurity-secext-1.0.xsd}AttributedString
    _AttributeWildcard = pyxb.binding.content.Wildcard(process_contents=pyxb.binding.content.Wildcard.PC_lax, namespace_constraint=(pyxb.binding.content.Wildcard.NC_not, u'http://docs.oasis-open.org/wss/2004/01/oasis-200401-wss-wssecurity-secext-1.0.xsd'))

    _ElementMap = AttributedString._ElementMap.copy()
    _ElementMap.update({
        
    })
    _AttributeMap = AttributedString._AttributeMap.copy()
    _AttributeMap.update({
        __EncodingType.name() : __EncodingType
    })
Namespace.addCategoryObject('typeBinding', u'EncodedString', EncodedString)


# Complex type {http://docs.oasis-open.org/wss/2004/01/oasis-200401-wss-wssecurity-secext-1.0.xsd}KeyIdentifierType with content type SIMPLE
class KeyIdentifierType (EncodedString):
    _TypeDefinition = pyxb.binding.datatypes.string
    _ContentTypeTag = pyxb.binding.basis.complexTypeDefinition._CT_SIMPLE
    _Abstract = False
    _ExpandedName = pyxb.namespace.ExpandedName(Namespace, u'KeyIdentifierType')
    _DefinitionLocation = pyxb.utils.utility.Location('/tmp/pyxbdist.RHB65sy/PyXB-1.1.5/pyxb/bundles/wssplat/schemas/wsse.xsd', 66, 1)
    # Base type is EncodedString
    
    # Attribute EncodingType inherited from {http://docs.oasis-open.org/wss/2004/01/oasis-200401-wss-wssecurity-secext-1.0.xsd}EncodedString
    
    # Attribute ValueType uses Python identifier ValueType
    __ValueType = pyxb.binding.content.AttributeUse(pyxb.namespace.ExpandedName(None, u'ValueType'), 'ValueType', '__httpdocs_oasis_open_orgwss200401oasis_200401_wss_wssecurity_secext_1_0_xsd_KeyIdentifierType_ValueType', pyxb.binding.datatypes.anyURI)
    __ValueType._DeclarationLocation = pyxb.utils.utility.Location('/tmp/pyxbdist.RHB65sy/PyXB-1.1.5/pyxb/bundles/wssplat/schemas/wsse.xsd', 72, 4)
    __ValueType._UseLocation = pyxb.utils.utility.Location('/tmp/pyxbdist.RHB65sy/PyXB-1.1.5/pyxb/bundles/wssplat/schemas/wsse.xsd', 72, 4)
    
    ValueType = property(__ValueType.value, __ValueType.set, None, None)

    
    # Attribute Id inherited from {http://docs.oasis-open.org/wss/2004/01/oasis-200401-wss-wssecurity-secext-1.0.xsd}AttributedString
    _AttributeWildcard = pyxb.binding.content.Wildcard(process_contents=pyxb.binding.content.Wildcard.PC_lax, namespace_constraint=(pyxb.binding.content.Wildcard.NC_not, u'http://docs.oasis-open.org/wss/2004/01/oasis-200401-wss-wssecurity-secext-1.0.xsd'))

    _ElementMap = EncodedString._ElementMap.copy()
    _ElementMap.update({
        
    })
    _AttributeMap = EncodedString._AttributeMap.copy()
    _AttributeMap.update({
        __ValueType.name() : __ValueType
    })
Namespace.addCategoryObject('typeBinding', u'KeyIdentifierType', KeyIdentifierType)


# Complex type {http://docs.oasis-open.org/wss/2004/01/oasis-200401-wss-wssecurity-secext-1.0.xsd}PasswordString with content type SIMPLE
class PasswordString (AttributedString):
    _TypeDefinition = pyxb.binding.datatypes.string
    _ContentTypeTag = pyxb.binding.basis.complexTypeDefinition._CT_SIMPLE
    _Abstract = False
    _ExpandedName = pyxb.namespace.ExpandedName(Namespace, u'PasswordString')
    _DefinitionLocation = pyxb.utils.utility.Location('/tmp/pyxbdist.RHB65sy/PyXB-1.1.5/pyxb/bundles/wssplat/schemas/wsse.xsd', 25, 1)
    # Base type is AttributedString
    
    # Attribute Type uses Python identifier Type
    __Type = pyxb.binding.content.AttributeUse(pyxb.namespace.ExpandedName(None, u'Type'), 'Type', '__httpdocs_oasis_open_orgwss200401oasis_200401_wss_wssecurity_secext_1_0_xsd_PasswordString_Type', pyxb.binding.datatypes.anyURI)
    __Type._DeclarationLocation = pyxb.utils.utility.Location('/tmp/pyxbdist.RHB65sy/PyXB-1.1.5/pyxb/bundles/wssplat/schemas/wsse.xsd', 31, 4)
    __Type._UseLocation = pyxb.utils.utility.Location('/tmp/pyxbdist.RHB65sy/PyXB-1.1.5/pyxb/bundles/wssplat/schemas/wsse.xsd', 31, 4)
    
    Type = property(__Type.value, __Type.set, None, None)

    
    # Attribute Id inherited from {http://docs.oasis-open.org/wss/2004/01/oasis-200401-wss-wssecurity-secext-1.0.xsd}AttributedString
    _AttributeWildcard = pyxb.binding.content.Wildcard(process_contents=pyxb.binding.content.Wildcard.PC_lax, namespace_constraint=(pyxb.binding.content.Wildcard.NC_not, u'http://docs.oasis-open.org/wss/2004/01/oasis-200401-wss-wssecurity-secext-1.0.xsd'))

    _ElementMap = AttributedString._ElementMap.copy()
    _ElementMap.update({
        
    })
    _AttributeMap = AttributedString._AttributeMap.copy()
    _AttributeMap.update({
        __Type.name() : __Type
    })
Namespace.addCategoryObject('typeBinding', u'PasswordString', PasswordString)


# Complex type {http://docs.oasis-open.org/wss/2004/01/oasis-200401-wss-wssecurity-secext-1.0.xsd}SecurityTokenReferenceType with content type ELEMENT_ONLY
class SecurityTokenReferenceType (pyxb.binding.basis.complexTypeDefinition):
    _TypeDefinition = None
    _ContentTypeTag = pyxb.binding.basis.complexTypeDefinition._CT_ELEMENT_ONLY
    _Abstract = False
    _ExpandedName = pyxb.namespace.ExpandedName(Namespace, u'SecurityTokenReferenceType')
    _DefinitionLocation = pyxb.utils.utility.Location('/tmp/pyxbdist.RHB65sy/PyXB-1.1.5/pyxb/bundles/wssplat/schemas/wsse.xsd', 105, 1)
    # Base type is pyxb.binding.datatypes.anyType
    
    # Attribute {http://docs.oasis-open.org/wss/2004/01/oasis-200401-wss-wssecurity-utility-1.0.xsd}Id uses Python identifier Id
    __Id = pyxb.binding.content.AttributeUse(pyxb.namespace.ExpandedName(pyxb.namespace.NamespaceForURI(u'http://docs.oasis-open.org/wss/2004/01/oasis-200401-wss-wssecurity-utility-1.0.xsd'), u'Id'), 'Id', '__httpdocs_oasis_open_orgwss200401oasis_200401_wss_wssecurity_secext_1_0_xsd_SecurityTokenReferenceType_httpdocs_oasis_open_orgwss200401oasis_200401_wss_wssecurity_utility_1_0_xsdId', pyxb.binding.datatypes.ID)
    __Id._DeclarationLocation = pyxb.utils.utility.Location('/tmp/pyxbdist.RHB65sy/PyXB-1.1.5/pyxb/bundles/wssplat/schemas/wsu.xsd', 28, 1)
    __Id._UseLocation = pyxb.utils.utility.Location('/tmp/pyxbdist.RHB65sy/PyXB-1.1.5/pyxb/bundles/wssplat/schemas/wsse.xsd', 112, 2)
    
    Id = property(__Id.value, __Id.set, None, u'\nThis global attribute supports annotating arbitrary elements with an ID.\n          ')

    
    # Attribute {http://docs.oasis-open.org/wss/2004/01/oasis-200401-wss-wssecurity-secext-1.0.xsd}Usage uses Python identifier Usage
    __Usage = pyxb.binding.content.AttributeUse(pyxb.namespace.ExpandedName(Namespace, u'Usage'), 'Usage', '__httpdocs_oasis_open_orgwss200401oasis_200401_wss_wssecurity_secext_1_0_xsd_SecurityTokenReferenceType_httpdocs_oasis_open_orgwss200401oasis_200401_wss_wssecurity_secext_1_0_xsdUsage', tUsage)
    __Usage._DeclarationLocation = pyxb.utils.utility.Location('/tmp/pyxbdist.RHB65sy/PyXB-1.1.5/pyxb/bundles/wssplat/schemas/wsse.xsd', 82, 1)
    __Usage._UseLocation = pyxb.utils.utility.Location('/tmp/pyxbdist.RHB65sy/PyXB-1.1.5/pyxb/bundles/wssplat/schemas/wsse.xsd', 113, 2)
    
    Usage = property(__Usage.value, __Usage.set, None, u'This global attribute is used to indicate the usage of a referenced or indicated token within the containing context')

    _AttributeWildcard = pyxb.binding.content.Wildcard(process_contents=pyxb.binding.content.Wildcard.PC_lax, namespace_constraint=(pyxb.binding.content.Wildcard.NC_not, u'http://docs.oasis-open.org/wss/2004/01/oasis-200401-wss-wssecurity-secext-1.0.xsd'))
    _HasWildcardElement = True

    _ElementMap = {
        
    }
    _AttributeMap = {
        __Id.name() : __Id,
        __Usage.name() : __Usage
    }
Namespace.addCategoryObject('typeBinding', u'SecurityTokenReferenceType', SecurityTokenReferenceType)


# Complex type {http://docs.oasis-open.org/wss/2004/01/oasis-200401-wss-wssecurity-secext-1.0.xsd}EmbeddedType with content type ELEMENT_ONLY
class EmbeddedType (pyxb.binding.basis.complexTypeDefinition):
    _TypeDefinition = None
    _ContentTypeTag = pyxb.binding.basis.complexTypeDefinition._CT_ELEMENT_ONLY
    _Abstract = False
    _ExpandedName = pyxb.namespace.ExpandedName(Namespace, u'EmbeddedType')
    _DefinitionLocation = pyxb.utils.utility.Location('/tmp/pyxbdist.RHB65sy/PyXB-1.1.5/pyxb/bundles/wssplat/schemas/wsse.xsd', 95, 1)
    # Base type is pyxb.binding.datatypes.anyType
    
    # Attribute ValueType uses Python identifier ValueType
    __ValueType = pyxb.binding.content.AttributeUse(pyxb.namespace.ExpandedName(None, u'ValueType'), 'ValueType', '__httpdocs_oasis_open_orgwss200401oasis_200401_wss_wssecurity_secext_1_0_xsd_EmbeddedType_ValueType', pyxb.binding.datatypes.anyURI)
    __ValueType._DeclarationLocation = pyxb.utils.utility.Location('/tmp/pyxbdist.RHB65sy/PyXB-1.1.5/pyxb/bundles/wssplat/schemas/wsse.xsd', 102, 2)
    __ValueType._UseLocation = pyxb.utils.utility.Location('/tmp/pyxbdist.RHB65sy/PyXB-1.1.5/pyxb/bundles/wssplat/schemas/wsse.xsd', 102, 2)
    
    ValueType = property(__ValueType.value, __ValueType.set, None, None)

    _AttributeWildcard = pyxb.binding.content.Wildcard(process_contents=pyxb.binding.content.Wildcard.PC_lax, namespace_constraint=(pyxb.binding.content.Wildcard.NC_not, u'http://docs.oasis-open.org/wss/2004/01/oasis-200401-wss-wssecurity-secext-1.0.xsd'))
    _HasWildcardElement = True

    _ElementMap = {
        
    }
    _AttributeMap = {
        __ValueType.name() : __ValueType
    }
Namespace.addCategoryObject('typeBinding', u'EmbeddedType', EmbeddedType)


# Complex type {http://docs.oasis-open.org/wss/2004/01/oasis-200401-wss-wssecurity-secext-1.0.xsd}UsernameTokenType with content type ELEMENT_ONLY
class UsernameTokenType (pyxb.binding.basis.complexTypeDefinition):
    _TypeDefinition = None
    _ContentTypeTag = pyxb.binding.basis.complexTypeDefinition._CT_ELEMENT_ONLY
    _Abstract = False
    _ExpandedName = pyxb.namespace.ExpandedName(Namespace, u'UsernameTokenType')
    _DefinitionLocation = pyxb.utils.utility.Location('/tmp/pyxbdist.RHB65sy/PyXB-1.1.5/pyxb/bundles/wssplat/schemas/wsse.xsd', 45, 1)
    # Base type is pyxb.binding.datatypes.anyType
    
    # Element {http://docs.oasis-open.org/wss/2004/01/oasis-200401-wss-wssecurity-secext-1.0.xsd}Username uses Python identifier Username
    __Username = pyxb.binding.content.ElementUse(pyxb.namespace.ExpandedName(Namespace, u'Username'), 'Username', '__httpdocs_oasis_open_orgwss200401oasis_200401_wss_wssecurity_secext_1_0_xsd_UsernameTokenType_httpdocs_oasis_open_orgwss200401oasis_200401_wss_wssecurity_secext_1_0_xsdUsername', False)
    __Username._DeclarationLocation = pyxb.utils.utility.Location('/tmp/pyxbdist.RHB65sy/PyXB-1.1.5/pyxb/bundles/wssplat/schemas/wsse.xsd', 50, 3)
    __Username._UseLocation = pyxb.utils.utility.Location('/tmp/pyxbdist.RHB65sy/PyXB-1.1.5/pyxb/bundles/wssplat/schemas/wsse.xsd', 49, 2)

    
    Username = property(__Username.value, __Username.set, None, None)

    
    # Attribute {http://docs.oasis-open.org/wss/2004/01/oasis-200401-wss-wssecurity-utility-1.0.xsd}Id uses Python identifier Id
    __Id = pyxb.binding.content.AttributeUse(pyxb.namespace.ExpandedName(pyxb.namespace.NamespaceForURI(u'http://docs.oasis-open.org/wss/2004/01/oasis-200401-wss-wssecurity-utility-1.0.xsd'), u'Id'), 'Id', '__httpdocs_oasis_open_orgwss200401oasis_200401_wss_wssecurity_secext_1_0_xsd_UsernameTokenType_httpdocs_oasis_open_orgwss200401oasis_200401_wss_wssecurity_utility_1_0_xsdId', pyxb.binding.datatypes.ID)
    __Id._DeclarationLocation = pyxb.utils.utility.Location('/tmp/pyxbdist.RHB65sy/PyXB-1.1.5/pyxb/bundles/wssplat/schemas/wsu.xsd', 28, 1)
    __Id._UseLocation = pyxb.utils.utility.Location('/tmp/pyxbdist.RHB65sy/PyXB-1.1.5/pyxb/bundles/wssplat/schemas/wsse.xsd', 53, 2)
    
    Id = property(__Id.value, __Id.set, None, u'\nThis global attribute supports annotating arbitrary elements with an ID.\n          ')

    _AttributeWildcard = pyxb.binding.content.Wildcard(process_contents=pyxb.binding.content.Wildcard.PC_lax, namespace_constraint=(pyxb.binding.content.Wildcard.NC_not, u'http://docs.oasis-open.org/wss/2004/01/oasis-200401-wss-wssecurity-secext-1.0.xsd'))
    _HasWildcardElement = True

    _ElementMap = {
        __Username.name() : __Username
    }
    _AttributeMap = {
        __Id.name() : __Id
    }
Namespace.addCategoryObject('typeBinding', u'UsernameTokenType', UsernameTokenType)


# Complex type {http://docs.oasis-open.org/wss/2004/01/oasis-200401-wss-wssecurity-secext-1.0.xsd}SecurityHeaderType with content type ELEMENT_ONLY
class SecurityHeaderType (pyxb.binding.basis.complexTypeDefinition):
    _TypeDefinition = None
    _ContentTypeTag = pyxb.binding.basis.complexTypeDefinition._CT_ELEMENT_ONLY
    _Abstract = False
    _ExpandedName = pyxb.namespace.ExpandedName(Namespace, u'SecurityHeaderType')
    _DefinitionLocation = pyxb.utils.utility.Location('/tmp/pyxbdist.RHB65sy/PyXB-1.1.5/pyxb/bundles/wssplat/schemas/wsse.xsd', 116, 1)
    # Base type is pyxb.binding.datatypes.anyType
    _AttributeWildcard = pyxb.binding.content.Wildcard(process_contents=pyxb.binding.content.Wildcard.PC_lax, namespace_constraint=(pyxb.binding.content.Wildcard.NC_not, u'http://docs.oasis-open.org/wss/2004/01/oasis-200401-wss-wssecurity-secext-1.0.xsd'))
    _HasWildcardElement = True

    _ElementMap = {
        
    }
    _AttributeMap = {
        
    }
Namespace.addCategoryObject('typeBinding', u'SecurityHeaderType', SecurityHeaderType)


# Complex type {http://docs.oasis-open.org/wss/2004/01/oasis-200401-wss-wssecurity-secext-1.0.xsd}ReferenceType with content type EMPTY
class ReferenceType (pyxb.binding.basis.complexTypeDefinition):
    _TypeDefinition = None
    _ContentTypeTag = pyxb.binding.basis.complexTypeDefinition._CT_EMPTY
    _Abstract = False
    _ExpandedName = pyxb.namespace.ExpandedName(Namespace, u'ReferenceType')
    _DefinitionLocation = pyxb.utils.utility.Location('/tmp/pyxbdist.RHB65sy/PyXB-1.1.5/pyxb/bundles/wssplat/schemas/wsse.xsd', 87, 1)
    # Base type is pyxb.binding.datatypes.anyType
    
    # Attribute ValueType uses Python identifier ValueType
    __ValueType = pyxb.binding.content.AttributeUse(pyxb.namespace.ExpandedName(None, u'ValueType'), 'ValueType', '__httpdocs_oasis_open_orgwss200401oasis_200401_wss_wssecurity_secext_1_0_xsd_ReferenceType_ValueType', pyxb.binding.datatypes.anyURI)
    __ValueType._DeclarationLocation = pyxb.utils.utility.Location('/tmp/pyxbdist.RHB65sy/PyXB-1.1.5/pyxb/bundles/wssplat/schemas/wsse.xsd', 92, 2)
    __ValueType._UseLocation = pyxb.utils.utility.Location('/tmp/pyxbdist.RHB65sy/PyXB-1.1.5/pyxb/bundles/wssplat/schemas/wsse.xsd', 92, 2)
    
    ValueType = property(__ValueType.value, __ValueType.set, None, None)

    
    # Attribute URI uses Python identifier URI
    __URI = pyxb.binding.content.AttributeUse(pyxb.namespace.ExpandedName(None, u'URI'), 'URI', '__httpdocs_oasis_open_orgwss200401oasis_200401_wss_wssecurity_secext_1_0_xsd_ReferenceType_URI', pyxb.binding.datatypes.anyURI)
    __URI._DeclarationLocation = pyxb.utils.utility.Location('/tmp/pyxbdist.RHB65sy/PyXB-1.1.5/pyxb/bundles/wssplat/schemas/wsse.xsd', 91, 2)
    __URI._UseLocation = pyxb.utils.utility.Location('/tmp/pyxbdist.RHB65sy/PyXB-1.1.5/pyxb/bundles/wssplat/schemas/wsse.xsd', 91, 2)
    
    URI = property(__URI.value, __URI.set, None, None)

    _AttributeWildcard = pyxb.binding.content.Wildcard(process_contents=pyxb.binding.content.Wildcard.PC_lax, namespace_constraint=(pyxb.binding.content.Wildcard.NC_not, u'http://docs.oasis-open.org/wss/2004/01/oasis-200401-wss-wssecurity-secext-1.0.xsd'))

    _ElementMap = {
        
    }
    _AttributeMap = {
        __ValueType.name() : __ValueType,
        __URI.name() : __URI
    }
Namespace.addCategoryObject('typeBinding', u'ReferenceType', ReferenceType)


# Complex type {http://docs.oasis-open.org/wss/2004/01/oasis-200401-wss-wssecurity-secext-1.0.xsd}BinarySecurityTokenType with content type SIMPLE
class BinarySecurityTokenType (EncodedString):
    _TypeDefinition = pyxb.binding.datatypes.string
    _ContentTypeTag = pyxb.binding.basis.complexTypeDefinition._CT_SIMPLE
    _Abstract = False
    _ExpandedName = pyxb.namespace.ExpandedName(Namespace, u'BinarySecurityTokenType')
    _DefinitionLocation = pyxb.utils.utility.Location('/tmp/pyxbdist.RHB65sy/PyXB-1.1.5/pyxb/bundles/wssplat/schemas/wsse.xsd', 56, 1)
    # Base type is EncodedString
    
    # Attribute EncodingType inherited from {http://docs.oasis-open.org/wss/2004/01/oasis-200401-wss-wssecurity-secext-1.0.xsd}EncodedString
    
    # Attribute ValueType uses Python identifier ValueType
    __ValueType = pyxb.binding.content.AttributeUse(pyxb.namespace.ExpandedName(None, u'ValueType'), 'ValueType', '__httpdocs_oasis_open_orgwss200401oasis_200401_wss_wssecurity_secext_1_0_xsd_BinarySecurityTokenType_ValueType', pyxb.binding.datatypes.anyURI)
    __ValueType._DeclarationLocation = pyxb.utils.utility.Location('/tmp/pyxbdist.RHB65sy/PyXB-1.1.5/pyxb/bundles/wssplat/schemas/wsse.xsd', 62, 4)
    __ValueType._UseLocation = pyxb.utils.utility.Location('/tmp/pyxbdist.RHB65sy/PyXB-1.1.5/pyxb/bundles/wssplat/schemas/wsse.xsd', 62, 4)
    
    ValueType = property(__ValueType.value, __ValueType.set, None, None)

    
    # Attribute Id inherited from {http://docs.oasis-open.org/wss/2004/01/oasis-200401-wss-wssecurity-secext-1.0.xsd}AttributedString
    _AttributeWildcard = pyxb.binding.content.Wildcard(process_contents=pyxb.binding.content.Wildcard.PC_lax, namespace_constraint=(pyxb.binding.content.Wildcard.NC_not, u'http://docs.oasis-open.org/wss/2004/01/oasis-200401-wss-wssecurity-secext-1.0.xsd'))

    _ElementMap = EncodedString._ElementMap.copy()
    _ElementMap.update({
        
    })
    _AttributeMap = EncodedString._AttributeMap.copy()
    _AttributeMap.update({
        __ValueType.name() : __ValueType
    })
Namespace.addCategoryObject('typeBinding', u'BinarySecurityTokenType', BinarySecurityTokenType)


# Complex type {http://docs.oasis-open.org/wss/2004/01/oasis-200401-wss-wssecurity-secext-1.0.xsd}TransformationParametersType with content type ELEMENT_ONLY
class TransformationParametersType (pyxb.binding.basis.complexTypeDefinition):
    _TypeDefinition = None
    _ContentTypeTag = pyxb.binding.basis.complexTypeDefinition._CT_ELEMENT_ONLY
    _Abstract = False
    _ExpandedName = pyxb.namespace.ExpandedName(Namespace, u'TransformationParametersType')
    _DefinitionLocation = pyxb.utils.utility.Location('/tmp/pyxbdist.RHB65sy/PyXB-1.1.5/pyxb/bundles/wssplat/schemas/wsse.xsd', 129, 1)
    # Base type is pyxb.binding.datatypes.anyType
    _AttributeWildcard = pyxb.binding.content.Wildcard(process_contents=pyxb.binding.content.Wildcard.PC_lax, namespace_constraint=(pyxb.binding.content.Wildcard.NC_not, u'http://docs.oasis-open.org/wss/2004/01/oasis-200401-wss-wssecurity-secext-1.0.xsd'))
    _HasWildcardElement = True

    _ElementMap = {
        
    }
    _AttributeMap = {
        
    }
Namespace.addCategoryObject('typeBinding', u'TransformationParametersType', TransformationParametersType)


KeyIdentifier = pyxb.binding.basis.element(pyxb.namespace.ExpandedName(Namespace, u'KeyIdentifier'), KeyIdentifierType, documentation=u'This element defines a key identifier reference')
Namespace.addCategoryObject('elementBinding', KeyIdentifier.name().localName(), KeyIdentifier)

Nonce = pyxb.binding.basis.element(pyxb.namespace.ExpandedName(Namespace, u'Nonce'), EncodedString)
Namespace.addCategoryObject('elementBinding', Nonce.name().localName(), Nonce)

Password = pyxb.binding.basis.element(pyxb.namespace.ExpandedName(Namespace, u'Password'), PasswordString)
Namespace.addCategoryObject('elementBinding', Password.name().localName(), Password)

SecurityTokenReference = pyxb.binding.basis.element(pyxb.namespace.ExpandedName(Namespace, u'SecurityTokenReference'), SecurityTokenReferenceType, documentation=u'This element defines the wsse:SecurityTokenReference per Section 4.3.')
Namespace.addCategoryObject('elementBinding', SecurityTokenReference.name().localName(), SecurityTokenReference)

Embedded = pyxb.binding.basis.element(pyxb.namespace.ExpandedName(Namespace, u'Embedded'), EmbeddedType, documentation=u'This element defines a security token embedded reference')
Namespace.addCategoryObject('elementBinding', Embedded.name().localName(), Embedded)

UsernameToken = pyxb.binding.basis.element(pyxb.namespace.ExpandedName(Namespace, u'UsernameToken'), UsernameTokenType, documentation=u'This element defines the wsse:UsernameToken element per Section 4.1.')
Namespace.addCategoryObject('elementBinding', UsernameToken.name().localName(), UsernameToken)

Security = pyxb.binding.basis.element(pyxb.namespace.ExpandedName(Namespace, u'Security'), SecurityHeaderType, documentation=u'This element defines the wsse:Security SOAP header element per Section 4.')
Namespace.addCategoryObject('elementBinding', Security.name().localName(), Security)

Reference = pyxb.binding.basis.element(pyxb.namespace.ExpandedName(Namespace, u'Reference'), ReferenceType, documentation=u'This element defines a security token reference')
Namespace.addCategoryObject('elementBinding', Reference.name().localName(), Reference)

BinarySecurityToken = pyxb.binding.basis.element(pyxb.namespace.ExpandedName(Namespace, u'BinarySecurityToken'), BinarySecurityTokenType, documentation=u'This element defines the wsse:BinarySecurityToken element per Section 4.2.')
Namespace.addCategoryObject('elementBinding', BinarySecurityToken.name().localName(), BinarySecurityToken)

TransformationParameters = pyxb.binding.basis.element(pyxb.namespace.ExpandedName(Namespace, u'TransformationParameters'), TransformationParametersType, documentation=u'This element contains properties for transformations from any namespace, including DSIG.')
Namespace.addCategoryObject('elementBinding', TransformationParameters.name().localName(), TransformationParameters)


SecurityTokenReferenceType._GroupModel = pyxb.binding.content.GroupChoice(
    pyxb.binding.content.ParticleModel(pyxb.binding.content.Wildcard(process_contents=pyxb.binding.content.Wildcard.PC_lax, namespace_constraint=pyxb.binding.content.Wildcard.NC_any), min_occurs=1, max_occurs=1)
    )
SecurityTokenReferenceType._ContentModel = pyxb.binding.content.ParticleModel(SecurityTokenReferenceType._GroupModel, min_occurs=0L, max_occurs=None)


EmbeddedType._GroupModel = pyxb.binding.content.GroupChoice(
    pyxb.binding.content.ParticleModel(pyxb.binding.content.Wildcard(process_contents=pyxb.binding.content.Wildcard.PC_lax, namespace_constraint=pyxb.binding.content.Wildcard.NC_any), min_occurs=1, max_occurs=1)
    )
EmbeddedType._ContentModel = pyxb.binding.content.ParticleModel(EmbeddedType._GroupModel, min_occurs=0L, max_occurs=None)



UsernameTokenType._AddElement(pyxb.binding.basis.element(pyxb.namespace.ExpandedName(Namespace, u'Username'), AttributedString, scope=UsernameTokenType))
UsernameTokenType._GroupModel = pyxb.binding.content.GroupSequence(
    pyxb.binding.content.ParticleModel(UsernameTokenType._UseForTag(pyxb.namespace.ExpandedName(Namespace, u'Username')), min_occurs=1, max_occurs=1),
    pyxb.binding.content.ParticleModel(pyxb.binding.content.Wildcard(process_contents=pyxb.binding.content.Wildcard.PC_lax, namespace_constraint=pyxb.binding.content.Wildcard.NC_any), min_occurs=0L, max_occurs=None)
    )
UsernameTokenType._ContentModel = pyxb.binding.content.ParticleModel(UsernameTokenType._GroupModel, min_occurs=1, max_occurs=1)


SecurityHeaderType._GroupModel = pyxb.binding.content.GroupSequence(
    pyxb.binding.content.ParticleModel(pyxb.binding.content.Wildcard(process_contents=pyxb.binding.content.Wildcard.PC_lax, namespace_constraint=pyxb.binding.content.Wildcard.NC_any), min_occurs=0L, max_occurs=None)
    )
SecurityHeaderType._ContentModel = pyxb.binding.content.ParticleModel(SecurityHeaderType._GroupModel, min_occurs=1, max_occurs=1)


TransformationParametersType._GroupModel = pyxb.binding.content.GroupSequence(
    pyxb.binding.content.ParticleModel(pyxb.binding.content.Wildcard(process_contents=pyxb.binding.content.Wildcard.PC_lax, namespace_constraint=pyxb.binding.content.Wildcard.NC_any), min_occurs=0L, max_occurs=None)
    )
TransformationParametersType._ContentModel = pyxb.binding.content.ParticleModel(TransformationParametersType._GroupModel, min_occurs=1, max_occurs=1)
