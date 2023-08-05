# ./pyxb/bundles/wssplat/raw/xenc.py
# -*- coding: utf-8 -*-
# PyXB bindings for NM:7ed00f02a5533309db63dc4da4f345e09e5bf96a
# Generated 2012-11-01 15:13:36.198085 by PyXB version 1.1.5
# Namespace http://www.w3.org/2001/04/xmlenc#

import pyxb
import pyxb.binding
import pyxb.binding.saxer
import StringIO
import pyxb.utils.utility
import pyxb.utils.domutils
import sys

# Unique identifier for bindings created at the same time
_GenerationUID = pyxb.utils.utility.UniqueIdentifier('urn:uuid:9e0cbdb6-2460-11e2-beeb-c8600024e903')

# Import bindings for namespaces imported into schema
import pyxb.binding.datatypes
import pyxb.bundles.wssplat.ds

Namespace = pyxb.namespace.NamespaceForURI(u'http://www.w3.org/2001/04/xmlenc#', create_if_missing=True)
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


# Atomic simple type: {http://www.w3.org/2001/04/xmlenc#}KeySizeType
class KeySizeType (pyxb.binding.datatypes.integer):

    """An atomic simple type."""

    _ExpandedName = pyxb.namespace.ExpandedName(Namespace, u'KeySizeType')
    _DefinitionLocation = pyxb.utils.utility.Location('/tmp/pyxbdist.RHB65sy/PyXB-1.1.5/pyxb/bundles/wssplat/schemas/xenc.xsd', 45, 4)
    _Documentation = None
KeySizeType._InitializeFacetMap()
Namespace.addCategoryObject('typeBinding', u'KeySizeType', KeySizeType)

# Complex type {http://www.w3.org/2001/04/xmlenc#}CipherReferenceType with content type ELEMENT_ONLY
class CipherReferenceType (pyxb.binding.basis.complexTypeDefinition):
    _TypeDefinition = None
    _ContentTypeTag = pyxb.binding.basis.complexTypeDefinition._CT_ELEMENT_ONLY
    _Abstract = False
    _ExpandedName = pyxb.namespace.ExpandedName(Namespace, u'CipherReferenceType')
    _DefinitionLocation = pyxb.utils.utility.Location('/tmp/pyxbdist.RHB65sy/PyXB-1.1.5/pyxb/bundles/wssplat/schemas/xenc.xsd', 58, 3)
    # Base type is pyxb.binding.datatypes.anyType
    
    # Element {http://www.w3.org/2001/04/xmlenc#}Transforms uses Python identifier Transforms
    __Transforms = pyxb.binding.content.ElementUse(pyxb.namespace.ExpandedName(Namespace, u'Transforms'), 'Transforms', '__httpwww_w3_org200104xmlenc_CipherReferenceType_httpwww_w3_org200104xmlencTransforms', False)
    __Transforms._DeclarationLocation = pyxb.utils.utility.Location('/tmp/pyxbdist.RHB65sy/PyXB-1.1.5/pyxb/bundles/wssplat/schemas/xenc.xsd', 60, 9)
    __Transforms._UseLocation = pyxb.utils.utility.Location('/tmp/pyxbdist.RHB65sy/PyXB-1.1.5/pyxb/bundles/wssplat/schemas/xenc.xsd', 59, 7)

    
    Transforms = property(__Transforms.value, __Transforms.set, None, None)

    
    # Attribute URI uses Python identifier URI
    __URI = pyxb.binding.content.AttributeUse(pyxb.namespace.ExpandedName(None, u'URI'), 'URI', '__httpwww_w3_org200104xmlenc_CipherReferenceType_URI', pyxb.binding.datatypes.anyURI, required=True)
    __URI._DeclarationLocation = pyxb.utils.utility.Location('/tmp/pyxbdist.RHB65sy/PyXB-1.1.5/pyxb/bundles/wssplat/schemas/xenc.xsd', 62, 7)
    __URI._UseLocation = pyxb.utils.utility.Location('/tmp/pyxbdist.RHB65sy/PyXB-1.1.5/pyxb/bundles/wssplat/schemas/xenc.xsd', 62, 7)
    
    URI = property(__URI.value, __URI.set, None, None)


    _ElementMap = {
        __Transforms.name() : __Transforms
    }
    _AttributeMap = {
        __URI.name() : __URI
    }
Namespace.addCategoryObject('typeBinding', u'CipherReferenceType', CipherReferenceType)


# Complex type {http://www.w3.org/2001/04/xmlenc#}AgreementMethodType with content type MIXED
class AgreementMethodType (pyxb.binding.basis.complexTypeDefinition):
    _TypeDefinition = None
    _ContentTypeTag = pyxb.binding.basis.complexTypeDefinition._CT_MIXED
    _Abstract = False
    _ExpandedName = pyxb.namespace.ExpandedName(Namespace, u'AgreementMethodType')
    _DefinitionLocation = pyxb.utils.utility.Location('/tmp/pyxbdist.RHB65sy/PyXB-1.1.5/pyxb/bundles/wssplat/schemas/xenc.xsd', 97, 4)
    # Base type is pyxb.binding.datatypes.anyType
    
    # Element {http://www.w3.org/2001/04/xmlenc#}RecipientKeyInfo uses Python identifier RecipientKeyInfo
    __RecipientKeyInfo = pyxb.binding.content.ElementUse(pyxb.namespace.ExpandedName(Namespace, u'RecipientKeyInfo'), 'RecipientKeyInfo', '__httpwww_w3_org200104xmlenc_AgreementMethodType_httpwww_w3_org200104xmlencRecipientKeyInfo', False)
    __RecipientKeyInfo._DeclarationLocation = pyxb.utils.utility.Location('/tmp/pyxbdist.RHB65sy/PyXB-1.1.5/pyxb/bundles/wssplat/schemas/xenc.xsd', 103, 8)
    __RecipientKeyInfo._UseLocation = pyxb.utils.utility.Location('/tmp/pyxbdist.RHB65sy/PyXB-1.1.5/pyxb/bundles/wssplat/schemas/xenc.xsd', 98, 6)

    
    RecipientKeyInfo = property(__RecipientKeyInfo.value, __RecipientKeyInfo.set, None, None)

    
    # Element {http://www.w3.org/2001/04/xmlenc#}OriginatorKeyInfo uses Python identifier OriginatorKeyInfo
    __OriginatorKeyInfo = pyxb.binding.content.ElementUse(pyxb.namespace.ExpandedName(Namespace, u'OriginatorKeyInfo'), 'OriginatorKeyInfo', '__httpwww_w3_org200104xmlenc_AgreementMethodType_httpwww_w3_org200104xmlencOriginatorKeyInfo', False)
    __OriginatorKeyInfo._DeclarationLocation = pyxb.utils.utility.Location('/tmp/pyxbdist.RHB65sy/PyXB-1.1.5/pyxb/bundles/wssplat/schemas/xenc.xsd', 102, 8)
    __OriginatorKeyInfo._UseLocation = pyxb.utils.utility.Location('/tmp/pyxbdist.RHB65sy/PyXB-1.1.5/pyxb/bundles/wssplat/schemas/xenc.xsd', 98, 6)

    
    OriginatorKeyInfo = property(__OriginatorKeyInfo.value, __OriginatorKeyInfo.set, None, None)

    
    # Element {http://www.w3.org/2001/04/xmlenc#}KA-Nonce uses Python identifier KA_Nonce
    __KA_Nonce = pyxb.binding.content.ElementUse(pyxb.namespace.ExpandedName(Namespace, u'KA-Nonce'), 'KA_Nonce', '__httpwww_w3_org200104xmlenc_AgreementMethodType_httpwww_w3_org200104xmlencKA_Nonce', False)
    __KA_Nonce._DeclarationLocation = pyxb.utils.utility.Location('/tmp/pyxbdist.RHB65sy/PyXB-1.1.5/pyxb/bundles/wssplat/schemas/xenc.xsd', 99, 8)
    __KA_Nonce._UseLocation = pyxb.utils.utility.Location('/tmp/pyxbdist.RHB65sy/PyXB-1.1.5/pyxb/bundles/wssplat/schemas/xenc.xsd', 98, 6)

    
    KA_Nonce = property(__KA_Nonce.value, __KA_Nonce.set, None, None)

    
    # Attribute Algorithm uses Python identifier Algorithm
    __Algorithm = pyxb.binding.content.AttributeUse(pyxb.namespace.ExpandedName(None, u'Algorithm'), 'Algorithm', '__httpwww_w3_org200104xmlenc_AgreementMethodType_Algorithm', pyxb.binding.datatypes.anyURI, required=True)
    __Algorithm._DeclarationLocation = pyxb.utils.utility.Location('/tmp/pyxbdist.RHB65sy/PyXB-1.1.5/pyxb/bundles/wssplat/schemas/xenc.xsd', 105, 6)
    __Algorithm._UseLocation = pyxb.utils.utility.Location('/tmp/pyxbdist.RHB65sy/PyXB-1.1.5/pyxb/bundles/wssplat/schemas/xenc.xsd', 105, 6)
    
    Algorithm = property(__Algorithm.value, __Algorithm.set, None, None)

    _HasWildcardElement = True

    _ElementMap = {
        __RecipientKeyInfo.name() : __RecipientKeyInfo,
        __OriginatorKeyInfo.name() : __OriginatorKeyInfo,
        __KA_Nonce.name() : __KA_Nonce
    }
    _AttributeMap = {
        __Algorithm.name() : __Algorithm
    }
Namespace.addCategoryObject('typeBinding', u'AgreementMethodType', AgreementMethodType)


# Complex type {http://www.w3.org/2001/04/xmlenc#}CipherDataType with content type ELEMENT_ONLY
class CipherDataType (pyxb.binding.basis.complexTypeDefinition):
    _TypeDefinition = None
    _ContentTypeTag = pyxb.binding.basis.complexTypeDefinition._CT_ELEMENT_ONLY
    _Abstract = False
    _ExpandedName = pyxb.namespace.ExpandedName(Namespace, u'CipherDataType')
    _DefinitionLocation = pyxb.utils.utility.Location('/tmp/pyxbdist.RHB65sy/PyXB-1.1.5/pyxb/bundles/wssplat/schemas/xenc.xsd', 50, 2)
    # Base type is pyxb.binding.datatypes.anyType
    
    # Element {http://www.w3.org/2001/04/xmlenc#}CipherValue uses Python identifier CipherValue
    __CipherValue = pyxb.binding.content.ElementUse(pyxb.namespace.ExpandedName(Namespace, u'CipherValue'), 'CipherValue', '__httpwww_w3_org200104xmlenc_CipherDataType_httpwww_w3_org200104xmlencCipherValue', False)
    __CipherValue._DeclarationLocation = pyxb.utils.utility.Location('/tmp/pyxbdist.RHB65sy/PyXB-1.1.5/pyxb/bundles/wssplat/schemas/xenc.xsd', 52, 7)
    __CipherValue._UseLocation = pyxb.utils.utility.Location('/tmp/pyxbdist.RHB65sy/PyXB-1.1.5/pyxb/bundles/wssplat/schemas/xenc.xsd', 51, 5)

    
    CipherValue = property(__CipherValue.value, __CipherValue.set, None, None)

    
    # Element {http://www.w3.org/2001/04/xmlenc#}CipherReference uses Python identifier CipherReference
    __CipherReference = pyxb.binding.content.ElementUse(pyxb.namespace.ExpandedName(Namespace, u'CipherReference'), 'CipherReference', '__httpwww_w3_org200104xmlenc_CipherDataType_httpwww_w3_org200104xmlencCipherReference', False)
    __CipherReference._DeclarationLocation = pyxb.utils.utility.Location('/tmp/pyxbdist.RHB65sy/PyXB-1.1.5/pyxb/bundles/wssplat/schemas/xenc.xsd', 57, 3)
    __CipherReference._UseLocation = pyxb.utils.utility.Location('/tmp/pyxbdist.RHB65sy/PyXB-1.1.5/pyxb/bundles/wssplat/schemas/xenc.xsd', 51, 5)

    
    CipherReference = property(__CipherReference.value, __CipherReference.set, None, None)


    _ElementMap = {
        __CipherValue.name() : __CipherValue,
        __CipherReference.name() : __CipherReference
    }
    _AttributeMap = {
        
    }
Namespace.addCategoryObject('typeBinding', u'CipherDataType', CipherDataType)


# Complex type {http://www.w3.org/2001/04/xmlenc#}TransformsType with content type ELEMENT_ONLY
class TransformsType (pyxb.binding.basis.complexTypeDefinition):
    _TypeDefinition = None
    _ContentTypeTag = pyxb.binding.basis.complexTypeDefinition._CT_ELEMENT_ONLY
    _Abstract = False
    _ExpandedName = pyxb.namespace.ExpandedName(Namespace, u'TransformsType')
    _DefinitionLocation = pyxb.utils.utility.Location('/tmp/pyxbdist.RHB65sy/PyXB-1.1.5/pyxb/bundles/wssplat/schemas/xenc.xsd', 65, 5)
    # Base type is pyxb.binding.datatypes.anyType
    
    # Element {http://www.w3.org/2000/09/xmldsig#}Transform uses Python identifier Transform
    __Transform = pyxb.binding.content.ElementUse(pyxb.namespace.ExpandedName(pyxb.namespace.NamespaceForURI(u'http://www.w3.org/2000/09/xmldsig#'), u'Transform'), 'Transform', '__httpwww_w3_org200104xmlenc_TransformsType_httpwww_w3_org200009xmldsigTransform', True)
    __Transform._DeclarationLocation = pyxb.utils.utility.Location('/tmp/pyxbdist.RHB65sy/PyXB-1.1.5/pyxb/bundles/wssplat/schemas/ds.xsd', 115, 2)
    __Transform._UseLocation = pyxb.utils.utility.Location('/tmp/pyxbdist.RHB65sy/PyXB-1.1.5/pyxb/bundles/wssplat/schemas/xenc.xsd', 66, 7)

    
    Transform = property(__Transform.value, __Transform.set, None, None)


    _ElementMap = {
        __Transform.name() : __Transform
    }
    _AttributeMap = {
        
    }
Namespace.addCategoryObject('typeBinding', u'TransformsType', TransformsType)


# Complex type {http://www.w3.org/2001/04/xmlenc#}EncryptionPropertyType with content type MIXED
class EncryptionPropertyType (pyxb.binding.basis.complexTypeDefinition):
    _TypeDefinition = None
    _ContentTypeTag = pyxb.binding.basis.complexTypeDefinition._CT_MIXED
    _Abstract = False
    _ExpandedName = pyxb.namespace.ExpandedName(Namespace, u'EncryptionPropertyType')
    _DefinitionLocation = pyxb.utils.utility.Location('/tmp/pyxbdist.RHB65sy/PyXB-1.1.5/pyxb/bundles/wssplat/schemas/xenc.xsd', 136, 4)
    # Base type is pyxb.binding.datatypes.anyType
    
    # Attribute Target uses Python identifier Target
    __Target = pyxb.binding.content.AttributeUse(pyxb.namespace.ExpandedName(None, u'Target'), 'Target', '__httpwww_w3_org200104xmlenc_EncryptionPropertyType_Target', pyxb.binding.datatypes.anyURI)
    __Target._DeclarationLocation = pyxb.utils.utility.Location('/tmp/pyxbdist.RHB65sy/PyXB-1.1.5/pyxb/bundles/wssplat/schemas/xenc.xsd', 140, 6)
    __Target._UseLocation = pyxb.utils.utility.Location('/tmp/pyxbdist.RHB65sy/PyXB-1.1.5/pyxb/bundles/wssplat/schemas/xenc.xsd', 140, 6)
    
    Target = property(__Target.value, __Target.set, None, None)

    
    # Attribute Id uses Python identifier Id
    __Id = pyxb.binding.content.AttributeUse(pyxb.namespace.ExpandedName(None, u'Id'), 'Id', '__httpwww_w3_org200104xmlenc_EncryptionPropertyType_Id', pyxb.binding.datatypes.ID)
    __Id._DeclarationLocation = pyxb.utils.utility.Location('/tmp/pyxbdist.RHB65sy/PyXB-1.1.5/pyxb/bundles/wssplat/schemas/xenc.xsd', 141, 6)
    __Id._UseLocation = pyxb.utils.utility.Location('/tmp/pyxbdist.RHB65sy/PyXB-1.1.5/pyxb/bundles/wssplat/schemas/xenc.xsd', 141, 6)
    
    Id = property(__Id.value, __Id.set, None, None)

    _AttributeWildcard = pyxb.binding.content.Wildcard(process_contents=pyxb.binding.content.Wildcard.PC_strict, namespace_constraint=set(['http://www.w3.org/XML/1998/namespace']))
    _HasWildcardElement = True

    _ElementMap = {
        
    }
    _AttributeMap = {
        __Target.name() : __Target,
        __Id.name() : __Id
    }
Namespace.addCategoryObject('typeBinding', u'EncryptionPropertyType', EncryptionPropertyType)


# Complex type [anonymous] with content type ELEMENT_ONLY
class CTD_ANON (pyxb.binding.basis.complexTypeDefinition):
    _TypeDefinition = None
    _ContentTypeTag = pyxb.binding.basis.complexTypeDefinition._CT_ELEMENT_ONLY
    _Abstract = False
    _ExpandedName = None
    _DefinitionLocation = pyxb.utils.utility.Location('/tmp/pyxbdist.RHB65sy/PyXB-1.1.5/pyxb/bundles/wssplat/schemas/xenc.xsd', 111, 4)
    # Base type is pyxb.binding.datatypes.anyType
    
    # Element {http://www.w3.org/2001/04/xmlenc#}KeyReference uses Python identifier KeyReference
    __KeyReference = pyxb.binding.content.ElementUse(pyxb.namespace.ExpandedName(Namespace, u'KeyReference'), 'KeyReference', '__httpwww_w3_org200104xmlenc_CTD_ANON_httpwww_w3_org200104xmlencKeyReference', True)
    __KeyReference._DeclarationLocation = pyxb.utils.utility.Location('/tmp/pyxbdist.RHB65sy/PyXB-1.1.5/pyxb/bundles/wssplat/schemas/xenc.xsd', 114, 8)
    __KeyReference._UseLocation = pyxb.utils.utility.Location('/tmp/pyxbdist.RHB65sy/PyXB-1.1.5/pyxb/bundles/wssplat/schemas/xenc.xsd', 112, 6)

    
    KeyReference = property(__KeyReference.value, __KeyReference.set, None, None)

    
    # Element {http://www.w3.org/2001/04/xmlenc#}DataReference uses Python identifier DataReference
    __DataReference = pyxb.binding.content.ElementUse(pyxb.namespace.ExpandedName(Namespace, u'DataReference'), 'DataReference', '__httpwww_w3_org200104xmlenc_CTD_ANON_httpwww_w3_org200104xmlencDataReference', True)
    __DataReference._DeclarationLocation = pyxb.utils.utility.Location('/tmp/pyxbdist.RHB65sy/PyXB-1.1.5/pyxb/bundles/wssplat/schemas/xenc.xsd', 113, 8)
    __DataReference._UseLocation = pyxb.utils.utility.Location('/tmp/pyxbdist.RHB65sy/PyXB-1.1.5/pyxb/bundles/wssplat/schemas/xenc.xsd', 112, 6)

    
    DataReference = property(__DataReference.value, __DataReference.set, None, None)


    _ElementMap = {
        __KeyReference.name() : __KeyReference,
        __DataReference.name() : __DataReference
    }
    _AttributeMap = {
        
    }



# Complex type {http://www.w3.org/2001/04/xmlenc#}EncryptionMethodType with content type MIXED
class EncryptionMethodType (pyxb.binding.basis.complexTypeDefinition):
    _TypeDefinition = None
    _ContentTypeTag = pyxb.binding.basis.complexTypeDefinition._CT_MIXED
    _Abstract = False
    _ExpandedName = pyxb.namespace.ExpandedName(Namespace, u'EncryptionMethodType')
    _DefinitionLocation = pyxb.utils.utility.Location('/tmp/pyxbdist.RHB65sy/PyXB-1.1.5/pyxb/bundles/wssplat/schemas/xenc.xsd', 36, 2)
    # Base type is pyxb.binding.datatypes.anyType
    
    # Element {http://www.w3.org/2001/04/xmlenc#}KeySize uses Python identifier KeySize
    __KeySize = pyxb.binding.content.ElementUse(pyxb.namespace.ExpandedName(Namespace, u'KeySize'), 'KeySize', '__httpwww_w3_org200104xmlenc_EncryptionMethodType_httpwww_w3_org200104xmlencKeySize', False)
    __KeySize._DeclarationLocation = pyxb.utils.utility.Location('/tmp/pyxbdist.RHB65sy/PyXB-1.1.5/pyxb/bundles/wssplat/schemas/xenc.xsd', 38, 6)
    __KeySize._UseLocation = pyxb.utils.utility.Location('/tmp/pyxbdist.RHB65sy/PyXB-1.1.5/pyxb/bundles/wssplat/schemas/xenc.xsd', 37, 4)

    
    KeySize = property(__KeySize.value, __KeySize.set, None, None)

    
    # Element {http://www.w3.org/2001/04/xmlenc#}OAEPparams uses Python identifier OAEPparams
    __OAEPparams = pyxb.binding.content.ElementUse(pyxb.namespace.ExpandedName(Namespace, u'OAEPparams'), 'OAEPparams', '__httpwww_w3_org200104xmlenc_EncryptionMethodType_httpwww_w3_org200104xmlencOAEPparams', False)
    __OAEPparams._DeclarationLocation = pyxb.utils.utility.Location('/tmp/pyxbdist.RHB65sy/PyXB-1.1.5/pyxb/bundles/wssplat/schemas/xenc.xsd', 39, 6)
    __OAEPparams._UseLocation = pyxb.utils.utility.Location('/tmp/pyxbdist.RHB65sy/PyXB-1.1.5/pyxb/bundles/wssplat/schemas/xenc.xsd', 37, 4)

    
    OAEPparams = property(__OAEPparams.value, __OAEPparams.set, None, None)

    
    # Attribute Algorithm uses Python identifier Algorithm
    __Algorithm = pyxb.binding.content.AttributeUse(pyxb.namespace.ExpandedName(None, u'Algorithm'), 'Algorithm', '__httpwww_w3_org200104xmlenc_EncryptionMethodType_Algorithm', pyxb.binding.datatypes.anyURI, required=True)
    __Algorithm._DeclarationLocation = pyxb.utils.utility.Location('/tmp/pyxbdist.RHB65sy/PyXB-1.1.5/pyxb/bundles/wssplat/schemas/xenc.xsd', 42, 4)
    __Algorithm._UseLocation = pyxb.utils.utility.Location('/tmp/pyxbdist.RHB65sy/PyXB-1.1.5/pyxb/bundles/wssplat/schemas/xenc.xsd', 42, 4)
    
    Algorithm = property(__Algorithm.value, __Algorithm.set, None, None)

    _HasWildcardElement = True

    _ElementMap = {
        __KeySize.name() : __KeySize,
        __OAEPparams.name() : __OAEPparams
    }
    _AttributeMap = {
        __Algorithm.name() : __Algorithm
    }
Namespace.addCategoryObject('typeBinding', u'EncryptionMethodType', EncryptionMethodType)


# Complex type {http://www.w3.org/2001/04/xmlenc#}EncryptionPropertiesType with content type ELEMENT_ONLY
class EncryptionPropertiesType (pyxb.binding.basis.complexTypeDefinition):
    _TypeDefinition = None
    _ContentTypeTag = pyxb.binding.basis.complexTypeDefinition._CT_ELEMENT_ONLY
    _Abstract = False
    _ExpandedName = pyxb.namespace.ExpandedName(Namespace, u'EncryptionPropertiesType')
    _DefinitionLocation = pyxb.utils.utility.Location('/tmp/pyxbdist.RHB65sy/PyXB-1.1.5/pyxb/bundles/wssplat/schemas/xenc.xsd', 128, 2)
    # Base type is pyxb.binding.datatypes.anyType
    
    # Element {http://www.w3.org/2001/04/xmlenc#}EncryptionProperty uses Python identifier EncryptionProperty
    __EncryptionProperty = pyxb.binding.content.ElementUse(pyxb.namespace.ExpandedName(Namespace, u'EncryptionProperty'), 'EncryptionProperty', '__httpwww_w3_org200104xmlenc_EncryptionPropertiesType_httpwww_w3_org200104xmlencEncryptionProperty', True)
    __EncryptionProperty._DeclarationLocation = pyxb.utils.utility.Location('/tmp/pyxbdist.RHB65sy/PyXB-1.1.5/pyxb/bundles/wssplat/schemas/xenc.xsd', 135, 4)
    __EncryptionProperty._UseLocation = pyxb.utils.utility.Location('/tmp/pyxbdist.RHB65sy/PyXB-1.1.5/pyxb/bundles/wssplat/schemas/xenc.xsd', 129, 4)

    
    EncryptionProperty = property(__EncryptionProperty.value, __EncryptionProperty.set, None, None)

    
    # Attribute Id uses Python identifier Id
    __Id = pyxb.binding.content.AttributeUse(pyxb.namespace.ExpandedName(None, u'Id'), 'Id', '__httpwww_w3_org200104xmlenc_EncryptionPropertiesType_Id', pyxb.binding.datatypes.ID)
    __Id._DeclarationLocation = pyxb.utils.utility.Location('/tmp/pyxbdist.RHB65sy/PyXB-1.1.5/pyxb/bundles/wssplat/schemas/xenc.xsd', 132, 4)
    __Id._UseLocation = pyxb.utils.utility.Location('/tmp/pyxbdist.RHB65sy/PyXB-1.1.5/pyxb/bundles/wssplat/schemas/xenc.xsd', 132, 4)
    
    Id = property(__Id.value, __Id.set, None, None)


    _ElementMap = {
        __EncryptionProperty.name() : __EncryptionProperty
    }
    _AttributeMap = {
        __Id.name() : __Id
    }
Namespace.addCategoryObject('typeBinding', u'EncryptionPropertiesType', EncryptionPropertiesType)


# Complex type {http://www.w3.org/2001/04/xmlenc#}ReferenceType with content type ELEMENT_ONLY
class ReferenceType (pyxb.binding.basis.complexTypeDefinition):
    _TypeDefinition = None
    _ContentTypeTag = pyxb.binding.basis.complexTypeDefinition._CT_ELEMENT_ONLY
    _Abstract = False
    _ExpandedName = pyxb.namespace.ExpandedName(Namespace, u'ReferenceType')
    _DefinitionLocation = pyxb.utils.utility.Location('/tmp/pyxbdist.RHB65sy/PyXB-1.1.5/pyxb/bundles/wssplat/schemas/xenc.xsd', 119, 2)
    # Base type is pyxb.binding.datatypes.anyType
    
    # Attribute URI uses Python identifier URI
    __URI = pyxb.binding.content.AttributeUse(pyxb.namespace.ExpandedName(None, u'URI'), 'URI', '__httpwww_w3_org200104xmlenc_ReferenceType_URI', pyxb.binding.datatypes.anyURI, required=True)
    __URI._DeclarationLocation = pyxb.utils.utility.Location('/tmp/pyxbdist.RHB65sy/PyXB-1.1.5/pyxb/bundles/wssplat/schemas/xenc.xsd', 123, 4)
    __URI._UseLocation = pyxb.utils.utility.Location('/tmp/pyxbdist.RHB65sy/PyXB-1.1.5/pyxb/bundles/wssplat/schemas/xenc.xsd', 123, 4)
    
    URI = property(__URI.value, __URI.set, None, None)

    _HasWildcardElement = True

    _ElementMap = {
        
    }
    _AttributeMap = {
        __URI.name() : __URI
    }
Namespace.addCategoryObject('typeBinding', u'ReferenceType', ReferenceType)


# Complex type {http://www.w3.org/2001/04/xmlenc#}EncryptedType with content type ELEMENT_ONLY
class EncryptedType (pyxb.binding.basis.complexTypeDefinition):
    _TypeDefinition = None
    _ContentTypeTag = pyxb.binding.basis.complexTypeDefinition._CT_ELEMENT_ONLY
    _Abstract = True
    _ExpandedName = pyxb.namespace.ExpandedName(Namespace, u'EncryptedType')
    _DefinitionLocation = pyxb.utils.utility.Location('/tmp/pyxbdist.RHB65sy/PyXB-1.1.5/pyxb/bundles/wssplat/schemas/xenc.xsd', 22, 2)
    # Base type is pyxb.binding.datatypes.anyType
    
    # Element {http://www.w3.org/2001/04/xmlenc#}EncryptionMethod uses Python identifier EncryptionMethod
    __EncryptionMethod = pyxb.binding.content.ElementUse(pyxb.namespace.ExpandedName(Namespace, u'EncryptionMethod'), 'EncryptionMethod', '__httpwww_w3_org200104xmlenc_EncryptedType_httpwww_w3_org200104xmlencEncryptionMethod', False)
    __EncryptionMethod._DeclarationLocation = pyxb.utils.utility.Location('/tmp/pyxbdist.RHB65sy/PyXB-1.1.5/pyxb/bundles/wssplat/schemas/xenc.xsd', 24, 6)
    __EncryptionMethod._UseLocation = pyxb.utils.utility.Location('/tmp/pyxbdist.RHB65sy/PyXB-1.1.5/pyxb/bundles/wssplat/schemas/xenc.xsd', 23, 4)

    
    EncryptionMethod = property(__EncryptionMethod.value, __EncryptionMethod.set, None, None)

    
    # Element {http://www.w3.org/2001/04/xmlenc#}CipherData uses Python identifier CipherData
    __CipherData = pyxb.binding.content.ElementUse(pyxb.namespace.ExpandedName(Namespace, u'CipherData'), 'CipherData', '__httpwww_w3_org200104xmlenc_EncryptedType_httpwww_w3_org200104xmlencCipherData', False)
    __CipherData._DeclarationLocation = pyxb.utils.utility.Location('/tmp/pyxbdist.RHB65sy/PyXB-1.1.5/pyxb/bundles/wssplat/schemas/xenc.xsd', 49, 2)
    __CipherData._UseLocation = pyxb.utils.utility.Location('/tmp/pyxbdist.RHB65sy/PyXB-1.1.5/pyxb/bundles/wssplat/schemas/xenc.xsd', 23, 4)

    
    CipherData = property(__CipherData.value, __CipherData.set, None, None)

    
    # Element {http://www.w3.org/2000/09/xmldsig#}KeyInfo uses Python identifier KeyInfo
    __KeyInfo = pyxb.binding.content.ElementUse(pyxb.namespace.ExpandedName(pyxb.namespace.NamespaceForURI(u'http://www.w3.org/2000/09/xmldsig#'), u'KeyInfo'), 'KeyInfo', '__httpwww_w3_org200104xmlenc_EncryptedType_httpwww_w3_org200009xmldsigKeyInfo', False)
    __KeyInfo._DeclarationLocation = pyxb.utils.utility.Location('/tmp/pyxbdist.RHB65sy/PyXB-1.1.5/pyxb/bundles/wssplat/schemas/ds.xsd', 144, 0)
    __KeyInfo._UseLocation = pyxb.utils.utility.Location('/tmp/pyxbdist.RHB65sy/PyXB-1.1.5/pyxb/bundles/wssplat/schemas/xenc.xsd', 23, 4)

    
    KeyInfo = property(__KeyInfo.value, __KeyInfo.set, None, None)

    
    # Element {http://www.w3.org/2001/04/xmlenc#}EncryptionProperties uses Python identifier EncryptionProperties
    __EncryptionProperties = pyxb.binding.content.ElementUse(pyxb.namespace.ExpandedName(Namespace, u'EncryptionProperties'), 'EncryptionProperties', '__httpwww_w3_org200104xmlenc_EncryptedType_httpwww_w3_org200104xmlencEncryptionProperties', False)
    __EncryptionProperties._DeclarationLocation = pyxb.utils.utility.Location('/tmp/pyxbdist.RHB65sy/PyXB-1.1.5/pyxb/bundles/wssplat/schemas/xenc.xsd', 127, 2)
    __EncryptionProperties._UseLocation = pyxb.utils.utility.Location('/tmp/pyxbdist.RHB65sy/PyXB-1.1.5/pyxb/bundles/wssplat/schemas/xenc.xsd', 23, 4)

    
    EncryptionProperties = property(__EncryptionProperties.value, __EncryptionProperties.set, None, None)

    
    # Attribute MimeType uses Python identifier MimeType
    __MimeType = pyxb.binding.content.AttributeUse(pyxb.namespace.ExpandedName(None, u'MimeType'), 'MimeType', '__httpwww_w3_org200104xmlenc_EncryptedType_MimeType', pyxb.binding.datatypes.string)
    __MimeType._DeclarationLocation = pyxb.utils.utility.Location('/tmp/pyxbdist.RHB65sy/PyXB-1.1.5/pyxb/bundles/wssplat/schemas/xenc.xsd', 32, 4)
    __MimeType._UseLocation = pyxb.utils.utility.Location('/tmp/pyxbdist.RHB65sy/PyXB-1.1.5/pyxb/bundles/wssplat/schemas/xenc.xsd', 32, 4)
    
    MimeType = property(__MimeType.value, __MimeType.set, None, None)

    
    # Attribute Id uses Python identifier Id
    __Id = pyxb.binding.content.AttributeUse(pyxb.namespace.ExpandedName(None, u'Id'), 'Id', '__httpwww_w3_org200104xmlenc_EncryptedType_Id', pyxb.binding.datatypes.ID)
    __Id._DeclarationLocation = pyxb.utils.utility.Location('/tmp/pyxbdist.RHB65sy/PyXB-1.1.5/pyxb/bundles/wssplat/schemas/xenc.xsd', 30, 4)
    __Id._UseLocation = pyxb.utils.utility.Location('/tmp/pyxbdist.RHB65sy/PyXB-1.1.5/pyxb/bundles/wssplat/schemas/xenc.xsd', 30, 4)
    
    Id = property(__Id.value, __Id.set, None, None)

    
    # Attribute Encoding uses Python identifier Encoding
    __Encoding = pyxb.binding.content.AttributeUse(pyxb.namespace.ExpandedName(None, u'Encoding'), 'Encoding', '__httpwww_w3_org200104xmlenc_EncryptedType_Encoding', pyxb.binding.datatypes.anyURI)
    __Encoding._DeclarationLocation = pyxb.utils.utility.Location('/tmp/pyxbdist.RHB65sy/PyXB-1.1.5/pyxb/bundles/wssplat/schemas/xenc.xsd', 33, 4)
    __Encoding._UseLocation = pyxb.utils.utility.Location('/tmp/pyxbdist.RHB65sy/PyXB-1.1.5/pyxb/bundles/wssplat/schemas/xenc.xsd', 33, 4)
    
    Encoding = property(__Encoding.value, __Encoding.set, None, None)

    
    # Attribute Type uses Python identifier Type
    __Type = pyxb.binding.content.AttributeUse(pyxb.namespace.ExpandedName(None, u'Type'), 'Type', '__httpwww_w3_org200104xmlenc_EncryptedType_Type', pyxb.binding.datatypes.anyURI)
    __Type._DeclarationLocation = pyxb.utils.utility.Location('/tmp/pyxbdist.RHB65sy/PyXB-1.1.5/pyxb/bundles/wssplat/schemas/xenc.xsd', 31, 4)
    __Type._UseLocation = pyxb.utils.utility.Location('/tmp/pyxbdist.RHB65sy/PyXB-1.1.5/pyxb/bundles/wssplat/schemas/xenc.xsd', 31, 4)
    
    Type = property(__Type.value, __Type.set, None, None)


    _ElementMap = {
        __EncryptionMethod.name() : __EncryptionMethod,
        __CipherData.name() : __CipherData,
        __KeyInfo.name() : __KeyInfo,
        __EncryptionProperties.name() : __EncryptionProperties
    }
    _AttributeMap = {
        __MimeType.name() : __MimeType,
        __Id.name() : __Id,
        __Encoding.name() : __Encoding,
        __Type.name() : __Type
    }
Namespace.addCategoryObject('typeBinding', u'EncryptedType', EncryptedType)


# Complex type {http://www.w3.org/2001/04/xmlenc#}EncryptedDataType with content type ELEMENT_ONLY
class EncryptedDataType (EncryptedType):
    _TypeDefinition = None
    _ContentTypeTag = pyxb.binding.basis.complexTypeDefinition._CT_ELEMENT_ONLY
    _Abstract = False
    _ExpandedName = pyxb.namespace.ExpandedName(Namespace, u'EncryptedDataType')
    _DefinitionLocation = pyxb.utils.utility.Location('/tmp/pyxbdist.RHB65sy/PyXB-1.1.5/pyxb/bundles/wssplat/schemas/xenc.xsd', 73, 2)
    # Base type is EncryptedType
    
    # Element EncryptionMethod ({http://www.w3.org/2001/04/xmlenc#}EncryptionMethod) inherited from {http://www.w3.org/2001/04/xmlenc#}EncryptedType
    
    # Element CipherData ({http://www.w3.org/2001/04/xmlenc#}CipherData) inherited from {http://www.w3.org/2001/04/xmlenc#}EncryptedType
    
    # Element KeyInfo ({http://www.w3.org/2000/09/xmldsig#}KeyInfo) inherited from {http://www.w3.org/2001/04/xmlenc#}EncryptedType
    
    # Element EncryptionProperties ({http://www.w3.org/2001/04/xmlenc#}EncryptionProperties) inherited from {http://www.w3.org/2001/04/xmlenc#}EncryptedType
    
    # Attribute MimeType inherited from {http://www.w3.org/2001/04/xmlenc#}EncryptedType
    
    # Attribute Id inherited from {http://www.w3.org/2001/04/xmlenc#}EncryptedType
    
    # Attribute Encoding inherited from {http://www.w3.org/2001/04/xmlenc#}EncryptedType
    
    # Attribute Type inherited from {http://www.w3.org/2001/04/xmlenc#}EncryptedType

    _ElementMap = EncryptedType._ElementMap.copy()
    _ElementMap.update({
        
    })
    _AttributeMap = EncryptedType._AttributeMap.copy()
    _AttributeMap.update({
        
    })
Namespace.addCategoryObject('typeBinding', u'EncryptedDataType', EncryptedDataType)


# Complex type {http://www.w3.org/2001/04/xmlenc#}EncryptedKeyType with content type ELEMENT_ONLY
class EncryptedKeyType (EncryptedType):
    _TypeDefinition = None
    _ContentTypeTag = pyxb.binding.basis.complexTypeDefinition._CT_ELEMENT_ONLY
    _Abstract = False
    _ExpandedName = pyxb.namespace.ExpandedName(Namespace, u'EncryptedKeyType')
    _DefinitionLocation = pyxb.utils.utility.Location('/tmp/pyxbdist.RHB65sy/PyXB-1.1.5/pyxb/bundles/wssplat/schemas/xenc.xsd', 83, 2)
    # Base type is EncryptedType
    
    # Element KeyInfo ({http://www.w3.org/2000/09/xmldsig#}KeyInfo) inherited from {http://www.w3.org/2001/04/xmlenc#}EncryptedType
    
    # Element {http://www.w3.org/2001/04/xmlenc#}CarriedKeyName uses Python identifier CarriedKeyName
    __CarriedKeyName = pyxb.binding.content.ElementUse(pyxb.namespace.ExpandedName(Namespace, u'CarriedKeyName'), 'CarriedKeyName', '__httpwww_w3_org200104xmlenc_EncryptedKeyType_httpwww_w3_org200104xmlencCarriedKeyName', False)
    __CarriedKeyName._DeclarationLocation = pyxb.utils.utility.Location('/tmp/pyxbdist.RHB65sy/PyXB-1.1.5/pyxb/bundles/wssplat/schemas/xenc.xsd', 88, 10)
    __CarriedKeyName._UseLocation = None

    
    CarriedKeyName = property(__CarriedKeyName.value, __CarriedKeyName.set, None, None)

    
    # Element {http://www.w3.org/2001/04/xmlenc#}ReferenceList uses Python identifier ReferenceList
    __ReferenceList = pyxb.binding.content.ElementUse(pyxb.namespace.ExpandedName(Namespace, u'ReferenceList'), 'ReferenceList', '__httpwww_w3_org200104xmlenc_EncryptedKeyType_httpwww_w3_org200104xmlencReferenceList', False)
    __ReferenceList._DeclarationLocation = pyxb.utils.utility.Location('/tmp/pyxbdist.RHB65sy/PyXB-1.1.5/pyxb/bundles/wssplat/schemas/xenc.xsd', 110, 2)
    __ReferenceList._UseLocation = None

    
    ReferenceList = property(__ReferenceList.value, __ReferenceList.set, None, None)

    
    # Element CipherData ({http://www.w3.org/2001/04/xmlenc#}CipherData) inherited from {http://www.w3.org/2001/04/xmlenc#}EncryptedType
    
    # Element EncryptionMethod ({http://www.w3.org/2001/04/xmlenc#}EncryptionMethod) inherited from {http://www.w3.org/2001/04/xmlenc#}EncryptedType
    
    # Element EncryptionProperties ({http://www.w3.org/2001/04/xmlenc#}EncryptionProperties) inherited from {http://www.w3.org/2001/04/xmlenc#}EncryptedType
    
    # Attribute MimeType inherited from {http://www.w3.org/2001/04/xmlenc#}EncryptedType
    
    # Attribute Recipient uses Python identifier Recipient
    __Recipient = pyxb.binding.content.AttributeUse(pyxb.namespace.ExpandedName(None, u'Recipient'), 'Recipient', '__httpwww_w3_org200104xmlenc_EncryptedKeyType_Recipient', pyxb.binding.datatypes.string)
    __Recipient._DeclarationLocation = pyxb.utils.utility.Location('/tmp/pyxbdist.RHB65sy/PyXB-1.1.5/pyxb/bundles/wssplat/schemas/xenc.xsd', 90, 8)
    __Recipient._UseLocation = pyxb.utils.utility.Location('/tmp/pyxbdist.RHB65sy/PyXB-1.1.5/pyxb/bundles/wssplat/schemas/xenc.xsd', 90, 8)
    
    Recipient = property(__Recipient.value, __Recipient.set, None, None)

    
    # Attribute Id inherited from {http://www.w3.org/2001/04/xmlenc#}EncryptedType
    
    # Attribute Encoding inherited from {http://www.w3.org/2001/04/xmlenc#}EncryptedType
    
    # Attribute Type inherited from {http://www.w3.org/2001/04/xmlenc#}EncryptedType

    _ElementMap = EncryptedType._ElementMap.copy()
    _ElementMap.update({
        __CarriedKeyName.name() : __CarriedKeyName,
        __ReferenceList.name() : __ReferenceList
    })
    _AttributeMap = EncryptedType._AttributeMap.copy()
    _AttributeMap.update({
        __Recipient.name() : __Recipient
    })
Namespace.addCategoryObject('typeBinding', u'EncryptedKeyType', EncryptedKeyType)


AgreementMethod = pyxb.binding.basis.element(pyxb.namespace.ExpandedName(Namespace, u'AgreementMethod'), AgreementMethodType)
Namespace.addCategoryObject('elementBinding', AgreementMethod.name().localName(), AgreementMethod)

CipherData = pyxb.binding.basis.element(pyxb.namespace.ExpandedName(Namespace, u'CipherData'), CipherDataType)
Namespace.addCategoryObject('elementBinding', CipherData.name().localName(), CipherData)

EncryptionProperty = pyxb.binding.basis.element(pyxb.namespace.ExpandedName(Namespace, u'EncryptionProperty'), EncryptionPropertyType)
Namespace.addCategoryObject('elementBinding', EncryptionProperty.name().localName(), EncryptionProperty)

CipherReference = pyxb.binding.basis.element(pyxb.namespace.ExpandedName(Namespace, u'CipherReference'), CipherReferenceType)
Namespace.addCategoryObject('elementBinding', CipherReference.name().localName(), CipherReference)

ReferenceList = pyxb.binding.basis.element(pyxb.namespace.ExpandedName(Namespace, u'ReferenceList'), CTD_ANON)
Namespace.addCategoryObject('elementBinding', ReferenceList.name().localName(), ReferenceList)

EncryptedData = pyxb.binding.basis.element(pyxb.namespace.ExpandedName(Namespace, u'EncryptedData'), EncryptedDataType)
Namespace.addCategoryObject('elementBinding', EncryptedData.name().localName(), EncryptedData)

EncryptionProperties = pyxb.binding.basis.element(pyxb.namespace.ExpandedName(Namespace, u'EncryptionProperties'), EncryptionPropertiesType)
Namespace.addCategoryObject('elementBinding', EncryptionProperties.name().localName(), EncryptionProperties)

EncryptedKey = pyxb.binding.basis.element(pyxb.namespace.ExpandedName(Namespace, u'EncryptedKey'), EncryptedKeyType)
Namespace.addCategoryObject('elementBinding', EncryptedKey.name().localName(), EncryptedKey)



CipherReferenceType._AddElement(pyxb.binding.basis.element(pyxb.namespace.ExpandedName(Namespace, u'Transforms'), TransformsType, scope=CipherReferenceType))
CipherReferenceType._GroupModel = pyxb.binding.content.GroupChoice(
    pyxb.binding.content.ParticleModel(CipherReferenceType._UseForTag(pyxb.namespace.ExpandedName(Namespace, u'Transforms')), min_occurs=0L, max_occurs=1)
    )
CipherReferenceType._ContentModel = pyxb.binding.content.ParticleModel(CipherReferenceType._GroupModel, min_occurs=1, max_occurs=1)



AgreementMethodType._AddElement(pyxb.binding.basis.element(pyxb.namespace.ExpandedName(Namespace, u'RecipientKeyInfo'), pyxb.bundles.wssplat.ds.KeyInfoType, scope=AgreementMethodType))

AgreementMethodType._AddElement(pyxb.binding.basis.element(pyxb.namespace.ExpandedName(Namespace, u'OriginatorKeyInfo'), pyxb.bundles.wssplat.ds.KeyInfoType, scope=AgreementMethodType))

AgreementMethodType._AddElement(pyxb.binding.basis.element(pyxb.namespace.ExpandedName(Namespace, u'KA-Nonce'), pyxb.binding.datatypes.base64Binary, scope=AgreementMethodType))
AgreementMethodType._GroupModel = pyxb.binding.content.GroupSequence(
    pyxb.binding.content.ParticleModel(AgreementMethodType._UseForTag(pyxb.namespace.ExpandedName(Namespace, u'KA-Nonce')), min_occurs=0L, max_occurs=1),
    pyxb.binding.content.ParticleModel(pyxb.binding.content.Wildcard(process_contents=pyxb.binding.content.Wildcard.PC_strict, namespace_constraint=(pyxb.binding.content.Wildcard.NC_not, u'http://www.w3.org/2001/04/xmlenc#')), min_occurs=0L, max_occurs=None),
    pyxb.binding.content.ParticleModel(AgreementMethodType._UseForTag(pyxb.namespace.ExpandedName(Namespace, u'OriginatorKeyInfo')), min_occurs=0L, max_occurs=1),
    pyxb.binding.content.ParticleModel(AgreementMethodType._UseForTag(pyxb.namespace.ExpandedName(Namespace, u'RecipientKeyInfo')), min_occurs=0L, max_occurs=1)
    )
AgreementMethodType._ContentModel = pyxb.binding.content.ParticleModel(AgreementMethodType._GroupModel, min_occurs=1, max_occurs=1)



CipherDataType._AddElement(pyxb.binding.basis.element(pyxb.namespace.ExpandedName(Namespace, u'CipherValue'), pyxb.binding.datatypes.base64Binary, scope=CipherDataType))

CipherDataType._AddElement(pyxb.binding.basis.element(pyxb.namespace.ExpandedName(Namespace, u'CipherReference'), CipherReferenceType, scope=CipherDataType))
CipherDataType._GroupModel = pyxb.binding.content.GroupChoice(
    pyxb.binding.content.ParticleModel(CipherDataType._UseForTag(pyxb.namespace.ExpandedName(Namespace, u'CipherValue')), min_occurs=1, max_occurs=1),
    pyxb.binding.content.ParticleModel(CipherDataType._UseForTag(pyxb.namespace.ExpandedName(Namespace, u'CipherReference')), min_occurs=1, max_occurs=1)
    )
CipherDataType._ContentModel = pyxb.binding.content.ParticleModel(CipherDataType._GroupModel, min_occurs=1, max_occurs=1)



TransformsType._AddElement(pyxb.binding.basis.element(pyxb.namespace.ExpandedName(pyxb.namespace.NamespaceForURI(u'http://www.w3.org/2000/09/xmldsig#'), u'Transform'), pyxb.bundles.wssplat.ds.TransformType, scope=TransformsType))
TransformsType._GroupModel = pyxb.binding.content.GroupSequence(
    pyxb.binding.content.ParticleModel(TransformsType._UseForTag(pyxb.namespace.ExpandedName(pyxb.namespace.NamespaceForURI(u'http://www.w3.org/2000/09/xmldsig#'), u'Transform')), min_occurs=1, max_occurs=None)
    )
TransformsType._ContentModel = pyxb.binding.content.ParticleModel(TransformsType._GroupModel, min_occurs=1, max_occurs=1)


EncryptionPropertyType._GroupModel = pyxb.binding.content.GroupChoice(
    pyxb.binding.content.ParticleModel(pyxb.binding.content.Wildcard(process_contents=pyxb.binding.content.Wildcard.PC_lax, namespace_constraint=(pyxb.binding.content.Wildcard.NC_not, u'http://www.w3.org/2001/04/xmlenc#')), min_occurs=1, max_occurs=1)
    )
EncryptionPropertyType._ContentModel = pyxb.binding.content.ParticleModel(EncryptionPropertyType._GroupModel, min_occurs=1, max_occurs=None)



CTD_ANON._AddElement(pyxb.binding.basis.element(pyxb.namespace.ExpandedName(Namespace, u'KeyReference'), ReferenceType, scope=CTD_ANON))

CTD_ANON._AddElement(pyxb.binding.basis.element(pyxb.namespace.ExpandedName(Namespace, u'DataReference'), ReferenceType, scope=CTD_ANON))
CTD_ANON._GroupModel = pyxb.binding.content.GroupChoice(
    pyxb.binding.content.ParticleModel(CTD_ANON._UseForTag(pyxb.namespace.ExpandedName(Namespace, u'DataReference')), min_occurs=1, max_occurs=1),
    pyxb.binding.content.ParticleModel(CTD_ANON._UseForTag(pyxb.namespace.ExpandedName(Namespace, u'KeyReference')), min_occurs=1, max_occurs=1)
    )
CTD_ANON._ContentModel = pyxb.binding.content.ParticleModel(CTD_ANON._GroupModel, min_occurs=1L, max_occurs=None)



EncryptionMethodType._AddElement(pyxb.binding.basis.element(pyxb.namespace.ExpandedName(Namespace, u'KeySize'), KeySizeType, scope=EncryptionMethodType))

EncryptionMethodType._AddElement(pyxb.binding.basis.element(pyxb.namespace.ExpandedName(Namespace, u'OAEPparams'), pyxb.binding.datatypes.base64Binary, scope=EncryptionMethodType))
EncryptionMethodType._GroupModel = pyxb.binding.content.GroupSequence(
    pyxb.binding.content.ParticleModel(EncryptionMethodType._UseForTag(pyxb.namespace.ExpandedName(Namespace, u'KeySize')), min_occurs=0L, max_occurs=1),
    pyxb.binding.content.ParticleModel(EncryptionMethodType._UseForTag(pyxb.namespace.ExpandedName(Namespace, u'OAEPparams')), min_occurs=0L, max_occurs=1),
    pyxb.binding.content.ParticleModel(pyxb.binding.content.Wildcard(process_contents=pyxb.binding.content.Wildcard.PC_strict, namespace_constraint=(pyxb.binding.content.Wildcard.NC_not, u'http://www.w3.org/2001/04/xmlenc#')), min_occurs=0L, max_occurs=None)
    )
EncryptionMethodType._ContentModel = pyxb.binding.content.ParticleModel(EncryptionMethodType._GroupModel, min_occurs=1, max_occurs=1)



EncryptionPropertiesType._AddElement(pyxb.binding.basis.element(pyxb.namespace.ExpandedName(Namespace, u'EncryptionProperty'), EncryptionPropertyType, scope=EncryptionPropertiesType))
EncryptionPropertiesType._GroupModel = pyxb.binding.content.GroupSequence(
    pyxb.binding.content.ParticleModel(EncryptionPropertiesType._UseForTag(pyxb.namespace.ExpandedName(Namespace, u'EncryptionProperty')), min_occurs=1, max_occurs=None)
    )
EncryptionPropertiesType._ContentModel = pyxb.binding.content.ParticleModel(EncryptionPropertiesType._GroupModel, min_occurs=1, max_occurs=1)


ReferenceType._GroupModel = pyxb.binding.content.GroupSequence(
    pyxb.binding.content.ParticleModel(pyxb.binding.content.Wildcard(process_contents=pyxb.binding.content.Wildcard.PC_strict, namespace_constraint=(pyxb.binding.content.Wildcard.NC_not, u'http://www.w3.org/2001/04/xmlenc#')), min_occurs=0L, max_occurs=None)
    )
ReferenceType._ContentModel = pyxb.binding.content.ParticleModel(ReferenceType._GroupModel, min_occurs=1, max_occurs=1)



EncryptedType._AddElement(pyxb.binding.basis.element(pyxb.namespace.ExpandedName(Namespace, u'EncryptionMethod'), EncryptionMethodType, scope=EncryptedType))

EncryptedType._AddElement(pyxb.binding.basis.element(pyxb.namespace.ExpandedName(Namespace, u'CipherData'), CipherDataType, scope=EncryptedType))

EncryptedType._AddElement(pyxb.binding.basis.element(pyxb.namespace.ExpandedName(pyxb.namespace.NamespaceForURI(u'http://www.w3.org/2000/09/xmldsig#'), u'KeyInfo'), pyxb.bundles.wssplat.ds.KeyInfoType, scope=EncryptedType))

EncryptedType._AddElement(pyxb.binding.basis.element(pyxb.namespace.ExpandedName(Namespace, u'EncryptionProperties'), EncryptionPropertiesType, scope=EncryptedType))
EncryptedType._GroupModel = pyxb.binding.content.GroupSequence(
    pyxb.binding.content.ParticleModel(EncryptedType._UseForTag(pyxb.namespace.ExpandedName(Namespace, u'EncryptionMethod')), min_occurs=0L, max_occurs=1),
    pyxb.binding.content.ParticleModel(EncryptedType._UseForTag(pyxb.namespace.ExpandedName(pyxb.namespace.NamespaceForURI(u'http://www.w3.org/2000/09/xmldsig#'), u'KeyInfo')), min_occurs=0L, max_occurs=1),
    pyxb.binding.content.ParticleModel(EncryptedType._UseForTag(pyxb.namespace.ExpandedName(Namespace, u'CipherData')), min_occurs=1, max_occurs=1),
    pyxb.binding.content.ParticleModel(EncryptedType._UseForTag(pyxb.namespace.ExpandedName(Namespace, u'EncryptionProperties')), min_occurs=0L, max_occurs=1)
    )
EncryptedType._ContentModel = pyxb.binding.content.ParticleModel(EncryptedType._GroupModel, min_occurs=1, max_occurs=1)


EncryptedDataType._GroupModel = pyxb.binding.content.GroupSequence(
    pyxb.binding.content.ParticleModel(EncryptedDataType._UseForTag(pyxb.namespace.ExpandedName(Namespace, u'EncryptionMethod')), min_occurs=0L, max_occurs=1),
    pyxb.binding.content.ParticleModel(EncryptedDataType._UseForTag(pyxb.namespace.ExpandedName(pyxb.namespace.NamespaceForURI(u'http://www.w3.org/2000/09/xmldsig#'), u'KeyInfo')), min_occurs=0L, max_occurs=1),
    pyxb.binding.content.ParticleModel(EncryptedDataType._UseForTag(pyxb.namespace.ExpandedName(Namespace, u'CipherData')), min_occurs=1, max_occurs=1),
    pyxb.binding.content.ParticleModel(EncryptedDataType._UseForTag(pyxb.namespace.ExpandedName(Namespace, u'EncryptionProperties')), min_occurs=0L, max_occurs=1)
    )
EncryptedDataType._ContentModel = pyxb.binding.content.ParticleModel(EncryptedDataType._GroupModel, min_occurs=1, max_occurs=1)



EncryptedKeyType._AddElement(pyxb.binding.basis.element(pyxb.namespace.ExpandedName(Namespace, u'CarriedKeyName'), pyxb.binding.datatypes.string, scope=EncryptedKeyType))

EncryptedKeyType._AddElement(pyxb.binding.basis.element(pyxb.namespace.ExpandedName(Namespace, u'ReferenceList'), CTD_ANON, scope=EncryptedKeyType))
EncryptedKeyType._GroupModel_ = pyxb.binding.content.GroupSequence(
    pyxb.binding.content.ParticleModel(EncryptedKeyType._UseForTag(pyxb.namespace.ExpandedName(Namespace, u'EncryptionMethod')), min_occurs=0L, max_occurs=1),
    pyxb.binding.content.ParticleModel(EncryptedKeyType._UseForTag(pyxb.namespace.ExpandedName(pyxb.namespace.NamespaceForURI(u'http://www.w3.org/2000/09/xmldsig#'), u'KeyInfo')), min_occurs=0L, max_occurs=1),
    pyxb.binding.content.ParticleModel(EncryptedKeyType._UseForTag(pyxb.namespace.ExpandedName(Namespace, u'CipherData')), min_occurs=1, max_occurs=1),
    pyxb.binding.content.ParticleModel(EncryptedKeyType._UseForTag(pyxb.namespace.ExpandedName(Namespace, u'EncryptionProperties')), min_occurs=0L, max_occurs=1)
    )
EncryptedKeyType._GroupModel_2 = pyxb.binding.content.GroupSequence(
    pyxb.binding.content.ParticleModel(EncryptedKeyType._UseForTag(pyxb.namespace.ExpandedName(Namespace, u'ReferenceList')), min_occurs=0L, max_occurs=1),
    pyxb.binding.content.ParticleModel(EncryptedKeyType._UseForTag(pyxb.namespace.ExpandedName(Namespace, u'CarriedKeyName')), min_occurs=0L, max_occurs=1)
    )
EncryptedKeyType._GroupModel = pyxb.binding.content.GroupSequence(
    pyxb.binding.content.ParticleModel(EncryptedKeyType._GroupModel_, min_occurs=1, max_occurs=1),
    pyxb.binding.content.ParticleModel(EncryptedKeyType._GroupModel_2, min_occurs=1, max_occurs=1)
    )
EncryptedKeyType._ContentModel = pyxb.binding.content.ParticleModel(EncryptedKeyType._GroupModel, min_occurs=1, max_occurs=1)
