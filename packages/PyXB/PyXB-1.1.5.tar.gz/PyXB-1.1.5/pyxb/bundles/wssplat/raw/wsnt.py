# ./pyxb/bundles/wssplat/raw/wsnt.py
# -*- coding: utf-8 -*-
# PyXB bindings for NM:0e37c4ef493bd279efcad02c74006a905f5748fd
# Generated 2012-11-01 15:13:39.138206 by PyXB version 1.1.5
# Namespace http://docs.oasis-open.org/wsn/b-2

import pyxb
import pyxb.binding
import pyxb.binding.saxer
import StringIO
import pyxb.utils.utility
import pyxb.utils.domutils
import sys

# Unique identifier for bindings created at the same time
_GenerationUID = pyxb.utils.utility.UniqueIdentifier('urn:uuid:9fc61c4c-2460-11e2-ad39-c8600024e903')

# Import bindings for namespaces imported into schema
import pyxb.binding.datatypes
import pyxb.bundles.wssplat.wsa
import pyxb.bundles.wssplat.wsrf_bf
import pyxb.bundles.wssplat.wstop

Namespace = pyxb.namespace.NamespaceForURI(u'http://docs.oasis-open.org/wsn/b-2', create_if_missing=True)
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


# Union simple type: {http://docs.oasis-open.org/wsn/b-2}AbsoluteOrRelativeTimeType
# superclasses pyxb.binding.datatypes.anySimpleType
class AbsoluteOrRelativeTimeType (pyxb.binding.basis.STD_union):

    """Simple type that is a union of pyxb.binding.datatypes.dateTime, pyxb.binding.datatypes.duration."""

    _ExpandedName = pyxb.namespace.ExpandedName(Namespace, u'AbsoluteOrRelativeTimeType')
    _DefinitionLocation = pyxb.utils.utility.Location('/tmp/pyxbdist.RHB65sy/PyXB-1.1.5/pyxb/bundles/wssplat/schemas/wsnt.xsd', 158, 2)
    _Documentation = None

    _MemberTypes = ( pyxb.binding.datatypes.dateTime, pyxb.binding.datatypes.duration, )
AbsoluteOrRelativeTimeType._CF_pattern = pyxb.binding.facets.CF_pattern()
AbsoluteOrRelativeTimeType._CF_enumeration = pyxb.binding.facets.CF_enumeration(value_datatype=AbsoluteOrRelativeTimeType)
AbsoluteOrRelativeTimeType._InitializeFacetMap(AbsoluteOrRelativeTimeType._CF_pattern,
   AbsoluteOrRelativeTimeType._CF_enumeration)
Namespace.addCategoryObject('typeBinding', u'AbsoluteOrRelativeTimeType', AbsoluteOrRelativeTimeType)

# Complex type {http://docs.oasis-open.org/wsn/b-2}FilterType with content type ELEMENT_ONLY
class FilterType (pyxb.binding.basis.complexTypeDefinition):
    _TypeDefinition = None
    _ContentTypeTag = pyxb.binding.basis.complexTypeDefinition._CT_ELEMENT_ONLY
    _Abstract = False
    _ExpandedName = pyxb.namespace.ExpandedName(Namespace, u'FilterType')
    _DefinitionLocation = pyxb.utils.utility.Location('/tmp/pyxbdist.RHB65sy/PyXB-1.1.5/pyxb/bundles/wssplat/schemas/wsnt.xsd', 57, 2)
    # Base type is pyxb.binding.datatypes.anyType
    _HasWildcardElement = True

    _ElementMap = {
        
    }
    _AttributeMap = {
        
    }
Namespace.addCategoryObject('typeBinding', u'FilterType', FilterType)


# Complex type {http://docs.oasis-open.org/wsn/b-2}SubscriptionPolicyType with content type ELEMENT_ONLY
class SubscriptionPolicyType (pyxb.binding.basis.complexTypeDefinition):
    _TypeDefinition = None
    _ContentTypeTag = pyxb.binding.basis.complexTypeDefinition._CT_ELEMENT_ONLY
    _Abstract = False
    _ExpandedName = pyxb.namespace.ExpandedName(Namespace, u'SubscriptionPolicyType')
    _DefinitionLocation = pyxb.utils.utility.Location('/tmp/pyxbdist.RHB65sy/PyXB-1.1.5/pyxb/bundles/wssplat/schemas/wsnt.xsd', 63, 2)
    # Base type is pyxb.binding.datatypes.anyType
    _HasWildcardElement = True

    _ElementMap = {
        
    }
    _AttributeMap = {
        
    }
Namespace.addCategoryObject('typeBinding', u'SubscriptionPolicyType', SubscriptionPolicyType)


# Complex type [anonymous] with content type ELEMENT_ONLY
class CTD_ANON (pyxb.binding.basis.complexTypeDefinition):
    _TypeDefinition = None
    _ContentTypeTag = pyxb.binding.basis.complexTypeDefinition._CT_ELEMENT_ONLY
    _Abstract = False
    _ExpandedName = None
    _DefinitionLocation = pyxb.utils.utility.Location('/tmp/pyxbdist.RHB65sy/PyXB-1.1.5/pyxb/bundles/wssplat/schemas/wsnt.xsd', 100, 4)
    # Base type is pyxb.binding.datatypes.anyType
    
    # Element {http://docs.oasis-open.org/wsn/b-2}ConsumerReference uses Python identifier ConsumerReference
    __ConsumerReference = pyxb.binding.content.ElementUse(pyxb.namespace.ExpandedName(Namespace, u'ConsumerReference'), 'ConsumerReference', '__httpdocs_oasis_open_orgwsnb_2_CTD_ANON_httpdocs_oasis_open_orgwsnb_2ConsumerReference', False)
    __ConsumerReference._DeclarationLocation = pyxb.utils.utility.Location('/tmp/pyxbdist.RHB65sy/PyXB-1.1.5/pyxb/bundles/wssplat/schemas/wsnt.xsd', 91, 2)
    __ConsumerReference._UseLocation = pyxb.utils.utility.Location('/tmp/pyxbdist.RHB65sy/PyXB-1.1.5/pyxb/bundles/wssplat/schemas/wsnt.xsd', 101, 6)

    
    ConsumerReference = property(__ConsumerReference.value, __ConsumerReference.set, None, None)

    
    # Element {http://docs.oasis-open.org/wsn/b-2}CreationTime uses Python identifier CreationTime
    __CreationTime = pyxb.binding.content.ElementUse(pyxb.namespace.ExpandedName(Namespace, u'CreationTime'), 'CreationTime', '__httpdocs_oasis_open_orgwsnb_2_CTD_ANON_httpdocs_oasis_open_orgwsnb_2CreationTime', False)
    __CreationTime._DeclarationLocation = pyxb.utils.utility.Location('/tmp/pyxbdist.RHB65sy/PyXB-1.1.5/pyxb/bundles/wssplat/schemas/wsnt.xsd', 97, 2)
    __CreationTime._UseLocation = pyxb.utils.utility.Location('/tmp/pyxbdist.RHB65sy/PyXB-1.1.5/pyxb/bundles/wssplat/schemas/wsnt.xsd', 101, 6)

    
    CreationTime = property(__CreationTime.value, __CreationTime.set, None, None)

    
    # Element {http://docs.oasis-open.org/wsn/b-2}SubscriptionPolicy uses Python identifier SubscriptionPolicy
    __SubscriptionPolicy = pyxb.binding.content.ElementUse(pyxb.namespace.ExpandedName(Namespace, u'SubscriptionPolicy'), 'SubscriptionPolicy', '__httpdocs_oasis_open_orgwsnb_2_CTD_ANON_httpdocs_oasis_open_orgwsnb_2SubscriptionPolicy', False)
    __SubscriptionPolicy._DeclarationLocation = pyxb.utils.utility.Location('/tmp/pyxbdist.RHB65sy/PyXB-1.1.5/pyxb/bundles/wssplat/schemas/wsnt.xsd', 94, 2)
    __SubscriptionPolicy._UseLocation = pyxb.utils.utility.Location('/tmp/pyxbdist.RHB65sy/PyXB-1.1.5/pyxb/bundles/wssplat/schemas/wsnt.xsd', 101, 6)

    
    SubscriptionPolicy = property(__SubscriptionPolicy.value, __SubscriptionPolicy.set, None, None)

    
    # Element {http://docs.oasis-open.org/wsn/b-2}Filter uses Python identifier Filter
    __Filter = pyxb.binding.content.ElementUse(pyxb.namespace.ExpandedName(Namespace, u'Filter'), 'Filter', '__httpdocs_oasis_open_orgwsnb_2_CTD_ANON_httpdocs_oasis_open_orgwsnb_2Filter', False)
    __Filter._DeclarationLocation = pyxb.utils.utility.Location('/tmp/pyxbdist.RHB65sy/PyXB-1.1.5/pyxb/bundles/wssplat/schemas/wsnt.xsd', 93, 2)
    __Filter._UseLocation = pyxb.utils.utility.Location('/tmp/pyxbdist.RHB65sy/PyXB-1.1.5/pyxb/bundles/wssplat/schemas/wsnt.xsd', 101, 6)

    
    Filter = property(__Filter.value, __Filter.set, None, None)


    _ElementMap = {
        __ConsumerReference.name() : __ConsumerReference,
        __CreationTime.name() : __CreationTime,
        __SubscriptionPolicy.name() : __SubscriptionPolicy,
        __Filter.name() : __Filter
    }
    _AttributeMap = {
        
    }



# Complex type {http://docs.oasis-open.org/wsn/b-2}MultipleTopicsSpecifiedFaultType with content type ELEMENT_ONLY
class MultipleTopicsSpecifiedFaultType (pyxb.bundles.wssplat.wsrf_bf.BaseFaultType):
    _TypeDefinition = None
    _ContentTypeTag = pyxb.binding.basis.complexTypeDefinition._CT_ELEMENT_ONLY
    _Abstract = False
    _ExpandedName = pyxb.namespace.ExpandedName(Namespace, u'MultipleTopicsSpecifiedFaultType')
    _DefinitionLocation = pyxb.utils.utility.Location('/tmp/pyxbdist.RHB65sy/PyXB-1.1.5/pyxb/bundles/wssplat/schemas/wsnt.xsd', 284, 2)
    # Base type is pyxb.bundles.wssplat.wsrf_bf.BaseFaultType
    
    # Element ErrorCode ({http://docs.oasis-open.org/wsrf/bf-2}ErrorCode) inherited from {http://docs.oasis-open.org/wsrf/bf-2}BaseFaultType
    
    # Element Originator ({http://docs.oasis-open.org/wsrf/bf-2}Originator) inherited from {http://docs.oasis-open.org/wsrf/bf-2}BaseFaultType
    
    # Element FaultCause ({http://docs.oasis-open.org/wsrf/bf-2}FaultCause) inherited from {http://docs.oasis-open.org/wsrf/bf-2}BaseFaultType
    
    # Element Description ({http://docs.oasis-open.org/wsrf/bf-2}Description) inherited from {http://docs.oasis-open.org/wsrf/bf-2}BaseFaultType
    
    # Element Timestamp ({http://docs.oasis-open.org/wsrf/bf-2}Timestamp) inherited from {http://docs.oasis-open.org/wsrf/bf-2}BaseFaultType
    _AttributeWildcard = pyxb.binding.content.Wildcard(process_contents=pyxb.binding.content.Wildcard.PC_lax, namespace_constraint=(pyxb.binding.content.Wildcard.NC_not, u'http://docs.oasis-open.org/wsrf/bf-2'))
    _HasWildcardElement = True

    _ElementMap = pyxb.bundles.wssplat.wsrf_bf.BaseFaultType._ElementMap.copy()
    _ElementMap.update({
        
    })
    _AttributeMap = pyxb.bundles.wssplat.wsrf_bf.BaseFaultType._AttributeMap.copy()
    _AttributeMap.update({
        
    })
Namespace.addCategoryObject('typeBinding', u'MultipleTopicsSpecifiedFaultType', MultipleTopicsSpecifiedFaultType)


# Complex type [anonymous] with content type ELEMENT_ONLY
class CTD_ANON_ (pyxb.binding.basis.complexTypeDefinition):
    _TypeDefinition = None
    _ContentTypeTag = pyxb.binding.basis.complexTypeDefinition._CT_ELEMENT_ONLY
    _Abstract = False
    _ExpandedName = None
    _DefinitionLocation = pyxb.utils.utility.Location('/tmp/pyxbdist.RHB65sy/PyXB-1.1.5/pyxb/bundles/wssplat/schemas/wsnt.xsd', 231, 4)
    # Base type is pyxb.binding.datatypes.anyType
    _HasWildcardElement = True

    _ElementMap = {
        
    }
    _AttributeMap = {
        
    }



# Complex type [anonymous] with content type ELEMENT_ONLY
class CTD_ANON_2 (pyxb.binding.basis.complexTypeDefinition):
    _TypeDefinition = None
    _ContentTypeTag = pyxb.binding.basis.complexTypeDefinition._CT_ELEMENT_ONLY
    _Abstract = False
    _ExpandedName = None
    _DefinitionLocation = pyxb.utils.utility.Location('/tmp/pyxbdist.RHB65sy/PyXB-1.1.5/pyxb/bundles/wssplat/schemas/wsnt.xsd', 220, 4)
    # Base type is pyxb.binding.datatypes.anyType
    
    # Element {http://docs.oasis-open.org/wsn/b-2}Topic uses Python identifier Topic
    __Topic = pyxb.binding.content.ElementUse(pyxb.namespace.ExpandedName(Namespace, u'Topic'), 'Topic', '__httpdocs_oasis_open_orgwsnb_2_CTD_ANON_2_httpdocs_oasis_open_orgwsnb_2Topic', False)
    __Topic._DeclarationLocation = pyxb.utils.utility.Location('/tmp/pyxbdist.RHB65sy/PyXB-1.1.5/pyxb/bundles/wssplat/schemas/wsnt.xsd', 222, 8)
    __Topic._UseLocation = pyxb.utils.utility.Location('/tmp/pyxbdist.RHB65sy/PyXB-1.1.5/pyxb/bundles/wssplat/schemas/wsnt.xsd', 221, 6)

    
    Topic = property(__Topic.value, __Topic.set, None, None)

    _HasWildcardElement = True

    _ElementMap = {
        __Topic.name() : __Topic
    }
    _AttributeMap = {
        
    }



# Complex type {http://docs.oasis-open.org/wsn/b-2}TopicExpressionType with content type MIXED
class TopicExpressionType (pyxb.binding.basis.complexTypeDefinition):
    _TypeDefinition = None
    _ContentTypeTag = pyxb.binding.basis.complexTypeDefinition._CT_MIXED
    _Abstract = False
    _ExpandedName = pyxb.namespace.ExpandedName(Namespace, u'TopicExpressionType')
    _DefinitionLocation = pyxb.utils.utility.Location('/tmp/pyxbdist.RHB65sy/PyXB-1.1.5/pyxb/bundles/wssplat/schemas/wsnt.xsd', 49, 2)
    # Base type is pyxb.binding.datatypes.anyType
    
    # Attribute Dialect uses Python identifier Dialect
    __Dialect = pyxb.binding.content.AttributeUse(pyxb.namespace.ExpandedName(None, u'Dialect'), 'Dialect', '__httpdocs_oasis_open_orgwsnb_2_TopicExpressionType_Dialect', pyxb.binding.datatypes.anyURI, required=True)
    __Dialect._DeclarationLocation = pyxb.utils.utility.Location('/tmp/pyxbdist.RHB65sy/PyXB-1.1.5/pyxb/bundles/wssplat/schemas/wsnt.xsd', 53, 4)
    __Dialect._UseLocation = pyxb.utils.utility.Location('/tmp/pyxbdist.RHB65sy/PyXB-1.1.5/pyxb/bundles/wssplat/schemas/wsnt.xsd', 53, 4)
    
    Dialect = property(__Dialect.value, __Dialect.set, None, None)

    _AttributeWildcard = pyxb.binding.content.Wildcard(process_contents=pyxb.binding.content.Wildcard.PC_strict, namespace_constraint=pyxb.binding.content.Wildcard.NC_any)
    _HasWildcardElement = True

    _ElementMap = {
        
    }
    _AttributeMap = {
        __Dialect.name() : __Dialect
    }
Namespace.addCategoryObject('typeBinding', u'TopicExpressionType', TopicExpressionType)


# Complex type {http://docs.oasis-open.org/wsn/b-2}NotificationMessageHolderType with content type ELEMENT_ONLY
class NotificationMessageHolderType (pyxb.binding.basis.complexTypeDefinition):
    _TypeDefinition = None
    _ContentTypeTag = pyxb.binding.basis.complexTypeDefinition._CT_ELEMENT_ONLY
    _Abstract = False
    _ExpandedName = pyxb.namespace.ExpandedName(Namespace, u'NotificationMessageHolderType')
    _DefinitionLocation = pyxb.utils.utility.Location('/tmp/pyxbdist.RHB65sy/PyXB-1.1.5/pyxb/bundles/wssplat/schemas/wsnt.xsd', 123, 2)
    # Base type is pyxb.binding.datatypes.anyType
    
    # Element {http://docs.oasis-open.org/wsn/b-2}Topic uses Python identifier Topic
    __Topic = pyxb.binding.content.ElementUse(pyxb.namespace.ExpandedName(Namespace, u'Topic'), 'Topic', '__httpdocs_oasis_open_orgwsnb_2_NotificationMessageHolderType_httpdocs_oasis_open_orgwsnb_2Topic', False)
    __Topic._DeclarationLocation = pyxb.utils.utility.Location('/tmp/pyxbdist.RHB65sy/PyXB-1.1.5/pyxb/bundles/wssplat/schemas/wsnt.xsd', 117, 2)
    __Topic._UseLocation = pyxb.utils.utility.Location('/tmp/pyxbdist.RHB65sy/PyXB-1.1.5/pyxb/bundles/wssplat/schemas/wsnt.xsd', 124, 4)

    
    Topic = property(__Topic.value, __Topic.set, None, None)

    
    # Element {http://docs.oasis-open.org/wsn/b-2}ProducerReference uses Python identifier ProducerReference
    __ProducerReference = pyxb.binding.content.ElementUse(pyxb.namespace.ExpandedName(Namespace, u'ProducerReference'), 'ProducerReference', '__httpdocs_oasis_open_orgwsnb_2_NotificationMessageHolderType_httpdocs_oasis_open_orgwsnb_2ProducerReference', False)
    __ProducerReference._DeclarationLocation = pyxb.utils.utility.Location('/tmp/pyxbdist.RHB65sy/PyXB-1.1.5/pyxb/bundles/wssplat/schemas/wsnt.xsd', 119, 2)
    __ProducerReference._UseLocation = pyxb.utils.utility.Location('/tmp/pyxbdist.RHB65sy/PyXB-1.1.5/pyxb/bundles/wssplat/schemas/wsnt.xsd', 124, 4)

    
    ProducerReference = property(__ProducerReference.value, __ProducerReference.set, None, None)

    
    # Element {http://docs.oasis-open.org/wsn/b-2}SubscriptionReference uses Python identifier SubscriptionReference
    __SubscriptionReference = pyxb.binding.content.ElementUse(pyxb.namespace.ExpandedName(Namespace, u'SubscriptionReference'), 'SubscriptionReference', '__httpdocs_oasis_open_orgwsnb_2_NotificationMessageHolderType_httpdocs_oasis_open_orgwsnb_2SubscriptionReference', False)
    __SubscriptionReference._DeclarationLocation = pyxb.utils.utility.Location('/tmp/pyxbdist.RHB65sy/PyXB-1.1.5/pyxb/bundles/wssplat/schemas/wsnt.xsd', 115, 2)
    __SubscriptionReference._UseLocation = pyxb.utils.utility.Location('/tmp/pyxbdist.RHB65sy/PyXB-1.1.5/pyxb/bundles/wssplat/schemas/wsnt.xsd', 124, 4)

    
    SubscriptionReference = property(__SubscriptionReference.value, __SubscriptionReference.set, None, None)

    
    # Element {http://docs.oasis-open.org/wsn/b-2}Message uses Python identifier Message
    __Message = pyxb.binding.content.ElementUse(pyxb.namespace.ExpandedName(Namespace, u'Message'), 'Message', '__httpdocs_oasis_open_orgwsnb_2_NotificationMessageHolderType_httpdocs_oasis_open_orgwsnb_2Message', False)
    __Message._DeclarationLocation = pyxb.utils.utility.Location('/tmp/pyxbdist.RHB65sy/PyXB-1.1.5/pyxb/bundles/wssplat/schemas/wsnt.xsd', 131, 6)
    __Message._UseLocation = pyxb.utils.utility.Location('/tmp/pyxbdist.RHB65sy/PyXB-1.1.5/pyxb/bundles/wssplat/schemas/wsnt.xsd', 124, 4)

    
    Message = property(__Message.value, __Message.set, None, None)


    _ElementMap = {
        __Topic.name() : __Topic,
        __ProducerReference.name() : __ProducerReference,
        __SubscriptionReference.name() : __SubscriptionReference,
        __Message.name() : __Message
    }
    _AttributeMap = {
        
    }
Namespace.addCategoryObject('typeBinding', u'NotificationMessageHolderType', NotificationMessageHolderType)


# Complex type {http://docs.oasis-open.org/wsn/b-2}QueryExpressionType with content type MIXED
class QueryExpressionType (pyxb.binding.basis.complexTypeDefinition):
    _TypeDefinition = None
    _ContentTypeTag = pyxb.binding.basis.complexTypeDefinition._CT_MIXED
    _Abstract = False
    _ExpandedName = pyxb.namespace.ExpandedName(Namespace, u'QueryExpressionType')
    _DefinitionLocation = pyxb.utils.utility.Location('/tmp/pyxbdist.RHB65sy/PyXB-1.1.5/pyxb/bundles/wssplat/schemas/wsnt.xsd', 42, 2)
    # Base type is pyxb.binding.datatypes.anyType
    
    # Attribute Dialect uses Python identifier Dialect
    __Dialect = pyxb.binding.content.AttributeUse(pyxb.namespace.ExpandedName(None, u'Dialect'), 'Dialect', '__httpdocs_oasis_open_orgwsnb_2_QueryExpressionType_Dialect', pyxb.binding.datatypes.anyURI, required=True)
    __Dialect._DeclarationLocation = pyxb.utils.utility.Location('/tmp/pyxbdist.RHB65sy/PyXB-1.1.5/pyxb/bundles/wssplat/schemas/wsnt.xsd', 46, 4)
    __Dialect._UseLocation = pyxb.utils.utility.Location('/tmp/pyxbdist.RHB65sy/PyXB-1.1.5/pyxb/bundles/wssplat/schemas/wsnt.xsd', 46, 4)
    
    Dialect = property(__Dialect.value, __Dialect.set, None, None)

    _HasWildcardElement = True

    _ElementMap = {
        
    }
    _AttributeMap = {
        __Dialect.name() : __Dialect
    }
Namespace.addCategoryObject('typeBinding', u'QueryExpressionType', QueryExpressionType)


# Complex type [anonymous] with content type ELEMENT_ONLY
class CTD_ANON_3 (pyxb.binding.basis.complexTypeDefinition):
    _TypeDefinition = None
    _ContentTypeTag = pyxb.binding.basis.complexTypeDefinition._CT_ELEMENT_ONLY
    _Abstract = False
    _ExpandedName = None
    _DefinitionLocation = pyxb.utils.utility.Location('/tmp/pyxbdist.RHB65sy/PyXB-1.1.5/pyxb/bundles/wssplat/schemas/wsnt.xsd', 132, 8)
    # Base type is pyxb.binding.datatypes.anyType
    _HasWildcardElement = True

    _ElementMap = {
        
    }
    _AttributeMap = {
        
    }



# Complex type {http://docs.oasis-open.org/wsn/b-2}SubscribeCreationFailedFaultType with content type ELEMENT_ONLY
class SubscribeCreationFailedFaultType (pyxb.bundles.wssplat.wsrf_bf.BaseFaultType):
    _TypeDefinition = None
    _ContentTypeTag = pyxb.binding.basis.complexTypeDefinition._CT_ELEMENT_ONLY
    _Abstract = False
    _ExpandedName = pyxb.namespace.ExpandedName(Namespace, u'SubscribeCreationFailedFaultType')
    _DefinitionLocation = pyxb.utils.utility.Location('/tmp/pyxbdist.RHB65sy/PyXB-1.1.5/pyxb/bundles/wssplat/schemas/wsnt.xsd', 239, 2)
    # Base type is pyxb.bundles.wssplat.wsrf_bf.BaseFaultType
    
    # Element ErrorCode ({http://docs.oasis-open.org/wsrf/bf-2}ErrorCode) inherited from {http://docs.oasis-open.org/wsrf/bf-2}BaseFaultType
    
    # Element Originator ({http://docs.oasis-open.org/wsrf/bf-2}Originator) inherited from {http://docs.oasis-open.org/wsrf/bf-2}BaseFaultType
    
    # Element FaultCause ({http://docs.oasis-open.org/wsrf/bf-2}FaultCause) inherited from {http://docs.oasis-open.org/wsrf/bf-2}BaseFaultType
    
    # Element Description ({http://docs.oasis-open.org/wsrf/bf-2}Description) inherited from {http://docs.oasis-open.org/wsrf/bf-2}BaseFaultType
    
    # Element Timestamp ({http://docs.oasis-open.org/wsrf/bf-2}Timestamp) inherited from {http://docs.oasis-open.org/wsrf/bf-2}BaseFaultType
    _AttributeWildcard = pyxb.binding.content.Wildcard(process_contents=pyxb.binding.content.Wildcard.PC_lax, namespace_constraint=(pyxb.binding.content.Wildcard.NC_not, u'http://docs.oasis-open.org/wsrf/bf-2'))
    _HasWildcardElement = True

    _ElementMap = pyxb.bundles.wssplat.wsrf_bf.BaseFaultType._ElementMap.copy()
    _ElementMap.update({
        
    })
    _AttributeMap = pyxb.bundles.wssplat.wsrf_bf.BaseFaultType._AttributeMap.copy()
    _AttributeMap.update({
        
    })
Namespace.addCategoryObject('typeBinding', u'SubscribeCreationFailedFaultType', SubscribeCreationFailedFaultType)


# Complex type [anonymous] with content type ELEMENT_ONLY
class CTD_ANON_4 (pyxb.binding.basis.complexTypeDefinition):
    _TypeDefinition = None
    _ContentTypeTag = pyxb.binding.basis.complexTypeDefinition._CT_ELEMENT_ONLY
    _Abstract = False
    _ExpandedName = None
    _DefinitionLocation = pyxb.utils.utility.Location('/tmp/pyxbdist.RHB65sy/PyXB-1.1.5/pyxb/bundles/wssplat/schemas/wsnt.xsd', 204, 4)
    # Base type is pyxb.binding.datatypes.anyType
    
    # Element {http://docs.oasis-open.org/wsn/b-2}SubscriptionReference uses Python identifier SubscriptionReference
    __SubscriptionReference = pyxb.binding.content.ElementUse(pyxb.namespace.ExpandedName(Namespace, u'SubscriptionReference'), 'SubscriptionReference', '__httpdocs_oasis_open_orgwsnb_2_CTD_ANON_4_httpdocs_oasis_open_orgwsnb_2SubscriptionReference', False)
    __SubscriptionReference._DeclarationLocation = pyxb.utils.utility.Location('/tmp/pyxbdist.RHB65sy/PyXB-1.1.5/pyxb/bundles/wssplat/schemas/wsnt.xsd', 206, 8)
    __SubscriptionReference._UseLocation = pyxb.utils.utility.Location('/tmp/pyxbdist.RHB65sy/PyXB-1.1.5/pyxb/bundles/wssplat/schemas/wsnt.xsd', 205, 6)

    
    SubscriptionReference = property(__SubscriptionReference.value, __SubscriptionReference.set, None, None)

    
    # Element {http://docs.oasis-open.org/wsn/b-2}TerminationTime uses Python identifier TerminationTime
    __TerminationTime = pyxb.binding.content.ElementUse(pyxb.namespace.ExpandedName(Namespace, u'TerminationTime'), 'TerminationTime', '__httpdocs_oasis_open_orgwsnb_2_CTD_ANON_4_httpdocs_oasis_open_orgwsnb_2TerminationTime', False)
    __TerminationTime._DeclarationLocation = pyxb.utils.utility.Location('/tmp/pyxbdist.RHB65sy/PyXB-1.1.5/pyxb/bundles/wssplat/schemas/wsnt.xsd', 164, 2)
    __TerminationTime._UseLocation = pyxb.utils.utility.Location('/tmp/pyxbdist.RHB65sy/PyXB-1.1.5/pyxb/bundles/wssplat/schemas/wsnt.xsd', 205, 6)

    
    TerminationTime = property(__TerminationTime.value, __TerminationTime.set, None, None)

    
    # Element {http://docs.oasis-open.org/wsn/b-2}CurrentTime uses Python identifier CurrentTime
    __CurrentTime = pyxb.binding.content.ElementUse(pyxb.namespace.ExpandedName(Namespace, u'CurrentTime'), 'CurrentTime', '__httpdocs_oasis_open_orgwsnb_2_CTD_ANON_4_httpdocs_oasis_open_orgwsnb_2CurrentTime', False)
    __CurrentTime._DeclarationLocation = pyxb.utils.utility.Location('/tmp/pyxbdist.RHB65sy/PyXB-1.1.5/pyxb/bundles/wssplat/schemas/wsnt.xsd', 162, 2)
    __CurrentTime._UseLocation = pyxb.utils.utility.Location('/tmp/pyxbdist.RHB65sy/PyXB-1.1.5/pyxb/bundles/wssplat/schemas/wsnt.xsd', 205, 6)

    
    CurrentTime = property(__CurrentTime.value, __CurrentTime.set, None, None)

    _HasWildcardElement = True

    _ElementMap = {
        __SubscriptionReference.name() : __SubscriptionReference,
        __TerminationTime.name() : __TerminationTime,
        __CurrentTime.name() : __CurrentTime
    }
    _AttributeMap = {
        
    }



# Complex type {http://docs.oasis-open.org/wsn/b-2}InvalidFilterFaultType with content type ELEMENT_ONLY
class InvalidFilterFaultType (pyxb.bundles.wssplat.wsrf_bf.BaseFaultType):
    _TypeDefinition = None
    _ContentTypeTag = pyxb.binding.basis.complexTypeDefinition._CT_ELEMENT_ONLY
    _Abstract = False
    _ExpandedName = pyxb.namespace.ExpandedName(Namespace, u'InvalidFilterFaultType')
    _DefinitionLocation = pyxb.utils.utility.Location('/tmp/pyxbdist.RHB65sy/PyXB-1.1.5/pyxb/bundles/wssplat/schemas/wsnt.xsd', 247, 2)
    # Base type is pyxb.bundles.wssplat.wsrf_bf.BaseFaultType
    
    # Element ErrorCode ({http://docs.oasis-open.org/wsrf/bf-2}ErrorCode) inherited from {http://docs.oasis-open.org/wsrf/bf-2}BaseFaultType
    
    # Element Timestamp ({http://docs.oasis-open.org/wsrf/bf-2}Timestamp) inherited from {http://docs.oasis-open.org/wsrf/bf-2}BaseFaultType
    
    # Element FaultCause ({http://docs.oasis-open.org/wsrf/bf-2}FaultCause) inherited from {http://docs.oasis-open.org/wsrf/bf-2}BaseFaultType
    
    # Element {http://docs.oasis-open.org/wsn/b-2}UnknownFilter uses Python identifier UnknownFilter
    __UnknownFilter = pyxb.binding.content.ElementUse(pyxb.namespace.ExpandedName(Namespace, u'UnknownFilter'), 'UnknownFilter', '__httpdocs_oasis_open_orgwsnb_2_InvalidFilterFaultType_httpdocs_oasis_open_orgwsnb_2UnknownFilter', True)
    __UnknownFilter._DeclarationLocation = pyxb.utils.utility.Location('/tmp/pyxbdist.RHB65sy/PyXB-1.1.5/pyxb/bundles/wssplat/schemas/wsnt.xsd', 251, 10)
    __UnknownFilter._UseLocation = None

    
    UnknownFilter = property(__UnknownFilter.value, __UnknownFilter.set, None, None)

    
    # Element Originator ({http://docs.oasis-open.org/wsrf/bf-2}Originator) inherited from {http://docs.oasis-open.org/wsrf/bf-2}BaseFaultType
    
    # Element Description ({http://docs.oasis-open.org/wsrf/bf-2}Description) inherited from {http://docs.oasis-open.org/wsrf/bf-2}BaseFaultType
    _AttributeWildcard = pyxb.binding.content.Wildcard(process_contents=pyxb.binding.content.Wildcard.PC_lax, namespace_constraint=(pyxb.binding.content.Wildcard.NC_not, u'http://docs.oasis-open.org/wsrf/bf-2'))
    _HasWildcardElement = True

    _ElementMap = pyxb.bundles.wssplat.wsrf_bf.BaseFaultType._ElementMap.copy()
    _ElementMap.update({
        __UnknownFilter.name() : __UnknownFilter
    })
    _AttributeMap = pyxb.bundles.wssplat.wsrf_bf.BaseFaultType._AttributeMap.copy()
    _AttributeMap.update({
        
    })
Namespace.addCategoryObject('typeBinding', u'InvalidFilterFaultType', InvalidFilterFaultType)


# Complex type {http://docs.oasis-open.org/wsn/b-2}TopicExpressionDialectUnknownFaultType with content type ELEMENT_ONLY
class TopicExpressionDialectUnknownFaultType (pyxb.bundles.wssplat.wsrf_bf.BaseFaultType):
    _TypeDefinition = None
    _ContentTypeTag = pyxb.binding.basis.complexTypeDefinition._CT_ELEMENT_ONLY
    _Abstract = False
    _ExpandedName = pyxb.namespace.ExpandedName(Namespace, u'TopicExpressionDialectUnknownFaultType')
    _DefinitionLocation = pyxb.utils.utility.Location('/tmp/pyxbdist.RHB65sy/PyXB-1.1.5/pyxb/bundles/wssplat/schemas/wsnt.xsd', 260, 2)
    # Base type is pyxb.bundles.wssplat.wsrf_bf.BaseFaultType
    
    # Element ErrorCode ({http://docs.oasis-open.org/wsrf/bf-2}ErrorCode) inherited from {http://docs.oasis-open.org/wsrf/bf-2}BaseFaultType
    
    # Element Originator ({http://docs.oasis-open.org/wsrf/bf-2}Originator) inherited from {http://docs.oasis-open.org/wsrf/bf-2}BaseFaultType
    
    # Element FaultCause ({http://docs.oasis-open.org/wsrf/bf-2}FaultCause) inherited from {http://docs.oasis-open.org/wsrf/bf-2}BaseFaultType
    
    # Element Description ({http://docs.oasis-open.org/wsrf/bf-2}Description) inherited from {http://docs.oasis-open.org/wsrf/bf-2}BaseFaultType
    
    # Element Timestamp ({http://docs.oasis-open.org/wsrf/bf-2}Timestamp) inherited from {http://docs.oasis-open.org/wsrf/bf-2}BaseFaultType
    _AttributeWildcard = pyxb.binding.content.Wildcard(process_contents=pyxb.binding.content.Wildcard.PC_lax, namespace_constraint=(pyxb.binding.content.Wildcard.NC_not, u'http://docs.oasis-open.org/wsrf/bf-2'))
    _HasWildcardElement = True

    _ElementMap = pyxb.bundles.wssplat.wsrf_bf.BaseFaultType._ElementMap.copy()
    _ElementMap.update({
        
    })
    _AttributeMap = pyxb.bundles.wssplat.wsrf_bf.BaseFaultType._AttributeMap.copy()
    _AttributeMap.update({
        
    })
Namespace.addCategoryObject('typeBinding', u'TopicExpressionDialectUnknownFaultType', TopicExpressionDialectUnknownFaultType)


# Complex type {http://docs.oasis-open.org/wsn/b-2}InvalidTopicExpressionFaultType with content type ELEMENT_ONLY
class InvalidTopicExpressionFaultType (pyxb.bundles.wssplat.wsrf_bf.BaseFaultType):
    _TypeDefinition = None
    _ContentTypeTag = pyxb.binding.basis.complexTypeDefinition._CT_ELEMENT_ONLY
    _Abstract = False
    _ExpandedName = pyxb.namespace.ExpandedName(Namespace, u'InvalidTopicExpressionFaultType')
    _DefinitionLocation = pyxb.utils.utility.Location('/tmp/pyxbdist.RHB65sy/PyXB-1.1.5/pyxb/bundles/wssplat/schemas/wsnt.xsd', 268, 2)
    # Base type is pyxb.bundles.wssplat.wsrf_bf.BaseFaultType
    
    # Element ErrorCode ({http://docs.oasis-open.org/wsrf/bf-2}ErrorCode) inherited from {http://docs.oasis-open.org/wsrf/bf-2}BaseFaultType
    
    # Element Originator ({http://docs.oasis-open.org/wsrf/bf-2}Originator) inherited from {http://docs.oasis-open.org/wsrf/bf-2}BaseFaultType
    
    # Element FaultCause ({http://docs.oasis-open.org/wsrf/bf-2}FaultCause) inherited from {http://docs.oasis-open.org/wsrf/bf-2}BaseFaultType
    
    # Element Description ({http://docs.oasis-open.org/wsrf/bf-2}Description) inherited from {http://docs.oasis-open.org/wsrf/bf-2}BaseFaultType
    
    # Element Timestamp ({http://docs.oasis-open.org/wsrf/bf-2}Timestamp) inherited from {http://docs.oasis-open.org/wsrf/bf-2}BaseFaultType
    _AttributeWildcard = pyxb.binding.content.Wildcard(process_contents=pyxb.binding.content.Wildcard.PC_lax, namespace_constraint=(pyxb.binding.content.Wildcard.NC_not, u'http://docs.oasis-open.org/wsrf/bf-2'))
    _HasWildcardElement = True

    _ElementMap = pyxb.bundles.wssplat.wsrf_bf.BaseFaultType._ElementMap.copy()
    _ElementMap.update({
        
    })
    _AttributeMap = pyxb.bundles.wssplat.wsrf_bf.BaseFaultType._AttributeMap.copy()
    _AttributeMap.update({
        
    })
Namespace.addCategoryObject('typeBinding', u'InvalidTopicExpressionFaultType', InvalidTopicExpressionFaultType)


# Complex type {http://docs.oasis-open.org/wsn/b-2}TopicNotSupportedFaultType with content type ELEMENT_ONLY
class TopicNotSupportedFaultType (pyxb.bundles.wssplat.wsrf_bf.BaseFaultType):
    _TypeDefinition = None
    _ContentTypeTag = pyxb.binding.basis.complexTypeDefinition._CT_ELEMENT_ONLY
    _Abstract = False
    _ExpandedName = pyxb.namespace.ExpandedName(Namespace, u'TopicNotSupportedFaultType')
    _DefinitionLocation = pyxb.utils.utility.Location('/tmp/pyxbdist.RHB65sy/PyXB-1.1.5/pyxb/bundles/wssplat/schemas/wsnt.xsd', 276, 2)
    # Base type is pyxb.bundles.wssplat.wsrf_bf.BaseFaultType
    
    # Element ErrorCode ({http://docs.oasis-open.org/wsrf/bf-2}ErrorCode) inherited from {http://docs.oasis-open.org/wsrf/bf-2}BaseFaultType
    
    # Element Originator ({http://docs.oasis-open.org/wsrf/bf-2}Originator) inherited from {http://docs.oasis-open.org/wsrf/bf-2}BaseFaultType
    
    # Element FaultCause ({http://docs.oasis-open.org/wsrf/bf-2}FaultCause) inherited from {http://docs.oasis-open.org/wsrf/bf-2}BaseFaultType
    
    # Element Description ({http://docs.oasis-open.org/wsrf/bf-2}Description) inherited from {http://docs.oasis-open.org/wsrf/bf-2}BaseFaultType
    
    # Element Timestamp ({http://docs.oasis-open.org/wsrf/bf-2}Timestamp) inherited from {http://docs.oasis-open.org/wsrf/bf-2}BaseFaultType
    _AttributeWildcard = pyxb.binding.content.Wildcard(process_contents=pyxb.binding.content.Wildcard.PC_lax, namespace_constraint=(pyxb.binding.content.Wildcard.NC_not, u'http://docs.oasis-open.org/wsrf/bf-2'))
    _HasWildcardElement = True

    _ElementMap = pyxb.bundles.wssplat.wsrf_bf.BaseFaultType._ElementMap.copy()
    _ElementMap.update({
        
    })
    _AttributeMap = pyxb.bundles.wssplat.wsrf_bf.BaseFaultType._AttributeMap.copy()
    _AttributeMap.update({
        
    })
Namespace.addCategoryObject('typeBinding', u'TopicNotSupportedFaultType', TopicNotSupportedFaultType)


# Complex type {http://docs.oasis-open.org/wsn/b-2}InvalidProducerPropertiesExpressionFaultType with content type ELEMENT_ONLY
class InvalidProducerPropertiesExpressionFaultType (pyxb.bundles.wssplat.wsrf_bf.BaseFaultType):
    _TypeDefinition = None
    _ContentTypeTag = pyxb.binding.basis.complexTypeDefinition._CT_ELEMENT_ONLY
    _Abstract = False
    _ExpandedName = pyxb.namespace.ExpandedName(Namespace, u'InvalidProducerPropertiesExpressionFaultType')
    _DefinitionLocation = pyxb.utils.utility.Location('/tmp/pyxbdist.RHB65sy/PyXB-1.1.5/pyxb/bundles/wssplat/schemas/wsnt.xsd', 292, 2)
    # Base type is pyxb.bundles.wssplat.wsrf_bf.BaseFaultType
    
    # Element ErrorCode ({http://docs.oasis-open.org/wsrf/bf-2}ErrorCode) inherited from {http://docs.oasis-open.org/wsrf/bf-2}BaseFaultType
    
    # Element Originator ({http://docs.oasis-open.org/wsrf/bf-2}Originator) inherited from {http://docs.oasis-open.org/wsrf/bf-2}BaseFaultType
    
    # Element FaultCause ({http://docs.oasis-open.org/wsrf/bf-2}FaultCause) inherited from {http://docs.oasis-open.org/wsrf/bf-2}BaseFaultType
    
    # Element Description ({http://docs.oasis-open.org/wsrf/bf-2}Description) inherited from {http://docs.oasis-open.org/wsrf/bf-2}BaseFaultType
    
    # Element Timestamp ({http://docs.oasis-open.org/wsrf/bf-2}Timestamp) inherited from {http://docs.oasis-open.org/wsrf/bf-2}BaseFaultType
    _AttributeWildcard = pyxb.binding.content.Wildcard(process_contents=pyxb.binding.content.Wildcard.PC_lax, namespace_constraint=(pyxb.binding.content.Wildcard.NC_not, u'http://docs.oasis-open.org/wsrf/bf-2'))
    _HasWildcardElement = True

    _ElementMap = pyxb.bundles.wssplat.wsrf_bf.BaseFaultType._ElementMap.copy()
    _ElementMap.update({
        
    })
    _AttributeMap = pyxb.bundles.wssplat.wsrf_bf.BaseFaultType._AttributeMap.copy()
    _AttributeMap.update({
        
    })
Namespace.addCategoryObject('typeBinding', u'InvalidProducerPropertiesExpressionFaultType', InvalidProducerPropertiesExpressionFaultType)


# Complex type [anonymous] with content type EMPTY
class CTD_ANON_5 (pyxb.binding.basis.complexTypeDefinition):
    _TypeDefinition = None
    _ContentTypeTag = pyxb.binding.basis.complexTypeDefinition._CT_EMPTY
    _Abstract = False
    _ExpandedName = None
    _DefinitionLocation = pyxb.utils.utility.Location('/tmp/pyxbdist.RHB65sy/PyXB-1.1.5/pyxb/bundles/wssplat/schemas/wsnt.xsd', 173, 29)
    # Base type is pyxb.binding.datatypes.anyType

    _ElementMap = {
        
    }
    _AttributeMap = {
        
    }



# Complex type {http://docs.oasis-open.org/wsn/b-2}InvalidMessageContentExpressionFaultType with content type ELEMENT_ONLY
class InvalidMessageContentExpressionFaultType (pyxb.bundles.wssplat.wsrf_bf.BaseFaultType):
    _TypeDefinition = None
    _ContentTypeTag = pyxb.binding.basis.complexTypeDefinition._CT_ELEMENT_ONLY
    _Abstract = False
    _ExpandedName = pyxb.namespace.ExpandedName(Namespace, u'InvalidMessageContentExpressionFaultType')
    _DefinitionLocation = pyxb.utils.utility.Location('/tmp/pyxbdist.RHB65sy/PyXB-1.1.5/pyxb/bundles/wssplat/schemas/wsnt.xsd', 300, 2)
    # Base type is pyxb.bundles.wssplat.wsrf_bf.BaseFaultType
    
    # Element ErrorCode ({http://docs.oasis-open.org/wsrf/bf-2}ErrorCode) inherited from {http://docs.oasis-open.org/wsrf/bf-2}BaseFaultType
    
    # Element Originator ({http://docs.oasis-open.org/wsrf/bf-2}Originator) inherited from {http://docs.oasis-open.org/wsrf/bf-2}BaseFaultType
    
    # Element FaultCause ({http://docs.oasis-open.org/wsrf/bf-2}FaultCause) inherited from {http://docs.oasis-open.org/wsrf/bf-2}BaseFaultType
    
    # Element Description ({http://docs.oasis-open.org/wsrf/bf-2}Description) inherited from {http://docs.oasis-open.org/wsrf/bf-2}BaseFaultType
    
    # Element Timestamp ({http://docs.oasis-open.org/wsrf/bf-2}Timestamp) inherited from {http://docs.oasis-open.org/wsrf/bf-2}BaseFaultType
    _AttributeWildcard = pyxb.binding.content.Wildcard(process_contents=pyxb.binding.content.Wildcard.PC_lax, namespace_constraint=(pyxb.binding.content.Wildcard.NC_not, u'http://docs.oasis-open.org/wsrf/bf-2'))
    _HasWildcardElement = True

    _ElementMap = pyxb.bundles.wssplat.wsrf_bf.BaseFaultType._ElementMap.copy()
    _ElementMap.update({
        
    })
    _AttributeMap = pyxb.bundles.wssplat.wsrf_bf.BaseFaultType._AttributeMap.copy()
    _AttributeMap.update({
        
    })
Namespace.addCategoryObject('typeBinding', u'InvalidMessageContentExpressionFaultType', InvalidMessageContentExpressionFaultType)


# Complex type [anonymous] with content type ELEMENT_ONLY
class CTD_ANON_6 (pyxb.binding.basis.complexTypeDefinition):
    _TypeDefinition = None
    _ContentTypeTag = pyxb.binding.basis.complexTypeDefinition._CT_ELEMENT_ONLY
    _Abstract = False
    _ExpandedName = None
    _DefinitionLocation = pyxb.utils.utility.Location('/tmp/pyxbdist.RHB65sy/PyXB-1.1.5/pyxb/bundles/wssplat/schemas/wsnt.xsd', 176, 4)
    # Base type is pyxb.binding.datatypes.anyType
    
    # Element {http://docs.oasis-open.org/wsn/b-2}ConsumerReference uses Python identifier ConsumerReference
    __ConsumerReference = pyxb.binding.content.ElementUse(pyxb.namespace.ExpandedName(Namespace, u'ConsumerReference'), 'ConsumerReference', '__httpdocs_oasis_open_orgwsnb_2_CTD_ANON_6_httpdocs_oasis_open_orgwsnb_2ConsumerReference', False)
    __ConsumerReference._DeclarationLocation = pyxb.utils.utility.Location('/tmp/pyxbdist.RHB65sy/PyXB-1.1.5/pyxb/bundles/wssplat/schemas/wsnt.xsd', 178, 8)
    __ConsumerReference._UseLocation = pyxb.utils.utility.Location('/tmp/pyxbdist.RHB65sy/PyXB-1.1.5/pyxb/bundles/wssplat/schemas/wsnt.xsd', 177, 6)

    
    ConsumerReference = property(__ConsumerReference.value, __ConsumerReference.set, None, None)

    
    # Element {http://docs.oasis-open.org/wsn/b-2}InitialTerminationTime uses Python identifier InitialTerminationTime
    __InitialTerminationTime = pyxb.binding.content.ElementUse(pyxb.namespace.ExpandedName(Namespace, u'InitialTerminationTime'), 'InitialTerminationTime', '__httpdocs_oasis_open_orgwsnb_2_CTD_ANON_6_httpdocs_oasis_open_orgwsnb_2InitialTerminationTime', False)
    __InitialTerminationTime._DeclarationLocation = pyxb.utils.utility.Location('/tmp/pyxbdist.RHB65sy/PyXB-1.1.5/pyxb/bundles/wssplat/schemas/wsnt.xsd', 184, 8)
    __InitialTerminationTime._UseLocation = pyxb.utils.utility.Location('/tmp/pyxbdist.RHB65sy/PyXB-1.1.5/pyxb/bundles/wssplat/schemas/wsnt.xsd', 177, 6)

    
    InitialTerminationTime = property(__InitialTerminationTime.value, __InitialTerminationTime.set, None, None)

    
    # Element {http://docs.oasis-open.org/wsn/b-2}Filter uses Python identifier Filter
    __Filter = pyxb.binding.content.ElementUse(pyxb.namespace.ExpandedName(Namespace, u'Filter'), 'Filter', '__httpdocs_oasis_open_orgwsnb_2_CTD_ANON_6_httpdocs_oasis_open_orgwsnb_2Filter', False)
    __Filter._DeclarationLocation = pyxb.utils.utility.Location('/tmp/pyxbdist.RHB65sy/PyXB-1.1.5/pyxb/bundles/wssplat/schemas/wsnt.xsd', 181, 8)
    __Filter._UseLocation = pyxb.utils.utility.Location('/tmp/pyxbdist.RHB65sy/PyXB-1.1.5/pyxb/bundles/wssplat/schemas/wsnt.xsd', 177, 6)

    
    Filter = property(__Filter.value, __Filter.set, None, None)

    
    # Element {http://docs.oasis-open.org/wsn/b-2}SubscriptionPolicy uses Python identifier SubscriptionPolicy
    __SubscriptionPolicy = pyxb.binding.content.ElementUse(pyxb.namespace.ExpandedName(Namespace, u'SubscriptionPolicy'), 'SubscriptionPolicy', '__httpdocs_oasis_open_orgwsnb_2_CTD_ANON_6_httpdocs_oasis_open_orgwsnb_2SubscriptionPolicy', False)
    __SubscriptionPolicy._DeclarationLocation = pyxb.utils.utility.Location('/tmp/pyxbdist.RHB65sy/PyXB-1.1.5/pyxb/bundles/wssplat/schemas/wsnt.xsd', 188, 8)
    __SubscriptionPolicy._UseLocation = pyxb.utils.utility.Location('/tmp/pyxbdist.RHB65sy/PyXB-1.1.5/pyxb/bundles/wssplat/schemas/wsnt.xsd', 177, 6)

    
    SubscriptionPolicy = property(__SubscriptionPolicy.value, __SubscriptionPolicy.set, None, None)

    _HasWildcardElement = True

    _ElementMap = {
        __ConsumerReference.name() : __ConsumerReference,
        __InitialTerminationTime.name() : __InitialTerminationTime,
        __Filter.name() : __Filter,
        __SubscriptionPolicy.name() : __SubscriptionPolicy
    }
    _AttributeMap = {
        
    }



# Complex type {http://docs.oasis-open.org/wsn/b-2}NoCurrentMessageOnTopicFaultType with content type ELEMENT_ONLY
class NoCurrentMessageOnTopicFaultType (pyxb.bundles.wssplat.wsrf_bf.BaseFaultType):
    _TypeDefinition = None
    _ContentTypeTag = pyxb.binding.basis.complexTypeDefinition._CT_ELEMENT_ONLY
    _Abstract = False
    _ExpandedName = pyxb.namespace.ExpandedName(Namespace, u'NoCurrentMessageOnTopicFaultType')
    _DefinitionLocation = pyxb.utils.utility.Location('/tmp/pyxbdist.RHB65sy/PyXB-1.1.5/pyxb/bundles/wssplat/schemas/wsnt.xsd', 356, 2)
    # Base type is pyxb.bundles.wssplat.wsrf_bf.BaseFaultType
    
    # Element ErrorCode ({http://docs.oasis-open.org/wsrf/bf-2}ErrorCode) inherited from {http://docs.oasis-open.org/wsrf/bf-2}BaseFaultType
    
    # Element Originator ({http://docs.oasis-open.org/wsrf/bf-2}Originator) inherited from {http://docs.oasis-open.org/wsrf/bf-2}BaseFaultType
    
    # Element FaultCause ({http://docs.oasis-open.org/wsrf/bf-2}FaultCause) inherited from {http://docs.oasis-open.org/wsrf/bf-2}BaseFaultType
    
    # Element Description ({http://docs.oasis-open.org/wsrf/bf-2}Description) inherited from {http://docs.oasis-open.org/wsrf/bf-2}BaseFaultType
    
    # Element Timestamp ({http://docs.oasis-open.org/wsrf/bf-2}Timestamp) inherited from {http://docs.oasis-open.org/wsrf/bf-2}BaseFaultType
    _AttributeWildcard = pyxb.binding.content.Wildcard(process_contents=pyxb.binding.content.Wildcard.PC_lax, namespace_constraint=(pyxb.binding.content.Wildcard.NC_not, u'http://docs.oasis-open.org/wsrf/bf-2'))
    _HasWildcardElement = True

    _ElementMap = pyxb.bundles.wssplat.wsrf_bf.BaseFaultType._ElementMap.copy()
    _ElementMap.update({
        
    })
    _AttributeMap = pyxb.bundles.wssplat.wsrf_bf.BaseFaultType._AttributeMap.copy()
    _AttributeMap.update({
        
    })
Namespace.addCategoryObject('typeBinding', u'NoCurrentMessageOnTopicFaultType', NoCurrentMessageOnTopicFaultType)


# Complex type [anonymous] with content type ELEMENT_ONLY
class CTD_ANON_7 (pyxb.binding.basis.complexTypeDefinition):
    _TypeDefinition = None
    _ContentTypeTag = pyxb.binding.basis.complexTypeDefinition._CT_ELEMENT_ONLY
    _Abstract = False
    _ExpandedName = None
    _DefinitionLocation = pyxb.utils.utility.Location('/tmp/pyxbdist.RHB65sy/PyXB-1.1.5/pyxb/bundles/wssplat/schemas/wsnt.xsd', 401, 4)
    # Base type is pyxb.binding.datatypes.anyType
    _AttributeWildcard = pyxb.binding.content.Wildcard(process_contents=pyxb.binding.content.Wildcard.PC_strict, namespace_constraint=pyxb.binding.content.Wildcard.NC_any)
    _HasWildcardElement = True

    _ElementMap = {
        
    }
    _AttributeMap = {
        
    }



# Complex type {http://docs.oasis-open.org/wsn/b-2}UnsupportedPolicyRequestFaultType with content type ELEMENT_ONLY
class UnsupportedPolicyRequestFaultType (pyxb.bundles.wssplat.wsrf_bf.BaseFaultType):
    _TypeDefinition = None
    _ContentTypeTag = pyxb.binding.basis.complexTypeDefinition._CT_ELEMENT_ONLY
    _Abstract = False
    _ExpandedName = pyxb.namespace.ExpandedName(Namespace, u'UnsupportedPolicyRequestFaultType')
    _DefinitionLocation = pyxb.utils.utility.Location('/tmp/pyxbdist.RHB65sy/PyXB-1.1.5/pyxb/bundles/wssplat/schemas/wsnt.xsd', 321, 2)
    # Base type is pyxb.bundles.wssplat.wsrf_bf.BaseFaultType
    
    # Element ErrorCode ({http://docs.oasis-open.org/wsrf/bf-2}ErrorCode) inherited from {http://docs.oasis-open.org/wsrf/bf-2}BaseFaultType
    
    # Element Timestamp ({http://docs.oasis-open.org/wsrf/bf-2}Timestamp) inherited from {http://docs.oasis-open.org/wsrf/bf-2}BaseFaultType
    
    # Element FaultCause ({http://docs.oasis-open.org/wsrf/bf-2}FaultCause) inherited from {http://docs.oasis-open.org/wsrf/bf-2}BaseFaultType
    
    # Element {http://docs.oasis-open.org/wsn/b-2}UnsupportedPolicy uses Python identifier UnsupportedPolicy
    __UnsupportedPolicy = pyxb.binding.content.ElementUse(pyxb.namespace.ExpandedName(Namespace, u'UnsupportedPolicy'), 'UnsupportedPolicy', '__httpdocs_oasis_open_orgwsnb_2_UnsupportedPolicyRequestFaultType_httpdocs_oasis_open_orgwsnb_2UnsupportedPolicy', True)
    __UnsupportedPolicy._DeclarationLocation = pyxb.utils.utility.Location('/tmp/pyxbdist.RHB65sy/PyXB-1.1.5/pyxb/bundles/wssplat/schemas/wsnt.xsd', 325, 13)
    __UnsupportedPolicy._UseLocation = None

    
    UnsupportedPolicy = property(__UnsupportedPolicy.value, __UnsupportedPolicy.set, None, None)

    
    # Element Originator ({http://docs.oasis-open.org/wsrf/bf-2}Originator) inherited from {http://docs.oasis-open.org/wsrf/bf-2}BaseFaultType
    
    # Element Description ({http://docs.oasis-open.org/wsrf/bf-2}Description) inherited from {http://docs.oasis-open.org/wsrf/bf-2}BaseFaultType
    _AttributeWildcard = pyxb.binding.content.Wildcard(process_contents=pyxb.binding.content.Wildcard.PC_lax, namespace_constraint=(pyxb.binding.content.Wildcard.NC_not, u'http://docs.oasis-open.org/wsrf/bf-2'))
    _HasWildcardElement = True

    _ElementMap = pyxb.bundles.wssplat.wsrf_bf.BaseFaultType._ElementMap.copy()
    _ElementMap.update({
        __UnsupportedPolicy.name() : __UnsupportedPolicy
    })
    _AttributeMap = pyxb.bundles.wssplat.wsrf_bf.BaseFaultType._AttributeMap.copy()
    _AttributeMap.update({
        
    })
Namespace.addCategoryObject('typeBinding', u'UnsupportedPolicyRequestFaultType', UnsupportedPolicyRequestFaultType)


# Complex type {http://docs.oasis-open.org/wsn/b-2}NotifyMessageNotSupportedFaultType with content type ELEMENT_ONLY
class NotifyMessageNotSupportedFaultType (pyxb.bundles.wssplat.wsrf_bf.BaseFaultType):
    _TypeDefinition = None
    _ContentTypeTag = pyxb.binding.basis.complexTypeDefinition._CT_ELEMENT_ONLY
    _Abstract = False
    _ExpandedName = pyxb.namespace.ExpandedName(Namespace, u'NotifyMessageNotSupportedFaultType')
    _DefinitionLocation = pyxb.utils.utility.Location('/tmp/pyxbdist.RHB65sy/PyXB-1.1.5/pyxb/bundles/wssplat/schemas/wsnt.xsd', 334, 2)
    # Base type is pyxb.bundles.wssplat.wsrf_bf.BaseFaultType
    
    # Element ErrorCode ({http://docs.oasis-open.org/wsrf/bf-2}ErrorCode) inherited from {http://docs.oasis-open.org/wsrf/bf-2}BaseFaultType
    
    # Element Originator ({http://docs.oasis-open.org/wsrf/bf-2}Originator) inherited from {http://docs.oasis-open.org/wsrf/bf-2}BaseFaultType
    
    # Element FaultCause ({http://docs.oasis-open.org/wsrf/bf-2}FaultCause) inherited from {http://docs.oasis-open.org/wsrf/bf-2}BaseFaultType
    
    # Element Description ({http://docs.oasis-open.org/wsrf/bf-2}Description) inherited from {http://docs.oasis-open.org/wsrf/bf-2}BaseFaultType
    
    # Element Timestamp ({http://docs.oasis-open.org/wsrf/bf-2}Timestamp) inherited from {http://docs.oasis-open.org/wsrf/bf-2}BaseFaultType
    _AttributeWildcard = pyxb.binding.content.Wildcard(process_contents=pyxb.binding.content.Wildcard.PC_lax, namespace_constraint=(pyxb.binding.content.Wildcard.NC_not, u'http://docs.oasis-open.org/wsrf/bf-2'))
    _HasWildcardElement = True

    _ElementMap = pyxb.bundles.wssplat.wsrf_bf.BaseFaultType._ElementMap.copy()
    _ElementMap.update({
        
    })
    _AttributeMap = pyxb.bundles.wssplat.wsrf_bf.BaseFaultType._AttributeMap.copy()
    _AttributeMap.update({
        
    })
Namespace.addCategoryObject('typeBinding', u'NotifyMessageNotSupportedFaultType', NotifyMessageNotSupportedFaultType)


# Complex type [anonymous] with content type ELEMENT_ONLY
class CTD_ANON_8 (pyxb.binding.basis.complexTypeDefinition):
    _TypeDefinition = None
    _ContentTypeTag = pyxb.binding.basis.complexTypeDefinition._CT_ELEMENT_ONLY
    _Abstract = False
    _ExpandedName = None
    _DefinitionLocation = pyxb.utils.utility.Location('/tmp/pyxbdist.RHB65sy/PyXB-1.1.5/pyxb/bundles/wssplat/schemas/wsnt.xsd', 461, 4)
    # Base type is pyxb.binding.datatypes.anyType
    
    # Element {http://docs.oasis-open.org/wsn/b-2}TerminationTime uses Python identifier TerminationTime
    __TerminationTime = pyxb.binding.content.ElementUse(pyxb.namespace.ExpandedName(Namespace, u'TerminationTime'), 'TerminationTime', '__httpdocs_oasis_open_orgwsnb_2_CTD_ANON_8_httpdocs_oasis_open_orgwsnb_2TerminationTime', False)
    __TerminationTime._DeclarationLocation = pyxb.utils.utility.Location('/tmp/pyxbdist.RHB65sy/PyXB-1.1.5/pyxb/bundles/wssplat/schemas/wsnt.xsd', 463, 8)
    __TerminationTime._UseLocation = pyxb.utils.utility.Location('/tmp/pyxbdist.RHB65sy/PyXB-1.1.5/pyxb/bundles/wssplat/schemas/wsnt.xsd', 462, 6)

    
    TerminationTime = property(__TerminationTime.value, __TerminationTime.set, None, None)

    _HasWildcardElement = True

    _ElementMap = {
        __TerminationTime.name() : __TerminationTime
    }
    _AttributeMap = {
        
    }



# Complex type [anonymous] with content type ELEMENT_ONLY
class CTD_ANON_9 (pyxb.binding.basis.complexTypeDefinition):
    _TypeDefinition = None
    _ContentTypeTag = pyxb.binding.basis.complexTypeDefinition._CT_ELEMENT_ONLY
    _Abstract = False
    _ExpandedName = None
    _DefinitionLocation = pyxb.utils.utility.Location('/tmp/pyxbdist.RHB65sy/PyXB-1.1.5/pyxb/bundles/wssplat/schemas/wsnt.xsd', 529, 4)
    # Base type is pyxb.binding.datatypes.anyType
    _HasWildcardElement = True

    _ElementMap = {
        
    }
    _AttributeMap = {
        
    }



# Complex type [anonymous] with content type ELEMENT_ONLY
class CTD_ANON_10 (pyxb.binding.basis.complexTypeDefinition):
    _TypeDefinition = None
    _ContentTypeTag = pyxb.binding.basis.complexTypeDefinition._CT_ELEMENT_ONLY
    _Abstract = False
    _ExpandedName = None
    _DefinitionLocation = pyxb.utils.utility.Location('/tmp/pyxbdist.RHB65sy/PyXB-1.1.5/pyxb/bundles/wssplat/schemas/wsnt.xsd', 474, 4)
    # Base type is pyxb.binding.datatypes.anyType
    
    # Element {http://docs.oasis-open.org/wsn/b-2}TerminationTime uses Python identifier TerminationTime
    __TerminationTime = pyxb.binding.content.ElementUse(pyxb.namespace.ExpandedName(Namespace, u'TerminationTime'), 'TerminationTime', '__httpdocs_oasis_open_orgwsnb_2_CTD_ANON_10_httpdocs_oasis_open_orgwsnb_2TerminationTime', False)
    __TerminationTime._DeclarationLocation = pyxb.utils.utility.Location('/tmp/pyxbdist.RHB65sy/PyXB-1.1.5/pyxb/bundles/wssplat/schemas/wsnt.xsd', 164, 2)
    __TerminationTime._UseLocation = pyxb.utils.utility.Location('/tmp/pyxbdist.RHB65sy/PyXB-1.1.5/pyxb/bundles/wssplat/schemas/wsnt.xsd', 475, 6)

    
    TerminationTime = property(__TerminationTime.value, __TerminationTime.set, None, None)

    
    # Element {http://docs.oasis-open.org/wsn/b-2}CurrentTime uses Python identifier CurrentTime
    __CurrentTime = pyxb.binding.content.ElementUse(pyxb.namespace.ExpandedName(Namespace, u'CurrentTime'), 'CurrentTime', '__httpdocs_oasis_open_orgwsnb_2_CTD_ANON_10_httpdocs_oasis_open_orgwsnb_2CurrentTime', False)
    __CurrentTime._DeclarationLocation = pyxb.utils.utility.Location('/tmp/pyxbdist.RHB65sy/PyXB-1.1.5/pyxb/bundles/wssplat/schemas/wsnt.xsd', 162, 2)
    __CurrentTime._UseLocation = pyxb.utils.utility.Location('/tmp/pyxbdist.RHB65sy/PyXB-1.1.5/pyxb/bundles/wssplat/schemas/wsnt.xsd', 475, 6)

    
    CurrentTime = property(__CurrentTime.value, __CurrentTime.set, None, None)

    _HasWildcardElement = True

    _ElementMap = {
        __TerminationTime.name() : __TerminationTime,
        __CurrentTime.name() : __CurrentTime
    }
    _AttributeMap = {
        
    }



# Complex type {http://docs.oasis-open.org/wsn/b-2}UnrecognizedPolicyRequestFaultType with content type ELEMENT_ONLY
class UnrecognizedPolicyRequestFaultType (pyxb.bundles.wssplat.wsrf_bf.BaseFaultType):
    _TypeDefinition = None
    _ContentTypeTag = pyxb.binding.basis.complexTypeDefinition._CT_ELEMENT_ONLY
    _Abstract = False
    _ExpandedName = pyxb.namespace.ExpandedName(Namespace, u'UnrecognizedPolicyRequestFaultType')
    _DefinitionLocation = pyxb.utils.utility.Location('/tmp/pyxbdist.RHB65sy/PyXB-1.1.5/pyxb/bundles/wssplat/schemas/wsnt.xsd', 308, 2)
    # Base type is pyxb.bundles.wssplat.wsrf_bf.BaseFaultType
    
    # Element ErrorCode ({http://docs.oasis-open.org/wsrf/bf-2}ErrorCode) inherited from {http://docs.oasis-open.org/wsrf/bf-2}BaseFaultType
    
    # Element Timestamp ({http://docs.oasis-open.org/wsrf/bf-2}Timestamp) inherited from {http://docs.oasis-open.org/wsrf/bf-2}BaseFaultType
    
    # Element FaultCause ({http://docs.oasis-open.org/wsrf/bf-2}FaultCause) inherited from {http://docs.oasis-open.org/wsrf/bf-2}BaseFaultType
    
    # Element Originator ({http://docs.oasis-open.org/wsrf/bf-2}Originator) inherited from {http://docs.oasis-open.org/wsrf/bf-2}BaseFaultType
    
    # Element {http://docs.oasis-open.org/wsn/b-2}UnrecognizedPolicy uses Python identifier UnrecognizedPolicy
    __UnrecognizedPolicy = pyxb.binding.content.ElementUse(pyxb.namespace.ExpandedName(Namespace, u'UnrecognizedPolicy'), 'UnrecognizedPolicy', '__httpdocs_oasis_open_orgwsnb_2_UnrecognizedPolicyRequestFaultType_httpdocs_oasis_open_orgwsnb_2UnrecognizedPolicy', True)
    __UnrecognizedPolicy._DeclarationLocation = pyxb.utils.utility.Location('/tmp/pyxbdist.RHB65sy/PyXB-1.1.5/pyxb/bundles/wssplat/schemas/wsnt.xsd', 312, 13)
    __UnrecognizedPolicy._UseLocation = None

    
    UnrecognizedPolicy = property(__UnrecognizedPolicy.value, __UnrecognizedPolicy.set, None, None)

    
    # Element Description ({http://docs.oasis-open.org/wsrf/bf-2}Description) inherited from {http://docs.oasis-open.org/wsrf/bf-2}BaseFaultType
    _AttributeWildcard = pyxb.binding.content.Wildcard(process_contents=pyxb.binding.content.Wildcard.PC_lax, namespace_constraint=(pyxb.binding.content.Wildcard.NC_not, u'http://docs.oasis-open.org/wsrf/bf-2'))
    _HasWildcardElement = True

    _ElementMap = pyxb.bundles.wssplat.wsrf_bf.BaseFaultType._ElementMap.copy()
    _ElementMap.update({
        __UnrecognizedPolicy.name() : __UnrecognizedPolicy
    })
    _AttributeMap = pyxb.bundles.wssplat.wsrf_bf.BaseFaultType._AttributeMap.copy()
    _AttributeMap.update({
        
    })
Namespace.addCategoryObject('typeBinding', u'UnrecognizedPolicyRequestFaultType', UnrecognizedPolicyRequestFaultType)


# Complex type {http://docs.oasis-open.org/wsn/b-2}UnacceptableInitialTerminationTimeFaultType with content type ELEMENT_ONLY
class UnacceptableInitialTerminationTimeFaultType (pyxb.bundles.wssplat.wsrf_bf.BaseFaultType):
    _TypeDefinition = None
    _ContentTypeTag = pyxb.binding.basis.complexTypeDefinition._CT_ELEMENT_ONLY
    _Abstract = False
    _ExpandedName = pyxb.namespace.ExpandedName(Namespace, u'UnacceptableInitialTerminationTimeFaultType')
    _DefinitionLocation = pyxb.utils.utility.Location('/tmp/pyxbdist.RHB65sy/PyXB-1.1.5/pyxb/bundles/wssplat/schemas/wsnt.xsd', 342, 2)
    # Base type is pyxb.bundles.wssplat.wsrf_bf.BaseFaultType
    
    # Element ErrorCode ({http://docs.oasis-open.org/wsrf/bf-2}ErrorCode) inherited from {http://docs.oasis-open.org/wsrf/bf-2}BaseFaultType
    
    # Element Originator ({http://docs.oasis-open.org/wsrf/bf-2}Originator) inherited from {http://docs.oasis-open.org/wsrf/bf-2}BaseFaultType
    
    # Element {http://docs.oasis-open.org/wsn/b-2}MinimumTime uses Python identifier MinimumTime
    __MinimumTime = pyxb.binding.content.ElementUse(pyxb.namespace.ExpandedName(Namespace, u'MinimumTime'), 'MinimumTime', '__httpdocs_oasis_open_orgwsnb_2_UnacceptableInitialTerminationTimeFaultType_httpdocs_oasis_open_orgwsnb_2MinimumTime', False)
    __MinimumTime._DeclarationLocation = pyxb.utils.utility.Location('/tmp/pyxbdist.RHB65sy/PyXB-1.1.5/pyxb/bundles/wssplat/schemas/wsnt.xsd', 346, 10)
    __MinimumTime._UseLocation = None

    
    MinimumTime = property(__MinimumTime.value, __MinimumTime.set, None, None)

    
    # Element FaultCause ({http://docs.oasis-open.org/wsrf/bf-2}FaultCause) inherited from {http://docs.oasis-open.org/wsrf/bf-2}BaseFaultType
    
    # Element Timestamp ({http://docs.oasis-open.org/wsrf/bf-2}Timestamp) inherited from {http://docs.oasis-open.org/wsrf/bf-2}BaseFaultType
    
    # Element {http://docs.oasis-open.org/wsn/b-2}MaximumTime uses Python identifier MaximumTime
    __MaximumTime = pyxb.binding.content.ElementUse(pyxb.namespace.ExpandedName(Namespace, u'MaximumTime'), 'MaximumTime', '__httpdocs_oasis_open_orgwsnb_2_UnacceptableInitialTerminationTimeFaultType_httpdocs_oasis_open_orgwsnb_2MaximumTime', False)
    __MaximumTime._DeclarationLocation = pyxb.utils.utility.Location('/tmp/pyxbdist.RHB65sy/PyXB-1.1.5/pyxb/bundles/wssplat/schemas/wsnt.xsd', 347, 10)
    __MaximumTime._UseLocation = None

    
    MaximumTime = property(__MaximumTime.value, __MaximumTime.set, None, None)

    
    # Element Description ({http://docs.oasis-open.org/wsrf/bf-2}Description) inherited from {http://docs.oasis-open.org/wsrf/bf-2}BaseFaultType
    _AttributeWildcard = pyxb.binding.content.Wildcard(process_contents=pyxb.binding.content.Wildcard.PC_lax, namespace_constraint=(pyxb.binding.content.Wildcard.NC_not, u'http://docs.oasis-open.org/wsrf/bf-2'))
    _HasWildcardElement = True

    _ElementMap = pyxb.bundles.wssplat.wsrf_bf.BaseFaultType._ElementMap.copy()
    _ElementMap.update({
        __MinimumTime.name() : __MinimumTime,
        __MaximumTime.name() : __MaximumTime
    })
    _AttributeMap = pyxb.bundles.wssplat.wsrf_bf.BaseFaultType._AttributeMap.copy()
    _AttributeMap.update({
        
    })
Namespace.addCategoryObject('typeBinding', u'UnacceptableInitialTerminationTimeFaultType', UnacceptableInitialTerminationTimeFaultType)


# Complex type [anonymous] with content type ELEMENT_ONLY
class CTD_ANON_11 (pyxb.binding.basis.complexTypeDefinition):
    _TypeDefinition = None
    _ContentTypeTag = pyxb.binding.basis.complexTypeDefinition._CT_ELEMENT_ONLY
    _Abstract = False
    _ExpandedName = None
    _DefinitionLocation = pyxb.utils.utility.Location('/tmp/pyxbdist.RHB65sy/PyXB-1.1.5/pyxb/bundles/wssplat/schemas/wsnt.xsd', 366, 4)
    # Base type is pyxb.binding.datatypes.anyType
    
    # Element {http://docs.oasis-open.org/wsn/b-2}MaximumNumber uses Python identifier MaximumNumber
    __MaximumNumber = pyxb.binding.content.ElementUse(pyxb.namespace.ExpandedName(Namespace, u'MaximumNumber'), 'MaximumNumber', '__httpdocs_oasis_open_orgwsnb_2_CTD_ANON_11_httpdocs_oasis_open_orgwsnb_2MaximumNumber', False)
    __MaximumNumber._DeclarationLocation = pyxb.utils.utility.Location('/tmp/pyxbdist.RHB65sy/PyXB-1.1.5/pyxb/bundles/wssplat/schemas/wsnt.xsd', 368, 8)
    __MaximumNumber._UseLocation = pyxb.utils.utility.Location('/tmp/pyxbdist.RHB65sy/PyXB-1.1.5/pyxb/bundles/wssplat/schemas/wsnt.xsd', 367, 6)

    
    MaximumNumber = property(__MaximumNumber.value, __MaximumNumber.set, None, None)

    _AttributeWildcard = pyxb.binding.content.Wildcard(process_contents=pyxb.binding.content.Wildcard.PC_strict, namespace_constraint=pyxb.binding.content.Wildcard.NC_any)
    _HasWildcardElement = True

    _ElementMap = {
        __MaximumNumber.name() : __MaximumNumber
    }
    _AttributeMap = {
        
    }



# Complex type {http://docs.oasis-open.org/wsn/b-2}UnacceptableTerminationTimeFaultType with content type ELEMENT_ONLY
class UnacceptableTerminationTimeFaultType (pyxb.bundles.wssplat.wsrf_bf.BaseFaultType):
    _TypeDefinition = None
    _ContentTypeTag = pyxb.binding.basis.complexTypeDefinition._CT_ELEMENT_ONLY
    _Abstract = False
    _ExpandedName = pyxb.namespace.ExpandedName(Namespace, u'UnacceptableTerminationTimeFaultType')
    _DefinitionLocation = pyxb.utils.utility.Location('/tmp/pyxbdist.RHB65sy/PyXB-1.1.5/pyxb/bundles/wssplat/schemas/wsnt.xsd', 486, 2)
    # Base type is pyxb.bundles.wssplat.wsrf_bf.BaseFaultType
    
    # Element ErrorCode ({http://docs.oasis-open.org/wsrf/bf-2}ErrorCode) inherited from {http://docs.oasis-open.org/wsrf/bf-2}BaseFaultType
    
    # Element Originator ({http://docs.oasis-open.org/wsrf/bf-2}Originator) inherited from {http://docs.oasis-open.org/wsrf/bf-2}BaseFaultType
    
    # Element {http://docs.oasis-open.org/wsn/b-2}MaximumTime uses Python identifier MaximumTime
    __MaximumTime = pyxb.binding.content.ElementUse(pyxb.namespace.ExpandedName(Namespace, u'MaximumTime'), 'MaximumTime', '__httpdocs_oasis_open_orgwsnb_2_UnacceptableTerminationTimeFaultType_httpdocs_oasis_open_orgwsnb_2MaximumTime', False)
    __MaximumTime._DeclarationLocation = pyxb.utils.utility.Location('/tmp/pyxbdist.RHB65sy/PyXB-1.1.5/pyxb/bundles/wssplat/schemas/wsnt.xsd', 491, 10)
    __MaximumTime._UseLocation = None

    
    MaximumTime = property(__MaximumTime.value, __MaximumTime.set, None, None)

    
    # Element FaultCause ({http://docs.oasis-open.org/wsrf/bf-2}FaultCause) inherited from {http://docs.oasis-open.org/wsrf/bf-2}BaseFaultType
    
    # Element Timestamp ({http://docs.oasis-open.org/wsrf/bf-2}Timestamp) inherited from {http://docs.oasis-open.org/wsrf/bf-2}BaseFaultType
    
    # Element {http://docs.oasis-open.org/wsn/b-2}MinimumTime uses Python identifier MinimumTime
    __MinimumTime = pyxb.binding.content.ElementUse(pyxb.namespace.ExpandedName(Namespace, u'MinimumTime'), 'MinimumTime', '__httpdocs_oasis_open_orgwsnb_2_UnacceptableTerminationTimeFaultType_httpdocs_oasis_open_orgwsnb_2MinimumTime', False)
    __MinimumTime._DeclarationLocation = pyxb.utils.utility.Location('/tmp/pyxbdist.RHB65sy/PyXB-1.1.5/pyxb/bundles/wssplat/schemas/wsnt.xsd', 490, 10)
    __MinimumTime._UseLocation = None

    
    MinimumTime = property(__MinimumTime.value, __MinimumTime.set, None, None)

    
    # Element Description ({http://docs.oasis-open.org/wsrf/bf-2}Description) inherited from {http://docs.oasis-open.org/wsrf/bf-2}BaseFaultType
    _AttributeWildcard = pyxb.binding.content.Wildcard(process_contents=pyxb.binding.content.Wildcard.PC_lax, namespace_constraint=(pyxb.binding.content.Wildcard.NC_not, u'http://docs.oasis-open.org/wsrf/bf-2'))
    _HasWildcardElement = True

    _ElementMap = pyxb.bundles.wssplat.wsrf_bf.BaseFaultType._ElementMap.copy()
    _ElementMap.update({
        __MaximumTime.name() : __MaximumTime,
        __MinimumTime.name() : __MinimumTime
    })
    _AttributeMap = pyxb.bundles.wssplat.wsrf_bf.BaseFaultType._AttributeMap.copy()
    _AttributeMap.update({
        
    })
Namespace.addCategoryObject('typeBinding', u'UnacceptableTerminationTimeFaultType', UnacceptableTerminationTimeFaultType)


# Complex type [anonymous] with content type ELEMENT_ONLY
class CTD_ANON_12 (pyxb.binding.basis.complexTypeDefinition):
    _TypeDefinition = None
    _ContentTypeTag = pyxb.binding.basis.complexTypeDefinition._CT_ELEMENT_ONLY
    _Abstract = False
    _ExpandedName = None
    _DefinitionLocation = pyxb.utils.utility.Location('/tmp/pyxbdist.RHB65sy/PyXB-1.1.5/pyxb/bundles/wssplat/schemas/wsnt.xsd', 379, 4)
    # Base type is pyxb.binding.datatypes.anyType
    
    # Element {http://docs.oasis-open.org/wsn/b-2}NotificationMessage uses Python identifier NotificationMessage
    __NotificationMessage = pyxb.binding.content.ElementUse(pyxb.namespace.ExpandedName(Namespace, u'NotificationMessage'), 'NotificationMessage', '__httpdocs_oasis_open_orgwsnb_2_CTD_ANON_12_httpdocs_oasis_open_orgwsnb_2NotificationMessage', True)
    __NotificationMessage._DeclarationLocation = pyxb.utils.utility.Location('/tmp/pyxbdist.RHB65sy/PyXB-1.1.5/pyxb/bundles/wssplat/schemas/wsnt.xsd', 141, 2)
    __NotificationMessage._UseLocation = pyxb.utils.utility.Location('/tmp/pyxbdist.RHB65sy/PyXB-1.1.5/pyxb/bundles/wssplat/schemas/wsnt.xsd', 380, 6)

    
    NotificationMessage = property(__NotificationMessage.value, __NotificationMessage.set, None, None)

    _AttributeWildcard = pyxb.binding.content.Wildcard(process_contents=pyxb.binding.content.Wildcard.PC_strict, namespace_constraint=pyxb.binding.content.Wildcard.NC_any)
    _HasWildcardElement = True

    _ElementMap = {
        __NotificationMessage.name() : __NotificationMessage
    }
    _AttributeMap = {
        
    }



# Complex type [anonymous] with content type ELEMENT_ONLY
class CTD_ANON_13 (pyxb.binding.basis.complexTypeDefinition):
    _TypeDefinition = None
    _ContentTypeTag = pyxb.binding.basis.complexTypeDefinition._CT_ELEMENT_ONLY
    _Abstract = False
    _ExpandedName = None
    _DefinitionLocation = pyxb.utils.utility.Location('/tmp/pyxbdist.RHB65sy/PyXB-1.1.5/pyxb/bundles/wssplat/schemas/wsnt.xsd', 146, 4)
    # Base type is pyxb.binding.datatypes.anyType
    
    # Element {http://docs.oasis-open.org/wsn/b-2}NotificationMessage uses Python identifier NotificationMessage
    __NotificationMessage = pyxb.binding.content.ElementUse(pyxb.namespace.ExpandedName(Namespace, u'NotificationMessage'), 'NotificationMessage', '__httpdocs_oasis_open_orgwsnb_2_CTD_ANON_13_httpdocs_oasis_open_orgwsnb_2NotificationMessage', True)
    __NotificationMessage._DeclarationLocation = pyxb.utils.utility.Location('/tmp/pyxbdist.RHB65sy/PyXB-1.1.5/pyxb/bundles/wssplat/schemas/wsnt.xsd', 141, 2)
    __NotificationMessage._UseLocation = pyxb.utils.utility.Location('/tmp/pyxbdist.RHB65sy/PyXB-1.1.5/pyxb/bundles/wssplat/schemas/wsnt.xsd', 147, 6)

    
    NotificationMessage = property(__NotificationMessage.value, __NotificationMessage.set, None, None)

    _HasWildcardElement = True

    _ElementMap = {
        __NotificationMessage.name() : __NotificationMessage
    }
    _AttributeMap = {
        
    }



# Complex type {http://docs.oasis-open.org/wsn/b-2}PauseFailedFaultType with content type ELEMENT_ONLY
class PauseFailedFaultType (pyxb.bundles.wssplat.wsrf_bf.BaseFaultType):
    _TypeDefinition = None
    _ContentTypeTag = pyxb.binding.basis.complexTypeDefinition._CT_ELEMENT_ONLY
    _Abstract = False
    _ExpandedName = pyxb.namespace.ExpandedName(Namespace, u'PauseFailedFaultType')
    _DefinitionLocation = pyxb.utils.utility.Location('/tmp/pyxbdist.RHB65sy/PyXB-1.1.5/pyxb/bundles/wssplat/schemas/wsnt.xsd', 564, 2)
    # Base type is pyxb.bundles.wssplat.wsrf_bf.BaseFaultType
    
    # Element ErrorCode ({http://docs.oasis-open.org/wsrf/bf-2}ErrorCode) inherited from {http://docs.oasis-open.org/wsrf/bf-2}BaseFaultType
    
    # Element Originator ({http://docs.oasis-open.org/wsrf/bf-2}Originator) inherited from {http://docs.oasis-open.org/wsrf/bf-2}BaseFaultType
    
    # Element FaultCause ({http://docs.oasis-open.org/wsrf/bf-2}FaultCause) inherited from {http://docs.oasis-open.org/wsrf/bf-2}BaseFaultType
    
    # Element Description ({http://docs.oasis-open.org/wsrf/bf-2}Description) inherited from {http://docs.oasis-open.org/wsrf/bf-2}BaseFaultType
    
    # Element Timestamp ({http://docs.oasis-open.org/wsrf/bf-2}Timestamp) inherited from {http://docs.oasis-open.org/wsrf/bf-2}BaseFaultType
    _AttributeWildcard = pyxb.binding.content.Wildcard(process_contents=pyxb.binding.content.Wildcard.PC_lax, namespace_constraint=(pyxb.binding.content.Wildcard.NC_not, u'http://docs.oasis-open.org/wsrf/bf-2'))
    _HasWildcardElement = True

    _ElementMap = pyxb.bundles.wssplat.wsrf_bf.BaseFaultType._ElementMap.copy()
    _ElementMap.update({
        
    })
    _AttributeMap = pyxb.bundles.wssplat.wsrf_bf.BaseFaultType._AttributeMap.copy()
    _AttributeMap.update({
        
    })
Namespace.addCategoryObject('typeBinding', u'PauseFailedFaultType', PauseFailedFaultType)


# Complex type [anonymous] with content type ELEMENT_ONLY
class CTD_ANON_14 (pyxb.binding.basis.complexTypeDefinition):
    _TypeDefinition = None
    _ContentTypeTag = pyxb.binding.basis.complexTypeDefinition._CT_ELEMENT_ONLY
    _Abstract = False
    _ExpandedName = None
    _DefinitionLocation = pyxb.utils.utility.Location('/tmp/pyxbdist.RHB65sy/PyXB-1.1.5/pyxb/bundles/wssplat/schemas/wsnt.xsd', 510, 4)
    # Base type is pyxb.binding.datatypes.anyType
    _HasWildcardElement = True

    _ElementMap = {
        
    }
    _AttributeMap = {
        
    }



# Complex type [anonymous] with content type ELEMENT_ONLY
class CTD_ANON_15 (pyxb.binding.basis.complexTypeDefinition):
    _TypeDefinition = None
    _ContentTypeTag = pyxb.binding.basis.complexTypeDefinition._CT_ELEMENT_ONLY
    _Abstract = False
    _ExpandedName = None
    _DefinitionLocation = pyxb.utils.utility.Location('/tmp/pyxbdist.RHB65sy/PyXB-1.1.5/pyxb/bundles/wssplat/schemas/wsnt.xsd', 391, 4)
    # Base type is pyxb.binding.datatypes.anyType
    _AttributeWildcard = pyxb.binding.content.Wildcard(process_contents=pyxb.binding.content.Wildcard.PC_strict, namespace_constraint=pyxb.binding.content.Wildcard.NC_any)
    _HasWildcardElement = True

    _ElementMap = {
        
    }
    _AttributeMap = {
        
    }



# Complex type {http://docs.oasis-open.org/wsn/b-2}UnableToDestroySubscriptionFaultType with content type ELEMENT_ONLY
class UnableToDestroySubscriptionFaultType (pyxb.bundles.wssplat.wsrf_bf.BaseFaultType):
    _TypeDefinition = None
    _ContentTypeTag = pyxb.binding.basis.complexTypeDefinition._CT_ELEMENT_ONLY
    _Abstract = False
    _ExpandedName = pyxb.namespace.ExpandedName(Namespace, u'UnableToDestroySubscriptionFaultType')
    _DefinitionLocation = pyxb.utils.utility.Location('/tmp/pyxbdist.RHB65sy/PyXB-1.1.5/pyxb/bundles/wssplat/schemas/wsnt.xsd', 518, 2)
    # Base type is pyxb.bundles.wssplat.wsrf_bf.BaseFaultType
    
    # Element ErrorCode ({http://docs.oasis-open.org/wsrf/bf-2}ErrorCode) inherited from {http://docs.oasis-open.org/wsrf/bf-2}BaseFaultType
    
    # Element Originator ({http://docs.oasis-open.org/wsrf/bf-2}Originator) inherited from {http://docs.oasis-open.org/wsrf/bf-2}BaseFaultType
    
    # Element FaultCause ({http://docs.oasis-open.org/wsrf/bf-2}FaultCause) inherited from {http://docs.oasis-open.org/wsrf/bf-2}BaseFaultType
    
    # Element Description ({http://docs.oasis-open.org/wsrf/bf-2}Description) inherited from {http://docs.oasis-open.org/wsrf/bf-2}BaseFaultType
    
    # Element Timestamp ({http://docs.oasis-open.org/wsrf/bf-2}Timestamp) inherited from {http://docs.oasis-open.org/wsrf/bf-2}BaseFaultType
    _AttributeWildcard = pyxb.binding.content.Wildcard(process_contents=pyxb.binding.content.Wildcard.PC_lax, namespace_constraint=(pyxb.binding.content.Wildcard.NC_not, u'http://docs.oasis-open.org/wsrf/bf-2'))
    _HasWildcardElement = True

    _ElementMap = pyxb.bundles.wssplat.wsrf_bf.BaseFaultType._ElementMap.copy()
    _ElementMap.update({
        
    })
    _AttributeMap = pyxb.bundles.wssplat.wsrf_bf.BaseFaultType._AttributeMap.copy()
    _AttributeMap.update({
        
    })
Namespace.addCategoryObject('typeBinding', u'UnableToDestroySubscriptionFaultType', UnableToDestroySubscriptionFaultType)


# Complex type {http://docs.oasis-open.org/wsn/b-2}ResumeFailedFaultType with content type ELEMENT_ONLY
class ResumeFailedFaultType (pyxb.bundles.wssplat.wsrf_bf.BaseFaultType):
    _TypeDefinition = None
    _ContentTypeTag = pyxb.binding.basis.complexTypeDefinition._CT_ELEMENT_ONLY
    _Abstract = False
    _ExpandedName = pyxb.namespace.ExpandedName(Namespace, u'ResumeFailedFaultType')
    _DefinitionLocation = pyxb.utils.utility.Location('/tmp/pyxbdist.RHB65sy/PyXB-1.1.5/pyxb/bundles/wssplat/schemas/wsnt.xsd', 572, 2)
    # Base type is pyxb.bundles.wssplat.wsrf_bf.BaseFaultType
    
    # Element ErrorCode ({http://docs.oasis-open.org/wsrf/bf-2}ErrorCode) inherited from {http://docs.oasis-open.org/wsrf/bf-2}BaseFaultType
    
    # Element Originator ({http://docs.oasis-open.org/wsrf/bf-2}Originator) inherited from {http://docs.oasis-open.org/wsrf/bf-2}BaseFaultType
    
    # Element FaultCause ({http://docs.oasis-open.org/wsrf/bf-2}FaultCause) inherited from {http://docs.oasis-open.org/wsrf/bf-2}BaseFaultType
    
    # Element Description ({http://docs.oasis-open.org/wsrf/bf-2}Description) inherited from {http://docs.oasis-open.org/wsrf/bf-2}BaseFaultType
    
    # Element Timestamp ({http://docs.oasis-open.org/wsrf/bf-2}Timestamp) inherited from {http://docs.oasis-open.org/wsrf/bf-2}BaseFaultType
    _AttributeWildcard = pyxb.binding.content.Wildcard(process_contents=pyxb.binding.content.Wildcard.PC_lax, namespace_constraint=(pyxb.binding.content.Wildcard.NC_not, u'http://docs.oasis-open.org/wsrf/bf-2'))
    _HasWildcardElement = True

    _ElementMap = pyxb.bundles.wssplat.wsrf_bf.BaseFaultType._ElementMap.copy()
    _ElementMap.update({
        
    })
    _AttributeMap = pyxb.bundles.wssplat.wsrf_bf.BaseFaultType._AttributeMap.copy()
    _AttributeMap.update({
        
    })
Namespace.addCategoryObject('typeBinding', u'ResumeFailedFaultType', ResumeFailedFaultType)


# Complex type [anonymous] with content type ELEMENT_ONLY
class CTD_ANON_16 (pyxb.binding.basis.complexTypeDefinition):
    _TypeDefinition = None
    _ContentTypeTag = pyxb.binding.basis.complexTypeDefinition._CT_ELEMENT_ONLY
    _Abstract = False
    _ExpandedName = None
    _DefinitionLocation = pyxb.utils.utility.Location('/tmp/pyxbdist.RHB65sy/PyXB-1.1.5/pyxb/bundles/wssplat/schemas/wsnt.xsd', 538, 4)
    # Base type is pyxb.binding.datatypes.anyType
    _HasWildcardElement = True

    _ElementMap = {
        
    }
    _AttributeMap = {
        
    }



# Complex type {http://docs.oasis-open.org/wsn/b-2}UnableToGetMessagesFaultType with content type ELEMENT_ONLY
class UnableToGetMessagesFaultType (pyxb.bundles.wssplat.wsrf_bf.BaseFaultType):
    _TypeDefinition = None
    _ContentTypeTag = pyxb.binding.basis.complexTypeDefinition._CT_ELEMENT_ONLY
    _Abstract = False
    _ExpandedName = pyxb.namespace.ExpandedName(Namespace, u'UnableToGetMessagesFaultType')
    _DefinitionLocation = pyxb.utils.utility.Location('/tmp/pyxbdist.RHB65sy/PyXB-1.1.5/pyxb/bundles/wssplat/schemas/wsnt.xsd', 410, 2)
    # Base type is pyxb.bundles.wssplat.wsrf_bf.BaseFaultType
    
    # Element ErrorCode ({http://docs.oasis-open.org/wsrf/bf-2}ErrorCode) inherited from {http://docs.oasis-open.org/wsrf/bf-2}BaseFaultType
    
    # Element Originator ({http://docs.oasis-open.org/wsrf/bf-2}Originator) inherited from {http://docs.oasis-open.org/wsrf/bf-2}BaseFaultType
    
    # Element FaultCause ({http://docs.oasis-open.org/wsrf/bf-2}FaultCause) inherited from {http://docs.oasis-open.org/wsrf/bf-2}BaseFaultType
    
    # Element Description ({http://docs.oasis-open.org/wsrf/bf-2}Description) inherited from {http://docs.oasis-open.org/wsrf/bf-2}BaseFaultType
    
    # Element Timestamp ({http://docs.oasis-open.org/wsrf/bf-2}Timestamp) inherited from {http://docs.oasis-open.org/wsrf/bf-2}BaseFaultType
    _AttributeWildcard = pyxb.binding.content.Wildcard(process_contents=pyxb.binding.content.Wildcard.PC_lax, namespace_constraint=(pyxb.binding.content.Wildcard.NC_not, u'http://docs.oasis-open.org/wsrf/bf-2'))
    _HasWildcardElement = True

    _ElementMap = pyxb.bundles.wssplat.wsrf_bf.BaseFaultType._ElementMap.copy()
    _ElementMap.update({
        
    })
    _AttributeMap = pyxb.bundles.wssplat.wsrf_bf.BaseFaultType._AttributeMap.copy()
    _AttributeMap.update({
        
    })
Namespace.addCategoryObject('typeBinding', u'UnableToGetMessagesFaultType', UnableToGetMessagesFaultType)


# Complex type {http://docs.oasis-open.org/wsn/b-2}UnableToDestroyPullPointFaultType with content type ELEMENT_ONLY
class UnableToDestroyPullPointFaultType (pyxb.bundles.wssplat.wsrf_bf.BaseFaultType):
    _TypeDefinition = None
    _ContentTypeTag = pyxb.binding.basis.complexTypeDefinition._CT_ELEMENT_ONLY
    _Abstract = False
    _ExpandedName = pyxb.namespace.ExpandedName(Namespace, u'UnableToDestroyPullPointFaultType')
    _DefinitionLocation = pyxb.utils.utility.Location('/tmp/pyxbdist.RHB65sy/PyXB-1.1.5/pyxb/bundles/wssplat/schemas/wsnt.xsd', 419, 0)
    # Base type is pyxb.bundles.wssplat.wsrf_bf.BaseFaultType
    
    # Element ErrorCode ({http://docs.oasis-open.org/wsrf/bf-2}ErrorCode) inherited from {http://docs.oasis-open.org/wsrf/bf-2}BaseFaultType
    
    # Element Originator ({http://docs.oasis-open.org/wsrf/bf-2}Originator) inherited from {http://docs.oasis-open.org/wsrf/bf-2}BaseFaultType
    
    # Element FaultCause ({http://docs.oasis-open.org/wsrf/bf-2}FaultCause) inherited from {http://docs.oasis-open.org/wsrf/bf-2}BaseFaultType
    
    # Element Description ({http://docs.oasis-open.org/wsrf/bf-2}Description) inherited from {http://docs.oasis-open.org/wsrf/bf-2}BaseFaultType
    
    # Element Timestamp ({http://docs.oasis-open.org/wsrf/bf-2}Timestamp) inherited from {http://docs.oasis-open.org/wsrf/bf-2}BaseFaultType
    _AttributeWildcard = pyxb.binding.content.Wildcard(process_contents=pyxb.binding.content.Wildcard.PC_lax, namespace_constraint=(pyxb.binding.content.Wildcard.NC_not, u'http://docs.oasis-open.org/wsrf/bf-2'))
    _HasWildcardElement = True

    _ElementMap = pyxb.bundles.wssplat.wsrf_bf.BaseFaultType._ElementMap.copy()
    _ElementMap.update({
        
    })
    _AttributeMap = pyxb.bundles.wssplat.wsrf_bf.BaseFaultType._AttributeMap.copy()
    _AttributeMap.update({
        
    })
Namespace.addCategoryObject('typeBinding', u'UnableToDestroyPullPointFaultType', UnableToDestroyPullPointFaultType)


# Complex type [anonymous] with content type ELEMENT_ONLY
class CTD_ANON_17 (pyxb.binding.basis.complexTypeDefinition):
    _TypeDefinition = None
    _ContentTypeTag = pyxb.binding.basis.complexTypeDefinition._CT_ELEMENT_ONLY
    _Abstract = False
    _ExpandedName = None
    _DefinitionLocation = pyxb.utils.utility.Location('/tmp/pyxbdist.RHB65sy/PyXB-1.1.5/pyxb/bundles/wssplat/schemas/wsnt.xsd', 430, 4)
    # Base type is pyxb.binding.datatypes.anyType
    _AttributeWildcard = pyxb.binding.content.Wildcard(process_contents=pyxb.binding.content.Wildcard.PC_strict, namespace_constraint=pyxb.binding.content.Wildcard.NC_any)
    _HasWildcardElement = True

    _ElementMap = {
        
    }
    _AttributeMap = {
        
    }



# Complex type [anonymous] with content type ELEMENT_ONLY
class CTD_ANON_18 (pyxb.binding.basis.complexTypeDefinition):
    _TypeDefinition = None
    _ContentTypeTag = pyxb.binding.basis.complexTypeDefinition._CT_ELEMENT_ONLY
    _Abstract = False
    _ExpandedName = None
    _DefinitionLocation = pyxb.utils.utility.Location('/tmp/pyxbdist.RHB65sy/PyXB-1.1.5/pyxb/bundles/wssplat/schemas/wsnt.xsd', 190, 10)
    # Base type is pyxb.binding.datatypes.anyType
    _HasWildcardElement = True

    _ElementMap = {
        
    }
    _AttributeMap = {
        
    }



# Complex type [anonymous] with content type ELEMENT_ONLY
class CTD_ANON_19 (pyxb.binding.basis.complexTypeDefinition):
    _TypeDefinition = None
    _ContentTypeTag = pyxb.binding.basis.complexTypeDefinition._CT_ELEMENT_ONLY
    _Abstract = False
    _ExpandedName = None
    _DefinitionLocation = pyxb.utils.utility.Location('/tmp/pyxbdist.RHB65sy/PyXB-1.1.5/pyxb/bundles/wssplat/schemas/wsnt.xsd', 547, 4)
    # Base type is pyxb.binding.datatypes.anyType
    _HasWildcardElement = True

    _ElementMap = {
        
    }
    _AttributeMap = {
        
    }



# Complex type [anonymous] with content type ELEMENT_ONLY
class CTD_ANON_20 (pyxb.binding.basis.complexTypeDefinition):
    _TypeDefinition = None
    _ContentTypeTag = pyxb.binding.basis.complexTypeDefinition._CT_ELEMENT_ONLY
    _Abstract = False
    _ExpandedName = None
    _DefinitionLocation = pyxb.utils.utility.Location('/tmp/pyxbdist.RHB65sy/PyXB-1.1.5/pyxb/bundles/wssplat/schemas/wsnt.xsd', 501, 4)
    # Base type is pyxb.binding.datatypes.anyType
    _HasWildcardElement = True

    _ElementMap = {
        
    }
    _AttributeMap = {
        
    }



# Complex type [anonymous] with content type ELEMENT_ONLY
class CTD_ANON_21 (pyxb.binding.basis.complexTypeDefinition):
    _TypeDefinition = None
    _ContentTypeTag = pyxb.binding.basis.complexTypeDefinition._CT_ELEMENT_ONLY
    _Abstract = False
    _ExpandedName = None
    _DefinitionLocation = pyxb.utils.utility.Location('/tmp/pyxbdist.RHB65sy/PyXB-1.1.5/pyxb/bundles/wssplat/schemas/wsnt.xsd', 440, 4)
    # Base type is pyxb.binding.datatypes.anyType
    
    # Element {http://docs.oasis-open.org/wsn/b-2}PullPoint uses Python identifier PullPoint
    __PullPoint = pyxb.binding.content.ElementUse(pyxb.namespace.ExpandedName(Namespace, u'PullPoint'), 'PullPoint', '__httpdocs_oasis_open_orgwsnb_2_CTD_ANON_21_httpdocs_oasis_open_orgwsnb_2PullPoint', False)
    __PullPoint._DeclarationLocation = pyxb.utils.utility.Location('/tmp/pyxbdist.RHB65sy/PyXB-1.1.5/pyxb/bundles/wssplat/schemas/wsnt.xsd', 442, 8)
    __PullPoint._UseLocation = pyxb.utils.utility.Location('/tmp/pyxbdist.RHB65sy/PyXB-1.1.5/pyxb/bundles/wssplat/schemas/wsnt.xsd', 441, 6)

    
    PullPoint = property(__PullPoint.value, __PullPoint.set, None, None)

    _AttributeWildcard = pyxb.binding.content.Wildcard(process_contents=pyxb.binding.content.Wildcard.PC_strict, namespace_constraint=pyxb.binding.content.Wildcard.NC_any)
    _HasWildcardElement = True

    _ElementMap = {
        __PullPoint.name() : __PullPoint
    }
    _AttributeMap = {
        
    }



# Complex type [anonymous] with content type ELEMENT_ONLY
class CTD_ANON_22 (pyxb.binding.basis.complexTypeDefinition):
    _TypeDefinition = None
    _ContentTypeTag = pyxb.binding.basis.complexTypeDefinition._CT_ELEMENT_ONLY
    _Abstract = False
    _ExpandedName = None
    _DefinitionLocation = pyxb.utils.utility.Location('/tmp/pyxbdist.RHB65sy/PyXB-1.1.5/pyxb/bundles/wssplat/schemas/wsnt.xsd', 556, 4)
    # Base type is pyxb.binding.datatypes.anyType
    _HasWildcardElement = True

    _ElementMap = {
        
    }
    _AttributeMap = {
        
    }



# Complex type {http://docs.oasis-open.org/wsn/b-2}UnableToCreatePullPointFaultType with content type ELEMENT_ONLY
class UnableToCreatePullPointFaultType (pyxb.bundles.wssplat.wsrf_bf.BaseFaultType):
    _TypeDefinition = None
    _ContentTypeTag = pyxb.binding.basis.complexTypeDefinition._CT_ELEMENT_ONLY
    _Abstract = False
    _ExpandedName = pyxb.namespace.ExpandedName(Namespace, u'UnableToCreatePullPointFaultType')
    _DefinitionLocation = pyxb.utils.utility.Location('/tmp/pyxbdist.RHB65sy/PyXB-1.1.5/pyxb/bundles/wssplat/schemas/wsnt.xsd', 451, 2)
    # Base type is pyxb.bundles.wssplat.wsrf_bf.BaseFaultType
    
    # Element ErrorCode ({http://docs.oasis-open.org/wsrf/bf-2}ErrorCode) inherited from {http://docs.oasis-open.org/wsrf/bf-2}BaseFaultType
    
    # Element Originator ({http://docs.oasis-open.org/wsrf/bf-2}Originator) inherited from {http://docs.oasis-open.org/wsrf/bf-2}BaseFaultType
    
    # Element FaultCause ({http://docs.oasis-open.org/wsrf/bf-2}FaultCause) inherited from {http://docs.oasis-open.org/wsrf/bf-2}BaseFaultType
    
    # Element Description ({http://docs.oasis-open.org/wsrf/bf-2}Description) inherited from {http://docs.oasis-open.org/wsrf/bf-2}BaseFaultType
    
    # Element Timestamp ({http://docs.oasis-open.org/wsrf/bf-2}Timestamp) inherited from {http://docs.oasis-open.org/wsrf/bf-2}BaseFaultType
    _AttributeWildcard = pyxb.binding.content.Wildcard(process_contents=pyxb.binding.content.Wildcard.PC_lax, namespace_constraint=(pyxb.binding.content.Wildcard.NC_not, u'http://docs.oasis-open.org/wsrf/bf-2'))
    _HasWildcardElement = True

    _ElementMap = pyxb.bundles.wssplat.wsrf_bf.BaseFaultType._ElementMap.copy()
    _ElementMap.update({
        
    })
    _AttributeMap = pyxb.bundles.wssplat.wsrf_bf.BaseFaultType._AttributeMap.copy()
    _AttributeMap.update({
        
    })
Namespace.addCategoryObject('typeBinding', u'UnableToCreatePullPointFaultType', UnableToCreatePullPointFaultType)


# Complex type [anonymous] with content type ELEMENT_ONLY
class CTD_ANON_23 (pyxb.binding.basis.complexTypeDefinition):
    _TypeDefinition = None
    _ContentTypeTag = pyxb.binding.basis.complexTypeDefinition._CT_ELEMENT_ONLY
    _Abstract = False
    _ExpandedName = None
    _DefinitionLocation = pyxb.utils.utility.Location('/tmp/pyxbdist.RHB65sy/PyXB-1.1.5/pyxb/bundles/wssplat/schemas/wsnt.xsd', 76, 4)
    # Base type is pyxb.binding.datatypes.anyType
    
    # Element {http://docs.oasis-open.org/wsn/b-2}FixedTopicSet uses Python identifier FixedTopicSet
    __FixedTopicSet = pyxb.binding.content.ElementUse(pyxb.namespace.ExpandedName(Namespace, u'FixedTopicSet'), 'FixedTopicSet', '__httpdocs_oasis_open_orgwsnb_2_CTD_ANON_23_httpdocs_oasis_open_orgwsnb_2FixedTopicSet', False)
    __FixedTopicSet._DeclarationLocation = pyxb.utils.utility.Location('/tmp/pyxbdist.RHB65sy/PyXB-1.1.5/pyxb/bundles/wssplat/schemas/wsnt.xsd', 72, 2)
    __FixedTopicSet._UseLocation = pyxb.utils.utility.Location('/tmp/pyxbdist.RHB65sy/PyXB-1.1.5/pyxb/bundles/wssplat/schemas/wsnt.xsd', 77, 6)

    
    FixedTopicSet = property(__FixedTopicSet.value, __FixedTopicSet.set, None, None)

    
    # Element {http://docs.oasis-open.org/wsn/t-1}TopicSet uses Python identifier TopicSet
    __TopicSet = pyxb.binding.content.ElementUse(pyxb.namespace.ExpandedName(pyxb.namespace.NamespaceForURI(u'http://docs.oasis-open.org/wsn/t-1'), u'TopicSet'), 'TopicSet', '__httpdocs_oasis_open_orgwsnb_2_CTD_ANON_23_httpdocs_oasis_open_orgwsnt_1TopicSet', False)
    __TopicSet._DeclarationLocation = pyxb.utils.utility.Location('/tmp/pyxbdist.RHB65sy/PyXB-1.1.5/pyxb/bundles/wssplat/schemas/wstop.xsd', 133, 2)
    __TopicSet._UseLocation = pyxb.utils.utility.Location('/tmp/pyxbdist.RHB65sy/PyXB-1.1.5/pyxb/bundles/wssplat/schemas/wsnt.xsd', 77, 6)

    
    TopicSet = property(__TopicSet.value, __TopicSet.set, None, None)

    
    # Element {http://docs.oasis-open.org/wsn/b-2}TopicExpressionDialect uses Python identifier TopicExpressionDialect
    __TopicExpressionDialect = pyxb.binding.content.ElementUse(pyxb.namespace.ExpandedName(Namespace, u'TopicExpressionDialect'), 'TopicExpressionDialect', '__httpdocs_oasis_open_orgwsnb_2_CTD_ANON_23_httpdocs_oasis_open_orgwsnb_2TopicExpressionDialect', True)
    __TopicExpressionDialect._DeclarationLocation = pyxb.utils.utility.Location('/tmp/pyxbdist.RHB65sy/PyXB-1.1.5/pyxb/bundles/wssplat/schemas/wsnt.xsd', 73, 2)
    __TopicExpressionDialect._UseLocation = pyxb.utils.utility.Location('/tmp/pyxbdist.RHB65sy/PyXB-1.1.5/pyxb/bundles/wssplat/schemas/wsnt.xsd', 77, 6)

    
    TopicExpressionDialect = property(__TopicExpressionDialect.value, __TopicExpressionDialect.set, None, None)

    
    # Element {http://docs.oasis-open.org/wsn/b-2}TopicExpression uses Python identifier TopicExpression
    __TopicExpression = pyxb.binding.content.ElementUse(pyxb.namespace.ExpandedName(Namespace, u'TopicExpression'), 'TopicExpression', '__httpdocs_oasis_open_orgwsnb_2_CTD_ANON_23_httpdocs_oasis_open_orgwsnb_2TopicExpression', True)
    __TopicExpression._DeclarationLocation = pyxb.utils.utility.Location('/tmp/pyxbdist.RHB65sy/PyXB-1.1.5/pyxb/bundles/wssplat/schemas/wsnt.xsd', 71, 2)
    __TopicExpression._UseLocation = pyxb.utils.utility.Location('/tmp/pyxbdist.RHB65sy/PyXB-1.1.5/pyxb/bundles/wssplat/schemas/wsnt.xsd', 77, 6)

    
    TopicExpression = property(__TopicExpression.value, __TopicExpression.set, None, None)


    _ElementMap = {
        __FixedTopicSet.name() : __FixedTopicSet,
        __TopicSet.name() : __TopicSet,
        __TopicExpressionDialect.name() : __TopicExpressionDialect,
        __TopicExpression.name() : __TopicExpression
    }
    _AttributeMap = {
        
    }



Filter = pyxb.binding.basis.element(pyxb.namespace.ExpandedName(Namespace, u'Filter'), FilterType)
Namespace.addCategoryObject('elementBinding', Filter.name().localName(), Filter)

SubscriptionPolicy = pyxb.binding.basis.element(pyxb.namespace.ExpandedName(Namespace, u'SubscriptionPolicy'), SubscriptionPolicyType)
Namespace.addCategoryObject('elementBinding', SubscriptionPolicy.name().localName(), SubscriptionPolicy)

CreationTime = pyxb.binding.basis.element(pyxb.namespace.ExpandedName(Namespace, u'CreationTime'), pyxb.binding.datatypes.dateTime)
Namespace.addCategoryObject('elementBinding', CreationTime.name().localName(), CreationTime)

SubscriptionManagerRP = pyxb.binding.basis.element(pyxb.namespace.ExpandedName(Namespace, u'SubscriptionManagerRP'), CTD_ANON)
Namespace.addCategoryObject('elementBinding', SubscriptionManagerRP.name().localName(), SubscriptionManagerRP)

MultipleTopicsSpecifiedFault = pyxb.binding.basis.element(pyxb.namespace.ExpandedName(Namespace, u'MultipleTopicsSpecifiedFault'), MultipleTopicsSpecifiedFaultType)
Namespace.addCategoryObject('elementBinding', MultipleTopicsSpecifiedFault.name().localName(), MultipleTopicsSpecifiedFault)

GetCurrentMessageResponse = pyxb.binding.basis.element(pyxb.namespace.ExpandedName(Namespace, u'GetCurrentMessageResponse'), CTD_ANON_)
Namespace.addCategoryObject('elementBinding', GetCurrentMessageResponse.name().localName(), GetCurrentMessageResponse)

GetCurrentMessage = pyxb.binding.basis.element(pyxb.namespace.ExpandedName(Namespace, u'GetCurrentMessage'), CTD_ANON_2)
Namespace.addCategoryObject('elementBinding', GetCurrentMessage.name().localName(), GetCurrentMessage)

SubscriptionReference = pyxb.binding.basis.element(pyxb.namespace.ExpandedName(Namespace, u'SubscriptionReference'), pyxb.bundles.wssplat.wsa.EndpointReferenceType)
Namespace.addCategoryObject('elementBinding', SubscriptionReference.name().localName(), SubscriptionReference)

Topic = pyxb.binding.basis.element(pyxb.namespace.ExpandedName(Namespace, u'Topic'), TopicExpressionType)
Namespace.addCategoryObject('elementBinding', Topic.name().localName(), Topic)

ProducerReference = pyxb.binding.basis.element(pyxb.namespace.ExpandedName(Namespace, u'ProducerReference'), pyxb.bundles.wssplat.wsa.EndpointReferenceType)
Namespace.addCategoryObject('elementBinding', ProducerReference.name().localName(), ProducerReference)

MessageContent = pyxb.binding.basis.element(pyxb.namespace.ExpandedName(Namespace, u'MessageContent'), QueryExpressionType)
Namespace.addCategoryObject('elementBinding', MessageContent.name().localName(), MessageContent)

ConsumerReference = pyxb.binding.basis.element(pyxb.namespace.ExpandedName(Namespace, u'ConsumerReference'), pyxb.bundles.wssplat.wsa.EndpointReferenceType)
Namespace.addCategoryObject('elementBinding', ConsumerReference.name().localName(), ConsumerReference)

FixedTopicSet = pyxb.binding.basis.element(pyxb.namespace.ExpandedName(Namespace, u'FixedTopicSet'), pyxb.binding.datatypes.boolean)
Namespace.addCategoryObject('elementBinding', FixedTopicSet.name().localName(), FixedTopicSet)

SubscribeCreationFailedFault = pyxb.binding.basis.element(pyxb.namespace.ExpandedName(Namespace, u'SubscribeCreationFailedFault'), SubscribeCreationFailedFaultType)
Namespace.addCategoryObject('elementBinding', SubscribeCreationFailedFault.name().localName(), SubscribeCreationFailedFault)

SubscribeResponse = pyxb.binding.basis.element(pyxb.namespace.ExpandedName(Namespace, u'SubscribeResponse'), CTD_ANON_4)
Namespace.addCategoryObject('elementBinding', SubscribeResponse.name().localName(), SubscribeResponse)

NotificationMessage = pyxb.binding.basis.element(pyxb.namespace.ExpandedName(Namespace, u'NotificationMessage'), NotificationMessageHolderType)
Namespace.addCategoryObject('elementBinding', NotificationMessage.name().localName(), NotificationMessage)

InvalidFilterFault = pyxb.binding.basis.element(pyxb.namespace.ExpandedName(Namespace, u'InvalidFilterFault'), InvalidFilterFaultType)
Namespace.addCategoryObject('elementBinding', InvalidFilterFault.name().localName(), InvalidFilterFault)

TopicExpressionDialectUnknownFault = pyxb.binding.basis.element(pyxb.namespace.ExpandedName(Namespace, u'TopicExpressionDialectUnknownFault'), TopicExpressionDialectUnknownFaultType)
Namespace.addCategoryObject('elementBinding', TopicExpressionDialectUnknownFault.name().localName(), TopicExpressionDialectUnknownFault)

InvalidTopicExpressionFault = pyxb.binding.basis.element(pyxb.namespace.ExpandedName(Namespace, u'InvalidTopicExpressionFault'), InvalidTopicExpressionFaultType)
Namespace.addCategoryObject('elementBinding', InvalidTopicExpressionFault.name().localName(), InvalidTopicExpressionFault)

TopicNotSupportedFault = pyxb.binding.basis.element(pyxb.namespace.ExpandedName(Namespace, u'TopicNotSupportedFault'), TopicNotSupportedFaultType)
Namespace.addCategoryObject('elementBinding', TopicNotSupportedFault.name().localName(), TopicNotSupportedFault)

CurrentTime = pyxb.binding.basis.element(pyxb.namespace.ExpandedName(Namespace, u'CurrentTime'), pyxb.binding.datatypes.dateTime)
Namespace.addCategoryObject('elementBinding', CurrentTime.name().localName(), CurrentTime)

TerminationTime = pyxb.binding.basis.element(pyxb.namespace.ExpandedName(Namespace, u'TerminationTime'), pyxb.binding.datatypes.dateTime, nillable=pyxb.binding.datatypes.boolean(1))
Namespace.addCategoryObject('elementBinding', TerminationTime.name().localName(), TerminationTime)

ProducerProperties = pyxb.binding.basis.element(pyxb.namespace.ExpandedName(Namespace, u'ProducerProperties'), QueryExpressionType)
Namespace.addCategoryObject('elementBinding', ProducerProperties.name().localName(), ProducerProperties)

InvalidProducerPropertiesExpressionFault = pyxb.binding.basis.element(pyxb.namespace.ExpandedName(Namespace, u'InvalidProducerPropertiesExpressionFault'), InvalidProducerPropertiesExpressionFaultType)
Namespace.addCategoryObject('elementBinding', InvalidProducerPropertiesExpressionFault.name().localName(), InvalidProducerPropertiesExpressionFault)

UseRaw = pyxb.binding.basis.element(pyxb.namespace.ExpandedName(Namespace, u'UseRaw'), CTD_ANON_5)
Namespace.addCategoryObject('elementBinding', UseRaw.name().localName(), UseRaw)

InvalidMessageContentExpressionFault = pyxb.binding.basis.element(pyxb.namespace.ExpandedName(Namespace, u'InvalidMessageContentExpressionFault'), InvalidMessageContentExpressionFaultType)
Namespace.addCategoryObject('elementBinding', InvalidMessageContentExpressionFault.name().localName(), InvalidMessageContentExpressionFault)

Subscribe = pyxb.binding.basis.element(pyxb.namespace.ExpandedName(Namespace, u'Subscribe'), CTD_ANON_6)
Namespace.addCategoryObject('elementBinding', Subscribe.name().localName(), Subscribe)

NoCurrentMessageOnTopicFault = pyxb.binding.basis.element(pyxb.namespace.ExpandedName(Namespace, u'NoCurrentMessageOnTopicFault'), NoCurrentMessageOnTopicFaultType)
Namespace.addCategoryObject('elementBinding', NoCurrentMessageOnTopicFault.name().localName(), NoCurrentMessageOnTopicFault)

DestroyPullPointResponse = pyxb.binding.basis.element(pyxb.namespace.ExpandedName(Namespace, u'DestroyPullPointResponse'), CTD_ANON_7)
Namespace.addCategoryObject('elementBinding', DestroyPullPointResponse.name().localName(), DestroyPullPointResponse)

UnsupportedPolicyRequestFault = pyxb.binding.basis.element(pyxb.namespace.ExpandedName(Namespace, u'UnsupportedPolicyRequestFault'), UnsupportedPolicyRequestFaultType)
Namespace.addCategoryObject('elementBinding', UnsupportedPolicyRequestFault.name().localName(), UnsupportedPolicyRequestFault)

NotifyMessageNotSupportedFault = pyxb.binding.basis.element(pyxb.namespace.ExpandedName(Namespace, u'NotifyMessageNotSupportedFault'), NotifyMessageNotSupportedFaultType)
Namespace.addCategoryObject('elementBinding', NotifyMessageNotSupportedFault.name().localName(), NotifyMessageNotSupportedFault)

Renew = pyxb.binding.basis.element(pyxb.namespace.ExpandedName(Namespace, u'Renew'), CTD_ANON_8)
Namespace.addCategoryObject('elementBinding', Renew.name().localName(), Renew)

PauseSubscription = pyxb.binding.basis.element(pyxb.namespace.ExpandedName(Namespace, u'PauseSubscription'), CTD_ANON_9)
Namespace.addCategoryObject('elementBinding', PauseSubscription.name().localName(), PauseSubscription)

RenewResponse = pyxb.binding.basis.element(pyxb.namespace.ExpandedName(Namespace, u'RenewResponse'), CTD_ANON_10)
Namespace.addCategoryObject('elementBinding', RenewResponse.name().localName(), RenewResponse)

UnrecognizedPolicyRequestFault = pyxb.binding.basis.element(pyxb.namespace.ExpandedName(Namespace, u'UnrecognizedPolicyRequestFault'), UnrecognizedPolicyRequestFaultType)
Namespace.addCategoryObject('elementBinding', UnrecognizedPolicyRequestFault.name().localName(), UnrecognizedPolicyRequestFault)

UnacceptableInitialTerminationTimeFault = pyxb.binding.basis.element(pyxb.namespace.ExpandedName(Namespace, u'UnacceptableInitialTerminationTimeFault'), UnacceptableInitialTerminationTimeFaultType)
Namespace.addCategoryObject('elementBinding', UnacceptableInitialTerminationTimeFault.name().localName(), UnacceptableInitialTerminationTimeFault)

GetMessages = pyxb.binding.basis.element(pyxb.namespace.ExpandedName(Namespace, u'GetMessages'), CTD_ANON_11)
Namespace.addCategoryObject('elementBinding', GetMessages.name().localName(), GetMessages)

UnacceptableTerminationTimeFault = pyxb.binding.basis.element(pyxb.namespace.ExpandedName(Namespace, u'UnacceptableTerminationTimeFault'), UnacceptableTerminationTimeFaultType)
Namespace.addCategoryObject('elementBinding', UnacceptableTerminationTimeFault.name().localName(), UnacceptableTerminationTimeFault)

TopicExpression = pyxb.binding.basis.element(pyxb.namespace.ExpandedName(Namespace, u'TopicExpression'), TopicExpressionType)
Namespace.addCategoryObject('elementBinding', TopicExpression.name().localName(), TopicExpression)

GetMessagesResponse = pyxb.binding.basis.element(pyxb.namespace.ExpandedName(Namespace, u'GetMessagesResponse'), CTD_ANON_12)
Namespace.addCategoryObject('elementBinding', GetMessagesResponse.name().localName(), GetMessagesResponse)

Notify = pyxb.binding.basis.element(pyxb.namespace.ExpandedName(Namespace, u'Notify'), CTD_ANON_13)
Namespace.addCategoryObject('elementBinding', Notify.name().localName(), Notify)

PauseFailedFault = pyxb.binding.basis.element(pyxb.namespace.ExpandedName(Namespace, u'PauseFailedFault'), PauseFailedFaultType)
Namespace.addCategoryObject('elementBinding', PauseFailedFault.name().localName(), PauseFailedFault)

UnsubscribeResponse = pyxb.binding.basis.element(pyxb.namespace.ExpandedName(Namespace, u'UnsubscribeResponse'), CTD_ANON_14)
Namespace.addCategoryObject('elementBinding', UnsubscribeResponse.name().localName(), UnsubscribeResponse)

DestroyPullPoint = pyxb.binding.basis.element(pyxb.namespace.ExpandedName(Namespace, u'DestroyPullPoint'), CTD_ANON_15)
Namespace.addCategoryObject('elementBinding', DestroyPullPoint.name().localName(), DestroyPullPoint)

UnableToDestroySubscriptionFault = pyxb.binding.basis.element(pyxb.namespace.ExpandedName(Namespace, u'UnableToDestroySubscriptionFault'), UnableToDestroySubscriptionFaultType)
Namespace.addCategoryObject('elementBinding', UnableToDestroySubscriptionFault.name().localName(), UnableToDestroySubscriptionFault)

ResumeFailedFault = pyxb.binding.basis.element(pyxb.namespace.ExpandedName(Namespace, u'ResumeFailedFault'), ResumeFailedFaultType)
Namespace.addCategoryObject('elementBinding', ResumeFailedFault.name().localName(), ResumeFailedFault)

PauseSubscriptionResponse = pyxb.binding.basis.element(pyxb.namespace.ExpandedName(Namespace, u'PauseSubscriptionResponse'), CTD_ANON_16)
Namespace.addCategoryObject('elementBinding', PauseSubscriptionResponse.name().localName(), PauseSubscriptionResponse)

UnableToGetMessagesFault = pyxb.binding.basis.element(pyxb.namespace.ExpandedName(Namespace, u'UnableToGetMessagesFault'), UnableToGetMessagesFaultType)
Namespace.addCategoryObject('elementBinding', UnableToGetMessagesFault.name().localName(), UnableToGetMessagesFault)

UnableToDestroyPullPointFault = pyxb.binding.basis.element(pyxb.namespace.ExpandedName(Namespace, u'UnableToDestroyPullPointFault'), UnableToDestroyPullPointFaultType)
Namespace.addCategoryObject('elementBinding', UnableToDestroyPullPointFault.name().localName(), UnableToDestroyPullPointFault)

CreatePullPoint = pyxb.binding.basis.element(pyxb.namespace.ExpandedName(Namespace, u'CreatePullPoint'), CTD_ANON_17)
Namespace.addCategoryObject('elementBinding', CreatePullPoint.name().localName(), CreatePullPoint)

ResumeSubscription = pyxb.binding.basis.element(pyxb.namespace.ExpandedName(Namespace, u'ResumeSubscription'), CTD_ANON_19)
Namespace.addCategoryObject('elementBinding', ResumeSubscription.name().localName(), ResumeSubscription)

Unsubscribe = pyxb.binding.basis.element(pyxb.namespace.ExpandedName(Namespace, u'Unsubscribe'), CTD_ANON_20)
Namespace.addCategoryObject('elementBinding', Unsubscribe.name().localName(), Unsubscribe)

CreatePullPointResponse = pyxb.binding.basis.element(pyxb.namespace.ExpandedName(Namespace, u'CreatePullPointResponse'), CTD_ANON_21)
Namespace.addCategoryObject('elementBinding', CreatePullPointResponse.name().localName(), CreatePullPointResponse)

ResumeSubscriptionResponse = pyxb.binding.basis.element(pyxb.namespace.ExpandedName(Namespace, u'ResumeSubscriptionResponse'), CTD_ANON_22)
Namespace.addCategoryObject('elementBinding', ResumeSubscriptionResponse.name().localName(), ResumeSubscriptionResponse)

UnableToCreatePullPointFault = pyxb.binding.basis.element(pyxb.namespace.ExpandedName(Namespace, u'UnableToCreatePullPointFault'), UnableToCreatePullPointFaultType)
Namespace.addCategoryObject('elementBinding', UnableToCreatePullPointFault.name().localName(), UnableToCreatePullPointFault)

TopicExpressionDialect = pyxb.binding.basis.element(pyxb.namespace.ExpandedName(Namespace, u'TopicExpressionDialect'), pyxb.binding.datatypes.anyURI)
Namespace.addCategoryObject('elementBinding', TopicExpressionDialect.name().localName(), TopicExpressionDialect)

NotificationProducerRP = pyxb.binding.basis.element(pyxb.namespace.ExpandedName(Namespace, u'NotificationProducerRP'), CTD_ANON_23)
Namespace.addCategoryObject('elementBinding', NotificationProducerRP.name().localName(), NotificationProducerRP)


FilterType._GroupModel = pyxb.binding.content.GroupSequence(
    pyxb.binding.content.ParticleModel(pyxb.binding.content.Wildcard(process_contents=pyxb.binding.content.Wildcard.PC_strict, namespace_constraint=pyxb.binding.content.Wildcard.NC_any), min_occurs=0L, max_occurs=None)
    )
FilterType._ContentModel = pyxb.binding.content.ParticleModel(FilterType._GroupModel, min_occurs=1, max_occurs=1)


SubscriptionPolicyType._GroupModel = pyxb.binding.content.GroupSequence(
    pyxb.binding.content.ParticleModel(pyxb.binding.content.Wildcard(process_contents=pyxb.binding.content.Wildcard.PC_lax, namespace_constraint=pyxb.binding.content.Wildcard.NC_any), min_occurs=0L, max_occurs=None)
    )
SubscriptionPolicyType._ContentModel = pyxb.binding.content.ParticleModel(SubscriptionPolicyType._GroupModel, min_occurs=1, max_occurs=1)



CTD_ANON._AddElement(pyxb.binding.basis.element(pyxb.namespace.ExpandedName(Namespace, u'ConsumerReference'), pyxb.bundles.wssplat.wsa.EndpointReferenceType, scope=CTD_ANON))

CTD_ANON._AddElement(pyxb.binding.basis.element(pyxb.namespace.ExpandedName(Namespace, u'CreationTime'), pyxb.binding.datatypes.dateTime, scope=CTD_ANON))

CTD_ANON._AddElement(pyxb.binding.basis.element(pyxb.namespace.ExpandedName(Namespace, u'SubscriptionPolicy'), SubscriptionPolicyType, scope=CTD_ANON))

CTD_ANON._AddElement(pyxb.binding.basis.element(pyxb.namespace.ExpandedName(Namespace, u'Filter'), FilterType, scope=CTD_ANON))
CTD_ANON._GroupModel = pyxb.binding.content.GroupSequence(
    pyxb.binding.content.ParticleModel(CTD_ANON._UseForTag(pyxb.namespace.ExpandedName(Namespace, u'ConsumerReference')), min_occurs=1L, max_occurs=1L),
    pyxb.binding.content.ParticleModel(CTD_ANON._UseForTag(pyxb.namespace.ExpandedName(Namespace, u'Filter')), min_occurs=0L, max_occurs=1L),
    pyxb.binding.content.ParticleModel(CTD_ANON._UseForTag(pyxb.namespace.ExpandedName(Namespace, u'SubscriptionPolicy')), min_occurs=0L, max_occurs=1L),
    pyxb.binding.content.ParticleModel(CTD_ANON._UseForTag(pyxb.namespace.ExpandedName(Namespace, u'CreationTime')), min_occurs=0L, max_occurs=1L)
    )
CTD_ANON._ContentModel = pyxb.binding.content.ParticleModel(CTD_ANON._GroupModel, min_occurs=1, max_occurs=1)


MultipleTopicsSpecifiedFaultType._GroupModel_ = pyxb.binding.content.GroupSequence(
    pyxb.binding.content.ParticleModel(pyxb.binding.content.Wildcard(process_contents=pyxb.binding.content.Wildcard.PC_lax, namespace_constraint=(pyxb.binding.content.Wildcard.NC_not, u'http://docs.oasis-open.org/wsrf/bf-2')), min_occurs=0L, max_occurs=None),
    pyxb.binding.content.ParticleModel(MultipleTopicsSpecifiedFaultType._UseForTag(pyxb.namespace.ExpandedName(pyxb.namespace.NamespaceForURI(u'http://docs.oasis-open.org/wsrf/bf-2'), u'Timestamp')), min_occurs=1L, max_occurs=1L),
    pyxb.binding.content.ParticleModel(MultipleTopicsSpecifiedFaultType._UseForTag(pyxb.namespace.ExpandedName(pyxb.namespace.NamespaceForURI(u'http://docs.oasis-open.org/wsrf/bf-2'), u'Originator')), min_occurs=0L, max_occurs=1L),
    pyxb.binding.content.ParticleModel(MultipleTopicsSpecifiedFaultType._UseForTag(pyxb.namespace.ExpandedName(pyxb.namespace.NamespaceForURI(u'http://docs.oasis-open.org/wsrf/bf-2'), u'ErrorCode')), min_occurs=0L, max_occurs=1L),
    pyxb.binding.content.ParticleModel(MultipleTopicsSpecifiedFaultType._UseForTag(pyxb.namespace.ExpandedName(pyxb.namespace.NamespaceForURI(u'http://docs.oasis-open.org/wsrf/bf-2'), u'Description')), min_occurs=0L, max_occurs=None),
    pyxb.binding.content.ParticleModel(MultipleTopicsSpecifiedFaultType._UseForTag(pyxb.namespace.ExpandedName(pyxb.namespace.NamespaceForURI(u'http://docs.oasis-open.org/wsrf/bf-2'), u'FaultCause')), min_occurs=0L, max_occurs=1L)
    )
MultipleTopicsSpecifiedFaultType._ContentModel = pyxb.binding.content.ParticleModel(MultipleTopicsSpecifiedFaultType._GroupModel_, min_occurs=1, max_occurs=1)


CTD_ANON_._GroupModel = pyxb.binding.content.GroupSequence(
    pyxb.binding.content.ParticleModel(pyxb.binding.content.Wildcard(process_contents=pyxb.binding.content.Wildcard.PC_lax, namespace_constraint=(pyxb.binding.content.Wildcard.NC_not, u'http://docs.oasis-open.org/wsn/b-2')), min_occurs=0L, max_occurs=None)
    )
CTD_ANON_._ContentModel = pyxb.binding.content.ParticleModel(CTD_ANON_._GroupModel, min_occurs=1, max_occurs=1)



CTD_ANON_2._AddElement(pyxb.binding.basis.element(pyxb.namespace.ExpandedName(Namespace, u'Topic'), TopicExpressionType, scope=CTD_ANON_2))
CTD_ANON_2._GroupModel = pyxb.binding.content.GroupSequence(
    pyxb.binding.content.ParticleModel(CTD_ANON_2._UseForTag(pyxb.namespace.ExpandedName(Namespace, u'Topic')), min_occurs=1, max_occurs=1),
    pyxb.binding.content.ParticleModel(pyxb.binding.content.Wildcard(process_contents=pyxb.binding.content.Wildcard.PC_lax, namespace_constraint=(pyxb.binding.content.Wildcard.NC_not, u'http://docs.oasis-open.org/wsn/b-2')), min_occurs=0L, max_occurs=None)
    )
CTD_ANON_2._ContentModel = pyxb.binding.content.ParticleModel(CTD_ANON_2._GroupModel, min_occurs=1, max_occurs=1)


TopicExpressionType._GroupModel = pyxb.binding.content.GroupSequence(
    pyxb.binding.content.ParticleModel(pyxb.binding.content.Wildcard(process_contents=pyxb.binding.content.Wildcard.PC_lax, namespace_constraint=pyxb.binding.content.Wildcard.NC_any), min_occurs=0L, max_occurs=1L)
    )
TopicExpressionType._ContentModel = pyxb.binding.content.ParticleModel(TopicExpressionType._GroupModel, min_occurs=1, max_occurs=1)



NotificationMessageHolderType._AddElement(pyxb.binding.basis.element(pyxb.namespace.ExpandedName(Namespace, u'Topic'), TopicExpressionType, scope=NotificationMessageHolderType))

NotificationMessageHolderType._AddElement(pyxb.binding.basis.element(pyxb.namespace.ExpandedName(Namespace, u'ProducerReference'), pyxb.bundles.wssplat.wsa.EndpointReferenceType, scope=NotificationMessageHolderType))

NotificationMessageHolderType._AddElement(pyxb.binding.basis.element(pyxb.namespace.ExpandedName(Namespace, u'SubscriptionReference'), pyxb.bundles.wssplat.wsa.EndpointReferenceType, scope=NotificationMessageHolderType))

NotificationMessageHolderType._AddElement(pyxb.binding.basis.element(pyxb.namespace.ExpandedName(Namespace, u'Message'), CTD_ANON_3, scope=NotificationMessageHolderType))
NotificationMessageHolderType._GroupModel = pyxb.binding.content.GroupSequence(
    pyxb.binding.content.ParticleModel(NotificationMessageHolderType._UseForTag(pyxb.namespace.ExpandedName(Namespace, u'SubscriptionReference')), min_occurs=0L, max_occurs=1L),
    pyxb.binding.content.ParticleModel(NotificationMessageHolderType._UseForTag(pyxb.namespace.ExpandedName(Namespace, u'Topic')), min_occurs=0L, max_occurs=1L),
    pyxb.binding.content.ParticleModel(NotificationMessageHolderType._UseForTag(pyxb.namespace.ExpandedName(Namespace, u'ProducerReference')), min_occurs=0L, max_occurs=1L),
    pyxb.binding.content.ParticleModel(NotificationMessageHolderType._UseForTag(pyxb.namespace.ExpandedName(Namespace, u'Message')), min_occurs=1, max_occurs=1)
    )
NotificationMessageHolderType._ContentModel = pyxb.binding.content.ParticleModel(NotificationMessageHolderType._GroupModel, min_occurs=1, max_occurs=1)


QueryExpressionType._GroupModel = pyxb.binding.content.GroupSequence(
    pyxb.binding.content.ParticleModel(pyxb.binding.content.Wildcard(process_contents=pyxb.binding.content.Wildcard.PC_lax, namespace_constraint=pyxb.binding.content.Wildcard.NC_any), min_occurs=0L, max_occurs=1L)
    )
QueryExpressionType._ContentModel = pyxb.binding.content.ParticleModel(QueryExpressionType._GroupModel, min_occurs=1, max_occurs=1)


CTD_ANON_3._GroupModel = pyxb.binding.content.GroupSequence(
    pyxb.binding.content.ParticleModel(pyxb.binding.content.Wildcard(process_contents=pyxb.binding.content.Wildcard.PC_lax, namespace_constraint=pyxb.binding.content.Wildcard.NC_any), min_occurs=1L, max_occurs=1L)
    )
CTD_ANON_3._ContentModel = pyxb.binding.content.ParticleModel(CTD_ANON_3._GroupModel, min_occurs=1, max_occurs=1)


SubscribeCreationFailedFaultType._GroupModel_ = pyxb.binding.content.GroupSequence(
    pyxb.binding.content.ParticleModel(pyxb.binding.content.Wildcard(process_contents=pyxb.binding.content.Wildcard.PC_lax, namespace_constraint=(pyxb.binding.content.Wildcard.NC_not, u'http://docs.oasis-open.org/wsrf/bf-2')), min_occurs=0L, max_occurs=None),
    pyxb.binding.content.ParticleModel(SubscribeCreationFailedFaultType._UseForTag(pyxb.namespace.ExpandedName(pyxb.namespace.NamespaceForURI(u'http://docs.oasis-open.org/wsrf/bf-2'), u'Timestamp')), min_occurs=1L, max_occurs=1L),
    pyxb.binding.content.ParticleModel(SubscribeCreationFailedFaultType._UseForTag(pyxb.namespace.ExpandedName(pyxb.namespace.NamespaceForURI(u'http://docs.oasis-open.org/wsrf/bf-2'), u'Originator')), min_occurs=0L, max_occurs=1L),
    pyxb.binding.content.ParticleModel(SubscribeCreationFailedFaultType._UseForTag(pyxb.namespace.ExpandedName(pyxb.namespace.NamespaceForURI(u'http://docs.oasis-open.org/wsrf/bf-2'), u'ErrorCode')), min_occurs=0L, max_occurs=1L),
    pyxb.binding.content.ParticleModel(SubscribeCreationFailedFaultType._UseForTag(pyxb.namespace.ExpandedName(pyxb.namespace.NamespaceForURI(u'http://docs.oasis-open.org/wsrf/bf-2'), u'Description')), min_occurs=0L, max_occurs=None),
    pyxb.binding.content.ParticleModel(SubscribeCreationFailedFaultType._UseForTag(pyxb.namespace.ExpandedName(pyxb.namespace.NamespaceForURI(u'http://docs.oasis-open.org/wsrf/bf-2'), u'FaultCause')), min_occurs=0L, max_occurs=1L)
    )
SubscribeCreationFailedFaultType._ContentModel = pyxb.binding.content.ParticleModel(SubscribeCreationFailedFaultType._GroupModel_, min_occurs=1, max_occurs=1)



CTD_ANON_4._AddElement(pyxb.binding.basis.element(pyxb.namespace.ExpandedName(Namespace, u'SubscriptionReference'), pyxb.bundles.wssplat.wsa.EndpointReferenceType, scope=CTD_ANON_4))

CTD_ANON_4._AddElement(pyxb.binding.basis.element(pyxb.namespace.ExpandedName(Namespace, u'TerminationTime'), pyxb.binding.datatypes.dateTime, nillable=pyxb.binding.datatypes.boolean(1), scope=CTD_ANON_4))

CTD_ANON_4._AddElement(pyxb.binding.basis.element(pyxb.namespace.ExpandedName(Namespace, u'CurrentTime'), pyxb.binding.datatypes.dateTime, scope=CTD_ANON_4))
CTD_ANON_4._GroupModel = pyxb.binding.content.GroupSequence(
    pyxb.binding.content.ParticleModel(CTD_ANON_4._UseForTag(pyxb.namespace.ExpandedName(Namespace, u'SubscriptionReference')), min_occurs=1L, max_occurs=1L),
    pyxb.binding.content.ParticleModel(CTD_ANON_4._UseForTag(pyxb.namespace.ExpandedName(Namespace, u'CurrentTime')), min_occurs=0L, max_occurs=1L),
    pyxb.binding.content.ParticleModel(CTD_ANON_4._UseForTag(pyxb.namespace.ExpandedName(Namespace, u'TerminationTime')), min_occurs=0L, max_occurs=1L),
    pyxb.binding.content.ParticleModel(pyxb.binding.content.Wildcard(process_contents=pyxb.binding.content.Wildcard.PC_lax, namespace_constraint=(pyxb.binding.content.Wildcard.NC_not, u'http://docs.oasis-open.org/wsn/b-2')), min_occurs=0L, max_occurs=None)
    )
CTD_ANON_4._ContentModel = pyxb.binding.content.ParticleModel(CTD_ANON_4._GroupModel, min_occurs=1, max_occurs=1)



InvalidFilterFaultType._AddElement(pyxb.binding.basis.element(pyxb.namespace.ExpandedName(Namespace, u'UnknownFilter'), pyxb.binding.datatypes.QName, scope=InvalidFilterFaultType))
InvalidFilterFaultType._GroupModel_2 = pyxb.binding.content.GroupSequence(
    pyxb.binding.content.ParticleModel(pyxb.binding.content.Wildcard(process_contents=pyxb.binding.content.Wildcard.PC_lax, namespace_constraint=(pyxb.binding.content.Wildcard.NC_not, u'http://docs.oasis-open.org/wsrf/bf-2')), min_occurs=0L, max_occurs=None),
    pyxb.binding.content.ParticleModel(InvalidFilterFaultType._UseForTag(pyxb.namespace.ExpandedName(pyxb.namespace.NamespaceForURI(u'http://docs.oasis-open.org/wsrf/bf-2'), u'Timestamp')), min_occurs=1L, max_occurs=1L),
    pyxb.binding.content.ParticleModel(InvalidFilterFaultType._UseForTag(pyxb.namespace.ExpandedName(pyxb.namespace.NamespaceForURI(u'http://docs.oasis-open.org/wsrf/bf-2'), u'Originator')), min_occurs=0L, max_occurs=1L),
    pyxb.binding.content.ParticleModel(InvalidFilterFaultType._UseForTag(pyxb.namespace.ExpandedName(pyxb.namespace.NamespaceForURI(u'http://docs.oasis-open.org/wsrf/bf-2'), u'ErrorCode')), min_occurs=0L, max_occurs=1L),
    pyxb.binding.content.ParticleModel(InvalidFilterFaultType._UseForTag(pyxb.namespace.ExpandedName(pyxb.namespace.NamespaceForURI(u'http://docs.oasis-open.org/wsrf/bf-2'), u'Description')), min_occurs=0L, max_occurs=None),
    pyxb.binding.content.ParticleModel(InvalidFilterFaultType._UseForTag(pyxb.namespace.ExpandedName(pyxb.namespace.NamespaceForURI(u'http://docs.oasis-open.org/wsrf/bf-2'), u'FaultCause')), min_occurs=0L, max_occurs=1L)
    )
InvalidFilterFaultType._GroupModel_3 = pyxb.binding.content.GroupSequence(
    pyxb.binding.content.ParticleModel(InvalidFilterFaultType._UseForTag(pyxb.namespace.ExpandedName(Namespace, u'UnknownFilter')), min_occurs=1L, max_occurs=None)
    )
InvalidFilterFaultType._GroupModel_ = pyxb.binding.content.GroupSequence(
    pyxb.binding.content.ParticleModel(InvalidFilterFaultType._GroupModel_2, min_occurs=1, max_occurs=1),
    pyxb.binding.content.ParticleModel(InvalidFilterFaultType._GroupModel_3, min_occurs=1, max_occurs=1)
    )
InvalidFilterFaultType._ContentModel = pyxb.binding.content.ParticleModel(InvalidFilterFaultType._GroupModel_, min_occurs=1, max_occurs=1)


TopicExpressionDialectUnknownFaultType._GroupModel_ = pyxb.binding.content.GroupSequence(
    pyxb.binding.content.ParticleModel(pyxb.binding.content.Wildcard(process_contents=pyxb.binding.content.Wildcard.PC_lax, namespace_constraint=(pyxb.binding.content.Wildcard.NC_not, u'http://docs.oasis-open.org/wsrf/bf-2')), min_occurs=0L, max_occurs=None),
    pyxb.binding.content.ParticleModel(TopicExpressionDialectUnknownFaultType._UseForTag(pyxb.namespace.ExpandedName(pyxb.namespace.NamespaceForURI(u'http://docs.oasis-open.org/wsrf/bf-2'), u'Timestamp')), min_occurs=1L, max_occurs=1L),
    pyxb.binding.content.ParticleModel(TopicExpressionDialectUnknownFaultType._UseForTag(pyxb.namespace.ExpandedName(pyxb.namespace.NamespaceForURI(u'http://docs.oasis-open.org/wsrf/bf-2'), u'Originator')), min_occurs=0L, max_occurs=1L),
    pyxb.binding.content.ParticleModel(TopicExpressionDialectUnknownFaultType._UseForTag(pyxb.namespace.ExpandedName(pyxb.namespace.NamespaceForURI(u'http://docs.oasis-open.org/wsrf/bf-2'), u'ErrorCode')), min_occurs=0L, max_occurs=1L),
    pyxb.binding.content.ParticleModel(TopicExpressionDialectUnknownFaultType._UseForTag(pyxb.namespace.ExpandedName(pyxb.namespace.NamespaceForURI(u'http://docs.oasis-open.org/wsrf/bf-2'), u'Description')), min_occurs=0L, max_occurs=None),
    pyxb.binding.content.ParticleModel(TopicExpressionDialectUnknownFaultType._UseForTag(pyxb.namespace.ExpandedName(pyxb.namespace.NamespaceForURI(u'http://docs.oasis-open.org/wsrf/bf-2'), u'FaultCause')), min_occurs=0L, max_occurs=1L)
    )
TopicExpressionDialectUnknownFaultType._ContentModel = pyxb.binding.content.ParticleModel(TopicExpressionDialectUnknownFaultType._GroupModel_, min_occurs=1, max_occurs=1)


InvalidTopicExpressionFaultType._GroupModel_ = pyxb.binding.content.GroupSequence(
    pyxb.binding.content.ParticleModel(pyxb.binding.content.Wildcard(process_contents=pyxb.binding.content.Wildcard.PC_lax, namespace_constraint=(pyxb.binding.content.Wildcard.NC_not, u'http://docs.oasis-open.org/wsrf/bf-2')), min_occurs=0L, max_occurs=None),
    pyxb.binding.content.ParticleModel(InvalidTopicExpressionFaultType._UseForTag(pyxb.namespace.ExpandedName(pyxb.namespace.NamespaceForURI(u'http://docs.oasis-open.org/wsrf/bf-2'), u'Timestamp')), min_occurs=1L, max_occurs=1L),
    pyxb.binding.content.ParticleModel(InvalidTopicExpressionFaultType._UseForTag(pyxb.namespace.ExpandedName(pyxb.namespace.NamespaceForURI(u'http://docs.oasis-open.org/wsrf/bf-2'), u'Originator')), min_occurs=0L, max_occurs=1L),
    pyxb.binding.content.ParticleModel(InvalidTopicExpressionFaultType._UseForTag(pyxb.namespace.ExpandedName(pyxb.namespace.NamespaceForURI(u'http://docs.oasis-open.org/wsrf/bf-2'), u'ErrorCode')), min_occurs=0L, max_occurs=1L),
    pyxb.binding.content.ParticleModel(InvalidTopicExpressionFaultType._UseForTag(pyxb.namespace.ExpandedName(pyxb.namespace.NamespaceForURI(u'http://docs.oasis-open.org/wsrf/bf-2'), u'Description')), min_occurs=0L, max_occurs=None),
    pyxb.binding.content.ParticleModel(InvalidTopicExpressionFaultType._UseForTag(pyxb.namespace.ExpandedName(pyxb.namespace.NamespaceForURI(u'http://docs.oasis-open.org/wsrf/bf-2'), u'FaultCause')), min_occurs=0L, max_occurs=1L)
    )
InvalidTopicExpressionFaultType._ContentModel = pyxb.binding.content.ParticleModel(InvalidTopicExpressionFaultType._GroupModel_, min_occurs=1, max_occurs=1)


TopicNotSupportedFaultType._GroupModel_ = pyxb.binding.content.GroupSequence(
    pyxb.binding.content.ParticleModel(pyxb.binding.content.Wildcard(process_contents=pyxb.binding.content.Wildcard.PC_lax, namespace_constraint=(pyxb.binding.content.Wildcard.NC_not, u'http://docs.oasis-open.org/wsrf/bf-2')), min_occurs=0L, max_occurs=None),
    pyxb.binding.content.ParticleModel(TopicNotSupportedFaultType._UseForTag(pyxb.namespace.ExpandedName(pyxb.namespace.NamespaceForURI(u'http://docs.oasis-open.org/wsrf/bf-2'), u'Timestamp')), min_occurs=1L, max_occurs=1L),
    pyxb.binding.content.ParticleModel(TopicNotSupportedFaultType._UseForTag(pyxb.namespace.ExpandedName(pyxb.namespace.NamespaceForURI(u'http://docs.oasis-open.org/wsrf/bf-2'), u'Originator')), min_occurs=0L, max_occurs=1L),
    pyxb.binding.content.ParticleModel(TopicNotSupportedFaultType._UseForTag(pyxb.namespace.ExpandedName(pyxb.namespace.NamespaceForURI(u'http://docs.oasis-open.org/wsrf/bf-2'), u'ErrorCode')), min_occurs=0L, max_occurs=1L),
    pyxb.binding.content.ParticleModel(TopicNotSupportedFaultType._UseForTag(pyxb.namespace.ExpandedName(pyxb.namespace.NamespaceForURI(u'http://docs.oasis-open.org/wsrf/bf-2'), u'Description')), min_occurs=0L, max_occurs=None),
    pyxb.binding.content.ParticleModel(TopicNotSupportedFaultType._UseForTag(pyxb.namespace.ExpandedName(pyxb.namespace.NamespaceForURI(u'http://docs.oasis-open.org/wsrf/bf-2'), u'FaultCause')), min_occurs=0L, max_occurs=1L)
    )
TopicNotSupportedFaultType._ContentModel = pyxb.binding.content.ParticleModel(TopicNotSupportedFaultType._GroupModel_, min_occurs=1, max_occurs=1)


InvalidProducerPropertiesExpressionFaultType._GroupModel_ = pyxb.binding.content.GroupSequence(
    pyxb.binding.content.ParticleModel(pyxb.binding.content.Wildcard(process_contents=pyxb.binding.content.Wildcard.PC_lax, namespace_constraint=(pyxb.binding.content.Wildcard.NC_not, u'http://docs.oasis-open.org/wsrf/bf-2')), min_occurs=0L, max_occurs=None),
    pyxb.binding.content.ParticleModel(InvalidProducerPropertiesExpressionFaultType._UseForTag(pyxb.namespace.ExpandedName(pyxb.namespace.NamespaceForURI(u'http://docs.oasis-open.org/wsrf/bf-2'), u'Timestamp')), min_occurs=1L, max_occurs=1L),
    pyxb.binding.content.ParticleModel(InvalidProducerPropertiesExpressionFaultType._UseForTag(pyxb.namespace.ExpandedName(pyxb.namespace.NamespaceForURI(u'http://docs.oasis-open.org/wsrf/bf-2'), u'Originator')), min_occurs=0L, max_occurs=1L),
    pyxb.binding.content.ParticleModel(InvalidProducerPropertiesExpressionFaultType._UseForTag(pyxb.namespace.ExpandedName(pyxb.namespace.NamespaceForURI(u'http://docs.oasis-open.org/wsrf/bf-2'), u'ErrorCode')), min_occurs=0L, max_occurs=1L),
    pyxb.binding.content.ParticleModel(InvalidProducerPropertiesExpressionFaultType._UseForTag(pyxb.namespace.ExpandedName(pyxb.namespace.NamespaceForURI(u'http://docs.oasis-open.org/wsrf/bf-2'), u'Description')), min_occurs=0L, max_occurs=None),
    pyxb.binding.content.ParticleModel(InvalidProducerPropertiesExpressionFaultType._UseForTag(pyxb.namespace.ExpandedName(pyxb.namespace.NamespaceForURI(u'http://docs.oasis-open.org/wsrf/bf-2'), u'FaultCause')), min_occurs=0L, max_occurs=1L)
    )
InvalidProducerPropertiesExpressionFaultType._ContentModel = pyxb.binding.content.ParticleModel(InvalidProducerPropertiesExpressionFaultType._GroupModel_, min_occurs=1, max_occurs=1)


InvalidMessageContentExpressionFaultType._GroupModel_ = pyxb.binding.content.GroupSequence(
    pyxb.binding.content.ParticleModel(pyxb.binding.content.Wildcard(process_contents=pyxb.binding.content.Wildcard.PC_lax, namespace_constraint=(pyxb.binding.content.Wildcard.NC_not, u'http://docs.oasis-open.org/wsrf/bf-2')), min_occurs=0L, max_occurs=None),
    pyxb.binding.content.ParticleModel(InvalidMessageContentExpressionFaultType._UseForTag(pyxb.namespace.ExpandedName(pyxb.namespace.NamespaceForURI(u'http://docs.oasis-open.org/wsrf/bf-2'), u'Timestamp')), min_occurs=1L, max_occurs=1L),
    pyxb.binding.content.ParticleModel(InvalidMessageContentExpressionFaultType._UseForTag(pyxb.namespace.ExpandedName(pyxb.namespace.NamespaceForURI(u'http://docs.oasis-open.org/wsrf/bf-2'), u'Originator')), min_occurs=0L, max_occurs=1L),
    pyxb.binding.content.ParticleModel(InvalidMessageContentExpressionFaultType._UseForTag(pyxb.namespace.ExpandedName(pyxb.namespace.NamespaceForURI(u'http://docs.oasis-open.org/wsrf/bf-2'), u'ErrorCode')), min_occurs=0L, max_occurs=1L),
    pyxb.binding.content.ParticleModel(InvalidMessageContentExpressionFaultType._UseForTag(pyxb.namespace.ExpandedName(pyxb.namespace.NamespaceForURI(u'http://docs.oasis-open.org/wsrf/bf-2'), u'Description')), min_occurs=0L, max_occurs=None),
    pyxb.binding.content.ParticleModel(InvalidMessageContentExpressionFaultType._UseForTag(pyxb.namespace.ExpandedName(pyxb.namespace.NamespaceForURI(u'http://docs.oasis-open.org/wsrf/bf-2'), u'FaultCause')), min_occurs=0L, max_occurs=1L)
    )
InvalidMessageContentExpressionFaultType._ContentModel = pyxb.binding.content.ParticleModel(InvalidMessageContentExpressionFaultType._GroupModel_, min_occurs=1, max_occurs=1)



CTD_ANON_6._AddElement(pyxb.binding.basis.element(pyxb.namespace.ExpandedName(Namespace, u'ConsumerReference'), pyxb.bundles.wssplat.wsa.EndpointReferenceType, scope=CTD_ANON_6))

CTD_ANON_6._AddElement(pyxb.binding.basis.element(pyxb.namespace.ExpandedName(Namespace, u'InitialTerminationTime'), AbsoluteOrRelativeTimeType, nillable=pyxb.binding.datatypes.boolean(1), scope=CTD_ANON_6))

CTD_ANON_6._AddElement(pyxb.binding.basis.element(pyxb.namespace.ExpandedName(Namespace, u'Filter'), FilterType, scope=CTD_ANON_6))

CTD_ANON_6._AddElement(pyxb.binding.basis.element(pyxb.namespace.ExpandedName(Namespace, u'SubscriptionPolicy'), CTD_ANON_18, scope=CTD_ANON_6))
CTD_ANON_6._GroupModel = pyxb.binding.content.GroupSequence(
    pyxb.binding.content.ParticleModel(CTD_ANON_6._UseForTag(pyxb.namespace.ExpandedName(Namespace, u'ConsumerReference')), min_occurs=1L, max_occurs=1L),
    pyxb.binding.content.ParticleModel(CTD_ANON_6._UseForTag(pyxb.namespace.ExpandedName(Namespace, u'Filter')), min_occurs=0L, max_occurs=1L),
    pyxb.binding.content.ParticleModel(CTD_ANON_6._UseForTag(pyxb.namespace.ExpandedName(Namespace, u'InitialTerminationTime')), min_occurs=0L, max_occurs=1L),
    pyxb.binding.content.ParticleModel(CTD_ANON_6._UseForTag(pyxb.namespace.ExpandedName(Namespace, u'SubscriptionPolicy')), min_occurs=0L, max_occurs=1L),
    pyxb.binding.content.ParticleModel(pyxb.binding.content.Wildcard(process_contents=pyxb.binding.content.Wildcard.PC_lax, namespace_constraint=(pyxb.binding.content.Wildcard.NC_not, u'http://docs.oasis-open.org/wsn/b-2')), min_occurs=0L, max_occurs=None)
    )
CTD_ANON_6._ContentModel = pyxb.binding.content.ParticleModel(CTD_ANON_6._GroupModel, min_occurs=1, max_occurs=1)


NoCurrentMessageOnTopicFaultType._GroupModel_ = pyxb.binding.content.GroupSequence(
    pyxb.binding.content.ParticleModel(pyxb.binding.content.Wildcard(process_contents=pyxb.binding.content.Wildcard.PC_lax, namespace_constraint=(pyxb.binding.content.Wildcard.NC_not, u'http://docs.oasis-open.org/wsrf/bf-2')), min_occurs=0L, max_occurs=None),
    pyxb.binding.content.ParticleModel(NoCurrentMessageOnTopicFaultType._UseForTag(pyxb.namespace.ExpandedName(pyxb.namespace.NamespaceForURI(u'http://docs.oasis-open.org/wsrf/bf-2'), u'Timestamp')), min_occurs=1L, max_occurs=1L),
    pyxb.binding.content.ParticleModel(NoCurrentMessageOnTopicFaultType._UseForTag(pyxb.namespace.ExpandedName(pyxb.namespace.NamespaceForURI(u'http://docs.oasis-open.org/wsrf/bf-2'), u'Originator')), min_occurs=0L, max_occurs=1L),
    pyxb.binding.content.ParticleModel(NoCurrentMessageOnTopicFaultType._UseForTag(pyxb.namespace.ExpandedName(pyxb.namespace.NamespaceForURI(u'http://docs.oasis-open.org/wsrf/bf-2'), u'ErrorCode')), min_occurs=0L, max_occurs=1L),
    pyxb.binding.content.ParticleModel(NoCurrentMessageOnTopicFaultType._UseForTag(pyxb.namespace.ExpandedName(pyxb.namespace.NamespaceForURI(u'http://docs.oasis-open.org/wsrf/bf-2'), u'Description')), min_occurs=0L, max_occurs=None),
    pyxb.binding.content.ParticleModel(NoCurrentMessageOnTopicFaultType._UseForTag(pyxb.namespace.ExpandedName(pyxb.namespace.NamespaceForURI(u'http://docs.oasis-open.org/wsrf/bf-2'), u'FaultCause')), min_occurs=0L, max_occurs=1L)
    )
NoCurrentMessageOnTopicFaultType._ContentModel = pyxb.binding.content.ParticleModel(NoCurrentMessageOnTopicFaultType._GroupModel_, min_occurs=1, max_occurs=1)


CTD_ANON_7._GroupModel = pyxb.binding.content.GroupSequence(
    pyxb.binding.content.ParticleModel(pyxb.binding.content.Wildcard(process_contents=pyxb.binding.content.Wildcard.PC_lax, namespace_constraint=(pyxb.binding.content.Wildcard.NC_not, u'http://docs.oasis-open.org/wsn/b-2')), min_occurs=0L, max_occurs=None)
    )
CTD_ANON_7._ContentModel = pyxb.binding.content.ParticleModel(CTD_ANON_7._GroupModel, min_occurs=1, max_occurs=1)



UnsupportedPolicyRequestFaultType._AddElement(pyxb.binding.basis.element(pyxb.namespace.ExpandedName(Namespace, u'UnsupportedPolicy'), pyxb.binding.datatypes.QName, scope=UnsupportedPolicyRequestFaultType))
UnsupportedPolicyRequestFaultType._GroupModel_2 = pyxb.binding.content.GroupSequence(
    pyxb.binding.content.ParticleModel(pyxb.binding.content.Wildcard(process_contents=pyxb.binding.content.Wildcard.PC_lax, namespace_constraint=(pyxb.binding.content.Wildcard.NC_not, u'http://docs.oasis-open.org/wsrf/bf-2')), min_occurs=0L, max_occurs=None),
    pyxb.binding.content.ParticleModel(UnsupportedPolicyRequestFaultType._UseForTag(pyxb.namespace.ExpandedName(pyxb.namespace.NamespaceForURI(u'http://docs.oasis-open.org/wsrf/bf-2'), u'Timestamp')), min_occurs=1L, max_occurs=1L),
    pyxb.binding.content.ParticleModel(UnsupportedPolicyRequestFaultType._UseForTag(pyxb.namespace.ExpandedName(pyxb.namespace.NamespaceForURI(u'http://docs.oasis-open.org/wsrf/bf-2'), u'Originator')), min_occurs=0L, max_occurs=1L),
    pyxb.binding.content.ParticleModel(UnsupportedPolicyRequestFaultType._UseForTag(pyxb.namespace.ExpandedName(pyxb.namespace.NamespaceForURI(u'http://docs.oasis-open.org/wsrf/bf-2'), u'ErrorCode')), min_occurs=0L, max_occurs=1L),
    pyxb.binding.content.ParticleModel(UnsupportedPolicyRequestFaultType._UseForTag(pyxb.namespace.ExpandedName(pyxb.namespace.NamespaceForURI(u'http://docs.oasis-open.org/wsrf/bf-2'), u'Description')), min_occurs=0L, max_occurs=None),
    pyxb.binding.content.ParticleModel(UnsupportedPolicyRequestFaultType._UseForTag(pyxb.namespace.ExpandedName(pyxb.namespace.NamespaceForURI(u'http://docs.oasis-open.org/wsrf/bf-2'), u'FaultCause')), min_occurs=0L, max_occurs=1L)
    )
UnsupportedPolicyRequestFaultType._GroupModel_3 = pyxb.binding.content.GroupSequence(
    pyxb.binding.content.ParticleModel(UnsupportedPolicyRequestFaultType._UseForTag(pyxb.namespace.ExpandedName(Namespace, u'UnsupportedPolicy')), min_occurs=0L, max_occurs=None)
    )
UnsupportedPolicyRequestFaultType._GroupModel_ = pyxb.binding.content.GroupSequence(
    pyxb.binding.content.ParticleModel(UnsupportedPolicyRequestFaultType._GroupModel_2, min_occurs=1, max_occurs=1),
    pyxb.binding.content.ParticleModel(UnsupportedPolicyRequestFaultType._GroupModel_3, min_occurs=1, max_occurs=1)
    )
UnsupportedPolicyRequestFaultType._ContentModel = pyxb.binding.content.ParticleModel(UnsupportedPolicyRequestFaultType._GroupModel_, min_occurs=1, max_occurs=1)


NotifyMessageNotSupportedFaultType._GroupModel_ = pyxb.binding.content.GroupSequence(
    pyxb.binding.content.ParticleModel(pyxb.binding.content.Wildcard(process_contents=pyxb.binding.content.Wildcard.PC_lax, namespace_constraint=(pyxb.binding.content.Wildcard.NC_not, u'http://docs.oasis-open.org/wsrf/bf-2')), min_occurs=0L, max_occurs=None),
    pyxb.binding.content.ParticleModel(NotifyMessageNotSupportedFaultType._UseForTag(pyxb.namespace.ExpandedName(pyxb.namespace.NamespaceForURI(u'http://docs.oasis-open.org/wsrf/bf-2'), u'Timestamp')), min_occurs=1L, max_occurs=1L),
    pyxb.binding.content.ParticleModel(NotifyMessageNotSupportedFaultType._UseForTag(pyxb.namespace.ExpandedName(pyxb.namespace.NamespaceForURI(u'http://docs.oasis-open.org/wsrf/bf-2'), u'Originator')), min_occurs=0L, max_occurs=1L),
    pyxb.binding.content.ParticleModel(NotifyMessageNotSupportedFaultType._UseForTag(pyxb.namespace.ExpandedName(pyxb.namespace.NamespaceForURI(u'http://docs.oasis-open.org/wsrf/bf-2'), u'ErrorCode')), min_occurs=0L, max_occurs=1L),
    pyxb.binding.content.ParticleModel(NotifyMessageNotSupportedFaultType._UseForTag(pyxb.namespace.ExpandedName(pyxb.namespace.NamespaceForURI(u'http://docs.oasis-open.org/wsrf/bf-2'), u'Description')), min_occurs=0L, max_occurs=None),
    pyxb.binding.content.ParticleModel(NotifyMessageNotSupportedFaultType._UseForTag(pyxb.namespace.ExpandedName(pyxb.namespace.NamespaceForURI(u'http://docs.oasis-open.org/wsrf/bf-2'), u'FaultCause')), min_occurs=0L, max_occurs=1L)
    )
NotifyMessageNotSupportedFaultType._ContentModel = pyxb.binding.content.ParticleModel(NotifyMessageNotSupportedFaultType._GroupModel_, min_occurs=1, max_occurs=1)



CTD_ANON_8._AddElement(pyxb.binding.basis.element(pyxb.namespace.ExpandedName(Namespace, u'TerminationTime'), AbsoluteOrRelativeTimeType, nillable=pyxb.binding.datatypes.boolean(1), scope=CTD_ANON_8))
CTD_ANON_8._GroupModel = pyxb.binding.content.GroupSequence(
    pyxb.binding.content.ParticleModel(CTD_ANON_8._UseForTag(pyxb.namespace.ExpandedName(Namespace, u'TerminationTime')), min_occurs=1L, max_occurs=1L),
    pyxb.binding.content.ParticleModel(pyxb.binding.content.Wildcard(process_contents=pyxb.binding.content.Wildcard.PC_lax, namespace_constraint=(pyxb.binding.content.Wildcard.NC_not, u'http://docs.oasis-open.org/wsn/b-2')), min_occurs=0L, max_occurs=None)
    )
CTD_ANON_8._ContentModel = pyxb.binding.content.ParticleModel(CTD_ANON_8._GroupModel, min_occurs=1, max_occurs=1)


CTD_ANON_9._GroupModel = pyxb.binding.content.GroupSequence(
    pyxb.binding.content.ParticleModel(pyxb.binding.content.Wildcard(process_contents=pyxb.binding.content.Wildcard.PC_lax, namespace_constraint=(pyxb.binding.content.Wildcard.NC_not, u'http://docs.oasis-open.org/wsn/b-2')), min_occurs=0L, max_occurs=None)
    )
CTD_ANON_9._ContentModel = pyxb.binding.content.ParticleModel(CTD_ANON_9._GroupModel, min_occurs=1, max_occurs=1)



CTD_ANON_10._AddElement(pyxb.binding.basis.element(pyxb.namespace.ExpandedName(Namespace, u'TerminationTime'), pyxb.binding.datatypes.dateTime, nillable=pyxb.binding.datatypes.boolean(1), scope=CTD_ANON_10))

CTD_ANON_10._AddElement(pyxb.binding.basis.element(pyxb.namespace.ExpandedName(Namespace, u'CurrentTime'), pyxb.binding.datatypes.dateTime, scope=CTD_ANON_10))
CTD_ANON_10._GroupModel = pyxb.binding.content.GroupSequence(
    pyxb.binding.content.ParticleModel(CTD_ANON_10._UseForTag(pyxb.namespace.ExpandedName(Namespace, u'TerminationTime')), min_occurs=1L, max_occurs=1L),
    pyxb.binding.content.ParticleModel(CTD_ANON_10._UseForTag(pyxb.namespace.ExpandedName(Namespace, u'CurrentTime')), min_occurs=0L, max_occurs=1L),
    pyxb.binding.content.ParticleModel(pyxb.binding.content.Wildcard(process_contents=pyxb.binding.content.Wildcard.PC_lax, namespace_constraint=(pyxb.binding.content.Wildcard.NC_not, u'http://docs.oasis-open.org/wsn/b-2')), min_occurs=0L, max_occurs=None)
    )
CTD_ANON_10._ContentModel = pyxb.binding.content.ParticleModel(CTD_ANON_10._GroupModel, min_occurs=1, max_occurs=1)



UnrecognizedPolicyRequestFaultType._AddElement(pyxb.binding.basis.element(pyxb.namespace.ExpandedName(Namespace, u'UnrecognizedPolicy'), pyxb.binding.datatypes.QName, scope=UnrecognizedPolicyRequestFaultType))
UnrecognizedPolicyRequestFaultType._GroupModel_2 = pyxb.binding.content.GroupSequence(
    pyxb.binding.content.ParticleModel(pyxb.binding.content.Wildcard(process_contents=pyxb.binding.content.Wildcard.PC_lax, namespace_constraint=(pyxb.binding.content.Wildcard.NC_not, u'http://docs.oasis-open.org/wsrf/bf-2')), min_occurs=0L, max_occurs=None),
    pyxb.binding.content.ParticleModel(UnrecognizedPolicyRequestFaultType._UseForTag(pyxb.namespace.ExpandedName(pyxb.namespace.NamespaceForURI(u'http://docs.oasis-open.org/wsrf/bf-2'), u'Timestamp')), min_occurs=1L, max_occurs=1L),
    pyxb.binding.content.ParticleModel(UnrecognizedPolicyRequestFaultType._UseForTag(pyxb.namespace.ExpandedName(pyxb.namespace.NamespaceForURI(u'http://docs.oasis-open.org/wsrf/bf-2'), u'Originator')), min_occurs=0L, max_occurs=1L),
    pyxb.binding.content.ParticleModel(UnrecognizedPolicyRequestFaultType._UseForTag(pyxb.namespace.ExpandedName(pyxb.namespace.NamespaceForURI(u'http://docs.oasis-open.org/wsrf/bf-2'), u'ErrorCode')), min_occurs=0L, max_occurs=1L),
    pyxb.binding.content.ParticleModel(UnrecognizedPolicyRequestFaultType._UseForTag(pyxb.namespace.ExpandedName(pyxb.namespace.NamespaceForURI(u'http://docs.oasis-open.org/wsrf/bf-2'), u'Description')), min_occurs=0L, max_occurs=None),
    pyxb.binding.content.ParticleModel(UnrecognizedPolicyRequestFaultType._UseForTag(pyxb.namespace.ExpandedName(pyxb.namespace.NamespaceForURI(u'http://docs.oasis-open.org/wsrf/bf-2'), u'FaultCause')), min_occurs=0L, max_occurs=1L)
    )
UnrecognizedPolicyRequestFaultType._GroupModel_3 = pyxb.binding.content.GroupSequence(
    pyxb.binding.content.ParticleModel(UnrecognizedPolicyRequestFaultType._UseForTag(pyxb.namespace.ExpandedName(Namespace, u'UnrecognizedPolicy')), min_occurs=0L, max_occurs=None)
    )
UnrecognizedPolicyRequestFaultType._GroupModel_ = pyxb.binding.content.GroupSequence(
    pyxb.binding.content.ParticleModel(UnrecognizedPolicyRequestFaultType._GroupModel_2, min_occurs=1, max_occurs=1),
    pyxb.binding.content.ParticleModel(UnrecognizedPolicyRequestFaultType._GroupModel_3, min_occurs=1, max_occurs=1)
    )
UnrecognizedPolicyRequestFaultType._ContentModel = pyxb.binding.content.ParticleModel(UnrecognizedPolicyRequestFaultType._GroupModel_, min_occurs=1, max_occurs=1)



UnacceptableInitialTerminationTimeFaultType._AddElement(pyxb.binding.basis.element(pyxb.namespace.ExpandedName(Namespace, u'MinimumTime'), pyxb.binding.datatypes.dateTime, scope=UnacceptableInitialTerminationTimeFaultType))

UnacceptableInitialTerminationTimeFaultType._AddElement(pyxb.binding.basis.element(pyxb.namespace.ExpandedName(Namespace, u'MaximumTime'), pyxb.binding.datatypes.dateTime, scope=UnacceptableInitialTerminationTimeFaultType))
UnacceptableInitialTerminationTimeFaultType._GroupModel_2 = pyxb.binding.content.GroupSequence(
    pyxb.binding.content.ParticleModel(pyxb.binding.content.Wildcard(process_contents=pyxb.binding.content.Wildcard.PC_lax, namespace_constraint=(pyxb.binding.content.Wildcard.NC_not, u'http://docs.oasis-open.org/wsrf/bf-2')), min_occurs=0L, max_occurs=None),
    pyxb.binding.content.ParticleModel(UnacceptableInitialTerminationTimeFaultType._UseForTag(pyxb.namespace.ExpandedName(pyxb.namespace.NamespaceForURI(u'http://docs.oasis-open.org/wsrf/bf-2'), u'Timestamp')), min_occurs=1L, max_occurs=1L),
    pyxb.binding.content.ParticleModel(UnacceptableInitialTerminationTimeFaultType._UseForTag(pyxb.namespace.ExpandedName(pyxb.namespace.NamespaceForURI(u'http://docs.oasis-open.org/wsrf/bf-2'), u'Originator')), min_occurs=0L, max_occurs=1L),
    pyxb.binding.content.ParticleModel(UnacceptableInitialTerminationTimeFaultType._UseForTag(pyxb.namespace.ExpandedName(pyxb.namespace.NamespaceForURI(u'http://docs.oasis-open.org/wsrf/bf-2'), u'ErrorCode')), min_occurs=0L, max_occurs=1L),
    pyxb.binding.content.ParticleModel(UnacceptableInitialTerminationTimeFaultType._UseForTag(pyxb.namespace.ExpandedName(pyxb.namespace.NamespaceForURI(u'http://docs.oasis-open.org/wsrf/bf-2'), u'Description')), min_occurs=0L, max_occurs=None),
    pyxb.binding.content.ParticleModel(UnacceptableInitialTerminationTimeFaultType._UseForTag(pyxb.namespace.ExpandedName(pyxb.namespace.NamespaceForURI(u'http://docs.oasis-open.org/wsrf/bf-2'), u'FaultCause')), min_occurs=0L, max_occurs=1L)
    )
UnacceptableInitialTerminationTimeFaultType._GroupModel_3 = pyxb.binding.content.GroupSequence(
    pyxb.binding.content.ParticleModel(UnacceptableInitialTerminationTimeFaultType._UseForTag(pyxb.namespace.ExpandedName(Namespace, u'MinimumTime')), min_occurs=1, max_occurs=1),
    pyxb.binding.content.ParticleModel(UnacceptableInitialTerminationTimeFaultType._UseForTag(pyxb.namespace.ExpandedName(Namespace, u'MaximumTime')), min_occurs=0L, max_occurs=1)
    )
UnacceptableInitialTerminationTimeFaultType._GroupModel_ = pyxb.binding.content.GroupSequence(
    pyxb.binding.content.ParticleModel(UnacceptableInitialTerminationTimeFaultType._GroupModel_2, min_occurs=1, max_occurs=1),
    pyxb.binding.content.ParticleModel(UnacceptableInitialTerminationTimeFaultType._GroupModel_3, min_occurs=1, max_occurs=1)
    )
UnacceptableInitialTerminationTimeFaultType._ContentModel = pyxb.binding.content.ParticleModel(UnacceptableInitialTerminationTimeFaultType._GroupModel_, min_occurs=1, max_occurs=1)



CTD_ANON_11._AddElement(pyxb.binding.basis.element(pyxb.namespace.ExpandedName(Namespace, u'MaximumNumber'), pyxb.binding.datatypes.nonNegativeInteger, scope=CTD_ANON_11))
CTD_ANON_11._GroupModel = pyxb.binding.content.GroupSequence(
    pyxb.binding.content.ParticleModel(CTD_ANON_11._UseForTag(pyxb.namespace.ExpandedName(Namespace, u'MaximumNumber')), min_occurs=0L, max_occurs=1),
    pyxb.binding.content.ParticleModel(pyxb.binding.content.Wildcard(process_contents=pyxb.binding.content.Wildcard.PC_lax, namespace_constraint=(pyxb.binding.content.Wildcard.NC_not, u'http://docs.oasis-open.org/wsn/b-2')), min_occurs=0L, max_occurs=None)
    )
CTD_ANON_11._ContentModel = pyxb.binding.content.ParticleModel(CTD_ANON_11._GroupModel, min_occurs=1, max_occurs=1)



UnacceptableTerminationTimeFaultType._AddElement(pyxb.binding.basis.element(pyxb.namespace.ExpandedName(Namespace, u'MaximumTime'), pyxb.binding.datatypes.dateTime, scope=UnacceptableTerminationTimeFaultType))

UnacceptableTerminationTimeFaultType._AddElement(pyxb.binding.basis.element(pyxb.namespace.ExpandedName(Namespace, u'MinimumTime'), pyxb.binding.datatypes.dateTime, scope=UnacceptableTerminationTimeFaultType))
UnacceptableTerminationTimeFaultType._GroupModel_2 = pyxb.binding.content.GroupSequence(
    pyxb.binding.content.ParticleModel(pyxb.binding.content.Wildcard(process_contents=pyxb.binding.content.Wildcard.PC_lax, namespace_constraint=(pyxb.binding.content.Wildcard.NC_not, u'http://docs.oasis-open.org/wsrf/bf-2')), min_occurs=0L, max_occurs=None),
    pyxb.binding.content.ParticleModel(UnacceptableTerminationTimeFaultType._UseForTag(pyxb.namespace.ExpandedName(pyxb.namespace.NamespaceForURI(u'http://docs.oasis-open.org/wsrf/bf-2'), u'Timestamp')), min_occurs=1L, max_occurs=1L),
    pyxb.binding.content.ParticleModel(UnacceptableTerminationTimeFaultType._UseForTag(pyxb.namespace.ExpandedName(pyxb.namespace.NamespaceForURI(u'http://docs.oasis-open.org/wsrf/bf-2'), u'Originator')), min_occurs=0L, max_occurs=1L),
    pyxb.binding.content.ParticleModel(UnacceptableTerminationTimeFaultType._UseForTag(pyxb.namespace.ExpandedName(pyxb.namespace.NamespaceForURI(u'http://docs.oasis-open.org/wsrf/bf-2'), u'ErrorCode')), min_occurs=0L, max_occurs=1L),
    pyxb.binding.content.ParticleModel(UnacceptableTerminationTimeFaultType._UseForTag(pyxb.namespace.ExpandedName(pyxb.namespace.NamespaceForURI(u'http://docs.oasis-open.org/wsrf/bf-2'), u'Description')), min_occurs=0L, max_occurs=None),
    pyxb.binding.content.ParticleModel(UnacceptableTerminationTimeFaultType._UseForTag(pyxb.namespace.ExpandedName(pyxb.namespace.NamespaceForURI(u'http://docs.oasis-open.org/wsrf/bf-2'), u'FaultCause')), min_occurs=0L, max_occurs=1L)
    )
UnacceptableTerminationTimeFaultType._GroupModel_3 = pyxb.binding.content.GroupSequence(
    pyxb.binding.content.ParticleModel(UnacceptableTerminationTimeFaultType._UseForTag(pyxb.namespace.ExpandedName(Namespace, u'MinimumTime')), min_occurs=1, max_occurs=1),
    pyxb.binding.content.ParticleModel(UnacceptableTerminationTimeFaultType._UseForTag(pyxb.namespace.ExpandedName(Namespace, u'MaximumTime')), min_occurs=0L, max_occurs=1)
    )
UnacceptableTerminationTimeFaultType._GroupModel_ = pyxb.binding.content.GroupSequence(
    pyxb.binding.content.ParticleModel(UnacceptableTerminationTimeFaultType._GroupModel_2, min_occurs=1, max_occurs=1),
    pyxb.binding.content.ParticleModel(UnacceptableTerminationTimeFaultType._GroupModel_3, min_occurs=1, max_occurs=1)
    )
UnacceptableTerminationTimeFaultType._ContentModel = pyxb.binding.content.ParticleModel(UnacceptableTerminationTimeFaultType._GroupModel_, min_occurs=1, max_occurs=1)



CTD_ANON_12._AddElement(pyxb.binding.basis.element(pyxb.namespace.ExpandedName(Namespace, u'NotificationMessage'), NotificationMessageHolderType, scope=CTD_ANON_12))
CTD_ANON_12._GroupModel = pyxb.binding.content.GroupSequence(
    pyxb.binding.content.ParticleModel(CTD_ANON_12._UseForTag(pyxb.namespace.ExpandedName(Namespace, u'NotificationMessage')), min_occurs=0L, max_occurs=None),
    pyxb.binding.content.ParticleModel(pyxb.binding.content.Wildcard(process_contents=pyxb.binding.content.Wildcard.PC_lax, namespace_constraint=(pyxb.binding.content.Wildcard.NC_not, u'http://docs.oasis-open.org/wsn/b-2')), min_occurs=0L, max_occurs=None)
    )
CTD_ANON_12._ContentModel = pyxb.binding.content.ParticleModel(CTD_ANON_12._GroupModel, min_occurs=1, max_occurs=1)



CTD_ANON_13._AddElement(pyxb.binding.basis.element(pyxb.namespace.ExpandedName(Namespace, u'NotificationMessage'), NotificationMessageHolderType, scope=CTD_ANON_13))
CTD_ANON_13._GroupModel = pyxb.binding.content.GroupSequence(
    pyxb.binding.content.ParticleModel(CTD_ANON_13._UseForTag(pyxb.namespace.ExpandedName(Namespace, u'NotificationMessage')), min_occurs=1L, max_occurs=None),
    pyxb.binding.content.ParticleModel(pyxb.binding.content.Wildcard(process_contents=pyxb.binding.content.Wildcard.PC_lax, namespace_constraint=(pyxb.binding.content.Wildcard.NC_not, u'http://docs.oasis-open.org/wsn/b-2')), min_occurs=0L, max_occurs=None)
    )
CTD_ANON_13._ContentModel = pyxb.binding.content.ParticleModel(CTD_ANON_13._GroupModel, min_occurs=1, max_occurs=1)


PauseFailedFaultType._GroupModel_ = pyxb.binding.content.GroupSequence(
    pyxb.binding.content.ParticleModel(pyxb.binding.content.Wildcard(process_contents=pyxb.binding.content.Wildcard.PC_lax, namespace_constraint=(pyxb.binding.content.Wildcard.NC_not, u'http://docs.oasis-open.org/wsrf/bf-2')), min_occurs=0L, max_occurs=None),
    pyxb.binding.content.ParticleModel(PauseFailedFaultType._UseForTag(pyxb.namespace.ExpandedName(pyxb.namespace.NamespaceForURI(u'http://docs.oasis-open.org/wsrf/bf-2'), u'Timestamp')), min_occurs=1L, max_occurs=1L),
    pyxb.binding.content.ParticleModel(PauseFailedFaultType._UseForTag(pyxb.namespace.ExpandedName(pyxb.namespace.NamespaceForURI(u'http://docs.oasis-open.org/wsrf/bf-2'), u'Originator')), min_occurs=0L, max_occurs=1L),
    pyxb.binding.content.ParticleModel(PauseFailedFaultType._UseForTag(pyxb.namespace.ExpandedName(pyxb.namespace.NamespaceForURI(u'http://docs.oasis-open.org/wsrf/bf-2'), u'ErrorCode')), min_occurs=0L, max_occurs=1L),
    pyxb.binding.content.ParticleModel(PauseFailedFaultType._UseForTag(pyxb.namespace.ExpandedName(pyxb.namespace.NamespaceForURI(u'http://docs.oasis-open.org/wsrf/bf-2'), u'Description')), min_occurs=0L, max_occurs=None),
    pyxb.binding.content.ParticleModel(PauseFailedFaultType._UseForTag(pyxb.namespace.ExpandedName(pyxb.namespace.NamespaceForURI(u'http://docs.oasis-open.org/wsrf/bf-2'), u'FaultCause')), min_occurs=0L, max_occurs=1L)
    )
PauseFailedFaultType._ContentModel = pyxb.binding.content.ParticleModel(PauseFailedFaultType._GroupModel_, min_occurs=1, max_occurs=1)


CTD_ANON_14._GroupModel = pyxb.binding.content.GroupSequence(
    pyxb.binding.content.ParticleModel(pyxb.binding.content.Wildcard(process_contents=pyxb.binding.content.Wildcard.PC_lax, namespace_constraint=(pyxb.binding.content.Wildcard.NC_not, u'http://docs.oasis-open.org/wsn/b-2')), min_occurs=0L, max_occurs=None)
    )
CTD_ANON_14._ContentModel = pyxb.binding.content.ParticleModel(CTD_ANON_14._GroupModel, min_occurs=1, max_occurs=1)


CTD_ANON_15._GroupModel = pyxb.binding.content.GroupSequence(
    pyxb.binding.content.ParticleModel(pyxb.binding.content.Wildcard(process_contents=pyxb.binding.content.Wildcard.PC_lax, namespace_constraint=(pyxb.binding.content.Wildcard.NC_not, u'http://docs.oasis-open.org/wsn/b-2')), min_occurs=0L, max_occurs=None)
    )
CTD_ANON_15._ContentModel = pyxb.binding.content.ParticleModel(CTD_ANON_15._GroupModel, min_occurs=1, max_occurs=1)


UnableToDestroySubscriptionFaultType._GroupModel_ = pyxb.binding.content.GroupSequence(
    pyxb.binding.content.ParticleModel(pyxb.binding.content.Wildcard(process_contents=pyxb.binding.content.Wildcard.PC_lax, namespace_constraint=(pyxb.binding.content.Wildcard.NC_not, u'http://docs.oasis-open.org/wsrf/bf-2')), min_occurs=0L, max_occurs=None),
    pyxb.binding.content.ParticleModel(UnableToDestroySubscriptionFaultType._UseForTag(pyxb.namespace.ExpandedName(pyxb.namespace.NamespaceForURI(u'http://docs.oasis-open.org/wsrf/bf-2'), u'Timestamp')), min_occurs=1L, max_occurs=1L),
    pyxb.binding.content.ParticleModel(UnableToDestroySubscriptionFaultType._UseForTag(pyxb.namespace.ExpandedName(pyxb.namespace.NamespaceForURI(u'http://docs.oasis-open.org/wsrf/bf-2'), u'Originator')), min_occurs=0L, max_occurs=1L),
    pyxb.binding.content.ParticleModel(UnableToDestroySubscriptionFaultType._UseForTag(pyxb.namespace.ExpandedName(pyxb.namespace.NamespaceForURI(u'http://docs.oasis-open.org/wsrf/bf-2'), u'ErrorCode')), min_occurs=0L, max_occurs=1L),
    pyxb.binding.content.ParticleModel(UnableToDestroySubscriptionFaultType._UseForTag(pyxb.namespace.ExpandedName(pyxb.namespace.NamespaceForURI(u'http://docs.oasis-open.org/wsrf/bf-2'), u'Description')), min_occurs=0L, max_occurs=None),
    pyxb.binding.content.ParticleModel(UnableToDestroySubscriptionFaultType._UseForTag(pyxb.namespace.ExpandedName(pyxb.namespace.NamespaceForURI(u'http://docs.oasis-open.org/wsrf/bf-2'), u'FaultCause')), min_occurs=0L, max_occurs=1L)
    )
UnableToDestroySubscriptionFaultType._ContentModel = pyxb.binding.content.ParticleModel(UnableToDestroySubscriptionFaultType._GroupModel_, min_occurs=1, max_occurs=1)


ResumeFailedFaultType._GroupModel_ = pyxb.binding.content.GroupSequence(
    pyxb.binding.content.ParticleModel(pyxb.binding.content.Wildcard(process_contents=pyxb.binding.content.Wildcard.PC_lax, namespace_constraint=(pyxb.binding.content.Wildcard.NC_not, u'http://docs.oasis-open.org/wsrf/bf-2')), min_occurs=0L, max_occurs=None),
    pyxb.binding.content.ParticleModel(ResumeFailedFaultType._UseForTag(pyxb.namespace.ExpandedName(pyxb.namespace.NamespaceForURI(u'http://docs.oasis-open.org/wsrf/bf-2'), u'Timestamp')), min_occurs=1L, max_occurs=1L),
    pyxb.binding.content.ParticleModel(ResumeFailedFaultType._UseForTag(pyxb.namespace.ExpandedName(pyxb.namespace.NamespaceForURI(u'http://docs.oasis-open.org/wsrf/bf-2'), u'Originator')), min_occurs=0L, max_occurs=1L),
    pyxb.binding.content.ParticleModel(ResumeFailedFaultType._UseForTag(pyxb.namespace.ExpandedName(pyxb.namespace.NamespaceForURI(u'http://docs.oasis-open.org/wsrf/bf-2'), u'ErrorCode')), min_occurs=0L, max_occurs=1L),
    pyxb.binding.content.ParticleModel(ResumeFailedFaultType._UseForTag(pyxb.namespace.ExpandedName(pyxb.namespace.NamespaceForURI(u'http://docs.oasis-open.org/wsrf/bf-2'), u'Description')), min_occurs=0L, max_occurs=None),
    pyxb.binding.content.ParticleModel(ResumeFailedFaultType._UseForTag(pyxb.namespace.ExpandedName(pyxb.namespace.NamespaceForURI(u'http://docs.oasis-open.org/wsrf/bf-2'), u'FaultCause')), min_occurs=0L, max_occurs=1L)
    )
ResumeFailedFaultType._ContentModel = pyxb.binding.content.ParticleModel(ResumeFailedFaultType._GroupModel_, min_occurs=1, max_occurs=1)


CTD_ANON_16._GroupModel = pyxb.binding.content.GroupSequence(
    pyxb.binding.content.ParticleModel(pyxb.binding.content.Wildcard(process_contents=pyxb.binding.content.Wildcard.PC_lax, namespace_constraint=(pyxb.binding.content.Wildcard.NC_not, u'http://docs.oasis-open.org/wsn/b-2')), min_occurs=0L, max_occurs=None)
    )
CTD_ANON_16._ContentModel = pyxb.binding.content.ParticleModel(CTD_ANON_16._GroupModel, min_occurs=1, max_occurs=1)


UnableToGetMessagesFaultType._GroupModel_ = pyxb.binding.content.GroupSequence(
    pyxb.binding.content.ParticleModel(pyxb.binding.content.Wildcard(process_contents=pyxb.binding.content.Wildcard.PC_lax, namespace_constraint=(pyxb.binding.content.Wildcard.NC_not, u'http://docs.oasis-open.org/wsrf/bf-2')), min_occurs=0L, max_occurs=None),
    pyxb.binding.content.ParticleModel(UnableToGetMessagesFaultType._UseForTag(pyxb.namespace.ExpandedName(pyxb.namespace.NamespaceForURI(u'http://docs.oasis-open.org/wsrf/bf-2'), u'Timestamp')), min_occurs=1L, max_occurs=1L),
    pyxb.binding.content.ParticleModel(UnableToGetMessagesFaultType._UseForTag(pyxb.namespace.ExpandedName(pyxb.namespace.NamespaceForURI(u'http://docs.oasis-open.org/wsrf/bf-2'), u'Originator')), min_occurs=0L, max_occurs=1L),
    pyxb.binding.content.ParticleModel(UnableToGetMessagesFaultType._UseForTag(pyxb.namespace.ExpandedName(pyxb.namespace.NamespaceForURI(u'http://docs.oasis-open.org/wsrf/bf-2'), u'ErrorCode')), min_occurs=0L, max_occurs=1L),
    pyxb.binding.content.ParticleModel(UnableToGetMessagesFaultType._UseForTag(pyxb.namespace.ExpandedName(pyxb.namespace.NamespaceForURI(u'http://docs.oasis-open.org/wsrf/bf-2'), u'Description')), min_occurs=0L, max_occurs=None),
    pyxb.binding.content.ParticleModel(UnableToGetMessagesFaultType._UseForTag(pyxb.namespace.ExpandedName(pyxb.namespace.NamespaceForURI(u'http://docs.oasis-open.org/wsrf/bf-2'), u'FaultCause')), min_occurs=0L, max_occurs=1L)
    )
UnableToGetMessagesFaultType._ContentModel = pyxb.binding.content.ParticleModel(UnableToGetMessagesFaultType._GroupModel_, min_occurs=1, max_occurs=1)


UnableToDestroyPullPointFaultType._GroupModel_ = pyxb.binding.content.GroupSequence(
    pyxb.binding.content.ParticleModel(pyxb.binding.content.Wildcard(process_contents=pyxb.binding.content.Wildcard.PC_lax, namespace_constraint=(pyxb.binding.content.Wildcard.NC_not, u'http://docs.oasis-open.org/wsrf/bf-2')), min_occurs=0L, max_occurs=None),
    pyxb.binding.content.ParticleModel(UnableToDestroyPullPointFaultType._UseForTag(pyxb.namespace.ExpandedName(pyxb.namespace.NamespaceForURI(u'http://docs.oasis-open.org/wsrf/bf-2'), u'Timestamp')), min_occurs=1L, max_occurs=1L),
    pyxb.binding.content.ParticleModel(UnableToDestroyPullPointFaultType._UseForTag(pyxb.namespace.ExpandedName(pyxb.namespace.NamespaceForURI(u'http://docs.oasis-open.org/wsrf/bf-2'), u'Originator')), min_occurs=0L, max_occurs=1L),
    pyxb.binding.content.ParticleModel(UnableToDestroyPullPointFaultType._UseForTag(pyxb.namespace.ExpandedName(pyxb.namespace.NamespaceForURI(u'http://docs.oasis-open.org/wsrf/bf-2'), u'ErrorCode')), min_occurs=0L, max_occurs=1L),
    pyxb.binding.content.ParticleModel(UnableToDestroyPullPointFaultType._UseForTag(pyxb.namespace.ExpandedName(pyxb.namespace.NamespaceForURI(u'http://docs.oasis-open.org/wsrf/bf-2'), u'Description')), min_occurs=0L, max_occurs=None),
    pyxb.binding.content.ParticleModel(UnableToDestroyPullPointFaultType._UseForTag(pyxb.namespace.ExpandedName(pyxb.namespace.NamespaceForURI(u'http://docs.oasis-open.org/wsrf/bf-2'), u'FaultCause')), min_occurs=0L, max_occurs=1L)
    )
UnableToDestroyPullPointFaultType._ContentModel = pyxb.binding.content.ParticleModel(UnableToDestroyPullPointFaultType._GroupModel_, min_occurs=1, max_occurs=1)


CTD_ANON_17._GroupModel = pyxb.binding.content.GroupSequence(
    pyxb.binding.content.ParticleModel(pyxb.binding.content.Wildcard(process_contents=pyxb.binding.content.Wildcard.PC_lax, namespace_constraint=(pyxb.binding.content.Wildcard.NC_not, u'http://docs.oasis-open.org/wsn/b-2')), min_occurs=0L, max_occurs=None)
    )
CTD_ANON_17._ContentModel = pyxb.binding.content.ParticleModel(CTD_ANON_17._GroupModel, min_occurs=1, max_occurs=1)


CTD_ANON_18._GroupModel = pyxb.binding.content.GroupSequence(
    pyxb.binding.content.ParticleModel(pyxb.binding.content.Wildcard(process_contents=pyxb.binding.content.Wildcard.PC_lax, namespace_constraint=pyxb.binding.content.Wildcard.NC_any), min_occurs=0L, max_occurs=None)
    )
CTD_ANON_18._ContentModel = pyxb.binding.content.ParticleModel(CTD_ANON_18._GroupModel, min_occurs=1, max_occurs=1)


CTD_ANON_19._GroupModel = pyxb.binding.content.GroupSequence(
    pyxb.binding.content.ParticleModel(pyxb.binding.content.Wildcard(process_contents=pyxb.binding.content.Wildcard.PC_lax, namespace_constraint=(pyxb.binding.content.Wildcard.NC_not, u'http://docs.oasis-open.org/wsn/b-2')), min_occurs=0L, max_occurs=None)
    )
CTD_ANON_19._ContentModel = pyxb.binding.content.ParticleModel(CTD_ANON_19._GroupModel, min_occurs=1, max_occurs=1)


CTD_ANON_20._GroupModel = pyxb.binding.content.GroupSequence(
    pyxb.binding.content.ParticleModel(pyxb.binding.content.Wildcard(process_contents=pyxb.binding.content.Wildcard.PC_lax, namespace_constraint=(pyxb.binding.content.Wildcard.NC_not, u'http://docs.oasis-open.org/wsn/b-2')), min_occurs=0L, max_occurs=None)
    )
CTD_ANON_20._ContentModel = pyxb.binding.content.ParticleModel(CTD_ANON_20._GroupModel, min_occurs=1, max_occurs=1)



CTD_ANON_21._AddElement(pyxb.binding.basis.element(pyxb.namespace.ExpandedName(Namespace, u'PullPoint'), pyxb.bundles.wssplat.wsa.EndpointReferenceType, scope=CTD_ANON_21))
CTD_ANON_21._GroupModel = pyxb.binding.content.GroupSequence(
    pyxb.binding.content.ParticleModel(CTD_ANON_21._UseForTag(pyxb.namespace.ExpandedName(Namespace, u'PullPoint')), min_occurs=1, max_occurs=1),
    pyxb.binding.content.ParticleModel(pyxb.binding.content.Wildcard(process_contents=pyxb.binding.content.Wildcard.PC_lax, namespace_constraint=(pyxb.binding.content.Wildcard.NC_not, u'http://docs.oasis-open.org/wsn/b-2')), min_occurs=0L, max_occurs=None)
    )
CTD_ANON_21._ContentModel = pyxb.binding.content.ParticleModel(CTD_ANON_21._GroupModel, min_occurs=1, max_occurs=1)


CTD_ANON_22._GroupModel = pyxb.binding.content.GroupSequence(
    pyxb.binding.content.ParticleModel(pyxb.binding.content.Wildcard(process_contents=pyxb.binding.content.Wildcard.PC_lax, namespace_constraint=(pyxb.binding.content.Wildcard.NC_not, u'http://docs.oasis-open.org/wsn/b-2')), min_occurs=0L, max_occurs=None)
    )
CTD_ANON_22._ContentModel = pyxb.binding.content.ParticleModel(CTD_ANON_22._GroupModel, min_occurs=1, max_occurs=1)


UnableToCreatePullPointFaultType._GroupModel_ = pyxb.binding.content.GroupSequence(
    pyxb.binding.content.ParticleModel(pyxb.binding.content.Wildcard(process_contents=pyxb.binding.content.Wildcard.PC_lax, namespace_constraint=(pyxb.binding.content.Wildcard.NC_not, u'http://docs.oasis-open.org/wsrf/bf-2')), min_occurs=0L, max_occurs=None),
    pyxb.binding.content.ParticleModel(UnableToCreatePullPointFaultType._UseForTag(pyxb.namespace.ExpandedName(pyxb.namespace.NamespaceForURI(u'http://docs.oasis-open.org/wsrf/bf-2'), u'Timestamp')), min_occurs=1L, max_occurs=1L),
    pyxb.binding.content.ParticleModel(UnableToCreatePullPointFaultType._UseForTag(pyxb.namespace.ExpandedName(pyxb.namespace.NamespaceForURI(u'http://docs.oasis-open.org/wsrf/bf-2'), u'Originator')), min_occurs=0L, max_occurs=1L),
    pyxb.binding.content.ParticleModel(UnableToCreatePullPointFaultType._UseForTag(pyxb.namespace.ExpandedName(pyxb.namespace.NamespaceForURI(u'http://docs.oasis-open.org/wsrf/bf-2'), u'ErrorCode')), min_occurs=0L, max_occurs=1L),
    pyxb.binding.content.ParticleModel(UnableToCreatePullPointFaultType._UseForTag(pyxb.namespace.ExpandedName(pyxb.namespace.NamespaceForURI(u'http://docs.oasis-open.org/wsrf/bf-2'), u'Description')), min_occurs=0L, max_occurs=None),
    pyxb.binding.content.ParticleModel(UnableToCreatePullPointFaultType._UseForTag(pyxb.namespace.ExpandedName(pyxb.namespace.NamespaceForURI(u'http://docs.oasis-open.org/wsrf/bf-2'), u'FaultCause')), min_occurs=0L, max_occurs=1L)
    )
UnableToCreatePullPointFaultType._ContentModel = pyxb.binding.content.ParticleModel(UnableToCreatePullPointFaultType._GroupModel_, min_occurs=1, max_occurs=1)



CTD_ANON_23._AddElement(pyxb.binding.basis.element(pyxb.namespace.ExpandedName(Namespace, u'FixedTopicSet'), pyxb.binding.datatypes.boolean, scope=CTD_ANON_23))

CTD_ANON_23._AddElement(pyxb.binding.basis.element(pyxb.namespace.ExpandedName(pyxb.namespace.NamespaceForURI(u'http://docs.oasis-open.org/wsn/t-1'), u'TopicSet'), pyxb.bundles.wssplat.wstop.TopicSetType, scope=CTD_ANON_23))

CTD_ANON_23._AddElement(pyxb.binding.basis.element(pyxb.namespace.ExpandedName(Namespace, u'TopicExpressionDialect'), pyxb.binding.datatypes.anyURI, scope=CTD_ANON_23))

CTD_ANON_23._AddElement(pyxb.binding.basis.element(pyxb.namespace.ExpandedName(Namespace, u'TopicExpression'), TopicExpressionType, scope=CTD_ANON_23))
CTD_ANON_23._GroupModel = pyxb.binding.content.GroupSequence(
    pyxb.binding.content.ParticleModel(CTD_ANON_23._UseForTag(pyxb.namespace.ExpandedName(Namespace, u'TopicExpression')), min_occurs=0L, max_occurs=None),
    pyxb.binding.content.ParticleModel(CTD_ANON_23._UseForTag(pyxb.namespace.ExpandedName(Namespace, u'FixedTopicSet')), min_occurs=0L, max_occurs=1L),
    pyxb.binding.content.ParticleModel(CTD_ANON_23._UseForTag(pyxb.namespace.ExpandedName(Namespace, u'TopicExpressionDialect')), min_occurs=0L, max_occurs=None),
    pyxb.binding.content.ParticleModel(CTD_ANON_23._UseForTag(pyxb.namespace.ExpandedName(pyxb.namespace.NamespaceForURI(u'http://docs.oasis-open.org/wsn/t-1'), u'TopicSet')), min_occurs=0L, max_occurs=1L)
    )
CTD_ANON_23._ContentModel = pyxb.binding.content.ParticleModel(CTD_ANON_23._GroupModel, min_occurs=1, max_occurs=1)
