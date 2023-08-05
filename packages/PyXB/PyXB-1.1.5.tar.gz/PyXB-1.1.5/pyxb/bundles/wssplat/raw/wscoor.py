# ./pyxb/bundles/wssplat/raw/wscoor.py
# -*- coding: utf-8 -*-
# PyXB bindings for NM:53926fc38ff5e8ef8d845111c1f3663a73eea53c
# Generated 2012-11-01 15:13:37.828881 by PyXB version 1.1.5
# Namespace http://docs.oasis-open.org/ws-tx/wscoor/2006/06

import pyxb
import pyxb.binding
import pyxb.binding.saxer
import StringIO
import pyxb.utils.utility
import pyxb.utils.domutils
import sys

# Unique identifier for bindings created at the same time
_GenerationUID = pyxb.utils.utility.UniqueIdentifier('urn:uuid:9f06f286-2460-11e2-b7f6-c8600024e903')

# Import bindings for namespaces imported into schema
import pyxb.binding.datatypes
import pyxb.bundles.wssplat.wsa

Namespace = pyxb.namespace.NamespaceForURI(u'http://docs.oasis-open.org/ws-tx/wscoor/2006/06', create_if_missing=True)
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


# Atomic simple type: {http://docs.oasis-open.org/ws-tx/wscoor/2006/06}ErrorCodes
class ErrorCodes (pyxb.binding.datatypes.QName, pyxb.binding.basis.enumeration_mixin):

    """An atomic simple type."""

    _ExpandedName = pyxb.namespace.ExpandedName(Namespace, u'ErrorCodes')
    _DefinitionLocation = pyxb.utils.utility.Location('/tmp/pyxbdist.RHB65sy/PyXB-1.1.5/pyxb/bundles/wssplat/schemas/wscoor.xsd', 87, 2)
    _Documentation = None
ErrorCodes._CF_enumeration = pyxb.binding.facets.CF_enumeration(value_datatype=ErrorCodes, enum_prefix=None)
ErrorCodes.wscoorInvalidParameters = ErrorCodes._CF_enumeration.addEnumeration(unicode_value=u'wscoor:InvalidParameters', tag=u'wscoorInvalidParameters')
ErrorCodes.wscoorInvalidProtocol = ErrorCodes._CF_enumeration.addEnumeration(unicode_value=u'wscoor:InvalidProtocol', tag=u'wscoorInvalidProtocol')
ErrorCodes.wscoorInvalidState = ErrorCodes._CF_enumeration.addEnumeration(unicode_value=u'wscoor:InvalidState', tag=u'wscoorInvalidState')
ErrorCodes.wscoorCannotCreateContext = ErrorCodes._CF_enumeration.addEnumeration(unicode_value=u'wscoor:CannotCreateContext', tag=u'wscoorCannotCreateContext')
ErrorCodes.wscoorCannotRegisterParticipant = ErrorCodes._CF_enumeration.addEnumeration(unicode_value=u'wscoor:CannotRegisterParticipant', tag=u'wscoorCannotRegisterParticipant')
ErrorCodes._InitializeFacetMap(ErrorCodes._CF_enumeration)
Namespace.addCategoryObject('typeBinding', u'ErrorCodes', ErrorCodes)

# Complex type {http://docs.oasis-open.org/ws-tx/wscoor/2006/06}CreateCoordinationContextType with content type ELEMENT_ONLY
class CreateCoordinationContextType (pyxb.binding.basis.complexTypeDefinition):
    _TypeDefinition = None
    _ContentTypeTag = pyxb.binding.basis.complexTypeDefinition._CT_ELEMENT_ONLY
    _Abstract = False
    _ExpandedName = pyxb.namespace.ExpandedName(Namespace, u'CreateCoordinationContextType')
    _DefinitionLocation = pyxb.utils.utility.Location('/tmp/pyxbdist.RHB65sy/PyXB-1.1.5/pyxb/bundles/wssplat/schemas/wscoor.xsd', 42, 2)
    # Base type is pyxb.binding.datatypes.anyType
    
    # Element {http://docs.oasis-open.org/ws-tx/wscoor/2006/06}Expires uses Python identifier Expires
    __Expires = pyxb.binding.content.ElementUse(pyxb.namespace.ExpandedName(Namespace, u'Expires'), 'Expires', '__httpdocs_oasis_open_orgws_txwscoor200606_CreateCoordinationContextType_httpdocs_oasis_open_orgws_txwscoor200606Expires', False)
    __Expires._DeclarationLocation = pyxb.utils.utility.Location('/tmp/pyxbdist.RHB65sy/PyXB-1.1.5/pyxb/bundles/wssplat/schemas/wscoor.xsd', 5, 2)
    __Expires._UseLocation = pyxb.utils.utility.Location('/tmp/pyxbdist.RHB65sy/PyXB-1.1.5/pyxb/bundles/wssplat/schemas/wscoor.xsd', 43, 4)

    
    Expires = property(__Expires.value, __Expires.set, None, None)

    
    # Element {http://docs.oasis-open.org/ws-tx/wscoor/2006/06}CurrentContext uses Python identifier CurrentContext
    __CurrentContext = pyxb.binding.content.ElementUse(pyxb.namespace.ExpandedName(Namespace, u'CurrentContext'), 'CurrentContext', '__httpdocs_oasis_open_orgws_txwscoor200606_CreateCoordinationContextType_httpdocs_oasis_open_orgws_txwscoor200606CurrentContext', False)
    __CurrentContext._DeclarationLocation = pyxb.utils.utility.Location('/tmp/pyxbdist.RHB65sy/PyXB-1.1.5/pyxb/bundles/wssplat/schemas/wscoor.xsd', 45, 6)
    __CurrentContext._UseLocation = pyxb.utils.utility.Location('/tmp/pyxbdist.RHB65sy/PyXB-1.1.5/pyxb/bundles/wssplat/schemas/wscoor.xsd', 43, 4)

    
    CurrentContext = property(__CurrentContext.value, __CurrentContext.set, None, None)

    
    # Element {http://docs.oasis-open.org/ws-tx/wscoor/2006/06}CoordinationType uses Python identifier CoordinationType
    __CoordinationType = pyxb.binding.content.ElementUse(pyxb.namespace.ExpandedName(Namespace, u'CoordinationType'), 'CoordinationType', '__httpdocs_oasis_open_orgws_txwscoor200606_CreateCoordinationContextType_httpdocs_oasis_open_orgws_txwscoor200606CoordinationType', False)
    __CoordinationType._DeclarationLocation = pyxb.utils.utility.Location('/tmp/pyxbdist.RHB65sy/PyXB-1.1.5/pyxb/bundles/wssplat/schemas/wscoor.xsd', 56, 6)
    __CoordinationType._UseLocation = pyxb.utils.utility.Location('/tmp/pyxbdist.RHB65sy/PyXB-1.1.5/pyxb/bundles/wssplat/schemas/wscoor.xsd', 43, 4)

    
    CoordinationType = property(__CoordinationType.value, __CoordinationType.set, None, None)

    _AttributeWildcard = pyxb.binding.content.Wildcard(process_contents=pyxb.binding.content.Wildcard.PC_lax, namespace_constraint=(pyxb.binding.content.Wildcard.NC_not, u'http://docs.oasis-open.org/ws-tx/wscoor/2006/06'))
    _HasWildcardElement = True

    _ElementMap = {
        __Expires.name() : __Expires,
        __CurrentContext.name() : __CurrentContext,
        __CoordinationType.name() : __CoordinationType
    }
    _AttributeMap = {
        
    }
Namespace.addCategoryObject('typeBinding', u'CreateCoordinationContextType', CreateCoordinationContextType)


# Complex type {http://docs.oasis-open.org/ws-tx/wscoor/2006/06}RegisterType with content type ELEMENT_ONLY
class RegisterType (pyxb.binding.basis.complexTypeDefinition):
    _TypeDefinition = None
    _ContentTypeTag = pyxb.binding.basis.complexTypeDefinition._CT_ELEMENT_ONLY
    _Abstract = False
    _ExpandedName = pyxb.namespace.ExpandedName(Namespace, u'RegisterType')
    _DefinitionLocation = pyxb.utils.utility.Location('/tmp/pyxbdist.RHB65sy/PyXB-1.1.5/pyxb/bundles/wssplat/schemas/wscoor.xsd', 70, 2)
    # Base type is pyxb.binding.datatypes.anyType
    
    # Element {http://docs.oasis-open.org/ws-tx/wscoor/2006/06}ProtocolIdentifier uses Python identifier ProtocolIdentifier
    __ProtocolIdentifier = pyxb.binding.content.ElementUse(pyxb.namespace.ExpandedName(Namespace, u'ProtocolIdentifier'), 'ProtocolIdentifier', '__httpdocs_oasis_open_orgws_txwscoor200606_RegisterType_httpdocs_oasis_open_orgws_txwscoor200606ProtocolIdentifier', False)
    __ProtocolIdentifier._DeclarationLocation = pyxb.utils.utility.Location('/tmp/pyxbdist.RHB65sy/PyXB-1.1.5/pyxb/bundles/wssplat/schemas/wscoor.xsd', 72, 6)
    __ProtocolIdentifier._UseLocation = pyxb.utils.utility.Location('/tmp/pyxbdist.RHB65sy/PyXB-1.1.5/pyxb/bundles/wssplat/schemas/wscoor.xsd', 71, 4)

    
    ProtocolIdentifier = property(__ProtocolIdentifier.value, __ProtocolIdentifier.set, None, None)

    
    # Element {http://docs.oasis-open.org/ws-tx/wscoor/2006/06}ParticipantProtocolService uses Python identifier ParticipantProtocolService
    __ParticipantProtocolService = pyxb.binding.content.ElementUse(pyxb.namespace.ExpandedName(Namespace, u'ParticipantProtocolService'), 'ParticipantProtocolService', '__httpdocs_oasis_open_orgws_txwscoor200606_RegisterType_httpdocs_oasis_open_orgws_txwscoor200606ParticipantProtocolService', False)
    __ParticipantProtocolService._DeclarationLocation = pyxb.utils.utility.Location('/tmp/pyxbdist.RHB65sy/PyXB-1.1.5/pyxb/bundles/wssplat/schemas/wscoor.xsd', 73, 6)
    __ParticipantProtocolService._UseLocation = pyxb.utils.utility.Location('/tmp/pyxbdist.RHB65sy/PyXB-1.1.5/pyxb/bundles/wssplat/schemas/wscoor.xsd', 71, 4)

    
    ParticipantProtocolService = property(__ParticipantProtocolService.value, __ParticipantProtocolService.set, None, None)

    _AttributeWildcard = pyxb.binding.content.Wildcard(process_contents=pyxb.binding.content.Wildcard.PC_lax, namespace_constraint=(pyxb.binding.content.Wildcard.NC_not, u'http://docs.oasis-open.org/ws-tx/wscoor/2006/06'))
    _HasWildcardElement = True

    _ElementMap = {
        __ProtocolIdentifier.name() : __ProtocolIdentifier,
        __ParticipantProtocolService.name() : __ParticipantProtocolService
    }
    _AttributeMap = {
        
    }
Namespace.addCategoryObject('typeBinding', u'RegisterType', RegisterType)


# Complex type {http://docs.oasis-open.org/ws-tx/wscoor/2006/06}RegisterResponseType with content type ELEMENT_ONLY
class RegisterResponseType (pyxb.binding.basis.complexTypeDefinition):
    _TypeDefinition = None
    _ContentTypeTag = pyxb.binding.basis.complexTypeDefinition._CT_ELEMENT_ONLY
    _Abstract = False
    _ExpandedName = pyxb.namespace.ExpandedName(Namespace, u'RegisterResponseType')
    _DefinitionLocation = pyxb.utils.utility.Location('/tmp/pyxbdist.RHB65sy/PyXB-1.1.5/pyxb/bundles/wssplat/schemas/wscoor.xsd', 79, 2)
    # Base type is pyxb.binding.datatypes.anyType
    
    # Element {http://docs.oasis-open.org/ws-tx/wscoor/2006/06}CoordinatorProtocolService uses Python identifier CoordinatorProtocolService
    __CoordinatorProtocolService = pyxb.binding.content.ElementUse(pyxb.namespace.ExpandedName(Namespace, u'CoordinatorProtocolService'), 'CoordinatorProtocolService', '__httpdocs_oasis_open_orgws_txwscoor200606_RegisterResponseType_httpdocs_oasis_open_orgws_txwscoor200606CoordinatorProtocolService', False)
    __CoordinatorProtocolService._DeclarationLocation = pyxb.utils.utility.Location('/tmp/pyxbdist.RHB65sy/PyXB-1.1.5/pyxb/bundles/wssplat/schemas/wscoor.xsd', 81, 6)
    __CoordinatorProtocolService._UseLocation = pyxb.utils.utility.Location('/tmp/pyxbdist.RHB65sy/PyXB-1.1.5/pyxb/bundles/wssplat/schemas/wscoor.xsd', 80, 4)

    
    CoordinatorProtocolService = property(__CoordinatorProtocolService.value, __CoordinatorProtocolService.set, None, None)

    _AttributeWildcard = pyxb.binding.content.Wildcard(process_contents=pyxb.binding.content.Wildcard.PC_lax, namespace_constraint=(pyxb.binding.content.Wildcard.NC_not, u'http://docs.oasis-open.org/ws-tx/wscoor/2006/06'))
    _HasWildcardElement = True

    _ElementMap = {
        __CoordinatorProtocolService.name() : __CoordinatorProtocolService
    }
    _AttributeMap = {
        
    }
Namespace.addCategoryObject('typeBinding', u'RegisterResponseType', RegisterResponseType)


# Complex type [anonymous] with content type SIMPLE
class CTD_ANON (pyxb.binding.basis.complexTypeDefinition):
    _TypeDefinition = pyxb.binding.datatypes.unsignedInt
    _ContentTypeTag = pyxb.binding.basis.complexTypeDefinition._CT_SIMPLE
    _Abstract = False
    _ExpandedName = None
    _DefinitionLocation = pyxb.utils.utility.Location('/tmp/pyxbdist.RHB65sy/PyXB-1.1.5/pyxb/bundles/wssplat/schemas/wscoor.xsd', 6, 4)
    # Base type is pyxb.binding.datatypes.unsignedInt
    _AttributeWildcard = pyxb.binding.content.Wildcard(process_contents=pyxb.binding.content.Wildcard.PC_strict, namespace_constraint=(pyxb.binding.content.Wildcard.NC_not, u'http://docs.oasis-open.org/ws-tx/wscoor/2006/06'))

    _ElementMap = {
        
    }
    _AttributeMap = {
        
    }



# Complex type {http://docs.oasis-open.org/ws-tx/wscoor/2006/06}CoordinationContextType with content type ELEMENT_ONLY
class CoordinationContextType (pyxb.binding.basis.complexTypeDefinition):
    _TypeDefinition = None
    _ContentTypeTag = pyxb.binding.basis.complexTypeDefinition._CT_ELEMENT_ONLY
    _Abstract = False
    _ExpandedName = pyxb.namespace.ExpandedName(Namespace, u'CoordinationContextType')
    _DefinitionLocation = pyxb.utils.utility.Location('/tmp/pyxbdist.RHB65sy/PyXB-1.1.5/pyxb/bundles/wssplat/schemas/wscoor.xsd', 14, 2)
    # Base type is pyxb.binding.datatypes.anyType
    
    # Element {http://docs.oasis-open.org/ws-tx/wscoor/2006/06}CoordinationType uses Python identifier CoordinationType
    __CoordinationType = pyxb.binding.content.ElementUse(pyxb.namespace.ExpandedName(Namespace, u'CoordinationType'), 'CoordinationType', '__httpdocs_oasis_open_orgws_txwscoor200606_CoordinationContextType_httpdocs_oasis_open_orgws_txwscoor200606CoordinationType', False)
    __CoordinationType._DeclarationLocation = pyxb.utils.utility.Location('/tmp/pyxbdist.RHB65sy/PyXB-1.1.5/pyxb/bundles/wssplat/schemas/wscoor.xsd', 26, 6)
    __CoordinationType._UseLocation = pyxb.utils.utility.Location('/tmp/pyxbdist.RHB65sy/PyXB-1.1.5/pyxb/bundles/wssplat/schemas/wscoor.xsd', 15, 4)

    
    CoordinationType = property(__CoordinationType.value, __CoordinationType.set, None, None)

    
    # Element {http://docs.oasis-open.org/ws-tx/wscoor/2006/06}Expires uses Python identifier Expires
    __Expires = pyxb.binding.content.ElementUse(pyxb.namespace.ExpandedName(Namespace, u'Expires'), 'Expires', '__httpdocs_oasis_open_orgws_txwscoor200606_CoordinationContextType_httpdocs_oasis_open_orgws_txwscoor200606Expires', False)
    __Expires._DeclarationLocation = pyxb.utils.utility.Location('/tmp/pyxbdist.RHB65sy/PyXB-1.1.5/pyxb/bundles/wssplat/schemas/wscoor.xsd', 5, 2)
    __Expires._UseLocation = pyxb.utils.utility.Location('/tmp/pyxbdist.RHB65sy/PyXB-1.1.5/pyxb/bundles/wssplat/schemas/wscoor.xsd', 15, 4)

    
    Expires = property(__Expires.value, __Expires.set, None, None)

    
    # Element {http://docs.oasis-open.org/ws-tx/wscoor/2006/06}Identifier uses Python identifier Identifier
    __Identifier = pyxb.binding.content.ElementUse(pyxb.namespace.ExpandedName(Namespace, u'Identifier'), 'Identifier', '__httpdocs_oasis_open_orgws_txwscoor200606_CoordinationContextType_httpdocs_oasis_open_orgws_txwscoor200606Identifier', False)
    __Identifier._DeclarationLocation = pyxb.utils.utility.Location('/tmp/pyxbdist.RHB65sy/PyXB-1.1.5/pyxb/bundles/wssplat/schemas/wscoor.xsd', 16, 6)
    __Identifier._UseLocation = pyxb.utils.utility.Location('/tmp/pyxbdist.RHB65sy/PyXB-1.1.5/pyxb/bundles/wssplat/schemas/wscoor.xsd', 15, 4)

    
    Identifier = property(__Identifier.value, __Identifier.set, None, None)

    
    # Element {http://docs.oasis-open.org/ws-tx/wscoor/2006/06}RegistrationService uses Python identifier RegistrationService
    __RegistrationService = pyxb.binding.content.ElementUse(pyxb.namespace.ExpandedName(Namespace, u'RegistrationService'), 'RegistrationService', '__httpdocs_oasis_open_orgws_txwscoor200606_CoordinationContextType_httpdocs_oasis_open_orgws_txwscoor200606RegistrationService', False)
    __RegistrationService._DeclarationLocation = pyxb.utils.utility.Location('/tmp/pyxbdist.RHB65sy/PyXB-1.1.5/pyxb/bundles/wssplat/schemas/wscoor.xsd', 27, 6)
    __RegistrationService._UseLocation = pyxb.utils.utility.Location('/tmp/pyxbdist.RHB65sy/PyXB-1.1.5/pyxb/bundles/wssplat/schemas/wscoor.xsd', 15, 4)

    
    RegistrationService = property(__RegistrationService.value, __RegistrationService.set, None, None)

    _AttributeWildcard = pyxb.binding.content.Wildcard(process_contents=pyxb.binding.content.Wildcard.PC_lax, namespace_constraint=(pyxb.binding.content.Wildcard.NC_not, u'http://docs.oasis-open.org/ws-tx/wscoor/2006/06'))

    _ElementMap = {
        __CoordinationType.name() : __CoordinationType,
        __Expires.name() : __Expires,
        __Identifier.name() : __Identifier,
        __RegistrationService.name() : __RegistrationService
    }
    _AttributeMap = {
        
    }
Namespace.addCategoryObject('typeBinding', u'CoordinationContextType', CoordinationContextType)


# Complex type [anonymous] with content type ELEMENT_ONLY
class CTD_ANON_ (CoordinationContextType):
    _TypeDefinition = None
    _ContentTypeTag = pyxb.binding.basis.complexTypeDefinition._CT_ELEMENT_ONLY
    _Abstract = False
    _ExpandedName = None
    _DefinitionLocation = pyxb.utils.utility.Location('/tmp/pyxbdist.RHB65sy/PyXB-1.1.5/pyxb/bundles/wssplat/schemas/wscoor.xsd', 32, 4)
    # Base type is CoordinationContextType
    
    # Element CoordinationType ({http://docs.oasis-open.org/ws-tx/wscoor/2006/06}CoordinationType) inherited from {http://docs.oasis-open.org/ws-tx/wscoor/2006/06}CoordinationContextType
    
    # Element Expires ({http://docs.oasis-open.org/ws-tx/wscoor/2006/06}Expires) inherited from {http://docs.oasis-open.org/ws-tx/wscoor/2006/06}CoordinationContextType
    
    # Element Identifier ({http://docs.oasis-open.org/ws-tx/wscoor/2006/06}Identifier) inherited from {http://docs.oasis-open.org/ws-tx/wscoor/2006/06}CoordinationContextType
    
    # Element RegistrationService ({http://docs.oasis-open.org/ws-tx/wscoor/2006/06}RegistrationService) inherited from {http://docs.oasis-open.org/ws-tx/wscoor/2006/06}CoordinationContextType
    _AttributeWildcard = pyxb.binding.content.Wildcard(process_contents=pyxb.binding.content.Wildcard.PC_lax, namespace_constraint=(pyxb.binding.content.Wildcard.NC_not, u'http://docs.oasis-open.org/ws-tx/wscoor/2006/06'))
    _HasWildcardElement = True

    _ElementMap = CoordinationContextType._ElementMap.copy()
    _ElementMap.update({
        
    })
    _AttributeMap = CoordinationContextType._AttributeMap.copy()
    _AttributeMap.update({
        
    })



# Complex type [anonymous] with content type ELEMENT_ONLY
class CTD_ANON_2 (CoordinationContextType):
    _TypeDefinition = None
    _ContentTypeTag = pyxb.binding.basis.complexTypeDefinition._CT_ELEMENT_ONLY
    _Abstract = False
    _ExpandedName = None
    _DefinitionLocation = pyxb.utils.utility.Location('/tmp/pyxbdist.RHB65sy/PyXB-1.1.5/pyxb/bundles/wssplat/schemas/wscoor.xsd', 46, 8)
    # Base type is CoordinationContextType
    
    # Element CoordinationType ({http://docs.oasis-open.org/ws-tx/wscoor/2006/06}CoordinationType) inherited from {http://docs.oasis-open.org/ws-tx/wscoor/2006/06}CoordinationContextType
    
    # Element Expires ({http://docs.oasis-open.org/ws-tx/wscoor/2006/06}Expires) inherited from {http://docs.oasis-open.org/ws-tx/wscoor/2006/06}CoordinationContextType
    
    # Element Identifier ({http://docs.oasis-open.org/ws-tx/wscoor/2006/06}Identifier) inherited from {http://docs.oasis-open.org/ws-tx/wscoor/2006/06}CoordinationContextType
    
    # Element RegistrationService ({http://docs.oasis-open.org/ws-tx/wscoor/2006/06}RegistrationService) inherited from {http://docs.oasis-open.org/ws-tx/wscoor/2006/06}CoordinationContextType
    _AttributeWildcard = pyxb.binding.content.Wildcard(process_contents=pyxb.binding.content.Wildcard.PC_lax, namespace_constraint=(pyxb.binding.content.Wildcard.NC_not, u'http://docs.oasis-open.org/ws-tx/wscoor/2006/06'))
    _HasWildcardElement = True

    _ElementMap = CoordinationContextType._ElementMap.copy()
    _ElementMap.update({
        
    })
    _AttributeMap = CoordinationContextType._AttributeMap.copy()
    _AttributeMap.update({
        
    })



# Complex type [anonymous] with content type SIMPLE
class CTD_ANON_3 (pyxb.binding.basis.complexTypeDefinition):
    _TypeDefinition = pyxb.binding.datatypes.anyURI
    _ContentTypeTag = pyxb.binding.basis.complexTypeDefinition._CT_SIMPLE
    _Abstract = False
    _ExpandedName = None
    _DefinitionLocation = pyxb.utils.utility.Location('/tmp/pyxbdist.RHB65sy/PyXB-1.1.5/pyxb/bundles/wssplat/schemas/wscoor.xsd', 17, 8)
    # Base type is pyxb.binding.datatypes.anyURI
    _AttributeWildcard = pyxb.binding.content.Wildcard(process_contents=pyxb.binding.content.Wildcard.PC_strict, namespace_constraint=(pyxb.binding.content.Wildcard.NC_not, u'http://docs.oasis-open.org/ws-tx/wscoor/2006/06'))

    _ElementMap = {
        
    }
    _AttributeMap = {
        
    }



# Complex type {http://docs.oasis-open.org/ws-tx/wscoor/2006/06}CreateCoordinationContextResponseType with content type ELEMENT_ONLY
class CreateCoordinationContextResponseType (pyxb.binding.basis.complexTypeDefinition):
    _TypeDefinition = None
    _ContentTypeTag = pyxb.binding.basis.complexTypeDefinition._CT_ELEMENT_ONLY
    _Abstract = False
    _ExpandedName = pyxb.namespace.ExpandedName(Namespace, u'CreateCoordinationContextResponseType')
    _DefinitionLocation = pyxb.utils.utility.Location('/tmp/pyxbdist.RHB65sy/PyXB-1.1.5/pyxb/bundles/wssplat/schemas/wscoor.xsd', 62, 2)
    # Base type is pyxb.binding.datatypes.anyType
    
    # Element {http://docs.oasis-open.org/ws-tx/wscoor/2006/06}CoordinationContext uses Python identifier CoordinationContext
    __CoordinationContext = pyxb.binding.content.ElementUse(pyxb.namespace.ExpandedName(Namespace, u'CoordinationContext'), 'CoordinationContext', '__httpdocs_oasis_open_orgws_txwscoor200606_CreateCoordinationContextResponseType_httpdocs_oasis_open_orgws_txwscoor200606CoordinationContext', False)
    __CoordinationContext._DeclarationLocation = pyxb.utils.utility.Location('/tmp/pyxbdist.RHB65sy/PyXB-1.1.5/pyxb/bundles/wssplat/schemas/wscoor.xsd', 31, 2)
    __CoordinationContext._UseLocation = pyxb.utils.utility.Location('/tmp/pyxbdist.RHB65sy/PyXB-1.1.5/pyxb/bundles/wssplat/schemas/wscoor.xsd', 63, 4)

    
    CoordinationContext = property(__CoordinationContext.value, __CoordinationContext.set, None, None)

    _AttributeWildcard = pyxb.binding.content.Wildcard(process_contents=pyxb.binding.content.Wildcard.PC_lax, namespace_constraint=(pyxb.binding.content.Wildcard.NC_not, u'http://docs.oasis-open.org/ws-tx/wscoor/2006/06'))
    _HasWildcardElement = True

    _ElementMap = {
        __CoordinationContext.name() : __CoordinationContext
    }
    _AttributeMap = {
        
    }
Namespace.addCategoryObject('typeBinding', u'CreateCoordinationContextResponseType', CreateCoordinationContextResponseType)


CreateCoordinationContext = pyxb.binding.basis.element(pyxb.namespace.ExpandedName(Namespace, u'CreateCoordinationContext'), CreateCoordinationContextType)
Namespace.addCategoryObject('elementBinding', CreateCoordinationContext.name().localName(), CreateCoordinationContext)

Register = pyxb.binding.basis.element(pyxb.namespace.ExpandedName(Namespace, u'Register'), RegisterType)
Namespace.addCategoryObject('elementBinding', Register.name().localName(), Register)

RegisterResponse = pyxb.binding.basis.element(pyxb.namespace.ExpandedName(Namespace, u'RegisterResponse'), RegisterResponseType)
Namespace.addCategoryObject('elementBinding', RegisterResponse.name().localName(), RegisterResponse)

Expires = pyxb.binding.basis.element(pyxb.namespace.ExpandedName(Namespace, u'Expires'), CTD_ANON)
Namespace.addCategoryObject('elementBinding', Expires.name().localName(), Expires)

CoordinationContext = pyxb.binding.basis.element(pyxb.namespace.ExpandedName(Namespace, u'CoordinationContext'), CTD_ANON_)
Namespace.addCategoryObject('elementBinding', CoordinationContext.name().localName(), CoordinationContext)

CreateCoordinationContextResponse = pyxb.binding.basis.element(pyxb.namespace.ExpandedName(Namespace, u'CreateCoordinationContextResponse'), CreateCoordinationContextResponseType)
Namespace.addCategoryObject('elementBinding', CreateCoordinationContextResponse.name().localName(), CreateCoordinationContextResponse)



CreateCoordinationContextType._AddElement(pyxb.binding.basis.element(pyxb.namespace.ExpandedName(Namespace, u'Expires'), CTD_ANON, scope=CreateCoordinationContextType))

CreateCoordinationContextType._AddElement(pyxb.binding.basis.element(pyxb.namespace.ExpandedName(Namespace, u'CurrentContext'), CTD_ANON_2, scope=CreateCoordinationContextType))

CreateCoordinationContextType._AddElement(pyxb.binding.basis.element(pyxb.namespace.ExpandedName(Namespace, u'CoordinationType'), pyxb.binding.datatypes.anyURI, scope=CreateCoordinationContextType))
CreateCoordinationContextType._GroupModel = pyxb.binding.content.GroupSequence(
    pyxb.binding.content.ParticleModel(CreateCoordinationContextType._UseForTag(pyxb.namespace.ExpandedName(Namespace, u'Expires')), min_occurs=0L, max_occurs=1),
    pyxb.binding.content.ParticleModel(CreateCoordinationContextType._UseForTag(pyxb.namespace.ExpandedName(Namespace, u'CurrentContext')), min_occurs=0L, max_occurs=1),
    pyxb.binding.content.ParticleModel(CreateCoordinationContextType._UseForTag(pyxb.namespace.ExpandedName(Namespace, u'CoordinationType')), min_occurs=1, max_occurs=1),
    pyxb.binding.content.ParticleModel(pyxb.binding.content.Wildcard(process_contents=pyxb.binding.content.Wildcard.PC_lax, namespace_constraint=pyxb.binding.content.Wildcard.NC_any), min_occurs=0L, max_occurs=None)
    )
CreateCoordinationContextType._ContentModel = pyxb.binding.content.ParticleModel(CreateCoordinationContextType._GroupModel, min_occurs=1, max_occurs=1)



RegisterType._AddElement(pyxb.binding.basis.element(pyxb.namespace.ExpandedName(Namespace, u'ProtocolIdentifier'), pyxb.binding.datatypes.anyURI, scope=RegisterType))

RegisterType._AddElement(pyxb.binding.basis.element(pyxb.namespace.ExpandedName(Namespace, u'ParticipantProtocolService'), pyxb.bundles.wssplat.wsa.EndpointReferenceType, scope=RegisterType))
RegisterType._GroupModel = pyxb.binding.content.GroupSequence(
    pyxb.binding.content.ParticleModel(RegisterType._UseForTag(pyxb.namespace.ExpandedName(Namespace, u'ProtocolIdentifier')), min_occurs=1, max_occurs=1),
    pyxb.binding.content.ParticleModel(RegisterType._UseForTag(pyxb.namespace.ExpandedName(Namespace, u'ParticipantProtocolService')), min_occurs=1, max_occurs=1),
    pyxb.binding.content.ParticleModel(pyxb.binding.content.Wildcard(process_contents=pyxb.binding.content.Wildcard.PC_lax, namespace_constraint=pyxb.binding.content.Wildcard.NC_any), min_occurs=0L, max_occurs=None)
    )
RegisterType._ContentModel = pyxb.binding.content.ParticleModel(RegisterType._GroupModel, min_occurs=1, max_occurs=1)



RegisterResponseType._AddElement(pyxb.binding.basis.element(pyxb.namespace.ExpandedName(Namespace, u'CoordinatorProtocolService'), pyxb.bundles.wssplat.wsa.EndpointReferenceType, scope=RegisterResponseType))
RegisterResponseType._GroupModel = pyxb.binding.content.GroupSequence(
    pyxb.binding.content.ParticleModel(RegisterResponseType._UseForTag(pyxb.namespace.ExpandedName(Namespace, u'CoordinatorProtocolService')), min_occurs=1, max_occurs=1),
    pyxb.binding.content.ParticleModel(pyxb.binding.content.Wildcard(process_contents=pyxb.binding.content.Wildcard.PC_lax, namespace_constraint=pyxb.binding.content.Wildcard.NC_any), min_occurs=0L, max_occurs=None)
    )
RegisterResponseType._ContentModel = pyxb.binding.content.ParticleModel(RegisterResponseType._GroupModel, min_occurs=1, max_occurs=1)



CoordinationContextType._AddElement(pyxb.binding.basis.element(pyxb.namespace.ExpandedName(Namespace, u'CoordinationType'), pyxb.binding.datatypes.anyURI, scope=CoordinationContextType))

CoordinationContextType._AddElement(pyxb.binding.basis.element(pyxb.namespace.ExpandedName(Namespace, u'Expires'), CTD_ANON, scope=CoordinationContextType))

CoordinationContextType._AddElement(pyxb.binding.basis.element(pyxb.namespace.ExpandedName(Namespace, u'Identifier'), CTD_ANON_3, scope=CoordinationContextType))

CoordinationContextType._AddElement(pyxb.binding.basis.element(pyxb.namespace.ExpandedName(Namespace, u'RegistrationService'), pyxb.bundles.wssplat.wsa.EndpointReferenceType, scope=CoordinationContextType))
CoordinationContextType._GroupModel = pyxb.binding.content.GroupSequence(
    pyxb.binding.content.ParticleModel(CoordinationContextType._UseForTag(pyxb.namespace.ExpandedName(Namespace, u'Identifier')), min_occurs=1, max_occurs=1),
    pyxb.binding.content.ParticleModel(CoordinationContextType._UseForTag(pyxb.namespace.ExpandedName(Namespace, u'Expires')), min_occurs=0L, max_occurs=1),
    pyxb.binding.content.ParticleModel(CoordinationContextType._UseForTag(pyxb.namespace.ExpandedName(Namespace, u'CoordinationType')), min_occurs=1, max_occurs=1),
    pyxb.binding.content.ParticleModel(CoordinationContextType._UseForTag(pyxb.namespace.ExpandedName(Namespace, u'RegistrationService')), min_occurs=1, max_occurs=1)
    )
CoordinationContextType._ContentModel = pyxb.binding.content.ParticleModel(CoordinationContextType._GroupModel, min_occurs=1, max_occurs=1)


CTD_ANON_._GroupModel_ = pyxb.binding.content.GroupSequence(
    pyxb.binding.content.ParticleModel(CTD_ANON_._UseForTag(pyxb.namespace.ExpandedName(Namespace, u'Identifier')), min_occurs=1, max_occurs=1),
    pyxb.binding.content.ParticleModel(CTD_ANON_._UseForTag(pyxb.namespace.ExpandedName(Namespace, u'Expires')), min_occurs=0L, max_occurs=1),
    pyxb.binding.content.ParticleModel(CTD_ANON_._UseForTag(pyxb.namespace.ExpandedName(Namespace, u'CoordinationType')), min_occurs=1, max_occurs=1),
    pyxb.binding.content.ParticleModel(CTD_ANON_._UseForTag(pyxb.namespace.ExpandedName(Namespace, u'RegistrationService')), min_occurs=1, max_occurs=1)
    )
CTD_ANON_._GroupModel_2 = pyxb.binding.content.GroupSequence(
    pyxb.binding.content.ParticleModel(pyxb.binding.content.Wildcard(process_contents=pyxb.binding.content.Wildcard.PC_lax, namespace_constraint=(pyxb.binding.content.Wildcard.NC_not, u'http://docs.oasis-open.org/ws-tx/wscoor/2006/06')), min_occurs=0L, max_occurs=None)
    )
CTD_ANON_._GroupModel = pyxb.binding.content.GroupSequence(
    pyxb.binding.content.ParticleModel(CTD_ANON_._GroupModel_, min_occurs=1, max_occurs=1),
    pyxb.binding.content.ParticleModel(CTD_ANON_._GroupModel_2, min_occurs=1, max_occurs=1)
    )
CTD_ANON_._ContentModel = pyxb.binding.content.ParticleModel(CTD_ANON_._GroupModel, min_occurs=1, max_occurs=1)


CTD_ANON_2._GroupModel_ = pyxb.binding.content.GroupSequence(
    pyxb.binding.content.ParticleModel(CTD_ANON_2._UseForTag(pyxb.namespace.ExpandedName(Namespace, u'Identifier')), min_occurs=1, max_occurs=1),
    pyxb.binding.content.ParticleModel(CTD_ANON_2._UseForTag(pyxb.namespace.ExpandedName(Namespace, u'Expires')), min_occurs=0L, max_occurs=1),
    pyxb.binding.content.ParticleModel(CTD_ANON_2._UseForTag(pyxb.namespace.ExpandedName(Namespace, u'CoordinationType')), min_occurs=1, max_occurs=1),
    pyxb.binding.content.ParticleModel(CTD_ANON_2._UseForTag(pyxb.namespace.ExpandedName(Namespace, u'RegistrationService')), min_occurs=1, max_occurs=1)
    )
CTD_ANON_2._GroupModel_2 = pyxb.binding.content.GroupSequence(
    pyxb.binding.content.ParticleModel(pyxb.binding.content.Wildcard(process_contents=pyxb.binding.content.Wildcard.PC_lax, namespace_constraint=(pyxb.binding.content.Wildcard.NC_not, u'http://docs.oasis-open.org/ws-tx/wscoor/2006/06')), min_occurs=0L, max_occurs=None)
    )
CTD_ANON_2._GroupModel = pyxb.binding.content.GroupSequence(
    pyxb.binding.content.ParticleModel(CTD_ANON_2._GroupModel_, min_occurs=1, max_occurs=1),
    pyxb.binding.content.ParticleModel(CTD_ANON_2._GroupModel_2, min_occurs=1, max_occurs=1)
    )
CTD_ANON_2._ContentModel = pyxb.binding.content.ParticleModel(CTD_ANON_2._GroupModel, min_occurs=0L, max_occurs=1)



CreateCoordinationContextResponseType._AddElement(pyxb.binding.basis.element(pyxb.namespace.ExpandedName(Namespace, u'CoordinationContext'), CTD_ANON_, scope=CreateCoordinationContextResponseType))
CreateCoordinationContextResponseType._GroupModel = pyxb.binding.content.GroupSequence(
    pyxb.binding.content.ParticleModel(CreateCoordinationContextResponseType._UseForTag(pyxb.namespace.ExpandedName(Namespace, u'CoordinationContext')), min_occurs=1, max_occurs=1),
    pyxb.binding.content.ParticleModel(pyxb.binding.content.Wildcard(process_contents=pyxb.binding.content.Wildcard.PC_lax, namespace_constraint=(pyxb.binding.content.Wildcard.NC_not, u'http://docs.oasis-open.org/ws-tx/wscoor/2006/06')), min_occurs=0L, max_occurs=None)
    )
CreateCoordinationContextResponseType._ContentModel = pyxb.binding.content.ParticleModel(CreateCoordinationContextResponseType._GroupModel, min_occurs=1, max_occurs=1)
