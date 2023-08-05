# ./pyxb/bundles/wssplat/raw/wstop.py
# -*- coding: utf-8 -*-
# PyXB bindings for NM:4e8dbbb71a72b67c5dc95d408f0b903c3981ba86
# Generated 2012-11-01 15:13:38.677555 by PyXB version 1.1.5
# Namespace http://docs.oasis-open.org/wsn/t-1

import pyxb
import pyxb.binding
import pyxb.binding.saxer
import StringIO
import pyxb.utils.utility
import pyxb.utils.domutils
import sys

# Unique identifier for bindings created at the same time
_GenerationUID = pyxb.utils.utility.UniqueIdentifier('urn:uuid:9f847ca6-2460-11e2-941a-c8600024e903')

# Import bindings for namespaces imported into schema
import pyxb.binding.datatypes

Namespace = pyxb.namespace.NamespaceForURI(u'http://docs.oasis-open.org/wsn/t-1', create_if_missing=True)
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


# Atomic simple type: {http://docs.oasis-open.org/wsn/t-1}SimpleTopicExpression
class SimpleTopicExpression (pyxb.binding.datatypes.QName):

    """An atomic simple type."""

    _ExpandedName = pyxb.namespace.ExpandedName(Namespace, u'SimpleTopicExpression')
    _DefinitionLocation = pyxb.utils.utility.Location('/tmp/pyxbdist.RHB65sy/PyXB-1.1.5/pyxb/bundles/wssplat/schemas/wstop.xsd', 173, 2)
    _Documentation = None
SimpleTopicExpression._InitializeFacetMap()
Namespace.addCategoryObject('typeBinding', u'SimpleTopicExpression', SimpleTopicExpression)

# List simple type: [anonymous]
# superclasses pyxb.binding.datatypes.anySimpleType
class STD_ANON (pyxb.binding.basis.STD_list):

    """Simple type that is a list of pyxb.binding.datatypes.QName."""

    _ExpandedName = None
    _DefinitionLocation = pyxb.utils.utility.Location('/tmp/pyxbdist.RHB65sy/PyXB-1.1.5/pyxb/bundles/wssplat/schemas/wstop.xsd', 109, 10)
    _Documentation = None

    _ItemType = pyxb.binding.datatypes.QName
STD_ANON._InitializeFacetMap()

# Atomic simple type: {http://docs.oasis-open.org/wsn/t-1}FullTopicExpression
class FullTopicExpression (pyxb.binding.datatypes.token):

    """An atomic simple type."""

    _ExpandedName = pyxb.namespace.ExpandedName(Namespace, u'FullTopicExpression')
    _DefinitionLocation = pyxb.utils.utility.Location('/tmp/pyxbdist.RHB65sy/PyXB-1.1.5/pyxb/bundles/wssplat/schemas/wstop.xsd', 138, 2)
    _Documentation = None
FullTopicExpression._CF_pattern = pyxb.binding.facets.CF_pattern()
FullTopicExpression._CF_pattern.addPattern(pattern=u'([\\i-[:]][\\c-[:]]*:)?(//)?([\\i-[:]][\\c-[:]]*|\\*)((/|//)(([\\i-[:]][\\c-[:]]*:)?[\\i-[:]][\\c-[:]]*|\\*|[.]))*(\\|([\\i-[:]][\\c-[:]]*:)?(//)?([\\i-[:]][\\c-[:]]*|\\*)((/|//)(([\\i-[:]][\\c-[:]]*:)?[\\i-[:]][\\c-[:]]*|\\*|[.]))*)*')
FullTopicExpression._InitializeFacetMap(FullTopicExpression._CF_pattern)
Namespace.addCategoryObject('typeBinding', u'FullTopicExpression', FullTopicExpression)

# Atomic simple type: {http://docs.oasis-open.org/wsn/t-1}ConcreteTopicExpression
class ConcreteTopicExpression (pyxb.binding.datatypes.token):

    """An atomic simple type."""

    _ExpandedName = pyxb.namespace.ExpandedName(Namespace, u'ConcreteTopicExpression')
    _DefinitionLocation = pyxb.utils.utility.Location('/tmp/pyxbdist.RHB65sy/PyXB-1.1.5/pyxb/bundles/wssplat/schemas/wstop.xsd', 156, 2)
    _Documentation = None
ConcreteTopicExpression._CF_pattern = pyxb.binding.facets.CF_pattern()
ConcreteTopicExpression._CF_pattern.addPattern(pattern=u'(([\\i-[:]][\\c-[:]]*:)?[\\i-[:]][\\c-[:]]*)(/([\\i-[:]][\\c-[:]]*:)?[\\i-[:]][\\c-[:]]*)*')
ConcreteTopicExpression._InitializeFacetMap(ConcreteTopicExpression._CF_pattern)
Namespace.addCategoryObject('typeBinding', u'ConcreteTopicExpression', ConcreteTopicExpression)

# Complex type {http://docs.oasis-open.org/wsn/t-1}QueryExpressionType with content type MIXED
class QueryExpressionType (pyxb.binding.basis.complexTypeDefinition):
    _TypeDefinition = None
    _ContentTypeTag = pyxb.binding.basis.complexTypeDefinition._CT_MIXED
    _Abstract = False
    _ExpandedName = pyxb.namespace.ExpandedName(Namespace, u'QueryExpressionType')
    _DefinitionLocation = pyxb.utils.utility.Location('/tmp/pyxbdist.RHB65sy/PyXB-1.1.5/pyxb/bundles/wssplat/schemas/wstop.xsd', 42, 0)
    # Base type is pyxb.binding.datatypes.anyType
    
    # Attribute Dialect uses Python identifier Dialect
    __Dialect = pyxb.binding.content.AttributeUse(pyxb.namespace.ExpandedName(None, u'Dialect'), 'Dialect', '__httpdocs_oasis_open_orgwsnt_1_QueryExpressionType_Dialect', pyxb.binding.datatypes.anyURI, required=True)
    __Dialect._DeclarationLocation = pyxb.utils.utility.Location('/tmp/pyxbdist.RHB65sy/PyXB-1.1.5/pyxb/bundles/wssplat/schemas/wstop.xsd', 46, 2)
    __Dialect._UseLocation = pyxb.utils.utility.Location('/tmp/pyxbdist.RHB65sy/PyXB-1.1.5/pyxb/bundles/wssplat/schemas/wstop.xsd', 46, 2)
    
    Dialect = property(__Dialect.value, __Dialect.set, None, None)

    _HasWildcardElement = True

    _ElementMap = {
        
    }
    _AttributeMap = {
        __Dialect.name() : __Dialect
    }
Namespace.addCategoryObject('typeBinding', u'QueryExpressionType', QueryExpressionType)


# Complex type {http://docs.oasis-open.org/wsn/t-1}Documentation with content type MIXED
class Documentation (pyxb.binding.basis.complexTypeDefinition):
    _TypeDefinition = None
    _ContentTypeTag = pyxb.binding.basis.complexTypeDefinition._CT_MIXED
    _Abstract = False
    _ExpandedName = pyxb.namespace.ExpandedName(Namespace, u'Documentation')
    _DefinitionLocation = pyxb.utils.utility.Location('/tmp/pyxbdist.RHB65sy/PyXB-1.1.5/pyxb/bundles/wssplat/schemas/wstop.xsd', 26, 2)
    # Base type is pyxb.binding.datatypes.anyType
    _HasWildcardElement = True

    _ElementMap = {
        
    }
    _AttributeMap = {
        
    }
Namespace.addCategoryObject('typeBinding', u'Documentation', Documentation)


# Complex type {http://docs.oasis-open.org/wsn/t-1}ExtensibleDocumented with content type ELEMENT_ONLY
class ExtensibleDocumented (pyxb.binding.basis.complexTypeDefinition):
    _TypeDefinition = None
    _ContentTypeTag = pyxb.binding.basis.complexTypeDefinition._CT_ELEMENT_ONLY
    _Abstract = True
    _ExpandedName = pyxb.namespace.ExpandedName(Namespace, u'ExtensibleDocumented')
    _DefinitionLocation = pyxb.utils.utility.Location('/tmp/pyxbdist.RHB65sy/PyXB-1.1.5/pyxb/bundles/wssplat/schemas/wstop.xsd', 33, 2)
    # Base type is pyxb.binding.datatypes.anyType
    
    # Element {http://docs.oasis-open.org/wsn/t-1}documentation uses Python identifier documentation
    __documentation = pyxb.binding.content.ElementUse(pyxb.namespace.ExpandedName(Namespace, u'documentation'), 'documentation', '__httpdocs_oasis_open_orgwsnt_1_ExtensibleDocumented_httpdocs_oasis_open_orgwsnt_1documentation', False)
    __documentation._DeclarationLocation = pyxb.utils.utility.Location('/tmp/pyxbdist.RHB65sy/PyXB-1.1.5/pyxb/bundles/wssplat/schemas/wstop.xsd', 36, 6)
    __documentation._UseLocation = pyxb.utils.utility.Location('/tmp/pyxbdist.RHB65sy/PyXB-1.1.5/pyxb/bundles/wssplat/schemas/wstop.xsd', 35, 4)

    
    documentation = property(__documentation.value, __documentation.set, None, None)

    _AttributeWildcard = pyxb.binding.content.Wildcard(process_contents=pyxb.binding.content.Wildcard.PC_lax, namespace_constraint=(pyxb.binding.content.Wildcard.NC_not, u'http://docs.oasis-open.org/wsn/t-1'))

    _ElementMap = {
        __documentation.name() : __documentation
    }
    _AttributeMap = {
        
    }
Namespace.addCategoryObject('typeBinding', u'ExtensibleDocumented', ExtensibleDocumented)


# Complex type {http://docs.oasis-open.org/wsn/t-1}TopicNamespaceType with content type ELEMENT_ONLY
class TopicNamespaceType (ExtensibleDocumented):
    _TypeDefinition = None
    _ContentTypeTag = pyxb.binding.basis.complexTypeDefinition._CT_ELEMENT_ONLY
    _Abstract = False
    _ExpandedName = pyxb.namespace.ExpandedName(Namespace, u'TopicNamespaceType')
    _DefinitionLocation = pyxb.utils.utility.Location('/tmp/pyxbdist.RHB65sy/PyXB-1.1.5/pyxb/bundles/wssplat/schemas/wstop.xsd', 50, 2)
    # Base type is ExtensibleDocumented
    
    # Element {http://docs.oasis-open.org/wsn/t-1}Topic uses Python identifier Topic
    __Topic = pyxb.binding.content.ElementUse(pyxb.namespace.ExpandedName(Namespace, u'Topic'), 'Topic', '__httpdocs_oasis_open_orgwsnt_1_TopicNamespaceType_httpdocs_oasis_open_orgwsnt_1Topic', True)
    __Topic._DeclarationLocation = pyxb.utils.utility.Location('/tmp/pyxbdist.RHB65sy/PyXB-1.1.5/pyxb/bundles/wssplat/schemas/wstop.xsd', 54, 11)
    __Topic._UseLocation = None

    
    Topic = property(__Topic.value, __Topic.set, None, None)

    
    # Element documentation ({http://docs.oasis-open.org/wsn/t-1}documentation) inherited from {http://docs.oasis-open.org/wsn/t-1}ExtensibleDocumented
    
    # Attribute targetNamespace uses Python identifier targetNamespace
    __targetNamespace = pyxb.binding.content.AttributeUse(pyxb.namespace.ExpandedName(None, u'targetNamespace'), 'targetNamespace', '__httpdocs_oasis_open_orgwsnt_1_TopicNamespaceType_targetNamespace', pyxb.binding.datatypes.anyURI, required=True)
    __targetNamespace._DeclarationLocation = pyxb.utils.utility.Location('/tmp/pyxbdist.RHB65sy/PyXB-1.1.5/pyxb/bundles/wssplat/schemas/wstop.xsd', 69, 9)
    __targetNamespace._UseLocation = pyxb.utils.utility.Location('/tmp/pyxbdist.RHB65sy/PyXB-1.1.5/pyxb/bundles/wssplat/schemas/wstop.xsd', 69, 9)
    
    targetNamespace = property(__targetNamespace.value, __targetNamespace.set, None, None)

    
    # Attribute final uses Python identifier final
    __final = pyxb.binding.content.AttributeUse(pyxb.namespace.ExpandedName(None, u'final'), 'final', '__httpdocs_oasis_open_orgwsnt_1_TopicNamespaceType_final', pyxb.binding.datatypes.boolean, unicode_default=u'false')
    __final._DeclarationLocation = pyxb.utils.utility.Location('/tmp/pyxbdist.RHB65sy/PyXB-1.1.5/pyxb/bundles/wssplat/schemas/wstop.xsd', 71, 9)
    __final._UseLocation = pyxb.utils.utility.Location('/tmp/pyxbdist.RHB65sy/PyXB-1.1.5/pyxb/bundles/wssplat/schemas/wstop.xsd', 71, 9)
    
    final = property(__final.value, __final.set, None, None)

    
    # Attribute name uses Python identifier name
    __name = pyxb.binding.content.AttributeUse(pyxb.namespace.ExpandedName(None, u'name'), 'name', '__httpdocs_oasis_open_orgwsnt_1_TopicNamespaceType_name', pyxb.binding.datatypes.NCName)
    __name._DeclarationLocation = pyxb.utils.utility.Location('/tmp/pyxbdist.RHB65sy/PyXB-1.1.5/pyxb/bundles/wssplat/schemas/wstop.xsd', 68, 9)
    __name._UseLocation = pyxb.utils.utility.Location('/tmp/pyxbdist.RHB65sy/PyXB-1.1.5/pyxb/bundles/wssplat/schemas/wstop.xsd', 68, 9)
    
    name = property(__name.value, __name.set, None, None)

    _AttributeWildcard = pyxb.binding.content.Wildcard(process_contents=pyxb.binding.content.Wildcard.PC_lax, namespace_constraint=(pyxb.binding.content.Wildcard.NC_not, u'http://docs.oasis-open.org/wsn/t-1'))
    _HasWildcardElement = True

    _ElementMap = ExtensibleDocumented._ElementMap.copy()
    _ElementMap.update({
        __Topic.name() : __Topic
    })
    _AttributeMap = ExtensibleDocumented._AttributeMap.copy()
    _AttributeMap.update({
        __targetNamespace.name() : __targetNamespace,
        __final.name() : __final,
        __name.name() : __name
    })
Namespace.addCategoryObject('typeBinding', u'TopicNamespaceType', TopicNamespaceType)


# Complex type {http://docs.oasis-open.org/wsn/t-1}TopicType with content type ELEMENT_ONLY
class TopicType (ExtensibleDocumented):
    _TypeDefinition = None
    _ContentTypeTag = pyxb.binding.basis.complexTypeDefinition._CT_ELEMENT_ONLY
    _Abstract = False
    _ExpandedName = pyxb.namespace.ExpandedName(Namespace, u'TopicType')
    _DefinitionLocation = pyxb.utils.utility.Location('/tmp/pyxbdist.RHB65sy/PyXB-1.1.5/pyxb/bundles/wssplat/schemas/wstop.xsd', 90, 2)
    # Base type is ExtensibleDocumented
    
    # Element documentation ({http://docs.oasis-open.org/wsn/t-1}documentation) inherited from {http://docs.oasis-open.org/wsn/t-1}ExtensibleDocumented
    
    # Element {http://docs.oasis-open.org/wsn/t-1}MessagePattern uses Python identifier MessagePattern
    __MessagePattern = pyxb.binding.content.ElementUse(pyxb.namespace.ExpandedName(Namespace, u'MessagePattern'), 'MessagePattern', '__httpdocs_oasis_open_orgwsnt_1_TopicType_httpdocs_oasis_open_orgwsnt_1MessagePattern', False)
    __MessagePattern._DeclarationLocation = pyxb.utils.utility.Location('/tmp/pyxbdist.RHB65sy/PyXB-1.1.5/pyxb/bundles/wssplat/schemas/wstop.xsd', 94, 10)
    __MessagePattern._UseLocation = None

    
    MessagePattern = property(__MessagePattern.value, __MessagePattern.set, None, None)

    
    # Element {http://docs.oasis-open.org/wsn/t-1}Topic uses Python identifier Topic
    __Topic = pyxb.binding.content.ElementUse(pyxb.namespace.ExpandedName(Namespace, u'Topic'), 'Topic', '__httpdocs_oasis_open_orgwsnt_1_TopicType_httpdocs_oasis_open_orgwsnt_1Topic', True)
    __Topic._DeclarationLocation = pyxb.utils.utility.Location('/tmp/pyxbdist.RHB65sy/PyXB-1.1.5/pyxb/bundles/wssplat/schemas/wstop.xsd', 97, 10)
    __Topic._UseLocation = None

    
    Topic = property(__Topic.value, __Topic.set, None, None)

    
    # Attribute final uses Python identifier final
    __final = pyxb.binding.content.AttributeUse(pyxb.namespace.ExpandedName(None, u'final'), 'final', '__httpdocs_oasis_open_orgwsnt_1_TopicType_final', pyxb.binding.datatypes.boolean, unicode_default=u'false')
    __final._DeclarationLocation = pyxb.utils.utility.Location('/tmp/pyxbdist.RHB65sy/PyXB-1.1.5/pyxb/bundles/wssplat/schemas/wstop.xsd', 113, 8)
    __final._UseLocation = pyxb.utils.utility.Location('/tmp/pyxbdist.RHB65sy/PyXB-1.1.5/pyxb/bundles/wssplat/schemas/wstop.xsd', 113, 8)
    
    final = property(__final.value, __final.set, None, None)

    
    # Attribute messageTypes uses Python identifier messageTypes
    __messageTypes = pyxb.binding.content.AttributeUse(pyxb.namespace.ExpandedName(None, u'messageTypes'), 'messageTypes', '__httpdocs_oasis_open_orgwsnt_1_TopicType_messageTypes', STD_ANON)
    __messageTypes._DeclarationLocation = pyxb.utils.utility.Location('/tmp/pyxbdist.RHB65sy/PyXB-1.1.5/pyxb/bundles/wssplat/schemas/wstop.xsd', 108, 8)
    __messageTypes._UseLocation = pyxb.utils.utility.Location('/tmp/pyxbdist.RHB65sy/PyXB-1.1.5/pyxb/bundles/wssplat/schemas/wstop.xsd', 108, 8)
    
    messageTypes = property(__messageTypes.value, __messageTypes.set, None, None)

    
    # Attribute name uses Python identifier name
    __name = pyxb.binding.content.AttributeUse(pyxb.namespace.ExpandedName(None, u'name'), 'name', '__httpdocs_oasis_open_orgwsnt_1_TopicType_name', pyxb.binding.datatypes.NCName, required=True)
    __name._DeclarationLocation = pyxb.utils.utility.Location('/tmp/pyxbdist.RHB65sy/PyXB-1.1.5/pyxb/bundles/wssplat/schemas/wstop.xsd', 107, 8)
    __name._UseLocation = pyxb.utils.utility.Location('/tmp/pyxbdist.RHB65sy/PyXB-1.1.5/pyxb/bundles/wssplat/schemas/wstop.xsd', 107, 8)
    
    name = property(__name.value, __name.set, None, None)

    _AttributeWildcard = pyxb.binding.content.Wildcard(process_contents=pyxb.binding.content.Wildcard.PC_lax, namespace_constraint=(pyxb.binding.content.Wildcard.NC_not, u'http://docs.oasis-open.org/wsn/t-1'))
    _HasWildcardElement = True

    _ElementMap = ExtensibleDocumented._ElementMap.copy()
    _ElementMap.update({
        __MessagePattern.name() : __MessagePattern,
        __Topic.name() : __Topic
    })
    _AttributeMap = ExtensibleDocumented._AttributeMap.copy()
    _AttributeMap.update({
        __final.name() : __final,
        __messageTypes.name() : __messageTypes,
        __name.name() : __name
    })
Namespace.addCategoryObject('typeBinding', u'TopicType', TopicType)


# Complex type {http://docs.oasis-open.org/wsn/t-1}TopicSetType with content type ELEMENT_ONLY
class TopicSetType (ExtensibleDocumented):
    _TypeDefinition = None
    _ContentTypeTag = pyxb.binding.basis.complexTypeDefinition._CT_ELEMENT_ONLY
    _Abstract = False
    _ExpandedName = pyxb.namespace.ExpandedName(Namespace, u'TopicSetType')
    _DefinitionLocation = pyxb.utils.utility.Location('/tmp/pyxbdist.RHB65sy/PyXB-1.1.5/pyxb/bundles/wssplat/schemas/wstop.xsd', 121, 2)
    # Base type is ExtensibleDocumented
    
    # Element documentation ({http://docs.oasis-open.org/wsn/t-1}documentation) inherited from {http://docs.oasis-open.org/wsn/t-1}ExtensibleDocumented
    _AttributeWildcard = pyxb.binding.content.Wildcard(process_contents=pyxb.binding.content.Wildcard.PC_lax, namespace_constraint=(pyxb.binding.content.Wildcard.NC_not, u'http://docs.oasis-open.org/wsn/t-1'))
    _HasWildcardElement = True

    _ElementMap = ExtensibleDocumented._ElementMap.copy()
    _ElementMap.update({
        
    })
    _AttributeMap = ExtensibleDocumented._AttributeMap.copy()
    _AttributeMap.update({
        
    })
Namespace.addCategoryObject('typeBinding', u'TopicSetType', TopicSetType)


# Complex type [anonymous] with content type ELEMENT_ONLY
class CTD_ANON (TopicType):
    _TypeDefinition = None
    _ContentTypeTag = pyxb.binding.basis.complexTypeDefinition._CT_ELEMENT_ONLY
    _Abstract = False
    _ExpandedName = None
    _DefinitionLocation = pyxb.utils.utility.Location('/tmp/pyxbdist.RHB65sy/PyXB-1.1.5/pyxb/bundles/wssplat/schemas/wstop.xsd', 56, 14)
    # Base type is TopicType
    
    # Element documentation ({http://docs.oasis-open.org/wsn/t-1}documentation) inherited from {http://docs.oasis-open.org/wsn/t-1}ExtensibleDocumented
    
    # Element MessagePattern ({http://docs.oasis-open.org/wsn/t-1}MessagePattern) inherited from {http://docs.oasis-open.org/wsn/t-1}TopicType
    
    # Element Topic ({http://docs.oasis-open.org/wsn/t-1}Topic) inherited from {http://docs.oasis-open.org/wsn/t-1}TopicType
    
    # Attribute final inherited from {http://docs.oasis-open.org/wsn/t-1}TopicType
    
    # Attribute name inherited from {http://docs.oasis-open.org/wsn/t-1}TopicType
    
    # Attribute messageTypes inherited from {http://docs.oasis-open.org/wsn/t-1}TopicType
    
    # Attribute parent uses Python identifier parent
    __parent = pyxb.binding.content.AttributeUse(pyxb.namespace.ExpandedName(None, u'parent'), 'parent', '__httpdocs_oasis_open_orgwsnt_1_CTD_ANON_parent', ConcreteTopicExpression)
    __parent._DeclarationLocation = pyxb.utils.utility.Location('/tmp/pyxbdist.RHB65sy/PyXB-1.1.5/pyxb/bundles/wssplat/schemas/wstop.xsd', 59, 19)
    __parent._UseLocation = pyxb.utils.utility.Location('/tmp/pyxbdist.RHB65sy/PyXB-1.1.5/pyxb/bundles/wssplat/schemas/wstop.xsd', 59, 19)
    
    parent = property(__parent.value, __parent.set, None, None)

    _AttributeWildcard = pyxb.binding.content.Wildcard(process_contents=pyxb.binding.content.Wildcard.PC_lax, namespace_constraint=(pyxb.binding.content.Wildcard.NC_not, u'http://docs.oasis-open.org/wsn/t-1'))
    _HasWildcardElement = True

    _ElementMap = TopicType._ElementMap.copy()
    _ElementMap.update({
        
    })
    _AttributeMap = TopicType._AttributeMap.copy()
    _AttributeMap.update({
        __parent.name() : __parent
    })



TopicNamespace = pyxb.binding.basis.element(pyxb.namespace.ExpandedName(Namespace, u'TopicNamespace'), TopicNamespaceType)
Namespace.addCategoryObject('elementBinding', TopicNamespace.name().localName(), TopicNamespace)

TopicSet = pyxb.binding.basis.element(pyxb.namespace.ExpandedName(Namespace, u'TopicSet'), TopicSetType)
Namespace.addCategoryObject('elementBinding', TopicSet.name().localName(), TopicSet)


QueryExpressionType._GroupModel = pyxb.binding.content.GroupSequence(
    pyxb.binding.content.ParticleModel(pyxb.binding.content.Wildcard(process_contents=pyxb.binding.content.Wildcard.PC_lax, namespace_constraint=pyxb.binding.content.Wildcard.NC_any), min_occurs=0L, max_occurs=1L)
    )
QueryExpressionType._ContentModel = pyxb.binding.content.ParticleModel(QueryExpressionType._GroupModel, min_occurs=1, max_occurs=1)


Documentation._GroupModel = pyxb.binding.content.GroupSequence(
    pyxb.binding.content.ParticleModel(pyxb.binding.content.Wildcard(process_contents=pyxb.binding.content.Wildcard.PC_lax, namespace_constraint=pyxb.binding.content.Wildcard.NC_any), min_occurs=0L, max_occurs=None)
    )
Documentation._ContentModel = pyxb.binding.content.ParticleModel(Documentation._GroupModel, min_occurs=1, max_occurs=1)



ExtensibleDocumented._AddElement(pyxb.binding.basis.element(pyxb.namespace.ExpandedName(Namespace, u'documentation'), Documentation, scope=ExtensibleDocumented))
ExtensibleDocumented._GroupModel = pyxb.binding.content.GroupSequence(
    pyxb.binding.content.ParticleModel(ExtensibleDocumented._UseForTag(pyxb.namespace.ExpandedName(Namespace, u'documentation')), min_occurs=0L, max_occurs=1)
    )
ExtensibleDocumented._ContentModel = pyxb.binding.content.ParticleModel(ExtensibleDocumented._GroupModel, min_occurs=1, max_occurs=1)



TopicNamespaceType._AddElement(pyxb.binding.basis.element(pyxb.namespace.ExpandedName(Namespace, u'Topic'), CTD_ANON, scope=TopicNamespaceType))
TopicNamespaceType._GroupModel_ = pyxb.binding.content.GroupSequence(
    pyxb.binding.content.ParticleModel(TopicNamespaceType._UseForTag(pyxb.namespace.ExpandedName(Namespace, u'documentation')), min_occurs=0L, max_occurs=1)
    )
TopicNamespaceType._GroupModel_2 = pyxb.binding.content.GroupSequence(
    pyxb.binding.content.ParticleModel(TopicNamespaceType._UseForTag(pyxb.namespace.ExpandedName(Namespace, u'Topic')), min_occurs=0L, max_occurs=None),
    pyxb.binding.content.ParticleModel(pyxb.binding.content.Wildcard(process_contents=pyxb.binding.content.Wildcard.PC_lax, namespace_constraint=(pyxb.binding.content.Wildcard.NC_not, u'http://docs.oasis-open.org/wsn/t-1')), min_occurs=0L, max_occurs=None)
    )
TopicNamespaceType._GroupModel = pyxb.binding.content.GroupSequence(
    pyxb.binding.content.ParticleModel(TopicNamespaceType._GroupModel_, min_occurs=1, max_occurs=1),
    pyxb.binding.content.ParticleModel(TopicNamespaceType._GroupModel_2, min_occurs=1, max_occurs=1)
    )
TopicNamespaceType._ContentModel = pyxb.binding.content.ParticleModel(TopicNamespaceType._GroupModel, min_occurs=1, max_occurs=1)



TopicType._AddElement(pyxb.binding.basis.element(pyxb.namespace.ExpandedName(Namespace, u'MessagePattern'), QueryExpressionType, scope=TopicType))

TopicType._AddElement(pyxb.binding.basis.element(pyxb.namespace.ExpandedName(Namespace, u'Topic'), TopicType, scope=TopicType))
TopicType._GroupModel_ = pyxb.binding.content.GroupSequence(
    pyxb.binding.content.ParticleModel(TopicType._UseForTag(pyxb.namespace.ExpandedName(Namespace, u'documentation')), min_occurs=0L, max_occurs=1)
    )
TopicType._GroupModel_2 = pyxb.binding.content.GroupSequence(
    pyxb.binding.content.ParticleModel(TopicType._UseForTag(pyxb.namespace.ExpandedName(Namespace, u'MessagePattern')), min_occurs=0L, max_occurs=1L),
    pyxb.binding.content.ParticleModel(TopicType._UseForTag(pyxb.namespace.ExpandedName(Namespace, u'Topic')), min_occurs=0L, max_occurs=None),
    pyxb.binding.content.ParticleModel(pyxb.binding.content.Wildcard(process_contents=pyxb.binding.content.Wildcard.PC_strict, namespace_constraint=(pyxb.binding.content.Wildcard.NC_not, u'http://docs.oasis-open.org/wsn/t-1')), min_occurs=0L, max_occurs=None)
    )
TopicType._GroupModel = pyxb.binding.content.GroupSequence(
    pyxb.binding.content.ParticleModel(TopicType._GroupModel_, min_occurs=1, max_occurs=1),
    pyxb.binding.content.ParticleModel(TopicType._GroupModel_2, min_occurs=1, max_occurs=1)
    )
TopicType._ContentModel = pyxb.binding.content.ParticleModel(TopicType._GroupModel, min_occurs=1, max_occurs=1)


TopicSetType._GroupModel_ = pyxb.binding.content.GroupSequence(
    pyxb.binding.content.ParticleModel(TopicSetType._UseForTag(pyxb.namespace.ExpandedName(Namespace, u'documentation')), min_occurs=0L, max_occurs=1)
    )
TopicSetType._GroupModel_2 = pyxb.binding.content.GroupSequence(
    pyxb.binding.content.ParticleModel(pyxb.binding.content.Wildcard(process_contents=pyxb.binding.content.Wildcard.PC_lax, namespace_constraint=(pyxb.binding.content.Wildcard.NC_not, u'http://docs.oasis-open.org/wsn/t-1')), min_occurs=0L, max_occurs=None)
    )
TopicSetType._GroupModel = pyxb.binding.content.GroupSequence(
    pyxb.binding.content.ParticleModel(TopicSetType._GroupModel_, min_occurs=1, max_occurs=1),
    pyxb.binding.content.ParticleModel(TopicSetType._GroupModel_2, min_occurs=1, max_occurs=1)
    )
TopicSetType._ContentModel = pyxb.binding.content.ParticleModel(TopicSetType._GroupModel, min_occurs=1, max_occurs=1)


CTD_ANON._GroupModel_ = pyxb.binding.content.GroupSequence(
    pyxb.binding.content.ParticleModel(CTD_ANON._UseForTag(pyxb.namespace.ExpandedName(Namespace, u'documentation')), min_occurs=0L, max_occurs=1)
    )
CTD_ANON._GroupModel_2 = pyxb.binding.content.GroupSequence(
    pyxb.binding.content.ParticleModel(CTD_ANON._UseForTag(pyxb.namespace.ExpandedName(Namespace, u'MessagePattern')), min_occurs=0L, max_occurs=1L),
    pyxb.binding.content.ParticleModel(CTD_ANON._UseForTag(pyxb.namespace.ExpandedName(Namespace, u'Topic')), min_occurs=0L, max_occurs=None),
    pyxb.binding.content.ParticleModel(pyxb.binding.content.Wildcard(process_contents=pyxb.binding.content.Wildcard.PC_strict, namespace_constraint=(pyxb.binding.content.Wildcard.NC_not, u'http://docs.oasis-open.org/wsn/t-1')), min_occurs=0L, max_occurs=None)
    )
CTD_ANON._GroupModel = pyxb.binding.content.GroupSequence(
    pyxb.binding.content.ParticleModel(CTD_ANON._GroupModel_, min_occurs=1, max_occurs=1),
    pyxb.binding.content.ParticleModel(CTD_ANON._GroupModel_2, min_occurs=1, max_occurs=1)
    )
CTD_ANON._ContentModel = pyxb.binding.content.ParticleModel(CTD_ANON._GroupModel, min_occurs=1, max_occurs=1)
