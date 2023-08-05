# ./pyxb/bundles/wssplat/raw/wsp200607.py
# -*- coding: utf-8 -*-
# PyXB bindings for NM:f7a1b3ccf248600ac00f0ba01aeba7fdd42b4412
# Generated 2012-11-01 15:13:37.029060 by PyXB version 1.1.5
# Namespace http://www.w3.org/2006/07/ws-policy

import pyxb
import pyxb.binding
import pyxb.binding.saxer
import StringIO
import pyxb.utils.utility
import pyxb.utils.domutils
import sys

# Unique identifier for bindings created at the same time
_GenerationUID = pyxb.utils.utility.UniqueIdentifier('urn:uuid:9e8d8a04-2460-11e2-aa24-c8600024e903')

# Import bindings for namespaces imported into schema
import pyxb.binding.datatypes

Namespace = pyxb.namespace.NamespaceForURI(u'http://www.w3.org/2006/07/ws-policy', create_if_missing=True)
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


# List simple type: [anonymous]
# superclasses pyxb.binding.datatypes.anySimpleType
class STD_ANON (pyxb.binding.basis.STD_list):

    """Simple type that is a list of pyxb.binding.datatypes.anyURI."""

    _ExpandedName = None
    _DefinitionLocation = pyxb.utils.utility.Location('/tmp/pyxbdist.RHB65sy/PyXB-1.1.5/pyxb/bundles/wssplat/schemas/wsp200607.xsd', 74, 4)
    _Documentation = None

    _ItemType = pyxb.binding.datatypes.anyURI
STD_ANON._InitializeFacetMap()

# Complex type [anonymous] with content type EMPTY
class CTD_ANON (pyxb.binding.basis.complexTypeDefinition):
    _TypeDefinition = None
    _ContentTypeTag = pyxb.binding.basis.complexTypeDefinition._CT_EMPTY
    _Abstract = False
    _ExpandedName = None
    _DefinitionLocation = pyxb.utils.utility.Location('/tmp/pyxbdist.RHB65sy/PyXB-1.1.5/pyxb/bundles/wssplat/schemas/wsp200607.xsd', 60, 4)
    # Base type is pyxb.binding.datatypes.anyType
    
    # Attribute DigestAlgorithm uses Python identifier DigestAlgorithm
    __DigestAlgorithm = pyxb.binding.content.AttributeUse(pyxb.namespace.ExpandedName(None, u'DigestAlgorithm'), 'DigestAlgorithm', '__httpwww_w3_org200607ws_policy_CTD_ANON_DigestAlgorithm', pyxb.binding.datatypes.anyURI, unicode_default=u'http://www.w3.org/2006/07/policy/Sha1Exc')
    __DigestAlgorithm._DeclarationLocation = pyxb.utils.utility.Location('/tmp/pyxbdist.RHB65sy/PyXB-1.1.5/pyxb/bundles/wssplat/schemas/wsp200607.xsd', 64, 6)
    __DigestAlgorithm._UseLocation = pyxb.utils.utility.Location('/tmp/pyxbdist.RHB65sy/PyXB-1.1.5/pyxb/bundles/wssplat/schemas/wsp200607.xsd', 64, 6)
    
    DigestAlgorithm = property(__DigestAlgorithm.value, __DigestAlgorithm.set, None, None)

    
    # Attribute Digest uses Python identifier Digest
    __Digest = pyxb.binding.content.AttributeUse(pyxb.namespace.ExpandedName(None, u'Digest'), 'Digest', '__httpwww_w3_org200607ws_policy_CTD_ANON_Digest', pyxb.binding.datatypes.base64Binary)
    __Digest._DeclarationLocation = pyxb.utils.utility.Location('/tmp/pyxbdist.RHB65sy/PyXB-1.1.5/pyxb/bundles/wssplat/schemas/wsp200607.xsd', 63, 6)
    __Digest._UseLocation = pyxb.utils.utility.Location('/tmp/pyxbdist.RHB65sy/PyXB-1.1.5/pyxb/bundles/wssplat/schemas/wsp200607.xsd', 63, 6)
    
    Digest = property(__Digest.value, __Digest.set, None, None)

    
    # Attribute URI uses Python identifier URI
    __URI = pyxb.binding.content.AttributeUse(pyxb.namespace.ExpandedName(None, u'URI'), 'URI', '__httpwww_w3_org200607ws_policy_CTD_ANON_URI', pyxb.binding.datatypes.anyURI, required=True)
    __URI._DeclarationLocation = pyxb.utils.utility.Location('/tmp/pyxbdist.RHB65sy/PyXB-1.1.5/pyxb/bundles/wssplat/schemas/wsp200607.xsd', 61, 6)
    __URI._UseLocation = pyxb.utils.utility.Location('/tmp/pyxbdist.RHB65sy/PyXB-1.1.5/pyxb/bundles/wssplat/schemas/wsp200607.xsd', 61, 6)
    
    URI = property(__URI.value, __URI.set, None, None)

    _AttributeWildcard = pyxb.binding.content.Wildcard(process_contents=pyxb.binding.content.Wildcard.PC_lax, namespace_constraint=pyxb.binding.content.Wildcard.NC_any)

    _ElementMap = {
        
    }
    _AttributeMap = {
        __DigestAlgorithm.name() : __DigestAlgorithm,
        __Digest.name() : __Digest,
        __URI.name() : __URI
    }



# Complex type {http://www.w3.org/2006/07/ws-policy}OperatorContentType with content type ELEMENT_ONLY
class OperatorContentType (pyxb.binding.basis.complexTypeDefinition):
    _TypeDefinition = None
    _ContentTypeTag = pyxb.binding.basis.complexTypeDefinition._CT_ELEMENT_ONLY
    _Abstract = False
    _ExpandedName = pyxb.namespace.ExpandedName(Namespace, u'OperatorContentType')
    _DefinitionLocation = pyxb.utils.utility.Location('/tmp/pyxbdist.RHB65sy/PyXB-1.1.5/pyxb/bundles/wssplat/schemas/wsp200607.xsd', 46, 2)
    # Base type is pyxb.binding.datatypes.anyType
    
    # Element {http://www.w3.org/2006/07/ws-policy}PolicyReference uses Python identifier PolicyReference
    __PolicyReference = pyxb.binding.content.ElementUse(pyxb.namespace.ExpandedName(Namespace, u'PolicyReference'), 'PolicyReference', '__httpwww_w3_org200607ws_policy_OperatorContentType_httpwww_w3_org200607ws_policyPolicyReference', True)
    __PolicyReference._DeclarationLocation = pyxb.utils.utility.Location('/tmp/pyxbdist.RHB65sy/PyXB-1.1.5/pyxb/bundles/wssplat/schemas/wsp200607.xsd', 59, 2)
    __PolicyReference._UseLocation = pyxb.utils.utility.Location('/tmp/pyxbdist.RHB65sy/PyXB-1.1.5/pyxb/bundles/wssplat/schemas/wsp200607.xsd', 47, 4)

    
    PolicyReference = property(__PolicyReference.value, __PolicyReference.set, None, None)

    
    # Element {http://www.w3.org/2006/07/ws-policy}Policy uses Python identifier Policy
    __Policy = pyxb.binding.content.ElementUse(pyxb.namespace.ExpandedName(Namespace, u'Policy'), 'Policy', '__httpwww_w3_org200607ws_policy_OperatorContentType_httpwww_w3_org200607ws_policyPolicy', True)
    __Policy._DeclarationLocation = pyxb.utils.utility.Location('/tmp/pyxbdist.RHB65sy/PyXB-1.1.5/pyxb/bundles/wssplat/schemas/wsp200607.xsd', 30, 2)
    __Policy._UseLocation = pyxb.utils.utility.Location('/tmp/pyxbdist.RHB65sy/PyXB-1.1.5/pyxb/bundles/wssplat/schemas/wsp200607.xsd', 47, 4)

    
    Policy = property(__Policy.value, __Policy.set, None, None)

    
    # Element {http://www.w3.org/2006/07/ws-policy}ExactlyOne uses Python identifier ExactlyOne
    __ExactlyOne = pyxb.binding.content.ElementUse(pyxb.namespace.ExpandedName(Namespace, u'ExactlyOne'), 'ExactlyOne', '__httpwww_w3_org200607ws_policy_OperatorContentType_httpwww_w3_org200607ws_policyExactlyOne', True)
    __ExactlyOne._DeclarationLocation = pyxb.utils.utility.Location('/tmp/pyxbdist.RHB65sy/PyXB-1.1.5/pyxb/bundles/wssplat/schemas/wsp200607.xsd', 44, 2)
    __ExactlyOne._UseLocation = pyxb.utils.utility.Location('/tmp/pyxbdist.RHB65sy/PyXB-1.1.5/pyxb/bundles/wssplat/schemas/wsp200607.xsd', 47, 4)

    
    ExactlyOne = property(__ExactlyOne.value, __ExactlyOne.set, None, None)

    
    # Element {http://www.w3.org/2006/07/ws-policy}All uses Python identifier All
    __All = pyxb.binding.content.ElementUse(pyxb.namespace.ExpandedName(Namespace, u'All'), 'All', '__httpwww_w3_org200607ws_policy_OperatorContentType_httpwww_w3_org200607ws_policyAll', True)
    __All._DeclarationLocation = pyxb.utils.utility.Location('/tmp/pyxbdist.RHB65sy/PyXB-1.1.5/pyxb/bundles/wssplat/schemas/wsp200607.xsd', 43, 2)
    __All._UseLocation = pyxb.utils.utility.Location('/tmp/pyxbdist.RHB65sy/PyXB-1.1.5/pyxb/bundles/wssplat/schemas/wsp200607.xsd', 47, 4)

    
    All = property(__All.value, __All.set, None, None)

    _HasWildcardElement = True

    _ElementMap = {
        __PolicyReference.name() : __PolicyReference,
        __Policy.name() : __Policy,
        __ExactlyOne.name() : __ExactlyOne,
        __All.name() : __All
    }
    _AttributeMap = {
        
    }
Namespace.addCategoryObject('typeBinding', u'OperatorContentType', OperatorContentType)


# Complex type [anonymous] with content type ELEMENT_ONLY
class CTD_ANON_ (OperatorContentType):
    _TypeDefinition = None
    _ContentTypeTag = pyxb.binding.basis.complexTypeDefinition._CT_ELEMENT_ONLY
    _Abstract = False
    _ExpandedName = None
    _DefinitionLocation = pyxb.utils.utility.Location('/tmp/pyxbdist.RHB65sy/PyXB-1.1.5/pyxb/bundles/wssplat/schemas/wsp200607.xsd', 31, 4)
    # Base type is OperatorContentType
    
    # Element PolicyReference ({http://www.w3.org/2006/07/ws-policy}PolicyReference) inherited from {http://www.w3.org/2006/07/ws-policy}OperatorContentType
    
    # Element Policy ({http://www.w3.org/2006/07/ws-policy}Policy) inherited from {http://www.w3.org/2006/07/ws-policy}OperatorContentType
    
    # Element ExactlyOne ({http://www.w3.org/2006/07/ws-policy}ExactlyOne) inherited from {http://www.w3.org/2006/07/ws-policy}OperatorContentType
    
    # Element All ({http://www.w3.org/2006/07/ws-policy}All) inherited from {http://www.w3.org/2006/07/ws-policy}OperatorContentType
    
    # Attribute Name uses Python identifier Name
    __Name = pyxb.binding.content.AttributeUse(pyxb.namespace.ExpandedName(None, u'Name'), 'Name', '__httpwww_w3_org200607ws_policy_CTD_ANON__Name', pyxb.binding.datatypes.anyURI)
    __Name._DeclarationLocation = pyxb.utils.utility.Location('/tmp/pyxbdist.RHB65sy/PyXB-1.1.5/pyxb/bundles/wssplat/schemas/wsp200607.xsd', 35, 10)
    __Name._UseLocation = pyxb.utils.utility.Location('/tmp/pyxbdist.RHB65sy/PyXB-1.1.5/pyxb/bundles/wssplat/schemas/wsp200607.xsd', 35, 10)
    
    Name = property(__Name.value, __Name.set, None, None)

    
    # Attribute {http://docs.oasis-open.org/wss/2004/01/oasis-200401-wss-wssecurity-utility-1.0.xsd}Id uses Python identifier Id
    __Id = pyxb.binding.content.AttributeUse(pyxb.namespace.ExpandedName(pyxb.namespace.NamespaceForURI(u'http://docs.oasis-open.org/wss/2004/01/oasis-200401-wss-wssecurity-utility-1.0.xsd'), u'Id'), 'Id', '__httpwww_w3_org200607ws_policy_CTD_ANON__httpdocs_oasis_open_orgwss200401oasis_200401_wss_wssecurity_utility_1_0_xsdId', pyxb.binding.datatypes.ID)
    __Id._DeclarationLocation = pyxb.utils.utility.Location('/tmp/pyxbdist.RHB65sy/PyXB-1.1.5/pyxb/bundles/wssplat/schemas/wsu.xsd', 28, 1)
    __Id._UseLocation = pyxb.utils.utility.Location('/tmp/pyxbdist.RHB65sy/PyXB-1.1.5/pyxb/bundles/wssplat/schemas/wsp200607.xsd', 36, 10)
    
    Id = property(__Id.value, __Id.set, None, u'\nThis global attribute supports annotating arbitrary elements with an ID.\n          ')

    _AttributeWildcard = pyxb.binding.content.Wildcard(process_contents=pyxb.binding.content.Wildcard.PC_lax, namespace_constraint=pyxb.binding.content.Wildcard.NC_any)
    _HasWildcardElement = True

    _ElementMap = OperatorContentType._ElementMap.copy()
    _ElementMap.update({
        
    })
    _AttributeMap = OperatorContentType._AttributeMap.copy()
    _AttributeMap.update({
        __Name.name() : __Name,
        __Id.name() : __Id
    })



# Complex type [anonymous] with content type ELEMENT_ONLY
class CTD_ANON_2 (pyxb.binding.basis.complexTypeDefinition):
    _TypeDefinition = None
    _ContentTypeTag = pyxb.binding.basis.complexTypeDefinition._CT_ELEMENT_ONLY
    _Abstract = False
    _ExpandedName = None
    _DefinitionLocation = pyxb.utils.utility.Location('/tmp/pyxbdist.RHB65sy/PyXB-1.1.5/pyxb/bundles/wssplat/schemas/wsp200607.xsd', 80, 4)
    # Base type is pyxb.binding.datatypes.anyType
    
    # Element {http://www.w3.org/2006/07/ws-policy}PolicyReference uses Python identifier PolicyReference
    __PolicyReference = pyxb.binding.content.ElementUse(pyxb.namespace.ExpandedName(Namespace, u'PolicyReference'), 'PolicyReference', '__httpwww_w3_org200607ws_policy_CTD_ANON_2_httpwww_w3_org200607ws_policyPolicyReference', True)
    __PolicyReference._DeclarationLocation = pyxb.utils.utility.Location('/tmp/pyxbdist.RHB65sy/PyXB-1.1.5/pyxb/bundles/wssplat/schemas/wsp200607.xsd', 59, 2)
    __PolicyReference._UseLocation = pyxb.utils.utility.Location('/tmp/pyxbdist.RHB65sy/PyXB-1.1.5/pyxb/bundles/wssplat/schemas/wsp200607.xsd', 81, 6)

    
    PolicyReference = property(__PolicyReference.value, __PolicyReference.set, None, None)

    
    # Element {http://www.w3.org/2006/07/ws-policy}AppliesTo uses Python identifier AppliesTo
    __AppliesTo = pyxb.binding.content.ElementUse(pyxb.namespace.ExpandedName(Namespace, u'AppliesTo'), 'AppliesTo', '__httpwww_w3_org200607ws_policy_CTD_ANON_2_httpwww_w3_org200607ws_policyAppliesTo', False)
    __AppliesTo._DeclarationLocation = pyxb.utils.utility.Location('/tmp/pyxbdist.RHB65sy/PyXB-1.1.5/pyxb/bundles/wssplat/schemas/wsp200607.xsd', 98, 2)
    __AppliesTo._UseLocation = pyxb.utils.utility.Location('/tmp/pyxbdist.RHB65sy/PyXB-1.1.5/pyxb/bundles/wssplat/schemas/wsp200607.xsd', 81, 6)

    
    AppliesTo = property(__AppliesTo.value, __AppliesTo.set, None, None)

    
    # Element {http://www.w3.org/2006/07/ws-policy}Policy uses Python identifier Policy
    __Policy = pyxb.binding.content.ElementUse(pyxb.namespace.ExpandedName(Namespace, u'Policy'), 'Policy', '__httpwww_w3_org200607ws_policy_CTD_ANON_2_httpwww_w3_org200607ws_policyPolicy', True)
    __Policy._DeclarationLocation = pyxb.utils.utility.Location('/tmp/pyxbdist.RHB65sy/PyXB-1.1.5/pyxb/bundles/wssplat/schemas/wsp200607.xsd', 30, 2)
    __Policy._UseLocation = pyxb.utils.utility.Location('/tmp/pyxbdist.RHB65sy/PyXB-1.1.5/pyxb/bundles/wssplat/schemas/wsp200607.xsd', 81, 6)

    
    Policy = property(__Policy.value, __Policy.set, None, None)

    _AttributeWildcard = pyxb.binding.content.Wildcard(process_contents=pyxb.binding.content.Wildcard.PC_lax, namespace_constraint=pyxb.binding.content.Wildcard.NC_any)
    _HasWildcardElement = True

    _ElementMap = {
        __PolicyReference.name() : __PolicyReference,
        __AppliesTo.name() : __AppliesTo,
        __Policy.name() : __Policy
    }
    _AttributeMap = {
        
    }



# Complex type [anonymous] with content type ELEMENT_ONLY
class CTD_ANON_3 (pyxb.binding.basis.complexTypeDefinition):
    _TypeDefinition = None
    _ContentTypeTag = pyxb.binding.basis.complexTypeDefinition._CT_ELEMENT_ONLY
    _Abstract = False
    _ExpandedName = None
    _DefinitionLocation = pyxb.utils.utility.Location('/tmp/pyxbdist.RHB65sy/PyXB-1.1.5/pyxb/bundles/wssplat/schemas/wsp200607.xsd', 99, 4)
    # Base type is pyxb.binding.datatypes.anyType
    _AttributeWildcard = pyxb.binding.content.Wildcard(process_contents=pyxb.binding.content.Wildcard.PC_lax, namespace_constraint=pyxb.binding.content.Wildcard.NC_any)
    _HasWildcardElement = True

    _ElementMap = {
        
    }
    _AttributeMap = {
        
    }



PolicyReference = pyxb.binding.basis.element(pyxb.namespace.ExpandedName(Namespace, u'PolicyReference'), CTD_ANON)
Namespace.addCategoryObject('elementBinding', PolicyReference.name().localName(), PolicyReference)

Policy = pyxb.binding.basis.element(pyxb.namespace.ExpandedName(Namespace, u'Policy'), CTD_ANON_)
Namespace.addCategoryObject('elementBinding', Policy.name().localName(), Policy)

PolicyAttachment = pyxb.binding.basis.element(pyxb.namespace.ExpandedName(Namespace, u'PolicyAttachment'), CTD_ANON_2)
Namespace.addCategoryObject('elementBinding', PolicyAttachment.name().localName(), PolicyAttachment)

ExactlyOne = pyxb.binding.basis.element(pyxb.namespace.ExpandedName(Namespace, u'ExactlyOne'), OperatorContentType)
Namespace.addCategoryObject('elementBinding', ExactlyOne.name().localName(), ExactlyOne)

AppliesTo = pyxb.binding.basis.element(pyxb.namespace.ExpandedName(Namespace, u'AppliesTo'), CTD_ANON_3)
Namespace.addCategoryObject('elementBinding', AppliesTo.name().localName(), AppliesTo)

All = pyxb.binding.basis.element(pyxb.namespace.ExpandedName(Namespace, u'All'), OperatorContentType)
Namespace.addCategoryObject('elementBinding', All.name().localName(), All)



OperatorContentType._AddElement(pyxb.binding.basis.element(pyxb.namespace.ExpandedName(Namespace, u'PolicyReference'), CTD_ANON, scope=OperatorContentType))

OperatorContentType._AddElement(pyxb.binding.basis.element(pyxb.namespace.ExpandedName(Namespace, u'Policy'), CTD_ANON_, scope=OperatorContentType))

OperatorContentType._AddElement(pyxb.binding.basis.element(pyxb.namespace.ExpandedName(Namespace, u'ExactlyOne'), OperatorContentType, scope=OperatorContentType))

OperatorContentType._AddElement(pyxb.binding.basis.element(pyxb.namespace.ExpandedName(Namespace, u'All'), OperatorContentType, scope=OperatorContentType))
OperatorContentType._GroupModel_ = pyxb.binding.content.GroupChoice(
    pyxb.binding.content.ParticleModel(OperatorContentType._UseForTag(pyxb.namespace.ExpandedName(Namespace, u'Policy')), min_occurs=1, max_occurs=1),
    pyxb.binding.content.ParticleModel(OperatorContentType._UseForTag(pyxb.namespace.ExpandedName(Namespace, u'All')), min_occurs=1, max_occurs=1),
    pyxb.binding.content.ParticleModel(OperatorContentType._UseForTag(pyxb.namespace.ExpandedName(Namespace, u'ExactlyOne')), min_occurs=1, max_occurs=1),
    pyxb.binding.content.ParticleModel(OperatorContentType._UseForTag(pyxb.namespace.ExpandedName(Namespace, u'PolicyReference')), min_occurs=1, max_occurs=1),
    pyxb.binding.content.ParticleModel(pyxb.binding.content.Wildcard(process_contents=pyxb.binding.content.Wildcard.PC_lax, namespace_constraint=(pyxb.binding.content.Wildcard.NC_not, u'http://www.w3.org/2006/07/ws-policy')), min_occurs=1L, max_occurs=1L)
    )
OperatorContentType._GroupModel = pyxb.binding.content.GroupSequence(
    pyxb.binding.content.ParticleModel(OperatorContentType._GroupModel_, min_occurs=0L, max_occurs=None)
    )
OperatorContentType._ContentModel = pyxb.binding.content.ParticleModel(OperatorContentType._GroupModel, min_occurs=1, max_occurs=1)


CTD_ANON_._GroupModel_ = pyxb.binding.content.GroupChoice(
    pyxb.binding.content.ParticleModel(CTD_ANON_._UseForTag(pyxb.namespace.ExpandedName(Namespace, u'Policy')), min_occurs=1, max_occurs=1),
    pyxb.binding.content.ParticleModel(CTD_ANON_._UseForTag(pyxb.namespace.ExpandedName(Namespace, u'All')), min_occurs=1, max_occurs=1),
    pyxb.binding.content.ParticleModel(CTD_ANON_._UseForTag(pyxb.namespace.ExpandedName(Namespace, u'ExactlyOne')), min_occurs=1, max_occurs=1),
    pyxb.binding.content.ParticleModel(CTD_ANON_._UseForTag(pyxb.namespace.ExpandedName(Namespace, u'PolicyReference')), min_occurs=1, max_occurs=1),
    pyxb.binding.content.ParticleModel(pyxb.binding.content.Wildcard(process_contents=pyxb.binding.content.Wildcard.PC_lax, namespace_constraint=(pyxb.binding.content.Wildcard.NC_not, u'http://www.w3.org/2006/07/ws-policy')), min_occurs=1L, max_occurs=1L)
    )
CTD_ANON_._GroupModel = pyxb.binding.content.GroupSequence(
    pyxb.binding.content.ParticleModel(CTD_ANON_._GroupModel_, min_occurs=0L, max_occurs=None)
    )
CTD_ANON_._ContentModel = pyxb.binding.content.ParticleModel(CTD_ANON_._GroupModel, min_occurs=1, max_occurs=1)



CTD_ANON_2._AddElement(pyxb.binding.basis.element(pyxb.namespace.ExpandedName(Namespace, u'PolicyReference'), CTD_ANON, scope=CTD_ANON_2))

CTD_ANON_2._AddElement(pyxb.binding.basis.element(pyxb.namespace.ExpandedName(Namespace, u'AppliesTo'), CTD_ANON_3, scope=CTD_ANON_2))

CTD_ANON_2._AddElement(pyxb.binding.basis.element(pyxb.namespace.ExpandedName(Namespace, u'Policy'), CTD_ANON_, scope=CTD_ANON_2))
CTD_ANON_2._GroupModel_ = pyxb.binding.content.GroupChoice(
    pyxb.binding.content.ParticleModel(CTD_ANON_2._UseForTag(pyxb.namespace.ExpandedName(Namespace, u'Policy')), min_occurs=1, max_occurs=1),
    pyxb.binding.content.ParticleModel(CTD_ANON_2._UseForTag(pyxb.namespace.ExpandedName(Namespace, u'PolicyReference')), min_occurs=1, max_occurs=1)
    )
CTD_ANON_2._GroupModel = pyxb.binding.content.GroupSequence(
    pyxb.binding.content.ParticleModel(CTD_ANON_2._UseForTag(pyxb.namespace.ExpandedName(Namespace, u'AppliesTo')), min_occurs=1, max_occurs=1),
    pyxb.binding.content.ParticleModel(CTD_ANON_2._GroupModel_, min_occurs=1, max_occurs=None),
    pyxb.binding.content.ParticleModel(pyxb.binding.content.Wildcard(process_contents=pyxb.binding.content.Wildcard.PC_lax, namespace_constraint=(pyxb.binding.content.Wildcard.NC_not, u'http://www.w3.org/2006/07/ws-policy')), min_occurs=0L, max_occurs=None)
    )
CTD_ANON_2._ContentModel = pyxb.binding.content.ParticleModel(CTD_ANON_2._GroupModel, min_occurs=1, max_occurs=1)


CTD_ANON_3._GroupModel = pyxb.binding.content.GroupSequence(
    pyxb.binding.content.ParticleModel(pyxb.binding.content.Wildcard(process_contents=pyxb.binding.content.Wildcard.PC_lax, namespace_constraint=pyxb.binding.content.Wildcard.NC_any), min_occurs=1L, max_occurs=None)
    )
CTD_ANON_3._ContentModel = pyxb.binding.content.ParticleModel(CTD_ANON_3._GroupModel, min_occurs=1, max_occurs=1)
