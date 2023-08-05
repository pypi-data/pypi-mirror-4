# ./pyxb/bundles/wssplat/raw/wsu.py
# -*- coding: utf-8 -*-
# PyXB bindings for NM:e2891a804ace8fbcc4a500f1dbc94cf01e38e023
# Generated 2012-11-01 15:13:36.409149 by PyXB version 1.1.5
# Namespace http://docs.oasis-open.org/wss/2004/01/oasis-200401-wss-wssecurity-utility-1.0.xsd

import pyxb
import pyxb.binding
import pyxb.binding.saxer
import StringIO
import pyxb.utils.utility
import pyxb.utils.domutils
import sys

# Unique identifier for bindings created at the same time
_GenerationUID = pyxb.utils.utility.UniqueIdentifier('urn:uuid:9e2fe796-2460-11e2-ba0e-c8600024e903')

# Import bindings for namespaces imported into schema
import pyxb.binding.datatypes

Namespace = pyxb.namespace.NamespaceForURI(u'http://docs.oasis-open.org/wss/2004/01/oasis-200401-wss-wssecurity-utility-1.0.xsd', create_if_missing=True)
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


# Atomic simple type: {http://docs.oasis-open.org/wss/2004/01/oasis-200401-wss-wssecurity-utility-1.0.xsd}tTimestampFault
class tTimestampFault (pyxb.binding.datatypes.QName, pyxb.binding.basis.enumeration_mixin):

    """
This type defines the fault code value for Timestamp message expiration.
          """

    _ExpandedName = pyxb.namespace.ExpandedName(Namespace, u'tTimestampFault')
    _DefinitionLocation = pyxb.utils.utility.Location('/tmp/pyxbdist.RHB65sy/PyXB-1.1.5/pyxb/bundles/wssplat/schemas/wsu.xsd', 17, 1)
    _Documentation = u'\nThis type defines the fault code value for Timestamp message expiration.\n          '
tTimestampFault._CF_enumeration = pyxb.binding.facets.CF_enumeration(value_datatype=tTimestampFault, enum_prefix=None)
tTimestampFault.wsuMessageExpired = tTimestampFault._CF_enumeration.addEnumeration(unicode_value=u'wsu:MessageExpired', tag=u'wsuMessageExpired')
tTimestampFault._InitializeFacetMap(tTimestampFault._CF_enumeration)
Namespace.addCategoryObject('typeBinding', u'tTimestampFault', tTimestampFault)

# Complex type {http://docs.oasis-open.org/wss/2004/01/oasis-200401-wss-wssecurity-utility-1.0.xsd}AttributedDateTime with content type SIMPLE
class AttributedDateTime (pyxb.binding.basis.complexTypeDefinition):
    _TypeDefinition = pyxb.binding.datatypes.string
    _ContentTypeTag = pyxb.binding.basis.complexTypeDefinition._CT_SIMPLE
    _Abstract = False
    _ExpandedName = pyxb.namespace.ExpandedName(Namespace, u'AttributedDateTime')
    _DefinitionLocation = pyxb.utils.utility.Location('/tmp/pyxbdist.RHB65sy/PyXB-1.1.5/pyxb/bundles/wssplat/schemas/wsu.xsd', 45, 1)
    # Base type is pyxb.binding.datatypes.string
    
    # Attribute {http://docs.oasis-open.org/wss/2004/01/oasis-200401-wss-wssecurity-utility-1.0.xsd}Id uses Python identifier Id
    __Id = pyxb.binding.content.AttributeUse(pyxb.namespace.ExpandedName(Namespace, u'Id'), 'Id', '__httpdocs_oasis_open_orgwss200401oasis_200401_wss_wssecurity_utility_1_0_xsd_AttributedDateTime_httpdocs_oasis_open_orgwss200401oasis_200401_wss_wssecurity_utility_1_0_xsdId', pyxb.binding.datatypes.ID)
    __Id._DeclarationLocation = pyxb.utils.utility.Location('/tmp/pyxbdist.RHB65sy/PyXB-1.1.5/pyxb/bundles/wssplat/schemas/wsu.xsd', 28, 1)
    __Id._UseLocation = pyxb.utils.utility.Location('/tmp/pyxbdist.RHB65sy/PyXB-1.1.5/pyxb/bundles/wssplat/schemas/wsu.xsd', 41, 2)
    
    Id = property(__Id.value, __Id.set, None, u'\nThis global attribute supports annotating arbitrary elements with an ID.\n          ')

    _AttributeWildcard = pyxb.binding.content.Wildcard(process_contents=pyxb.binding.content.Wildcard.PC_lax, namespace_constraint=(pyxb.binding.content.Wildcard.NC_not, u'http://docs.oasis-open.org/wss/2004/01/oasis-200401-wss-wssecurity-utility-1.0.xsd'))

    _ElementMap = {
        
    }
    _AttributeMap = {
        __Id.name() : __Id
    }
Namespace.addCategoryObject('typeBinding', u'AttributedDateTime', AttributedDateTime)


# Complex type {http://docs.oasis-open.org/wss/2004/01/oasis-200401-wss-wssecurity-utility-1.0.xsd}AttributedURI with content type SIMPLE
class AttributedURI (pyxb.binding.basis.complexTypeDefinition):
    _TypeDefinition = pyxb.binding.datatypes.anyURI
    _ContentTypeTag = pyxb.binding.basis.complexTypeDefinition._CT_SIMPLE
    _Abstract = False
    _ExpandedName = pyxb.namespace.ExpandedName(Namespace, u'AttributedURI')
    _DefinitionLocation = pyxb.utils.utility.Location('/tmp/pyxbdist.RHB65sy/PyXB-1.1.5/pyxb/bundles/wssplat/schemas/wsu.xsd', 57, 1)
    # Base type is pyxb.binding.datatypes.anyURI
    
    # Attribute {http://docs.oasis-open.org/wss/2004/01/oasis-200401-wss-wssecurity-utility-1.0.xsd}Id uses Python identifier Id
    __Id = pyxb.binding.content.AttributeUse(pyxb.namespace.ExpandedName(Namespace, u'Id'), 'Id', '__httpdocs_oasis_open_orgwss200401oasis_200401_wss_wssecurity_utility_1_0_xsd_AttributedURI_httpdocs_oasis_open_orgwss200401oasis_200401_wss_wssecurity_utility_1_0_xsdId', pyxb.binding.datatypes.ID)
    __Id._DeclarationLocation = pyxb.utils.utility.Location('/tmp/pyxbdist.RHB65sy/PyXB-1.1.5/pyxb/bundles/wssplat/schemas/wsu.xsd', 28, 1)
    __Id._UseLocation = pyxb.utils.utility.Location('/tmp/pyxbdist.RHB65sy/PyXB-1.1.5/pyxb/bundles/wssplat/schemas/wsu.xsd', 41, 2)
    
    Id = property(__Id.value, __Id.set, None, u'\nThis global attribute supports annotating arbitrary elements with an ID.\n          ')

    _AttributeWildcard = pyxb.binding.content.Wildcard(process_contents=pyxb.binding.content.Wildcard.PC_lax, namespace_constraint=(pyxb.binding.content.Wildcard.NC_not, u'http://docs.oasis-open.org/wss/2004/01/oasis-200401-wss-wssecurity-utility-1.0.xsd'))

    _ElementMap = {
        
    }
    _AttributeMap = {
        __Id.name() : __Id
    }
Namespace.addCategoryObject('typeBinding', u'AttributedURI', AttributedURI)


# Complex type {http://docs.oasis-open.org/wss/2004/01/oasis-200401-wss-wssecurity-utility-1.0.xsd}TimestampType with content type ELEMENT_ONLY
class TimestampType (pyxb.binding.basis.complexTypeDefinition):
    _TypeDefinition = None
    _ContentTypeTag = pyxb.binding.basis.complexTypeDefinition._CT_ELEMENT_ONLY
    _Abstract = False
    _ExpandedName = pyxb.namespace.ExpandedName(Namespace, u'TimestampType')
    _DefinitionLocation = pyxb.utils.utility.Location('/tmp/pyxbdist.RHB65sy/PyXB-1.1.5/pyxb/bundles/wssplat/schemas/wsu.xsd', 70, 1)
    # Base type is pyxb.binding.datatypes.anyType
    
    # Element {http://docs.oasis-open.org/wss/2004/01/oasis-200401-wss-wssecurity-utility-1.0.xsd}Created uses Python identifier Created
    __Created = pyxb.binding.content.ElementUse(pyxb.namespace.ExpandedName(Namespace, u'Created'), 'Created', '__httpdocs_oasis_open_orgwss200401oasis_200401_wss_wssecurity_utility_1_0_xsd_TimestampType_httpdocs_oasis_open_orgwss200401oasis_200401_wss_wssecurity_utility_1_0_xsdCreated', False)
    __Created._DeclarationLocation = pyxb.utils.utility.Location('/tmp/pyxbdist.RHB65sy/PyXB-1.1.5/pyxb/bundles/wssplat/schemas/wsu.xsd', 101, 1)
    __Created._UseLocation = pyxb.utils.utility.Location('/tmp/pyxbdist.RHB65sy/PyXB-1.1.5/pyxb/bundles/wssplat/schemas/wsu.xsd', 76, 2)

    
    Created = property(__Created.value, __Created.set, None, u'\nThis element allows a creation time to be applied anywhere element wildcards are present.\n            ')

    
    # Element {http://docs.oasis-open.org/wss/2004/01/oasis-200401-wss-wssecurity-utility-1.0.xsd}Expires uses Python identifier Expires
    __Expires = pyxb.binding.content.ElementUse(pyxb.namespace.ExpandedName(Namespace, u'Expires'), 'Expires', '__httpdocs_oasis_open_orgwss200401oasis_200401_wss_wssecurity_utility_1_0_xsd_TimestampType_httpdocs_oasis_open_orgwss200401oasis_200401_wss_wssecurity_utility_1_0_xsdExpires', False)
    __Expires._DeclarationLocation = pyxb.utils.utility.Location('/tmp/pyxbdist.RHB65sy/PyXB-1.1.5/pyxb/bundles/wssplat/schemas/wsu.xsd', 94, 1)
    __Expires._UseLocation = pyxb.utils.utility.Location('/tmp/pyxbdist.RHB65sy/PyXB-1.1.5/pyxb/bundles/wssplat/schemas/wsu.xsd', 76, 2)

    
    Expires = property(__Expires.value, __Expires.set, None, u'\nThis element allows an expiration time to be applied anywhere element wildcards are present.\n            ')

    
    # Attribute {http://docs.oasis-open.org/wss/2004/01/oasis-200401-wss-wssecurity-utility-1.0.xsd}Id uses Python identifier Id
    __Id = pyxb.binding.content.AttributeUse(pyxb.namespace.ExpandedName(Namespace, u'Id'), 'Id', '__httpdocs_oasis_open_orgwss200401oasis_200401_wss_wssecurity_utility_1_0_xsd_TimestampType_httpdocs_oasis_open_orgwss200401oasis_200401_wss_wssecurity_utility_1_0_xsdId', pyxb.binding.datatypes.ID)
    __Id._DeclarationLocation = pyxb.utils.utility.Location('/tmp/pyxbdist.RHB65sy/PyXB-1.1.5/pyxb/bundles/wssplat/schemas/wsu.xsd', 28, 1)
    __Id._UseLocation = pyxb.utils.utility.Location('/tmp/pyxbdist.RHB65sy/PyXB-1.1.5/pyxb/bundles/wssplat/schemas/wsu.xsd', 41, 2)
    
    Id = property(__Id.value, __Id.set, None, u'\nThis global attribute supports annotating arbitrary elements with an ID.\n          ')

    _AttributeWildcard = pyxb.binding.content.Wildcard(process_contents=pyxb.binding.content.Wildcard.PC_lax, namespace_constraint=(pyxb.binding.content.Wildcard.NC_not, u'http://docs.oasis-open.org/wss/2004/01/oasis-200401-wss-wssecurity-utility-1.0.xsd'))
    _HasWildcardElement = True

    _ElementMap = {
        __Created.name() : __Created,
        __Expires.name() : __Expires
    }
    _AttributeMap = {
        __Id.name() : __Id
    }
Namespace.addCategoryObject('typeBinding', u'TimestampType', TimestampType)


Expires = pyxb.binding.basis.element(pyxb.namespace.ExpandedName(Namespace, u'Expires'), AttributedDateTime, documentation=u'\nThis element allows an expiration time to be applied anywhere element wildcards are present.\n            ')
Namespace.addCategoryObject('elementBinding', Expires.name().localName(), Expires)

Created = pyxb.binding.basis.element(pyxb.namespace.ExpandedName(Namespace, u'Created'), AttributedDateTime, documentation=u'\nThis element allows a creation time to be applied anywhere element wildcards are present.\n            ')
Namespace.addCategoryObject('elementBinding', Created.name().localName(), Created)

Timestamp = pyxb.binding.basis.element(pyxb.namespace.ExpandedName(Namespace, u'Timestamp'), TimestampType, documentation=u'\nThis element allows Timestamps to be applied anywhere element wildcards are present,\nincluding as a SOAP header.\n            ')
Namespace.addCategoryObject('elementBinding', Timestamp.name().localName(), Timestamp)



TimestampType._AddElement(pyxb.binding.basis.element(pyxb.namespace.ExpandedName(Namespace, u'Created'), AttributedDateTime, scope=TimestampType, documentation=u'\nThis element allows a creation time to be applied anywhere element wildcards are present.\n            '))

TimestampType._AddElement(pyxb.binding.basis.element(pyxb.namespace.ExpandedName(Namespace, u'Expires'), AttributedDateTime, scope=TimestampType, documentation=u'\nThis element allows an expiration time to be applied anywhere element wildcards are present.\n            '))
TimestampType._GroupModel_ = pyxb.binding.content.GroupChoice(
    pyxb.binding.content.ParticleModel(pyxb.binding.content.Wildcard(process_contents=pyxb.binding.content.Wildcard.PC_lax, namespace_constraint=(pyxb.binding.content.Wildcard.NC_not, u'http://docs.oasis-open.org/wss/2004/01/oasis-200401-wss-wssecurity-utility-1.0.xsd')), min_occurs=1, max_occurs=1)
    )
TimestampType._GroupModel = pyxb.binding.content.GroupSequence(
    pyxb.binding.content.ParticleModel(TimestampType._UseForTag(pyxb.namespace.ExpandedName(Namespace, u'Created')), min_occurs=0L, max_occurs=1),
    pyxb.binding.content.ParticleModel(TimestampType._UseForTag(pyxb.namespace.ExpandedName(Namespace, u'Expires')), min_occurs=0L, max_occurs=1),
    pyxb.binding.content.ParticleModel(TimestampType._GroupModel_, min_occurs=0L, max_occurs=None)
    )
TimestampType._ContentModel = pyxb.binding.content.ParticleModel(TimestampType._GroupModel, min_occurs=1, max_occurs=1)
