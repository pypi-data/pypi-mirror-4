# ./pyxb/bundles/wssplat/raw/wsrf_bf.py
# -*- coding: utf-8 -*-
# PyXB bindings for NM:1f695b8b0461ea6da4ae596208b164781fcb562b
# Generated 2012-11-01 15:13:38.885464 by PyXB version 1.1.5
# Namespace http://docs.oasis-open.org/wsrf/bf-2

import pyxb
import pyxb.binding
import pyxb.binding.saxer
import StringIO
import pyxb.utils.utility
import pyxb.utils.domutils
import sys

# Unique identifier for bindings created at the same time
_GenerationUID = pyxb.utils.utility.UniqueIdentifier('urn:uuid:9fa95346-2460-11e2-937f-c8600024e903')

# Import bindings for namespaces imported into schema
import pyxb.binding.datatypes
import pyxb.binding.xml_
import pyxb.bundles.wssplat.wsa

Namespace = pyxb.namespace.NamespaceForURI(u'http://docs.oasis-open.org/wsrf/bf-2', create_if_missing=True)
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


# Complex type [anonymous] with content type ELEMENT_ONLY
class CTD_ANON (pyxb.binding.basis.complexTypeDefinition):
    _TypeDefinition = None
    _ContentTypeTag = pyxb.binding.basis.complexTypeDefinition._CT_ELEMENT_ONLY
    _Abstract = False
    _ExpandedName = None
    _DefinitionLocation = pyxb.utils.utility.Location('/tmp/pyxbdist.RHB65sy/PyXB-1.1.5/pyxb/bundles/wssplat/schemas/wsrf_bf.xsd', 75, 8)
    # Base type is pyxb.binding.datatypes.anyType
    _HasWildcardElement = True

    _ElementMap = {
        
    }
    _AttributeMap = {
        
    }



# Complex type [anonymous] with content type SIMPLE
class CTD_ANON_ (pyxb.binding.basis.complexTypeDefinition):
    _TypeDefinition = pyxb.binding.datatypes.string
    _ContentTypeTag = pyxb.binding.basis.complexTypeDefinition._CT_SIMPLE
    _Abstract = False
    _ExpandedName = None
    _DefinitionLocation = pyxb.utils.utility.Location('/tmp/pyxbdist.RHB65sy/PyXB-1.1.5/pyxb/bundles/wssplat/schemas/wsrf_bf.xsd', 66, 8)
    # Base type is pyxb.binding.datatypes.string
    
    # Attribute {http://www.w3.org/XML/1998/namespace}lang uses Python identifier lang
    __lang = pyxb.binding.content.AttributeUse(pyxb.namespace.ExpandedName(pyxb.namespace.XML, 'lang'), 'lang', '__httpdocs_oasis_open_orgwsrfbf_2_CTD_ANON__httpwww_w3_orgXML1998namespacelang', pyxb.binding.xml_.STD_ANON_lang)
    __lang._DeclarationLocation = None
    __lang._UseLocation = pyxb.utils.utility.Location('/tmp/pyxbdist.RHB65sy/PyXB-1.1.5/pyxb/bundles/wssplat/schemas/wsrf_bf.xsd', 69, 14)
    
    lang = property(__lang.value, __lang.set, None, None)


    _ElementMap = {
        
    }
    _AttributeMap = {
        __lang.name() : __lang
    }



# Complex type {http://docs.oasis-open.org/wsrf/bf-2}BaseFaultType with content type ELEMENT_ONLY
class BaseFaultType (pyxb.binding.basis.complexTypeDefinition):
    _TypeDefinition = None
    _ContentTypeTag = pyxb.binding.basis.complexTypeDefinition._CT_ELEMENT_ONLY
    _Abstract = False
    _ExpandedName = pyxb.namespace.ExpandedName(Namespace, u'BaseFaultType')
    _DefinitionLocation = pyxb.utils.utility.Location('/tmp/pyxbdist.RHB65sy/PyXB-1.1.5/pyxb/bundles/wssplat/schemas/wsrf_bf.xsd', 44, 2)
    # Base type is pyxb.binding.datatypes.anyType
    
    # Element {http://docs.oasis-open.org/wsrf/bf-2}Timestamp uses Python identifier Timestamp
    __Timestamp = pyxb.binding.content.ElementUse(pyxb.namespace.ExpandedName(Namespace, u'Timestamp'), 'Timestamp', '__httpdocs_oasis_open_orgwsrfbf_2_BaseFaultType_httpdocs_oasis_open_orgwsrfbf_2Timestamp', False)
    __Timestamp._DeclarationLocation = pyxb.utils.utility.Location('/tmp/pyxbdist.RHB65sy/PyXB-1.1.5/pyxb/bundles/wssplat/schemas/wsrf_bf.xsd', 48, 6)
    __Timestamp._UseLocation = pyxb.utils.utility.Location('/tmp/pyxbdist.RHB65sy/PyXB-1.1.5/pyxb/bundles/wssplat/schemas/wsrf_bf.xsd', 45, 4)

    
    Timestamp = property(__Timestamp.value, __Timestamp.set, None, None)

    
    # Element {http://docs.oasis-open.org/wsrf/bf-2}Originator uses Python identifier Originator
    __Originator = pyxb.binding.content.ElementUse(pyxb.namespace.ExpandedName(Namespace, u'Originator'), 'Originator', '__httpdocs_oasis_open_orgwsrfbf_2_BaseFaultType_httpdocs_oasis_open_orgwsrfbf_2Originator', False)
    __Originator._DeclarationLocation = pyxb.utils.utility.Location('/tmp/pyxbdist.RHB65sy/PyXB-1.1.5/pyxb/bundles/wssplat/schemas/wsrf_bf.xsd', 50, 6)
    __Originator._UseLocation = pyxb.utils.utility.Location('/tmp/pyxbdist.RHB65sy/PyXB-1.1.5/pyxb/bundles/wssplat/schemas/wsrf_bf.xsd', 45, 4)

    
    Originator = property(__Originator.value, __Originator.set, None, None)

    
    # Element {http://docs.oasis-open.org/wsrf/bf-2}FaultCause uses Python identifier FaultCause
    __FaultCause = pyxb.binding.content.ElementUse(pyxb.namespace.ExpandedName(Namespace, u'FaultCause'), 'FaultCause', '__httpdocs_oasis_open_orgwsrfbf_2_BaseFaultType_httpdocs_oasis_open_orgwsrfbf_2FaultCause', False)
    __FaultCause._DeclarationLocation = pyxb.utils.utility.Location('/tmp/pyxbdist.RHB65sy/PyXB-1.1.5/pyxb/bundles/wssplat/schemas/wsrf_bf.xsd', 74, 6)
    __FaultCause._UseLocation = pyxb.utils.utility.Location('/tmp/pyxbdist.RHB65sy/PyXB-1.1.5/pyxb/bundles/wssplat/schemas/wsrf_bf.xsd', 45, 4)

    
    FaultCause = property(__FaultCause.value, __FaultCause.set, None, None)

    
    # Element {http://docs.oasis-open.org/wsrf/bf-2}Description uses Python identifier Description
    __Description = pyxb.binding.content.ElementUse(pyxb.namespace.ExpandedName(Namespace, u'Description'), 'Description', '__httpdocs_oasis_open_orgwsrfbf_2_BaseFaultType_httpdocs_oasis_open_orgwsrfbf_2Description', True)
    __Description._DeclarationLocation = pyxb.utils.utility.Location('/tmp/pyxbdist.RHB65sy/PyXB-1.1.5/pyxb/bundles/wssplat/schemas/wsrf_bf.xsd', 64, 6)
    __Description._UseLocation = pyxb.utils.utility.Location('/tmp/pyxbdist.RHB65sy/PyXB-1.1.5/pyxb/bundles/wssplat/schemas/wsrf_bf.xsd', 45, 4)

    
    Description = property(__Description.value, __Description.set, None, None)

    
    # Element {http://docs.oasis-open.org/wsrf/bf-2}ErrorCode uses Python identifier ErrorCode
    __ErrorCode = pyxb.binding.content.ElementUse(pyxb.namespace.ExpandedName(Namespace, u'ErrorCode'), 'ErrorCode', '__httpdocs_oasis_open_orgwsrfbf_2_BaseFaultType_httpdocs_oasis_open_orgwsrfbf_2ErrorCode', False)
    __ErrorCode._DeclarationLocation = pyxb.utils.utility.Location('/tmp/pyxbdist.RHB65sy/PyXB-1.1.5/pyxb/bundles/wssplat/schemas/wsrf_bf.xsd', 52, 6)
    __ErrorCode._UseLocation = pyxb.utils.utility.Location('/tmp/pyxbdist.RHB65sy/PyXB-1.1.5/pyxb/bundles/wssplat/schemas/wsrf_bf.xsd', 45, 4)

    
    ErrorCode = property(__ErrorCode.value, __ErrorCode.set, None, None)

    _AttributeWildcard = pyxb.binding.content.Wildcard(process_contents=pyxb.binding.content.Wildcard.PC_lax, namespace_constraint=(pyxb.binding.content.Wildcard.NC_not, u'http://docs.oasis-open.org/wsrf/bf-2'))
    _HasWildcardElement = True

    _ElementMap = {
        __Timestamp.name() : __Timestamp,
        __Originator.name() : __Originator,
        __FaultCause.name() : __FaultCause,
        __Description.name() : __Description,
        __ErrorCode.name() : __ErrorCode
    }
    _AttributeMap = {
        
    }
Namespace.addCategoryObject('typeBinding', u'BaseFaultType', BaseFaultType)


# Complex type [anonymous] with content type MIXED
class CTD_ANON_2 (pyxb.binding.basis.complexTypeDefinition):
    _TypeDefinition = None
    _ContentTypeTag = pyxb.binding.basis.complexTypeDefinition._CT_MIXED
    _Abstract = False
    _ExpandedName = None
    _DefinitionLocation = pyxb.utils.utility.Location('/tmp/pyxbdist.RHB65sy/PyXB-1.1.5/pyxb/bundles/wssplat/schemas/wsrf_bf.xsd', 54, 8)
    # Base type is pyxb.binding.datatypes.anyType
    
    # Attribute dialect uses Python identifier dialect
    __dialect = pyxb.binding.content.AttributeUse(pyxb.namespace.ExpandedName(None, u'dialect'), 'dialect', '__httpdocs_oasis_open_orgwsrfbf_2_CTD_ANON_2_dialect', pyxb.binding.datatypes.anyURI, required=True)
    __dialect._DeclarationLocation = pyxb.utils.utility.Location('/tmp/pyxbdist.RHB65sy/PyXB-1.1.5/pyxb/bundles/wssplat/schemas/wsrf_bf.xsd', 57, 14)
    __dialect._UseLocation = pyxb.utils.utility.Location('/tmp/pyxbdist.RHB65sy/PyXB-1.1.5/pyxb/bundles/wssplat/schemas/wsrf_bf.xsd', 57, 14)
    
    dialect = property(__dialect.value, __dialect.set, None, None)

    _AttributeWildcard = pyxb.binding.content.Wildcard(process_contents=pyxb.binding.content.Wildcard.PC_lax, namespace_constraint=pyxb.binding.content.Wildcard.NC_any)
    _HasWildcardElement = True

    _ElementMap = {
        
    }
    _AttributeMap = {
        __dialect.name() : __dialect
    }



BaseFault = pyxb.binding.basis.element(pyxb.namespace.ExpandedName(Namespace, u'BaseFault'), BaseFaultType)
Namespace.addCategoryObject('elementBinding', BaseFault.name().localName(), BaseFault)


CTD_ANON._GroupModel = pyxb.binding.content.GroupSequence(
    pyxb.binding.content.ParticleModel(pyxb.binding.content.Wildcard(process_contents=pyxb.binding.content.Wildcard.PC_lax, namespace_constraint=(pyxb.binding.content.Wildcard.NC_not, u'http://docs.oasis-open.org/wsrf/bf-2')), min_occurs=1L, max_occurs=1L)
    )
CTD_ANON._ContentModel = pyxb.binding.content.ParticleModel(CTD_ANON._GroupModel, min_occurs=1, max_occurs=1)



BaseFaultType._AddElement(pyxb.binding.basis.element(pyxb.namespace.ExpandedName(Namespace, u'Timestamp'), pyxb.binding.datatypes.dateTime, scope=BaseFaultType))

BaseFaultType._AddElement(pyxb.binding.basis.element(pyxb.namespace.ExpandedName(Namespace, u'Originator'), pyxb.bundles.wssplat.wsa.EndpointReferenceType, scope=BaseFaultType))

BaseFaultType._AddElement(pyxb.binding.basis.element(pyxb.namespace.ExpandedName(Namespace, u'FaultCause'), CTD_ANON, scope=BaseFaultType))

BaseFaultType._AddElement(pyxb.binding.basis.element(pyxb.namespace.ExpandedName(Namespace, u'Description'), CTD_ANON_, scope=BaseFaultType))

BaseFaultType._AddElement(pyxb.binding.basis.element(pyxb.namespace.ExpandedName(Namespace, u'ErrorCode'), CTD_ANON_2, scope=BaseFaultType))
BaseFaultType._GroupModel = pyxb.binding.content.GroupSequence(
    pyxb.binding.content.ParticleModel(pyxb.binding.content.Wildcard(process_contents=pyxb.binding.content.Wildcard.PC_lax, namespace_constraint=(pyxb.binding.content.Wildcard.NC_not, u'http://docs.oasis-open.org/wsrf/bf-2')), min_occurs=0L, max_occurs=None),
    pyxb.binding.content.ParticleModel(BaseFaultType._UseForTag(pyxb.namespace.ExpandedName(Namespace, u'Timestamp')), min_occurs=1L, max_occurs=1L),
    pyxb.binding.content.ParticleModel(BaseFaultType._UseForTag(pyxb.namespace.ExpandedName(Namespace, u'Originator')), min_occurs=0L, max_occurs=1L),
    pyxb.binding.content.ParticleModel(BaseFaultType._UseForTag(pyxb.namespace.ExpandedName(Namespace, u'ErrorCode')), min_occurs=0L, max_occurs=1L),
    pyxb.binding.content.ParticleModel(BaseFaultType._UseForTag(pyxb.namespace.ExpandedName(Namespace, u'Description')), min_occurs=0L, max_occurs=None),
    pyxb.binding.content.ParticleModel(BaseFaultType._UseForTag(pyxb.namespace.ExpandedName(Namespace, u'FaultCause')), min_occurs=0L, max_occurs=1L)
    )
BaseFaultType._ContentModel = pyxb.binding.content.ParticleModel(BaseFaultType._GroupModel, min_occurs=1, max_occurs=1)


CTD_ANON_2._GroupModel_ = pyxb.binding.content.GroupSequence(
    pyxb.binding.content.ParticleModel(pyxb.binding.content.Wildcard(process_contents=pyxb.binding.content.Wildcard.PC_lax, namespace_constraint=pyxb.binding.content.Wildcard.NC_any), min_occurs=0, max_occurs=None)
    )
CTD_ANON_2._GroupModel_2 = pyxb.binding.content.GroupSequence(
    
    )
CTD_ANON_2._GroupModel = pyxb.binding.content.GroupSequence(
    pyxb.binding.content.ParticleModel(CTD_ANON_2._GroupModel_, min_occurs=1, max_occurs=1),
    pyxb.binding.content.ParticleModel(CTD_ANON_2._GroupModel_2, min_occurs=0L, max_occurs=1L)
    )
CTD_ANON_2._ContentModel = pyxb.binding.content.ParticleModel(CTD_ANON_2._GroupModel, min_occurs=0L, max_occurs=1L)
