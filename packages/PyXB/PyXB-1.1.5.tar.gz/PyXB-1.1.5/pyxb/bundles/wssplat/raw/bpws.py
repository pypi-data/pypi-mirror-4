# ./pyxb/bundles/wssplat/raw/bpws.py
# -*- coding: utf-8 -*-
# PyXB bindings for NM:157fc4d84d91f9f337276fbd45fc8a0cd667f150
# Generated 2012-11-01 15:13:33.763679 by PyXB version 1.1.5
# Namespace http://schemas.xmlsoap.org/ws/2003/03/business-process/

import pyxb
import pyxb.binding
import pyxb.binding.saxer
import StringIO
import pyxb.utils.utility
import pyxb.utils.domutils
import sys

# Unique identifier for bindings created at the same time
_GenerationUID = pyxb.utils.utility.UniqueIdentifier('urn:uuid:9c8c5fdc-2460-11e2-b8a0-c8600024e903')

# Import bindings for namespaces imported into schema
import pyxb.binding.datatypes

Namespace = pyxb.namespace.NamespaceForURI(u'http://schemas.xmlsoap.org/ws/2003/03/business-process/', create_if_missing=True)
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


# Atomic simple type: {http://schemas.xmlsoap.org/ws/2003/03/business-process/}tBoolean
class tBoolean (pyxb.binding.datatypes.string, pyxb.binding.basis.enumeration_mixin):

    """An atomic simple type."""

    _ExpandedName = pyxb.namespace.ExpandedName(Namespace, u'tBoolean')
    _DefinitionLocation = pyxb.utils.utility.Location('/tmp/pyxbdist.RHB65sy/PyXB-1.1.5/pyxb/bundles/wssplat/schemas/bpws.xsd', 666, 4)
    _Documentation = None
tBoolean._CF_enumeration = pyxb.binding.facets.CF_enumeration(value_datatype=tBoolean, enum_prefix=None)
tBoolean.yes = tBoolean._CF_enumeration.addEnumeration(unicode_value=u'yes', tag=u'yes')
tBoolean.no = tBoolean._CF_enumeration.addEnumeration(unicode_value=u'no', tag=u'no')
tBoolean._InitializeFacetMap(tBoolean._CF_enumeration)
Namespace.addCategoryObject('typeBinding', u'tBoolean', tBoolean)

# Atomic simple type: {http://schemas.xmlsoap.org/ws/2003/03/business-process/}tBoolean-expr
class tBoolean_expr (pyxb.binding.datatypes.string):

    """An atomic simple type."""

    _ExpandedName = pyxb.namespace.ExpandedName(Namespace, u'tBoolean-expr')
    _DefinitionLocation = pyxb.utils.utility.Location('/tmp/pyxbdist.RHB65sy/PyXB-1.1.5/pyxb/bundles/wssplat/schemas/bpws.xsd', 654, 4)
    _Documentation = None
tBoolean_expr._InitializeFacetMap()
Namespace.addCategoryObject('typeBinding', u'tBoolean-expr', tBoolean_expr)

# Atomic simple type: {http://schemas.xmlsoap.org/ws/2003/03/business-process/}tDeadline-expr
class tDeadline_expr (pyxb.binding.datatypes.string):

    """An atomic simple type."""

    _ExpandedName = pyxb.namespace.ExpandedName(Namespace, u'tDeadline-expr')
    _DefinitionLocation = pyxb.utils.utility.Location('/tmp/pyxbdist.RHB65sy/PyXB-1.1.5/pyxb/bundles/wssplat/schemas/bpws.xsd', 662, 4)
    _Documentation = None
tDeadline_expr._InitializeFacetMap()
Namespace.addCategoryObject('typeBinding', u'tDeadline-expr', tDeadline_expr)

# Atomic simple type: {http://schemas.xmlsoap.org/ws/2003/03/business-process/}tDuration-expr
class tDuration_expr (pyxb.binding.datatypes.string):

    """An atomic simple type."""

    _ExpandedName = pyxb.namespace.ExpandedName(Namespace, u'tDuration-expr')
    _DefinitionLocation = pyxb.utils.utility.Location('/tmp/pyxbdist.RHB65sy/PyXB-1.1.5/pyxb/bundles/wssplat/schemas/bpws.xsd', 658, 4)
    _Documentation = None
tDuration_expr._InitializeFacetMap()
Namespace.addCategoryObject('typeBinding', u'tDuration-expr', tDuration_expr)

# Atomic simple type: {http://schemas.xmlsoap.org/ws/2003/03/business-process/}tRoles
class tRoles (pyxb.binding.datatypes.string, pyxb.binding.basis.enumeration_mixin):

    """An atomic simple type."""

    _ExpandedName = pyxb.namespace.ExpandedName(Namespace, u'tRoles')
    _DefinitionLocation = pyxb.utils.utility.Location('/tmp/pyxbdist.RHB65sy/PyXB-1.1.5/pyxb/bundles/wssplat/schemas/bpws.xsd', 673, 4)
    _Documentation = None
tRoles._CF_enumeration = pyxb.binding.facets.CF_enumeration(value_datatype=tRoles, enum_prefix=None)
tRoles.myRole = tRoles._CF_enumeration.addEnumeration(unicode_value=u'myRole', tag=u'myRole')
tRoles.partnerRole = tRoles._CF_enumeration.addEnumeration(unicode_value=u'partnerRole', tag=u'partnerRole')
tRoles._InitializeFacetMap(tRoles._CF_enumeration)
Namespace.addCategoryObject('typeBinding', u'tRoles', tRoles)

# Atomic simple type: [anonymous]
class STD_ANON (pyxb.binding.datatypes.string, pyxb.binding.basis.enumeration_mixin):

    """An atomic simple type."""

    _ExpandedName = None
    _DefinitionLocation = pyxb.utils.utility.Location('/tmp/pyxbdist.RHB65sy/PyXB-1.1.5/pyxb/bundles/wssplat/schemas/bpws.xsd', 370, 20)
    _Documentation = None
STD_ANON._CF_enumeration = pyxb.binding.facets.CF_enumeration(value_datatype=STD_ANON, enum_prefix=None)
STD_ANON.in_ = STD_ANON._CF_enumeration.addEnumeration(unicode_value=u'in', tag=u'in_')
STD_ANON.out = STD_ANON._CF_enumeration.addEnumeration(unicode_value=u'out', tag=u'out')
STD_ANON.out_in = STD_ANON._CF_enumeration.addEnumeration(unicode_value=u'out-in', tag=u'out_in')
STD_ANON._InitializeFacetMap(STD_ANON._CF_enumeration)

# List simple type: [anonymous]
# superclasses pyxb.binding.datatypes.anySimpleType
class STD_ANON_ (pyxb.binding.basis.STD_list):

    """Simple type that is a list of pyxb.binding.datatypes.QName."""

    _ExpandedName = None
    _DefinitionLocation = pyxb.utils.utility.Location('/tmp/pyxbdist.RHB65sy/PyXB-1.1.5/pyxb/bundles/wssplat/schemas/bpws.xsd', 276, 20)
    _Documentation = None

    _ItemType = pyxb.binding.datatypes.QName
STD_ANON_._InitializeFacetMap()

# Complex type {http://schemas.xmlsoap.org/ws/2003/03/business-process/}tExtensibleElements with content type ELEMENT_ONLY
class tExtensibleElements (pyxb.binding.basis.complexTypeDefinition):
    _TypeDefinition = None
    _ContentTypeTag = pyxb.binding.basis.complexTypeDefinition._CT_ELEMENT_ONLY
    _Abstract = False
    _ExpandedName = pyxb.namespace.ExpandedName(Namespace, u'tExtensibleElements')
    _DefinitionLocation = pyxb.utils.utility.Location('/tmp/pyxbdist.RHB65sy/PyXB-1.1.5/pyxb/bundles/wssplat/schemas/bpws.xsd', 11, 4)
    # Base type is pyxb.binding.datatypes.anyType
    _AttributeWildcard = pyxb.binding.content.Wildcard(process_contents=pyxb.binding.content.Wildcard.PC_lax, namespace_constraint=(pyxb.binding.content.Wildcard.NC_not, u'http://schemas.xmlsoap.org/ws/2003/03/business-process/'))
    _HasWildcardElement = True

    _ElementMap = {
        
    }
    _AttributeMap = {
        
    }
Namespace.addCategoryObject('typeBinding', u'tExtensibleElements', tExtensibleElements)


# Complex type {http://schemas.xmlsoap.org/ws/2003/03/business-process/}tActivity with content type ELEMENT_ONLY
class tActivity (tExtensibleElements):
    _TypeDefinition = None
    _ContentTypeTag = pyxb.binding.basis.complexTypeDefinition._CT_ELEMENT_ONLY
    _Abstract = False
    _ExpandedName = pyxb.namespace.ExpandedName(Namespace, u'tActivity')
    _DefinitionLocation = pyxb.utils.utility.Location('/tmp/pyxbdist.RHB65sy/PyXB-1.1.5/pyxb/bundles/wssplat/schemas/bpws.xsd', 286, 4)
    # Base type is tExtensibleElements
    
    # Element {http://schemas.xmlsoap.org/ws/2003/03/business-process/}source uses Python identifier source
    __source = pyxb.binding.content.ElementUse(pyxb.namespace.ExpandedName(Namespace, u'source'), 'source', '__httpschemas_xmlsoap_orgws200303business_process_tActivity_httpschemas_xmlsoap_orgws200303business_processsource', True)
    __source._DeclarationLocation = pyxb.utils.utility.Location('/tmp/pyxbdist.RHB65sy/PyXB-1.1.5/pyxb/bundles/wssplat/schemas/bpws.xsd', 292, 20)
    __source._UseLocation = None

    
    source = property(__source.value, __source.set, None, None)

    
    # Element {http://schemas.xmlsoap.org/ws/2003/03/business-process/}target uses Python identifier target
    __target = pyxb.binding.content.ElementUse(pyxb.namespace.ExpandedName(Namespace, u'target'), 'target', '__httpschemas_xmlsoap_orgws200303business_process_tActivity_httpschemas_xmlsoap_orgws200303business_processtarget', True)
    __target._DeclarationLocation = pyxb.utils.utility.Location('/tmp/pyxbdist.RHB65sy/PyXB-1.1.5/pyxb/bundles/wssplat/schemas/bpws.xsd', 290, 20)
    __target._UseLocation = None

    
    target = property(__target.value, __target.set, None, None)

    
    # Attribute name uses Python identifier name
    __name = pyxb.binding.content.AttributeUse(pyxb.namespace.ExpandedName(None, u'name'), 'name', '__httpschemas_xmlsoap_orgws200303business_process_tActivity_name', pyxb.binding.datatypes.NCName)
    __name._DeclarationLocation = pyxb.utils.utility.Location('/tmp/pyxbdist.RHB65sy/PyXB-1.1.5/pyxb/bundles/wssplat/schemas/bpws.xsd', 295, 16)
    __name._UseLocation = pyxb.utils.utility.Location('/tmp/pyxbdist.RHB65sy/PyXB-1.1.5/pyxb/bundles/wssplat/schemas/bpws.xsd', 295, 16)
    
    name = property(__name.value, __name.set, None, None)

    
    # Attribute joinCondition uses Python identifier joinCondition
    __joinCondition = pyxb.binding.content.AttributeUse(pyxb.namespace.ExpandedName(None, u'joinCondition'), 'joinCondition', '__httpschemas_xmlsoap_orgws200303business_process_tActivity_joinCondition', tBoolean_expr)
    __joinCondition._DeclarationLocation = pyxb.utils.utility.Location('/tmp/pyxbdist.RHB65sy/PyXB-1.1.5/pyxb/bundles/wssplat/schemas/bpws.xsd', 296, 16)
    __joinCondition._UseLocation = pyxb.utils.utility.Location('/tmp/pyxbdist.RHB65sy/PyXB-1.1.5/pyxb/bundles/wssplat/schemas/bpws.xsd', 296, 16)
    
    joinCondition = property(__joinCondition.value, __joinCondition.set, None, None)

    
    # Attribute suppressJoinFailure uses Python identifier suppressJoinFailure
    __suppressJoinFailure = pyxb.binding.content.AttributeUse(pyxb.namespace.ExpandedName(None, u'suppressJoinFailure'), 'suppressJoinFailure', '__httpschemas_xmlsoap_orgws200303business_process_tActivity_suppressJoinFailure', tBoolean, unicode_default=u'no')
    __suppressJoinFailure._DeclarationLocation = pyxb.utils.utility.Location('/tmp/pyxbdist.RHB65sy/PyXB-1.1.5/pyxb/bundles/wssplat/schemas/bpws.xsd', 298, 16)
    __suppressJoinFailure._UseLocation = pyxb.utils.utility.Location('/tmp/pyxbdist.RHB65sy/PyXB-1.1.5/pyxb/bundles/wssplat/schemas/bpws.xsd', 298, 16)
    
    suppressJoinFailure = property(__suppressJoinFailure.value, __suppressJoinFailure.set, None, None)

    _AttributeWildcard = pyxb.binding.content.Wildcard(process_contents=pyxb.binding.content.Wildcard.PC_lax, namespace_constraint=(pyxb.binding.content.Wildcard.NC_not, u'http://schemas.xmlsoap.org/ws/2003/03/business-process/'))
    _HasWildcardElement = True

    _ElementMap = tExtensibleElements._ElementMap.copy()
    _ElementMap.update({
        __source.name() : __source,
        __target.name() : __target
    })
    _AttributeMap = tExtensibleElements._AttributeMap.copy()
    _AttributeMap.update({
        __name.name() : __name,
        __joinCondition.name() : __joinCondition,
        __suppressJoinFailure.name() : __suppressJoinFailure
    })
Namespace.addCategoryObject('typeBinding', u'tActivity', tActivity)


# Complex type {http://schemas.xmlsoap.org/ws/2003/03/business-process/}tInvoke with content type ELEMENT_ONLY
class tInvoke (tActivity):
    _TypeDefinition = None
    _ContentTypeTag = pyxb.binding.basis.complexTypeDefinition._CT_ELEMENT_ONLY
    _Abstract = False
    _ExpandedName = pyxb.namespace.ExpandedName(Namespace, u'tInvoke')
    _DefinitionLocation = pyxb.utils.utility.Location('/tmp/pyxbdist.RHB65sy/PyXB-1.1.5/pyxb/bundles/wssplat/schemas/bpws.xsd', 384, 4)
    # Base type is tActivity
    
    # Element {http://schemas.xmlsoap.org/ws/2003/03/business-process/}compensationHandler uses Python identifier compensationHandler
    __compensationHandler = pyxb.binding.content.ElementUse(pyxb.namespace.ExpandedName(Namespace, u'compensationHandler'), 'compensationHandler', '__httpschemas_xmlsoap_orgws200303business_process_tInvoke_httpschemas_xmlsoap_orgws200303business_processcompensationHandler', False)
    __compensationHandler._DeclarationLocation = pyxb.utils.utility.Location('/tmp/pyxbdist.RHB65sy/PyXB-1.1.5/pyxb/bundles/wssplat/schemas/bpws.xsd', 396, 20)
    __compensationHandler._UseLocation = None

    
    compensationHandler = property(__compensationHandler.value, __compensationHandler.set, None, None)

    
    # Element {http://schemas.xmlsoap.org/ws/2003/03/business-process/}correlations uses Python identifier correlations
    __correlations = pyxb.binding.content.ElementUse(pyxb.namespace.ExpandedName(Namespace, u'correlations'), 'correlations', '__httpschemas_xmlsoap_orgws200303business_process_tInvoke_httpschemas_xmlsoap_orgws200303business_processcorrelations', False)
    __correlations._DeclarationLocation = pyxb.utils.utility.Location('/tmp/pyxbdist.RHB65sy/PyXB-1.1.5/pyxb/bundles/wssplat/schemas/bpws.xsd', 388, 20)
    __correlations._UseLocation = None

    
    correlations = property(__correlations.value, __correlations.set, None, None)

    
    # Element {http://schemas.xmlsoap.org/ws/2003/03/business-process/}catchAll uses Python identifier catchAll
    __catchAll = pyxb.binding.content.ElementUse(pyxb.namespace.ExpandedName(Namespace, u'catchAll'), 'catchAll', '__httpschemas_xmlsoap_orgws200303business_process_tInvoke_httpschemas_xmlsoap_orgws200303business_processcatchAll', False)
    __catchAll._DeclarationLocation = pyxb.utils.utility.Location('/tmp/pyxbdist.RHB65sy/PyXB-1.1.5/pyxb/bundles/wssplat/schemas/bpws.xsd', 393, 20)
    __catchAll._UseLocation = None

    
    catchAll = property(__catchAll.value, __catchAll.set, None, None)

    
    # Element {http://schemas.xmlsoap.org/ws/2003/03/business-process/}catch uses Python identifier catch
    __catch = pyxb.binding.content.ElementUse(pyxb.namespace.ExpandedName(Namespace, u'catch'), 'catch', '__httpschemas_xmlsoap_orgws200303business_process_tInvoke_httpschemas_xmlsoap_orgws200303business_processcatch', True)
    __catch._DeclarationLocation = pyxb.utils.utility.Location('/tmp/pyxbdist.RHB65sy/PyXB-1.1.5/pyxb/bundles/wssplat/schemas/bpws.xsd', 391, 20)
    __catch._UseLocation = None

    
    catch = property(__catch.value, __catch.set, None, None)

    
    # Element source ({http://schemas.xmlsoap.org/ws/2003/03/business-process/}source) inherited from {http://schemas.xmlsoap.org/ws/2003/03/business-process/}tActivity
    
    # Element target ({http://schemas.xmlsoap.org/ws/2003/03/business-process/}target) inherited from {http://schemas.xmlsoap.org/ws/2003/03/business-process/}tActivity
    
    # Attribute suppressJoinFailure inherited from {http://schemas.xmlsoap.org/ws/2003/03/business-process/}tActivity
    
    # Attribute joinCondition inherited from {http://schemas.xmlsoap.org/ws/2003/03/business-process/}tActivity
    
    # Attribute operation uses Python identifier operation
    __operation = pyxb.binding.content.AttributeUse(pyxb.namespace.ExpandedName(None, u'operation'), 'operation', '__httpschemas_xmlsoap_orgws200303business_process_tInvoke_operation', pyxb.binding.datatypes.NCName, required=True)
    __operation._DeclarationLocation = pyxb.utils.utility.Location('/tmp/pyxbdist.RHB65sy/PyXB-1.1.5/pyxb/bundles/wssplat/schemas/bpws.xsd', 401, 16)
    __operation._UseLocation = pyxb.utils.utility.Location('/tmp/pyxbdist.RHB65sy/PyXB-1.1.5/pyxb/bundles/wssplat/schemas/bpws.xsd', 401, 16)
    
    operation = property(__operation.value, __operation.set, None, None)

    
    # Attribute outputVariable uses Python identifier outputVariable
    __outputVariable = pyxb.binding.content.AttributeUse(pyxb.namespace.ExpandedName(None, u'outputVariable'), 'outputVariable', '__httpschemas_xmlsoap_orgws200303business_process_tInvoke_outputVariable', pyxb.binding.datatypes.NCName)
    __outputVariable._DeclarationLocation = pyxb.utils.utility.Location('/tmp/pyxbdist.RHB65sy/PyXB-1.1.5/pyxb/bundles/wssplat/schemas/bpws.xsd', 404, 16)
    __outputVariable._UseLocation = pyxb.utils.utility.Location('/tmp/pyxbdist.RHB65sy/PyXB-1.1.5/pyxb/bundles/wssplat/schemas/bpws.xsd', 404, 16)
    
    outputVariable = property(__outputVariable.value, __outputVariable.set, None, None)

    
    # Attribute inputVariable uses Python identifier inputVariable
    __inputVariable = pyxb.binding.content.AttributeUse(pyxb.namespace.ExpandedName(None, u'inputVariable'), 'inputVariable', '__httpschemas_xmlsoap_orgws200303business_process_tInvoke_inputVariable', pyxb.binding.datatypes.NCName)
    __inputVariable._DeclarationLocation = pyxb.utils.utility.Location('/tmp/pyxbdist.RHB65sy/PyXB-1.1.5/pyxb/bundles/wssplat/schemas/bpws.xsd', 402, 16)
    __inputVariable._UseLocation = pyxb.utils.utility.Location('/tmp/pyxbdist.RHB65sy/PyXB-1.1.5/pyxb/bundles/wssplat/schemas/bpws.xsd', 402, 16)
    
    inputVariable = property(__inputVariable.value, __inputVariable.set, None, None)

    
    # Attribute name inherited from {http://schemas.xmlsoap.org/ws/2003/03/business-process/}tActivity
    
    # Attribute partnerLink uses Python identifier partnerLink
    __partnerLink = pyxb.binding.content.AttributeUse(pyxb.namespace.ExpandedName(None, u'partnerLink'), 'partnerLink', '__httpschemas_xmlsoap_orgws200303business_process_tInvoke_partnerLink', pyxb.binding.datatypes.NCName, required=True)
    __partnerLink._DeclarationLocation = pyxb.utils.utility.Location('/tmp/pyxbdist.RHB65sy/PyXB-1.1.5/pyxb/bundles/wssplat/schemas/bpws.xsd', 399, 16)
    __partnerLink._UseLocation = pyxb.utils.utility.Location('/tmp/pyxbdist.RHB65sy/PyXB-1.1.5/pyxb/bundles/wssplat/schemas/bpws.xsd', 399, 16)
    
    partnerLink = property(__partnerLink.value, __partnerLink.set, None, None)

    
    # Attribute portType uses Python identifier portType
    __portType = pyxb.binding.content.AttributeUse(pyxb.namespace.ExpandedName(None, u'portType'), 'portType', '__httpschemas_xmlsoap_orgws200303business_process_tInvoke_portType', pyxb.binding.datatypes.QName, required=True)
    __portType._DeclarationLocation = pyxb.utils.utility.Location('/tmp/pyxbdist.RHB65sy/PyXB-1.1.5/pyxb/bundles/wssplat/schemas/bpws.xsd', 400, 16)
    __portType._UseLocation = pyxb.utils.utility.Location('/tmp/pyxbdist.RHB65sy/PyXB-1.1.5/pyxb/bundles/wssplat/schemas/bpws.xsd', 400, 16)
    
    portType = property(__portType.value, __portType.set, None, None)

    _AttributeWildcard = pyxb.binding.content.Wildcard(process_contents=pyxb.binding.content.Wildcard.PC_lax, namespace_constraint=(pyxb.binding.content.Wildcard.NC_not, u'http://schemas.xmlsoap.org/ws/2003/03/business-process/'))
    _HasWildcardElement = True

    _ElementMap = tActivity._ElementMap.copy()
    _ElementMap.update({
        __compensationHandler.name() : __compensationHandler,
        __correlations.name() : __correlations,
        __catchAll.name() : __catchAll,
        __catch.name() : __catch
    })
    _AttributeMap = tActivity._AttributeMap.copy()
    _AttributeMap.update({
        __operation.name() : __operation,
        __outputVariable.name() : __outputVariable,
        __inputVariable.name() : __inputVariable,
        __partnerLink.name() : __partnerLink,
        __portType.name() : __portType
    })
Namespace.addCategoryObject('typeBinding', u'tInvoke', tInvoke)


# Complex type {http://schemas.xmlsoap.org/ws/2003/03/business-process/}tWhile with content type ELEMENT_ONLY
class tWhile (tActivity):
    _TypeDefinition = None
    _ContentTypeTag = pyxb.binding.basis.complexTypeDefinition._CT_ELEMENT_ONLY
    _Abstract = False
    _ExpandedName = pyxb.namespace.ExpandedName(Namespace, u'tWhile')
    _DefinitionLocation = pyxb.utils.utility.Location('/tmp/pyxbdist.RHB65sy/PyXB-1.1.5/pyxb/bundles/wssplat/schemas/bpws.xsd', 586, 4)
    # Base type is tActivity
    
    # Element {http://schemas.xmlsoap.org/ws/2003/03/business-process/}scope uses Python identifier scope
    __scope = pyxb.binding.content.ElementUse(pyxb.namespace.ExpandedName(Namespace, u'scope'), 'scope', '__httpschemas_xmlsoap_orgws200303business_process_tWhile_httpschemas_xmlsoap_orgws200303business_processscope', False)
    __scope._DeclarationLocation = pyxb.utils.utility.Location('/tmp/pyxbdist.RHB65sy/PyXB-1.1.5/pyxb/bundles/wssplat/schemas/bpws.xsd', 82, 12)
    __scope._UseLocation = None

    
    scope = property(__scope.value, __scope.set, None, None)

    
    # Element {http://schemas.xmlsoap.org/ws/2003/03/business-process/}invoke uses Python identifier invoke
    __invoke = pyxb.binding.content.ElementUse(pyxb.namespace.ExpandedName(Namespace, u'invoke'), 'invoke', '__httpschemas_xmlsoap_orgws200303business_process_tWhile_httpschemas_xmlsoap_orgws200303business_processinvoke', False)
    __invoke._DeclarationLocation = pyxb.utils.utility.Location('/tmp/pyxbdist.RHB65sy/PyXB-1.1.5/pyxb/bundles/wssplat/schemas/bpws.xsd', 70, 12)
    __invoke._UseLocation = None

    
    invoke = property(__invoke.value, __invoke.set, None, None)

    
    # Element {http://schemas.xmlsoap.org/ws/2003/03/business-process/}switch uses Python identifier switch
    __switch = pyxb.binding.content.ElementUse(pyxb.namespace.ExpandedName(Namespace, u'switch'), 'switch', '__httpschemas_xmlsoap_orgws200303business_process_tWhile_httpschemas_xmlsoap_orgws200303business_processswitch', False)
    __switch._DeclarationLocation = pyxb.utils.utility.Location('/tmp/pyxbdist.RHB65sy/PyXB-1.1.5/pyxb/bundles/wssplat/schemas/bpws.xsd', 78, 12)
    __switch._UseLocation = None

    
    switch = property(__switch.value, __switch.set, None, None)

    
    # Element {http://schemas.xmlsoap.org/ws/2003/03/business-process/}throw uses Python identifier throw
    __throw = pyxb.binding.content.ElementUse(pyxb.namespace.ExpandedName(Namespace, u'throw'), 'throw', '__httpschemas_xmlsoap_orgws200303business_process_tWhile_httpschemas_xmlsoap_orgws200303business_processthrow', False)
    __throw._DeclarationLocation = pyxb.utils.utility.Location('/tmp/pyxbdist.RHB65sy/PyXB-1.1.5/pyxb/bundles/wssplat/schemas/bpws.xsd', 75, 12)
    __throw._UseLocation = None

    
    throw = property(__throw.value, __throw.set, None, None)

    
    # Element {http://schemas.xmlsoap.org/ws/2003/03/business-process/}assign uses Python identifier assign
    __assign = pyxb.binding.content.ElementUse(pyxb.namespace.ExpandedName(Namespace, u'assign'), 'assign', '__httpschemas_xmlsoap_orgws200303business_process_tWhile_httpschemas_xmlsoap_orgws200303business_processassign', False)
    __assign._DeclarationLocation = pyxb.utils.utility.Location('/tmp/pyxbdist.RHB65sy/PyXB-1.1.5/pyxb/bundles/wssplat/schemas/bpws.xsd', 73, 12)
    __assign._UseLocation = None

    
    assign = property(__assign.value, __assign.set, None, None)

    
    # Element {http://schemas.xmlsoap.org/ws/2003/03/business-process/}receive uses Python identifier receive
    __receive = pyxb.binding.content.ElementUse(pyxb.namespace.ExpandedName(Namespace, u'receive'), 'receive', '__httpschemas_xmlsoap_orgws200303business_process_tWhile_httpschemas_xmlsoap_orgws200303business_processreceive', False)
    __receive._DeclarationLocation = pyxb.utils.utility.Location('/tmp/pyxbdist.RHB65sy/PyXB-1.1.5/pyxb/bundles/wssplat/schemas/bpws.xsd', 71, 12)
    __receive._UseLocation = None

    
    receive = property(__receive.value, __receive.set, None, None)

    
    # Element {http://schemas.xmlsoap.org/ws/2003/03/business-process/}sequence uses Python identifier sequence
    __sequence = pyxb.binding.content.ElementUse(pyxb.namespace.ExpandedName(Namespace, u'sequence'), 'sequence', '__httpschemas_xmlsoap_orgws200303business_process_tWhile_httpschemas_xmlsoap_orgws200303business_processsequence', False)
    __sequence._DeclarationLocation = pyxb.utils.utility.Location('/tmp/pyxbdist.RHB65sy/PyXB-1.1.5/pyxb/bundles/wssplat/schemas/bpws.xsd', 80, 12)
    __sequence._UseLocation = None

    
    sequence = property(__sequence.value, __sequence.set, None, None)

    
    # Element {http://schemas.xmlsoap.org/ws/2003/03/business-process/}terminate uses Python identifier terminate
    __terminate = pyxb.binding.content.ElementUse(pyxb.namespace.ExpandedName(Namespace, u'terminate'), 'terminate', '__httpschemas_xmlsoap_orgws200303business_process_tWhile_httpschemas_xmlsoap_orgws200303business_processterminate', False)
    __terminate._DeclarationLocation = pyxb.utils.utility.Location('/tmp/pyxbdist.RHB65sy/PyXB-1.1.5/pyxb/bundles/wssplat/schemas/bpws.xsd', 76, 12)
    __terminate._UseLocation = None

    
    terminate = property(__terminate.value, __terminate.set, None, None)

    
    # Element {http://schemas.xmlsoap.org/ws/2003/03/business-process/}while uses Python identifier while_
    __while = pyxb.binding.content.ElementUse(pyxb.namespace.ExpandedName(Namespace, u'while'), 'while_', '__httpschemas_xmlsoap_orgws200303business_process_tWhile_httpschemas_xmlsoap_orgws200303business_processwhile', False)
    __while._DeclarationLocation = pyxb.utils.utility.Location('/tmp/pyxbdist.RHB65sy/PyXB-1.1.5/pyxb/bundles/wssplat/schemas/bpws.xsd', 79, 12)
    __while._UseLocation = None

    
    while_ = property(__while.value, __while.set, None, None)

    
    # Element {http://schemas.xmlsoap.org/ws/2003/03/business-process/}empty uses Python identifier empty
    __empty = pyxb.binding.content.ElementUse(pyxb.namespace.ExpandedName(Namespace, u'empty'), 'empty', '__httpschemas_xmlsoap_orgws200303business_process_tWhile_httpschemas_xmlsoap_orgws200303business_processempty', False)
    __empty._DeclarationLocation = pyxb.utils.utility.Location('/tmp/pyxbdist.RHB65sy/PyXB-1.1.5/pyxb/bundles/wssplat/schemas/bpws.xsd', 69, 12)
    __empty._UseLocation = None

    
    empty = property(__empty.value, __empty.set, None, None)

    
    # Element {http://schemas.xmlsoap.org/ws/2003/03/business-process/}flow uses Python identifier flow
    __flow = pyxb.binding.content.ElementUse(pyxb.namespace.ExpandedName(Namespace, u'flow'), 'flow', '__httpschemas_xmlsoap_orgws200303business_process_tWhile_httpschemas_xmlsoap_orgws200303business_processflow', False)
    __flow._DeclarationLocation = pyxb.utils.utility.Location('/tmp/pyxbdist.RHB65sy/PyXB-1.1.5/pyxb/bundles/wssplat/schemas/bpws.xsd', 77, 12)
    __flow._UseLocation = None

    
    flow = property(__flow.value, __flow.set, None, None)

    
    # Element {http://schemas.xmlsoap.org/ws/2003/03/business-process/}pick uses Python identifier pick
    __pick = pyxb.binding.content.ElementUse(pyxb.namespace.ExpandedName(Namespace, u'pick'), 'pick', '__httpschemas_xmlsoap_orgws200303business_process_tWhile_httpschemas_xmlsoap_orgws200303business_processpick', False)
    __pick._DeclarationLocation = pyxb.utils.utility.Location('/tmp/pyxbdist.RHB65sy/PyXB-1.1.5/pyxb/bundles/wssplat/schemas/bpws.xsd', 81, 12)
    __pick._UseLocation = None

    
    pick = property(__pick.value, __pick.set, None, None)

    
    # Element {http://schemas.xmlsoap.org/ws/2003/03/business-process/}reply uses Python identifier reply
    __reply = pyxb.binding.content.ElementUse(pyxb.namespace.ExpandedName(Namespace, u'reply'), 'reply', '__httpschemas_xmlsoap_orgws200303business_process_tWhile_httpschemas_xmlsoap_orgws200303business_processreply', False)
    __reply._DeclarationLocation = pyxb.utils.utility.Location('/tmp/pyxbdist.RHB65sy/PyXB-1.1.5/pyxb/bundles/wssplat/schemas/bpws.xsd', 72, 12)
    __reply._UseLocation = None

    
    reply = property(__reply.value, __reply.set, None, None)

    
    # Element {http://schemas.xmlsoap.org/ws/2003/03/business-process/}wait uses Python identifier wait
    __wait = pyxb.binding.content.ElementUse(pyxb.namespace.ExpandedName(Namespace, u'wait'), 'wait', '__httpschemas_xmlsoap_orgws200303business_process_tWhile_httpschemas_xmlsoap_orgws200303business_processwait', False)
    __wait._DeclarationLocation = pyxb.utils.utility.Location('/tmp/pyxbdist.RHB65sy/PyXB-1.1.5/pyxb/bundles/wssplat/schemas/bpws.xsd', 74, 12)
    __wait._UseLocation = None

    
    wait = property(__wait.value, __wait.set, None, None)

    
    # Element source ({http://schemas.xmlsoap.org/ws/2003/03/business-process/}source) inherited from {http://schemas.xmlsoap.org/ws/2003/03/business-process/}tActivity
    
    # Element target ({http://schemas.xmlsoap.org/ws/2003/03/business-process/}target) inherited from {http://schemas.xmlsoap.org/ws/2003/03/business-process/}tActivity
    
    # Attribute name inherited from {http://schemas.xmlsoap.org/ws/2003/03/business-process/}tActivity
    
    # Attribute condition uses Python identifier condition
    __condition = pyxb.binding.content.AttributeUse(pyxb.namespace.ExpandedName(None, u'condition'), 'condition', '__httpschemas_xmlsoap_orgws200303business_process_tWhile_condition', tBoolean_expr, required=True)
    __condition._DeclarationLocation = pyxb.utils.utility.Location('/tmp/pyxbdist.RHB65sy/PyXB-1.1.5/pyxb/bundles/wssplat/schemas/bpws.xsd', 592, 16)
    __condition._UseLocation = pyxb.utils.utility.Location('/tmp/pyxbdist.RHB65sy/PyXB-1.1.5/pyxb/bundles/wssplat/schemas/bpws.xsd', 592, 16)
    
    condition = property(__condition.value, __condition.set, None, None)

    
    # Attribute joinCondition inherited from {http://schemas.xmlsoap.org/ws/2003/03/business-process/}tActivity
    
    # Attribute suppressJoinFailure inherited from {http://schemas.xmlsoap.org/ws/2003/03/business-process/}tActivity
    _AttributeWildcard = pyxb.binding.content.Wildcard(process_contents=pyxb.binding.content.Wildcard.PC_lax, namespace_constraint=(pyxb.binding.content.Wildcard.NC_not, u'http://schemas.xmlsoap.org/ws/2003/03/business-process/'))
    _HasWildcardElement = True

    _ElementMap = tActivity._ElementMap.copy()
    _ElementMap.update({
        __scope.name() : __scope,
        __invoke.name() : __invoke,
        __switch.name() : __switch,
        __throw.name() : __throw,
        __assign.name() : __assign,
        __receive.name() : __receive,
        __sequence.name() : __sequence,
        __terminate.name() : __terminate,
        __while.name() : __while,
        __empty.name() : __empty,
        __flow.name() : __flow,
        __pick.name() : __pick,
        __reply.name() : __reply,
        __wait.name() : __wait
    })
    _AttributeMap = tActivity._AttributeMap.copy()
    _AttributeMap.update({
        __condition.name() : __condition
    })
Namespace.addCategoryObject('typeBinding', u'tWhile', tWhile)


# Complex type {http://schemas.xmlsoap.org/ws/2003/03/business-process/}tTerminate with content type ELEMENT_ONLY
class tTerminate (tActivity):
    _TypeDefinition = None
    _ContentTypeTag = pyxb.binding.basis.complexTypeDefinition._CT_ELEMENT_ONLY
    _Abstract = False
    _ExpandedName = pyxb.namespace.ExpandedName(Namespace, u'tTerminate')
    _DefinitionLocation = pyxb.utils.utility.Location('/tmp/pyxbdist.RHB65sy/PyXB-1.1.5/pyxb/bundles/wssplat/schemas/bpws.xsd', 526, 4)
    # Base type is tActivity
    
    # Element source ({http://schemas.xmlsoap.org/ws/2003/03/business-process/}source) inherited from {http://schemas.xmlsoap.org/ws/2003/03/business-process/}tActivity
    
    # Element target ({http://schemas.xmlsoap.org/ws/2003/03/business-process/}target) inherited from {http://schemas.xmlsoap.org/ws/2003/03/business-process/}tActivity
    
    # Attribute name inherited from {http://schemas.xmlsoap.org/ws/2003/03/business-process/}tActivity
    
    # Attribute joinCondition inherited from {http://schemas.xmlsoap.org/ws/2003/03/business-process/}tActivity
    
    # Attribute suppressJoinFailure inherited from {http://schemas.xmlsoap.org/ws/2003/03/business-process/}tActivity
    _AttributeWildcard = pyxb.binding.content.Wildcard(process_contents=pyxb.binding.content.Wildcard.PC_lax, namespace_constraint=(pyxb.binding.content.Wildcard.NC_not, u'http://schemas.xmlsoap.org/ws/2003/03/business-process/'))
    _HasWildcardElement = True

    _ElementMap = tActivity._ElementMap.copy()
    _ElementMap.update({
        
    })
    _AttributeMap = tActivity._AttributeMap.copy()
    _AttributeMap.update({
        
    })
Namespace.addCategoryObject('typeBinding', u'tTerminate', tTerminate)


# Complex type {http://schemas.xmlsoap.org/ws/2003/03/business-process/}tFlow with content type ELEMENT_ONLY
class tFlow (tActivity):
    _TypeDefinition = None
    _ContentTypeTag = pyxb.binding.basis.complexTypeDefinition._CT_ELEMENT_ONLY
    _Abstract = False
    _ExpandedName = pyxb.namespace.ExpandedName(Namespace, u'tFlow')
    _DefinitionLocation = pyxb.utils.utility.Location('/tmp/pyxbdist.RHB65sy/PyXB-1.1.5/pyxb/bundles/wssplat/schemas/bpws.xsd', 532, 4)
    # Base type is tActivity
    
    # Element {http://schemas.xmlsoap.org/ws/2003/03/business-process/}switch uses Python identifier switch
    __switch = pyxb.binding.content.ElementUse(pyxb.namespace.ExpandedName(Namespace, u'switch'), 'switch', '__httpschemas_xmlsoap_orgws200303business_process_tFlow_httpschemas_xmlsoap_orgws200303business_processswitch', True)
    __switch._DeclarationLocation = pyxb.utils.utility.Location('/tmp/pyxbdist.RHB65sy/PyXB-1.1.5/pyxb/bundles/wssplat/schemas/bpws.xsd', 78, 12)
    __switch._UseLocation = None

    
    switch = property(__switch.value, __switch.set, None, None)

    
    # Element {http://schemas.xmlsoap.org/ws/2003/03/business-process/}pick uses Python identifier pick
    __pick = pyxb.binding.content.ElementUse(pyxb.namespace.ExpandedName(Namespace, u'pick'), 'pick', '__httpschemas_xmlsoap_orgws200303business_process_tFlow_httpschemas_xmlsoap_orgws200303business_processpick', True)
    __pick._DeclarationLocation = pyxb.utils.utility.Location('/tmp/pyxbdist.RHB65sy/PyXB-1.1.5/pyxb/bundles/wssplat/schemas/bpws.xsd', 81, 12)
    __pick._UseLocation = None

    
    pick = property(__pick.value, __pick.set, None, None)

    
    # Element {http://schemas.xmlsoap.org/ws/2003/03/business-process/}invoke uses Python identifier invoke
    __invoke = pyxb.binding.content.ElementUse(pyxb.namespace.ExpandedName(Namespace, u'invoke'), 'invoke', '__httpschemas_xmlsoap_orgws200303business_process_tFlow_httpschemas_xmlsoap_orgws200303business_processinvoke', True)
    __invoke._DeclarationLocation = pyxb.utils.utility.Location('/tmp/pyxbdist.RHB65sy/PyXB-1.1.5/pyxb/bundles/wssplat/schemas/bpws.xsd', 70, 12)
    __invoke._UseLocation = None

    
    invoke = property(__invoke.value, __invoke.set, None, None)

    
    # Element {http://schemas.xmlsoap.org/ws/2003/03/business-process/}assign uses Python identifier assign
    __assign = pyxb.binding.content.ElementUse(pyxb.namespace.ExpandedName(Namespace, u'assign'), 'assign', '__httpschemas_xmlsoap_orgws200303business_process_tFlow_httpschemas_xmlsoap_orgws200303business_processassign', True)
    __assign._DeclarationLocation = pyxb.utils.utility.Location('/tmp/pyxbdist.RHB65sy/PyXB-1.1.5/pyxb/bundles/wssplat/schemas/bpws.xsd', 73, 12)
    __assign._UseLocation = None

    
    assign = property(__assign.value, __assign.set, None, None)

    
    # Element {http://schemas.xmlsoap.org/ws/2003/03/business-process/}receive uses Python identifier receive
    __receive = pyxb.binding.content.ElementUse(pyxb.namespace.ExpandedName(Namespace, u'receive'), 'receive', '__httpschemas_xmlsoap_orgws200303business_process_tFlow_httpschemas_xmlsoap_orgws200303business_processreceive', True)
    __receive._DeclarationLocation = pyxb.utils.utility.Location('/tmp/pyxbdist.RHB65sy/PyXB-1.1.5/pyxb/bundles/wssplat/schemas/bpws.xsd', 71, 12)
    __receive._UseLocation = None

    
    receive = property(__receive.value, __receive.set, None, None)

    
    # Element source ({http://schemas.xmlsoap.org/ws/2003/03/business-process/}source) inherited from {http://schemas.xmlsoap.org/ws/2003/03/business-process/}tActivity
    
    # Element {http://schemas.xmlsoap.org/ws/2003/03/business-process/}flow uses Python identifier flow
    __flow = pyxb.binding.content.ElementUse(pyxb.namespace.ExpandedName(Namespace, u'flow'), 'flow', '__httpschemas_xmlsoap_orgws200303business_process_tFlow_httpschemas_xmlsoap_orgws200303business_processflow', True)
    __flow._DeclarationLocation = pyxb.utils.utility.Location('/tmp/pyxbdist.RHB65sy/PyXB-1.1.5/pyxb/bundles/wssplat/schemas/bpws.xsd', 77, 12)
    __flow._UseLocation = None

    
    flow = property(__flow.value, __flow.set, None, None)

    
    # Element {http://schemas.xmlsoap.org/ws/2003/03/business-process/}wait uses Python identifier wait
    __wait = pyxb.binding.content.ElementUse(pyxb.namespace.ExpandedName(Namespace, u'wait'), 'wait', '__httpschemas_xmlsoap_orgws200303business_process_tFlow_httpschemas_xmlsoap_orgws200303business_processwait', True)
    __wait._DeclarationLocation = pyxb.utils.utility.Location('/tmp/pyxbdist.RHB65sy/PyXB-1.1.5/pyxb/bundles/wssplat/schemas/bpws.xsd', 74, 12)
    __wait._UseLocation = None

    
    wait = property(__wait.value, __wait.set, None, None)

    
    # Element {http://schemas.xmlsoap.org/ws/2003/03/business-process/}while uses Python identifier while_
    __while = pyxb.binding.content.ElementUse(pyxb.namespace.ExpandedName(Namespace, u'while'), 'while_', '__httpschemas_xmlsoap_orgws200303business_process_tFlow_httpschemas_xmlsoap_orgws200303business_processwhile', True)
    __while._DeclarationLocation = pyxb.utils.utility.Location('/tmp/pyxbdist.RHB65sy/PyXB-1.1.5/pyxb/bundles/wssplat/schemas/bpws.xsd', 79, 12)
    __while._UseLocation = None

    
    while_ = property(__while.value, __while.set, None, None)

    
    # Element {http://schemas.xmlsoap.org/ws/2003/03/business-process/}scope uses Python identifier scope
    __scope = pyxb.binding.content.ElementUse(pyxb.namespace.ExpandedName(Namespace, u'scope'), 'scope', '__httpschemas_xmlsoap_orgws200303business_process_tFlow_httpschemas_xmlsoap_orgws200303business_processscope', True)
    __scope._DeclarationLocation = pyxb.utils.utility.Location('/tmp/pyxbdist.RHB65sy/PyXB-1.1.5/pyxb/bundles/wssplat/schemas/bpws.xsd', 82, 12)
    __scope._UseLocation = None

    
    scope = property(__scope.value, __scope.set, None, None)

    
    # Element {http://schemas.xmlsoap.org/ws/2003/03/business-process/}reply uses Python identifier reply
    __reply = pyxb.binding.content.ElementUse(pyxb.namespace.ExpandedName(Namespace, u'reply'), 'reply', '__httpschemas_xmlsoap_orgws200303business_process_tFlow_httpschemas_xmlsoap_orgws200303business_processreply', True)
    __reply._DeclarationLocation = pyxb.utils.utility.Location('/tmp/pyxbdist.RHB65sy/PyXB-1.1.5/pyxb/bundles/wssplat/schemas/bpws.xsd', 72, 12)
    __reply._UseLocation = None

    
    reply = property(__reply.value, __reply.set, None, None)

    
    # Element {http://schemas.xmlsoap.org/ws/2003/03/business-process/}terminate uses Python identifier terminate
    __terminate = pyxb.binding.content.ElementUse(pyxb.namespace.ExpandedName(Namespace, u'terminate'), 'terminate', '__httpschemas_xmlsoap_orgws200303business_process_tFlow_httpschemas_xmlsoap_orgws200303business_processterminate', True)
    __terminate._DeclarationLocation = pyxb.utils.utility.Location('/tmp/pyxbdist.RHB65sy/PyXB-1.1.5/pyxb/bundles/wssplat/schemas/bpws.xsd', 76, 12)
    __terminate._UseLocation = None

    
    terminate = property(__terminate.value, __terminate.set, None, None)

    
    # Element {http://schemas.xmlsoap.org/ws/2003/03/business-process/}throw uses Python identifier throw
    __throw = pyxb.binding.content.ElementUse(pyxb.namespace.ExpandedName(Namespace, u'throw'), 'throw', '__httpschemas_xmlsoap_orgws200303business_process_tFlow_httpschemas_xmlsoap_orgws200303business_processthrow', True)
    __throw._DeclarationLocation = pyxb.utils.utility.Location('/tmp/pyxbdist.RHB65sy/PyXB-1.1.5/pyxb/bundles/wssplat/schemas/bpws.xsd', 75, 12)
    __throw._UseLocation = None

    
    throw = property(__throw.value, __throw.set, None, None)

    
    # Element {http://schemas.xmlsoap.org/ws/2003/03/business-process/}sequence uses Python identifier sequence
    __sequence = pyxb.binding.content.ElementUse(pyxb.namespace.ExpandedName(Namespace, u'sequence'), 'sequence', '__httpschemas_xmlsoap_orgws200303business_process_tFlow_httpschemas_xmlsoap_orgws200303business_processsequence', True)
    __sequence._DeclarationLocation = pyxb.utils.utility.Location('/tmp/pyxbdist.RHB65sy/PyXB-1.1.5/pyxb/bundles/wssplat/schemas/bpws.xsd', 80, 12)
    __sequence._UseLocation = None

    
    sequence = property(__sequence.value, __sequence.set, None, None)

    
    # Element {http://schemas.xmlsoap.org/ws/2003/03/business-process/}links uses Python identifier links
    __links = pyxb.binding.content.ElementUse(pyxb.namespace.ExpandedName(Namespace, u'links'), 'links', '__httpschemas_xmlsoap_orgws200303business_process_tFlow_httpschemas_xmlsoap_orgws200303business_processlinks', False)
    __links._DeclarationLocation = pyxb.utils.utility.Location('/tmp/pyxbdist.RHB65sy/PyXB-1.1.5/pyxb/bundles/wssplat/schemas/bpws.xsd', 536, 20)
    __links._UseLocation = None

    
    links = property(__links.value, __links.set, None, None)

    
    # Element {http://schemas.xmlsoap.org/ws/2003/03/business-process/}empty uses Python identifier empty
    __empty = pyxb.binding.content.ElementUse(pyxb.namespace.ExpandedName(Namespace, u'empty'), 'empty', '__httpschemas_xmlsoap_orgws200303business_process_tFlow_httpschemas_xmlsoap_orgws200303business_processempty', True)
    __empty._DeclarationLocation = pyxb.utils.utility.Location('/tmp/pyxbdist.RHB65sy/PyXB-1.1.5/pyxb/bundles/wssplat/schemas/bpws.xsd', 69, 12)
    __empty._UseLocation = None

    
    empty = property(__empty.value, __empty.set, None, None)

    
    # Element target ({http://schemas.xmlsoap.org/ws/2003/03/business-process/}target) inherited from {http://schemas.xmlsoap.org/ws/2003/03/business-process/}tActivity
    
    # Attribute name inherited from {http://schemas.xmlsoap.org/ws/2003/03/business-process/}tActivity
    
    # Attribute joinCondition inherited from {http://schemas.xmlsoap.org/ws/2003/03/business-process/}tActivity
    
    # Attribute suppressJoinFailure inherited from {http://schemas.xmlsoap.org/ws/2003/03/business-process/}tActivity
    _AttributeWildcard = pyxb.binding.content.Wildcard(process_contents=pyxb.binding.content.Wildcard.PC_lax, namespace_constraint=(pyxb.binding.content.Wildcard.NC_not, u'http://schemas.xmlsoap.org/ws/2003/03/business-process/'))
    _HasWildcardElement = True

    _ElementMap = tActivity._ElementMap.copy()
    _ElementMap.update({
        __switch.name() : __switch,
        __pick.name() : __pick,
        __invoke.name() : __invoke,
        __assign.name() : __assign,
        __receive.name() : __receive,
        __flow.name() : __flow,
        __wait.name() : __wait,
        __while.name() : __while,
        __scope.name() : __scope,
        __reply.name() : __reply,
        __terminate.name() : __terminate,
        __throw.name() : __throw,
        __sequence.name() : __sequence,
        __links.name() : __links,
        __empty.name() : __empty
    })
    _AttributeMap = tActivity._AttributeMap.copy()
    _AttributeMap.update({
        
    })
Namespace.addCategoryObject('typeBinding', u'tFlow', tFlow)


# Complex type {http://schemas.xmlsoap.org/ws/2003/03/business-process/}tReceive with content type ELEMENT_ONLY
class tReceive (tActivity):
    _TypeDefinition = None
    _ContentTypeTag = pyxb.binding.basis.complexTypeDefinition._CT_ELEMENT_ONLY
    _Abstract = False
    _ExpandedName = pyxb.namespace.ExpandedName(Namespace, u'tReceive')
    _DefinitionLocation = pyxb.utils.utility.Location('/tmp/pyxbdist.RHB65sy/PyXB-1.1.5/pyxb/bundles/wssplat/schemas/bpws.xsd', 410, 4)
    # Base type is tActivity
    
    # Element {http://schemas.xmlsoap.org/ws/2003/03/business-process/}correlations uses Python identifier correlations
    __correlations = pyxb.binding.content.ElementUse(pyxb.namespace.ExpandedName(Namespace, u'correlations'), 'correlations', '__httpschemas_xmlsoap_orgws200303business_process_tReceive_httpschemas_xmlsoap_orgws200303business_processcorrelations', False)
    __correlations._DeclarationLocation = pyxb.utils.utility.Location('/tmp/pyxbdist.RHB65sy/PyXB-1.1.5/pyxb/bundles/wssplat/schemas/bpws.xsd', 414, 20)
    __correlations._UseLocation = None

    
    correlations = property(__correlations.value, __correlations.set, None, None)

    
    # Element source ({http://schemas.xmlsoap.org/ws/2003/03/business-process/}source) inherited from {http://schemas.xmlsoap.org/ws/2003/03/business-process/}tActivity
    
    # Element target ({http://schemas.xmlsoap.org/ws/2003/03/business-process/}target) inherited from {http://schemas.xmlsoap.org/ws/2003/03/business-process/}tActivity
    
    # Attribute operation uses Python identifier operation
    __operation = pyxb.binding.content.AttributeUse(pyxb.namespace.ExpandedName(None, u'operation'), 'operation', '__httpschemas_xmlsoap_orgws200303business_process_tReceive_operation', pyxb.binding.datatypes.NCName, required=True)
    __operation._DeclarationLocation = pyxb.utils.utility.Location('/tmp/pyxbdist.RHB65sy/PyXB-1.1.5/pyxb/bundles/wssplat/schemas/bpws.xsd', 419, 16)
    __operation._UseLocation = pyxb.utils.utility.Location('/tmp/pyxbdist.RHB65sy/PyXB-1.1.5/pyxb/bundles/wssplat/schemas/bpws.xsd', 419, 16)
    
    operation = property(__operation.value, __operation.set, None, None)

    
    # Attribute suppressJoinFailure inherited from {http://schemas.xmlsoap.org/ws/2003/03/business-process/}tActivity
    
    # Attribute partnerLink uses Python identifier partnerLink
    __partnerLink = pyxb.binding.content.AttributeUse(pyxb.namespace.ExpandedName(None, u'partnerLink'), 'partnerLink', '__httpschemas_xmlsoap_orgws200303business_process_tReceive_partnerLink', pyxb.binding.datatypes.NCName, required=True)
    __partnerLink._DeclarationLocation = pyxb.utils.utility.Location('/tmp/pyxbdist.RHB65sy/PyXB-1.1.5/pyxb/bundles/wssplat/schemas/bpws.xsd', 417, 16)
    __partnerLink._UseLocation = pyxb.utils.utility.Location('/tmp/pyxbdist.RHB65sy/PyXB-1.1.5/pyxb/bundles/wssplat/schemas/bpws.xsd', 417, 16)
    
    partnerLink = property(__partnerLink.value, __partnerLink.set, None, None)

    
    # Attribute variable uses Python identifier variable
    __variable = pyxb.binding.content.AttributeUse(pyxb.namespace.ExpandedName(None, u'variable'), 'variable', '__httpschemas_xmlsoap_orgws200303business_process_tReceive_variable', pyxb.binding.datatypes.NCName)
    __variable._DeclarationLocation = pyxb.utils.utility.Location('/tmp/pyxbdist.RHB65sy/PyXB-1.1.5/pyxb/bundles/wssplat/schemas/bpws.xsd', 420, 16)
    __variable._UseLocation = pyxb.utils.utility.Location('/tmp/pyxbdist.RHB65sy/PyXB-1.1.5/pyxb/bundles/wssplat/schemas/bpws.xsd', 420, 16)
    
    variable = property(__variable.value, __variable.set, None, None)

    
    # Attribute createInstance uses Python identifier createInstance
    __createInstance = pyxb.binding.content.AttributeUse(pyxb.namespace.ExpandedName(None, u'createInstance'), 'createInstance', '__httpschemas_xmlsoap_orgws200303business_process_tReceive_createInstance', tBoolean, unicode_default=u'no')
    __createInstance._DeclarationLocation = pyxb.utils.utility.Location('/tmp/pyxbdist.RHB65sy/PyXB-1.1.5/pyxb/bundles/wssplat/schemas/bpws.xsd', 421, 16)
    __createInstance._UseLocation = pyxb.utils.utility.Location('/tmp/pyxbdist.RHB65sy/PyXB-1.1.5/pyxb/bundles/wssplat/schemas/bpws.xsd', 421, 16)
    
    createInstance = property(__createInstance.value, __createInstance.set, None, None)

    
    # Attribute name inherited from {http://schemas.xmlsoap.org/ws/2003/03/business-process/}tActivity
    
    # Attribute portType uses Python identifier portType
    __portType = pyxb.binding.content.AttributeUse(pyxb.namespace.ExpandedName(None, u'portType'), 'portType', '__httpschemas_xmlsoap_orgws200303business_process_tReceive_portType', pyxb.binding.datatypes.QName, required=True)
    __portType._DeclarationLocation = pyxb.utils.utility.Location('/tmp/pyxbdist.RHB65sy/PyXB-1.1.5/pyxb/bundles/wssplat/schemas/bpws.xsd', 418, 16)
    __portType._UseLocation = pyxb.utils.utility.Location('/tmp/pyxbdist.RHB65sy/PyXB-1.1.5/pyxb/bundles/wssplat/schemas/bpws.xsd', 418, 16)
    
    portType = property(__portType.value, __portType.set, None, None)

    
    # Attribute joinCondition inherited from {http://schemas.xmlsoap.org/ws/2003/03/business-process/}tActivity
    _AttributeWildcard = pyxb.binding.content.Wildcard(process_contents=pyxb.binding.content.Wildcard.PC_lax, namespace_constraint=(pyxb.binding.content.Wildcard.NC_not, u'http://schemas.xmlsoap.org/ws/2003/03/business-process/'))
    _HasWildcardElement = True

    _ElementMap = tActivity._ElementMap.copy()
    _ElementMap.update({
        __correlations.name() : __correlations
    })
    _AttributeMap = tActivity._AttributeMap.copy()
    _AttributeMap.update({
        __operation.name() : __operation,
        __partnerLink.name() : __partnerLink,
        __variable.name() : __variable,
        __createInstance.name() : __createInstance,
        __portType.name() : __portType
    })
Namespace.addCategoryObject('typeBinding', u'tReceive', tReceive)


# Complex type {http://schemas.xmlsoap.org/ws/2003/03/business-process/}tCopy with content type ELEMENT_ONLY
class tCopy (tExtensibleElements):
    _TypeDefinition = None
    _ContentTypeTag = pyxb.binding.basis.complexTypeDefinition._CT_ELEMENT_ONLY
    _Abstract = False
    _ExpandedName = pyxb.namespace.ExpandedName(Namespace, u'tCopy')
    _DefinitionLocation = pyxb.utils.utility.Location('/tmp/pyxbdist.RHB65sy/PyXB-1.1.5/pyxb/bundles/wssplat/schemas/bpws.xsd', 455, 4)
    # Base type is tExtensibleElements
    
    # Element {http://schemas.xmlsoap.org/ws/2003/03/business-process/}from uses Python identifier from_
    __from = pyxb.binding.content.ElementUse(pyxb.namespace.ExpandedName(Namespace, u'from'), 'from_', '__httpschemas_xmlsoap_orgws200303business_process_tCopy_httpschemas_xmlsoap_orgws200303business_processfrom', False)
    __from._DeclarationLocation = pyxb.utils.utility.Location('/tmp/pyxbdist.RHB65sy/PyXB-1.1.5/pyxb/bundles/wssplat/schemas/bpws.xsd', 466, 4)
    __from._UseLocation = None

    
    from_ = property(__from.value, __from.set, None, None)

    
    # Element {http://schemas.xmlsoap.org/ws/2003/03/business-process/}to uses Python identifier to
    __to = pyxb.binding.content.ElementUse(pyxb.namespace.ExpandedName(Namespace, u'to'), 'to', '__httpschemas_xmlsoap_orgws200303business_process_tCopy_httpschemas_xmlsoap_orgws200303business_processto', False)
    __to._DeclarationLocation = pyxb.utils.utility.Location('/tmp/pyxbdist.RHB65sy/PyXB-1.1.5/pyxb/bundles/wssplat/schemas/bpws.xsd', 482, 4)
    __to._UseLocation = None

    
    to = property(__to.value, __to.set, None, None)

    _AttributeWildcard = pyxb.binding.content.Wildcard(process_contents=pyxb.binding.content.Wildcard.PC_lax, namespace_constraint=(pyxb.binding.content.Wildcard.NC_not, u'http://schemas.xmlsoap.org/ws/2003/03/business-process/'))
    _HasWildcardElement = True

    _ElementMap = tExtensibleElements._ElementMap.copy()
    _ElementMap.update({
        __from.name() : __from,
        __to.name() : __to
    })
    _AttributeMap = tExtensibleElements._AttributeMap.copy()
    _AttributeMap.update({
        
    })
Namespace.addCategoryObject('typeBinding', u'tCopy', tCopy)


# Complex type {http://schemas.xmlsoap.org/ws/2003/03/business-process/}tReply with content type ELEMENT_ONLY
class tReply (tActivity):
    _TypeDefinition = None
    _ContentTypeTag = pyxb.binding.basis.complexTypeDefinition._CT_ELEMENT_ONLY
    _Abstract = False
    _ExpandedName = pyxb.namespace.ExpandedName(Namespace, u'tReply')
    _DefinitionLocation = pyxb.utils.utility.Location('/tmp/pyxbdist.RHB65sy/PyXB-1.1.5/pyxb/bundles/wssplat/schemas/bpws.xsd', 427, 4)
    # Base type is tActivity
    
    # Element {http://schemas.xmlsoap.org/ws/2003/03/business-process/}correlations uses Python identifier correlations
    __correlations = pyxb.binding.content.ElementUse(pyxb.namespace.ExpandedName(Namespace, u'correlations'), 'correlations', '__httpschemas_xmlsoap_orgws200303business_process_tReply_httpschemas_xmlsoap_orgws200303business_processcorrelations', False)
    __correlations._DeclarationLocation = pyxb.utils.utility.Location('/tmp/pyxbdist.RHB65sy/PyXB-1.1.5/pyxb/bundles/wssplat/schemas/bpws.xsd', 431, 20)
    __correlations._UseLocation = None

    
    correlations = property(__correlations.value, __correlations.set, None, None)

    
    # Element source ({http://schemas.xmlsoap.org/ws/2003/03/business-process/}source) inherited from {http://schemas.xmlsoap.org/ws/2003/03/business-process/}tActivity
    
    # Element target ({http://schemas.xmlsoap.org/ws/2003/03/business-process/}target) inherited from {http://schemas.xmlsoap.org/ws/2003/03/business-process/}tActivity
    
    # Attribute suppressJoinFailure inherited from {http://schemas.xmlsoap.org/ws/2003/03/business-process/}tActivity
    
    # Attribute partnerLink uses Python identifier partnerLink
    __partnerLink = pyxb.binding.content.AttributeUse(pyxb.namespace.ExpandedName(None, u'partnerLink'), 'partnerLink', '__httpschemas_xmlsoap_orgws200303business_process_tReply_partnerLink', pyxb.binding.datatypes.NCName, required=True)
    __partnerLink._DeclarationLocation = pyxb.utils.utility.Location('/tmp/pyxbdist.RHB65sy/PyXB-1.1.5/pyxb/bundles/wssplat/schemas/bpws.xsd', 434, 16)
    __partnerLink._UseLocation = pyxb.utils.utility.Location('/tmp/pyxbdist.RHB65sy/PyXB-1.1.5/pyxb/bundles/wssplat/schemas/bpws.xsd', 434, 16)
    
    partnerLink = property(__partnerLink.value, __partnerLink.set, None, None)

    
    # Attribute faultName uses Python identifier faultName
    __faultName = pyxb.binding.content.AttributeUse(pyxb.namespace.ExpandedName(None, u'faultName'), 'faultName', '__httpschemas_xmlsoap_orgws200303business_process_tReply_faultName', pyxb.binding.datatypes.QName)
    __faultName._DeclarationLocation = pyxb.utils.utility.Location('/tmp/pyxbdist.RHB65sy/PyXB-1.1.5/pyxb/bundles/wssplat/schemas/bpws.xsd', 439, 16)
    __faultName._UseLocation = pyxb.utils.utility.Location('/tmp/pyxbdist.RHB65sy/PyXB-1.1.5/pyxb/bundles/wssplat/schemas/bpws.xsd', 439, 16)
    
    faultName = property(__faultName.value, __faultName.set, None, None)

    
    # Attribute portType uses Python identifier portType
    __portType = pyxb.binding.content.AttributeUse(pyxb.namespace.ExpandedName(None, u'portType'), 'portType', '__httpschemas_xmlsoap_orgws200303business_process_tReply_portType', pyxb.binding.datatypes.QName, required=True)
    __portType._DeclarationLocation = pyxb.utils.utility.Location('/tmp/pyxbdist.RHB65sy/PyXB-1.1.5/pyxb/bundles/wssplat/schemas/bpws.xsd', 435, 16)
    __portType._UseLocation = pyxb.utils.utility.Location('/tmp/pyxbdist.RHB65sy/PyXB-1.1.5/pyxb/bundles/wssplat/schemas/bpws.xsd', 435, 16)
    
    portType = property(__portType.value, __portType.set, None, None)

    
    # Attribute name inherited from {http://schemas.xmlsoap.org/ws/2003/03/business-process/}tActivity
    
    # Attribute operation uses Python identifier operation
    __operation = pyxb.binding.content.AttributeUse(pyxb.namespace.ExpandedName(None, u'operation'), 'operation', '__httpschemas_xmlsoap_orgws200303business_process_tReply_operation', pyxb.binding.datatypes.NCName, required=True)
    __operation._DeclarationLocation = pyxb.utils.utility.Location('/tmp/pyxbdist.RHB65sy/PyXB-1.1.5/pyxb/bundles/wssplat/schemas/bpws.xsd', 436, 16)
    __operation._UseLocation = pyxb.utils.utility.Location('/tmp/pyxbdist.RHB65sy/PyXB-1.1.5/pyxb/bundles/wssplat/schemas/bpws.xsd', 436, 16)
    
    operation = property(__operation.value, __operation.set, None, None)

    
    # Attribute joinCondition inherited from {http://schemas.xmlsoap.org/ws/2003/03/business-process/}tActivity
    
    # Attribute variable uses Python identifier variable
    __variable = pyxb.binding.content.AttributeUse(pyxb.namespace.ExpandedName(None, u'variable'), 'variable', '__httpschemas_xmlsoap_orgws200303business_process_tReply_variable', pyxb.binding.datatypes.NCName)
    __variable._DeclarationLocation = pyxb.utils.utility.Location('/tmp/pyxbdist.RHB65sy/PyXB-1.1.5/pyxb/bundles/wssplat/schemas/bpws.xsd', 437, 16)
    __variable._UseLocation = pyxb.utils.utility.Location('/tmp/pyxbdist.RHB65sy/PyXB-1.1.5/pyxb/bundles/wssplat/schemas/bpws.xsd', 437, 16)
    
    variable = property(__variable.value, __variable.set, None, None)

    _AttributeWildcard = pyxb.binding.content.Wildcard(process_contents=pyxb.binding.content.Wildcard.PC_lax, namespace_constraint=(pyxb.binding.content.Wildcard.NC_not, u'http://schemas.xmlsoap.org/ws/2003/03/business-process/'))
    _HasWildcardElement = True

    _ElementMap = tActivity._ElementMap.copy()
    _ElementMap.update({
        __correlations.name() : __correlations
    })
    _AttributeMap = tActivity._AttributeMap.copy()
    _AttributeMap.update({
        __partnerLink.name() : __partnerLink,
        __faultName.name() : __faultName,
        __portType.name() : __portType,
        __operation.name() : __operation,
        __variable.name() : __variable
    })
Namespace.addCategoryObject('typeBinding', u'tReply', tReply)


# Complex type {http://schemas.xmlsoap.org/ws/2003/03/business-process/}tActivityContainer with content type ELEMENT_ONLY
class tActivityContainer (tExtensibleElements):
    _TypeDefinition = None
    _ContentTypeTag = pyxb.binding.basis.complexTypeDefinition._CT_ELEMENT_ONLY
    _Abstract = False
    _ExpandedName = pyxb.namespace.ExpandedName(Namespace, u'tActivityContainer')
    _DefinitionLocation = pyxb.utils.utility.Location('/tmp/pyxbdist.RHB65sy/PyXB-1.1.5/pyxb/bundles/wssplat/schemas/bpws.xsd', 167, 4)
    # Base type is tExtensibleElements
    
    # Element {http://schemas.xmlsoap.org/ws/2003/03/business-process/}flow uses Python identifier flow
    __flow = pyxb.binding.content.ElementUse(pyxb.namespace.ExpandedName(Namespace, u'flow'), 'flow', '__httpschemas_xmlsoap_orgws200303business_process_tActivityContainer_httpschemas_xmlsoap_orgws200303business_processflow', False)
    __flow._DeclarationLocation = pyxb.utils.utility.Location('/tmp/pyxbdist.RHB65sy/PyXB-1.1.5/pyxb/bundles/wssplat/schemas/bpws.xsd', 77, 12)
    __flow._UseLocation = None

    
    flow = property(__flow.value, __flow.set, None, None)

    
    # Element {http://schemas.xmlsoap.org/ws/2003/03/business-process/}reply uses Python identifier reply
    __reply = pyxb.binding.content.ElementUse(pyxb.namespace.ExpandedName(Namespace, u'reply'), 'reply', '__httpschemas_xmlsoap_orgws200303business_process_tActivityContainer_httpschemas_xmlsoap_orgws200303business_processreply', False)
    __reply._DeclarationLocation = pyxb.utils.utility.Location('/tmp/pyxbdist.RHB65sy/PyXB-1.1.5/pyxb/bundles/wssplat/schemas/bpws.xsd', 72, 12)
    __reply._UseLocation = None

    
    reply = property(__reply.value, __reply.set, None, None)

    
    # Element {http://schemas.xmlsoap.org/ws/2003/03/business-process/}pick uses Python identifier pick
    __pick = pyxb.binding.content.ElementUse(pyxb.namespace.ExpandedName(Namespace, u'pick'), 'pick', '__httpschemas_xmlsoap_orgws200303business_process_tActivityContainer_httpschemas_xmlsoap_orgws200303business_processpick', False)
    __pick._DeclarationLocation = pyxb.utils.utility.Location('/tmp/pyxbdist.RHB65sy/PyXB-1.1.5/pyxb/bundles/wssplat/schemas/bpws.xsd', 81, 12)
    __pick._UseLocation = None

    
    pick = property(__pick.value, __pick.set, None, None)

    
    # Element {http://schemas.xmlsoap.org/ws/2003/03/business-process/}empty uses Python identifier empty
    __empty = pyxb.binding.content.ElementUse(pyxb.namespace.ExpandedName(Namespace, u'empty'), 'empty', '__httpschemas_xmlsoap_orgws200303business_process_tActivityContainer_httpschemas_xmlsoap_orgws200303business_processempty', False)
    __empty._DeclarationLocation = pyxb.utils.utility.Location('/tmp/pyxbdist.RHB65sy/PyXB-1.1.5/pyxb/bundles/wssplat/schemas/bpws.xsd', 69, 12)
    __empty._UseLocation = None

    
    empty = property(__empty.value, __empty.set, None, None)

    
    # Element {http://schemas.xmlsoap.org/ws/2003/03/business-process/}invoke uses Python identifier invoke
    __invoke = pyxb.binding.content.ElementUse(pyxb.namespace.ExpandedName(Namespace, u'invoke'), 'invoke', '__httpschemas_xmlsoap_orgws200303business_process_tActivityContainer_httpschemas_xmlsoap_orgws200303business_processinvoke', False)
    __invoke._DeclarationLocation = pyxb.utils.utility.Location('/tmp/pyxbdist.RHB65sy/PyXB-1.1.5/pyxb/bundles/wssplat/schemas/bpws.xsd', 70, 12)
    __invoke._UseLocation = None

    
    invoke = property(__invoke.value, __invoke.set, None, None)

    
    # Element {http://schemas.xmlsoap.org/ws/2003/03/business-process/}switch uses Python identifier switch
    __switch = pyxb.binding.content.ElementUse(pyxb.namespace.ExpandedName(Namespace, u'switch'), 'switch', '__httpschemas_xmlsoap_orgws200303business_process_tActivityContainer_httpschemas_xmlsoap_orgws200303business_processswitch', False)
    __switch._DeclarationLocation = pyxb.utils.utility.Location('/tmp/pyxbdist.RHB65sy/PyXB-1.1.5/pyxb/bundles/wssplat/schemas/bpws.xsd', 78, 12)
    __switch._UseLocation = None

    
    switch = property(__switch.value, __switch.set, None, None)

    
    # Element {http://schemas.xmlsoap.org/ws/2003/03/business-process/}assign uses Python identifier assign
    __assign = pyxb.binding.content.ElementUse(pyxb.namespace.ExpandedName(Namespace, u'assign'), 'assign', '__httpschemas_xmlsoap_orgws200303business_process_tActivityContainer_httpschemas_xmlsoap_orgws200303business_processassign', False)
    __assign._DeclarationLocation = pyxb.utils.utility.Location('/tmp/pyxbdist.RHB65sy/PyXB-1.1.5/pyxb/bundles/wssplat/schemas/bpws.xsd', 73, 12)
    __assign._UseLocation = None

    
    assign = property(__assign.value, __assign.set, None, None)

    
    # Element {http://schemas.xmlsoap.org/ws/2003/03/business-process/}terminate uses Python identifier terminate
    __terminate = pyxb.binding.content.ElementUse(pyxb.namespace.ExpandedName(Namespace, u'terminate'), 'terminate', '__httpschemas_xmlsoap_orgws200303business_process_tActivityContainer_httpschemas_xmlsoap_orgws200303business_processterminate', False)
    __terminate._DeclarationLocation = pyxb.utils.utility.Location('/tmp/pyxbdist.RHB65sy/PyXB-1.1.5/pyxb/bundles/wssplat/schemas/bpws.xsd', 76, 12)
    __terminate._UseLocation = None

    
    terminate = property(__terminate.value, __terminate.set, None, None)

    
    # Element {http://schemas.xmlsoap.org/ws/2003/03/business-process/}throw uses Python identifier throw
    __throw = pyxb.binding.content.ElementUse(pyxb.namespace.ExpandedName(Namespace, u'throw'), 'throw', '__httpschemas_xmlsoap_orgws200303business_process_tActivityContainer_httpschemas_xmlsoap_orgws200303business_processthrow', False)
    __throw._DeclarationLocation = pyxb.utils.utility.Location('/tmp/pyxbdist.RHB65sy/PyXB-1.1.5/pyxb/bundles/wssplat/schemas/bpws.xsd', 75, 12)
    __throw._UseLocation = None

    
    throw = property(__throw.value, __throw.set, None, None)

    
    # Element {http://schemas.xmlsoap.org/ws/2003/03/business-process/}while uses Python identifier while_
    __while = pyxb.binding.content.ElementUse(pyxb.namespace.ExpandedName(Namespace, u'while'), 'while_', '__httpschemas_xmlsoap_orgws200303business_process_tActivityContainer_httpschemas_xmlsoap_orgws200303business_processwhile', False)
    __while._DeclarationLocation = pyxb.utils.utility.Location('/tmp/pyxbdist.RHB65sy/PyXB-1.1.5/pyxb/bundles/wssplat/schemas/bpws.xsd', 79, 12)
    __while._UseLocation = None

    
    while_ = property(__while.value, __while.set, None, None)

    
    # Element {http://schemas.xmlsoap.org/ws/2003/03/business-process/}receive uses Python identifier receive
    __receive = pyxb.binding.content.ElementUse(pyxb.namespace.ExpandedName(Namespace, u'receive'), 'receive', '__httpschemas_xmlsoap_orgws200303business_process_tActivityContainer_httpschemas_xmlsoap_orgws200303business_processreceive', False)
    __receive._DeclarationLocation = pyxb.utils.utility.Location('/tmp/pyxbdist.RHB65sy/PyXB-1.1.5/pyxb/bundles/wssplat/schemas/bpws.xsd', 71, 12)
    __receive._UseLocation = None

    
    receive = property(__receive.value, __receive.set, None, None)

    
    # Element {http://schemas.xmlsoap.org/ws/2003/03/business-process/}scope uses Python identifier scope
    __scope = pyxb.binding.content.ElementUse(pyxb.namespace.ExpandedName(Namespace, u'scope'), 'scope', '__httpschemas_xmlsoap_orgws200303business_process_tActivityContainer_httpschemas_xmlsoap_orgws200303business_processscope', False)
    __scope._DeclarationLocation = pyxb.utils.utility.Location('/tmp/pyxbdist.RHB65sy/PyXB-1.1.5/pyxb/bundles/wssplat/schemas/bpws.xsd', 82, 12)
    __scope._UseLocation = None

    
    scope = property(__scope.value, __scope.set, None, None)

    
    # Element {http://schemas.xmlsoap.org/ws/2003/03/business-process/}wait uses Python identifier wait
    __wait = pyxb.binding.content.ElementUse(pyxb.namespace.ExpandedName(Namespace, u'wait'), 'wait', '__httpschemas_xmlsoap_orgws200303business_process_tActivityContainer_httpschemas_xmlsoap_orgws200303business_processwait', False)
    __wait._DeclarationLocation = pyxb.utils.utility.Location('/tmp/pyxbdist.RHB65sy/PyXB-1.1.5/pyxb/bundles/wssplat/schemas/bpws.xsd', 74, 12)
    __wait._UseLocation = None

    
    wait = property(__wait.value, __wait.set, None, None)

    
    # Element {http://schemas.xmlsoap.org/ws/2003/03/business-process/}sequence uses Python identifier sequence
    __sequence = pyxb.binding.content.ElementUse(pyxb.namespace.ExpandedName(Namespace, u'sequence'), 'sequence', '__httpschemas_xmlsoap_orgws200303business_process_tActivityContainer_httpschemas_xmlsoap_orgws200303business_processsequence', False)
    __sequence._DeclarationLocation = pyxb.utils.utility.Location('/tmp/pyxbdist.RHB65sy/PyXB-1.1.5/pyxb/bundles/wssplat/schemas/bpws.xsd', 80, 12)
    __sequence._UseLocation = None

    
    sequence = property(__sequence.value, __sequence.set, None, None)

    _AttributeWildcard = pyxb.binding.content.Wildcard(process_contents=pyxb.binding.content.Wildcard.PC_lax, namespace_constraint=(pyxb.binding.content.Wildcard.NC_not, u'http://schemas.xmlsoap.org/ws/2003/03/business-process/'))
    _HasWildcardElement = True

    _ElementMap = tExtensibleElements._ElementMap.copy()
    _ElementMap.update({
        __flow.name() : __flow,
        __reply.name() : __reply,
        __pick.name() : __pick,
        __empty.name() : __empty,
        __invoke.name() : __invoke,
        __switch.name() : __switch,
        __assign.name() : __assign,
        __terminate.name() : __terminate,
        __throw.name() : __throw,
        __while.name() : __while,
        __receive.name() : __receive,
        __scope.name() : __scope,
        __wait.name() : __wait,
        __sequence.name() : __sequence
    })
    _AttributeMap = tExtensibleElements._AttributeMap.copy()
    _AttributeMap.update({
        
    })
Namespace.addCategoryObject('typeBinding', u'tActivityContainer', tActivityContainer)


# Complex type [anonymous] with content type ELEMENT_ONLY
class CTD_ANON (tActivityContainer):
    _TypeDefinition = None
    _ContentTypeTag = pyxb.binding.basis.complexTypeDefinition._CT_ELEMENT_ONLY
    _Abstract = False
    _ExpandedName = None
    _DefinitionLocation = pyxb.utils.utility.Location('/tmp/pyxbdist.RHB65sy/PyXB-1.1.5/pyxb/bundles/wssplat/schemas/bpws.xsd', 568, 24)
    # Base type is tActivityContainer
    
    # Element flow ({http://schemas.xmlsoap.org/ws/2003/03/business-process/}flow) inherited from {http://schemas.xmlsoap.org/ws/2003/03/business-process/}tActivityContainer
    
    # Element reply ({http://schemas.xmlsoap.org/ws/2003/03/business-process/}reply) inherited from {http://schemas.xmlsoap.org/ws/2003/03/business-process/}tActivityContainer
    
    # Element pick ({http://schemas.xmlsoap.org/ws/2003/03/business-process/}pick) inherited from {http://schemas.xmlsoap.org/ws/2003/03/business-process/}tActivityContainer
    
    # Element empty ({http://schemas.xmlsoap.org/ws/2003/03/business-process/}empty) inherited from {http://schemas.xmlsoap.org/ws/2003/03/business-process/}tActivityContainer
    
    # Element invoke ({http://schemas.xmlsoap.org/ws/2003/03/business-process/}invoke) inherited from {http://schemas.xmlsoap.org/ws/2003/03/business-process/}tActivityContainer
    
    # Element switch ({http://schemas.xmlsoap.org/ws/2003/03/business-process/}switch) inherited from {http://schemas.xmlsoap.org/ws/2003/03/business-process/}tActivityContainer
    
    # Element assign ({http://schemas.xmlsoap.org/ws/2003/03/business-process/}assign) inherited from {http://schemas.xmlsoap.org/ws/2003/03/business-process/}tActivityContainer
    
    # Element terminate ({http://schemas.xmlsoap.org/ws/2003/03/business-process/}terminate) inherited from {http://schemas.xmlsoap.org/ws/2003/03/business-process/}tActivityContainer
    
    # Element throw ({http://schemas.xmlsoap.org/ws/2003/03/business-process/}throw) inherited from {http://schemas.xmlsoap.org/ws/2003/03/business-process/}tActivityContainer
    
    # Element while_ ({http://schemas.xmlsoap.org/ws/2003/03/business-process/}while) inherited from {http://schemas.xmlsoap.org/ws/2003/03/business-process/}tActivityContainer
    
    # Element receive ({http://schemas.xmlsoap.org/ws/2003/03/business-process/}receive) inherited from {http://schemas.xmlsoap.org/ws/2003/03/business-process/}tActivityContainer
    
    # Element scope ({http://schemas.xmlsoap.org/ws/2003/03/business-process/}scope) inherited from {http://schemas.xmlsoap.org/ws/2003/03/business-process/}tActivityContainer
    
    # Element wait ({http://schemas.xmlsoap.org/ws/2003/03/business-process/}wait) inherited from {http://schemas.xmlsoap.org/ws/2003/03/business-process/}tActivityContainer
    
    # Element sequence ({http://schemas.xmlsoap.org/ws/2003/03/business-process/}sequence) inherited from {http://schemas.xmlsoap.org/ws/2003/03/business-process/}tActivityContainer
    
    # Attribute condition uses Python identifier condition
    __condition = pyxb.binding.content.AttributeUse(pyxb.namespace.ExpandedName(None, u'condition'), 'condition', '__httpschemas_xmlsoap_orgws200303business_process_CTD_ANON_condition', tBoolean_expr, required=True)
    __condition._DeclarationLocation = pyxb.utils.utility.Location('/tmp/pyxbdist.RHB65sy/PyXB-1.1.5/pyxb/bundles/wssplat/schemas/bpws.xsd', 571, 36)
    __condition._UseLocation = pyxb.utils.utility.Location('/tmp/pyxbdist.RHB65sy/PyXB-1.1.5/pyxb/bundles/wssplat/schemas/bpws.xsd', 571, 36)
    
    condition = property(__condition.value, __condition.set, None, None)

    _AttributeWildcard = pyxb.binding.content.Wildcard(process_contents=pyxb.binding.content.Wildcard.PC_lax, namespace_constraint=(pyxb.binding.content.Wildcard.NC_not, u'http://schemas.xmlsoap.org/ws/2003/03/business-process/'))
    _HasWildcardElement = True

    _ElementMap = tActivityContainer._ElementMap.copy()
    _ElementMap.update({
        
    })
    _AttributeMap = tActivityContainer._AttributeMap.copy()
    _AttributeMap.update({
        __condition.name() : __condition
    })



# Complex type {http://schemas.xmlsoap.org/ws/2003/03/business-process/}tActivityOrCompensateContainer with content type ELEMENT_ONLY
class tActivityOrCompensateContainer (tExtensibleElements):
    _TypeDefinition = None
    _ContentTypeTag = pyxb.binding.basis.complexTypeDefinition._CT_ELEMENT_ONLY
    _Abstract = False
    _ExpandedName = pyxb.namespace.ExpandedName(Namespace, u'tActivityOrCompensateContainer')
    _DefinitionLocation = pyxb.utils.utility.Location('/tmp/pyxbdist.RHB65sy/PyXB-1.1.5/pyxb/bundles/wssplat/schemas/bpws.xsd', 176, 4)
    # Base type is tExtensibleElements
    
    # Element {http://schemas.xmlsoap.org/ws/2003/03/business-process/}throw uses Python identifier throw
    __throw = pyxb.binding.content.ElementUse(pyxb.namespace.ExpandedName(Namespace, u'throw'), 'throw', '__httpschemas_xmlsoap_orgws200303business_process_tActivityOrCompensateContainer_httpschemas_xmlsoap_orgws200303business_processthrow', False)
    __throw._DeclarationLocation = pyxb.utils.utility.Location('/tmp/pyxbdist.RHB65sy/PyXB-1.1.5/pyxb/bundles/wssplat/schemas/bpws.xsd', 75, 12)
    __throw._UseLocation = None

    
    throw = property(__throw.value, __throw.set, None, None)

    
    # Element {http://schemas.xmlsoap.org/ws/2003/03/business-process/}invoke uses Python identifier invoke
    __invoke = pyxb.binding.content.ElementUse(pyxb.namespace.ExpandedName(Namespace, u'invoke'), 'invoke', '__httpschemas_xmlsoap_orgws200303business_process_tActivityOrCompensateContainer_httpschemas_xmlsoap_orgws200303business_processinvoke', False)
    __invoke._DeclarationLocation = pyxb.utils.utility.Location('/tmp/pyxbdist.RHB65sy/PyXB-1.1.5/pyxb/bundles/wssplat/schemas/bpws.xsd', 70, 12)
    __invoke._UseLocation = None

    
    invoke = property(__invoke.value, __invoke.set, None, None)

    
    # Element {http://schemas.xmlsoap.org/ws/2003/03/business-process/}while uses Python identifier while_
    __while = pyxb.binding.content.ElementUse(pyxb.namespace.ExpandedName(Namespace, u'while'), 'while_', '__httpschemas_xmlsoap_orgws200303business_process_tActivityOrCompensateContainer_httpschemas_xmlsoap_orgws200303business_processwhile', False)
    __while._DeclarationLocation = pyxb.utils.utility.Location('/tmp/pyxbdist.RHB65sy/PyXB-1.1.5/pyxb/bundles/wssplat/schemas/bpws.xsd', 79, 12)
    __while._UseLocation = None

    
    while_ = property(__while.value, __while.set, None, None)

    
    # Element {http://schemas.xmlsoap.org/ws/2003/03/business-process/}assign uses Python identifier assign
    __assign = pyxb.binding.content.ElementUse(pyxb.namespace.ExpandedName(Namespace, u'assign'), 'assign', '__httpschemas_xmlsoap_orgws200303business_process_tActivityOrCompensateContainer_httpschemas_xmlsoap_orgws200303business_processassign', False)
    __assign._DeclarationLocation = pyxb.utils.utility.Location('/tmp/pyxbdist.RHB65sy/PyXB-1.1.5/pyxb/bundles/wssplat/schemas/bpws.xsd', 73, 12)
    __assign._UseLocation = None

    
    assign = property(__assign.value, __assign.set, None, None)

    
    # Element {http://schemas.xmlsoap.org/ws/2003/03/business-process/}terminate uses Python identifier terminate
    __terminate = pyxb.binding.content.ElementUse(pyxb.namespace.ExpandedName(Namespace, u'terminate'), 'terminate', '__httpschemas_xmlsoap_orgws200303business_process_tActivityOrCompensateContainer_httpschemas_xmlsoap_orgws200303business_processterminate', False)
    __terminate._DeclarationLocation = pyxb.utils.utility.Location('/tmp/pyxbdist.RHB65sy/PyXB-1.1.5/pyxb/bundles/wssplat/schemas/bpws.xsd', 76, 12)
    __terminate._UseLocation = None

    
    terminate = property(__terminate.value, __terminate.set, None, None)

    
    # Element {http://schemas.xmlsoap.org/ws/2003/03/business-process/}switch uses Python identifier switch
    __switch = pyxb.binding.content.ElementUse(pyxb.namespace.ExpandedName(Namespace, u'switch'), 'switch', '__httpschemas_xmlsoap_orgws200303business_process_tActivityOrCompensateContainer_httpschemas_xmlsoap_orgws200303business_processswitch', False)
    __switch._DeclarationLocation = pyxb.utils.utility.Location('/tmp/pyxbdist.RHB65sy/PyXB-1.1.5/pyxb/bundles/wssplat/schemas/bpws.xsd', 78, 12)
    __switch._UseLocation = None

    
    switch = property(__switch.value, __switch.set, None, None)

    
    # Element {http://schemas.xmlsoap.org/ws/2003/03/business-process/}scope uses Python identifier scope
    __scope = pyxb.binding.content.ElementUse(pyxb.namespace.ExpandedName(Namespace, u'scope'), 'scope', '__httpschemas_xmlsoap_orgws200303business_process_tActivityOrCompensateContainer_httpschemas_xmlsoap_orgws200303business_processscope', False)
    __scope._DeclarationLocation = pyxb.utils.utility.Location('/tmp/pyxbdist.RHB65sy/PyXB-1.1.5/pyxb/bundles/wssplat/schemas/bpws.xsd', 82, 12)
    __scope._UseLocation = None

    
    scope = property(__scope.value, __scope.set, None, None)

    
    # Element {http://schemas.xmlsoap.org/ws/2003/03/business-process/}receive uses Python identifier receive
    __receive = pyxb.binding.content.ElementUse(pyxb.namespace.ExpandedName(Namespace, u'receive'), 'receive', '__httpschemas_xmlsoap_orgws200303business_process_tActivityOrCompensateContainer_httpschemas_xmlsoap_orgws200303business_processreceive', False)
    __receive._DeclarationLocation = pyxb.utils.utility.Location('/tmp/pyxbdist.RHB65sy/PyXB-1.1.5/pyxb/bundles/wssplat/schemas/bpws.xsd', 71, 12)
    __receive._UseLocation = None

    
    receive = property(__receive.value, __receive.set, None, None)

    
    # Element {http://schemas.xmlsoap.org/ws/2003/03/business-process/}wait uses Python identifier wait
    __wait = pyxb.binding.content.ElementUse(pyxb.namespace.ExpandedName(Namespace, u'wait'), 'wait', '__httpschemas_xmlsoap_orgws200303business_process_tActivityOrCompensateContainer_httpschemas_xmlsoap_orgws200303business_processwait', False)
    __wait._DeclarationLocation = pyxb.utils.utility.Location('/tmp/pyxbdist.RHB65sy/PyXB-1.1.5/pyxb/bundles/wssplat/schemas/bpws.xsd', 74, 12)
    __wait._UseLocation = None

    
    wait = property(__wait.value, __wait.set, None, None)

    
    # Element {http://schemas.xmlsoap.org/ws/2003/03/business-process/}sequence uses Python identifier sequence
    __sequence = pyxb.binding.content.ElementUse(pyxb.namespace.ExpandedName(Namespace, u'sequence'), 'sequence', '__httpschemas_xmlsoap_orgws200303business_process_tActivityOrCompensateContainer_httpschemas_xmlsoap_orgws200303business_processsequence', False)
    __sequence._DeclarationLocation = pyxb.utils.utility.Location('/tmp/pyxbdist.RHB65sy/PyXB-1.1.5/pyxb/bundles/wssplat/schemas/bpws.xsd', 80, 12)
    __sequence._UseLocation = None

    
    sequence = property(__sequence.value, __sequence.set, None, None)

    
    # Element {http://schemas.xmlsoap.org/ws/2003/03/business-process/}pick uses Python identifier pick
    __pick = pyxb.binding.content.ElementUse(pyxb.namespace.ExpandedName(Namespace, u'pick'), 'pick', '__httpschemas_xmlsoap_orgws200303business_process_tActivityOrCompensateContainer_httpschemas_xmlsoap_orgws200303business_processpick', False)
    __pick._DeclarationLocation = pyxb.utils.utility.Location('/tmp/pyxbdist.RHB65sy/PyXB-1.1.5/pyxb/bundles/wssplat/schemas/bpws.xsd', 81, 12)
    __pick._UseLocation = None

    
    pick = property(__pick.value, __pick.set, None, None)

    
    # Element {http://schemas.xmlsoap.org/ws/2003/03/business-process/}flow uses Python identifier flow
    __flow = pyxb.binding.content.ElementUse(pyxb.namespace.ExpandedName(Namespace, u'flow'), 'flow', '__httpschemas_xmlsoap_orgws200303business_process_tActivityOrCompensateContainer_httpschemas_xmlsoap_orgws200303business_processflow', False)
    __flow._DeclarationLocation = pyxb.utils.utility.Location('/tmp/pyxbdist.RHB65sy/PyXB-1.1.5/pyxb/bundles/wssplat/schemas/bpws.xsd', 77, 12)
    __flow._UseLocation = None

    
    flow = property(__flow.value, __flow.set, None, None)

    
    # Element {http://schemas.xmlsoap.org/ws/2003/03/business-process/}compensate uses Python identifier compensate
    __compensate = pyxb.binding.content.ElementUse(pyxb.namespace.ExpandedName(Namespace, u'compensate'), 'compensate', '__httpschemas_xmlsoap_orgws200303business_process_tActivityOrCompensateContainer_httpschemas_xmlsoap_orgws200303business_processcompensate', False)
    __compensate._DeclarationLocation = pyxb.utils.utility.Location('/tmp/pyxbdist.RHB65sy/PyXB-1.1.5/pyxb/bundles/wssplat/schemas/bpws.xsd', 181, 20)
    __compensate._UseLocation = None

    
    compensate = property(__compensate.value, __compensate.set, None, None)

    
    # Element {http://schemas.xmlsoap.org/ws/2003/03/business-process/}reply uses Python identifier reply
    __reply = pyxb.binding.content.ElementUse(pyxb.namespace.ExpandedName(Namespace, u'reply'), 'reply', '__httpschemas_xmlsoap_orgws200303business_process_tActivityOrCompensateContainer_httpschemas_xmlsoap_orgws200303business_processreply', False)
    __reply._DeclarationLocation = pyxb.utils.utility.Location('/tmp/pyxbdist.RHB65sy/PyXB-1.1.5/pyxb/bundles/wssplat/schemas/bpws.xsd', 72, 12)
    __reply._UseLocation = None

    
    reply = property(__reply.value, __reply.set, None, None)

    
    # Element {http://schemas.xmlsoap.org/ws/2003/03/business-process/}empty uses Python identifier empty
    __empty = pyxb.binding.content.ElementUse(pyxb.namespace.ExpandedName(Namespace, u'empty'), 'empty', '__httpschemas_xmlsoap_orgws200303business_process_tActivityOrCompensateContainer_httpschemas_xmlsoap_orgws200303business_processempty', False)
    __empty._DeclarationLocation = pyxb.utils.utility.Location('/tmp/pyxbdist.RHB65sy/PyXB-1.1.5/pyxb/bundles/wssplat/schemas/bpws.xsd', 69, 12)
    __empty._UseLocation = None

    
    empty = property(__empty.value, __empty.set, None, None)

    _AttributeWildcard = pyxb.binding.content.Wildcard(process_contents=pyxb.binding.content.Wildcard.PC_lax, namespace_constraint=(pyxb.binding.content.Wildcard.NC_not, u'http://schemas.xmlsoap.org/ws/2003/03/business-process/'))
    _HasWildcardElement = True

    _ElementMap = tExtensibleElements._ElementMap.copy()
    _ElementMap.update({
        __throw.name() : __throw,
        __invoke.name() : __invoke,
        __while.name() : __while,
        __assign.name() : __assign,
        __terminate.name() : __terminate,
        __switch.name() : __switch,
        __scope.name() : __scope,
        __receive.name() : __receive,
        __wait.name() : __wait,
        __sequence.name() : __sequence,
        __pick.name() : __pick,
        __flow.name() : __flow,
        __compensate.name() : __compensate,
        __reply.name() : __reply,
        __empty.name() : __empty
    })
    _AttributeMap = tExtensibleElements._AttributeMap.copy()
    _AttributeMap.update({
        
    })
Namespace.addCategoryObject('typeBinding', u'tActivityOrCompensateContainer', tActivityOrCompensateContainer)


# Complex type {http://schemas.xmlsoap.org/ws/2003/03/business-process/}tCatch with content type ELEMENT_ONLY
class tCatch (tActivityOrCompensateContainer):
    _TypeDefinition = None
    _ContentTypeTag = pyxb.binding.basis.complexTypeDefinition._CT_ELEMENT_ONLY
    _Abstract = False
    _ExpandedName = pyxb.namespace.ExpandedName(Namespace, u'tCatch')
    _DefinitionLocation = pyxb.utils.utility.Location('/tmp/pyxbdist.RHB65sy/PyXB-1.1.5/pyxb/bundles/wssplat/schemas/bpws.xsd', 157, 4)
    # Base type is tActivityOrCompensateContainer
    
    # Element throw ({http://schemas.xmlsoap.org/ws/2003/03/business-process/}throw) inherited from {http://schemas.xmlsoap.org/ws/2003/03/business-process/}tActivityOrCompensateContainer
    
    # Element invoke ({http://schemas.xmlsoap.org/ws/2003/03/business-process/}invoke) inherited from {http://schemas.xmlsoap.org/ws/2003/03/business-process/}tActivityOrCompensateContainer
    
    # Element while_ ({http://schemas.xmlsoap.org/ws/2003/03/business-process/}while) inherited from {http://schemas.xmlsoap.org/ws/2003/03/business-process/}tActivityOrCompensateContainer
    
    # Element assign ({http://schemas.xmlsoap.org/ws/2003/03/business-process/}assign) inherited from {http://schemas.xmlsoap.org/ws/2003/03/business-process/}tActivityOrCompensateContainer
    
    # Element terminate ({http://schemas.xmlsoap.org/ws/2003/03/business-process/}terminate) inherited from {http://schemas.xmlsoap.org/ws/2003/03/business-process/}tActivityOrCompensateContainer
    
    # Element switch ({http://schemas.xmlsoap.org/ws/2003/03/business-process/}switch) inherited from {http://schemas.xmlsoap.org/ws/2003/03/business-process/}tActivityOrCompensateContainer
    
    # Element scope ({http://schemas.xmlsoap.org/ws/2003/03/business-process/}scope) inherited from {http://schemas.xmlsoap.org/ws/2003/03/business-process/}tActivityOrCompensateContainer
    
    # Element receive ({http://schemas.xmlsoap.org/ws/2003/03/business-process/}receive) inherited from {http://schemas.xmlsoap.org/ws/2003/03/business-process/}tActivityOrCompensateContainer
    
    # Element wait ({http://schemas.xmlsoap.org/ws/2003/03/business-process/}wait) inherited from {http://schemas.xmlsoap.org/ws/2003/03/business-process/}tActivityOrCompensateContainer
    
    # Element sequence ({http://schemas.xmlsoap.org/ws/2003/03/business-process/}sequence) inherited from {http://schemas.xmlsoap.org/ws/2003/03/business-process/}tActivityOrCompensateContainer
    
    # Element pick ({http://schemas.xmlsoap.org/ws/2003/03/business-process/}pick) inherited from {http://schemas.xmlsoap.org/ws/2003/03/business-process/}tActivityOrCompensateContainer
    
    # Element flow ({http://schemas.xmlsoap.org/ws/2003/03/business-process/}flow) inherited from {http://schemas.xmlsoap.org/ws/2003/03/business-process/}tActivityOrCompensateContainer
    
    # Element compensate ({http://schemas.xmlsoap.org/ws/2003/03/business-process/}compensate) inherited from {http://schemas.xmlsoap.org/ws/2003/03/business-process/}tActivityOrCompensateContainer
    
    # Element reply ({http://schemas.xmlsoap.org/ws/2003/03/business-process/}reply) inherited from {http://schemas.xmlsoap.org/ws/2003/03/business-process/}tActivityOrCompensateContainer
    
    # Element empty ({http://schemas.xmlsoap.org/ws/2003/03/business-process/}empty) inherited from {http://schemas.xmlsoap.org/ws/2003/03/business-process/}tActivityOrCompensateContainer
    
    # Attribute faultVariable uses Python identifier faultVariable
    __faultVariable = pyxb.binding.content.AttributeUse(pyxb.namespace.ExpandedName(None, u'faultVariable'), 'faultVariable', '__httpschemas_xmlsoap_orgws200303business_process_tCatch_faultVariable', pyxb.binding.datatypes.NCName)
    __faultVariable._DeclarationLocation = pyxb.utils.utility.Location('/tmp/pyxbdist.RHB65sy/PyXB-1.1.5/pyxb/bundles/wssplat/schemas/bpws.xsd', 161, 16)
    __faultVariable._UseLocation = pyxb.utils.utility.Location('/tmp/pyxbdist.RHB65sy/PyXB-1.1.5/pyxb/bundles/wssplat/schemas/bpws.xsd', 161, 16)
    
    faultVariable = property(__faultVariable.value, __faultVariable.set, None, None)

    
    # Attribute faultName uses Python identifier faultName
    __faultName = pyxb.binding.content.AttributeUse(pyxb.namespace.ExpandedName(None, u'faultName'), 'faultName', '__httpschemas_xmlsoap_orgws200303business_process_tCatch_faultName', pyxb.binding.datatypes.QName)
    __faultName._DeclarationLocation = pyxb.utils.utility.Location('/tmp/pyxbdist.RHB65sy/PyXB-1.1.5/pyxb/bundles/wssplat/schemas/bpws.xsd', 160, 16)
    __faultName._UseLocation = pyxb.utils.utility.Location('/tmp/pyxbdist.RHB65sy/PyXB-1.1.5/pyxb/bundles/wssplat/schemas/bpws.xsd', 160, 16)
    
    faultName = property(__faultName.value, __faultName.set, None, None)

    _AttributeWildcard = pyxb.binding.content.Wildcard(process_contents=pyxb.binding.content.Wildcard.PC_lax, namespace_constraint=(pyxb.binding.content.Wildcard.NC_not, u'http://schemas.xmlsoap.org/ws/2003/03/business-process/'))
    _HasWildcardElement = True

    _ElementMap = tActivityOrCompensateContainer._ElementMap.copy()
    _ElementMap.update({
        
    })
    _AttributeMap = tActivityOrCompensateContainer._AttributeMap.copy()
    _AttributeMap.update({
        __faultVariable.name() : __faultVariable,
        __faultName.name() : __faultName
    })
Namespace.addCategoryObject('typeBinding', u'tCatch', tCatch)


# Complex type {http://schemas.xmlsoap.org/ws/2003/03/business-process/}tThrow with content type ELEMENT_ONLY
class tThrow (tActivity):
    _TypeDefinition = None
    _ContentTypeTag = pyxb.binding.basis.complexTypeDefinition._CT_ELEMENT_ONLY
    _Abstract = False
    _ExpandedName = pyxb.namespace.ExpandedName(Namespace, u'tThrow')
    _DefinitionLocation = pyxb.utils.utility.Location('/tmp/pyxbdist.RHB65sy/PyXB-1.1.5/pyxb/bundles/wssplat/schemas/bpws.xsd', 509, 4)
    # Base type is tActivity
    
    # Element source ({http://schemas.xmlsoap.org/ws/2003/03/business-process/}source) inherited from {http://schemas.xmlsoap.org/ws/2003/03/business-process/}tActivity
    
    # Element target ({http://schemas.xmlsoap.org/ws/2003/03/business-process/}target) inherited from {http://schemas.xmlsoap.org/ws/2003/03/business-process/}tActivity
    
    # Attribute name inherited from {http://schemas.xmlsoap.org/ws/2003/03/business-process/}tActivity
    
    # Attribute faultVariable uses Python identifier faultVariable
    __faultVariable = pyxb.binding.content.AttributeUse(pyxb.namespace.ExpandedName(None, u'faultVariable'), 'faultVariable', '__httpschemas_xmlsoap_orgws200303business_process_tThrow_faultVariable', pyxb.binding.datatypes.NCName)
    __faultVariable._DeclarationLocation = pyxb.utils.utility.Location('/tmp/pyxbdist.RHB65sy/PyXB-1.1.5/pyxb/bundles/wssplat/schemas/bpws.xsd', 513, 16)
    __faultVariable._UseLocation = pyxb.utils.utility.Location('/tmp/pyxbdist.RHB65sy/PyXB-1.1.5/pyxb/bundles/wssplat/schemas/bpws.xsd', 513, 16)
    
    faultVariable = property(__faultVariable.value, __faultVariable.set, None, None)

    
    # Attribute faultName uses Python identifier faultName
    __faultName = pyxb.binding.content.AttributeUse(pyxb.namespace.ExpandedName(None, u'faultName'), 'faultName', '__httpschemas_xmlsoap_orgws200303business_process_tThrow_faultName', pyxb.binding.datatypes.QName, required=True)
    __faultName._DeclarationLocation = pyxb.utils.utility.Location('/tmp/pyxbdist.RHB65sy/PyXB-1.1.5/pyxb/bundles/wssplat/schemas/bpws.xsd', 512, 16)
    __faultName._UseLocation = pyxb.utils.utility.Location('/tmp/pyxbdist.RHB65sy/PyXB-1.1.5/pyxb/bundles/wssplat/schemas/bpws.xsd', 512, 16)
    
    faultName = property(__faultName.value, __faultName.set, None, None)

    
    # Attribute suppressJoinFailure inherited from {http://schemas.xmlsoap.org/ws/2003/03/business-process/}tActivity
    
    # Attribute joinCondition inherited from {http://schemas.xmlsoap.org/ws/2003/03/business-process/}tActivity
    _AttributeWildcard = pyxb.binding.content.Wildcard(process_contents=pyxb.binding.content.Wildcard.PC_lax, namespace_constraint=(pyxb.binding.content.Wildcard.NC_not, u'http://schemas.xmlsoap.org/ws/2003/03/business-process/'))
    _HasWildcardElement = True

    _ElementMap = tActivity._ElementMap.copy()
    _ElementMap.update({
        
    })
    _AttributeMap = tActivity._AttributeMap.copy()
    _AttributeMap.update({
        __faultVariable.name() : __faultVariable,
        __faultName.name() : __faultName
    })
Namespace.addCategoryObject('typeBinding', u'tThrow', tThrow)


# Complex type {http://schemas.xmlsoap.org/ws/2003/03/business-process/}tEmpty with content type ELEMENT_ONLY
class tEmpty (tActivity):
    _TypeDefinition = None
    _ContentTypeTag = pyxb.binding.basis.complexTypeDefinition._CT_ELEMENT_ONLY
    _Abstract = False
    _ExpandedName = pyxb.namespace.ExpandedName(Namespace, u'tEmpty')
    _DefinitionLocation = pyxb.utils.utility.Location('/tmp/pyxbdist.RHB65sy/PyXB-1.1.5/pyxb/bundles/wssplat/schemas/bpws.xsd', 325, 4)
    # Base type is tActivity
    
    # Element source ({http://schemas.xmlsoap.org/ws/2003/03/business-process/}source) inherited from {http://schemas.xmlsoap.org/ws/2003/03/business-process/}tActivity
    
    # Element target ({http://schemas.xmlsoap.org/ws/2003/03/business-process/}target) inherited from {http://schemas.xmlsoap.org/ws/2003/03/business-process/}tActivity
    
    # Attribute name inherited from {http://schemas.xmlsoap.org/ws/2003/03/business-process/}tActivity
    
    # Attribute joinCondition inherited from {http://schemas.xmlsoap.org/ws/2003/03/business-process/}tActivity
    
    # Attribute suppressJoinFailure inherited from {http://schemas.xmlsoap.org/ws/2003/03/business-process/}tActivity
    _AttributeWildcard = pyxb.binding.content.Wildcard(process_contents=pyxb.binding.content.Wildcard.PC_lax, namespace_constraint=(pyxb.binding.content.Wildcard.NC_not, u'http://schemas.xmlsoap.org/ws/2003/03/business-process/'))
    _HasWildcardElement = True

    _ElementMap = tActivity._ElementMap.copy()
    _ElementMap.update({
        
    })
    _AttributeMap = tActivity._AttributeMap.copy()
    _AttributeMap.update({
        
    })
Namespace.addCategoryObject('typeBinding', u'tEmpty', tEmpty)


# Complex type {http://schemas.xmlsoap.org/ws/2003/03/business-process/}tAssign with content type ELEMENT_ONLY
class tAssign (tActivity):
    _TypeDefinition = None
    _ContentTypeTag = pyxb.binding.basis.complexTypeDefinition._CT_ELEMENT_ONLY
    _Abstract = False
    _ExpandedName = pyxb.namespace.ExpandedName(Namespace, u'tAssign')
    _DefinitionLocation = pyxb.utils.utility.Location('/tmp/pyxbdist.RHB65sy/PyXB-1.1.5/pyxb/bundles/wssplat/schemas/bpws.xsd', 444, 4)
    # Base type is tActivity
    
    # Element {http://schemas.xmlsoap.org/ws/2003/03/business-process/}copy uses Python identifier copy
    __copy = pyxb.binding.content.ElementUse(pyxb.namespace.ExpandedName(Namespace, u'copy'), 'copy', '__httpschemas_xmlsoap_orgws200303business_process_tAssign_httpschemas_xmlsoap_orgws200303business_processcopy', True)
    __copy._DeclarationLocation = pyxb.utils.utility.Location('/tmp/pyxbdist.RHB65sy/PyXB-1.1.5/pyxb/bundles/wssplat/schemas/bpws.xsd', 448, 20)
    __copy._UseLocation = None

    
    copy = property(__copy.value, __copy.set, None, None)

    
    # Element source ({http://schemas.xmlsoap.org/ws/2003/03/business-process/}source) inherited from {http://schemas.xmlsoap.org/ws/2003/03/business-process/}tActivity
    
    # Element target ({http://schemas.xmlsoap.org/ws/2003/03/business-process/}target) inherited from {http://schemas.xmlsoap.org/ws/2003/03/business-process/}tActivity
    
    # Attribute name inherited from {http://schemas.xmlsoap.org/ws/2003/03/business-process/}tActivity
    
    # Attribute joinCondition inherited from {http://schemas.xmlsoap.org/ws/2003/03/business-process/}tActivity
    
    # Attribute suppressJoinFailure inherited from {http://schemas.xmlsoap.org/ws/2003/03/business-process/}tActivity
    _AttributeWildcard = pyxb.binding.content.Wildcard(process_contents=pyxb.binding.content.Wildcard.PC_lax, namespace_constraint=(pyxb.binding.content.Wildcard.NC_not, u'http://schemas.xmlsoap.org/ws/2003/03/business-process/'))
    _HasWildcardElement = True

    _ElementMap = tActivity._ElementMap.copy()
    _ElementMap.update({
        __copy.name() : __copy
    })
    _AttributeMap = tActivity._AttributeMap.copy()
    _AttributeMap.update({
        
    })
Namespace.addCategoryObject('typeBinding', u'tAssign', tAssign)


# Complex type {http://schemas.xmlsoap.org/ws/2003/03/business-process/}tWait with content type ELEMENT_ONLY
class tWait (tActivity):
    _TypeDefinition = None
    _ContentTypeTag = pyxb.binding.basis.complexTypeDefinition._CT_ELEMENT_ONLY
    _Abstract = False
    _ExpandedName = pyxb.namespace.ExpandedName(Namespace, u'tWait')
    _DefinitionLocation = pyxb.utils.utility.Location('/tmp/pyxbdist.RHB65sy/PyXB-1.1.5/pyxb/bundles/wssplat/schemas/bpws.xsd', 498, 4)
    # Base type is tActivity
    
    # Element source ({http://schemas.xmlsoap.org/ws/2003/03/business-process/}source) inherited from {http://schemas.xmlsoap.org/ws/2003/03/business-process/}tActivity
    
    # Element target ({http://schemas.xmlsoap.org/ws/2003/03/business-process/}target) inherited from {http://schemas.xmlsoap.org/ws/2003/03/business-process/}tActivity
    
    # Attribute name inherited from {http://schemas.xmlsoap.org/ws/2003/03/business-process/}tActivity
    
    # Attribute for uses Python identifier for_
    __for = pyxb.binding.content.AttributeUse(pyxb.namespace.ExpandedName(None, u'for'), 'for_', '__httpschemas_xmlsoap_orgws200303business_process_tWait_for', tDuration_expr)
    __for._DeclarationLocation = pyxb.utils.utility.Location('/tmp/pyxbdist.RHB65sy/PyXB-1.1.5/pyxb/bundles/wssplat/schemas/bpws.xsd', 501, 16)
    __for._UseLocation = pyxb.utils.utility.Location('/tmp/pyxbdist.RHB65sy/PyXB-1.1.5/pyxb/bundles/wssplat/schemas/bpws.xsd', 501, 16)
    
    for_ = property(__for.value, __for.set, None, None)

    
    # Attribute until uses Python identifier until
    __until = pyxb.binding.content.AttributeUse(pyxb.namespace.ExpandedName(None, u'until'), 'until', '__httpschemas_xmlsoap_orgws200303business_process_tWait_until', tDeadline_expr)
    __until._DeclarationLocation = pyxb.utils.utility.Location('/tmp/pyxbdist.RHB65sy/PyXB-1.1.5/pyxb/bundles/wssplat/schemas/bpws.xsd', 503, 16)
    __until._UseLocation = pyxb.utils.utility.Location('/tmp/pyxbdist.RHB65sy/PyXB-1.1.5/pyxb/bundles/wssplat/schemas/bpws.xsd', 503, 16)
    
    until = property(__until.value, __until.set, None, None)

    
    # Attribute joinCondition inherited from {http://schemas.xmlsoap.org/ws/2003/03/business-process/}tActivity
    
    # Attribute suppressJoinFailure inherited from {http://schemas.xmlsoap.org/ws/2003/03/business-process/}tActivity
    _AttributeWildcard = pyxb.binding.content.Wildcard(process_contents=pyxb.binding.content.Wildcard.PC_lax, namespace_constraint=(pyxb.binding.content.Wildcard.NC_not, u'http://schemas.xmlsoap.org/ws/2003/03/business-process/'))
    _HasWildcardElement = True

    _ElementMap = tActivity._ElementMap.copy()
    _ElementMap.update({
        
    })
    _AttributeMap = tActivity._AttributeMap.copy()
    _AttributeMap.update({
        __for.name() : __for,
        __until.name() : __until
    })
Namespace.addCategoryObject('typeBinding', u'tWait', tWait)


# Complex type {http://schemas.xmlsoap.org/ws/2003/03/business-process/}tEventHandlers with content type ELEMENT_ONLY
class tEventHandlers (tExtensibleElements):
    _TypeDefinition = None
    _ContentTypeTag = pyxb.binding.basis.complexTypeDefinition._CT_ELEMENT_ONLY
    _Abstract = False
    _ExpandedName = pyxb.namespace.ExpandedName(Namespace, u'tEventHandlers')
    _DefinitionLocation = pyxb.utils.utility.Location('/tmp/pyxbdist.RHB65sy/PyXB-1.1.5/pyxb/bundles/wssplat/schemas/bpws.xsd', 187, 4)
    # Base type is tExtensibleElements
    
    # Element {http://schemas.xmlsoap.org/ws/2003/03/business-process/}onAlarm uses Python identifier onAlarm
    __onAlarm = pyxb.binding.content.ElementUse(pyxb.namespace.ExpandedName(Namespace, u'onAlarm'), 'onAlarm', '__httpschemas_xmlsoap_orgws200303business_process_tEventHandlers_httpschemas_xmlsoap_orgws200303business_processonAlarm', True)
    __onAlarm._DeclarationLocation = pyxb.utils.utility.Location('/tmp/pyxbdist.RHB65sy/PyXB-1.1.5/pyxb/bundles/wssplat/schemas/bpws.xsd', 193, 19)
    __onAlarm._UseLocation = None

    
    onAlarm = property(__onAlarm.value, __onAlarm.set, None, None)

    
    # Element {http://schemas.xmlsoap.org/ws/2003/03/business-process/}onMessage uses Python identifier onMessage
    __onMessage = pyxb.binding.content.ElementUse(pyxb.namespace.ExpandedName(Namespace, u'onMessage'), 'onMessage', '__httpschemas_xmlsoap_orgws200303business_process_tEventHandlers_httpschemas_xmlsoap_orgws200303business_processonMessage', True)
    __onMessage._DeclarationLocation = pyxb.utils.utility.Location('/tmp/pyxbdist.RHB65sy/PyXB-1.1.5/pyxb/bundles/wssplat/schemas/bpws.xsd', 191, 19)
    __onMessage._UseLocation = None

    
    onMessage = property(__onMessage.value, __onMessage.set, None, None)

    _AttributeWildcard = pyxb.binding.content.Wildcard(process_contents=pyxb.binding.content.Wildcard.PC_lax, namespace_constraint=(pyxb.binding.content.Wildcard.NC_not, u'http://schemas.xmlsoap.org/ws/2003/03/business-process/'))
    _HasWildcardElement = True

    _ElementMap = tExtensibleElements._ElementMap.copy()
    _ElementMap.update({
        __onAlarm.name() : __onAlarm,
        __onMessage.name() : __onMessage
    })
    _AttributeMap = tExtensibleElements._AttributeMap.copy()
    _AttributeMap.update({
        
    })
Namespace.addCategoryObject('typeBinding', u'tEventHandlers', tEventHandlers)


# Complex type {http://schemas.xmlsoap.org/ws/2003/03/business-process/}tSwitch with content type ELEMENT_ONLY
class tSwitch (tActivity):
    _TypeDefinition = None
    _ContentTypeTag = pyxb.binding.basis.complexTypeDefinition._CT_ELEMENT_ONLY
    _Abstract = False
    _ExpandedName = pyxb.namespace.ExpandedName(Namespace, u'tSwitch')
    _DefinitionLocation = pyxb.utils.utility.Location('/tmp/pyxbdist.RHB65sy/PyXB-1.1.5/pyxb/bundles/wssplat/schemas/bpws.xsd', 563, 4)
    # Base type is tActivity
    
    # Element {http://schemas.xmlsoap.org/ws/2003/03/business-process/}otherwise uses Python identifier otherwise
    __otherwise = pyxb.binding.content.ElementUse(pyxb.namespace.ExpandedName(Namespace, u'otherwise'), 'otherwise', '__httpschemas_xmlsoap_orgws200303business_process_tSwitch_httpschemas_xmlsoap_orgws200303business_processotherwise', False)
    __otherwise._DeclarationLocation = pyxb.utils.utility.Location('/tmp/pyxbdist.RHB65sy/PyXB-1.1.5/pyxb/bundles/wssplat/schemas/bpws.xsd', 578, 20)
    __otherwise._UseLocation = None

    
    otherwise = property(__otherwise.value, __otherwise.set, None, None)

    
    # Element {http://schemas.xmlsoap.org/ws/2003/03/business-process/}case uses Python identifier case
    __case = pyxb.binding.content.ElementUse(pyxb.namespace.ExpandedName(Namespace, u'case'), 'case', '__httpschemas_xmlsoap_orgws200303business_process_tSwitch_httpschemas_xmlsoap_orgws200303business_processcase', True)
    __case._DeclarationLocation = pyxb.utils.utility.Location('/tmp/pyxbdist.RHB65sy/PyXB-1.1.5/pyxb/bundles/wssplat/schemas/bpws.xsd', 567, 20)
    __case._UseLocation = None

    
    case = property(__case.value, __case.set, None, None)

    
    # Element source ({http://schemas.xmlsoap.org/ws/2003/03/business-process/}source) inherited from {http://schemas.xmlsoap.org/ws/2003/03/business-process/}tActivity
    
    # Element target ({http://schemas.xmlsoap.org/ws/2003/03/business-process/}target) inherited from {http://schemas.xmlsoap.org/ws/2003/03/business-process/}tActivity
    
    # Attribute name inherited from {http://schemas.xmlsoap.org/ws/2003/03/business-process/}tActivity
    
    # Attribute joinCondition inherited from {http://schemas.xmlsoap.org/ws/2003/03/business-process/}tActivity
    
    # Attribute suppressJoinFailure inherited from {http://schemas.xmlsoap.org/ws/2003/03/business-process/}tActivity
    _AttributeWildcard = pyxb.binding.content.Wildcard(process_contents=pyxb.binding.content.Wildcard.PC_lax, namespace_constraint=(pyxb.binding.content.Wildcard.NC_not, u'http://schemas.xmlsoap.org/ws/2003/03/business-process/'))
    _HasWildcardElement = True

    _ElementMap = tActivity._ElementMap.copy()
    _ElementMap.update({
        __otherwise.name() : __otherwise,
        __case.name() : __case
    })
    _AttributeMap = tActivity._AttributeMap.copy()
    _AttributeMap.update({
        
    })
Namespace.addCategoryObject('typeBinding', u'tSwitch', tSwitch)


# Complex type {http://schemas.xmlsoap.org/ws/2003/03/business-process/}tPick with content type ELEMENT_ONLY
class tPick (tActivity):
    _TypeDefinition = None
    _ContentTypeTag = pyxb.binding.basis.complexTypeDefinition._CT_ELEMENT_ONLY
    _Abstract = False
    _ExpandedName = pyxb.namespace.ExpandedName(Namespace, u'tPick')
    _DefinitionLocation = pyxb.utils.utility.Location('/tmp/pyxbdist.RHB65sy/PyXB-1.1.5/pyxb/bundles/wssplat/schemas/bpws.xsd', 609, 4)
    # Base type is tActivity
    
    # Element {http://schemas.xmlsoap.org/ws/2003/03/business-process/}onAlarm uses Python identifier onAlarm
    __onAlarm = pyxb.binding.content.ElementUse(pyxb.namespace.ExpandedName(Namespace, u'onAlarm'), 'onAlarm', '__httpschemas_xmlsoap_orgws200303business_process_tPick_httpschemas_xmlsoap_orgws200303business_processonAlarm', True)
    __onAlarm._DeclarationLocation = pyxb.utils.utility.Location('/tmp/pyxbdist.RHB65sy/PyXB-1.1.5/pyxb/bundles/wssplat/schemas/bpws.xsd', 616, 20)
    __onAlarm._UseLocation = None

    
    onAlarm = property(__onAlarm.value, __onAlarm.set, None, None)

    
    # Element source ({http://schemas.xmlsoap.org/ws/2003/03/business-process/}source) inherited from {http://schemas.xmlsoap.org/ws/2003/03/business-process/}tActivity
    
    # Element target ({http://schemas.xmlsoap.org/ws/2003/03/business-process/}target) inherited from {http://schemas.xmlsoap.org/ws/2003/03/business-process/}tActivity
    
    # Element {http://schemas.xmlsoap.org/ws/2003/03/business-process/}onMessage uses Python identifier onMessage
    __onMessage = pyxb.binding.content.ElementUse(pyxb.namespace.ExpandedName(Namespace, u'onMessage'), 'onMessage', '__httpschemas_xmlsoap_orgws200303business_process_tPick_httpschemas_xmlsoap_orgws200303business_processonMessage', True)
    __onMessage._DeclarationLocation = pyxb.utils.utility.Location('/tmp/pyxbdist.RHB65sy/PyXB-1.1.5/pyxb/bundles/wssplat/schemas/bpws.xsd', 613, 20)
    __onMessage._UseLocation = None

    
    onMessage = property(__onMessage.value, __onMessage.set, None, None)

    
    # Attribute name inherited from {http://schemas.xmlsoap.org/ws/2003/03/business-process/}tActivity
    
    # Attribute createInstance uses Python identifier createInstance
    __createInstance = pyxb.binding.content.AttributeUse(pyxb.namespace.ExpandedName(None, u'createInstance'), 'createInstance', '__httpschemas_xmlsoap_orgws200303business_process_tPick_createInstance', tBoolean, unicode_default=u'no')
    __createInstance._DeclarationLocation = pyxb.utils.utility.Location('/tmp/pyxbdist.RHB65sy/PyXB-1.1.5/pyxb/bundles/wssplat/schemas/bpws.xsd', 620, 16)
    __createInstance._UseLocation = pyxb.utils.utility.Location('/tmp/pyxbdist.RHB65sy/PyXB-1.1.5/pyxb/bundles/wssplat/schemas/bpws.xsd', 620, 16)
    
    createInstance = property(__createInstance.value, __createInstance.set, None, None)

    
    # Attribute joinCondition inherited from {http://schemas.xmlsoap.org/ws/2003/03/business-process/}tActivity
    
    # Attribute suppressJoinFailure inherited from {http://schemas.xmlsoap.org/ws/2003/03/business-process/}tActivity
    _AttributeWildcard = pyxb.binding.content.Wildcard(process_contents=pyxb.binding.content.Wildcard.PC_lax, namespace_constraint=(pyxb.binding.content.Wildcard.NC_not, u'http://schemas.xmlsoap.org/ws/2003/03/business-process/'))
    _HasWildcardElement = True

    _ElementMap = tActivity._ElementMap.copy()
    _ElementMap.update({
        __onAlarm.name() : __onAlarm,
        __onMessage.name() : __onMessage
    })
    _AttributeMap = tActivity._AttributeMap.copy()
    _AttributeMap.update({
        __createInstance.name() : __createInstance
    })
Namespace.addCategoryObject('typeBinding', u'tPick', tPick)


# Complex type [anonymous] with content type ELEMENT_ONLY
class CTD_ANON_ (tExtensibleElements):
    _TypeDefinition = None
    _ContentTypeTag = pyxb.binding.basis.complexTypeDefinition._CT_ELEMENT_ONLY
    _Abstract = False
    _ExpandedName = None
    _DefinitionLocation = pyxb.utils.utility.Location('/tmp/pyxbdist.RHB65sy/PyXB-1.1.5/pyxb/bundles/wssplat/schemas/bpws.xsd', 128, 21)
    # Base type is tExtensibleElements
    
    # Attribute name uses Python identifier name
    __name = pyxb.binding.content.AttributeUse(pyxb.namespace.ExpandedName(None, u'name'), 'name', '__httpschemas_xmlsoap_orgws200303business_process_CTD_ANON__name', pyxb.binding.datatypes.NCName, required=True)
    __name._DeclarationLocation = pyxb.utils.utility.Location('/tmp/pyxbdist.RHB65sy/PyXB-1.1.5/pyxb/bundles/wssplat/schemas/bpws.xsd', 131, 31)
    __name._UseLocation = pyxb.utils.utility.Location('/tmp/pyxbdist.RHB65sy/PyXB-1.1.5/pyxb/bundles/wssplat/schemas/bpws.xsd', 131, 31)
    
    name = property(__name.value, __name.set, None, None)

    _AttributeWildcard = pyxb.binding.content.Wildcard(process_contents=pyxb.binding.content.Wildcard.PC_lax, namespace_constraint=(pyxb.binding.content.Wildcard.NC_not, u'http://schemas.xmlsoap.org/ws/2003/03/business-process/'))
    _HasWildcardElement = True

    _ElementMap = tExtensibleElements._ElementMap.copy()
    _ElementMap.update({
        
    })
    _AttributeMap = tExtensibleElements._AttributeMap.copy()
    _AttributeMap.update({
        __name.name() : __name
    })



# Complex type {http://schemas.xmlsoap.org/ws/2003/03/business-process/}tSequence with content type ELEMENT_ONLY
class tSequence (tActivity):
    _TypeDefinition = None
    _ContentTypeTag = pyxb.binding.basis.complexTypeDefinition._CT_ELEMENT_ONLY
    _Abstract = False
    _ExpandedName = pyxb.namespace.ExpandedName(Namespace, u'tSequence')
    _DefinitionLocation = pyxb.utils.utility.Location('/tmp/pyxbdist.RHB65sy/PyXB-1.1.5/pyxb/bundles/wssplat/schemas/bpws.xsd', 599, 4)
    # Base type is tActivity
    
    # Element {http://schemas.xmlsoap.org/ws/2003/03/business-process/}switch uses Python identifier switch
    __switch = pyxb.binding.content.ElementUse(pyxb.namespace.ExpandedName(Namespace, u'switch'), 'switch', '__httpschemas_xmlsoap_orgws200303business_process_tSequence_httpschemas_xmlsoap_orgws200303business_processswitch', True)
    __switch._DeclarationLocation = pyxb.utils.utility.Location('/tmp/pyxbdist.RHB65sy/PyXB-1.1.5/pyxb/bundles/wssplat/schemas/bpws.xsd', 78, 12)
    __switch._UseLocation = None

    
    switch = property(__switch.value, __switch.set, None, None)

    
    # Element {http://schemas.xmlsoap.org/ws/2003/03/business-process/}reply uses Python identifier reply
    __reply = pyxb.binding.content.ElementUse(pyxb.namespace.ExpandedName(Namespace, u'reply'), 'reply', '__httpschemas_xmlsoap_orgws200303business_process_tSequence_httpschemas_xmlsoap_orgws200303business_processreply', True)
    __reply._DeclarationLocation = pyxb.utils.utility.Location('/tmp/pyxbdist.RHB65sy/PyXB-1.1.5/pyxb/bundles/wssplat/schemas/bpws.xsd', 72, 12)
    __reply._UseLocation = None

    
    reply = property(__reply.value, __reply.set, None, None)

    
    # Element {http://schemas.xmlsoap.org/ws/2003/03/business-process/}pick uses Python identifier pick
    __pick = pyxb.binding.content.ElementUse(pyxb.namespace.ExpandedName(Namespace, u'pick'), 'pick', '__httpschemas_xmlsoap_orgws200303business_process_tSequence_httpschemas_xmlsoap_orgws200303business_processpick', True)
    __pick._DeclarationLocation = pyxb.utils.utility.Location('/tmp/pyxbdist.RHB65sy/PyXB-1.1.5/pyxb/bundles/wssplat/schemas/bpws.xsd', 81, 12)
    __pick._UseLocation = None

    
    pick = property(__pick.value, __pick.set, None, None)

    
    # Element {http://schemas.xmlsoap.org/ws/2003/03/business-process/}wait uses Python identifier wait
    __wait = pyxb.binding.content.ElementUse(pyxb.namespace.ExpandedName(Namespace, u'wait'), 'wait', '__httpschemas_xmlsoap_orgws200303business_process_tSequence_httpschemas_xmlsoap_orgws200303business_processwait', True)
    __wait._DeclarationLocation = pyxb.utils.utility.Location('/tmp/pyxbdist.RHB65sy/PyXB-1.1.5/pyxb/bundles/wssplat/schemas/bpws.xsd', 74, 12)
    __wait._UseLocation = None

    
    wait = property(__wait.value, __wait.set, None, None)

    
    # Element {http://schemas.xmlsoap.org/ws/2003/03/business-process/}terminate uses Python identifier terminate
    __terminate = pyxb.binding.content.ElementUse(pyxb.namespace.ExpandedName(Namespace, u'terminate'), 'terminate', '__httpschemas_xmlsoap_orgws200303business_process_tSequence_httpschemas_xmlsoap_orgws200303business_processterminate', True)
    __terminate._DeclarationLocation = pyxb.utils.utility.Location('/tmp/pyxbdist.RHB65sy/PyXB-1.1.5/pyxb/bundles/wssplat/schemas/bpws.xsd', 76, 12)
    __terminate._UseLocation = None

    
    terminate = property(__terminate.value, __terminate.set, None, None)

    
    # Element {http://schemas.xmlsoap.org/ws/2003/03/business-process/}empty uses Python identifier empty
    __empty = pyxb.binding.content.ElementUse(pyxb.namespace.ExpandedName(Namespace, u'empty'), 'empty', '__httpschemas_xmlsoap_orgws200303business_process_tSequence_httpschemas_xmlsoap_orgws200303business_processempty', True)
    __empty._DeclarationLocation = pyxb.utils.utility.Location('/tmp/pyxbdist.RHB65sy/PyXB-1.1.5/pyxb/bundles/wssplat/schemas/bpws.xsd', 69, 12)
    __empty._UseLocation = None

    
    empty = property(__empty.value, __empty.set, None, None)

    
    # Element source ({http://schemas.xmlsoap.org/ws/2003/03/business-process/}source) inherited from {http://schemas.xmlsoap.org/ws/2003/03/business-process/}tActivity
    
    # Element {http://schemas.xmlsoap.org/ws/2003/03/business-process/}while uses Python identifier while_
    __while = pyxb.binding.content.ElementUse(pyxb.namespace.ExpandedName(Namespace, u'while'), 'while_', '__httpschemas_xmlsoap_orgws200303business_process_tSequence_httpschemas_xmlsoap_orgws200303business_processwhile', True)
    __while._DeclarationLocation = pyxb.utils.utility.Location('/tmp/pyxbdist.RHB65sy/PyXB-1.1.5/pyxb/bundles/wssplat/schemas/bpws.xsd', 79, 12)
    __while._UseLocation = None

    
    while_ = property(__while.value, __while.set, None, None)

    
    # Element {http://schemas.xmlsoap.org/ws/2003/03/business-process/}throw uses Python identifier throw
    __throw = pyxb.binding.content.ElementUse(pyxb.namespace.ExpandedName(Namespace, u'throw'), 'throw', '__httpschemas_xmlsoap_orgws200303business_process_tSequence_httpschemas_xmlsoap_orgws200303business_processthrow', True)
    __throw._DeclarationLocation = pyxb.utils.utility.Location('/tmp/pyxbdist.RHB65sy/PyXB-1.1.5/pyxb/bundles/wssplat/schemas/bpws.xsd', 75, 12)
    __throw._UseLocation = None

    
    throw = property(__throw.value, __throw.set, None, None)

    
    # Element {http://schemas.xmlsoap.org/ws/2003/03/business-process/}scope uses Python identifier scope
    __scope = pyxb.binding.content.ElementUse(pyxb.namespace.ExpandedName(Namespace, u'scope'), 'scope', '__httpschemas_xmlsoap_orgws200303business_process_tSequence_httpschemas_xmlsoap_orgws200303business_processscope', True)
    __scope._DeclarationLocation = pyxb.utils.utility.Location('/tmp/pyxbdist.RHB65sy/PyXB-1.1.5/pyxb/bundles/wssplat/schemas/bpws.xsd', 82, 12)
    __scope._UseLocation = None

    
    scope = property(__scope.value, __scope.set, None, None)

    
    # Element {http://schemas.xmlsoap.org/ws/2003/03/business-process/}flow uses Python identifier flow
    __flow = pyxb.binding.content.ElementUse(pyxb.namespace.ExpandedName(Namespace, u'flow'), 'flow', '__httpschemas_xmlsoap_orgws200303business_process_tSequence_httpschemas_xmlsoap_orgws200303business_processflow', True)
    __flow._DeclarationLocation = pyxb.utils.utility.Location('/tmp/pyxbdist.RHB65sy/PyXB-1.1.5/pyxb/bundles/wssplat/schemas/bpws.xsd', 77, 12)
    __flow._UseLocation = None

    
    flow = property(__flow.value, __flow.set, None, None)

    
    # Element {http://schemas.xmlsoap.org/ws/2003/03/business-process/}receive uses Python identifier receive
    __receive = pyxb.binding.content.ElementUse(pyxb.namespace.ExpandedName(Namespace, u'receive'), 'receive', '__httpschemas_xmlsoap_orgws200303business_process_tSequence_httpschemas_xmlsoap_orgws200303business_processreceive', True)
    __receive._DeclarationLocation = pyxb.utils.utility.Location('/tmp/pyxbdist.RHB65sy/PyXB-1.1.5/pyxb/bundles/wssplat/schemas/bpws.xsd', 71, 12)
    __receive._UseLocation = None

    
    receive = property(__receive.value, __receive.set, None, None)

    
    # Element {http://schemas.xmlsoap.org/ws/2003/03/business-process/}sequence uses Python identifier sequence
    __sequence = pyxb.binding.content.ElementUse(pyxb.namespace.ExpandedName(Namespace, u'sequence'), 'sequence', '__httpschemas_xmlsoap_orgws200303business_process_tSequence_httpschemas_xmlsoap_orgws200303business_processsequence', True)
    __sequence._DeclarationLocation = pyxb.utils.utility.Location('/tmp/pyxbdist.RHB65sy/PyXB-1.1.5/pyxb/bundles/wssplat/schemas/bpws.xsd', 80, 12)
    __sequence._UseLocation = None

    
    sequence = property(__sequence.value, __sequence.set, None, None)

    
    # Element target ({http://schemas.xmlsoap.org/ws/2003/03/business-process/}target) inherited from {http://schemas.xmlsoap.org/ws/2003/03/business-process/}tActivity
    
    # Element {http://schemas.xmlsoap.org/ws/2003/03/business-process/}invoke uses Python identifier invoke
    __invoke = pyxb.binding.content.ElementUse(pyxb.namespace.ExpandedName(Namespace, u'invoke'), 'invoke', '__httpschemas_xmlsoap_orgws200303business_process_tSequence_httpschemas_xmlsoap_orgws200303business_processinvoke', True)
    __invoke._DeclarationLocation = pyxb.utils.utility.Location('/tmp/pyxbdist.RHB65sy/PyXB-1.1.5/pyxb/bundles/wssplat/schemas/bpws.xsd', 70, 12)
    __invoke._UseLocation = None

    
    invoke = property(__invoke.value, __invoke.set, None, None)

    
    # Element {http://schemas.xmlsoap.org/ws/2003/03/business-process/}assign uses Python identifier assign
    __assign = pyxb.binding.content.ElementUse(pyxb.namespace.ExpandedName(Namespace, u'assign'), 'assign', '__httpschemas_xmlsoap_orgws200303business_process_tSequence_httpschemas_xmlsoap_orgws200303business_processassign', True)
    __assign._DeclarationLocation = pyxb.utils.utility.Location('/tmp/pyxbdist.RHB65sy/PyXB-1.1.5/pyxb/bundles/wssplat/schemas/bpws.xsd', 73, 12)
    __assign._UseLocation = None

    
    assign = property(__assign.value, __assign.set, None, None)

    
    # Attribute name inherited from {http://schemas.xmlsoap.org/ws/2003/03/business-process/}tActivity
    
    # Attribute joinCondition inherited from {http://schemas.xmlsoap.org/ws/2003/03/business-process/}tActivity
    
    # Attribute suppressJoinFailure inherited from {http://schemas.xmlsoap.org/ws/2003/03/business-process/}tActivity
    _AttributeWildcard = pyxb.binding.content.Wildcard(process_contents=pyxb.binding.content.Wildcard.PC_lax, namespace_constraint=(pyxb.binding.content.Wildcard.NC_not, u'http://schemas.xmlsoap.org/ws/2003/03/business-process/'))
    _HasWildcardElement = True

    _ElementMap = tActivity._ElementMap.copy()
    _ElementMap.update({
        __switch.name() : __switch,
        __reply.name() : __reply,
        __pick.name() : __pick,
        __wait.name() : __wait,
        __terminate.name() : __terminate,
        __empty.name() : __empty,
        __while.name() : __while,
        __throw.name() : __throw,
        __scope.name() : __scope,
        __flow.name() : __flow,
        __receive.name() : __receive,
        __sequence.name() : __sequence,
        __invoke.name() : __invoke,
        __assign.name() : __assign
    })
    _AttributeMap = tActivity._AttributeMap.copy()
    _AttributeMap.update({
        
    })
Namespace.addCategoryObject('typeBinding', u'tSequence', tSequence)


# Complex type {http://schemas.xmlsoap.org/ws/2003/03/business-process/}tCorrelationsWithPattern with content type ELEMENT_ONLY
class tCorrelationsWithPattern (tExtensibleElements):
    _TypeDefinition = None
    _ContentTypeTag = pyxb.binding.basis.complexTypeDefinition._CT_ELEMENT_ONLY
    _Abstract = False
    _ExpandedName = pyxb.namespace.ExpandedName(Namespace, u'tCorrelationsWithPattern')
    _DefinitionLocation = pyxb.utils.utility.Location('/tmp/pyxbdist.RHB65sy/PyXB-1.1.5/pyxb/bundles/wssplat/schemas/bpws.xsd', 353, 4)
    # Base type is tExtensibleElements
    
    # Element {http://schemas.xmlsoap.org/ws/2003/03/business-process/}correlation uses Python identifier correlation
    __correlation = pyxb.binding.content.ElementUse(pyxb.namespace.ExpandedName(Namespace, u'correlation'), 'correlation', '__httpschemas_xmlsoap_orgws200303business_process_tCorrelationsWithPattern_httpschemas_xmlsoap_orgws200303business_processcorrelation', True)
    __correlation._DeclarationLocation = pyxb.utils.utility.Location('/tmp/pyxbdist.RHB65sy/PyXB-1.1.5/pyxb/bundles/wssplat/schemas/bpws.xsd', 357, 20)
    __correlation._UseLocation = None

    
    correlation = property(__correlation.value, __correlation.set, None, None)

    _AttributeWildcard = pyxb.binding.content.Wildcard(process_contents=pyxb.binding.content.Wildcard.PC_lax, namespace_constraint=(pyxb.binding.content.Wildcard.NC_not, u'http://schemas.xmlsoap.org/ws/2003/03/business-process/'))
    _HasWildcardElement = True

    _ElementMap = tExtensibleElements._ElementMap.copy()
    _ElementMap.update({
        __correlation.name() : __correlation
    })
    _AttributeMap = tExtensibleElements._AttributeMap.copy()
    _AttributeMap.update({
        
    })
Namespace.addCategoryObject('typeBinding', u'tCorrelationsWithPattern', tCorrelationsWithPattern)


# Complex type {http://schemas.xmlsoap.org/ws/2003/03/business-process/}tVariables with content type ELEMENT_ONLY
class tVariables (tExtensibleElements):
    _TypeDefinition = None
    _ContentTypeTag = pyxb.binding.basis.complexTypeDefinition._CT_ELEMENT_ONLY
    _Abstract = False
    _ExpandedName = pyxb.namespace.ExpandedName(Namespace, u'tVariables')
    _DefinitionLocation = pyxb.utils.utility.Location('/tmp/pyxbdist.RHB65sy/PyXB-1.1.5/pyxb/bundles/wssplat/schemas/bpws.xsd', 234, 4)
    # Base type is tExtensibleElements
    
    # Element {http://schemas.xmlsoap.org/ws/2003/03/business-process/}variable uses Python identifier variable
    __variable = pyxb.binding.content.ElementUse(pyxb.namespace.ExpandedName(Namespace, u'variable'), 'variable', '__httpschemas_xmlsoap_orgws200303business_process_tVariables_httpschemas_xmlsoap_orgws200303business_processvariable', True)
    __variable._DeclarationLocation = pyxb.utils.utility.Location('/tmp/pyxbdist.RHB65sy/PyXB-1.1.5/pyxb/bundles/wssplat/schemas/bpws.xsd', 238, 20)
    __variable._UseLocation = None

    
    variable = property(__variable.value, __variable.set, None, None)

    _AttributeWildcard = pyxb.binding.content.Wildcard(process_contents=pyxb.binding.content.Wildcard.PC_lax, namespace_constraint=(pyxb.binding.content.Wildcard.NC_not, u'http://schemas.xmlsoap.org/ws/2003/03/business-process/'))
    _HasWildcardElement = True

    _ElementMap = tExtensibleElements._ElementMap.copy()
    _ElementMap.update({
        __variable.name() : __variable
    })
    _AttributeMap = tExtensibleElements._AttributeMap.copy()
    _AttributeMap.update({
        
    })
Namespace.addCategoryObject('typeBinding', u'tVariables', tVariables)


# Complex type {http://schemas.xmlsoap.org/ws/2003/03/business-process/}tCorrelationSets with content type ELEMENT_ONLY
class tCorrelationSets (tExtensibleElements):
    _TypeDefinition = None
    _ContentTypeTag = pyxb.binding.basis.complexTypeDefinition._CT_ELEMENT_ONLY
    _Abstract = False
    _ExpandedName = pyxb.namespace.ExpandedName(Namespace, u'tCorrelationSets')
    _DefinitionLocation = pyxb.utils.utility.Location('/tmp/pyxbdist.RHB65sy/PyXB-1.1.5/pyxb/bundles/wssplat/schemas/bpws.xsd', 259, 4)
    # Base type is tExtensibleElements
    
    # Element {http://schemas.xmlsoap.org/ws/2003/03/business-process/}correlationSet uses Python identifier correlationSet
    __correlationSet = pyxb.binding.content.ElementUse(pyxb.namespace.ExpandedName(Namespace, u'correlationSet'), 'correlationSet', '__httpschemas_xmlsoap_orgws200303business_process_tCorrelationSets_httpschemas_xmlsoap_orgws200303business_processcorrelationSet', True)
    __correlationSet._DeclarationLocation = pyxb.utils.utility.Location('/tmp/pyxbdist.RHB65sy/PyXB-1.1.5/pyxb/bundles/wssplat/schemas/bpws.xsd', 263, 20)
    __correlationSet._UseLocation = None

    
    correlationSet = property(__correlationSet.value, __correlationSet.set, None, None)

    _AttributeWildcard = pyxb.binding.content.Wildcard(process_contents=pyxb.binding.content.Wildcard.PC_lax, namespace_constraint=(pyxb.binding.content.Wildcard.NC_not, u'http://schemas.xmlsoap.org/ws/2003/03/business-process/'))
    _HasWildcardElement = True

    _ElementMap = tExtensibleElements._ElementMap.copy()
    _ElementMap.update({
        __correlationSet.name() : __correlationSet
    })
    _AttributeMap = tExtensibleElements._AttributeMap.copy()
    _AttributeMap.update({
        
    })
Namespace.addCategoryObject('typeBinding', u'tCorrelationSets', tCorrelationSets)


# Complex type {http://schemas.xmlsoap.org/ws/2003/03/business-process/}tFaultHandlers with content type ELEMENT_ONLY
class tFaultHandlers (tExtensibleElements):
    _TypeDefinition = None
    _ContentTypeTag = pyxb.binding.basis.complexTypeDefinition._CT_ELEMENT_ONLY
    _Abstract = False
    _ExpandedName = pyxb.namespace.ExpandedName(Namespace, u'tFaultHandlers')
    _DefinitionLocation = pyxb.utils.utility.Location('/tmp/pyxbdist.RHB65sy/PyXB-1.1.5/pyxb/bundles/wssplat/schemas/bpws.xsd', 143, 4)
    # Base type is tExtensibleElements
    
    # Element {http://schemas.xmlsoap.org/ws/2003/03/business-process/}catchAll uses Python identifier catchAll
    __catchAll = pyxb.binding.content.ElementUse(pyxb.namespace.ExpandedName(Namespace, u'catchAll'), 'catchAll', '__httpschemas_xmlsoap_orgws200303business_process_tFaultHandlers_httpschemas_xmlsoap_orgws200303business_processcatchAll', False)
    __catchAll._DeclarationLocation = pyxb.utils.utility.Location('/tmp/pyxbdist.RHB65sy/PyXB-1.1.5/pyxb/bundles/wssplat/schemas/bpws.xsd', 150, 20)
    __catchAll._UseLocation = None

    
    catchAll = property(__catchAll.value, __catchAll.set, None, None)

    
    # Element {http://schemas.xmlsoap.org/ws/2003/03/business-process/}catch uses Python identifier catch
    __catch = pyxb.binding.content.ElementUse(pyxb.namespace.ExpandedName(Namespace, u'catch'), 'catch', '__httpschemas_xmlsoap_orgws200303business_process_tFaultHandlers_httpschemas_xmlsoap_orgws200303business_processcatch', True)
    __catch._DeclarationLocation = pyxb.utils.utility.Location('/tmp/pyxbdist.RHB65sy/PyXB-1.1.5/pyxb/bundles/wssplat/schemas/bpws.xsd', 148, 20)
    __catch._UseLocation = None

    
    catch = property(__catch.value, __catch.set, None, None)

    _AttributeWildcard = pyxb.binding.content.Wildcard(process_contents=pyxb.binding.content.Wildcard.PC_lax, namespace_constraint=(pyxb.binding.content.Wildcard.NC_not, u'http://schemas.xmlsoap.org/ws/2003/03/business-process/'))
    _HasWildcardElement = True

    _ElementMap = tExtensibleElements._ElementMap.copy()
    _ElementMap.update({
        __catchAll.name() : __catchAll,
        __catch.name() : __catch
    })
    _AttributeMap = tExtensibleElements._AttributeMap.copy()
    _AttributeMap.update({
        
    })
Namespace.addCategoryObject('typeBinding', u'tFaultHandlers', tFaultHandlers)


# Complex type {http://schemas.xmlsoap.org/ws/2003/03/business-process/}tOnMessage with content type ELEMENT_ONLY
class tOnMessage (tExtensibleElements):
    _TypeDefinition = None
    _ContentTypeTag = pyxb.binding.basis.complexTypeDefinition._CT_ELEMENT_ONLY
    _Abstract = False
    _ExpandedName = pyxb.namespace.ExpandedName(Namespace, u'tOnMessage')
    _DefinitionLocation = pyxb.utils.utility.Location('/tmp/pyxbdist.RHB65sy/PyXB-1.1.5/pyxb/bundles/wssplat/schemas/bpws.xsd', 201, 4)
    # Base type is tExtensibleElements
    
    # Element {http://schemas.xmlsoap.org/ws/2003/03/business-process/}invoke uses Python identifier invoke
    __invoke = pyxb.binding.content.ElementUse(pyxb.namespace.ExpandedName(Namespace, u'invoke'), 'invoke', '__httpschemas_xmlsoap_orgws200303business_process_tOnMessage_httpschemas_xmlsoap_orgws200303business_processinvoke', False)
    __invoke._DeclarationLocation = pyxb.utils.utility.Location('/tmp/pyxbdist.RHB65sy/PyXB-1.1.5/pyxb/bundles/wssplat/schemas/bpws.xsd', 70, 12)
    __invoke._UseLocation = None

    
    invoke = property(__invoke.value, __invoke.set, None, None)

    
    # Element {http://schemas.xmlsoap.org/ws/2003/03/business-process/}scope uses Python identifier scope
    __scope = pyxb.binding.content.ElementUse(pyxb.namespace.ExpandedName(Namespace, u'scope'), 'scope', '__httpschemas_xmlsoap_orgws200303business_process_tOnMessage_httpschemas_xmlsoap_orgws200303business_processscope', False)
    __scope._DeclarationLocation = pyxb.utils.utility.Location('/tmp/pyxbdist.RHB65sy/PyXB-1.1.5/pyxb/bundles/wssplat/schemas/bpws.xsd', 82, 12)
    __scope._UseLocation = None

    
    scope = property(__scope.value, __scope.set, None, None)

    
    # Element {http://schemas.xmlsoap.org/ws/2003/03/business-process/}assign uses Python identifier assign
    __assign = pyxb.binding.content.ElementUse(pyxb.namespace.ExpandedName(Namespace, u'assign'), 'assign', '__httpschemas_xmlsoap_orgws200303business_process_tOnMessage_httpschemas_xmlsoap_orgws200303business_processassign', False)
    __assign._DeclarationLocation = pyxb.utils.utility.Location('/tmp/pyxbdist.RHB65sy/PyXB-1.1.5/pyxb/bundles/wssplat/schemas/bpws.xsd', 73, 12)
    __assign._UseLocation = None

    
    assign = property(__assign.value, __assign.set, None, None)

    
    # Element {http://schemas.xmlsoap.org/ws/2003/03/business-process/}switch uses Python identifier switch
    __switch = pyxb.binding.content.ElementUse(pyxb.namespace.ExpandedName(Namespace, u'switch'), 'switch', '__httpschemas_xmlsoap_orgws200303business_process_tOnMessage_httpschemas_xmlsoap_orgws200303business_processswitch', False)
    __switch._DeclarationLocation = pyxb.utils.utility.Location('/tmp/pyxbdist.RHB65sy/PyXB-1.1.5/pyxb/bundles/wssplat/schemas/bpws.xsd', 78, 12)
    __switch._UseLocation = None

    
    switch = property(__switch.value, __switch.set, None, None)

    
    # Element {http://schemas.xmlsoap.org/ws/2003/03/business-process/}sequence uses Python identifier sequence
    __sequence = pyxb.binding.content.ElementUse(pyxb.namespace.ExpandedName(Namespace, u'sequence'), 'sequence', '__httpschemas_xmlsoap_orgws200303business_process_tOnMessage_httpschemas_xmlsoap_orgws200303business_processsequence', False)
    __sequence._DeclarationLocation = pyxb.utils.utility.Location('/tmp/pyxbdist.RHB65sy/PyXB-1.1.5/pyxb/bundles/wssplat/schemas/bpws.xsd', 80, 12)
    __sequence._UseLocation = None

    
    sequence = property(__sequence.value, __sequence.set, None, None)

    
    # Element {http://schemas.xmlsoap.org/ws/2003/03/business-process/}correlations uses Python identifier correlations
    __correlations = pyxb.binding.content.ElementUse(pyxb.namespace.ExpandedName(Namespace, u'correlations'), 'correlations', '__httpschemas_xmlsoap_orgws200303business_process_tOnMessage_httpschemas_xmlsoap_orgws200303business_processcorrelations', False)
    __correlations._DeclarationLocation = pyxb.utils.utility.Location('/tmp/pyxbdist.RHB65sy/PyXB-1.1.5/pyxb/bundles/wssplat/schemas/bpws.xsd', 205, 20)
    __correlations._UseLocation = None

    
    correlations = property(__correlations.value, __correlations.set, None, None)

    
    # Element {http://schemas.xmlsoap.org/ws/2003/03/business-process/}receive uses Python identifier receive
    __receive = pyxb.binding.content.ElementUse(pyxb.namespace.ExpandedName(Namespace, u'receive'), 'receive', '__httpschemas_xmlsoap_orgws200303business_process_tOnMessage_httpschemas_xmlsoap_orgws200303business_processreceive', False)
    __receive._DeclarationLocation = pyxb.utils.utility.Location('/tmp/pyxbdist.RHB65sy/PyXB-1.1.5/pyxb/bundles/wssplat/schemas/bpws.xsd', 71, 12)
    __receive._UseLocation = None

    
    receive = property(__receive.value, __receive.set, None, None)

    
    # Element {http://schemas.xmlsoap.org/ws/2003/03/business-process/}while uses Python identifier while_
    __while = pyxb.binding.content.ElementUse(pyxb.namespace.ExpandedName(Namespace, u'while'), 'while_', '__httpschemas_xmlsoap_orgws200303business_process_tOnMessage_httpschemas_xmlsoap_orgws200303business_processwhile', False)
    __while._DeclarationLocation = pyxb.utils.utility.Location('/tmp/pyxbdist.RHB65sy/PyXB-1.1.5/pyxb/bundles/wssplat/schemas/bpws.xsd', 79, 12)
    __while._UseLocation = None

    
    while_ = property(__while.value, __while.set, None, None)

    
    # Element {http://schemas.xmlsoap.org/ws/2003/03/business-process/}wait uses Python identifier wait
    __wait = pyxb.binding.content.ElementUse(pyxb.namespace.ExpandedName(Namespace, u'wait'), 'wait', '__httpschemas_xmlsoap_orgws200303business_process_tOnMessage_httpschemas_xmlsoap_orgws200303business_processwait', False)
    __wait._DeclarationLocation = pyxb.utils.utility.Location('/tmp/pyxbdist.RHB65sy/PyXB-1.1.5/pyxb/bundles/wssplat/schemas/bpws.xsd', 74, 12)
    __wait._UseLocation = None

    
    wait = property(__wait.value, __wait.set, None, None)

    
    # Element {http://schemas.xmlsoap.org/ws/2003/03/business-process/}empty uses Python identifier empty
    __empty = pyxb.binding.content.ElementUse(pyxb.namespace.ExpandedName(Namespace, u'empty'), 'empty', '__httpschemas_xmlsoap_orgws200303business_process_tOnMessage_httpschemas_xmlsoap_orgws200303business_processempty', False)
    __empty._DeclarationLocation = pyxb.utils.utility.Location('/tmp/pyxbdist.RHB65sy/PyXB-1.1.5/pyxb/bundles/wssplat/schemas/bpws.xsd', 69, 12)
    __empty._UseLocation = None

    
    empty = property(__empty.value, __empty.set, None, None)

    
    # Element {http://schemas.xmlsoap.org/ws/2003/03/business-process/}terminate uses Python identifier terminate
    __terminate = pyxb.binding.content.ElementUse(pyxb.namespace.ExpandedName(Namespace, u'terminate'), 'terminate', '__httpschemas_xmlsoap_orgws200303business_process_tOnMessage_httpschemas_xmlsoap_orgws200303business_processterminate', False)
    __terminate._DeclarationLocation = pyxb.utils.utility.Location('/tmp/pyxbdist.RHB65sy/PyXB-1.1.5/pyxb/bundles/wssplat/schemas/bpws.xsd', 76, 12)
    __terminate._UseLocation = None

    
    terminate = property(__terminate.value, __terminate.set, None, None)

    
    # Element {http://schemas.xmlsoap.org/ws/2003/03/business-process/}reply uses Python identifier reply
    __reply = pyxb.binding.content.ElementUse(pyxb.namespace.ExpandedName(Namespace, u'reply'), 'reply', '__httpschemas_xmlsoap_orgws200303business_process_tOnMessage_httpschemas_xmlsoap_orgws200303business_processreply', False)
    __reply._DeclarationLocation = pyxb.utils.utility.Location('/tmp/pyxbdist.RHB65sy/PyXB-1.1.5/pyxb/bundles/wssplat/schemas/bpws.xsd', 72, 12)
    __reply._UseLocation = None

    
    reply = property(__reply.value, __reply.set, None, None)

    
    # Element {http://schemas.xmlsoap.org/ws/2003/03/business-process/}pick uses Python identifier pick
    __pick = pyxb.binding.content.ElementUse(pyxb.namespace.ExpandedName(Namespace, u'pick'), 'pick', '__httpschemas_xmlsoap_orgws200303business_process_tOnMessage_httpschemas_xmlsoap_orgws200303business_processpick', False)
    __pick._DeclarationLocation = pyxb.utils.utility.Location('/tmp/pyxbdist.RHB65sy/PyXB-1.1.5/pyxb/bundles/wssplat/schemas/bpws.xsd', 81, 12)
    __pick._UseLocation = None

    
    pick = property(__pick.value, __pick.set, None, None)

    
    # Element {http://schemas.xmlsoap.org/ws/2003/03/business-process/}throw uses Python identifier throw
    __throw = pyxb.binding.content.ElementUse(pyxb.namespace.ExpandedName(Namespace, u'throw'), 'throw', '__httpschemas_xmlsoap_orgws200303business_process_tOnMessage_httpschemas_xmlsoap_orgws200303business_processthrow', False)
    __throw._DeclarationLocation = pyxb.utils.utility.Location('/tmp/pyxbdist.RHB65sy/PyXB-1.1.5/pyxb/bundles/wssplat/schemas/bpws.xsd', 75, 12)
    __throw._UseLocation = None

    
    throw = property(__throw.value, __throw.set, None, None)

    
    # Element {http://schemas.xmlsoap.org/ws/2003/03/business-process/}flow uses Python identifier flow
    __flow = pyxb.binding.content.ElementUse(pyxb.namespace.ExpandedName(Namespace, u'flow'), 'flow', '__httpschemas_xmlsoap_orgws200303business_process_tOnMessage_httpschemas_xmlsoap_orgws200303business_processflow', False)
    __flow._DeclarationLocation = pyxb.utils.utility.Location('/tmp/pyxbdist.RHB65sy/PyXB-1.1.5/pyxb/bundles/wssplat/schemas/bpws.xsd', 77, 12)
    __flow._UseLocation = None

    
    flow = property(__flow.value, __flow.set, None, None)

    
    # Attribute partnerLink uses Python identifier partnerLink
    __partnerLink = pyxb.binding.content.AttributeUse(pyxb.namespace.ExpandedName(None, u'partnerLink'), 'partnerLink', '__httpschemas_xmlsoap_orgws200303business_process_tOnMessage_partnerLink', pyxb.binding.datatypes.NCName, required=True)
    __partnerLink._DeclarationLocation = pyxb.utils.utility.Location('/tmp/pyxbdist.RHB65sy/PyXB-1.1.5/pyxb/bundles/wssplat/schemas/bpws.xsd', 209, 16)
    __partnerLink._UseLocation = pyxb.utils.utility.Location('/tmp/pyxbdist.RHB65sy/PyXB-1.1.5/pyxb/bundles/wssplat/schemas/bpws.xsd', 209, 16)
    
    partnerLink = property(__partnerLink.value, __partnerLink.set, None, None)

    
    # Attribute operation uses Python identifier operation
    __operation = pyxb.binding.content.AttributeUse(pyxb.namespace.ExpandedName(None, u'operation'), 'operation', '__httpschemas_xmlsoap_orgws200303business_process_tOnMessage_operation', pyxb.binding.datatypes.NCName, required=True)
    __operation._DeclarationLocation = pyxb.utils.utility.Location('/tmp/pyxbdist.RHB65sy/PyXB-1.1.5/pyxb/bundles/wssplat/schemas/bpws.xsd', 211, 16)
    __operation._UseLocation = pyxb.utils.utility.Location('/tmp/pyxbdist.RHB65sy/PyXB-1.1.5/pyxb/bundles/wssplat/schemas/bpws.xsd', 211, 16)
    
    operation = property(__operation.value, __operation.set, None, None)

    
    # Attribute variable uses Python identifier variable
    __variable = pyxb.binding.content.AttributeUse(pyxb.namespace.ExpandedName(None, u'variable'), 'variable', '__httpschemas_xmlsoap_orgws200303business_process_tOnMessage_variable', pyxb.binding.datatypes.NCName)
    __variable._DeclarationLocation = pyxb.utils.utility.Location('/tmp/pyxbdist.RHB65sy/PyXB-1.1.5/pyxb/bundles/wssplat/schemas/bpws.xsd', 212, 16)
    __variable._UseLocation = pyxb.utils.utility.Location('/tmp/pyxbdist.RHB65sy/PyXB-1.1.5/pyxb/bundles/wssplat/schemas/bpws.xsd', 212, 16)
    
    variable = property(__variable.value, __variable.set, None, None)

    
    # Attribute portType uses Python identifier portType
    __portType = pyxb.binding.content.AttributeUse(pyxb.namespace.ExpandedName(None, u'portType'), 'portType', '__httpschemas_xmlsoap_orgws200303business_process_tOnMessage_portType', pyxb.binding.datatypes.QName, required=True)
    __portType._DeclarationLocation = pyxb.utils.utility.Location('/tmp/pyxbdist.RHB65sy/PyXB-1.1.5/pyxb/bundles/wssplat/schemas/bpws.xsd', 210, 16)
    __portType._UseLocation = pyxb.utils.utility.Location('/tmp/pyxbdist.RHB65sy/PyXB-1.1.5/pyxb/bundles/wssplat/schemas/bpws.xsd', 210, 16)
    
    portType = property(__portType.value, __portType.set, None, None)

    _AttributeWildcard = pyxb.binding.content.Wildcard(process_contents=pyxb.binding.content.Wildcard.PC_lax, namespace_constraint=(pyxb.binding.content.Wildcard.NC_not, u'http://schemas.xmlsoap.org/ws/2003/03/business-process/'))
    _HasWildcardElement = True

    _ElementMap = tExtensibleElements._ElementMap.copy()
    _ElementMap.update({
        __invoke.name() : __invoke,
        __scope.name() : __scope,
        __assign.name() : __assign,
        __switch.name() : __switch,
        __sequence.name() : __sequence,
        __correlations.name() : __correlations,
        __receive.name() : __receive,
        __while.name() : __while,
        __wait.name() : __wait,
        __empty.name() : __empty,
        __terminate.name() : __terminate,
        __reply.name() : __reply,
        __pick.name() : __pick,
        __throw.name() : __throw,
        __flow.name() : __flow
    })
    _AttributeMap = tExtensibleElements._AttributeMap.copy()
    _AttributeMap.update({
        __partnerLink.name() : __partnerLink,
        __operation.name() : __operation,
        __variable.name() : __variable,
        __portType.name() : __portType
    })
Namespace.addCategoryObject('typeBinding', u'tOnMessage', tOnMessage)


# Complex type {http://schemas.xmlsoap.org/ws/2003/03/business-process/}tCompensationHandler with content type ELEMENT_ONLY
class tCompensationHandler (tActivityOrCompensateContainer):
    _TypeDefinition = None
    _ContentTypeTag = pyxb.binding.basis.complexTypeDefinition._CT_ELEMENT_ONLY
    _Abstract = False
    _ExpandedName = pyxb.namespace.ExpandedName(Namespace, u'tCompensationHandler')
    _DefinitionLocation = pyxb.utils.utility.Location('/tmp/pyxbdist.RHB65sy/PyXB-1.1.5/pyxb/bundles/wssplat/schemas/bpws.xsd', 228, 4)
    # Base type is tActivityOrCompensateContainer
    
    # Element throw ({http://schemas.xmlsoap.org/ws/2003/03/business-process/}throw) inherited from {http://schemas.xmlsoap.org/ws/2003/03/business-process/}tActivityOrCompensateContainer
    
    # Element invoke ({http://schemas.xmlsoap.org/ws/2003/03/business-process/}invoke) inherited from {http://schemas.xmlsoap.org/ws/2003/03/business-process/}tActivityOrCompensateContainer
    
    # Element while_ ({http://schemas.xmlsoap.org/ws/2003/03/business-process/}while) inherited from {http://schemas.xmlsoap.org/ws/2003/03/business-process/}tActivityOrCompensateContainer
    
    # Element assign ({http://schemas.xmlsoap.org/ws/2003/03/business-process/}assign) inherited from {http://schemas.xmlsoap.org/ws/2003/03/business-process/}tActivityOrCompensateContainer
    
    # Element terminate ({http://schemas.xmlsoap.org/ws/2003/03/business-process/}terminate) inherited from {http://schemas.xmlsoap.org/ws/2003/03/business-process/}tActivityOrCompensateContainer
    
    # Element switch ({http://schemas.xmlsoap.org/ws/2003/03/business-process/}switch) inherited from {http://schemas.xmlsoap.org/ws/2003/03/business-process/}tActivityOrCompensateContainer
    
    # Element scope ({http://schemas.xmlsoap.org/ws/2003/03/business-process/}scope) inherited from {http://schemas.xmlsoap.org/ws/2003/03/business-process/}tActivityOrCompensateContainer
    
    # Element receive ({http://schemas.xmlsoap.org/ws/2003/03/business-process/}receive) inherited from {http://schemas.xmlsoap.org/ws/2003/03/business-process/}tActivityOrCompensateContainer
    
    # Element wait ({http://schemas.xmlsoap.org/ws/2003/03/business-process/}wait) inherited from {http://schemas.xmlsoap.org/ws/2003/03/business-process/}tActivityOrCompensateContainer
    
    # Element sequence ({http://schemas.xmlsoap.org/ws/2003/03/business-process/}sequence) inherited from {http://schemas.xmlsoap.org/ws/2003/03/business-process/}tActivityOrCompensateContainer
    
    # Element pick ({http://schemas.xmlsoap.org/ws/2003/03/business-process/}pick) inherited from {http://schemas.xmlsoap.org/ws/2003/03/business-process/}tActivityOrCompensateContainer
    
    # Element flow ({http://schemas.xmlsoap.org/ws/2003/03/business-process/}flow) inherited from {http://schemas.xmlsoap.org/ws/2003/03/business-process/}tActivityOrCompensateContainer
    
    # Element compensate ({http://schemas.xmlsoap.org/ws/2003/03/business-process/}compensate) inherited from {http://schemas.xmlsoap.org/ws/2003/03/business-process/}tActivityOrCompensateContainer
    
    # Element reply ({http://schemas.xmlsoap.org/ws/2003/03/business-process/}reply) inherited from {http://schemas.xmlsoap.org/ws/2003/03/business-process/}tActivityOrCompensateContainer
    
    # Element empty ({http://schemas.xmlsoap.org/ws/2003/03/business-process/}empty) inherited from {http://schemas.xmlsoap.org/ws/2003/03/business-process/}tActivityOrCompensateContainer
    _AttributeWildcard = pyxb.binding.content.Wildcard(process_contents=pyxb.binding.content.Wildcard.PC_lax, namespace_constraint=(pyxb.binding.content.Wildcard.NC_not, u'http://schemas.xmlsoap.org/ws/2003/03/business-process/'))
    _HasWildcardElement = True

    _ElementMap = tActivityOrCompensateContainer._ElementMap.copy()
    _ElementMap.update({
        
    })
    _AttributeMap = tActivityOrCompensateContainer._AttributeMap.copy()
    _AttributeMap.update({
        
    })
Namespace.addCategoryObject('typeBinding', u'tCompensationHandler', tCompensationHandler)


# Complex type {http://schemas.xmlsoap.org/ws/2003/03/business-process/}tCompensate with content type ELEMENT_ONLY
class tCompensate (tActivity):
    _TypeDefinition = None
    _ContentTypeTag = pyxb.binding.basis.complexTypeDefinition._CT_ELEMENT_ONLY
    _Abstract = False
    _ExpandedName = pyxb.namespace.ExpandedName(Namespace, u'tCompensate')
    _DefinitionLocation = pyxb.utils.utility.Location('/tmp/pyxbdist.RHB65sy/PyXB-1.1.5/pyxb/bundles/wssplat/schemas/bpws.xsd', 518, 4)
    # Base type is tActivity
    
    # Element source ({http://schemas.xmlsoap.org/ws/2003/03/business-process/}source) inherited from {http://schemas.xmlsoap.org/ws/2003/03/business-process/}tActivity
    
    # Element target ({http://schemas.xmlsoap.org/ws/2003/03/business-process/}target) inherited from {http://schemas.xmlsoap.org/ws/2003/03/business-process/}tActivity
    
    # Attribute joinCondition inherited from {http://schemas.xmlsoap.org/ws/2003/03/business-process/}tActivity
    
    # Attribute name inherited from {http://schemas.xmlsoap.org/ws/2003/03/business-process/}tActivity
    
    # Attribute suppressJoinFailure inherited from {http://schemas.xmlsoap.org/ws/2003/03/business-process/}tActivity
    
    # Attribute scope uses Python identifier scope
    __scope = pyxb.binding.content.AttributeUse(pyxb.namespace.ExpandedName(None, u'scope'), 'scope', '__httpschemas_xmlsoap_orgws200303business_process_tCompensate_scope', pyxb.binding.datatypes.NCName)
    __scope._DeclarationLocation = pyxb.utils.utility.Location('/tmp/pyxbdist.RHB65sy/PyXB-1.1.5/pyxb/bundles/wssplat/schemas/bpws.xsd', 521, 16)
    __scope._UseLocation = pyxb.utils.utility.Location('/tmp/pyxbdist.RHB65sy/PyXB-1.1.5/pyxb/bundles/wssplat/schemas/bpws.xsd', 521, 16)
    
    scope = property(__scope.value, __scope.set, None, None)

    _AttributeWildcard = pyxb.binding.content.Wildcard(process_contents=pyxb.binding.content.Wildcard.PC_lax, namespace_constraint=(pyxb.binding.content.Wildcard.NC_not, u'http://schemas.xmlsoap.org/ws/2003/03/business-process/'))
    _HasWildcardElement = True

    _ElementMap = tActivity._ElementMap.copy()
    _ElementMap.update({
        
    })
    _AttributeMap = tActivity._AttributeMap.copy()
    _AttributeMap.update({
        __scope.name() : __scope
    })
Namespace.addCategoryObject('typeBinding', u'tCompensate', tCompensate)


# Complex type {http://schemas.xmlsoap.org/ws/2003/03/business-process/}tTarget with content type ELEMENT_ONLY
class tTarget (tExtensibleElements):
    _TypeDefinition = None
    _ContentTypeTag = pyxb.binding.basis.complexTypeDefinition._CT_ELEMENT_ONLY
    _Abstract = False
    _ExpandedName = pyxb.namespace.ExpandedName(Namespace, u'tTarget')
    _DefinitionLocation = pyxb.utils.utility.Location('/tmp/pyxbdist.RHB65sy/PyXB-1.1.5/pyxb/bundles/wssplat/schemas/bpws.xsd', 316, 4)
    # Base type is tExtensibleElements
    
    # Attribute linkName uses Python identifier linkName
    __linkName = pyxb.binding.content.AttributeUse(pyxb.namespace.ExpandedName(None, u'linkName'), 'linkName', '__httpschemas_xmlsoap_orgws200303business_process_tTarget_linkName', pyxb.binding.datatypes.NCName, required=True)
    __linkName._DeclarationLocation = pyxb.utils.utility.Location('/tmp/pyxbdist.RHB65sy/PyXB-1.1.5/pyxb/bundles/wssplat/schemas/bpws.xsd', 319, 16)
    __linkName._UseLocation = pyxb.utils.utility.Location('/tmp/pyxbdist.RHB65sy/PyXB-1.1.5/pyxb/bundles/wssplat/schemas/bpws.xsd', 319, 16)
    
    linkName = property(__linkName.value, __linkName.set, None, None)

    _AttributeWildcard = pyxb.binding.content.Wildcard(process_contents=pyxb.binding.content.Wildcard.PC_lax, namespace_constraint=(pyxb.binding.content.Wildcard.NC_not, u'http://schemas.xmlsoap.org/ws/2003/03/business-process/'))
    _HasWildcardElement = True

    _ElementMap = tExtensibleElements._ElementMap.copy()
    _ElementMap.update({
        
    })
    _AttributeMap = tExtensibleElements._AttributeMap.copy()
    _AttributeMap.update({
        __linkName.name() : __linkName
    })
Namespace.addCategoryObject('typeBinding', u'tTarget', tTarget)


# Complex type {http://schemas.xmlsoap.org/ws/2003/03/business-process/}tScope with content type ELEMENT_ONLY
class tScope (tActivity):
    _TypeDefinition = None
    _ContentTypeTag = pyxb.binding.basis.complexTypeDefinition._CT_ELEMENT_ONLY
    _Abstract = False
    _ExpandedName = pyxb.namespace.ExpandedName(Namespace, u'tScope')
    _DefinitionLocation = pyxb.utils.utility.Location('/tmp/pyxbdist.RHB65sy/PyXB-1.1.5/pyxb/bundles/wssplat/schemas/bpws.xsd', 626, 4)
    # Base type is tActivity
    
    # Element {http://schemas.xmlsoap.org/ws/2003/03/business-process/}terminate uses Python identifier terminate
    __terminate = pyxb.binding.content.ElementUse(pyxb.namespace.ExpandedName(Namespace, u'terminate'), 'terminate', '__httpschemas_xmlsoap_orgws200303business_process_tScope_httpschemas_xmlsoap_orgws200303business_processterminate', False)
    __terminate._DeclarationLocation = pyxb.utils.utility.Location('/tmp/pyxbdist.RHB65sy/PyXB-1.1.5/pyxb/bundles/wssplat/schemas/bpws.xsd', 76, 12)
    __terminate._UseLocation = None

    
    terminate = property(__terminate.value, __terminate.set, None, None)

    
    # Element {http://schemas.xmlsoap.org/ws/2003/03/business-process/}assign uses Python identifier assign
    __assign = pyxb.binding.content.ElementUse(pyxb.namespace.ExpandedName(Namespace, u'assign'), 'assign', '__httpschemas_xmlsoap_orgws200303business_process_tScope_httpschemas_xmlsoap_orgws200303business_processassign', False)
    __assign._DeclarationLocation = pyxb.utils.utility.Location('/tmp/pyxbdist.RHB65sy/PyXB-1.1.5/pyxb/bundles/wssplat/schemas/bpws.xsd', 73, 12)
    __assign._UseLocation = None

    
    assign = property(__assign.value, __assign.set, None, None)

    
    # Element {http://schemas.xmlsoap.org/ws/2003/03/business-process/}faultHandlers uses Python identifier faultHandlers
    __faultHandlers = pyxb.binding.content.ElementUse(pyxb.namespace.ExpandedName(Namespace, u'faultHandlers'), 'faultHandlers', '__httpschemas_xmlsoap_orgws200303business_process_tScope_httpschemas_xmlsoap_orgws200303business_processfaultHandlers', False)
    __faultHandlers._DeclarationLocation = pyxb.utils.utility.Location('/tmp/pyxbdist.RHB65sy/PyXB-1.1.5/pyxb/bundles/wssplat/schemas/bpws.xsd', 636, 20)
    __faultHandlers._UseLocation = None

    
    faultHandlers = property(__faultHandlers.value, __faultHandlers.set, None, None)

    
    # Element {http://schemas.xmlsoap.org/ws/2003/03/business-process/}throw uses Python identifier throw
    __throw = pyxb.binding.content.ElementUse(pyxb.namespace.ExpandedName(Namespace, u'throw'), 'throw', '__httpschemas_xmlsoap_orgws200303business_process_tScope_httpschemas_xmlsoap_orgws200303business_processthrow', False)
    __throw._DeclarationLocation = pyxb.utils.utility.Location('/tmp/pyxbdist.RHB65sy/PyXB-1.1.5/pyxb/bundles/wssplat/schemas/bpws.xsd', 75, 12)
    __throw._UseLocation = None

    
    throw = property(__throw.value, __throw.set, None, None)

    
    # Element {http://schemas.xmlsoap.org/ws/2003/03/business-process/}sequence uses Python identifier sequence
    __sequence = pyxb.binding.content.ElementUse(pyxb.namespace.ExpandedName(Namespace, u'sequence'), 'sequence', '__httpschemas_xmlsoap_orgws200303business_process_tScope_httpschemas_xmlsoap_orgws200303business_processsequence', False)
    __sequence._DeclarationLocation = pyxb.utils.utility.Location('/tmp/pyxbdist.RHB65sy/PyXB-1.1.5/pyxb/bundles/wssplat/schemas/bpws.xsd', 80, 12)
    __sequence._UseLocation = None

    
    sequence = property(__sequence.value, __sequence.set, None, None)

    
    # Element {http://schemas.xmlsoap.org/ws/2003/03/business-process/}pick uses Python identifier pick
    __pick = pyxb.binding.content.ElementUse(pyxb.namespace.ExpandedName(Namespace, u'pick'), 'pick', '__httpschemas_xmlsoap_orgws200303business_process_tScope_httpschemas_xmlsoap_orgws200303business_processpick', False)
    __pick._DeclarationLocation = pyxb.utils.utility.Location('/tmp/pyxbdist.RHB65sy/PyXB-1.1.5/pyxb/bundles/wssplat/schemas/bpws.xsd', 81, 12)
    __pick._UseLocation = None

    
    pick = property(__pick.value, __pick.set, None, None)

    
    # Element {http://schemas.xmlsoap.org/ws/2003/03/business-process/}wait uses Python identifier wait
    __wait = pyxb.binding.content.ElementUse(pyxb.namespace.ExpandedName(Namespace, u'wait'), 'wait', '__httpschemas_xmlsoap_orgws200303business_process_tScope_httpschemas_xmlsoap_orgws200303business_processwait', False)
    __wait._DeclarationLocation = pyxb.utils.utility.Location('/tmp/pyxbdist.RHB65sy/PyXB-1.1.5/pyxb/bundles/wssplat/schemas/bpws.xsd', 74, 12)
    __wait._UseLocation = None

    
    wait = property(__wait.value, __wait.set, None, None)

    
    # Element {http://schemas.xmlsoap.org/ws/2003/03/business-process/}scope uses Python identifier scope
    __scope = pyxb.binding.content.ElementUse(pyxb.namespace.ExpandedName(Namespace, u'scope'), 'scope', '__httpschemas_xmlsoap_orgws200303business_process_tScope_httpschemas_xmlsoap_orgws200303business_processscope', False)
    __scope._DeclarationLocation = pyxb.utils.utility.Location('/tmp/pyxbdist.RHB65sy/PyXB-1.1.5/pyxb/bundles/wssplat/schemas/bpws.xsd', 82, 12)
    __scope._UseLocation = None

    
    scope = property(__scope.value, __scope.set, None, None)

    
    # Element {http://schemas.xmlsoap.org/ws/2003/03/business-process/}flow uses Python identifier flow
    __flow = pyxb.binding.content.ElementUse(pyxb.namespace.ExpandedName(Namespace, u'flow'), 'flow', '__httpschemas_xmlsoap_orgws200303business_process_tScope_httpschemas_xmlsoap_orgws200303business_processflow', False)
    __flow._DeclarationLocation = pyxb.utils.utility.Location('/tmp/pyxbdist.RHB65sy/PyXB-1.1.5/pyxb/bundles/wssplat/schemas/bpws.xsd', 77, 12)
    __flow._UseLocation = None

    
    flow = property(__flow.value, __flow.set, None, None)

    
    # Element {http://schemas.xmlsoap.org/ws/2003/03/business-process/}compensationHandler uses Python identifier compensationHandler
    __compensationHandler = pyxb.binding.content.ElementUse(pyxb.namespace.ExpandedName(Namespace, u'compensationHandler'), 'compensationHandler', '__httpschemas_xmlsoap_orgws200303business_process_tScope_httpschemas_xmlsoap_orgws200303business_processcompensationHandler', False)
    __compensationHandler._DeclarationLocation = pyxb.utils.utility.Location('/tmp/pyxbdist.RHB65sy/PyXB-1.1.5/pyxb/bundles/wssplat/schemas/bpws.xsd', 639, 20)
    __compensationHandler._UseLocation = None

    
    compensationHandler = property(__compensationHandler.value, __compensationHandler.set, None, None)

    
    # Element {http://schemas.xmlsoap.org/ws/2003/03/business-process/}empty uses Python identifier empty
    __empty = pyxb.binding.content.ElementUse(pyxb.namespace.ExpandedName(Namespace, u'empty'), 'empty', '__httpschemas_xmlsoap_orgws200303business_process_tScope_httpschemas_xmlsoap_orgws200303business_processempty', False)
    __empty._DeclarationLocation = pyxb.utils.utility.Location('/tmp/pyxbdist.RHB65sy/PyXB-1.1.5/pyxb/bundles/wssplat/schemas/bpws.xsd', 69, 12)
    __empty._UseLocation = None

    
    empty = property(__empty.value, __empty.set, None, None)

    
    # Element {http://schemas.xmlsoap.org/ws/2003/03/business-process/}correlationSets uses Python identifier correlationSets
    __correlationSets = pyxb.binding.content.ElementUse(pyxb.namespace.ExpandedName(Namespace, u'correlationSets'), 'correlationSets', '__httpschemas_xmlsoap_orgws200303business_process_tScope_httpschemas_xmlsoap_orgws200303business_processcorrelationSets', False)
    __correlationSets._DeclarationLocation = pyxb.utils.utility.Location('/tmp/pyxbdist.RHB65sy/PyXB-1.1.5/pyxb/bundles/wssplat/schemas/bpws.xsd', 633, 20)
    __correlationSets._UseLocation = None

    
    correlationSets = property(__correlationSets.value, __correlationSets.set, None, None)

    
    # Element {http://schemas.xmlsoap.org/ws/2003/03/business-process/}reply uses Python identifier reply
    __reply = pyxb.binding.content.ElementUse(pyxb.namespace.ExpandedName(Namespace, u'reply'), 'reply', '__httpschemas_xmlsoap_orgws200303business_process_tScope_httpschemas_xmlsoap_orgws200303business_processreply', False)
    __reply._DeclarationLocation = pyxb.utils.utility.Location('/tmp/pyxbdist.RHB65sy/PyXB-1.1.5/pyxb/bundles/wssplat/schemas/bpws.xsd', 72, 12)
    __reply._UseLocation = None

    
    reply = property(__reply.value, __reply.set, None, None)

    
    # Element {http://schemas.xmlsoap.org/ws/2003/03/business-process/}receive uses Python identifier receive
    __receive = pyxb.binding.content.ElementUse(pyxb.namespace.ExpandedName(Namespace, u'receive'), 'receive', '__httpschemas_xmlsoap_orgws200303business_process_tScope_httpschemas_xmlsoap_orgws200303business_processreceive', False)
    __receive._DeclarationLocation = pyxb.utils.utility.Location('/tmp/pyxbdist.RHB65sy/PyXB-1.1.5/pyxb/bundles/wssplat/schemas/bpws.xsd', 71, 12)
    __receive._UseLocation = None

    
    receive = property(__receive.value, __receive.set, None, None)

    
    # Element {http://schemas.xmlsoap.org/ws/2003/03/business-process/}switch uses Python identifier switch
    __switch = pyxb.binding.content.ElementUse(pyxb.namespace.ExpandedName(Namespace, u'switch'), 'switch', '__httpschemas_xmlsoap_orgws200303business_process_tScope_httpschemas_xmlsoap_orgws200303business_processswitch', False)
    __switch._DeclarationLocation = pyxb.utils.utility.Location('/tmp/pyxbdist.RHB65sy/PyXB-1.1.5/pyxb/bundles/wssplat/schemas/bpws.xsd', 78, 12)
    __switch._UseLocation = None

    
    switch = property(__switch.value, __switch.set, None, None)

    
    # Element {http://schemas.xmlsoap.org/ws/2003/03/business-process/}variables uses Python identifier variables
    __variables = pyxb.binding.content.ElementUse(pyxb.namespace.ExpandedName(Namespace, u'variables'), 'variables', '__httpschemas_xmlsoap_orgws200303business_process_tScope_httpschemas_xmlsoap_orgws200303business_processvariables', False)
    __variables._DeclarationLocation = pyxb.utils.utility.Location('/tmp/pyxbdist.RHB65sy/PyXB-1.1.5/pyxb/bundles/wssplat/schemas/bpws.xsd', 630, 20)
    __variables._UseLocation = None

    
    variables = property(__variables.value, __variables.set, None, None)

    
    # Element {http://schemas.xmlsoap.org/ws/2003/03/business-process/}invoke uses Python identifier invoke
    __invoke = pyxb.binding.content.ElementUse(pyxb.namespace.ExpandedName(Namespace, u'invoke'), 'invoke', '__httpschemas_xmlsoap_orgws200303business_process_tScope_httpschemas_xmlsoap_orgws200303business_processinvoke', False)
    __invoke._DeclarationLocation = pyxb.utils.utility.Location('/tmp/pyxbdist.RHB65sy/PyXB-1.1.5/pyxb/bundles/wssplat/schemas/bpws.xsd', 70, 12)
    __invoke._UseLocation = None

    
    invoke = property(__invoke.value, __invoke.set, None, None)

    
    # Element {http://schemas.xmlsoap.org/ws/2003/03/business-process/}while uses Python identifier while_
    __while = pyxb.binding.content.ElementUse(pyxb.namespace.ExpandedName(Namespace, u'while'), 'while_', '__httpschemas_xmlsoap_orgws200303business_process_tScope_httpschemas_xmlsoap_orgws200303business_processwhile', False)
    __while._DeclarationLocation = pyxb.utils.utility.Location('/tmp/pyxbdist.RHB65sy/PyXB-1.1.5/pyxb/bundles/wssplat/schemas/bpws.xsd', 79, 12)
    __while._UseLocation = None

    
    while_ = property(__while.value, __while.set, None, None)

    
    # Element target ({http://schemas.xmlsoap.org/ws/2003/03/business-process/}target) inherited from {http://schemas.xmlsoap.org/ws/2003/03/business-process/}tActivity
    
    # Element source ({http://schemas.xmlsoap.org/ws/2003/03/business-process/}source) inherited from {http://schemas.xmlsoap.org/ws/2003/03/business-process/}tActivity
    
    # Element {http://schemas.xmlsoap.org/ws/2003/03/business-process/}eventHandlers uses Python identifier eventHandlers
    __eventHandlers = pyxb.binding.content.ElementUse(pyxb.namespace.ExpandedName(Namespace, u'eventHandlers'), 'eventHandlers', '__httpschemas_xmlsoap_orgws200303business_process_tScope_httpschemas_xmlsoap_orgws200303business_processeventHandlers', False)
    __eventHandlers._DeclarationLocation = pyxb.utils.utility.Location('/tmp/pyxbdist.RHB65sy/PyXB-1.1.5/pyxb/bundles/wssplat/schemas/bpws.xsd', 642, 20)
    __eventHandlers._UseLocation = None

    
    eventHandlers = property(__eventHandlers.value, __eventHandlers.set, None, None)

    
    # Attribute name inherited from {http://schemas.xmlsoap.org/ws/2003/03/business-process/}tActivity
    
    # Attribute variableAccessSerializable uses Python identifier variableAccessSerializable
    __variableAccessSerializable = pyxb.binding.content.AttributeUse(pyxb.namespace.ExpandedName(None, u'variableAccessSerializable'), 'variableAccessSerializable', '__httpschemas_xmlsoap_orgws200303business_process_tScope_variableAccessSerializable', tBoolean, unicode_default=u'no')
    __variableAccessSerializable._DeclarationLocation = pyxb.utils.utility.Location('/tmp/pyxbdist.RHB65sy/PyXB-1.1.5/pyxb/bundles/wssplat/schemas/bpws.xsd', 647, 16)
    __variableAccessSerializable._UseLocation = pyxb.utils.utility.Location('/tmp/pyxbdist.RHB65sy/PyXB-1.1.5/pyxb/bundles/wssplat/schemas/bpws.xsd', 647, 16)
    
    variableAccessSerializable = property(__variableAccessSerializable.value, __variableAccessSerializable.set, None, None)

    
    # Attribute suppressJoinFailure inherited from {http://schemas.xmlsoap.org/ws/2003/03/business-process/}tActivity
    
    # Attribute joinCondition inherited from {http://schemas.xmlsoap.org/ws/2003/03/business-process/}tActivity
    _AttributeWildcard = pyxb.binding.content.Wildcard(process_contents=pyxb.binding.content.Wildcard.PC_lax, namespace_constraint=(pyxb.binding.content.Wildcard.NC_not, u'http://schemas.xmlsoap.org/ws/2003/03/business-process/'))
    _HasWildcardElement = True

    _ElementMap = tActivity._ElementMap.copy()
    _ElementMap.update({
        __terminate.name() : __terminate,
        __assign.name() : __assign,
        __faultHandlers.name() : __faultHandlers,
        __throw.name() : __throw,
        __sequence.name() : __sequence,
        __pick.name() : __pick,
        __wait.name() : __wait,
        __scope.name() : __scope,
        __flow.name() : __flow,
        __compensationHandler.name() : __compensationHandler,
        __empty.name() : __empty,
        __correlationSets.name() : __correlationSets,
        __reply.name() : __reply,
        __receive.name() : __receive,
        __switch.name() : __switch,
        __variables.name() : __variables,
        __invoke.name() : __invoke,
        __while.name() : __while,
        __eventHandlers.name() : __eventHandlers
    })
    _AttributeMap = tActivity._AttributeMap.copy()
    _AttributeMap.update({
        __variableAccessSerializable.name() : __variableAccessSerializable
    })
Namespace.addCategoryObject('typeBinding', u'tScope', tScope)


# Complex type {http://schemas.xmlsoap.org/ws/2003/03/business-process/}tFrom with content type ELEMENT_ONLY
class tFrom (tExtensibleElements):
    _TypeDefinition = None
    _ContentTypeTag = pyxb.binding.basis.complexTypeDefinition._CT_ELEMENT_ONLY
    _Abstract = False
    _ExpandedName = pyxb.namespace.ExpandedName(Namespace, u'tFrom')
    _DefinitionLocation = pyxb.utils.utility.Location('/tmp/pyxbdist.RHB65sy/PyXB-1.1.5/pyxb/bundles/wssplat/schemas/bpws.xsd', 467, 4)
    # Base type is tExtensibleElements
    
    # Attribute part uses Python identifier part
    __part = pyxb.binding.content.AttributeUse(pyxb.namespace.ExpandedName(None, u'part'), 'part', '__httpschemas_xmlsoap_orgws200303business_process_tFrom_part', pyxb.binding.datatypes.NCName)
    __part._DeclarationLocation = pyxb.utils.utility.Location('/tmp/pyxbdist.RHB65sy/PyXB-1.1.5/pyxb/bundles/wssplat/schemas/bpws.xsd', 471, 16)
    __part._UseLocation = pyxb.utils.utility.Location('/tmp/pyxbdist.RHB65sy/PyXB-1.1.5/pyxb/bundles/wssplat/schemas/bpws.xsd', 471, 16)
    
    part = property(__part.value, __part.set, None, None)

    
    # Attribute opaque uses Python identifier opaque
    __opaque = pyxb.binding.content.AttributeUse(pyxb.namespace.ExpandedName(None, u'opaque'), 'opaque', '__httpschemas_xmlsoap_orgws200303business_process_tFrom_opaque', tBoolean)
    __opaque._DeclarationLocation = pyxb.utils.utility.Location('/tmp/pyxbdist.RHB65sy/PyXB-1.1.5/pyxb/bundles/wssplat/schemas/bpws.xsd', 477, 16)
    __opaque._UseLocation = pyxb.utils.utility.Location('/tmp/pyxbdist.RHB65sy/PyXB-1.1.5/pyxb/bundles/wssplat/schemas/bpws.xsd', 477, 16)
    
    opaque = property(__opaque.value, __opaque.set, None, None)

    
    # Attribute endpointReference uses Python identifier endpointReference
    __endpointReference = pyxb.binding.content.AttributeUse(pyxb.namespace.ExpandedName(None, u'endpointReference'), 'endpointReference', '__httpschemas_xmlsoap_orgws200303business_process_tFrom_endpointReference', tRoles)
    __endpointReference._DeclarationLocation = pyxb.utils.utility.Location('/tmp/pyxbdist.RHB65sy/PyXB-1.1.5/pyxb/bundles/wssplat/schemas/bpws.xsd', 475, 16)
    __endpointReference._UseLocation = pyxb.utils.utility.Location('/tmp/pyxbdist.RHB65sy/PyXB-1.1.5/pyxb/bundles/wssplat/schemas/bpws.xsd', 475, 16)
    
    endpointReference = property(__endpointReference.value, __endpointReference.set, None, None)

    
    # Attribute query uses Python identifier query
    __query = pyxb.binding.content.AttributeUse(pyxb.namespace.ExpandedName(None, u'query'), 'query', '__httpschemas_xmlsoap_orgws200303business_process_tFrom_query', pyxb.binding.datatypes.string)
    __query._DeclarationLocation = pyxb.utils.utility.Location('/tmp/pyxbdist.RHB65sy/PyXB-1.1.5/pyxb/bundles/wssplat/schemas/bpws.xsd', 472, 16)
    __query._UseLocation = pyxb.utils.utility.Location('/tmp/pyxbdist.RHB65sy/PyXB-1.1.5/pyxb/bundles/wssplat/schemas/bpws.xsd', 472, 16)
    
    query = property(__query.value, __query.set, None, None)

    
    # Attribute property uses Python identifier property_
    __property = pyxb.binding.content.AttributeUse(pyxb.namespace.ExpandedName(None, u'property'), 'property_', '__httpschemas_xmlsoap_orgws200303business_process_tFrom_property', pyxb.binding.datatypes.QName)
    __property._DeclarationLocation = pyxb.utils.utility.Location('/tmp/pyxbdist.RHB65sy/PyXB-1.1.5/pyxb/bundles/wssplat/schemas/bpws.xsd', 473, 16)
    __property._UseLocation = pyxb.utils.utility.Location('/tmp/pyxbdist.RHB65sy/PyXB-1.1.5/pyxb/bundles/wssplat/schemas/bpws.xsd', 473, 16)
    
    property_ = property(__property.value, __property.set, None, None)

    
    # Attribute partnerLink uses Python identifier partnerLink
    __partnerLink = pyxb.binding.content.AttributeUse(pyxb.namespace.ExpandedName(None, u'partnerLink'), 'partnerLink', '__httpschemas_xmlsoap_orgws200303business_process_tFrom_partnerLink', pyxb.binding.datatypes.NCName)
    __partnerLink._DeclarationLocation = pyxb.utils.utility.Location('/tmp/pyxbdist.RHB65sy/PyXB-1.1.5/pyxb/bundles/wssplat/schemas/bpws.xsd', 474, 16)
    __partnerLink._UseLocation = pyxb.utils.utility.Location('/tmp/pyxbdist.RHB65sy/PyXB-1.1.5/pyxb/bundles/wssplat/schemas/bpws.xsd', 474, 16)
    
    partnerLink = property(__partnerLink.value, __partnerLink.set, None, None)

    
    # Attribute expression uses Python identifier expression
    __expression = pyxb.binding.content.AttributeUse(pyxb.namespace.ExpandedName(None, u'expression'), 'expression', '__httpschemas_xmlsoap_orgws200303business_process_tFrom_expression', pyxb.binding.datatypes.string)
    __expression._DeclarationLocation = pyxb.utils.utility.Location('/tmp/pyxbdist.RHB65sy/PyXB-1.1.5/pyxb/bundles/wssplat/schemas/bpws.xsd', 476, 16)
    __expression._UseLocation = pyxb.utils.utility.Location('/tmp/pyxbdist.RHB65sy/PyXB-1.1.5/pyxb/bundles/wssplat/schemas/bpws.xsd', 476, 16)
    
    expression = property(__expression.value, __expression.set, None, None)

    
    # Attribute variable uses Python identifier variable
    __variable = pyxb.binding.content.AttributeUse(pyxb.namespace.ExpandedName(None, u'variable'), 'variable', '__httpschemas_xmlsoap_orgws200303business_process_tFrom_variable', pyxb.binding.datatypes.NCName)
    __variable._DeclarationLocation = pyxb.utils.utility.Location('/tmp/pyxbdist.RHB65sy/PyXB-1.1.5/pyxb/bundles/wssplat/schemas/bpws.xsd', 470, 16)
    __variable._UseLocation = pyxb.utils.utility.Location('/tmp/pyxbdist.RHB65sy/PyXB-1.1.5/pyxb/bundles/wssplat/schemas/bpws.xsd', 470, 16)
    
    variable = property(__variable.value, __variable.set, None, None)

    _AttributeWildcard = pyxb.binding.content.Wildcard(process_contents=pyxb.binding.content.Wildcard.PC_lax, namespace_constraint=(pyxb.binding.content.Wildcard.NC_not, u'http://schemas.xmlsoap.org/ws/2003/03/business-process/'))
    _HasWildcardElement = True

    _ElementMap = tExtensibleElements._ElementMap.copy()
    _ElementMap.update({
        
    })
    _AttributeMap = tExtensibleElements._AttributeMap.copy()
    _AttributeMap.update({
        __part.name() : __part,
        __opaque.name() : __opaque,
        __endpointReference.name() : __endpointReference,
        __query.name() : __query,
        __property.name() : __property,
        __partnerLink.name() : __partnerLink,
        __expression.name() : __expression,
        __variable.name() : __variable
    })
Namespace.addCategoryObject('typeBinding', u'tFrom', tFrom)


# Complex type [anonymous] with content type EMPTY
class CTD_ANON_2 (tFrom):
    _TypeDefinition = None
    _ContentTypeTag = pyxb.binding.basis.complexTypeDefinition._CT_EMPTY
    _Abstract = False
    _ExpandedName = None
    _DefinitionLocation = pyxb.utils.utility.Location('/tmp/pyxbdist.RHB65sy/PyXB-1.1.5/pyxb/bundles/wssplat/schemas/bpws.xsd', 483, 8)
    # Base type is tFrom
    
    # Attribute part inherited from {http://schemas.xmlsoap.org/ws/2003/03/business-process/}tFrom
    
    # Attribute property_ inherited from {http://schemas.xmlsoap.org/ws/2003/03/business-process/}tFrom
    
    # Attribute opaque is restricted from parent
    
    # Attribute opaque uses Python identifier opaque
    __opaque = pyxb.binding.content.AttributeUse(pyxb.namespace.ExpandedName(None, u'opaque'), 'opaque', '__httpschemas_xmlsoap_orgws200303business_process_tFrom_opaque', tBoolean, prohibited=True)
    __opaque._DeclarationLocation = pyxb.utils.utility.Location('/tmp/pyxbdist.RHB65sy/PyXB-1.1.5/pyxb/bundles/wssplat/schemas/bpws.xsd', 488, 20)
    __opaque._UseLocation = pyxb.utils.utility.Location('/tmp/pyxbdist.RHB65sy/PyXB-1.1.5/pyxb/bundles/wssplat/schemas/bpws.xsd', 488, 20)
    
    opaque = property()

    
    # Attribute query inherited from {http://schemas.xmlsoap.org/ws/2003/03/business-process/}tFrom
    
    # Attribute endpointReference is restricted from parent
    
    # Attribute endpointReference uses Python identifier endpointReference
    __endpointReference = pyxb.binding.content.AttributeUse(pyxb.namespace.ExpandedName(None, u'endpointReference'), 'endpointReference', '__httpschemas_xmlsoap_orgws200303business_process_tFrom_endpointReference', tRoles, prohibited=True)
    __endpointReference._DeclarationLocation = pyxb.utils.utility.Location('/tmp/pyxbdist.RHB65sy/PyXB-1.1.5/pyxb/bundles/wssplat/schemas/bpws.xsd', 490, 20)
    __endpointReference._UseLocation = pyxb.utils.utility.Location('/tmp/pyxbdist.RHB65sy/PyXB-1.1.5/pyxb/bundles/wssplat/schemas/bpws.xsd', 490, 20)
    
    endpointReference = property()

    
    # Attribute partnerLink inherited from {http://schemas.xmlsoap.org/ws/2003/03/business-process/}tFrom
    
    # Attribute expression is restricted from parent
    
    # Attribute expression uses Python identifier expression
    __expression = pyxb.binding.content.AttributeUse(pyxb.namespace.ExpandedName(None, u'expression'), 'expression', '__httpschemas_xmlsoap_orgws200303business_process_tFrom_expression', pyxb.binding.datatypes.string, prohibited=True)
    __expression._DeclarationLocation = pyxb.utils.utility.Location('/tmp/pyxbdist.RHB65sy/PyXB-1.1.5/pyxb/bundles/wssplat/schemas/bpws.xsd', 486, 20)
    __expression._UseLocation = pyxb.utils.utility.Location('/tmp/pyxbdist.RHB65sy/PyXB-1.1.5/pyxb/bundles/wssplat/schemas/bpws.xsd', 486, 20)
    
    expression = property()

    
    # Attribute variable inherited from {http://schemas.xmlsoap.org/ws/2003/03/business-process/}tFrom

    _ElementMap = tFrom._ElementMap.copy()
    _ElementMap.update({
        
    })
    _AttributeMap = tFrom._AttributeMap.copy()
    _AttributeMap.update({
        __opaque.name() : __opaque,
        __endpointReference.name() : __endpointReference,
        __expression.name() : __expression
    })



# Complex type {http://schemas.xmlsoap.org/ws/2003/03/business-process/}tLinks with content type ELEMENT_ONLY
class tLinks (tExtensibleElements):
    _TypeDefinition = None
    _ContentTypeTag = pyxb.binding.basis.complexTypeDefinition._CT_ELEMENT_ONLY
    _Abstract = False
    _ExpandedName = pyxb.namespace.ExpandedName(Namespace, u'tLinks')
    _DefinitionLocation = pyxb.utils.utility.Location('/tmp/pyxbdist.RHB65sy/PyXB-1.1.5/pyxb/bundles/wssplat/schemas/bpws.xsd', 543, 4)
    # Base type is tExtensibleElements
    
    # Element {http://schemas.xmlsoap.org/ws/2003/03/business-process/}link uses Python identifier link
    __link = pyxb.binding.content.ElementUse(pyxb.namespace.ExpandedName(Namespace, u'link'), 'link', '__httpschemas_xmlsoap_orgws200303business_process_tLinks_httpschemas_xmlsoap_orgws200303business_processlink', True)
    __link._DeclarationLocation = pyxb.utils.utility.Location('/tmp/pyxbdist.RHB65sy/PyXB-1.1.5/pyxb/bundles/wssplat/schemas/bpws.xsd', 547, 20)
    __link._UseLocation = None

    
    link = property(__link.value, __link.set, None, None)

    _AttributeWildcard = pyxb.binding.content.Wildcard(process_contents=pyxb.binding.content.Wildcard.PC_lax, namespace_constraint=(pyxb.binding.content.Wildcard.NC_not, u'http://schemas.xmlsoap.org/ws/2003/03/business-process/'))
    _HasWildcardElement = True

    _ElementMap = tExtensibleElements._ElementMap.copy()
    _ElementMap.update({
        __link.name() : __link
    })
    _AttributeMap = tExtensibleElements._AttributeMap.copy()
    _AttributeMap.update({
        
    })
Namespace.addCategoryObject('typeBinding', u'tLinks', tLinks)


# Complex type {http://schemas.xmlsoap.org/ws/2003/03/business-process/}tProcess with content type ELEMENT_ONLY
class tProcess (tExtensibleElements):
    _TypeDefinition = None
    _ContentTypeTag = pyxb.binding.basis.complexTypeDefinition._CT_ELEMENT_ONLY
    _Abstract = False
    _ExpandedName = pyxb.namespace.ExpandedName(Namespace, u'tProcess')
    _DefinitionLocation = pyxb.utils.utility.Location('/tmp/pyxbdist.RHB65sy/PyXB-1.1.5/pyxb/bundles/wssplat/schemas/bpws.xsd', 28, 4)
    # Base type is tExtensibleElements
    
    # Element {http://schemas.xmlsoap.org/ws/2003/03/business-process/}reply uses Python identifier reply
    __reply = pyxb.binding.content.ElementUse(pyxb.namespace.ExpandedName(Namespace, u'reply'), 'reply', '__httpschemas_xmlsoap_orgws200303business_process_tProcess_httpschemas_xmlsoap_orgws200303business_processreply', False)
    __reply._DeclarationLocation = pyxb.utils.utility.Location('/tmp/pyxbdist.RHB65sy/PyXB-1.1.5/pyxb/bundles/wssplat/schemas/bpws.xsd', 72, 12)
    __reply._UseLocation = None

    
    reply = property(__reply.value, __reply.set, None, None)

    
    # Element {http://schemas.xmlsoap.org/ws/2003/03/business-process/}partners uses Python identifier partners
    __partners = pyxb.binding.content.ElementUse(pyxb.namespace.ExpandedName(Namespace, u'partners'), 'partners', '__httpschemas_xmlsoap_orgws200303business_process_tProcess_httpschemas_xmlsoap_orgws200303business_processpartners', False)
    __partners._DeclarationLocation = pyxb.utils.utility.Location('/tmp/pyxbdist.RHB65sy/PyXB-1.1.5/pyxb/bundles/wssplat/schemas/bpws.xsd', 34, 20)
    __partners._UseLocation = None

    
    partners = property(__partners.value, __partners.set, None, None)

    
    # Element {http://schemas.xmlsoap.org/ws/2003/03/business-process/}terminate uses Python identifier terminate
    __terminate = pyxb.binding.content.ElementUse(pyxb.namespace.ExpandedName(Namespace, u'terminate'), 'terminate', '__httpschemas_xmlsoap_orgws200303business_process_tProcess_httpschemas_xmlsoap_orgws200303business_processterminate', False)
    __terminate._DeclarationLocation = pyxb.utils.utility.Location('/tmp/pyxbdist.RHB65sy/PyXB-1.1.5/pyxb/bundles/wssplat/schemas/bpws.xsd', 76, 12)
    __terminate._UseLocation = None

    
    terminate = property(__terminate.value, __terminate.set, None, None)

    
    # Element {http://schemas.xmlsoap.org/ws/2003/03/business-process/}sequence uses Python identifier sequence
    __sequence = pyxb.binding.content.ElementUse(pyxb.namespace.ExpandedName(Namespace, u'sequence'), 'sequence', '__httpschemas_xmlsoap_orgws200303business_process_tProcess_httpschemas_xmlsoap_orgws200303business_processsequence', False)
    __sequence._DeclarationLocation = pyxb.utils.utility.Location('/tmp/pyxbdist.RHB65sy/PyXB-1.1.5/pyxb/bundles/wssplat/schemas/bpws.xsd', 80, 12)
    __sequence._UseLocation = None

    
    sequence = property(__sequence.value, __sequence.set, None, None)

    
    # Element {http://schemas.xmlsoap.org/ws/2003/03/business-process/}wait uses Python identifier wait
    __wait = pyxb.binding.content.ElementUse(pyxb.namespace.ExpandedName(Namespace, u'wait'), 'wait', '__httpschemas_xmlsoap_orgws200303business_process_tProcess_httpschemas_xmlsoap_orgws200303business_processwait', False)
    __wait._DeclarationLocation = pyxb.utils.utility.Location('/tmp/pyxbdist.RHB65sy/PyXB-1.1.5/pyxb/bundles/wssplat/schemas/bpws.xsd', 74, 12)
    __wait._UseLocation = None

    
    wait = property(__wait.value, __wait.set, None, None)

    
    # Element {http://schemas.xmlsoap.org/ws/2003/03/business-process/}receive uses Python identifier receive
    __receive = pyxb.binding.content.ElementUse(pyxb.namespace.ExpandedName(Namespace, u'receive'), 'receive', '__httpschemas_xmlsoap_orgws200303business_process_tProcess_httpschemas_xmlsoap_orgws200303business_processreceive', False)
    __receive._DeclarationLocation = pyxb.utils.utility.Location('/tmp/pyxbdist.RHB65sy/PyXB-1.1.5/pyxb/bundles/wssplat/schemas/bpws.xsd', 71, 12)
    __receive._UseLocation = None

    
    receive = property(__receive.value, __receive.set, None, None)

    
    # Element {http://schemas.xmlsoap.org/ws/2003/03/business-process/}partnerLinks uses Python identifier partnerLinks
    __partnerLinks = pyxb.binding.content.ElementUse(pyxb.namespace.ExpandedName(Namespace, u'partnerLinks'), 'partnerLinks', '__httpschemas_xmlsoap_orgws200303business_process_tProcess_httpschemas_xmlsoap_orgws200303business_processpartnerLinks', False)
    __partnerLinks._DeclarationLocation = pyxb.utils.utility.Location('/tmp/pyxbdist.RHB65sy/PyXB-1.1.5/pyxb/bundles/wssplat/schemas/bpws.xsd', 32, 20)
    __partnerLinks._UseLocation = None

    
    partnerLinks = property(__partnerLinks.value, __partnerLinks.set, None, None)

    
    # Element {http://schemas.xmlsoap.org/ws/2003/03/business-process/}eventHandlers uses Python identifier eventHandlers
    __eventHandlers = pyxb.binding.content.ElementUse(pyxb.namespace.ExpandedName(Namespace, u'eventHandlers'), 'eventHandlers', '__httpschemas_xmlsoap_orgws200303business_process_tProcess_httpschemas_xmlsoap_orgws200303business_processeventHandlers', False)
    __eventHandlers._DeclarationLocation = pyxb.utils.utility.Location('/tmp/pyxbdist.RHB65sy/PyXB-1.1.5/pyxb/bundles/wssplat/schemas/bpws.xsd', 45, 20)
    __eventHandlers._UseLocation = None

    
    eventHandlers = property(__eventHandlers.value, __eventHandlers.set, None, None)

    
    # Element {http://schemas.xmlsoap.org/ws/2003/03/business-process/}flow uses Python identifier flow
    __flow = pyxb.binding.content.ElementUse(pyxb.namespace.ExpandedName(Namespace, u'flow'), 'flow', '__httpschemas_xmlsoap_orgws200303business_process_tProcess_httpschemas_xmlsoap_orgws200303business_processflow', False)
    __flow._DeclarationLocation = pyxb.utils.utility.Location('/tmp/pyxbdist.RHB65sy/PyXB-1.1.5/pyxb/bundles/wssplat/schemas/bpws.xsd', 77, 12)
    __flow._UseLocation = None

    
    flow = property(__flow.value, __flow.set, None, None)

    
    # Element {http://schemas.xmlsoap.org/ws/2003/03/business-process/}pick uses Python identifier pick
    __pick = pyxb.binding.content.ElementUse(pyxb.namespace.ExpandedName(Namespace, u'pick'), 'pick', '__httpschemas_xmlsoap_orgws200303business_process_tProcess_httpschemas_xmlsoap_orgws200303business_processpick', False)
    __pick._DeclarationLocation = pyxb.utils.utility.Location('/tmp/pyxbdist.RHB65sy/PyXB-1.1.5/pyxb/bundles/wssplat/schemas/bpws.xsd', 81, 12)
    __pick._UseLocation = None

    
    pick = property(__pick.value, __pick.set, None, None)

    
    # Element {http://schemas.xmlsoap.org/ws/2003/03/business-process/}empty uses Python identifier empty
    __empty = pyxb.binding.content.ElementUse(pyxb.namespace.ExpandedName(Namespace, u'empty'), 'empty', '__httpschemas_xmlsoap_orgws200303business_process_tProcess_httpschemas_xmlsoap_orgws200303business_processempty', False)
    __empty._DeclarationLocation = pyxb.utils.utility.Location('/tmp/pyxbdist.RHB65sy/PyXB-1.1.5/pyxb/bundles/wssplat/schemas/bpws.xsd', 69, 12)
    __empty._UseLocation = None

    
    empty = property(__empty.value, __empty.set, None, None)

    
    # Element {http://schemas.xmlsoap.org/ws/2003/03/business-process/}invoke uses Python identifier invoke
    __invoke = pyxb.binding.content.ElementUse(pyxb.namespace.ExpandedName(Namespace, u'invoke'), 'invoke', '__httpschemas_xmlsoap_orgws200303business_process_tProcess_httpschemas_xmlsoap_orgws200303business_processinvoke', False)
    __invoke._DeclarationLocation = pyxb.utils.utility.Location('/tmp/pyxbdist.RHB65sy/PyXB-1.1.5/pyxb/bundles/wssplat/schemas/bpws.xsd', 70, 12)
    __invoke._UseLocation = None

    
    invoke = property(__invoke.value, __invoke.set, None, None)

    
    # Element {http://schemas.xmlsoap.org/ws/2003/03/business-process/}correlationSets uses Python identifier correlationSets
    __correlationSets = pyxb.binding.content.ElementUse(pyxb.namespace.ExpandedName(Namespace, u'correlationSets'), 'correlationSets', '__httpschemas_xmlsoap_orgws200303business_process_tProcess_httpschemas_xmlsoap_orgws200303business_processcorrelationSets', False)
    __correlationSets._DeclarationLocation = pyxb.utils.utility.Location('/tmp/pyxbdist.RHB65sy/PyXB-1.1.5/pyxb/bundles/wssplat/schemas/bpws.xsd', 39, 20)
    __correlationSets._UseLocation = None

    
    correlationSets = property(__correlationSets.value, __correlationSets.set, None, None)

    
    # Element {http://schemas.xmlsoap.org/ws/2003/03/business-process/}switch uses Python identifier switch
    __switch = pyxb.binding.content.ElementUse(pyxb.namespace.ExpandedName(Namespace, u'switch'), 'switch', '__httpschemas_xmlsoap_orgws200303business_process_tProcess_httpschemas_xmlsoap_orgws200303business_processswitch', False)
    __switch._DeclarationLocation = pyxb.utils.utility.Location('/tmp/pyxbdist.RHB65sy/PyXB-1.1.5/pyxb/bundles/wssplat/schemas/bpws.xsd', 78, 12)
    __switch._UseLocation = None

    
    switch = property(__switch.value, __switch.set, None, None)

    
    # Element {http://schemas.xmlsoap.org/ws/2003/03/business-process/}throw uses Python identifier throw
    __throw = pyxb.binding.content.ElementUse(pyxb.namespace.ExpandedName(Namespace, u'throw'), 'throw', '__httpschemas_xmlsoap_orgws200303business_process_tProcess_httpschemas_xmlsoap_orgws200303business_processthrow', False)
    __throw._DeclarationLocation = pyxb.utils.utility.Location('/tmp/pyxbdist.RHB65sy/PyXB-1.1.5/pyxb/bundles/wssplat/schemas/bpws.xsd', 75, 12)
    __throw._UseLocation = None

    
    throw = property(__throw.value, __throw.set, None, None)

    
    # Element {http://schemas.xmlsoap.org/ws/2003/03/business-process/}scope uses Python identifier scope
    __scope = pyxb.binding.content.ElementUse(pyxb.namespace.ExpandedName(Namespace, u'scope'), 'scope', '__httpschemas_xmlsoap_orgws200303business_process_tProcess_httpschemas_xmlsoap_orgws200303business_processscope', False)
    __scope._DeclarationLocation = pyxb.utils.utility.Location('/tmp/pyxbdist.RHB65sy/PyXB-1.1.5/pyxb/bundles/wssplat/schemas/bpws.xsd', 82, 12)
    __scope._UseLocation = None

    
    scope = property(__scope.value, __scope.set, None, None)

    
    # Element {http://schemas.xmlsoap.org/ws/2003/03/business-process/}variables uses Python identifier variables
    __variables = pyxb.binding.content.ElementUse(pyxb.namespace.ExpandedName(Namespace, u'variables'), 'variables', '__httpschemas_xmlsoap_orgws200303business_process_tProcess_httpschemas_xmlsoap_orgws200303business_processvariables', False)
    __variables._DeclarationLocation = pyxb.utils.utility.Location('/tmp/pyxbdist.RHB65sy/PyXB-1.1.5/pyxb/bundles/wssplat/schemas/bpws.xsd', 36, 20)
    __variables._UseLocation = None

    
    variables = property(__variables.value, __variables.set, None, None)

    
    # Element {http://schemas.xmlsoap.org/ws/2003/03/business-process/}faultHandlers uses Python identifier faultHandlers
    __faultHandlers = pyxb.binding.content.ElementUse(pyxb.namespace.ExpandedName(Namespace, u'faultHandlers'), 'faultHandlers', '__httpschemas_xmlsoap_orgws200303business_process_tProcess_httpschemas_xmlsoap_orgws200303business_processfaultHandlers', False)
    __faultHandlers._DeclarationLocation = pyxb.utils.utility.Location('/tmp/pyxbdist.RHB65sy/PyXB-1.1.5/pyxb/bundles/wssplat/schemas/bpws.xsd', 41, 20)
    __faultHandlers._UseLocation = None

    
    faultHandlers = property(__faultHandlers.value, __faultHandlers.set, None, None)

    
    # Element {http://schemas.xmlsoap.org/ws/2003/03/business-process/}while uses Python identifier while_
    __while = pyxb.binding.content.ElementUse(pyxb.namespace.ExpandedName(Namespace, u'while'), 'while_', '__httpschemas_xmlsoap_orgws200303business_process_tProcess_httpschemas_xmlsoap_orgws200303business_processwhile', False)
    __while._DeclarationLocation = pyxb.utils.utility.Location('/tmp/pyxbdist.RHB65sy/PyXB-1.1.5/pyxb/bundles/wssplat/schemas/bpws.xsd', 79, 12)
    __while._UseLocation = None

    
    while_ = property(__while.value, __while.set, None, None)

    
    # Element {http://schemas.xmlsoap.org/ws/2003/03/business-process/}assign uses Python identifier assign
    __assign = pyxb.binding.content.ElementUse(pyxb.namespace.ExpandedName(Namespace, u'assign'), 'assign', '__httpschemas_xmlsoap_orgws200303business_process_tProcess_httpschemas_xmlsoap_orgws200303business_processassign', False)
    __assign._DeclarationLocation = pyxb.utils.utility.Location('/tmp/pyxbdist.RHB65sy/PyXB-1.1.5/pyxb/bundles/wssplat/schemas/bpws.xsd', 73, 12)
    __assign._UseLocation = None

    
    assign = property(__assign.value, __assign.set, None, None)

    
    # Element {http://schemas.xmlsoap.org/ws/2003/03/business-process/}compensationHandler uses Python identifier compensationHandler
    __compensationHandler = pyxb.binding.content.ElementUse(pyxb.namespace.ExpandedName(Namespace, u'compensationHandler'), 'compensationHandler', '__httpschemas_xmlsoap_orgws200303business_process_tProcess_httpschemas_xmlsoap_orgws200303business_processcompensationHandler', False)
    __compensationHandler._DeclarationLocation = pyxb.utils.utility.Location('/tmp/pyxbdist.RHB65sy/PyXB-1.1.5/pyxb/bundles/wssplat/schemas/bpws.xsd', 43, 20)
    __compensationHandler._UseLocation = None

    
    compensationHandler = property(__compensationHandler.value, __compensationHandler.set, None, None)

    
    # Attribute abstractProcess uses Python identifier abstractProcess
    __abstractProcess = pyxb.binding.content.AttributeUse(pyxb.namespace.ExpandedName(None, u'abstractProcess'), 'abstractProcess', '__httpschemas_xmlsoap_orgws200303business_process_tProcess_abstractProcess', tBoolean, unicode_default=u'no')
    __abstractProcess._DeclarationLocation = pyxb.utils.utility.Location('/tmp/pyxbdist.RHB65sy/PyXB-1.1.5/pyxb/bundles/wssplat/schemas/bpws.xsd', 61, 16)
    __abstractProcess._UseLocation = pyxb.utils.utility.Location('/tmp/pyxbdist.RHB65sy/PyXB-1.1.5/pyxb/bundles/wssplat/schemas/bpws.xsd', 61, 16)
    
    abstractProcess = property(__abstractProcess.value, __abstractProcess.set, None, None)

    
    # Attribute expressionLanguage uses Python identifier expressionLanguage
    __expressionLanguage = pyxb.binding.content.AttributeUse(pyxb.namespace.ExpandedName(None, u'expressionLanguage'), 'expressionLanguage', '__httpschemas_xmlsoap_orgws200303business_process_tProcess_expressionLanguage', pyxb.binding.datatypes.anyURI, unicode_default=u'http://www.w3.org/TR/1999/REC-xpath-19991116')
    __expressionLanguage._DeclarationLocation = pyxb.utils.utility.Location('/tmp/pyxbdist.RHB65sy/PyXB-1.1.5/pyxb/bundles/wssplat/schemas/bpws.xsd', 55, 16)
    __expressionLanguage._UseLocation = pyxb.utils.utility.Location('/tmp/pyxbdist.RHB65sy/PyXB-1.1.5/pyxb/bundles/wssplat/schemas/bpws.xsd', 55, 16)
    
    expressionLanguage = property(__expressionLanguage.value, __expressionLanguage.set, None, None)

    
    # Attribute name uses Python identifier name
    __name = pyxb.binding.content.AttributeUse(pyxb.namespace.ExpandedName(None, u'name'), 'name', '__httpschemas_xmlsoap_orgws200303business_process_tProcess_name', pyxb.binding.datatypes.NCName, required=True)
    __name._DeclarationLocation = pyxb.utils.utility.Location('/tmp/pyxbdist.RHB65sy/PyXB-1.1.5/pyxb/bundles/wssplat/schemas/bpws.xsd', 49, 16)
    __name._UseLocation = pyxb.utils.utility.Location('/tmp/pyxbdist.RHB65sy/PyXB-1.1.5/pyxb/bundles/wssplat/schemas/bpws.xsd', 49, 16)
    
    name = property(__name.value, __name.set, None, None)

    
    # Attribute suppressJoinFailure uses Python identifier suppressJoinFailure
    __suppressJoinFailure = pyxb.binding.content.AttributeUse(pyxb.namespace.ExpandedName(None, u'suppressJoinFailure'), 'suppressJoinFailure', '__httpschemas_xmlsoap_orgws200303business_process_tProcess_suppressJoinFailure', tBoolean, unicode_default=u'no')
    __suppressJoinFailure._DeclarationLocation = pyxb.utils.utility.Location('/tmp/pyxbdist.RHB65sy/PyXB-1.1.5/pyxb/bundles/wssplat/schemas/bpws.xsd', 57, 16)
    __suppressJoinFailure._UseLocation = pyxb.utils.utility.Location('/tmp/pyxbdist.RHB65sy/PyXB-1.1.5/pyxb/bundles/wssplat/schemas/bpws.xsd', 57, 16)
    
    suppressJoinFailure = property(__suppressJoinFailure.value, __suppressJoinFailure.set, None, None)

    
    # Attribute targetNamespace uses Python identifier targetNamespace
    __targetNamespace = pyxb.binding.content.AttributeUse(pyxb.namespace.ExpandedName(None, u'targetNamespace'), 'targetNamespace', '__httpschemas_xmlsoap_orgws200303business_process_tProcess_targetNamespace', pyxb.binding.datatypes.anyURI, required=True)
    __targetNamespace._DeclarationLocation = pyxb.utils.utility.Location('/tmp/pyxbdist.RHB65sy/PyXB-1.1.5/pyxb/bundles/wssplat/schemas/bpws.xsd', 51, 16)
    __targetNamespace._UseLocation = pyxb.utils.utility.Location('/tmp/pyxbdist.RHB65sy/PyXB-1.1.5/pyxb/bundles/wssplat/schemas/bpws.xsd', 51, 16)
    
    targetNamespace = property(__targetNamespace.value, __targetNamespace.set, None, None)

    
    # Attribute enableInstanceCompensation uses Python identifier enableInstanceCompensation
    __enableInstanceCompensation = pyxb.binding.content.AttributeUse(pyxb.namespace.ExpandedName(None, u'enableInstanceCompensation'), 'enableInstanceCompensation', '__httpschemas_xmlsoap_orgws200303business_process_tProcess_enableInstanceCompensation', tBoolean, unicode_default=u'no')
    __enableInstanceCompensation._DeclarationLocation = pyxb.utils.utility.Location('/tmp/pyxbdist.RHB65sy/PyXB-1.1.5/pyxb/bundles/wssplat/schemas/bpws.xsd', 59, 16)
    __enableInstanceCompensation._UseLocation = pyxb.utils.utility.Location('/tmp/pyxbdist.RHB65sy/PyXB-1.1.5/pyxb/bundles/wssplat/schemas/bpws.xsd', 59, 16)
    
    enableInstanceCompensation = property(__enableInstanceCompensation.value, __enableInstanceCompensation.set, None, None)

    
    # Attribute queryLanguage uses Python identifier queryLanguage
    __queryLanguage = pyxb.binding.content.AttributeUse(pyxb.namespace.ExpandedName(None, u'queryLanguage'), 'queryLanguage', '__httpschemas_xmlsoap_orgws200303business_process_tProcess_queryLanguage', pyxb.binding.datatypes.anyURI, unicode_default=u'http://www.w3.org/TR/1999/REC-xpath-19991116')
    __queryLanguage._DeclarationLocation = pyxb.utils.utility.Location('/tmp/pyxbdist.RHB65sy/PyXB-1.1.5/pyxb/bundles/wssplat/schemas/bpws.xsd', 53, 16)
    __queryLanguage._UseLocation = pyxb.utils.utility.Location('/tmp/pyxbdist.RHB65sy/PyXB-1.1.5/pyxb/bundles/wssplat/schemas/bpws.xsd', 53, 16)
    
    queryLanguage = property(__queryLanguage.value, __queryLanguage.set, None, None)

    _AttributeWildcard = pyxb.binding.content.Wildcard(process_contents=pyxb.binding.content.Wildcard.PC_lax, namespace_constraint=(pyxb.binding.content.Wildcard.NC_not, u'http://schemas.xmlsoap.org/ws/2003/03/business-process/'))
    _HasWildcardElement = True

    _ElementMap = tExtensibleElements._ElementMap.copy()
    _ElementMap.update({
        __reply.name() : __reply,
        __partners.name() : __partners,
        __terminate.name() : __terminate,
        __sequence.name() : __sequence,
        __wait.name() : __wait,
        __receive.name() : __receive,
        __partnerLinks.name() : __partnerLinks,
        __eventHandlers.name() : __eventHandlers,
        __flow.name() : __flow,
        __pick.name() : __pick,
        __empty.name() : __empty,
        __invoke.name() : __invoke,
        __correlationSets.name() : __correlationSets,
        __switch.name() : __switch,
        __throw.name() : __throw,
        __scope.name() : __scope,
        __variables.name() : __variables,
        __faultHandlers.name() : __faultHandlers,
        __while.name() : __while,
        __assign.name() : __assign,
        __compensationHandler.name() : __compensationHandler
    })
    _AttributeMap = tExtensibleElements._AttributeMap.copy()
    _AttributeMap.update({
        __abstractProcess.name() : __abstractProcess,
        __expressionLanguage.name() : __expressionLanguage,
        __name.name() : __name,
        __suppressJoinFailure.name() : __suppressJoinFailure,
        __targetNamespace.name() : __targetNamespace,
        __enableInstanceCompensation.name() : __enableInstanceCompensation,
        __queryLanguage.name() : __queryLanguage
    })
Namespace.addCategoryObject('typeBinding', u'tProcess', tProcess)


# Complex type {http://schemas.xmlsoap.org/ws/2003/03/business-process/}tOnAlarm with content type ELEMENT_ONLY
class tOnAlarm (tActivityContainer):
    _TypeDefinition = None
    _ContentTypeTag = pyxb.binding.basis.complexTypeDefinition._CT_ELEMENT_ONLY
    _Abstract = False
    _ExpandedName = pyxb.namespace.ExpandedName(Namespace, u'tOnAlarm')
    _DefinitionLocation = pyxb.utils.utility.Location('/tmp/pyxbdist.RHB65sy/PyXB-1.1.5/pyxb/bundles/wssplat/schemas/bpws.xsd', 219, 4)
    # Base type is tActivityContainer
    
    # Element flow ({http://schemas.xmlsoap.org/ws/2003/03/business-process/}flow) inherited from {http://schemas.xmlsoap.org/ws/2003/03/business-process/}tActivityContainer
    
    # Element reply ({http://schemas.xmlsoap.org/ws/2003/03/business-process/}reply) inherited from {http://schemas.xmlsoap.org/ws/2003/03/business-process/}tActivityContainer
    
    # Element pick ({http://schemas.xmlsoap.org/ws/2003/03/business-process/}pick) inherited from {http://schemas.xmlsoap.org/ws/2003/03/business-process/}tActivityContainer
    
    # Element empty ({http://schemas.xmlsoap.org/ws/2003/03/business-process/}empty) inherited from {http://schemas.xmlsoap.org/ws/2003/03/business-process/}tActivityContainer
    
    # Element invoke ({http://schemas.xmlsoap.org/ws/2003/03/business-process/}invoke) inherited from {http://schemas.xmlsoap.org/ws/2003/03/business-process/}tActivityContainer
    
    # Element switch ({http://schemas.xmlsoap.org/ws/2003/03/business-process/}switch) inherited from {http://schemas.xmlsoap.org/ws/2003/03/business-process/}tActivityContainer
    
    # Element assign ({http://schemas.xmlsoap.org/ws/2003/03/business-process/}assign) inherited from {http://schemas.xmlsoap.org/ws/2003/03/business-process/}tActivityContainer
    
    # Element terminate ({http://schemas.xmlsoap.org/ws/2003/03/business-process/}terminate) inherited from {http://schemas.xmlsoap.org/ws/2003/03/business-process/}tActivityContainer
    
    # Element throw ({http://schemas.xmlsoap.org/ws/2003/03/business-process/}throw) inherited from {http://schemas.xmlsoap.org/ws/2003/03/business-process/}tActivityContainer
    
    # Element while_ ({http://schemas.xmlsoap.org/ws/2003/03/business-process/}while) inherited from {http://schemas.xmlsoap.org/ws/2003/03/business-process/}tActivityContainer
    
    # Element receive ({http://schemas.xmlsoap.org/ws/2003/03/business-process/}receive) inherited from {http://schemas.xmlsoap.org/ws/2003/03/business-process/}tActivityContainer
    
    # Element scope ({http://schemas.xmlsoap.org/ws/2003/03/business-process/}scope) inherited from {http://schemas.xmlsoap.org/ws/2003/03/business-process/}tActivityContainer
    
    # Element wait ({http://schemas.xmlsoap.org/ws/2003/03/business-process/}wait) inherited from {http://schemas.xmlsoap.org/ws/2003/03/business-process/}tActivityContainer
    
    # Element sequence ({http://schemas.xmlsoap.org/ws/2003/03/business-process/}sequence) inherited from {http://schemas.xmlsoap.org/ws/2003/03/business-process/}tActivityContainer
    
    # Attribute until uses Python identifier until
    __until = pyxb.binding.content.AttributeUse(pyxb.namespace.ExpandedName(None, u'until'), 'until', '__httpschemas_xmlsoap_orgws200303business_process_tOnAlarm_until', tDeadline_expr)
    __until._DeclarationLocation = pyxb.utils.utility.Location('/tmp/pyxbdist.RHB65sy/PyXB-1.1.5/pyxb/bundles/wssplat/schemas/bpws.xsd', 223, 16)
    __until._UseLocation = pyxb.utils.utility.Location('/tmp/pyxbdist.RHB65sy/PyXB-1.1.5/pyxb/bundles/wssplat/schemas/bpws.xsd', 223, 16)
    
    until = property(__until.value, __until.set, None, None)

    
    # Attribute for uses Python identifier for_
    __for = pyxb.binding.content.AttributeUse(pyxb.namespace.ExpandedName(None, u'for'), 'for_', '__httpschemas_xmlsoap_orgws200303business_process_tOnAlarm_for', tDuration_expr)
    __for._DeclarationLocation = pyxb.utils.utility.Location('/tmp/pyxbdist.RHB65sy/PyXB-1.1.5/pyxb/bundles/wssplat/schemas/bpws.xsd', 222, 16)
    __for._UseLocation = pyxb.utils.utility.Location('/tmp/pyxbdist.RHB65sy/PyXB-1.1.5/pyxb/bundles/wssplat/schemas/bpws.xsd', 222, 16)
    
    for_ = property(__for.value, __for.set, None, None)

    _AttributeWildcard = pyxb.binding.content.Wildcard(process_contents=pyxb.binding.content.Wildcard.PC_lax, namespace_constraint=(pyxb.binding.content.Wildcard.NC_not, u'http://schemas.xmlsoap.org/ws/2003/03/business-process/'))
    _HasWildcardElement = True

    _ElementMap = tActivityContainer._ElementMap.copy()
    _ElementMap.update({
        
    })
    _AttributeMap = tActivityContainer._AttributeMap.copy()
    _AttributeMap.update({
        __until.name() : __until,
        __for.name() : __for
    })
Namespace.addCategoryObject('typeBinding', u'tOnAlarm', tOnAlarm)


# Complex type {http://schemas.xmlsoap.org/ws/2003/03/business-process/}tCorrelations with content type ELEMENT_ONLY
class tCorrelations (tExtensibleElements):
    _TypeDefinition = None
    _ContentTypeTag = pyxb.binding.basis.complexTypeDefinition._CT_ELEMENT_ONLY
    _Abstract = False
    _ExpandedName = pyxb.namespace.ExpandedName(Namespace, u'tCorrelations')
    _DefinitionLocation = pyxb.utils.utility.Location('/tmp/pyxbdist.RHB65sy/PyXB-1.1.5/pyxb/bundles/wssplat/schemas/bpws.xsd', 331, 4)
    # Base type is tExtensibleElements
    
    # Element {http://schemas.xmlsoap.org/ws/2003/03/business-process/}correlation uses Python identifier correlation
    __correlation = pyxb.binding.content.ElementUse(pyxb.namespace.ExpandedName(Namespace, u'correlation'), 'correlation', '__httpschemas_xmlsoap_orgws200303business_process_tCorrelations_httpschemas_xmlsoap_orgws200303business_processcorrelation', True)
    __correlation._DeclarationLocation = pyxb.utils.utility.Location('/tmp/pyxbdist.RHB65sy/PyXB-1.1.5/pyxb/bundles/wssplat/schemas/bpws.xsd', 335, 18)
    __correlation._UseLocation = None

    
    correlation = property(__correlation.value, __correlation.set, None, None)

    _AttributeWildcard = pyxb.binding.content.Wildcard(process_contents=pyxb.binding.content.Wildcard.PC_lax, namespace_constraint=(pyxb.binding.content.Wildcard.NC_not, u'http://schemas.xmlsoap.org/ws/2003/03/business-process/'))
    _HasWildcardElement = True

    _ElementMap = tExtensibleElements._ElementMap.copy()
    _ElementMap.update({
        __correlation.name() : __correlation
    })
    _AttributeMap = tExtensibleElements._AttributeMap.copy()
    _AttributeMap.update({
        
    })
Namespace.addCategoryObject('typeBinding', u'tCorrelations', tCorrelations)


# Complex type {http://schemas.xmlsoap.org/ws/2003/03/business-process/}tCorrelation with content type ELEMENT_ONLY
class tCorrelation (tExtensibleElements):
    _TypeDefinition = None
    _ContentTypeTag = pyxb.binding.basis.complexTypeDefinition._CT_ELEMENT_ONLY
    _Abstract = False
    _ExpandedName = pyxb.namespace.ExpandedName(Namespace, u'tCorrelation')
    _DefinitionLocation = pyxb.utils.utility.Location('/tmp/pyxbdist.RHB65sy/PyXB-1.1.5/pyxb/bundles/wssplat/schemas/bpws.xsd', 342, 3)
    # Base type is tExtensibleElements
    
    # Attribute initiate uses Python identifier initiate
    __initiate = pyxb.binding.content.AttributeUse(pyxb.namespace.ExpandedName(None, u'initiate'), 'initiate', '__httpschemas_xmlsoap_orgws200303business_process_tCorrelation_initiate', tBoolean, unicode_default=u'no')
    __initiate._DeclarationLocation = pyxb.utils.utility.Location('/tmp/pyxbdist.RHB65sy/PyXB-1.1.5/pyxb/bundles/wssplat/schemas/bpws.xsd', 346, 16)
    __initiate._UseLocation = pyxb.utils.utility.Location('/tmp/pyxbdist.RHB65sy/PyXB-1.1.5/pyxb/bundles/wssplat/schemas/bpws.xsd', 346, 16)
    
    initiate = property(__initiate.value, __initiate.set, None, None)

    
    # Attribute set uses Python identifier set
    __set = pyxb.binding.content.AttributeUse(pyxb.namespace.ExpandedName(None, u'set'), 'set', '__httpschemas_xmlsoap_orgws200303business_process_tCorrelation_set', pyxb.binding.datatypes.NCName, required=True)
    __set._DeclarationLocation = pyxb.utils.utility.Location('/tmp/pyxbdist.RHB65sy/PyXB-1.1.5/pyxb/bundles/wssplat/schemas/bpws.xsd', 345, 16)
    __set._UseLocation = pyxb.utils.utility.Location('/tmp/pyxbdist.RHB65sy/PyXB-1.1.5/pyxb/bundles/wssplat/schemas/bpws.xsd', 345, 16)
    
    set = property(__set.value, __set.set, None, None)

    _AttributeWildcard = pyxb.binding.content.Wildcard(process_contents=pyxb.binding.content.Wildcard.PC_lax, namespace_constraint=(pyxb.binding.content.Wildcard.NC_not, u'http://schemas.xmlsoap.org/ws/2003/03/business-process/'))
    _HasWildcardElement = True

    _ElementMap = tExtensibleElements._ElementMap.copy()
    _ElementMap.update({
        
    })
    _AttributeMap = tExtensibleElements._AttributeMap.copy()
    _AttributeMap.update({
        __initiate.name() : __initiate,
        __set.name() : __set
    })
Namespace.addCategoryObject('typeBinding', u'tCorrelation', tCorrelation)


# Complex type {http://schemas.xmlsoap.org/ws/2003/03/business-process/}tCorrelationWithPattern with content type ELEMENT_ONLY
class tCorrelationWithPattern (tCorrelation):
    _TypeDefinition = None
    _ContentTypeTag = pyxb.binding.basis.complexTypeDefinition._CT_ELEMENT_ONLY
    _Abstract = False
    _ExpandedName = pyxb.namespace.ExpandedName(Namespace, u'tCorrelationWithPattern')
    _DefinitionLocation = pyxb.utils.utility.Location('/tmp/pyxbdist.RHB65sy/PyXB-1.1.5/pyxb/bundles/wssplat/schemas/bpws.xsd', 366, 4)
    # Base type is tCorrelation
    
    # Attribute initiate inherited from {http://schemas.xmlsoap.org/ws/2003/03/business-process/}tCorrelation
    
    # Attribute pattern uses Python identifier pattern
    __pattern = pyxb.binding.content.AttributeUse(pyxb.namespace.ExpandedName(None, u'pattern'), 'pattern', '__httpschemas_xmlsoap_orgws200303business_process_tCorrelationWithPattern_pattern', STD_ANON)
    __pattern._DeclarationLocation = pyxb.utils.utility.Location('/tmp/pyxbdist.RHB65sy/PyXB-1.1.5/pyxb/bundles/wssplat/schemas/bpws.xsd', 369, 16)
    __pattern._UseLocation = pyxb.utils.utility.Location('/tmp/pyxbdist.RHB65sy/PyXB-1.1.5/pyxb/bundles/wssplat/schemas/bpws.xsd', 369, 16)
    
    pattern = property(__pattern.value, __pattern.set, None, None)

    
    # Attribute set inherited from {http://schemas.xmlsoap.org/ws/2003/03/business-process/}tCorrelation
    _AttributeWildcard = pyxb.binding.content.Wildcard(process_contents=pyxb.binding.content.Wildcard.PC_lax, namespace_constraint=(pyxb.binding.content.Wildcard.NC_not, u'http://schemas.xmlsoap.org/ws/2003/03/business-process/'))
    _HasWildcardElement = True

    _ElementMap = tCorrelation._ElementMap.copy()
    _ElementMap.update({
        
    })
    _AttributeMap = tCorrelation._AttributeMap.copy()
    _AttributeMap.update({
        __pattern.name() : __pattern
    })
Namespace.addCategoryObject('typeBinding', u'tCorrelationWithPattern', tCorrelationWithPattern)


# Complex type {http://schemas.xmlsoap.org/ws/2003/03/business-process/}tPartnerLinks with content type ELEMENT_ONLY
class tPartnerLinks (tExtensibleElements):
    _TypeDefinition = None
    _ContentTypeTag = pyxb.binding.basis.complexTypeDefinition._CT_ELEMENT_ONLY
    _Abstract = False
    _ExpandedName = pyxb.namespace.ExpandedName(Namespace, u'tPartnerLinks')
    _DefinitionLocation = pyxb.utils.utility.Location('/tmp/pyxbdist.RHB65sy/PyXB-1.1.5/pyxb/bundles/wssplat/schemas/bpws.xsd', 87, 4)
    # Base type is tExtensibleElements
    
    # Element {http://schemas.xmlsoap.org/ws/2003/03/business-process/}partnerLink uses Python identifier partnerLink
    __partnerLink = pyxb.binding.content.ElementUse(pyxb.namespace.ExpandedName(Namespace, u'partnerLink'), 'partnerLink', '__httpschemas_xmlsoap_orgws200303business_process_tPartnerLinks_httpschemas_xmlsoap_orgws200303business_processpartnerLink', True)
    __partnerLink._DeclarationLocation = pyxb.utils.utility.Location('/tmp/pyxbdist.RHB65sy/PyXB-1.1.5/pyxb/bundles/wssplat/schemas/bpws.xsd', 91, 20)
    __partnerLink._UseLocation = None

    
    partnerLink = property(__partnerLink.value, __partnerLink.set, None, None)

    _AttributeWildcard = pyxb.binding.content.Wildcard(process_contents=pyxb.binding.content.Wildcard.PC_lax, namespace_constraint=(pyxb.binding.content.Wildcard.NC_not, u'http://schemas.xmlsoap.org/ws/2003/03/business-process/'))
    _HasWildcardElement = True

    _ElementMap = tExtensibleElements._ElementMap.copy()
    _ElementMap.update({
        __partnerLink.name() : __partnerLink
    })
    _AttributeMap = tExtensibleElements._AttributeMap.copy()
    _AttributeMap.update({
        
    })
Namespace.addCategoryObject('typeBinding', u'tPartnerLinks', tPartnerLinks)


# Complex type {http://schemas.xmlsoap.org/ws/2003/03/business-process/}tVariable with content type EMPTY
class tVariable (pyxb.binding.basis.complexTypeDefinition):
    _TypeDefinition = None
    _ContentTypeTag = pyxb.binding.basis.complexTypeDefinition._CT_EMPTY
    _Abstract = False
    _ExpandedName = pyxb.namespace.ExpandedName(Namespace, u'tVariable')
    _DefinitionLocation = pyxb.utils.utility.Location('/tmp/pyxbdist.RHB65sy/PyXB-1.1.5/pyxb/bundles/wssplat/schemas/bpws.xsd', 247, 4)
    # Base type is pyxb.binding.datatypes.anyType
    
    # Attribute element uses Python identifier element
    __element = pyxb.binding.content.AttributeUse(pyxb.namespace.ExpandedName(None, u'element'), 'element', '__httpschemas_xmlsoap_orgws200303business_process_tVariable_element', pyxb.binding.datatypes.QName)
    __element._DeclarationLocation = pyxb.utils.utility.Location('/tmp/pyxbdist.RHB65sy/PyXB-1.1.5/pyxb/bundles/wssplat/schemas/bpws.xsd', 254, 16)
    __element._UseLocation = pyxb.utils.utility.Location('/tmp/pyxbdist.RHB65sy/PyXB-1.1.5/pyxb/bundles/wssplat/schemas/bpws.xsd', 254, 16)
    
    element = property(__element.value, __element.set, None, None)

    
    # Attribute type uses Python identifier type
    __type = pyxb.binding.content.AttributeUse(pyxb.namespace.ExpandedName(None, u'type'), 'type', '__httpschemas_xmlsoap_orgws200303business_process_tVariable_type', pyxb.binding.datatypes.QName)
    __type._DeclarationLocation = pyxb.utils.utility.Location('/tmp/pyxbdist.RHB65sy/PyXB-1.1.5/pyxb/bundles/wssplat/schemas/bpws.xsd', 253, 16)
    __type._UseLocation = pyxb.utils.utility.Location('/tmp/pyxbdist.RHB65sy/PyXB-1.1.5/pyxb/bundles/wssplat/schemas/bpws.xsd', 253, 16)
    
    type = property(__type.value, __type.set, None, None)

    
    # Attribute messageType uses Python identifier messageType
    __messageType = pyxb.binding.content.AttributeUse(pyxb.namespace.ExpandedName(None, u'messageType'), 'messageType', '__httpschemas_xmlsoap_orgws200303business_process_tVariable_messageType', pyxb.binding.datatypes.QName)
    __messageType._DeclarationLocation = pyxb.utils.utility.Location('/tmp/pyxbdist.RHB65sy/PyXB-1.1.5/pyxb/bundles/wssplat/schemas/bpws.xsd', 252, 16)
    __messageType._UseLocation = pyxb.utils.utility.Location('/tmp/pyxbdist.RHB65sy/PyXB-1.1.5/pyxb/bundles/wssplat/schemas/bpws.xsd', 252, 16)
    
    messageType = property(__messageType.value, __messageType.set, None, None)

    
    # Attribute name uses Python identifier name
    __name = pyxb.binding.content.AttributeUse(pyxb.namespace.ExpandedName(None, u'name'), 'name', '__httpschemas_xmlsoap_orgws200303business_process_tVariable_name', pyxb.binding.datatypes.NCName, required=True)
    __name._DeclarationLocation = pyxb.utils.utility.Location('/tmp/pyxbdist.RHB65sy/PyXB-1.1.5/pyxb/bundles/wssplat/schemas/bpws.xsd', 251, 16)
    __name._UseLocation = pyxb.utils.utility.Location('/tmp/pyxbdist.RHB65sy/PyXB-1.1.5/pyxb/bundles/wssplat/schemas/bpws.xsd', 251, 16)
    
    name = property(__name.value, __name.set, None, None)

    _AttributeWildcard = pyxb.binding.content.Wildcard(process_contents=pyxb.binding.content.Wildcard.PC_lax, namespace_constraint=(pyxb.binding.content.Wildcard.NC_not, u'http://schemas.xmlsoap.org/ws/2003/03/business-process/'))

    _ElementMap = {
        
    }
    _AttributeMap = {
        __element.name() : __element,
        __type.name() : __type,
        __messageType.name() : __messageType,
        __name.name() : __name
    }
Namespace.addCategoryObject('typeBinding', u'tVariable', tVariable)


# Complex type {http://schemas.xmlsoap.org/ws/2003/03/business-process/}tPartner with content type ELEMENT_ONLY
class tPartner (tExtensibleElements):
    _TypeDefinition = None
    _ContentTypeTag = pyxb.binding.basis.complexTypeDefinition._CT_ELEMENT_ONLY
    _Abstract = False
    _ExpandedName = pyxb.namespace.ExpandedName(Namespace, u'tPartner')
    _DefinitionLocation = pyxb.utils.utility.Location('/tmp/pyxbdist.RHB65sy/PyXB-1.1.5/pyxb/bundles/wssplat/schemas/bpws.xsd', 122, 4)
    # Base type is tExtensibleElements
    
    # Element {http://schemas.xmlsoap.org/ws/2003/03/business-process/}partnerLink uses Python identifier partnerLink
    __partnerLink = pyxb.binding.content.ElementUse(pyxb.namespace.ExpandedName(Namespace, u'partnerLink'), 'partnerLink', '__httpschemas_xmlsoap_orgws200303business_process_tPartner_httpschemas_xmlsoap_orgws200303business_processpartnerLink', True)
    __partnerLink._DeclarationLocation = pyxb.utils.utility.Location('/tmp/pyxbdist.RHB65sy/PyXB-1.1.5/pyxb/bundles/wssplat/schemas/bpws.xsd', 126, 18)
    __partnerLink._UseLocation = None

    
    partnerLink = property(__partnerLink.value, __partnerLink.set, None, None)

    
    # Attribute name uses Python identifier name
    __name = pyxb.binding.content.AttributeUse(pyxb.namespace.ExpandedName(None, u'name'), 'name', '__httpschemas_xmlsoap_orgws200303business_process_tPartner_name', pyxb.binding.datatypes.NCName, required=True)
    __name._DeclarationLocation = pyxb.utils.utility.Location('/tmp/pyxbdist.RHB65sy/PyXB-1.1.5/pyxb/bundles/wssplat/schemas/bpws.xsd', 138, 15)
    __name._UseLocation = pyxb.utils.utility.Location('/tmp/pyxbdist.RHB65sy/PyXB-1.1.5/pyxb/bundles/wssplat/schemas/bpws.xsd', 138, 15)
    
    name = property(__name.value, __name.set, None, None)

    _AttributeWildcard = pyxb.binding.content.Wildcard(process_contents=pyxb.binding.content.Wildcard.PC_lax, namespace_constraint=(pyxb.binding.content.Wildcard.NC_not, u'http://schemas.xmlsoap.org/ws/2003/03/business-process/'))
    _HasWildcardElement = True

    _ElementMap = tExtensibleElements._ElementMap.copy()
    _ElementMap.update({
        __partnerLink.name() : __partnerLink
    })
    _AttributeMap = tExtensibleElements._AttributeMap.copy()
    _AttributeMap.update({
        __name.name() : __name
    })
Namespace.addCategoryObject('typeBinding', u'tPartner', tPartner)


# Complex type {http://schemas.xmlsoap.org/ws/2003/03/business-process/}tPartners with content type ELEMENT_ONLY
class tPartners (tExtensibleElements):
    _TypeDefinition = None
    _ContentTypeTag = pyxb.binding.basis.complexTypeDefinition._CT_ELEMENT_ONLY
    _Abstract = False
    _ExpandedName = pyxb.namespace.ExpandedName(Namespace, u'tPartners')
    _DefinitionLocation = pyxb.utils.utility.Location('/tmp/pyxbdist.RHB65sy/PyXB-1.1.5/pyxb/bundles/wssplat/schemas/bpws.xsd', 111, 4)
    # Base type is tExtensibleElements
    
    # Element {http://schemas.xmlsoap.org/ws/2003/03/business-process/}partner uses Python identifier partner
    __partner = pyxb.binding.content.ElementUse(pyxb.namespace.ExpandedName(Namespace, u'partner'), 'partner', '__httpschemas_xmlsoap_orgws200303business_process_tPartners_httpschemas_xmlsoap_orgws200303business_processpartner', True)
    __partner._DeclarationLocation = pyxb.utils.utility.Location('/tmp/pyxbdist.RHB65sy/PyXB-1.1.5/pyxb/bundles/wssplat/schemas/bpws.xsd', 115, 20)
    __partner._UseLocation = None

    
    partner = property(__partner.value, __partner.set, None, None)

    _AttributeWildcard = pyxb.binding.content.Wildcard(process_contents=pyxb.binding.content.Wildcard.PC_lax, namespace_constraint=(pyxb.binding.content.Wildcard.NC_not, u'http://schemas.xmlsoap.org/ws/2003/03/business-process/'))
    _HasWildcardElement = True

    _ElementMap = tExtensibleElements._ElementMap.copy()
    _ElementMap.update({
        __partner.name() : __partner
    })
    _AttributeMap = tExtensibleElements._AttributeMap.copy()
    _AttributeMap.update({
        
    })
Namespace.addCategoryObject('typeBinding', u'tPartners', tPartners)


# Complex type {http://schemas.xmlsoap.org/ws/2003/03/business-process/}tCorrelationSet with content type ELEMENT_ONLY
class tCorrelationSet (tExtensibleElements):
    _TypeDefinition = None
    _ContentTypeTag = pyxb.binding.basis.complexTypeDefinition._CT_ELEMENT_ONLY
    _Abstract = False
    _ExpandedName = pyxb.namespace.ExpandedName(Namespace, u'tCorrelationSet')
    _DefinitionLocation = pyxb.utils.utility.Location('/tmp/pyxbdist.RHB65sy/PyXB-1.1.5/pyxb/bundles/wssplat/schemas/bpws.xsd', 272, 4)
    # Base type is tExtensibleElements
    
    # Attribute name uses Python identifier name
    __name = pyxb.binding.content.AttributeUse(pyxb.namespace.ExpandedName(None, u'name'), 'name', '__httpschemas_xmlsoap_orgws200303business_process_tCorrelationSet_name', pyxb.binding.datatypes.NCName, required=True)
    __name._DeclarationLocation = pyxb.utils.utility.Location('/tmp/pyxbdist.RHB65sy/PyXB-1.1.5/pyxb/bundles/wssplat/schemas/bpws.xsd', 280, 16)
    __name._UseLocation = pyxb.utils.utility.Location('/tmp/pyxbdist.RHB65sy/PyXB-1.1.5/pyxb/bundles/wssplat/schemas/bpws.xsd', 280, 16)
    
    name = property(__name.value, __name.set, None, None)

    
    # Attribute properties uses Python identifier properties
    __properties = pyxb.binding.content.AttributeUse(pyxb.namespace.ExpandedName(None, u'properties'), 'properties', '__httpschemas_xmlsoap_orgws200303business_process_tCorrelationSet_properties', STD_ANON_, required=True)
    __properties._DeclarationLocation = pyxb.utils.utility.Location('/tmp/pyxbdist.RHB65sy/PyXB-1.1.5/pyxb/bundles/wssplat/schemas/bpws.xsd', 275, 16)
    __properties._UseLocation = pyxb.utils.utility.Location('/tmp/pyxbdist.RHB65sy/PyXB-1.1.5/pyxb/bundles/wssplat/schemas/bpws.xsd', 275, 16)
    
    properties = property(__properties.value, __properties.set, None, None)

    _AttributeWildcard = pyxb.binding.content.Wildcard(process_contents=pyxb.binding.content.Wildcard.PC_lax, namespace_constraint=(pyxb.binding.content.Wildcard.NC_not, u'http://schemas.xmlsoap.org/ws/2003/03/business-process/'))
    _HasWildcardElement = True

    _ElementMap = tExtensibleElements._ElementMap.copy()
    _ElementMap.update({
        
    })
    _AttributeMap = tExtensibleElements._AttributeMap.copy()
    _AttributeMap.update({
        __name.name() : __name,
        __properties.name() : __properties
    })
Namespace.addCategoryObject('typeBinding', u'tCorrelationSet', tCorrelationSet)


# Complex type {http://schemas.xmlsoap.org/ws/2003/03/business-process/}tSource with content type ELEMENT_ONLY
class tSource (tExtensibleElements):
    _TypeDefinition = None
    _ContentTypeTag = pyxb.binding.basis.complexTypeDefinition._CT_ELEMENT_ONLY
    _Abstract = False
    _ExpandedName = pyxb.namespace.ExpandedName(Namespace, u'tSource')
    _DefinitionLocation = pyxb.utils.utility.Location('/tmp/pyxbdist.RHB65sy/PyXB-1.1.5/pyxb/bundles/wssplat/schemas/bpws.xsd', 305, 4)
    # Base type is tExtensibleElements
    
    # Attribute linkName uses Python identifier linkName
    __linkName = pyxb.binding.content.AttributeUse(pyxb.namespace.ExpandedName(None, u'linkName'), 'linkName', '__httpschemas_xmlsoap_orgws200303business_process_tSource_linkName', pyxb.binding.datatypes.NCName, required=True)
    __linkName._DeclarationLocation = pyxb.utils.utility.Location('/tmp/pyxbdist.RHB65sy/PyXB-1.1.5/pyxb/bundles/wssplat/schemas/bpws.xsd', 308, 16)
    __linkName._UseLocation = pyxb.utils.utility.Location('/tmp/pyxbdist.RHB65sy/PyXB-1.1.5/pyxb/bundles/wssplat/schemas/bpws.xsd', 308, 16)
    
    linkName = property(__linkName.value, __linkName.set, None, None)

    
    # Attribute transitionCondition uses Python identifier transitionCondition
    __transitionCondition = pyxb.binding.content.AttributeUse(pyxb.namespace.ExpandedName(None, u'transitionCondition'), 'transitionCondition', '__httpschemas_xmlsoap_orgws200303business_process_tSource_transitionCondition', tBoolean_expr)
    __transitionCondition._DeclarationLocation = pyxb.utils.utility.Location('/tmp/pyxbdist.RHB65sy/PyXB-1.1.5/pyxb/bundles/wssplat/schemas/bpws.xsd', 309, 16)
    __transitionCondition._UseLocation = pyxb.utils.utility.Location('/tmp/pyxbdist.RHB65sy/PyXB-1.1.5/pyxb/bundles/wssplat/schemas/bpws.xsd', 309, 16)
    
    transitionCondition = property(__transitionCondition.value, __transitionCondition.set, None, None)

    _AttributeWildcard = pyxb.binding.content.Wildcard(process_contents=pyxb.binding.content.Wildcard.PC_lax, namespace_constraint=(pyxb.binding.content.Wildcard.NC_not, u'http://schemas.xmlsoap.org/ws/2003/03/business-process/'))
    _HasWildcardElement = True

    _ElementMap = tExtensibleElements._ElementMap.copy()
    _ElementMap.update({
        
    })
    _AttributeMap = tExtensibleElements._AttributeMap.copy()
    _AttributeMap.update({
        __linkName.name() : __linkName,
        __transitionCondition.name() : __transitionCondition
    })
Namespace.addCategoryObject('typeBinding', u'tSource', tSource)


# Complex type {http://schemas.xmlsoap.org/ws/2003/03/business-process/}tLink with content type ELEMENT_ONLY
class tLink (tExtensibleElements):
    _TypeDefinition = None
    _ContentTypeTag = pyxb.binding.basis.complexTypeDefinition._CT_ELEMENT_ONLY
    _Abstract = False
    _ExpandedName = pyxb.namespace.ExpandedName(Namespace, u'tLink')
    _DefinitionLocation = pyxb.utils.utility.Location('/tmp/pyxbdist.RHB65sy/PyXB-1.1.5/pyxb/bundles/wssplat/schemas/bpws.xsd', 555, 4)
    # Base type is tExtensibleElements
    
    # Attribute name uses Python identifier name
    __name = pyxb.binding.content.AttributeUse(pyxb.namespace.ExpandedName(None, u'name'), 'name', '__httpschemas_xmlsoap_orgws200303business_process_tLink_name', pyxb.binding.datatypes.NCName, required=True)
    __name._DeclarationLocation = pyxb.utils.utility.Location('/tmp/pyxbdist.RHB65sy/PyXB-1.1.5/pyxb/bundles/wssplat/schemas/bpws.xsd', 558, 16)
    __name._UseLocation = pyxb.utils.utility.Location('/tmp/pyxbdist.RHB65sy/PyXB-1.1.5/pyxb/bundles/wssplat/schemas/bpws.xsd', 558, 16)
    
    name = property(__name.value, __name.set, None, None)

    _AttributeWildcard = pyxb.binding.content.Wildcard(process_contents=pyxb.binding.content.Wildcard.PC_lax, namespace_constraint=(pyxb.binding.content.Wildcard.NC_not, u'http://schemas.xmlsoap.org/ws/2003/03/business-process/'))
    _HasWildcardElement = True

    _ElementMap = tExtensibleElements._ElementMap.copy()
    _ElementMap.update({
        
    })
    _AttributeMap = tExtensibleElements._AttributeMap.copy()
    _AttributeMap.update({
        __name.name() : __name
    })
Namespace.addCategoryObject('typeBinding', u'tLink', tLink)


# Complex type {http://schemas.xmlsoap.org/ws/2003/03/business-process/}tPartnerLink with content type ELEMENT_ONLY
class tPartnerLink (tExtensibleElements):
    _TypeDefinition = None
    _ContentTypeTag = pyxb.binding.basis.complexTypeDefinition._CT_ELEMENT_ONLY
    _Abstract = False
    _ExpandedName = pyxb.namespace.ExpandedName(Namespace, u'tPartnerLink')
    _DefinitionLocation = pyxb.utils.utility.Location('/tmp/pyxbdist.RHB65sy/PyXB-1.1.5/pyxb/bundles/wssplat/schemas/bpws.xsd', 98, 4)
    # Base type is tExtensibleElements
    
    # Attribute myRole uses Python identifier myRole
    __myRole = pyxb.binding.content.AttributeUse(pyxb.namespace.ExpandedName(None, u'myRole'), 'myRole', '__httpschemas_xmlsoap_orgws200303business_process_tPartnerLink_myRole', pyxb.binding.datatypes.NCName)
    __myRole._DeclarationLocation = pyxb.utils.utility.Location('/tmp/pyxbdist.RHB65sy/PyXB-1.1.5/pyxb/bundles/wssplat/schemas/bpws.xsd', 104, 16)
    __myRole._UseLocation = pyxb.utils.utility.Location('/tmp/pyxbdist.RHB65sy/PyXB-1.1.5/pyxb/bundles/wssplat/schemas/bpws.xsd', 104, 16)
    
    myRole = property(__myRole.value, __myRole.set, None, None)

    
    # Attribute name uses Python identifier name
    __name = pyxb.binding.content.AttributeUse(pyxb.namespace.ExpandedName(None, u'name'), 'name', '__httpschemas_xmlsoap_orgws200303business_process_tPartnerLink_name', pyxb.binding.datatypes.NCName, required=True)
    __name._DeclarationLocation = pyxb.utils.utility.Location('/tmp/pyxbdist.RHB65sy/PyXB-1.1.5/pyxb/bundles/wssplat/schemas/bpws.xsd', 101, 16)
    __name._UseLocation = pyxb.utils.utility.Location('/tmp/pyxbdist.RHB65sy/PyXB-1.1.5/pyxb/bundles/wssplat/schemas/bpws.xsd', 101, 16)
    
    name = property(__name.value, __name.set, None, None)

    
    # Attribute partnerRole uses Python identifier partnerRole
    __partnerRole = pyxb.binding.content.AttributeUse(pyxb.namespace.ExpandedName(None, u'partnerRole'), 'partnerRole', '__httpschemas_xmlsoap_orgws200303business_process_tPartnerLink_partnerRole', pyxb.binding.datatypes.NCName)
    __partnerRole._DeclarationLocation = pyxb.utils.utility.Location('/tmp/pyxbdist.RHB65sy/PyXB-1.1.5/pyxb/bundles/wssplat/schemas/bpws.xsd', 105, 16)
    __partnerRole._UseLocation = pyxb.utils.utility.Location('/tmp/pyxbdist.RHB65sy/PyXB-1.1.5/pyxb/bundles/wssplat/schemas/bpws.xsd', 105, 16)
    
    partnerRole = property(__partnerRole.value, __partnerRole.set, None, None)

    
    # Attribute partnerLinkType uses Python identifier partnerLinkType
    __partnerLinkType = pyxb.binding.content.AttributeUse(pyxb.namespace.ExpandedName(None, u'partnerLinkType'), 'partnerLinkType', '__httpschemas_xmlsoap_orgws200303business_process_tPartnerLink_partnerLinkType', pyxb.binding.datatypes.QName, required=True)
    __partnerLinkType._DeclarationLocation = pyxb.utils.utility.Location('/tmp/pyxbdist.RHB65sy/PyXB-1.1.5/pyxb/bundles/wssplat/schemas/bpws.xsd', 102, 16)
    __partnerLinkType._UseLocation = pyxb.utils.utility.Location('/tmp/pyxbdist.RHB65sy/PyXB-1.1.5/pyxb/bundles/wssplat/schemas/bpws.xsd', 102, 16)
    
    partnerLinkType = property(__partnerLinkType.value, __partnerLinkType.set, None, None)

    _AttributeWildcard = pyxb.binding.content.Wildcard(process_contents=pyxb.binding.content.Wildcard.PC_lax, namespace_constraint=(pyxb.binding.content.Wildcard.NC_not, u'http://schemas.xmlsoap.org/ws/2003/03/business-process/'))
    _HasWildcardElement = True

    _ElementMap = tExtensibleElements._ElementMap.copy()
    _ElementMap.update({
        
    })
    _AttributeMap = tExtensibleElements._AttributeMap.copy()
    _AttributeMap.update({
        __myRole.name() : __myRole,
        __name.name() : __name,
        __partnerRole.name() : __partnerRole,
        __partnerLinkType.name() : __partnerLinkType
    })
Namespace.addCategoryObject('typeBinding', u'tPartnerLink', tPartnerLink)


to = pyxb.binding.basis.element(pyxb.namespace.ExpandedName(Namespace, u'to'), CTD_ANON_2)
Namespace.addCategoryObject('elementBinding', to.name().localName(), to)

process = pyxb.binding.basis.element(pyxb.namespace.ExpandedName(Namespace, u'process'), tProcess)
Namespace.addCategoryObject('elementBinding', process.name().localName(), process)

from_ = pyxb.binding.basis.element(pyxb.namespace.ExpandedName(Namespace, u'from'), tFrom)
Namespace.addCategoryObject('elementBinding', from_.name().localName(), from_)


tExtensibleElements._GroupModel = pyxb.binding.content.GroupSequence(
    pyxb.binding.content.ParticleModel(pyxb.binding.content.Wildcard(process_contents=pyxb.binding.content.Wildcard.PC_lax, namespace_constraint=(pyxb.binding.content.Wildcard.NC_not, u'http://schemas.xmlsoap.org/ws/2003/03/business-process/')), min_occurs=0L, max_occurs=None)
    )
tExtensibleElements._ContentModel = pyxb.binding.content.ParticleModel(tExtensibleElements._GroupModel, min_occurs=1, max_occurs=1)



tActivity._AddElement(pyxb.binding.basis.element(pyxb.namespace.ExpandedName(Namespace, u'source'), tSource, scope=tActivity))

tActivity._AddElement(pyxb.binding.basis.element(pyxb.namespace.ExpandedName(Namespace, u'target'), tTarget, scope=tActivity))
tActivity._GroupModel_ = pyxb.binding.content.GroupSequence(
    pyxb.binding.content.ParticleModel(pyxb.binding.content.Wildcard(process_contents=pyxb.binding.content.Wildcard.PC_lax, namespace_constraint=(pyxb.binding.content.Wildcard.NC_not, u'http://schemas.xmlsoap.org/ws/2003/03/business-process/')), min_occurs=0L, max_occurs=None)
    )
tActivity._GroupModel_2 = pyxb.binding.content.GroupSequence(
    pyxb.binding.content.ParticleModel(tActivity._UseForTag(pyxb.namespace.ExpandedName(Namespace, u'target')), min_occurs=0L, max_occurs=None),
    pyxb.binding.content.ParticleModel(tActivity._UseForTag(pyxb.namespace.ExpandedName(Namespace, u'source')), min_occurs=0L, max_occurs=None)
    )
tActivity._GroupModel = pyxb.binding.content.GroupSequence(
    pyxb.binding.content.ParticleModel(tActivity._GroupModel_, min_occurs=1, max_occurs=1),
    pyxb.binding.content.ParticleModel(tActivity._GroupModel_2, min_occurs=1, max_occurs=1)
    )
tActivity._ContentModel = pyxb.binding.content.ParticleModel(tActivity._GroupModel, min_occurs=1, max_occurs=1)



tInvoke._AddElement(pyxb.binding.basis.element(pyxb.namespace.ExpandedName(Namespace, u'compensationHandler'), tCompensationHandler, scope=tInvoke))

tInvoke._AddElement(pyxb.binding.basis.element(pyxb.namespace.ExpandedName(Namespace, u'correlations'), tCorrelationsWithPattern, scope=tInvoke))

tInvoke._AddElement(pyxb.binding.basis.element(pyxb.namespace.ExpandedName(Namespace, u'catchAll'), tActivityOrCompensateContainer, scope=tInvoke))

tInvoke._AddElement(pyxb.binding.basis.element(pyxb.namespace.ExpandedName(Namespace, u'catch'), tCatch, scope=tInvoke))
tInvoke._GroupModel_2 = pyxb.binding.content.GroupSequence(
    pyxb.binding.content.ParticleModel(pyxb.binding.content.Wildcard(process_contents=pyxb.binding.content.Wildcard.PC_lax, namespace_constraint=(pyxb.binding.content.Wildcard.NC_not, u'http://schemas.xmlsoap.org/ws/2003/03/business-process/')), min_occurs=0L, max_occurs=None)
    )
tInvoke._GroupModel_3 = pyxb.binding.content.GroupSequence(
    pyxb.binding.content.ParticleModel(tInvoke._UseForTag(pyxb.namespace.ExpandedName(Namespace, u'target')), min_occurs=0L, max_occurs=None),
    pyxb.binding.content.ParticleModel(tInvoke._UseForTag(pyxb.namespace.ExpandedName(Namespace, u'source')), min_occurs=0L, max_occurs=None)
    )
tInvoke._GroupModel_ = pyxb.binding.content.GroupSequence(
    pyxb.binding.content.ParticleModel(tInvoke._GroupModel_2, min_occurs=1, max_occurs=1),
    pyxb.binding.content.ParticleModel(tInvoke._GroupModel_3, min_occurs=1, max_occurs=1)
    )
tInvoke._GroupModel_4 = pyxb.binding.content.GroupSequence(
    pyxb.binding.content.ParticleModel(tInvoke._UseForTag(pyxb.namespace.ExpandedName(Namespace, u'correlations')), min_occurs=0L, max_occurs=1L),
    pyxb.binding.content.ParticleModel(tInvoke._UseForTag(pyxb.namespace.ExpandedName(Namespace, u'catch')), min_occurs=0L, max_occurs=None),
    pyxb.binding.content.ParticleModel(tInvoke._UseForTag(pyxb.namespace.ExpandedName(Namespace, u'catchAll')), min_occurs=0L, max_occurs=1),
    pyxb.binding.content.ParticleModel(tInvoke._UseForTag(pyxb.namespace.ExpandedName(Namespace, u'compensationHandler')), min_occurs=0L, max_occurs=1)
    )
tInvoke._GroupModel = pyxb.binding.content.GroupSequence(
    pyxb.binding.content.ParticleModel(tInvoke._GroupModel_, min_occurs=1, max_occurs=1),
    pyxb.binding.content.ParticleModel(tInvoke._GroupModel_4, min_occurs=1, max_occurs=1)
    )
tInvoke._ContentModel = pyxb.binding.content.ParticleModel(tInvoke._GroupModel, min_occurs=1, max_occurs=1)



tWhile._AddElement(pyxb.binding.basis.element(pyxb.namespace.ExpandedName(Namespace, u'scope'), tScope, scope=tWhile))

tWhile._AddElement(pyxb.binding.basis.element(pyxb.namespace.ExpandedName(Namespace, u'invoke'), tInvoke, scope=tWhile))

tWhile._AddElement(pyxb.binding.basis.element(pyxb.namespace.ExpandedName(Namespace, u'switch'), tSwitch, scope=tWhile))

tWhile._AddElement(pyxb.binding.basis.element(pyxb.namespace.ExpandedName(Namespace, u'throw'), tThrow, scope=tWhile))

tWhile._AddElement(pyxb.binding.basis.element(pyxb.namespace.ExpandedName(Namespace, u'assign'), tAssign, scope=tWhile))

tWhile._AddElement(pyxb.binding.basis.element(pyxb.namespace.ExpandedName(Namespace, u'receive'), tReceive, scope=tWhile))

tWhile._AddElement(pyxb.binding.basis.element(pyxb.namespace.ExpandedName(Namespace, u'sequence'), tSequence, scope=tWhile))

tWhile._AddElement(pyxb.binding.basis.element(pyxb.namespace.ExpandedName(Namespace, u'terminate'), tTerminate, scope=tWhile))

tWhile._AddElement(pyxb.binding.basis.element(pyxb.namespace.ExpandedName(Namespace, u'while'), tWhile, scope=tWhile))

tWhile._AddElement(pyxb.binding.basis.element(pyxb.namespace.ExpandedName(Namespace, u'empty'), tEmpty, scope=tWhile))

tWhile._AddElement(pyxb.binding.basis.element(pyxb.namespace.ExpandedName(Namespace, u'flow'), tFlow, scope=tWhile))

tWhile._AddElement(pyxb.binding.basis.element(pyxb.namespace.ExpandedName(Namespace, u'pick'), tPick, scope=tWhile))

tWhile._AddElement(pyxb.binding.basis.element(pyxb.namespace.ExpandedName(Namespace, u'reply'), tReply, scope=tWhile))

tWhile._AddElement(pyxb.binding.basis.element(pyxb.namespace.ExpandedName(Namespace, u'wait'), tWait, scope=tWhile))
tWhile._GroupModel_2 = pyxb.binding.content.GroupSequence(
    pyxb.binding.content.ParticleModel(pyxb.binding.content.Wildcard(process_contents=pyxb.binding.content.Wildcard.PC_lax, namespace_constraint=(pyxb.binding.content.Wildcard.NC_not, u'http://schemas.xmlsoap.org/ws/2003/03/business-process/')), min_occurs=0L, max_occurs=None)
    )
tWhile._GroupModel_3 = pyxb.binding.content.GroupSequence(
    pyxb.binding.content.ParticleModel(tWhile._UseForTag(pyxb.namespace.ExpandedName(Namespace, u'target')), min_occurs=0L, max_occurs=None),
    pyxb.binding.content.ParticleModel(tWhile._UseForTag(pyxb.namespace.ExpandedName(Namespace, u'source')), min_occurs=0L, max_occurs=None)
    )
tWhile._GroupModel_ = pyxb.binding.content.GroupSequence(
    pyxb.binding.content.ParticleModel(tWhile._GroupModel_2, min_occurs=1, max_occurs=1),
    pyxb.binding.content.ParticleModel(tWhile._GroupModel_3, min_occurs=1, max_occurs=1)
    )
tWhile._GroupModel_5 = pyxb.binding.content.GroupChoice(
    pyxb.binding.content.ParticleModel(tWhile._UseForTag(pyxb.namespace.ExpandedName(Namespace, u'empty')), min_occurs=1, max_occurs=1),
    pyxb.binding.content.ParticleModel(tWhile._UseForTag(pyxb.namespace.ExpandedName(Namespace, u'invoke')), min_occurs=1, max_occurs=1),
    pyxb.binding.content.ParticleModel(tWhile._UseForTag(pyxb.namespace.ExpandedName(Namespace, u'receive')), min_occurs=1, max_occurs=1),
    pyxb.binding.content.ParticleModel(tWhile._UseForTag(pyxb.namespace.ExpandedName(Namespace, u'reply')), min_occurs=1, max_occurs=1),
    pyxb.binding.content.ParticleModel(tWhile._UseForTag(pyxb.namespace.ExpandedName(Namespace, u'assign')), min_occurs=1, max_occurs=1),
    pyxb.binding.content.ParticleModel(tWhile._UseForTag(pyxb.namespace.ExpandedName(Namespace, u'wait')), min_occurs=1, max_occurs=1),
    pyxb.binding.content.ParticleModel(tWhile._UseForTag(pyxb.namespace.ExpandedName(Namespace, u'throw')), min_occurs=1, max_occurs=1),
    pyxb.binding.content.ParticleModel(tWhile._UseForTag(pyxb.namespace.ExpandedName(Namespace, u'terminate')), min_occurs=1, max_occurs=1),
    pyxb.binding.content.ParticleModel(tWhile._UseForTag(pyxb.namespace.ExpandedName(Namespace, u'flow')), min_occurs=1, max_occurs=1),
    pyxb.binding.content.ParticleModel(tWhile._UseForTag(pyxb.namespace.ExpandedName(Namespace, u'switch')), min_occurs=1, max_occurs=1),
    pyxb.binding.content.ParticleModel(tWhile._UseForTag(pyxb.namespace.ExpandedName(Namespace, u'while')), min_occurs=1, max_occurs=1),
    pyxb.binding.content.ParticleModel(tWhile._UseForTag(pyxb.namespace.ExpandedName(Namespace, u'sequence')), min_occurs=1, max_occurs=1),
    pyxb.binding.content.ParticleModel(tWhile._UseForTag(pyxb.namespace.ExpandedName(Namespace, u'pick')), min_occurs=1, max_occurs=1),
    pyxb.binding.content.ParticleModel(tWhile._UseForTag(pyxb.namespace.ExpandedName(Namespace, u'scope')), min_occurs=1, max_occurs=1)
    )
tWhile._GroupModel_4 = pyxb.binding.content.GroupSequence(
    pyxb.binding.content.ParticleModel(tWhile._GroupModel_5, min_occurs=1, max_occurs=1)
    )
tWhile._GroupModel = pyxb.binding.content.GroupSequence(
    pyxb.binding.content.ParticleModel(tWhile._GroupModel_, min_occurs=1, max_occurs=1),
    pyxb.binding.content.ParticleModel(tWhile._GroupModel_4, min_occurs=1, max_occurs=1)
    )
tWhile._ContentModel = pyxb.binding.content.ParticleModel(tWhile._GroupModel, min_occurs=1, max_occurs=1)


tTerminate._GroupModel_ = pyxb.binding.content.GroupSequence(
    pyxb.binding.content.ParticleModel(pyxb.binding.content.Wildcard(process_contents=pyxb.binding.content.Wildcard.PC_lax, namespace_constraint=(pyxb.binding.content.Wildcard.NC_not, u'http://schemas.xmlsoap.org/ws/2003/03/business-process/')), min_occurs=0L, max_occurs=None)
    )
tTerminate._GroupModel_2 = pyxb.binding.content.GroupSequence(
    pyxb.binding.content.ParticleModel(tTerminate._UseForTag(pyxb.namespace.ExpandedName(Namespace, u'target')), min_occurs=0L, max_occurs=None),
    pyxb.binding.content.ParticleModel(tTerminate._UseForTag(pyxb.namespace.ExpandedName(Namespace, u'source')), min_occurs=0L, max_occurs=None)
    )
tTerminate._GroupModel = pyxb.binding.content.GroupSequence(
    pyxb.binding.content.ParticleModel(tTerminate._GroupModel_, min_occurs=1, max_occurs=1),
    pyxb.binding.content.ParticleModel(tTerminate._GroupModel_2, min_occurs=1, max_occurs=1)
    )
tTerminate._ContentModel = pyxb.binding.content.ParticleModel(tTerminate._GroupModel, min_occurs=1, max_occurs=1)



tFlow._AddElement(pyxb.binding.basis.element(pyxb.namespace.ExpandedName(Namespace, u'switch'), tSwitch, scope=tFlow))

tFlow._AddElement(pyxb.binding.basis.element(pyxb.namespace.ExpandedName(Namespace, u'pick'), tPick, scope=tFlow))

tFlow._AddElement(pyxb.binding.basis.element(pyxb.namespace.ExpandedName(Namespace, u'invoke'), tInvoke, scope=tFlow))

tFlow._AddElement(pyxb.binding.basis.element(pyxb.namespace.ExpandedName(Namespace, u'assign'), tAssign, scope=tFlow))

tFlow._AddElement(pyxb.binding.basis.element(pyxb.namespace.ExpandedName(Namespace, u'receive'), tReceive, scope=tFlow))

tFlow._AddElement(pyxb.binding.basis.element(pyxb.namespace.ExpandedName(Namespace, u'flow'), tFlow, scope=tFlow))

tFlow._AddElement(pyxb.binding.basis.element(pyxb.namespace.ExpandedName(Namespace, u'wait'), tWait, scope=tFlow))

tFlow._AddElement(pyxb.binding.basis.element(pyxb.namespace.ExpandedName(Namespace, u'while'), tWhile, scope=tFlow))

tFlow._AddElement(pyxb.binding.basis.element(pyxb.namespace.ExpandedName(Namespace, u'scope'), tScope, scope=tFlow))

tFlow._AddElement(pyxb.binding.basis.element(pyxb.namespace.ExpandedName(Namespace, u'reply'), tReply, scope=tFlow))

tFlow._AddElement(pyxb.binding.basis.element(pyxb.namespace.ExpandedName(Namespace, u'terminate'), tTerminate, scope=tFlow))

tFlow._AddElement(pyxb.binding.basis.element(pyxb.namespace.ExpandedName(Namespace, u'throw'), tThrow, scope=tFlow))

tFlow._AddElement(pyxb.binding.basis.element(pyxb.namespace.ExpandedName(Namespace, u'sequence'), tSequence, scope=tFlow))

tFlow._AddElement(pyxb.binding.basis.element(pyxb.namespace.ExpandedName(Namespace, u'links'), tLinks, scope=tFlow))

tFlow._AddElement(pyxb.binding.basis.element(pyxb.namespace.ExpandedName(Namespace, u'empty'), tEmpty, scope=tFlow))
tFlow._GroupModel_2 = pyxb.binding.content.GroupSequence(
    pyxb.binding.content.ParticleModel(pyxb.binding.content.Wildcard(process_contents=pyxb.binding.content.Wildcard.PC_lax, namespace_constraint=(pyxb.binding.content.Wildcard.NC_not, u'http://schemas.xmlsoap.org/ws/2003/03/business-process/')), min_occurs=0L, max_occurs=None)
    )
tFlow._GroupModel_3 = pyxb.binding.content.GroupSequence(
    pyxb.binding.content.ParticleModel(tFlow._UseForTag(pyxb.namespace.ExpandedName(Namespace, u'target')), min_occurs=0L, max_occurs=None),
    pyxb.binding.content.ParticleModel(tFlow._UseForTag(pyxb.namespace.ExpandedName(Namespace, u'source')), min_occurs=0L, max_occurs=None)
    )
tFlow._GroupModel_ = pyxb.binding.content.GroupSequence(
    pyxb.binding.content.ParticleModel(tFlow._GroupModel_2, min_occurs=1, max_occurs=1),
    pyxb.binding.content.ParticleModel(tFlow._GroupModel_3, min_occurs=1, max_occurs=1)
    )
tFlow._GroupModel_5 = pyxb.binding.content.GroupChoice(
    pyxb.binding.content.ParticleModel(tFlow._UseForTag(pyxb.namespace.ExpandedName(Namespace, u'empty')), min_occurs=1, max_occurs=1),
    pyxb.binding.content.ParticleModel(tFlow._UseForTag(pyxb.namespace.ExpandedName(Namespace, u'invoke')), min_occurs=1, max_occurs=1),
    pyxb.binding.content.ParticleModel(tFlow._UseForTag(pyxb.namespace.ExpandedName(Namespace, u'receive')), min_occurs=1, max_occurs=1),
    pyxb.binding.content.ParticleModel(tFlow._UseForTag(pyxb.namespace.ExpandedName(Namespace, u'reply')), min_occurs=1, max_occurs=1),
    pyxb.binding.content.ParticleModel(tFlow._UseForTag(pyxb.namespace.ExpandedName(Namespace, u'assign')), min_occurs=1, max_occurs=1),
    pyxb.binding.content.ParticleModel(tFlow._UseForTag(pyxb.namespace.ExpandedName(Namespace, u'wait')), min_occurs=1, max_occurs=1),
    pyxb.binding.content.ParticleModel(tFlow._UseForTag(pyxb.namespace.ExpandedName(Namespace, u'throw')), min_occurs=1, max_occurs=1),
    pyxb.binding.content.ParticleModel(tFlow._UseForTag(pyxb.namespace.ExpandedName(Namespace, u'terminate')), min_occurs=1, max_occurs=1),
    pyxb.binding.content.ParticleModel(tFlow._UseForTag(pyxb.namespace.ExpandedName(Namespace, u'flow')), min_occurs=1, max_occurs=1),
    pyxb.binding.content.ParticleModel(tFlow._UseForTag(pyxb.namespace.ExpandedName(Namespace, u'switch')), min_occurs=1, max_occurs=1),
    pyxb.binding.content.ParticleModel(tFlow._UseForTag(pyxb.namespace.ExpandedName(Namespace, u'while')), min_occurs=1, max_occurs=1),
    pyxb.binding.content.ParticleModel(tFlow._UseForTag(pyxb.namespace.ExpandedName(Namespace, u'sequence')), min_occurs=1, max_occurs=1),
    pyxb.binding.content.ParticleModel(tFlow._UseForTag(pyxb.namespace.ExpandedName(Namespace, u'pick')), min_occurs=1, max_occurs=1),
    pyxb.binding.content.ParticleModel(tFlow._UseForTag(pyxb.namespace.ExpandedName(Namespace, u'scope')), min_occurs=1, max_occurs=1)
    )
tFlow._GroupModel_4 = pyxb.binding.content.GroupSequence(
    pyxb.binding.content.ParticleModel(tFlow._UseForTag(pyxb.namespace.ExpandedName(Namespace, u'links')), min_occurs=0L, max_occurs=1),
    pyxb.binding.content.ParticleModel(tFlow._GroupModel_5, min_occurs=1, max_occurs=None)
    )
tFlow._GroupModel = pyxb.binding.content.GroupSequence(
    pyxb.binding.content.ParticleModel(tFlow._GroupModel_, min_occurs=1, max_occurs=1),
    pyxb.binding.content.ParticleModel(tFlow._GroupModel_4, min_occurs=1, max_occurs=1)
    )
tFlow._ContentModel = pyxb.binding.content.ParticleModel(tFlow._GroupModel, min_occurs=1, max_occurs=1)



tReceive._AddElement(pyxb.binding.basis.element(pyxb.namespace.ExpandedName(Namespace, u'correlations'), tCorrelations, scope=tReceive))
tReceive._GroupModel_2 = pyxb.binding.content.GroupSequence(
    pyxb.binding.content.ParticleModel(pyxb.binding.content.Wildcard(process_contents=pyxb.binding.content.Wildcard.PC_lax, namespace_constraint=(pyxb.binding.content.Wildcard.NC_not, u'http://schemas.xmlsoap.org/ws/2003/03/business-process/')), min_occurs=0L, max_occurs=None)
    )
tReceive._GroupModel_3 = pyxb.binding.content.GroupSequence(
    pyxb.binding.content.ParticleModel(tReceive._UseForTag(pyxb.namespace.ExpandedName(Namespace, u'target')), min_occurs=0L, max_occurs=None),
    pyxb.binding.content.ParticleModel(tReceive._UseForTag(pyxb.namespace.ExpandedName(Namespace, u'source')), min_occurs=0L, max_occurs=None)
    )
tReceive._GroupModel_ = pyxb.binding.content.GroupSequence(
    pyxb.binding.content.ParticleModel(tReceive._GroupModel_2, min_occurs=1, max_occurs=1),
    pyxb.binding.content.ParticleModel(tReceive._GroupModel_3, min_occurs=1, max_occurs=1)
    )
tReceive._GroupModel_4 = pyxb.binding.content.GroupSequence(
    pyxb.binding.content.ParticleModel(tReceive._UseForTag(pyxb.namespace.ExpandedName(Namespace, u'correlations')), min_occurs=0L, max_occurs=1)
    )
tReceive._GroupModel = pyxb.binding.content.GroupSequence(
    pyxb.binding.content.ParticleModel(tReceive._GroupModel_, min_occurs=1, max_occurs=1),
    pyxb.binding.content.ParticleModel(tReceive._GroupModel_4, min_occurs=1, max_occurs=1)
    )
tReceive._ContentModel = pyxb.binding.content.ParticleModel(tReceive._GroupModel, min_occurs=1, max_occurs=1)



tCopy._AddElement(pyxb.binding.basis.element(pyxb.namespace.ExpandedName(Namespace, u'from'), tFrom, scope=tCopy))

tCopy._AddElement(pyxb.binding.basis.element(pyxb.namespace.ExpandedName(Namespace, u'to'), CTD_ANON_2, scope=tCopy))
tCopy._GroupModel_ = pyxb.binding.content.GroupSequence(
    pyxb.binding.content.ParticleModel(pyxb.binding.content.Wildcard(process_contents=pyxb.binding.content.Wildcard.PC_lax, namespace_constraint=(pyxb.binding.content.Wildcard.NC_not, u'http://schemas.xmlsoap.org/ws/2003/03/business-process/')), min_occurs=0L, max_occurs=None)
    )
tCopy._GroupModel_2 = pyxb.binding.content.GroupSequence(
    pyxb.binding.content.ParticleModel(tCopy._UseForTag(pyxb.namespace.ExpandedName(Namespace, u'from')), min_occurs=1, max_occurs=1),
    pyxb.binding.content.ParticleModel(tCopy._UseForTag(pyxb.namespace.ExpandedName(Namespace, u'to')), min_occurs=1, max_occurs=1)
    )
tCopy._GroupModel = pyxb.binding.content.GroupSequence(
    pyxb.binding.content.ParticleModel(tCopy._GroupModel_, min_occurs=1, max_occurs=1),
    pyxb.binding.content.ParticleModel(tCopy._GroupModel_2, min_occurs=1, max_occurs=1)
    )
tCopy._ContentModel = pyxb.binding.content.ParticleModel(tCopy._GroupModel, min_occurs=1, max_occurs=1)



tReply._AddElement(pyxb.binding.basis.element(pyxb.namespace.ExpandedName(Namespace, u'correlations'), tCorrelations, scope=tReply))
tReply._GroupModel_2 = pyxb.binding.content.GroupSequence(
    pyxb.binding.content.ParticleModel(pyxb.binding.content.Wildcard(process_contents=pyxb.binding.content.Wildcard.PC_lax, namespace_constraint=(pyxb.binding.content.Wildcard.NC_not, u'http://schemas.xmlsoap.org/ws/2003/03/business-process/')), min_occurs=0L, max_occurs=None)
    )
tReply._GroupModel_3 = pyxb.binding.content.GroupSequence(
    pyxb.binding.content.ParticleModel(tReply._UseForTag(pyxb.namespace.ExpandedName(Namespace, u'target')), min_occurs=0L, max_occurs=None),
    pyxb.binding.content.ParticleModel(tReply._UseForTag(pyxb.namespace.ExpandedName(Namespace, u'source')), min_occurs=0L, max_occurs=None)
    )
tReply._GroupModel_ = pyxb.binding.content.GroupSequence(
    pyxb.binding.content.ParticleModel(tReply._GroupModel_2, min_occurs=1, max_occurs=1),
    pyxb.binding.content.ParticleModel(tReply._GroupModel_3, min_occurs=1, max_occurs=1)
    )
tReply._GroupModel_4 = pyxb.binding.content.GroupSequence(
    pyxb.binding.content.ParticleModel(tReply._UseForTag(pyxb.namespace.ExpandedName(Namespace, u'correlations')), min_occurs=0L, max_occurs=1)
    )
tReply._GroupModel = pyxb.binding.content.GroupSequence(
    pyxb.binding.content.ParticleModel(tReply._GroupModel_, min_occurs=1, max_occurs=1),
    pyxb.binding.content.ParticleModel(tReply._GroupModel_4, min_occurs=1, max_occurs=1)
    )
tReply._ContentModel = pyxb.binding.content.ParticleModel(tReply._GroupModel, min_occurs=1, max_occurs=1)



tActivityContainer._AddElement(pyxb.binding.basis.element(pyxb.namespace.ExpandedName(Namespace, u'flow'), tFlow, scope=tActivityContainer))

tActivityContainer._AddElement(pyxb.binding.basis.element(pyxb.namespace.ExpandedName(Namespace, u'reply'), tReply, scope=tActivityContainer))

tActivityContainer._AddElement(pyxb.binding.basis.element(pyxb.namespace.ExpandedName(Namespace, u'pick'), tPick, scope=tActivityContainer))

tActivityContainer._AddElement(pyxb.binding.basis.element(pyxb.namespace.ExpandedName(Namespace, u'empty'), tEmpty, scope=tActivityContainer))

tActivityContainer._AddElement(pyxb.binding.basis.element(pyxb.namespace.ExpandedName(Namespace, u'invoke'), tInvoke, scope=tActivityContainer))

tActivityContainer._AddElement(pyxb.binding.basis.element(pyxb.namespace.ExpandedName(Namespace, u'switch'), tSwitch, scope=tActivityContainer))

tActivityContainer._AddElement(pyxb.binding.basis.element(pyxb.namespace.ExpandedName(Namespace, u'assign'), tAssign, scope=tActivityContainer))

tActivityContainer._AddElement(pyxb.binding.basis.element(pyxb.namespace.ExpandedName(Namespace, u'terminate'), tTerminate, scope=tActivityContainer))

tActivityContainer._AddElement(pyxb.binding.basis.element(pyxb.namespace.ExpandedName(Namespace, u'throw'), tThrow, scope=tActivityContainer))

tActivityContainer._AddElement(pyxb.binding.basis.element(pyxb.namespace.ExpandedName(Namespace, u'while'), tWhile, scope=tActivityContainer))

tActivityContainer._AddElement(pyxb.binding.basis.element(pyxb.namespace.ExpandedName(Namespace, u'receive'), tReceive, scope=tActivityContainer))

tActivityContainer._AddElement(pyxb.binding.basis.element(pyxb.namespace.ExpandedName(Namespace, u'scope'), tScope, scope=tActivityContainer))

tActivityContainer._AddElement(pyxb.binding.basis.element(pyxb.namespace.ExpandedName(Namespace, u'wait'), tWait, scope=tActivityContainer))

tActivityContainer._AddElement(pyxb.binding.basis.element(pyxb.namespace.ExpandedName(Namespace, u'sequence'), tSequence, scope=tActivityContainer))
tActivityContainer._GroupModel_ = pyxb.binding.content.GroupSequence(
    pyxb.binding.content.ParticleModel(pyxb.binding.content.Wildcard(process_contents=pyxb.binding.content.Wildcard.PC_lax, namespace_constraint=(pyxb.binding.content.Wildcard.NC_not, u'http://schemas.xmlsoap.org/ws/2003/03/business-process/')), min_occurs=0L, max_occurs=None)
    )
tActivityContainer._GroupModel_3 = pyxb.binding.content.GroupChoice(
    pyxb.binding.content.ParticleModel(tActivityContainer._UseForTag(pyxb.namespace.ExpandedName(Namespace, u'empty')), min_occurs=1, max_occurs=1),
    pyxb.binding.content.ParticleModel(tActivityContainer._UseForTag(pyxb.namespace.ExpandedName(Namespace, u'invoke')), min_occurs=1, max_occurs=1),
    pyxb.binding.content.ParticleModel(tActivityContainer._UseForTag(pyxb.namespace.ExpandedName(Namespace, u'receive')), min_occurs=1, max_occurs=1),
    pyxb.binding.content.ParticleModel(tActivityContainer._UseForTag(pyxb.namespace.ExpandedName(Namespace, u'reply')), min_occurs=1, max_occurs=1),
    pyxb.binding.content.ParticleModel(tActivityContainer._UseForTag(pyxb.namespace.ExpandedName(Namespace, u'assign')), min_occurs=1, max_occurs=1),
    pyxb.binding.content.ParticleModel(tActivityContainer._UseForTag(pyxb.namespace.ExpandedName(Namespace, u'wait')), min_occurs=1, max_occurs=1),
    pyxb.binding.content.ParticleModel(tActivityContainer._UseForTag(pyxb.namespace.ExpandedName(Namespace, u'throw')), min_occurs=1, max_occurs=1),
    pyxb.binding.content.ParticleModel(tActivityContainer._UseForTag(pyxb.namespace.ExpandedName(Namespace, u'terminate')), min_occurs=1, max_occurs=1),
    pyxb.binding.content.ParticleModel(tActivityContainer._UseForTag(pyxb.namespace.ExpandedName(Namespace, u'flow')), min_occurs=1, max_occurs=1),
    pyxb.binding.content.ParticleModel(tActivityContainer._UseForTag(pyxb.namespace.ExpandedName(Namespace, u'switch')), min_occurs=1, max_occurs=1),
    pyxb.binding.content.ParticleModel(tActivityContainer._UseForTag(pyxb.namespace.ExpandedName(Namespace, u'while')), min_occurs=1, max_occurs=1),
    pyxb.binding.content.ParticleModel(tActivityContainer._UseForTag(pyxb.namespace.ExpandedName(Namespace, u'sequence')), min_occurs=1, max_occurs=1),
    pyxb.binding.content.ParticleModel(tActivityContainer._UseForTag(pyxb.namespace.ExpandedName(Namespace, u'pick')), min_occurs=1, max_occurs=1),
    pyxb.binding.content.ParticleModel(tActivityContainer._UseForTag(pyxb.namespace.ExpandedName(Namespace, u'scope')), min_occurs=1, max_occurs=1)
    )
tActivityContainer._GroupModel_2 = pyxb.binding.content.GroupSequence(
    pyxb.binding.content.ParticleModel(tActivityContainer._GroupModel_3, min_occurs=1, max_occurs=1)
    )
tActivityContainer._GroupModel = pyxb.binding.content.GroupSequence(
    pyxb.binding.content.ParticleModel(tActivityContainer._GroupModel_, min_occurs=1, max_occurs=1),
    pyxb.binding.content.ParticleModel(tActivityContainer._GroupModel_2, min_occurs=1, max_occurs=1)
    )
tActivityContainer._ContentModel = pyxb.binding.content.ParticleModel(tActivityContainer._GroupModel, min_occurs=1, max_occurs=1)


CTD_ANON._GroupModel_ = pyxb.binding.content.GroupSequence(
    pyxb.binding.content.ParticleModel(pyxb.binding.content.Wildcard(process_contents=pyxb.binding.content.Wildcard.PC_lax, namespace_constraint=(pyxb.binding.content.Wildcard.NC_not, u'http://schemas.xmlsoap.org/ws/2003/03/business-process/')), min_occurs=0L, max_occurs=None)
    )
CTD_ANON._GroupModel_3 = pyxb.binding.content.GroupChoice(
    pyxb.binding.content.ParticleModel(CTD_ANON._UseForTag(pyxb.namespace.ExpandedName(Namespace, u'empty')), min_occurs=1, max_occurs=1),
    pyxb.binding.content.ParticleModel(CTD_ANON._UseForTag(pyxb.namespace.ExpandedName(Namespace, u'invoke')), min_occurs=1, max_occurs=1),
    pyxb.binding.content.ParticleModel(CTD_ANON._UseForTag(pyxb.namespace.ExpandedName(Namespace, u'receive')), min_occurs=1, max_occurs=1),
    pyxb.binding.content.ParticleModel(CTD_ANON._UseForTag(pyxb.namespace.ExpandedName(Namespace, u'reply')), min_occurs=1, max_occurs=1),
    pyxb.binding.content.ParticleModel(CTD_ANON._UseForTag(pyxb.namespace.ExpandedName(Namespace, u'assign')), min_occurs=1, max_occurs=1),
    pyxb.binding.content.ParticleModel(CTD_ANON._UseForTag(pyxb.namespace.ExpandedName(Namespace, u'wait')), min_occurs=1, max_occurs=1),
    pyxb.binding.content.ParticleModel(CTD_ANON._UseForTag(pyxb.namespace.ExpandedName(Namespace, u'throw')), min_occurs=1, max_occurs=1),
    pyxb.binding.content.ParticleModel(CTD_ANON._UseForTag(pyxb.namespace.ExpandedName(Namespace, u'terminate')), min_occurs=1, max_occurs=1),
    pyxb.binding.content.ParticleModel(CTD_ANON._UseForTag(pyxb.namespace.ExpandedName(Namespace, u'flow')), min_occurs=1, max_occurs=1),
    pyxb.binding.content.ParticleModel(CTD_ANON._UseForTag(pyxb.namespace.ExpandedName(Namespace, u'switch')), min_occurs=1, max_occurs=1),
    pyxb.binding.content.ParticleModel(CTD_ANON._UseForTag(pyxb.namespace.ExpandedName(Namespace, u'while')), min_occurs=1, max_occurs=1),
    pyxb.binding.content.ParticleModel(CTD_ANON._UseForTag(pyxb.namespace.ExpandedName(Namespace, u'sequence')), min_occurs=1, max_occurs=1),
    pyxb.binding.content.ParticleModel(CTD_ANON._UseForTag(pyxb.namespace.ExpandedName(Namespace, u'pick')), min_occurs=1, max_occurs=1),
    pyxb.binding.content.ParticleModel(CTD_ANON._UseForTag(pyxb.namespace.ExpandedName(Namespace, u'scope')), min_occurs=1, max_occurs=1)
    )
CTD_ANON._GroupModel_2 = pyxb.binding.content.GroupSequence(
    pyxb.binding.content.ParticleModel(CTD_ANON._GroupModel_3, min_occurs=1, max_occurs=1)
    )
CTD_ANON._GroupModel = pyxb.binding.content.GroupSequence(
    pyxb.binding.content.ParticleModel(CTD_ANON._GroupModel_, min_occurs=1, max_occurs=1),
    pyxb.binding.content.ParticleModel(CTD_ANON._GroupModel_2, min_occurs=1, max_occurs=1)
    )
CTD_ANON._ContentModel = pyxb.binding.content.ParticleModel(CTD_ANON._GroupModel, min_occurs=1, max_occurs=1)



tActivityOrCompensateContainer._AddElement(pyxb.binding.basis.element(pyxb.namespace.ExpandedName(Namespace, u'throw'), tThrow, scope=tActivityOrCompensateContainer))

tActivityOrCompensateContainer._AddElement(pyxb.binding.basis.element(pyxb.namespace.ExpandedName(Namespace, u'invoke'), tInvoke, scope=tActivityOrCompensateContainer))

tActivityOrCompensateContainer._AddElement(pyxb.binding.basis.element(pyxb.namespace.ExpandedName(Namespace, u'while'), tWhile, scope=tActivityOrCompensateContainer))

tActivityOrCompensateContainer._AddElement(pyxb.binding.basis.element(pyxb.namespace.ExpandedName(Namespace, u'assign'), tAssign, scope=tActivityOrCompensateContainer))

tActivityOrCompensateContainer._AddElement(pyxb.binding.basis.element(pyxb.namespace.ExpandedName(Namespace, u'terminate'), tTerminate, scope=tActivityOrCompensateContainer))

tActivityOrCompensateContainer._AddElement(pyxb.binding.basis.element(pyxb.namespace.ExpandedName(Namespace, u'switch'), tSwitch, scope=tActivityOrCompensateContainer))

tActivityOrCompensateContainer._AddElement(pyxb.binding.basis.element(pyxb.namespace.ExpandedName(Namespace, u'scope'), tScope, scope=tActivityOrCompensateContainer))

tActivityOrCompensateContainer._AddElement(pyxb.binding.basis.element(pyxb.namespace.ExpandedName(Namespace, u'receive'), tReceive, scope=tActivityOrCompensateContainer))

tActivityOrCompensateContainer._AddElement(pyxb.binding.basis.element(pyxb.namespace.ExpandedName(Namespace, u'wait'), tWait, scope=tActivityOrCompensateContainer))

tActivityOrCompensateContainer._AddElement(pyxb.binding.basis.element(pyxb.namespace.ExpandedName(Namespace, u'sequence'), tSequence, scope=tActivityOrCompensateContainer))

tActivityOrCompensateContainer._AddElement(pyxb.binding.basis.element(pyxb.namespace.ExpandedName(Namespace, u'pick'), tPick, scope=tActivityOrCompensateContainer))

tActivityOrCompensateContainer._AddElement(pyxb.binding.basis.element(pyxb.namespace.ExpandedName(Namespace, u'flow'), tFlow, scope=tActivityOrCompensateContainer))

tActivityOrCompensateContainer._AddElement(pyxb.binding.basis.element(pyxb.namespace.ExpandedName(Namespace, u'compensate'), tCompensate, scope=tActivityOrCompensateContainer))

tActivityOrCompensateContainer._AddElement(pyxb.binding.basis.element(pyxb.namespace.ExpandedName(Namespace, u'reply'), tReply, scope=tActivityOrCompensateContainer))

tActivityOrCompensateContainer._AddElement(pyxb.binding.basis.element(pyxb.namespace.ExpandedName(Namespace, u'empty'), tEmpty, scope=tActivityOrCompensateContainer))
tActivityOrCompensateContainer._GroupModel_ = pyxb.binding.content.GroupSequence(
    pyxb.binding.content.ParticleModel(pyxb.binding.content.Wildcard(process_contents=pyxb.binding.content.Wildcard.PC_lax, namespace_constraint=(pyxb.binding.content.Wildcard.NC_not, u'http://schemas.xmlsoap.org/ws/2003/03/business-process/')), min_occurs=0L, max_occurs=None)
    )
tActivityOrCompensateContainer._GroupModel_3 = pyxb.binding.content.GroupChoice(
    pyxb.binding.content.ParticleModel(tActivityOrCompensateContainer._UseForTag(pyxb.namespace.ExpandedName(Namespace, u'empty')), min_occurs=1, max_occurs=1),
    pyxb.binding.content.ParticleModel(tActivityOrCompensateContainer._UseForTag(pyxb.namespace.ExpandedName(Namespace, u'invoke')), min_occurs=1, max_occurs=1),
    pyxb.binding.content.ParticleModel(tActivityOrCompensateContainer._UseForTag(pyxb.namespace.ExpandedName(Namespace, u'receive')), min_occurs=1, max_occurs=1),
    pyxb.binding.content.ParticleModel(tActivityOrCompensateContainer._UseForTag(pyxb.namespace.ExpandedName(Namespace, u'reply')), min_occurs=1, max_occurs=1),
    pyxb.binding.content.ParticleModel(tActivityOrCompensateContainer._UseForTag(pyxb.namespace.ExpandedName(Namespace, u'assign')), min_occurs=1, max_occurs=1),
    pyxb.binding.content.ParticleModel(tActivityOrCompensateContainer._UseForTag(pyxb.namespace.ExpandedName(Namespace, u'wait')), min_occurs=1, max_occurs=1),
    pyxb.binding.content.ParticleModel(tActivityOrCompensateContainer._UseForTag(pyxb.namespace.ExpandedName(Namespace, u'throw')), min_occurs=1, max_occurs=1),
    pyxb.binding.content.ParticleModel(tActivityOrCompensateContainer._UseForTag(pyxb.namespace.ExpandedName(Namespace, u'terminate')), min_occurs=1, max_occurs=1),
    pyxb.binding.content.ParticleModel(tActivityOrCompensateContainer._UseForTag(pyxb.namespace.ExpandedName(Namespace, u'flow')), min_occurs=1, max_occurs=1),
    pyxb.binding.content.ParticleModel(tActivityOrCompensateContainer._UseForTag(pyxb.namespace.ExpandedName(Namespace, u'switch')), min_occurs=1, max_occurs=1),
    pyxb.binding.content.ParticleModel(tActivityOrCompensateContainer._UseForTag(pyxb.namespace.ExpandedName(Namespace, u'while')), min_occurs=1, max_occurs=1),
    pyxb.binding.content.ParticleModel(tActivityOrCompensateContainer._UseForTag(pyxb.namespace.ExpandedName(Namespace, u'sequence')), min_occurs=1, max_occurs=1),
    pyxb.binding.content.ParticleModel(tActivityOrCompensateContainer._UseForTag(pyxb.namespace.ExpandedName(Namespace, u'pick')), min_occurs=1, max_occurs=1),
    pyxb.binding.content.ParticleModel(tActivityOrCompensateContainer._UseForTag(pyxb.namespace.ExpandedName(Namespace, u'scope')), min_occurs=1, max_occurs=1)
    )
tActivityOrCompensateContainer._GroupModel_2 = pyxb.binding.content.GroupChoice(
    pyxb.binding.content.ParticleModel(tActivityOrCompensateContainer._GroupModel_3, min_occurs=1, max_occurs=1),
    pyxb.binding.content.ParticleModel(tActivityOrCompensateContainer._UseForTag(pyxb.namespace.ExpandedName(Namespace, u'compensate')), min_occurs=1, max_occurs=1)
    )
tActivityOrCompensateContainer._GroupModel = pyxb.binding.content.GroupSequence(
    pyxb.binding.content.ParticleModel(tActivityOrCompensateContainer._GroupModel_, min_occurs=1, max_occurs=1),
    pyxb.binding.content.ParticleModel(tActivityOrCompensateContainer._GroupModel_2, min_occurs=1, max_occurs=1)
    )
tActivityOrCompensateContainer._ContentModel = pyxb.binding.content.ParticleModel(tActivityOrCompensateContainer._GroupModel, min_occurs=1, max_occurs=1)


tCatch._GroupModel_ = pyxb.binding.content.GroupSequence(
    pyxb.binding.content.ParticleModel(pyxb.binding.content.Wildcard(process_contents=pyxb.binding.content.Wildcard.PC_lax, namespace_constraint=(pyxb.binding.content.Wildcard.NC_not, u'http://schemas.xmlsoap.org/ws/2003/03/business-process/')), min_occurs=0L, max_occurs=None)
    )
tCatch._GroupModel_3 = pyxb.binding.content.GroupChoice(
    pyxb.binding.content.ParticleModel(tCatch._UseForTag(pyxb.namespace.ExpandedName(Namespace, u'empty')), min_occurs=1, max_occurs=1),
    pyxb.binding.content.ParticleModel(tCatch._UseForTag(pyxb.namespace.ExpandedName(Namespace, u'invoke')), min_occurs=1, max_occurs=1),
    pyxb.binding.content.ParticleModel(tCatch._UseForTag(pyxb.namespace.ExpandedName(Namespace, u'receive')), min_occurs=1, max_occurs=1),
    pyxb.binding.content.ParticleModel(tCatch._UseForTag(pyxb.namespace.ExpandedName(Namespace, u'reply')), min_occurs=1, max_occurs=1),
    pyxb.binding.content.ParticleModel(tCatch._UseForTag(pyxb.namespace.ExpandedName(Namespace, u'assign')), min_occurs=1, max_occurs=1),
    pyxb.binding.content.ParticleModel(tCatch._UseForTag(pyxb.namespace.ExpandedName(Namespace, u'wait')), min_occurs=1, max_occurs=1),
    pyxb.binding.content.ParticleModel(tCatch._UseForTag(pyxb.namespace.ExpandedName(Namespace, u'throw')), min_occurs=1, max_occurs=1),
    pyxb.binding.content.ParticleModel(tCatch._UseForTag(pyxb.namespace.ExpandedName(Namespace, u'terminate')), min_occurs=1, max_occurs=1),
    pyxb.binding.content.ParticleModel(tCatch._UseForTag(pyxb.namespace.ExpandedName(Namespace, u'flow')), min_occurs=1, max_occurs=1),
    pyxb.binding.content.ParticleModel(tCatch._UseForTag(pyxb.namespace.ExpandedName(Namespace, u'switch')), min_occurs=1, max_occurs=1),
    pyxb.binding.content.ParticleModel(tCatch._UseForTag(pyxb.namespace.ExpandedName(Namespace, u'while')), min_occurs=1, max_occurs=1),
    pyxb.binding.content.ParticleModel(tCatch._UseForTag(pyxb.namespace.ExpandedName(Namespace, u'sequence')), min_occurs=1, max_occurs=1),
    pyxb.binding.content.ParticleModel(tCatch._UseForTag(pyxb.namespace.ExpandedName(Namespace, u'pick')), min_occurs=1, max_occurs=1),
    pyxb.binding.content.ParticleModel(tCatch._UseForTag(pyxb.namespace.ExpandedName(Namespace, u'scope')), min_occurs=1, max_occurs=1)
    )
tCatch._GroupModel_2 = pyxb.binding.content.GroupChoice(
    pyxb.binding.content.ParticleModel(tCatch._GroupModel_3, min_occurs=1, max_occurs=1),
    pyxb.binding.content.ParticleModel(tCatch._UseForTag(pyxb.namespace.ExpandedName(Namespace, u'compensate')), min_occurs=1, max_occurs=1)
    )
tCatch._GroupModel = pyxb.binding.content.GroupSequence(
    pyxb.binding.content.ParticleModel(tCatch._GroupModel_, min_occurs=1, max_occurs=1),
    pyxb.binding.content.ParticleModel(tCatch._GroupModel_2, min_occurs=1, max_occurs=1)
    )
tCatch._ContentModel = pyxb.binding.content.ParticleModel(tCatch._GroupModel, min_occurs=1, max_occurs=1)


tThrow._GroupModel_ = pyxb.binding.content.GroupSequence(
    pyxb.binding.content.ParticleModel(pyxb.binding.content.Wildcard(process_contents=pyxb.binding.content.Wildcard.PC_lax, namespace_constraint=(pyxb.binding.content.Wildcard.NC_not, u'http://schemas.xmlsoap.org/ws/2003/03/business-process/')), min_occurs=0L, max_occurs=None)
    )
tThrow._GroupModel_2 = pyxb.binding.content.GroupSequence(
    pyxb.binding.content.ParticleModel(tThrow._UseForTag(pyxb.namespace.ExpandedName(Namespace, u'target')), min_occurs=0L, max_occurs=None),
    pyxb.binding.content.ParticleModel(tThrow._UseForTag(pyxb.namespace.ExpandedName(Namespace, u'source')), min_occurs=0L, max_occurs=None)
    )
tThrow._GroupModel = pyxb.binding.content.GroupSequence(
    pyxb.binding.content.ParticleModel(tThrow._GroupModel_, min_occurs=1, max_occurs=1),
    pyxb.binding.content.ParticleModel(tThrow._GroupModel_2, min_occurs=1, max_occurs=1)
    )
tThrow._ContentModel = pyxb.binding.content.ParticleModel(tThrow._GroupModel, min_occurs=1, max_occurs=1)


tEmpty._GroupModel_ = pyxb.binding.content.GroupSequence(
    pyxb.binding.content.ParticleModel(pyxb.binding.content.Wildcard(process_contents=pyxb.binding.content.Wildcard.PC_lax, namespace_constraint=(pyxb.binding.content.Wildcard.NC_not, u'http://schemas.xmlsoap.org/ws/2003/03/business-process/')), min_occurs=0L, max_occurs=None)
    )
tEmpty._GroupModel_2 = pyxb.binding.content.GroupSequence(
    pyxb.binding.content.ParticleModel(tEmpty._UseForTag(pyxb.namespace.ExpandedName(Namespace, u'target')), min_occurs=0L, max_occurs=None),
    pyxb.binding.content.ParticleModel(tEmpty._UseForTag(pyxb.namespace.ExpandedName(Namespace, u'source')), min_occurs=0L, max_occurs=None)
    )
tEmpty._GroupModel = pyxb.binding.content.GroupSequence(
    pyxb.binding.content.ParticleModel(tEmpty._GroupModel_, min_occurs=1, max_occurs=1),
    pyxb.binding.content.ParticleModel(tEmpty._GroupModel_2, min_occurs=1, max_occurs=1)
    )
tEmpty._ContentModel = pyxb.binding.content.ParticleModel(tEmpty._GroupModel, min_occurs=1, max_occurs=1)



tAssign._AddElement(pyxb.binding.basis.element(pyxb.namespace.ExpandedName(Namespace, u'copy'), tCopy, scope=tAssign))
tAssign._GroupModel_2 = pyxb.binding.content.GroupSequence(
    pyxb.binding.content.ParticleModel(pyxb.binding.content.Wildcard(process_contents=pyxb.binding.content.Wildcard.PC_lax, namespace_constraint=(pyxb.binding.content.Wildcard.NC_not, u'http://schemas.xmlsoap.org/ws/2003/03/business-process/')), min_occurs=0L, max_occurs=None)
    )
tAssign._GroupModel_3 = pyxb.binding.content.GroupSequence(
    pyxb.binding.content.ParticleModel(tAssign._UseForTag(pyxb.namespace.ExpandedName(Namespace, u'target')), min_occurs=0L, max_occurs=None),
    pyxb.binding.content.ParticleModel(tAssign._UseForTag(pyxb.namespace.ExpandedName(Namespace, u'source')), min_occurs=0L, max_occurs=None)
    )
tAssign._GroupModel_ = pyxb.binding.content.GroupSequence(
    pyxb.binding.content.ParticleModel(tAssign._GroupModel_2, min_occurs=1, max_occurs=1),
    pyxb.binding.content.ParticleModel(tAssign._GroupModel_3, min_occurs=1, max_occurs=1)
    )
tAssign._GroupModel_4 = pyxb.binding.content.GroupSequence(
    pyxb.binding.content.ParticleModel(tAssign._UseForTag(pyxb.namespace.ExpandedName(Namespace, u'copy')), min_occurs=1L, max_occurs=None)
    )
tAssign._GroupModel = pyxb.binding.content.GroupSequence(
    pyxb.binding.content.ParticleModel(tAssign._GroupModel_, min_occurs=1, max_occurs=1),
    pyxb.binding.content.ParticleModel(tAssign._GroupModel_4, min_occurs=1, max_occurs=1)
    )
tAssign._ContentModel = pyxb.binding.content.ParticleModel(tAssign._GroupModel, min_occurs=1, max_occurs=1)


tWait._GroupModel_ = pyxb.binding.content.GroupSequence(
    pyxb.binding.content.ParticleModel(pyxb.binding.content.Wildcard(process_contents=pyxb.binding.content.Wildcard.PC_lax, namespace_constraint=(pyxb.binding.content.Wildcard.NC_not, u'http://schemas.xmlsoap.org/ws/2003/03/business-process/')), min_occurs=0L, max_occurs=None)
    )
tWait._GroupModel_2 = pyxb.binding.content.GroupSequence(
    pyxb.binding.content.ParticleModel(tWait._UseForTag(pyxb.namespace.ExpandedName(Namespace, u'target')), min_occurs=0L, max_occurs=None),
    pyxb.binding.content.ParticleModel(tWait._UseForTag(pyxb.namespace.ExpandedName(Namespace, u'source')), min_occurs=0L, max_occurs=None)
    )
tWait._GroupModel = pyxb.binding.content.GroupSequence(
    pyxb.binding.content.ParticleModel(tWait._GroupModel_, min_occurs=1, max_occurs=1),
    pyxb.binding.content.ParticleModel(tWait._GroupModel_2, min_occurs=1, max_occurs=1)
    )
tWait._ContentModel = pyxb.binding.content.ParticleModel(tWait._GroupModel, min_occurs=1, max_occurs=1)



tEventHandlers._AddElement(pyxb.binding.basis.element(pyxb.namespace.ExpandedName(Namespace, u'onAlarm'), tOnAlarm, scope=tEventHandlers))

tEventHandlers._AddElement(pyxb.binding.basis.element(pyxb.namespace.ExpandedName(Namespace, u'onMessage'), tOnMessage, scope=tEventHandlers))
tEventHandlers._GroupModel_ = pyxb.binding.content.GroupSequence(
    pyxb.binding.content.ParticleModel(pyxb.binding.content.Wildcard(process_contents=pyxb.binding.content.Wildcard.PC_lax, namespace_constraint=(pyxb.binding.content.Wildcard.NC_not, u'http://schemas.xmlsoap.org/ws/2003/03/business-process/')), min_occurs=0L, max_occurs=None)
    )
tEventHandlers._GroupModel_2 = pyxb.binding.content.GroupSequence(
    pyxb.binding.content.ParticleModel(tEventHandlers._UseForTag(pyxb.namespace.ExpandedName(Namespace, u'onMessage')), min_occurs=0L, max_occurs=None),
    pyxb.binding.content.ParticleModel(tEventHandlers._UseForTag(pyxb.namespace.ExpandedName(Namespace, u'onAlarm')), min_occurs=0L, max_occurs=None)
    )
tEventHandlers._GroupModel = pyxb.binding.content.GroupSequence(
    pyxb.binding.content.ParticleModel(tEventHandlers._GroupModel_, min_occurs=1, max_occurs=1),
    pyxb.binding.content.ParticleModel(tEventHandlers._GroupModel_2, min_occurs=1, max_occurs=1)
    )
tEventHandlers._ContentModel = pyxb.binding.content.ParticleModel(tEventHandlers._GroupModel, min_occurs=1, max_occurs=1)



tSwitch._AddElement(pyxb.binding.basis.element(pyxb.namespace.ExpandedName(Namespace, u'otherwise'), tActivityContainer, scope=tSwitch))

tSwitch._AddElement(pyxb.binding.basis.element(pyxb.namespace.ExpandedName(Namespace, u'case'), CTD_ANON, scope=tSwitch))
tSwitch._GroupModel_2 = pyxb.binding.content.GroupSequence(
    pyxb.binding.content.ParticleModel(pyxb.binding.content.Wildcard(process_contents=pyxb.binding.content.Wildcard.PC_lax, namespace_constraint=(pyxb.binding.content.Wildcard.NC_not, u'http://schemas.xmlsoap.org/ws/2003/03/business-process/')), min_occurs=0L, max_occurs=None)
    )
tSwitch._GroupModel_3 = pyxb.binding.content.GroupSequence(
    pyxb.binding.content.ParticleModel(tSwitch._UseForTag(pyxb.namespace.ExpandedName(Namespace, u'target')), min_occurs=0L, max_occurs=None),
    pyxb.binding.content.ParticleModel(tSwitch._UseForTag(pyxb.namespace.ExpandedName(Namespace, u'source')), min_occurs=0L, max_occurs=None)
    )
tSwitch._GroupModel_ = pyxb.binding.content.GroupSequence(
    pyxb.binding.content.ParticleModel(tSwitch._GroupModel_2, min_occurs=1, max_occurs=1),
    pyxb.binding.content.ParticleModel(tSwitch._GroupModel_3, min_occurs=1, max_occurs=1)
    )
tSwitch._GroupModel_4 = pyxb.binding.content.GroupSequence(
    pyxb.binding.content.ParticleModel(tSwitch._UseForTag(pyxb.namespace.ExpandedName(Namespace, u'case')), min_occurs=1, max_occurs=None),
    pyxb.binding.content.ParticleModel(tSwitch._UseForTag(pyxb.namespace.ExpandedName(Namespace, u'otherwise')), min_occurs=0L, max_occurs=1)
    )
tSwitch._GroupModel = pyxb.binding.content.GroupSequence(
    pyxb.binding.content.ParticleModel(tSwitch._GroupModel_, min_occurs=1, max_occurs=1),
    pyxb.binding.content.ParticleModel(tSwitch._GroupModel_4, min_occurs=1, max_occurs=1)
    )
tSwitch._ContentModel = pyxb.binding.content.ParticleModel(tSwitch._GroupModel, min_occurs=1, max_occurs=1)



tPick._AddElement(pyxb.binding.basis.element(pyxb.namespace.ExpandedName(Namespace, u'onAlarm'), tOnAlarm, scope=tPick))

tPick._AddElement(pyxb.binding.basis.element(pyxb.namespace.ExpandedName(Namespace, u'onMessage'), tOnMessage, scope=tPick))
tPick._GroupModel_2 = pyxb.binding.content.GroupSequence(
    pyxb.binding.content.ParticleModel(pyxb.binding.content.Wildcard(process_contents=pyxb.binding.content.Wildcard.PC_lax, namespace_constraint=(pyxb.binding.content.Wildcard.NC_not, u'http://schemas.xmlsoap.org/ws/2003/03/business-process/')), min_occurs=0L, max_occurs=None)
    )
tPick._GroupModel_3 = pyxb.binding.content.GroupSequence(
    pyxb.binding.content.ParticleModel(tPick._UseForTag(pyxb.namespace.ExpandedName(Namespace, u'target')), min_occurs=0L, max_occurs=None),
    pyxb.binding.content.ParticleModel(tPick._UseForTag(pyxb.namespace.ExpandedName(Namespace, u'source')), min_occurs=0L, max_occurs=None)
    )
tPick._GroupModel_ = pyxb.binding.content.GroupSequence(
    pyxb.binding.content.ParticleModel(tPick._GroupModel_2, min_occurs=1, max_occurs=1),
    pyxb.binding.content.ParticleModel(tPick._GroupModel_3, min_occurs=1, max_occurs=1)
    )
tPick._GroupModel_4 = pyxb.binding.content.GroupSequence(
    pyxb.binding.content.ParticleModel(tPick._UseForTag(pyxb.namespace.ExpandedName(Namespace, u'onMessage')), min_occurs=1, max_occurs=None),
    pyxb.binding.content.ParticleModel(tPick._UseForTag(pyxb.namespace.ExpandedName(Namespace, u'onAlarm')), min_occurs=0L, max_occurs=None)
    )
tPick._GroupModel = pyxb.binding.content.GroupSequence(
    pyxb.binding.content.ParticleModel(tPick._GroupModel_, min_occurs=1, max_occurs=1),
    pyxb.binding.content.ParticleModel(tPick._GroupModel_4, min_occurs=1, max_occurs=1)
    )
tPick._ContentModel = pyxb.binding.content.ParticleModel(tPick._GroupModel, min_occurs=1, max_occurs=1)


CTD_ANON_._GroupModel = pyxb.binding.content.GroupSequence(
    pyxb.binding.content.ParticleModel(pyxb.binding.content.Wildcard(process_contents=pyxb.binding.content.Wildcard.PC_lax, namespace_constraint=(pyxb.binding.content.Wildcard.NC_not, u'http://schemas.xmlsoap.org/ws/2003/03/business-process/')), min_occurs=0L, max_occurs=None)
    )
CTD_ANON_._ContentModel = pyxb.binding.content.ParticleModel(CTD_ANON_._GroupModel, min_occurs=1, max_occurs=1)



tSequence._AddElement(pyxb.binding.basis.element(pyxb.namespace.ExpandedName(Namespace, u'switch'), tSwitch, scope=tSequence))

tSequence._AddElement(pyxb.binding.basis.element(pyxb.namespace.ExpandedName(Namespace, u'reply'), tReply, scope=tSequence))

tSequence._AddElement(pyxb.binding.basis.element(pyxb.namespace.ExpandedName(Namespace, u'pick'), tPick, scope=tSequence))

tSequence._AddElement(pyxb.binding.basis.element(pyxb.namespace.ExpandedName(Namespace, u'wait'), tWait, scope=tSequence))

tSequence._AddElement(pyxb.binding.basis.element(pyxb.namespace.ExpandedName(Namespace, u'terminate'), tTerminate, scope=tSequence))

tSequence._AddElement(pyxb.binding.basis.element(pyxb.namespace.ExpandedName(Namespace, u'empty'), tEmpty, scope=tSequence))

tSequence._AddElement(pyxb.binding.basis.element(pyxb.namespace.ExpandedName(Namespace, u'while'), tWhile, scope=tSequence))

tSequence._AddElement(pyxb.binding.basis.element(pyxb.namespace.ExpandedName(Namespace, u'throw'), tThrow, scope=tSequence))

tSequence._AddElement(pyxb.binding.basis.element(pyxb.namespace.ExpandedName(Namespace, u'scope'), tScope, scope=tSequence))

tSequence._AddElement(pyxb.binding.basis.element(pyxb.namespace.ExpandedName(Namespace, u'flow'), tFlow, scope=tSequence))

tSequence._AddElement(pyxb.binding.basis.element(pyxb.namespace.ExpandedName(Namespace, u'receive'), tReceive, scope=tSequence))

tSequence._AddElement(pyxb.binding.basis.element(pyxb.namespace.ExpandedName(Namespace, u'sequence'), tSequence, scope=tSequence))

tSequence._AddElement(pyxb.binding.basis.element(pyxb.namespace.ExpandedName(Namespace, u'invoke'), tInvoke, scope=tSequence))

tSequence._AddElement(pyxb.binding.basis.element(pyxb.namespace.ExpandedName(Namespace, u'assign'), tAssign, scope=tSequence))
tSequence._GroupModel_2 = pyxb.binding.content.GroupSequence(
    pyxb.binding.content.ParticleModel(pyxb.binding.content.Wildcard(process_contents=pyxb.binding.content.Wildcard.PC_lax, namespace_constraint=(pyxb.binding.content.Wildcard.NC_not, u'http://schemas.xmlsoap.org/ws/2003/03/business-process/')), min_occurs=0L, max_occurs=None)
    )
tSequence._GroupModel_3 = pyxb.binding.content.GroupSequence(
    pyxb.binding.content.ParticleModel(tSequence._UseForTag(pyxb.namespace.ExpandedName(Namespace, u'target')), min_occurs=0L, max_occurs=None),
    pyxb.binding.content.ParticleModel(tSequence._UseForTag(pyxb.namespace.ExpandedName(Namespace, u'source')), min_occurs=0L, max_occurs=None)
    )
tSequence._GroupModel_ = pyxb.binding.content.GroupSequence(
    pyxb.binding.content.ParticleModel(tSequence._GroupModel_2, min_occurs=1, max_occurs=1),
    pyxb.binding.content.ParticleModel(tSequence._GroupModel_3, min_occurs=1, max_occurs=1)
    )
tSequence._GroupModel_5 = pyxb.binding.content.GroupChoice(
    pyxb.binding.content.ParticleModel(tSequence._UseForTag(pyxb.namespace.ExpandedName(Namespace, u'empty')), min_occurs=1, max_occurs=1),
    pyxb.binding.content.ParticleModel(tSequence._UseForTag(pyxb.namespace.ExpandedName(Namespace, u'invoke')), min_occurs=1, max_occurs=1),
    pyxb.binding.content.ParticleModel(tSequence._UseForTag(pyxb.namespace.ExpandedName(Namespace, u'receive')), min_occurs=1, max_occurs=1),
    pyxb.binding.content.ParticleModel(tSequence._UseForTag(pyxb.namespace.ExpandedName(Namespace, u'reply')), min_occurs=1, max_occurs=1),
    pyxb.binding.content.ParticleModel(tSequence._UseForTag(pyxb.namespace.ExpandedName(Namespace, u'assign')), min_occurs=1, max_occurs=1),
    pyxb.binding.content.ParticleModel(tSequence._UseForTag(pyxb.namespace.ExpandedName(Namespace, u'wait')), min_occurs=1, max_occurs=1),
    pyxb.binding.content.ParticleModel(tSequence._UseForTag(pyxb.namespace.ExpandedName(Namespace, u'throw')), min_occurs=1, max_occurs=1),
    pyxb.binding.content.ParticleModel(tSequence._UseForTag(pyxb.namespace.ExpandedName(Namespace, u'terminate')), min_occurs=1, max_occurs=1),
    pyxb.binding.content.ParticleModel(tSequence._UseForTag(pyxb.namespace.ExpandedName(Namespace, u'flow')), min_occurs=1, max_occurs=1),
    pyxb.binding.content.ParticleModel(tSequence._UseForTag(pyxb.namespace.ExpandedName(Namespace, u'switch')), min_occurs=1, max_occurs=1),
    pyxb.binding.content.ParticleModel(tSequence._UseForTag(pyxb.namespace.ExpandedName(Namespace, u'while')), min_occurs=1, max_occurs=1),
    pyxb.binding.content.ParticleModel(tSequence._UseForTag(pyxb.namespace.ExpandedName(Namespace, u'sequence')), min_occurs=1, max_occurs=1),
    pyxb.binding.content.ParticleModel(tSequence._UseForTag(pyxb.namespace.ExpandedName(Namespace, u'pick')), min_occurs=1, max_occurs=1),
    pyxb.binding.content.ParticleModel(tSequence._UseForTag(pyxb.namespace.ExpandedName(Namespace, u'scope')), min_occurs=1, max_occurs=1)
    )
tSequence._GroupModel_4 = pyxb.binding.content.GroupSequence(
    pyxb.binding.content.ParticleModel(tSequence._GroupModel_5, min_occurs=1, max_occurs=None)
    )
tSequence._GroupModel = pyxb.binding.content.GroupSequence(
    pyxb.binding.content.ParticleModel(tSequence._GroupModel_, min_occurs=1, max_occurs=1),
    pyxb.binding.content.ParticleModel(tSequence._GroupModel_4, min_occurs=1, max_occurs=1)
    )
tSequence._ContentModel = pyxb.binding.content.ParticleModel(tSequence._GroupModel, min_occurs=1, max_occurs=1)



tCorrelationsWithPattern._AddElement(pyxb.binding.basis.element(pyxb.namespace.ExpandedName(Namespace, u'correlation'), tCorrelationWithPattern, scope=tCorrelationsWithPattern))
tCorrelationsWithPattern._GroupModel_ = pyxb.binding.content.GroupSequence(
    pyxb.binding.content.ParticleModel(pyxb.binding.content.Wildcard(process_contents=pyxb.binding.content.Wildcard.PC_lax, namespace_constraint=(pyxb.binding.content.Wildcard.NC_not, u'http://schemas.xmlsoap.org/ws/2003/03/business-process/')), min_occurs=0L, max_occurs=None)
    )
tCorrelationsWithPattern._GroupModel_2 = pyxb.binding.content.GroupSequence(
    pyxb.binding.content.ParticleModel(tCorrelationsWithPattern._UseForTag(pyxb.namespace.ExpandedName(Namespace, u'correlation')), min_occurs=1L, max_occurs=None)
    )
tCorrelationsWithPattern._GroupModel = pyxb.binding.content.GroupSequence(
    pyxb.binding.content.ParticleModel(tCorrelationsWithPattern._GroupModel_, min_occurs=1, max_occurs=1),
    pyxb.binding.content.ParticleModel(tCorrelationsWithPattern._GroupModel_2, min_occurs=1, max_occurs=1)
    )
tCorrelationsWithPattern._ContentModel = pyxb.binding.content.ParticleModel(tCorrelationsWithPattern._GroupModel, min_occurs=1, max_occurs=1)



tVariables._AddElement(pyxb.binding.basis.element(pyxb.namespace.ExpandedName(Namespace, u'variable'), tVariable, scope=tVariables))
tVariables._GroupModel_ = pyxb.binding.content.GroupSequence(
    pyxb.binding.content.ParticleModel(pyxb.binding.content.Wildcard(process_contents=pyxb.binding.content.Wildcard.PC_lax, namespace_constraint=(pyxb.binding.content.Wildcard.NC_not, u'http://schemas.xmlsoap.org/ws/2003/03/business-process/')), min_occurs=0L, max_occurs=None)
    )
tVariables._GroupModel_2 = pyxb.binding.content.GroupSequence(
    pyxb.binding.content.ParticleModel(tVariables._UseForTag(pyxb.namespace.ExpandedName(Namespace, u'variable')), min_occurs=1, max_occurs=None)
    )
tVariables._GroupModel = pyxb.binding.content.GroupSequence(
    pyxb.binding.content.ParticleModel(tVariables._GroupModel_, min_occurs=1, max_occurs=1),
    pyxb.binding.content.ParticleModel(tVariables._GroupModel_2, min_occurs=1, max_occurs=1)
    )
tVariables._ContentModel = pyxb.binding.content.ParticleModel(tVariables._GroupModel, min_occurs=1, max_occurs=1)



tCorrelationSets._AddElement(pyxb.binding.basis.element(pyxb.namespace.ExpandedName(Namespace, u'correlationSet'), tCorrelationSet, scope=tCorrelationSets))
tCorrelationSets._GroupModel_ = pyxb.binding.content.GroupSequence(
    pyxb.binding.content.ParticleModel(pyxb.binding.content.Wildcard(process_contents=pyxb.binding.content.Wildcard.PC_lax, namespace_constraint=(pyxb.binding.content.Wildcard.NC_not, u'http://schemas.xmlsoap.org/ws/2003/03/business-process/')), min_occurs=0L, max_occurs=None)
    )
tCorrelationSets._GroupModel_2 = pyxb.binding.content.GroupSequence(
    pyxb.binding.content.ParticleModel(tCorrelationSets._UseForTag(pyxb.namespace.ExpandedName(Namespace, u'correlationSet')), min_occurs=1, max_occurs=None)
    )
tCorrelationSets._GroupModel = pyxb.binding.content.GroupSequence(
    pyxb.binding.content.ParticleModel(tCorrelationSets._GroupModel_, min_occurs=1, max_occurs=1),
    pyxb.binding.content.ParticleModel(tCorrelationSets._GroupModel_2, min_occurs=1, max_occurs=1)
    )
tCorrelationSets._ContentModel = pyxb.binding.content.ParticleModel(tCorrelationSets._GroupModel, min_occurs=1, max_occurs=1)



tFaultHandlers._AddElement(pyxb.binding.basis.element(pyxb.namespace.ExpandedName(Namespace, u'catchAll'), tActivityOrCompensateContainer, scope=tFaultHandlers))

tFaultHandlers._AddElement(pyxb.binding.basis.element(pyxb.namespace.ExpandedName(Namespace, u'catch'), tCatch, scope=tFaultHandlers))
tFaultHandlers._GroupModel_ = pyxb.binding.content.GroupSequence(
    pyxb.binding.content.ParticleModel(pyxb.binding.content.Wildcard(process_contents=pyxb.binding.content.Wildcard.PC_lax, namespace_constraint=(pyxb.binding.content.Wildcard.NC_not, u'http://schemas.xmlsoap.org/ws/2003/03/business-process/')), min_occurs=0L, max_occurs=None)
    )
tFaultHandlers._GroupModel_2 = pyxb.binding.content.GroupSequence(
    pyxb.binding.content.ParticleModel(tFaultHandlers._UseForTag(pyxb.namespace.ExpandedName(Namespace, u'catch')), min_occurs=0L, max_occurs=None),
    pyxb.binding.content.ParticleModel(tFaultHandlers._UseForTag(pyxb.namespace.ExpandedName(Namespace, u'catchAll')), min_occurs=0L, max_occurs=1)
    )
tFaultHandlers._GroupModel = pyxb.binding.content.GroupSequence(
    pyxb.binding.content.ParticleModel(tFaultHandlers._GroupModel_, min_occurs=1, max_occurs=1),
    pyxb.binding.content.ParticleModel(tFaultHandlers._GroupModel_2, min_occurs=1, max_occurs=1)
    )
tFaultHandlers._ContentModel = pyxb.binding.content.ParticleModel(tFaultHandlers._GroupModel, min_occurs=1, max_occurs=1)



tOnMessage._AddElement(pyxb.binding.basis.element(pyxb.namespace.ExpandedName(Namespace, u'invoke'), tInvoke, scope=tOnMessage))

tOnMessage._AddElement(pyxb.binding.basis.element(pyxb.namespace.ExpandedName(Namespace, u'scope'), tScope, scope=tOnMessage))

tOnMessage._AddElement(pyxb.binding.basis.element(pyxb.namespace.ExpandedName(Namespace, u'assign'), tAssign, scope=tOnMessage))

tOnMessage._AddElement(pyxb.binding.basis.element(pyxb.namespace.ExpandedName(Namespace, u'switch'), tSwitch, scope=tOnMessage))

tOnMessage._AddElement(pyxb.binding.basis.element(pyxb.namespace.ExpandedName(Namespace, u'sequence'), tSequence, scope=tOnMessage))

tOnMessage._AddElement(pyxb.binding.basis.element(pyxb.namespace.ExpandedName(Namespace, u'correlations'), tCorrelations, scope=tOnMessage))

tOnMessage._AddElement(pyxb.binding.basis.element(pyxb.namespace.ExpandedName(Namespace, u'receive'), tReceive, scope=tOnMessage))

tOnMessage._AddElement(pyxb.binding.basis.element(pyxb.namespace.ExpandedName(Namespace, u'while'), tWhile, scope=tOnMessage))

tOnMessage._AddElement(pyxb.binding.basis.element(pyxb.namespace.ExpandedName(Namespace, u'wait'), tWait, scope=tOnMessage))

tOnMessage._AddElement(pyxb.binding.basis.element(pyxb.namespace.ExpandedName(Namespace, u'empty'), tEmpty, scope=tOnMessage))

tOnMessage._AddElement(pyxb.binding.basis.element(pyxb.namespace.ExpandedName(Namespace, u'terminate'), tTerminate, scope=tOnMessage))

tOnMessage._AddElement(pyxb.binding.basis.element(pyxb.namespace.ExpandedName(Namespace, u'reply'), tReply, scope=tOnMessage))

tOnMessage._AddElement(pyxb.binding.basis.element(pyxb.namespace.ExpandedName(Namespace, u'pick'), tPick, scope=tOnMessage))

tOnMessage._AddElement(pyxb.binding.basis.element(pyxb.namespace.ExpandedName(Namespace, u'throw'), tThrow, scope=tOnMessage))

tOnMessage._AddElement(pyxb.binding.basis.element(pyxb.namespace.ExpandedName(Namespace, u'flow'), tFlow, scope=tOnMessage))
tOnMessage._GroupModel_ = pyxb.binding.content.GroupSequence(
    pyxb.binding.content.ParticleModel(pyxb.binding.content.Wildcard(process_contents=pyxb.binding.content.Wildcard.PC_lax, namespace_constraint=(pyxb.binding.content.Wildcard.NC_not, u'http://schemas.xmlsoap.org/ws/2003/03/business-process/')), min_occurs=0L, max_occurs=None)
    )
tOnMessage._GroupModel_3 = pyxb.binding.content.GroupChoice(
    pyxb.binding.content.ParticleModel(tOnMessage._UseForTag(pyxb.namespace.ExpandedName(Namespace, u'empty')), min_occurs=1, max_occurs=1),
    pyxb.binding.content.ParticleModel(tOnMessage._UseForTag(pyxb.namespace.ExpandedName(Namespace, u'invoke')), min_occurs=1, max_occurs=1),
    pyxb.binding.content.ParticleModel(tOnMessage._UseForTag(pyxb.namespace.ExpandedName(Namespace, u'receive')), min_occurs=1, max_occurs=1),
    pyxb.binding.content.ParticleModel(tOnMessage._UseForTag(pyxb.namespace.ExpandedName(Namespace, u'reply')), min_occurs=1, max_occurs=1),
    pyxb.binding.content.ParticleModel(tOnMessage._UseForTag(pyxb.namespace.ExpandedName(Namespace, u'assign')), min_occurs=1, max_occurs=1),
    pyxb.binding.content.ParticleModel(tOnMessage._UseForTag(pyxb.namespace.ExpandedName(Namespace, u'wait')), min_occurs=1, max_occurs=1),
    pyxb.binding.content.ParticleModel(tOnMessage._UseForTag(pyxb.namespace.ExpandedName(Namespace, u'throw')), min_occurs=1, max_occurs=1),
    pyxb.binding.content.ParticleModel(tOnMessage._UseForTag(pyxb.namespace.ExpandedName(Namespace, u'terminate')), min_occurs=1, max_occurs=1),
    pyxb.binding.content.ParticleModel(tOnMessage._UseForTag(pyxb.namespace.ExpandedName(Namespace, u'flow')), min_occurs=1, max_occurs=1),
    pyxb.binding.content.ParticleModel(tOnMessage._UseForTag(pyxb.namespace.ExpandedName(Namespace, u'switch')), min_occurs=1, max_occurs=1),
    pyxb.binding.content.ParticleModel(tOnMessage._UseForTag(pyxb.namespace.ExpandedName(Namespace, u'while')), min_occurs=1, max_occurs=1),
    pyxb.binding.content.ParticleModel(tOnMessage._UseForTag(pyxb.namespace.ExpandedName(Namespace, u'sequence')), min_occurs=1, max_occurs=1),
    pyxb.binding.content.ParticleModel(tOnMessage._UseForTag(pyxb.namespace.ExpandedName(Namespace, u'pick')), min_occurs=1, max_occurs=1),
    pyxb.binding.content.ParticleModel(tOnMessage._UseForTag(pyxb.namespace.ExpandedName(Namespace, u'scope')), min_occurs=1, max_occurs=1)
    )
tOnMessage._GroupModel_2 = pyxb.binding.content.GroupSequence(
    pyxb.binding.content.ParticleModel(tOnMessage._UseForTag(pyxb.namespace.ExpandedName(Namespace, u'correlations')), min_occurs=0L, max_occurs=1),
    pyxb.binding.content.ParticleModel(tOnMessage._GroupModel_3, min_occurs=1, max_occurs=1)
    )
tOnMessage._GroupModel = pyxb.binding.content.GroupSequence(
    pyxb.binding.content.ParticleModel(tOnMessage._GroupModel_, min_occurs=1, max_occurs=1),
    pyxb.binding.content.ParticleModel(tOnMessage._GroupModel_2, min_occurs=1, max_occurs=1)
    )
tOnMessage._ContentModel = pyxb.binding.content.ParticleModel(tOnMessage._GroupModel, min_occurs=1, max_occurs=1)


tCompensationHandler._GroupModel_ = pyxb.binding.content.GroupSequence(
    pyxb.binding.content.ParticleModel(pyxb.binding.content.Wildcard(process_contents=pyxb.binding.content.Wildcard.PC_lax, namespace_constraint=(pyxb.binding.content.Wildcard.NC_not, u'http://schemas.xmlsoap.org/ws/2003/03/business-process/')), min_occurs=0L, max_occurs=None)
    )
tCompensationHandler._GroupModel_3 = pyxb.binding.content.GroupChoice(
    pyxb.binding.content.ParticleModel(tCompensationHandler._UseForTag(pyxb.namespace.ExpandedName(Namespace, u'empty')), min_occurs=1, max_occurs=1),
    pyxb.binding.content.ParticleModel(tCompensationHandler._UseForTag(pyxb.namespace.ExpandedName(Namespace, u'invoke')), min_occurs=1, max_occurs=1),
    pyxb.binding.content.ParticleModel(tCompensationHandler._UseForTag(pyxb.namespace.ExpandedName(Namespace, u'receive')), min_occurs=1, max_occurs=1),
    pyxb.binding.content.ParticleModel(tCompensationHandler._UseForTag(pyxb.namespace.ExpandedName(Namespace, u'reply')), min_occurs=1, max_occurs=1),
    pyxb.binding.content.ParticleModel(tCompensationHandler._UseForTag(pyxb.namespace.ExpandedName(Namespace, u'assign')), min_occurs=1, max_occurs=1),
    pyxb.binding.content.ParticleModel(tCompensationHandler._UseForTag(pyxb.namespace.ExpandedName(Namespace, u'wait')), min_occurs=1, max_occurs=1),
    pyxb.binding.content.ParticleModel(tCompensationHandler._UseForTag(pyxb.namespace.ExpandedName(Namespace, u'throw')), min_occurs=1, max_occurs=1),
    pyxb.binding.content.ParticleModel(tCompensationHandler._UseForTag(pyxb.namespace.ExpandedName(Namespace, u'terminate')), min_occurs=1, max_occurs=1),
    pyxb.binding.content.ParticleModel(tCompensationHandler._UseForTag(pyxb.namespace.ExpandedName(Namespace, u'flow')), min_occurs=1, max_occurs=1),
    pyxb.binding.content.ParticleModel(tCompensationHandler._UseForTag(pyxb.namespace.ExpandedName(Namespace, u'switch')), min_occurs=1, max_occurs=1),
    pyxb.binding.content.ParticleModel(tCompensationHandler._UseForTag(pyxb.namespace.ExpandedName(Namespace, u'while')), min_occurs=1, max_occurs=1),
    pyxb.binding.content.ParticleModel(tCompensationHandler._UseForTag(pyxb.namespace.ExpandedName(Namespace, u'sequence')), min_occurs=1, max_occurs=1),
    pyxb.binding.content.ParticleModel(tCompensationHandler._UseForTag(pyxb.namespace.ExpandedName(Namespace, u'pick')), min_occurs=1, max_occurs=1),
    pyxb.binding.content.ParticleModel(tCompensationHandler._UseForTag(pyxb.namespace.ExpandedName(Namespace, u'scope')), min_occurs=1, max_occurs=1)
    )
tCompensationHandler._GroupModel_2 = pyxb.binding.content.GroupChoice(
    pyxb.binding.content.ParticleModel(tCompensationHandler._GroupModel_3, min_occurs=1, max_occurs=1),
    pyxb.binding.content.ParticleModel(tCompensationHandler._UseForTag(pyxb.namespace.ExpandedName(Namespace, u'compensate')), min_occurs=1, max_occurs=1)
    )
tCompensationHandler._GroupModel = pyxb.binding.content.GroupSequence(
    pyxb.binding.content.ParticleModel(tCompensationHandler._GroupModel_, min_occurs=1, max_occurs=1),
    pyxb.binding.content.ParticleModel(tCompensationHandler._GroupModel_2, min_occurs=1, max_occurs=1)
    )
tCompensationHandler._ContentModel = pyxb.binding.content.ParticleModel(tCompensationHandler._GroupModel, min_occurs=1, max_occurs=1)


tCompensate._GroupModel_ = pyxb.binding.content.GroupSequence(
    pyxb.binding.content.ParticleModel(pyxb.binding.content.Wildcard(process_contents=pyxb.binding.content.Wildcard.PC_lax, namespace_constraint=(pyxb.binding.content.Wildcard.NC_not, u'http://schemas.xmlsoap.org/ws/2003/03/business-process/')), min_occurs=0L, max_occurs=None)
    )
tCompensate._GroupModel_2 = pyxb.binding.content.GroupSequence(
    pyxb.binding.content.ParticleModel(tCompensate._UseForTag(pyxb.namespace.ExpandedName(Namespace, u'target')), min_occurs=0L, max_occurs=None),
    pyxb.binding.content.ParticleModel(tCompensate._UseForTag(pyxb.namespace.ExpandedName(Namespace, u'source')), min_occurs=0L, max_occurs=None)
    )
tCompensate._GroupModel = pyxb.binding.content.GroupSequence(
    pyxb.binding.content.ParticleModel(tCompensate._GroupModel_, min_occurs=1, max_occurs=1),
    pyxb.binding.content.ParticleModel(tCompensate._GroupModel_2, min_occurs=1, max_occurs=1)
    )
tCompensate._ContentModel = pyxb.binding.content.ParticleModel(tCompensate._GroupModel, min_occurs=1, max_occurs=1)


tTarget._GroupModel = pyxb.binding.content.GroupSequence(
    pyxb.binding.content.ParticleModel(pyxb.binding.content.Wildcard(process_contents=pyxb.binding.content.Wildcard.PC_lax, namespace_constraint=(pyxb.binding.content.Wildcard.NC_not, u'http://schemas.xmlsoap.org/ws/2003/03/business-process/')), min_occurs=0L, max_occurs=None)
    )
tTarget._ContentModel = pyxb.binding.content.ParticleModel(tTarget._GroupModel, min_occurs=1, max_occurs=1)



tScope._AddElement(pyxb.binding.basis.element(pyxb.namespace.ExpandedName(Namespace, u'terminate'), tTerminate, scope=tScope))

tScope._AddElement(pyxb.binding.basis.element(pyxb.namespace.ExpandedName(Namespace, u'assign'), tAssign, scope=tScope))

tScope._AddElement(pyxb.binding.basis.element(pyxb.namespace.ExpandedName(Namespace, u'faultHandlers'), tFaultHandlers, scope=tScope))

tScope._AddElement(pyxb.binding.basis.element(pyxb.namespace.ExpandedName(Namespace, u'throw'), tThrow, scope=tScope))

tScope._AddElement(pyxb.binding.basis.element(pyxb.namespace.ExpandedName(Namespace, u'sequence'), tSequence, scope=tScope))

tScope._AddElement(pyxb.binding.basis.element(pyxb.namespace.ExpandedName(Namespace, u'pick'), tPick, scope=tScope))

tScope._AddElement(pyxb.binding.basis.element(pyxb.namespace.ExpandedName(Namespace, u'wait'), tWait, scope=tScope))

tScope._AddElement(pyxb.binding.basis.element(pyxb.namespace.ExpandedName(Namespace, u'scope'), tScope, scope=tScope))

tScope._AddElement(pyxb.binding.basis.element(pyxb.namespace.ExpandedName(Namespace, u'flow'), tFlow, scope=tScope))

tScope._AddElement(pyxb.binding.basis.element(pyxb.namespace.ExpandedName(Namespace, u'compensationHandler'), tCompensationHandler, scope=tScope))

tScope._AddElement(pyxb.binding.basis.element(pyxb.namespace.ExpandedName(Namespace, u'empty'), tEmpty, scope=tScope))

tScope._AddElement(pyxb.binding.basis.element(pyxb.namespace.ExpandedName(Namespace, u'correlationSets'), tCorrelationSets, scope=tScope))

tScope._AddElement(pyxb.binding.basis.element(pyxb.namespace.ExpandedName(Namespace, u'reply'), tReply, scope=tScope))

tScope._AddElement(pyxb.binding.basis.element(pyxb.namespace.ExpandedName(Namespace, u'receive'), tReceive, scope=tScope))

tScope._AddElement(pyxb.binding.basis.element(pyxb.namespace.ExpandedName(Namespace, u'switch'), tSwitch, scope=tScope))

tScope._AddElement(pyxb.binding.basis.element(pyxb.namespace.ExpandedName(Namespace, u'variables'), tVariables, scope=tScope))

tScope._AddElement(pyxb.binding.basis.element(pyxb.namespace.ExpandedName(Namespace, u'invoke'), tInvoke, scope=tScope))

tScope._AddElement(pyxb.binding.basis.element(pyxb.namespace.ExpandedName(Namespace, u'while'), tWhile, scope=tScope))

tScope._AddElement(pyxb.binding.basis.element(pyxb.namespace.ExpandedName(Namespace, u'eventHandlers'), tEventHandlers, scope=tScope))
tScope._GroupModel_2 = pyxb.binding.content.GroupSequence(
    pyxb.binding.content.ParticleModel(pyxb.binding.content.Wildcard(process_contents=pyxb.binding.content.Wildcard.PC_lax, namespace_constraint=(pyxb.binding.content.Wildcard.NC_not, u'http://schemas.xmlsoap.org/ws/2003/03/business-process/')), min_occurs=0L, max_occurs=None)
    )
tScope._GroupModel_3 = pyxb.binding.content.GroupSequence(
    pyxb.binding.content.ParticleModel(tScope._UseForTag(pyxb.namespace.ExpandedName(Namespace, u'target')), min_occurs=0L, max_occurs=None),
    pyxb.binding.content.ParticleModel(tScope._UseForTag(pyxb.namespace.ExpandedName(Namespace, u'source')), min_occurs=0L, max_occurs=None)
    )
tScope._GroupModel_ = pyxb.binding.content.GroupSequence(
    pyxb.binding.content.ParticleModel(tScope._GroupModel_2, min_occurs=1, max_occurs=1),
    pyxb.binding.content.ParticleModel(tScope._GroupModel_3, min_occurs=1, max_occurs=1)
    )
tScope._GroupModel_5 = pyxb.binding.content.GroupChoice(
    pyxb.binding.content.ParticleModel(tScope._UseForTag(pyxb.namespace.ExpandedName(Namespace, u'empty')), min_occurs=1, max_occurs=1),
    pyxb.binding.content.ParticleModel(tScope._UseForTag(pyxb.namespace.ExpandedName(Namespace, u'invoke')), min_occurs=1, max_occurs=1),
    pyxb.binding.content.ParticleModel(tScope._UseForTag(pyxb.namespace.ExpandedName(Namespace, u'receive')), min_occurs=1, max_occurs=1),
    pyxb.binding.content.ParticleModel(tScope._UseForTag(pyxb.namespace.ExpandedName(Namespace, u'reply')), min_occurs=1, max_occurs=1),
    pyxb.binding.content.ParticleModel(tScope._UseForTag(pyxb.namespace.ExpandedName(Namespace, u'assign')), min_occurs=1, max_occurs=1),
    pyxb.binding.content.ParticleModel(tScope._UseForTag(pyxb.namespace.ExpandedName(Namespace, u'wait')), min_occurs=1, max_occurs=1),
    pyxb.binding.content.ParticleModel(tScope._UseForTag(pyxb.namespace.ExpandedName(Namespace, u'throw')), min_occurs=1, max_occurs=1),
    pyxb.binding.content.ParticleModel(tScope._UseForTag(pyxb.namespace.ExpandedName(Namespace, u'terminate')), min_occurs=1, max_occurs=1),
    pyxb.binding.content.ParticleModel(tScope._UseForTag(pyxb.namespace.ExpandedName(Namespace, u'flow')), min_occurs=1, max_occurs=1),
    pyxb.binding.content.ParticleModel(tScope._UseForTag(pyxb.namespace.ExpandedName(Namespace, u'switch')), min_occurs=1, max_occurs=1),
    pyxb.binding.content.ParticleModel(tScope._UseForTag(pyxb.namespace.ExpandedName(Namespace, u'while')), min_occurs=1, max_occurs=1),
    pyxb.binding.content.ParticleModel(tScope._UseForTag(pyxb.namespace.ExpandedName(Namespace, u'sequence')), min_occurs=1, max_occurs=1),
    pyxb.binding.content.ParticleModel(tScope._UseForTag(pyxb.namespace.ExpandedName(Namespace, u'pick')), min_occurs=1, max_occurs=1),
    pyxb.binding.content.ParticleModel(tScope._UseForTag(pyxb.namespace.ExpandedName(Namespace, u'scope')), min_occurs=1, max_occurs=1)
    )
tScope._GroupModel_4 = pyxb.binding.content.GroupSequence(
    pyxb.binding.content.ParticleModel(tScope._UseForTag(pyxb.namespace.ExpandedName(Namespace, u'variables')), min_occurs=0L, max_occurs=1),
    pyxb.binding.content.ParticleModel(tScope._UseForTag(pyxb.namespace.ExpandedName(Namespace, u'correlationSets')), min_occurs=0L, max_occurs=1),
    pyxb.binding.content.ParticleModel(tScope._UseForTag(pyxb.namespace.ExpandedName(Namespace, u'faultHandlers')), min_occurs=0L, max_occurs=1),
    pyxb.binding.content.ParticleModel(tScope._UseForTag(pyxb.namespace.ExpandedName(Namespace, u'compensationHandler')), min_occurs=0L, max_occurs=1),
    pyxb.binding.content.ParticleModel(tScope._UseForTag(pyxb.namespace.ExpandedName(Namespace, u'eventHandlers')), min_occurs=0L, max_occurs=1),
    pyxb.binding.content.ParticleModel(tScope._GroupModel_5, min_occurs=1, max_occurs=1)
    )
tScope._GroupModel = pyxb.binding.content.GroupSequence(
    pyxb.binding.content.ParticleModel(tScope._GroupModel_, min_occurs=1, max_occurs=1),
    pyxb.binding.content.ParticleModel(tScope._GroupModel_4, min_occurs=1, max_occurs=1)
    )
tScope._ContentModel = pyxb.binding.content.ParticleModel(tScope._GroupModel, min_occurs=1, max_occurs=1)


tFrom._GroupModel = pyxb.binding.content.GroupSequence(
    pyxb.binding.content.ParticleModel(pyxb.binding.content.Wildcard(process_contents=pyxb.binding.content.Wildcard.PC_lax, namespace_constraint=(pyxb.binding.content.Wildcard.NC_not, u'http://schemas.xmlsoap.org/ws/2003/03/business-process/')), min_occurs=0L, max_occurs=None)
    )
tFrom._ContentModel = pyxb.binding.content.ParticleModel(tFrom._GroupModel, min_occurs=1, max_occurs=1)



tLinks._AddElement(pyxb.binding.basis.element(pyxb.namespace.ExpandedName(Namespace, u'link'), tLink, scope=tLinks))
tLinks._GroupModel_ = pyxb.binding.content.GroupSequence(
    pyxb.binding.content.ParticleModel(pyxb.binding.content.Wildcard(process_contents=pyxb.binding.content.Wildcard.PC_lax, namespace_constraint=(pyxb.binding.content.Wildcard.NC_not, u'http://schemas.xmlsoap.org/ws/2003/03/business-process/')), min_occurs=0L, max_occurs=None)
    )
tLinks._GroupModel_2 = pyxb.binding.content.GroupSequence(
    pyxb.binding.content.ParticleModel(tLinks._UseForTag(pyxb.namespace.ExpandedName(Namespace, u'link')), min_occurs=1, max_occurs=None)
    )
tLinks._GroupModel = pyxb.binding.content.GroupSequence(
    pyxb.binding.content.ParticleModel(tLinks._GroupModel_, min_occurs=1, max_occurs=1),
    pyxb.binding.content.ParticleModel(tLinks._GroupModel_2, min_occurs=1, max_occurs=1)
    )
tLinks._ContentModel = pyxb.binding.content.ParticleModel(tLinks._GroupModel, min_occurs=1, max_occurs=1)



tProcess._AddElement(pyxb.binding.basis.element(pyxb.namespace.ExpandedName(Namespace, u'reply'), tReply, scope=tProcess))

tProcess._AddElement(pyxb.binding.basis.element(pyxb.namespace.ExpandedName(Namespace, u'partners'), tPartners, scope=tProcess))

tProcess._AddElement(pyxb.binding.basis.element(pyxb.namespace.ExpandedName(Namespace, u'terminate'), tTerminate, scope=tProcess))

tProcess._AddElement(pyxb.binding.basis.element(pyxb.namespace.ExpandedName(Namespace, u'sequence'), tSequence, scope=tProcess))

tProcess._AddElement(pyxb.binding.basis.element(pyxb.namespace.ExpandedName(Namespace, u'wait'), tWait, scope=tProcess))

tProcess._AddElement(pyxb.binding.basis.element(pyxb.namespace.ExpandedName(Namespace, u'receive'), tReceive, scope=tProcess))

tProcess._AddElement(pyxb.binding.basis.element(pyxb.namespace.ExpandedName(Namespace, u'partnerLinks'), tPartnerLinks, scope=tProcess))

tProcess._AddElement(pyxb.binding.basis.element(pyxb.namespace.ExpandedName(Namespace, u'eventHandlers'), tEventHandlers, scope=tProcess))

tProcess._AddElement(pyxb.binding.basis.element(pyxb.namespace.ExpandedName(Namespace, u'flow'), tFlow, scope=tProcess))

tProcess._AddElement(pyxb.binding.basis.element(pyxb.namespace.ExpandedName(Namespace, u'pick'), tPick, scope=tProcess))

tProcess._AddElement(pyxb.binding.basis.element(pyxb.namespace.ExpandedName(Namespace, u'empty'), tEmpty, scope=tProcess))

tProcess._AddElement(pyxb.binding.basis.element(pyxb.namespace.ExpandedName(Namespace, u'invoke'), tInvoke, scope=tProcess))

tProcess._AddElement(pyxb.binding.basis.element(pyxb.namespace.ExpandedName(Namespace, u'correlationSets'), tCorrelationSets, scope=tProcess))

tProcess._AddElement(pyxb.binding.basis.element(pyxb.namespace.ExpandedName(Namespace, u'switch'), tSwitch, scope=tProcess))

tProcess._AddElement(pyxb.binding.basis.element(pyxb.namespace.ExpandedName(Namespace, u'throw'), tThrow, scope=tProcess))

tProcess._AddElement(pyxb.binding.basis.element(pyxb.namespace.ExpandedName(Namespace, u'scope'), tScope, scope=tProcess))

tProcess._AddElement(pyxb.binding.basis.element(pyxb.namespace.ExpandedName(Namespace, u'variables'), tVariables, scope=tProcess))

tProcess._AddElement(pyxb.binding.basis.element(pyxb.namespace.ExpandedName(Namespace, u'faultHandlers'), tFaultHandlers, scope=tProcess))

tProcess._AddElement(pyxb.binding.basis.element(pyxb.namespace.ExpandedName(Namespace, u'while'), tWhile, scope=tProcess))

tProcess._AddElement(pyxb.binding.basis.element(pyxb.namespace.ExpandedName(Namespace, u'assign'), tAssign, scope=tProcess))

tProcess._AddElement(pyxb.binding.basis.element(pyxb.namespace.ExpandedName(Namespace, u'compensationHandler'), tCompensationHandler, scope=tProcess))
tProcess._GroupModel_ = pyxb.binding.content.GroupSequence(
    pyxb.binding.content.ParticleModel(pyxb.binding.content.Wildcard(process_contents=pyxb.binding.content.Wildcard.PC_lax, namespace_constraint=(pyxb.binding.content.Wildcard.NC_not, u'http://schemas.xmlsoap.org/ws/2003/03/business-process/')), min_occurs=0L, max_occurs=None)
    )
tProcess._GroupModel_3 = pyxb.binding.content.GroupChoice(
    pyxb.binding.content.ParticleModel(tProcess._UseForTag(pyxb.namespace.ExpandedName(Namespace, u'empty')), min_occurs=1, max_occurs=1),
    pyxb.binding.content.ParticleModel(tProcess._UseForTag(pyxb.namespace.ExpandedName(Namespace, u'invoke')), min_occurs=1, max_occurs=1),
    pyxb.binding.content.ParticleModel(tProcess._UseForTag(pyxb.namespace.ExpandedName(Namespace, u'receive')), min_occurs=1, max_occurs=1),
    pyxb.binding.content.ParticleModel(tProcess._UseForTag(pyxb.namespace.ExpandedName(Namespace, u'reply')), min_occurs=1, max_occurs=1),
    pyxb.binding.content.ParticleModel(tProcess._UseForTag(pyxb.namespace.ExpandedName(Namespace, u'assign')), min_occurs=1, max_occurs=1),
    pyxb.binding.content.ParticleModel(tProcess._UseForTag(pyxb.namespace.ExpandedName(Namespace, u'wait')), min_occurs=1, max_occurs=1),
    pyxb.binding.content.ParticleModel(tProcess._UseForTag(pyxb.namespace.ExpandedName(Namespace, u'throw')), min_occurs=1, max_occurs=1),
    pyxb.binding.content.ParticleModel(tProcess._UseForTag(pyxb.namespace.ExpandedName(Namespace, u'terminate')), min_occurs=1, max_occurs=1),
    pyxb.binding.content.ParticleModel(tProcess._UseForTag(pyxb.namespace.ExpandedName(Namespace, u'flow')), min_occurs=1, max_occurs=1),
    pyxb.binding.content.ParticleModel(tProcess._UseForTag(pyxb.namespace.ExpandedName(Namespace, u'switch')), min_occurs=1, max_occurs=1),
    pyxb.binding.content.ParticleModel(tProcess._UseForTag(pyxb.namespace.ExpandedName(Namespace, u'while')), min_occurs=1, max_occurs=1),
    pyxb.binding.content.ParticleModel(tProcess._UseForTag(pyxb.namespace.ExpandedName(Namespace, u'sequence')), min_occurs=1, max_occurs=1),
    pyxb.binding.content.ParticleModel(tProcess._UseForTag(pyxb.namespace.ExpandedName(Namespace, u'pick')), min_occurs=1, max_occurs=1),
    pyxb.binding.content.ParticleModel(tProcess._UseForTag(pyxb.namespace.ExpandedName(Namespace, u'scope')), min_occurs=1, max_occurs=1)
    )
tProcess._GroupModel_2 = pyxb.binding.content.GroupSequence(
    pyxb.binding.content.ParticleModel(tProcess._UseForTag(pyxb.namespace.ExpandedName(Namespace, u'partnerLinks')), min_occurs=0L, max_occurs=1),
    pyxb.binding.content.ParticleModel(tProcess._UseForTag(pyxb.namespace.ExpandedName(Namespace, u'partners')), min_occurs=0L, max_occurs=1),
    pyxb.binding.content.ParticleModel(tProcess._UseForTag(pyxb.namespace.ExpandedName(Namespace, u'variables')), min_occurs=0L, max_occurs=1),
    pyxb.binding.content.ParticleModel(tProcess._UseForTag(pyxb.namespace.ExpandedName(Namespace, u'correlationSets')), min_occurs=0L, max_occurs=1),
    pyxb.binding.content.ParticleModel(tProcess._UseForTag(pyxb.namespace.ExpandedName(Namespace, u'faultHandlers')), min_occurs=0L, max_occurs=1),
    pyxb.binding.content.ParticleModel(tProcess._UseForTag(pyxb.namespace.ExpandedName(Namespace, u'compensationHandler')), min_occurs=0L, max_occurs=1),
    pyxb.binding.content.ParticleModel(tProcess._UseForTag(pyxb.namespace.ExpandedName(Namespace, u'eventHandlers')), min_occurs=0L, max_occurs=1),
    pyxb.binding.content.ParticleModel(tProcess._GroupModel_3, min_occurs=1, max_occurs=1)
    )
tProcess._GroupModel = pyxb.binding.content.GroupSequence(
    pyxb.binding.content.ParticleModel(tProcess._GroupModel_, min_occurs=1, max_occurs=1),
    pyxb.binding.content.ParticleModel(tProcess._GroupModel_2, min_occurs=1, max_occurs=1)
    )
tProcess._ContentModel = pyxb.binding.content.ParticleModel(tProcess._GroupModel, min_occurs=1, max_occurs=1)


tOnAlarm._GroupModel_ = pyxb.binding.content.GroupSequence(
    pyxb.binding.content.ParticleModel(pyxb.binding.content.Wildcard(process_contents=pyxb.binding.content.Wildcard.PC_lax, namespace_constraint=(pyxb.binding.content.Wildcard.NC_not, u'http://schemas.xmlsoap.org/ws/2003/03/business-process/')), min_occurs=0L, max_occurs=None)
    )
tOnAlarm._GroupModel_3 = pyxb.binding.content.GroupChoice(
    pyxb.binding.content.ParticleModel(tOnAlarm._UseForTag(pyxb.namespace.ExpandedName(Namespace, u'empty')), min_occurs=1, max_occurs=1),
    pyxb.binding.content.ParticleModel(tOnAlarm._UseForTag(pyxb.namespace.ExpandedName(Namespace, u'invoke')), min_occurs=1, max_occurs=1),
    pyxb.binding.content.ParticleModel(tOnAlarm._UseForTag(pyxb.namespace.ExpandedName(Namespace, u'receive')), min_occurs=1, max_occurs=1),
    pyxb.binding.content.ParticleModel(tOnAlarm._UseForTag(pyxb.namespace.ExpandedName(Namespace, u'reply')), min_occurs=1, max_occurs=1),
    pyxb.binding.content.ParticleModel(tOnAlarm._UseForTag(pyxb.namespace.ExpandedName(Namespace, u'assign')), min_occurs=1, max_occurs=1),
    pyxb.binding.content.ParticleModel(tOnAlarm._UseForTag(pyxb.namespace.ExpandedName(Namespace, u'wait')), min_occurs=1, max_occurs=1),
    pyxb.binding.content.ParticleModel(tOnAlarm._UseForTag(pyxb.namespace.ExpandedName(Namespace, u'throw')), min_occurs=1, max_occurs=1),
    pyxb.binding.content.ParticleModel(tOnAlarm._UseForTag(pyxb.namespace.ExpandedName(Namespace, u'terminate')), min_occurs=1, max_occurs=1),
    pyxb.binding.content.ParticleModel(tOnAlarm._UseForTag(pyxb.namespace.ExpandedName(Namespace, u'flow')), min_occurs=1, max_occurs=1),
    pyxb.binding.content.ParticleModel(tOnAlarm._UseForTag(pyxb.namespace.ExpandedName(Namespace, u'switch')), min_occurs=1, max_occurs=1),
    pyxb.binding.content.ParticleModel(tOnAlarm._UseForTag(pyxb.namespace.ExpandedName(Namespace, u'while')), min_occurs=1, max_occurs=1),
    pyxb.binding.content.ParticleModel(tOnAlarm._UseForTag(pyxb.namespace.ExpandedName(Namespace, u'sequence')), min_occurs=1, max_occurs=1),
    pyxb.binding.content.ParticleModel(tOnAlarm._UseForTag(pyxb.namespace.ExpandedName(Namespace, u'pick')), min_occurs=1, max_occurs=1),
    pyxb.binding.content.ParticleModel(tOnAlarm._UseForTag(pyxb.namespace.ExpandedName(Namespace, u'scope')), min_occurs=1, max_occurs=1)
    )
tOnAlarm._GroupModel_2 = pyxb.binding.content.GroupSequence(
    pyxb.binding.content.ParticleModel(tOnAlarm._GroupModel_3, min_occurs=1, max_occurs=1)
    )
tOnAlarm._GroupModel = pyxb.binding.content.GroupSequence(
    pyxb.binding.content.ParticleModel(tOnAlarm._GroupModel_, min_occurs=1, max_occurs=1),
    pyxb.binding.content.ParticleModel(tOnAlarm._GroupModel_2, min_occurs=1, max_occurs=1)
    )
tOnAlarm._ContentModel = pyxb.binding.content.ParticleModel(tOnAlarm._GroupModel, min_occurs=1, max_occurs=1)



tCorrelations._AddElement(pyxb.binding.basis.element(pyxb.namespace.ExpandedName(Namespace, u'correlation'), tCorrelation, scope=tCorrelations))
tCorrelations._GroupModel_ = pyxb.binding.content.GroupSequence(
    pyxb.binding.content.ParticleModel(pyxb.binding.content.Wildcard(process_contents=pyxb.binding.content.Wildcard.PC_lax, namespace_constraint=(pyxb.binding.content.Wildcard.NC_not, u'http://schemas.xmlsoap.org/ws/2003/03/business-process/')), min_occurs=0L, max_occurs=None)
    )
tCorrelations._GroupModel_2 = pyxb.binding.content.GroupSequence(
    pyxb.binding.content.ParticleModel(tCorrelations._UseForTag(pyxb.namespace.ExpandedName(Namespace, u'correlation')), min_occurs=1L, max_occurs=None)
    )
tCorrelations._GroupModel = pyxb.binding.content.GroupSequence(
    pyxb.binding.content.ParticleModel(tCorrelations._GroupModel_, min_occurs=1, max_occurs=1),
    pyxb.binding.content.ParticleModel(tCorrelations._GroupModel_2, min_occurs=1, max_occurs=1)
    )
tCorrelations._ContentModel = pyxb.binding.content.ParticleModel(tCorrelations._GroupModel, min_occurs=1, max_occurs=1)


tCorrelation._GroupModel = pyxb.binding.content.GroupSequence(
    pyxb.binding.content.ParticleModel(pyxb.binding.content.Wildcard(process_contents=pyxb.binding.content.Wildcard.PC_lax, namespace_constraint=(pyxb.binding.content.Wildcard.NC_not, u'http://schemas.xmlsoap.org/ws/2003/03/business-process/')), min_occurs=0L, max_occurs=None)
    )
tCorrelation._ContentModel = pyxb.binding.content.ParticleModel(tCorrelation._GroupModel, min_occurs=1, max_occurs=1)


tCorrelationWithPattern._GroupModel = pyxb.binding.content.GroupSequence(
    pyxb.binding.content.ParticleModel(pyxb.binding.content.Wildcard(process_contents=pyxb.binding.content.Wildcard.PC_lax, namespace_constraint=(pyxb.binding.content.Wildcard.NC_not, u'http://schemas.xmlsoap.org/ws/2003/03/business-process/')), min_occurs=0L, max_occurs=None)
    )
tCorrelationWithPattern._ContentModel = pyxb.binding.content.ParticleModel(tCorrelationWithPattern._GroupModel, min_occurs=1, max_occurs=1)



tPartnerLinks._AddElement(pyxb.binding.basis.element(pyxb.namespace.ExpandedName(Namespace, u'partnerLink'), tPartnerLink, scope=tPartnerLinks))
tPartnerLinks._GroupModel_ = pyxb.binding.content.GroupSequence(
    pyxb.binding.content.ParticleModel(pyxb.binding.content.Wildcard(process_contents=pyxb.binding.content.Wildcard.PC_lax, namespace_constraint=(pyxb.binding.content.Wildcard.NC_not, u'http://schemas.xmlsoap.org/ws/2003/03/business-process/')), min_occurs=0L, max_occurs=None)
    )
tPartnerLinks._GroupModel_2 = pyxb.binding.content.GroupSequence(
    pyxb.binding.content.ParticleModel(tPartnerLinks._UseForTag(pyxb.namespace.ExpandedName(Namespace, u'partnerLink')), min_occurs=1L, max_occurs=None)
    )
tPartnerLinks._GroupModel = pyxb.binding.content.GroupSequence(
    pyxb.binding.content.ParticleModel(tPartnerLinks._GroupModel_, min_occurs=1, max_occurs=1),
    pyxb.binding.content.ParticleModel(tPartnerLinks._GroupModel_2, min_occurs=1, max_occurs=1)
    )
tPartnerLinks._ContentModel = pyxb.binding.content.ParticleModel(tPartnerLinks._GroupModel, min_occurs=1, max_occurs=1)



tPartner._AddElement(pyxb.binding.basis.element(pyxb.namespace.ExpandedName(Namespace, u'partnerLink'), CTD_ANON_, scope=tPartner))
tPartner._GroupModel_ = pyxb.binding.content.GroupSequence(
    pyxb.binding.content.ParticleModel(pyxb.binding.content.Wildcard(process_contents=pyxb.binding.content.Wildcard.PC_lax, namespace_constraint=(pyxb.binding.content.Wildcard.NC_not, u'http://schemas.xmlsoap.org/ws/2003/03/business-process/')), min_occurs=0L, max_occurs=None)
    )
tPartner._GroupModel_2 = pyxb.binding.content.GroupSequence(
    pyxb.binding.content.ParticleModel(tPartner._UseForTag(pyxb.namespace.ExpandedName(Namespace, u'partnerLink')), min_occurs=1L, max_occurs=None)
    )
tPartner._GroupModel = pyxb.binding.content.GroupSequence(
    pyxb.binding.content.ParticleModel(tPartner._GroupModel_, min_occurs=1, max_occurs=1),
    pyxb.binding.content.ParticleModel(tPartner._GroupModel_2, min_occurs=1, max_occurs=1)
    )
tPartner._ContentModel = pyxb.binding.content.ParticleModel(tPartner._GroupModel, min_occurs=1, max_occurs=1)



tPartners._AddElement(pyxb.binding.basis.element(pyxb.namespace.ExpandedName(Namespace, u'partner'), tPartner, scope=tPartners))
tPartners._GroupModel_ = pyxb.binding.content.GroupSequence(
    pyxb.binding.content.ParticleModel(pyxb.binding.content.Wildcard(process_contents=pyxb.binding.content.Wildcard.PC_lax, namespace_constraint=(pyxb.binding.content.Wildcard.NC_not, u'http://schemas.xmlsoap.org/ws/2003/03/business-process/')), min_occurs=0L, max_occurs=None)
    )
tPartners._GroupModel_2 = pyxb.binding.content.GroupSequence(
    pyxb.binding.content.ParticleModel(tPartners._UseForTag(pyxb.namespace.ExpandedName(Namespace, u'partner')), min_occurs=1L, max_occurs=None)
    )
tPartners._GroupModel = pyxb.binding.content.GroupSequence(
    pyxb.binding.content.ParticleModel(tPartners._GroupModel_, min_occurs=1, max_occurs=1),
    pyxb.binding.content.ParticleModel(tPartners._GroupModel_2, min_occurs=1, max_occurs=1)
    )
tPartners._ContentModel = pyxb.binding.content.ParticleModel(tPartners._GroupModel, min_occurs=1, max_occurs=1)


tCorrelationSet._GroupModel = pyxb.binding.content.GroupSequence(
    pyxb.binding.content.ParticleModel(pyxb.binding.content.Wildcard(process_contents=pyxb.binding.content.Wildcard.PC_lax, namespace_constraint=(pyxb.binding.content.Wildcard.NC_not, u'http://schemas.xmlsoap.org/ws/2003/03/business-process/')), min_occurs=0L, max_occurs=None)
    )
tCorrelationSet._ContentModel = pyxb.binding.content.ParticleModel(tCorrelationSet._GroupModel, min_occurs=1, max_occurs=1)


tSource._GroupModel = pyxb.binding.content.GroupSequence(
    pyxb.binding.content.ParticleModel(pyxb.binding.content.Wildcard(process_contents=pyxb.binding.content.Wildcard.PC_lax, namespace_constraint=(pyxb.binding.content.Wildcard.NC_not, u'http://schemas.xmlsoap.org/ws/2003/03/business-process/')), min_occurs=0L, max_occurs=None)
    )
tSource._ContentModel = pyxb.binding.content.ParticleModel(tSource._GroupModel, min_occurs=1, max_occurs=1)


tLink._GroupModel = pyxb.binding.content.GroupSequence(
    pyxb.binding.content.ParticleModel(pyxb.binding.content.Wildcard(process_contents=pyxb.binding.content.Wildcard.PC_lax, namespace_constraint=(pyxb.binding.content.Wildcard.NC_not, u'http://schemas.xmlsoap.org/ws/2003/03/business-process/')), min_occurs=0L, max_occurs=None)
    )
tLink._ContentModel = pyxb.binding.content.ParticleModel(tLink._GroupModel, min_occurs=1, max_occurs=1)


tPartnerLink._GroupModel = pyxb.binding.content.GroupSequence(
    pyxb.binding.content.ParticleModel(pyxb.binding.content.Wildcard(process_contents=pyxb.binding.content.Wildcard.PC_lax, namespace_constraint=(pyxb.binding.content.Wildcard.NC_not, u'http://schemas.xmlsoap.org/ws/2003/03/business-process/')), min_occurs=0L, max_occurs=None)
    )
tPartnerLink._ContentModel = pyxb.binding.content.ParticleModel(tPartnerLink._GroupModel, min_occurs=1, max_occurs=1)
