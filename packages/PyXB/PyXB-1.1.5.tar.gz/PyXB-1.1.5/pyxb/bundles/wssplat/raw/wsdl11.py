# ./pyxb/bundles/wssplat/raw/wsdl11.py
# -*- coding: utf-8 -*-
# PyXB bindings for NM:d363f64a147eb09d66a961a815c9d842964c1c79
# Generated 2012-11-01 15:13:33.132842 by PyXB version 1.1.5
# Namespace http://schemas.xmlsoap.org/wsdl/

import pyxb
import pyxb.binding
import pyxb.binding.saxer
import StringIO
import pyxb.utils.utility
import pyxb.utils.domutils
import sys

# Unique identifier for bindings created at the same time
_GenerationUID = pyxb.utils.utility.UniqueIdentifier('urn:uuid:9c3755fa-2460-11e2-a751-c8600024e903')

# Import bindings for namespaces imported into schema
import pyxb.binding.datatypes

Namespace = pyxb.namespace.NamespaceForURI(u'http://schemas.xmlsoap.org/wsdl/', create_if_missing=True)
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


# Complex type {http://schemas.xmlsoap.org/wsdl/}tDocumented with content type ELEMENT_ONLY
class tDocumented (pyxb.binding.basis.complexTypeDefinition):
    _TypeDefinition = None
    _ContentTypeTag = pyxb.binding.basis.complexTypeDefinition._CT_ELEMENT_ONLY
    _Abstract = False
    _ExpandedName = pyxb.namespace.ExpandedName(Namespace, u'tDocumented')
    _DefinitionLocation = pyxb.utils.utility.Location('/tmp/pyxbdist.RHB65sy/PyXB-1.1.5/pyxb/bundles/wssplat/schemas/wsdl11.xsd', 43, 2)
    # Base type is pyxb.binding.datatypes.anyType
    
    # Element {http://schemas.xmlsoap.org/wsdl/}documentation uses Python identifier documentation
    __documentation = pyxb.binding.content.ElementUse(pyxb.namespace.ExpandedName(Namespace, u'documentation'), 'documentation', '__httpschemas_xmlsoap_orgwsdl_tDocumented_httpschemas_xmlsoap_orgwsdldocumentation', False)
    __documentation._DeclarationLocation = pyxb.utils.utility.Location('/tmp/pyxbdist.RHB65sy/PyXB-1.1.5/pyxb/bundles/wssplat/schemas/wsdl11.xsd', 50, 6)
    __documentation._UseLocation = pyxb.utils.utility.Location('/tmp/pyxbdist.RHB65sy/PyXB-1.1.5/pyxb/bundles/wssplat/schemas/wsdl11.xsd', 49, 4)

    
    documentation = property(__documentation.value, __documentation.set, None, None)


    _ElementMap = {
        __documentation.name() : __documentation
    }
    _AttributeMap = {
        
    }
Namespace.addCategoryObject('typeBinding', u'tDocumented', tDocumented)


# Complex type {http://schemas.xmlsoap.org/wsdl/}tExtensibleDocumented with content type ELEMENT_ONLY
class tExtensibleDocumented (tDocumented):
    _TypeDefinition = None
    _ContentTypeTag = pyxb.binding.basis.complexTypeDefinition._CT_ELEMENT_ONLY
    _Abstract = True
    _ExpandedName = pyxb.namespace.ExpandedName(Namespace, u'tExtensibleDocumented')
    _DefinitionLocation = pyxb.utils.utility.Location('/tmp/pyxbdist.RHB65sy/PyXB-1.1.5/pyxb/bundles/wssplat/schemas/wsdl11.xsd', 67, 2)
    # Base type is tDocumented
    
    # Element documentation ({http://schemas.xmlsoap.org/wsdl/}documentation) inherited from {http://schemas.xmlsoap.org/wsdl/}tDocumented
    _HasWildcardElement = True

    _ElementMap = tDocumented._ElementMap.copy()
    _ElementMap.update({
        
    })
    _AttributeMap = tDocumented._AttributeMap.copy()
    _AttributeMap.update({
        
    })
Namespace.addCategoryObject('typeBinding', u'tExtensibleDocumented', tExtensibleDocumented)


# Complex type {http://schemas.xmlsoap.org/wsdl/}tBindingOperation with content type ELEMENT_ONLY
class tBindingOperation (tExtensibleDocumented):
    _TypeDefinition = None
    _ContentTypeTag = pyxb.binding.basis.complexTypeDefinition._CT_ELEMENT_ONLY
    _Abstract = False
    _ExpandedName = pyxb.namespace.ExpandedName(Namespace, u'tBindingOperation')
    _DefinitionLocation = pyxb.utils.utility.Location('/tmp/pyxbdist.RHB65sy/PyXB-1.1.5/pyxb/bundles/wssplat/schemas/wsdl11.xsd', 271, 2)
    # Base type is tExtensibleDocumented
    
    # Element documentation ({http://schemas.xmlsoap.org/wsdl/}documentation) inherited from {http://schemas.xmlsoap.org/wsdl/}tDocumented
    
    # Element {http://schemas.xmlsoap.org/wsdl/}fault uses Python identifier fault
    __fault = pyxb.binding.content.ElementUse(pyxb.namespace.ExpandedName(Namespace, u'fault'), 'fault', '__httpschemas_xmlsoap_orgwsdl_tBindingOperation_httpschemas_xmlsoap_orgwsdlfault', True)
    __fault._DeclarationLocation = pyxb.utils.utility.Location('/tmp/pyxbdist.RHB65sy/PyXB-1.1.5/pyxb/bundles/wssplat/schemas/wsdl11.xsd', 277, 10)
    __fault._UseLocation = None

    
    fault = property(__fault.value, __fault.set, None, None)

    
    # Element {http://schemas.xmlsoap.org/wsdl/}output uses Python identifier output
    __output = pyxb.binding.content.ElementUse(pyxb.namespace.ExpandedName(Namespace, u'output'), 'output', '__httpschemas_xmlsoap_orgwsdl_tBindingOperation_httpschemas_xmlsoap_orgwsdloutput', False)
    __output._DeclarationLocation = pyxb.utils.utility.Location('/tmp/pyxbdist.RHB65sy/PyXB-1.1.5/pyxb/bundles/wssplat/schemas/wsdl11.xsd', 276, 10)
    __output._UseLocation = None

    
    output = property(__output.value, __output.set, None, None)

    
    # Element {http://schemas.xmlsoap.org/wsdl/}input uses Python identifier input
    __input = pyxb.binding.content.ElementUse(pyxb.namespace.ExpandedName(Namespace, u'input'), 'input', '__httpschemas_xmlsoap_orgwsdl_tBindingOperation_httpschemas_xmlsoap_orgwsdlinput', False)
    __input._DeclarationLocation = pyxb.utils.utility.Location('/tmp/pyxbdist.RHB65sy/PyXB-1.1.5/pyxb/bundles/wssplat/schemas/wsdl11.xsd', 275, 10)
    __input._UseLocation = None

    
    input = property(__input.value, __input.set, None, None)

    
    # Attribute name uses Python identifier name
    __name = pyxb.binding.content.AttributeUse(pyxb.namespace.ExpandedName(None, u'name'), 'name', '__httpschemas_xmlsoap_orgwsdl_tBindingOperation_name', pyxb.binding.datatypes.NCName, required=True)
    __name._DeclarationLocation = pyxb.utils.utility.Location('/tmp/pyxbdist.RHB65sy/PyXB-1.1.5/pyxb/bundles/wssplat/schemas/wsdl11.xsd', 279, 8)
    __name._UseLocation = pyxb.utils.utility.Location('/tmp/pyxbdist.RHB65sy/PyXB-1.1.5/pyxb/bundles/wssplat/schemas/wsdl11.xsd', 279, 8)
    
    name = property(__name.value, __name.set, None, None)

    _HasWildcardElement = True

    _ElementMap = tExtensibleDocumented._ElementMap.copy()
    _ElementMap.update({
        __fault.name() : __fault,
        __output.name() : __output,
        __input.name() : __input
    })
    _AttributeMap = tExtensibleDocumented._AttributeMap.copy()
    _AttributeMap.update({
        __name.name() : __name
    })
Namespace.addCategoryObject('typeBinding', u'tBindingOperation', tBindingOperation)


# Complex type {http://schemas.xmlsoap.org/wsdl/}tExtensibleAttributesDocumented with content type ELEMENT_ONLY
class tExtensibleAttributesDocumented (tDocumented):
    _TypeDefinition = None
    _ContentTypeTag = pyxb.binding.basis.complexTypeDefinition._CT_ELEMENT_ONLY
    _Abstract = True
    _ExpandedName = pyxb.namespace.ExpandedName(Namespace, u'tExtensibleAttributesDocumented')
    _DefinitionLocation = pyxb.utils.utility.Location('/tmp/pyxbdist.RHB65sy/PyXB-1.1.5/pyxb/bundles/wssplat/schemas/wsdl11.xsd', 54, 2)
    # Base type is tDocumented
    
    # Element documentation ({http://schemas.xmlsoap.org/wsdl/}documentation) inherited from {http://schemas.xmlsoap.org/wsdl/}tDocumented
    _AttributeWildcard = pyxb.binding.content.Wildcard(process_contents=pyxb.binding.content.Wildcard.PC_lax, namespace_constraint=(pyxb.binding.content.Wildcard.NC_not, u'http://schemas.xmlsoap.org/wsdl/'))

    _ElementMap = tDocumented._ElementMap.copy()
    _ElementMap.update({
        
    })
    _AttributeMap = tDocumented._AttributeMap.copy()
    _AttributeMap.update({
        
    })
Namespace.addCategoryObject('typeBinding', u'tExtensibleAttributesDocumented', tExtensibleAttributesDocumented)


# Complex type {http://schemas.xmlsoap.org/wsdl/}tParam with content type ELEMENT_ONLY
class tParam (tExtensibleAttributesDocumented):
    _TypeDefinition = None
    _ContentTypeTag = pyxb.binding.basis.complexTypeDefinition._CT_ELEMENT_ONLY
    _Abstract = False
    _ExpandedName = pyxb.namespace.ExpandedName(Namespace, u'tParam')
    _DefinitionLocation = pyxb.utils.utility.Location('/tmp/pyxbdist.RHB65sy/PyXB-1.1.5/pyxb/bundles/wssplat/schemas/wsdl11.xsd', 225, 2)
    # Base type is tExtensibleAttributesDocumented
    
    # Element documentation ({http://schemas.xmlsoap.org/wsdl/}documentation) inherited from {http://schemas.xmlsoap.org/wsdl/}tDocumented
    
    # Attribute message uses Python identifier message
    __message = pyxb.binding.content.AttributeUse(pyxb.namespace.ExpandedName(None, u'message'), 'message', '__httpschemas_xmlsoap_orgwsdl_tParam_message', pyxb.binding.datatypes.QName, required=True)
    __message._DeclarationLocation = pyxb.utils.utility.Location('/tmp/pyxbdist.RHB65sy/PyXB-1.1.5/pyxb/bundles/wssplat/schemas/wsdl11.xsd', 229, 8)
    __message._UseLocation = pyxb.utils.utility.Location('/tmp/pyxbdist.RHB65sy/PyXB-1.1.5/pyxb/bundles/wssplat/schemas/wsdl11.xsd', 229, 8)
    
    message = property(__message.value, __message.set, None, None)

    
    # Attribute name uses Python identifier name
    __name = pyxb.binding.content.AttributeUse(pyxb.namespace.ExpandedName(None, u'name'), 'name', '__httpschemas_xmlsoap_orgwsdl_tParam_name', pyxb.binding.datatypes.NCName)
    __name._DeclarationLocation = pyxb.utils.utility.Location('/tmp/pyxbdist.RHB65sy/PyXB-1.1.5/pyxb/bundles/wssplat/schemas/wsdl11.xsd', 228, 8)
    __name._UseLocation = pyxb.utils.utility.Location('/tmp/pyxbdist.RHB65sy/PyXB-1.1.5/pyxb/bundles/wssplat/schemas/wsdl11.xsd', 228, 8)
    
    name = property(__name.value, __name.set, None, None)

    _AttributeWildcard = pyxb.binding.content.Wildcard(process_contents=pyxb.binding.content.Wildcard.PC_lax, namespace_constraint=(pyxb.binding.content.Wildcard.NC_not, u'http://schemas.xmlsoap.org/wsdl/'))

    _ElementMap = tExtensibleAttributesDocumented._ElementMap.copy()
    _ElementMap.update({
        
    })
    _AttributeMap = tExtensibleAttributesDocumented._AttributeMap.copy()
    _AttributeMap.update({
        __message.name() : __message,
        __name.name() : __name
    })
Namespace.addCategoryObject('typeBinding', u'tParam', tParam)


# Complex type {http://schemas.xmlsoap.org/wsdl/}tMessage with content type ELEMENT_ONLY
class tMessage (tExtensibleDocumented):
    _TypeDefinition = None
    _ContentTypeTag = pyxb.binding.basis.complexTypeDefinition._CT_ELEMENT_ONLY
    _Abstract = False
    _ExpandedName = pyxb.namespace.ExpandedName(Namespace, u'tMessage')
    _DefinitionLocation = pyxb.utils.utility.Location('/tmp/pyxbdist.RHB65sy/PyXB-1.1.5/pyxb/bundles/wssplat/schemas/wsdl11.xsd', 158, 2)
    # Base type is tExtensibleDocumented
    
    # Element {http://schemas.xmlsoap.org/wsdl/}part uses Python identifier part
    __part = pyxb.binding.content.ElementUse(pyxb.namespace.ExpandedName(Namespace, u'part'), 'part', '__httpschemas_xmlsoap_orgwsdl_tMessage_httpschemas_xmlsoap_orgwsdlpart', True)
    __part._DeclarationLocation = pyxb.utils.utility.Location('/tmp/pyxbdist.RHB65sy/PyXB-1.1.5/pyxb/bundles/wssplat/schemas/wsdl11.xsd', 162, 10)
    __part._UseLocation = None

    
    part = property(__part.value, __part.set, None, None)

    
    # Element documentation ({http://schemas.xmlsoap.org/wsdl/}documentation) inherited from {http://schemas.xmlsoap.org/wsdl/}tDocumented
    
    # Attribute name uses Python identifier name
    __name = pyxb.binding.content.AttributeUse(pyxb.namespace.ExpandedName(None, u'name'), 'name', '__httpschemas_xmlsoap_orgwsdl_tMessage_name', pyxb.binding.datatypes.NCName, required=True)
    __name._DeclarationLocation = pyxb.utils.utility.Location('/tmp/pyxbdist.RHB65sy/PyXB-1.1.5/pyxb/bundles/wssplat/schemas/wsdl11.xsd', 164, 8)
    __name._UseLocation = pyxb.utils.utility.Location('/tmp/pyxbdist.RHB65sy/PyXB-1.1.5/pyxb/bundles/wssplat/schemas/wsdl11.xsd', 164, 8)
    
    name = property(__name.value, __name.set, None, None)

    _HasWildcardElement = True

    _ElementMap = tExtensibleDocumented._ElementMap.copy()
    _ElementMap.update({
        __part.name() : __part
    })
    _AttributeMap = tExtensibleDocumented._AttributeMap.copy()
    _AttributeMap.update({
        __name.name() : __name
    })
Namespace.addCategoryObject('typeBinding', u'tMessage', tMessage)


# Complex type {http://schemas.xmlsoap.org/wsdl/}tFault with content type ELEMENT_ONLY
class tFault (tExtensibleAttributesDocumented):
    _TypeDefinition = None
    _ContentTypeTag = pyxb.binding.basis.complexTypeDefinition._CT_ELEMENT_ONLY
    _Abstract = False
    _ExpandedName = pyxb.namespace.ExpandedName(Namespace, u'tFault')
    _DefinitionLocation = pyxb.utils.utility.Location('/tmp/pyxbdist.RHB65sy/PyXB-1.1.5/pyxb/bundles/wssplat/schemas/wsdl11.xsd', 234, 2)
    # Base type is tExtensibleAttributesDocumented
    
    # Element documentation ({http://schemas.xmlsoap.org/wsdl/}documentation) inherited from {http://schemas.xmlsoap.org/wsdl/}tDocumented
    
    # Attribute message uses Python identifier message
    __message = pyxb.binding.content.AttributeUse(pyxb.namespace.ExpandedName(None, u'message'), 'message', '__httpschemas_xmlsoap_orgwsdl_tFault_message', pyxb.binding.datatypes.QName, required=True)
    __message._DeclarationLocation = pyxb.utils.utility.Location('/tmp/pyxbdist.RHB65sy/PyXB-1.1.5/pyxb/bundles/wssplat/schemas/wsdl11.xsd', 238, 8)
    __message._UseLocation = pyxb.utils.utility.Location('/tmp/pyxbdist.RHB65sy/PyXB-1.1.5/pyxb/bundles/wssplat/schemas/wsdl11.xsd', 238, 8)
    
    message = property(__message.value, __message.set, None, None)

    
    # Attribute name uses Python identifier name
    __name = pyxb.binding.content.AttributeUse(pyxb.namespace.ExpandedName(None, u'name'), 'name', '__httpschemas_xmlsoap_orgwsdl_tFault_name', pyxb.binding.datatypes.NCName, required=True)
    __name._DeclarationLocation = pyxb.utils.utility.Location('/tmp/pyxbdist.RHB65sy/PyXB-1.1.5/pyxb/bundles/wssplat/schemas/wsdl11.xsd', 237, 8)
    __name._UseLocation = pyxb.utils.utility.Location('/tmp/pyxbdist.RHB65sy/PyXB-1.1.5/pyxb/bundles/wssplat/schemas/wsdl11.xsd', 237, 8)
    
    name = property(__name.value, __name.set, None, None)

    _AttributeWildcard = pyxb.binding.content.Wildcard(process_contents=pyxb.binding.content.Wildcard.PC_lax, namespace_constraint=(pyxb.binding.content.Wildcard.NC_not, u'http://schemas.xmlsoap.org/wsdl/'))

    _ElementMap = tExtensibleAttributesDocumented._ElementMap.copy()
    _ElementMap.update({
        
    })
    _AttributeMap = tExtensibleAttributesDocumented._AttributeMap.copy()
    _AttributeMap.update({
        __message.name() : __message,
        __name.name() : __name
    })
Namespace.addCategoryObject('typeBinding', u'tFault', tFault)


# Complex type {http://schemas.xmlsoap.org/wsdl/}tPortType with content type ELEMENT_ONLY
class tPortType (tExtensibleAttributesDocumented):
    _TypeDefinition = None
    _ContentTypeTag = pyxb.binding.basis.complexTypeDefinition._CT_ELEMENT_ONLY
    _Abstract = False
    _ExpandedName = pyxb.namespace.ExpandedName(Namespace, u'tPortType')
    _DefinitionLocation = pyxb.utils.utility.Location('/tmp/pyxbdist.RHB65sy/PyXB-1.1.5/pyxb/bundles/wssplat/schemas/wsdl11.xsd', 179, 2)
    # Base type is tExtensibleAttributesDocumented
    
    # Element {http://schemas.xmlsoap.org/wsdl/}operation uses Python identifier operation
    __operation = pyxb.binding.content.ElementUse(pyxb.namespace.ExpandedName(Namespace, u'operation'), 'operation', '__httpschemas_xmlsoap_orgwsdl_tPortType_httpschemas_xmlsoap_orgwsdloperation', True)
    __operation._DeclarationLocation = pyxb.utils.utility.Location('/tmp/pyxbdist.RHB65sy/PyXB-1.1.5/pyxb/bundles/wssplat/schemas/wsdl11.xsd', 183, 10)
    __operation._UseLocation = None

    
    operation = property(__operation.value, __operation.set, None, None)

    
    # Element documentation ({http://schemas.xmlsoap.org/wsdl/}documentation) inherited from {http://schemas.xmlsoap.org/wsdl/}tDocumented
    
    # Attribute name uses Python identifier name
    __name = pyxb.binding.content.AttributeUse(pyxb.namespace.ExpandedName(None, u'name'), 'name', '__httpschemas_xmlsoap_orgwsdl_tPortType_name', pyxb.binding.datatypes.NCName, required=True)
    __name._DeclarationLocation = pyxb.utils.utility.Location('/tmp/pyxbdist.RHB65sy/PyXB-1.1.5/pyxb/bundles/wssplat/schemas/wsdl11.xsd', 185, 8)
    __name._UseLocation = pyxb.utils.utility.Location('/tmp/pyxbdist.RHB65sy/PyXB-1.1.5/pyxb/bundles/wssplat/schemas/wsdl11.xsd', 185, 8)
    
    name = property(__name.value, __name.set, None, None)

    _AttributeWildcard = pyxb.binding.content.Wildcard(process_contents=pyxb.binding.content.Wildcard.PC_lax, namespace_constraint=(pyxb.binding.content.Wildcard.NC_not, u'http://schemas.xmlsoap.org/wsdl/'))

    _ElementMap = tExtensibleAttributesDocumented._ElementMap.copy()
    _ElementMap.update({
        __operation.name() : __operation
    })
    _AttributeMap = tExtensibleAttributesDocumented._AttributeMap.copy()
    _AttributeMap.update({
        __name.name() : __name
    })
Namespace.addCategoryObject('typeBinding', u'tPortType', tPortType)


# Complex type {http://schemas.xmlsoap.org/wsdl/}tBinding with content type ELEMENT_ONLY
class tBinding (tExtensibleDocumented):
    _TypeDefinition = None
    _ContentTypeTag = pyxb.binding.basis.complexTypeDefinition._CT_ELEMENT_ONLY
    _Abstract = False
    _ExpandedName = pyxb.namespace.ExpandedName(Namespace, u'tBinding')
    _DefinitionLocation = pyxb.utils.utility.Location('/tmp/pyxbdist.RHB65sy/PyXB-1.1.5/pyxb/bundles/wssplat/schemas/wsdl11.xsd', 243, 2)
    # Base type is tExtensibleDocumented
    
    # Element {http://schemas.xmlsoap.org/wsdl/}operation uses Python identifier operation
    __operation = pyxb.binding.content.ElementUse(pyxb.namespace.ExpandedName(Namespace, u'operation'), 'operation', '__httpschemas_xmlsoap_orgwsdl_tBinding_httpschemas_xmlsoap_orgwsdloperation', True)
    __operation._DeclarationLocation = pyxb.utils.utility.Location('/tmp/pyxbdist.RHB65sy/PyXB-1.1.5/pyxb/bundles/wssplat/schemas/wsdl11.xsd', 247, 10)
    __operation._UseLocation = None

    
    operation = property(__operation.value, __operation.set, None, None)

    
    # Element documentation ({http://schemas.xmlsoap.org/wsdl/}documentation) inherited from {http://schemas.xmlsoap.org/wsdl/}tDocumented
    
    # Attribute type uses Python identifier type
    __type = pyxb.binding.content.AttributeUse(pyxb.namespace.ExpandedName(None, u'type'), 'type', '__httpschemas_xmlsoap_orgwsdl_tBinding_type', pyxb.binding.datatypes.QName, required=True)
    __type._DeclarationLocation = pyxb.utils.utility.Location('/tmp/pyxbdist.RHB65sy/PyXB-1.1.5/pyxb/bundles/wssplat/schemas/wsdl11.xsd', 250, 8)
    __type._UseLocation = pyxb.utils.utility.Location('/tmp/pyxbdist.RHB65sy/PyXB-1.1.5/pyxb/bundles/wssplat/schemas/wsdl11.xsd', 250, 8)
    
    type = property(__type.value, __type.set, None, None)

    
    # Attribute name uses Python identifier name
    __name = pyxb.binding.content.AttributeUse(pyxb.namespace.ExpandedName(None, u'name'), 'name', '__httpschemas_xmlsoap_orgwsdl_tBinding_name', pyxb.binding.datatypes.NCName, required=True)
    __name._DeclarationLocation = pyxb.utils.utility.Location('/tmp/pyxbdist.RHB65sy/PyXB-1.1.5/pyxb/bundles/wssplat/schemas/wsdl11.xsd', 249, 8)
    __name._UseLocation = pyxb.utils.utility.Location('/tmp/pyxbdist.RHB65sy/PyXB-1.1.5/pyxb/bundles/wssplat/schemas/wsdl11.xsd', 249, 8)
    
    name = property(__name.value, __name.set, None, None)

    _HasWildcardElement = True

    _ElementMap = tExtensibleDocumented._ElementMap.copy()
    _ElementMap.update({
        __operation.name() : __operation
    })
    _AttributeMap = tExtensibleDocumented._AttributeMap.copy()
    _AttributeMap.update({
        __type.name() : __type,
        __name.name() : __name
    })
Namespace.addCategoryObject('typeBinding', u'tBinding', tBinding)


# Complex type {http://schemas.xmlsoap.org/wsdl/}tService with content type ELEMENT_ONLY
class tService (tExtensibleDocumented):
    _TypeDefinition = None
    _ContentTypeTag = pyxb.binding.basis.complexTypeDefinition._CT_ELEMENT_ONLY
    _Abstract = False
    _ExpandedName = pyxb.namespace.ExpandedName(Namespace, u'tService')
    _DefinitionLocation = pyxb.utils.utility.Location('/tmp/pyxbdist.RHB65sy/PyXB-1.1.5/pyxb/bundles/wssplat/schemas/wsdl11.xsd', 284, 2)
    # Base type is tExtensibleDocumented
    
    # Element {http://schemas.xmlsoap.org/wsdl/}port uses Python identifier port
    __port = pyxb.binding.content.ElementUse(pyxb.namespace.ExpandedName(Namespace, u'port'), 'port', '__httpschemas_xmlsoap_orgwsdl_tService_httpschemas_xmlsoap_orgwsdlport', True)
    __port._DeclarationLocation = pyxb.utils.utility.Location('/tmp/pyxbdist.RHB65sy/PyXB-1.1.5/pyxb/bundles/wssplat/schemas/wsdl11.xsd', 288, 10)
    __port._UseLocation = None

    
    port = property(__port.value, __port.set, None, None)

    
    # Element documentation ({http://schemas.xmlsoap.org/wsdl/}documentation) inherited from {http://schemas.xmlsoap.org/wsdl/}tDocumented
    
    # Attribute name uses Python identifier name
    __name = pyxb.binding.content.AttributeUse(pyxb.namespace.ExpandedName(None, u'name'), 'name', '__httpschemas_xmlsoap_orgwsdl_tService_name', pyxb.binding.datatypes.NCName, required=True)
    __name._DeclarationLocation = pyxb.utils.utility.Location('/tmp/pyxbdist.RHB65sy/PyXB-1.1.5/pyxb/bundles/wssplat/schemas/wsdl11.xsd', 290, 8)
    __name._UseLocation = pyxb.utils.utility.Location('/tmp/pyxbdist.RHB65sy/PyXB-1.1.5/pyxb/bundles/wssplat/schemas/wsdl11.xsd', 290, 8)
    
    name = property(__name.value, __name.set, None, None)

    _HasWildcardElement = True

    _ElementMap = tExtensibleDocumented._ElementMap.copy()
    _ElementMap.update({
        __port.name() : __port
    })
    _AttributeMap = tExtensibleDocumented._AttributeMap.copy()
    _AttributeMap.update({
        __name.name() : __name
    })
Namespace.addCategoryObject('typeBinding', u'tService', tService)


# Complex type {http://schemas.xmlsoap.org/wsdl/}tOperation with content type ELEMENT_ONLY
class tOperation (tExtensibleDocumented):
    _TypeDefinition = None
    _ContentTypeTag = pyxb.binding.basis.complexTypeDefinition._CT_ELEMENT_ONLY
    _Abstract = False
    _ExpandedName = pyxb.namespace.ExpandedName(Namespace, u'tOperation')
    _DefinitionLocation = pyxb.utils.utility.Location('/tmp/pyxbdist.RHB65sy/PyXB-1.1.5/pyxb/bundles/wssplat/schemas/wsdl11.xsd', 190, 2)
    # Base type is tExtensibleDocumented
    
    # Element {http://schemas.xmlsoap.org/wsdl/}fault uses Python identifier fault
    __fault = pyxb.binding.content.ElementUse(pyxb.namespace.ExpandedName(Namespace, u'fault'), 'fault', '__httpschemas_xmlsoap_orgwsdl_tOperation_httpschemas_xmlsoap_orgwsdlfault', True)
    __fault._DeclarationLocation = pyxb.utils.utility.Location('/tmp/pyxbdist.RHB65sy/PyXB-1.1.5/pyxb/bundles/wssplat/schemas/wsdl11.xsd', 210, 2)
    __fault._UseLocation = None

    
    fault = property(__fault.value, __fault.set, None, None)

    
    # Element documentation ({http://schemas.xmlsoap.org/wsdl/}documentation) inherited from {http://schemas.xmlsoap.org/wsdl/}tDocumented
    
    # Element {http://schemas.xmlsoap.org/wsdl/}output uses Python identifier output
    __output = pyxb.binding.content.ElementUse(pyxb.namespace.ExpandedName(Namespace, u'output'), 'output', '__httpschemas_xmlsoap_orgwsdl_tOperation_httpschemas_xmlsoap_orgwsdloutput', False)
    __output._DeclarationLocation = pyxb.utils.utility.Location('/tmp/pyxbdist.RHB65sy/PyXB-1.1.5/pyxb/bundles/wssplat/schemas/wsdl11.xsd', 209, 5)
    __output._UseLocation = None

    
    output = property(__output.value, __output.set, None, None)

    
    # Element {http://schemas.xmlsoap.org/wsdl/}input uses Python identifier input
    __input = pyxb.binding.content.ElementUse(pyxb.namespace.ExpandedName(Namespace, u'input'), 'input', '__httpschemas_xmlsoap_orgwsdl_tOperation_httpschemas_xmlsoap_orgwsdlinput', False)
    __input._DeclarationLocation = pyxb.utils.utility.Location('/tmp/pyxbdist.RHB65sy/PyXB-1.1.5/pyxb/bundles/wssplat/schemas/wsdl11.xsd', 207, 6)
    __input._UseLocation = None

    
    input = property(__input.value, __input.set, None, None)

    
    # Attribute name uses Python identifier name
    __name = pyxb.binding.content.AttributeUse(pyxb.namespace.ExpandedName(None, u'name'), 'name', '__httpschemas_xmlsoap_orgwsdl_tOperation_name', pyxb.binding.datatypes.NCName, required=True)
    __name._DeclarationLocation = pyxb.utils.utility.Location('/tmp/pyxbdist.RHB65sy/PyXB-1.1.5/pyxb/bundles/wssplat/schemas/wsdl11.xsd', 199, 8)
    __name._UseLocation = pyxb.utils.utility.Location('/tmp/pyxbdist.RHB65sy/PyXB-1.1.5/pyxb/bundles/wssplat/schemas/wsdl11.xsd', 199, 8)
    
    name = property(__name.value, __name.set, None, None)

    
    # Attribute parameterOrder uses Python identifier parameterOrder
    __parameterOrder = pyxb.binding.content.AttributeUse(pyxb.namespace.ExpandedName(None, u'parameterOrder'), 'parameterOrder', '__httpschemas_xmlsoap_orgwsdl_tOperation_parameterOrder', pyxb.binding.datatypes.NMTOKENS)
    __parameterOrder._DeclarationLocation = pyxb.utils.utility.Location('/tmp/pyxbdist.RHB65sy/PyXB-1.1.5/pyxb/bundles/wssplat/schemas/wsdl11.xsd', 200, 8)
    __parameterOrder._UseLocation = pyxb.utils.utility.Location('/tmp/pyxbdist.RHB65sy/PyXB-1.1.5/pyxb/bundles/wssplat/schemas/wsdl11.xsd', 200, 8)
    
    parameterOrder = property(__parameterOrder.value, __parameterOrder.set, None, None)

    _HasWildcardElement = True

    _ElementMap = tExtensibleDocumented._ElementMap.copy()
    _ElementMap.update({
        __fault.name() : __fault,
        __output.name() : __output,
        __input.name() : __input
    })
    _AttributeMap = tExtensibleDocumented._AttributeMap.copy()
    _AttributeMap.update({
        __name.name() : __name,
        __parameterOrder.name() : __parameterOrder
    })
Namespace.addCategoryObject('typeBinding', u'tOperation', tOperation)


# Complex type {http://schemas.xmlsoap.org/wsdl/}tDocumentation with content type MIXED
class tDocumentation (pyxb.binding.basis.complexTypeDefinition):
    _TypeDefinition = None
    _ContentTypeTag = pyxb.binding.basis.complexTypeDefinition._CT_MIXED
    _Abstract = False
    _ExpandedName = pyxb.namespace.ExpandedName(Namespace, u'tDocumentation')
    _DefinitionLocation = pyxb.utils.utility.Location('/tmp/pyxbdist.RHB65sy/PyXB-1.1.5/pyxb/bundles/wssplat/schemas/wsdl11.xsd', 37, 2)
    # Base type is pyxb.binding.datatypes.anyType
    _HasWildcardElement = True

    _ElementMap = {
        
    }
    _AttributeMap = {
        
    }
Namespace.addCategoryObject('typeBinding', u'tDocumentation', tDocumentation)


# Complex type {http://schemas.xmlsoap.org/wsdl/}tBindingOperationMessage with content type ELEMENT_ONLY
class tBindingOperationMessage (tExtensibleDocumented):
    _TypeDefinition = None
    _ContentTypeTag = pyxb.binding.basis.complexTypeDefinition._CT_ELEMENT_ONLY
    _Abstract = False
    _ExpandedName = pyxb.namespace.ExpandedName(Namespace, u'tBindingOperationMessage')
    _DefinitionLocation = pyxb.utils.utility.Location('/tmp/pyxbdist.RHB65sy/PyXB-1.1.5/pyxb/bundles/wssplat/schemas/wsdl11.xsd', 255, 2)
    # Base type is tExtensibleDocumented
    
    # Element documentation ({http://schemas.xmlsoap.org/wsdl/}documentation) inherited from {http://schemas.xmlsoap.org/wsdl/}tDocumented
    
    # Attribute name uses Python identifier name
    __name = pyxb.binding.content.AttributeUse(pyxb.namespace.ExpandedName(None, u'name'), 'name', '__httpschemas_xmlsoap_orgwsdl_tBindingOperationMessage_name', pyxb.binding.datatypes.NCName)
    __name._DeclarationLocation = pyxb.utils.utility.Location('/tmp/pyxbdist.RHB65sy/PyXB-1.1.5/pyxb/bundles/wssplat/schemas/wsdl11.xsd', 258, 8)
    __name._UseLocation = pyxb.utils.utility.Location('/tmp/pyxbdist.RHB65sy/PyXB-1.1.5/pyxb/bundles/wssplat/schemas/wsdl11.xsd', 258, 8)
    
    name = property(__name.value, __name.set, None, None)

    _HasWildcardElement = True

    _ElementMap = tExtensibleDocumented._ElementMap.copy()
    _ElementMap.update({
        
    })
    _AttributeMap = tExtensibleDocumented._AttributeMap.copy()
    _AttributeMap.update({
        __name.name() : __name
    })
Namespace.addCategoryObject('typeBinding', u'tBindingOperationMessage', tBindingOperationMessage)


# Complex type {http://schemas.xmlsoap.org/wsdl/}tBindingOperationFault with content type ELEMENT_ONLY
class tBindingOperationFault (tExtensibleDocumented):
    _TypeDefinition = None
    _ContentTypeTag = pyxb.binding.basis.complexTypeDefinition._CT_ELEMENT_ONLY
    _Abstract = False
    _ExpandedName = pyxb.namespace.ExpandedName(Namespace, u'tBindingOperationFault')
    _DefinitionLocation = pyxb.utils.utility.Location('/tmp/pyxbdist.RHB65sy/PyXB-1.1.5/pyxb/bundles/wssplat/schemas/wsdl11.xsd', 263, 2)
    # Base type is tExtensibleDocumented
    
    # Element documentation ({http://schemas.xmlsoap.org/wsdl/}documentation) inherited from {http://schemas.xmlsoap.org/wsdl/}tDocumented
    
    # Attribute name uses Python identifier name
    __name = pyxb.binding.content.AttributeUse(pyxb.namespace.ExpandedName(None, u'name'), 'name', '__httpschemas_xmlsoap_orgwsdl_tBindingOperationFault_name', pyxb.binding.datatypes.NCName, required=True)
    __name._DeclarationLocation = pyxb.utils.utility.Location('/tmp/pyxbdist.RHB65sy/PyXB-1.1.5/pyxb/bundles/wssplat/schemas/wsdl11.xsd', 266, 8)
    __name._UseLocation = pyxb.utils.utility.Location('/tmp/pyxbdist.RHB65sy/PyXB-1.1.5/pyxb/bundles/wssplat/schemas/wsdl11.xsd', 266, 8)
    
    name = property(__name.value, __name.set, None, None)

    _HasWildcardElement = True

    _ElementMap = tExtensibleDocumented._ElementMap.copy()
    _ElementMap.update({
        
    })
    _AttributeMap = tExtensibleDocumented._AttributeMap.copy()
    _AttributeMap.update({
        __name.name() : __name
    })
Namespace.addCategoryObject('typeBinding', u'tBindingOperationFault', tBindingOperationFault)


# Complex type {http://schemas.xmlsoap.org/wsdl/}tDefinitions with content type ELEMENT_ONLY
class tDefinitions (tExtensibleDocumented):
    _TypeDefinition = None
    _ContentTypeTag = pyxb.binding.basis.complexTypeDefinition._CT_ELEMENT_ONLY
    _Abstract = False
    _ExpandedName = pyxb.namespace.ExpandedName(Namespace, u'tDefinitions')
    _DefinitionLocation = pyxb.utils.utility.Location('/tmp/pyxbdist.RHB65sy/PyXB-1.1.5/pyxb/bundles/wssplat/schemas/wsdl11.xsd', 131, 2)
    # Base type is tExtensibleDocumented
    
    # Element {http://schemas.xmlsoap.org/wsdl/}message uses Python identifier message
    __message = pyxb.binding.content.ElementUse(pyxb.namespace.ExpandedName(Namespace, u'message'), 'message', '__httpschemas_xmlsoap_orgwsdl_tDefinitions_httpschemas_xmlsoap_orgwsdlmessage', True)
    __message._DeclarationLocation = pyxb.utils.utility.Location('/tmp/pyxbdist.RHB65sy/PyXB-1.1.5/pyxb/bundles/wssplat/schemas/wsdl11.xsd', 114, 6)
    __message._UseLocation = None

    
    message = property(__message.value, __message.set, None, None)

    
    # Element documentation ({http://schemas.xmlsoap.org/wsdl/}documentation) inherited from {http://schemas.xmlsoap.org/wsdl/}tDocumented
    
    # Element {http://schemas.xmlsoap.org/wsdl/}service uses Python identifier service
    __service = pyxb.binding.content.ElementUse(pyxb.namespace.ExpandedName(Namespace, u'service'), 'service', '__httpschemas_xmlsoap_orgwsdl_tDefinitions_httpschemas_xmlsoap_orgwsdlservice', True)
    __service._DeclarationLocation = pyxb.utils.utility.Location('/tmp/pyxbdist.RHB65sy/PyXB-1.1.5/pyxb/bundles/wssplat/schemas/wsdl11.xsd', 122, 6)
    __service._UseLocation = None

    
    service = property(__service.value, __service.set, None, None)

    
    # Element {http://schemas.xmlsoap.org/wsdl/}portType uses Python identifier portType
    __portType = pyxb.binding.content.ElementUse(pyxb.namespace.ExpandedName(Namespace, u'portType'), 'portType', '__httpschemas_xmlsoap_orgwsdl_tDefinitions_httpschemas_xmlsoap_orgwsdlportType', True)
    __portType._DeclarationLocation = pyxb.utils.utility.Location('/tmp/pyxbdist.RHB65sy/PyXB-1.1.5/pyxb/bundles/wssplat/schemas/wsdl11.xsd', 120, 6)
    __portType._UseLocation = None

    
    portType = property(__portType.value, __portType.set, None, None)

    
    # Element {http://schemas.xmlsoap.org/wsdl/}import uses Python identifier import_
    __import = pyxb.binding.content.ElementUse(pyxb.namespace.ExpandedName(Namespace, u'import'), 'import_', '__httpschemas_xmlsoap_orgwsdl_tDefinitions_httpschemas_xmlsoap_orgwsdlimport', True)
    __import._DeclarationLocation = pyxb.utils.utility.Location('/tmp/pyxbdist.RHB65sy/PyXB-1.1.5/pyxb/bundles/wssplat/schemas/wsdl11.xsd', 112, 6)
    __import._UseLocation = None

    
    import_ = property(__import.value, __import.set, None, None)

    
    # Element {http://schemas.xmlsoap.org/wsdl/}types uses Python identifier types
    __types = pyxb.binding.content.ElementUse(pyxb.namespace.ExpandedName(Namespace, u'types'), 'types', '__httpschemas_xmlsoap_orgwsdl_tDefinitions_httpschemas_xmlsoap_orgwsdltypes', True)
    __types._DeclarationLocation = pyxb.utils.utility.Location('/tmp/pyxbdist.RHB65sy/PyXB-1.1.5/pyxb/bundles/wssplat/schemas/wsdl11.xsd', 113, 6)
    __types._UseLocation = None

    
    types = property(__types.value, __types.set, None, None)

    
    # Element {http://schemas.xmlsoap.org/wsdl/}binding uses Python identifier binding
    __binding = pyxb.binding.content.ElementUse(pyxb.namespace.ExpandedName(Namespace, u'binding'), 'binding', '__httpschemas_xmlsoap_orgwsdl_tDefinitions_httpschemas_xmlsoap_orgwsdlbinding', True)
    __binding._DeclarationLocation = pyxb.utils.utility.Location('/tmp/pyxbdist.RHB65sy/PyXB-1.1.5/pyxb/bundles/wssplat/schemas/wsdl11.xsd', 121, 6)
    __binding._UseLocation = None

    
    binding = property(__binding.value, __binding.set, None, None)

    
    # Attribute targetNamespace uses Python identifier targetNamespace
    __targetNamespace = pyxb.binding.content.AttributeUse(pyxb.namespace.ExpandedName(None, u'targetNamespace'), 'targetNamespace', '__httpschemas_xmlsoap_orgwsdl_tDefinitions_targetNamespace', pyxb.binding.datatypes.anyURI)
    __targetNamespace._DeclarationLocation = pyxb.utils.utility.Location('/tmp/pyxbdist.RHB65sy/PyXB-1.1.5/pyxb/bundles/wssplat/schemas/wsdl11.xsd', 137, 8)
    __targetNamespace._UseLocation = pyxb.utils.utility.Location('/tmp/pyxbdist.RHB65sy/PyXB-1.1.5/pyxb/bundles/wssplat/schemas/wsdl11.xsd', 137, 8)
    
    targetNamespace = property(__targetNamespace.value, __targetNamespace.set, None, None)

    
    # Attribute name uses Python identifier name
    __name = pyxb.binding.content.AttributeUse(pyxb.namespace.ExpandedName(None, u'name'), 'name', '__httpschemas_xmlsoap_orgwsdl_tDefinitions_name', pyxb.binding.datatypes.NCName)
    __name._DeclarationLocation = pyxb.utils.utility.Location('/tmp/pyxbdist.RHB65sy/PyXB-1.1.5/pyxb/bundles/wssplat/schemas/wsdl11.xsd', 138, 8)
    __name._UseLocation = pyxb.utils.utility.Location('/tmp/pyxbdist.RHB65sy/PyXB-1.1.5/pyxb/bundles/wssplat/schemas/wsdl11.xsd', 138, 8)
    
    name = property(__name.value, __name.set, None, None)

    _HasWildcardElement = True

    _ElementMap = tExtensibleDocumented._ElementMap.copy()
    _ElementMap.update({
        __message.name() : __message,
        __service.name() : __service,
        __portType.name() : __portType,
        __import.name() : __import,
        __types.name() : __types,
        __binding.name() : __binding
    })
    _AttributeMap = tExtensibleDocumented._AttributeMap.copy()
    _AttributeMap.update({
        __targetNamespace.name() : __targetNamespace,
        __name.name() : __name
    })
Namespace.addCategoryObject('typeBinding', u'tDefinitions', tDefinitions)


# Complex type {http://schemas.xmlsoap.org/wsdl/}tExtensibilityElement with content type EMPTY
class tExtensibilityElement (pyxb.binding.basis.complexTypeDefinition):
    _TypeDefinition = None
    _ContentTypeTag = pyxb.binding.basis.complexTypeDefinition._CT_EMPTY
    _Abstract = True
    _ExpandedName = pyxb.namespace.ExpandedName(Namespace, u'tExtensibilityElement')
    _DefinitionLocation = pyxb.utils.utility.Location('/tmp/pyxbdist.RHB65sy/PyXB-1.1.5/pyxb/bundles/wssplat/schemas/wsdl11.xsd', 306, 2)
    # Base type is pyxb.binding.datatypes.anyType
    
    # Attribute {http://schemas.xmlsoap.org/wsdl/}required uses Python identifier required
    __required = pyxb.binding.content.AttributeUse(pyxb.namespace.ExpandedName(Namespace, u'required'), 'required', '__httpschemas_xmlsoap_orgwsdl_tExtensibilityElement_httpschemas_xmlsoap_orgwsdlrequired', pyxb.binding.datatypes.boolean)
    __required._DeclarationLocation = pyxb.utils.utility.Location('/tmp/pyxbdist.RHB65sy/PyXB-1.1.5/pyxb/bundles/wssplat/schemas/wsdl11.xsd', 305, 2)
    __required._UseLocation = pyxb.utils.utility.Location('/tmp/pyxbdist.RHB65sy/PyXB-1.1.5/pyxb/bundles/wssplat/schemas/wsdl11.xsd', 307, 4)
    
    required = property(__required.value, __required.set, None, None)


    _ElementMap = {
        
    }
    _AttributeMap = {
        __required.name() : __required
    }
Namespace.addCategoryObject('typeBinding', u'tExtensibilityElement', tExtensibilityElement)


# Complex type {http://schemas.xmlsoap.org/wsdl/}tImport with content type ELEMENT_ONLY
class tImport (tExtensibleAttributesDocumented):
    _TypeDefinition = None
    _ContentTypeTag = pyxb.binding.basis.complexTypeDefinition._CT_ELEMENT_ONLY
    _Abstract = False
    _ExpandedName = pyxb.namespace.ExpandedName(Namespace, u'tImport')
    _DefinitionLocation = pyxb.utils.utility.Location('/tmp/pyxbdist.RHB65sy/PyXB-1.1.5/pyxb/bundles/wssplat/schemas/wsdl11.xsd', 143, 2)
    # Base type is tExtensibleAttributesDocumented
    
    # Element documentation ({http://schemas.xmlsoap.org/wsdl/}documentation) inherited from {http://schemas.xmlsoap.org/wsdl/}tDocumented
    
    # Attribute namespace uses Python identifier namespace
    __namespace = pyxb.binding.content.AttributeUse(pyxb.namespace.ExpandedName(None, u'namespace'), 'namespace', '__httpschemas_xmlsoap_orgwsdl_tImport_namespace', pyxb.binding.datatypes.anyURI, required=True)
    __namespace._DeclarationLocation = pyxb.utils.utility.Location('/tmp/pyxbdist.RHB65sy/PyXB-1.1.5/pyxb/bundles/wssplat/schemas/wsdl11.xsd', 146, 8)
    __namespace._UseLocation = pyxb.utils.utility.Location('/tmp/pyxbdist.RHB65sy/PyXB-1.1.5/pyxb/bundles/wssplat/schemas/wsdl11.xsd', 146, 8)
    
    namespace = property(__namespace.value, __namespace.set, None, None)

    
    # Attribute location uses Python identifier location
    __location = pyxb.binding.content.AttributeUse(pyxb.namespace.ExpandedName(None, u'location'), 'location', '__httpschemas_xmlsoap_orgwsdl_tImport_location', pyxb.binding.datatypes.anyURI, required=True)
    __location._DeclarationLocation = pyxb.utils.utility.Location('/tmp/pyxbdist.RHB65sy/PyXB-1.1.5/pyxb/bundles/wssplat/schemas/wsdl11.xsd', 147, 8)
    __location._UseLocation = pyxb.utils.utility.Location('/tmp/pyxbdist.RHB65sy/PyXB-1.1.5/pyxb/bundles/wssplat/schemas/wsdl11.xsd', 147, 8)
    
    location = property(__location.value, __location.set, None, None)

    _AttributeWildcard = pyxb.binding.content.Wildcard(process_contents=pyxb.binding.content.Wildcard.PC_lax, namespace_constraint=(pyxb.binding.content.Wildcard.NC_not, u'http://schemas.xmlsoap.org/wsdl/'))

    _ElementMap = tExtensibleAttributesDocumented._ElementMap.copy()
    _ElementMap.update({
        
    })
    _AttributeMap = tExtensibleAttributesDocumented._AttributeMap.copy()
    _AttributeMap.update({
        __namespace.name() : __namespace,
        __location.name() : __location
    })
Namespace.addCategoryObject('typeBinding', u'tImport', tImport)


# Complex type {http://schemas.xmlsoap.org/wsdl/}tTypes with content type ELEMENT_ONLY
class tTypes (tExtensibleDocumented):
    _TypeDefinition = None
    _ContentTypeTag = pyxb.binding.basis.complexTypeDefinition._CT_ELEMENT_ONLY
    _Abstract = False
    _ExpandedName = pyxb.namespace.ExpandedName(Namespace, u'tTypes')
    _DefinitionLocation = pyxb.utils.utility.Location('/tmp/pyxbdist.RHB65sy/PyXB-1.1.5/pyxb/bundles/wssplat/schemas/wsdl11.xsd', 152, 2)
    # Base type is tExtensibleDocumented
    
    # Element documentation ({http://schemas.xmlsoap.org/wsdl/}documentation) inherited from {http://schemas.xmlsoap.org/wsdl/}tDocumented
    _HasWildcardElement = True

    _ElementMap = tExtensibleDocumented._ElementMap.copy()
    _ElementMap.update({
        
    })
    _AttributeMap = tExtensibleDocumented._AttributeMap.copy()
    _AttributeMap.update({
        
    })
Namespace.addCategoryObject('typeBinding', u'tTypes', tTypes)


# Complex type {http://schemas.xmlsoap.org/wsdl/}tPort with content type ELEMENT_ONLY
class tPort (tExtensibleDocumented):
    _TypeDefinition = None
    _ContentTypeTag = pyxb.binding.basis.complexTypeDefinition._CT_ELEMENT_ONLY
    _Abstract = False
    _ExpandedName = pyxb.namespace.ExpandedName(Namespace, u'tPort')
    _DefinitionLocation = pyxb.utils.utility.Location('/tmp/pyxbdist.RHB65sy/PyXB-1.1.5/pyxb/bundles/wssplat/schemas/wsdl11.xsd', 295, 2)
    # Base type is tExtensibleDocumented
    
    # Element documentation ({http://schemas.xmlsoap.org/wsdl/}documentation) inherited from {http://schemas.xmlsoap.org/wsdl/}tDocumented
    
    # Attribute binding uses Python identifier binding
    __binding = pyxb.binding.content.AttributeUse(pyxb.namespace.ExpandedName(None, u'binding'), 'binding', '__httpschemas_xmlsoap_orgwsdl_tPort_binding', pyxb.binding.datatypes.QName, required=True)
    __binding._DeclarationLocation = pyxb.utils.utility.Location('/tmp/pyxbdist.RHB65sy/PyXB-1.1.5/pyxb/bundles/wssplat/schemas/wsdl11.xsd', 299, 8)
    __binding._UseLocation = pyxb.utils.utility.Location('/tmp/pyxbdist.RHB65sy/PyXB-1.1.5/pyxb/bundles/wssplat/schemas/wsdl11.xsd', 299, 8)
    
    binding = property(__binding.value, __binding.set, None, None)

    
    # Attribute name uses Python identifier name
    __name = pyxb.binding.content.AttributeUse(pyxb.namespace.ExpandedName(None, u'name'), 'name', '__httpschemas_xmlsoap_orgwsdl_tPort_name', pyxb.binding.datatypes.NCName, required=True)
    __name._DeclarationLocation = pyxb.utils.utility.Location('/tmp/pyxbdist.RHB65sy/PyXB-1.1.5/pyxb/bundles/wssplat/schemas/wsdl11.xsd', 298, 8)
    __name._UseLocation = pyxb.utils.utility.Location('/tmp/pyxbdist.RHB65sy/PyXB-1.1.5/pyxb/bundles/wssplat/schemas/wsdl11.xsd', 298, 8)
    
    name = property(__name.value, __name.set, None, None)

    _HasWildcardElement = True

    _ElementMap = tExtensibleDocumented._ElementMap.copy()
    _ElementMap.update({
        
    })
    _AttributeMap = tExtensibleDocumented._AttributeMap.copy()
    _AttributeMap.update({
        __binding.name() : __binding,
        __name.name() : __name
    })
Namespace.addCategoryObject('typeBinding', u'tPort', tPort)


# Complex type {http://schemas.xmlsoap.org/wsdl/}tPart with content type ELEMENT_ONLY
class tPart (tExtensibleAttributesDocumented):
    _TypeDefinition = None
    _ContentTypeTag = pyxb.binding.basis.complexTypeDefinition._CT_ELEMENT_ONLY
    _Abstract = False
    _ExpandedName = pyxb.namespace.ExpandedName(Namespace, u'tPart')
    _DefinitionLocation = pyxb.utils.utility.Location('/tmp/pyxbdist.RHB65sy/PyXB-1.1.5/pyxb/bundles/wssplat/schemas/wsdl11.xsd', 169, 2)
    # Base type is tExtensibleAttributesDocumented
    
    # Element documentation ({http://schemas.xmlsoap.org/wsdl/}documentation) inherited from {http://schemas.xmlsoap.org/wsdl/}tDocumented
    
    # Attribute element uses Python identifier element
    __element = pyxb.binding.content.AttributeUse(pyxb.namespace.ExpandedName(None, u'element'), 'element', '__httpschemas_xmlsoap_orgwsdl_tPart_element', pyxb.binding.datatypes.QName)
    __element._DeclarationLocation = pyxb.utils.utility.Location('/tmp/pyxbdist.RHB65sy/PyXB-1.1.5/pyxb/bundles/wssplat/schemas/wsdl11.xsd', 173, 8)
    __element._UseLocation = pyxb.utils.utility.Location('/tmp/pyxbdist.RHB65sy/PyXB-1.1.5/pyxb/bundles/wssplat/schemas/wsdl11.xsd', 173, 8)
    
    element = property(__element.value, __element.set, None, None)

    
    # Attribute type uses Python identifier type
    __type = pyxb.binding.content.AttributeUse(pyxb.namespace.ExpandedName(None, u'type'), 'type', '__httpschemas_xmlsoap_orgwsdl_tPart_type', pyxb.binding.datatypes.QName)
    __type._DeclarationLocation = pyxb.utils.utility.Location('/tmp/pyxbdist.RHB65sy/PyXB-1.1.5/pyxb/bundles/wssplat/schemas/wsdl11.xsd', 174, 8)
    __type._UseLocation = pyxb.utils.utility.Location('/tmp/pyxbdist.RHB65sy/PyXB-1.1.5/pyxb/bundles/wssplat/schemas/wsdl11.xsd', 174, 8)
    
    type = property(__type.value, __type.set, None, None)

    
    # Attribute name uses Python identifier name
    __name = pyxb.binding.content.AttributeUse(pyxb.namespace.ExpandedName(None, u'name'), 'name', '__httpschemas_xmlsoap_orgwsdl_tPart_name', pyxb.binding.datatypes.NCName, required=True)
    __name._DeclarationLocation = pyxb.utils.utility.Location('/tmp/pyxbdist.RHB65sy/PyXB-1.1.5/pyxb/bundles/wssplat/schemas/wsdl11.xsd', 172, 8)
    __name._UseLocation = pyxb.utils.utility.Location('/tmp/pyxbdist.RHB65sy/PyXB-1.1.5/pyxb/bundles/wssplat/schemas/wsdl11.xsd', 172, 8)
    
    name = property(__name.value, __name.set, None, None)

    _AttributeWildcard = pyxb.binding.content.Wildcard(process_contents=pyxb.binding.content.Wildcard.PC_lax, namespace_constraint=(pyxb.binding.content.Wildcard.NC_not, u'http://schemas.xmlsoap.org/wsdl/'))

    _ElementMap = tExtensibleAttributesDocumented._ElementMap.copy()
    _ElementMap.update({
        
    })
    _AttributeMap = tExtensibleAttributesDocumented._AttributeMap.copy()
    _AttributeMap.update({
        __element.name() : __element,
        __type.name() : __type,
        __name.name() : __name
    })
Namespace.addCategoryObject('typeBinding', u'tPart', tPart)


definitions = pyxb.binding.basis.element(pyxb.namespace.ExpandedName(Namespace, u'definitions'), tDefinitions)
Namespace.addCategoryObject('elementBinding', definitions.name().localName(), definitions)



tDocumented._AddElement(pyxb.binding.basis.element(pyxb.namespace.ExpandedName(Namespace, u'documentation'), tDocumentation, scope=tDocumented))
tDocumented._GroupModel = pyxb.binding.content.GroupSequence(
    pyxb.binding.content.ParticleModel(tDocumented._UseForTag(pyxb.namespace.ExpandedName(Namespace, u'documentation')), min_occurs=0L, max_occurs=1)
    )
tDocumented._ContentModel = pyxb.binding.content.ParticleModel(tDocumented._GroupModel, min_occurs=1, max_occurs=1)


tExtensibleDocumented._GroupModel_ = pyxb.binding.content.GroupSequence(
    pyxb.binding.content.ParticleModel(tExtensibleDocumented._UseForTag(pyxb.namespace.ExpandedName(Namespace, u'documentation')), min_occurs=0L, max_occurs=1)
    )
tExtensibleDocumented._GroupModel_2 = pyxb.binding.content.GroupSequence(
    pyxb.binding.content.ParticleModel(pyxb.binding.content.Wildcard(process_contents=pyxb.binding.content.Wildcard.PC_lax, namespace_constraint=(pyxb.binding.content.Wildcard.NC_not, u'http://schemas.xmlsoap.org/wsdl/')), min_occurs=0L, max_occurs=None)
    )
tExtensibleDocumented._GroupModel = pyxb.binding.content.GroupSequence(
    pyxb.binding.content.ParticleModel(tExtensibleDocumented._GroupModel_, min_occurs=1, max_occurs=1),
    pyxb.binding.content.ParticleModel(tExtensibleDocumented._GroupModel_2, min_occurs=1, max_occurs=1)
    )
tExtensibleDocumented._ContentModel = pyxb.binding.content.ParticleModel(tExtensibleDocumented._GroupModel, min_occurs=1, max_occurs=1)



tBindingOperation._AddElement(pyxb.binding.basis.element(pyxb.namespace.ExpandedName(Namespace, u'fault'), tBindingOperationFault, scope=tBindingOperation))

tBindingOperation._AddElement(pyxb.binding.basis.element(pyxb.namespace.ExpandedName(Namespace, u'output'), tBindingOperationMessage, scope=tBindingOperation))

tBindingOperation._AddElement(pyxb.binding.basis.element(pyxb.namespace.ExpandedName(Namespace, u'input'), tBindingOperationMessage, scope=tBindingOperation))
tBindingOperation._GroupModel_2 = pyxb.binding.content.GroupSequence(
    pyxb.binding.content.ParticleModel(tBindingOperation._UseForTag(pyxb.namespace.ExpandedName(Namespace, u'documentation')), min_occurs=0L, max_occurs=1)
    )
tBindingOperation._GroupModel_3 = pyxb.binding.content.GroupSequence(
    pyxb.binding.content.ParticleModel(pyxb.binding.content.Wildcard(process_contents=pyxb.binding.content.Wildcard.PC_lax, namespace_constraint=(pyxb.binding.content.Wildcard.NC_not, u'http://schemas.xmlsoap.org/wsdl/')), min_occurs=0L, max_occurs=None)
    )
tBindingOperation._GroupModel_ = pyxb.binding.content.GroupSequence(
    pyxb.binding.content.ParticleModel(tBindingOperation._GroupModel_2, min_occurs=1, max_occurs=1),
    pyxb.binding.content.ParticleModel(tBindingOperation._GroupModel_3, min_occurs=1, max_occurs=1)
    )
tBindingOperation._GroupModel_4 = pyxb.binding.content.GroupSequence(
    pyxb.binding.content.ParticleModel(tBindingOperation._UseForTag(pyxb.namespace.ExpandedName(Namespace, u'input')), min_occurs=0L, max_occurs=1),
    pyxb.binding.content.ParticleModel(tBindingOperation._UseForTag(pyxb.namespace.ExpandedName(Namespace, u'output')), min_occurs=0L, max_occurs=1),
    pyxb.binding.content.ParticleModel(tBindingOperation._UseForTag(pyxb.namespace.ExpandedName(Namespace, u'fault')), min_occurs=0L, max_occurs=None)
    )
tBindingOperation._GroupModel = pyxb.binding.content.GroupSequence(
    pyxb.binding.content.ParticleModel(tBindingOperation._GroupModel_, min_occurs=1, max_occurs=1),
    pyxb.binding.content.ParticleModel(tBindingOperation._GroupModel_4, min_occurs=1, max_occurs=1)
    )
tBindingOperation._ContentModel = pyxb.binding.content.ParticleModel(tBindingOperation._GroupModel, min_occurs=1, max_occurs=1)


tExtensibleAttributesDocumented._GroupModel = pyxb.binding.content.GroupSequence(
    pyxb.binding.content.ParticleModel(tExtensibleAttributesDocumented._UseForTag(pyxb.namespace.ExpandedName(Namespace, u'documentation')), min_occurs=0L, max_occurs=1)
    )
tExtensibleAttributesDocumented._ContentModel = pyxb.binding.content.ParticleModel(tExtensibleAttributesDocumented._GroupModel, min_occurs=1, max_occurs=1)


tParam._GroupModel = pyxb.binding.content.GroupSequence(
    pyxb.binding.content.ParticleModel(tParam._UseForTag(pyxb.namespace.ExpandedName(Namespace, u'documentation')), min_occurs=0L, max_occurs=1)
    )
tParam._ContentModel = pyxb.binding.content.ParticleModel(tParam._GroupModel, min_occurs=1, max_occurs=1)



tMessage._AddElement(pyxb.binding.basis.element(pyxb.namespace.ExpandedName(Namespace, u'part'), tPart, scope=tMessage))
tMessage._GroupModel_2 = pyxb.binding.content.GroupSequence(
    pyxb.binding.content.ParticleModel(tMessage._UseForTag(pyxb.namespace.ExpandedName(Namespace, u'documentation')), min_occurs=0L, max_occurs=1)
    )
tMessage._GroupModel_3 = pyxb.binding.content.GroupSequence(
    pyxb.binding.content.ParticleModel(pyxb.binding.content.Wildcard(process_contents=pyxb.binding.content.Wildcard.PC_lax, namespace_constraint=(pyxb.binding.content.Wildcard.NC_not, u'http://schemas.xmlsoap.org/wsdl/')), min_occurs=0L, max_occurs=None)
    )
tMessage._GroupModel_ = pyxb.binding.content.GroupSequence(
    pyxb.binding.content.ParticleModel(tMessage._GroupModel_2, min_occurs=1, max_occurs=1),
    pyxb.binding.content.ParticleModel(tMessage._GroupModel_3, min_occurs=1, max_occurs=1)
    )
tMessage._GroupModel_4 = pyxb.binding.content.GroupSequence(
    pyxb.binding.content.ParticleModel(tMessage._UseForTag(pyxb.namespace.ExpandedName(Namespace, u'part')), min_occurs=0L, max_occurs=None)
    )
tMessage._GroupModel = pyxb.binding.content.GroupSequence(
    pyxb.binding.content.ParticleModel(tMessage._GroupModel_, min_occurs=1, max_occurs=1),
    pyxb.binding.content.ParticleModel(tMessage._GroupModel_4, min_occurs=1, max_occurs=1)
    )
tMessage._ContentModel = pyxb.binding.content.ParticleModel(tMessage._GroupModel, min_occurs=1, max_occurs=1)


tFault._GroupModel = pyxb.binding.content.GroupSequence(
    pyxb.binding.content.ParticleModel(tFault._UseForTag(pyxb.namespace.ExpandedName(Namespace, u'documentation')), min_occurs=0L, max_occurs=1)
    )
tFault._ContentModel = pyxb.binding.content.ParticleModel(tFault._GroupModel, min_occurs=1, max_occurs=1)



tPortType._AddElement(pyxb.binding.basis.element(pyxb.namespace.ExpandedName(Namespace, u'operation'), tOperation, scope=tPortType))
tPortType._GroupModel_ = pyxb.binding.content.GroupSequence(
    pyxb.binding.content.ParticleModel(tPortType._UseForTag(pyxb.namespace.ExpandedName(Namespace, u'documentation')), min_occurs=0L, max_occurs=1)
    )
tPortType._GroupModel_2 = pyxb.binding.content.GroupSequence(
    pyxb.binding.content.ParticleModel(tPortType._UseForTag(pyxb.namespace.ExpandedName(Namespace, u'operation')), min_occurs=0L, max_occurs=None)
    )
tPortType._GroupModel = pyxb.binding.content.GroupSequence(
    pyxb.binding.content.ParticleModel(tPortType._GroupModel_, min_occurs=1, max_occurs=1),
    pyxb.binding.content.ParticleModel(tPortType._GroupModel_2, min_occurs=1, max_occurs=1)
    )
tPortType._ContentModel = pyxb.binding.content.ParticleModel(tPortType._GroupModel, min_occurs=1, max_occurs=1)



tBinding._AddElement(pyxb.binding.basis.element(pyxb.namespace.ExpandedName(Namespace, u'operation'), tBindingOperation, scope=tBinding))
tBinding._GroupModel_2 = pyxb.binding.content.GroupSequence(
    pyxb.binding.content.ParticleModel(tBinding._UseForTag(pyxb.namespace.ExpandedName(Namespace, u'documentation')), min_occurs=0L, max_occurs=1)
    )
tBinding._GroupModel_3 = pyxb.binding.content.GroupSequence(
    pyxb.binding.content.ParticleModel(pyxb.binding.content.Wildcard(process_contents=pyxb.binding.content.Wildcard.PC_lax, namespace_constraint=(pyxb.binding.content.Wildcard.NC_not, u'http://schemas.xmlsoap.org/wsdl/')), min_occurs=0L, max_occurs=None)
    )
tBinding._GroupModel_ = pyxb.binding.content.GroupSequence(
    pyxb.binding.content.ParticleModel(tBinding._GroupModel_2, min_occurs=1, max_occurs=1),
    pyxb.binding.content.ParticleModel(tBinding._GroupModel_3, min_occurs=1, max_occurs=1)
    )
tBinding._GroupModel_4 = pyxb.binding.content.GroupSequence(
    pyxb.binding.content.ParticleModel(tBinding._UseForTag(pyxb.namespace.ExpandedName(Namespace, u'operation')), min_occurs=0L, max_occurs=None)
    )
tBinding._GroupModel = pyxb.binding.content.GroupSequence(
    pyxb.binding.content.ParticleModel(tBinding._GroupModel_, min_occurs=1, max_occurs=1),
    pyxb.binding.content.ParticleModel(tBinding._GroupModel_4, min_occurs=1, max_occurs=1)
    )
tBinding._ContentModel = pyxb.binding.content.ParticleModel(tBinding._GroupModel, min_occurs=1, max_occurs=1)



tService._AddElement(pyxb.binding.basis.element(pyxb.namespace.ExpandedName(Namespace, u'port'), tPort, scope=tService))
tService._GroupModel_2 = pyxb.binding.content.GroupSequence(
    pyxb.binding.content.ParticleModel(tService._UseForTag(pyxb.namespace.ExpandedName(Namespace, u'documentation')), min_occurs=0L, max_occurs=1)
    )
tService._GroupModel_3 = pyxb.binding.content.GroupSequence(
    pyxb.binding.content.ParticleModel(pyxb.binding.content.Wildcard(process_contents=pyxb.binding.content.Wildcard.PC_lax, namespace_constraint=(pyxb.binding.content.Wildcard.NC_not, u'http://schemas.xmlsoap.org/wsdl/')), min_occurs=0L, max_occurs=None)
    )
tService._GroupModel_ = pyxb.binding.content.GroupSequence(
    pyxb.binding.content.ParticleModel(tService._GroupModel_2, min_occurs=1, max_occurs=1),
    pyxb.binding.content.ParticleModel(tService._GroupModel_3, min_occurs=1, max_occurs=1)
    )
tService._GroupModel_4 = pyxb.binding.content.GroupSequence(
    pyxb.binding.content.ParticleModel(tService._UseForTag(pyxb.namespace.ExpandedName(Namespace, u'port')), min_occurs=0L, max_occurs=None)
    )
tService._GroupModel = pyxb.binding.content.GroupSequence(
    pyxb.binding.content.ParticleModel(tService._GroupModel_, min_occurs=1, max_occurs=1),
    pyxb.binding.content.ParticleModel(tService._GroupModel_4, min_occurs=1, max_occurs=1)
    )
tService._ContentModel = pyxb.binding.content.ParticleModel(tService._GroupModel, min_occurs=1, max_occurs=1)



tOperation._AddElement(pyxb.binding.basis.element(pyxb.namespace.ExpandedName(Namespace, u'fault'), tFault, scope=tOperation))

tOperation._AddElement(pyxb.binding.basis.element(pyxb.namespace.ExpandedName(Namespace, u'output'), tParam, scope=tOperation))

tOperation._AddElement(pyxb.binding.basis.element(pyxb.namespace.ExpandedName(Namespace, u'input'), tParam, scope=tOperation))
tOperation._GroupModel_2 = pyxb.binding.content.GroupSequence(
    pyxb.binding.content.ParticleModel(tOperation._UseForTag(pyxb.namespace.ExpandedName(Namespace, u'documentation')), min_occurs=0L, max_occurs=1)
    )
tOperation._GroupModel_3 = pyxb.binding.content.GroupSequence(
    pyxb.binding.content.ParticleModel(pyxb.binding.content.Wildcard(process_contents=pyxb.binding.content.Wildcard.PC_lax, namespace_constraint=(pyxb.binding.content.Wildcard.NC_not, u'http://schemas.xmlsoap.org/wsdl/')), min_occurs=0L, max_occurs=None)
    )
tOperation._GroupModel_ = pyxb.binding.content.GroupSequence(
    pyxb.binding.content.ParticleModel(tOperation._GroupModel_2, min_occurs=1, max_occurs=1),
    pyxb.binding.content.ParticleModel(tOperation._GroupModel_3, min_occurs=1, max_occurs=1)
    )
tOperation._GroupModel_7 = pyxb.binding.content.GroupSequence(
    pyxb.binding.content.ParticleModel(tOperation._UseForTag(pyxb.namespace.ExpandedName(Namespace, u'output')), min_occurs=1, max_occurs=1),
    pyxb.binding.content.ParticleModel(tOperation._UseForTag(pyxb.namespace.ExpandedName(Namespace, u'fault')), min_occurs=0L, max_occurs=None)
    )
tOperation._GroupModel_6 = pyxb.binding.content.GroupSequence(
    pyxb.binding.content.ParticleModel(tOperation._UseForTag(pyxb.namespace.ExpandedName(Namespace, u'input')), min_occurs=1, max_occurs=1),
    pyxb.binding.content.ParticleModel(tOperation._GroupModel_7, min_occurs=0L, max_occurs=1)
    )
tOperation._GroupModel_9 = pyxb.binding.content.GroupSequence(
    pyxb.binding.content.ParticleModel(tOperation._UseForTag(pyxb.namespace.ExpandedName(Namespace, u'input')), min_occurs=1, max_occurs=1),
    pyxb.binding.content.ParticleModel(tOperation._UseForTag(pyxb.namespace.ExpandedName(Namespace, u'fault')), min_occurs=0L, max_occurs=None)
    )
tOperation._GroupModel_8 = pyxb.binding.content.GroupSequence(
    pyxb.binding.content.ParticleModel(tOperation._UseForTag(pyxb.namespace.ExpandedName(Namespace, u'output')), min_occurs=1, max_occurs=1),
    pyxb.binding.content.ParticleModel(tOperation._GroupModel_9, min_occurs=0L, max_occurs=1)
    )
tOperation._GroupModel_5 = pyxb.binding.content.GroupChoice(
    pyxb.binding.content.ParticleModel(tOperation._GroupModel_6, min_occurs=1, max_occurs=1),
    pyxb.binding.content.ParticleModel(tOperation._GroupModel_8, min_occurs=1, max_occurs=1)
    )
tOperation._GroupModel_4 = pyxb.binding.content.GroupSequence(
    pyxb.binding.content.ParticleModel(tOperation._GroupModel_5, min_occurs=1, max_occurs=1)
    )
tOperation._GroupModel = pyxb.binding.content.GroupSequence(
    pyxb.binding.content.ParticleModel(tOperation._GroupModel_, min_occurs=1, max_occurs=1),
    pyxb.binding.content.ParticleModel(tOperation._GroupModel_4, min_occurs=1, max_occurs=1)
    )
tOperation._ContentModel = pyxb.binding.content.ParticleModel(tOperation._GroupModel, min_occurs=1, max_occurs=1)


tDocumentation._GroupModel = pyxb.binding.content.GroupSequence(
    pyxb.binding.content.ParticleModel(pyxb.binding.content.Wildcard(process_contents=pyxb.binding.content.Wildcard.PC_lax, namespace_constraint=pyxb.binding.content.Wildcard.NC_any), min_occurs=0L, max_occurs=None)
    )
tDocumentation._ContentModel = pyxb.binding.content.ParticleModel(tDocumentation._GroupModel, min_occurs=1, max_occurs=1)


tBindingOperationMessage._GroupModel_ = pyxb.binding.content.GroupSequence(
    pyxb.binding.content.ParticleModel(tBindingOperationMessage._UseForTag(pyxb.namespace.ExpandedName(Namespace, u'documentation')), min_occurs=0L, max_occurs=1)
    )
tBindingOperationMessage._GroupModel_2 = pyxb.binding.content.GroupSequence(
    pyxb.binding.content.ParticleModel(pyxb.binding.content.Wildcard(process_contents=pyxb.binding.content.Wildcard.PC_lax, namespace_constraint=(pyxb.binding.content.Wildcard.NC_not, u'http://schemas.xmlsoap.org/wsdl/')), min_occurs=0L, max_occurs=None)
    )
tBindingOperationMessage._GroupModel = pyxb.binding.content.GroupSequence(
    pyxb.binding.content.ParticleModel(tBindingOperationMessage._GroupModel_, min_occurs=1, max_occurs=1),
    pyxb.binding.content.ParticleModel(tBindingOperationMessage._GroupModel_2, min_occurs=1, max_occurs=1)
    )
tBindingOperationMessage._ContentModel = pyxb.binding.content.ParticleModel(tBindingOperationMessage._GroupModel, min_occurs=1, max_occurs=1)


tBindingOperationFault._GroupModel_ = pyxb.binding.content.GroupSequence(
    pyxb.binding.content.ParticleModel(tBindingOperationFault._UseForTag(pyxb.namespace.ExpandedName(Namespace, u'documentation')), min_occurs=0L, max_occurs=1)
    )
tBindingOperationFault._GroupModel_2 = pyxb.binding.content.GroupSequence(
    pyxb.binding.content.ParticleModel(pyxb.binding.content.Wildcard(process_contents=pyxb.binding.content.Wildcard.PC_lax, namespace_constraint=(pyxb.binding.content.Wildcard.NC_not, u'http://schemas.xmlsoap.org/wsdl/')), min_occurs=0L, max_occurs=None)
    )
tBindingOperationFault._GroupModel = pyxb.binding.content.GroupSequence(
    pyxb.binding.content.ParticleModel(tBindingOperationFault._GroupModel_, min_occurs=1, max_occurs=1),
    pyxb.binding.content.ParticleModel(tBindingOperationFault._GroupModel_2, min_occurs=1, max_occurs=1)
    )
tBindingOperationFault._ContentModel = pyxb.binding.content.ParticleModel(tBindingOperationFault._GroupModel, min_occurs=1, max_occurs=1)



tDefinitions._AddElement(pyxb.binding.basis.element(pyxb.namespace.ExpandedName(Namespace, u'message'), tMessage, scope=tDefinitions))

tDefinitions._AddElement(pyxb.binding.basis.element(pyxb.namespace.ExpandedName(Namespace, u'service'), tService, scope=tDefinitions))

tDefinitions._AddElement(pyxb.binding.basis.element(pyxb.namespace.ExpandedName(Namespace, u'portType'), tPortType, scope=tDefinitions))

tDefinitions._AddElement(pyxb.binding.basis.element(pyxb.namespace.ExpandedName(Namespace, u'import'), tImport, scope=tDefinitions))

tDefinitions._AddElement(pyxb.binding.basis.element(pyxb.namespace.ExpandedName(Namespace, u'types'), tTypes, scope=tDefinitions))

tDefinitions._AddElement(pyxb.binding.basis.element(pyxb.namespace.ExpandedName(Namespace, u'binding'), tBinding, scope=tDefinitions))
tDefinitions._GroupModel_2 = pyxb.binding.content.GroupSequence(
    pyxb.binding.content.ParticleModel(tDefinitions._UseForTag(pyxb.namespace.ExpandedName(Namespace, u'documentation')), min_occurs=0L, max_occurs=1)
    )
tDefinitions._GroupModel_3 = pyxb.binding.content.GroupSequence(
    pyxb.binding.content.ParticleModel(pyxb.binding.content.Wildcard(process_contents=pyxb.binding.content.Wildcard.PC_lax, namespace_constraint=(pyxb.binding.content.Wildcard.NC_not, u'http://schemas.xmlsoap.org/wsdl/')), min_occurs=0L, max_occurs=None)
    )
tDefinitions._GroupModel_ = pyxb.binding.content.GroupSequence(
    pyxb.binding.content.ParticleModel(tDefinitions._GroupModel_2, min_occurs=1, max_occurs=1),
    pyxb.binding.content.ParticleModel(tDefinitions._GroupModel_3, min_occurs=1, max_occurs=1)
    )
tDefinitions._GroupModel_5 = pyxb.binding.content.GroupChoice(
    pyxb.binding.content.ParticleModel(tDefinitions._UseForTag(pyxb.namespace.ExpandedName(Namespace, u'import')), min_occurs=1, max_occurs=1),
    pyxb.binding.content.ParticleModel(tDefinitions._UseForTag(pyxb.namespace.ExpandedName(Namespace, u'types')), min_occurs=1, max_occurs=1),
    pyxb.binding.content.ParticleModel(tDefinitions._UseForTag(pyxb.namespace.ExpandedName(Namespace, u'message')), min_occurs=1, max_occurs=1),
    pyxb.binding.content.ParticleModel(tDefinitions._UseForTag(pyxb.namespace.ExpandedName(Namespace, u'portType')), min_occurs=1, max_occurs=1),
    pyxb.binding.content.ParticleModel(tDefinitions._UseForTag(pyxb.namespace.ExpandedName(Namespace, u'binding')), min_occurs=1, max_occurs=1),
    pyxb.binding.content.ParticleModel(tDefinitions._UseForTag(pyxb.namespace.ExpandedName(Namespace, u'service')), min_occurs=1, max_occurs=1)
    )
tDefinitions._GroupModel_4 = pyxb.binding.content.GroupSequence(
    pyxb.binding.content.ParticleModel(tDefinitions._GroupModel_5, min_occurs=0L, max_occurs=None)
    )
tDefinitions._GroupModel = pyxb.binding.content.GroupSequence(
    pyxb.binding.content.ParticleModel(tDefinitions._GroupModel_, min_occurs=1, max_occurs=1),
    pyxb.binding.content.ParticleModel(tDefinitions._GroupModel_4, min_occurs=1, max_occurs=1)
    )
tDefinitions._ContentModel = pyxb.binding.content.ParticleModel(tDefinitions._GroupModel, min_occurs=1, max_occurs=1)


tImport._GroupModel = pyxb.binding.content.GroupSequence(
    pyxb.binding.content.ParticleModel(tImport._UseForTag(pyxb.namespace.ExpandedName(Namespace, u'documentation')), min_occurs=0L, max_occurs=1)
    )
tImport._ContentModel = pyxb.binding.content.ParticleModel(tImport._GroupModel, min_occurs=1, max_occurs=1)


tTypes._GroupModel_ = pyxb.binding.content.GroupSequence(
    pyxb.binding.content.ParticleModel(tTypes._UseForTag(pyxb.namespace.ExpandedName(Namespace, u'documentation')), min_occurs=0L, max_occurs=1)
    )
tTypes._GroupModel_2 = pyxb.binding.content.GroupSequence(
    pyxb.binding.content.ParticleModel(pyxb.binding.content.Wildcard(process_contents=pyxb.binding.content.Wildcard.PC_lax, namespace_constraint=(pyxb.binding.content.Wildcard.NC_not, u'http://schemas.xmlsoap.org/wsdl/')), min_occurs=0L, max_occurs=None)
    )
tTypes._GroupModel = pyxb.binding.content.GroupSequence(
    pyxb.binding.content.ParticleModel(tTypes._GroupModel_, min_occurs=1, max_occurs=1),
    pyxb.binding.content.ParticleModel(tTypes._GroupModel_2, min_occurs=1, max_occurs=1)
    )
tTypes._ContentModel = pyxb.binding.content.ParticleModel(tTypes._GroupModel, min_occurs=1, max_occurs=1)


tPort._GroupModel_ = pyxb.binding.content.GroupSequence(
    pyxb.binding.content.ParticleModel(tPort._UseForTag(pyxb.namespace.ExpandedName(Namespace, u'documentation')), min_occurs=0L, max_occurs=1)
    )
tPort._GroupModel_2 = pyxb.binding.content.GroupSequence(
    pyxb.binding.content.ParticleModel(pyxb.binding.content.Wildcard(process_contents=pyxb.binding.content.Wildcard.PC_lax, namespace_constraint=(pyxb.binding.content.Wildcard.NC_not, u'http://schemas.xmlsoap.org/wsdl/')), min_occurs=0L, max_occurs=None)
    )
tPort._GroupModel = pyxb.binding.content.GroupSequence(
    pyxb.binding.content.ParticleModel(tPort._GroupModel_, min_occurs=1, max_occurs=1),
    pyxb.binding.content.ParticleModel(tPort._GroupModel_2, min_occurs=1, max_occurs=1)
    )
tPort._ContentModel = pyxb.binding.content.ParticleModel(tPort._GroupModel, min_occurs=1, max_occurs=1)


tPart._GroupModel = pyxb.binding.content.GroupSequence(
    pyxb.binding.content.ParticleModel(tPart._UseForTag(pyxb.namespace.ExpandedName(Namespace, u'documentation')), min_occurs=0L, max_occurs=1)
    )
tPart._ContentModel = pyxb.binding.content.ParticleModel(tPart._GroupModel, min_occurs=1, max_occurs=1)
