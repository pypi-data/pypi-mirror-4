# ./pyxb/bundles/wssplat/raw/wsdl20.py
# -*- coding: utf-8 -*-
# PyXB bindings for NM:19bbf5816d83775dc94d85cfc7c87689406810ec
# Generated 2012-11-01 15:13:33.412271 by PyXB version 1.1.5
# Namespace http://www.w3.org/ns/wsdl

import pyxb
import pyxb.binding
import pyxb.binding.saxer
import StringIO
import pyxb.utils.utility
import pyxb.utils.domutils
import sys

# Unique identifier for bindings created at the same time
_GenerationUID = pyxb.utils.utility.UniqueIdentifier('urn:uuid:9c608308-2460-11e2-b769-c8600024e903')

# Import bindings for namespaces imported into schema
import pyxb.binding.datatypes

Namespace = pyxb.namespace.NamespaceForURI(u'http://www.w3.org/ns/wsdl', create_if_missing=True)
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


# Atomic simple type: [anonymous]
class STD_ANON (pyxb.binding.datatypes.token, pyxb.binding.basis.enumeration_mixin):

    """An atomic simple type."""

    _ExpandedName = None
    _DefinitionLocation = pyxb.utils.utility.Location('/tmp/pyxbdist.RHB65sy/PyXB-1.1.5/pyxb/bundles/wssplat/schemas/wsdl20.xsd', 215, 6)
    _Documentation = None
STD_ANON._CF_enumeration = pyxb.binding.facets.CF_enumeration(value_datatype=STD_ANON, enum_prefix=None)
STD_ANON.any = STD_ANON._CF_enumeration.addEnumeration(unicode_value=u'#any', tag=u'any')
STD_ANON.none = STD_ANON._CF_enumeration.addEnumeration(unicode_value=u'#none', tag=u'none')
STD_ANON.other = STD_ANON._CF_enumeration.addEnumeration(unicode_value=u'#other', tag=u'other')
STD_ANON._InitializeFacetMap(STD_ANON._CF_enumeration)

# Union simple type: {http://www.w3.org/ns/wsdl}ElementReferenceType
# superclasses pyxb.binding.datatypes.anySimpleType
class ElementReferenceType (pyxb.binding.basis.STD_union):

    """
      Use the QName of a GED that describes the content, 
      #any for any content, 
      #none for empty content, or 
      #other for content described by some other extension attribute that references a declaration in a non-XML extension type system.
      """

    _ExpandedName = pyxb.namespace.ExpandedName(Namespace, u'ElementReferenceType')
    _DefinitionLocation = pyxb.utils.utility.Location('/tmp/pyxbdist.RHB65sy/PyXB-1.1.5/pyxb/bundles/wssplat/schemas/wsdl20.xsd', 205, 2)
    _Documentation = u'\n      Use the QName of a GED that describes the content, \n      #any for any content, \n      #none for empty content, or \n      #other for content described by some other extension attribute that references a declaration in a non-XML extension type system.\n      '

    _MemberTypes = ( pyxb.binding.datatypes.QName, STD_ANON, )
ElementReferenceType._CF_pattern = pyxb.binding.facets.CF_pattern()
ElementReferenceType._CF_enumeration = pyxb.binding.facets.CF_enumeration(value_datatype=ElementReferenceType)
ElementReferenceType.any = u'#any'                # originally STD_ANON.any
ElementReferenceType.none = u'#none'              # originally STD_ANON.none
ElementReferenceType.other = u'#other'            # originally STD_ANON.other
ElementReferenceType._InitializeFacetMap(ElementReferenceType._CF_pattern,
   ElementReferenceType._CF_enumeration)
Namespace.addCategoryObject('typeBinding', u'ElementReferenceType', ElementReferenceType)

# List simple type: [anonymous]
# superclasses pyxb.binding.datatypes.anySimpleType
class STD_ANON_ (pyxb.binding.basis.STD_list):

    """Simple type that is a list of pyxb.binding.datatypes.anyURI."""

    _ExpandedName = None
    _DefinitionLocation = pyxb.utils.utility.Location('/tmp/pyxbdist.RHB65sy/PyXB-1.1.5/pyxb/bundles/wssplat/schemas/wsdl20.xsd', 167, 4)
    _Documentation = None

    _ItemType = pyxb.binding.datatypes.anyURI
STD_ANON_._InitializeFacetMap()

# List simple type: [anonymous]
# superclasses pyxb.binding.datatypes.anySimpleType
class STD_ANON_2 (pyxb.binding.basis.STD_list):

    """Simple type that is a list of pyxb.binding.datatypes.QName."""

    _ExpandedName = None
    _DefinitionLocation = pyxb.utils.utility.Location('/tmp/pyxbdist.RHB65sy/PyXB-1.1.5/pyxb/bundles/wssplat/schemas/wsdl20.xsd', 162, 4)
    _Documentation = None

    _ItemType = pyxb.binding.datatypes.QName
STD_ANON_2._InitializeFacetMap()

# Complex type {http://www.w3.org/ns/wsdl}DocumentedType with content type ELEMENT_ONLY
class DocumentedType (pyxb.binding.basis.complexTypeDefinition):
    _TypeDefinition = None
    _ContentTypeTag = pyxb.binding.basis.complexTypeDefinition._CT_ELEMENT_ONLY
    _Abstract = False
    _ExpandedName = pyxb.namespace.ExpandedName(Namespace, u'DocumentedType')
    _DefinitionLocation = pyxb.utils.utility.Location('/tmp/pyxbdist.RHB65sy/PyXB-1.1.5/pyxb/bundles/wssplat/schemas/wsdl20.xsd', 30, 2)
    # Base type is pyxb.binding.datatypes.anyType
    
    # Element {http://www.w3.org/ns/wsdl}documentation uses Python identifier documentation
    __documentation = pyxb.binding.content.ElementUse(pyxb.namespace.ExpandedName(Namespace, u'documentation'), 'documentation', '__httpwww_w3_orgnswsdl_DocumentedType_httpwww_w3_orgnswsdldocumentation', True)
    __documentation._DeclarationLocation = pyxb.utils.utility.Location('/tmp/pyxbdist.RHB65sy/PyXB-1.1.5/pyxb/bundles/wssplat/schemas/wsdl20.xsd', 22, 2)
    __documentation._UseLocation = pyxb.utils.utility.Location('/tmp/pyxbdist.RHB65sy/PyXB-1.1.5/pyxb/bundles/wssplat/schemas/wsdl20.xsd', 36, 4)

    
    documentation = property(__documentation.value, __documentation.set, None, None)


    _ElementMap = {
        __documentation.name() : __documentation
    }
    _AttributeMap = {
        
    }
Namespace.addCategoryObject('typeBinding', u'DocumentedType', DocumentedType)


# Complex type {http://www.w3.org/ns/wsdl}ExtensibleDocumentedType with content type ELEMENT_ONLY
class ExtensibleDocumentedType (DocumentedType):
    _TypeDefinition = None
    _ContentTypeTag = pyxb.binding.basis.complexTypeDefinition._CT_ELEMENT_ONLY
    _Abstract = True
    _ExpandedName = pyxb.namespace.ExpandedName(Namespace, u'ExtensibleDocumentedType')
    _DefinitionLocation = pyxb.utils.utility.Location('/tmp/pyxbdist.RHB65sy/PyXB-1.1.5/pyxb/bundles/wssplat/schemas/wsdl20.xsd', 41, 2)
    # Base type is DocumentedType
    
    # Element documentation ({http://www.w3.org/ns/wsdl}documentation) inherited from {http://www.w3.org/ns/wsdl}DocumentedType
    _AttributeWildcard = pyxb.binding.content.Wildcard(process_contents=pyxb.binding.content.Wildcard.PC_lax, namespace_constraint=(pyxb.binding.content.Wildcard.NC_not, u'http://www.w3.org/ns/wsdl'))

    _ElementMap = DocumentedType._ElementMap.copy()
    _ElementMap.update({
        
    })
    _AttributeMap = DocumentedType._AttributeMap.copy()
    _AttributeMap.update({
        
    })
Namespace.addCategoryObject('typeBinding', u'ExtensibleDocumentedType', ExtensibleDocumentedType)


# Complex type {http://www.w3.org/ns/wsdl}EndpointType with content type ELEMENT_ONLY
class EndpointType (ExtensibleDocumentedType):
    _TypeDefinition = None
    _ContentTypeTag = pyxb.binding.basis.complexTypeDefinition._CT_ELEMENT_ONLY
    _Abstract = False
    _ExpandedName = pyxb.namespace.ExpandedName(Namespace, u'EndpointType')
    _DefinitionLocation = pyxb.utils.utility.Location('/tmp/pyxbdist.RHB65sy/PyXB-1.1.5/pyxb/bundles/wssplat/schemas/wsdl20.xsd', 336, 2)
    # Base type is ExtensibleDocumentedType
    
    # Element documentation ({http://www.w3.org/ns/wsdl}documentation) inherited from {http://www.w3.org/ns/wsdl}DocumentedType
    
    # Attribute binding uses Python identifier binding
    __binding = pyxb.binding.content.AttributeUse(pyxb.namespace.ExpandedName(None, u'binding'), 'binding', '__httpwww_w3_orgnswsdl_EndpointType_binding', pyxb.binding.datatypes.QName, required=True)
    __binding._DeclarationLocation = pyxb.utils.utility.Location('/tmp/pyxbdist.RHB65sy/PyXB-1.1.5/pyxb/bundles/wssplat/schemas/wsdl20.xsd', 343, 8)
    __binding._UseLocation = pyxb.utils.utility.Location('/tmp/pyxbdist.RHB65sy/PyXB-1.1.5/pyxb/bundles/wssplat/schemas/wsdl20.xsd', 343, 8)
    
    binding = property(__binding.value, __binding.set, None, None)

    
    # Attribute address uses Python identifier address
    __address = pyxb.binding.content.AttributeUse(pyxb.namespace.ExpandedName(None, u'address'), 'address', '__httpwww_w3_orgnswsdl_EndpointType_address', pyxb.binding.datatypes.anyURI)
    __address._DeclarationLocation = pyxb.utils.utility.Location('/tmp/pyxbdist.RHB65sy/PyXB-1.1.5/pyxb/bundles/wssplat/schemas/wsdl20.xsd', 344, 8)
    __address._UseLocation = pyxb.utils.utility.Location('/tmp/pyxbdist.RHB65sy/PyXB-1.1.5/pyxb/bundles/wssplat/schemas/wsdl20.xsd', 344, 8)
    
    address = property(__address.value, __address.set, None, None)

    
    # Attribute name uses Python identifier name
    __name = pyxb.binding.content.AttributeUse(pyxb.namespace.ExpandedName(None, u'name'), 'name', '__httpwww_w3_orgnswsdl_EndpointType_name', pyxb.binding.datatypes.NCName, required=True)
    __name._DeclarationLocation = pyxb.utils.utility.Location('/tmp/pyxbdist.RHB65sy/PyXB-1.1.5/pyxb/bundles/wssplat/schemas/wsdl20.xsd', 342, 8)
    __name._UseLocation = pyxb.utils.utility.Location('/tmp/pyxbdist.RHB65sy/PyXB-1.1.5/pyxb/bundles/wssplat/schemas/wsdl20.xsd', 342, 8)
    
    name = property(__name.value, __name.set, None, None)

    _AttributeWildcard = pyxb.binding.content.Wildcard(process_contents=pyxb.binding.content.Wildcard.PC_lax, namespace_constraint=(pyxb.binding.content.Wildcard.NC_not, u'http://www.w3.org/ns/wsdl'))
    _HasWildcardElement = True

    _ElementMap = ExtensibleDocumentedType._ElementMap.copy()
    _ElementMap.update({
        
    })
    _AttributeMap = ExtensibleDocumentedType._AttributeMap.copy()
    _AttributeMap.update({
        __binding.name() : __binding,
        __address.name() : __address,
        __name.name() : __name
    })
Namespace.addCategoryObject('typeBinding', u'EndpointType', EndpointType)


# Complex type {http://www.w3.org/ns/wsdl}BindingFaultType with content type ELEMENT_ONLY
class BindingFaultType (ExtensibleDocumentedType):
    _TypeDefinition = None
    _ContentTypeTag = pyxb.binding.basis.complexTypeDefinition._CT_ELEMENT_ONLY
    _Abstract = False
    _ExpandedName = pyxb.namespace.ExpandedName(Namespace, u'BindingFaultType')
    _DefinitionLocation = pyxb.utils.utility.Location('/tmp/pyxbdist.RHB65sy/PyXB-1.1.5/pyxb/bundles/wssplat/schemas/wsdl20.xsd', 304, 2)
    # Base type is ExtensibleDocumentedType
    
    # Element documentation ({http://www.w3.org/ns/wsdl}documentation) inherited from {http://www.w3.org/ns/wsdl}DocumentedType
    
    # Attribute ref uses Python identifier ref
    __ref = pyxb.binding.content.AttributeUse(pyxb.namespace.ExpandedName(None, u'ref'), 'ref', '__httpwww_w3_orgnswsdl_BindingFaultType_ref', pyxb.binding.datatypes.QName, required=True)
    __ref._DeclarationLocation = pyxb.utils.utility.Location('/tmp/pyxbdist.RHB65sy/PyXB-1.1.5/pyxb/bundles/wssplat/schemas/wsdl20.xsd', 310, 8)
    __ref._UseLocation = pyxb.utils.utility.Location('/tmp/pyxbdist.RHB65sy/PyXB-1.1.5/pyxb/bundles/wssplat/schemas/wsdl20.xsd', 310, 8)
    
    ref = property(__ref.value, __ref.set, None, None)

    _AttributeWildcard = pyxb.binding.content.Wildcard(process_contents=pyxb.binding.content.Wildcard.PC_lax, namespace_constraint=(pyxb.binding.content.Wildcard.NC_not, u'http://www.w3.org/ns/wsdl'))
    _HasWildcardElement = True

    _ElementMap = ExtensibleDocumentedType._ElementMap.copy()
    _ElementMap.update({
        
    })
    _AttributeMap = ExtensibleDocumentedType._AttributeMap.copy()
    _AttributeMap.update({
        __ref.name() : __ref
    })
Namespace.addCategoryObject('typeBinding', u'BindingFaultType', BindingFaultType)


# Complex type {http://www.w3.org/ns/wsdl}InterfaceOperationType with content type ELEMENT_ONLY
class InterfaceOperationType (ExtensibleDocumentedType):
    _TypeDefinition = None
    _ContentTypeTag = pyxb.binding.basis.complexTypeDefinition._CT_ELEMENT_ONLY
    _Abstract = False
    _ExpandedName = pyxb.namespace.ExpandedName(Namespace, u'InterfaceOperationType')
    _DefinitionLocation = pyxb.utils.utility.Location('/tmp/pyxbdist.RHB65sy/PyXB-1.1.5/pyxb/bundles/wssplat/schemas/wsdl20.xsd', 175, 2)
    # Base type is ExtensibleDocumentedType
    
    # Element documentation ({http://www.w3.org/ns/wsdl}documentation) inherited from {http://www.w3.org/ns/wsdl}DocumentedType
    
    # Element {http://www.w3.org/ns/wsdl}outfault uses Python identifier outfault
    __outfault = pyxb.binding.content.ElementUse(pyxb.namespace.ExpandedName(Namespace, u'outfault'), 'outfault', '__httpwww_w3_orgnswsdl_InterfaceOperationType_httpwww_w3_orgnswsdloutfault', True)
    __outfault._DeclarationLocation = pyxb.utils.utility.Location('/tmp/pyxbdist.RHB65sy/PyXB-1.1.5/pyxb/bundles/wssplat/schemas/wsdl20.xsd', 182, 10)
    __outfault._UseLocation = None

    
    outfault = property(__outfault.value, __outfault.set, None, None)

    
    # Element {http://www.w3.org/ns/wsdl}input uses Python identifier input
    __input = pyxb.binding.content.ElementUse(pyxb.namespace.ExpandedName(Namespace, u'input'), 'input', '__httpwww_w3_orgnswsdl_InterfaceOperationType_httpwww_w3_orgnswsdlinput', True)
    __input._DeclarationLocation = pyxb.utils.utility.Location('/tmp/pyxbdist.RHB65sy/PyXB-1.1.5/pyxb/bundles/wssplat/schemas/wsdl20.xsd', 179, 10)
    __input._UseLocation = None

    
    input = property(__input.value, __input.set, None, None)

    
    # Element {http://www.w3.org/ns/wsdl}infault uses Python identifier infault
    __infault = pyxb.binding.content.ElementUse(pyxb.namespace.ExpandedName(Namespace, u'infault'), 'infault', '__httpwww_w3_orgnswsdl_InterfaceOperationType_httpwww_w3_orgnswsdlinfault', True)
    __infault._DeclarationLocation = pyxb.utils.utility.Location('/tmp/pyxbdist.RHB65sy/PyXB-1.1.5/pyxb/bundles/wssplat/schemas/wsdl20.xsd', 181, 10)
    __infault._UseLocation = None

    
    infault = property(__infault.value, __infault.set, None, None)

    
    # Element {http://www.w3.org/ns/wsdl}output uses Python identifier output
    __output = pyxb.binding.content.ElementUse(pyxb.namespace.ExpandedName(Namespace, u'output'), 'output', '__httpwww_w3_orgnswsdl_InterfaceOperationType_httpwww_w3_orgnswsdloutput', True)
    __output._DeclarationLocation = pyxb.utils.utility.Location('/tmp/pyxbdist.RHB65sy/PyXB-1.1.5/pyxb/bundles/wssplat/schemas/wsdl20.xsd', 180, 10)
    __output._UseLocation = None

    
    output = property(__output.value, __output.set, None, None)

    
    # Attribute name uses Python identifier name
    __name = pyxb.binding.content.AttributeUse(pyxb.namespace.ExpandedName(None, u'name'), 'name', '__httpwww_w3_orgnswsdl_InterfaceOperationType_name', pyxb.binding.datatypes.NCName, required=True)
    __name._DeclarationLocation = pyxb.utils.utility.Location('/tmp/pyxbdist.RHB65sy/PyXB-1.1.5/pyxb/bundles/wssplat/schemas/wsdl20.xsd', 185, 8)
    __name._UseLocation = pyxb.utils.utility.Location('/tmp/pyxbdist.RHB65sy/PyXB-1.1.5/pyxb/bundles/wssplat/schemas/wsdl20.xsd', 185, 8)
    
    name = property(__name.value, __name.set, None, None)

    
    # Attribute pattern uses Python identifier pattern
    __pattern = pyxb.binding.content.AttributeUse(pyxb.namespace.ExpandedName(None, u'pattern'), 'pattern', '__httpwww_w3_orgnswsdl_InterfaceOperationType_pattern', pyxb.binding.datatypes.anyURI)
    __pattern._DeclarationLocation = pyxb.utils.utility.Location('/tmp/pyxbdist.RHB65sy/PyXB-1.1.5/pyxb/bundles/wssplat/schemas/wsdl20.xsd', 186, 8)
    __pattern._UseLocation = pyxb.utils.utility.Location('/tmp/pyxbdist.RHB65sy/PyXB-1.1.5/pyxb/bundles/wssplat/schemas/wsdl20.xsd', 186, 8)
    
    pattern = property(__pattern.value, __pattern.set, None, None)

    
    # Attribute safe uses Python identifier safe
    __safe = pyxb.binding.content.AttributeUse(pyxb.namespace.ExpandedName(None, u'safe'), 'safe', '__httpwww_w3_orgnswsdl_InterfaceOperationType_safe', pyxb.binding.datatypes.boolean)
    __safe._DeclarationLocation = pyxb.utils.utility.Location('/tmp/pyxbdist.RHB65sy/PyXB-1.1.5/pyxb/bundles/wssplat/schemas/wsdl20.xsd', 187, 8)
    __safe._UseLocation = pyxb.utils.utility.Location('/tmp/pyxbdist.RHB65sy/PyXB-1.1.5/pyxb/bundles/wssplat/schemas/wsdl20.xsd', 187, 8)
    
    safe = property(__safe.value, __safe.set, None, None)

    
    # Attribute style uses Python identifier style
    __style = pyxb.binding.content.AttributeUse(pyxb.namespace.ExpandedName(None, u'style'), 'style', '__httpwww_w3_orgnswsdl_InterfaceOperationType_style', pyxb.binding.datatypes.anyURI)
    __style._DeclarationLocation = pyxb.utils.utility.Location('/tmp/pyxbdist.RHB65sy/PyXB-1.1.5/pyxb/bundles/wssplat/schemas/wsdl20.xsd', 188, 8)
    __style._UseLocation = pyxb.utils.utility.Location('/tmp/pyxbdist.RHB65sy/PyXB-1.1.5/pyxb/bundles/wssplat/schemas/wsdl20.xsd', 188, 8)
    
    style = property(__style.value, __style.set, None, None)

    _AttributeWildcard = pyxb.binding.content.Wildcard(process_contents=pyxb.binding.content.Wildcard.PC_lax, namespace_constraint=(pyxb.binding.content.Wildcard.NC_not, u'http://www.w3.org/ns/wsdl'))
    _HasWildcardElement = True

    _ElementMap = ExtensibleDocumentedType._ElementMap.copy()
    _ElementMap.update({
        __outfault.name() : __outfault,
        __input.name() : __input,
        __infault.name() : __infault,
        __output.name() : __output
    })
    _AttributeMap = ExtensibleDocumentedType._AttributeMap.copy()
    _AttributeMap.update({
        __name.name() : __name,
        __pattern.name() : __pattern,
        __safe.name() : __safe,
        __style.name() : __style
    })
Namespace.addCategoryObject('typeBinding', u'InterfaceOperationType', InterfaceOperationType)


# Complex type {http://www.w3.org/ns/wsdl}ServiceType with content type ELEMENT_ONLY
class ServiceType (ExtensibleDocumentedType):
    _TypeDefinition = None
    _ContentTypeTag = pyxb.binding.basis.complexTypeDefinition._CT_ELEMENT_ONLY
    _Abstract = False
    _ExpandedName = pyxb.namespace.ExpandedName(Namespace, u'ServiceType')
    _DefinitionLocation = pyxb.utils.utility.Location('/tmp/pyxbdist.RHB65sy/PyXB-1.1.5/pyxb/bundles/wssplat/schemas/wsdl20.xsd', 322, 2)
    # Base type is ExtensibleDocumentedType
    
    # Element {http://www.w3.org/ns/wsdl}endpoint uses Python identifier endpoint
    __endpoint = pyxb.binding.content.ElementUse(pyxb.namespace.ExpandedName(Namespace, u'endpoint'), 'endpoint', '__httpwww_w3_orgnswsdl_ServiceType_httpwww_w3_orgnswsdlendpoint', True)
    __endpoint._DeclarationLocation = pyxb.utils.utility.Location('/tmp/pyxbdist.RHB65sy/PyXB-1.1.5/pyxb/bundles/wssplat/schemas/wsdl20.xsd', 335, 2)
    __endpoint._UseLocation = None

    
    endpoint = property(__endpoint.value, __endpoint.set, None, None)

    
    # Element documentation ({http://www.w3.org/ns/wsdl}documentation) inherited from {http://www.w3.org/ns/wsdl}DocumentedType
    
    # Attribute interface uses Python identifier interface
    __interface = pyxb.binding.content.AttributeUse(pyxb.namespace.ExpandedName(None, u'interface'), 'interface', '__httpwww_w3_orgnswsdl_ServiceType_interface', pyxb.binding.datatypes.QName, required=True)
    __interface._DeclarationLocation = pyxb.utils.utility.Location('/tmp/pyxbdist.RHB65sy/PyXB-1.1.5/pyxb/bundles/wssplat/schemas/wsdl20.xsd', 330, 8)
    __interface._UseLocation = pyxb.utils.utility.Location('/tmp/pyxbdist.RHB65sy/PyXB-1.1.5/pyxb/bundles/wssplat/schemas/wsdl20.xsd', 330, 8)
    
    interface = property(__interface.value, __interface.set, None, None)

    
    # Attribute name uses Python identifier name
    __name = pyxb.binding.content.AttributeUse(pyxb.namespace.ExpandedName(None, u'name'), 'name', '__httpwww_w3_orgnswsdl_ServiceType_name', pyxb.binding.datatypes.NCName, required=True)
    __name._DeclarationLocation = pyxb.utils.utility.Location('/tmp/pyxbdist.RHB65sy/PyXB-1.1.5/pyxb/bundles/wssplat/schemas/wsdl20.xsd', 329, 8)
    __name._UseLocation = pyxb.utils.utility.Location('/tmp/pyxbdist.RHB65sy/PyXB-1.1.5/pyxb/bundles/wssplat/schemas/wsdl20.xsd', 329, 8)
    
    name = property(__name.value, __name.set, None, None)

    _AttributeWildcard = pyxb.binding.content.Wildcard(process_contents=pyxb.binding.content.Wildcard.PC_lax, namespace_constraint=(pyxb.binding.content.Wildcard.NC_not, u'http://www.w3.org/ns/wsdl'))
    _HasWildcardElement = True

    _ElementMap = ExtensibleDocumentedType._ElementMap.copy()
    _ElementMap.update({
        __endpoint.name() : __endpoint
    })
    _AttributeMap = ExtensibleDocumentedType._AttributeMap.copy()
    _AttributeMap.update({
        __interface.name() : __interface,
        __name.name() : __name
    })
Namespace.addCategoryObject('typeBinding', u'ServiceType', ServiceType)


# Complex type {http://www.w3.org/ns/wsdl}ImportType with content type ELEMENT_ONLY
class ImportType (ExtensibleDocumentedType):
    _TypeDefinition = None
    _ContentTypeTag = pyxb.binding.basis.complexTypeDefinition._CT_ELEMENT_ONLY
    _Abstract = False
    _ExpandedName = pyxb.namespace.ExpandedName(Namespace, u'ImportType')
    _DefinitionLocation = pyxb.utils.utility.Location('/tmp/pyxbdist.RHB65sy/PyXB-1.1.5/pyxb/bundles/wssplat/schemas/wsdl20.xsd', 106, 2)
    # Base type is ExtensibleDocumentedType
    
    # Element documentation ({http://www.w3.org/ns/wsdl}documentation) inherited from {http://www.w3.org/ns/wsdl}DocumentedType
    
    # Attribute namespace uses Python identifier namespace
    __namespace = pyxb.binding.content.AttributeUse(pyxb.namespace.ExpandedName(None, u'namespace'), 'namespace', '__httpwww_w3_orgnswsdl_ImportType_namespace', pyxb.binding.datatypes.anyURI, required=True)
    __namespace._DeclarationLocation = pyxb.utils.utility.Location('/tmp/pyxbdist.RHB65sy/PyXB-1.1.5/pyxb/bundles/wssplat/schemas/wsdl20.xsd', 112, 8)
    __namespace._UseLocation = pyxb.utils.utility.Location('/tmp/pyxbdist.RHB65sy/PyXB-1.1.5/pyxb/bundles/wssplat/schemas/wsdl20.xsd', 112, 8)
    
    namespace = property(__namespace.value, __namespace.set, None, None)

    
    # Attribute location uses Python identifier location
    __location = pyxb.binding.content.AttributeUse(pyxb.namespace.ExpandedName(None, u'location'), 'location', '__httpwww_w3_orgnswsdl_ImportType_location', pyxb.binding.datatypes.anyURI)
    __location._DeclarationLocation = pyxb.utils.utility.Location('/tmp/pyxbdist.RHB65sy/PyXB-1.1.5/pyxb/bundles/wssplat/schemas/wsdl20.xsd', 113, 8)
    __location._UseLocation = pyxb.utils.utility.Location('/tmp/pyxbdist.RHB65sy/PyXB-1.1.5/pyxb/bundles/wssplat/schemas/wsdl20.xsd', 113, 8)
    
    location = property(__location.value, __location.set, None, None)

    _AttributeWildcard = pyxb.binding.content.Wildcard(process_contents=pyxb.binding.content.Wildcard.PC_lax, namespace_constraint=(pyxb.binding.content.Wildcard.NC_not, u'http://www.w3.org/ns/wsdl'))
    _HasWildcardElement = True

    _ElementMap = ExtensibleDocumentedType._ElementMap.copy()
    _ElementMap.update({
        
    })
    _AttributeMap = ExtensibleDocumentedType._AttributeMap.copy()
    _AttributeMap.update({
        __namespace.name() : __namespace,
        __location.name() : __location
    })
Namespace.addCategoryObject('typeBinding', u'ImportType', ImportType)


# Complex type {http://www.w3.org/ns/wsdl}IncludeType with content type ELEMENT_ONLY
class IncludeType (ExtensibleDocumentedType):
    _TypeDefinition = None
    _ContentTypeTag = pyxb.binding.basis.complexTypeDefinition._CT_ELEMENT_ONLY
    _Abstract = False
    _ExpandedName = pyxb.namespace.ExpandedName(Namespace, u'IncludeType')
    _DefinitionLocation = pyxb.utils.utility.Location('/tmp/pyxbdist.RHB65sy/PyXB-1.1.5/pyxb/bundles/wssplat/schemas/wsdl20.xsd', 119, 2)
    # Base type is ExtensibleDocumentedType
    
    # Element documentation ({http://www.w3.org/ns/wsdl}documentation) inherited from {http://www.w3.org/ns/wsdl}DocumentedType
    
    # Attribute location uses Python identifier location
    __location = pyxb.binding.content.AttributeUse(pyxb.namespace.ExpandedName(None, u'location'), 'location', '__httpwww_w3_orgnswsdl_IncludeType_location', pyxb.binding.datatypes.anyURI, required=True)
    __location._DeclarationLocation = pyxb.utils.utility.Location('/tmp/pyxbdist.RHB65sy/PyXB-1.1.5/pyxb/bundles/wssplat/schemas/wsdl20.xsd', 125, 8)
    __location._UseLocation = pyxb.utils.utility.Location('/tmp/pyxbdist.RHB65sy/PyXB-1.1.5/pyxb/bundles/wssplat/schemas/wsdl20.xsd', 125, 8)
    
    location = property(__location.value, __location.set, None, None)

    _AttributeWildcard = pyxb.binding.content.Wildcard(process_contents=pyxb.binding.content.Wildcard.PC_lax, namespace_constraint=(pyxb.binding.content.Wildcard.NC_not, u'http://www.w3.org/ns/wsdl'))
    _HasWildcardElement = True

    _ElementMap = ExtensibleDocumentedType._ElementMap.copy()
    _ElementMap.update({
        
    })
    _AttributeMap = ExtensibleDocumentedType._AttributeMap.copy()
    _AttributeMap.update({
        __location.name() : __location
    })
Namespace.addCategoryObject('typeBinding', u'IncludeType', IncludeType)


# Complex type {http://www.w3.org/ns/wsdl}DocumentationType with content type MIXED
class DocumentationType (pyxb.binding.basis.complexTypeDefinition):
    _TypeDefinition = None
    _ContentTypeTag = pyxb.binding.basis.complexTypeDefinition._CT_MIXED
    _Abstract = False
    _ExpandedName = pyxb.namespace.ExpandedName(Namespace, u'DocumentationType')
    _DefinitionLocation = pyxb.utils.utility.Location('/tmp/pyxbdist.RHB65sy/PyXB-1.1.5/pyxb/bundles/wssplat/schemas/wsdl20.xsd', 23, 2)
    # Base type is pyxb.binding.datatypes.anyType
    _AttributeWildcard = pyxb.binding.content.Wildcard(process_contents=pyxb.binding.content.Wildcard.PC_lax, namespace_constraint=(pyxb.binding.content.Wildcard.NC_not, u'http://www.w3.org/ns/wsdl'))
    _HasWildcardElement = True

    _ElementMap = {
        
    }
    _AttributeMap = {
        
    }
Namespace.addCategoryObject('typeBinding', u'DocumentationType', DocumentationType)


# Complex type {http://www.w3.org/ns/wsdl}BindingOperationType with content type ELEMENT_ONLY
class BindingOperationType (ExtensibleDocumentedType):
    _TypeDefinition = None
    _ContentTypeTag = pyxb.binding.basis.complexTypeDefinition._CT_ELEMENT_ONLY
    _Abstract = False
    _ExpandedName = pyxb.namespace.ExpandedName(Namespace, u'BindingOperationType')
    _DefinitionLocation = pyxb.utils.utility.Location('/tmp/pyxbdist.RHB65sy/PyXB-1.1.5/pyxb/bundles/wssplat/schemas/wsdl20.xsd', 266, 2)
    # Base type is ExtensibleDocumentedType
    
    # Element {http://www.w3.org/ns/wsdl}outfault uses Python identifier outfault
    __outfault = pyxb.binding.content.ElementUse(pyxb.namespace.ExpandedName(Namespace, u'outfault'), 'outfault', '__httpwww_w3_orgnswsdl_BindingOperationType_httpwww_w3_orgnswsdloutfault', True)
    __outfault._DeclarationLocation = pyxb.utils.utility.Location('/tmp/pyxbdist.RHB65sy/PyXB-1.1.5/pyxb/bundles/wssplat/schemas/wsdl20.xsd', 273, 10)
    __outfault._UseLocation = None

    
    outfault = property(__outfault.value, __outfault.set, None, None)

    
    # Element {http://www.w3.org/ns/wsdl}input uses Python identifier input
    __input = pyxb.binding.content.ElementUse(pyxb.namespace.ExpandedName(Namespace, u'input'), 'input', '__httpwww_w3_orgnswsdl_BindingOperationType_httpwww_w3_orgnswsdlinput', True)
    __input._DeclarationLocation = pyxb.utils.utility.Location('/tmp/pyxbdist.RHB65sy/PyXB-1.1.5/pyxb/bundles/wssplat/schemas/wsdl20.xsd', 270, 10)
    __input._UseLocation = None

    
    input = property(__input.value, __input.set, None, None)

    
    # Element documentation ({http://www.w3.org/ns/wsdl}documentation) inherited from {http://www.w3.org/ns/wsdl}DocumentedType
    
    # Element {http://www.w3.org/ns/wsdl}output uses Python identifier output
    __output = pyxb.binding.content.ElementUse(pyxb.namespace.ExpandedName(Namespace, u'output'), 'output', '__httpwww_w3_orgnswsdl_BindingOperationType_httpwww_w3_orgnswsdloutput', True)
    __output._DeclarationLocation = pyxb.utils.utility.Location('/tmp/pyxbdist.RHB65sy/PyXB-1.1.5/pyxb/bundles/wssplat/schemas/wsdl20.xsd', 271, 10)
    __output._UseLocation = None

    
    output = property(__output.value, __output.set, None, None)

    
    # Element {http://www.w3.org/ns/wsdl}infault uses Python identifier infault
    __infault = pyxb.binding.content.ElementUse(pyxb.namespace.ExpandedName(Namespace, u'infault'), 'infault', '__httpwww_w3_orgnswsdl_BindingOperationType_httpwww_w3_orgnswsdlinfault', True)
    __infault._DeclarationLocation = pyxb.utils.utility.Location('/tmp/pyxbdist.RHB65sy/PyXB-1.1.5/pyxb/bundles/wssplat/schemas/wsdl20.xsd', 272, 10)
    __infault._UseLocation = None

    
    infault = property(__infault.value, __infault.set, None, None)

    
    # Attribute ref uses Python identifier ref
    __ref = pyxb.binding.content.AttributeUse(pyxb.namespace.ExpandedName(None, u'ref'), 'ref', '__httpwww_w3_orgnswsdl_BindingOperationType_ref', pyxb.binding.datatypes.QName, required=True)
    __ref._DeclarationLocation = pyxb.utils.utility.Location('/tmp/pyxbdist.RHB65sy/PyXB-1.1.5/pyxb/bundles/wssplat/schemas/wsdl20.xsd', 276, 8)
    __ref._UseLocation = pyxb.utils.utility.Location('/tmp/pyxbdist.RHB65sy/PyXB-1.1.5/pyxb/bundles/wssplat/schemas/wsdl20.xsd', 276, 8)
    
    ref = property(__ref.value, __ref.set, None, None)

    _AttributeWildcard = pyxb.binding.content.Wildcard(process_contents=pyxb.binding.content.Wildcard.PC_lax, namespace_constraint=(pyxb.binding.content.Wildcard.NC_not, u'http://www.w3.org/ns/wsdl'))
    _HasWildcardElement = True

    _ElementMap = ExtensibleDocumentedType._ElementMap.copy()
    _ElementMap.update({
        __outfault.name() : __outfault,
        __input.name() : __input,
        __output.name() : __output,
        __infault.name() : __infault
    })
    _AttributeMap = ExtensibleDocumentedType._AttributeMap.copy()
    _AttributeMap.update({
        __ref.name() : __ref
    })
Namespace.addCategoryObject('typeBinding', u'BindingOperationType', BindingOperationType)


# Complex type {http://www.w3.org/ns/wsdl}DescriptionType with content type ELEMENT_ONLY
class DescriptionType (ExtensibleDocumentedType):
    _TypeDefinition = None
    _ContentTypeTag = pyxb.binding.basis.complexTypeDefinition._CT_ELEMENT_ONLY
    _Abstract = False
    _ExpandedName = pyxb.namespace.ExpandedName(Namespace, u'DescriptionType')
    _DefinitionLocation = pyxb.utils.utility.Location('/tmp/pyxbdist.RHB65sy/PyXB-1.1.5/pyxb/bundles/wssplat/schemas/wsdl20.xsd', 71, 2)
    # Base type is ExtensibleDocumentedType
    
    # Element {http://www.w3.org/ns/wsdl}include uses Python identifier include
    __include = pyxb.binding.content.ElementUse(pyxb.namespace.ExpandedName(Namespace, u'include'), 'include', '__httpwww_w3_orgnswsdl_DescriptionType_httpwww_w3_orgnswsdlinclude', True)
    __include._DeclarationLocation = pyxb.utils.utility.Location('/tmp/pyxbdist.RHB65sy/PyXB-1.1.5/pyxb/bundles/wssplat/schemas/wsdl20.xsd', 118, 2)
    __include._UseLocation = None

    
    include = property(__include.value, __include.set, None, None)

    
    # Element {http://www.w3.org/ns/wsdl}binding uses Python identifier binding
    __binding = pyxb.binding.content.ElementUse(pyxb.namespace.ExpandedName(Namespace, u'binding'), 'binding', '__httpwww_w3_orgnswsdl_DescriptionType_httpwww_w3_orgnswsdlbinding', True)
    __binding._DeclarationLocation = pyxb.utils.utility.Location('/tmp/pyxbdist.RHB65sy/PyXB-1.1.5/pyxb/bundles/wssplat/schemas/wsdl20.xsd', 250, 2)
    __binding._UseLocation = None

    
    binding = property(__binding.value, __binding.set, None, None)

    
    # Element {http://www.w3.org/ns/wsdl}types uses Python identifier types
    __types = pyxb.binding.content.ElementUse(pyxb.namespace.ExpandedName(Namespace, u'types'), 'types', '__httpwww_w3_orgnswsdl_DescriptionType_httpwww_w3_orgnswsdltypes', True)
    __types._DeclarationLocation = pyxb.utils.utility.Location('/tmp/pyxbdist.RHB65sy/PyXB-1.1.5/pyxb/bundles/wssplat/schemas/wsdl20.xsd', 130, 2)
    __types._UseLocation = None

    
    types = property(__types.value, __types.set, None, None)

    
    # Element {http://www.w3.org/ns/wsdl}service uses Python identifier service
    __service = pyxb.binding.content.ElementUse(pyxb.namespace.ExpandedName(Namespace, u'service'), 'service', '__httpwww_w3_orgnswsdl_DescriptionType_httpwww_w3_orgnswsdlservice', True)
    __service._DeclarationLocation = pyxb.utils.utility.Location('/tmp/pyxbdist.RHB65sy/PyXB-1.1.5/pyxb/bundles/wssplat/schemas/wsdl20.xsd', 316, 2)
    __service._UseLocation = None

    
    service = property(__service.value, __service.set, None, None)

    
    # Element documentation ({http://www.w3.org/ns/wsdl}documentation) inherited from {http://www.w3.org/ns/wsdl}DocumentedType
    
    # Element {http://www.w3.org/ns/wsdl}interface uses Python identifier interface
    __interface = pyxb.binding.content.ElementUse(pyxb.namespace.ExpandedName(Namespace, u'interface'), 'interface', '__httpwww_w3_orgnswsdl_DescriptionType_httpwww_w3_orgnswsdlinterface', True)
    __interface._DeclarationLocation = pyxb.utils.utility.Location('/tmp/pyxbdist.RHB65sy/PyXB-1.1.5/pyxb/bundles/wssplat/schemas/wsdl20.xsd', 142, 2)
    __interface._UseLocation = None

    
    interface = property(__interface.value, __interface.set, None, None)

    
    # Element {http://www.w3.org/ns/wsdl}import uses Python identifier import_
    __import = pyxb.binding.content.ElementUse(pyxb.namespace.ExpandedName(Namespace, u'import'), 'import_', '__httpwww_w3_orgnswsdl_DescriptionType_httpwww_w3_orgnswsdlimport', True)
    __import._DeclarationLocation = pyxb.utils.utility.Location('/tmp/pyxbdist.RHB65sy/PyXB-1.1.5/pyxb/bundles/wssplat/schemas/wsdl20.xsd', 105, 2)
    __import._UseLocation = None

    
    import_ = property(__import.value, __import.set, None, None)

    
    # Attribute targetNamespace uses Python identifier targetNamespace
    __targetNamespace = pyxb.binding.content.AttributeUse(pyxb.namespace.ExpandedName(None, u'targetNamespace'), 'targetNamespace', '__httpwww_w3_orgnswsdl_DescriptionType_targetNamespace', pyxb.binding.datatypes.anyURI, required=True)
    __targetNamespace._DeclarationLocation = pyxb.utils.utility.Location('/tmp/pyxbdist.RHB65sy/PyXB-1.1.5/pyxb/bundles/wssplat/schemas/wsdl20.xsd', 99, 1)
    __targetNamespace._UseLocation = pyxb.utils.utility.Location('/tmp/pyxbdist.RHB65sy/PyXB-1.1.5/pyxb/bundles/wssplat/schemas/wsdl20.xsd', 99, 1)
    
    targetNamespace = property(__targetNamespace.value, __targetNamespace.set, None, None)

    _AttributeWildcard = pyxb.binding.content.Wildcard(process_contents=pyxb.binding.content.Wildcard.PC_lax, namespace_constraint=(pyxb.binding.content.Wildcard.NC_not, u'http://www.w3.org/ns/wsdl'))
    _HasWildcardElement = True

    _ElementMap = ExtensibleDocumentedType._ElementMap.copy()
    _ElementMap.update({
        __include.name() : __include,
        __binding.name() : __binding,
        __types.name() : __types,
        __service.name() : __service,
        __interface.name() : __interface,
        __import.name() : __import
    })
    _AttributeMap = ExtensibleDocumentedType._AttributeMap.copy()
    _AttributeMap.update({
        __targetNamespace.name() : __targetNamespace
    })
Namespace.addCategoryObject('typeBinding', u'DescriptionType', DescriptionType)


# Complex type {http://www.w3.org/ns/wsdl}TypesType with content type ELEMENT_ONLY
class TypesType (ExtensibleDocumentedType):
    _TypeDefinition = None
    _ContentTypeTag = pyxb.binding.basis.complexTypeDefinition._CT_ELEMENT_ONLY
    _Abstract = False
    _ExpandedName = pyxb.namespace.ExpandedName(Namespace, u'TypesType')
    _DefinitionLocation = pyxb.utils.utility.Location('/tmp/pyxbdist.RHB65sy/PyXB-1.1.5/pyxb/bundles/wssplat/schemas/wsdl20.xsd', 131, 2)
    # Base type is ExtensibleDocumentedType
    
    # Element documentation ({http://www.w3.org/ns/wsdl}documentation) inherited from {http://www.w3.org/ns/wsdl}DocumentedType
    _AttributeWildcard = pyxb.binding.content.Wildcard(process_contents=pyxb.binding.content.Wildcard.PC_lax, namespace_constraint=(pyxb.binding.content.Wildcard.NC_not, u'http://www.w3.org/ns/wsdl'))
    _HasWildcardElement = True

    _ElementMap = ExtensibleDocumentedType._ElementMap.copy()
    _ElementMap.update({
        
    })
    _AttributeMap = ExtensibleDocumentedType._AttributeMap.copy()
    _AttributeMap.update({
        
    })
Namespace.addCategoryObject('typeBinding', u'TypesType', TypesType)


# Complex type {http://www.w3.org/ns/wsdl}BindingType with content type ELEMENT_ONLY
class BindingType (ExtensibleDocumentedType):
    _TypeDefinition = None
    _ContentTypeTag = pyxb.binding.basis.complexTypeDefinition._CT_ELEMENT_ONLY
    _Abstract = False
    _ExpandedName = pyxb.namespace.ExpandedName(Namespace, u'BindingType')
    _DefinitionLocation = pyxb.utils.utility.Location('/tmp/pyxbdist.RHB65sy/PyXB-1.1.5/pyxb/bundles/wssplat/schemas/wsdl20.xsd', 251, 2)
    # Base type is ExtensibleDocumentedType
    
    # Element documentation ({http://www.w3.org/ns/wsdl}documentation) inherited from {http://www.w3.org/ns/wsdl}DocumentedType
    
    # Element {http://www.w3.org/ns/wsdl}fault uses Python identifier fault
    __fault = pyxb.binding.content.ElementUse(pyxb.namespace.ExpandedName(Namespace, u'fault'), 'fault', '__httpwww_w3_orgnswsdl_BindingType_httpwww_w3_orgnswsdlfault', True)
    __fault._DeclarationLocation = pyxb.utils.utility.Location('/tmp/pyxbdist.RHB65sy/PyXB-1.1.5/pyxb/bundles/wssplat/schemas/wsdl20.xsd', 256, 10)
    __fault._UseLocation = None

    
    fault = property(__fault.value, __fault.set, None, None)

    
    # Element {http://www.w3.org/ns/wsdl}operation uses Python identifier operation
    __operation = pyxb.binding.content.ElementUse(pyxb.namespace.ExpandedName(Namespace, u'operation'), 'operation', '__httpwww_w3_orgnswsdl_BindingType_httpwww_w3_orgnswsdloperation', True)
    __operation._DeclarationLocation = pyxb.utils.utility.Location('/tmp/pyxbdist.RHB65sy/PyXB-1.1.5/pyxb/bundles/wssplat/schemas/wsdl20.xsd', 255, 10)
    __operation._UseLocation = None

    
    operation = property(__operation.value, __operation.set, None, None)

    
    # Attribute name uses Python identifier name
    __name = pyxb.binding.content.AttributeUse(pyxb.namespace.ExpandedName(None, u'name'), 'name', '__httpwww_w3_orgnswsdl_BindingType_name', pyxb.binding.datatypes.NCName, required=True)
    __name._DeclarationLocation = pyxb.utils.utility.Location('/tmp/pyxbdist.RHB65sy/PyXB-1.1.5/pyxb/bundles/wssplat/schemas/wsdl20.xsd', 259, 8)
    __name._UseLocation = pyxb.utils.utility.Location('/tmp/pyxbdist.RHB65sy/PyXB-1.1.5/pyxb/bundles/wssplat/schemas/wsdl20.xsd', 259, 8)
    
    name = property(__name.value, __name.set, None, None)

    
    # Attribute interface uses Python identifier interface
    __interface = pyxb.binding.content.AttributeUse(pyxb.namespace.ExpandedName(None, u'interface'), 'interface', '__httpwww_w3_orgnswsdl_BindingType_interface', pyxb.binding.datatypes.QName)
    __interface._DeclarationLocation = pyxb.utils.utility.Location('/tmp/pyxbdist.RHB65sy/PyXB-1.1.5/pyxb/bundles/wssplat/schemas/wsdl20.xsd', 261, 8)
    __interface._UseLocation = pyxb.utils.utility.Location('/tmp/pyxbdist.RHB65sy/PyXB-1.1.5/pyxb/bundles/wssplat/schemas/wsdl20.xsd', 261, 8)
    
    interface = property(__interface.value, __interface.set, None, None)

    
    # Attribute type uses Python identifier type
    __type = pyxb.binding.content.AttributeUse(pyxb.namespace.ExpandedName(None, u'type'), 'type', '__httpwww_w3_orgnswsdl_BindingType_type', pyxb.binding.datatypes.anyURI, required=True)
    __type._DeclarationLocation = pyxb.utils.utility.Location('/tmp/pyxbdist.RHB65sy/PyXB-1.1.5/pyxb/bundles/wssplat/schemas/wsdl20.xsd', 260, 8)
    __type._UseLocation = pyxb.utils.utility.Location('/tmp/pyxbdist.RHB65sy/PyXB-1.1.5/pyxb/bundles/wssplat/schemas/wsdl20.xsd', 260, 8)
    
    type = property(__type.value, __type.set, None, None)

    _AttributeWildcard = pyxb.binding.content.Wildcard(process_contents=pyxb.binding.content.Wildcard.PC_lax, namespace_constraint=(pyxb.binding.content.Wildcard.NC_not, u'http://www.w3.org/ns/wsdl'))
    _HasWildcardElement = True

    _ElementMap = ExtensibleDocumentedType._ElementMap.copy()
    _ElementMap.update({
        __fault.name() : __fault,
        __operation.name() : __operation
    })
    _AttributeMap = ExtensibleDocumentedType._AttributeMap.copy()
    _AttributeMap.update({
        __name.name() : __name,
        __interface.name() : __interface,
        __type.name() : __type
    })
Namespace.addCategoryObject('typeBinding', u'BindingType', BindingType)


# Complex type {http://www.w3.org/ns/wsdl}InterfaceFaultType with content type ELEMENT_ONLY
class InterfaceFaultType (ExtensibleDocumentedType):
    _TypeDefinition = None
    _ContentTypeTag = pyxb.binding.basis.complexTypeDefinition._CT_ELEMENT_ONLY
    _Abstract = False
    _ExpandedName = pyxb.namespace.ExpandedName(Namespace, u'InterfaceFaultType')
    _DefinitionLocation = pyxb.utils.utility.Location('/tmp/pyxbdist.RHB65sy/PyXB-1.1.5/pyxb/bundles/wssplat/schemas/wsdl20.xsd', 237, 2)
    # Base type is ExtensibleDocumentedType
    
    # Element documentation ({http://www.w3.org/ns/wsdl}documentation) inherited from {http://www.w3.org/ns/wsdl}DocumentedType
    
    # Attribute name uses Python identifier name
    __name = pyxb.binding.content.AttributeUse(pyxb.namespace.ExpandedName(None, u'name'), 'name', '__httpwww_w3_orgnswsdl_InterfaceFaultType_name', pyxb.binding.datatypes.NCName, required=True)
    __name._DeclarationLocation = pyxb.utils.utility.Location('/tmp/pyxbdist.RHB65sy/PyXB-1.1.5/pyxb/bundles/wssplat/schemas/wsdl20.xsd', 243, 8)
    __name._UseLocation = pyxb.utils.utility.Location('/tmp/pyxbdist.RHB65sy/PyXB-1.1.5/pyxb/bundles/wssplat/schemas/wsdl20.xsd', 243, 8)
    
    name = property(__name.value, __name.set, None, None)

    
    # Attribute element uses Python identifier element
    __element = pyxb.binding.content.AttributeUse(pyxb.namespace.ExpandedName(None, u'element'), 'element', '__httpwww_w3_orgnswsdl_InterfaceFaultType_element', ElementReferenceType)
    __element._DeclarationLocation = pyxb.utils.utility.Location('/tmp/pyxbdist.RHB65sy/PyXB-1.1.5/pyxb/bundles/wssplat/schemas/wsdl20.xsd', 244, 8)
    __element._UseLocation = pyxb.utils.utility.Location('/tmp/pyxbdist.RHB65sy/PyXB-1.1.5/pyxb/bundles/wssplat/schemas/wsdl20.xsd', 244, 8)
    
    element = property(__element.value, __element.set, None, None)

    _AttributeWildcard = pyxb.binding.content.Wildcard(process_contents=pyxb.binding.content.Wildcard.PC_lax, namespace_constraint=(pyxb.binding.content.Wildcard.NC_not, u'http://www.w3.org/ns/wsdl'))
    _HasWildcardElement = True

    _ElementMap = ExtensibleDocumentedType._ElementMap.copy()
    _ElementMap.update({
        
    })
    _AttributeMap = ExtensibleDocumentedType._AttributeMap.copy()
    _AttributeMap.update({
        __name.name() : __name,
        __element.name() : __element
    })
Namespace.addCategoryObject('typeBinding', u'InterfaceFaultType', InterfaceFaultType)


# Complex type {http://www.w3.org/ns/wsdl}BindingOperationMessageType with content type ELEMENT_ONLY
class BindingOperationMessageType (ExtensibleDocumentedType):
    _TypeDefinition = None
    _ContentTypeTag = pyxb.binding.basis.complexTypeDefinition._CT_ELEMENT_ONLY
    _Abstract = False
    _ExpandedName = pyxb.namespace.ExpandedName(Namespace, u'BindingOperationMessageType')
    _DefinitionLocation = pyxb.utils.utility.Location('/tmp/pyxbdist.RHB65sy/PyXB-1.1.5/pyxb/bundles/wssplat/schemas/wsdl20.xsd', 281, 2)
    # Base type is ExtensibleDocumentedType
    
    # Element documentation ({http://www.w3.org/ns/wsdl}documentation) inherited from {http://www.w3.org/ns/wsdl}DocumentedType
    
    # Attribute messageLabel uses Python identifier messageLabel
    __messageLabel = pyxb.binding.content.AttributeUse(pyxb.namespace.ExpandedName(None, u'messageLabel'), 'messageLabel', '__httpwww_w3_orgnswsdl_BindingOperationMessageType_messageLabel', pyxb.binding.datatypes.NCName)
    __messageLabel._DeclarationLocation = pyxb.utils.utility.Location('/tmp/pyxbdist.RHB65sy/PyXB-1.1.5/pyxb/bundles/wssplat/schemas/wsdl20.xsd', 287, 8)
    __messageLabel._UseLocation = pyxb.utils.utility.Location('/tmp/pyxbdist.RHB65sy/PyXB-1.1.5/pyxb/bundles/wssplat/schemas/wsdl20.xsd', 287, 8)
    
    messageLabel = property(__messageLabel.value, __messageLabel.set, None, None)

    _AttributeWildcard = pyxb.binding.content.Wildcard(process_contents=pyxb.binding.content.Wildcard.PC_lax, namespace_constraint=(pyxb.binding.content.Wildcard.NC_not, u'http://www.w3.org/ns/wsdl'))
    _HasWildcardElement = True

    _ElementMap = ExtensibleDocumentedType._ElementMap.copy()
    _ElementMap.update({
        
    })
    _AttributeMap = ExtensibleDocumentedType._AttributeMap.copy()
    _AttributeMap.update({
        __messageLabel.name() : __messageLabel
    })
Namespace.addCategoryObject('typeBinding', u'BindingOperationMessageType', BindingOperationMessageType)


# Complex type {http://www.w3.org/ns/wsdl}InterfaceType with content type ELEMENT_ONLY
class InterfaceType (ExtensibleDocumentedType):
    _TypeDefinition = None
    _ContentTypeTag = pyxb.binding.basis.complexTypeDefinition._CT_ELEMENT_ONLY
    _Abstract = False
    _ExpandedName = pyxb.namespace.ExpandedName(Namespace, u'InterfaceType')
    _DefinitionLocation = pyxb.utils.utility.Location('/tmp/pyxbdist.RHB65sy/PyXB-1.1.5/pyxb/bundles/wssplat/schemas/wsdl20.xsd', 152, 2)
    # Base type is ExtensibleDocumentedType
    
    # Element {http://www.w3.org/ns/wsdl}fault uses Python identifier fault
    __fault = pyxb.binding.content.ElementUse(pyxb.namespace.ExpandedName(Namespace, u'fault'), 'fault', '__httpwww_w3_orgnswsdl_InterfaceType_httpwww_w3_orgnswsdlfault', True)
    __fault._DeclarationLocation = pyxb.utils.utility.Location('/tmp/pyxbdist.RHB65sy/PyXB-1.1.5/pyxb/bundles/wssplat/schemas/wsdl20.xsd', 157, 10)
    __fault._UseLocation = None

    
    fault = property(__fault.value, __fault.set, None, None)

    
    # Element documentation ({http://www.w3.org/ns/wsdl}documentation) inherited from {http://www.w3.org/ns/wsdl}DocumentedType
    
    # Element {http://www.w3.org/ns/wsdl}operation uses Python identifier operation
    __operation = pyxb.binding.content.ElementUse(pyxb.namespace.ExpandedName(Namespace, u'operation'), 'operation', '__httpwww_w3_orgnswsdl_InterfaceType_httpwww_w3_orgnswsdloperation', True)
    __operation._DeclarationLocation = pyxb.utils.utility.Location('/tmp/pyxbdist.RHB65sy/PyXB-1.1.5/pyxb/bundles/wssplat/schemas/wsdl20.xsd', 156, 10)
    __operation._UseLocation = None

    
    operation = property(__operation.value, __operation.set, None, None)

    
    # Attribute styleDefault uses Python identifier styleDefault
    __styleDefault = pyxb.binding.content.AttributeUse(pyxb.namespace.ExpandedName(None, u'styleDefault'), 'styleDefault', '__httpwww_w3_orgnswsdl_InterfaceType_styleDefault', STD_ANON_)
    __styleDefault._DeclarationLocation = pyxb.utils.utility.Location('/tmp/pyxbdist.RHB65sy/PyXB-1.1.5/pyxb/bundles/wssplat/schemas/wsdl20.xsd', 166, 8)
    __styleDefault._UseLocation = pyxb.utils.utility.Location('/tmp/pyxbdist.RHB65sy/PyXB-1.1.5/pyxb/bundles/wssplat/schemas/wsdl20.xsd', 166, 8)
    
    styleDefault = property(__styleDefault.value, __styleDefault.set, None, None)

    
    # Attribute extends uses Python identifier extends
    __extends = pyxb.binding.content.AttributeUse(pyxb.namespace.ExpandedName(None, u'extends'), 'extends', '__httpwww_w3_orgnswsdl_InterfaceType_extends', STD_ANON_2)
    __extends._DeclarationLocation = pyxb.utils.utility.Location('/tmp/pyxbdist.RHB65sy/PyXB-1.1.5/pyxb/bundles/wssplat/schemas/wsdl20.xsd', 161, 8)
    __extends._UseLocation = pyxb.utils.utility.Location('/tmp/pyxbdist.RHB65sy/PyXB-1.1.5/pyxb/bundles/wssplat/schemas/wsdl20.xsd', 161, 8)
    
    extends = property(__extends.value, __extends.set, None, None)

    
    # Attribute name uses Python identifier name
    __name = pyxb.binding.content.AttributeUse(pyxb.namespace.ExpandedName(None, u'name'), 'name', '__httpwww_w3_orgnswsdl_InterfaceType_name', pyxb.binding.datatypes.NCName, required=True)
    __name._DeclarationLocation = pyxb.utils.utility.Location('/tmp/pyxbdist.RHB65sy/PyXB-1.1.5/pyxb/bundles/wssplat/schemas/wsdl20.xsd', 160, 8)
    __name._UseLocation = pyxb.utils.utility.Location('/tmp/pyxbdist.RHB65sy/PyXB-1.1.5/pyxb/bundles/wssplat/schemas/wsdl20.xsd', 160, 8)
    
    name = property(__name.value, __name.set, None, None)

    _AttributeWildcard = pyxb.binding.content.Wildcard(process_contents=pyxb.binding.content.Wildcard.PC_lax, namespace_constraint=(pyxb.binding.content.Wildcard.NC_not, u'http://www.w3.org/ns/wsdl'))
    _HasWildcardElement = True

    _ElementMap = ExtensibleDocumentedType._ElementMap.copy()
    _ElementMap.update({
        __fault.name() : __fault,
        __operation.name() : __operation
    })
    _AttributeMap = ExtensibleDocumentedType._AttributeMap.copy()
    _AttributeMap.update({
        __styleDefault.name() : __styleDefault,
        __extends.name() : __extends,
        __name.name() : __name
    })
Namespace.addCategoryObject('typeBinding', u'InterfaceType', InterfaceType)


# Complex type {http://www.w3.org/ns/wsdl}MessageRefType with content type ELEMENT_ONLY
class MessageRefType (ExtensibleDocumentedType):
    _TypeDefinition = None
    _ContentTypeTag = pyxb.binding.basis.complexTypeDefinition._CT_ELEMENT_ONLY
    _Abstract = False
    _ExpandedName = pyxb.namespace.ExpandedName(Namespace, u'MessageRefType')
    _DefinitionLocation = pyxb.utils.utility.Location('/tmp/pyxbdist.RHB65sy/PyXB-1.1.5/pyxb/bundles/wssplat/schemas/wsdl20.xsd', 193, 2)
    # Base type is ExtensibleDocumentedType
    
    # Element documentation ({http://www.w3.org/ns/wsdl}documentation) inherited from {http://www.w3.org/ns/wsdl}DocumentedType
    
    # Attribute messageLabel uses Python identifier messageLabel
    __messageLabel = pyxb.binding.content.AttributeUse(pyxb.namespace.ExpandedName(None, u'messageLabel'), 'messageLabel', '__httpwww_w3_orgnswsdl_MessageRefType_messageLabel', pyxb.binding.datatypes.NCName)
    __messageLabel._DeclarationLocation = pyxb.utils.utility.Location('/tmp/pyxbdist.RHB65sy/PyXB-1.1.5/pyxb/bundles/wssplat/schemas/wsdl20.xsd', 199, 8)
    __messageLabel._UseLocation = pyxb.utils.utility.Location('/tmp/pyxbdist.RHB65sy/PyXB-1.1.5/pyxb/bundles/wssplat/schemas/wsdl20.xsd', 199, 8)
    
    messageLabel = property(__messageLabel.value, __messageLabel.set, None, None)

    
    # Attribute element uses Python identifier element
    __element = pyxb.binding.content.AttributeUse(pyxb.namespace.ExpandedName(None, u'element'), 'element', '__httpwww_w3_orgnswsdl_MessageRefType_element', ElementReferenceType)
    __element._DeclarationLocation = pyxb.utils.utility.Location('/tmp/pyxbdist.RHB65sy/PyXB-1.1.5/pyxb/bundles/wssplat/schemas/wsdl20.xsd', 200, 8)
    __element._UseLocation = pyxb.utils.utility.Location('/tmp/pyxbdist.RHB65sy/PyXB-1.1.5/pyxb/bundles/wssplat/schemas/wsdl20.xsd', 200, 8)
    
    element = property(__element.value, __element.set, None, None)

    _AttributeWildcard = pyxb.binding.content.Wildcard(process_contents=pyxb.binding.content.Wildcard.PC_lax, namespace_constraint=(pyxb.binding.content.Wildcard.NC_not, u'http://www.w3.org/ns/wsdl'))
    _HasWildcardElement = True

    _ElementMap = ExtensibleDocumentedType._ElementMap.copy()
    _ElementMap.update({
        
    })
    _AttributeMap = ExtensibleDocumentedType._AttributeMap.copy()
    _AttributeMap.update({
        __messageLabel.name() : __messageLabel,
        __element.name() : __element
    })
Namespace.addCategoryObject('typeBinding', u'MessageRefType', MessageRefType)


# Complex type {http://www.w3.org/ns/wsdl}BindingOperationFaultType with content type ELEMENT_ONLY
class BindingOperationFaultType (ExtensibleDocumentedType):
    _TypeDefinition = None
    _ContentTypeTag = pyxb.binding.basis.complexTypeDefinition._CT_ELEMENT_ONLY
    _Abstract = False
    _ExpandedName = pyxb.namespace.ExpandedName(Namespace, u'BindingOperationFaultType')
    _DefinitionLocation = pyxb.utils.utility.Location('/tmp/pyxbdist.RHB65sy/PyXB-1.1.5/pyxb/bundles/wssplat/schemas/wsdl20.xsd', 292, 2)
    # Base type is ExtensibleDocumentedType
    
    # Element documentation ({http://www.w3.org/ns/wsdl}documentation) inherited from {http://www.w3.org/ns/wsdl}DocumentedType
    
    # Attribute messageLabel uses Python identifier messageLabel
    __messageLabel = pyxb.binding.content.AttributeUse(pyxb.namespace.ExpandedName(None, u'messageLabel'), 'messageLabel', '__httpwww_w3_orgnswsdl_BindingOperationFaultType_messageLabel', pyxb.binding.datatypes.NCName)
    __messageLabel._DeclarationLocation = pyxb.utils.utility.Location('/tmp/pyxbdist.RHB65sy/PyXB-1.1.5/pyxb/bundles/wssplat/schemas/wsdl20.xsd', 299, 8)
    __messageLabel._UseLocation = pyxb.utils.utility.Location('/tmp/pyxbdist.RHB65sy/PyXB-1.1.5/pyxb/bundles/wssplat/schemas/wsdl20.xsd', 299, 8)
    
    messageLabel = property(__messageLabel.value, __messageLabel.set, None, None)

    
    # Attribute ref uses Python identifier ref
    __ref = pyxb.binding.content.AttributeUse(pyxb.namespace.ExpandedName(None, u'ref'), 'ref', '__httpwww_w3_orgnswsdl_BindingOperationFaultType_ref', pyxb.binding.datatypes.QName, required=True)
    __ref._DeclarationLocation = pyxb.utils.utility.Location('/tmp/pyxbdist.RHB65sy/PyXB-1.1.5/pyxb/bundles/wssplat/schemas/wsdl20.xsd', 298, 8)
    __ref._UseLocation = pyxb.utils.utility.Location('/tmp/pyxbdist.RHB65sy/PyXB-1.1.5/pyxb/bundles/wssplat/schemas/wsdl20.xsd', 298, 8)
    
    ref = property(__ref.value, __ref.set, None, None)

    _AttributeWildcard = pyxb.binding.content.Wildcard(process_contents=pyxb.binding.content.Wildcard.PC_lax, namespace_constraint=(pyxb.binding.content.Wildcard.NC_not, u'http://www.w3.org/ns/wsdl'))
    _HasWildcardElement = True

    _ElementMap = ExtensibleDocumentedType._ElementMap.copy()
    _ElementMap.update({
        
    })
    _AttributeMap = ExtensibleDocumentedType._AttributeMap.copy()
    _AttributeMap.update({
        __messageLabel.name() : __messageLabel,
        __ref.name() : __ref
    })
Namespace.addCategoryObject('typeBinding', u'BindingOperationFaultType', BindingOperationFaultType)


# Complex type {http://www.w3.org/ns/wsdl}MessageRefFaultType with content type ELEMENT_ONLY
class MessageRefFaultType (ExtensibleDocumentedType):
    _TypeDefinition = None
    _ContentTypeTag = pyxb.binding.basis.complexTypeDefinition._CT_ELEMENT_ONLY
    _Abstract = False
    _ExpandedName = pyxb.namespace.ExpandedName(Namespace, u'MessageRefFaultType')
    _DefinitionLocation = pyxb.utils.utility.Location('/tmp/pyxbdist.RHB65sy/PyXB-1.1.5/pyxb/bundles/wssplat/schemas/wsdl20.xsd', 225, 2)
    # Base type is ExtensibleDocumentedType
    
    # Element documentation ({http://www.w3.org/ns/wsdl}documentation) inherited from {http://www.w3.org/ns/wsdl}DocumentedType
    
    # Attribute messageLabel uses Python identifier messageLabel
    __messageLabel = pyxb.binding.content.AttributeUse(pyxb.namespace.ExpandedName(None, u'messageLabel'), 'messageLabel', '__httpwww_w3_orgnswsdl_MessageRefFaultType_messageLabel', pyxb.binding.datatypes.NCName)
    __messageLabel._DeclarationLocation = pyxb.utils.utility.Location('/tmp/pyxbdist.RHB65sy/PyXB-1.1.5/pyxb/bundles/wssplat/schemas/wsdl20.xsd', 232, 8)
    __messageLabel._UseLocation = pyxb.utils.utility.Location('/tmp/pyxbdist.RHB65sy/PyXB-1.1.5/pyxb/bundles/wssplat/schemas/wsdl20.xsd', 232, 8)
    
    messageLabel = property(__messageLabel.value, __messageLabel.set, None, None)

    
    # Attribute ref uses Python identifier ref
    __ref = pyxb.binding.content.AttributeUse(pyxb.namespace.ExpandedName(None, u'ref'), 'ref', '__httpwww_w3_orgnswsdl_MessageRefFaultType_ref', pyxb.binding.datatypes.QName, required=True)
    __ref._DeclarationLocation = pyxb.utils.utility.Location('/tmp/pyxbdist.RHB65sy/PyXB-1.1.5/pyxb/bundles/wssplat/schemas/wsdl20.xsd', 231, 8)
    __ref._UseLocation = pyxb.utils.utility.Location('/tmp/pyxbdist.RHB65sy/PyXB-1.1.5/pyxb/bundles/wssplat/schemas/wsdl20.xsd', 231, 8)
    
    ref = property(__ref.value, __ref.set, None, None)

    _AttributeWildcard = pyxb.binding.content.Wildcard(process_contents=pyxb.binding.content.Wildcard.PC_lax, namespace_constraint=(pyxb.binding.content.Wildcard.NC_not, u'http://www.w3.org/ns/wsdl'))
    _HasWildcardElement = True

    _ElementMap = ExtensibleDocumentedType._ElementMap.copy()
    _ElementMap.update({
        
    })
    _AttributeMap = ExtensibleDocumentedType._AttributeMap.copy()
    _AttributeMap.update({
        __messageLabel.name() : __messageLabel,
        __ref.name() : __ref
    })
Namespace.addCategoryObject('typeBinding', u'MessageRefFaultType', MessageRefFaultType)


# Complex type {http://www.w3.org/ns/wsdl}ExtensionElement with content type EMPTY
class ExtensionElement (pyxb.binding.basis.complexTypeDefinition):
    _TypeDefinition = None
    _ContentTypeTag = pyxb.binding.basis.complexTypeDefinition._CT_EMPTY
    _Abstract = True
    _ExpandedName = pyxb.namespace.ExpandedName(Namespace, u'ExtensionElement')
    _DefinitionLocation = pyxb.utils.utility.Location('/tmp/pyxbdist.RHB65sy/PyXB-1.1.5/pyxb/bundles/wssplat/schemas/wsdl20.xsd', 351, 2)
    # Base type is pyxb.binding.datatypes.anyType
    
    # Attribute {http://www.w3.org/ns/wsdl}required uses Python identifier required
    __required = pyxb.binding.content.AttributeUse(pyxb.namespace.ExpandedName(Namespace, u'required'), 'required', '__httpwww_w3_orgnswsdl_ExtensionElement_httpwww_w3_orgnswsdlrequired', pyxb.binding.datatypes.boolean)
    __required._DeclarationLocation = pyxb.utils.utility.Location('/tmp/pyxbdist.RHB65sy/PyXB-1.1.5/pyxb/bundles/wssplat/schemas/wsdl20.xsd', 349, 2)
    __required._UseLocation = pyxb.utils.utility.Location('/tmp/pyxbdist.RHB65sy/PyXB-1.1.5/pyxb/bundles/wssplat/schemas/wsdl20.xsd', 359, 4)
    
    required = property(__required.value, __required.set, None, None)


    _ElementMap = {
        
    }
    _AttributeMap = {
        __required.name() : __required
    }
Namespace.addCategoryObject('typeBinding', u'ExtensionElement', ExtensionElement)


endpoint = pyxb.binding.basis.element(pyxb.namespace.ExpandedName(Namespace, u'endpoint'), EndpointType)
Namespace.addCategoryObject('elementBinding', endpoint.name().localName(), endpoint)

service = pyxb.binding.basis.element(pyxb.namespace.ExpandedName(Namespace, u'service'), ServiceType)
Namespace.addCategoryObject('elementBinding', service.name().localName(), service)

include = pyxb.binding.basis.element(pyxb.namespace.ExpandedName(Namespace, u'include'), IncludeType)
Namespace.addCategoryObject('elementBinding', include.name().localName(), include)

documentation = pyxb.binding.basis.element(pyxb.namespace.ExpandedName(Namespace, u'documentation'), DocumentationType)
Namespace.addCategoryObject('elementBinding', documentation.name().localName(), documentation)

description = pyxb.binding.basis.element(pyxb.namespace.ExpandedName(Namespace, u'description'), DescriptionType)
Namespace.addCategoryObject('elementBinding', description.name().localName(), description)

types = pyxb.binding.basis.element(pyxb.namespace.ExpandedName(Namespace, u'types'), TypesType)
Namespace.addCategoryObject('elementBinding', types.name().localName(), types)

binding = pyxb.binding.basis.element(pyxb.namespace.ExpandedName(Namespace, u'binding'), BindingType)
Namespace.addCategoryObject('elementBinding', binding.name().localName(), binding)

interface = pyxb.binding.basis.element(pyxb.namespace.ExpandedName(Namespace, u'interface'), InterfaceType)
Namespace.addCategoryObject('elementBinding', interface.name().localName(), interface)

import_ = pyxb.binding.basis.element(pyxb.namespace.ExpandedName(Namespace, u'import'), ImportType)
Namespace.addCategoryObject('elementBinding', import_.name().localName(), import_)



DocumentedType._AddElement(pyxb.binding.basis.element(pyxb.namespace.ExpandedName(Namespace, u'documentation'), DocumentationType, scope=DocumentedType))
DocumentedType._GroupModel = pyxb.binding.content.GroupSequence(
    pyxb.binding.content.ParticleModel(DocumentedType._UseForTag(pyxb.namespace.ExpandedName(Namespace, u'documentation')), min_occurs=0L, max_occurs=None)
    )
DocumentedType._ContentModel = pyxb.binding.content.ParticleModel(DocumentedType._GroupModel, min_occurs=1, max_occurs=1)


ExtensibleDocumentedType._GroupModel = pyxb.binding.content.GroupSequence(
    pyxb.binding.content.ParticleModel(ExtensibleDocumentedType._UseForTag(pyxb.namespace.ExpandedName(Namespace, u'documentation')), min_occurs=0L, max_occurs=None)
    )
ExtensibleDocumentedType._ContentModel = pyxb.binding.content.ParticleModel(ExtensibleDocumentedType._GroupModel, min_occurs=1, max_occurs=1)


EndpointType._GroupModel_ = pyxb.binding.content.GroupSequence(
    pyxb.binding.content.ParticleModel(EndpointType._UseForTag(pyxb.namespace.ExpandedName(Namespace, u'documentation')), min_occurs=0L, max_occurs=None)
    )
EndpointType._GroupModel_2 = pyxb.binding.content.GroupChoice(
    pyxb.binding.content.ParticleModel(pyxb.binding.content.Wildcard(process_contents=pyxb.binding.content.Wildcard.PC_lax, namespace_constraint=(pyxb.binding.content.Wildcard.NC_not, u'http://www.w3.org/ns/wsdl')), min_occurs=1L, max_occurs=1L)
    )
EndpointType._GroupModel = pyxb.binding.content.GroupSequence(
    pyxb.binding.content.ParticleModel(EndpointType._GroupModel_, min_occurs=1, max_occurs=1),
    pyxb.binding.content.ParticleModel(EndpointType._GroupModel_2, min_occurs=0L, max_occurs=None)
    )
EndpointType._ContentModel = pyxb.binding.content.ParticleModel(EndpointType._GroupModel, min_occurs=1, max_occurs=1)


BindingFaultType._GroupModel_ = pyxb.binding.content.GroupSequence(
    pyxb.binding.content.ParticleModel(BindingFaultType._UseForTag(pyxb.namespace.ExpandedName(Namespace, u'documentation')), min_occurs=0L, max_occurs=None)
    )
BindingFaultType._GroupModel_2 = pyxb.binding.content.GroupChoice(
    pyxb.binding.content.ParticleModel(pyxb.binding.content.Wildcard(process_contents=pyxb.binding.content.Wildcard.PC_lax, namespace_constraint=(pyxb.binding.content.Wildcard.NC_not, u'http://www.w3.org/ns/wsdl')), min_occurs=1L, max_occurs=1L)
    )
BindingFaultType._GroupModel = pyxb.binding.content.GroupSequence(
    pyxb.binding.content.ParticleModel(BindingFaultType._GroupModel_, min_occurs=1, max_occurs=1),
    pyxb.binding.content.ParticleModel(BindingFaultType._GroupModel_2, min_occurs=0L, max_occurs=None)
    )
BindingFaultType._ContentModel = pyxb.binding.content.ParticleModel(BindingFaultType._GroupModel, min_occurs=1, max_occurs=1)



InterfaceOperationType._AddElement(pyxb.binding.basis.element(pyxb.namespace.ExpandedName(Namespace, u'outfault'), MessageRefFaultType, scope=InterfaceOperationType))

InterfaceOperationType._AddElement(pyxb.binding.basis.element(pyxb.namespace.ExpandedName(Namespace, u'input'), MessageRefType, scope=InterfaceOperationType))

InterfaceOperationType._AddElement(pyxb.binding.basis.element(pyxb.namespace.ExpandedName(Namespace, u'infault'), MessageRefFaultType, scope=InterfaceOperationType))

InterfaceOperationType._AddElement(pyxb.binding.basis.element(pyxb.namespace.ExpandedName(Namespace, u'output'), MessageRefType, scope=InterfaceOperationType))
InterfaceOperationType._GroupModel_ = pyxb.binding.content.GroupSequence(
    pyxb.binding.content.ParticleModel(InterfaceOperationType._UseForTag(pyxb.namespace.ExpandedName(Namespace, u'documentation')), min_occurs=0L, max_occurs=None)
    )
InterfaceOperationType._GroupModel_2 = pyxb.binding.content.GroupChoice(
    pyxb.binding.content.ParticleModel(InterfaceOperationType._UseForTag(pyxb.namespace.ExpandedName(Namespace, u'input')), min_occurs=1, max_occurs=1),
    pyxb.binding.content.ParticleModel(InterfaceOperationType._UseForTag(pyxb.namespace.ExpandedName(Namespace, u'output')), min_occurs=1, max_occurs=1),
    pyxb.binding.content.ParticleModel(InterfaceOperationType._UseForTag(pyxb.namespace.ExpandedName(Namespace, u'infault')), min_occurs=1, max_occurs=1),
    pyxb.binding.content.ParticleModel(InterfaceOperationType._UseForTag(pyxb.namespace.ExpandedName(Namespace, u'outfault')), min_occurs=1, max_occurs=1),
    pyxb.binding.content.ParticleModel(pyxb.binding.content.Wildcard(process_contents=pyxb.binding.content.Wildcard.PC_lax, namespace_constraint=(pyxb.binding.content.Wildcard.NC_not, u'http://www.w3.org/ns/wsdl')), min_occurs=1L, max_occurs=1L)
    )
InterfaceOperationType._GroupModel = pyxb.binding.content.GroupSequence(
    pyxb.binding.content.ParticleModel(InterfaceOperationType._GroupModel_, min_occurs=1, max_occurs=1),
    pyxb.binding.content.ParticleModel(InterfaceOperationType._GroupModel_2, min_occurs=0L, max_occurs=None)
    )
InterfaceOperationType._ContentModel = pyxb.binding.content.ParticleModel(InterfaceOperationType._GroupModel, min_occurs=1, max_occurs=1)



ServiceType._AddElement(pyxb.binding.basis.element(pyxb.namespace.ExpandedName(Namespace, u'endpoint'), EndpointType, scope=ServiceType))
ServiceType._GroupModel_ = pyxb.binding.content.GroupSequence(
    pyxb.binding.content.ParticleModel(ServiceType._UseForTag(pyxb.namespace.ExpandedName(Namespace, u'documentation')), min_occurs=0L, max_occurs=None)
    )
ServiceType._GroupModel_2 = pyxb.binding.content.GroupChoice(
    pyxb.binding.content.ParticleModel(ServiceType._UseForTag(pyxb.namespace.ExpandedName(Namespace, u'endpoint')), min_occurs=1, max_occurs=1),
    pyxb.binding.content.ParticleModel(pyxb.binding.content.Wildcard(process_contents=pyxb.binding.content.Wildcard.PC_lax, namespace_constraint=(pyxb.binding.content.Wildcard.NC_not, u'http://www.w3.org/ns/wsdl')), min_occurs=1L, max_occurs=1L)
    )
ServiceType._GroupModel = pyxb.binding.content.GroupSequence(
    pyxb.binding.content.ParticleModel(ServiceType._GroupModel_, min_occurs=1, max_occurs=1),
    pyxb.binding.content.ParticleModel(ServiceType._GroupModel_2, min_occurs=1L, max_occurs=None)
    )
ServiceType._ContentModel = pyxb.binding.content.ParticleModel(ServiceType._GroupModel, min_occurs=1, max_occurs=1)


ImportType._GroupModel_ = pyxb.binding.content.GroupSequence(
    pyxb.binding.content.ParticleModel(ImportType._UseForTag(pyxb.namespace.ExpandedName(Namespace, u'documentation')), min_occurs=0L, max_occurs=None)
    )
ImportType._GroupModel_2 = pyxb.binding.content.GroupSequence(
    pyxb.binding.content.ParticleModel(pyxb.binding.content.Wildcard(process_contents=pyxb.binding.content.Wildcard.PC_strict, namespace_constraint=(pyxb.binding.content.Wildcard.NC_not, u'http://www.w3.org/ns/wsdl')), min_occurs=0L, max_occurs=None)
    )
ImportType._GroupModel = pyxb.binding.content.GroupSequence(
    pyxb.binding.content.ParticleModel(ImportType._GroupModel_, min_occurs=1, max_occurs=1),
    pyxb.binding.content.ParticleModel(ImportType._GroupModel_2, min_occurs=1, max_occurs=1)
    )
ImportType._ContentModel = pyxb.binding.content.ParticleModel(ImportType._GroupModel, min_occurs=1, max_occurs=1)


IncludeType._GroupModel_ = pyxb.binding.content.GroupSequence(
    pyxb.binding.content.ParticleModel(IncludeType._UseForTag(pyxb.namespace.ExpandedName(Namespace, u'documentation')), min_occurs=0L, max_occurs=None)
    )
IncludeType._GroupModel_2 = pyxb.binding.content.GroupSequence(
    pyxb.binding.content.ParticleModel(pyxb.binding.content.Wildcard(process_contents=pyxb.binding.content.Wildcard.PC_strict, namespace_constraint=(pyxb.binding.content.Wildcard.NC_not, u'http://www.w3.org/ns/wsdl')), min_occurs=0L, max_occurs=None)
    )
IncludeType._GroupModel = pyxb.binding.content.GroupSequence(
    pyxb.binding.content.ParticleModel(IncludeType._GroupModel_, min_occurs=1, max_occurs=1),
    pyxb.binding.content.ParticleModel(IncludeType._GroupModel_2, min_occurs=1, max_occurs=1)
    )
IncludeType._ContentModel = pyxb.binding.content.ParticleModel(IncludeType._GroupModel, min_occurs=1, max_occurs=1)


DocumentationType._GroupModel = pyxb.binding.content.GroupSequence(
    pyxb.binding.content.ParticleModel(pyxb.binding.content.Wildcard(process_contents=pyxb.binding.content.Wildcard.PC_lax, namespace_constraint=pyxb.binding.content.Wildcard.NC_any), min_occurs=0L, max_occurs=None)
    )
DocumentationType._ContentModel = pyxb.binding.content.ParticleModel(DocumentationType._GroupModel, min_occurs=1, max_occurs=1)



BindingOperationType._AddElement(pyxb.binding.basis.element(pyxb.namespace.ExpandedName(Namespace, u'outfault'), BindingOperationFaultType, scope=BindingOperationType))

BindingOperationType._AddElement(pyxb.binding.basis.element(pyxb.namespace.ExpandedName(Namespace, u'input'), BindingOperationMessageType, scope=BindingOperationType))

BindingOperationType._AddElement(pyxb.binding.basis.element(pyxb.namespace.ExpandedName(Namespace, u'output'), BindingOperationMessageType, scope=BindingOperationType))

BindingOperationType._AddElement(pyxb.binding.basis.element(pyxb.namespace.ExpandedName(Namespace, u'infault'), BindingOperationFaultType, scope=BindingOperationType))
BindingOperationType._GroupModel_ = pyxb.binding.content.GroupSequence(
    pyxb.binding.content.ParticleModel(BindingOperationType._UseForTag(pyxb.namespace.ExpandedName(Namespace, u'documentation')), min_occurs=0L, max_occurs=None)
    )
BindingOperationType._GroupModel_2 = pyxb.binding.content.GroupChoice(
    pyxb.binding.content.ParticleModel(BindingOperationType._UseForTag(pyxb.namespace.ExpandedName(Namespace, u'input')), min_occurs=1, max_occurs=1),
    pyxb.binding.content.ParticleModel(BindingOperationType._UseForTag(pyxb.namespace.ExpandedName(Namespace, u'output')), min_occurs=1, max_occurs=1),
    pyxb.binding.content.ParticleModel(BindingOperationType._UseForTag(pyxb.namespace.ExpandedName(Namespace, u'infault')), min_occurs=1, max_occurs=1),
    pyxb.binding.content.ParticleModel(BindingOperationType._UseForTag(pyxb.namespace.ExpandedName(Namespace, u'outfault')), min_occurs=1, max_occurs=1),
    pyxb.binding.content.ParticleModel(pyxb.binding.content.Wildcard(process_contents=pyxb.binding.content.Wildcard.PC_lax, namespace_constraint=(pyxb.binding.content.Wildcard.NC_not, u'http://www.w3.org/ns/wsdl')), min_occurs=1L, max_occurs=1L)
    )
BindingOperationType._GroupModel = pyxb.binding.content.GroupSequence(
    pyxb.binding.content.ParticleModel(BindingOperationType._GroupModel_, min_occurs=1, max_occurs=1),
    pyxb.binding.content.ParticleModel(BindingOperationType._GroupModel_2, min_occurs=0L, max_occurs=None)
    )
BindingOperationType._ContentModel = pyxb.binding.content.ParticleModel(BindingOperationType._GroupModel, min_occurs=1, max_occurs=1)



DescriptionType._AddElement(pyxb.binding.basis.element(pyxb.namespace.ExpandedName(Namespace, u'include'), IncludeType, scope=DescriptionType))

DescriptionType._AddElement(pyxb.binding.basis.element(pyxb.namespace.ExpandedName(Namespace, u'binding'), BindingType, scope=DescriptionType))

DescriptionType._AddElement(pyxb.binding.basis.element(pyxb.namespace.ExpandedName(Namespace, u'types'), TypesType, scope=DescriptionType))

DescriptionType._AddElement(pyxb.binding.basis.element(pyxb.namespace.ExpandedName(Namespace, u'service'), ServiceType, scope=DescriptionType))

DescriptionType._AddElement(pyxb.binding.basis.element(pyxb.namespace.ExpandedName(Namespace, u'interface'), InterfaceType, scope=DescriptionType))

DescriptionType._AddElement(pyxb.binding.basis.element(pyxb.namespace.ExpandedName(Namespace, u'import'), ImportType, scope=DescriptionType))
DescriptionType._GroupModel_ = pyxb.binding.content.GroupSequence(
    pyxb.binding.content.ParticleModel(DescriptionType._UseForTag(pyxb.namespace.ExpandedName(Namespace, u'documentation')), min_occurs=0L, max_occurs=None)
    )
DescriptionType._GroupModel_2 = pyxb.binding.content.GroupChoice(
    pyxb.binding.content.ParticleModel(DescriptionType._UseForTag(pyxb.namespace.ExpandedName(Namespace, u'import')), min_occurs=1, max_occurs=1),
    pyxb.binding.content.ParticleModel(DescriptionType._UseForTag(pyxb.namespace.ExpandedName(Namespace, u'include')), min_occurs=1, max_occurs=1),
    pyxb.binding.content.ParticleModel(DescriptionType._UseForTag(pyxb.namespace.ExpandedName(Namespace, u'types')), min_occurs=1, max_occurs=1),
    pyxb.binding.content.ParticleModel(DescriptionType._UseForTag(pyxb.namespace.ExpandedName(Namespace, u'interface')), min_occurs=1, max_occurs=1),
    pyxb.binding.content.ParticleModel(DescriptionType._UseForTag(pyxb.namespace.ExpandedName(Namespace, u'binding')), min_occurs=1, max_occurs=1),
    pyxb.binding.content.ParticleModel(DescriptionType._UseForTag(pyxb.namespace.ExpandedName(Namespace, u'service')), min_occurs=1, max_occurs=1),
    pyxb.binding.content.ParticleModel(pyxb.binding.content.Wildcard(process_contents=pyxb.binding.content.Wildcard.PC_lax, namespace_constraint=(pyxb.binding.content.Wildcard.NC_not, u'http://www.w3.org/ns/wsdl')), min_occurs=1L, max_occurs=1L)
    )
DescriptionType._GroupModel = pyxb.binding.content.GroupSequence(
    pyxb.binding.content.ParticleModel(DescriptionType._GroupModel_, min_occurs=1, max_occurs=1),
    pyxb.binding.content.ParticleModel(DescriptionType._GroupModel_2, min_occurs=0L, max_occurs=None)
    )
DescriptionType._ContentModel = pyxb.binding.content.ParticleModel(DescriptionType._GroupModel, min_occurs=1, max_occurs=1)


TypesType._GroupModel_ = pyxb.binding.content.GroupSequence(
    pyxb.binding.content.ParticleModel(TypesType._UseForTag(pyxb.namespace.ExpandedName(Namespace, u'documentation')), min_occurs=0L, max_occurs=None)
    )
TypesType._GroupModel_2 = pyxb.binding.content.GroupSequence(
    pyxb.binding.content.ParticleModel(pyxb.binding.content.Wildcard(process_contents=pyxb.binding.content.Wildcard.PC_strict, namespace_constraint=(pyxb.binding.content.Wildcard.NC_not, u'http://www.w3.org/ns/wsdl')), min_occurs=0L, max_occurs=None)
    )
TypesType._GroupModel = pyxb.binding.content.GroupSequence(
    pyxb.binding.content.ParticleModel(TypesType._GroupModel_, min_occurs=1, max_occurs=1),
    pyxb.binding.content.ParticleModel(TypesType._GroupModel_2, min_occurs=1, max_occurs=1)
    )
TypesType._ContentModel = pyxb.binding.content.ParticleModel(TypesType._GroupModel, min_occurs=1, max_occurs=1)



BindingType._AddElement(pyxb.binding.basis.element(pyxb.namespace.ExpandedName(Namespace, u'fault'), BindingFaultType, scope=BindingType))

BindingType._AddElement(pyxb.binding.basis.element(pyxb.namespace.ExpandedName(Namespace, u'operation'), BindingOperationType, scope=BindingType))
BindingType._GroupModel_ = pyxb.binding.content.GroupSequence(
    pyxb.binding.content.ParticleModel(BindingType._UseForTag(pyxb.namespace.ExpandedName(Namespace, u'documentation')), min_occurs=0L, max_occurs=None)
    )
BindingType._GroupModel_2 = pyxb.binding.content.GroupChoice(
    pyxb.binding.content.ParticleModel(BindingType._UseForTag(pyxb.namespace.ExpandedName(Namespace, u'operation')), min_occurs=1, max_occurs=1),
    pyxb.binding.content.ParticleModel(BindingType._UseForTag(pyxb.namespace.ExpandedName(Namespace, u'fault')), min_occurs=1, max_occurs=1),
    pyxb.binding.content.ParticleModel(pyxb.binding.content.Wildcard(process_contents=pyxb.binding.content.Wildcard.PC_lax, namespace_constraint=(pyxb.binding.content.Wildcard.NC_not, u'http://www.w3.org/ns/wsdl')), min_occurs=1L, max_occurs=1L)
    )
BindingType._GroupModel = pyxb.binding.content.GroupSequence(
    pyxb.binding.content.ParticleModel(BindingType._GroupModel_, min_occurs=1, max_occurs=1),
    pyxb.binding.content.ParticleModel(BindingType._GroupModel_2, min_occurs=0L, max_occurs=None)
    )
BindingType._ContentModel = pyxb.binding.content.ParticleModel(BindingType._GroupModel, min_occurs=1, max_occurs=1)


InterfaceFaultType._GroupModel_ = pyxb.binding.content.GroupSequence(
    pyxb.binding.content.ParticleModel(InterfaceFaultType._UseForTag(pyxb.namespace.ExpandedName(Namespace, u'documentation')), min_occurs=0L, max_occurs=None)
    )
InterfaceFaultType._GroupModel_2 = pyxb.binding.content.GroupChoice(
    pyxb.binding.content.ParticleModel(pyxb.binding.content.Wildcard(process_contents=pyxb.binding.content.Wildcard.PC_lax, namespace_constraint=(pyxb.binding.content.Wildcard.NC_not, u'http://www.w3.org/ns/wsdl')), min_occurs=1L, max_occurs=1L)
    )
InterfaceFaultType._GroupModel = pyxb.binding.content.GroupSequence(
    pyxb.binding.content.ParticleModel(InterfaceFaultType._GroupModel_, min_occurs=1, max_occurs=1),
    pyxb.binding.content.ParticleModel(InterfaceFaultType._GroupModel_2, min_occurs=0L, max_occurs=None)
    )
InterfaceFaultType._ContentModel = pyxb.binding.content.ParticleModel(InterfaceFaultType._GroupModel, min_occurs=1, max_occurs=1)


BindingOperationMessageType._GroupModel_ = pyxb.binding.content.GroupSequence(
    pyxb.binding.content.ParticleModel(BindingOperationMessageType._UseForTag(pyxb.namespace.ExpandedName(Namespace, u'documentation')), min_occurs=0L, max_occurs=None)
    )
BindingOperationMessageType._GroupModel_2 = pyxb.binding.content.GroupChoice(
    pyxb.binding.content.ParticleModel(pyxb.binding.content.Wildcard(process_contents=pyxb.binding.content.Wildcard.PC_lax, namespace_constraint=(pyxb.binding.content.Wildcard.NC_not, u'http://www.w3.org/ns/wsdl')), min_occurs=1L, max_occurs=1L)
    )
BindingOperationMessageType._GroupModel = pyxb.binding.content.GroupSequence(
    pyxb.binding.content.ParticleModel(BindingOperationMessageType._GroupModel_, min_occurs=1, max_occurs=1),
    pyxb.binding.content.ParticleModel(BindingOperationMessageType._GroupModel_2, min_occurs=0L, max_occurs=None)
    )
BindingOperationMessageType._ContentModel = pyxb.binding.content.ParticleModel(BindingOperationMessageType._GroupModel, min_occurs=1, max_occurs=1)



InterfaceType._AddElement(pyxb.binding.basis.element(pyxb.namespace.ExpandedName(Namespace, u'fault'), InterfaceFaultType, scope=InterfaceType))

InterfaceType._AddElement(pyxb.binding.basis.element(pyxb.namespace.ExpandedName(Namespace, u'operation'), InterfaceOperationType, scope=InterfaceType))
InterfaceType._GroupModel_ = pyxb.binding.content.GroupSequence(
    pyxb.binding.content.ParticleModel(InterfaceType._UseForTag(pyxb.namespace.ExpandedName(Namespace, u'documentation')), min_occurs=0L, max_occurs=None)
    )
InterfaceType._GroupModel_2 = pyxb.binding.content.GroupChoice(
    pyxb.binding.content.ParticleModel(InterfaceType._UseForTag(pyxb.namespace.ExpandedName(Namespace, u'operation')), min_occurs=1, max_occurs=1),
    pyxb.binding.content.ParticleModel(InterfaceType._UseForTag(pyxb.namespace.ExpandedName(Namespace, u'fault')), min_occurs=1, max_occurs=1),
    pyxb.binding.content.ParticleModel(pyxb.binding.content.Wildcard(process_contents=pyxb.binding.content.Wildcard.PC_lax, namespace_constraint=(pyxb.binding.content.Wildcard.NC_not, u'http://www.w3.org/ns/wsdl')), min_occurs=1L, max_occurs=1L)
    )
InterfaceType._GroupModel = pyxb.binding.content.GroupSequence(
    pyxb.binding.content.ParticleModel(InterfaceType._GroupModel_, min_occurs=1, max_occurs=1),
    pyxb.binding.content.ParticleModel(InterfaceType._GroupModel_2, min_occurs=0L, max_occurs=None)
    )
InterfaceType._ContentModel = pyxb.binding.content.ParticleModel(InterfaceType._GroupModel, min_occurs=1, max_occurs=1)


MessageRefType._GroupModel_ = pyxb.binding.content.GroupSequence(
    pyxb.binding.content.ParticleModel(MessageRefType._UseForTag(pyxb.namespace.ExpandedName(Namespace, u'documentation')), min_occurs=0L, max_occurs=None)
    )
MessageRefType._GroupModel_2 = pyxb.binding.content.GroupChoice(
    pyxb.binding.content.ParticleModel(pyxb.binding.content.Wildcard(process_contents=pyxb.binding.content.Wildcard.PC_lax, namespace_constraint=(pyxb.binding.content.Wildcard.NC_not, u'http://www.w3.org/ns/wsdl')), min_occurs=1L, max_occurs=1L)
    )
MessageRefType._GroupModel = pyxb.binding.content.GroupSequence(
    pyxb.binding.content.ParticleModel(MessageRefType._GroupModel_, min_occurs=1, max_occurs=1),
    pyxb.binding.content.ParticleModel(MessageRefType._GroupModel_2, min_occurs=0L, max_occurs=None)
    )
MessageRefType._ContentModel = pyxb.binding.content.ParticleModel(MessageRefType._GroupModel, min_occurs=1, max_occurs=1)


BindingOperationFaultType._GroupModel_ = pyxb.binding.content.GroupSequence(
    pyxb.binding.content.ParticleModel(BindingOperationFaultType._UseForTag(pyxb.namespace.ExpandedName(Namespace, u'documentation')), min_occurs=0L, max_occurs=None)
    )
BindingOperationFaultType._GroupModel_2 = pyxb.binding.content.GroupChoice(
    pyxb.binding.content.ParticleModel(pyxb.binding.content.Wildcard(process_contents=pyxb.binding.content.Wildcard.PC_lax, namespace_constraint=(pyxb.binding.content.Wildcard.NC_not, u'http://www.w3.org/ns/wsdl')), min_occurs=1L, max_occurs=1L)
    )
BindingOperationFaultType._GroupModel = pyxb.binding.content.GroupSequence(
    pyxb.binding.content.ParticleModel(BindingOperationFaultType._GroupModel_, min_occurs=1, max_occurs=1),
    pyxb.binding.content.ParticleModel(BindingOperationFaultType._GroupModel_2, min_occurs=0L, max_occurs=None)
    )
BindingOperationFaultType._ContentModel = pyxb.binding.content.ParticleModel(BindingOperationFaultType._GroupModel, min_occurs=1, max_occurs=1)


MessageRefFaultType._GroupModel_ = pyxb.binding.content.GroupSequence(
    pyxb.binding.content.ParticleModel(MessageRefFaultType._UseForTag(pyxb.namespace.ExpandedName(Namespace, u'documentation')), min_occurs=0L, max_occurs=None)
    )
MessageRefFaultType._GroupModel_2 = pyxb.binding.content.GroupChoice(
    pyxb.binding.content.ParticleModel(pyxb.binding.content.Wildcard(process_contents=pyxb.binding.content.Wildcard.PC_lax, namespace_constraint=(pyxb.binding.content.Wildcard.NC_not, u'http://www.w3.org/ns/wsdl')), min_occurs=1L, max_occurs=1L)
    )
MessageRefFaultType._GroupModel = pyxb.binding.content.GroupSequence(
    pyxb.binding.content.ParticleModel(MessageRefFaultType._GroupModel_, min_occurs=1, max_occurs=1),
    pyxb.binding.content.ParticleModel(MessageRefFaultType._GroupModel_2, min_occurs=0L, max_occurs=None)
    )
MessageRefFaultType._ContentModel = pyxb.binding.content.ParticleModel(MessageRefFaultType._GroupModel, min_occurs=1, max_occurs=1)
