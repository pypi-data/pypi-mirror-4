# ./pyxb/bundles/saml20/raw/metadata.py
# -*- coding: utf-8 -*-
# PyXB bindings for NM:f9d428fdbafcf137fd6f3c6128735cdf8829c2c0
# Generated 2012-11-01 15:13:40.116647 by PyXB version 1.1.5
# Namespace urn:oasis:names:tc:SAML:2.0:metadata

import pyxb
import pyxb.binding
import pyxb.binding.saxer
import StringIO
import pyxb.utils.utility
import pyxb.utils.domutils
import sys

# Unique identifier for bindings created at the same time
_GenerationUID = pyxb.utils.utility.UniqueIdentifier('urn:uuid:a05a1fb4-2460-11e2-b47c-c8600024e903')

# Import bindings for namespaces imported into schema
import pyxb.binding.datatypes
import pyxb.bundles.saml20.assertion
import pyxb.bundles.wssplat.ds
import pyxb.binding.xml_
import pyxb.bundles.wssplat.xenc

Namespace = pyxb.namespace.NamespaceForURI(u'urn:oasis:names:tc:SAML:2.0:metadata', create_if_missing=True)
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


# List simple type: {urn:oasis:names:tc:SAML:2.0:metadata}anyURIListType
# superclasses pyxb.binding.datatypes.anySimpleType
class anyURIListType (pyxb.binding.basis.STD_list):

    """Simple type that is a list of pyxb.binding.datatypes.anyURI."""

    _ExpandedName = pyxb.namespace.ExpandedName(Namespace, u'anyURIListType')
    _DefinitionLocation = pyxb.utils.utility.Location('/tmp/pyxbdist.RHB65sy/PyXB-1.1.5/pyxb/bundles/saml20/schemas/metadata.xsd', 186, 4)
    _Documentation = None

    _ItemType = pyxb.binding.datatypes.anyURI
anyURIListType._InitializeFacetMap()
Namespace.addCategoryObject('typeBinding', u'anyURIListType', anyURIListType)

# Atomic simple type: {urn:oasis:names:tc:SAML:2.0:metadata}KeyTypes
class KeyTypes (pyxb.binding.datatypes.string, pyxb.binding.basis.enumeration_mixin):

    """An atomic simple type."""

    _ExpandedName = pyxb.namespace.ExpandedName(Namespace, u'KeyTypes')
    _DefinitionLocation = pyxb.utils.utility.Location('/tmp/pyxbdist.RHB65sy/PyXB-1.1.5/pyxb/bundles/saml20/schemas/metadata.xsd', 198, 4)
    _Documentation = None
KeyTypes._CF_enumeration = pyxb.binding.facets.CF_enumeration(value_datatype=KeyTypes, enum_prefix=None)
KeyTypes.encryption = KeyTypes._CF_enumeration.addEnumeration(unicode_value=u'encryption', tag=u'encryption')
KeyTypes.signing = KeyTypes._CF_enumeration.addEnumeration(unicode_value=u'signing', tag=u'signing')
KeyTypes._InitializeFacetMap(KeyTypes._CF_enumeration)
Namespace.addCategoryObject('typeBinding', u'KeyTypes', KeyTypes)

# Atomic simple type: {urn:oasis:names:tc:SAML:2.0:metadata}ContactTypeType
class ContactTypeType (pyxb.binding.datatypes.string, pyxb.binding.basis.enumeration_mixin):

    """An atomic simple type."""

    _ExpandedName = pyxb.namespace.ExpandedName(Namespace, u'ContactTypeType')
    _DefinitionLocation = pyxb.utils.utility.Location('/tmp/pyxbdist.RHB65sy/PyXB-1.1.5/pyxb/bundles/saml20/schemas/metadata.xsd', 151, 4)
    _Documentation = None
ContactTypeType._CF_enumeration = pyxb.binding.facets.CF_enumeration(value_datatype=ContactTypeType, enum_prefix=None)
ContactTypeType.technical = ContactTypeType._CF_enumeration.addEnumeration(unicode_value=u'technical', tag=u'technical')
ContactTypeType.support = ContactTypeType._CF_enumeration.addEnumeration(unicode_value=u'support', tag=u'support')
ContactTypeType.administrative = ContactTypeType._CF_enumeration.addEnumeration(unicode_value=u'administrative', tag=u'administrative')
ContactTypeType.billing = ContactTypeType._CF_enumeration.addEnumeration(unicode_value=u'billing', tag=u'billing')
ContactTypeType.other = ContactTypeType._CF_enumeration.addEnumeration(unicode_value=u'other', tag=u'other')
ContactTypeType._InitializeFacetMap(ContactTypeType._CF_enumeration)
Namespace.addCategoryObject('typeBinding', u'ContactTypeType', ContactTypeType)

# Atomic simple type: {urn:oasis:names:tc:SAML:2.0:metadata}entityIDType
class entityIDType (pyxb.binding.datatypes.anyURI):

    """An atomic simple type."""

    _ExpandedName = pyxb.namespace.ExpandedName(Namespace, u'entityIDType')
    _DefinitionLocation = pyxb.utils.utility.Location('/tmp/pyxbdist.RHB65sy/PyXB-1.1.5/pyxb/bundles/saml20/schemas/metadata.xsd', 31, 4)
    _Documentation = None
entityIDType._CF_maxLength = pyxb.binding.facets.CF_maxLength(value=pyxb.binding.datatypes.nonNegativeInteger(1024L))
entityIDType._InitializeFacetMap(entityIDType._CF_maxLength)
Namespace.addCategoryObject('typeBinding', u'entityIDType', entityIDType)

# Complex type {urn:oasis:names:tc:SAML:2.0:metadata}EndpointType with content type ELEMENT_ONLY
class EndpointType (pyxb.binding.basis.complexTypeDefinition):
    _TypeDefinition = None
    _ContentTypeTag = pyxb.binding.basis.complexTypeDefinition._CT_ELEMENT_ONLY
    _Abstract = False
    _ExpandedName = pyxb.namespace.ExpandedName(Namespace, u'EndpointType')
    _DefinitionLocation = pyxb.utils.utility.Location('/tmp/pyxbdist.RHB65sy/PyXB-1.1.5/pyxb/bundles/saml20/schemas/metadata.xsd', 58, 4)
    # Base type is pyxb.binding.datatypes.anyType
    
    # Attribute ResponseLocation uses Python identifier ResponseLocation
    __ResponseLocation = pyxb.binding.content.AttributeUse(pyxb.namespace.ExpandedName(None, u'ResponseLocation'), 'ResponseLocation', '__urnoasisnamestcSAML2_0metadata_EndpointType_ResponseLocation', pyxb.binding.datatypes.anyURI)
    __ResponseLocation._DeclarationLocation = pyxb.utils.utility.Location('/tmp/pyxbdist.RHB65sy/PyXB-1.1.5/pyxb/bundles/saml20/schemas/metadata.xsd', 64, 8)
    __ResponseLocation._UseLocation = pyxb.utils.utility.Location('/tmp/pyxbdist.RHB65sy/PyXB-1.1.5/pyxb/bundles/saml20/schemas/metadata.xsd', 64, 8)
    
    ResponseLocation = property(__ResponseLocation.value, __ResponseLocation.set, None, None)

    
    # Attribute Location uses Python identifier Location
    __Location = pyxb.binding.content.AttributeUse(pyxb.namespace.ExpandedName(None, u'Location'), 'Location', '__urnoasisnamestcSAML2_0metadata_EndpointType_Location', pyxb.binding.datatypes.anyURI, required=True)
    __Location._DeclarationLocation = pyxb.utils.utility.Location('/tmp/pyxbdist.RHB65sy/PyXB-1.1.5/pyxb/bundles/saml20/schemas/metadata.xsd', 63, 8)
    __Location._UseLocation = pyxb.utils.utility.Location('/tmp/pyxbdist.RHB65sy/PyXB-1.1.5/pyxb/bundles/saml20/schemas/metadata.xsd', 63, 8)
    
    Location = property(__Location.value, __Location.set, None, None)

    
    # Attribute Binding uses Python identifier Binding
    __Binding = pyxb.binding.content.AttributeUse(pyxb.namespace.ExpandedName(None, u'Binding'), 'Binding', '__urnoasisnamestcSAML2_0metadata_EndpointType_Binding', pyxb.binding.datatypes.anyURI, required=True)
    __Binding._DeclarationLocation = pyxb.utils.utility.Location('/tmp/pyxbdist.RHB65sy/PyXB-1.1.5/pyxb/bundles/saml20/schemas/metadata.xsd', 62, 8)
    __Binding._UseLocation = pyxb.utils.utility.Location('/tmp/pyxbdist.RHB65sy/PyXB-1.1.5/pyxb/bundles/saml20/schemas/metadata.xsd', 62, 8)
    
    Binding = property(__Binding.value, __Binding.set, None, None)

    _AttributeWildcard = pyxb.binding.content.Wildcard(process_contents=pyxb.binding.content.Wildcard.PC_lax, namespace_constraint=(pyxb.binding.content.Wildcard.NC_not, u'urn:oasis:names:tc:SAML:2.0:metadata'))
    _HasWildcardElement = True

    _ElementMap = {
        
    }
    _AttributeMap = {
        __ResponseLocation.name() : __ResponseLocation,
        __Location.name() : __Location,
        __Binding.name() : __Binding
    }
Namespace.addCategoryObject('typeBinding', u'EndpointType', EndpointType)


# Complex type {urn:oasis:names:tc:SAML:2.0:metadata}IndexedEndpointType with content type ELEMENT_ONLY
class IndexedEndpointType (EndpointType):
    _TypeDefinition = None
    _ContentTypeTag = pyxb.binding.basis.complexTypeDefinition._CT_ELEMENT_ONLY
    _Abstract = False
    _ExpandedName = pyxb.namespace.ExpandedName(Namespace, u'IndexedEndpointType')
    _DefinitionLocation = pyxb.utils.utility.Location('/tmp/pyxbdist.RHB65sy/PyXB-1.1.5/pyxb/bundles/saml20/schemas/metadata.xsd', 68, 4)
    # Base type is EndpointType
    
    # Attribute isDefault uses Python identifier isDefault
    __isDefault = pyxb.binding.content.AttributeUse(pyxb.namespace.ExpandedName(None, u'isDefault'), 'isDefault', '__urnoasisnamestcSAML2_0metadata_IndexedEndpointType_isDefault', pyxb.binding.datatypes.boolean)
    __isDefault._DeclarationLocation = pyxb.utils.utility.Location('/tmp/pyxbdist.RHB65sy/PyXB-1.1.5/pyxb/bundles/saml20/schemas/metadata.xsd', 72, 16)
    __isDefault._UseLocation = pyxb.utils.utility.Location('/tmp/pyxbdist.RHB65sy/PyXB-1.1.5/pyxb/bundles/saml20/schemas/metadata.xsd', 72, 16)
    
    isDefault = property(__isDefault.value, __isDefault.set, None, None)

    
    # Attribute ResponseLocation inherited from {urn:oasis:names:tc:SAML:2.0:metadata}EndpointType
    
    # Attribute index uses Python identifier index
    __index = pyxb.binding.content.AttributeUse(pyxb.namespace.ExpandedName(None, u'index'), 'index', '__urnoasisnamestcSAML2_0metadata_IndexedEndpointType_index', pyxb.binding.datatypes.unsignedShort, required=True)
    __index._DeclarationLocation = pyxb.utils.utility.Location('/tmp/pyxbdist.RHB65sy/PyXB-1.1.5/pyxb/bundles/saml20/schemas/metadata.xsd', 71, 16)
    __index._UseLocation = pyxb.utils.utility.Location('/tmp/pyxbdist.RHB65sy/PyXB-1.1.5/pyxb/bundles/saml20/schemas/metadata.xsd', 71, 16)
    
    index = property(__index.value, __index.set, None, None)

    
    # Attribute Location inherited from {urn:oasis:names:tc:SAML:2.0:metadata}EndpointType
    
    # Attribute Binding inherited from {urn:oasis:names:tc:SAML:2.0:metadata}EndpointType
    _AttributeWildcard = pyxb.binding.content.Wildcard(process_contents=pyxb.binding.content.Wildcard.PC_lax, namespace_constraint=(pyxb.binding.content.Wildcard.NC_not, u'urn:oasis:names:tc:SAML:2.0:metadata'))
    _HasWildcardElement = True

    _ElementMap = EndpointType._ElementMap.copy()
    _ElementMap.update({
        
    })
    _AttributeMap = EndpointType._AttributeMap.copy()
    _AttributeMap.update({
        __isDefault.name() : __isDefault,
        __index.name() : __index
    })
Namespace.addCategoryObject('typeBinding', u'IndexedEndpointType', IndexedEndpointType)


# Complex type {urn:oasis:names:tc:SAML:2.0:metadata}OrganizationType with content type ELEMENT_ONLY
class OrganizationType (pyxb.binding.basis.complexTypeDefinition):
    _TypeDefinition = None
    _ContentTypeTag = pyxb.binding.basis.complexTypeDefinition._CT_ELEMENT_ONLY
    _Abstract = False
    _ExpandedName = pyxb.namespace.ExpandedName(Namespace, u'OrganizationType')
    _DefinitionLocation = pyxb.utils.utility.Location('/tmp/pyxbdist.RHB65sy/PyXB-1.1.5/pyxb/bundles/saml20/schemas/metadata.xsd', 121, 4)
    # Base type is pyxb.binding.datatypes.anyType
    
    # Element {urn:oasis:names:tc:SAML:2.0:metadata}Extensions uses Python identifier Extensions
    __Extensions = pyxb.binding.content.ElementUse(pyxb.namespace.ExpandedName(Namespace, u'Extensions'), 'Extensions', '__urnoasisnamestcSAML2_0metadata_OrganizationType_urnoasisnamestcSAML2_0metadataExtensions', False)
    __Extensions._DeclarationLocation = pyxb.utils.utility.Location('/tmp/pyxbdist.RHB65sy/PyXB-1.1.5/pyxb/bundles/saml20/schemas/metadata.xsd', 51, 4)
    __Extensions._UseLocation = pyxb.utils.utility.Location('/tmp/pyxbdist.RHB65sy/PyXB-1.1.5/pyxb/bundles/saml20/schemas/metadata.xsd', 122, 8)

    
    Extensions = property(__Extensions.value, __Extensions.set, None, None)

    
    # Element {urn:oasis:names:tc:SAML:2.0:metadata}OrganizationURL uses Python identifier OrganizationURL
    __OrganizationURL = pyxb.binding.content.ElementUse(pyxb.namespace.ExpandedName(Namespace, u'OrganizationURL'), 'OrganizationURL', '__urnoasisnamestcSAML2_0metadata_OrganizationType_urnoasisnamestcSAML2_0metadataOrganizationURL', True)
    __OrganizationURL._DeclarationLocation = pyxb.utils.utility.Location('/tmp/pyxbdist.RHB65sy/PyXB-1.1.5/pyxb/bundles/saml20/schemas/metadata.xsd', 132, 4)
    __OrganizationURL._UseLocation = pyxb.utils.utility.Location('/tmp/pyxbdist.RHB65sy/PyXB-1.1.5/pyxb/bundles/saml20/schemas/metadata.xsd', 122, 8)

    
    OrganizationURL = property(__OrganizationURL.value, __OrganizationURL.set, None, None)

    
    # Element {urn:oasis:names:tc:SAML:2.0:metadata}OrganizationDisplayName uses Python identifier OrganizationDisplayName
    __OrganizationDisplayName = pyxb.binding.content.ElementUse(pyxb.namespace.ExpandedName(Namespace, u'OrganizationDisplayName'), 'OrganizationDisplayName', '__urnoasisnamestcSAML2_0metadata_OrganizationType_urnoasisnamestcSAML2_0metadataOrganizationDisplayName', True)
    __OrganizationDisplayName._DeclarationLocation = pyxb.utils.utility.Location('/tmp/pyxbdist.RHB65sy/PyXB-1.1.5/pyxb/bundles/saml20/schemas/metadata.xsd', 131, 4)
    __OrganizationDisplayName._UseLocation = pyxb.utils.utility.Location('/tmp/pyxbdist.RHB65sy/PyXB-1.1.5/pyxb/bundles/saml20/schemas/metadata.xsd', 122, 8)

    
    OrganizationDisplayName = property(__OrganizationDisplayName.value, __OrganizationDisplayName.set, None, None)

    
    # Element {urn:oasis:names:tc:SAML:2.0:metadata}OrganizationName uses Python identifier OrganizationName
    __OrganizationName = pyxb.binding.content.ElementUse(pyxb.namespace.ExpandedName(Namespace, u'OrganizationName'), 'OrganizationName', '__urnoasisnamestcSAML2_0metadata_OrganizationType_urnoasisnamestcSAML2_0metadataOrganizationName', True)
    __OrganizationName._DeclarationLocation = pyxb.utils.utility.Location('/tmp/pyxbdist.RHB65sy/PyXB-1.1.5/pyxb/bundles/saml20/schemas/metadata.xsd', 130, 4)
    __OrganizationName._UseLocation = pyxb.utils.utility.Location('/tmp/pyxbdist.RHB65sy/PyXB-1.1.5/pyxb/bundles/saml20/schemas/metadata.xsd', 122, 8)

    
    OrganizationName = property(__OrganizationName.value, __OrganizationName.set, None, None)

    _AttributeWildcard = pyxb.binding.content.Wildcard(process_contents=pyxb.binding.content.Wildcard.PC_lax, namespace_constraint=(pyxb.binding.content.Wildcard.NC_not, u'urn:oasis:names:tc:SAML:2.0:metadata'))

    _ElementMap = {
        __Extensions.name() : __Extensions,
        __OrganizationURL.name() : __OrganizationURL,
        __OrganizationDisplayName.name() : __OrganizationDisplayName,
        __OrganizationName.name() : __OrganizationName
    }
    _AttributeMap = {
        
    }
Namespace.addCategoryObject('typeBinding', u'OrganizationType', OrganizationType)


# Complex type {urn:oasis:names:tc:SAML:2.0:metadata}RequestedAttributeType with content type ELEMENT_ONLY
class RequestedAttributeType (pyxb.bundles.saml20.assertion.AttributeType):
    _TypeDefinition = None
    _ContentTypeTag = pyxb.binding.basis.complexTypeDefinition._CT_ELEMENT_ONLY
    _Abstract = False
    _ExpandedName = pyxb.namespace.ExpandedName(Namespace, u'RequestedAttributeType')
    _DefinitionLocation = pyxb.utils.utility.Location('/tmp/pyxbdist.RHB65sy/PyXB-1.1.5/pyxb/bundles/saml20/schemas/metadata.xsd', 270, 4)
    # Base type is pyxb.bundles.saml20.assertion.AttributeType
    
    # Element AttributeValue ({urn:oasis:names:tc:SAML:2.0:assertion}AttributeValue) inherited from {urn:oasis:names:tc:SAML:2.0:assertion}AttributeType
    
    # Attribute FriendlyName inherited from {urn:oasis:names:tc:SAML:2.0:assertion}AttributeType
    
    # Attribute NameFormat inherited from {urn:oasis:names:tc:SAML:2.0:assertion}AttributeType
    
    # Attribute Name inherited from {urn:oasis:names:tc:SAML:2.0:assertion}AttributeType
    
    # Attribute isRequired uses Python identifier isRequired
    __isRequired = pyxb.binding.content.AttributeUse(pyxb.namespace.ExpandedName(None, u'isRequired'), 'isRequired', '__urnoasisnamestcSAML2_0metadata_RequestedAttributeType_isRequired', pyxb.binding.datatypes.boolean)
    __isRequired._DeclarationLocation = pyxb.utils.utility.Location('/tmp/pyxbdist.RHB65sy/PyXB-1.1.5/pyxb/bundles/saml20/schemas/metadata.xsd', 273, 16)
    __isRequired._UseLocation = pyxb.utils.utility.Location('/tmp/pyxbdist.RHB65sy/PyXB-1.1.5/pyxb/bundles/saml20/schemas/metadata.xsd', 273, 16)
    
    isRequired = property(__isRequired.value, __isRequired.set, None, None)

    _AttributeWildcard = pyxb.binding.content.Wildcard(process_contents=pyxb.binding.content.Wildcard.PC_lax, namespace_constraint=(pyxb.binding.content.Wildcard.NC_not, u'urn:oasis:names:tc:SAML:2.0:assertion'))

    _ElementMap = pyxb.bundles.saml20.assertion.AttributeType._ElementMap.copy()
    _ElementMap.update({
        
    })
    _AttributeMap = pyxb.bundles.saml20.assertion.AttributeType._AttributeMap.copy()
    _AttributeMap.update({
        __isRequired.name() : __isRequired
    })
Namespace.addCategoryObject('typeBinding', u'RequestedAttributeType', RequestedAttributeType)


# Complex type {urn:oasis:names:tc:SAML:2.0:metadata}RoleDescriptorType with content type ELEMENT_ONLY
class RoleDescriptorType (pyxb.binding.basis.complexTypeDefinition):
    _TypeDefinition = None
    _ContentTypeTag = pyxb.binding.basis.complexTypeDefinition._CT_ELEMENT_ONLY
    _Abstract = True
    _ExpandedName = pyxb.namespace.ExpandedName(Namespace, u'RoleDescriptorType')
    _DefinitionLocation = pyxb.utils.utility.Location('/tmp/pyxbdist.RHB65sy/PyXB-1.1.5/pyxb/bundles/saml20/schemas/metadata.xsd', 171, 4)
    # Base type is pyxb.binding.datatypes.anyType
    
    # Element {urn:oasis:names:tc:SAML:2.0:metadata}Extensions uses Python identifier Extensions
    __Extensions = pyxb.binding.content.ElementUse(pyxb.namespace.ExpandedName(Namespace, u'Extensions'), 'Extensions', '__urnoasisnamestcSAML2_0metadata_RoleDescriptorType_urnoasisnamestcSAML2_0metadataExtensions', False)
    __Extensions._DeclarationLocation = pyxb.utils.utility.Location('/tmp/pyxbdist.RHB65sy/PyXB-1.1.5/pyxb/bundles/saml20/schemas/metadata.xsd', 51, 4)
    __Extensions._UseLocation = pyxb.utils.utility.Location('/tmp/pyxbdist.RHB65sy/PyXB-1.1.5/pyxb/bundles/saml20/schemas/metadata.xsd', 172, 8)

    
    Extensions = property(__Extensions.value, __Extensions.set, None, None)

    
    # Element {urn:oasis:names:tc:SAML:2.0:metadata}Organization uses Python identifier Organization
    __Organization = pyxb.binding.content.ElementUse(pyxb.namespace.ExpandedName(Namespace, u'Organization'), 'Organization', '__urnoasisnamestcSAML2_0metadata_RoleDescriptorType_urnoasisnamestcSAML2_0metadataOrganization', False)
    __Organization._DeclarationLocation = pyxb.utils.utility.Location('/tmp/pyxbdist.RHB65sy/PyXB-1.1.5/pyxb/bundles/saml20/schemas/metadata.xsd', 120, 4)
    __Organization._UseLocation = pyxb.utils.utility.Location('/tmp/pyxbdist.RHB65sy/PyXB-1.1.5/pyxb/bundles/saml20/schemas/metadata.xsd', 172, 8)

    
    Organization = property(__Organization.value, __Organization.set, None, None)

    
    # Element {urn:oasis:names:tc:SAML:2.0:metadata}KeyDescriptor uses Python identifier KeyDescriptor
    __KeyDescriptor = pyxb.binding.content.ElementUse(pyxb.namespace.ExpandedName(Namespace, u'KeyDescriptor'), 'KeyDescriptor', '__urnoasisnamestcSAML2_0metadata_RoleDescriptorType_urnoasisnamestcSAML2_0metadataKeyDescriptor', True)
    __KeyDescriptor._DeclarationLocation = pyxb.utils.utility.Location('/tmp/pyxbdist.RHB65sy/PyXB-1.1.5/pyxb/bundles/saml20/schemas/metadata.xsd', 190, 4)
    __KeyDescriptor._UseLocation = pyxb.utils.utility.Location('/tmp/pyxbdist.RHB65sy/PyXB-1.1.5/pyxb/bundles/saml20/schemas/metadata.xsd', 172, 8)

    
    KeyDescriptor = property(__KeyDescriptor.value, __KeyDescriptor.set, None, None)

    
    # Element {http://www.w3.org/2000/09/xmldsig#}Signature uses Python identifier Signature
    __Signature = pyxb.binding.content.ElementUse(pyxb.namespace.ExpandedName(pyxb.namespace.NamespaceForURI(u'http://www.w3.org/2000/09/xmldsig#'), u'Signature'), 'Signature', '__urnoasisnamestcSAML2_0metadata_RoleDescriptorType_httpwww_w3_org200009xmldsigSignature', False)
    __Signature._DeclarationLocation = pyxb.utils.utility.Location('/tmp/pyxbdist.RHB65sy/PyXB-1.1.5/pyxb/bundles/wssplat/schemas/ds.xsd', 43, 0)
    __Signature._UseLocation = pyxb.utils.utility.Location('/tmp/pyxbdist.RHB65sy/PyXB-1.1.5/pyxb/bundles/saml20/schemas/metadata.xsd', 172, 8)

    
    Signature = property(__Signature.value, __Signature.set, None, None)

    
    # Element {urn:oasis:names:tc:SAML:2.0:metadata}ContactPerson uses Python identifier ContactPerson
    __ContactPerson = pyxb.binding.content.ElementUse(pyxb.namespace.ExpandedName(Namespace, u'ContactPerson'), 'ContactPerson', '__urnoasisnamestcSAML2_0metadata_RoleDescriptorType_urnoasisnamestcSAML2_0metadataContactPerson', True)
    __ContactPerson._DeclarationLocation = pyxb.utils.utility.Location('/tmp/pyxbdist.RHB65sy/PyXB-1.1.5/pyxb/bundles/saml20/schemas/metadata.xsd', 133, 4)
    __ContactPerson._UseLocation = pyxb.utils.utility.Location('/tmp/pyxbdist.RHB65sy/PyXB-1.1.5/pyxb/bundles/saml20/schemas/metadata.xsd', 172, 8)

    
    ContactPerson = property(__ContactPerson.value, __ContactPerson.set, None, None)

    
    # Attribute protocolSupportEnumeration uses Python identifier protocolSupportEnumeration
    __protocolSupportEnumeration = pyxb.binding.content.AttributeUse(pyxb.namespace.ExpandedName(None, u'protocolSupportEnumeration'), 'protocolSupportEnumeration', '__urnoasisnamestcSAML2_0metadata_RoleDescriptorType_protocolSupportEnumeration', anyURIListType, required=True)
    __protocolSupportEnumeration._DeclarationLocation = pyxb.utils.utility.Location('/tmp/pyxbdist.RHB65sy/PyXB-1.1.5/pyxb/bundles/saml20/schemas/metadata.xsd', 182, 8)
    __protocolSupportEnumeration._UseLocation = pyxb.utils.utility.Location('/tmp/pyxbdist.RHB65sy/PyXB-1.1.5/pyxb/bundles/saml20/schemas/metadata.xsd', 182, 8)
    
    protocolSupportEnumeration = property(__protocolSupportEnumeration.value, __protocolSupportEnumeration.set, None, None)

    
    # Attribute ID uses Python identifier ID
    __ID = pyxb.binding.content.AttributeUse(pyxb.namespace.ExpandedName(None, u'ID'), 'ID', '__urnoasisnamestcSAML2_0metadata_RoleDescriptorType_ID', pyxb.binding.datatypes.ID)
    __ID._DeclarationLocation = pyxb.utils.utility.Location('/tmp/pyxbdist.RHB65sy/PyXB-1.1.5/pyxb/bundles/saml20/schemas/metadata.xsd', 179, 8)
    __ID._UseLocation = pyxb.utils.utility.Location('/tmp/pyxbdist.RHB65sy/PyXB-1.1.5/pyxb/bundles/saml20/schemas/metadata.xsd', 179, 8)
    
    ID = property(__ID.value, __ID.set, None, None)

    
    # Attribute errorURL uses Python identifier errorURL
    __errorURL = pyxb.binding.content.AttributeUse(pyxb.namespace.ExpandedName(None, u'errorURL'), 'errorURL', '__urnoasisnamestcSAML2_0metadata_RoleDescriptorType_errorURL', pyxb.binding.datatypes.anyURI)
    __errorURL._DeclarationLocation = pyxb.utils.utility.Location('/tmp/pyxbdist.RHB65sy/PyXB-1.1.5/pyxb/bundles/saml20/schemas/metadata.xsd', 183, 8)
    __errorURL._UseLocation = pyxb.utils.utility.Location('/tmp/pyxbdist.RHB65sy/PyXB-1.1.5/pyxb/bundles/saml20/schemas/metadata.xsd', 183, 8)
    
    errorURL = property(__errorURL.value, __errorURL.set, None, None)

    
    # Attribute cacheDuration uses Python identifier cacheDuration
    __cacheDuration = pyxb.binding.content.AttributeUse(pyxb.namespace.ExpandedName(None, u'cacheDuration'), 'cacheDuration', '__urnoasisnamestcSAML2_0metadata_RoleDescriptorType_cacheDuration', pyxb.binding.datatypes.duration)
    __cacheDuration._DeclarationLocation = pyxb.utils.utility.Location('/tmp/pyxbdist.RHB65sy/PyXB-1.1.5/pyxb/bundles/saml20/schemas/metadata.xsd', 181, 8)
    __cacheDuration._UseLocation = pyxb.utils.utility.Location('/tmp/pyxbdist.RHB65sy/PyXB-1.1.5/pyxb/bundles/saml20/schemas/metadata.xsd', 181, 8)
    
    cacheDuration = property(__cacheDuration.value, __cacheDuration.set, None, None)

    
    # Attribute validUntil uses Python identifier validUntil
    __validUntil = pyxb.binding.content.AttributeUse(pyxb.namespace.ExpandedName(None, u'validUntil'), 'validUntil', '__urnoasisnamestcSAML2_0metadata_RoleDescriptorType_validUntil', pyxb.binding.datatypes.dateTime)
    __validUntil._DeclarationLocation = pyxb.utils.utility.Location('/tmp/pyxbdist.RHB65sy/PyXB-1.1.5/pyxb/bundles/saml20/schemas/metadata.xsd', 180, 8)
    __validUntil._UseLocation = pyxb.utils.utility.Location('/tmp/pyxbdist.RHB65sy/PyXB-1.1.5/pyxb/bundles/saml20/schemas/metadata.xsd', 180, 8)
    
    validUntil = property(__validUntil.value, __validUntil.set, None, None)

    _AttributeWildcard = pyxb.binding.content.Wildcard(process_contents=pyxb.binding.content.Wildcard.PC_lax, namespace_constraint=(pyxb.binding.content.Wildcard.NC_not, u'urn:oasis:names:tc:SAML:2.0:metadata'))

    _ElementMap = {
        __Extensions.name() : __Extensions,
        __Organization.name() : __Organization,
        __KeyDescriptor.name() : __KeyDescriptor,
        __Signature.name() : __Signature,
        __ContactPerson.name() : __ContactPerson
    }
    _AttributeMap = {
        __protocolSupportEnumeration.name() : __protocolSupportEnumeration,
        __ID.name() : __ID,
        __errorURL.name() : __errorURL,
        __cacheDuration.name() : __cacheDuration,
        __validUntil.name() : __validUntil
    }
Namespace.addCategoryObject('typeBinding', u'RoleDescriptorType', RoleDescriptorType)


# Complex type {urn:oasis:names:tc:SAML:2.0:metadata}PDPDescriptorType with content type ELEMENT_ONLY
class PDPDescriptorType (RoleDescriptorType):
    _TypeDefinition = None
    _ContentTypeTag = pyxb.binding.basis.complexTypeDefinition._CT_ELEMENT_ONLY
    _Abstract = False
    _ExpandedName = pyxb.namespace.ExpandedName(Namespace, u'PDPDescriptorType')
    _DefinitionLocation = pyxb.utils.utility.Location('/tmp/pyxbdist.RHB65sy/PyXB-1.1.5/pyxb/bundles/saml20/schemas/metadata.xsd', 293, 4)
    # Base type is RoleDescriptorType
    
    # Element KeyDescriptor ({urn:oasis:names:tc:SAML:2.0:metadata}KeyDescriptor) inherited from {urn:oasis:names:tc:SAML:2.0:metadata}RoleDescriptorType
    
    # Element Organization ({urn:oasis:names:tc:SAML:2.0:metadata}Organization) inherited from {urn:oasis:names:tc:SAML:2.0:metadata}RoleDescriptorType
    
    # Element Signature ({http://www.w3.org/2000/09/xmldsig#}Signature) inherited from {urn:oasis:names:tc:SAML:2.0:metadata}RoleDescriptorType
    
    # Element {urn:oasis:names:tc:SAML:2.0:metadata}NameIDFormat uses Python identifier NameIDFormat
    __NameIDFormat = pyxb.binding.content.ElementUse(pyxb.namespace.ExpandedName(Namespace, u'NameIDFormat'), 'NameIDFormat', '__urnoasisnamestcSAML2_0metadata_PDPDescriptorType_urnoasisnamestcSAML2_0metadataNameIDFormat', True)
    __NameIDFormat._DeclarationLocation = pyxb.utils.utility.Location('/tmp/pyxbdist.RHB65sy/PyXB-1.1.5/pyxb/bundles/saml20/schemas/metadata.xsd', 221, 4)
    __NameIDFormat._UseLocation = None

    
    NameIDFormat = property(__NameIDFormat.value, __NameIDFormat.set, None, None)

    
    # Element {urn:oasis:names:tc:SAML:2.0:metadata}AssertionIDRequestService uses Python identifier AssertionIDRequestService
    __AssertionIDRequestService = pyxb.binding.content.ElementUse(pyxb.namespace.ExpandedName(Namespace, u'AssertionIDRequestService'), 'AssertionIDRequestService', '__urnoasisnamestcSAML2_0metadata_PDPDescriptorType_urnoasisnamestcSAML2_0metadataAssertionIDRequestService', True)
    __AssertionIDRequestService._DeclarationLocation = pyxb.utils.utility.Location('/tmp/pyxbdist.RHB65sy/PyXB-1.1.5/pyxb/bundles/saml20/schemas/metadata.xsd', 240, 4)
    __AssertionIDRequestService._UseLocation = None

    
    AssertionIDRequestService = property(__AssertionIDRequestService.value, __AssertionIDRequestService.set, None, None)

    
    # Element Extensions ({urn:oasis:names:tc:SAML:2.0:metadata}Extensions) inherited from {urn:oasis:names:tc:SAML:2.0:metadata}RoleDescriptorType
    
    # Element ContactPerson ({urn:oasis:names:tc:SAML:2.0:metadata}ContactPerson) inherited from {urn:oasis:names:tc:SAML:2.0:metadata}RoleDescriptorType
    
    # Element {urn:oasis:names:tc:SAML:2.0:metadata}AuthzService uses Python identifier AuthzService
    __AuthzService = pyxb.binding.content.ElementUse(pyxb.namespace.ExpandedName(Namespace, u'AuthzService'), 'AuthzService', '__urnoasisnamestcSAML2_0metadata_PDPDescriptorType_urnoasisnamestcSAML2_0metadataAuthzService', True)
    __AuthzService._DeclarationLocation = pyxb.utils.utility.Location('/tmp/pyxbdist.RHB65sy/PyXB-1.1.5/pyxb/bundles/saml20/schemas/metadata.xsd', 304, 4)
    __AuthzService._UseLocation = None

    
    AuthzService = property(__AuthzService.value, __AuthzService.set, None, None)

    
    # Attribute protocolSupportEnumeration inherited from {urn:oasis:names:tc:SAML:2.0:metadata}RoleDescriptorType
    
    # Attribute errorURL inherited from {urn:oasis:names:tc:SAML:2.0:metadata}RoleDescriptorType
    
    # Attribute validUntil inherited from {urn:oasis:names:tc:SAML:2.0:metadata}RoleDescriptorType
    
    # Attribute ID inherited from {urn:oasis:names:tc:SAML:2.0:metadata}RoleDescriptorType
    
    # Attribute cacheDuration inherited from {urn:oasis:names:tc:SAML:2.0:metadata}RoleDescriptorType
    _AttributeWildcard = pyxb.binding.content.Wildcard(process_contents=pyxb.binding.content.Wildcard.PC_lax, namespace_constraint=(pyxb.binding.content.Wildcard.NC_not, u'urn:oasis:names:tc:SAML:2.0:metadata'))

    _ElementMap = RoleDescriptorType._ElementMap.copy()
    _ElementMap.update({
        __NameIDFormat.name() : __NameIDFormat,
        __AssertionIDRequestService.name() : __AssertionIDRequestService,
        __AuthzService.name() : __AuthzService
    })
    _AttributeMap = RoleDescriptorType._AttributeMap.copy()
    _AttributeMap.update({
        
    })
Namespace.addCategoryObject('typeBinding', u'PDPDescriptorType', PDPDescriptorType)


# Complex type {urn:oasis:names:tc:SAML:2.0:metadata}localizedNameType with content type SIMPLE
class localizedNameType (pyxb.binding.basis.complexTypeDefinition):
    _TypeDefinition = pyxb.binding.datatypes.string
    _ContentTypeTag = pyxb.binding.basis.complexTypeDefinition._CT_SIMPLE
    _Abstract = False
    _ExpandedName = pyxb.namespace.ExpandedName(Namespace, u'localizedNameType')
    _DefinitionLocation = pyxb.utils.utility.Location('/tmp/pyxbdist.RHB65sy/PyXB-1.1.5/pyxb/bundles/saml20/schemas/metadata.xsd', 36, 4)
    # Base type is pyxb.binding.datatypes.string
    
    # Attribute {http://www.w3.org/XML/1998/namespace}lang uses Python identifier lang
    __lang = pyxb.binding.content.AttributeUse(pyxb.namespace.ExpandedName(pyxb.namespace.XML, 'lang'), 'lang', '__urnoasisnamestcSAML2_0metadata_localizedNameType_httpwww_w3_orgXML1998namespacelang', pyxb.binding.xml_.STD_ANON_lang, required=True)
    __lang._DeclarationLocation = None
    __lang._UseLocation = pyxb.utils.utility.Location('/tmp/pyxbdist.RHB65sy/PyXB-1.1.5/pyxb/bundles/saml20/schemas/metadata.xsd', 39, 16)
    
    lang = property(__lang.value, __lang.set, None, None)


    _ElementMap = {
        
    }
    _AttributeMap = {
        __lang.name() : __lang
    }
Namespace.addCategoryObject('typeBinding', u'localizedNameType', localizedNameType)


# Complex type {urn:oasis:names:tc:SAML:2.0:metadata}ExtensionsType with content type ELEMENT_ONLY
class ExtensionsType (pyxb.binding.basis.complexTypeDefinition):
    _TypeDefinition = None
    _ContentTypeTag = pyxb.binding.basis.complexTypeDefinition._CT_ELEMENT_ONLY
    _Abstract = False
    _ExpandedName = pyxb.namespace.ExpandedName(Namespace, u'ExtensionsType')
    _DefinitionLocation = pyxb.utils.utility.Location('/tmp/pyxbdist.RHB65sy/PyXB-1.1.5/pyxb/bundles/saml20/schemas/metadata.xsd', 52, 4)
    # Base type is pyxb.binding.datatypes.anyType
    _HasWildcardElement = True

    _ElementMap = {
        
    }
    _AttributeMap = {
        
    }
Namespace.addCategoryObject('typeBinding', u'ExtensionsType', ExtensionsType)


# Complex type {urn:oasis:names:tc:SAML:2.0:metadata}KeyDescriptorType with content type ELEMENT_ONLY
class KeyDescriptorType (pyxb.binding.basis.complexTypeDefinition):
    _TypeDefinition = None
    _ContentTypeTag = pyxb.binding.basis.complexTypeDefinition._CT_ELEMENT_ONLY
    _Abstract = False
    _ExpandedName = pyxb.namespace.ExpandedName(Namespace, u'KeyDescriptorType')
    _DefinitionLocation = pyxb.utils.utility.Location('/tmp/pyxbdist.RHB65sy/PyXB-1.1.5/pyxb/bundles/saml20/schemas/metadata.xsd', 191, 4)
    # Base type is pyxb.binding.datatypes.anyType
    
    # Element {http://www.w3.org/2000/09/xmldsig#}KeyInfo uses Python identifier KeyInfo
    __KeyInfo = pyxb.binding.content.ElementUse(pyxb.namespace.ExpandedName(pyxb.namespace.NamespaceForURI(u'http://www.w3.org/2000/09/xmldsig#'), u'KeyInfo'), 'KeyInfo', '__urnoasisnamestcSAML2_0metadata_KeyDescriptorType_httpwww_w3_org200009xmldsigKeyInfo', False)
    __KeyInfo._DeclarationLocation = pyxb.utils.utility.Location('/tmp/pyxbdist.RHB65sy/PyXB-1.1.5/pyxb/bundles/wssplat/schemas/ds.xsd', 144, 0)
    __KeyInfo._UseLocation = pyxb.utils.utility.Location('/tmp/pyxbdist.RHB65sy/PyXB-1.1.5/pyxb/bundles/saml20/schemas/metadata.xsd', 192, 8)

    
    KeyInfo = property(__KeyInfo.value, __KeyInfo.set, None, None)

    
    # Element {urn:oasis:names:tc:SAML:2.0:metadata}EncryptionMethod uses Python identifier EncryptionMethod
    __EncryptionMethod = pyxb.binding.content.ElementUse(pyxb.namespace.ExpandedName(Namespace, u'EncryptionMethod'), 'EncryptionMethod', '__urnoasisnamestcSAML2_0metadata_KeyDescriptorType_urnoasisnamestcSAML2_0metadataEncryptionMethod', True)
    __EncryptionMethod._DeclarationLocation = pyxb.utils.utility.Location('/tmp/pyxbdist.RHB65sy/PyXB-1.1.5/pyxb/bundles/saml20/schemas/metadata.xsd', 204, 4)
    __EncryptionMethod._UseLocation = pyxb.utils.utility.Location('/tmp/pyxbdist.RHB65sy/PyXB-1.1.5/pyxb/bundles/saml20/schemas/metadata.xsd', 192, 8)

    
    EncryptionMethod = property(__EncryptionMethod.value, __EncryptionMethod.set, None, None)

    
    # Attribute use uses Python identifier use
    __use = pyxb.binding.content.AttributeUse(pyxb.namespace.ExpandedName(None, u'use'), 'use', '__urnoasisnamestcSAML2_0metadata_KeyDescriptorType_use', KeyTypes)
    __use._DeclarationLocation = pyxb.utils.utility.Location('/tmp/pyxbdist.RHB65sy/PyXB-1.1.5/pyxb/bundles/saml20/schemas/metadata.xsd', 196, 8)
    __use._UseLocation = pyxb.utils.utility.Location('/tmp/pyxbdist.RHB65sy/PyXB-1.1.5/pyxb/bundles/saml20/schemas/metadata.xsd', 196, 8)
    
    use = property(__use.value, __use.set, None, None)


    _ElementMap = {
        __KeyInfo.name() : __KeyInfo,
        __EncryptionMethod.name() : __EncryptionMethod
    }
    _AttributeMap = {
        __use.name() : __use
    }
Namespace.addCategoryObject('typeBinding', u'KeyDescriptorType', KeyDescriptorType)


# Complex type {urn:oasis:names:tc:SAML:2.0:metadata}EntitiesDescriptorType with content type ELEMENT_ONLY
class EntitiesDescriptorType (pyxb.binding.basis.complexTypeDefinition):
    _TypeDefinition = None
    _ContentTypeTag = pyxb.binding.basis.complexTypeDefinition._CT_ELEMENT_ONLY
    _Abstract = False
    _ExpandedName = pyxb.namespace.ExpandedName(Namespace, u'EntitiesDescriptorType')
    _DefinitionLocation = pyxb.utils.utility.Location('/tmp/pyxbdist.RHB65sy/PyXB-1.1.5/pyxb/bundles/saml20/schemas/metadata.xsd', 78, 4)
    # Base type is pyxb.binding.datatypes.anyType
    
    # Element {http://www.w3.org/2000/09/xmldsig#}Signature uses Python identifier Signature
    __Signature = pyxb.binding.content.ElementUse(pyxb.namespace.ExpandedName(pyxb.namespace.NamespaceForURI(u'http://www.w3.org/2000/09/xmldsig#'), u'Signature'), 'Signature', '__urnoasisnamestcSAML2_0metadata_EntitiesDescriptorType_httpwww_w3_org200009xmldsigSignature', False)
    __Signature._DeclarationLocation = pyxb.utils.utility.Location('/tmp/pyxbdist.RHB65sy/PyXB-1.1.5/pyxb/bundles/wssplat/schemas/ds.xsd', 43, 0)
    __Signature._UseLocation = pyxb.utils.utility.Location('/tmp/pyxbdist.RHB65sy/PyXB-1.1.5/pyxb/bundles/saml20/schemas/metadata.xsd', 79, 8)

    
    Signature = property(__Signature.value, __Signature.set, None, None)

    
    # Element {urn:oasis:names:tc:SAML:2.0:metadata}EntityDescriptor uses Python identifier EntityDescriptor
    __EntityDescriptor = pyxb.binding.content.ElementUse(pyxb.namespace.ExpandedName(Namespace, u'EntityDescriptor'), 'EntityDescriptor', '__urnoasisnamestcSAML2_0metadata_EntitiesDescriptorType_urnoasisnamestcSAML2_0metadataEntityDescriptor', True)
    __EntityDescriptor._DeclarationLocation = pyxb.utils.utility.Location('/tmp/pyxbdist.RHB65sy/PyXB-1.1.5/pyxb/bundles/saml20/schemas/metadata.xsd', 93, 4)
    __EntityDescriptor._UseLocation = pyxb.utils.utility.Location('/tmp/pyxbdist.RHB65sy/PyXB-1.1.5/pyxb/bundles/saml20/schemas/metadata.xsd', 79, 8)

    
    EntityDescriptor = property(__EntityDescriptor.value, __EntityDescriptor.set, None, None)

    
    # Element {urn:oasis:names:tc:SAML:2.0:metadata}Extensions uses Python identifier Extensions
    __Extensions = pyxb.binding.content.ElementUse(pyxb.namespace.ExpandedName(Namespace, u'Extensions'), 'Extensions', '__urnoasisnamestcSAML2_0metadata_EntitiesDescriptorType_urnoasisnamestcSAML2_0metadataExtensions', False)
    __Extensions._DeclarationLocation = pyxb.utils.utility.Location('/tmp/pyxbdist.RHB65sy/PyXB-1.1.5/pyxb/bundles/saml20/schemas/metadata.xsd', 51, 4)
    __Extensions._UseLocation = pyxb.utils.utility.Location('/tmp/pyxbdist.RHB65sy/PyXB-1.1.5/pyxb/bundles/saml20/schemas/metadata.xsd', 79, 8)

    
    Extensions = property(__Extensions.value, __Extensions.set, None, None)

    
    # Element {urn:oasis:names:tc:SAML:2.0:metadata}EntitiesDescriptor uses Python identifier EntitiesDescriptor
    __EntitiesDescriptor = pyxb.binding.content.ElementUse(pyxb.namespace.ExpandedName(Namespace, u'EntitiesDescriptor'), 'EntitiesDescriptor', '__urnoasisnamestcSAML2_0metadata_EntitiesDescriptorType_urnoasisnamestcSAML2_0metadataEntitiesDescriptor', True)
    __EntitiesDescriptor._DeclarationLocation = pyxb.utils.utility.Location('/tmp/pyxbdist.RHB65sy/PyXB-1.1.5/pyxb/bundles/saml20/schemas/metadata.xsd', 77, 4)
    __EntitiesDescriptor._UseLocation = pyxb.utils.utility.Location('/tmp/pyxbdist.RHB65sy/PyXB-1.1.5/pyxb/bundles/saml20/schemas/metadata.xsd', 79, 8)

    
    EntitiesDescriptor = property(__EntitiesDescriptor.value, __EntitiesDescriptor.set, None, None)

    
    # Attribute cacheDuration uses Python identifier cacheDuration
    __cacheDuration = pyxb.binding.content.AttributeUse(pyxb.namespace.ExpandedName(None, u'cacheDuration'), 'cacheDuration', '__urnoasisnamestcSAML2_0metadata_EntitiesDescriptorType_cacheDuration', pyxb.binding.datatypes.duration)
    __cacheDuration._DeclarationLocation = pyxb.utils.utility.Location('/tmp/pyxbdist.RHB65sy/PyXB-1.1.5/pyxb/bundles/saml20/schemas/metadata.xsd', 88, 8)
    __cacheDuration._UseLocation = pyxb.utils.utility.Location('/tmp/pyxbdist.RHB65sy/PyXB-1.1.5/pyxb/bundles/saml20/schemas/metadata.xsd', 88, 8)
    
    cacheDuration = property(__cacheDuration.value, __cacheDuration.set, None, None)

    
    # Attribute Name uses Python identifier Name
    __Name = pyxb.binding.content.AttributeUse(pyxb.namespace.ExpandedName(None, u'Name'), 'Name', '__urnoasisnamestcSAML2_0metadata_EntitiesDescriptorType_Name', pyxb.binding.datatypes.string)
    __Name._DeclarationLocation = pyxb.utils.utility.Location('/tmp/pyxbdist.RHB65sy/PyXB-1.1.5/pyxb/bundles/saml20/schemas/metadata.xsd', 90, 8)
    __Name._UseLocation = pyxb.utils.utility.Location('/tmp/pyxbdist.RHB65sy/PyXB-1.1.5/pyxb/bundles/saml20/schemas/metadata.xsd', 90, 8)
    
    Name = property(__Name.value, __Name.set, None, None)

    
    # Attribute ID uses Python identifier ID
    __ID = pyxb.binding.content.AttributeUse(pyxb.namespace.ExpandedName(None, u'ID'), 'ID', '__urnoasisnamestcSAML2_0metadata_EntitiesDescriptorType_ID', pyxb.binding.datatypes.ID)
    __ID._DeclarationLocation = pyxb.utils.utility.Location('/tmp/pyxbdist.RHB65sy/PyXB-1.1.5/pyxb/bundles/saml20/schemas/metadata.xsd', 89, 8)
    __ID._UseLocation = pyxb.utils.utility.Location('/tmp/pyxbdist.RHB65sy/PyXB-1.1.5/pyxb/bundles/saml20/schemas/metadata.xsd', 89, 8)
    
    ID = property(__ID.value, __ID.set, None, None)

    
    # Attribute validUntil uses Python identifier validUntil
    __validUntil = pyxb.binding.content.AttributeUse(pyxb.namespace.ExpandedName(None, u'validUntil'), 'validUntil', '__urnoasisnamestcSAML2_0metadata_EntitiesDescriptorType_validUntil', pyxb.binding.datatypes.dateTime)
    __validUntil._DeclarationLocation = pyxb.utils.utility.Location('/tmp/pyxbdist.RHB65sy/PyXB-1.1.5/pyxb/bundles/saml20/schemas/metadata.xsd', 87, 8)
    __validUntil._UseLocation = pyxb.utils.utility.Location('/tmp/pyxbdist.RHB65sy/PyXB-1.1.5/pyxb/bundles/saml20/schemas/metadata.xsd', 87, 8)
    
    validUntil = property(__validUntil.value, __validUntil.set, None, None)


    _ElementMap = {
        __Signature.name() : __Signature,
        __EntityDescriptor.name() : __EntityDescriptor,
        __Extensions.name() : __Extensions,
        __EntitiesDescriptor.name() : __EntitiesDescriptor
    }
    _AttributeMap = {
        __cacheDuration.name() : __cacheDuration,
        __Name.name() : __Name,
        __ID.name() : __ID,
        __validUntil.name() : __validUntil
    }
Namespace.addCategoryObject('typeBinding', u'EntitiesDescriptorType', EntitiesDescriptorType)


# Complex type {urn:oasis:names:tc:SAML:2.0:metadata}ContactType with content type ELEMENT_ONLY
class ContactType (pyxb.binding.basis.complexTypeDefinition):
    _TypeDefinition = None
    _ContentTypeTag = pyxb.binding.basis.complexTypeDefinition._CT_ELEMENT_ONLY
    _Abstract = False
    _ExpandedName = pyxb.namespace.ExpandedName(Namespace, u'ContactType')
    _DefinitionLocation = pyxb.utils.utility.Location('/tmp/pyxbdist.RHB65sy/PyXB-1.1.5/pyxb/bundles/saml20/schemas/metadata.xsd', 134, 4)
    # Base type is pyxb.binding.datatypes.anyType
    
    # Element {urn:oasis:names:tc:SAML:2.0:metadata}EmailAddress uses Python identifier EmailAddress
    __EmailAddress = pyxb.binding.content.ElementUse(pyxb.namespace.ExpandedName(Namespace, u'EmailAddress'), 'EmailAddress', '__urnoasisnamestcSAML2_0metadata_ContactType_urnoasisnamestcSAML2_0metadataEmailAddress', True)
    __EmailAddress._DeclarationLocation = pyxb.utils.utility.Location('/tmp/pyxbdist.RHB65sy/PyXB-1.1.5/pyxb/bundles/saml20/schemas/metadata.xsd', 149, 4)
    __EmailAddress._UseLocation = pyxb.utils.utility.Location('/tmp/pyxbdist.RHB65sy/PyXB-1.1.5/pyxb/bundles/saml20/schemas/metadata.xsd', 135, 8)

    
    EmailAddress = property(__EmailAddress.value, __EmailAddress.set, None, None)

    
    # Element {urn:oasis:names:tc:SAML:2.0:metadata}Extensions uses Python identifier Extensions
    __Extensions = pyxb.binding.content.ElementUse(pyxb.namespace.ExpandedName(Namespace, u'Extensions'), 'Extensions', '__urnoasisnamestcSAML2_0metadata_ContactType_urnoasisnamestcSAML2_0metadataExtensions', False)
    __Extensions._DeclarationLocation = pyxb.utils.utility.Location('/tmp/pyxbdist.RHB65sy/PyXB-1.1.5/pyxb/bundles/saml20/schemas/metadata.xsd', 51, 4)
    __Extensions._UseLocation = pyxb.utils.utility.Location('/tmp/pyxbdist.RHB65sy/PyXB-1.1.5/pyxb/bundles/saml20/schemas/metadata.xsd', 135, 8)

    
    Extensions = property(__Extensions.value, __Extensions.set, None, None)

    
    # Element {urn:oasis:names:tc:SAML:2.0:metadata}GivenName uses Python identifier GivenName
    __GivenName = pyxb.binding.content.ElementUse(pyxb.namespace.ExpandedName(Namespace, u'GivenName'), 'GivenName', '__urnoasisnamestcSAML2_0metadata_ContactType_urnoasisnamestcSAML2_0metadataGivenName', False)
    __GivenName._DeclarationLocation = pyxb.utils.utility.Location('/tmp/pyxbdist.RHB65sy/PyXB-1.1.5/pyxb/bundles/saml20/schemas/metadata.xsd', 147, 4)
    __GivenName._UseLocation = pyxb.utils.utility.Location('/tmp/pyxbdist.RHB65sy/PyXB-1.1.5/pyxb/bundles/saml20/schemas/metadata.xsd', 135, 8)

    
    GivenName = property(__GivenName.value, __GivenName.set, None, None)

    
    # Element {urn:oasis:names:tc:SAML:2.0:metadata}TelephoneNumber uses Python identifier TelephoneNumber
    __TelephoneNumber = pyxb.binding.content.ElementUse(pyxb.namespace.ExpandedName(Namespace, u'TelephoneNumber'), 'TelephoneNumber', '__urnoasisnamestcSAML2_0metadata_ContactType_urnoasisnamestcSAML2_0metadataTelephoneNumber', True)
    __TelephoneNumber._DeclarationLocation = pyxb.utils.utility.Location('/tmp/pyxbdist.RHB65sy/PyXB-1.1.5/pyxb/bundles/saml20/schemas/metadata.xsd', 150, 4)
    __TelephoneNumber._UseLocation = pyxb.utils.utility.Location('/tmp/pyxbdist.RHB65sy/PyXB-1.1.5/pyxb/bundles/saml20/schemas/metadata.xsd', 135, 8)

    
    TelephoneNumber = property(__TelephoneNumber.value, __TelephoneNumber.set, None, None)

    
    # Element {urn:oasis:names:tc:SAML:2.0:metadata}SurName uses Python identifier SurName
    __SurName = pyxb.binding.content.ElementUse(pyxb.namespace.ExpandedName(Namespace, u'SurName'), 'SurName', '__urnoasisnamestcSAML2_0metadata_ContactType_urnoasisnamestcSAML2_0metadataSurName', False)
    __SurName._DeclarationLocation = pyxb.utils.utility.Location('/tmp/pyxbdist.RHB65sy/PyXB-1.1.5/pyxb/bundles/saml20/schemas/metadata.xsd', 148, 4)
    __SurName._UseLocation = pyxb.utils.utility.Location('/tmp/pyxbdist.RHB65sy/PyXB-1.1.5/pyxb/bundles/saml20/schemas/metadata.xsd', 135, 8)

    
    SurName = property(__SurName.value, __SurName.set, None, None)

    
    # Element {urn:oasis:names:tc:SAML:2.0:metadata}Company uses Python identifier Company
    __Company = pyxb.binding.content.ElementUse(pyxb.namespace.ExpandedName(Namespace, u'Company'), 'Company', '__urnoasisnamestcSAML2_0metadata_ContactType_urnoasisnamestcSAML2_0metadataCompany', False)
    __Company._DeclarationLocation = pyxb.utils.utility.Location('/tmp/pyxbdist.RHB65sy/PyXB-1.1.5/pyxb/bundles/saml20/schemas/metadata.xsd', 146, 4)
    __Company._UseLocation = pyxb.utils.utility.Location('/tmp/pyxbdist.RHB65sy/PyXB-1.1.5/pyxb/bundles/saml20/schemas/metadata.xsd', 135, 8)

    
    Company = property(__Company.value, __Company.set, None, None)

    
    # Attribute contactType uses Python identifier contactType
    __contactType = pyxb.binding.content.AttributeUse(pyxb.namespace.ExpandedName(None, u'contactType'), 'contactType', '__urnoasisnamestcSAML2_0metadata_ContactType_contactType', ContactTypeType, required=True)
    __contactType._DeclarationLocation = pyxb.utils.utility.Location('/tmp/pyxbdist.RHB65sy/PyXB-1.1.5/pyxb/bundles/saml20/schemas/metadata.xsd', 143, 8)
    __contactType._UseLocation = pyxb.utils.utility.Location('/tmp/pyxbdist.RHB65sy/PyXB-1.1.5/pyxb/bundles/saml20/schemas/metadata.xsd', 143, 8)
    
    contactType = property(__contactType.value, __contactType.set, None, None)

    _AttributeWildcard = pyxb.binding.content.Wildcard(process_contents=pyxb.binding.content.Wildcard.PC_lax, namespace_constraint=(pyxb.binding.content.Wildcard.NC_not, u'urn:oasis:names:tc:SAML:2.0:metadata'))

    _ElementMap = {
        __EmailAddress.name() : __EmailAddress,
        __Extensions.name() : __Extensions,
        __GivenName.name() : __GivenName,
        __TelephoneNumber.name() : __TelephoneNumber,
        __SurName.name() : __SurName,
        __Company.name() : __Company
    }
    _AttributeMap = {
        __contactType.name() : __contactType
    }
Namespace.addCategoryObject('typeBinding', u'ContactType', ContactType)


# Complex type {urn:oasis:names:tc:SAML:2.0:metadata}AffiliationDescriptorType with content type ELEMENT_ONLY
class AffiliationDescriptorType (pyxb.binding.basis.complexTypeDefinition):
    _TypeDefinition = None
    _ContentTypeTag = pyxb.binding.basis.complexTypeDefinition._CT_ELEMENT_ONLY
    _Abstract = False
    _ExpandedName = pyxb.namespace.ExpandedName(Namespace, u'AffiliationDescriptorType')
    _DefinitionLocation = pyxb.utils.utility.Location('/tmp/pyxbdist.RHB65sy/PyXB-1.1.5/pyxb/bundles/saml20/schemas/metadata.xsd', 323, 4)
    # Base type is pyxb.binding.datatypes.anyType
    
    # Element {urn:oasis:names:tc:SAML:2.0:metadata}AffiliateMember uses Python identifier AffiliateMember
    __AffiliateMember = pyxb.binding.content.ElementUse(pyxb.namespace.ExpandedName(Namespace, u'AffiliateMember'), 'AffiliateMember', '__urnoasisnamestcSAML2_0metadata_AffiliationDescriptorType_urnoasisnamestcSAML2_0metadataAffiliateMember', True)
    __AffiliateMember._DeclarationLocation = pyxb.utils.utility.Location('/tmp/pyxbdist.RHB65sy/PyXB-1.1.5/pyxb/bundles/saml20/schemas/metadata.xsd', 336, 4)
    __AffiliateMember._UseLocation = pyxb.utils.utility.Location('/tmp/pyxbdist.RHB65sy/PyXB-1.1.5/pyxb/bundles/saml20/schemas/metadata.xsd', 324, 8)

    
    AffiliateMember = property(__AffiliateMember.value, __AffiliateMember.set, None, None)

    
    # Element {http://www.w3.org/2000/09/xmldsig#}Signature uses Python identifier Signature
    __Signature = pyxb.binding.content.ElementUse(pyxb.namespace.ExpandedName(pyxb.namespace.NamespaceForURI(u'http://www.w3.org/2000/09/xmldsig#'), u'Signature'), 'Signature', '__urnoasisnamestcSAML2_0metadata_AffiliationDescriptorType_httpwww_w3_org200009xmldsigSignature', False)
    __Signature._DeclarationLocation = pyxb.utils.utility.Location('/tmp/pyxbdist.RHB65sy/PyXB-1.1.5/pyxb/bundles/wssplat/schemas/ds.xsd', 43, 0)
    __Signature._UseLocation = pyxb.utils.utility.Location('/tmp/pyxbdist.RHB65sy/PyXB-1.1.5/pyxb/bundles/saml20/schemas/metadata.xsd', 324, 8)

    
    Signature = property(__Signature.value, __Signature.set, None, None)

    
    # Element {urn:oasis:names:tc:SAML:2.0:metadata}Extensions uses Python identifier Extensions
    __Extensions = pyxb.binding.content.ElementUse(pyxb.namespace.ExpandedName(Namespace, u'Extensions'), 'Extensions', '__urnoasisnamestcSAML2_0metadata_AffiliationDescriptorType_urnoasisnamestcSAML2_0metadataExtensions', False)
    __Extensions._DeclarationLocation = pyxb.utils.utility.Location('/tmp/pyxbdist.RHB65sy/PyXB-1.1.5/pyxb/bundles/saml20/schemas/metadata.xsd', 51, 4)
    __Extensions._UseLocation = pyxb.utils.utility.Location('/tmp/pyxbdist.RHB65sy/PyXB-1.1.5/pyxb/bundles/saml20/schemas/metadata.xsd', 324, 8)

    
    Extensions = property(__Extensions.value, __Extensions.set, None, None)

    
    # Element {urn:oasis:names:tc:SAML:2.0:metadata}KeyDescriptor uses Python identifier KeyDescriptor
    __KeyDescriptor = pyxb.binding.content.ElementUse(pyxb.namespace.ExpandedName(Namespace, u'KeyDescriptor'), 'KeyDescriptor', '__urnoasisnamestcSAML2_0metadata_AffiliationDescriptorType_urnoasisnamestcSAML2_0metadataKeyDescriptor', True)
    __KeyDescriptor._DeclarationLocation = pyxb.utils.utility.Location('/tmp/pyxbdist.RHB65sy/PyXB-1.1.5/pyxb/bundles/saml20/schemas/metadata.xsd', 190, 4)
    __KeyDescriptor._UseLocation = pyxb.utils.utility.Location('/tmp/pyxbdist.RHB65sy/PyXB-1.1.5/pyxb/bundles/saml20/schemas/metadata.xsd', 324, 8)

    
    KeyDescriptor = property(__KeyDescriptor.value, __KeyDescriptor.set, None, None)

    
    # Attribute affiliationOwnerID uses Python identifier affiliationOwnerID
    __affiliationOwnerID = pyxb.binding.content.AttributeUse(pyxb.namespace.ExpandedName(None, u'affiliationOwnerID'), 'affiliationOwnerID', '__urnoasisnamestcSAML2_0metadata_AffiliationDescriptorType_affiliationOwnerID', entityIDType, required=True)
    __affiliationOwnerID._DeclarationLocation = pyxb.utils.utility.Location('/tmp/pyxbdist.RHB65sy/PyXB-1.1.5/pyxb/bundles/saml20/schemas/metadata.xsd', 330, 8)
    __affiliationOwnerID._UseLocation = pyxb.utils.utility.Location('/tmp/pyxbdist.RHB65sy/PyXB-1.1.5/pyxb/bundles/saml20/schemas/metadata.xsd', 330, 8)
    
    affiliationOwnerID = property(__affiliationOwnerID.value, __affiliationOwnerID.set, None, None)

    
    # Attribute validUntil uses Python identifier validUntil
    __validUntil = pyxb.binding.content.AttributeUse(pyxb.namespace.ExpandedName(None, u'validUntil'), 'validUntil', '__urnoasisnamestcSAML2_0metadata_AffiliationDescriptorType_validUntil', pyxb.binding.datatypes.dateTime)
    __validUntil._DeclarationLocation = pyxb.utils.utility.Location('/tmp/pyxbdist.RHB65sy/PyXB-1.1.5/pyxb/bundles/saml20/schemas/metadata.xsd', 331, 8)
    __validUntil._UseLocation = pyxb.utils.utility.Location('/tmp/pyxbdist.RHB65sy/PyXB-1.1.5/pyxb/bundles/saml20/schemas/metadata.xsd', 331, 8)
    
    validUntil = property(__validUntil.value, __validUntil.set, None, None)

    
    # Attribute cacheDuration uses Python identifier cacheDuration
    __cacheDuration = pyxb.binding.content.AttributeUse(pyxb.namespace.ExpandedName(None, u'cacheDuration'), 'cacheDuration', '__urnoasisnamestcSAML2_0metadata_AffiliationDescriptorType_cacheDuration', pyxb.binding.datatypes.duration)
    __cacheDuration._DeclarationLocation = pyxb.utils.utility.Location('/tmp/pyxbdist.RHB65sy/PyXB-1.1.5/pyxb/bundles/saml20/schemas/metadata.xsd', 332, 8)
    __cacheDuration._UseLocation = pyxb.utils.utility.Location('/tmp/pyxbdist.RHB65sy/PyXB-1.1.5/pyxb/bundles/saml20/schemas/metadata.xsd', 332, 8)
    
    cacheDuration = property(__cacheDuration.value, __cacheDuration.set, None, None)

    
    # Attribute ID uses Python identifier ID
    __ID = pyxb.binding.content.AttributeUse(pyxb.namespace.ExpandedName(None, u'ID'), 'ID', '__urnoasisnamestcSAML2_0metadata_AffiliationDescriptorType_ID', pyxb.binding.datatypes.ID)
    __ID._DeclarationLocation = pyxb.utils.utility.Location('/tmp/pyxbdist.RHB65sy/PyXB-1.1.5/pyxb/bundles/saml20/schemas/metadata.xsd', 333, 8)
    __ID._UseLocation = pyxb.utils.utility.Location('/tmp/pyxbdist.RHB65sy/PyXB-1.1.5/pyxb/bundles/saml20/schemas/metadata.xsd', 333, 8)
    
    ID = property(__ID.value, __ID.set, None, None)

    _AttributeWildcard = pyxb.binding.content.Wildcard(process_contents=pyxb.binding.content.Wildcard.PC_lax, namespace_constraint=(pyxb.binding.content.Wildcard.NC_not, u'urn:oasis:names:tc:SAML:2.0:metadata'))

    _ElementMap = {
        __AffiliateMember.name() : __AffiliateMember,
        __Signature.name() : __Signature,
        __Extensions.name() : __Extensions,
        __KeyDescriptor.name() : __KeyDescriptor
    }
    _AttributeMap = {
        __affiliationOwnerID.name() : __affiliationOwnerID,
        __validUntil.name() : __validUntil,
        __cacheDuration.name() : __cacheDuration,
        __ID.name() : __ID
    }
Namespace.addCategoryObject('typeBinding', u'AffiliationDescriptorType', AffiliationDescriptorType)


# Complex type {urn:oasis:names:tc:SAML:2.0:metadata}EntityDescriptorType with content type ELEMENT_ONLY
class EntityDescriptorType (pyxb.binding.basis.complexTypeDefinition):
    _TypeDefinition = None
    _ContentTypeTag = pyxb.binding.basis.complexTypeDefinition._CT_ELEMENT_ONLY
    _Abstract = False
    _ExpandedName = pyxb.namespace.ExpandedName(Namespace, u'EntityDescriptorType')
    _DefinitionLocation = pyxb.utils.utility.Location('/tmp/pyxbdist.RHB65sy/PyXB-1.1.5/pyxb/bundles/saml20/schemas/metadata.xsd', 94, 4)
    # Base type is pyxb.binding.datatypes.anyType
    
    # Element {urn:oasis:names:tc:SAML:2.0:metadata}SPSSODescriptor uses Python identifier SPSSODescriptor
    __SPSSODescriptor = pyxb.binding.content.ElementUse(pyxb.namespace.ExpandedName(Namespace, u'SPSSODescriptor'), 'SPSSODescriptor', '__urnoasisnamestcSAML2_0metadata_EntityDescriptorType_urnoasisnamestcSAML2_0metadataSPSSODescriptor', True)
    __SPSSODescriptor._DeclarationLocation = pyxb.utils.utility.Location('/tmp/pyxbdist.RHB65sy/PyXB-1.1.5/pyxb/bundles/saml20/schemas/metadata.xsd', 243, 4)
    __SPSSODescriptor._UseLocation = pyxb.utils.utility.Location('/tmp/pyxbdist.RHB65sy/PyXB-1.1.5/pyxb/bundles/saml20/schemas/metadata.xsd', 95, 8)

    
    SPSSODescriptor = property(__SPSSODescriptor.value, __SPSSODescriptor.set, None, None)

    
    # Element {urn:oasis:names:tc:SAML:2.0:metadata}PDPDescriptor uses Python identifier PDPDescriptor
    __PDPDescriptor = pyxb.binding.content.ElementUse(pyxb.namespace.ExpandedName(Namespace, u'PDPDescriptor'), 'PDPDescriptor', '__urnoasisnamestcSAML2_0metadata_EntityDescriptorType_urnoasisnamestcSAML2_0metadataPDPDescriptor', True)
    __PDPDescriptor._DeclarationLocation = pyxb.utils.utility.Location('/tmp/pyxbdist.RHB65sy/PyXB-1.1.5/pyxb/bundles/saml20/schemas/metadata.xsd', 292, 4)
    __PDPDescriptor._UseLocation = pyxb.utils.utility.Location('/tmp/pyxbdist.RHB65sy/PyXB-1.1.5/pyxb/bundles/saml20/schemas/metadata.xsd', 95, 8)

    
    PDPDescriptor = property(__PDPDescriptor.value, __PDPDescriptor.set, None, None)

    
    # Element {urn:oasis:names:tc:SAML:2.0:metadata}AffiliationDescriptor uses Python identifier AffiliationDescriptor
    __AffiliationDescriptor = pyxb.binding.content.ElementUse(pyxb.namespace.ExpandedName(Namespace, u'AffiliationDescriptor'), 'AffiliationDescriptor', '__urnoasisnamestcSAML2_0metadata_EntityDescriptorType_urnoasisnamestcSAML2_0metadataAffiliationDescriptor', False)
    __AffiliationDescriptor._DeclarationLocation = pyxb.utils.utility.Location('/tmp/pyxbdist.RHB65sy/PyXB-1.1.5/pyxb/bundles/saml20/schemas/metadata.xsd', 322, 4)
    __AffiliationDescriptor._UseLocation = pyxb.utils.utility.Location('/tmp/pyxbdist.RHB65sy/PyXB-1.1.5/pyxb/bundles/saml20/schemas/metadata.xsd', 95, 8)

    
    AffiliationDescriptor = property(__AffiliationDescriptor.value, __AffiliationDescriptor.set, None, None)

    
    # Element {urn:oasis:names:tc:SAML:2.0:metadata}ContactPerson uses Python identifier ContactPerson
    __ContactPerson = pyxb.binding.content.ElementUse(pyxb.namespace.ExpandedName(Namespace, u'ContactPerson'), 'ContactPerson', '__urnoasisnamestcSAML2_0metadata_EntityDescriptorType_urnoasisnamestcSAML2_0metadataContactPerson', True)
    __ContactPerson._DeclarationLocation = pyxb.utils.utility.Location('/tmp/pyxbdist.RHB65sy/PyXB-1.1.5/pyxb/bundles/saml20/schemas/metadata.xsd', 133, 4)
    __ContactPerson._UseLocation = pyxb.utils.utility.Location('/tmp/pyxbdist.RHB65sy/PyXB-1.1.5/pyxb/bundles/saml20/schemas/metadata.xsd', 95, 8)

    
    ContactPerson = property(__ContactPerson.value, __ContactPerson.set, None, None)

    
    # Element {urn:oasis:names:tc:SAML:2.0:metadata}RoleDescriptor uses Python identifier RoleDescriptor
    __RoleDescriptor = pyxb.binding.content.ElementUse(pyxb.namespace.ExpandedName(Namespace, u'RoleDescriptor'), 'RoleDescriptor', '__urnoasisnamestcSAML2_0metadata_EntityDescriptorType_urnoasisnamestcSAML2_0metadataRoleDescriptor', True)
    __RoleDescriptor._DeclarationLocation = pyxb.utils.utility.Location('/tmp/pyxbdist.RHB65sy/PyXB-1.1.5/pyxb/bundles/saml20/schemas/metadata.xsd', 170, 4)
    __RoleDescriptor._UseLocation = pyxb.utils.utility.Location('/tmp/pyxbdist.RHB65sy/PyXB-1.1.5/pyxb/bundles/saml20/schemas/metadata.xsd', 95, 8)

    
    RoleDescriptor = property(__RoleDescriptor.value, __RoleDescriptor.set, None, None)

    
    # Element {urn:oasis:names:tc:SAML:2.0:metadata}AdditionalMetadataLocation uses Python identifier AdditionalMetadataLocation
    __AdditionalMetadataLocation = pyxb.binding.content.ElementUse(pyxb.namespace.ExpandedName(Namespace, u'AdditionalMetadataLocation'), 'AdditionalMetadataLocation', '__urnoasisnamestcSAML2_0metadata_EntityDescriptorType_urnoasisnamestcSAML2_0metadataAdditionalMetadataLocation', True)
    __AdditionalMetadataLocation._DeclarationLocation = pyxb.utils.utility.Location('/tmp/pyxbdist.RHB65sy/PyXB-1.1.5/pyxb/bundles/saml20/schemas/metadata.xsd', 161, 4)
    __AdditionalMetadataLocation._UseLocation = pyxb.utils.utility.Location('/tmp/pyxbdist.RHB65sy/PyXB-1.1.5/pyxb/bundles/saml20/schemas/metadata.xsd', 95, 8)

    
    AdditionalMetadataLocation = property(__AdditionalMetadataLocation.value, __AdditionalMetadataLocation.set, None, None)

    
    # Element {urn:oasis:names:tc:SAML:2.0:metadata}AuthnAuthorityDescriptor uses Python identifier AuthnAuthorityDescriptor
    __AuthnAuthorityDescriptor = pyxb.binding.content.ElementUse(pyxb.namespace.ExpandedName(Namespace, u'AuthnAuthorityDescriptor'), 'AuthnAuthorityDescriptor', '__urnoasisnamestcSAML2_0metadata_EntityDescriptorType_urnoasisnamestcSAML2_0metadataAuthnAuthorityDescriptor', True)
    __AuthnAuthorityDescriptor._DeclarationLocation = pyxb.utils.utility.Location('/tmp/pyxbdist.RHB65sy/PyXB-1.1.5/pyxb/bundles/saml20/schemas/metadata.xsd', 278, 4)
    __AuthnAuthorityDescriptor._UseLocation = pyxb.utils.utility.Location('/tmp/pyxbdist.RHB65sy/PyXB-1.1.5/pyxb/bundles/saml20/schemas/metadata.xsd', 95, 8)

    
    AuthnAuthorityDescriptor = property(__AuthnAuthorityDescriptor.value, __AuthnAuthorityDescriptor.set, None, None)

    
    # Element {urn:oasis:names:tc:SAML:2.0:metadata}IDPSSODescriptor uses Python identifier IDPSSODescriptor
    __IDPSSODescriptor = pyxb.binding.content.ElementUse(pyxb.namespace.ExpandedName(Namespace, u'IDPSSODescriptor'), 'IDPSSODescriptor', '__urnoasisnamestcSAML2_0metadata_EntityDescriptorType_urnoasisnamestcSAML2_0metadataIDPSSODescriptor', True)
    __IDPSSODescriptor._DeclarationLocation = pyxb.utils.utility.Location('/tmp/pyxbdist.RHB65sy/PyXB-1.1.5/pyxb/bundles/saml20/schemas/metadata.xsd', 223, 4)
    __IDPSSODescriptor._UseLocation = pyxb.utils.utility.Location('/tmp/pyxbdist.RHB65sy/PyXB-1.1.5/pyxb/bundles/saml20/schemas/metadata.xsd', 95, 8)

    
    IDPSSODescriptor = property(__IDPSSODescriptor.value, __IDPSSODescriptor.set, None, None)

    
    # Element {urn:oasis:names:tc:SAML:2.0:metadata}AttributeAuthorityDescriptor uses Python identifier AttributeAuthorityDescriptor
    __AttributeAuthorityDescriptor = pyxb.binding.content.ElementUse(pyxb.namespace.ExpandedName(Namespace, u'AttributeAuthorityDescriptor'), 'AttributeAuthorityDescriptor', '__urnoasisnamestcSAML2_0metadata_EntityDescriptorType_urnoasisnamestcSAML2_0metadataAttributeAuthorityDescriptor', True)
    __AttributeAuthorityDescriptor._DeclarationLocation = pyxb.utils.utility.Location('/tmp/pyxbdist.RHB65sy/PyXB-1.1.5/pyxb/bundles/saml20/schemas/metadata.xsd', 306, 4)
    __AttributeAuthorityDescriptor._UseLocation = pyxb.utils.utility.Location('/tmp/pyxbdist.RHB65sy/PyXB-1.1.5/pyxb/bundles/saml20/schemas/metadata.xsd', 95, 8)

    
    AttributeAuthorityDescriptor = property(__AttributeAuthorityDescriptor.value, __AttributeAuthorityDescriptor.set, None, None)

    
    # Element {urn:oasis:names:tc:SAML:2.0:metadata}Extensions uses Python identifier Extensions
    __Extensions = pyxb.binding.content.ElementUse(pyxb.namespace.ExpandedName(Namespace, u'Extensions'), 'Extensions', '__urnoasisnamestcSAML2_0metadata_EntityDescriptorType_urnoasisnamestcSAML2_0metadataExtensions', False)
    __Extensions._DeclarationLocation = pyxb.utils.utility.Location('/tmp/pyxbdist.RHB65sy/PyXB-1.1.5/pyxb/bundles/saml20/schemas/metadata.xsd', 51, 4)
    __Extensions._UseLocation = pyxb.utils.utility.Location('/tmp/pyxbdist.RHB65sy/PyXB-1.1.5/pyxb/bundles/saml20/schemas/metadata.xsd', 95, 8)

    
    Extensions = property(__Extensions.value, __Extensions.set, None, None)

    
    # Element {http://www.w3.org/2000/09/xmldsig#}Signature uses Python identifier Signature
    __Signature = pyxb.binding.content.ElementUse(pyxb.namespace.ExpandedName(pyxb.namespace.NamespaceForURI(u'http://www.w3.org/2000/09/xmldsig#'), u'Signature'), 'Signature', '__urnoasisnamestcSAML2_0metadata_EntityDescriptorType_httpwww_w3_org200009xmldsigSignature', False)
    __Signature._DeclarationLocation = pyxb.utils.utility.Location('/tmp/pyxbdist.RHB65sy/PyXB-1.1.5/pyxb/bundles/wssplat/schemas/ds.xsd', 43, 0)
    __Signature._UseLocation = pyxb.utils.utility.Location('/tmp/pyxbdist.RHB65sy/PyXB-1.1.5/pyxb/bundles/saml20/schemas/metadata.xsd', 95, 8)

    
    Signature = property(__Signature.value, __Signature.set, None, None)

    
    # Element {urn:oasis:names:tc:SAML:2.0:metadata}Organization uses Python identifier Organization
    __Organization = pyxb.binding.content.ElementUse(pyxb.namespace.ExpandedName(Namespace, u'Organization'), 'Organization', '__urnoasisnamestcSAML2_0metadata_EntityDescriptorType_urnoasisnamestcSAML2_0metadataOrganization', False)
    __Organization._DeclarationLocation = pyxb.utils.utility.Location('/tmp/pyxbdist.RHB65sy/PyXB-1.1.5/pyxb/bundles/saml20/schemas/metadata.xsd', 120, 4)
    __Organization._UseLocation = pyxb.utils.utility.Location('/tmp/pyxbdist.RHB65sy/PyXB-1.1.5/pyxb/bundles/saml20/schemas/metadata.xsd', 95, 8)

    
    Organization = property(__Organization.value, __Organization.set, None, None)

    
    # Attribute cacheDuration uses Python identifier cacheDuration
    __cacheDuration = pyxb.binding.content.AttributeUse(pyxb.namespace.ExpandedName(None, u'cacheDuration'), 'cacheDuration', '__urnoasisnamestcSAML2_0metadata_EntityDescriptorType_cacheDuration', pyxb.binding.datatypes.duration)
    __cacheDuration._DeclarationLocation = pyxb.utils.utility.Location('/tmp/pyxbdist.RHB65sy/PyXB-1.1.5/pyxb/bundles/saml20/schemas/metadata.xsd', 115, 8)
    __cacheDuration._UseLocation = pyxb.utils.utility.Location('/tmp/pyxbdist.RHB65sy/PyXB-1.1.5/pyxb/bundles/saml20/schemas/metadata.xsd', 115, 8)
    
    cacheDuration = property(__cacheDuration.value, __cacheDuration.set, None, None)

    
    # Attribute ID uses Python identifier ID
    __ID = pyxb.binding.content.AttributeUse(pyxb.namespace.ExpandedName(None, u'ID'), 'ID', '__urnoasisnamestcSAML2_0metadata_EntityDescriptorType_ID', pyxb.binding.datatypes.ID)
    __ID._DeclarationLocation = pyxb.utils.utility.Location('/tmp/pyxbdist.RHB65sy/PyXB-1.1.5/pyxb/bundles/saml20/schemas/metadata.xsd', 116, 8)
    __ID._UseLocation = pyxb.utils.utility.Location('/tmp/pyxbdist.RHB65sy/PyXB-1.1.5/pyxb/bundles/saml20/schemas/metadata.xsd', 116, 8)
    
    ID = property(__ID.value, __ID.set, None, None)

    
    # Attribute entityID uses Python identifier entityID
    __entityID = pyxb.binding.content.AttributeUse(pyxb.namespace.ExpandedName(None, u'entityID'), 'entityID', '__urnoasisnamestcSAML2_0metadata_EntityDescriptorType_entityID', entityIDType, required=True)
    __entityID._DeclarationLocation = pyxb.utils.utility.Location('/tmp/pyxbdist.RHB65sy/PyXB-1.1.5/pyxb/bundles/saml20/schemas/metadata.xsd', 113, 8)
    __entityID._UseLocation = pyxb.utils.utility.Location('/tmp/pyxbdist.RHB65sy/PyXB-1.1.5/pyxb/bundles/saml20/schemas/metadata.xsd', 113, 8)
    
    entityID = property(__entityID.value, __entityID.set, None, None)

    
    # Attribute validUntil uses Python identifier validUntil
    __validUntil = pyxb.binding.content.AttributeUse(pyxb.namespace.ExpandedName(None, u'validUntil'), 'validUntil', '__urnoasisnamestcSAML2_0metadata_EntityDescriptorType_validUntil', pyxb.binding.datatypes.dateTime)
    __validUntil._DeclarationLocation = pyxb.utils.utility.Location('/tmp/pyxbdist.RHB65sy/PyXB-1.1.5/pyxb/bundles/saml20/schemas/metadata.xsd', 114, 8)
    __validUntil._UseLocation = pyxb.utils.utility.Location('/tmp/pyxbdist.RHB65sy/PyXB-1.1.5/pyxb/bundles/saml20/schemas/metadata.xsd', 114, 8)
    
    validUntil = property(__validUntil.value, __validUntil.set, None, None)

    _AttributeWildcard = pyxb.binding.content.Wildcard(process_contents=pyxb.binding.content.Wildcard.PC_lax, namespace_constraint=(pyxb.binding.content.Wildcard.NC_not, u'urn:oasis:names:tc:SAML:2.0:metadata'))

    _ElementMap = {
        __SPSSODescriptor.name() : __SPSSODescriptor,
        __PDPDescriptor.name() : __PDPDescriptor,
        __AffiliationDescriptor.name() : __AffiliationDescriptor,
        __ContactPerson.name() : __ContactPerson,
        __RoleDescriptor.name() : __RoleDescriptor,
        __AdditionalMetadataLocation.name() : __AdditionalMetadataLocation,
        __AuthnAuthorityDescriptor.name() : __AuthnAuthorityDescriptor,
        __IDPSSODescriptor.name() : __IDPSSODescriptor,
        __AttributeAuthorityDescriptor.name() : __AttributeAuthorityDescriptor,
        __Extensions.name() : __Extensions,
        __Signature.name() : __Signature,
        __Organization.name() : __Organization
    }
    _AttributeMap = {
        __cacheDuration.name() : __cacheDuration,
        __ID.name() : __ID,
        __entityID.name() : __entityID,
        __validUntil.name() : __validUntil
    }
Namespace.addCategoryObject('typeBinding', u'EntityDescriptorType', EntityDescriptorType)


# Complex type {urn:oasis:names:tc:SAML:2.0:metadata}AdditionalMetadataLocationType with content type SIMPLE
class AdditionalMetadataLocationType (pyxb.binding.basis.complexTypeDefinition):
    _TypeDefinition = pyxb.binding.datatypes.anyURI
    _ContentTypeTag = pyxb.binding.basis.complexTypeDefinition._CT_SIMPLE
    _Abstract = False
    _ExpandedName = pyxb.namespace.ExpandedName(Namespace, u'AdditionalMetadataLocationType')
    _DefinitionLocation = pyxb.utils.utility.Location('/tmp/pyxbdist.RHB65sy/PyXB-1.1.5/pyxb/bundles/saml20/schemas/metadata.xsd', 162, 4)
    # Base type is pyxb.binding.datatypes.anyURI
    
    # Attribute namespace uses Python identifier namespace
    __namespace = pyxb.binding.content.AttributeUse(pyxb.namespace.ExpandedName(None, u'namespace'), 'namespace', '__urnoasisnamestcSAML2_0metadata_AdditionalMetadataLocationType_namespace', pyxb.binding.datatypes.anyURI, required=True)
    __namespace._DeclarationLocation = pyxb.utils.utility.Location('/tmp/pyxbdist.RHB65sy/PyXB-1.1.5/pyxb/bundles/saml20/schemas/metadata.xsd', 165, 16)
    __namespace._UseLocation = pyxb.utils.utility.Location('/tmp/pyxbdist.RHB65sy/PyXB-1.1.5/pyxb/bundles/saml20/schemas/metadata.xsd', 165, 16)
    
    namespace = property(__namespace.value, __namespace.set, None, None)


    _ElementMap = {
        
    }
    _AttributeMap = {
        __namespace.name() : __namespace
    }
Namespace.addCategoryObject('typeBinding', u'AdditionalMetadataLocationType', AdditionalMetadataLocationType)


# Complex type {urn:oasis:names:tc:SAML:2.0:metadata}AuthnAuthorityDescriptorType with content type ELEMENT_ONLY
class AuthnAuthorityDescriptorType (RoleDescriptorType):
    _TypeDefinition = None
    _ContentTypeTag = pyxb.binding.basis.complexTypeDefinition._CT_ELEMENT_ONLY
    _Abstract = False
    _ExpandedName = pyxb.namespace.ExpandedName(Namespace, u'AuthnAuthorityDescriptorType')
    _DefinitionLocation = pyxb.utils.utility.Location('/tmp/pyxbdist.RHB65sy/PyXB-1.1.5/pyxb/bundles/saml20/schemas/metadata.xsd', 279, 4)
    # Base type is RoleDescriptorType
    
    # Element KeyDescriptor ({urn:oasis:names:tc:SAML:2.0:metadata}KeyDescriptor) inherited from {urn:oasis:names:tc:SAML:2.0:metadata}RoleDescriptorType
    
    # Element Organization ({urn:oasis:names:tc:SAML:2.0:metadata}Organization) inherited from {urn:oasis:names:tc:SAML:2.0:metadata}RoleDescriptorType
    
    # Element Signature ({http://www.w3.org/2000/09/xmldsig#}Signature) inherited from {urn:oasis:names:tc:SAML:2.0:metadata}RoleDescriptorType
    
    # Element {urn:oasis:names:tc:SAML:2.0:metadata}NameIDFormat uses Python identifier NameIDFormat
    __NameIDFormat = pyxb.binding.content.ElementUse(pyxb.namespace.ExpandedName(Namespace, u'NameIDFormat'), 'NameIDFormat', '__urnoasisnamestcSAML2_0metadata_AuthnAuthorityDescriptorType_urnoasisnamestcSAML2_0metadataNameIDFormat', True)
    __NameIDFormat._DeclarationLocation = pyxb.utils.utility.Location('/tmp/pyxbdist.RHB65sy/PyXB-1.1.5/pyxb/bundles/saml20/schemas/metadata.xsd', 221, 4)
    __NameIDFormat._UseLocation = None

    
    NameIDFormat = property(__NameIDFormat.value, __NameIDFormat.set, None, None)

    
    # Element Extensions ({urn:oasis:names:tc:SAML:2.0:metadata}Extensions) inherited from {urn:oasis:names:tc:SAML:2.0:metadata}RoleDescriptorType
    
    # Element {urn:oasis:names:tc:SAML:2.0:metadata}AuthnQueryService uses Python identifier AuthnQueryService
    __AuthnQueryService = pyxb.binding.content.ElementUse(pyxb.namespace.ExpandedName(Namespace, u'AuthnQueryService'), 'AuthnQueryService', '__urnoasisnamestcSAML2_0metadata_AuthnAuthorityDescriptorType_urnoasisnamestcSAML2_0metadataAuthnQueryService', True)
    __AuthnQueryService._DeclarationLocation = pyxb.utils.utility.Location('/tmp/pyxbdist.RHB65sy/PyXB-1.1.5/pyxb/bundles/saml20/schemas/metadata.xsd', 290, 4)
    __AuthnQueryService._UseLocation = None

    
    AuthnQueryService = property(__AuthnQueryService.value, __AuthnQueryService.set, None, None)

    
    # Element ContactPerson ({urn:oasis:names:tc:SAML:2.0:metadata}ContactPerson) inherited from {urn:oasis:names:tc:SAML:2.0:metadata}RoleDescriptorType
    
    # Element {urn:oasis:names:tc:SAML:2.0:metadata}AssertionIDRequestService uses Python identifier AssertionIDRequestService
    __AssertionIDRequestService = pyxb.binding.content.ElementUse(pyxb.namespace.ExpandedName(Namespace, u'AssertionIDRequestService'), 'AssertionIDRequestService', '__urnoasisnamestcSAML2_0metadata_AuthnAuthorityDescriptorType_urnoasisnamestcSAML2_0metadataAssertionIDRequestService', True)
    __AssertionIDRequestService._DeclarationLocation = pyxb.utils.utility.Location('/tmp/pyxbdist.RHB65sy/PyXB-1.1.5/pyxb/bundles/saml20/schemas/metadata.xsd', 240, 4)
    __AssertionIDRequestService._UseLocation = None

    
    AssertionIDRequestService = property(__AssertionIDRequestService.value, __AssertionIDRequestService.set, None, None)

    
    # Attribute protocolSupportEnumeration inherited from {urn:oasis:names:tc:SAML:2.0:metadata}RoleDescriptorType
    
    # Attribute errorURL inherited from {urn:oasis:names:tc:SAML:2.0:metadata}RoleDescriptorType
    
    # Attribute validUntil inherited from {urn:oasis:names:tc:SAML:2.0:metadata}RoleDescriptorType
    
    # Attribute ID inherited from {urn:oasis:names:tc:SAML:2.0:metadata}RoleDescriptorType
    
    # Attribute cacheDuration inherited from {urn:oasis:names:tc:SAML:2.0:metadata}RoleDescriptorType
    _AttributeWildcard = pyxb.binding.content.Wildcard(process_contents=pyxb.binding.content.Wildcard.PC_lax, namespace_constraint=(pyxb.binding.content.Wildcard.NC_not, u'urn:oasis:names:tc:SAML:2.0:metadata'))

    _ElementMap = RoleDescriptorType._ElementMap.copy()
    _ElementMap.update({
        __NameIDFormat.name() : __NameIDFormat,
        __AuthnQueryService.name() : __AuthnQueryService,
        __AssertionIDRequestService.name() : __AssertionIDRequestService
    })
    _AttributeMap = RoleDescriptorType._AttributeMap.copy()
    _AttributeMap.update({
        
    })
Namespace.addCategoryObject('typeBinding', u'AuthnAuthorityDescriptorType', AuthnAuthorityDescriptorType)


# Complex type {urn:oasis:names:tc:SAML:2.0:metadata}AttributeConsumingServiceType with content type ELEMENT_ONLY
class AttributeConsumingServiceType (pyxb.binding.basis.complexTypeDefinition):
    _TypeDefinition = None
    _ContentTypeTag = pyxb.binding.basis.complexTypeDefinition._CT_ELEMENT_ONLY
    _Abstract = False
    _ExpandedName = pyxb.namespace.ExpandedName(Namespace, u'AttributeConsumingServiceType')
    _DefinitionLocation = pyxb.utils.utility.Location('/tmp/pyxbdist.RHB65sy/PyXB-1.1.5/pyxb/bundles/saml20/schemas/metadata.xsd', 258, 4)
    # Base type is pyxb.binding.datatypes.anyType
    
    # Element {urn:oasis:names:tc:SAML:2.0:metadata}RequestedAttribute uses Python identifier RequestedAttribute
    __RequestedAttribute = pyxb.binding.content.ElementUse(pyxb.namespace.ExpandedName(Namespace, u'RequestedAttribute'), 'RequestedAttribute', '__urnoasisnamestcSAML2_0metadata_AttributeConsumingServiceType_urnoasisnamestcSAML2_0metadataRequestedAttribute', True)
    __RequestedAttribute._DeclarationLocation = pyxb.utils.utility.Location('/tmp/pyxbdist.RHB65sy/PyXB-1.1.5/pyxb/bundles/saml20/schemas/metadata.xsd', 269, 4)
    __RequestedAttribute._UseLocation = pyxb.utils.utility.Location('/tmp/pyxbdist.RHB65sy/PyXB-1.1.5/pyxb/bundles/saml20/schemas/metadata.xsd', 259, 8)

    
    RequestedAttribute = property(__RequestedAttribute.value, __RequestedAttribute.set, None, None)

    
    # Element {urn:oasis:names:tc:SAML:2.0:metadata}ServiceName uses Python identifier ServiceName
    __ServiceName = pyxb.binding.content.ElementUse(pyxb.namespace.ExpandedName(Namespace, u'ServiceName'), 'ServiceName', '__urnoasisnamestcSAML2_0metadata_AttributeConsumingServiceType_urnoasisnamestcSAML2_0metadataServiceName', True)
    __ServiceName._DeclarationLocation = pyxb.utils.utility.Location('/tmp/pyxbdist.RHB65sy/PyXB-1.1.5/pyxb/bundles/saml20/schemas/metadata.xsd', 267, 4)
    __ServiceName._UseLocation = pyxb.utils.utility.Location('/tmp/pyxbdist.RHB65sy/PyXB-1.1.5/pyxb/bundles/saml20/schemas/metadata.xsd', 259, 8)

    
    ServiceName = property(__ServiceName.value, __ServiceName.set, None, None)

    
    # Element {urn:oasis:names:tc:SAML:2.0:metadata}ServiceDescription uses Python identifier ServiceDescription
    __ServiceDescription = pyxb.binding.content.ElementUse(pyxb.namespace.ExpandedName(Namespace, u'ServiceDescription'), 'ServiceDescription', '__urnoasisnamestcSAML2_0metadata_AttributeConsumingServiceType_urnoasisnamestcSAML2_0metadataServiceDescription', True)
    __ServiceDescription._DeclarationLocation = pyxb.utils.utility.Location('/tmp/pyxbdist.RHB65sy/PyXB-1.1.5/pyxb/bundles/saml20/schemas/metadata.xsd', 268, 4)
    __ServiceDescription._UseLocation = pyxb.utils.utility.Location('/tmp/pyxbdist.RHB65sy/PyXB-1.1.5/pyxb/bundles/saml20/schemas/metadata.xsd', 259, 8)

    
    ServiceDescription = property(__ServiceDescription.value, __ServiceDescription.set, None, None)

    
    # Attribute index uses Python identifier index
    __index = pyxb.binding.content.AttributeUse(pyxb.namespace.ExpandedName(None, u'index'), 'index', '__urnoasisnamestcSAML2_0metadata_AttributeConsumingServiceType_index', pyxb.binding.datatypes.unsignedShort, required=True)
    __index._DeclarationLocation = pyxb.utils.utility.Location('/tmp/pyxbdist.RHB65sy/PyXB-1.1.5/pyxb/bundles/saml20/schemas/metadata.xsd', 264, 8)
    __index._UseLocation = pyxb.utils.utility.Location('/tmp/pyxbdist.RHB65sy/PyXB-1.1.5/pyxb/bundles/saml20/schemas/metadata.xsd', 264, 8)
    
    index = property(__index.value, __index.set, None, None)

    
    # Attribute isDefault uses Python identifier isDefault
    __isDefault = pyxb.binding.content.AttributeUse(pyxb.namespace.ExpandedName(None, u'isDefault'), 'isDefault', '__urnoasisnamestcSAML2_0metadata_AttributeConsumingServiceType_isDefault', pyxb.binding.datatypes.boolean)
    __isDefault._DeclarationLocation = pyxb.utils.utility.Location('/tmp/pyxbdist.RHB65sy/PyXB-1.1.5/pyxb/bundles/saml20/schemas/metadata.xsd', 265, 8)
    __isDefault._UseLocation = pyxb.utils.utility.Location('/tmp/pyxbdist.RHB65sy/PyXB-1.1.5/pyxb/bundles/saml20/schemas/metadata.xsd', 265, 8)
    
    isDefault = property(__isDefault.value, __isDefault.set, None, None)


    _ElementMap = {
        __RequestedAttribute.name() : __RequestedAttribute,
        __ServiceName.name() : __ServiceName,
        __ServiceDescription.name() : __ServiceDescription
    }
    _AttributeMap = {
        __index.name() : __index,
        __isDefault.name() : __isDefault
    }
Namespace.addCategoryObject('typeBinding', u'AttributeConsumingServiceType', AttributeConsumingServiceType)


# Complex type {urn:oasis:names:tc:SAML:2.0:metadata}SSODescriptorType with content type ELEMENT_ONLY
class SSODescriptorType (RoleDescriptorType):
    _TypeDefinition = None
    _ContentTypeTag = pyxb.binding.basis.complexTypeDefinition._CT_ELEMENT_ONLY
    _Abstract = True
    _ExpandedName = pyxb.namespace.ExpandedName(Namespace, u'SSODescriptorType')
    _DefinitionLocation = pyxb.utils.utility.Location('/tmp/pyxbdist.RHB65sy/PyXB-1.1.5/pyxb/bundles/saml20/schemas/metadata.xsd', 206, 4)
    # Base type is RoleDescriptorType
    
    # Element {urn:oasis:names:tc:SAML:2.0:metadata}SingleLogoutService uses Python identifier SingleLogoutService
    __SingleLogoutService = pyxb.binding.content.ElementUse(pyxb.namespace.ExpandedName(Namespace, u'SingleLogoutService'), 'SingleLogoutService', '__urnoasisnamestcSAML2_0metadata_SSODescriptorType_urnoasisnamestcSAML2_0metadataSingleLogoutService', True)
    __SingleLogoutService._DeclarationLocation = pyxb.utils.utility.Location('/tmp/pyxbdist.RHB65sy/PyXB-1.1.5/pyxb/bundles/saml20/schemas/metadata.xsd', 219, 4)
    __SingleLogoutService._UseLocation = None

    
    SingleLogoutService = property(__SingleLogoutService.value, __SingleLogoutService.set, None, None)

    
    # Element KeyDescriptor ({urn:oasis:names:tc:SAML:2.0:metadata}KeyDescriptor) inherited from {urn:oasis:names:tc:SAML:2.0:metadata}RoleDescriptorType
    
    # Element {urn:oasis:names:tc:SAML:2.0:metadata}ManageNameIDService uses Python identifier ManageNameIDService
    __ManageNameIDService = pyxb.binding.content.ElementUse(pyxb.namespace.ExpandedName(Namespace, u'ManageNameIDService'), 'ManageNameIDService', '__urnoasisnamestcSAML2_0metadata_SSODescriptorType_urnoasisnamestcSAML2_0metadataManageNameIDService', True)
    __ManageNameIDService._DeclarationLocation = pyxb.utils.utility.Location('/tmp/pyxbdist.RHB65sy/PyXB-1.1.5/pyxb/bundles/saml20/schemas/metadata.xsd', 220, 4)
    __ManageNameIDService._UseLocation = None

    
    ManageNameIDService = property(__ManageNameIDService.value, __ManageNameIDService.set, None, None)

    
    # Element Signature ({http://www.w3.org/2000/09/xmldsig#}Signature) inherited from {urn:oasis:names:tc:SAML:2.0:metadata}RoleDescriptorType
    
    # Element Organization ({urn:oasis:names:tc:SAML:2.0:metadata}Organization) inherited from {urn:oasis:names:tc:SAML:2.0:metadata}RoleDescriptorType
    
    # Element {urn:oasis:names:tc:SAML:2.0:metadata}ArtifactResolutionService uses Python identifier ArtifactResolutionService
    __ArtifactResolutionService = pyxb.binding.content.ElementUse(pyxb.namespace.ExpandedName(Namespace, u'ArtifactResolutionService'), 'ArtifactResolutionService', '__urnoasisnamestcSAML2_0metadata_SSODescriptorType_urnoasisnamestcSAML2_0metadataArtifactResolutionService', True)
    __ArtifactResolutionService._DeclarationLocation = pyxb.utils.utility.Location('/tmp/pyxbdist.RHB65sy/PyXB-1.1.5/pyxb/bundles/saml20/schemas/metadata.xsd', 218, 4)
    __ArtifactResolutionService._UseLocation = None

    
    ArtifactResolutionService = property(__ArtifactResolutionService.value, __ArtifactResolutionService.set, None, None)

    
    # Element Extensions ({urn:oasis:names:tc:SAML:2.0:metadata}Extensions) inherited from {urn:oasis:names:tc:SAML:2.0:metadata}RoleDescriptorType
    
    # Element {urn:oasis:names:tc:SAML:2.0:metadata}NameIDFormat uses Python identifier NameIDFormat
    __NameIDFormat = pyxb.binding.content.ElementUse(pyxb.namespace.ExpandedName(Namespace, u'NameIDFormat'), 'NameIDFormat', '__urnoasisnamestcSAML2_0metadata_SSODescriptorType_urnoasisnamestcSAML2_0metadataNameIDFormat', True)
    __NameIDFormat._DeclarationLocation = pyxb.utils.utility.Location('/tmp/pyxbdist.RHB65sy/PyXB-1.1.5/pyxb/bundles/saml20/schemas/metadata.xsd', 221, 4)
    __NameIDFormat._UseLocation = None

    
    NameIDFormat = property(__NameIDFormat.value, __NameIDFormat.set, None, None)

    
    # Element ContactPerson ({urn:oasis:names:tc:SAML:2.0:metadata}ContactPerson) inherited from {urn:oasis:names:tc:SAML:2.0:metadata}RoleDescriptorType
    
    # Attribute protocolSupportEnumeration inherited from {urn:oasis:names:tc:SAML:2.0:metadata}RoleDescriptorType
    
    # Attribute errorURL inherited from {urn:oasis:names:tc:SAML:2.0:metadata}RoleDescriptorType
    
    # Attribute validUntil inherited from {urn:oasis:names:tc:SAML:2.0:metadata}RoleDescriptorType
    
    # Attribute ID inherited from {urn:oasis:names:tc:SAML:2.0:metadata}RoleDescriptorType
    
    # Attribute cacheDuration inherited from {urn:oasis:names:tc:SAML:2.0:metadata}RoleDescriptorType
    _AttributeWildcard = pyxb.binding.content.Wildcard(process_contents=pyxb.binding.content.Wildcard.PC_lax, namespace_constraint=(pyxb.binding.content.Wildcard.NC_not, u'urn:oasis:names:tc:SAML:2.0:metadata'))

    _ElementMap = RoleDescriptorType._ElementMap.copy()
    _ElementMap.update({
        __SingleLogoutService.name() : __SingleLogoutService,
        __ManageNameIDService.name() : __ManageNameIDService,
        __ArtifactResolutionService.name() : __ArtifactResolutionService,
        __NameIDFormat.name() : __NameIDFormat
    })
    _AttributeMap = RoleDescriptorType._AttributeMap.copy()
    _AttributeMap.update({
        
    })
Namespace.addCategoryObject('typeBinding', u'SSODescriptorType', SSODescriptorType)


# Complex type {urn:oasis:names:tc:SAML:2.0:metadata}IDPSSODescriptorType with content type ELEMENT_ONLY
class IDPSSODescriptorType (SSODescriptorType):
    _TypeDefinition = None
    _ContentTypeTag = pyxb.binding.basis.complexTypeDefinition._CT_ELEMENT_ONLY
    _Abstract = False
    _ExpandedName = pyxb.namespace.ExpandedName(Namespace, u'IDPSSODescriptorType')
    _DefinitionLocation = pyxb.utils.utility.Location('/tmp/pyxbdist.RHB65sy/PyXB-1.1.5/pyxb/bundles/saml20/schemas/metadata.xsd', 224, 4)
    # Base type is SSODescriptorType
    
    # Element SingleLogoutService ({urn:oasis:names:tc:SAML:2.0:metadata}SingleLogoutService) inherited from {urn:oasis:names:tc:SAML:2.0:metadata}SSODescriptorType
    
    # Element KeyDescriptor ({urn:oasis:names:tc:SAML:2.0:metadata}KeyDescriptor) inherited from {urn:oasis:names:tc:SAML:2.0:metadata}RoleDescriptorType
    
    # Element {urn:oasis:names:tc:SAML:2.0:metadata}AttributeProfile uses Python identifier AttributeProfile
    __AttributeProfile = pyxb.binding.content.ElementUse(pyxb.namespace.ExpandedName(Namespace, u'AttributeProfile'), 'AttributeProfile', '__urnoasisnamestcSAML2_0metadata_IDPSSODescriptorType_urnoasisnamestcSAML2_0metadataAttributeProfile', True)
    __AttributeProfile._DeclarationLocation = pyxb.utils.utility.Location('/tmp/pyxbdist.RHB65sy/PyXB-1.1.5/pyxb/bundles/saml20/schemas/metadata.xsd', 241, 4)
    __AttributeProfile._UseLocation = None

    
    AttributeProfile = property(__AttributeProfile.value, __AttributeProfile.set, None, None)

    
    # Element {urn:oasis:names:tc:SAML:2.0:metadata}NameIDMappingService uses Python identifier NameIDMappingService
    __NameIDMappingService = pyxb.binding.content.ElementUse(pyxb.namespace.ExpandedName(Namespace, u'NameIDMappingService'), 'NameIDMappingService', '__urnoasisnamestcSAML2_0metadata_IDPSSODescriptorType_urnoasisnamestcSAML2_0metadataNameIDMappingService', True)
    __NameIDMappingService._DeclarationLocation = pyxb.utils.utility.Location('/tmp/pyxbdist.RHB65sy/PyXB-1.1.5/pyxb/bundles/saml20/schemas/metadata.xsd', 239, 4)
    __NameIDMappingService._UseLocation = None

    
    NameIDMappingService = property(__NameIDMappingService.value, __NameIDMappingService.set, None, None)

    
    # Element {urn:oasis:names:tc:SAML:2.0:assertion}Attribute uses Python identifier Attribute
    __Attribute = pyxb.binding.content.ElementUse(pyxb.namespace.ExpandedName(pyxb.namespace.NamespaceForURI(u'urn:oasis:names:tc:SAML:2.0:assertion'), u'Attribute'), 'Attribute', '__urnoasisnamestcSAML2_0metadata_IDPSSODescriptorType_urnoasisnamestcSAML2_0assertionAttribute', True)
    __Attribute._DeclarationLocation = pyxb.utils.utility.Location('/tmp/pyxbdist.RHB65sy/PyXB-1.1.5/pyxb/bundles/saml20/schemas/assertion.xsd', 271, 4)
    __Attribute._UseLocation = None

    
    Attribute = property(__Attribute.value, __Attribute.set, None, None)

    
    # Element Signature ({http://www.w3.org/2000/09/xmldsig#}Signature) inherited from {urn:oasis:names:tc:SAML:2.0:metadata}RoleDescriptorType
    
    # Element Organization ({urn:oasis:names:tc:SAML:2.0:metadata}Organization) inherited from {urn:oasis:names:tc:SAML:2.0:metadata}RoleDescriptorType
    
    # Element {urn:oasis:names:tc:SAML:2.0:metadata}AssertionIDRequestService uses Python identifier AssertionIDRequestService
    __AssertionIDRequestService = pyxb.binding.content.ElementUse(pyxb.namespace.ExpandedName(Namespace, u'AssertionIDRequestService'), 'AssertionIDRequestService', '__urnoasisnamestcSAML2_0metadata_IDPSSODescriptorType_urnoasisnamestcSAML2_0metadataAssertionIDRequestService', True)
    __AssertionIDRequestService._DeclarationLocation = pyxb.utils.utility.Location('/tmp/pyxbdist.RHB65sy/PyXB-1.1.5/pyxb/bundles/saml20/schemas/metadata.xsd', 240, 4)
    __AssertionIDRequestService._UseLocation = None

    
    AssertionIDRequestService = property(__AssertionIDRequestService.value, __AssertionIDRequestService.set, None, None)

    
    # Element Extensions ({urn:oasis:names:tc:SAML:2.0:metadata}Extensions) inherited from {urn:oasis:names:tc:SAML:2.0:metadata}RoleDescriptorType
    
    # Element ManageNameIDService ({urn:oasis:names:tc:SAML:2.0:metadata}ManageNameIDService) inherited from {urn:oasis:names:tc:SAML:2.0:metadata}SSODescriptorType
    
    # Element NameIDFormat ({urn:oasis:names:tc:SAML:2.0:metadata}NameIDFormat) inherited from {urn:oasis:names:tc:SAML:2.0:metadata}SSODescriptorType
    
    # Element ContactPerson ({urn:oasis:names:tc:SAML:2.0:metadata}ContactPerson) inherited from {urn:oasis:names:tc:SAML:2.0:metadata}RoleDescriptorType
    
    # Element {urn:oasis:names:tc:SAML:2.0:metadata}SingleSignOnService uses Python identifier SingleSignOnService
    __SingleSignOnService = pyxb.binding.content.ElementUse(pyxb.namespace.ExpandedName(Namespace, u'SingleSignOnService'), 'SingleSignOnService', '__urnoasisnamestcSAML2_0metadata_IDPSSODescriptorType_urnoasisnamestcSAML2_0metadataSingleSignOnService', True)
    __SingleSignOnService._DeclarationLocation = pyxb.utils.utility.Location('/tmp/pyxbdist.RHB65sy/PyXB-1.1.5/pyxb/bundles/saml20/schemas/metadata.xsd', 238, 4)
    __SingleSignOnService._UseLocation = None

    
    SingleSignOnService = property(__SingleSignOnService.value, __SingleSignOnService.set, None, None)

    
    # Element ArtifactResolutionService ({urn:oasis:names:tc:SAML:2.0:metadata}ArtifactResolutionService) inherited from {urn:oasis:names:tc:SAML:2.0:metadata}SSODescriptorType
    
    # Attribute WantAuthnRequestsSigned uses Python identifier WantAuthnRequestsSigned
    __WantAuthnRequestsSigned = pyxb.binding.content.AttributeUse(pyxb.namespace.ExpandedName(None, u'WantAuthnRequestsSigned'), 'WantAuthnRequestsSigned', '__urnoasisnamestcSAML2_0metadata_IDPSSODescriptorType_WantAuthnRequestsSigned', pyxb.binding.datatypes.boolean)
    __WantAuthnRequestsSigned._DeclarationLocation = pyxb.utils.utility.Location('/tmp/pyxbdist.RHB65sy/PyXB-1.1.5/pyxb/bundles/saml20/schemas/metadata.xsd', 234, 16)
    __WantAuthnRequestsSigned._UseLocation = pyxb.utils.utility.Location('/tmp/pyxbdist.RHB65sy/PyXB-1.1.5/pyxb/bundles/saml20/schemas/metadata.xsd', 234, 16)
    
    WantAuthnRequestsSigned = property(__WantAuthnRequestsSigned.value, __WantAuthnRequestsSigned.set, None, None)

    
    # Attribute validUntil inherited from {urn:oasis:names:tc:SAML:2.0:metadata}RoleDescriptorType
    
    # Attribute cacheDuration inherited from {urn:oasis:names:tc:SAML:2.0:metadata}RoleDescriptorType
    
    # Attribute protocolSupportEnumeration inherited from {urn:oasis:names:tc:SAML:2.0:metadata}RoleDescriptorType
    
    # Attribute ID inherited from {urn:oasis:names:tc:SAML:2.0:metadata}RoleDescriptorType
    
    # Attribute errorURL inherited from {urn:oasis:names:tc:SAML:2.0:metadata}RoleDescriptorType
    _AttributeWildcard = pyxb.binding.content.Wildcard(process_contents=pyxb.binding.content.Wildcard.PC_lax, namespace_constraint=(pyxb.binding.content.Wildcard.NC_not, u'urn:oasis:names:tc:SAML:2.0:metadata'))

    _ElementMap = SSODescriptorType._ElementMap.copy()
    _ElementMap.update({
        __AttributeProfile.name() : __AttributeProfile,
        __NameIDMappingService.name() : __NameIDMappingService,
        __Attribute.name() : __Attribute,
        __AssertionIDRequestService.name() : __AssertionIDRequestService,
        __SingleSignOnService.name() : __SingleSignOnService
    })
    _AttributeMap = SSODescriptorType._AttributeMap.copy()
    _AttributeMap.update({
        __WantAuthnRequestsSigned.name() : __WantAuthnRequestsSigned
    })
Namespace.addCategoryObject('typeBinding', u'IDPSSODescriptorType', IDPSSODescriptorType)


# Complex type {urn:oasis:names:tc:SAML:2.0:metadata}AttributeAuthorityDescriptorType with content type ELEMENT_ONLY
class AttributeAuthorityDescriptorType (RoleDescriptorType):
    _TypeDefinition = None
    _ContentTypeTag = pyxb.binding.basis.complexTypeDefinition._CT_ELEMENT_ONLY
    _Abstract = False
    _ExpandedName = pyxb.namespace.ExpandedName(Namespace, u'AttributeAuthorityDescriptorType')
    _DefinitionLocation = pyxb.utils.utility.Location('/tmp/pyxbdist.RHB65sy/PyXB-1.1.5/pyxb/bundles/saml20/schemas/metadata.xsd', 307, 4)
    # Base type is RoleDescriptorType
    
    # Element {urn:oasis:names:tc:SAML:2.0:assertion}Attribute uses Python identifier Attribute
    __Attribute = pyxb.binding.content.ElementUse(pyxb.namespace.ExpandedName(pyxb.namespace.NamespaceForURI(u'urn:oasis:names:tc:SAML:2.0:assertion'), u'Attribute'), 'Attribute', '__urnoasisnamestcSAML2_0metadata_AttributeAuthorityDescriptorType_urnoasisnamestcSAML2_0assertionAttribute', True)
    __Attribute._DeclarationLocation = pyxb.utils.utility.Location('/tmp/pyxbdist.RHB65sy/PyXB-1.1.5/pyxb/bundles/saml20/schemas/assertion.xsd', 271, 4)
    __Attribute._UseLocation = None

    
    Attribute = property(__Attribute.value, __Attribute.set, None, None)

    
    # Element Organization ({urn:oasis:names:tc:SAML:2.0:metadata}Organization) inherited from {urn:oasis:names:tc:SAML:2.0:metadata}RoleDescriptorType
    
    # Element {urn:oasis:names:tc:SAML:2.0:metadata}NameIDFormat uses Python identifier NameIDFormat
    __NameIDFormat = pyxb.binding.content.ElementUse(pyxb.namespace.ExpandedName(Namespace, u'NameIDFormat'), 'NameIDFormat', '__urnoasisnamestcSAML2_0metadata_AttributeAuthorityDescriptorType_urnoasisnamestcSAML2_0metadataNameIDFormat', True)
    __NameIDFormat._DeclarationLocation = pyxb.utils.utility.Location('/tmp/pyxbdist.RHB65sy/PyXB-1.1.5/pyxb/bundles/saml20/schemas/metadata.xsd', 221, 4)
    __NameIDFormat._UseLocation = None

    
    NameIDFormat = property(__NameIDFormat.value, __NameIDFormat.set, None, None)

    
    # Element Signature ({http://www.w3.org/2000/09/xmldsig#}Signature) inherited from {urn:oasis:names:tc:SAML:2.0:metadata}RoleDescriptorType
    
    # Element {urn:oasis:names:tc:SAML:2.0:metadata}AttributeService uses Python identifier AttributeService
    __AttributeService = pyxb.binding.content.ElementUse(pyxb.namespace.ExpandedName(Namespace, u'AttributeService'), 'AttributeService', '__urnoasisnamestcSAML2_0metadata_AttributeAuthorityDescriptorType_urnoasisnamestcSAML2_0metadataAttributeService', True)
    __AttributeService._DeclarationLocation = pyxb.utils.utility.Location('/tmp/pyxbdist.RHB65sy/PyXB-1.1.5/pyxb/bundles/saml20/schemas/metadata.xsd', 320, 4)
    __AttributeService._UseLocation = None

    
    AttributeService = property(__AttributeService.value, __AttributeService.set, None, None)

    
    # Element Extensions ({urn:oasis:names:tc:SAML:2.0:metadata}Extensions) inherited from {urn:oasis:names:tc:SAML:2.0:metadata}RoleDescriptorType
    
    # Element {urn:oasis:names:tc:SAML:2.0:metadata}AttributeProfile uses Python identifier AttributeProfile
    __AttributeProfile = pyxb.binding.content.ElementUse(pyxb.namespace.ExpandedName(Namespace, u'AttributeProfile'), 'AttributeProfile', '__urnoasisnamestcSAML2_0metadata_AttributeAuthorityDescriptorType_urnoasisnamestcSAML2_0metadataAttributeProfile', True)
    __AttributeProfile._DeclarationLocation = pyxb.utils.utility.Location('/tmp/pyxbdist.RHB65sy/PyXB-1.1.5/pyxb/bundles/saml20/schemas/metadata.xsd', 241, 4)
    __AttributeProfile._UseLocation = None

    
    AttributeProfile = property(__AttributeProfile.value, __AttributeProfile.set, None, None)

    
    # Element ContactPerson ({urn:oasis:names:tc:SAML:2.0:metadata}ContactPerson) inherited from {urn:oasis:names:tc:SAML:2.0:metadata}RoleDescriptorType
    
    # Element {urn:oasis:names:tc:SAML:2.0:metadata}AssertionIDRequestService uses Python identifier AssertionIDRequestService
    __AssertionIDRequestService = pyxb.binding.content.ElementUse(pyxb.namespace.ExpandedName(Namespace, u'AssertionIDRequestService'), 'AssertionIDRequestService', '__urnoasisnamestcSAML2_0metadata_AttributeAuthorityDescriptorType_urnoasisnamestcSAML2_0metadataAssertionIDRequestService', True)
    __AssertionIDRequestService._DeclarationLocation = pyxb.utils.utility.Location('/tmp/pyxbdist.RHB65sy/PyXB-1.1.5/pyxb/bundles/saml20/schemas/metadata.xsd', 240, 4)
    __AssertionIDRequestService._UseLocation = None

    
    AssertionIDRequestService = property(__AssertionIDRequestService.value, __AssertionIDRequestService.set, None, None)

    
    # Element KeyDescriptor ({urn:oasis:names:tc:SAML:2.0:metadata}KeyDescriptor) inherited from {urn:oasis:names:tc:SAML:2.0:metadata}RoleDescriptorType
    
    # Attribute protocolSupportEnumeration inherited from {urn:oasis:names:tc:SAML:2.0:metadata}RoleDescriptorType
    
    # Attribute errorURL inherited from {urn:oasis:names:tc:SAML:2.0:metadata}RoleDescriptorType
    
    # Attribute validUntil inherited from {urn:oasis:names:tc:SAML:2.0:metadata}RoleDescriptorType
    
    # Attribute ID inherited from {urn:oasis:names:tc:SAML:2.0:metadata}RoleDescriptorType
    
    # Attribute cacheDuration inherited from {urn:oasis:names:tc:SAML:2.0:metadata}RoleDescriptorType
    _AttributeWildcard = pyxb.binding.content.Wildcard(process_contents=pyxb.binding.content.Wildcard.PC_lax, namespace_constraint=(pyxb.binding.content.Wildcard.NC_not, u'urn:oasis:names:tc:SAML:2.0:metadata'))

    _ElementMap = RoleDescriptorType._ElementMap.copy()
    _ElementMap.update({
        __Attribute.name() : __Attribute,
        __NameIDFormat.name() : __NameIDFormat,
        __AttributeService.name() : __AttributeService,
        __AttributeProfile.name() : __AttributeProfile,
        __AssertionIDRequestService.name() : __AssertionIDRequestService
    })
    _AttributeMap = RoleDescriptorType._AttributeMap.copy()
    _AttributeMap.update({
        
    })
Namespace.addCategoryObject('typeBinding', u'AttributeAuthorityDescriptorType', AttributeAuthorityDescriptorType)


# Complex type {urn:oasis:names:tc:SAML:2.0:metadata}localizedURIType with content type SIMPLE
class localizedURIType (pyxb.binding.basis.complexTypeDefinition):
    _TypeDefinition = pyxb.binding.datatypes.anyURI
    _ContentTypeTag = pyxb.binding.basis.complexTypeDefinition._CT_SIMPLE
    _Abstract = False
    _ExpandedName = pyxb.namespace.ExpandedName(Namespace, u'localizedURIType')
    _DefinitionLocation = pyxb.utils.utility.Location('/tmp/pyxbdist.RHB65sy/PyXB-1.1.5/pyxb/bundles/saml20/schemas/metadata.xsd', 43, 4)
    # Base type is pyxb.binding.datatypes.anyURI
    
    # Attribute {http://www.w3.org/XML/1998/namespace}lang uses Python identifier lang
    __lang = pyxb.binding.content.AttributeUse(pyxb.namespace.ExpandedName(pyxb.namespace.XML, 'lang'), 'lang', '__urnoasisnamestcSAML2_0metadata_localizedURIType_httpwww_w3_orgXML1998namespacelang', pyxb.binding.xml_.STD_ANON_lang, required=True)
    __lang._DeclarationLocation = None
    __lang._UseLocation = pyxb.utils.utility.Location('/tmp/pyxbdist.RHB65sy/PyXB-1.1.5/pyxb/bundles/saml20/schemas/metadata.xsd', 46, 16)
    
    lang = property(__lang.value, __lang.set, None, None)


    _ElementMap = {
        
    }
    _AttributeMap = {
        __lang.name() : __lang
    }
Namespace.addCategoryObject('typeBinding', u'localizedURIType', localizedURIType)


# Complex type {urn:oasis:names:tc:SAML:2.0:metadata}SPSSODescriptorType with content type ELEMENT_ONLY
class SPSSODescriptorType (SSODescriptorType):
    _TypeDefinition = None
    _ContentTypeTag = pyxb.binding.basis.complexTypeDefinition._CT_ELEMENT_ONLY
    _Abstract = False
    _ExpandedName = pyxb.namespace.ExpandedName(Namespace, u'SPSSODescriptorType')
    _DefinitionLocation = pyxb.utils.utility.Location('/tmp/pyxbdist.RHB65sy/PyXB-1.1.5/pyxb/bundles/saml20/schemas/metadata.xsd', 244, 4)
    # Base type is SSODescriptorType
    
    # Element SingleLogoutService ({urn:oasis:names:tc:SAML:2.0:metadata}SingleLogoutService) inherited from {urn:oasis:names:tc:SAML:2.0:metadata}SSODescriptorType
    
    # Element {urn:oasis:names:tc:SAML:2.0:metadata}AssertionConsumerService uses Python identifier AssertionConsumerService
    __AssertionConsumerService = pyxb.binding.content.ElementUse(pyxb.namespace.ExpandedName(Namespace, u'AssertionConsumerService'), 'AssertionConsumerService', '__urnoasisnamestcSAML2_0metadata_SPSSODescriptorType_urnoasisnamestcSAML2_0metadataAssertionConsumerService', True)
    __AssertionConsumerService._DeclarationLocation = pyxb.utils.utility.Location('/tmp/pyxbdist.RHB65sy/PyXB-1.1.5/pyxb/bundles/saml20/schemas/metadata.xsd', 256, 4)
    __AssertionConsumerService._UseLocation = None

    
    AssertionConsumerService = property(__AssertionConsumerService.value, __AssertionConsumerService.set, None, None)

    
    # Element KeyDescriptor ({urn:oasis:names:tc:SAML:2.0:metadata}KeyDescriptor) inherited from {urn:oasis:names:tc:SAML:2.0:metadata}RoleDescriptorType
    
    # Element ManageNameIDService ({urn:oasis:names:tc:SAML:2.0:metadata}ManageNameIDService) inherited from {urn:oasis:names:tc:SAML:2.0:metadata}SSODescriptorType
    
    # Element Signature ({http://www.w3.org/2000/09/xmldsig#}Signature) inherited from {urn:oasis:names:tc:SAML:2.0:metadata}RoleDescriptorType
    
    # Element Organization ({urn:oasis:names:tc:SAML:2.0:metadata}Organization) inherited from {urn:oasis:names:tc:SAML:2.0:metadata}RoleDescriptorType
    
    # Element ArtifactResolutionService ({urn:oasis:names:tc:SAML:2.0:metadata}ArtifactResolutionService) inherited from {urn:oasis:names:tc:SAML:2.0:metadata}SSODescriptorType
    
    # Element Extensions ({urn:oasis:names:tc:SAML:2.0:metadata}Extensions) inherited from {urn:oasis:names:tc:SAML:2.0:metadata}RoleDescriptorType
    
    # Element NameIDFormat ({urn:oasis:names:tc:SAML:2.0:metadata}NameIDFormat) inherited from {urn:oasis:names:tc:SAML:2.0:metadata}SSODescriptorType
    
    # Element ContactPerson ({urn:oasis:names:tc:SAML:2.0:metadata}ContactPerson) inherited from {urn:oasis:names:tc:SAML:2.0:metadata}RoleDescriptorType
    
    # Element {urn:oasis:names:tc:SAML:2.0:metadata}AttributeConsumingService uses Python identifier AttributeConsumingService
    __AttributeConsumingService = pyxb.binding.content.ElementUse(pyxb.namespace.ExpandedName(Namespace, u'AttributeConsumingService'), 'AttributeConsumingService', '__urnoasisnamestcSAML2_0metadata_SPSSODescriptorType_urnoasisnamestcSAML2_0metadataAttributeConsumingService', True)
    __AttributeConsumingService._DeclarationLocation = pyxb.utils.utility.Location('/tmp/pyxbdist.RHB65sy/PyXB-1.1.5/pyxb/bundles/saml20/schemas/metadata.xsd', 257, 4)
    __AttributeConsumingService._UseLocation = None

    
    AttributeConsumingService = property(__AttributeConsumingService.value, __AttributeConsumingService.set, None, None)

    
    # Attribute validUntil inherited from {urn:oasis:names:tc:SAML:2.0:metadata}RoleDescriptorType
    
    # Attribute WantAssertionsSigned uses Python identifier WantAssertionsSigned
    __WantAssertionsSigned = pyxb.binding.content.AttributeUse(pyxb.namespace.ExpandedName(None, u'WantAssertionsSigned'), 'WantAssertionsSigned', '__urnoasisnamestcSAML2_0metadata_SPSSODescriptorType_WantAssertionsSigned', pyxb.binding.datatypes.boolean)
    __WantAssertionsSigned._DeclarationLocation = pyxb.utils.utility.Location('/tmp/pyxbdist.RHB65sy/PyXB-1.1.5/pyxb/bundles/saml20/schemas/metadata.xsd', 252, 16)
    __WantAssertionsSigned._UseLocation = pyxb.utils.utility.Location('/tmp/pyxbdist.RHB65sy/PyXB-1.1.5/pyxb/bundles/saml20/schemas/metadata.xsd', 252, 16)
    
    WantAssertionsSigned = property(__WantAssertionsSigned.value, __WantAssertionsSigned.set, None, None)

    
    # Attribute cacheDuration inherited from {urn:oasis:names:tc:SAML:2.0:metadata}RoleDescriptorType
    
    # Attribute protocolSupportEnumeration inherited from {urn:oasis:names:tc:SAML:2.0:metadata}RoleDescriptorType
    
    # Attribute ID inherited from {urn:oasis:names:tc:SAML:2.0:metadata}RoleDescriptorType
    
    # Attribute errorURL inherited from {urn:oasis:names:tc:SAML:2.0:metadata}RoleDescriptorType
    
    # Attribute AuthnRequestsSigned uses Python identifier AuthnRequestsSigned
    __AuthnRequestsSigned = pyxb.binding.content.AttributeUse(pyxb.namespace.ExpandedName(None, u'AuthnRequestsSigned'), 'AuthnRequestsSigned', '__urnoasisnamestcSAML2_0metadata_SPSSODescriptorType_AuthnRequestsSigned', pyxb.binding.datatypes.boolean)
    __AuthnRequestsSigned._DeclarationLocation = pyxb.utils.utility.Location('/tmp/pyxbdist.RHB65sy/PyXB-1.1.5/pyxb/bundles/saml20/schemas/metadata.xsd', 251, 16)
    __AuthnRequestsSigned._UseLocation = pyxb.utils.utility.Location('/tmp/pyxbdist.RHB65sy/PyXB-1.1.5/pyxb/bundles/saml20/schemas/metadata.xsd', 251, 16)
    
    AuthnRequestsSigned = property(__AuthnRequestsSigned.value, __AuthnRequestsSigned.set, None, None)

    _AttributeWildcard = pyxb.binding.content.Wildcard(process_contents=pyxb.binding.content.Wildcard.PC_lax, namespace_constraint=(pyxb.binding.content.Wildcard.NC_not, u'urn:oasis:names:tc:SAML:2.0:metadata'))

    _ElementMap = SSODescriptorType._ElementMap.copy()
    _ElementMap.update({
        __AssertionConsumerService.name() : __AssertionConsumerService,
        __AttributeConsumingService.name() : __AttributeConsumingService
    })
    _AttributeMap = SSODescriptorType._AttributeMap.copy()
    _AttributeMap.update({
        __WantAssertionsSigned.name() : __WantAssertionsSigned,
        __AuthnRequestsSigned.name() : __AuthnRequestsSigned
    })
Namespace.addCategoryObject('typeBinding', u'SPSSODescriptorType', SPSSODescriptorType)


AttributeProfile = pyxb.binding.basis.element(pyxb.namespace.ExpandedName(Namespace, u'AttributeProfile'), pyxb.binding.datatypes.anyURI)
Namespace.addCategoryObject('elementBinding', AttributeProfile.name().localName(), AttributeProfile)

TelephoneNumber = pyxb.binding.basis.element(pyxb.namespace.ExpandedName(Namespace, u'TelephoneNumber'), pyxb.binding.datatypes.string)
Namespace.addCategoryObject('elementBinding', TelephoneNumber.name().localName(), TelephoneNumber)

ServiceName = pyxb.binding.basis.element(pyxb.namespace.ExpandedName(Namespace, u'ServiceName'), localizedNameType)
Namespace.addCategoryObject('elementBinding', ServiceName.name().localName(), ServiceName)

ArtifactResolutionService = pyxb.binding.basis.element(pyxb.namespace.ExpandedName(Namespace, u'ArtifactResolutionService'), IndexedEndpointType)
Namespace.addCategoryObject('elementBinding', ArtifactResolutionService.name().localName(), ArtifactResolutionService)

SingleLogoutService = pyxb.binding.basis.element(pyxb.namespace.ExpandedName(Namespace, u'SingleLogoutService'), EndpointType)
Namespace.addCategoryObject('elementBinding', SingleLogoutService.name().localName(), SingleLogoutService)

EntitiesDescriptor = pyxb.binding.basis.element(pyxb.namespace.ExpandedName(Namespace, u'EntitiesDescriptor'), EntitiesDescriptorType)
Namespace.addCategoryObject('elementBinding', EntitiesDescriptor.name().localName(), EntitiesDescriptor)

OrganizationName = pyxb.binding.basis.element(pyxb.namespace.ExpandedName(Namespace, u'OrganizationName'), localizedNameType)
Namespace.addCategoryObject('elementBinding', OrganizationName.name().localName(), OrganizationName)

NameIDFormat = pyxb.binding.basis.element(pyxb.namespace.ExpandedName(Namespace, u'NameIDFormat'), pyxb.binding.datatypes.anyURI)
Namespace.addCategoryObject('elementBinding', NameIDFormat.name().localName(), NameIDFormat)

ContactPerson = pyxb.binding.basis.element(pyxb.namespace.ExpandedName(Namespace, u'ContactPerson'), ContactType)
Namespace.addCategoryObject('elementBinding', ContactPerson.name().localName(), ContactPerson)

EntityDescriptor = pyxb.binding.basis.element(pyxb.namespace.ExpandedName(Namespace, u'EntityDescriptor'), EntityDescriptorType)
Namespace.addCategoryObject('elementBinding', EntityDescriptor.name().localName(), EntityDescriptor)

Extensions = pyxb.binding.basis.element(pyxb.namespace.ExpandedName(Namespace, u'Extensions'), ExtensionsType)
Namespace.addCategoryObject('elementBinding', Extensions.name().localName(), Extensions)

ServiceDescription = pyxb.binding.basis.element(pyxb.namespace.ExpandedName(Namespace, u'ServiceDescription'), localizedNameType)
Namespace.addCategoryObject('elementBinding', ServiceDescription.name().localName(), ServiceDescription)

RequestedAttribute = pyxb.binding.basis.element(pyxb.namespace.ExpandedName(Namespace, u'RequestedAttribute'), RequestedAttributeType)
Namespace.addCategoryObject('elementBinding', RequestedAttribute.name().localName(), RequestedAttribute)

AssertionConsumerService = pyxb.binding.basis.element(pyxb.namespace.ExpandedName(Namespace, u'AssertionConsumerService'), IndexedEndpointType)
Namespace.addCategoryObject('elementBinding', AssertionConsumerService.name().localName(), AssertionConsumerService)

AuthnAuthorityDescriptor = pyxb.binding.basis.element(pyxb.namespace.ExpandedName(Namespace, u'AuthnAuthorityDescriptor'), AuthnAuthorityDescriptorType)
Namespace.addCategoryObject('elementBinding', AuthnAuthorityDescriptor.name().localName(), AuthnAuthorityDescriptor)

KeyDescriptor = pyxb.binding.basis.element(pyxb.namespace.ExpandedName(Namespace, u'KeyDescriptor'), KeyDescriptorType)
Namespace.addCategoryObject('elementBinding', KeyDescriptor.name().localName(), KeyDescriptor)

AuthnQueryService = pyxb.binding.basis.element(pyxb.namespace.ExpandedName(Namespace, u'AuthnQueryService'), EndpointType)
Namespace.addCategoryObject('elementBinding', AuthnQueryService.name().localName(), AuthnQueryService)

EncryptionMethod = pyxb.binding.basis.element(pyxb.namespace.ExpandedName(Namespace, u'EncryptionMethod'), pyxb.bundles.wssplat.xenc.EncryptionMethodType)
Namespace.addCategoryObject('elementBinding', EncryptionMethod.name().localName(), EncryptionMethod)

ManageNameIDService = pyxb.binding.basis.element(pyxb.namespace.ExpandedName(Namespace, u'ManageNameIDService'), EndpointType)
Namespace.addCategoryObject('elementBinding', ManageNameIDService.name().localName(), ManageNameIDService)

AuthzService = pyxb.binding.basis.element(pyxb.namespace.ExpandedName(Namespace, u'AuthzService'), EndpointType)
Namespace.addCategoryObject('elementBinding', AuthzService.name().localName(), AuthzService)

AttributeAuthorityDescriptor = pyxb.binding.basis.element(pyxb.namespace.ExpandedName(Namespace, u'AttributeAuthorityDescriptor'), AttributeAuthorityDescriptorType)
Namespace.addCategoryObject('elementBinding', AttributeAuthorityDescriptor.name().localName(), AttributeAuthorityDescriptor)

OrganizationDisplayName = pyxb.binding.basis.element(pyxb.namespace.ExpandedName(Namespace, u'OrganizationDisplayName'), localizedNameType)
Namespace.addCategoryObject('elementBinding', OrganizationDisplayName.name().localName(), OrganizationDisplayName)

OrganizationURL = pyxb.binding.basis.element(pyxb.namespace.ExpandedName(Namespace, u'OrganizationURL'), localizedURIType)
Namespace.addCategoryObject('elementBinding', OrganizationURL.name().localName(), OrganizationURL)

IDPSSODescriptor = pyxb.binding.basis.element(pyxb.namespace.ExpandedName(Namespace, u'IDPSSODescriptor'), IDPSSODescriptorType)
Namespace.addCategoryObject('elementBinding', IDPSSODescriptor.name().localName(), IDPSSODescriptor)

SPSSODescriptor = pyxb.binding.basis.element(pyxb.namespace.ExpandedName(Namespace, u'SPSSODescriptor'), SPSSODescriptorType)
Namespace.addCategoryObject('elementBinding', SPSSODescriptor.name().localName(), SPSSODescriptor)

AttributeService = pyxb.binding.basis.element(pyxb.namespace.ExpandedName(Namespace, u'AttributeService'), EndpointType)
Namespace.addCategoryObject('elementBinding', AttributeService.name().localName(), AttributeService)

AffiliationDescriptor = pyxb.binding.basis.element(pyxb.namespace.ExpandedName(Namespace, u'AffiliationDescriptor'), AffiliationDescriptorType)
Namespace.addCategoryObject('elementBinding', AffiliationDescriptor.name().localName(), AffiliationDescriptor)

PDPDescriptor = pyxb.binding.basis.element(pyxb.namespace.ExpandedName(Namespace, u'PDPDescriptor'), PDPDescriptorType)
Namespace.addCategoryObject('elementBinding', PDPDescriptor.name().localName(), PDPDescriptor)

SingleSignOnService = pyxb.binding.basis.element(pyxb.namespace.ExpandedName(Namespace, u'SingleSignOnService'), EndpointType)
Namespace.addCategoryObject('elementBinding', SingleSignOnService.name().localName(), SingleSignOnService)

NameIDMappingService = pyxb.binding.basis.element(pyxb.namespace.ExpandedName(Namespace, u'NameIDMappingService'), EndpointType)
Namespace.addCategoryObject('elementBinding', NameIDMappingService.name().localName(), NameIDMappingService)

GivenName = pyxb.binding.basis.element(pyxb.namespace.ExpandedName(Namespace, u'GivenName'), pyxb.binding.datatypes.string)
Namespace.addCategoryObject('elementBinding', GivenName.name().localName(), GivenName)

SurName = pyxb.binding.basis.element(pyxb.namespace.ExpandedName(Namespace, u'SurName'), pyxb.binding.datatypes.string)
Namespace.addCategoryObject('elementBinding', SurName.name().localName(), SurName)

EmailAddress = pyxb.binding.basis.element(pyxb.namespace.ExpandedName(Namespace, u'EmailAddress'), pyxb.binding.datatypes.anyURI)
Namespace.addCategoryObject('elementBinding', EmailAddress.name().localName(), EmailAddress)

Organization = pyxb.binding.basis.element(pyxb.namespace.ExpandedName(Namespace, u'Organization'), OrganizationType)
Namespace.addCategoryObject('elementBinding', Organization.name().localName(), Organization)

AdditionalMetadataLocation = pyxb.binding.basis.element(pyxb.namespace.ExpandedName(Namespace, u'AdditionalMetadataLocation'), AdditionalMetadataLocationType)
Namespace.addCategoryObject('elementBinding', AdditionalMetadataLocation.name().localName(), AdditionalMetadataLocation)

RoleDescriptor = pyxb.binding.basis.element(pyxb.namespace.ExpandedName(Namespace, u'RoleDescriptor'), RoleDescriptorType)
Namespace.addCategoryObject('elementBinding', RoleDescriptor.name().localName(), RoleDescriptor)

AffiliateMember = pyxb.binding.basis.element(pyxb.namespace.ExpandedName(Namespace, u'AffiliateMember'), entityIDType)
Namespace.addCategoryObject('elementBinding', AffiliateMember.name().localName(), AffiliateMember)

AttributeConsumingService = pyxb.binding.basis.element(pyxb.namespace.ExpandedName(Namespace, u'AttributeConsumingService'), AttributeConsumingServiceType)
Namespace.addCategoryObject('elementBinding', AttributeConsumingService.name().localName(), AttributeConsumingService)

Company = pyxb.binding.basis.element(pyxb.namespace.ExpandedName(Namespace, u'Company'), pyxb.binding.datatypes.string)
Namespace.addCategoryObject('elementBinding', Company.name().localName(), Company)

AssertionIDRequestService = pyxb.binding.basis.element(pyxb.namespace.ExpandedName(Namespace, u'AssertionIDRequestService'), EndpointType)
Namespace.addCategoryObject('elementBinding', AssertionIDRequestService.name().localName(), AssertionIDRequestService)


EndpointType._GroupModel = pyxb.binding.content.GroupSequence(
    pyxb.binding.content.ParticleModel(pyxb.binding.content.Wildcard(process_contents=pyxb.binding.content.Wildcard.PC_lax, namespace_constraint=(pyxb.binding.content.Wildcard.NC_not, u'urn:oasis:names:tc:SAML:2.0:metadata')), min_occurs=0L, max_occurs=None)
    )
EndpointType._ContentModel = pyxb.binding.content.ParticleModel(EndpointType._GroupModel, min_occurs=1, max_occurs=1)


IndexedEndpointType._GroupModel = pyxb.binding.content.GroupSequence(
    pyxb.binding.content.ParticleModel(pyxb.binding.content.Wildcard(process_contents=pyxb.binding.content.Wildcard.PC_lax, namespace_constraint=(pyxb.binding.content.Wildcard.NC_not, u'urn:oasis:names:tc:SAML:2.0:metadata')), min_occurs=0L, max_occurs=None)
    )
IndexedEndpointType._ContentModel = pyxb.binding.content.ParticleModel(IndexedEndpointType._GroupModel, min_occurs=1, max_occurs=1)



OrganizationType._AddElement(pyxb.binding.basis.element(pyxb.namespace.ExpandedName(Namespace, u'Extensions'), ExtensionsType, scope=OrganizationType))

OrganizationType._AddElement(pyxb.binding.basis.element(pyxb.namespace.ExpandedName(Namespace, u'OrganizationURL'), localizedURIType, scope=OrganizationType))

OrganizationType._AddElement(pyxb.binding.basis.element(pyxb.namespace.ExpandedName(Namespace, u'OrganizationDisplayName'), localizedNameType, scope=OrganizationType))

OrganizationType._AddElement(pyxb.binding.basis.element(pyxb.namespace.ExpandedName(Namespace, u'OrganizationName'), localizedNameType, scope=OrganizationType))
OrganizationType._GroupModel = pyxb.binding.content.GroupSequence(
    pyxb.binding.content.ParticleModel(OrganizationType._UseForTag(pyxb.namespace.ExpandedName(Namespace, u'Extensions')), min_occurs=0L, max_occurs=1),
    pyxb.binding.content.ParticleModel(OrganizationType._UseForTag(pyxb.namespace.ExpandedName(Namespace, u'OrganizationName')), min_occurs=1, max_occurs=None),
    pyxb.binding.content.ParticleModel(OrganizationType._UseForTag(pyxb.namespace.ExpandedName(Namespace, u'OrganizationDisplayName')), min_occurs=1, max_occurs=None),
    pyxb.binding.content.ParticleModel(OrganizationType._UseForTag(pyxb.namespace.ExpandedName(Namespace, u'OrganizationURL')), min_occurs=1, max_occurs=None)
    )
OrganizationType._ContentModel = pyxb.binding.content.ParticleModel(OrganizationType._GroupModel, min_occurs=1, max_occurs=1)


RequestedAttributeType._GroupModel_ = pyxb.binding.content.GroupSequence(
    pyxb.binding.content.ParticleModel(RequestedAttributeType._UseForTag(pyxb.namespace.ExpandedName(pyxb.namespace.NamespaceForURI(u'urn:oasis:names:tc:SAML:2.0:assertion'), u'AttributeValue')), min_occurs=0L, max_occurs=None)
    )
RequestedAttributeType._ContentModel = pyxb.binding.content.ParticleModel(RequestedAttributeType._GroupModel_, min_occurs=1, max_occurs=1)



RoleDescriptorType._AddElement(pyxb.binding.basis.element(pyxb.namespace.ExpandedName(Namespace, u'Extensions'), ExtensionsType, scope=RoleDescriptorType))

RoleDescriptorType._AddElement(pyxb.binding.basis.element(pyxb.namespace.ExpandedName(Namespace, u'Organization'), OrganizationType, scope=RoleDescriptorType))

RoleDescriptorType._AddElement(pyxb.binding.basis.element(pyxb.namespace.ExpandedName(Namespace, u'KeyDescriptor'), KeyDescriptorType, scope=RoleDescriptorType))

RoleDescriptorType._AddElement(pyxb.binding.basis.element(pyxb.namespace.ExpandedName(pyxb.namespace.NamespaceForURI(u'http://www.w3.org/2000/09/xmldsig#'), u'Signature'), pyxb.bundles.wssplat.ds.SignatureType, scope=RoleDescriptorType))

RoleDescriptorType._AddElement(pyxb.binding.basis.element(pyxb.namespace.ExpandedName(Namespace, u'ContactPerson'), ContactType, scope=RoleDescriptorType))
RoleDescriptorType._GroupModel = pyxb.binding.content.GroupSequence(
    pyxb.binding.content.ParticleModel(RoleDescriptorType._UseForTag(pyxb.namespace.ExpandedName(pyxb.namespace.NamespaceForURI(u'http://www.w3.org/2000/09/xmldsig#'), u'Signature')), min_occurs=0L, max_occurs=1),
    pyxb.binding.content.ParticleModel(RoleDescriptorType._UseForTag(pyxb.namespace.ExpandedName(Namespace, u'Extensions')), min_occurs=0L, max_occurs=1),
    pyxb.binding.content.ParticleModel(RoleDescriptorType._UseForTag(pyxb.namespace.ExpandedName(Namespace, u'KeyDescriptor')), min_occurs=0L, max_occurs=None),
    pyxb.binding.content.ParticleModel(RoleDescriptorType._UseForTag(pyxb.namespace.ExpandedName(Namespace, u'Organization')), min_occurs=0L, max_occurs=1),
    pyxb.binding.content.ParticleModel(RoleDescriptorType._UseForTag(pyxb.namespace.ExpandedName(Namespace, u'ContactPerson')), min_occurs=0L, max_occurs=None)
    )
RoleDescriptorType._ContentModel = pyxb.binding.content.ParticleModel(RoleDescriptorType._GroupModel, min_occurs=1, max_occurs=1)



PDPDescriptorType._AddElement(pyxb.binding.basis.element(pyxb.namespace.ExpandedName(Namespace, u'NameIDFormat'), pyxb.binding.datatypes.anyURI, scope=PDPDescriptorType))

PDPDescriptorType._AddElement(pyxb.binding.basis.element(pyxb.namespace.ExpandedName(Namespace, u'AssertionIDRequestService'), EndpointType, scope=PDPDescriptorType))

PDPDescriptorType._AddElement(pyxb.binding.basis.element(pyxb.namespace.ExpandedName(Namespace, u'AuthzService'), EndpointType, scope=PDPDescriptorType))
PDPDescriptorType._GroupModel_ = pyxb.binding.content.GroupSequence(
    pyxb.binding.content.ParticleModel(PDPDescriptorType._UseForTag(pyxb.namespace.ExpandedName(pyxb.namespace.NamespaceForURI(u'http://www.w3.org/2000/09/xmldsig#'), u'Signature')), min_occurs=0L, max_occurs=1),
    pyxb.binding.content.ParticleModel(PDPDescriptorType._UseForTag(pyxb.namespace.ExpandedName(Namespace, u'Extensions')), min_occurs=0L, max_occurs=1),
    pyxb.binding.content.ParticleModel(PDPDescriptorType._UseForTag(pyxb.namespace.ExpandedName(Namespace, u'KeyDescriptor')), min_occurs=0L, max_occurs=None),
    pyxb.binding.content.ParticleModel(PDPDescriptorType._UseForTag(pyxb.namespace.ExpandedName(Namespace, u'Organization')), min_occurs=0L, max_occurs=1),
    pyxb.binding.content.ParticleModel(PDPDescriptorType._UseForTag(pyxb.namespace.ExpandedName(Namespace, u'ContactPerson')), min_occurs=0L, max_occurs=None)
    )
PDPDescriptorType._GroupModel_2 = pyxb.binding.content.GroupSequence(
    pyxb.binding.content.ParticleModel(PDPDescriptorType._UseForTag(pyxb.namespace.ExpandedName(Namespace, u'AuthzService')), min_occurs=1, max_occurs=None),
    pyxb.binding.content.ParticleModel(PDPDescriptorType._UseForTag(pyxb.namespace.ExpandedName(Namespace, u'AssertionIDRequestService')), min_occurs=0L, max_occurs=None),
    pyxb.binding.content.ParticleModel(PDPDescriptorType._UseForTag(pyxb.namespace.ExpandedName(Namespace, u'NameIDFormat')), min_occurs=0L, max_occurs=None)
    )
PDPDescriptorType._GroupModel = pyxb.binding.content.GroupSequence(
    pyxb.binding.content.ParticleModel(PDPDescriptorType._GroupModel_, min_occurs=1, max_occurs=1),
    pyxb.binding.content.ParticleModel(PDPDescriptorType._GroupModel_2, min_occurs=1, max_occurs=1)
    )
PDPDescriptorType._ContentModel = pyxb.binding.content.ParticleModel(PDPDescriptorType._GroupModel, min_occurs=1, max_occurs=1)


ExtensionsType._GroupModel = pyxb.binding.content.GroupSequence(
    pyxb.binding.content.ParticleModel(pyxb.binding.content.Wildcard(process_contents=pyxb.binding.content.Wildcard.PC_lax, namespace_constraint=(pyxb.binding.content.Wildcard.NC_not, u'urn:oasis:names:tc:SAML:2.0:metadata')), min_occurs=1, max_occurs=None)
    )
ExtensionsType._ContentModel = pyxb.binding.content.ParticleModel(ExtensionsType._GroupModel, min_occurs=1, max_occurs=1)



KeyDescriptorType._AddElement(pyxb.binding.basis.element(pyxb.namespace.ExpandedName(pyxb.namespace.NamespaceForURI(u'http://www.w3.org/2000/09/xmldsig#'), u'KeyInfo'), pyxb.bundles.wssplat.ds.KeyInfoType, scope=KeyDescriptorType))

KeyDescriptorType._AddElement(pyxb.binding.basis.element(pyxb.namespace.ExpandedName(Namespace, u'EncryptionMethod'), pyxb.bundles.wssplat.xenc.EncryptionMethodType, scope=KeyDescriptorType))
KeyDescriptorType._GroupModel = pyxb.binding.content.GroupSequence(
    pyxb.binding.content.ParticleModel(KeyDescriptorType._UseForTag(pyxb.namespace.ExpandedName(pyxb.namespace.NamespaceForURI(u'http://www.w3.org/2000/09/xmldsig#'), u'KeyInfo')), min_occurs=1, max_occurs=1),
    pyxb.binding.content.ParticleModel(KeyDescriptorType._UseForTag(pyxb.namespace.ExpandedName(Namespace, u'EncryptionMethod')), min_occurs=0L, max_occurs=None)
    )
KeyDescriptorType._ContentModel = pyxb.binding.content.ParticleModel(KeyDescriptorType._GroupModel, min_occurs=1, max_occurs=1)



EntitiesDescriptorType._AddElement(pyxb.binding.basis.element(pyxb.namespace.ExpandedName(pyxb.namespace.NamespaceForURI(u'http://www.w3.org/2000/09/xmldsig#'), u'Signature'), pyxb.bundles.wssplat.ds.SignatureType, scope=EntitiesDescriptorType))

EntitiesDescriptorType._AddElement(pyxb.binding.basis.element(pyxb.namespace.ExpandedName(Namespace, u'EntityDescriptor'), EntityDescriptorType, scope=EntitiesDescriptorType))

EntitiesDescriptorType._AddElement(pyxb.binding.basis.element(pyxb.namespace.ExpandedName(Namespace, u'Extensions'), ExtensionsType, scope=EntitiesDescriptorType))

EntitiesDescriptorType._AddElement(pyxb.binding.basis.element(pyxb.namespace.ExpandedName(Namespace, u'EntitiesDescriptor'), EntitiesDescriptorType, scope=EntitiesDescriptorType))
EntitiesDescriptorType._GroupModel_ = pyxb.binding.content.GroupChoice(
    pyxb.binding.content.ParticleModel(EntitiesDescriptorType._UseForTag(pyxb.namespace.ExpandedName(Namespace, u'EntityDescriptor')), min_occurs=1, max_occurs=1),
    pyxb.binding.content.ParticleModel(EntitiesDescriptorType._UseForTag(pyxb.namespace.ExpandedName(Namespace, u'EntitiesDescriptor')), min_occurs=1, max_occurs=1)
    )
EntitiesDescriptorType._GroupModel = pyxb.binding.content.GroupSequence(
    pyxb.binding.content.ParticleModel(EntitiesDescriptorType._UseForTag(pyxb.namespace.ExpandedName(pyxb.namespace.NamespaceForURI(u'http://www.w3.org/2000/09/xmldsig#'), u'Signature')), min_occurs=0L, max_occurs=1),
    pyxb.binding.content.ParticleModel(EntitiesDescriptorType._UseForTag(pyxb.namespace.ExpandedName(Namespace, u'Extensions')), min_occurs=0L, max_occurs=1),
    pyxb.binding.content.ParticleModel(EntitiesDescriptorType._GroupModel_, min_occurs=1L, max_occurs=None)
    )
EntitiesDescriptorType._ContentModel = pyxb.binding.content.ParticleModel(EntitiesDescriptorType._GroupModel, min_occurs=1, max_occurs=1)



ContactType._AddElement(pyxb.binding.basis.element(pyxb.namespace.ExpandedName(Namespace, u'EmailAddress'), pyxb.binding.datatypes.anyURI, scope=ContactType))

ContactType._AddElement(pyxb.binding.basis.element(pyxb.namespace.ExpandedName(Namespace, u'Extensions'), ExtensionsType, scope=ContactType))

ContactType._AddElement(pyxb.binding.basis.element(pyxb.namespace.ExpandedName(Namespace, u'GivenName'), pyxb.binding.datatypes.string, scope=ContactType))

ContactType._AddElement(pyxb.binding.basis.element(pyxb.namespace.ExpandedName(Namespace, u'TelephoneNumber'), pyxb.binding.datatypes.string, scope=ContactType))

ContactType._AddElement(pyxb.binding.basis.element(pyxb.namespace.ExpandedName(Namespace, u'SurName'), pyxb.binding.datatypes.string, scope=ContactType))

ContactType._AddElement(pyxb.binding.basis.element(pyxb.namespace.ExpandedName(Namespace, u'Company'), pyxb.binding.datatypes.string, scope=ContactType))
ContactType._GroupModel = pyxb.binding.content.GroupSequence(
    pyxb.binding.content.ParticleModel(ContactType._UseForTag(pyxb.namespace.ExpandedName(Namespace, u'Extensions')), min_occurs=0L, max_occurs=1),
    pyxb.binding.content.ParticleModel(ContactType._UseForTag(pyxb.namespace.ExpandedName(Namespace, u'Company')), min_occurs=0L, max_occurs=1),
    pyxb.binding.content.ParticleModel(ContactType._UseForTag(pyxb.namespace.ExpandedName(Namespace, u'GivenName')), min_occurs=0L, max_occurs=1),
    pyxb.binding.content.ParticleModel(ContactType._UseForTag(pyxb.namespace.ExpandedName(Namespace, u'SurName')), min_occurs=0L, max_occurs=1),
    pyxb.binding.content.ParticleModel(ContactType._UseForTag(pyxb.namespace.ExpandedName(Namespace, u'EmailAddress')), min_occurs=0L, max_occurs=None),
    pyxb.binding.content.ParticleModel(ContactType._UseForTag(pyxb.namespace.ExpandedName(Namespace, u'TelephoneNumber')), min_occurs=0L, max_occurs=None)
    )
ContactType._ContentModel = pyxb.binding.content.ParticleModel(ContactType._GroupModel, min_occurs=1, max_occurs=1)



AffiliationDescriptorType._AddElement(pyxb.binding.basis.element(pyxb.namespace.ExpandedName(Namespace, u'AffiliateMember'), entityIDType, scope=AffiliationDescriptorType))

AffiliationDescriptorType._AddElement(pyxb.binding.basis.element(pyxb.namespace.ExpandedName(pyxb.namespace.NamespaceForURI(u'http://www.w3.org/2000/09/xmldsig#'), u'Signature'), pyxb.bundles.wssplat.ds.SignatureType, scope=AffiliationDescriptorType))

AffiliationDescriptorType._AddElement(pyxb.binding.basis.element(pyxb.namespace.ExpandedName(Namespace, u'Extensions'), ExtensionsType, scope=AffiliationDescriptorType))

AffiliationDescriptorType._AddElement(pyxb.binding.basis.element(pyxb.namespace.ExpandedName(Namespace, u'KeyDescriptor'), KeyDescriptorType, scope=AffiliationDescriptorType))
AffiliationDescriptorType._GroupModel = pyxb.binding.content.GroupSequence(
    pyxb.binding.content.ParticleModel(AffiliationDescriptorType._UseForTag(pyxb.namespace.ExpandedName(pyxb.namespace.NamespaceForURI(u'http://www.w3.org/2000/09/xmldsig#'), u'Signature')), min_occurs=0L, max_occurs=1),
    pyxb.binding.content.ParticleModel(AffiliationDescriptorType._UseForTag(pyxb.namespace.ExpandedName(Namespace, u'Extensions')), min_occurs=0L, max_occurs=1),
    pyxb.binding.content.ParticleModel(AffiliationDescriptorType._UseForTag(pyxb.namespace.ExpandedName(Namespace, u'AffiliateMember')), min_occurs=1, max_occurs=None),
    pyxb.binding.content.ParticleModel(AffiliationDescriptorType._UseForTag(pyxb.namespace.ExpandedName(Namespace, u'KeyDescriptor')), min_occurs=0L, max_occurs=None)
    )
AffiliationDescriptorType._ContentModel = pyxb.binding.content.ParticleModel(AffiliationDescriptorType._GroupModel, min_occurs=1, max_occurs=1)



EntityDescriptorType._AddElement(pyxb.binding.basis.element(pyxb.namespace.ExpandedName(Namespace, u'SPSSODescriptor'), SPSSODescriptorType, scope=EntityDescriptorType))

EntityDescriptorType._AddElement(pyxb.binding.basis.element(pyxb.namespace.ExpandedName(Namespace, u'PDPDescriptor'), PDPDescriptorType, scope=EntityDescriptorType))

EntityDescriptorType._AddElement(pyxb.binding.basis.element(pyxb.namespace.ExpandedName(Namespace, u'AffiliationDescriptor'), AffiliationDescriptorType, scope=EntityDescriptorType))

EntityDescriptorType._AddElement(pyxb.binding.basis.element(pyxb.namespace.ExpandedName(Namespace, u'ContactPerson'), ContactType, scope=EntityDescriptorType))

EntityDescriptorType._AddElement(pyxb.binding.basis.element(pyxb.namespace.ExpandedName(Namespace, u'RoleDescriptor'), RoleDescriptorType, scope=EntityDescriptorType))

EntityDescriptorType._AddElement(pyxb.binding.basis.element(pyxb.namespace.ExpandedName(Namespace, u'AdditionalMetadataLocation'), AdditionalMetadataLocationType, scope=EntityDescriptorType))

EntityDescriptorType._AddElement(pyxb.binding.basis.element(pyxb.namespace.ExpandedName(Namespace, u'AuthnAuthorityDescriptor'), AuthnAuthorityDescriptorType, scope=EntityDescriptorType))

EntityDescriptorType._AddElement(pyxb.binding.basis.element(pyxb.namespace.ExpandedName(Namespace, u'IDPSSODescriptor'), IDPSSODescriptorType, scope=EntityDescriptorType))

EntityDescriptorType._AddElement(pyxb.binding.basis.element(pyxb.namespace.ExpandedName(Namespace, u'AttributeAuthorityDescriptor'), AttributeAuthorityDescriptorType, scope=EntityDescriptorType))

EntityDescriptorType._AddElement(pyxb.binding.basis.element(pyxb.namespace.ExpandedName(Namespace, u'Extensions'), ExtensionsType, scope=EntityDescriptorType))

EntityDescriptorType._AddElement(pyxb.binding.basis.element(pyxb.namespace.ExpandedName(pyxb.namespace.NamespaceForURI(u'http://www.w3.org/2000/09/xmldsig#'), u'Signature'), pyxb.bundles.wssplat.ds.SignatureType, scope=EntityDescriptorType))

EntityDescriptorType._AddElement(pyxb.binding.basis.element(pyxb.namespace.ExpandedName(Namespace, u'Organization'), OrganizationType, scope=EntityDescriptorType))
EntityDescriptorType._GroupModel_2 = pyxb.binding.content.GroupChoice(
    pyxb.binding.content.ParticleModel(EntityDescriptorType._UseForTag(pyxb.namespace.ExpandedName(Namespace, u'RoleDescriptor')), min_occurs=1, max_occurs=1),
    pyxb.binding.content.ParticleModel(EntityDescriptorType._UseForTag(pyxb.namespace.ExpandedName(Namespace, u'IDPSSODescriptor')), min_occurs=1, max_occurs=1),
    pyxb.binding.content.ParticleModel(EntityDescriptorType._UseForTag(pyxb.namespace.ExpandedName(Namespace, u'SPSSODescriptor')), min_occurs=1, max_occurs=1),
    pyxb.binding.content.ParticleModel(EntityDescriptorType._UseForTag(pyxb.namespace.ExpandedName(Namespace, u'AuthnAuthorityDescriptor')), min_occurs=1, max_occurs=1),
    pyxb.binding.content.ParticleModel(EntityDescriptorType._UseForTag(pyxb.namespace.ExpandedName(Namespace, u'AttributeAuthorityDescriptor')), min_occurs=1, max_occurs=1),
    pyxb.binding.content.ParticleModel(EntityDescriptorType._UseForTag(pyxb.namespace.ExpandedName(Namespace, u'PDPDescriptor')), min_occurs=1, max_occurs=1)
    )
EntityDescriptorType._GroupModel_ = pyxb.binding.content.GroupChoice(
    pyxb.binding.content.ParticleModel(EntityDescriptorType._GroupModel_2, min_occurs=1, max_occurs=None),
    pyxb.binding.content.ParticleModel(EntityDescriptorType._UseForTag(pyxb.namespace.ExpandedName(Namespace, u'AffiliationDescriptor')), min_occurs=1, max_occurs=1)
    )
EntityDescriptorType._GroupModel = pyxb.binding.content.GroupSequence(
    pyxb.binding.content.ParticleModel(EntityDescriptorType._UseForTag(pyxb.namespace.ExpandedName(pyxb.namespace.NamespaceForURI(u'http://www.w3.org/2000/09/xmldsig#'), u'Signature')), min_occurs=0L, max_occurs=1),
    pyxb.binding.content.ParticleModel(EntityDescriptorType._UseForTag(pyxb.namespace.ExpandedName(Namespace, u'Extensions')), min_occurs=0L, max_occurs=1),
    pyxb.binding.content.ParticleModel(EntityDescriptorType._GroupModel_, min_occurs=1, max_occurs=1),
    pyxb.binding.content.ParticleModel(EntityDescriptorType._UseForTag(pyxb.namespace.ExpandedName(Namespace, u'Organization')), min_occurs=0L, max_occurs=1),
    pyxb.binding.content.ParticleModel(EntityDescriptorType._UseForTag(pyxb.namespace.ExpandedName(Namespace, u'ContactPerson')), min_occurs=0L, max_occurs=None),
    pyxb.binding.content.ParticleModel(EntityDescriptorType._UseForTag(pyxb.namespace.ExpandedName(Namespace, u'AdditionalMetadataLocation')), min_occurs=0L, max_occurs=None)
    )
EntityDescriptorType._ContentModel = pyxb.binding.content.ParticleModel(EntityDescriptorType._GroupModel, min_occurs=1, max_occurs=1)



AuthnAuthorityDescriptorType._AddElement(pyxb.binding.basis.element(pyxb.namespace.ExpandedName(Namespace, u'NameIDFormat'), pyxb.binding.datatypes.anyURI, scope=AuthnAuthorityDescriptorType))

AuthnAuthorityDescriptorType._AddElement(pyxb.binding.basis.element(pyxb.namespace.ExpandedName(Namespace, u'AuthnQueryService'), EndpointType, scope=AuthnAuthorityDescriptorType))

AuthnAuthorityDescriptorType._AddElement(pyxb.binding.basis.element(pyxb.namespace.ExpandedName(Namespace, u'AssertionIDRequestService'), EndpointType, scope=AuthnAuthorityDescriptorType))
AuthnAuthorityDescriptorType._GroupModel_ = pyxb.binding.content.GroupSequence(
    pyxb.binding.content.ParticleModel(AuthnAuthorityDescriptorType._UseForTag(pyxb.namespace.ExpandedName(pyxb.namespace.NamespaceForURI(u'http://www.w3.org/2000/09/xmldsig#'), u'Signature')), min_occurs=0L, max_occurs=1),
    pyxb.binding.content.ParticleModel(AuthnAuthorityDescriptorType._UseForTag(pyxb.namespace.ExpandedName(Namespace, u'Extensions')), min_occurs=0L, max_occurs=1),
    pyxb.binding.content.ParticleModel(AuthnAuthorityDescriptorType._UseForTag(pyxb.namespace.ExpandedName(Namespace, u'KeyDescriptor')), min_occurs=0L, max_occurs=None),
    pyxb.binding.content.ParticleModel(AuthnAuthorityDescriptorType._UseForTag(pyxb.namespace.ExpandedName(Namespace, u'Organization')), min_occurs=0L, max_occurs=1),
    pyxb.binding.content.ParticleModel(AuthnAuthorityDescriptorType._UseForTag(pyxb.namespace.ExpandedName(Namespace, u'ContactPerson')), min_occurs=0L, max_occurs=None)
    )
AuthnAuthorityDescriptorType._GroupModel_2 = pyxb.binding.content.GroupSequence(
    pyxb.binding.content.ParticleModel(AuthnAuthorityDescriptorType._UseForTag(pyxb.namespace.ExpandedName(Namespace, u'AuthnQueryService')), min_occurs=1, max_occurs=None),
    pyxb.binding.content.ParticleModel(AuthnAuthorityDescriptorType._UseForTag(pyxb.namespace.ExpandedName(Namespace, u'AssertionIDRequestService')), min_occurs=0L, max_occurs=None),
    pyxb.binding.content.ParticleModel(AuthnAuthorityDescriptorType._UseForTag(pyxb.namespace.ExpandedName(Namespace, u'NameIDFormat')), min_occurs=0L, max_occurs=None)
    )
AuthnAuthorityDescriptorType._GroupModel = pyxb.binding.content.GroupSequence(
    pyxb.binding.content.ParticleModel(AuthnAuthorityDescriptorType._GroupModel_, min_occurs=1, max_occurs=1),
    pyxb.binding.content.ParticleModel(AuthnAuthorityDescriptorType._GroupModel_2, min_occurs=1, max_occurs=1)
    )
AuthnAuthorityDescriptorType._ContentModel = pyxb.binding.content.ParticleModel(AuthnAuthorityDescriptorType._GroupModel, min_occurs=1, max_occurs=1)



AttributeConsumingServiceType._AddElement(pyxb.binding.basis.element(pyxb.namespace.ExpandedName(Namespace, u'RequestedAttribute'), RequestedAttributeType, scope=AttributeConsumingServiceType))

AttributeConsumingServiceType._AddElement(pyxb.binding.basis.element(pyxb.namespace.ExpandedName(Namespace, u'ServiceName'), localizedNameType, scope=AttributeConsumingServiceType))

AttributeConsumingServiceType._AddElement(pyxb.binding.basis.element(pyxb.namespace.ExpandedName(Namespace, u'ServiceDescription'), localizedNameType, scope=AttributeConsumingServiceType))
AttributeConsumingServiceType._GroupModel = pyxb.binding.content.GroupSequence(
    pyxb.binding.content.ParticleModel(AttributeConsumingServiceType._UseForTag(pyxb.namespace.ExpandedName(Namespace, u'ServiceName')), min_occurs=1, max_occurs=None),
    pyxb.binding.content.ParticleModel(AttributeConsumingServiceType._UseForTag(pyxb.namespace.ExpandedName(Namespace, u'ServiceDescription')), min_occurs=0L, max_occurs=None),
    pyxb.binding.content.ParticleModel(AttributeConsumingServiceType._UseForTag(pyxb.namespace.ExpandedName(Namespace, u'RequestedAttribute')), min_occurs=1, max_occurs=None)
    )
AttributeConsumingServiceType._ContentModel = pyxb.binding.content.ParticleModel(AttributeConsumingServiceType._GroupModel, min_occurs=1, max_occurs=1)



SSODescriptorType._AddElement(pyxb.binding.basis.element(pyxb.namespace.ExpandedName(Namespace, u'SingleLogoutService'), EndpointType, scope=SSODescriptorType))

SSODescriptorType._AddElement(pyxb.binding.basis.element(pyxb.namespace.ExpandedName(Namespace, u'ManageNameIDService'), EndpointType, scope=SSODescriptorType))

SSODescriptorType._AddElement(pyxb.binding.basis.element(pyxb.namespace.ExpandedName(Namespace, u'ArtifactResolutionService'), IndexedEndpointType, scope=SSODescriptorType))

SSODescriptorType._AddElement(pyxb.binding.basis.element(pyxb.namespace.ExpandedName(Namespace, u'NameIDFormat'), pyxb.binding.datatypes.anyURI, scope=SSODescriptorType))
SSODescriptorType._GroupModel_ = pyxb.binding.content.GroupSequence(
    pyxb.binding.content.ParticleModel(SSODescriptorType._UseForTag(pyxb.namespace.ExpandedName(pyxb.namespace.NamespaceForURI(u'http://www.w3.org/2000/09/xmldsig#'), u'Signature')), min_occurs=0L, max_occurs=1),
    pyxb.binding.content.ParticleModel(SSODescriptorType._UseForTag(pyxb.namespace.ExpandedName(Namespace, u'Extensions')), min_occurs=0L, max_occurs=1),
    pyxb.binding.content.ParticleModel(SSODescriptorType._UseForTag(pyxb.namespace.ExpandedName(Namespace, u'KeyDescriptor')), min_occurs=0L, max_occurs=None),
    pyxb.binding.content.ParticleModel(SSODescriptorType._UseForTag(pyxb.namespace.ExpandedName(Namespace, u'Organization')), min_occurs=0L, max_occurs=1),
    pyxb.binding.content.ParticleModel(SSODescriptorType._UseForTag(pyxb.namespace.ExpandedName(Namespace, u'ContactPerson')), min_occurs=0L, max_occurs=None)
    )
SSODescriptorType._GroupModel_2 = pyxb.binding.content.GroupSequence(
    pyxb.binding.content.ParticleModel(SSODescriptorType._UseForTag(pyxb.namespace.ExpandedName(Namespace, u'ArtifactResolutionService')), min_occurs=0L, max_occurs=None),
    pyxb.binding.content.ParticleModel(SSODescriptorType._UseForTag(pyxb.namespace.ExpandedName(Namespace, u'SingleLogoutService')), min_occurs=0L, max_occurs=None),
    pyxb.binding.content.ParticleModel(SSODescriptorType._UseForTag(pyxb.namespace.ExpandedName(Namespace, u'ManageNameIDService')), min_occurs=0L, max_occurs=None),
    pyxb.binding.content.ParticleModel(SSODescriptorType._UseForTag(pyxb.namespace.ExpandedName(Namespace, u'NameIDFormat')), min_occurs=0L, max_occurs=None)
    )
SSODescriptorType._GroupModel = pyxb.binding.content.GroupSequence(
    pyxb.binding.content.ParticleModel(SSODescriptorType._GroupModel_, min_occurs=1, max_occurs=1),
    pyxb.binding.content.ParticleModel(SSODescriptorType._GroupModel_2, min_occurs=1, max_occurs=1)
    )
SSODescriptorType._ContentModel = pyxb.binding.content.ParticleModel(SSODescriptorType._GroupModel, min_occurs=1, max_occurs=1)



IDPSSODescriptorType._AddElement(pyxb.binding.basis.element(pyxb.namespace.ExpandedName(Namespace, u'AttributeProfile'), pyxb.binding.datatypes.anyURI, scope=IDPSSODescriptorType))

IDPSSODescriptorType._AddElement(pyxb.binding.basis.element(pyxb.namespace.ExpandedName(Namespace, u'NameIDMappingService'), EndpointType, scope=IDPSSODescriptorType))

IDPSSODescriptorType._AddElement(pyxb.binding.basis.element(pyxb.namespace.ExpandedName(pyxb.namespace.NamespaceForURI(u'urn:oasis:names:tc:SAML:2.0:assertion'), u'Attribute'), pyxb.bundles.saml20.assertion.AttributeType, scope=IDPSSODescriptorType))

IDPSSODescriptorType._AddElement(pyxb.binding.basis.element(pyxb.namespace.ExpandedName(Namespace, u'AssertionIDRequestService'), EndpointType, scope=IDPSSODescriptorType))

IDPSSODescriptorType._AddElement(pyxb.binding.basis.element(pyxb.namespace.ExpandedName(Namespace, u'SingleSignOnService'), EndpointType, scope=IDPSSODescriptorType))
IDPSSODescriptorType._GroupModel_2 = pyxb.binding.content.GroupSequence(
    pyxb.binding.content.ParticleModel(IDPSSODescriptorType._UseForTag(pyxb.namespace.ExpandedName(pyxb.namespace.NamespaceForURI(u'http://www.w3.org/2000/09/xmldsig#'), u'Signature')), min_occurs=0L, max_occurs=1),
    pyxb.binding.content.ParticleModel(IDPSSODescriptorType._UseForTag(pyxb.namespace.ExpandedName(Namespace, u'Extensions')), min_occurs=0L, max_occurs=1),
    pyxb.binding.content.ParticleModel(IDPSSODescriptorType._UseForTag(pyxb.namespace.ExpandedName(Namespace, u'KeyDescriptor')), min_occurs=0L, max_occurs=None),
    pyxb.binding.content.ParticleModel(IDPSSODescriptorType._UseForTag(pyxb.namespace.ExpandedName(Namespace, u'Organization')), min_occurs=0L, max_occurs=1),
    pyxb.binding.content.ParticleModel(IDPSSODescriptorType._UseForTag(pyxb.namespace.ExpandedName(Namespace, u'ContactPerson')), min_occurs=0L, max_occurs=None)
    )
IDPSSODescriptorType._GroupModel_3 = pyxb.binding.content.GroupSequence(
    pyxb.binding.content.ParticleModel(IDPSSODescriptorType._UseForTag(pyxb.namespace.ExpandedName(Namespace, u'ArtifactResolutionService')), min_occurs=0L, max_occurs=None),
    pyxb.binding.content.ParticleModel(IDPSSODescriptorType._UseForTag(pyxb.namespace.ExpandedName(Namespace, u'SingleLogoutService')), min_occurs=0L, max_occurs=None),
    pyxb.binding.content.ParticleModel(IDPSSODescriptorType._UseForTag(pyxb.namespace.ExpandedName(Namespace, u'ManageNameIDService')), min_occurs=0L, max_occurs=None),
    pyxb.binding.content.ParticleModel(IDPSSODescriptorType._UseForTag(pyxb.namespace.ExpandedName(Namespace, u'NameIDFormat')), min_occurs=0L, max_occurs=None)
    )
IDPSSODescriptorType._GroupModel_ = pyxb.binding.content.GroupSequence(
    pyxb.binding.content.ParticleModel(IDPSSODescriptorType._GroupModel_2, min_occurs=1, max_occurs=1),
    pyxb.binding.content.ParticleModel(IDPSSODescriptorType._GroupModel_3, min_occurs=1, max_occurs=1)
    )
IDPSSODescriptorType._GroupModel_4 = pyxb.binding.content.GroupSequence(
    pyxb.binding.content.ParticleModel(IDPSSODescriptorType._UseForTag(pyxb.namespace.ExpandedName(Namespace, u'SingleSignOnService')), min_occurs=1, max_occurs=None),
    pyxb.binding.content.ParticleModel(IDPSSODescriptorType._UseForTag(pyxb.namespace.ExpandedName(Namespace, u'NameIDMappingService')), min_occurs=0L, max_occurs=None),
    pyxb.binding.content.ParticleModel(IDPSSODescriptorType._UseForTag(pyxb.namespace.ExpandedName(Namespace, u'AssertionIDRequestService')), min_occurs=0L, max_occurs=None),
    pyxb.binding.content.ParticleModel(IDPSSODescriptorType._UseForTag(pyxb.namespace.ExpandedName(Namespace, u'AttributeProfile')), min_occurs=0L, max_occurs=None),
    pyxb.binding.content.ParticleModel(IDPSSODescriptorType._UseForTag(pyxb.namespace.ExpandedName(pyxb.namespace.NamespaceForURI(u'urn:oasis:names:tc:SAML:2.0:assertion'), u'Attribute')), min_occurs=0L, max_occurs=None)
    )
IDPSSODescriptorType._GroupModel = pyxb.binding.content.GroupSequence(
    pyxb.binding.content.ParticleModel(IDPSSODescriptorType._GroupModel_, min_occurs=1, max_occurs=1),
    pyxb.binding.content.ParticleModel(IDPSSODescriptorType._GroupModel_4, min_occurs=1, max_occurs=1)
    )
IDPSSODescriptorType._ContentModel = pyxb.binding.content.ParticleModel(IDPSSODescriptorType._GroupModel, min_occurs=1, max_occurs=1)



AttributeAuthorityDescriptorType._AddElement(pyxb.binding.basis.element(pyxb.namespace.ExpandedName(pyxb.namespace.NamespaceForURI(u'urn:oasis:names:tc:SAML:2.0:assertion'), u'Attribute'), pyxb.bundles.saml20.assertion.AttributeType, scope=AttributeAuthorityDescriptorType))

AttributeAuthorityDescriptorType._AddElement(pyxb.binding.basis.element(pyxb.namespace.ExpandedName(Namespace, u'NameIDFormat'), pyxb.binding.datatypes.anyURI, scope=AttributeAuthorityDescriptorType))

AttributeAuthorityDescriptorType._AddElement(pyxb.binding.basis.element(pyxb.namespace.ExpandedName(Namespace, u'AttributeService'), EndpointType, scope=AttributeAuthorityDescriptorType))

AttributeAuthorityDescriptorType._AddElement(pyxb.binding.basis.element(pyxb.namespace.ExpandedName(Namespace, u'AttributeProfile'), pyxb.binding.datatypes.anyURI, scope=AttributeAuthorityDescriptorType))

AttributeAuthorityDescriptorType._AddElement(pyxb.binding.basis.element(pyxb.namespace.ExpandedName(Namespace, u'AssertionIDRequestService'), EndpointType, scope=AttributeAuthorityDescriptorType))
AttributeAuthorityDescriptorType._GroupModel_ = pyxb.binding.content.GroupSequence(
    pyxb.binding.content.ParticleModel(AttributeAuthorityDescriptorType._UseForTag(pyxb.namespace.ExpandedName(pyxb.namespace.NamespaceForURI(u'http://www.w3.org/2000/09/xmldsig#'), u'Signature')), min_occurs=0L, max_occurs=1),
    pyxb.binding.content.ParticleModel(AttributeAuthorityDescriptorType._UseForTag(pyxb.namespace.ExpandedName(Namespace, u'Extensions')), min_occurs=0L, max_occurs=1),
    pyxb.binding.content.ParticleModel(AttributeAuthorityDescriptorType._UseForTag(pyxb.namespace.ExpandedName(Namespace, u'KeyDescriptor')), min_occurs=0L, max_occurs=None),
    pyxb.binding.content.ParticleModel(AttributeAuthorityDescriptorType._UseForTag(pyxb.namespace.ExpandedName(Namespace, u'Organization')), min_occurs=0L, max_occurs=1),
    pyxb.binding.content.ParticleModel(AttributeAuthorityDescriptorType._UseForTag(pyxb.namespace.ExpandedName(Namespace, u'ContactPerson')), min_occurs=0L, max_occurs=None)
    )
AttributeAuthorityDescriptorType._GroupModel_2 = pyxb.binding.content.GroupSequence(
    pyxb.binding.content.ParticleModel(AttributeAuthorityDescriptorType._UseForTag(pyxb.namespace.ExpandedName(Namespace, u'AttributeService')), min_occurs=1, max_occurs=None),
    pyxb.binding.content.ParticleModel(AttributeAuthorityDescriptorType._UseForTag(pyxb.namespace.ExpandedName(Namespace, u'AssertionIDRequestService')), min_occurs=0L, max_occurs=None),
    pyxb.binding.content.ParticleModel(AttributeAuthorityDescriptorType._UseForTag(pyxb.namespace.ExpandedName(Namespace, u'NameIDFormat')), min_occurs=0L, max_occurs=None),
    pyxb.binding.content.ParticleModel(AttributeAuthorityDescriptorType._UseForTag(pyxb.namespace.ExpandedName(Namespace, u'AttributeProfile')), min_occurs=0L, max_occurs=None),
    pyxb.binding.content.ParticleModel(AttributeAuthorityDescriptorType._UseForTag(pyxb.namespace.ExpandedName(pyxb.namespace.NamespaceForURI(u'urn:oasis:names:tc:SAML:2.0:assertion'), u'Attribute')), min_occurs=0L, max_occurs=None)
    )
AttributeAuthorityDescriptorType._GroupModel = pyxb.binding.content.GroupSequence(
    pyxb.binding.content.ParticleModel(AttributeAuthorityDescriptorType._GroupModel_, min_occurs=1, max_occurs=1),
    pyxb.binding.content.ParticleModel(AttributeAuthorityDescriptorType._GroupModel_2, min_occurs=1, max_occurs=1)
    )
AttributeAuthorityDescriptorType._ContentModel = pyxb.binding.content.ParticleModel(AttributeAuthorityDescriptorType._GroupModel, min_occurs=1, max_occurs=1)



SPSSODescriptorType._AddElement(pyxb.binding.basis.element(pyxb.namespace.ExpandedName(Namespace, u'AssertionConsumerService'), IndexedEndpointType, scope=SPSSODescriptorType))

SPSSODescriptorType._AddElement(pyxb.binding.basis.element(pyxb.namespace.ExpandedName(Namespace, u'AttributeConsumingService'), AttributeConsumingServiceType, scope=SPSSODescriptorType))
SPSSODescriptorType._GroupModel_2 = pyxb.binding.content.GroupSequence(
    pyxb.binding.content.ParticleModel(SPSSODescriptorType._UseForTag(pyxb.namespace.ExpandedName(pyxb.namespace.NamespaceForURI(u'http://www.w3.org/2000/09/xmldsig#'), u'Signature')), min_occurs=0L, max_occurs=1),
    pyxb.binding.content.ParticleModel(SPSSODescriptorType._UseForTag(pyxb.namespace.ExpandedName(Namespace, u'Extensions')), min_occurs=0L, max_occurs=1),
    pyxb.binding.content.ParticleModel(SPSSODescriptorType._UseForTag(pyxb.namespace.ExpandedName(Namespace, u'KeyDescriptor')), min_occurs=0L, max_occurs=None),
    pyxb.binding.content.ParticleModel(SPSSODescriptorType._UseForTag(pyxb.namespace.ExpandedName(Namespace, u'Organization')), min_occurs=0L, max_occurs=1),
    pyxb.binding.content.ParticleModel(SPSSODescriptorType._UseForTag(pyxb.namespace.ExpandedName(Namespace, u'ContactPerson')), min_occurs=0L, max_occurs=None)
    )
SPSSODescriptorType._GroupModel_3 = pyxb.binding.content.GroupSequence(
    pyxb.binding.content.ParticleModel(SPSSODescriptorType._UseForTag(pyxb.namespace.ExpandedName(Namespace, u'ArtifactResolutionService')), min_occurs=0L, max_occurs=None),
    pyxb.binding.content.ParticleModel(SPSSODescriptorType._UseForTag(pyxb.namespace.ExpandedName(Namespace, u'SingleLogoutService')), min_occurs=0L, max_occurs=None),
    pyxb.binding.content.ParticleModel(SPSSODescriptorType._UseForTag(pyxb.namespace.ExpandedName(Namespace, u'ManageNameIDService')), min_occurs=0L, max_occurs=None),
    pyxb.binding.content.ParticleModel(SPSSODescriptorType._UseForTag(pyxb.namespace.ExpandedName(Namespace, u'NameIDFormat')), min_occurs=0L, max_occurs=None)
    )
SPSSODescriptorType._GroupModel_ = pyxb.binding.content.GroupSequence(
    pyxb.binding.content.ParticleModel(SPSSODescriptorType._GroupModel_2, min_occurs=1, max_occurs=1),
    pyxb.binding.content.ParticleModel(SPSSODescriptorType._GroupModel_3, min_occurs=1, max_occurs=1)
    )
SPSSODescriptorType._GroupModel_4 = pyxb.binding.content.GroupSequence(
    pyxb.binding.content.ParticleModel(SPSSODescriptorType._UseForTag(pyxb.namespace.ExpandedName(Namespace, u'AssertionConsumerService')), min_occurs=1, max_occurs=None),
    pyxb.binding.content.ParticleModel(SPSSODescriptorType._UseForTag(pyxb.namespace.ExpandedName(Namespace, u'AttributeConsumingService')), min_occurs=0L, max_occurs=None)
    )
SPSSODescriptorType._GroupModel = pyxb.binding.content.GroupSequence(
    pyxb.binding.content.ParticleModel(SPSSODescriptorType._GroupModel_, min_occurs=1, max_occurs=1),
    pyxb.binding.content.ParticleModel(SPSSODescriptorType._GroupModel_4, min_occurs=1, max_occurs=1)
    )
SPSSODescriptorType._ContentModel = pyxb.binding.content.ParticleModel(SPSSODescriptorType._GroupModel, min_occurs=1, max_occurs=1)
