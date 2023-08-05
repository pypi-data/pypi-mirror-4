# ./pyxb/bundles/wssplat/raw/ds.py
# -*- coding: utf-8 -*-
# PyXB bindings for NM:f1c343a882e7a65fb879f4ee813309f8231f28c8
# Generated 2012-11-01 15:13:35.944923 by PyXB version 1.1.5
# Namespace http://www.w3.org/2000/09/xmldsig#

import pyxb
import pyxb.binding
import pyxb.binding.saxer
import StringIO
import pyxb.utils.utility
import pyxb.utils.domutils
import sys

# Unique identifier for bindings created at the same time
_GenerationUID = pyxb.utils.utility.UniqueIdentifier('urn:uuid:9de38c16-2460-11e2-b340-c8600024e903')

# Import bindings for namespaces imported into schema
import pyxb.binding.datatypes

Namespace = pyxb.namespace.NamespaceForURI(u'http://www.w3.org/2000/09/xmldsig#', create_if_missing=True)
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


# Atomic simple type: {http://www.w3.org/2000/09/xmldsig#}CryptoBinary
class CryptoBinary (pyxb.binding.datatypes.base64Binary):

    """An atomic simple type."""

    _ExpandedName = pyxb.namespace.ExpandedName(Namespace, u'CryptoBinary')
    _DefinitionLocation = pyxb.utils.utility.Location('/tmp/pyxbdist.RHB65sy/PyXB-1.1.5/pyxb/bundles/wssplat/schemas/ds.xsd', 36, 0)
    _Documentation = None
CryptoBinary._InitializeFacetMap()
Namespace.addCategoryObject('typeBinding', u'CryptoBinary', CryptoBinary)

# Atomic simple type: {http://www.w3.org/2000/09/xmldsig#}HMACOutputLengthType
class HMACOutputLengthType (pyxb.binding.datatypes.integer):

    """An atomic simple type."""

    _ExpandedName = pyxb.namespace.ExpandedName(Namespace, u'HMACOutputLengthType')
    _DefinitionLocation = pyxb.utils.utility.Location('/tmp/pyxbdist.RHB65sy/PyXB-1.1.5/pyxb/bundles/wssplat/schemas/ds.xsd', 283, 0)
    _Documentation = None
HMACOutputLengthType._InitializeFacetMap()
Namespace.addCategoryObject('typeBinding', u'HMACOutputLengthType', HMACOutputLengthType)

# Atomic simple type: {http://www.w3.org/2000/09/xmldsig#}DigestValueType
class DigestValueType (pyxb.binding.datatypes.base64Binary):

    """An atomic simple type."""

    _ExpandedName = pyxb.namespace.ExpandedName(Namespace, u'DigestValueType')
    _DefinitionLocation = pyxb.utils.utility.Location('/tmp/pyxbdist.RHB65sy/PyXB-1.1.5/pyxb/bundles/wssplat/schemas/ds.xsd', 136, 0)
    _Documentation = None
DigestValueType._InitializeFacetMap()
Namespace.addCategoryObject('typeBinding', u'DigestValueType', DigestValueType)

# Complex type {http://www.w3.org/2000/09/xmldsig#}DSAKeyValueType with content type ELEMENT_ONLY
class DSAKeyValueType (pyxb.binding.basis.complexTypeDefinition):
    _TypeDefinition = None
    _ContentTypeTag = pyxb.binding.basis.complexTypeDefinition._CT_ELEMENT_ONLY
    _Abstract = False
    _ExpandedName = pyxb.namespace.ExpandedName(Namespace, u'DSAKeyValueType')
    _DefinitionLocation = pyxb.utils.utility.Location('/tmp/pyxbdist.RHB65sy/PyXB-1.1.5/pyxb/bundles/wssplat/schemas/ds.xsd', 290, 0)
    # Base type is pyxb.binding.datatypes.anyType
    
    # Element {http://www.w3.org/2000/09/xmldsig#}P uses Python identifier P
    __P = pyxb.binding.content.ElementUse(pyxb.namespace.ExpandedName(Namespace, u'P'), 'P', '__httpwww_w3_org200009xmldsig_DSAKeyValueType_httpwww_w3_org200009xmldsigP', False)
    __P._DeclarationLocation = pyxb.utils.utility.Location('/tmp/pyxbdist.RHB65sy/PyXB-1.1.5/pyxb/bundles/wssplat/schemas/ds.xsd', 293, 6)
    __P._UseLocation = pyxb.utils.utility.Location('/tmp/pyxbdist.RHB65sy/PyXB-1.1.5/pyxb/bundles/wssplat/schemas/ds.xsd', 291, 2)

    
    P = property(__P.value, __P.set, None, None)

    
    # Element {http://www.w3.org/2000/09/xmldsig#}J uses Python identifier J
    __J = pyxb.binding.content.ElementUse(pyxb.namespace.ExpandedName(Namespace, u'J'), 'J', '__httpwww_w3_org200009xmldsig_DSAKeyValueType_httpwww_w3_org200009xmldsigJ', False)
    __J._DeclarationLocation = pyxb.utils.utility.Location('/tmp/pyxbdist.RHB65sy/PyXB-1.1.5/pyxb/bundles/wssplat/schemas/ds.xsd', 298, 4)
    __J._UseLocation = pyxb.utils.utility.Location('/tmp/pyxbdist.RHB65sy/PyXB-1.1.5/pyxb/bundles/wssplat/schemas/ds.xsd', 291, 2)

    
    J = property(__J.value, __J.set, None, None)

    
    # Element {http://www.w3.org/2000/09/xmldsig#}Q uses Python identifier Q
    __Q = pyxb.binding.content.ElementUse(pyxb.namespace.ExpandedName(Namespace, u'Q'), 'Q', '__httpwww_w3_org200009xmldsig_DSAKeyValueType_httpwww_w3_org200009xmldsigQ', False)
    __Q._DeclarationLocation = pyxb.utils.utility.Location('/tmp/pyxbdist.RHB65sy/PyXB-1.1.5/pyxb/bundles/wssplat/schemas/ds.xsd', 294, 6)
    __Q._UseLocation = pyxb.utils.utility.Location('/tmp/pyxbdist.RHB65sy/PyXB-1.1.5/pyxb/bundles/wssplat/schemas/ds.xsd', 291, 2)

    
    Q = property(__Q.value, __Q.set, None, None)

    
    # Element {http://www.w3.org/2000/09/xmldsig#}G uses Python identifier G
    __G = pyxb.binding.content.ElementUse(pyxb.namespace.ExpandedName(Namespace, u'G'), 'G', '__httpwww_w3_org200009xmldsig_DSAKeyValueType_httpwww_w3_org200009xmldsigG', False)
    __G._DeclarationLocation = pyxb.utils.utility.Location('/tmp/pyxbdist.RHB65sy/PyXB-1.1.5/pyxb/bundles/wssplat/schemas/ds.xsd', 296, 4)
    __G._UseLocation = pyxb.utils.utility.Location('/tmp/pyxbdist.RHB65sy/PyXB-1.1.5/pyxb/bundles/wssplat/schemas/ds.xsd', 291, 2)

    
    G = property(__G.value, __G.set, None, None)

    
    # Element {http://www.w3.org/2000/09/xmldsig#}Seed uses Python identifier Seed
    __Seed = pyxb.binding.content.ElementUse(pyxb.namespace.ExpandedName(Namespace, u'Seed'), 'Seed', '__httpwww_w3_org200009xmldsig_DSAKeyValueType_httpwww_w3_org200009xmldsigSeed', False)
    __Seed._DeclarationLocation = pyxb.utils.utility.Location('/tmp/pyxbdist.RHB65sy/PyXB-1.1.5/pyxb/bundles/wssplat/schemas/ds.xsd', 300, 6)
    __Seed._UseLocation = pyxb.utils.utility.Location('/tmp/pyxbdist.RHB65sy/PyXB-1.1.5/pyxb/bundles/wssplat/schemas/ds.xsd', 291, 2)

    
    Seed = property(__Seed.value, __Seed.set, None, None)

    
    # Element {http://www.w3.org/2000/09/xmldsig#}Y uses Python identifier Y
    __Y = pyxb.binding.content.ElementUse(pyxb.namespace.ExpandedName(Namespace, u'Y'), 'Y', '__httpwww_w3_org200009xmldsig_DSAKeyValueType_httpwww_w3_org200009xmldsigY', False)
    __Y._DeclarationLocation = pyxb.utils.utility.Location('/tmp/pyxbdist.RHB65sy/PyXB-1.1.5/pyxb/bundles/wssplat/schemas/ds.xsd', 297, 4)
    __Y._UseLocation = pyxb.utils.utility.Location('/tmp/pyxbdist.RHB65sy/PyXB-1.1.5/pyxb/bundles/wssplat/schemas/ds.xsd', 291, 2)

    
    Y = property(__Y.value, __Y.set, None, None)

    
    # Element {http://www.w3.org/2000/09/xmldsig#}PgenCounter uses Python identifier PgenCounter
    __PgenCounter = pyxb.binding.content.ElementUse(pyxb.namespace.ExpandedName(Namespace, u'PgenCounter'), 'PgenCounter', '__httpwww_w3_org200009xmldsig_DSAKeyValueType_httpwww_w3_org200009xmldsigPgenCounter', False)
    __PgenCounter._DeclarationLocation = pyxb.utils.utility.Location('/tmp/pyxbdist.RHB65sy/PyXB-1.1.5/pyxb/bundles/wssplat/schemas/ds.xsd', 301, 6)
    __PgenCounter._UseLocation = pyxb.utils.utility.Location('/tmp/pyxbdist.RHB65sy/PyXB-1.1.5/pyxb/bundles/wssplat/schemas/ds.xsd', 291, 2)

    
    PgenCounter = property(__PgenCounter.value, __PgenCounter.set, None, None)


    _ElementMap = {
        __P.name() : __P,
        __J.name() : __J,
        __Q.name() : __Q,
        __G.name() : __G,
        __Seed.name() : __Seed,
        __Y.name() : __Y,
        __PgenCounter.name() : __PgenCounter
    }
    _AttributeMap = {
        
    }
Namespace.addCategoryObject('typeBinding', u'DSAKeyValueType', DSAKeyValueType)


# Complex type {http://www.w3.org/2000/09/xmldsig#}CanonicalizationMethodType with content type MIXED
class CanonicalizationMethodType (pyxb.binding.basis.complexTypeDefinition):
    _TypeDefinition = None
    _ContentTypeTag = pyxb.binding.basis.complexTypeDefinition._CT_MIXED
    _Abstract = False
    _ExpandedName = pyxb.namespace.ExpandedName(Namespace, u'CanonicalizationMethodType')
    _DefinitionLocation = pyxb.utils.utility.Location('/tmp/pyxbdist.RHB65sy/PyXB-1.1.5/pyxb/bundles/wssplat/schemas/ds.xsd', 76, 2)
    # Base type is pyxb.binding.datatypes.anyType
    
    # Attribute Algorithm uses Python identifier Algorithm
    __Algorithm = pyxb.binding.content.AttributeUse(pyxb.namespace.ExpandedName(None, u'Algorithm'), 'Algorithm', '__httpwww_w3_org200009xmldsig_CanonicalizationMethodType_Algorithm', pyxb.binding.datatypes.anyURI, required=True)
    __Algorithm._DeclarationLocation = pyxb.utils.utility.Location('/tmp/pyxbdist.RHB65sy/PyXB-1.1.5/pyxb/bundles/wssplat/schemas/ds.xsd', 81, 4)
    __Algorithm._UseLocation = pyxb.utils.utility.Location('/tmp/pyxbdist.RHB65sy/PyXB-1.1.5/pyxb/bundles/wssplat/schemas/ds.xsd', 81, 4)
    
    Algorithm = property(__Algorithm.value, __Algorithm.set, None, None)

    _HasWildcardElement = True

    _ElementMap = {
        
    }
    _AttributeMap = {
        __Algorithm.name() : __Algorithm
    }
Namespace.addCategoryObject('typeBinding', u'CanonicalizationMethodType', CanonicalizationMethodType)


# Complex type {http://www.w3.org/2000/09/xmldsig#}TransformType with content type MIXED
class TransformType (pyxb.binding.basis.complexTypeDefinition):
    _TypeDefinition = None
    _ContentTypeTag = pyxb.binding.basis.complexTypeDefinition._CT_MIXED
    _Abstract = False
    _ExpandedName = pyxb.namespace.ExpandedName(Namespace, u'TransformType')
    _DefinitionLocation = pyxb.utils.utility.Location('/tmp/pyxbdist.RHB65sy/PyXB-1.1.5/pyxb/bundles/wssplat/schemas/ds.xsd', 116, 2)
    # Base type is pyxb.binding.datatypes.anyType
    
    # Element {http://www.w3.org/2000/09/xmldsig#}XPath uses Python identifier XPath
    __XPath = pyxb.binding.content.ElementUse(pyxb.namespace.ExpandedName(Namespace, u'XPath'), 'XPath', '__httpwww_w3_org200009xmldsig_TransformType_httpwww_w3_org200009xmldsigXPath', True)
    __XPath._DeclarationLocation = pyxb.utils.utility.Location('/tmp/pyxbdist.RHB65sy/PyXB-1.1.5/pyxb/bundles/wssplat/schemas/ds.xsd', 120, 6)
    __XPath._UseLocation = pyxb.utils.utility.Location('/tmp/pyxbdist.RHB65sy/PyXB-1.1.5/pyxb/bundles/wssplat/schemas/ds.xsd', 117, 4)

    
    XPath = property(__XPath.value, __XPath.set, None, None)

    
    # Attribute Algorithm uses Python identifier Algorithm
    __Algorithm = pyxb.binding.content.AttributeUse(pyxb.namespace.ExpandedName(None, u'Algorithm'), 'Algorithm', '__httpwww_w3_org200009xmldsig_TransformType_Algorithm', pyxb.binding.datatypes.anyURI, required=True)
    __Algorithm._DeclarationLocation = pyxb.utils.utility.Location('/tmp/pyxbdist.RHB65sy/PyXB-1.1.5/pyxb/bundles/wssplat/schemas/ds.xsd', 122, 4)
    __Algorithm._UseLocation = pyxb.utils.utility.Location('/tmp/pyxbdist.RHB65sy/PyXB-1.1.5/pyxb/bundles/wssplat/schemas/ds.xsd', 122, 4)
    
    Algorithm = property(__Algorithm.value, __Algorithm.set, None, None)

    _HasWildcardElement = True

    _ElementMap = {
        __XPath.name() : __XPath
    }
    _AttributeMap = {
        __Algorithm.name() : __Algorithm
    }
Namespace.addCategoryObject('typeBinding', u'TransformType', TransformType)


# Complex type {http://www.w3.org/2000/09/xmldsig#}PGPDataType with content type ELEMENT_ONLY
class PGPDataType (pyxb.binding.basis.complexTypeDefinition):
    _TypeDefinition = None
    _ContentTypeTag = pyxb.binding.basis.complexTypeDefinition._CT_ELEMENT_ONLY
    _Abstract = False
    _ExpandedName = pyxb.namespace.ExpandedName(Namespace, u'PGPDataType')
    _DefinitionLocation = pyxb.utils.utility.Location('/tmp/pyxbdist.RHB65sy/PyXB-1.1.5/pyxb/bundles/wssplat/schemas/ds.xsd', 209, 0)
    # Base type is pyxb.binding.datatypes.anyType
    
    # Element {http://www.w3.org/2000/09/xmldsig#}PGPKeyID uses Python identifier PGPKeyID
    __PGPKeyID = pyxb.binding.content.ElementUse(pyxb.namespace.ExpandedName(Namespace, u'PGPKeyID'), 'PGPKeyID', '__httpwww_w3_org200009xmldsig_PGPDataType_httpwww_w3_org200009xmldsigPGPKeyID', False)
    __PGPKeyID._DeclarationLocation = pyxb.utils.utility.Location('/tmp/pyxbdist.RHB65sy/PyXB-1.1.5/pyxb/bundles/wssplat/schemas/ds.xsd', 212, 6)
    __PGPKeyID._UseLocation = pyxb.utils.utility.Location('/tmp/pyxbdist.RHB65sy/PyXB-1.1.5/pyxb/bundles/wssplat/schemas/ds.xsd', 210, 2)

    
    PGPKeyID = property(__PGPKeyID.value, __PGPKeyID.set, None, None)

    
    # Element {http://www.w3.org/2000/09/xmldsig#}PGPKeyPacket uses Python identifier PGPKeyPacket
    __PGPKeyPacket = pyxb.binding.content.ElementUse(pyxb.namespace.ExpandedName(Namespace, u'PGPKeyPacket'), 'PGPKeyPacket', '__httpwww_w3_org200009xmldsig_PGPDataType_httpwww_w3_org200009xmldsigPGPKeyPacket', False)
    __PGPKeyPacket._DeclarationLocation = pyxb.utils.utility.Location('/tmp/pyxbdist.RHB65sy/PyXB-1.1.5/pyxb/bundles/wssplat/schemas/ds.xsd', 213, 6)
    __PGPKeyPacket._UseLocation = pyxb.utils.utility.Location('/tmp/pyxbdist.RHB65sy/PyXB-1.1.5/pyxb/bundles/wssplat/schemas/ds.xsd', 210, 2)

    
    PGPKeyPacket = property(__PGPKeyPacket.value, __PGPKeyPacket.set, None, None)

    _HasWildcardElement = True

    _ElementMap = {
        __PGPKeyID.name() : __PGPKeyID,
        __PGPKeyPacket.name() : __PGPKeyPacket
    }
    _AttributeMap = {
        
    }
Namespace.addCategoryObject('typeBinding', u'PGPDataType', PGPDataType)


# Complex type {http://www.w3.org/2000/09/xmldsig#}ReferenceType with content type ELEMENT_ONLY
class ReferenceType (pyxb.binding.basis.complexTypeDefinition):
    _TypeDefinition = None
    _ContentTypeTag = pyxb.binding.basis.complexTypeDefinition._CT_ELEMENT_ONLY
    _Abstract = False
    _ExpandedName = pyxb.namespace.ExpandedName(Namespace, u'ReferenceType')
    _DefinitionLocation = pyxb.utils.utility.Location('/tmp/pyxbdist.RHB65sy/PyXB-1.1.5/pyxb/bundles/wssplat/schemas/ds.xsd', 97, 0)
    # Base type is pyxb.binding.datatypes.anyType
    
    # Element {http://www.w3.org/2000/09/xmldsig#}DigestMethod uses Python identifier DigestMethod
    __DigestMethod = pyxb.binding.content.ElementUse(pyxb.namespace.ExpandedName(Namespace, u'DigestMethod'), 'DigestMethod', '__httpwww_w3_org200009xmldsig_ReferenceType_httpwww_w3_org200009xmldsigDigestMethod', False)
    __DigestMethod._DeclarationLocation = pyxb.utils.utility.Location('/tmp/pyxbdist.RHB65sy/PyXB-1.1.5/pyxb/bundles/wssplat/schemas/ds.xsd', 127, 0)
    __DigestMethod._UseLocation = pyxb.utils.utility.Location('/tmp/pyxbdist.RHB65sy/PyXB-1.1.5/pyxb/bundles/wssplat/schemas/ds.xsd', 98, 2)

    
    DigestMethod = property(__DigestMethod.value, __DigestMethod.set, None, None)

    
    # Element {http://www.w3.org/2000/09/xmldsig#}DigestValue uses Python identifier DigestValue
    __DigestValue = pyxb.binding.content.ElementUse(pyxb.namespace.ExpandedName(Namespace, u'DigestValue'), 'DigestValue', '__httpwww_w3_org200009xmldsig_ReferenceType_httpwww_w3_org200009xmldsigDigestValue', False)
    __DigestValue._DeclarationLocation = pyxb.utils.utility.Location('/tmp/pyxbdist.RHB65sy/PyXB-1.1.5/pyxb/bundles/wssplat/schemas/ds.xsd', 135, 0)
    __DigestValue._UseLocation = pyxb.utils.utility.Location('/tmp/pyxbdist.RHB65sy/PyXB-1.1.5/pyxb/bundles/wssplat/schemas/ds.xsd', 98, 2)

    
    DigestValue = property(__DigestValue.value, __DigestValue.set, None, None)

    
    # Element {http://www.w3.org/2000/09/xmldsig#}Transforms uses Python identifier Transforms
    __Transforms = pyxb.binding.content.ElementUse(pyxb.namespace.ExpandedName(Namespace, u'Transforms'), 'Transforms', '__httpwww_w3_org200009xmldsig_ReferenceType_httpwww_w3_org200009xmldsigTransforms', False)
    __Transforms._DeclarationLocation = pyxb.utils.utility.Location('/tmp/pyxbdist.RHB65sy/PyXB-1.1.5/pyxb/bundles/wssplat/schemas/ds.xsd', 108, 2)
    __Transforms._UseLocation = pyxb.utils.utility.Location('/tmp/pyxbdist.RHB65sy/PyXB-1.1.5/pyxb/bundles/wssplat/schemas/ds.xsd', 98, 2)

    
    Transforms = property(__Transforms.value, __Transforms.set, None, None)

    
    # Attribute Type uses Python identifier Type
    __Type = pyxb.binding.content.AttributeUse(pyxb.namespace.ExpandedName(None, u'Type'), 'Type', '__httpwww_w3_org200009xmldsig_ReferenceType_Type', pyxb.binding.datatypes.anyURI)
    __Type._DeclarationLocation = pyxb.utils.utility.Location('/tmp/pyxbdist.RHB65sy/PyXB-1.1.5/pyxb/bundles/wssplat/schemas/ds.xsd', 105, 2)
    __Type._UseLocation = pyxb.utils.utility.Location('/tmp/pyxbdist.RHB65sy/PyXB-1.1.5/pyxb/bundles/wssplat/schemas/ds.xsd', 105, 2)
    
    Type = property(__Type.value, __Type.set, None, None)

    
    # Attribute URI uses Python identifier URI
    __URI = pyxb.binding.content.AttributeUse(pyxb.namespace.ExpandedName(None, u'URI'), 'URI', '__httpwww_w3_org200009xmldsig_ReferenceType_URI', pyxb.binding.datatypes.anyURI)
    __URI._DeclarationLocation = pyxb.utils.utility.Location('/tmp/pyxbdist.RHB65sy/PyXB-1.1.5/pyxb/bundles/wssplat/schemas/ds.xsd', 104, 2)
    __URI._UseLocation = pyxb.utils.utility.Location('/tmp/pyxbdist.RHB65sy/PyXB-1.1.5/pyxb/bundles/wssplat/schemas/ds.xsd', 104, 2)
    
    URI = property(__URI.value, __URI.set, None, None)

    
    # Attribute Id uses Python identifier Id
    __Id = pyxb.binding.content.AttributeUse(pyxb.namespace.ExpandedName(None, u'Id'), 'Id', '__httpwww_w3_org200009xmldsig_ReferenceType_Id', pyxb.binding.datatypes.ID)
    __Id._DeclarationLocation = pyxb.utils.utility.Location('/tmp/pyxbdist.RHB65sy/PyXB-1.1.5/pyxb/bundles/wssplat/schemas/ds.xsd', 103, 2)
    __Id._UseLocation = pyxb.utils.utility.Location('/tmp/pyxbdist.RHB65sy/PyXB-1.1.5/pyxb/bundles/wssplat/schemas/ds.xsd', 103, 2)
    
    Id = property(__Id.value, __Id.set, None, None)


    _ElementMap = {
        __DigestMethod.name() : __DigestMethod,
        __DigestValue.name() : __DigestValue,
        __Transforms.name() : __Transforms
    }
    _AttributeMap = {
        __Type.name() : __Type,
        __URI.name() : __URI,
        __Id.name() : __Id
    }
Namespace.addCategoryObject('typeBinding', u'ReferenceType', ReferenceType)


# Complex type {http://www.w3.org/2000/09/xmldsig#}SPKIDataType with content type ELEMENT_ONLY
class SPKIDataType (pyxb.binding.basis.complexTypeDefinition):
    _TypeDefinition = None
    _ContentTypeTag = pyxb.binding.basis.complexTypeDefinition._CT_ELEMENT_ONLY
    _Abstract = False
    _ExpandedName = pyxb.namespace.ExpandedName(Namespace, u'SPKIDataType')
    _DefinitionLocation = pyxb.utils.utility.Location('/tmp/pyxbdist.RHB65sy/PyXB-1.1.5/pyxb/bundles/wssplat/schemas/ds.xsd', 230, 0)
    # Base type is pyxb.binding.datatypes.anyType
    
    # Element {http://www.w3.org/2000/09/xmldsig#}SPKISexp uses Python identifier SPKISexp
    __SPKISexp = pyxb.binding.content.ElementUse(pyxb.namespace.ExpandedName(Namespace, u'SPKISexp'), 'SPKISexp', '__httpwww_w3_org200009xmldsig_SPKIDataType_httpwww_w3_org200009xmldsigSPKISexp', True)
    __SPKISexp._DeclarationLocation = pyxb.utils.utility.Location('/tmp/pyxbdist.RHB65sy/PyXB-1.1.5/pyxb/bundles/wssplat/schemas/ds.xsd', 232, 4)
    __SPKISexp._UseLocation = pyxb.utils.utility.Location('/tmp/pyxbdist.RHB65sy/PyXB-1.1.5/pyxb/bundles/wssplat/schemas/ds.xsd', 231, 2)

    
    SPKISexp = property(__SPKISexp.value, __SPKISexp.set, None, None)

    _HasWildcardElement = True

    _ElementMap = {
        __SPKISexp.name() : __SPKISexp
    }
    _AttributeMap = {
        
    }
Namespace.addCategoryObject('typeBinding', u'SPKIDataType', SPKIDataType)


# Complex type {http://www.w3.org/2000/09/xmldsig#}RSAKeyValueType with content type ELEMENT_ONLY
class RSAKeyValueType (pyxb.binding.basis.complexTypeDefinition):
    _TypeDefinition = None
    _ContentTypeTag = pyxb.binding.basis.complexTypeDefinition._CT_ELEMENT_ONLY
    _Abstract = False
    _ExpandedName = pyxb.namespace.ExpandedName(Namespace, u'RSAKeyValueType')
    _DefinitionLocation = pyxb.utils.utility.Location('/tmp/pyxbdist.RHB65sy/PyXB-1.1.5/pyxb/bundles/wssplat/schemas/ds.xsd', 307, 0)
    # Base type is pyxb.binding.datatypes.anyType
    
    # Element {http://www.w3.org/2000/09/xmldsig#}Exponent uses Python identifier Exponent
    __Exponent = pyxb.binding.content.ElementUse(pyxb.namespace.ExpandedName(Namespace, u'Exponent'), 'Exponent', '__httpwww_w3_org200009xmldsig_RSAKeyValueType_httpwww_w3_org200009xmldsigExponent', False)
    __Exponent._DeclarationLocation = pyxb.utils.utility.Location('/tmp/pyxbdist.RHB65sy/PyXB-1.1.5/pyxb/bundles/wssplat/schemas/ds.xsd', 310, 4)
    __Exponent._UseLocation = pyxb.utils.utility.Location('/tmp/pyxbdist.RHB65sy/PyXB-1.1.5/pyxb/bundles/wssplat/schemas/ds.xsd', 308, 2)

    
    Exponent = property(__Exponent.value, __Exponent.set, None, None)

    
    # Element {http://www.w3.org/2000/09/xmldsig#}Modulus uses Python identifier Modulus
    __Modulus = pyxb.binding.content.ElementUse(pyxb.namespace.ExpandedName(Namespace, u'Modulus'), 'Modulus', '__httpwww_w3_org200009xmldsig_RSAKeyValueType_httpwww_w3_org200009xmldsigModulus', False)
    __Modulus._DeclarationLocation = pyxb.utils.utility.Location('/tmp/pyxbdist.RHB65sy/PyXB-1.1.5/pyxb/bundles/wssplat/schemas/ds.xsd', 309, 4)
    __Modulus._UseLocation = pyxb.utils.utility.Location('/tmp/pyxbdist.RHB65sy/PyXB-1.1.5/pyxb/bundles/wssplat/schemas/ds.xsd', 308, 2)

    
    Modulus = property(__Modulus.value, __Modulus.set, None, None)


    _ElementMap = {
        __Exponent.name() : __Exponent,
        __Modulus.name() : __Modulus
    }
    _AttributeMap = {
        
    }
Namespace.addCategoryObject('typeBinding', u'RSAKeyValueType', RSAKeyValueType)


# Complex type {http://www.w3.org/2000/09/xmldsig#}KeyInfoType with content type MIXED
class KeyInfoType (pyxb.binding.basis.complexTypeDefinition):
    _TypeDefinition = None
    _ContentTypeTag = pyxb.binding.basis.complexTypeDefinition._CT_MIXED
    _Abstract = False
    _ExpandedName = pyxb.namespace.ExpandedName(Namespace, u'KeyInfoType')
    _DefinitionLocation = pyxb.utils.utility.Location('/tmp/pyxbdist.RHB65sy/PyXB-1.1.5/pyxb/bundles/wssplat/schemas/ds.xsd', 145, 0)
    # Base type is pyxb.binding.datatypes.anyType
    
    # Element {http://www.w3.org/2000/09/xmldsig#}PGPData uses Python identifier PGPData
    __PGPData = pyxb.binding.content.ElementUse(pyxb.namespace.ExpandedName(Namespace, u'PGPData'), 'PGPData', '__httpwww_w3_org200009xmldsig_KeyInfoType_httpwww_w3_org200009xmldsigPGPData', True)
    __PGPData._DeclarationLocation = pyxb.utils.utility.Location('/tmp/pyxbdist.RHB65sy/PyXB-1.1.5/pyxb/bundles/wssplat/schemas/ds.xsd', 208, 0)
    __PGPData._UseLocation = pyxb.utils.utility.Location('/tmp/pyxbdist.RHB65sy/PyXB-1.1.5/pyxb/bundles/wssplat/schemas/ds.xsd', 146, 2)

    
    PGPData = property(__PGPData.value, __PGPData.set, None, None)

    
    # Element {http://www.w3.org/2000/09/xmldsig#}RetrievalMethod uses Python identifier RetrievalMethod
    __RetrievalMethod = pyxb.binding.content.ElementUse(pyxb.namespace.ExpandedName(Namespace, u'RetrievalMethod'), 'RetrievalMethod', '__httpwww_w3_org200009xmldsig_KeyInfoType_httpwww_w3_org200009xmldsigRetrievalMethod', True)
    __RetrievalMethod._DeclarationLocation = pyxb.utils.utility.Location('/tmp/pyxbdist.RHB65sy/PyXB-1.1.5/pyxb/bundles/wssplat/schemas/ds.xsd', 172, 2)
    __RetrievalMethod._UseLocation = pyxb.utils.utility.Location('/tmp/pyxbdist.RHB65sy/PyXB-1.1.5/pyxb/bundles/wssplat/schemas/ds.xsd', 146, 2)

    
    RetrievalMethod = property(__RetrievalMethod.value, __RetrievalMethod.set, None, None)

    
    # Element {http://www.w3.org/2000/09/xmldsig#}SPKIData uses Python identifier SPKIData
    __SPKIData = pyxb.binding.content.ElementUse(pyxb.namespace.ExpandedName(Namespace, u'SPKIData'), 'SPKIData', '__httpwww_w3_org200009xmldsig_KeyInfoType_httpwww_w3_org200009xmldsigSPKIData', True)
    __SPKIData._DeclarationLocation = pyxb.utils.utility.Location('/tmp/pyxbdist.RHB65sy/PyXB-1.1.5/pyxb/bundles/wssplat/schemas/ds.xsd', 229, 0)
    __SPKIData._UseLocation = pyxb.utils.utility.Location('/tmp/pyxbdist.RHB65sy/PyXB-1.1.5/pyxb/bundles/wssplat/schemas/ds.xsd', 146, 2)

    
    SPKIData = property(__SPKIData.value, __SPKIData.set, None, None)

    
    # Element {http://www.w3.org/2000/09/xmldsig#}KeyName uses Python identifier KeyName
    __KeyName = pyxb.binding.content.ElementUse(pyxb.namespace.ExpandedName(Namespace, u'KeyName'), 'KeyName', '__httpwww_w3_org200009xmldsig_KeyInfoType_httpwww_w3_org200009xmldsigKeyName', True)
    __KeyName._DeclarationLocation = pyxb.utils.utility.Location('/tmp/pyxbdist.RHB65sy/PyXB-1.1.5/pyxb/bundles/wssplat/schemas/ds.xsd', 160, 2)
    __KeyName._UseLocation = pyxb.utils.utility.Location('/tmp/pyxbdist.RHB65sy/PyXB-1.1.5/pyxb/bundles/wssplat/schemas/ds.xsd', 146, 2)

    
    KeyName = property(__KeyName.value, __KeyName.set, None, None)

    
    # Element {http://www.w3.org/2000/09/xmldsig#}X509Data uses Python identifier X509Data
    __X509Data = pyxb.binding.content.ElementUse(pyxb.namespace.ExpandedName(Namespace, u'X509Data'), 'X509Data', '__httpwww_w3_org200009xmldsig_KeyInfoType_httpwww_w3_org200009xmldsigX509Data', True)
    __X509Data._DeclarationLocation = pyxb.utils.utility.Location('/tmp/pyxbdist.RHB65sy/PyXB-1.1.5/pyxb/bundles/wssplat/schemas/ds.xsd', 183, 0)
    __X509Data._UseLocation = pyxb.utils.utility.Location('/tmp/pyxbdist.RHB65sy/PyXB-1.1.5/pyxb/bundles/wssplat/schemas/ds.xsd', 146, 2)

    
    X509Data = property(__X509Data.value, __X509Data.set, None, None)

    
    # Element {http://www.w3.org/2000/09/xmldsig#}MgmtData uses Python identifier MgmtData
    __MgmtData = pyxb.binding.content.ElementUse(pyxb.namespace.ExpandedName(Namespace, u'MgmtData'), 'MgmtData', '__httpwww_w3_org200009xmldsig_KeyInfoType_httpwww_w3_org200009xmldsigMgmtData', True)
    __MgmtData._DeclarationLocation = pyxb.utils.utility.Location('/tmp/pyxbdist.RHB65sy/PyXB-1.1.5/pyxb/bundles/wssplat/schemas/ds.xsd', 161, 2)
    __MgmtData._UseLocation = pyxb.utils.utility.Location('/tmp/pyxbdist.RHB65sy/PyXB-1.1.5/pyxb/bundles/wssplat/schemas/ds.xsd', 146, 2)

    
    MgmtData = property(__MgmtData.value, __MgmtData.set, None, None)

    
    # Element {http://www.w3.org/2000/09/xmldsig#}KeyValue uses Python identifier KeyValue
    __KeyValue = pyxb.binding.content.ElementUse(pyxb.namespace.ExpandedName(Namespace, u'KeyValue'), 'KeyValue', '__httpwww_w3_org200009xmldsig_KeyInfoType_httpwww_w3_org200009xmldsigKeyValue', True)
    __KeyValue._DeclarationLocation = pyxb.utils.utility.Location('/tmp/pyxbdist.RHB65sy/PyXB-1.1.5/pyxb/bundles/wssplat/schemas/ds.xsd', 163, 2)
    __KeyValue._UseLocation = pyxb.utils.utility.Location('/tmp/pyxbdist.RHB65sy/PyXB-1.1.5/pyxb/bundles/wssplat/schemas/ds.xsd', 146, 2)

    
    KeyValue = property(__KeyValue.value, __KeyValue.set, None, None)

    
    # Attribute Id uses Python identifier Id
    __Id = pyxb.binding.content.AttributeUse(pyxb.namespace.ExpandedName(None, u'Id'), 'Id', '__httpwww_w3_org200009xmldsig_KeyInfoType_Id', pyxb.binding.datatypes.ID)
    __Id._DeclarationLocation = pyxb.utils.utility.Location('/tmp/pyxbdist.RHB65sy/PyXB-1.1.5/pyxb/bundles/wssplat/schemas/ds.xsd', 157, 2)
    __Id._UseLocation = pyxb.utils.utility.Location('/tmp/pyxbdist.RHB65sy/PyXB-1.1.5/pyxb/bundles/wssplat/schemas/ds.xsd', 157, 2)
    
    Id = property(__Id.value, __Id.set, None, None)

    _HasWildcardElement = True

    _ElementMap = {
        __PGPData.name() : __PGPData,
        __RetrievalMethod.name() : __RetrievalMethod,
        __SPKIData.name() : __SPKIData,
        __KeyName.name() : __KeyName,
        __X509Data.name() : __X509Data,
        __MgmtData.name() : __MgmtData,
        __KeyValue.name() : __KeyValue
    }
    _AttributeMap = {
        __Id.name() : __Id
    }
Namespace.addCategoryObject('typeBinding', u'KeyInfoType', KeyInfoType)


# Complex type {http://www.w3.org/2000/09/xmldsig#}X509DataType with content type ELEMENT_ONLY
class X509DataType (pyxb.binding.basis.complexTypeDefinition):
    _TypeDefinition = None
    _ContentTypeTag = pyxb.binding.basis.complexTypeDefinition._CT_ELEMENT_ONLY
    _Abstract = False
    _ExpandedName = pyxb.namespace.ExpandedName(Namespace, u'X509DataType')
    _DefinitionLocation = pyxb.utils.utility.Location('/tmp/pyxbdist.RHB65sy/PyXB-1.1.5/pyxb/bundles/wssplat/schemas/ds.xsd', 184, 0)
    # Base type is pyxb.binding.datatypes.anyType
    
    # Element {http://www.w3.org/2000/09/xmldsig#}X509IssuerSerial uses Python identifier X509IssuerSerial
    __X509IssuerSerial = pyxb.binding.content.ElementUse(pyxb.namespace.ExpandedName(Namespace, u'X509IssuerSerial'), 'X509IssuerSerial', '__httpwww_w3_org200009xmldsig_X509DataType_httpwww_w3_org200009xmldsigX509IssuerSerial', True)
    __X509IssuerSerial._DeclarationLocation = pyxb.utils.utility.Location('/tmp/pyxbdist.RHB65sy/PyXB-1.1.5/pyxb/bundles/wssplat/schemas/ds.xsd', 187, 6)
    __X509IssuerSerial._UseLocation = pyxb.utils.utility.Location('/tmp/pyxbdist.RHB65sy/PyXB-1.1.5/pyxb/bundles/wssplat/schemas/ds.xsd', 185, 2)

    
    X509IssuerSerial = property(__X509IssuerSerial.value, __X509IssuerSerial.set, None, None)

    
    # Element {http://www.w3.org/2000/09/xmldsig#}X509SKI uses Python identifier X509SKI
    __X509SKI = pyxb.binding.content.ElementUse(pyxb.namespace.ExpandedName(Namespace, u'X509SKI'), 'X509SKI', '__httpwww_w3_org200009xmldsig_X509DataType_httpwww_w3_org200009xmldsigX509SKI', True)
    __X509SKI._DeclarationLocation = pyxb.utils.utility.Location('/tmp/pyxbdist.RHB65sy/PyXB-1.1.5/pyxb/bundles/wssplat/schemas/ds.xsd', 188, 6)
    __X509SKI._UseLocation = pyxb.utils.utility.Location('/tmp/pyxbdist.RHB65sy/PyXB-1.1.5/pyxb/bundles/wssplat/schemas/ds.xsd', 185, 2)

    
    X509SKI = property(__X509SKI.value, __X509SKI.set, None, None)

    
    # Element {http://www.w3.org/2000/09/xmldsig#}X509SubjectName uses Python identifier X509SubjectName
    __X509SubjectName = pyxb.binding.content.ElementUse(pyxb.namespace.ExpandedName(Namespace, u'X509SubjectName'), 'X509SubjectName', '__httpwww_w3_org200009xmldsig_X509DataType_httpwww_w3_org200009xmldsigX509SubjectName', True)
    __X509SubjectName._DeclarationLocation = pyxb.utils.utility.Location('/tmp/pyxbdist.RHB65sy/PyXB-1.1.5/pyxb/bundles/wssplat/schemas/ds.xsd', 189, 6)
    __X509SubjectName._UseLocation = pyxb.utils.utility.Location('/tmp/pyxbdist.RHB65sy/PyXB-1.1.5/pyxb/bundles/wssplat/schemas/ds.xsd', 185, 2)

    
    X509SubjectName = property(__X509SubjectName.value, __X509SubjectName.set, None, None)

    
    # Element {http://www.w3.org/2000/09/xmldsig#}X509Certificate uses Python identifier X509Certificate
    __X509Certificate = pyxb.binding.content.ElementUse(pyxb.namespace.ExpandedName(Namespace, u'X509Certificate'), 'X509Certificate', '__httpwww_w3_org200009xmldsig_X509DataType_httpwww_w3_org200009xmldsigX509Certificate', True)
    __X509Certificate._DeclarationLocation = pyxb.utils.utility.Location('/tmp/pyxbdist.RHB65sy/PyXB-1.1.5/pyxb/bundles/wssplat/schemas/ds.xsd', 190, 6)
    __X509Certificate._UseLocation = pyxb.utils.utility.Location('/tmp/pyxbdist.RHB65sy/PyXB-1.1.5/pyxb/bundles/wssplat/schemas/ds.xsd', 185, 2)

    
    X509Certificate = property(__X509Certificate.value, __X509Certificate.set, None, None)

    
    # Element {http://www.w3.org/2000/09/xmldsig#}X509CRL uses Python identifier X509CRL
    __X509CRL = pyxb.binding.content.ElementUse(pyxb.namespace.ExpandedName(Namespace, u'X509CRL'), 'X509CRL', '__httpwww_w3_org200009xmldsig_X509DataType_httpwww_w3_org200009xmldsigX509CRL', True)
    __X509CRL._DeclarationLocation = pyxb.utils.utility.Location('/tmp/pyxbdist.RHB65sy/PyXB-1.1.5/pyxb/bundles/wssplat/schemas/ds.xsd', 191, 6)
    __X509CRL._UseLocation = pyxb.utils.utility.Location('/tmp/pyxbdist.RHB65sy/PyXB-1.1.5/pyxb/bundles/wssplat/schemas/ds.xsd', 185, 2)

    
    X509CRL = property(__X509CRL.value, __X509CRL.set, None, None)

    _HasWildcardElement = True

    _ElementMap = {
        __X509IssuerSerial.name() : __X509IssuerSerial,
        __X509SKI.name() : __X509SKI,
        __X509SubjectName.name() : __X509SubjectName,
        __X509Certificate.name() : __X509Certificate,
        __X509CRL.name() : __X509CRL
    }
    _AttributeMap = {
        
    }
Namespace.addCategoryObject('typeBinding', u'X509DataType', X509DataType)


# Complex type {http://www.w3.org/2000/09/xmldsig#}SignedInfoType with content type ELEMENT_ONLY
class SignedInfoType (pyxb.binding.basis.complexTypeDefinition):
    _TypeDefinition = None
    _ContentTypeTag = pyxb.binding.basis.complexTypeDefinition._CT_ELEMENT_ONLY
    _Abstract = False
    _ExpandedName = pyxb.namespace.ExpandedName(Namespace, u'SignedInfoType')
    _DefinitionLocation = pyxb.utils.utility.Location('/tmp/pyxbdist.RHB65sy/PyXB-1.1.5/pyxb/bundles/wssplat/schemas/ds.xsd', 66, 0)
    # Base type is pyxb.binding.datatypes.anyType
    
    # Element {http://www.w3.org/2000/09/xmldsig#}CanonicalizationMethod uses Python identifier CanonicalizationMethod
    __CanonicalizationMethod = pyxb.binding.content.ElementUse(pyxb.namespace.ExpandedName(Namespace, u'CanonicalizationMethod'), 'CanonicalizationMethod', '__httpwww_w3_org200009xmldsig_SignedInfoType_httpwww_w3_org200009xmldsigCanonicalizationMethod', False)
    __CanonicalizationMethod._DeclarationLocation = pyxb.utils.utility.Location('/tmp/pyxbdist.RHB65sy/PyXB-1.1.5/pyxb/bundles/wssplat/schemas/ds.xsd', 75, 2)
    __CanonicalizationMethod._UseLocation = pyxb.utils.utility.Location('/tmp/pyxbdist.RHB65sy/PyXB-1.1.5/pyxb/bundles/wssplat/schemas/ds.xsd', 67, 2)

    
    CanonicalizationMethod = property(__CanonicalizationMethod.value, __CanonicalizationMethod.set, None, None)

    
    # Element {http://www.w3.org/2000/09/xmldsig#}Reference uses Python identifier Reference
    __Reference = pyxb.binding.content.ElementUse(pyxb.namespace.ExpandedName(Namespace, u'Reference'), 'Reference', '__httpwww_w3_org200009xmldsig_SignedInfoType_httpwww_w3_org200009xmldsigReference', True)
    __Reference._DeclarationLocation = pyxb.utils.utility.Location('/tmp/pyxbdist.RHB65sy/PyXB-1.1.5/pyxb/bundles/wssplat/schemas/ds.xsd', 96, 0)
    __Reference._UseLocation = pyxb.utils.utility.Location('/tmp/pyxbdist.RHB65sy/PyXB-1.1.5/pyxb/bundles/wssplat/schemas/ds.xsd', 67, 2)

    
    Reference = property(__Reference.value, __Reference.set, None, None)

    
    # Element {http://www.w3.org/2000/09/xmldsig#}SignatureMethod uses Python identifier SignatureMethod
    __SignatureMethod = pyxb.binding.content.ElementUse(pyxb.namespace.ExpandedName(Namespace, u'SignatureMethod'), 'SignatureMethod', '__httpwww_w3_org200009xmldsig_SignedInfoType_httpwww_w3_org200009xmldsigSignatureMethod', False)
    __SignatureMethod._DeclarationLocation = pyxb.utils.utility.Location('/tmp/pyxbdist.RHB65sy/PyXB-1.1.5/pyxb/bundles/wssplat/schemas/ds.xsd', 84, 2)
    __SignatureMethod._UseLocation = pyxb.utils.utility.Location('/tmp/pyxbdist.RHB65sy/PyXB-1.1.5/pyxb/bundles/wssplat/schemas/ds.xsd', 67, 2)

    
    SignatureMethod = property(__SignatureMethod.value, __SignatureMethod.set, None, None)

    
    # Attribute Id uses Python identifier Id
    __Id = pyxb.binding.content.AttributeUse(pyxb.namespace.ExpandedName(None, u'Id'), 'Id', '__httpwww_w3_org200009xmldsig_SignedInfoType_Id', pyxb.binding.datatypes.ID)
    __Id._DeclarationLocation = pyxb.utils.utility.Location('/tmp/pyxbdist.RHB65sy/PyXB-1.1.5/pyxb/bundles/wssplat/schemas/ds.xsd', 72, 2)
    __Id._UseLocation = pyxb.utils.utility.Location('/tmp/pyxbdist.RHB65sy/PyXB-1.1.5/pyxb/bundles/wssplat/schemas/ds.xsd', 72, 2)
    
    Id = property(__Id.value, __Id.set, None, None)


    _ElementMap = {
        __CanonicalizationMethod.name() : __CanonicalizationMethod,
        __Reference.name() : __Reference,
        __SignatureMethod.name() : __SignatureMethod
    }
    _AttributeMap = {
        __Id.name() : __Id
    }
Namespace.addCategoryObject('typeBinding', u'SignedInfoType', SignedInfoType)


# Complex type {http://www.w3.org/2000/09/xmldsig#}X509IssuerSerialType with content type ELEMENT_ONLY
class X509IssuerSerialType (pyxb.binding.basis.complexTypeDefinition):
    _TypeDefinition = None
    _ContentTypeTag = pyxb.binding.basis.complexTypeDefinition._CT_ELEMENT_ONLY
    _Abstract = False
    _ExpandedName = pyxb.namespace.ExpandedName(Namespace, u'X509IssuerSerialType')
    _DefinitionLocation = pyxb.utils.utility.Location('/tmp/pyxbdist.RHB65sy/PyXB-1.1.5/pyxb/bundles/wssplat/schemas/ds.xsd', 197, 0)
    # Base type is pyxb.binding.datatypes.anyType
    
    # Element {http://www.w3.org/2000/09/xmldsig#}X509SerialNumber uses Python identifier X509SerialNumber
    __X509SerialNumber = pyxb.binding.content.ElementUse(pyxb.namespace.ExpandedName(Namespace, u'X509SerialNumber'), 'X509SerialNumber', '__httpwww_w3_org200009xmldsig_X509IssuerSerialType_httpwww_w3_org200009xmldsigX509SerialNumber', False)
    __X509SerialNumber._DeclarationLocation = pyxb.utils.utility.Location('/tmp/pyxbdist.RHB65sy/PyXB-1.1.5/pyxb/bundles/wssplat/schemas/ds.xsd', 200, 4)
    __X509SerialNumber._UseLocation = pyxb.utils.utility.Location('/tmp/pyxbdist.RHB65sy/PyXB-1.1.5/pyxb/bundles/wssplat/schemas/ds.xsd', 198, 2)

    
    X509SerialNumber = property(__X509SerialNumber.value, __X509SerialNumber.set, None, None)

    
    # Element {http://www.w3.org/2000/09/xmldsig#}X509IssuerName uses Python identifier X509IssuerName
    __X509IssuerName = pyxb.binding.content.ElementUse(pyxb.namespace.ExpandedName(Namespace, u'X509IssuerName'), 'X509IssuerName', '__httpwww_w3_org200009xmldsig_X509IssuerSerialType_httpwww_w3_org200009xmldsigX509IssuerName', False)
    __X509IssuerName._DeclarationLocation = pyxb.utils.utility.Location('/tmp/pyxbdist.RHB65sy/PyXB-1.1.5/pyxb/bundles/wssplat/schemas/ds.xsd', 199, 4)
    __X509IssuerName._UseLocation = pyxb.utils.utility.Location('/tmp/pyxbdist.RHB65sy/PyXB-1.1.5/pyxb/bundles/wssplat/schemas/ds.xsd', 198, 2)

    
    X509IssuerName = property(__X509IssuerName.value, __X509IssuerName.set, None, None)


    _ElementMap = {
        __X509SerialNumber.name() : __X509SerialNumber,
        __X509IssuerName.name() : __X509IssuerName
    }
    _AttributeMap = {
        
    }
Namespace.addCategoryObject('typeBinding', u'X509IssuerSerialType', X509IssuerSerialType)


# Complex type {http://www.w3.org/2000/09/xmldsig#}SignatureMethodType with content type MIXED
class SignatureMethodType (pyxb.binding.basis.complexTypeDefinition):
    _TypeDefinition = None
    _ContentTypeTag = pyxb.binding.basis.complexTypeDefinition._CT_MIXED
    _Abstract = False
    _ExpandedName = pyxb.namespace.ExpandedName(Namespace, u'SignatureMethodType')
    _DefinitionLocation = pyxb.utils.utility.Location('/tmp/pyxbdist.RHB65sy/PyXB-1.1.5/pyxb/bundles/wssplat/schemas/ds.xsd', 85, 2)
    # Base type is pyxb.binding.datatypes.anyType
    
    # Element {http://www.w3.org/2000/09/xmldsig#}HMACOutputLength uses Python identifier HMACOutputLength
    __HMACOutputLength = pyxb.binding.content.ElementUse(pyxb.namespace.ExpandedName(Namespace, u'HMACOutputLength'), 'HMACOutputLength', '__httpwww_w3_org200009xmldsig_SignatureMethodType_httpwww_w3_org200009xmldsigHMACOutputLength', False)
    __HMACOutputLength._DeclarationLocation = pyxb.utils.utility.Location('/tmp/pyxbdist.RHB65sy/PyXB-1.1.5/pyxb/bundles/wssplat/schemas/ds.xsd', 87, 6)
    __HMACOutputLength._UseLocation = pyxb.utils.utility.Location('/tmp/pyxbdist.RHB65sy/PyXB-1.1.5/pyxb/bundles/wssplat/schemas/ds.xsd', 86, 4)

    
    HMACOutputLength = property(__HMACOutputLength.value, __HMACOutputLength.set, None, None)

    
    # Attribute Algorithm uses Python identifier Algorithm
    __Algorithm = pyxb.binding.content.AttributeUse(pyxb.namespace.ExpandedName(None, u'Algorithm'), 'Algorithm', '__httpwww_w3_org200009xmldsig_SignatureMethodType_Algorithm', pyxb.binding.datatypes.anyURI, required=True)
    __Algorithm._DeclarationLocation = pyxb.utils.utility.Location('/tmp/pyxbdist.RHB65sy/PyXB-1.1.5/pyxb/bundles/wssplat/schemas/ds.xsd', 91, 4)
    __Algorithm._UseLocation = pyxb.utils.utility.Location('/tmp/pyxbdist.RHB65sy/PyXB-1.1.5/pyxb/bundles/wssplat/schemas/ds.xsd', 91, 4)
    
    Algorithm = property(__Algorithm.value, __Algorithm.set, None, None)

    _HasWildcardElement = True

    _ElementMap = {
        __HMACOutputLength.name() : __HMACOutputLength
    }
    _AttributeMap = {
        __Algorithm.name() : __Algorithm
    }
Namespace.addCategoryObject('typeBinding', u'SignatureMethodType', SignatureMethodType)


# Complex type {http://www.w3.org/2000/09/xmldsig#}SignatureType with content type ELEMENT_ONLY
class SignatureType (pyxb.binding.basis.complexTypeDefinition):
    _TypeDefinition = None
    _ContentTypeTag = pyxb.binding.basis.complexTypeDefinition._CT_ELEMENT_ONLY
    _Abstract = False
    _ExpandedName = pyxb.namespace.ExpandedName(Namespace, u'SignatureType')
    _DefinitionLocation = pyxb.utils.utility.Location('/tmp/pyxbdist.RHB65sy/PyXB-1.1.5/pyxb/bundles/wssplat/schemas/ds.xsd', 44, 0)
    # Base type is pyxb.binding.datatypes.anyType
    
    # Element {http://www.w3.org/2000/09/xmldsig#}Object uses Python identifier Object
    __Object = pyxb.binding.content.ElementUse(pyxb.namespace.ExpandedName(Namespace, u'Object'), 'Object', '__httpwww_w3_org200009xmldsig_SignatureType_httpwww_w3_org200009xmldsigObject', True)
    __Object._DeclarationLocation = pyxb.utils.utility.Location('/tmp/pyxbdist.RHB65sy/PyXB-1.1.5/pyxb/bundles/wssplat/schemas/ds.xsd', 243, 0)
    __Object._UseLocation = pyxb.utils.utility.Location('/tmp/pyxbdist.RHB65sy/PyXB-1.1.5/pyxb/bundles/wssplat/schemas/ds.xsd', 45, 2)

    
    Object = property(__Object.value, __Object.set, None, None)

    
    # Element {http://www.w3.org/2000/09/xmldsig#}SignedInfo uses Python identifier SignedInfo
    __SignedInfo = pyxb.binding.content.ElementUse(pyxb.namespace.ExpandedName(Namespace, u'SignedInfo'), 'SignedInfo', '__httpwww_w3_org200009xmldsig_SignatureType_httpwww_w3_org200009xmldsigSignedInfo', False)
    __SignedInfo._DeclarationLocation = pyxb.utils.utility.Location('/tmp/pyxbdist.RHB65sy/PyXB-1.1.5/pyxb/bundles/wssplat/schemas/ds.xsd', 65, 0)
    __SignedInfo._UseLocation = pyxb.utils.utility.Location('/tmp/pyxbdist.RHB65sy/PyXB-1.1.5/pyxb/bundles/wssplat/schemas/ds.xsd', 45, 2)

    
    SignedInfo = property(__SignedInfo.value, __SignedInfo.set, None, None)

    
    # Element {http://www.w3.org/2000/09/xmldsig#}KeyInfo uses Python identifier KeyInfo
    __KeyInfo = pyxb.binding.content.ElementUse(pyxb.namespace.ExpandedName(Namespace, u'KeyInfo'), 'KeyInfo', '__httpwww_w3_org200009xmldsig_SignatureType_httpwww_w3_org200009xmldsigKeyInfo', False)
    __KeyInfo._DeclarationLocation = pyxb.utils.utility.Location('/tmp/pyxbdist.RHB65sy/PyXB-1.1.5/pyxb/bundles/wssplat/schemas/ds.xsd', 144, 0)
    __KeyInfo._UseLocation = pyxb.utils.utility.Location('/tmp/pyxbdist.RHB65sy/PyXB-1.1.5/pyxb/bundles/wssplat/schemas/ds.xsd', 45, 2)

    
    KeyInfo = property(__KeyInfo.value, __KeyInfo.set, None, None)

    
    # Element {http://www.w3.org/2000/09/xmldsig#}SignatureValue uses Python identifier SignatureValue
    __SignatureValue = pyxb.binding.content.ElementUse(pyxb.namespace.ExpandedName(Namespace, u'SignatureValue'), 'SignatureValue', '__httpwww_w3_org200009xmldsig_SignatureType_httpwww_w3_org200009xmldsigSignatureValue', False)
    __SignatureValue._DeclarationLocation = pyxb.utils.utility.Location('/tmp/pyxbdist.RHB65sy/PyXB-1.1.5/pyxb/bundles/wssplat/schemas/ds.xsd', 54, 2)
    __SignatureValue._UseLocation = pyxb.utils.utility.Location('/tmp/pyxbdist.RHB65sy/PyXB-1.1.5/pyxb/bundles/wssplat/schemas/ds.xsd', 45, 2)

    
    SignatureValue = property(__SignatureValue.value, __SignatureValue.set, None, None)

    
    # Attribute Id uses Python identifier Id
    __Id = pyxb.binding.content.AttributeUse(pyxb.namespace.ExpandedName(None, u'Id'), 'Id', '__httpwww_w3_org200009xmldsig_SignatureType_Id', pyxb.binding.datatypes.ID)
    __Id._DeclarationLocation = pyxb.utils.utility.Location('/tmp/pyxbdist.RHB65sy/PyXB-1.1.5/pyxb/bundles/wssplat/schemas/ds.xsd', 51, 2)
    __Id._UseLocation = pyxb.utils.utility.Location('/tmp/pyxbdist.RHB65sy/PyXB-1.1.5/pyxb/bundles/wssplat/schemas/ds.xsd', 51, 2)
    
    Id = property(__Id.value, __Id.set, None, None)


    _ElementMap = {
        __Object.name() : __Object,
        __SignedInfo.name() : __SignedInfo,
        __KeyInfo.name() : __KeyInfo,
        __SignatureValue.name() : __SignatureValue
    }
    _AttributeMap = {
        __Id.name() : __Id
    }
Namespace.addCategoryObject('typeBinding', u'SignatureType', SignatureType)


# Complex type {http://www.w3.org/2000/09/xmldsig#}SignaturePropertiesType with content type ELEMENT_ONLY
class SignaturePropertiesType (pyxb.binding.basis.complexTypeDefinition):
    _TypeDefinition = None
    _ContentTypeTag = pyxb.binding.basis.complexTypeDefinition._CT_ELEMENT_ONLY
    _Abstract = False
    _ExpandedName = pyxb.namespace.ExpandedName(Namespace, u'SignaturePropertiesType')
    _DefinitionLocation = pyxb.utils.utility.Location('/tmp/pyxbdist.RHB65sy/PyXB-1.1.5/pyxb/bundles/wssplat/schemas/ds.xsd', 262, 0)
    # Base type is pyxb.binding.datatypes.anyType
    
    # Element {http://www.w3.org/2000/09/xmldsig#}SignatureProperty uses Python identifier SignatureProperty
    __SignatureProperty = pyxb.binding.content.ElementUse(pyxb.namespace.ExpandedName(Namespace, u'SignatureProperty'), 'SignatureProperty', '__httpwww_w3_org200009xmldsig_SignaturePropertiesType_httpwww_w3_org200009xmldsigSignatureProperty', True)
    __SignatureProperty._DeclarationLocation = pyxb.utils.utility.Location('/tmp/pyxbdist.RHB65sy/PyXB-1.1.5/pyxb/bundles/wssplat/schemas/ds.xsd', 269, 3)
    __SignatureProperty._UseLocation = pyxb.utils.utility.Location('/tmp/pyxbdist.RHB65sy/PyXB-1.1.5/pyxb/bundles/wssplat/schemas/ds.xsd', 263, 2)

    
    SignatureProperty = property(__SignatureProperty.value, __SignatureProperty.set, None, None)

    
    # Attribute Id uses Python identifier Id
    __Id = pyxb.binding.content.AttributeUse(pyxb.namespace.ExpandedName(None, u'Id'), 'Id', '__httpwww_w3_org200009xmldsig_SignaturePropertiesType_Id', pyxb.binding.datatypes.ID)
    __Id._DeclarationLocation = pyxb.utils.utility.Location('/tmp/pyxbdist.RHB65sy/PyXB-1.1.5/pyxb/bundles/wssplat/schemas/ds.xsd', 266, 2)
    __Id._UseLocation = pyxb.utils.utility.Location('/tmp/pyxbdist.RHB65sy/PyXB-1.1.5/pyxb/bundles/wssplat/schemas/ds.xsd', 266, 2)
    
    Id = property(__Id.value, __Id.set, None, None)


    _ElementMap = {
        __SignatureProperty.name() : __SignatureProperty
    }
    _AttributeMap = {
        __Id.name() : __Id
    }
Namespace.addCategoryObject('typeBinding', u'SignaturePropertiesType', SignaturePropertiesType)


# Complex type {http://www.w3.org/2000/09/xmldsig#}TransformsType with content type ELEMENT_ONLY
class TransformsType (pyxb.binding.basis.complexTypeDefinition):
    _TypeDefinition = None
    _ContentTypeTag = pyxb.binding.basis.complexTypeDefinition._CT_ELEMENT_ONLY
    _Abstract = False
    _ExpandedName = pyxb.namespace.ExpandedName(Namespace, u'TransformsType')
    _DefinitionLocation = pyxb.utils.utility.Location('/tmp/pyxbdist.RHB65sy/PyXB-1.1.5/pyxb/bundles/wssplat/schemas/ds.xsd', 109, 2)
    # Base type is pyxb.binding.datatypes.anyType
    
    # Element {http://www.w3.org/2000/09/xmldsig#}Transform uses Python identifier Transform
    __Transform = pyxb.binding.content.ElementUse(pyxb.namespace.ExpandedName(Namespace, u'Transform'), 'Transform', '__httpwww_w3_org200009xmldsig_TransformsType_httpwww_w3_org200009xmldsigTransform', True)
    __Transform._DeclarationLocation = pyxb.utils.utility.Location('/tmp/pyxbdist.RHB65sy/PyXB-1.1.5/pyxb/bundles/wssplat/schemas/ds.xsd', 115, 2)
    __Transform._UseLocation = pyxb.utils.utility.Location('/tmp/pyxbdist.RHB65sy/PyXB-1.1.5/pyxb/bundles/wssplat/schemas/ds.xsd', 110, 4)

    
    Transform = property(__Transform.value, __Transform.set, None, None)


    _ElementMap = {
        __Transform.name() : __Transform
    }
    _AttributeMap = {
        
    }
Namespace.addCategoryObject('typeBinding', u'TransformsType', TransformsType)


# Complex type {http://www.w3.org/2000/09/xmldsig#}SignatureValueType with content type SIMPLE
class SignatureValueType (pyxb.binding.basis.complexTypeDefinition):
    _TypeDefinition = pyxb.binding.datatypes.base64Binary
    _ContentTypeTag = pyxb.binding.basis.complexTypeDefinition._CT_SIMPLE
    _Abstract = False
    _ExpandedName = pyxb.namespace.ExpandedName(Namespace, u'SignatureValueType')
    _DefinitionLocation = pyxb.utils.utility.Location('/tmp/pyxbdist.RHB65sy/PyXB-1.1.5/pyxb/bundles/wssplat/schemas/ds.xsd', 55, 2)
    # Base type is pyxb.binding.datatypes.base64Binary
    
    # Attribute Id uses Python identifier Id
    __Id = pyxb.binding.content.AttributeUse(pyxb.namespace.ExpandedName(None, u'Id'), 'Id', '__httpwww_w3_org200009xmldsig_SignatureValueType_Id', pyxb.binding.datatypes.ID)
    __Id._DeclarationLocation = pyxb.utils.utility.Location('/tmp/pyxbdist.RHB65sy/PyXB-1.1.5/pyxb/bundles/wssplat/schemas/ds.xsd', 58, 8)
    __Id._UseLocation = pyxb.utils.utility.Location('/tmp/pyxbdist.RHB65sy/PyXB-1.1.5/pyxb/bundles/wssplat/schemas/ds.xsd', 58, 8)
    
    Id = property(__Id.value, __Id.set, None, None)


    _ElementMap = {
        
    }
    _AttributeMap = {
        __Id.name() : __Id
    }
Namespace.addCategoryObject('typeBinding', u'SignatureValueType', SignatureValueType)


# Complex type {http://www.w3.org/2000/09/xmldsig#}DigestMethodType with content type MIXED
class DigestMethodType (pyxb.binding.basis.complexTypeDefinition):
    _TypeDefinition = None
    _ContentTypeTag = pyxb.binding.basis.complexTypeDefinition._CT_MIXED
    _Abstract = False
    _ExpandedName = pyxb.namespace.ExpandedName(Namespace, u'DigestMethodType')
    _DefinitionLocation = pyxb.utils.utility.Location('/tmp/pyxbdist.RHB65sy/PyXB-1.1.5/pyxb/bundles/wssplat/schemas/ds.xsd', 128, 0)
    # Base type is pyxb.binding.datatypes.anyType
    
    # Attribute Algorithm uses Python identifier Algorithm
    __Algorithm = pyxb.binding.content.AttributeUse(pyxb.namespace.ExpandedName(None, u'Algorithm'), 'Algorithm', '__httpwww_w3_org200009xmldsig_DigestMethodType_Algorithm', pyxb.binding.datatypes.anyURI, required=True)
    __Algorithm._DeclarationLocation = pyxb.utils.utility.Location('/tmp/pyxbdist.RHB65sy/PyXB-1.1.5/pyxb/bundles/wssplat/schemas/ds.xsd', 132, 2)
    __Algorithm._UseLocation = pyxb.utils.utility.Location('/tmp/pyxbdist.RHB65sy/PyXB-1.1.5/pyxb/bundles/wssplat/schemas/ds.xsd', 132, 2)
    
    Algorithm = property(__Algorithm.value, __Algorithm.set, None, None)

    _HasWildcardElement = True

    _ElementMap = {
        
    }
    _AttributeMap = {
        __Algorithm.name() : __Algorithm
    }
Namespace.addCategoryObject('typeBinding', u'DigestMethodType', DigestMethodType)


# Complex type {http://www.w3.org/2000/09/xmldsig#}ObjectType with content type MIXED
class ObjectType (pyxb.binding.basis.complexTypeDefinition):
    _TypeDefinition = None
    _ContentTypeTag = pyxb.binding.basis.complexTypeDefinition._CT_MIXED
    _Abstract = False
    _ExpandedName = pyxb.namespace.ExpandedName(Namespace, u'ObjectType')
    _DefinitionLocation = pyxb.utils.utility.Location('/tmp/pyxbdist.RHB65sy/PyXB-1.1.5/pyxb/bundles/wssplat/schemas/ds.xsd', 244, 0)
    # Base type is pyxb.binding.datatypes.anyType
    
    # Attribute MimeType uses Python identifier MimeType
    __MimeType = pyxb.binding.content.AttributeUse(pyxb.namespace.ExpandedName(None, u'MimeType'), 'MimeType', '__httpwww_w3_org200009xmldsig_ObjectType_MimeType', pyxb.binding.datatypes.string)
    __MimeType._DeclarationLocation = pyxb.utils.utility.Location('/tmp/pyxbdist.RHB65sy/PyXB-1.1.5/pyxb/bundles/wssplat/schemas/ds.xsd', 249, 2)
    __MimeType._UseLocation = pyxb.utils.utility.Location('/tmp/pyxbdist.RHB65sy/PyXB-1.1.5/pyxb/bundles/wssplat/schemas/ds.xsd', 249, 2)
    
    MimeType = property(__MimeType.value, __MimeType.set, None, None)

    
    # Attribute Encoding uses Python identifier Encoding
    __Encoding = pyxb.binding.content.AttributeUse(pyxb.namespace.ExpandedName(None, u'Encoding'), 'Encoding', '__httpwww_w3_org200009xmldsig_ObjectType_Encoding', pyxb.binding.datatypes.anyURI)
    __Encoding._DeclarationLocation = pyxb.utils.utility.Location('/tmp/pyxbdist.RHB65sy/PyXB-1.1.5/pyxb/bundles/wssplat/schemas/ds.xsd', 250, 2)
    __Encoding._UseLocation = pyxb.utils.utility.Location('/tmp/pyxbdist.RHB65sy/PyXB-1.1.5/pyxb/bundles/wssplat/schemas/ds.xsd', 250, 2)
    
    Encoding = property(__Encoding.value, __Encoding.set, None, None)

    
    # Attribute Id uses Python identifier Id
    __Id = pyxb.binding.content.AttributeUse(pyxb.namespace.ExpandedName(None, u'Id'), 'Id', '__httpwww_w3_org200009xmldsig_ObjectType_Id', pyxb.binding.datatypes.ID)
    __Id._DeclarationLocation = pyxb.utils.utility.Location('/tmp/pyxbdist.RHB65sy/PyXB-1.1.5/pyxb/bundles/wssplat/schemas/ds.xsd', 248, 2)
    __Id._UseLocation = pyxb.utils.utility.Location('/tmp/pyxbdist.RHB65sy/PyXB-1.1.5/pyxb/bundles/wssplat/schemas/ds.xsd', 248, 2)
    
    Id = property(__Id.value, __Id.set, None, None)

    _HasWildcardElement = True

    _ElementMap = {
        
    }
    _AttributeMap = {
        __MimeType.name() : __MimeType,
        __Encoding.name() : __Encoding,
        __Id.name() : __Id
    }
Namespace.addCategoryObject('typeBinding', u'ObjectType', ObjectType)


# Complex type {http://www.w3.org/2000/09/xmldsig#}SignaturePropertyType with content type MIXED
class SignaturePropertyType (pyxb.binding.basis.complexTypeDefinition):
    _TypeDefinition = None
    _ContentTypeTag = pyxb.binding.basis.complexTypeDefinition._CT_MIXED
    _Abstract = False
    _ExpandedName = pyxb.namespace.ExpandedName(Namespace, u'SignaturePropertyType')
    _DefinitionLocation = pyxb.utils.utility.Location('/tmp/pyxbdist.RHB65sy/PyXB-1.1.5/pyxb/bundles/wssplat/schemas/ds.xsd', 270, 3)
    # Base type is pyxb.binding.datatypes.anyType
    
    # Attribute Target uses Python identifier Target
    __Target = pyxb.binding.content.AttributeUse(pyxb.namespace.ExpandedName(None, u'Target'), 'Target', '__httpwww_w3_org200009xmldsig_SignaturePropertyType_Target', pyxb.binding.datatypes.anyURI, required=True)
    __Target._DeclarationLocation = pyxb.utils.utility.Location('/tmp/pyxbdist.RHB65sy/PyXB-1.1.5/pyxb/bundles/wssplat/schemas/ds.xsd', 275, 5)
    __Target._UseLocation = pyxb.utils.utility.Location('/tmp/pyxbdist.RHB65sy/PyXB-1.1.5/pyxb/bundles/wssplat/schemas/ds.xsd', 275, 5)
    
    Target = property(__Target.value, __Target.set, None, None)

    
    # Attribute Id uses Python identifier Id
    __Id = pyxb.binding.content.AttributeUse(pyxb.namespace.ExpandedName(None, u'Id'), 'Id', '__httpwww_w3_org200009xmldsig_SignaturePropertyType_Id', pyxb.binding.datatypes.ID)
    __Id._DeclarationLocation = pyxb.utils.utility.Location('/tmp/pyxbdist.RHB65sy/PyXB-1.1.5/pyxb/bundles/wssplat/schemas/ds.xsd', 276, 5)
    __Id._UseLocation = pyxb.utils.utility.Location('/tmp/pyxbdist.RHB65sy/PyXB-1.1.5/pyxb/bundles/wssplat/schemas/ds.xsd', 276, 5)
    
    Id = property(__Id.value, __Id.set, None, None)

    _HasWildcardElement = True

    _ElementMap = {
        
    }
    _AttributeMap = {
        __Target.name() : __Target,
        __Id.name() : __Id
    }
Namespace.addCategoryObject('typeBinding', u'SignaturePropertyType', SignaturePropertyType)


# Complex type {http://www.w3.org/2000/09/xmldsig#}KeyValueType with content type MIXED
class KeyValueType (pyxb.binding.basis.complexTypeDefinition):
    _TypeDefinition = None
    _ContentTypeTag = pyxb.binding.basis.complexTypeDefinition._CT_MIXED
    _Abstract = False
    _ExpandedName = pyxb.namespace.ExpandedName(Namespace, u'KeyValueType')
    _DefinitionLocation = pyxb.utils.utility.Location('/tmp/pyxbdist.RHB65sy/PyXB-1.1.5/pyxb/bundles/wssplat/schemas/ds.xsd', 164, 2)
    # Base type is pyxb.binding.datatypes.anyType
    
    # Element {http://www.w3.org/2000/09/xmldsig#}RSAKeyValue uses Python identifier RSAKeyValue
    __RSAKeyValue = pyxb.binding.content.ElementUse(pyxb.namespace.ExpandedName(Namespace, u'RSAKeyValue'), 'RSAKeyValue', '__httpwww_w3_org200009xmldsig_KeyValueType_httpwww_w3_org200009xmldsigRSAKeyValue', False)
    __RSAKeyValue._DeclarationLocation = pyxb.utils.utility.Location('/tmp/pyxbdist.RHB65sy/PyXB-1.1.5/pyxb/bundles/wssplat/schemas/ds.xsd', 306, 0)
    __RSAKeyValue._UseLocation = pyxb.utils.utility.Location('/tmp/pyxbdist.RHB65sy/PyXB-1.1.5/pyxb/bundles/wssplat/schemas/ds.xsd', 165, 3)

    
    RSAKeyValue = property(__RSAKeyValue.value, __RSAKeyValue.set, None, None)

    
    # Element {http://www.w3.org/2000/09/xmldsig#}DSAKeyValue uses Python identifier DSAKeyValue
    __DSAKeyValue = pyxb.binding.content.ElementUse(pyxb.namespace.ExpandedName(Namespace, u'DSAKeyValue'), 'DSAKeyValue', '__httpwww_w3_org200009xmldsig_KeyValueType_httpwww_w3_org200009xmldsigDSAKeyValue', False)
    __DSAKeyValue._DeclarationLocation = pyxb.utils.utility.Location('/tmp/pyxbdist.RHB65sy/PyXB-1.1.5/pyxb/bundles/wssplat/schemas/ds.xsd', 289, 0)
    __DSAKeyValue._UseLocation = pyxb.utils.utility.Location('/tmp/pyxbdist.RHB65sy/PyXB-1.1.5/pyxb/bundles/wssplat/schemas/ds.xsd', 165, 3)

    
    DSAKeyValue = property(__DSAKeyValue.value, __DSAKeyValue.set, None, None)

    _HasWildcardElement = True

    _ElementMap = {
        __RSAKeyValue.name() : __RSAKeyValue,
        __DSAKeyValue.name() : __DSAKeyValue
    }
    _AttributeMap = {
        
    }
Namespace.addCategoryObject('typeBinding', u'KeyValueType', KeyValueType)


# Complex type {http://www.w3.org/2000/09/xmldsig#}RetrievalMethodType with content type ELEMENT_ONLY
class RetrievalMethodType (pyxb.binding.basis.complexTypeDefinition):
    _TypeDefinition = None
    _ContentTypeTag = pyxb.binding.basis.complexTypeDefinition._CT_ELEMENT_ONLY
    _Abstract = False
    _ExpandedName = pyxb.namespace.ExpandedName(Namespace, u'RetrievalMethodType')
    _DefinitionLocation = pyxb.utils.utility.Location('/tmp/pyxbdist.RHB65sy/PyXB-1.1.5/pyxb/bundles/wssplat/schemas/ds.xsd', 173, 2)
    # Base type is pyxb.binding.datatypes.anyType
    
    # Element {http://www.w3.org/2000/09/xmldsig#}Transforms uses Python identifier Transforms
    __Transforms = pyxb.binding.content.ElementUse(pyxb.namespace.ExpandedName(Namespace, u'Transforms'), 'Transforms', '__httpwww_w3_org200009xmldsig_RetrievalMethodType_httpwww_w3_org200009xmldsigTransforms', False)
    __Transforms._DeclarationLocation = pyxb.utils.utility.Location('/tmp/pyxbdist.RHB65sy/PyXB-1.1.5/pyxb/bundles/wssplat/schemas/ds.xsd', 108, 2)
    __Transforms._UseLocation = pyxb.utils.utility.Location('/tmp/pyxbdist.RHB65sy/PyXB-1.1.5/pyxb/bundles/wssplat/schemas/ds.xsd', 174, 4)

    
    Transforms = property(__Transforms.value, __Transforms.set, None, None)

    
    # Attribute Type uses Python identifier Type
    __Type = pyxb.binding.content.AttributeUse(pyxb.namespace.ExpandedName(None, u'Type'), 'Type', '__httpwww_w3_org200009xmldsig_RetrievalMethodType_Type', pyxb.binding.datatypes.anyURI)
    __Type._DeclarationLocation = pyxb.utils.utility.Location('/tmp/pyxbdist.RHB65sy/PyXB-1.1.5/pyxb/bundles/wssplat/schemas/ds.xsd', 178, 4)
    __Type._UseLocation = pyxb.utils.utility.Location('/tmp/pyxbdist.RHB65sy/PyXB-1.1.5/pyxb/bundles/wssplat/schemas/ds.xsd', 178, 4)
    
    Type = property(__Type.value, __Type.set, None, None)

    
    # Attribute URI uses Python identifier URI
    __URI = pyxb.binding.content.AttributeUse(pyxb.namespace.ExpandedName(None, u'URI'), 'URI', '__httpwww_w3_org200009xmldsig_RetrievalMethodType_URI', pyxb.binding.datatypes.anyURI)
    __URI._DeclarationLocation = pyxb.utils.utility.Location('/tmp/pyxbdist.RHB65sy/PyXB-1.1.5/pyxb/bundles/wssplat/schemas/ds.xsd', 177, 4)
    __URI._UseLocation = pyxb.utils.utility.Location('/tmp/pyxbdist.RHB65sy/PyXB-1.1.5/pyxb/bundles/wssplat/schemas/ds.xsd', 177, 4)
    
    URI = property(__URI.value, __URI.set, None, None)


    _ElementMap = {
        __Transforms.name() : __Transforms
    }
    _AttributeMap = {
        __Type.name() : __Type,
        __URI.name() : __URI
    }
Namespace.addCategoryObject('typeBinding', u'RetrievalMethodType', RetrievalMethodType)


# Complex type {http://www.w3.org/2000/09/xmldsig#}ManifestType with content type ELEMENT_ONLY
class ManifestType (pyxb.binding.basis.complexTypeDefinition):
    _TypeDefinition = None
    _ContentTypeTag = pyxb.binding.basis.complexTypeDefinition._CT_ELEMENT_ONLY
    _Abstract = False
    _ExpandedName = pyxb.namespace.ExpandedName(Namespace, u'ManifestType')
    _DefinitionLocation = pyxb.utils.utility.Location('/tmp/pyxbdist.RHB65sy/PyXB-1.1.5/pyxb/bundles/wssplat/schemas/ds.xsd', 254, 0)
    # Base type is pyxb.binding.datatypes.anyType
    
    # Element {http://www.w3.org/2000/09/xmldsig#}Reference uses Python identifier Reference
    __Reference = pyxb.binding.content.ElementUse(pyxb.namespace.ExpandedName(Namespace, u'Reference'), 'Reference', '__httpwww_w3_org200009xmldsig_ManifestType_httpwww_w3_org200009xmldsigReference', True)
    __Reference._DeclarationLocation = pyxb.utils.utility.Location('/tmp/pyxbdist.RHB65sy/PyXB-1.1.5/pyxb/bundles/wssplat/schemas/ds.xsd', 96, 0)
    __Reference._UseLocation = pyxb.utils.utility.Location('/tmp/pyxbdist.RHB65sy/PyXB-1.1.5/pyxb/bundles/wssplat/schemas/ds.xsd', 255, 2)

    
    Reference = property(__Reference.value, __Reference.set, None, None)

    
    # Attribute Id uses Python identifier Id
    __Id = pyxb.binding.content.AttributeUse(pyxb.namespace.ExpandedName(None, u'Id'), 'Id', '__httpwww_w3_org200009xmldsig_ManifestType_Id', pyxb.binding.datatypes.ID)
    __Id._DeclarationLocation = pyxb.utils.utility.Location('/tmp/pyxbdist.RHB65sy/PyXB-1.1.5/pyxb/bundles/wssplat/schemas/ds.xsd', 258, 2)
    __Id._UseLocation = pyxb.utils.utility.Location('/tmp/pyxbdist.RHB65sy/PyXB-1.1.5/pyxb/bundles/wssplat/schemas/ds.xsd', 258, 2)
    
    Id = property(__Id.value, __Id.set, None, None)


    _ElementMap = {
        __Reference.name() : __Reference
    }
    _AttributeMap = {
        __Id.name() : __Id
    }
Namespace.addCategoryObject('typeBinding', u'ManifestType', ManifestType)


CanonicalizationMethod = pyxb.binding.basis.element(pyxb.namespace.ExpandedName(Namespace, u'CanonicalizationMethod'), CanonicalizationMethodType)
Namespace.addCategoryObject('elementBinding', CanonicalizationMethod.name().localName(), CanonicalizationMethod)

KeyName = pyxb.binding.basis.element(pyxb.namespace.ExpandedName(Namespace, u'KeyName'), pyxb.binding.datatypes.string)
Namespace.addCategoryObject('elementBinding', KeyName.name().localName(), KeyName)

KeyInfo = pyxb.binding.basis.element(pyxb.namespace.ExpandedName(Namespace, u'KeyInfo'), KeyInfoType)
Namespace.addCategoryObject('elementBinding', KeyInfo.name().localName(), KeyInfo)

SignedInfo = pyxb.binding.basis.element(pyxb.namespace.ExpandedName(Namespace, u'SignedInfo'), SignedInfoType)
Namespace.addCategoryObject('elementBinding', SignedInfo.name().localName(), SignedInfo)

RSAKeyValue = pyxb.binding.basis.element(pyxb.namespace.ExpandedName(Namespace, u'RSAKeyValue'), RSAKeyValueType)
Namespace.addCategoryObject('elementBinding', RSAKeyValue.name().localName(), RSAKeyValue)

Signature = pyxb.binding.basis.element(pyxb.namespace.ExpandedName(Namespace, u'Signature'), SignatureType)
Namespace.addCategoryObject('elementBinding', Signature.name().localName(), Signature)

SPKIData = pyxb.binding.basis.element(pyxb.namespace.ExpandedName(Namespace, u'SPKIData'), SPKIDataType)
Namespace.addCategoryObject('elementBinding', SPKIData.name().localName(), SPKIData)

SignatureProperties = pyxb.binding.basis.element(pyxb.namespace.ExpandedName(Namespace, u'SignatureProperties'), SignaturePropertiesType)
Namespace.addCategoryObject('elementBinding', SignatureProperties.name().localName(), SignatureProperties)

MgmtData = pyxb.binding.basis.element(pyxb.namespace.ExpandedName(Namespace, u'MgmtData'), pyxb.binding.datatypes.string)
Namespace.addCategoryObject('elementBinding', MgmtData.name().localName(), MgmtData)

Transforms = pyxb.binding.basis.element(pyxb.namespace.ExpandedName(Namespace, u'Transforms'), TransformsType)
Namespace.addCategoryObject('elementBinding', Transforms.name().localName(), Transforms)

Transform = pyxb.binding.basis.element(pyxb.namespace.ExpandedName(Namespace, u'Transform'), TransformType)
Namespace.addCategoryObject('elementBinding', Transform.name().localName(), Transform)

DigestMethod = pyxb.binding.basis.element(pyxb.namespace.ExpandedName(Namespace, u'DigestMethod'), DigestMethodType)
Namespace.addCategoryObject('elementBinding', DigestMethod.name().localName(), DigestMethod)

Object = pyxb.binding.basis.element(pyxb.namespace.ExpandedName(Namespace, u'Object'), ObjectType)
Namespace.addCategoryObject('elementBinding', Object.name().localName(), Object)

SignatureValue = pyxb.binding.basis.element(pyxb.namespace.ExpandedName(Namespace, u'SignatureValue'), SignatureValueType)
Namespace.addCategoryObject('elementBinding', SignatureValue.name().localName(), SignatureValue)

Reference = pyxb.binding.basis.element(pyxb.namespace.ExpandedName(Namespace, u'Reference'), ReferenceType)
Namespace.addCategoryObject('elementBinding', Reference.name().localName(), Reference)

SignatureProperty = pyxb.binding.basis.element(pyxb.namespace.ExpandedName(Namespace, u'SignatureProperty'), SignaturePropertyType)
Namespace.addCategoryObject('elementBinding', SignatureProperty.name().localName(), SignatureProperty)

KeyValue = pyxb.binding.basis.element(pyxb.namespace.ExpandedName(Namespace, u'KeyValue'), KeyValueType)
Namespace.addCategoryObject('elementBinding', KeyValue.name().localName(), KeyValue)

SignatureMethod = pyxb.binding.basis.element(pyxb.namespace.ExpandedName(Namespace, u'SignatureMethod'), SignatureMethodType)
Namespace.addCategoryObject('elementBinding', SignatureMethod.name().localName(), SignatureMethod)

X509Data = pyxb.binding.basis.element(pyxb.namespace.ExpandedName(Namespace, u'X509Data'), X509DataType)
Namespace.addCategoryObject('elementBinding', X509Data.name().localName(), X509Data)

PGPData = pyxb.binding.basis.element(pyxb.namespace.ExpandedName(Namespace, u'PGPData'), PGPDataType)
Namespace.addCategoryObject('elementBinding', PGPData.name().localName(), PGPData)

DSAKeyValue = pyxb.binding.basis.element(pyxb.namespace.ExpandedName(Namespace, u'DSAKeyValue'), DSAKeyValueType)
Namespace.addCategoryObject('elementBinding', DSAKeyValue.name().localName(), DSAKeyValue)

DigestValue = pyxb.binding.basis.element(pyxb.namespace.ExpandedName(Namespace, u'DigestValue'), DigestValueType)
Namespace.addCategoryObject('elementBinding', DigestValue.name().localName(), DigestValue)

Manifest = pyxb.binding.basis.element(pyxb.namespace.ExpandedName(Namespace, u'Manifest'), ManifestType)
Namespace.addCategoryObject('elementBinding', Manifest.name().localName(), Manifest)

RetrievalMethod = pyxb.binding.basis.element(pyxb.namespace.ExpandedName(Namespace, u'RetrievalMethod'), RetrievalMethodType)
Namespace.addCategoryObject('elementBinding', RetrievalMethod.name().localName(), RetrievalMethod)



DSAKeyValueType._AddElement(pyxb.binding.basis.element(pyxb.namespace.ExpandedName(Namespace, u'P'), CryptoBinary, scope=DSAKeyValueType))

DSAKeyValueType._AddElement(pyxb.binding.basis.element(pyxb.namespace.ExpandedName(Namespace, u'J'), CryptoBinary, scope=DSAKeyValueType))

DSAKeyValueType._AddElement(pyxb.binding.basis.element(pyxb.namespace.ExpandedName(Namespace, u'Q'), CryptoBinary, scope=DSAKeyValueType))

DSAKeyValueType._AddElement(pyxb.binding.basis.element(pyxb.namespace.ExpandedName(Namespace, u'G'), CryptoBinary, scope=DSAKeyValueType))

DSAKeyValueType._AddElement(pyxb.binding.basis.element(pyxb.namespace.ExpandedName(Namespace, u'Seed'), CryptoBinary, scope=DSAKeyValueType))

DSAKeyValueType._AddElement(pyxb.binding.basis.element(pyxb.namespace.ExpandedName(Namespace, u'Y'), CryptoBinary, scope=DSAKeyValueType))

DSAKeyValueType._AddElement(pyxb.binding.basis.element(pyxb.namespace.ExpandedName(Namespace, u'PgenCounter'), CryptoBinary, scope=DSAKeyValueType))
DSAKeyValueType._GroupModel_ = pyxb.binding.content.GroupSequence(
    pyxb.binding.content.ParticleModel(DSAKeyValueType._UseForTag(pyxb.namespace.ExpandedName(Namespace, u'P')), min_occurs=1, max_occurs=1),
    pyxb.binding.content.ParticleModel(DSAKeyValueType._UseForTag(pyxb.namespace.ExpandedName(Namespace, u'Q')), min_occurs=1, max_occurs=1)
    )
DSAKeyValueType._GroupModel_2 = pyxb.binding.content.GroupSequence(
    pyxb.binding.content.ParticleModel(DSAKeyValueType._UseForTag(pyxb.namespace.ExpandedName(Namespace, u'Seed')), min_occurs=1, max_occurs=1),
    pyxb.binding.content.ParticleModel(DSAKeyValueType._UseForTag(pyxb.namespace.ExpandedName(Namespace, u'PgenCounter')), min_occurs=1, max_occurs=1)
    )
DSAKeyValueType._GroupModel = pyxb.binding.content.GroupSequence(
    pyxb.binding.content.ParticleModel(DSAKeyValueType._GroupModel_, min_occurs=0L, max_occurs=1),
    pyxb.binding.content.ParticleModel(DSAKeyValueType._UseForTag(pyxb.namespace.ExpandedName(Namespace, u'G')), min_occurs=0L, max_occurs=1),
    pyxb.binding.content.ParticleModel(DSAKeyValueType._UseForTag(pyxb.namespace.ExpandedName(Namespace, u'Y')), min_occurs=1, max_occurs=1),
    pyxb.binding.content.ParticleModel(DSAKeyValueType._UseForTag(pyxb.namespace.ExpandedName(Namespace, u'J')), min_occurs=0L, max_occurs=1),
    pyxb.binding.content.ParticleModel(DSAKeyValueType._GroupModel_2, min_occurs=0L, max_occurs=1)
    )
DSAKeyValueType._ContentModel = pyxb.binding.content.ParticleModel(DSAKeyValueType._GroupModel, min_occurs=1, max_occurs=1)


CanonicalizationMethodType._GroupModel = pyxb.binding.content.GroupSequence(
    pyxb.binding.content.ParticleModel(pyxb.binding.content.Wildcard(process_contents=pyxb.binding.content.Wildcard.PC_strict, namespace_constraint=pyxb.binding.content.Wildcard.NC_any), min_occurs=0L, max_occurs=None)
    )
CanonicalizationMethodType._ContentModel = pyxb.binding.content.ParticleModel(CanonicalizationMethodType._GroupModel, min_occurs=1, max_occurs=1)



TransformType._AddElement(pyxb.binding.basis.element(pyxb.namespace.ExpandedName(Namespace, u'XPath'), pyxb.binding.datatypes.string, scope=TransformType))
TransformType._GroupModel = pyxb.binding.content.GroupChoice(
    pyxb.binding.content.ParticleModel(pyxb.binding.content.Wildcard(process_contents=pyxb.binding.content.Wildcard.PC_lax, namespace_constraint=(pyxb.binding.content.Wildcard.NC_not, u'http://www.w3.org/2000/09/xmldsig#')), min_occurs=1, max_occurs=1),
    pyxb.binding.content.ParticleModel(TransformType._UseForTag(pyxb.namespace.ExpandedName(Namespace, u'XPath')), min_occurs=1, max_occurs=1)
    )
TransformType._ContentModel = pyxb.binding.content.ParticleModel(TransformType._GroupModel, min_occurs=0L, max_occurs=None)



PGPDataType._AddElement(pyxb.binding.basis.element(pyxb.namespace.ExpandedName(Namespace, u'PGPKeyID'), pyxb.binding.datatypes.base64Binary, scope=PGPDataType))

PGPDataType._AddElement(pyxb.binding.basis.element(pyxb.namespace.ExpandedName(Namespace, u'PGPKeyPacket'), pyxb.binding.datatypes.base64Binary, scope=PGPDataType))
PGPDataType._GroupModel_ = pyxb.binding.content.GroupSequence(
    pyxb.binding.content.ParticleModel(PGPDataType._UseForTag(pyxb.namespace.ExpandedName(Namespace, u'PGPKeyID')), min_occurs=1, max_occurs=1),
    pyxb.binding.content.ParticleModel(PGPDataType._UseForTag(pyxb.namespace.ExpandedName(Namespace, u'PGPKeyPacket')), min_occurs=0L, max_occurs=1),
    pyxb.binding.content.ParticleModel(pyxb.binding.content.Wildcard(process_contents=pyxb.binding.content.Wildcard.PC_lax, namespace_constraint=(pyxb.binding.content.Wildcard.NC_not, u'http://www.w3.org/2000/09/xmldsig#')), min_occurs=0L, max_occurs=None)
    )
PGPDataType._GroupModel_2 = pyxb.binding.content.GroupSequence(
    pyxb.binding.content.ParticleModel(PGPDataType._UseForTag(pyxb.namespace.ExpandedName(Namespace, u'PGPKeyPacket')), min_occurs=1, max_occurs=1),
    pyxb.binding.content.ParticleModel(pyxb.binding.content.Wildcard(process_contents=pyxb.binding.content.Wildcard.PC_lax, namespace_constraint=(pyxb.binding.content.Wildcard.NC_not, u'http://www.w3.org/2000/09/xmldsig#')), min_occurs=0L, max_occurs=None)
    )
PGPDataType._GroupModel = pyxb.binding.content.GroupChoice(
    pyxb.binding.content.ParticleModel(PGPDataType._GroupModel_, min_occurs=1, max_occurs=1),
    pyxb.binding.content.ParticleModel(PGPDataType._GroupModel_2, min_occurs=1, max_occurs=1)
    )
PGPDataType._ContentModel = pyxb.binding.content.ParticleModel(PGPDataType._GroupModel, min_occurs=1, max_occurs=1)



ReferenceType._AddElement(pyxb.binding.basis.element(pyxb.namespace.ExpandedName(Namespace, u'DigestMethod'), DigestMethodType, scope=ReferenceType))

ReferenceType._AddElement(pyxb.binding.basis.element(pyxb.namespace.ExpandedName(Namespace, u'DigestValue'), DigestValueType, scope=ReferenceType))

ReferenceType._AddElement(pyxb.binding.basis.element(pyxb.namespace.ExpandedName(Namespace, u'Transforms'), TransformsType, scope=ReferenceType))
ReferenceType._GroupModel = pyxb.binding.content.GroupSequence(
    pyxb.binding.content.ParticleModel(ReferenceType._UseForTag(pyxb.namespace.ExpandedName(Namespace, u'Transforms')), min_occurs=0L, max_occurs=1),
    pyxb.binding.content.ParticleModel(ReferenceType._UseForTag(pyxb.namespace.ExpandedName(Namespace, u'DigestMethod')), min_occurs=1, max_occurs=1),
    pyxb.binding.content.ParticleModel(ReferenceType._UseForTag(pyxb.namespace.ExpandedName(Namespace, u'DigestValue')), min_occurs=1, max_occurs=1)
    )
ReferenceType._ContentModel = pyxb.binding.content.ParticleModel(ReferenceType._GroupModel, min_occurs=1, max_occurs=1)



SPKIDataType._AddElement(pyxb.binding.basis.element(pyxb.namespace.ExpandedName(Namespace, u'SPKISexp'), pyxb.binding.datatypes.base64Binary, scope=SPKIDataType))
SPKIDataType._GroupModel = pyxb.binding.content.GroupSequence(
    pyxb.binding.content.ParticleModel(SPKIDataType._UseForTag(pyxb.namespace.ExpandedName(Namespace, u'SPKISexp')), min_occurs=1, max_occurs=1),
    pyxb.binding.content.ParticleModel(pyxb.binding.content.Wildcard(process_contents=pyxb.binding.content.Wildcard.PC_lax, namespace_constraint=(pyxb.binding.content.Wildcard.NC_not, u'http://www.w3.org/2000/09/xmldsig#')), min_occurs=0L, max_occurs=1)
    )
SPKIDataType._ContentModel = pyxb.binding.content.ParticleModel(SPKIDataType._GroupModel, min_occurs=1, max_occurs=None)



RSAKeyValueType._AddElement(pyxb.binding.basis.element(pyxb.namespace.ExpandedName(Namespace, u'Exponent'), CryptoBinary, scope=RSAKeyValueType))

RSAKeyValueType._AddElement(pyxb.binding.basis.element(pyxb.namespace.ExpandedName(Namespace, u'Modulus'), CryptoBinary, scope=RSAKeyValueType))
RSAKeyValueType._GroupModel = pyxb.binding.content.GroupSequence(
    pyxb.binding.content.ParticleModel(RSAKeyValueType._UseForTag(pyxb.namespace.ExpandedName(Namespace, u'Modulus')), min_occurs=1, max_occurs=1),
    pyxb.binding.content.ParticleModel(RSAKeyValueType._UseForTag(pyxb.namespace.ExpandedName(Namespace, u'Exponent')), min_occurs=1, max_occurs=1)
    )
RSAKeyValueType._ContentModel = pyxb.binding.content.ParticleModel(RSAKeyValueType._GroupModel, min_occurs=1, max_occurs=1)



KeyInfoType._AddElement(pyxb.binding.basis.element(pyxb.namespace.ExpandedName(Namespace, u'PGPData'), PGPDataType, scope=KeyInfoType))

KeyInfoType._AddElement(pyxb.binding.basis.element(pyxb.namespace.ExpandedName(Namespace, u'RetrievalMethod'), RetrievalMethodType, scope=KeyInfoType))

KeyInfoType._AddElement(pyxb.binding.basis.element(pyxb.namespace.ExpandedName(Namespace, u'SPKIData'), SPKIDataType, scope=KeyInfoType))

KeyInfoType._AddElement(pyxb.binding.basis.element(pyxb.namespace.ExpandedName(Namespace, u'KeyName'), pyxb.binding.datatypes.string, scope=KeyInfoType))

KeyInfoType._AddElement(pyxb.binding.basis.element(pyxb.namespace.ExpandedName(Namespace, u'X509Data'), X509DataType, scope=KeyInfoType))

KeyInfoType._AddElement(pyxb.binding.basis.element(pyxb.namespace.ExpandedName(Namespace, u'MgmtData'), pyxb.binding.datatypes.string, scope=KeyInfoType))

KeyInfoType._AddElement(pyxb.binding.basis.element(pyxb.namespace.ExpandedName(Namespace, u'KeyValue'), KeyValueType, scope=KeyInfoType))
KeyInfoType._GroupModel = pyxb.binding.content.GroupChoice(
    pyxb.binding.content.ParticleModel(KeyInfoType._UseForTag(pyxb.namespace.ExpandedName(Namespace, u'KeyName')), min_occurs=1, max_occurs=1),
    pyxb.binding.content.ParticleModel(KeyInfoType._UseForTag(pyxb.namespace.ExpandedName(Namespace, u'KeyValue')), min_occurs=1, max_occurs=1),
    pyxb.binding.content.ParticleModel(KeyInfoType._UseForTag(pyxb.namespace.ExpandedName(Namespace, u'RetrievalMethod')), min_occurs=1, max_occurs=1),
    pyxb.binding.content.ParticleModel(KeyInfoType._UseForTag(pyxb.namespace.ExpandedName(Namespace, u'X509Data')), min_occurs=1, max_occurs=1),
    pyxb.binding.content.ParticleModel(KeyInfoType._UseForTag(pyxb.namespace.ExpandedName(Namespace, u'PGPData')), min_occurs=1, max_occurs=1),
    pyxb.binding.content.ParticleModel(KeyInfoType._UseForTag(pyxb.namespace.ExpandedName(Namespace, u'SPKIData')), min_occurs=1, max_occurs=1),
    pyxb.binding.content.ParticleModel(KeyInfoType._UseForTag(pyxb.namespace.ExpandedName(Namespace, u'MgmtData')), min_occurs=1, max_occurs=1),
    pyxb.binding.content.ParticleModel(pyxb.binding.content.Wildcard(process_contents=pyxb.binding.content.Wildcard.PC_lax, namespace_constraint=(pyxb.binding.content.Wildcard.NC_not, u'http://www.w3.org/2000/09/xmldsig#')), min_occurs=1, max_occurs=1)
    )
KeyInfoType._ContentModel = pyxb.binding.content.ParticleModel(KeyInfoType._GroupModel, min_occurs=1, max_occurs=None)



X509DataType._AddElement(pyxb.binding.basis.element(pyxb.namespace.ExpandedName(Namespace, u'X509IssuerSerial'), X509IssuerSerialType, scope=X509DataType))

X509DataType._AddElement(pyxb.binding.basis.element(pyxb.namespace.ExpandedName(Namespace, u'X509SKI'), pyxb.binding.datatypes.base64Binary, scope=X509DataType))

X509DataType._AddElement(pyxb.binding.basis.element(pyxb.namespace.ExpandedName(Namespace, u'X509SubjectName'), pyxb.binding.datatypes.string, scope=X509DataType))

X509DataType._AddElement(pyxb.binding.basis.element(pyxb.namespace.ExpandedName(Namespace, u'X509Certificate'), pyxb.binding.datatypes.base64Binary, scope=X509DataType))

X509DataType._AddElement(pyxb.binding.basis.element(pyxb.namespace.ExpandedName(Namespace, u'X509CRL'), pyxb.binding.datatypes.base64Binary, scope=X509DataType))
X509DataType._GroupModel_ = pyxb.binding.content.GroupChoice(
    pyxb.binding.content.ParticleModel(X509DataType._UseForTag(pyxb.namespace.ExpandedName(Namespace, u'X509IssuerSerial')), min_occurs=1, max_occurs=1),
    pyxb.binding.content.ParticleModel(X509DataType._UseForTag(pyxb.namespace.ExpandedName(Namespace, u'X509SKI')), min_occurs=1, max_occurs=1),
    pyxb.binding.content.ParticleModel(X509DataType._UseForTag(pyxb.namespace.ExpandedName(Namespace, u'X509SubjectName')), min_occurs=1, max_occurs=1),
    pyxb.binding.content.ParticleModel(X509DataType._UseForTag(pyxb.namespace.ExpandedName(Namespace, u'X509Certificate')), min_occurs=1, max_occurs=1),
    pyxb.binding.content.ParticleModel(X509DataType._UseForTag(pyxb.namespace.ExpandedName(Namespace, u'X509CRL')), min_occurs=1, max_occurs=1),
    pyxb.binding.content.ParticleModel(pyxb.binding.content.Wildcard(process_contents=pyxb.binding.content.Wildcard.PC_lax, namespace_constraint=(pyxb.binding.content.Wildcard.NC_not, u'http://www.w3.org/2000/09/xmldsig#')), min_occurs=1, max_occurs=1)
    )
X509DataType._GroupModel = pyxb.binding.content.GroupSequence(
    pyxb.binding.content.ParticleModel(X509DataType._GroupModel_, min_occurs=1, max_occurs=1)
    )
X509DataType._ContentModel = pyxb.binding.content.ParticleModel(X509DataType._GroupModel, min_occurs=1, max_occurs=None)



SignedInfoType._AddElement(pyxb.binding.basis.element(pyxb.namespace.ExpandedName(Namespace, u'CanonicalizationMethod'), CanonicalizationMethodType, scope=SignedInfoType))

SignedInfoType._AddElement(pyxb.binding.basis.element(pyxb.namespace.ExpandedName(Namespace, u'Reference'), ReferenceType, scope=SignedInfoType))

SignedInfoType._AddElement(pyxb.binding.basis.element(pyxb.namespace.ExpandedName(Namespace, u'SignatureMethod'), SignatureMethodType, scope=SignedInfoType))
SignedInfoType._GroupModel = pyxb.binding.content.GroupSequence(
    pyxb.binding.content.ParticleModel(SignedInfoType._UseForTag(pyxb.namespace.ExpandedName(Namespace, u'CanonicalizationMethod')), min_occurs=1, max_occurs=1),
    pyxb.binding.content.ParticleModel(SignedInfoType._UseForTag(pyxb.namespace.ExpandedName(Namespace, u'SignatureMethod')), min_occurs=1, max_occurs=1),
    pyxb.binding.content.ParticleModel(SignedInfoType._UseForTag(pyxb.namespace.ExpandedName(Namespace, u'Reference')), min_occurs=1, max_occurs=None)
    )
SignedInfoType._ContentModel = pyxb.binding.content.ParticleModel(SignedInfoType._GroupModel, min_occurs=1, max_occurs=1)



X509IssuerSerialType._AddElement(pyxb.binding.basis.element(pyxb.namespace.ExpandedName(Namespace, u'X509SerialNumber'), pyxb.binding.datatypes.integer, scope=X509IssuerSerialType))

X509IssuerSerialType._AddElement(pyxb.binding.basis.element(pyxb.namespace.ExpandedName(Namespace, u'X509IssuerName'), pyxb.binding.datatypes.string, scope=X509IssuerSerialType))
X509IssuerSerialType._GroupModel = pyxb.binding.content.GroupSequence(
    pyxb.binding.content.ParticleModel(X509IssuerSerialType._UseForTag(pyxb.namespace.ExpandedName(Namespace, u'X509IssuerName')), min_occurs=1, max_occurs=1),
    pyxb.binding.content.ParticleModel(X509IssuerSerialType._UseForTag(pyxb.namespace.ExpandedName(Namespace, u'X509SerialNumber')), min_occurs=1, max_occurs=1)
    )
X509IssuerSerialType._ContentModel = pyxb.binding.content.ParticleModel(X509IssuerSerialType._GroupModel, min_occurs=1, max_occurs=1)



SignatureMethodType._AddElement(pyxb.binding.basis.element(pyxb.namespace.ExpandedName(Namespace, u'HMACOutputLength'), HMACOutputLengthType, scope=SignatureMethodType))
SignatureMethodType._GroupModel = pyxb.binding.content.GroupSequence(
    pyxb.binding.content.ParticleModel(SignatureMethodType._UseForTag(pyxb.namespace.ExpandedName(Namespace, u'HMACOutputLength')), min_occurs=0L, max_occurs=1),
    pyxb.binding.content.ParticleModel(pyxb.binding.content.Wildcard(process_contents=pyxb.binding.content.Wildcard.PC_strict, namespace_constraint=(pyxb.binding.content.Wildcard.NC_not, u'http://www.w3.org/2000/09/xmldsig#')), min_occurs=0L, max_occurs=None)
    )
SignatureMethodType._ContentModel = pyxb.binding.content.ParticleModel(SignatureMethodType._GroupModel, min_occurs=1, max_occurs=1)



SignatureType._AddElement(pyxb.binding.basis.element(pyxb.namespace.ExpandedName(Namespace, u'Object'), ObjectType, scope=SignatureType))

SignatureType._AddElement(pyxb.binding.basis.element(pyxb.namespace.ExpandedName(Namespace, u'SignedInfo'), SignedInfoType, scope=SignatureType))

SignatureType._AddElement(pyxb.binding.basis.element(pyxb.namespace.ExpandedName(Namespace, u'KeyInfo'), KeyInfoType, scope=SignatureType))

SignatureType._AddElement(pyxb.binding.basis.element(pyxb.namespace.ExpandedName(Namespace, u'SignatureValue'), SignatureValueType, scope=SignatureType))
SignatureType._GroupModel = pyxb.binding.content.GroupSequence(
    pyxb.binding.content.ParticleModel(SignatureType._UseForTag(pyxb.namespace.ExpandedName(Namespace, u'SignedInfo')), min_occurs=1, max_occurs=1),
    pyxb.binding.content.ParticleModel(SignatureType._UseForTag(pyxb.namespace.ExpandedName(Namespace, u'SignatureValue')), min_occurs=1, max_occurs=1),
    pyxb.binding.content.ParticleModel(SignatureType._UseForTag(pyxb.namespace.ExpandedName(Namespace, u'KeyInfo')), min_occurs=0L, max_occurs=1),
    pyxb.binding.content.ParticleModel(SignatureType._UseForTag(pyxb.namespace.ExpandedName(Namespace, u'Object')), min_occurs=0L, max_occurs=None)
    )
SignatureType._ContentModel = pyxb.binding.content.ParticleModel(SignatureType._GroupModel, min_occurs=1, max_occurs=1)



SignaturePropertiesType._AddElement(pyxb.binding.basis.element(pyxb.namespace.ExpandedName(Namespace, u'SignatureProperty'), SignaturePropertyType, scope=SignaturePropertiesType))
SignaturePropertiesType._GroupModel = pyxb.binding.content.GroupSequence(
    pyxb.binding.content.ParticleModel(SignaturePropertiesType._UseForTag(pyxb.namespace.ExpandedName(Namespace, u'SignatureProperty')), min_occurs=1, max_occurs=None)
    )
SignaturePropertiesType._ContentModel = pyxb.binding.content.ParticleModel(SignaturePropertiesType._GroupModel, min_occurs=1, max_occurs=1)



TransformsType._AddElement(pyxb.binding.basis.element(pyxb.namespace.ExpandedName(Namespace, u'Transform'), TransformType, scope=TransformsType))
TransformsType._GroupModel = pyxb.binding.content.GroupSequence(
    pyxb.binding.content.ParticleModel(TransformsType._UseForTag(pyxb.namespace.ExpandedName(Namespace, u'Transform')), min_occurs=1, max_occurs=None)
    )
TransformsType._ContentModel = pyxb.binding.content.ParticleModel(TransformsType._GroupModel, min_occurs=1, max_occurs=1)


DigestMethodType._GroupModel = pyxb.binding.content.GroupSequence(
    pyxb.binding.content.ParticleModel(pyxb.binding.content.Wildcard(process_contents=pyxb.binding.content.Wildcard.PC_lax, namespace_constraint=(pyxb.binding.content.Wildcard.NC_not, u'http://www.w3.org/2000/09/xmldsig#')), min_occurs=0L, max_occurs=None)
    )
DigestMethodType._ContentModel = pyxb.binding.content.ParticleModel(DigestMethodType._GroupModel, min_occurs=1, max_occurs=1)


ObjectType._GroupModel = pyxb.binding.content.GroupSequence(
    pyxb.binding.content.ParticleModel(pyxb.binding.content.Wildcard(process_contents=pyxb.binding.content.Wildcard.PC_lax, namespace_constraint=pyxb.binding.content.Wildcard.NC_any), min_occurs=1, max_occurs=1)
    )
ObjectType._ContentModel = pyxb.binding.content.ParticleModel(ObjectType._GroupModel, min_occurs=0L, max_occurs=None)


SignaturePropertyType._GroupModel = pyxb.binding.content.GroupChoice(
    pyxb.binding.content.ParticleModel(pyxb.binding.content.Wildcard(process_contents=pyxb.binding.content.Wildcard.PC_lax, namespace_constraint=(pyxb.binding.content.Wildcard.NC_not, u'http://www.w3.org/2000/09/xmldsig#')), min_occurs=1, max_occurs=1)
    )
SignaturePropertyType._ContentModel = pyxb.binding.content.ParticleModel(SignaturePropertyType._GroupModel, min_occurs=1, max_occurs=None)



KeyValueType._AddElement(pyxb.binding.basis.element(pyxb.namespace.ExpandedName(Namespace, u'RSAKeyValue'), RSAKeyValueType, scope=KeyValueType))

KeyValueType._AddElement(pyxb.binding.basis.element(pyxb.namespace.ExpandedName(Namespace, u'DSAKeyValue'), DSAKeyValueType, scope=KeyValueType))
KeyValueType._GroupModel = pyxb.binding.content.GroupChoice(
    pyxb.binding.content.ParticleModel(KeyValueType._UseForTag(pyxb.namespace.ExpandedName(Namespace, u'DSAKeyValue')), min_occurs=1, max_occurs=1),
    pyxb.binding.content.ParticleModel(KeyValueType._UseForTag(pyxb.namespace.ExpandedName(Namespace, u'RSAKeyValue')), min_occurs=1, max_occurs=1),
    pyxb.binding.content.ParticleModel(pyxb.binding.content.Wildcard(process_contents=pyxb.binding.content.Wildcard.PC_lax, namespace_constraint=(pyxb.binding.content.Wildcard.NC_not, u'http://www.w3.org/2000/09/xmldsig#')), min_occurs=1, max_occurs=1)
    )
KeyValueType._ContentModel = pyxb.binding.content.ParticleModel(KeyValueType._GroupModel, min_occurs=1, max_occurs=1)



RetrievalMethodType._AddElement(pyxb.binding.basis.element(pyxb.namespace.ExpandedName(Namespace, u'Transforms'), TransformsType, scope=RetrievalMethodType))
RetrievalMethodType._GroupModel = pyxb.binding.content.GroupSequence(
    pyxb.binding.content.ParticleModel(RetrievalMethodType._UseForTag(pyxb.namespace.ExpandedName(Namespace, u'Transforms')), min_occurs=0L, max_occurs=1)
    )
RetrievalMethodType._ContentModel = pyxb.binding.content.ParticleModel(RetrievalMethodType._GroupModel, min_occurs=1, max_occurs=1)



ManifestType._AddElement(pyxb.binding.basis.element(pyxb.namespace.ExpandedName(Namespace, u'Reference'), ReferenceType, scope=ManifestType))
ManifestType._GroupModel = pyxb.binding.content.GroupSequence(
    pyxb.binding.content.ParticleModel(ManifestType._UseForTag(pyxb.namespace.ExpandedName(Namespace, u'Reference')), min_occurs=1, max_occurs=None)
    )
ManifestType._ContentModel = pyxb.binding.content.ParticleModel(ManifestType._GroupModel, min_occurs=1, max_occurs=1)
