# ./pyxb/bundles/wssplat/raw/soapbind12.py
# -*- coding: utf-8 -*-
# PyXB bindings for NM:fe6dee6f975d5202c12c3e364c8df804f68deab8
# Generated 2012-11-01 15:13:35.503487 by PyXB version 1.1.5
# Namespace http://schemas.xmlsoap.org/wsdl/soap12/

import pyxb
import pyxb.binding
import pyxb.binding.saxer
import StringIO
import pyxb.utils.utility
import pyxb.utils.domutils
import sys

# Unique identifier for bindings created at the same time
_GenerationUID = pyxb.utils.utility.UniqueIdentifier('urn:uuid:9da27190-2460-11e2-9a61-c8600024e903')

# Import bindings for namespaces imported into schema
import pyxb.binding.datatypes
import pyxb.bundles.wssplat.wsdl11

Namespace = pyxb.namespace.NamespaceForURI(u'http://schemas.xmlsoap.org/wsdl/soap12/', create_if_missing=True)
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


# Atomic simple type: {http://schemas.xmlsoap.org/wsdl/soap12/}useChoice
class useChoice (pyxb.binding.datatypes.string, pyxb.binding.basis.enumeration_mixin):

    """An atomic simple type."""

    _ExpandedName = pyxb.namespace.ExpandedName(Namespace, u'useChoice')
    _DefinitionLocation = pyxb.utils.utility.Location('/tmp/pyxbdist.RHB65sy/PyXB-1.1.5/pyxb/bundles/wssplat/schemas/soapbind12.xsd', 83, 2)
    _Documentation = None
useChoice._CF_enumeration = pyxb.binding.facets.CF_enumeration(value_datatype=useChoice, enum_prefix=None)
useChoice.literal = useChoice._CF_enumeration.addEnumeration(unicode_value=u'literal', tag=u'literal')
useChoice.encoded = useChoice._CF_enumeration.addEnumeration(unicode_value=u'encoded', tag=u'encoded')
useChoice._InitializeFacetMap(useChoice._CF_enumeration)
Namespace.addCategoryObject('typeBinding', u'useChoice', useChoice)

# Atomic simple type: {http://schemas.xmlsoap.org/wsdl/soap12/}tStyleChoice
class tStyleChoice (pyxb.binding.datatypes.string, pyxb.binding.basis.enumeration_mixin):

    """An atomic simple type."""

    _ExpandedName = pyxb.namespace.ExpandedName(Namespace, u'tStyleChoice')
    _DefinitionLocation = pyxb.utils.utility.Location('/tmp/pyxbdist.RHB65sy/PyXB-1.1.5/pyxb/bundles/wssplat/schemas/soapbind12.xsd', 46, 2)
    _Documentation = None
tStyleChoice._CF_enumeration = pyxb.binding.facets.CF_enumeration(value_datatype=tStyleChoice, enum_prefix=None)
tStyleChoice.rpc = tStyleChoice._CF_enumeration.addEnumeration(unicode_value=u'rpc', tag=u'rpc')
tStyleChoice.document = tStyleChoice._CF_enumeration.addEnumeration(unicode_value=u'document', tag=u'document')
tStyleChoice._InitializeFacetMap(tStyleChoice._CF_enumeration)
Namespace.addCategoryObject('typeBinding', u'tStyleChoice', tStyleChoice)

# List simple type: {http://schemas.xmlsoap.org/wsdl/soap12/}tParts
# superclasses pyxb.binding.datatypes.anySimpleType
class tParts (pyxb.binding.basis.STD_list):

    """Simple type that is a list of pyxb.binding.datatypes.NMTOKEN."""

    _ExpandedName = pyxb.namespace.ExpandedName(Namespace, u'tParts')
    _DefinitionLocation = pyxb.utils.utility.Location('/tmp/pyxbdist.RHB65sy/PyXB-1.1.5/pyxb/bundles/wssplat/schemas/soapbind12.xsd', 71, 2)
    _Documentation = None

    _ItemType = pyxb.binding.datatypes.NMTOKEN
tParts._InitializeFacetMap()
Namespace.addCategoryObject('typeBinding', u'tParts', tParts)

# Complex type {http://schemas.xmlsoap.org/wsdl/soap12/}tExtensibilityElementOpenAttrs with content type EMPTY
class tExtensibilityElementOpenAttrs (pyxb.bundles.wssplat.wsdl11.tExtensibilityElement):
    _TypeDefinition = None
    _ContentTypeTag = pyxb.binding.basis.complexTypeDefinition._CT_EMPTY
    _Abstract = False
    _ExpandedName = pyxb.namespace.ExpandedName(Namespace, u'tExtensibilityElementOpenAttrs')
    _DefinitionLocation = pyxb.utils.utility.Location('/tmp/pyxbdist.RHB65sy/PyXB-1.1.5/pyxb/bundles/wssplat/schemas/soapbind12.xsd', 28, 2)
    # Base type is pyxb.bundles.wssplat.wsdl11.tExtensibilityElement
    
    # Attribute required inherited from {http://schemas.xmlsoap.org/wsdl/}tExtensibilityElement
    _AttributeWildcard = pyxb.binding.content.Wildcard(process_contents=pyxb.binding.content.Wildcard.PC_lax, namespace_constraint=(pyxb.binding.content.Wildcard.NC_not, u'http://schemas.xmlsoap.org/wsdl/soap12/'))

    _ElementMap = pyxb.bundles.wssplat.wsdl11.tExtensibilityElement._ElementMap.copy()
    _ElementMap.update({
        
    })
    _AttributeMap = pyxb.bundles.wssplat.wsdl11.tExtensibilityElement._AttributeMap.copy()
    _AttributeMap.update({
        
    })
Namespace.addCategoryObject('typeBinding', u'tExtensibilityElementOpenAttrs', tExtensibilityElementOpenAttrs)


# Complex type {http://schemas.xmlsoap.org/wsdl/soap12/}tHeader with content type ELEMENT_ONLY
class tHeader (tExtensibilityElementOpenAttrs):
    _TypeDefinition = None
    _ContentTypeTag = pyxb.binding.basis.complexTypeDefinition._CT_ELEMENT_ONLY
    _Abstract = False
    _ExpandedName = pyxb.namespace.ExpandedName(Namespace, u'tHeader')
    _DefinitionLocation = pyxb.utils.utility.Location('/tmp/pyxbdist.RHB65sy/PyXB-1.1.5/pyxb/bundles/wssplat/schemas/soapbind12.xsd', 117, 2)
    # Base type is tExtensibilityElementOpenAttrs
    
    # Element {http://schemas.xmlsoap.org/wsdl/soap12/}headerfault uses Python identifier headerfault
    __headerfault = pyxb.binding.content.ElementUse(pyxb.namespace.ExpandedName(Namespace, u'headerfault'), 'headerfault', '__httpschemas_xmlsoap_orgwsdlsoap12_tHeader_httpschemas_xmlsoap_orgwsdlsoap12headerfault', True)
    __headerfault._DeclarationLocation = pyxb.utils.utility.Location('/tmp/pyxbdist.RHB65sy/PyXB-1.1.5/pyxb/bundles/wssplat/schemas/soapbind12.xsd', 128, 2)
    __headerfault._UseLocation = pyxb.utils.utility.Location('/tmp/pyxbdist.RHB65sy/PyXB-1.1.5/pyxb/bundles/wssplat/schemas/soapbind12.xsd', 120, 8)

    
    headerfault = property(__headerfault.value, __headerfault.set, None, None)

    
    # Attribute part uses Python identifier part
    __part = pyxb.binding.content.AttributeUse(pyxb.namespace.ExpandedName(None, u'part'), 'part', '__httpschemas_xmlsoap_orgwsdlsoap12_tHeader_part', pyxb.binding.datatypes.NMTOKEN, required=True)
    __part._DeclarationLocation = pyxb.utils.utility.Location('/tmp/pyxbdist.RHB65sy/PyXB-1.1.5/pyxb/bundles/wssplat/schemas/soapbind12.xsd', 112, 4)
    __part._UseLocation = pyxb.utils.utility.Location('/tmp/pyxbdist.RHB65sy/PyXB-1.1.5/pyxb/bundles/wssplat/schemas/soapbind12.xsd', 112, 4)
    
    part = property(__part.value, __part.set, None, None)

    
    # Attribute message uses Python identifier message
    __message = pyxb.binding.content.AttributeUse(pyxb.namespace.ExpandedName(None, u'message'), 'message', '__httpschemas_xmlsoap_orgwsdlsoap12_tHeader_message', pyxb.binding.datatypes.QName, required=True)
    __message._DeclarationLocation = pyxb.utils.utility.Location('/tmp/pyxbdist.RHB65sy/PyXB-1.1.5/pyxb/bundles/wssplat/schemas/soapbind12.xsd', 111, 4)
    __message._UseLocation = pyxb.utils.utility.Location('/tmp/pyxbdist.RHB65sy/PyXB-1.1.5/pyxb/bundles/wssplat/schemas/soapbind12.xsd', 111, 4)
    
    message = property(__message.value, __message.set, None, None)

    
    # Attribute namespace uses Python identifier namespace
    __namespace = pyxb.binding.content.AttributeUse(pyxb.namespace.ExpandedName(None, u'namespace'), 'namespace', '__httpschemas_xmlsoap_orgwsdlsoap12_tHeader_namespace', pyxb.binding.datatypes.anyURI)
    __namespace._DeclarationLocation = pyxb.utils.utility.Location('/tmp/pyxbdist.RHB65sy/PyXB-1.1.5/pyxb/bundles/wssplat/schemas/soapbind12.xsd', 115, 4)
    __namespace._UseLocation = pyxb.utils.utility.Location('/tmp/pyxbdist.RHB65sy/PyXB-1.1.5/pyxb/bundles/wssplat/schemas/soapbind12.xsd', 115, 4)
    
    namespace = property(__namespace.value, __namespace.set, None, None)

    
    # Attribute use uses Python identifier use
    __use = pyxb.binding.content.AttributeUse(pyxb.namespace.ExpandedName(None, u'use'), 'use', '__httpschemas_xmlsoap_orgwsdlsoap12_tHeader_use', useChoice, required=True)
    __use._DeclarationLocation = pyxb.utils.utility.Location('/tmp/pyxbdist.RHB65sy/PyXB-1.1.5/pyxb/bundles/wssplat/schemas/soapbind12.xsd', 113, 4)
    __use._UseLocation = pyxb.utils.utility.Location('/tmp/pyxbdist.RHB65sy/PyXB-1.1.5/pyxb/bundles/wssplat/schemas/soapbind12.xsd', 113, 4)
    
    use = property(__use.value, __use.set, None, None)

    
    # Attribute required inherited from {http://schemas.xmlsoap.org/wsdl/}tExtensibilityElement
    
    # Attribute encodingStyle uses Python identifier encodingStyle
    __encodingStyle = pyxb.binding.content.AttributeUse(pyxb.namespace.ExpandedName(None, u'encodingStyle'), 'encodingStyle', '__httpschemas_xmlsoap_orgwsdlsoap12_tHeader_encodingStyle', pyxb.binding.datatypes.anyURI)
    __encodingStyle._DeclarationLocation = pyxb.utils.utility.Location('/tmp/pyxbdist.RHB65sy/PyXB-1.1.5/pyxb/bundles/wssplat/schemas/soapbind12.xsd', 114, 4)
    __encodingStyle._UseLocation = pyxb.utils.utility.Location('/tmp/pyxbdist.RHB65sy/PyXB-1.1.5/pyxb/bundles/wssplat/schemas/soapbind12.xsd', 114, 4)
    
    encodingStyle = property(__encodingStyle.value, __encodingStyle.set, None, None)

    _AttributeWildcard = pyxb.binding.content.Wildcard(process_contents=pyxb.binding.content.Wildcard.PC_lax, namespace_constraint=(pyxb.binding.content.Wildcard.NC_not, u'http://schemas.xmlsoap.org/wsdl/soap12/'))

    _ElementMap = tExtensibilityElementOpenAttrs._ElementMap.copy()
    _ElementMap.update({
        __headerfault.name() : __headerfault
    })
    _AttributeMap = tExtensibilityElementOpenAttrs._AttributeMap.copy()
    _AttributeMap.update({
        __part.name() : __part,
        __message.name() : __message,
        __namespace.name() : __namespace,
        __use.name() : __use,
        __encodingStyle.name() : __encodingStyle
    })
Namespace.addCategoryObject('typeBinding', u'tHeader', tHeader)


# Complex type {http://schemas.xmlsoap.org/wsdl/soap12/}tHeaderFault with content type EMPTY
class tHeaderFault (pyxb.binding.basis.complexTypeDefinition):
    _TypeDefinition = None
    _ContentTypeTag = pyxb.binding.basis.complexTypeDefinition._CT_EMPTY
    _Abstract = False
    _ExpandedName = pyxb.namespace.ExpandedName(Namespace, u'tHeaderFault')
    _DefinitionLocation = pyxb.utils.utility.Location('/tmp/pyxbdist.RHB65sy/PyXB-1.1.5/pyxb/bundles/wssplat/schemas/soapbind12.xsd', 129, 2)
    # Base type is pyxb.binding.datatypes.anyType
    
    # Attribute encodingStyle uses Python identifier encodingStyle
    __encodingStyle = pyxb.binding.content.AttributeUse(pyxb.namespace.ExpandedName(None, u'encodingStyle'), 'encodingStyle', '__httpschemas_xmlsoap_orgwsdlsoap12_tHeaderFault_encodingStyle', pyxb.binding.datatypes.anyURI)
    __encodingStyle._DeclarationLocation = pyxb.utils.utility.Location('/tmp/pyxbdist.RHB65sy/PyXB-1.1.5/pyxb/bundles/wssplat/schemas/soapbind12.xsd', 114, 4)
    __encodingStyle._UseLocation = pyxb.utils.utility.Location('/tmp/pyxbdist.RHB65sy/PyXB-1.1.5/pyxb/bundles/wssplat/schemas/soapbind12.xsd', 114, 4)
    
    encodingStyle = property(__encodingStyle.value, __encodingStyle.set, None, None)

    
    # Attribute part uses Python identifier part
    __part = pyxb.binding.content.AttributeUse(pyxb.namespace.ExpandedName(None, u'part'), 'part', '__httpschemas_xmlsoap_orgwsdlsoap12_tHeaderFault_part', pyxb.binding.datatypes.NMTOKEN, required=True)
    __part._DeclarationLocation = pyxb.utils.utility.Location('/tmp/pyxbdist.RHB65sy/PyXB-1.1.5/pyxb/bundles/wssplat/schemas/soapbind12.xsd', 112, 4)
    __part._UseLocation = pyxb.utils.utility.Location('/tmp/pyxbdist.RHB65sy/PyXB-1.1.5/pyxb/bundles/wssplat/schemas/soapbind12.xsd', 112, 4)
    
    part = property(__part.value, __part.set, None, None)

    
    # Attribute message uses Python identifier message
    __message = pyxb.binding.content.AttributeUse(pyxb.namespace.ExpandedName(None, u'message'), 'message', '__httpschemas_xmlsoap_orgwsdlsoap12_tHeaderFault_message', pyxb.binding.datatypes.QName, required=True)
    __message._DeclarationLocation = pyxb.utils.utility.Location('/tmp/pyxbdist.RHB65sy/PyXB-1.1.5/pyxb/bundles/wssplat/schemas/soapbind12.xsd', 111, 4)
    __message._UseLocation = pyxb.utils.utility.Location('/tmp/pyxbdist.RHB65sy/PyXB-1.1.5/pyxb/bundles/wssplat/schemas/soapbind12.xsd', 111, 4)
    
    message = property(__message.value, __message.set, None, None)

    
    # Attribute use uses Python identifier use
    __use = pyxb.binding.content.AttributeUse(pyxb.namespace.ExpandedName(None, u'use'), 'use', '__httpschemas_xmlsoap_orgwsdlsoap12_tHeaderFault_use', useChoice, required=True)
    __use._DeclarationLocation = pyxb.utils.utility.Location('/tmp/pyxbdist.RHB65sy/PyXB-1.1.5/pyxb/bundles/wssplat/schemas/soapbind12.xsd', 113, 4)
    __use._UseLocation = pyxb.utils.utility.Location('/tmp/pyxbdist.RHB65sy/PyXB-1.1.5/pyxb/bundles/wssplat/schemas/soapbind12.xsd', 113, 4)
    
    use = property(__use.value, __use.set, None, None)

    
    # Attribute namespace uses Python identifier namespace
    __namespace = pyxb.binding.content.AttributeUse(pyxb.namespace.ExpandedName(None, u'namespace'), 'namespace', '__httpschemas_xmlsoap_orgwsdlsoap12_tHeaderFault_namespace', pyxb.binding.datatypes.anyURI)
    __namespace._DeclarationLocation = pyxb.utils.utility.Location('/tmp/pyxbdist.RHB65sy/PyXB-1.1.5/pyxb/bundles/wssplat/schemas/soapbind12.xsd', 115, 4)
    __namespace._UseLocation = pyxb.utils.utility.Location('/tmp/pyxbdist.RHB65sy/PyXB-1.1.5/pyxb/bundles/wssplat/schemas/soapbind12.xsd', 115, 4)
    
    namespace = property(__namespace.value, __namespace.set, None, None)

    _AttributeWildcard = pyxb.binding.content.Wildcard(process_contents=pyxb.binding.content.Wildcard.PC_lax, namespace_constraint=(pyxb.binding.content.Wildcard.NC_not, u'http://schemas.xmlsoap.org/wsdl/soap12/'))

    _ElementMap = {
        
    }
    _AttributeMap = {
        __encodingStyle.name() : __encodingStyle,
        __part.name() : __part,
        __message.name() : __message,
        __use.name() : __use,
        __namespace.name() : __namespace
    }
Namespace.addCategoryObject('typeBinding', u'tHeaderFault', tHeaderFault)


# Complex type {http://schemas.xmlsoap.org/wsdl/soap12/}tAddress with content type EMPTY
class tAddress (tExtensibilityElementOpenAttrs):
    _TypeDefinition = None
    _ContentTypeTag = pyxb.binding.basis.complexTypeDefinition._CT_EMPTY
    _Abstract = False
    _ExpandedName = pyxb.namespace.ExpandedName(Namespace, u'tAddress')
    _DefinitionLocation = pyxb.utils.utility.Location('/tmp/pyxbdist.RHB65sy/PyXB-1.1.5/pyxb/bundles/wssplat/schemas/soapbind12.xsd', 135, 2)
    # Base type is tExtensibilityElementOpenAttrs
    
    # Attribute required inherited from {http://schemas.xmlsoap.org/wsdl/}tExtensibilityElement
    
    # Attribute location uses Python identifier location
    __location = pyxb.binding.content.AttributeUse(pyxb.namespace.ExpandedName(None, u'location'), 'location', '__httpschemas_xmlsoap_orgwsdlsoap12_tAddress_location', pyxb.binding.datatypes.anyURI, required=True)
    __location._DeclarationLocation = pyxb.utils.utility.Location('/tmp/pyxbdist.RHB65sy/PyXB-1.1.5/pyxb/bundles/wssplat/schemas/soapbind12.xsd', 138, 8)
    __location._UseLocation = pyxb.utils.utility.Location('/tmp/pyxbdist.RHB65sy/PyXB-1.1.5/pyxb/bundles/wssplat/schemas/soapbind12.xsd', 138, 8)
    
    location = property(__location.value, __location.set, None, None)

    _AttributeWildcard = pyxb.binding.content.Wildcard(process_contents=pyxb.binding.content.Wildcard.PC_lax, namespace_constraint=(pyxb.binding.content.Wildcard.NC_not, u'http://schemas.xmlsoap.org/wsdl/soap12/'))

    _ElementMap = tExtensibilityElementOpenAttrs._ElementMap.copy()
    _ElementMap.update({
        
    })
    _AttributeMap = tExtensibilityElementOpenAttrs._AttributeMap.copy()
    _AttributeMap.update({
        __location.name() : __location
    })
Namespace.addCategoryObject('typeBinding', u'tAddress', tAddress)


# Complex type {http://schemas.xmlsoap.org/wsdl/soap12/}tBinding with content type EMPTY
class tBinding (tExtensibilityElementOpenAttrs):
    _TypeDefinition = None
    _ContentTypeTag = pyxb.binding.basis.complexTypeDefinition._CT_EMPTY
    _Abstract = False
    _ExpandedName = pyxb.namespace.ExpandedName(Namespace, u'tBinding')
    _DefinitionLocation = pyxb.utils.utility.Location('/tmp/pyxbdist.RHB65sy/PyXB-1.1.5/pyxb/bundles/wssplat/schemas/soapbind12.xsd', 37, 2)
    # Base type is tExtensibilityElementOpenAttrs
    
    # Attribute required inherited from {http://schemas.xmlsoap.org/wsdl/}tExtensibilityElement
    
    # Attribute style uses Python identifier style
    __style = pyxb.binding.content.AttributeUse(pyxb.namespace.ExpandedName(None, u'style'), 'style', '__httpschemas_xmlsoap_orgwsdlsoap12_tBinding_style', tStyleChoice)
    __style._DeclarationLocation = pyxb.utils.utility.Location('/tmp/pyxbdist.RHB65sy/PyXB-1.1.5/pyxb/bundles/wssplat/schemas/soapbind12.xsd', 41, 8)
    __style._UseLocation = pyxb.utils.utility.Location('/tmp/pyxbdist.RHB65sy/PyXB-1.1.5/pyxb/bundles/wssplat/schemas/soapbind12.xsd', 41, 8)
    
    style = property(__style.value, __style.set, None, None)

    
    # Attribute transport uses Python identifier transport
    __transport = pyxb.binding.content.AttributeUse(pyxb.namespace.ExpandedName(None, u'transport'), 'transport', '__httpschemas_xmlsoap_orgwsdlsoap12_tBinding_transport', pyxb.binding.datatypes.anyURI, required=True)
    __transport._DeclarationLocation = pyxb.utils.utility.Location('/tmp/pyxbdist.RHB65sy/PyXB-1.1.5/pyxb/bundles/wssplat/schemas/soapbind12.xsd', 40, 8)
    __transport._UseLocation = pyxb.utils.utility.Location('/tmp/pyxbdist.RHB65sy/PyXB-1.1.5/pyxb/bundles/wssplat/schemas/soapbind12.xsd', 40, 8)
    
    transport = property(__transport.value, __transport.set, None, None)

    _AttributeWildcard = pyxb.binding.content.Wildcard(process_contents=pyxb.binding.content.Wildcard.PC_lax, namespace_constraint=(pyxb.binding.content.Wildcard.NC_not, u'http://schemas.xmlsoap.org/wsdl/soap12/'))

    _ElementMap = tExtensibilityElementOpenAttrs._ElementMap.copy()
    _ElementMap.update({
        
    })
    _AttributeMap = tExtensibilityElementOpenAttrs._AttributeMap.copy()
    _AttributeMap.update({
        __style.name() : __style,
        __transport.name() : __transport
    })
Namespace.addCategoryObject('typeBinding', u'tBinding', tBinding)


# Complex type {http://schemas.xmlsoap.org/wsdl/soap12/}tBody with content type EMPTY
class tBody (tExtensibilityElementOpenAttrs):
    _TypeDefinition = None
    _ContentTypeTag = pyxb.binding.basis.complexTypeDefinition._CT_EMPTY
    _Abstract = False
    _ExpandedName = pyxb.namespace.ExpandedName(Namespace, u'tBody')
    _DefinitionLocation = pyxb.utils.utility.Location('/tmp/pyxbdist.RHB65sy/PyXB-1.1.5/pyxb/bundles/wssplat/schemas/soapbind12.xsd', 74, 2)
    # Base type is tExtensibilityElementOpenAttrs
    
    # Attribute namespace uses Python identifier namespace
    __namespace = pyxb.binding.content.AttributeUse(pyxb.namespace.ExpandedName(None, u'namespace'), 'namespace', '__httpschemas_xmlsoap_orgwsdlsoap12_tBody_namespace', pyxb.binding.datatypes.anyURI)
    __namespace._DeclarationLocation = pyxb.utils.utility.Location('/tmp/pyxbdist.RHB65sy/PyXB-1.1.5/pyxb/bundles/wssplat/schemas/soapbind12.xsd', 69, 4)
    __namespace._UseLocation = pyxb.utils.utility.Location('/tmp/pyxbdist.RHB65sy/PyXB-1.1.5/pyxb/bundles/wssplat/schemas/soapbind12.xsd', 69, 4)
    
    namespace = property(__namespace.value, __namespace.set, None, None)

    
    # Attribute use uses Python identifier use
    __use = pyxb.binding.content.AttributeUse(pyxb.namespace.ExpandedName(None, u'use'), 'use', '__httpschemas_xmlsoap_orgwsdlsoap12_tBody_use', useChoice)
    __use._DeclarationLocation = pyxb.utils.utility.Location('/tmp/pyxbdist.RHB65sy/PyXB-1.1.5/pyxb/bundles/wssplat/schemas/soapbind12.xsd', 68, 4)
    __use._UseLocation = pyxb.utils.utility.Location('/tmp/pyxbdist.RHB65sy/PyXB-1.1.5/pyxb/bundles/wssplat/schemas/soapbind12.xsd', 68, 4)
    
    use = property(__use.value, __use.set, None, None)

    
    # Attribute required inherited from {http://schemas.xmlsoap.org/wsdl/}tExtensibilityElement
    
    # Attribute encodingStyle uses Python identifier encodingStyle
    __encodingStyle = pyxb.binding.content.AttributeUse(pyxb.namespace.ExpandedName(None, u'encodingStyle'), 'encodingStyle', '__httpschemas_xmlsoap_orgwsdlsoap12_tBody_encodingStyle', pyxb.binding.datatypes.anyURI)
    __encodingStyle._DeclarationLocation = pyxb.utils.utility.Location('/tmp/pyxbdist.RHB65sy/PyXB-1.1.5/pyxb/bundles/wssplat/schemas/soapbind12.xsd', 67, 4)
    __encodingStyle._UseLocation = pyxb.utils.utility.Location('/tmp/pyxbdist.RHB65sy/PyXB-1.1.5/pyxb/bundles/wssplat/schemas/soapbind12.xsd', 67, 4)
    
    encodingStyle = property(__encodingStyle.value, __encodingStyle.set, None, None)

    
    # Attribute parts uses Python identifier parts
    __parts = pyxb.binding.content.AttributeUse(pyxb.namespace.ExpandedName(None, u'parts'), 'parts', '__httpschemas_xmlsoap_orgwsdlsoap12_tBody_parts', tParts)
    __parts._DeclarationLocation = pyxb.utils.utility.Location('/tmp/pyxbdist.RHB65sy/PyXB-1.1.5/pyxb/bundles/wssplat/schemas/soapbind12.xsd', 77, 8)
    __parts._UseLocation = pyxb.utils.utility.Location('/tmp/pyxbdist.RHB65sy/PyXB-1.1.5/pyxb/bundles/wssplat/schemas/soapbind12.xsd', 77, 8)
    
    parts = property(__parts.value, __parts.set, None, None)

    _AttributeWildcard = pyxb.binding.content.Wildcard(process_contents=pyxb.binding.content.Wildcard.PC_lax, namespace_constraint=(pyxb.binding.content.Wildcard.NC_not, u'http://schemas.xmlsoap.org/wsdl/soap12/'))

    _ElementMap = tExtensibilityElementOpenAttrs._ElementMap.copy()
    _ElementMap.update({
        
    })
    _AttributeMap = tExtensibilityElementOpenAttrs._AttributeMap.copy()
    _AttributeMap.update({
        __namespace.name() : __namespace,
        __use.name() : __use,
        __encodingStyle.name() : __encodingStyle,
        __parts.name() : __parts
    })
Namespace.addCategoryObject('typeBinding', u'tBody', tBody)


# Complex type {http://schemas.xmlsoap.org/wsdl/soap12/}tFaultRes with content type EMPTY
class tFaultRes (tBody):
    _TypeDefinition = None
    _ContentTypeTag = pyxb.binding.basis.complexTypeDefinition._CT_EMPTY
    _Abstract = True
    _ExpandedName = pyxb.namespace.ExpandedName(Namespace, u'tFaultRes')
    _DefinitionLocation = pyxb.utils.utility.Location('/tmp/pyxbdist.RHB65sy/PyXB-1.1.5/pyxb/bundles/wssplat/schemas/soapbind12.xsd', 91, 2)
    # Base type is tBody
    
    # Attribute required is restricted from parent
    
    # Attribute {http://schemas.xmlsoap.org/wsdl/}required uses Python identifier required
    __required = pyxb.binding.content.AttributeUse(pyxb.namespace.ExpandedName(pyxb.namespace.NamespaceForURI(u'http://schemas.xmlsoap.org/wsdl/'), u'required'), 'required', '__httpschemas_xmlsoap_orgwsdl_tExtensibilityElement_httpschemas_xmlsoap_orgwsdlrequired', pyxb.binding.datatypes.boolean)
    __required._DeclarationLocation = pyxb.utils.utility.Location('/tmp/pyxbdist.RHB65sy/PyXB-1.1.5/pyxb/bundles/wssplat/schemas/wsdl11.xsd', 305, 2)
    __required._UseLocation = pyxb.utils.utility.Location('/tmp/pyxbdist.RHB65sy/PyXB-1.1.5/pyxb/bundles/wssplat/schemas/soapbind12.xsd', 94, 5)
    
    required = property(__required.value, __required.set, None, None)

    
    # Attribute parts is restricted from parent
    
    # Attribute parts uses Python identifier parts
    __parts = pyxb.binding.content.AttributeUse(pyxb.namespace.ExpandedName(None, u'parts'), 'parts', '__httpschemas_xmlsoap_orgwsdlsoap12_tBody_parts', tParts, prohibited=True)
    __parts._DeclarationLocation = pyxb.utils.utility.Location('/tmp/pyxbdist.RHB65sy/PyXB-1.1.5/pyxb/bundles/wssplat/schemas/soapbind12.xsd', 95, 8)
    __parts._UseLocation = pyxb.utils.utility.Location('/tmp/pyxbdist.RHB65sy/PyXB-1.1.5/pyxb/bundles/wssplat/schemas/soapbind12.xsd', 95, 8)
    
    parts = property()

    
    # Attribute encodingStyle is restricted from parent
    
    # Attribute encodingStyle uses Python identifier encodingStyle
    __encodingStyle = pyxb.binding.content.AttributeUse(pyxb.namespace.ExpandedName(None, u'encodingStyle'), 'encodingStyle', '__httpschemas_xmlsoap_orgwsdlsoap12_tBody_encodingStyle', pyxb.binding.datatypes.anyURI)
    __encodingStyle._DeclarationLocation = pyxb.utils.utility.Location('/tmp/pyxbdist.RHB65sy/PyXB-1.1.5/pyxb/bundles/wssplat/schemas/soapbind12.xsd', 67, 4)
    __encodingStyle._UseLocation = pyxb.utils.utility.Location('/tmp/pyxbdist.RHB65sy/PyXB-1.1.5/pyxb/bundles/wssplat/schemas/soapbind12.xsd', 67, 4)
    
    encodingStyle = property(__encodingStyle.value, __encodingStyle.set, None, None)

    
    # Attribute namespace is restricted from parent
    
    # Attribute namespace uses Python identifier namespace
    __namespace = pyxb.binding.content.AttributeUse(pyxb.namespace.ExpandedName(None, u'namespace'), 'namespace', '__httpschemas_xmlsoap_orgwsdlsoap12_tBody_namespace', pyxb.binding.datatypes.anyURI)
    __namespace._DeclarationLocation = pyxb.utils.utility.Location('/tmp/pyxbdist.RHB65sy/PyXB-1.1.5/pyxb/bundles/wssplat/schemas/soapbind12.xsd', 69, 4)
    __namespace._UseLocation = pyxb.utils.utility.Location('/tmp/pyxbdist.RHB65sy/PyXB-1.1.5/pyxb/bundles/wssplat/schemas/soapbind12.xsd', 69, 4)
    
    namespace = property(__namespace.value, __namespace.set, None, None)

    
    # Attribute use is restricted from parent
    
    # Attribute use uses Python identifier use
    __use = pyxb.binding.content.AttributeUse(pyxb.namespace.ExpandedName(None, u'use'), 'use', '__httpschemas_xmlsoap_orgwsdlsoap12_tBody_use', useChoice)
    __use._DeclarationLocation = pyxb.utils.utility.Location('/tmp/pyxbdist.RHB65sy/PyXB-1.1.5/pyxb/bundles/wssplat/schemas/soapbind12.xsd', 68, 4)
    __use._UseLocation = pyxb.utils.utility.Location('/tmp/pyxbdist.RHB65sy/PyXB-1.1.5/pyxb/bundles/wssplat/schemas/soapbind12.xsd', 68, 4)
    
    use = property(__use.value, __use.set, None, None)


    _ElementMap = tBody._ElementMap.copy()
    _ElementMap.update({
        
    })
    _AttributeMap = tBody._AttributeMap.copy()
    _AttributeMap.update({
        __required.name() : __required,
        __parts.name() : __parts,
        __encodingStyle.name() : __encodingStyle,
        __namespace.name() : __namespace,
        __use.name() : __use
    })
Namespace.addCategoryObject('typeBinding', u'tFaultRes', tFaultRes)


# Complex type {http://schemas.xmlsoap.org/wsdl/soap12/}tFault with content type EMPTY
class tFault (tFaultRes):
    _TypeDefinition = None
    _ContentTypeTag = pyxb.binding.basis.complexTypeDefinition._CT_EMPTY
    _Abstract = False
    _ExpandedName = pyxb.namespace.ExpandedName(Namespace, u'tFault')
    _DefinitionLocation = pyxb.utils.utility.Location('/tmp/pyxbdist.RHB65sy/PyXB-1.1.5/pyxb/bundles/wssplat/schemas/soapbind12.xsd', 100, 2)
    # Base type is tFaultRes
    
    # Attribute encodingStyle_ inherited from {http://schemas.xmlsoap.org/wsdl/soap12/}tFaultRes
    
    # Attribute required_ inherited from {http://schemas.xmlsoap.org/wsdl/soap12/}tFaultRes
    
    # Attribute namespace_ inherited from {http://schemas.xmlsoap.org/wsdl/soap12/}tFaultRes
    
    # Attribute parts_ inherited from {http://schemas.xmlsoap.org/wsdl/soap12/}tFaultRes
    
    # Attribute use_ inherited from {http://schemas.xmlsoap.org/wsdl/soap12/}tFaultRes
    
    # Attribute name uses Python identifier name
    __name = pyxb.binding.content.AttributeUse(pyxb.namespace.ExpandedName(None, u'name'), 'name', '__httpschemas_xmlsoap_orgwsdlsoap12_tFault_name', pyxb.binding.datatypes.NCName, required=True)
    __name._DeclarationLocation = pyxb.utils.utility.Location('/tmp/pyxbdist.RHB65sy/PyXB-1.1.5/pyxb/bundles/wssplat/schemas/soapbind12.xsd', 103, 8)
    __name._UseLocation = pyxb.utils.utility.Location('/tmp/pyxbdist.RHB65sy/PyXB-1.1.5/pyxb/bundles/wssplat/schemas/soapbind12.xsd', 103, 8)
    
    name = property(__name.value, __name.set, None, None)


    _ElementMap = tFaultRes._ElementMap.copy()
    _ElementMap.update({
        
    })
    _AttributeMap = tFaultRes._AttributeMap.copy()
    _AttributeMap.update({
        __name.name() : __name
    })
Namespace.addCategoryObject('typeBinding', u'tFault', tFault)


# Complex type {http://schemas.xmlsoap.org/wsdl/soap12/}tOperation with content type EMPTY
class tOperation (tExtensibilityElementOpenAttrs):
    _TypeDefinition = None
    _ContentTypeTag = pyxb.binding.basis.complexTypeDefinition._CT_EMPTY
    _Abstract = False
    _ExpandedName = pyxb.namespace.ExpandedName(Namespace, u'tOperation')
    _DefinitionLocation = pyxb.utils.utility.Location('/tmp/pyxbdist.RHB65sy/PyXB-1.1.5/pyxb/bundles/wssplat/schemas/soapbind12.xsd', 54, 2)
    # Base type is tExtensibilityElementOpenAttrs
    
    # Attribute required inherited from {http://schemas.xmlsoap.org/wsdl/}tExtensibilityElement
    
    # Attribute soapAction uses Python identifier soapAction
    __soapAction = pyxb.binding.content.AttributeUse(pyxb.namespace.ExpandedName(None, u'soapAction'), 'soapAction', '__httpschemas_xmlsoap_orgwsdlsoap12_tOperation_soapAction', pyxb.binding.datatypes.anyURI)
    __soapAction._DeclarationLocation = pyxb.utils.utility.Location('/tmp/pyxbdist.RHB65sy/PyXB-1.1.5/pyxb/bundles/wssplat/schemas/soapbind12.xsd', 57, 8)
    __soapAction._UseLocation = pyxb.utils.utility.Location('/tmp/pyxbdist.RHB65sy/PyXB-1.1.5/pyxb/bundles/wssplat/schemas/soapbind12.xsd', 57, 8)
    
    soapAction = property(__soapAction.value, __soapAction.set, None, None)

    
    # Attribute soapActionRequired uses Python identifier soapActionRequired
    __soapActionRequired = pyxb.binding.content.AttributeUse(pyxb.namespace.ExpandedName(None, u'soapActionRequired'), 'soapActionRequired', '__httpschemas_xmlsoap_orgwsdlsoap12_tOperation_soapActionRequired', pyxb.binding.datatypes.boolean)
    __soapActionRequired._DeclarationLocation = pyxb.utils.utility.Location('/tmp/pyxbdist.RHB65sy/PyXB-1.1.5/pyxb/bundles/wssplat/schemas/soapbind12.xsd', 58, 8)
    __soapActionRequired._UseLocation = pyxb.utils.utility.Location('/tmp/pyxbdist.RHB65sy/PyXB-1.1.5/pyxb/bundles/wssplat/schemas/soapbind12.xsd', 58, 8)
    
    soapActionRequired = property(__soapActionRequired.value, __soapActionRequired.set, None, None)

    
    # Attribute style uses Python identifier style
    __style = pyxb.binding.content.AttributeUse(pyxb.namespace.ExpandedName(None, u'style'), 'style', '__httpschemas_xmlsoap_orgwsdlsoap12_tOperation_style', tStyleChoice)
    __style._DeclarationLocation = pyxb.utils.utility.Location('/tmp/pyxbdist.RHB65sy/PyXB-1.1.5/pyxb/bundles/wssplat/schemas/soapbind12.xsd', 59, 8)
    __style._UseLocation = pyxb.utils.utility.Location('/tmp/pyxbdist.RHB65sy/PyXB-1.1.5/pyxb/bundles/wssplat/schemas/soapbind12.xsd', 59, 8)
    
    style = property(__style.value, __style.set, None, None)

    _AttributeWildcard = pyxb.binding.content.Wildcard(process_contents=pyxb.binding.content.Wildcard.PC_lax, namespace_constraint=(pyxb.binding.content.Wildcard.NC_not, u'http://schemas.xmlsoap.org/wsdl/soap12/'))

    _ElementMap = tExtensibilityElementOpenAttrs._ElementMap.copy()
    _ElementMap.update({
        
    })
    _AttributeMap = tExtensibilityElementOpenAttrs._AttributeMap.copy()
    _AttributeMap.update({
        __soapAction.name() : __soapAction,
        __soapActionRequired.name() : __soapActionRequired,
        __style.name() : __style
    })
Namespace.addCategoryObject('typeBinding', u'tOperation', tOperation)


header = pyxb.binding.basis.element(pyxb.namespace.ExpandedName(Namespace, u'header'), tHeader)
Namespace.addCategoryObject('elementBinding', header.name().localName(), header)

headerfault = pyxb.binding.basis.element(pyxb.namespace.ExpandedName(Namespace, u'headerfault'), tHeaderFault)
Namespace.addCategoryObject('elementBinding', headerfault.name().localName(), headerfault)

address = pyxb.binding.basis.element(pyxb.namespace.ExpandedName(Namespace, u'address'), tAddress)
Namespace.addCategoryObject('elementBinding', address.name().localName(), address)

binding = pyxb.binding.basis.element(pyxb.namespace.ExpandedName(Namespace, u'binding'), tBinding)
Namespace.addCategoryObject('elementBinding', binding.name().localName(), binding)

fault = pyxb.binding.basis.element(pyxb.namespace.ExpandedName(Namespace, u'fault'), tFault)
Namespace.addCategoryObject('elementBinding', fault.name().localName(), fault)

body = pyxb.binding.basis.element(pyxb.namespace.ExpandedName(Namespace, u'body'), tBody)
Namespace.addCategoryObject('elementBinding', body.name().localName(), body)

operation = pyxb.binding.basis.element(pyxb.namespace.ExpandedName(Namespace, u'operation'), tOperation)
Namespace.addCategoryObject('elementBinding', operation.name().localName(), operation)



tHeader._AddElement(pyxb.binding.basis.element(pyxb.namespace.ExpandedName(Namespace, u'headerfault'), tHeaderFault, scope=tHeader))
tHeader._GroupModel = pyxb.binding.content.GroupSequence(
    pyxb.binding.content.ParticleModel(tHeader._UseForTag(pyxb.namespace.ExpandedName(Namespace, u'headerfault')), min_occurs=0L, max_occurs=None)
    )
tHeader._ContentModel = pyxb.binding.content.ParticleModel(tHeader._GroupModel, min_occurs=1, max_occurs=1)
