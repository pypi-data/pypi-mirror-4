# ./pyxb/bundles/saml20/raw/protocol.py
# -*- coding: utf-8 -*-
# PyXB bindings for NM:36a732e723673f7ad63838d43d722888bbbdeb09
# Generated 2012-11-01 15:13:40.459003 by PyXB version 1.1.5
# Namespace urn:oasis:names:tc:SAML:2.0:protocol

import pyxb
import pyxb.binding
import pyxb.binding.saxer
import StringIO
import pyxb.utils.utility
import pyxb.utils.domutils
import sys

# Unique identifier for bindings created at the same time
_GenerationUID = pyxb.utils.utility.UniqueIdentifier('urn:uuid:a08f64a8-2460-11e2-b5e2-c8600024e903')

# Import bindings for namespaces imported into schema
import pyxb.binding.datatypes
import pyxb.bundles.wssplat.ds
import pyxb.bundles.saml20.assertion

Namespace = pyxb.namespace.NamespaceForURI(u'urn:oasis:names:tc:SAML:2.0:protocol', create_if_missing=True)
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


# Atomic simple type: {urn:oasis:names:tc:SAML:2.0:protocol}AuthnContextComparisonType
class AuthnContextComparisonType (pyxb.binding.datatypes.string, pyxb.binding.basis.enumeration_mixin):

    """An atomic simple type."""

    _ExpandedName = pyxb.namespace.ExpandedName(Namespace, u'AuthnContextComparisonType')
    _DefinitionLocation = pyxb.utils.utility.Location('/tmp/pyxbdist.RHB65sy/PyXB-1.1.5/pyxb/bundles/saml20/schemas/protocol.xsd', 122, 4)
    _Documentation = None
AuthnContextComparisonType._CF_enumeration = pyxb.binding.facets.CF_enumeration(value_datatype=AuthnContextComparisonType, enum_prefix=None)
AuthnContextComparisonType.exact = AuthnContextComparisonType._CF_enumeration.addEnumeration(unicode_value=u'exact', tag=u'exact')
AuthnContextComparisonType.minimum = AuthnContextComparisonType._CF_enumeration.addEnumeration(unicode_value=u'minimum', tag=u'minimum')
AuthnContextComparisonType.maximum = AuthnContextComparisonType._CF_enumeration.addEnumeration(unicode_value=u'maximum', tag=u'maximum')
AuthnContextComparisonType.better = AuthnContextComparisonType._CF_enumeration.addEnumeration(unicode_value=u'better', tag=u'better')
AuthnContextComparisonType._InitializeFacetMap(AuthnContextComparisonType._CF_enumeration)
Namespace.addCategoryObject('typeBinding', u'AuthnContextComparisonType', AuthnContextComparisonType)

# Complex type {urn:oasis:names:tc:SAML:2.0:protocol}RequestAbstractType with content type ELEMENT_ONLY
class RequestAbstractType (pyxb.binding.basis.complexTypeDefinition):
    _TypeDefinition = None
    _ContentTypeTag = pyxb.binding.basis.complexTypeDefinition._CT_ELEMENT_ONLY
    _Abstract = True
    _ExpandedName = pyxb.namespace.ExpandedName(Namespace, u'RequestAbstractType')
    _DefinitionLocation = pyxb.utils.utility.Location('/tmp/pyxbdist.RHB65sy/PyXB-1.1.5/pyxb/bundles/saml20/schemas/protocol.xsd', 29, 4)
    # Base type is pyxb.binding.datatypes.anyType
    
    # Element {http://www.w3.org/2000/09/xmldsig#}Signature uses Python identifier Signature
    __Signature = pyxb.binding.content.ElementUse(pyxb.namespace.ExpandedName(pyxb.namespace.NamespaceForURI(u'http://www.w3.org/2000/09/xmldsig#'), u'Signature'), 'Signature', '__urnoasisnamestcSAML2_0protocol_RequestAbstractType_httpwww_w3_org200009xmldsigSignature', False)
    __Signature._DeclarationLocation = pyxb.utils.utility.Location('/tmp/pyxbdist.RHB65sy/PyXB-1.1.5/pyxb/bundles/wssplat/schemas/ds.xsd', 43, 0)
    __Signature._UseLocation = pyxb.utils.utility.Location('/tmp/pyxbdist.RHB65sy/PyXB-1.1.5/pyxb/bundles/saml20/schemas/protocol.xsd', 30, 8)

    
    Signature = property(__Signature.value, __Signature.set, None, None)

    
    # Element {urn:oasis:names:tc:SAML:2.0:protocol}Extensions uses Python identifier Extensions
    __Extensions = pyxb.binding.content.ElementUse(pyxb.namespace.ExpandedName(Namespace, u'Extensions'), 'Extensions', '__urnoasisnamestcSAML2_0protocol_RequestAbstractType_urnoasisnamestcSAML2_0protocolExtensions', False)
    __Extensions._DeclarationLocation = pyxb.utils.utility.Location('/tmp/pyxbdist.RHB65sy/PyXB-1.1.5/pyxb/bundles/saml20/schemas/protocol.xsd', 41, 4)
    __Extensions._UseLocation = pyxb.utils.utility.Location('/tmp/pyxbdist.RHB65sy/PyXB-1.1.5/pyxb/bundles/saml20/schemas/protocol.xsd', 30, 8)

    
    Extensions = property(__Extensions.value, __Extensions.set, None, None)

    
    # Element {urn:oasis:names:tc:SAML:2.0:assertion}Issuer uses Python identifier Issuer
    __Issuer = pyxb.binding.content.ElementUse(pyxb.namespace.ExpandedName(pyxb.namespace.NamespaceForURI(u'urn:oasis:names:tc:SAML:2.0:assertion'), u'Issuer'), 'Issuer', '__urnoasisnamestcSAML2_0protocol_RequestAbstractType_urnoasisnamestcSAML2_0assertionIssuer', False)
    __Issuer._DeclarationLocation = pyxb.utils.utility.Location('/tmp/pyxbdist.RHB65sy/PyXB-1.1.5/pyxb/bundles/saml20/schemas/assertion.xsd', 54, 4)
    __Issuer._UseLocation = pyxb.utils.utility.Location('/tmp/pyxbdist.RHB65sy/PyXB-1.1.5/pyxb/bundles/saml20/schemas/protocol.xsd', 30, 8)

    
    Issuer = property(__Issuer.value, __Issuer.set, None, None)

    
    # Attribute Version uses Python identifier Version
    __Version = pyxb.binding.content.AttributeUse(pyxb.namespace.ExpandedName(None, u'Version'), 'Version', '__urnoasisnamestcSAML2_0protocol_RequestAbstractType_Version', pyxb.binding.datatypes.string, required=True)
    __Version._DeclarationLocation = pyxb.utils.utility.Location('/tmp/pyxbdist.RHB65sy/PyXB-1.1.5/pyxb/bundles/saml20/schemas/protocol.xsd', 36, 8)
    __Version._UseLocation = pyxb.utils.utility.Location('/tmp/pyxbdist.RHB65sy/PyXB-1.1.5/pyxb/bundles/saml20/schemas/protocol.xsd', 36, 8)
    
    Version = property(__Version.value, __Version.set, None, None)

    
    # Attribute IssueInstant uses Python identifier IssueInstant
    __IssueInstant = pyxb.binding.content.AttributeUse(pyxb.namespace.ExpandedName(None, u'IssueInstant'), 'IssueInstant', '__urnoasisnamestcSAML2_0protocol_RequestAbstractType_IssueInstant', pyxb.binding.datatypes.dateTime, required=True)
    __IssueInstant._DeclarationLocation = pyxb.utils.utility.Location('/tmp/pyxbdist.RHB65sy/PyXB-1.1.5/pyxb/bundles/saml20/schemas/protocol.xsd', 37, 8)
    __IssueInstant._UseLocation = pyxb.utils.utility.Location('/tmp/pyxbdist.RHB65sy/PyXB-1.1.5/pyxb/bundles/saml20/schemas/protocol.xsd', 37, 8)
    
    IssueInstant = property(__IssueInstant.value, __IssueInstant.set, None, None)

    
    # Attribute ID uses Python identifier ID
    __ID = pyxb.binding.content.AttributeUse(pyxb.namespace.ExpandedName(None, u'ID'), 'ID', '__urnoasisnamestcSAML2_0protocol_RequestAbstractType_ID', pyxb.binding.datatypes.ID, required=True)
    __ID._DeclarationLocation = pyxb.utils.utility.Location('/tmp/pyxbdist.RHB65sy/PyXB-1.1.5/pyxb/bundles/saml20/schemas/protocol.xsd', 35, 8)
    __ID._UseLocation = pyxb.utils.utility.Location('/tmp/pyxbdist.RHB65sy/PyXB-1.1.5/pyxb/bundles/saml20/schemas/protocol.xsd', 35, 8)
    
    ID = property(__ID.value, __ID.set, None, None)

    
    # Attribute Consent uses Python identifier Consent
    __Consent = pyxb.binding.content.AttributeUse(pyxb.namespace.ExpandedName(None, u'Consent'), 'Consent', '__urnoasisnamestcSAML2_0protocol_RequestAbstractType_Consent', pyxb.binding.datatypes.anyURI)
    __Consent._DeclarationLocation = pyxb.utils.utility.Location('/tmp/pyxbdist.RHB65sy/PyXB-1.1.5/pyxb/bundles/saml20/schemas/protocol.xsd', 39, 5)
    __Consent._UseLocation = pyxb.utils.utility.Location('/tmp/pyxbdist.RHB65sy/PyXB-1.1.5/pyxb/bundles/saml20/schemas/protocol.xsd', 39, 5)
    
    Consent = property(__Consent.value, __Consent.set, None, None)

    
    # Attribute Destination uses Python identifier Destination
    __Destination = pyxb.binding.content.AttributeUse(pyxb.namespace.ExpandedName(None, u'Destination'), 'Destination', '__urnoasisnamestcSAML2_0protocol_RequestAbstractType_Destination', pyxb.binding.datatypes.anyURI)
    __Destination._DeclarationLocation = pyxb.utils.utility.Location('/tmp/pyxbdist.RHB65sy/PyXB-1.1.5/pyxb/bundles/saml20/schemas/protocol.xsd', 38, 8)
    __Destination._UseLocation = pyxb.utils.utility.Location('/tmp/pyxbdist.RHB65sy/PyXB-1.1.5/pyxb/bundles/saml20/schemas/protocol.xsd', 38, 8)
    
    Destination = property(__Destination.value, __Destination.set, None, None)


    _ElementMap = {
        __Signature.name() : __Signature,
        __Extensions.name() : __Extensions,
        __Issuer.name() : __Issuer
    }
    _AttributeMap = {
        __Version.name() : __Version,
        __IssueInstant.name() : __IssueInstant,
        __ID.name() : __ID,
        __Consent.name() : __Consent,
        __Destination.name() : __Destination
    }
Namespace.addCategoryObject('typeBinding', u'RequestAbstractType', RequestAbstractType)


# Complex type {urn:oasis:names:tc:SAML:2.0:protocol}SubjectQueryAbstractType with content type ELEMENT_ONLY
class SubjectQueryAbstractType (RequestAbstractType):
    _TypeDefinition = None
    _ContentTypeTag = pyxb.binding.basis.complexTypeDefinition._CT_ELEMENT_ONLY
    _Abstract = True
    _ExpandedName = pyxb.namespace.ExpandedName(Namespace, u'SubjectQueryAbstractType')
    _DefinitionLocation = pyxb.utils.utility.Location('/tmp/pyxbdist.RHB65sy/PyXB-1.1.5/pyxb/bundles/saml20/schemas/protocol.xsd', 94, 4)
    # Base type is RequestAbstractType
    
    # Element Signature ({http://www.w3.org/2000/09/xmldsig#}Signature) inherited from {urn:oasis:names:tc:SAML:2.0:protocol}RequestAbstractType
    
    # Element {urn:oasis:names:tc:SAML:2.0:assertion}Subject uses Python identifier Subject
    __Subject = pyxb.binding.content.ElementUse(pyxb.namespace.ExpandedName(pyxb.namespace.NamespaceForURI(u'urn:oasis:names:tc:SAML:2.0:assertion'), u'Subject'), 'Subject', '__urnoasisnamestcSAML2_0protocol_SubjectQueryAbstractType_urnoasisnamestcSAML2_0assertionSubject', False)
    __Subject._DeclarationLocation = pyxb.utils.utility.Location('/tmp/pyxbdist.RHB65sy/PyXB-1.1.5/pyxb/bundles/saml20/schemas/assertion.xsd', 76, 4)
    __Subject._UseLocation = None

    
    Subject = property(__Subject.value, __Subject.set, None, None)

    
    # Element Extensions ({urn:oasis:names:tc:SAML:2.0:protocol}Extensions) inherited from {urn:oasis:names:tc:SAML:2.0:protocol}RequestAbstractType
    
    # Element Issuer ({urn:oasis:names:tc:SAML:2.0:assertion}Issuer) inherited from {urn:oasis:names:tc:SAML:2.0:protocol}RequestAbstractType
    
    # Attribute Destination inherited from {urn:oasis:names:tc:SAML:2.0:protocol}RequestAbstractType
    
    # Attribute Consent inherited from {urn:oasis:names:tc:SAML:2.0:protocol}RequestAbstractType
    
    # Attribute ID inherited from {urn:oasis:names:tc:SAML:2.0:protocol}RequestAbstractType
    
    # Attribute IssueInstant inherited from {urn:oasis:names:tc:SAML:2.0:protocol}RequestAbstractType
    
    # Attribute Version inherited from {urn:oasis:names:tc:SAML:2.0:protocol}RequestAbstractType

    _ElementMap = RequestAbstractType._ElementMap.copy()
    _ElementMap.update({
        __Subject.name() : __Subject
    })
    _AttributeMap = RequestAbstractType._AttributeMap.copy()
    _AttributeMap.update({
        
    })
Namespace.addCategoryObject('typeBinding', u'SubjectQueryAbstractType', SubjectQueryAbstractType)


# Complex type {urn:oasis:names:tc:SAML:2.0:protocol}TerminateType with content type EMPTY
class TerminateType (pyxb.binding.basis.complexTypeDefinition):
    _TypeDefinition = None
    _ContentTypeTag = pyxb.binding.basis.complexTypeDefinition._CT_EMPTY
    _Abstract = False
    _ExpandedName = pyxb.namespace.ExpandedName(Namespace, u'TerminateType')
    _DefinitionLocation = pyxb.utils.utility.Location('/tmp/pyxbdist.RHB65sy/PyXB-1.1.5/pyxb/bundles/saml20/schemas/protocol.xsd', 255, 4)
    # Base type is pyxb.binding.datatypes.anyType

    _ElementMap = {
        
    }
    _AttributeMap = {
        
    }
Namespace.addCategoryObject('typeBinding', u'TerminateType', TerminateType)


# Complex type {urn:oasis:names:tc:SAML:2.0:protocol}ArtifactResolveType with content type ELEMENT_ONLY
class ArtifactResolveType (RequestAbstractType):
    _TypeDefinition = None
    _ContentTypeTag = pyxb.binding.basis.complexTypeDefinition._CT_ELEMENT_ONLY
    _Abstract = False
    _ExpandedName = pyxb.namespace.ExpandedName(Namespace, u'ArtifactResolveType')
    _DefinitionLocation = pyxb.utils.utility.Location('/tmp/pyxbdist.RHB65sy/PyXB-1.1.5/pyxb/bundles/saml20/schemas/protocol.xsd', 214, 4)
    # Base type is RequestAbstractType
    
    # Element Signature ({http://www.w3.org/2000/09/xmldsig#}Signature) inherited from {urn:oasis:names:tc:SAML:2.0:protocol}RequestAbstractType
    
    # Element {urn:oasis:names:tc:SAML:2.0:protocol}Artifact uses Python identifier Artifact
    __Artifact = pyxb.binding.content.ElementUse(pyxb.namespace.ExpandedName(Namespace, u'Artifact'), 'Artifact', '__urnoasisnamestcSAML2_0protocol_ArtifactResolveType_urnoasisnamestcSAML2_0protocolArtifact', False)
    __Artifact._DeclarationLocation = pyxb.utils.utility.Location('/tmp/pyxbdist.RHB65sy/PyXB-1.1.5/pyxb/bundles/saml20/schemas/protocol.xsd', 223, 4)
    __Artifact._UseLocation = None

    
    Artifact = property(__Artifact.value, __Artifact.set, None, None)

    
    # Element Extensions ({urn:oasis:names:tc:SAML:2.0:protocol}Extensions) inherited from {urn:oasis:names:tc:SAML:2.0:protocol}RequestAbstractType
    
    # Element Issuer ({urn:oasis:names:tc:SAML:2.0:assertion}Issuer) inherited from {urn:oasis:names:tc:SAML:2.0:protocol}RequestAbstractType
    
    # Attribute Destination inherited from {urn:oasis:names:tc:SAML:2.0:protocol}RequestAbstractType
    
    # Attribute Consent inherited from {urn:oasis:names:tc:SAML:2.0:protocol}RequestAbstractType
    
    # Attribute ID inherited from {urn:oasis:names:tc:SAML:2.0:protocol}RequestAbstractType
    
    # Attribute IssueInstant inherited from {urn:oasis:names:tc:SAML:2.0:protocol}RequestAbstractType
    
    # Attribute Version inherited from {urn:oasis:names:tc:SAML:2.0:protocol}RequestAbstractType

    _ElementMap = RequestAbstractType._ElementMap.copy()
    _ElementMap.update({
        __Artifact.name() : __Artifact
    })
    _AttributeMap = RequestAbstractType._AttributeMap.copy()
    _AttributeMap.update({
        
    })
Namespace.addCategoryObject('typeBinding', u'ArtifactResolveType', ArtifactResolveType)


# Complex type {urn:oasis:names:tc:SAML:2.0:protocol}AuthnRequestType with content type ELEMENT_ONLY
class AuthnRequestType (RequestAbstractType):
    _TypeDefinition = None
    _ContentTypeTag = pyxb.binding.basis.complexTypeDefinition._CT_ELEMENT_ONLY
    _Abstract = False
    _ExpandedName = pyxb.namespace.ExpandedName(Namespace, u'AuthnRequestType')
    _DefinitionLocation = pyxb.utils.utility.Location('/tmp/pyxbdist.RHB65sy/PyXB-1.1.5/pyxb/bundles/saml20/schemas/protocol.xsd', 153, 4)
    # Base type is RequestAbstractType
    
    # Element {urn:oasis:names:tc:SAML:2.0:protocol}RequestedAuthnContext uses Python identifier RequestedAuthnContext
    __RequestedAuthnContext = pyxb.binding.content.ElementUse(pyxb.namespace.ExpandedName(Namespace, u'RequestedAuthnContext'), 'RequestedAuthnContext', '__urnoasisnamestcSAML2_0protocol_AuthnRequestType_urnoasisnamestcSAML2_0protocolRequestedAuthnContext', False)
    __RequestedAuthnContext._DeclarationLocation = pyxb.utils.utility.Location('/tmp/pyxbdist.RHB65sy/PyXB-1.1.5/pyxb/bundles/saml20/schemas/protocol.xsd', 114, 4)
    __RequestedAuthnContext._UseLocation = None

    
    RequestedAuthnContext = property(__RequestedAuthnContext.value, __RequestedAuthnContext.set, None, None)

    
    # Element Extensions ({urn:oasis:names:tc:SAML:2.0:protocol}Extensions) inherited from {urn:oasis:names:tc:SAML:2.0:protocol}RequestAbstractType
    
    # Element {urn:oasis:names:tc:SAML:2.0:protocol}NameIDPolicy uses Python identifier NameIDPolicy
    __NameIDPolicy = pyxb.binding.content.ElementUse(pyxb.namespace.ExpandedName(Namespace, u'NameIDPolicy'), 'NameIDPolicy', '__urnoasisnamestcSAML2_0protocol_AuthnRequestType_urnoasisnamestcSAML2_0protocolNameIDPolicy', False)
    __NameIDPolicy._DeclarationLocation = pyxb.utils.utility.Location('/tmp/pyxbdist.RHB65sy/PyXB-1.1.5/pyxb/bundles/saml20/schemas/protocol.xsd', 173, 4)
    __NameIDPolicy._UseLocation = None

    
    NameIDPolicy = property(__NameIDPolicy.value, __NameIDPolicy.set, None, None)

    
    # Element Issuer ({urn:oasis:names:tc:SAML:2.0:assertion}Issuer) inherited from {urn:oasis:names:tc:SAML:2.0:protocol}RequestAbstractType
    
    # Element {urn:oasis:names:tc:SAML:2.0:protocol}Scoping uses Python identifier Scoping
    __Scoping = pyxb.binding.content.ElementUse(pyxb.namespace.ExpandedName(Namespace, u'Scoping'), 'Scoping', '__urnoasisnamestcSAML2_0protocol_AuthnRequestType_urnoasisnamestcSAML2_0protocolScoping', False)
    __Scoping._DeclarationLocation = pyxb.utils.utility.Location('/tmp/pyxbdist.RHB65sy/PyXB-1.1.5/pyxb/bundles/saml20/schemas/protocol.xsd', 179, 4)
    __Scoping._UseLocation = None

    
    Scoping = property(__Scoping.value, __Scoping.set, None, None)

    
    # Element {urn:oasis:names:tc:SAML:2.0:assertion}Conditions uses Python identifier Conditions
    __Conditions = pyxb.binding.content.ElementUse(pyxb.namespace.ExpandedName(pyxb.namespace.NamespaceForURI(u'urn:oasis:names:tc:SAML:2.0:assertion'), u'Conditions'), 'Conditions', '__urnoasisnamestcSAML2_0protocol_AuthnRequestType_urnoasisnamestcSAML2_0assertionConditions', False)
    __Conditions._DeclarationLocation = pyxb.utils.utility.Location('/tmp/pyxbdist.RHB65sy/PyXB-1.1.5/pyxb/bundles/saml20/schemas/assertion.xsd', 127, 4)
    __Conditions._UseLocation = None

    
    Conditions = property(__Conditions.value, __Conditions.set, None, None)

    
    # Element Signature ({http://www.w3.org/2000/09/xmldsig#}Signature) inherited from {urn:oasis:names:tc:SAML:2.0:protocol}RequestAbstractType
    
    # Element {urn:oasis:names:tc:SAML:2.0:assertion}Subject uses Python identifier Subject
    __Subject = pyxb.binding.content.ElementUse(pyxb.namespace.ExpandedName(pyxb.namespace.NamespaceForURI(u'urn:oasis:names:tc:SAML:2.0:assertion'), u'Subject'), 'Subject', '__urnoasisnamestcSAML2_0protocol_AuthnRequestType_urnoasisnamestcSAML2_0assertionSubject', False)
    __Subject._DeclarationLocation = pyxb.utils.utility.Location('/tmp/pyxbdist.RHB65sy/PyXB-1.1.5/pyxb/bundles/saml20/schemas/assertion.xsd', 76, 4)
    __Subject._UseLocation = None

    
    Subject = property(__Subject.value, __Subject.set, None, None)

    
    # Attribute AttributeConsumingServiceIndex uses Python identifier AttributeConsumingServiceIndex
    __AttributeConsumingServiceIndex = pyxb.binding.content.AttributeUse(pyxb.namespace.ExpandedName(None, u'AttributeConsumingServiceIndex'), 'AttributeConsumingServiceIndex', '__urnoasisnamestcSAML2_0protocol_AuthnRequestType_AttributeConsumingServiceIndex', pyxb.binding.datatypes.unsignedShort)
    __AttributeConsumingServiceIndex._DeclarationLocation = pyxb.utils.utility.Location('/tmp/pyxbdist.RHB65sy/PyXB-1.1.5/pyxb/bundles/saml20/schemas/protocol.xsd', 168, 16)
    __AttributeConsumingServiceIndex._UseLocation = pyxb.utils.utility.Location('/tmp/pyxbdist.RHB65sy/PyXB-1.1.5/pyxb/bundles/saml20/schemas/protocol.xsd', 168, 16)
    
    AttributeConsumingServiceIndex = property(__AttributeConsumingServiceIndex.value, __AttributeConsumingServiceIndex.set, None, None)

    
    # Attribute ProtocolBinding uses Python identifier ProtocolBinding
    __ProtocolBinding = pyxb.binding.content.AttributeUse(pyxb.namespace.ExpandedName(None, u'ProtocolBinding'), 'ProtocolBinding', '__urnoasisnamestcSAML2_0protocol_AuthnRequestType_ProtocolBinding', pyxb.binding.datatypes.anyURI)
    __ProtocolBinding._DeclarationLocation = pyxb.utils.utility.Location('/tmp/pyxbdist.RHB65sy/PyXB-1.1.5/pyxb/bundles/saml20/schemas/protocol.xsd', 165, 16)
    __ProtocolBinding._UseLocation = pyxb.utils.utility.Location('/tmp/pyxbdist.RHB65sy/PyXB-1.1.5/pyxb/bundles/saml20/schemas/protocol.xsd', 165, 16)
    
    ProtocolBinding = property(__ProtocolBinding.value, __ProtocolBinding.set, None, None)

    
    # Attribute ProviderName uses Python identifier ProviderName
    __ProviderName = pyxb.binding.content.AttributeUse(pyxb.namespace.ExpandedName(None, u'ProviderName'), 'ProviderName', '__urnoasisnamestcSAML2_0protocol_AuthnRequestType_ProviderName', pyxb.binding.datatypes.string)
    __ProviderName._DeclarationLocation = pyxb.utils.utility.Location('/tmp/pyxbdist.RHB65sy/PyXB-1.1.5/pyxb/bundles/saml20/schemas/protocol.xsd', 169, 16)
    __ProviderName._UseLocation = pyxb.utils.utility.Location('/tmp/pyxbdist.RHB65sy/PyXB-1.1.5/pyxb/bundles/saml20/schemas/protocol.xsd', 169, 16)
    
    ProviderName = property(__ProviderName.value, __ProviderName.set, None, None)

    
    # Attribute Version inherited from {urn:oasis:names:tc:SAML:2.0:protocol}RequestAbstractType
    
    # Attribute IssueInstant inherited from {urn:oasis:names:tc:SAML:2.0:protocol}RequestAbstractType
    
    # Attribute ID inherited from {urn:oasis:names:tc:SAML:2.0:protocol}RequestAbstractType
    
    # Attribute AssertionConsumerServiceIndex uses Python identifier AssertionConsumerServiceIndex
    __AssertionConsumerServiceIndex = pyxb.binding.content.AttributeUse(pyxb.namespace.ExpandedName(None, u'AssertionConsumerServiceIndex'), 'AssertionConsumerServiceIndex', '__urnoasisnamestcSAML2_0protocol_AuthnRequestType_AssertionConsumerServiceIndex', pyxb.binding.datatypes.unsignedShort)
    __AssertionConsumerServiceIndex._DeclarationLocation = pyxb.utils.utility.Location('/tmp/pyxbdist.RHB65sy/PyXB-1.1.5/pyxb/bundles/saml20/schemas/protocol.xsd', 166, 16)
    __AssertionConsumerServiceIndex._UseLocation = pyxb.utils.utility.Location('/tmp/pyxbdist.RHB65sy/PyXB-1.1.5/pyxb/bundles/saml20/schemas/protocol.xsd', 166, 16)
    
    AssertionConsumerServiceIndex = property(__AssertionConsumerServiceIndex.value, __AssertionConsumerServiceIndex.set, None, None)

    
    # Attribute Destination inherited from {urn:oasis:names:tc:SAML:2.0:protocol}RequestAbstractType
    
    # Attribute IsPassive uses Python identifier IsPassive
    __IsPassive = pyxb.binding.content.AttributeUse(pyxb.namespace.ExpandedName(None, u'IsPassive'), 'IsPassive', '__urnoasisnamestcSAML2_0protocol_AuthnRequestType_IsPassive', pyxb.binding.datatypes.boolean)
    __IsPassive._DeclarationLocation = pyxb.utils.utility.Location('/tmp/pyxbdist.RHB65sy/PyXB-1.1.5/pyxb/bundles/saml20/schemas/protocol.xsd', 164, 16)
    __IsPassive._UseLocation = pyxb.utils.utility.Location('/tmp/pyxbdist.RHB65sy/PyXB-1.1.5/pyxb/bundles/saml20/schemas/protocol.xsd', 164, 16)
    
    IsPassive = property(__IsPassive.value, __IsPassive.set, None, None)

    
    # Attribute ForceAuthn uses Python identifier ForceAuthn
    __ForceAuthn = pyxb.binding.content.AttributeUse(pyxb.namespace.ExpandedName(None, u'ForceAuthn'), 'ForceAuthn', '__urnoasisnamestcSAML2_0protocol_AuthnRequestType_ForceAuthn', pyxb.binding.datatypes.boolean)
    __ForceAuthn._DeclarationLocation = pyxb.utils.utility.Location('/tmp/pyxbdist.RHB65sy/PyXB-1.1.5/pyxb/bundles/saml20/schemas/protocol.xsd', 163, 16)
    __ForceAuthn._UseLocation = pyxb.utils.utility.Location('/tmp/pyxbdist.RHB65sy/PyXB-1.1.5/pyxb/bundles/saml20/schemas/protocol.xsd', 163, 16)
    
    ForceAuthn = property(__ForceAuthn.value, __ForceAuthn.set, None, None)

    
    # Attribute Consent inherited from {urn:oasis:names:tc:SAML:2.0:protocol}RequestAbstractType
    
    # Attribute AssertionConsumerServiceURL uses Python identifier AssertionConsumerServiceURL
    __AssertionConsumerServiceURL = pyxb.binding.content.AttributeUse(pyxb.namespace.ExpandedName(None, u'AssertionConsumerServiceURL'), 'AssertionConsumerServiceURL', '__urnoasisnamestcSAML2_0protocol_AuthnRequestType_AssertionConsumerServiceURL', pyxb.binding.datatypes.anyURI)
    __AssertionConsumerServiceURL._DeclarationLocation = pyxb.utils.utility.Location('/tmp/pyxbdist.RHB65sy/PyXB-1.1.5/pyxb/bundles/saml20/schemas/protocol.xsd', 167, 16)
    __AssertionConsumerServiceURL._UseLocation = pyxb.utils.utility.Location('/tmp/pyxbdist.RHB65sy/PyXB-1.1.5/pyxb/bundles/saml20/schemas/protocol.xsd', 167, 16)
    
    AssertionConsumerServiceURL = property(__AssertionConsumerServiceURL.value, __AssertionConsumerServiceURL.set, None, None)


    _ElementMap = RequestAbstractType._ElementMap.copy()
    _ElementMap.update({
        __RequestedAuthnContext.name() : __RequestedAuthnContext,
        __NameIDPolicy.name() : __NameIDPolicy,
        __Scoping.name() : __Scoping,
        __Conditions.name() : __Conditions,
        __Subject.name() : __Subject
    })
    _AttributeMap = RequestAbstractType._AttributeMap.copy()
    _AttributeMap.update({
        __AttributeConsumingServiceIndex.name() : __AttributeConsumingServiceIndex,
        __ProtocolBinding.name() : __ProtocolBinding,
        __ProviderName.name() : __ProviderName,
        __AssertionConsumerServiceIndex.name() : __AssertionConsumerServiceIndex,
        __IsPassive.name() : __IsPassive,
        __ForceAuthn.name() : __ForceAuthn,
        __AssertionConsumerServiceURL.name() : __AssertionConsumerServiceURL
    })
Namespace.addCategoryObject('typeBinding', u'AuthnRequestType', AuthnRequestType)


# Complex type {urn:oasis:names:tc:SAML:2.0:protocol}ScopingType with content type ELEMENT_ONLY
class ScopingType (pyxb.binding.basis.complexTypeDefinition):
    _TypeDefinition = None
    _ContentTypeTag = pyxb.binding.basis.complexTypeDefinition._CT_ELEMENT_ONLY
    _Abstract = False
    _ExpandedName = pyxb.namespace.ExpandedName(Namespace, u'ScopingType')
    _DefinitionLocation = pyxb.utils.utility.Location('/tmp/pyxbdist.RHB65sy/PyXB-1.1.5/pyxb/bundles/saml20/schemas/protocol.xsd', 180, 4)
    # Base type is pyxb.binding.datatypes.anyType
    
    # Element {urn:oasis:names:tc:SAML:2.0:protocol}IDPList uses Python identifier IDPList
    __IDPList = pyxb.binding.content.ElementUse(pyxb.namespace.ExpandedName(Namespace, u'IDPList'), 'IDPList', '__urnoasisnamestcSAML2_0protocol_ScopingType_urnoasisnamestcSAML2_0protocolIDPList', False)
    __IDPList._DeclarationLocation = pyxb.utils.utility.Location('/tmp/pyxbdist.RHB65sy/PyXB-1.1.5/pyxb/bundles/saml20/schemas/protocol.xsd', 188, 4)
    __IDPList._UseLocation = pyxb.utils.utility.Location('/tmp/pyxbdist.RHB65sy/PyXB-1.1.5/pyxb/bundles/saml20/schemas/protocol.xsd', 181, 8)

    
    IDPList = property(__IDPList.value, __IDPList.set, None, None)

    
    # Element {urn:oasis:names:tc:SAML:2.0:protocol}RequesterID uses Python identifier RequesterID
    __RequesterID = pyxb.binding.content.ElementUse(pyxb.namespace.ExpandedName(Namespace, u'RequesterID'), 'RequesterID', '__urnoasisnamestcSAML2_0protocol_ScopingType_urnoasisnamestcSAML2_0protocolRequesterID', True)
    __RequesterID._DeclarationLocation = pyxb.utils.utility.Location('/tmp/pyxbdist.RHB65sy/PyXB-1.1.5/pyxb/bundles/saml20/schemas/protocol.xsd', 187, 4)
    __RequesterID._UseLocation = pyxb.utils.utility.Location('/tmp/pyxbdist.RHB65sy/PyXB-1.1.5/pyxb/bundles/saml20/schemas/protocol.xsd', 181, 8)

    
    RequesterID = property(__RequesterID.value, __RequesterID.set, None, None)

    
    # Attribute ProxyCount uses Python identifier ProxyCount
    __ProxyCount = pyxb.binding.content.AttributeUse(pyxb.namespace.ExpandedName(None, u'ProxyCount'), 'ProxyCount', '__urnoasisnamestcSAML2_0protocol_ScopingType_ProxyCount', pyxb.binding.datatypes.nonNegativeInteger)
    __ProxyCount._DeclarationLocation = pyxb.utils.utility.Location('/tmp/pyxbdist.RHB65sy/PyXB-1.1.5/pyxb/bundles/saml20/schemas/protocol.xsd', 185, 8)
    __ProxyCount._UseLocation = pyxb.utils.utility.Location('/tmp/pyxbdist.RHB65sy/PyXB-1.1.5/pyxb/bundles/saml20/schemas/protocol.xsd', 185, 8)
    
    ProxyCount = property(__ProxyCount.value, __ProxyCount.set, None, None)


    _ElementMap = {
        __IDPList.name() : __IDPList,
        __RequesterID.name() : __RequesterID
    }
    _AttributeMap = {
        __ProxyCount.name() : __ProxyCount
    }
Namespace.addCategoryObject('typeBinding', u'ScopingType', ScopingType)


# Complex type {urn:oasis:names:tc:SAML:2.0:protocol}RequestedAuthnContextType with content type ELEMENT_ONLY
class RequestedAuthnContextType (pyxb.binding.basis.complexTypeDefinition):
    _TypeDefinition = None
    _ContentTypeTag = pyxb.binding.basis.complexTypeDefinition._CT_ELEMENT_ONLY
    _Abstract = False
    _ExpandedName = pyxb.namespace.ExpandedName(Namespace, u'RequestedAuthnContextType')
    _DefinitionLocation = pyxb.utils.utility.Location('/tmp/pyxbdist.RHB65sy/PyXB-1.1.5/pyxb/bundles/saml20/schemas/protocol.xsd', 115, 4)
    # Base type is pyxb.binding.datatypes.anyType
    
    # Element {urn:oasis:names:tc:SAML:2.0:assertion}AuthnContextClassRef uses Python identifier AuthnContextClassRef
    __AuthnContextClassRef = pyxb.binding.content.ElementUse(pyxb.namespace.ExpandedName(pyxb.namespace.NamespaceForURI(u'urn:oasis:names:tc:SAML:2.0:assertion'), u'AuthnContextClassRef'), 'AuthnContextClassRef', '__urnoasisnamestcSAML2_0protocol_RequestedAuthnContextType_urnoasisnamestcSAML2_0assertionAuthnContextClassRef', True)
    __AuthnContextClassRef._DeclarationLocation = pyxb.utils.utility.Location('/tmp/pyxbdist.RHB65sy/PyXB-1.1.5/pyxb/bundles/saml20/schemas/assertion.xsd', 219, 4)
    __AuthnContextClassRef._UseLocation = pyxb.utils.utility.Location('/tmp/pyxbdist.RHB65sy/PyXB-1.1.5/pyxb/bundles/saml20/schemas/protocol.xsd', 116, 8)

    
    AuthnContextClassRef = property(__AuthnContextClassRef.value, __AuthnContextClassRef.set, None, None)

    
    # Element {urn:oasis:names:tc:SAML:2.0:assertion}AuthnContextDeclRef uses Python identifier AuthnContextDeclRef
    __AuthnContextDeclRef = pyxb.binding.content.ElementUse(pyxb.namespace.ExpandedName(pyxb.namespace.NamespaceForURI(u'urn:oasis:names:tc:SAML:2.0:assertion'), u'AuthnContextDeclRef'), 'AuthnContextDeclRef', '__urnoasisnamestcSAML2_0protocol_RequestedAuthnContextType_urnoasisnamestcSAML2_0assertionAuthnContextDeclRef', True)
    __AuthnContextDeclRef._DeclarationLocation = pyxb.utils.utility.Location('/tmp/pyxbdist.RHB65sy/PyXB-1.1.5/pyxb/bundles/saml20/schemas/assertion.xsd', 220, 4)
    __AuthnContextDeclRef._UseLocation = pyxb.utils.utility.Location('/tmp/pyxbdist.RHB65sy/PyXB-1.1.5/pyxb/bundles/saml20/schemas/protocol.xsd', 116, 8)

    
    AuthnContextDeclRef = property(__AuthnContextDeclRef.value, __AuthnContextDeclRef.set, None, None)

    
    # Attribute Comparison uses Python identifier Comparison
    __Comparison = pyxb.binding.content.AttributeUse(pyxb.namespace.ExpandedName(None, u'Comparison'), 'Comparison', '__urnoasisnamestcSAML2_0protocol_RequestedAuthnContextType_Comparison', AuthnContextComparisonType)
    __Comparison._DeclarationLocation = pyxb.utils.utility.Location('/tmp/pyxbdist.RHB65sy/PyXB-1.1.5/pyxb/bundles/saml20/schemas/protocol.xsd', 120, 8)
    __Comparison._UseLocation = pyxb.utils.utility.Location('/tmp/pyxbdist.RHB65sy/PyXB-1.1.5/pyxb/bundles/saml20/schemas/protocol.xsd', 120, 8)
    
    Comparison = property(__Comparison.value, __Comparison.set, None, None)


    _ElementMap = {
        __AuthnContextClassRef.name() : __AuthnContextClassRef,
        __AuthnContextDeclRef.name() : __AuthnContextDeclRef
    }
    _AttributeMap = {
        __Comparison.name() : __Comparison
    }
Namespace.addCategoryObject('typeBinding', u'RequestedAuthnContextType', RequestedAuthnContextType)


# Complex type {urn:oasis:names:tc:SAML:2.0:protocol}StatusType with content type ELEMENT_ONLY
class StatusType (pyxb.binding.basis.complexTypeDefinition):
    _TypeDefinition = None
    _ContentTypeTag = pyxb.binding.basis.complexTypeDefinition._CT_ELEMENT_ONLY
    _Abstract = False
    _ExpandedName = pyxb.namespace.ExpandedName(Namespace, u'StatusType')
    _DefinitionLocation = pyxb.utils.utility.Location('/tmp/pyxbdist.RHB65sy/PyXB-1.1.5/pyxb/bundles/saml20/schemas/protocol.xsd', 62, 4)
    # Base type is pyxb.binding.datatypes.anyType
    
    # Element {urn:oasis:names:tc:SAML:2.0:protocol}StatusDetail uses Python identifier StatusDetail
    __StatusDetail = pyxb.binding.content.ElementUse(pyxb.namespace.ExpandedName(Namespace, u'StatusDetail'), 'StatusDetail', '__urnoasisnamestcSAML2_0protocol_StatusType_urnoasisnamestcSAML2_0protocolStatusDetail', False)
    __StatusDetail._DeclarationLocation = pyxb.utils.utility.Location('/tmp/pyxbdist.RHB65sy/PyXB-1.1.5/pyxb/bundles/saml20/schemas/protocol.xsd', 77, 4)
    __StatusDetail._UseLocation = pyxb.utils.utility.Location('/tmp/pyxbdist.RHB65sy/PyXB-1.1.5/pyxb/bundles/saml20/schemas/protocol.xsd', 63, 8)

    
    StatusDetail = property(__StatusDetail.value, __StatusDetail.set, None, None)

    
    # Element {urn:oasis:names:tc:SAML:2.0:protocol}StatusCode uses Python identifier StatusCode
    __StatusCode = pyxb.binding.content.ElementUse(pyxb.namespace.ExpandedName(Namespace, u'StatusCode'), 'StatusCode', '__urnoasisnamestcSAML2_0protocol_StatusType_urnoasisnamestcSAML2_0protocolStatusCode', False)
    __StatusCode._DeclarationLocation = pyxb.utils.utility.Location('/tmp/pyxbdist.RHB65sy/PyXB-1.1.5/pyxb/bundles/saml20/schemas/protocol.xsd', 69, 4)
    __StatusCode._UseLocation = pyxb.utils.utility.Location('/tmp/pyxbdist.RHB65sy/PyXB-1.1.5/pyxb/bundles/saml20/schemas/protocol.xsd', 63, 8)

    
    StatusCode = property(__StatusCode.value, __StatusCode.set, None, None)

    
    # Element {urn:oasis:names:tc:SAML:2.0:protocol}StatusMessage uses Python identifier StatusMessage
    __StatusMessage = pyxb.binding.content.ElementUse(pyxb.namespace.ExpandedName(Namespace, u'StatusMessage'), 'StatusMessage', '__urnoasisnamestcSAML2_0protocol_StatusType_urnoasisnamestcSAML2_0protocolStatusMessage', False)
    __StatusMessage._DeclarationLocation = pyxb.utils.utility.Location('/tmp/pyxbdist.RHB65sy/PyXB-1.1.5/pyxb/bundles/saml20/schemas/protocol.xsd', 76, 4)
    __StatusMessage._UseLocation = pyxb.utils.utility.Location('/tmp/pyxbdist.RHB65sy/PyXB-1.1.5/pyxb/bundles/saml20/schemas/protocol.xsd', 63, 8)

    
    StatusMessage = property(__StatusMessage.value, __StatusMessage.set, None, None)


    _ElementMap = {
        __StatusDetail.name() : __StatusDetail,
        __StatusCode.name() : __StatusCode,
        __StatusMessage.name() : __StatusMessage
    }
    _AttributeMap = {
        
    }
Namespace.addCategoryObject('typeBinding', u'StatusType', StatusType)


# Complex type {urn:oasis:names:tc:SAML:2.0:protocol}StatusResponseType with content type ELEMENT_ONLY
class StatusResponseType (pyxb.binding.basis.complexTypeDefinition):
    _TypeDefinition = None
    _ContentTypeTag = pyxb.binding.basis.complexTypeDefinition._CT_ELEMENT_ONLY
    _Abstract = False
    _ExpandedName = pyxb.namespace.ExpandedName(Namespace, u'StatusResponseType')
    _DefinitionLocation = pyxb.utils.utility.Location('/tmp/pyxbdist.RHB65sy/PyXB-1.1.5/pyxb/bundles/saml20/schemas/protocol.xsd', 47, 4)
    # Base type is pyxb.binding.datatypes.anyType
    
    # Element {urn:oasis:names:tc:SAML:2.0:protocol}Extensions uses Python identifier Extensions
    __Extensions = pyxb.binding.content.ElementUse(pyxb.namespace.ExpandedName(Namespace, u'Extensions'), 'Extensions', '__urnoasisnamestcSAML2_0protocol_StatusResponseType_urnoasisnamestcSAML2_0protocolExtensions', False)
    __Extensions._DeclarationLocation = pyxb.utils.utility.Location('/tmp/pyxbdist.RHB65sy/PyXB-1.1.5/pyxb/bundles/saml20/schemas/protocol.xsd', 41, 4)
    __Extensions._UseLocation = pyxb.utils.utility.Location('/tmp/pyxbdist.RHB65sy/PyXB-1.1.5/pyxb/bundles/saml20/schemas/protocol.xsd', 48, 5)

    
    Extensions = property(__Extensions.value, __Extensions.set, None, None)

    
    # Element {urn:oasis:names:tc:SAML:2.0:protocol}Status uses Python identifier Status
    __Status = pyxb.binding.content.ElementUse(pyxb.namespace.ExpandedName(Namespace, u'Status'), 'Status', '__urnoasisnamestcSAML2_0protocol_StatusResponseType_urnoasisnamestcSAML2_0protocolStatus', False)
    __Status._DeclarationLocation = pyxb.utils.utility.Location('/tmp/pyxbdist.RHB65sy/PyXB-1.1.5/pyxb/bundles/saml20/schemas/protocol.xsd', 61, 4)
    __Status._UseLocation = pyxb.utils.utility.Location('/tmp/pyxbdist.RHB65sy/PyXB-1.1.5/pyxb/bundles/saml20/schemas/protocol.xsd', 48, 5)

    
    Status = property(__Status.value, __Status.set, None, None)

    
    # Element {urn:oasis:names:tc:SAML:2.0:assertion}Issuer uses Python identifier Issuer
    __Issuer = pyxb.binding.content.ElementUse(pyxb.namespace.ExpandedName(pyxb.namespace.NamespaceForURI(u'urn:oasis:names:tc:SAML:2.0:assertion'), u'Issuer'), 'Issuer', '__urnoasisnamestcSAML2_0protocol_StatusResponseType_urnoasisnamestcSAML2_0assertionIssuer', False)
    __Issuer._DeclarationLocation = pyxb.utils.utility.Location('/tmp/pyxbdist.RHB65sy/PyXB-1.1.5/pyxb/bundles/saml20/schemas/assertion.xsd', 54, 4)
    __Issuer._UseLocation = pyxb.utils.utility.Location('/tmp/pyxbdist.RHB65sy/PyXB-1.1.5/pyxb/bundles/saml20/schemas/protocol.xsd', 48, 5)

    
    Issuer = property(__Issuer.value, __Issuer.set, None, None)

    
    # Element {http://www.w3.org/2000/09/xmldsig#}Signature uses Python identifier Signature
    __Signature = pyxb.binding.content.ElementUse(pyxb.namespace.ExpandedName(pyxb.namespace.NamespaceForURI(u'http://www.w3.org/2000/09/xmldsig#'), u'Signature'), 'Signature', '__urnoasisnamestcSAML2_0protocol_StatusResponseType_httpwww_w3_org200009xmldsigSignature', False)
    __Signature._DeclarationLocation = pyxb.utils.utility.Location('/tmp/pyxbdist.RHB65sy/PyXB-1.1.5/pyxb/bundles/wssplat/schemas/ds.xsd', 43, 0)
    __Signature._UseLocation = pyxb.utils.utility.Location('/tmp/pyxbdist.RHB65sy/PyXB-1.1.5/pyxb/bundles/saml20/schemas/protocol.xsd', 48, 5)

    
    Signature = property(__Signature.value, __Signature.set, None, None)

    
    # Attribute Version uses Python identifier Version
    __Version = pyxb.binding.content.AttributeUse(pyxb.namespace.ExpandedName(None, u'Version'), 'Version', '__urnoasisnamestcSAML2_0protocol_StatusResponseType_Version', pyxb.binding.datatypes.string, required=True)
    __Version._DeclarationLocation = pyxb.utils.utility.Location('/tmp/pyxbdist.RHB65sy/PyXB-1.1.5/pyxb/bundles/saml20/schemas/protocol.xsd', 56, 5)
    __Version._UseLocation = pyxb.utils.utility.Location('/tmp/pyxbdist.RHB65sy/PyXB-1.1.5/pyxb/bundles/saml20/schemas/protocol.xsd', 56, 5)
    
    Version = property(__Version.value, __Version.set, None, None)

    
    # Attribute Destination uses Python identifier Destination
    __Destination = pyxb.binding.content.AttributeUse(pyxb.namespace.ExpandedName(None, u'Destination'), 'Destination', '__urnoasisnamestcSAML2_0protocol_StatusResponseType_Destination', pyxb.binding.datatypes.anyURI)
    __Destination._DeclarationLocation = pyxb.utils.utility.Location('/tmp/pyxbdist.RHB65sy/PyXB-1.1.5/pyxb/bundles/saml20/schemas/protocol.xsd', 58, 5)
    __Destination._UseLocation = pyxb.utils.utility.Location('/tmp/pyxbdist.RHB65sy/PyXB-1.1.5/pyxb/bundles/saml20/schemas/protocol.xsd', 58, 5)
    
    Destination = property(__Destination.value, __Destination.set, None, None)

    
    # Attribute IssueInstant uses Python identifier IssueInstant
    __IssueInstant = pyxb.binding.content.AttributeUse(pyxb.namespace.ExpandedName(None, u'IssueInstant'), 'IssueInstant', '__urnoasisnamestcSAML2_0protocol_StatusResponseType_IssueInstant', pyxb.binding.datatypes.dateTime, required=True)
    __IssueInstant._DeclarationLocation = pyxb.utils.utility.Location('/tmp/pyxbdist.RHB65sy/PyXB-1.1.5/pyxb/bundles/saml20/schemas/protocol.xsd', 57, 5)
    __IssueInstant._UseLocation = pyxb.utils.utility.Location('/tmp/pyxbdist.RHB65sy/PyXB-1.1.5/pyxb/bundles/saml20/schemas/protocol.xsd', 57, 5)
    
    IssueInstant = property(__IssueInstant.value, __IssueInstant.set, None, None)

    
    # Attribute ID uses Python identifier ID
    __ID = pyxb.binding.content.AttributeUse(pyxb.namespace.ExpandedName(None, u'ID'), 'ID', '__urnoasisnamestcSAML2_0protocol_StatusResponseType_ID', pyxb.binding.datatypes.ID, required=True)
    __ID._DeclarationLocation = pyxb.utils.utility.Location('/tmp/pyxbdist.RHB65sy/PyXB-1.1.5/pyxb/bundles/saml20/schemas/protocol.xsd', 54, 5)
    __ID._UseLocation = pyxb.utils.utility.Location('/tmp/pyxbdist.RHB65sy/PyXB-1.1.5/pyxb/bundles/saml20/schemas/protocol.xsd', 54, 5)
    
    ID = property(__ID.value, __ID.set, None, None)

    
    # Attribute Consent uses Python identifier Consent
    __Consent = pyxb.binding.content.AttributeUse(pyxb.namespace.ExpandedName(None, u'Consent'), 'Consent', '__urnoasisnamestcSAML2_0protocol_StatusResponseType_Consent', pyxb.binding.datatypes.anyURI)
    __Consent._DeclarationLocation = pyxb.utils.utility.Location('/tmp/pyxbdist.RHB65sy/PyXB-1.1.5/pyxb/bundles/saml20/schemas/protocol.xsd', 59, 5)
    __Consent._UseLocation = pyxb.utils.utility.Location('/tmp/pyxbdist.RHB65sy/PyXB-1.1.5/pyxb/bundles/saml20/schemas/protocol.xsd', 59, 5)
    
    Consent = property(__Consent.value, __Consent.set, None, None)

    
    # Attribute InResponseTo uses Python identifier InResponseTo
    __InResponseTo = pyxb.binding.content.AttributeUse(pyxb.namespace.ExpandedName(None, u'InResponseTo'), 'InResponseTo', '__urnoasisnamestcSAML2_0protocol_StatusResponseType_InResponseTo', pyxb.binding.datatypes.NCName)
    __InResponseTo._DeclarationLocation = pyxb.utils.utility.Location('/tmp/pyxbdist.RHB65sy/PyXB-1.1.5/pyxb/bundles/saml20/schemas/protocol.xsd', 55, 5)
    __InResponseTo._UseLocation = pyxb.utils.utility.Location('/tmp/pyxbdist.RHB65sy/PyXB-1.1.5/pyxb/bundles/saml20/schemas/protocol.xsd', 55, 5)
    
    InResponseTo = property(__InResponseTo.value, __InResponseTo.set, None, None)


    _ElementMap = {
        __Extensions.name() : __Extensions,
        __Status.name() : __Status,
        __Issuer.name() : __Issuer,
        __Signature.name() : __Signature
    }
    _AttributeMap = {
        __Version.name() : __Version,
        __Destination.name() : __Destination,
        __IssueInstant.name() : __IssueInstant,
        __ID.name() : __ID,
        __Consent.name() : __Consent,
        __InResponseTo.name() : __InResponseTo
    }
Namespace.addCategoryObject('typeBinding', u'StatusResponseType', StatusResponseType)


# Complex type {urn:oasis:names:tc:SAML:2.0:protocol}ArtifactResponseType with content type ELEMENT_ONLY
class ArtifactResponseType (StatusResponseType):
    _TypeDefinition = None
    _ContentTypeTag = pyxb.binding.basis.complexTypeDefinition._CT_ELEMENT_ONLY
    _Abstract = False
    _ExpandedName = pyxb.namespace.ExpandedName(Namespace, u'ArtifactResponseType')
    _DefinitionLocation = pyxb.utils.utility.Location('/tmp/pyxbdist.RHB65sy/PyXB-1.1.5/pyxb/bundles/saml20/schemas/protocol.xsd', 225, 4)
    # Base type is StatusResponseType
    
    # Element Extensions ({urn:oasis:names:tc:SAML:2.0:protocol}Extensions) inherited from {urn:oasis:names:tc:SAML:2.0:protocol}StatusResponseType
    
    # Element Issuer ({urn:oasis:names:tc:SAML:2.0:assertion}Issuer) inherited from {urn:oasis:names:tc:SAML:2.0:protocol}StatusResponseType
    
    # Element Signature ({http://www.w3.org/2000/09/xmldsig#}Signature) inherited from {urn:oasis:names:tc:SAML:2.0:protocol}StatusResponseType
    
    # Element Status ({urn:oasis:names:tc:SAML:2.0:protocol}Status) inherited from {urn:oasis:names:tc:SAML:2.0:protocol}StatusResponseType
    
    # Attribute Version inherited from {urn:oasis:names:tc:SAML:2.0:protocol}StatusResponseType
    
    # Attribute Destination inherited from {urn:oasis:names:tc:SAML:2.0:protocol}StatusResponseType
    
    # Attribute IssueInstant inherited from {urn:oasis:names:tc:SAML:2.0:protocol}StatusResponseType
    
    # Attribute ID inherited from {urn:oasis:names:tc:SAML:2.0:protocol}StatusResponseType
    
    # Attribute Consent inherited from {urn:oasis:names:tc:SAML:2.0:protocol}StatusResponseType
    
    # Attribute InResponseTo inherited from {urn:oasis:names:tc:SAML:2.0:protocol}StatusResponseType
    _HasWildcardElement = True

    _ElementMap = StatusResponseType._ElementMap.copy()
    _ElementMap.update({
        
    })
    _AttributeMap = StatusResponseType._AttributeMap.copy()
    _AttributeMap.update({
        
    })
Namespace.addCategoryObject('typeBinding', u'ArtifactResponseType', ArtifactResponseType)


# Complex type {urn:oasis:names:tc:SAML:2.0:protocol}IDPEntryType with content type EMPTY
class IDPEntryType (pyxb.binding.basis.complexTypeDefinition):
    _TypeDefinition = None
    _ContentTypeTag = pyxb.binding.basis.complexTypeDefinition._CT_EMPTY
    _Abstract = False
    _ExpandedName = pyxb.namespace.ExpandedName(Namespace, u'IDPEntryType')
    _DefinitionLocation = pyxb.utils.utility.Location('/tmp/pyxbdist.RHB65sy/PyXB-1.1.5/pyxb/bundles/saml20/schemas/protocol.xsd', 196, 4)
    # Base type is pyxb.binding.datatypes.anyType
    
    # Attribute Loc uses Python identifier Loc
    __Loc = pyxb.binding.content.AttributeUse(pyxb.namespace.ExpandedName(None, u'Loc'), 'Loc', '__urnoasisnamestcSAML2_0protocol_IDPEntryType_Loc', pyxb.binding.datatypes.anyURI)
    __Loc._DeclarationLocation = pyxb.utils.utility.Location('/tmp/pyxbdist.RHB65sy/PyXB-1.1.5/pyxb/bundles/saml20/schemas/protocol.xsd', 199, 8)
    __Loc._UseLocation = pyxb.utils.utility.Location('/tmp/pyxbdist.RHB65sy/PyXB-1.1.5/pyxb/bundles/saml20/schemas/protocol.xsd', 199, 8)
    
    Loc = property(__Loc.value, __Loc.set, None, None)

    
    # Attribute Name uses Python identifier Name
    __Name = pyxb.binding.content.AttributeUse(pyxb.namespace.ExpandedName(None, u'Name'), 'Name', '__urnoasisnamestcSAML2_0protocol_IDPEntryType_Name', pyxb.binding.datatypes.string)
    __Name._DeclarationLocation = pyxb.utils.utility.Location('/tmp/pyxbdist.RHB65sy/PyXB-1.1.5/pyxb/bundles/saml20/schemas/protocol.xsd', 198, 8)
    __Name._UseLocation = pyxb.utils.utility.Location('/tmp/pyxbdist.RHB65sy/PyXB-1.1.5/pyxb/bundles/saml20/schemas/protocol.xsd', 198, 8)
    
    Name = property(__Name.value, __Name.set, None, None)

    
    # Attribute ProviderID uses Python identifier ProviderID
    __ProviderID = pyxb.binding.content.AttributeUse(pyxb.namespace.ExpandedName(None, u'ProviderID'), 'ProviderID', '__urnoasisnamestcSAML2_0protocol_IDPEntryType_ProviderID', pyxb.binding.datatypes.anyURI, required=True)
    __ProviderID._DeclarationLocation = pyxb.utils.utility.Location('/tmp/pyxbdist.RHB65sy/PyXB-1.1.5/pyxb/bundles/saml20/schemas/protocol.xsd', 197, 8)
    __ProviderID._UseLocation = pyxb.utils.utility.Location('/tmp/pyxbdist.RHB65sy/PyXB-1.1.5/pyxb/bundles/saml20/schemas/protocol.xsd', 197, 8)
    
    ProviderID = property(__ProviderID.value, __ProviderID.set, None, None)


    _ElementMap = {
        
    }
    _AttributeMap = {
        __Loc.name() : __Loc,
        __Name.name() : __Name,
        __ProviderID.name() : __ProviderID
    }
Namespace.addCategoryObject('typeBinding', u'IDPEntryType', IDPEntryType)


# Complex type {urn:oasis:names:tc:SAML:2.0:protocol}StatusCodeType with content type ELEMENT_ONLY
class StatusCodeType (pyxb.binding.basis.complexTypeDefinition):
    _TypeDefinition = None
    _ContentTypeTag = pyxb.binding.basis.complexTypeDefinition._CT_ELEMENT_ONLY
    _Abstract = False
    _ExpandedName = pyxb.namespace.ExpandedName(Namespace, u'StatusCodeType')
    _DefinitionLocation = pyxb.utils.utility.Location('/tmp/pyxbdist.RHB65sy/PyXB-1.1.5/pyxb/bundles/saml20/schemas/protocol.xsd', 70, 4)
    # Base type is pyxb.binding.datatypes.anyType
    
    # Element {urn:oasis:names:tc:SAML:2.0:protocol}StatusCode uses Python identifier StatusCode
    __StatusCode = pyxb.binding.content.ElementUse(pyxb.namespace.ExpandedName(Namespace, u'StatusCode'), 'StatusCode', '__urnoasisnamestcSAML2_0protocol_StatusCodeType_urnoasisnamestcSAML2_0protocolStatusCode', False)
    __StatusCode._DeclarationLocation = pyxb.utils.utility.Location('/tmp/pyxbdist.RHB65sy/PyXB-1.1.5/pyxb/bundles/saml20/schemas/protocol.xsd', 69, 4)
    __StatusCode._UseLocation = pyxb.utils.utility.Location('/tmp/pyxbdist.RHB65sy/PyXB-1.1.5/pyxb/bundles/saml20/schemas/protocol.xsd', 71, 8)

    
    StatusCode = property(__StatusCode.value, __StatusCode.set, None, None)

    
    # Attribute Value uses Python identifier Value
    __Value = pyxb.binding.content.AttributeUse(pyxb.namespace.ExpandedName(None, u'Value'), 'Value', '__urnoasisnamestcSAML2_0protocol_StatusCodeType_Value', pyxb.binding.datatypes.anyURI, required=True)
    __Value._DeclarationLocation = pyxb.utils.utility.Location('/tmp/pyxbdist.RHB65sy/PyXB-1.1.5/pyxb/bundles/saml20/schemas/protocol.xsd', 74, 8)
    __Value._UseLocation = pyxb.utils.utility.Location('/tmp/pyxbdist.RHB65sy/PyXB-1.1.5/pyxb/bundles/saml20/schemas/protocol.xsd', 74, 8)
    
    Value = property(__Value.value, __Value.set, None, None)


    _ElementMap = {
        __StatusCode.name() : __StatusCode
    }
    _AttributeMap = {
        __Value.name() : __Value
    }
Namespace.addCategoryObject('typeBinding', u'StatusCodeType', StatusCodeType)


# Complex type {urn:oasis:names:tc:SAML:2.0:protocol}NameIDMappingRequestType with content type ELEMENT_ONLY
class NameIDMappingRequestType (RequestAbstractType):
    _TypeDefinition = None
    _ContentTypeTag = pyxb.binding.basis.complexTypeDefinition._CT_ELEMENT_ONLY
    _Abstract = False
    _ExpandedName = pyxb.namespace.ExpandedName(Namespace, u'NameIDMappingRequestType')
    _DefinitionLocation = pyxb.utils.utility.Location('/tmp/pyxbdist.RHB65sy/PyXB-1.1.5/pyxb/bundles/saml20/schemas/protocol.xsd', 277, 4)
    # Base type is RequestAbstractType
    
    # Element Extensions ({urn:oasis:names:tc:SAML:2.0:protocol}Extensions) inherited from {urn:oasis:names:tc:SAML:2.0:protocol}RequestAbstractType
    
    # Element Issuer ({urn:oasis:names:tc:SAML:2.0:assertion}Issuer) inherited from {urn:oasis:names:tc:SAML:2.0:protocol}RequestAbstractType
    
    # Element {urn:oasis:names:tc:SAML:2.0:assertion}BaseID uses Python identifier BaseID
    __BaseID = pyxb.binding.content.ElementUse(pyxb.namespace.ExpandedName(pyxb.namespace.NamespaceForURI(u'urn:oasis:names:tc:SAML:2.0:assertion'), u'BaseID'), 'BaseID', '__urnoasisnamestcSAML2_0protocol_NameIDMappingRequestType_urnoasisnamestcSAML2_0assertionBaseID', False)
    __BaseID._DeclarationLocation = pyxb.utils.utility.Location('/tmp/pyxbdist.RHB65sy/PyXB-1.1.5/pyxb/bundles/saml20/schemas/assertion.xsd', 33, 4)
    __BaseID._UseLocation = None

    
    BaseID = property(__BaseID.value, __BaseID.set, None, None)

    
    # Element {urn:oasis:names:tc:SAML:2.0:assertion}NameID uses Python identifier NameID
    __NameID = pyxb.binding.content.ElementUse(pyxb.namespace.ExpandedName(pyxb.namespace.NamespaceForURI(u'urn:oasis:names:tc:SAML:2.0:assertion'), u'NameID'), 'NameID', '__urnoasisnamestcSAML2_0protocol_NameIDMappingRequestType_urnoasisnamestcSAML2_0assertionNameID', False)
    __NameID._DeclarationLocation = pyxb.utils.utility.Location('/tmp/pyxbdist.RHB65sy/PyXB-1.1.5/pyxb/bundles/saml20/schemas/assertion.xsd', 37, 4)
    __NameID._UseLocation = None

    
    NameID = property(__NameID.value, __NameID.set, None, None)

    
    # Element Signature ({http://www.w3.org/2000/09/xmldsig#}Signature) inherited from {urn:oasis:names:tc:SAML:2.0:protocol}RequestAbstractType
    
    # Element {urn:oasis:names:tc:SAML:2.0:assertion}EncryptedID uses Python identifier EncryptedID
    __EncryptedID = pyxb.binding.content.ElementUse(pyxb.namespace.ExpandedName(pyxb.namespace.NamespaceForURI(u'urn:oasis:names:tc:SAML:2.0:assertion'), u'EncryptedID'), 'EncryptedID', '__urnoasisnamestcSAML2_0protocol_NameIDMappingRequestType_urnoasisnamestcSAML2_0assertionEncryptedID', False)
    __EncryptedID._DeclarationLocation = pyxb.utils.utility.Location('/tmp/pyxbdist.RHB65sy/PyXB-1.1.5/pyxb/bundles/saml20/schemas/assertion.xsd', 53, 4)
    __EncryptedID._UseLocation = None

    
    EncryptedID = property(__EncryptedID.value, __EncryptedID.set, None, None)

    
    # Element {urn:oasis:names:tc:SAML:2.0:protocol}NameIDPolicy uses Python identifier NameIDPolicy
    __NameIDPolicy = pyxb.binding.content.ElementUse(pyxb.namespace.ExpandedName(Namespace, u'NameIDPolicy'), 'NameIDPolicy', '__urnoasisnamestcSAML2_0protocol_NameIDMappingRequestType_urnoasisnamestcSAML2_0protocolNameIDPolicy', False)
    __NameIDPolicy._DeclarationLocation = pyxb.utils.utility.Location('/tmp/pyxbdist.RHB65sy/PyXB-1.1.5/pyxb/bundles/saml20/schemas/protocol.xsd', 173, 4)
    __NameIDPolicy._UseLocation = None

    
    NameIDPolicy = property(__NameIDPolicy.value, __NameIDPolicy.set, None, None)

    
    # Attribute Destination inherited from {urn:oasis:names:tc:SAML:2.0:protocol}RequestAbstractType
    
    # Attribute Consent inherited from {urn:oasis:names:tc:SAML:2.0:protocol}RequestAbstractType
    
    # Attribute ID inherited from {urn:oasis:names:tc:SAML:2.0:protocol}RequestAbstractType
    
    # Attribute IssueInstant inherited from {urn:oasis:names:tc:SAML:2.0:protocol}RequestAbstractType
    
    # Attribute Version inherited from {urn:oasis:names:tc:SAML:2.0:protocol}RequestAbstractType

    _ElementMap = RequestAbstractType._ElementMap.copy()
    _ElementMap.update({
        __BaseID.name() : __BaseID,
        __NameID.name() : __NameID,
        __EncryptedID.name() : __EncryptedID,
        __NameIDPolicy.name() : __NameIDPolicy
    })
    _AttributeMap = RequestAbstractType._AttributeMap.copy()
    _AttributeMap.update({
        
    })
Namespace.addCategoryObject('typeBinding', u'NameIDMappingRequestType', NameIDMappingRequestType)


# Complex type {urn:oasis:names:tc:SAML:2.0:protocol}IDPListType with content type ELEMENT_ONLY
class IDPListType (pyxb.binding.basis.complexTypeDefinition):
    _TypeDefinition = None
    _ContentTypeTag = pyxb.binding.basis.complexTypeDefinition._CT_ELEMENT_ONLY
    _Abstract = False
    _ExpandedName = pyxb.namespace.ExpandedName(Namespace, u'IDPListType')
    _DefinitionLocation = pyxb.utils.utility.Location('/tmp/pyxbdist.RHB65sy/PyXB-1.1.5/pyxb/bundles/saml20/schemas/protocol.xsd', 189, 4)
    # Base type is pyxb.binding.datatypes.anyType
    
    # Element {urn:oasis:names:tc:SAML:2.0:protocol}GetComplete uses Python identifier GetComplete
    __GetComplete = pyxb.binding.content.ElementUse(pyxb.namespace.ExpandedName(Namespace, u'GetComplete'), 'GetComplete', '__urnoasisnamestcSAML2_0protocol_IDPListType_urnoasisnamestcSAML2_0protocolGetComplete', False)
    __GetComplete._DeclarationLocation = pyxb.utils.utility.Location('/tmp/pyxbdist.RHB65sy/PyXB-1.1.5/pyxb/bundles/saml20/schemas/protocol.xsd', 201, 4)
    __GetComplete._UseLocation = pyxb.utils.utility.Location('/tmp/pyxbdist.RHB65sy/PyXB-1.1.5/pyxb/bundles/saml20/schemas/protocol.xsd', 190, 8)

    
    GetComplete = property(__GetComplete.value, __GetComplete.set, None, None)

    
    # Element {urn:oasis:names:tc:SAML:2.0:protocol}IDPEntry uses Python identifier IDPEntry
    __IDPEntry = pyxb.binding.content.ElementUse(pyxb.namespace.ExpandedName(Namespace, u'IDPEntry'), 'IDPEntry', '__urnoasisnamestcSAML2_0protocol_IDPListType_urnoasisnamestcSAML2_0protocolIDPEntry', True)
    __IDPEntry._DeclarationLocation = pyxb.utils.utility.Location('/tmp/pyxbdist.RHB65sy/PyXB-1.1.5/pyxb/bundles/saml20/schemas/protocol.xsd', 195, 4)
    __IDPEntry._UseLocation = pyxb.utils.utility.Location('/tmp/pyxbdist.RHB65sy/PyXB-1.1.5/pyxb/bundles/saml20/schemas/protocol.xsd', 190, 8)

    
    IDPEntry = property(__IDPEntry.value, __IDPEntry.set, None, None)


    _ElementMap = {
        __GetComplete.name() : __GetComplete,
        __IDPEntry.name() : __IDPEntry
    }
    _AttributeMap = {
        
    }
Namespace.addCategoryObject('typeBinding', u'IDPListType', IDPListType)


# Complex type {urn:oasis:names:tc:SAML:2.0:protocol}ExtensionsType with content type ELEMENT_ONLY
class ExtensionsType (pyxb.binding.basis.complexTypeDefinition):
    _TypeDefinition = None
    _ContentTypeTag = pyxb.binding.basis.complexTypeDefinition._CT_ELEMENT_ONLY
    _Abstract = False
    _ExpandedName = pyxb.namespace.ExpandedName(Namespace, u'ExtensionsType')
    _DefinitionLocation = pyxb.utils.utility.Location('/tmp/pyxbdist.RHB65sy/PyXB-1.1.5/pyxb/bundles/saml20/schemas/protocol.xsd', 42, 4)
    # Base type is pyxb.binding.datatypes.anyType
    _HasWildcardElement = True

    _ElementMap = {
        
    }
    _AttributeMap = {
        
    }
Namespace.addCategoryObject('typeBinding', u'ExtensionsType', ExtensionsType)


# Complex type {urn:oasis:names:tc:SAML:2.0:protocol}NameIDPolicyType with content type EMPTY
class NameIDPolicyType (pyxb.binding.basis.complexTypeDefinition):
    _TypeDefinition = None
    _ContentTypeTag = pyxb.binding.basis.complexTypeDefinition._CT_EMPTY
    _Abstract = False
    _ExpandedName = pyxb.namespace.ExpandedName(Namespace, u'NameIDPolicyType')
    _DefinitionLocation = pyxb.utils.utility.Location('/tmp/pyxbdist.RHB65sy/PyXB-1.1.5/pyxb/bundles/saml20/schemas/protocol.xsd', 174, 4)
    # Base type is pyxb.binding.datatypes.anyType
    
    # Attribute Format uses Python identifier Format
    __Format = pyxb.binding.content.AttributeUse(pyxb.namespace.ExpandedName(None, u'Format'), 'Format', '__urnoasisnamestcSAML2_0protocol_NameIDPolicyType_Format', pyxb.binding.datatypes.anyURI)
    __Format._DeclarationLocation = pyxb.utils.utility.Location('/tmp/pyxbdist.RHB65sy/PyXB-1.1.5/pyxb/bundles/saml20/schemas/protocol.xsd', 175, 8)
    __Format._UseLocation = pyxb.utils.utility.Location('/tmp/pyxbdist.RHB65sy/PyXB-1.1.5/pyxb/bundles/saml20/schemas/protocol.xsd', 175, 8)
    
    Format = property(__Format.value, __Format.set, None, None)

    
    # Attribute AllowCreate uses Python identifier AllowCreate
    __AllowCreate = pyxb.binding.content.AttributeUse(pyxb.namespace.ExpandedName(None, u'AllowCreate'), 'AllowCreate', '__urnoasisnamestcSAML2_0protocol_NameIDPolicyType_AllowCreate', pyxb.binding.datatypes.boolean)
    __AllowCreate._DeclarationLocation = pyxb.utils.utility.Location('/tmp/pyxbdist.RHB65sy/PyXB-1.1.5/pyxb/bundles/saml20/schemas/protocol.xsd', 177, 8)
    __AllowCreate._UseLocation = pyxb.utils.utility.Location('/tmp/pyxbdist.RHB65sy/PyXB-1.1.5/pyxb/bundles/saml20/schemas/protocol.xsd', 177, 8)
    
    AllowCreate = property(__AllowCreate.value, __AllowCreate.set, None, None)

    
    # Attribute SPNameQualifier uses Python identifier SPNameQualifier
    __SPNameQualifier = pyxb.binding.content.AttributeUse(pyxb.namespace.ExpandedName(None, u'SPNameQualifier'), 'SPNameQualifier', '__urnoasisnamestcSAML2_0protocol_NameIDPolicyType_SPNameQualifier', pyxb.binding.datatypes.string)
    __SPNameQualifier._DeclarationLocation = pyxb.utils.utility.Location('/tmp/pyxbdist.RHB65sy/PyXB-1.1.5/pyxb/bundles/saml20/schemas/protocol.xsd', 176, 8)
    __SPNameQualifier._UseLocation = pyxb.utils.utility.Location('/tmp/pyxbdist.RHB65sy/PyXB-1.1.5/pyxb/bundles/saml20/schemas/protocol.xsd', 176, 8)
    
    SPNameQualifier = property(__SPNameQualifier.value, __SPNameQualifier.set, None, None)


    _ElementMap = {
        
    }
    _AttributeMap = {
        __Format.name() : __Format,
        __AllowCreate.name() : __AllowCreate,
        __SPNameQualifier.name() : __SPNameQualifier
    }
Namespace.addCategoryObject('typeBinding', u'NameIDPolicyType', NameIDPolicyType)


# Complex type {urn:oasis:names:tc:SAML:2.0:protocol}AuthnQueryType with content type ELEMENT_ONLY
class AuthnQueryType (SubjectQueryAbstractType):
    _TypeDefinition = None
    _ContentTypeTag = pyxb.binding.basis.complexTypeDefinition._CT_ELEMENT_ONLY
    _Abstract = False
    _ExpandedName = pyxb.namespace.ExpandedName(Namespace, u'AuthnQueryType')
    _DefinitionLocation = pyxb.utils.utility.Location('/tmp/pyxbdist.RHB65sy/PyXB-1.1.5/pyxb/bundles/saml20/schemas/protocol.xsd', 104, 4)
    # Base type is SubjectQueryAbstractType
    
    # Element {urn:oasis:names:tc:SAML:2.0:protocol}RequestedAuthnContext uses Python identifier RequestedAuthnContext
    __RequestedAuthnContext = pyxb.binding.content.ElementUse(pyxb.namespace.ExpandedName(Namespace, u'RequestedAuthnContext'), 'RequestedAuthnContext', '__urnoasisnamestcSAML2_0protocol_AuthnQueryType_urnoasisnamestcSAML2_0protocolRequestedAuthnContext', False)
    __RequestedAuthnContext._DeclarationLocation = pyxb.utils.utility.Location('/tmp/pyxbdist.RHB65sy/PyXB-1.1.5/pyxb/bundles/saml20/schemas/protocol.xsd', 114, 4)
    __RequestedAuthnContext._UseLocation = None

    
    RequestedAuthnContext = property(__RequestedAuthnContext.value, __RequestedAuthnContext.set, None, None)

    
    # Element Issuer ({urn:oasis:names:tc:SAML:2.0:assertion}Issuer) inherited from {urn:oasis:names:tc:SAML:2.0:protocol}RequestAbstractType
    
    # Element Subject ({urn:oasis:names:tc:SAML:2.0:assertion}Subject) inherited from {urn:oasis:names:tc:SAML:2.0:protocol}SubjectQueryAbstractType
    
    # Element Extensions ({urn:oasis:names:tc:SAML:2.0:protocol}Extensions) inherited from {urn:oasis:names:tc:SAML:2.0:protocol}RequestAbstractType
    
    # Element Signature ({http://www.w3.org/2000/09/xmldsig#}Signature) inherited from {urn:oasis:names:tc:SAML:2.0:protocol}RequestAbstractType
    
    # Attribute SessionIndex uses Python identifier SessionIndex
    __SessionIndex = pyxb.binding.content.AttributeUse(pyxb.namespace.ExpandedName(None, u'SessionIndex'), 'SessionIndex', '__urnoasisnamestcSAML2_0protocol_AuthnQueryType_SessionIndex', pyxb.binding.datatypes.string)
    __SessionIndex._DeclarationLocation = pyxb.utils.utility.Location('/tmp/pyxbdist.RHB65sy/PyXB-1.1.5/pyxb/bundles/saml20/schemas/protocol.xsd', 110, 16)
    __SessionIndex._UseLocation = pyxb.utils.utility.Location('/tmp/pyxbdist.RHB65sy/PyXB-1.1.5/pyxb/bundles/saml20/schemas/protocol.xsd', 110, 16)
    
    SessionIndex = property(__SessionIndex.value, __SessionIndex.set, None, None)

    
    # Attribute Version inherited from {urn:oasis:names:tc:SAML:2.0:protocol}RequestAbstractType
    
    # Attribute IssueInstant inherited from {urn:oasis:names:tc:SAML:2.0:protocol}RequestAbstractType
    
    # Attribute Destination inherited from {urn:oasis:names:tc:SAML:2.0:protocol}RequestAbstractType
    
    # Attribute Consent inherited from {urn:oasis:names:tc:SAML:2.0:protocol}RequestAbstractType
    
    # Attribute ID inherited from {urn:oasis:names:tc:SAML:2.0:protocol}RequestAbstractType

    _ElementMap = SubjectQueryAbstractType._ElementMap.copy()
    _ElementMap.update({
        __RequestedAuthnContext.name() : __RequestedAuthnContext
    })
    _AttributeMap = SubjectQueryAbstractType._AttributeMap.copy()
    _AttributeMap.update({
        __SessionIndex.name() : __SessionIndex
    })
Namespace.addCategoryObject('typeBinding', u'AuthnQueryType', AuthnQueryType)


# Complex type {urn:oasis:names:tc:SAML:2.0:protocol}ResponseType with content type ELEMENT_ONLY
class ResponseType (StatusResponseType):
    _TypeDefinition = None
    _ContentTypeTag = pyxb.binding.basis.complexTypeDefinition._CT_ELEMENT_ONLY
    _Abstract = False
    _ExpandedName = pyxb.namespace.ExpandedName(Namespace, u'ResponseType')
    _DefinitionLocation = pyxb.utils.utility.Location('/tmp/pyxbdist.RHB65sy/PyXB-1.1.5/pyxb/bundles/saml20/schemas/protocol.xsd', 203, 4)
    # Base type is StatusResponseType
    
    # Element {urn:oasis:names:tc:SAML:2.0:assertion}EncryptedAssertion uses Python identifier EncryptedAssertion
    __EncryptedAssertion = pyxb.binding.content.ElementUse(pyxb.namespace.ExpandedName(pyxb.namespace.NamespaceForURI(u'urn:oasis:names:tc:SAML:2.0:assertion'), u'EncryptedAssertion'), 'EncryptedAssertion', '__urnoasisnamestcSAML2_0protocol_ResponseType_urnoasisnamestcSAML2_0assertionEncryptedAssertion', True)
    __EncryptedAssertion._DeclarationLocation = pyxb.utils.utility.Location('/tmp/pyxbdist.RHB65sy/PyXB-1.1.5/pyxb/bundles/saml20/schemas/assertion.xsd', 178, 4)
    __EncryptedAssertion._UseLocation = None

    
    EncryptedAssertion = property(__EncryptedAssertion.value, __EncryptedAssertion.set, None, None)

    
    # Element Issuer ({urn:oasis:names:tc:SAML:2.0:assertion}Issuer) inherited from {urn:oasis:names:tc:SAML:2.0:protocol}StatusResponseType
    
    # Element {urn:oasis:names:tc:SAML:2.0:assertion}Assertion uses Python identifier Assertion
    __Assertion = pyxb.binding.content.ElementUse(pyxb.namespace.ExpandedName(pyxb.namespace.NamespaceForURI(u'urn:oasis:names:tc:SAML:2.0:assertion'), u'Assertion'), 'Assertion', '__urnoasisnamestcSAML2_0protocol_ResponseType_urnoasisnamestcSAML2_0assertionAssertion', True)
    __Assertion._DeclarationLocation = pyxb.utils.utility.Location('/tmp/pyxbdist.RHB65sy/PyXB-1.1.5/pyxb/bundles/saml20/schemas/assertion.xsd', 57, 4)
    __Assertion._UseLocation = None

    
    Assertion = property(__Assertion.value, __Assertion.set, None, None)

    
    # Element Status ({urn:oasis:names:tc:SAML:2.0:protocol}Status) inherited from {urn:oasis:names:tc:SAML:2.0:protocol}StatusResponseType
    
    # Element Extensions ({urn:oasis:names:tc:SAML:2.0:protocol}Extensions) inherited from {urn:oasis:names:tc:SAML:2.0:protocol}StatusResponseType
    
    # Element Signature ({http://www.w3.org/2000/09/xmldsig#}Signature) inherited from {urn:oasis:names:tc:SAML:2.0:protocol}StatusResponseType
    
    # Attribute Version inherited from {urn:oasis:names:tc:SAML:2.0:protocol}StatusResponseType
    
    # Attribute Destination inherited from {urn:oasis:names:tc:SAML:2.0:protocol}StatusResponseType
    
    # Attribute IssueInstant inherited from {urn:oasis:names:tc:SAML:2.0:protocol}StatusResponseType
    
    # Attribute ID inherited from {urn:oasis:names:tc:SAML:2.0:protocol}StatusResponseType
    
    # Attribute Consent inherited from {urn:oasis:names:tc:SAML:2.0:protocol}StatusResponseType
    
    # Attribute InResponseTo inherited from {urn:oasis:names:tc:SAML:2.0:protocol}StatusResponseType

    _ElementMap = StatusResponseType._ElementMap.copy()
    _ElementMap.update({
        __EncryptedAssertion.name() : __EncryptedAssertion,
        __Assertion.name() : __Assertion
    })
    _AttributeMap = StatusResponseType._AttributeMap.copy()
    _AttributeMap.update({
        
    })
Namespace.addCategoryObject('typeBinding', u'ResponseType', ResponseType)


# Complex type {urn:oasis:names:tc:SAML:2.0:protocol}ManageNameIDRequestType with content type ELEMENT_ONLY
class ManageNameIDRequestType (RequestAbstractType):
    _TypeDefinition = None
    _ContentTypeTag = pyxb.binding.basis.complexTypeDefinition._CT_ELEMENT_ONLY
    _Abstract = False
    _ExpandedName = pyxb.namespace.ExpandedName(Namespace, u'ManageNameIDRequestType')
    _DefinitionLocation = pyxb.utils.utility.Location('/tmp/pyxbdist.RHB65sy/PyXB-1.1.5/pyxb/bundles/saml20/schemas/protocol.xsd', 235, 4)
    # Base type is RequestAbstractType
    
    # Element Extensions ({urn:oasis:names:tc:SAML:2.0:protocol}Extensions) inherited from {urn:oasis:names:tc:SAML:2.0:protocol}RequestAbstractType
    
    # Element {urn:oasis:names:tc:SAML:2.0:protocol}NewEncryptedID uses Python identifier NewEncryptedID
    __NewEncryptedID = pyxb.binding.content.ElementUse(pyxb.namespace.ExpandedName(Namespace, u'NewEncryptedID'), 'NewEncryptedID', '__urnoasisnamestcSAML2_0protocol_ManageNameIDRequestType_urnoasisnamestcSAML2_0protocolNewEncryptedID', False)
    __NewEncryptedID._DeclarationLocation = pyxb.utils.utility.Location('/tmp/pyxbdist.RHB65sy/PyXB-1.1.5/pyxb/bundles/saml20/schemas/protocol.xsd', 253, 4)
    __NewEncryptedID._UseLocation = None

    
    NewEncryptedID = property(__NewEncryptedID.value, __NewEncryptedID.set, None, None)

    
    # Element Issuer ({urn:oasis:names:tc:SAML:2.0:assertion}Issuer) inherited from {urn:oasis:names:tc:SAML:2.0:protocol}RequestAbstractType
    
    # Element {urn:oasis:names:tc:SAML:2.0:assertion}EncryptedID uses Python identifier EncryptedID
    __EncryptedID = pyxb.binding.content.ElementUse(pyxb.namespace.ExpandedName(pyxb.namespace.NamespaceForURI(u'urn:oasis:names:tc:SAML:2.0:assertion'), u'EncryptedID'), 'EncryptedID', '__urnoasisnamestcSAML2_0protocol_ManageNameIDRequestType_urnoasisnamestcSAML2_0assertionEncryptedID', False)
    __EncryptedID._DeclarationLocation = pyxb.utils.utility.Location('/tmp/pyxbdist.RHB65sy/PyXB-1.1.5/pyxb/bundles/saml20/schemas/assertion.xsd', 53, 4)
    __EncryptedID._UseLocation = None

    
    EncryptedID = property(__EncryptedID.value, __EncryptedID.set, None, None)

    
    # Element {urn:oasis:names:tc:SAML:2.0:assertion}NameID uses Python identifier NameID
    __NameID = pyxb.binding.content.ElementUse(pyxb.namespace.ExpandedName(pyxb.namespace.NamespaceForURI(u'urn:oasis:names:tc:SAML:2.0:assertion'), u'NameID'), 'NameID', '__urnoasisnamestcSAML2_0protocol_ManageNameIDRequestType_urnoasisnamestcSAML2_0assertionNameID', False)
    __NameID._DeclarationLocation = pyxb.utils.utility.Location('/tmp/pyxbdist.RHB65sy/PyXB-1.1.5/pyxb/bundles/saml20/schemas/assertion.xsd', 37, 4)
    __NameID._UseLocation = None

    
    NameID = property(__NameID.value, __NameID.set, None, None)

    
    # Element Signature ({http://www.w3.org/2000/09/xmldsig#}Signature) inherited from {urn:oasis:names:tc:SAML:2.0:protocol}RequestAbstractType
    
    # Element {urn:oasis:names:tc:SAML:2.0:protocol}Terminate uses Python identifier Terminate
    __Terminate = pyxb.binding.content.ElementUse(pyxb.namespace.ExpandedName(Namespace, u'Terminate'), 'Terminate', '__urnoasisnamestcSAML2_0protocol_ManageNameIDRequestType_urnoasisnamestcSAML2_0protocolTerminate', False)
    __Terminate._DeclarationLocation = pyxb.utils.utility.Location('/tmp/pyxbdist.RHB65sy/PyXB-1.1.5/pyxb/bundles/saml20/schemas/protocol.xsd', 254, 4)
    __Terminate._UseLocation = None

    
    Terminate = property(__Terminate.value, __Terminate.set, None, None)

    
    # Element {urn:oasis:names:tc:SAML:2.0:protocol}NewID uses Python identifier NewID
    __NewID = pyxb.binding.content.ElementUse(pyxb.namespace.ExpandedName(Namespace, u'NewID'), 'NewID', '__urnoasisnamestcSAML2_0protocol_ManageNameIDRequestType_urnoasisnamestcSAML2_0protocolNewID', False)
    __NewID._DeclarationLocation = pyxb.utils.utility.Location('/tmp/pyxbdist.RHB65sy/PyXB-1.1.5/pyxb/bundles/saml20/schemas/protocol.xsd', 252, 4)
    __NewID._UseLocation = None

    
    NewID = property(__NewID.value, __NewID.set, None, None)

    
    # Attribute Destination inherited from {urn:oasis:names:tc:SAML:2.0:protocol}RequestAbstractType
    
    # Attribute Consent inherited from {urn:oasis:names:tc:SAML:2.0:protocol}RequestAbstractType
    
    # Attribute ID inherited from {urn:oasis:names:tc:SAML:2.0:protocol}RequestAbstractType
    
    # Attribute IssueInstant inherited from {urn:oasis:names:tc:SAML:2.0:protocol}RequestAbstractType
    
    # Attribute Version inherited from {urn:oasis:names:tc:SAML:2.0:protocol}RequestAbstractType

    _ElementMap = RequestAbstractType._ElementMap.copy()
    _ElementMap.update({
        __NewEncryptedID.name() : __NewEncryptedID,
        __EncryptedID.name() : __EncryptedID,
        __NameID.name() : __NameID,
        __Terminate.name() : __Terminate,
        __NewID.name() : __NewID
    })
    _AttributeMap = RequestAbstractType._AttributeMap.copy()
    _AttributeMap.update({
        
    })
Namespace.addCategoryObject('typeBinding', u'ManageNameIDRequestType', ManageNameIDRequestType)


# Complex type {urn:oasis:names:tc:SAML:2.0:protocol}StatusDetailType with content type ELEMENT_ONLY
class StatusDetailType (pyxb.binding.basis.complexTypeDefinition):
    _TypeDefinition = None
    _ContentTypeTag = pyxb.binding.basis.complexTypeDefinition._CT_ELEMENT_ONLY
    _Abstract = False
    _ExpandedName = pyxb.namespace.ExpandedName(Namespace, u'StatusDetailType')
    _DefinitionLocation = pyxb.utils.utility.Location('/tmp/pyxbdist.RHB65sy/PyXB-1.1.5/pyxb/bundles/saml20/schemas/protocol.xsd', 78, 4)
    # Base type is pyxb.binding.datatypes.anyType
    _HasWildcardElement = True

    _ElementMap = {
        
    }
    _AttributeMap = {
        
    }
Namespace.addCategoryObject('typeBinding', u'StatusDetailType', StatusDetailType)


# Complex type {urn:oasis:names:tc:SAML:2.0:protocol}AuthzDecisionQueryType with content type ELEMENT_ONLY
class AuthzDecisionQueryType (SubjectQueryAbstractType):
    _TypeDefinition = None
    _ContentTypeTag = pyxb.binding.basis.complexTypeDefinition._CT_ELEMENT_ONLY
    _Abstract = False
    _ExpandedName = pyxb.namespace.ExpandedName(Namespace, u'AuthzDecisionQueryType')
    _DefinitionLocation = pyxb.utils.utility.Location('/tmp/pyxbdist.RHB65sy/PyXB-1.1.5/pyxb/bundles/saml20/schemas/protocol.xsd', 141, 4)
    # Base type is SubjectQueryAbstractType
    
    # Element Extensions ({urn:oasis:names:tc:SAML:2.0:protocol}Extensions) inherited from {urn:oasis:names:tc:SAML:2.0:protocol}RequestAbstractType
    
    # Element {urn:oasis:names:tc:SAML:2.0:assertion}Action uses Python identifier Action
    __Action = pyxb.binding.content.ElementUse(pyxb.namespace.ExpandedName(pyxb.namespace.NamespaceForURI(u'urn:oasis:names:tc:SAML:2.0:assertion'), u'Action'), 'Action', '__urnoasisnamestcSAML2_0protocol_AuthzDecisionQueryType_urnoasisnamestcSAML2_0assertionAction', True)
    __Action._DeclarationLocation = pyxb.utils.utility.Location('/tmp/pyxbdist.RHB65sy/PyXB-1.1.5/pyxb/bundles/saml20/schemas/assertion.xsd', 243, 4)
    __Action._UseLocation = None

    
    Action = property(__Action.value, __Action.set, None, None)

    
    # Element Issuer ({urn:oasis:names:tc:SAML:2.0:assertion}Issuer) inherited from {urn:oasis:names:tc:SAML:2.0:protocol}RequestAbstractType
    
    # Element Subject ({urn:oasis:names:tc:SAML:2.0:assertion}Subject) inherited from {urn:oasis:names:tc:SAML:2.0:protocol}SubjectQueryAbstractType
    
    # Element {urn:oasis:names:tc:SAML:2.0:assertion}Evidence uses Python identifier Evidence
    __Evidence = pyxb.binding.content.ElementUse(pyxb.namespace.ExpandedName(pyxb.namespace.NamespaceForURI(u'urn:oasis:names:tc:SAML:2.0:assertion'), u'Evidence'), 'Evidence', '__urnoasisnamestcSAML2_0protocol_AuthzDecisionQueryType_urnoasisnamestcSAML2_0assertionEvidence', False)
    __Evidence._DeclarationLocation = pyxb.utils.utility.Location('/tmp/pyxbdist.RHB65sy/PyXB-1.1.5/pyxb/bundles/saml20/schemas/assertion.xsd', 251, 4)
    __Evidence._UseLocation = None

    
    Evidence = property(__Evidence.value, __Evidence.set, None, None)

    
    # Element Signature ({http://www.w3.org/2000/09/xmldsig#}Signature) inherited from {urn:oasis:names:tc:SAML:2.0:protocol}RequestAbstractType
    
    # Attribute Version inherited from {urn:oasis:names:tc:SAML:2.0:protocol}RequestAbstractType
    
    # Attribute IssueInstant inherited from {urn:oasis:names:tc:SAML:2.0:protocol}RequestAbstractType
    
    # Attribute Destination inherited from {urn:oasis:names:tc:SAML:2.0:protocol}RequestAbstractType
    
    # Attribute Resource uses Python identifier Resource
    __Resource = pyxb.binding.content.AttributeUse(pyxb.namespace.ExpandedName(None, u'Resource'), 'Resource', '__urnoasisnamestcSAML2_0protocol_AuthzDecisionQueryType_Resource', pyxb.binding.datatypes.anyURI, required=True)
    __Resource._DeclarationLocation = pyxb.utils.utility.Location('/tmp/pyxbdist.RHB65sy/PyXB-1.1.5/pyxb/bundles/saml20/schemas/protocol.xsd', 148, 16)
    __Resource._UseLocation = pyxb.utils.utility.Location('/tmp/pyxbdist.RHB65sy/PyXB-1.1.5/pyxb/bundles/saml20/schemas/protocol.xsd', 148, 16)
    
    Resource = property(__Resource.value, __Resource.set, None, None)

    
    # Attribute ID inherited from {urn:oasis:names:tc:SAML:2.0:protocol}RequestAbstractType
    
    # Attribute Consent inherited from {urn:oasis:names:tc:SAML:2.0:protocol}RequestAbstractType

    _ElementMap = SubjectQueryAbstractType._ElementMap.copy()
    _ElementMap.update({
        __Action.name() : __Action,
        __Evidence.name() : __Evidence
    })
    _AttributeMap = SubjectQueryAbstractType._AttributeMap.copy()
    _AttributeMap.update({
        __Resource.name() : __Resource
    })
Namespace.addCategoryObject('typeBinding', u'AuthzDecisionQueryType', AuthzDecisionQueryType)


# Complex type {urn:oasis:names:tc:SAML:2.0:protocol}LogoutRequestType with content type ELEMENT_ONLY
class LogoutRequestType (RequestAbstractType):
    _TypeDefinition = None
    _ContentTypeTag = pyxb.binding.basis.complexTypeDefinition._CT_ELEMENT_ONLY
    _Abstract = False
    _ExpandedName = pyxb.namespace.ExpandedName(Namespace, u'LogoutRequestType')
    _DefinitionLocation = pyxb.utils.utility.Location('/tmp/pyxbdist.RHB65sy/PyXB-1.1.5/pyxb/bundles/saml20/schemas/protocol.xsd', 258, 4)
    # Base type is RequestAbstractType
    
    # Element {urn:oasis:names:tc:SAML:2.0:assertion}EncryptedID uses Python identifier EncryptedID
    __EncryptedID = pyxb.binding.content.ElementUse(pyxb.namespace.ExpandedName(pyxb.namespace.NamespaceForURI(u'urn:oasis:names:tc:SAML:2.0:assertion'), u'EncryptedID'), 'EncryptedID', '__urnoasisnamestcSAML2_0protocol_LogoutRequestType_urnoasisnamestcSAML2_0assertionEncryptedID', False)
    __EncryptedID._DeclarationLocation = pyxb.utils.utility.Location('/tmp/pyxbdist.RHB65sy/PyXB-1.1.5/pyxb/bundles/saml20/schemas/assertion.xsd', 53, 4)
    __EncryptedID._UseLocation = None

    
    EncryptedID = property(__EncryptedID.value, __EncryptedID.set, None, None)

    
    # Element Extensions ({urn:oasis:names:tc:SAML:2.0:protocol}Extensions) inherited from {urn:oasis:names:tc:SAML:2.0:protocol}RequestAbstractType
    
    # Element {urn:oasis:names:tc:SAML:2.0:protocol}SessionIndex uses Python identifier SessionIndex
    __SessionIndex = pyxb.binding.content.ElementUse(pyxb.namespace.ExpandedName(Namespace, u'SessionIndex'), 'SessionIndex', '__urnoasisnamestcSAML2_0protocol_LogoutRequestType_urnoasisnamestcSAML2_0protocolSessionIndex', True)
    __SessionIndex._DeclarationLocation = pyxb.utils.utility.Location('/tmp/pyxbdist.RHB65sy/PyXB-1.1.5/pyxb/bundles/saml20/schemas/protocol.xsd', 274, 4)
    __SessionIndex._UseLocation = None

    
    SessionIndex = property(__SessionIndex.value, __SessionIndex.set, None, None)

    
    # Element Issuer ({urn:oasis:names:tc:SAML:2.0:assertion}Issuer) inherited from {urn:oasis:names:tc:SAML:2.0:protocol}RequestAbstractType
    
    # Element {urn:oasis:names:tc:SAML:2.0:assertion}NameID uses Python identifier NameID
    __NameID = pyxb.binding.content.ElementUse(pyxb.namespace.ExpandedName(pyxb.namespace.NamespaceForURI(u'urn:oasis:names:tc:SAML:2.0:assertion'), u'NameID'), 'NameID', '__urnoasisnamestcSAML2_0protocol_LogoutRequestType_urnoasisnamestcSAML2_0assertionNameID', False)
    __NameID._DeclarationLocation = pyxb.utils.utility.Location('/tmp/pyxbdist.RHB65sy/PyXB-1.1.5/pyxb/bundles/saml20/schemas/assertion.xsd', 37, 4)
    __NameID._UseLocation = None

    
    NameID = property(__NameID.value, __NameID.set, None, None)

    
    # Element {urn:oasis:names:tc:SAML:2.0:assertion}BaseID uses Python identifier BaseID
    __BaseID = pyxb.binding.content.ElementUse(pyxb.namespace.ExpandedName(pyxb.namespace.NamespaceForURI(u'urn:oasis:names:tc:SAML:2.0:assertion'), u'BaseID'), 'BaseID', '__urnoasisnamestcSAML2_0protocol_LogoutRequestType_urnoasisnamestcSAML2_0assertionBaseID', False)
    __BaseID._DeclarationLocation = pyxb.utils.utility.Location('/tmp/pyxbdist.RHB65sy/PyXB-1.1.5/pyxb/bundles/saml20/schemas/assertion.xsd', 33, 4)
    __BaseID._UseLocation = None

    
    BaseID = property(__BaseID.value, __BaseID.set, None, None)

    
    # Element Signature ({http://www.w3.org/2000/09/xmldsig#}Signature) inherited from {urn:oasis:names:tc:SAML:2.0:protocol}RequestAbstractType
    
    # Attribute Version inherited from {urn:oasis:names:tc:SAML:2.0:protocol}RequestAbstractType
    
    # Attribute NotOnOrAfter uses Python identifier NotOnOrAfter
    __NotOnOrAfter = pyxb.binding.content.AttributeUse(pyxb.namespace.ExpandedName(None, u'NotOnOrAfter'), 'NotOnOrAfter', '__urnoasisnamestcSAML2_0protocol_LogoutRequestType_NotOnOrAfter', pyxb.binding.datatypes.dateTime)
    __NotOnOrAfter._DeclarationLocation = pyxb.utils.utility.Location('/tmp/pyxbdist.RHB65sy/PyXB-1.1.5/pyxb/bundles/saml20/schemas/protocol.xsd', 270, 16)
    __NotOnOrAfter._UseLocation = pyxb.utils.utility.Location('/tmp/pyxbdist.RHB65sy/PyXB-1.1.5/pyxb/bundles/saml20/schemas/protocol.xsd', 270, 16)
    
    NotOnOrAfter = property(__NotOnOrAfter.value, __NotOnOrAfter.set, None, None)

    
    # Attribute IssueInstant inherited from {urn:oasis:names:tc:SAML:2.0:protocol}RequestAbstractType
    
    # Attribute Destination inherited from {urn:oasis:names:tc:SAML:2.0:protocol}RequestAbstractType
    
    # Attribute ID inherited from {urn:oasis:names:tc:SAML:2.0:protocol}RequestAbstractType
    
    # Attribute Reason uses Python identifier Reason
    __Reason = pyxb.binding.content.AttributeUse(pyxb.namespace.ExpandedName(None, u'Reason'), 'Reason', '__urnoasisnamestcSAML2_0protocol_LogoutRequestType_Reason', pyxb.binding.datatypes.string)
    __Reason._DeclarationLocation = pyxb.utils.utility.Location('/tmp/pyxbdist.RHB65sy/PyXB-1.1.5/pyxb/bundles/saml20/schemas/protocol.xsd', 269, 16)
    __Reason._UseLocation = pyxb.utils.utility.Location('/tmp/pyxbdist.RHB65sy/PyXB-1.1.5/pyxb/bundles/saml20/schemas/protocol.xsd', 269, 16)
    
    Reason = property(__Reason.value, __Reason.set, None, None)

    
    # Attribute Consent inherited from {urn:oasis:names:tc:SAML:2.0:protocol}RequestAbstractType

    _ElementMap = RequestAbstractType._ElementMap.copy()
    _ElementMap.update({
        __EncryptedID.name() : __EncryptedID,
        __SessionIndex.name() : __SessionIndex,
        __NameID.name() : __NameID,
        __BaseID.name() : __BaseID
    })
    _AttributeMap = RequestAbstractType._AttributeMap.copy()
    _AttributeMap.update({
        __NotOnOrAfter.name() : __NotOnOrAfter,
        __Reason.name() : __Reason
    })
Namespace.addCategoryObject('typeBinding', u'LogoutRequestType', LogoutRequestType)


# Complex type {urn:oasis:names:tc:SAML:2.0:protocol}AssertionIDRequestType with content type ELEMENT_ONLY
class AssertionIDRequestType (RequestAbstractType):
    _TypeDefinition = None
    _ContentTypeTag = pyxb.binding.basis.complexTypeDefinition._CT_ELEMENT_ONLY
    _Abstract = False
    _ExpandedName = pyxb.namespace.ExpandedName(Namespace, u'AssertionIDRequestType')
    _DefinitionLocation = pyxb.utils.utility.Location('/tmp/pyxbdist.RHB65sy/PyXB-1.1.5/pyxb/bundles/saml20/schemas/protocol.xsd', 84, 4)
    # Base type is RequestAbstractType
    
    # Element Signature ({http://www.w3.org/2000/09/xmldsig#}Signature) inherited from {urn:oasis:names:tc:SAML:2.0:protocol}RequestAbstractType
    
    # Element {urn:oasis:names:tc:SAML:2.0:assertion}AssertionIDRef uses Python identifier AssertionIDRef
    __AssertionIDRef = pyxb.binding.content.ElementUse(pyxb.namespace.ExpandedName(pyxb.namespace.NamespaceForURI(u'urn:oasis:names:tc:SAML:2.0:assertion'), u'AssertionIDRef'), 'AssertionIDRef', '__urnoasisnamestcSAML2_0protocol_AssertionIDRequestType_urnoasisnamestcSAML2_0assertionAssertionIDRef', True)
    __AssertionIDRef._DeclarationLocation = pyxb.utils.utility.Location('/tmp/pyxbdist.RHB65sy/PyXB-1.1.5/pyxb/bundles/saml20/schemas/assertion.xsd', 55, 4)
    __AssertionIDRef._UseLocation = None

    
    AssertionIDRef = property(__AssertionIDRef.value, __AssertionIDRef.set, None, None)

    
    # Element Extensions ({urn:oasis:names:tc:SAML:2.0:protocol}Extensions) inherited from {urn:oasis:names:tc:SAML:2.0:protocol}RequestAbstractType
    
    # Element Issuer ({urn:oasis:names:tc:SAML:2.0:assertion}Issuer) inherited from {urn:oasis:names:tc:SAML:2.0:protocol}RequestAbstractType
    
    # Attribute Destination inherited from {urn:oasis:names:tc:SAML:2.0:protocol}RequestAbstractType
    
    # Attribute Consent inherited from {urn:oasis:names:tc:SAML:2.0:protocol}RequestAbstractType
    
    # Attribute ID inherited from {urn:oasis:names:tc:SAML:2.0:protocol}RequestAbstractType
    
    # Attribute IssueInstant inherited from {urn:oasis:names:tc:SAML:2.0:protocol}RequestAbstractType
    
    # Attribute Version inherited from {urn:oasis:names:tc:SAML:2.0:protocol}RequestAbstractType

    _ElementMap = RequestAbstractType._ElementMap.copy()
    _ElementMap.update({
        __AssertionIDRef.name() : __AssertionIDRef
    })
    _AttributeMap = RequestAbstractType._AttributeMap.copy()
    _AttributeMap.update({
        
    })
Namespace.addCategoryObject('typeBinding', u'AssertionIDRequestType', AssertionIDRequestType)


# Complex type {urn:oasis:names:tc:SAML:2.0:protocol}NameIDMappingResponseType with content type ELEMENT_ONLY
class NameIDMappingResponseType (StatusResponseType):
    _TypeDefinition = None
    _ContentTypeTag = pyxb.binding.basis.complexTypeDefinition._CT_ELEMENT_ONLY
    _Abstract = False
    _ExpandedName = pyxb.namespace.ExpandedName(Namespace, u'NameIDMappingResponseType')
    _DefinitionLocation = pyxb.utils.utility.Location('/tmp/pyxbdist.RHB65sy/PyXB-1.1.5/pyxb/bundles/saml20/schemas/protocol.xsd', 292, 4)
    # Base type is StatusResponseType
    
    # Element Extensions ({urn:oasis:names:tc:SAML:2.0:protocol}Extensions) inherited from {urn:oasis:names:tc:SAML:2.0:protocol}StatusResponseType
    
    # Element Issuer ({urn:oasis:names:tc:SAML:2.0:assertion}Issuer) inherited from {urn:oasis:names:tc:SAML:2.0:protocol}StatusResponseType
    
    # Element Signature ({http://www.w3.org/2000/09/xmldsig#}Signature) inherited from {urn:oasis:names:tc:SAML:2.0:protocol}StatusResponseType
    
    # Element {urn:oasis:names:tc:SAML:2.0:assertion}NameID uses Python identifier NameID
    __NameID = pyxb.binding.content.ElementUse(pyxb.namespace.ExpandedName(pyxb.namespace.NamespaceForURI(u'urn:oasis:names:tc:SAML:2.0:assertion'), u'NameID'), 'NameID', '__urnoasisnamestcSAML2_0protocol_NameIDMappingResponseType_urnoasisnamestcSAML2_0assertionNameID', False)
    __NameID._DeclarationLocation = pyxb.utils.utility.Location('/tmp/pyxbdist.RHB65sy/PyXB-1.1.5/pyxb/bundles/saml20/schemas/assertion.xsd', 37, 4)
    __NameID._UseLocation = None

    
    NameID = property(__NameID.value, __NameID.set, None, None)

    
    # Element Status ({urn:oasis:names:tc:SAML:2.0:protocol}Status) inherited from {urn:oasis:names:tc:SAML:2.0:protocol}StatusResponseType
    
    # Element {urn:oasis:names:tc:SAML:2.0:assertion}EncryptedID uses Python identifier EncryptedID
    __EncryptedID = pyxb.binding.content.ElementUse(pyxb.namespace.ExpandedName(pyxb.namespace.NamespaceForURI(u'urn:oasis:names:tc:SAML:2.0:assertion'), u'EncryptedID'), 'EncryptedID', '__urnoasisnamestcSAML2_0protocol_NameIDMappingResponseType_urnoasisnamestcSAML2_0assertionEncryptedID', False)
    __EncryptedID._DeclarationLocation = pyxb.utils.utility.Location('/tmp/pyxbdist.RHB65sy/PyXB-1.1.5/pyxb/bundles/saml20/schemas/assertion.xsd', 53, 4)
    __EncryptedID._UseLocation = None

    
    EncryptedID = property(__EncryptedID.value, __EncryptedID.set, None, None)

    
    # Attribute Version inherited from {urn:oasis:names:tc:SAML:2.0:protocol}StatusResponseType
    
    # Attribute Destination inherited from {urn:oasis:names:tc:SAML:2.0:protocol}StatusResponseType
    
    # Attribute IssueInstant inherited from {urn:oasis:names:tc:SAML:2.0:protocol}StatusResponseType
    
    # Attribute ID inherited from {urn:oasis:names:tc:SAML:2.0:protocol}StatusResponseType
    
    # Attribute Consent inherited from {urn:oasis:names:tc:SAML:2.0:protocol}StatusResponseType
    
    # Attribute InResponseTo inherited from {urn:oasis:names:tc:SAML:2.0:protocol}StatusResponseType

    _ElementMap = StatusResponseType._ElementMap.copy()
    _ElementMap.update({
        __NameID.name() : __NameID,
        __EncryptedID.name() : __EncryptedID
    })
    _AttributeMap = StatusResponseType._AttributeMap.copy()
    _AttributeMap.update({
        
    })
Namespace.addCategoryObject('typeBinding', u'NameIDMappingResponseType', NameIDMappingResponseType)


# Complex type {urn:oasis:names:tc:SAML:2.0:protocol}AttributeQueryType with content type ELEMENT_ONLY
class AttributeQueryType (SubjectQueryAbstractType):
    _TypeDefinition = None
    _ContentTypeTag = pyxb.binding.basis.complexTypeDefinition._CT_ELEMENT_ONLY
    _Abstract = False
    _ExpandedName = pyxb.namespace.ExpandedName(Namespace, u'AttributeQueryType')
    _DefinitionLocation = pyxb.utils.utility.Location('/tmp/pyxbdist.RHB65sy/PyXB-1.1.5/pyxb/bundles/saml20/schemas/protocol.xsd', 131, 4)
    # Base type is SubjectQueryAbstractType
    
    # Element {urn:oasis:names:tc:SAML:2.0:assertion}Attribute uses Python identifier Attribute
    __Attribute = pyxb.binding.content.ElementUse(pyxb.namespace.ExpandedName(pyxb.namespace.NamespaceForURI(u'urn:oasis:names:tc:SAML:2.0:assertion'), u'Attribute'), 'Attribute', '__urnoasisnamestcSAML2_0protocol_AttributeQueryType_urnoasisnamestcSAML2_0assertionAttribute', True)
    __Attribute._DeclarationLocation = pyxb.utils.utility.Location('/tmp/pyxbdist.RHB65sy/PyXB-1.1.5/pyxb/bundles/saml20/schemas/assertion.xsd', 271, 4)
    __Attribute._UseLocation = None

    
    Attribute = property(__Attribute.value, __Attribute.set, None, None)

    
    # Element Issuer ({urn:oasis:names:tc:SAML:2.0:assertion}Issuer) inherited from {urn:oasis:names:tc:SAML:2.0:protocol}RequestAbstractType
    
    # Element Subject ({urn:oasis:names:tc:SAML:2.0:assertion}Subject) inherited from {urn:oasis:names:tc:SAML:2.0:protocol}SubjectQueryAbstractType
    
    # Element Extensions ({urn:oasis:names:tc:SAML:2.0:protocol}Extensions) inherited from {urn:oasis:names:tc:SAML:2.0:protocol}RequestAbstractType
    
    # Element Signature ({http://www.w3.org/2000/09/xmldsig#}Signature) inherited from {urn:oasis:names:tc:SAML:2.0:protocol}RequestAbstractType
    
    # Attribute Version inherited from {urn:oasis:names:tc:SAML:2.0:protocol}RequestAbstractType
    
    # Attribute Destination inherited from {urn:oasis:names:tc:SAML:2.0:protocol}RequestAbstractType
    
    # Attribute ID inherited from {urn:oasis:names:tc:SAML:2.0:protocol}RequestAbstractType
    
    # Attribute IssueInstant inherited from {urn:oasis:names:tc:SAML:2.0:protocol}RequestAbstractType
    
    # Attribute Consent inherited from {urn:oasis:names:tc:SAML:2.0:protocol}RequestAbstractType

    _ElementMap = SubjectQueryAbstractType._ElementMap.copy()
    _ElementMap.update({
        __Attribute.name() : __Attribute
    })
    _AttributeMap = SubjectQueryAbstractType._AttributeMap.copy()
    _AttributeMap.update({
        
    })
Namespace.addCategoryObject('typeBinding', u'AttributeQueryType', AttributeQueryType)


SubjectQuery = pyxb.binding.basis.element(pyxb.namespace.ExpandedName(Namespace, u'SubjectQuery'), SubjectQueryAbstractType)
Namespace.addCategoryObject('elementBinding', SubjectQuery.name().localName(), SubjectQuery)

GetComplete = pyxb.binding.basis.element(pyxb.namespace.ExpandedName(Namespace, u'GetComplete'), pyxb.binding.datatypes.anyURI)
Namespace.addCategoryObject('elementBinding', GetComplete.name().localName(), GetComplete)

Terminate = pyxb.binding.basis.element(pyxb.namespace.ExpandedName(Namespace, u'Terminate'), TerminateType)
Namespace.addCategoryObject('elementBinding', Terminate.name().localName(), Terminate)

ArtifactResolve = pyxb.binding.basis.element(pyxb.namespace.ExpandedName(Namespace, u'ArtifactResolve'), ArtifactResolveType)
Namespace.addCategoryObject('elementBinding', ArtifactResolve.name().localName(), ArtifactResolve)

AuthnRequest = pyxb.binding.basis.element(pyxb.namespace.ExpandedName(Namespace, u'AuthnRequest'), AuthnRequestType)
Namespace.addCategoryObject('elementBinding', AuthnRequest.name().localName(), AuthnRequest)

Artifact = pyxb.binding.basis.element(pyxb.namespace.ExpandedName(Namespace, u'Artifact'), pyxb.binding.datatypes.string)
Namespace.addCategoryObject('elementBinding', Artifact.name().localName(), Artifact)

Status = pyxb.binding.basis.element(pyxb.namespace.ExpandedName(Namespace, u'Status'), StatusType)
Namespace.addCategoryObject('elementBinding', Status.name().localName(), Status)

ArtifactResponse = pyxb.binding.basis.element(pyxb.namespace.ExpandedName(Namespace, u'ArtifactResponse'), ArtifactResponseType)
Namespace.addCategoryObject('elementBinding', ArtifactResponse.name().localName(), ArtifactResponse)

IDPEntry = pyxb.binding.basis.element(pyxb.namespace.ExpandedName(Namespace, u'IDPEntry'), IDPEntryType)
Namespace.addCategoryObject('elementBinding', IDPEntry.name().localName(), IDPEntry)

RequesterID = pyxb.binding.basis.element(pyxb.namespace.ExpandedName(Namespace, u'RequesterID'), pyxb.binding.datatypes.anyURI)
Namespace.addCategoryObject('elementBinding', RequesterID.name().localName(), RequesterID)

StatusMessage = pyxb.binding.basis.element(pyxb.namespace.ExpandedName(Namespace, u'StatusMessage'), pyxb.binding.datatypes.string)
Namespace.addCategoryObject('elementBinding', StatusMessage.name().localName(), StatusMessage)

NameIDMappingRequest = pyxb.binding.basis.element(pyxb.namespace.ExpandedName(Namespace, u'NameIDMappingRequest'), NameIDMappingRequestType)
Namespace.addCategoryObject('elementBinding', NameIDMappingRequest.name().localName(), NameIDMappingRequest)

NewEncryptedID = pyxb.binding.basis.element(pyxb.namespace.ExpandedName(Namespace, u'NewEncryptedID'), pyxb.bundles.saml20.assertion.EncryptedElementType)
Namespace.addCategoryObject('elementBinding', NewEncryptedID.name().localName(), NewEncryptedID)

IDPList = pyxb.binding.basis.element(pyxb.namespace.ExpandedName(Namespace, u'IDPList'), IDPListType)
Namespace.addCategoryObject('elementBinding', IDPList.name().localName(), IDPList)

RequestedAuthnContext = pyxb.binding.basis.element(pyxb.namespace.ExpandedName(Namespace, u'RequestedAuthnContext'), RequestedAuthnContextType)
Namespace.addCategoryObject('elementBinding', RequestedAuthnContext.name().localName(), RequestedAuthnContext)

Extensions = pyxb.binding.basis.element(pyxb.namespace.ExpandedName(Namespace, u'Extensions'), ExtensionsType)
Namespace.addCategoryObject('elementBinding', Extensions.name().localName(), Extensions)

StatusCode = pyxb.binding.basis.element(pyxb.namespace.ExpandedName(Namespace, u'StatusCode'), StatusCodeType)
Namespace.addCategoryObject('elementBinding', StatusCode.name().localName(), StatusCode)

LogoutResponse = pyxb.binding.basis.element(pyxb.namespace.ExpandedName(Namespace, u'LogoutResponse'), StatusResponseType)
Namespace.addCategoryObject('elementBinding', LogoutResponse.name().localName(), LogoutResponse)

ManageNameIDResponse = pyxb.binding.basis.element(pyxb.namespace.ExpandedName(Namespace, u'ManageNameIDResponse'), StatusResponseType)
Namespace.addCategoryObject('elementBinding', ManageNameIDResponse.name().localName(), ManageNameIDResponse)

AuthnQuery = pyxb.binding.basis.element(pyxb.namespace.ExpandedName(Namespace, u'AuthnQuery'), AuthnQueryType)
Namespace.addCategoryObject('elementBinding', AuthnQuery.name().localName(), AuthnQuery)

NameIDPolicy = pyxb.binding.basis.element(pyxb.namespace.ExpandedName(Namespace, u'NameIDPolicy'), NameIDPolicyType)
Namespace.addCategoryObject('elementBinding', NameIDPolicy.name().localName(), NameIDPolicy)

Response = pyxb.binding.basis.element(pyxb.namespace.ExpandedName(Namespace, u'Response'), ResponseType)
Namespace.addCategoryObject('elementBinding', Response.name().localName(), Response)

ManageNameIDRequest = pyxb.binding.basis.element(pyxb.namespace.ExpandedName(Namespace, u'ManageNameIDRequest'), ManageNameIDRequestType)
Namespace.addCategoryObject('elementBinding', ManageNameIDRequest.name().localName(), ManageNameIDRequest)

StatusDetail = pyxb.binding.basis.element(pyxb.namespace.ExpandedName(Namespace, u'StatusDetail'), StatusDetailType)
Namespace.addCategoryObject('elementBinding', StatusDetail.name().localName(), StatusDetail)

SessionIndex = pyxb.binding.basis.element(pyxb.namespace.ExpandedName(Namespace, u'SessionIndex'), pyxb.binding.datatypes.string)
Namespace.addCategoryObject('elementBinding', SessionIndex.name().localName(), SessionIndex)

AuthzDecisionQuery = pyxb.binding.basis.element(pyxb.namespace.ExpandedName(Namespace, u'AuthzDecisionQuery'), AuthzDecisionQueryType)
Namespace.addCategoryObject('elementBinding', AuthzDecisionQuery.name().localName(), AuthzDecisionQuery)

LogoutRequest = pyxb.binding.basis.element(pyxb.namespace.ExpandedName(Namespace, u'LogoutRequest'), LogoutRequestType)
Namespace.addCategoryObject('elementBinding', LogoutRequest.name().localName(), LogoutRequest)

Scoping = pyxb.binding.basis.element(pyxb.namespace.ExpandedName(Namespace, u'Scoping'), ScopingType)
Namespace.addCategoryObject('elementBinding', Scoping.name().localName(), Scoping)

AssertionIDRequest = pyxb.binding.basis.element(pyxb.namespace.ExpandedName(Namespace, u'AssertionIDRequest'), AssertionIDRequestType)
Namespace.addCategoryObject('elementBinding', AssertionIDRequest.name().localName(), AssertionIDRequest)

NewID = pyxb.binding.basis.element(pyxb.namespace.ExpandedName(Namespace, u'NewID'), pyxb.binding.datatypes.string)
Namespace.addCategoryObject('elementBinding', NewID.name().localName(), NewID)

NameIDMappingResponse = pyxb.binding.basis.element(pyxb.namespace.ExpandedName(Namespace, u'NameIDMappingResponse'), NameIDMappingResponseType)
Namespace.addCategoryObject('elementBinding', NameIDMappingResponse.name().localName(), NameIDMappingResponse)

AttributeQuery = pyxb.binding.basis.element(pyxb.namespace.ExpandedName(Namespace, u'AttributeQuery'), AttributeQueryType)
Namespace.addCategoryObject('elementBinding', AttributeQuery.name().localName(), AttributeQuery)



RequestAbstractType._AddElement(pyxb.binding.basis.element(pyxb.namespace.ExpandedName(pyxb.namespace.NamespaceForURI(u'http://www.w3.org/2000/09/xmldsig#'), u'Signature'), pyxb.bundles.wssplat.ds.SignatureType, scope=RequestAbstractType))

RequestAbstractType._AddElement(pyxb.binding.basis.element(pyxb.namespace.ExpandedName(Namespace, u'Extensions'), ExtensionsType, scope=RequestAbstractType))

RequestAbstractType._AddElement(pyxb.binding.basis.element(pyxb.namespace.ExpandedName(pyxb.namespace.NamespaceForURI(u'urn:oasis:names:tc:SAML:2.0:assertion'), u'Issuer'), pyxb.bundles.saml20.assertion.NameIDType, scope=RequestAbstractType))
RequestAbstractType._GroupModel = pyxb.binding.content.GroupSequence(
    pyxb.binding.content.ParticleModel(RequestAbstractType._UseForTag(pyxb.namespace.ExpandedName(pyxb.namespace.NamespaceForURI(u'urn:oasis:names:tc:SAML:2.0:assertion'), u'Issuer')), min_occurs=0L, max_occurs=1),
    pyxb.binding.content.ParticleModel(RequestAbstractType._UseForTag(pyxb.namespace.ExpandedName(pyxb.namespace.NamespaceForURI(u'http://www.w3.org/2000/09/xmldsig#'), u'Signature')), min_occurs=0L, max_occurs=1),
    pyxb.binding.content.ParticleModel(RequestAbstractType._UseForTag(pyxb.namespace.ExpandedName(Namespace, u'Extensions')), min_occurs=0L, max_occurs=1)
    )
RequestAbstractType._ContentModel = pyxb.binding.content.ParticleModel(RequestAbstractType._GroupModel, min_occurs=1, max_occurs=1)



SubjectQueryAbstractType._AddElement(pyxb.binding.basis.element(pyxb.namespace.ExpandedName(pyxb.namespace.NamespaceForURI(u'urn:oasis:names:tc:SAML:2.0:assertion'), u'Subject'), pyxb.bundles.saml20.assertion.SubjectType, scope=SubjectQueryAbstractType))
SubjectQueryAbstractType._GroupModel_ = pyxb.binding.content.GroupSequence(
    pyxb.binding.content.ParticleModel(SubjectQueryAbstractType._UseForTag(pyxb.namespace.ExpandedName(pyxb.namespace.NamespaceForURI(u'urn:oasis:names:tc:SAML:2.0:assertion'), u'Issuer')), min_occurs=0L, max_occurs=1),
    pyxb.binding.content.ParticleModel(SubjectQueryAbstractType._UseForTag(pyxb.namespace.ExpandedName(pyxb.namespace.NamespaceForURI(u'http://www.w3.org/2000/09/xmldsig#'), u'Signature')), min_occurs=0L, max_occurs=1),
    pyxb.binding.content.ParticleModel(SubjectQueryAbstractType._UseForTag(pyxb.namespace.ExpandedName(Namespace, u'Extensions')), min_occurs=0L, max_occurs=1)
    )
SubjectQueryAbstractType._GroupModel_2 = pyxb.binding.content.GroupSequence(
    pyxb.binding.content.ParticleModel(SubjectQueryAbstractType._UseForTag(pyxb.namespace.ExpandedName(pyxb.namespace.NamespaceForURI(u'urn:oasis:names:tc:SAML:2.0:assertion'), u'Subject')), min_occurs=1, max_occurs=1)
    )
SubjectQueryAbstractType._GroupModel = pyxb.binding.content.GroupSequence(
    pyxb.binding.content.ParticleModel(SubjectQueryAbstractType._GroupModel_, min_occurs=1, max_occurs=1),
    pyxb.binding.content.ParticleModel(SubjectQueryAbstractType._GroupModel_2, min_occurs=1, max_occurs=1)
    )
SubjectQueryAbstractType._ContentModel = pyxb.binding.content.ParticleModel(SubjectQueryAbstractType._GroupModel, min_occurs=1, max_occurs=1)



ArtifactResolveType._AddElement(pyxb.binding.basis.element(pyxb.namespace.ExpandedName(Namespace, u'Artifact'), pyxb.binding.datatypes.string, scope=ArtifactResolveType))
ArtifactResolveType._GroupModel_ = pyxb.binding.content.GroupSequence(
    pyxb.binding.content.ParticleModel(ArtifactResolveType._UseForTag(pyxb.namespace.ExpandedName(pyxb.namespace.NamespaceForURI(u'urn:oasis:names:tc:SAML:2.0:assertion'), u'Issuer')), min_occurs=0L, max_occurs=1),
    pyxb.binding.content.ParticleModel(ArtifactResolveType._UseForTag(pyxb.namespace.ExpandedName(pyxb.namespace.NamespaceForURI(u'http://www.w3.org/2000/09/xmldsig#'), u'Signature')), min_occurs=0L, max_occurs=1),
    pyxb.binding.content.ParticleModel(ArtifactResolveType._UseForTag(pyxb.namespace.ExpandedName(Namespace, u'Extensions')), min_occurs=0L, max_occurs=1)
    )
ArtifactResolveType._GroupModel_2 = pyxb.binding.content.GroupSequence(
    pyxb.binding.content.ParticleModel(ArtifactResolveType._UseForTag(pyxb.namespace.ExpandedName(Namespace, u'Artifact')), min_occurs=1, max_occurs=1)
    )
ArtifactResolveType._GroupModel = pyxb.binding.content.GroupSequence(
    pyxb.binding.content.ParticleModel(ArtifactResolveType._GroupModel_, min_occurs=1, max_occurs=1),
    pyxb.binding.content.ParticleModel(ArtifactResolveType._GroupModel_2, min_occurs=1, max_occurs=1)
    )
ArtifactResolveType._ContentModel = pyxb.binding.content.ParticleModel(ArtifactResolveType._GroupModel, min_occurs=1, max_occurs=1)



AuthnRequestType._AddElement(pyxb.binding.basis.element(pyxb.namespace.ExpandedName(Namespace, u'RequestedAuthnContext'), RequestedAuthnContextType, scope=AuthnRequestType))

AuthnRequestType._AddElement(pyxb.binding.basis.element(pyxb.namespace.ExpandedName(Namespace, u'NameIDPolicy'), NameIDPolicyType, scope=AuthnRequestType))

AuthnRequestType._AddElement(pyxb.binding.basis.element(pyxb.namespace.ExpandedName(Namespace, u'Scoping'), ScopingType, scope=AuthnRequestType))

AuthnRequestType._AddElement(pyxb.binding.basis.element(pyxb.namespace.ExpandedName(pyxb.namespace.NamespaceForURI(u'urn:oasis:names:tc:SAML:2.0:assertion'), u'Conditions'), pyxb.bundles.saml20.assertion.ConditionsType, scope=AuthnRequestType))

AuthnRequestType._AddElement(pyxb.binding.basis.element(pyxb.namespace.ExpandedName(pyxb.namespace.NamespaceForURI(u'urn:oasis:names:tc:SAML:2.0:assertion'), u'Subject'), pyxb.bundles.saml20.assertion.SubjectType, scope=AuthnRequestType))
AuthnRequestType._GroupModel_ = pyxb.binding.content.GroupSequence(
    pyxb.binding.content.ParticleModel(AuthnRequestType._UseForTag(pyxb.namespace.ExpandedName(pyxb.namespace.NamespaceForURI(u'urn:oasis:names:tc:SAML:2.0:assertion'), u'Issuer')), min_occurs=0L, max_occurs=1),
    pyxb.binding.content.ParticleModel(AuthnRequestType._UseForTag(pyxb.namespace.ExpandedName(pyxb.namespace.NamespaceForURI(u'http://www.w3.org/2000/09/xmldsig#'), u'Signature')), min_occurs=0L, max_occurs=1),
    pyxb.binding.content.ParticleModel(AuthnRequestType._UseForTag(pyxb.namespace.ExpandedName(Namespace, u'Extensions')), min_occurs=0L, max_occurs=1)
    )
AuthnRequestType._GroupModel_2 = pyxb.binding.content.GroupSequence(
    pyxb.binding.content.ParticleModel(AuthnRequestType._UseForTag(pyxb.namespace.ExpandedName(pyxb.namespace.NamespaceForURI(u'urn:oasis:names:tc:SAML:2.0:assertion'), u'Subject')), min_occurs=0L, max_occurs=1),
    pyxb.binding.content.ParticleModel(AuthnRequestType._UseForTag(pyxb.namespace.ExpandedName(Namespace, u'NameIDPolicy')), min_occurs=0L, max_occurs=1),
    pyxb.binding.content.ParticleModel(AuthnRequestType._UseForTag(pyxb.namespace.ExpandedName(pyxb.namespace.NamespaceForURI(u'urn:oasis:names:tc:SAML:2.0:assertion'), u'Conditions')), min_occurs=0L, max_occurs=1),
    pyxb.binding.content.ParticleModel(AuthnRequestType._UseForTag(pyxb.namespace.ExpandedName(Namespace, u'RequestedAuthnContext')), min_occurs=0L, max_occurs=1),
    pyxb.binding.content.ParticleModel(AuthnRequestType._UseForTag(pyxb.namespace.ExpandedName(Namespace, u'Scoping')), min_occurs=0L, max_occurs=1)
    )
AuthnRequestType._GroupModel = pyxb.binding.content.GroupSequence(
    pyxb.binding.content.ParticleModel(AuthnRequestType._GroupModel_, min_occurs=1, max_occurs=1),
    pyxb.binding.content.ParticleModel(AuthnRequestType._GroupModel_2, min_occurs=1, max_occurs=1)
    )
AuthnRequestType._ContentModel = pyxb.binding.content.ParticleModel(AuthnRequestType._GroupModel, min_occurs=1, max_occurs=1)



ScopingType._AddElement(pyxb.binding.basis.element(pyxb.namespace.ExpandedName(Namespace, u'IDPList'), IDPListType, scope=ScopingType))

ScopingType._AddElement(pyxb.binding.basis.element(pyxb.namespace.ExpandedName(Namespace, u'RequesterID'), pyxb.binding.datatypes.anyURI, scope=ScopingType))
ScopingType._GroupModel = pyxb.binding.content.GroupSequence(
    pyxb.binding.content.ParticleModel(ScopingType._UseForTag(pyxb.namespace.ExpandedName(Namespace, u'IDPList')), min_occurs=0L, max_occurs=1),
    pyxb.binding.content.ParticleModel(ScopingType._UseForTag(pyxb.namespace.ExpandedName(Namespace, u'RequesterID')), min_occurs=0L, max_occurs=None)
    )
ScopingType._ContentModel = pyxb.binding.content.ParticleModel(ScopingType._GroupModel, min_occurs=1, max_occurs=1)



RequestedAuthnContextType._AddElement(pyxb.binding.basis.element(pyxb.namespace.ExpandedName(pyxb.namespace.NamespaceForURI(u'urn:oasis:names:tc:SAML:2.0:assertion'), u'AuthnContextClassRef'), pyxb.binding.datatypes.anyURI, scope=RequestedAuthnContextType))

RequestedAuthnContextType._AddElement(pyxb.binding.basis.element(pyxb.namespace.ExpandedName(pyxb.namespace.NamespaceForURI(u'urn:oasis:names:tc:SAML:2.0:assertion'), u'AuthnContextDeclRef'), pyxb.binding.datatypes.anyURI, scope=RequestedAuthnContextType))
RequestedAuthnContextType._GroupModel = pyxb.binding.content.GroupChoice(
    pyxb.binding.content.ParticleModel(RequestedAuthnContextType._UseForTag(pyxb.namespace.ExpandedName(pyxb.namespace.NamespaceForURI(u'urn:oasis:names:tc:SAML:2.0:assertion'), u'AuthnContextClassRef')), min_occurs=1, max_occurs=None),
    pyxb.binding.content.ParticleModel(RequestedAuthnContextType._UseForTag(pyxb.namespace.ExpandedName(pyxb.namespace.NamespaceForURI(u'urn:oasis:names:tc:SAML:2.0:assertion'), u'AuthnContextDeclRef')), min_occurs=1, max_occurs=None)
    )
RequestedAuthnContextType._ContentModel = pyxb.binding.content.ParticleModel(RequestedAuthnContextType._GroupModel, min_occurs=1, max_occurs=1)



StatusType._AddElement(pyxb.binding.basis.element(pyxb.namespace.ExpandedName(Namespace, u'StatusDetail'), StatusDetailType, scope=StatusType))

StatusType._AddElement(pyxb.binding.basis.element(pyxb.namespace.ExpandedName(Namespace, u'StatusCode'), StatusCodeType, scope=StatusType))

StatusType._AddElement(pyxb.binding.basis.element(pyxb.namespace.ExpandedName(Namespace, u'StatusMessage'), pyxb.binding.datatypes.string, scope=StatusType))
StatusType._GroupModel = pyxb.binding.content.GroupSequence(
    pyxb.binding.content.ParticleModel(StatusType._UseForTag(pyxb.namespace.ExpandedName(Namespace, u'StatusCode')), min_occurs=1, max_occurs=1),
    pyxb.binding.content.ParticleModel(StatusType._UseForTag(pyxb.namespace.ExpandedName(Namespace, u'StatusMessage')), min_occurs=0L, max_occurs=1),
    pyxb.binding.content.ParticleModel(StatusType._UseForTag(pyxb.namespace.ExpandedName(Namespace, u'StatusDetail')), min_occurs=0L, max_occurs=1)
    )
StatusType._ContentModel = pyxb.binding.content.ParticleModel(StatusType._GroupModel, min_occurs=1, max_occurs=1)



StatusResponseType._AddElement(pyxb.binding.basis.element(pyxb.namespace.ExpandedName(Namespace, u'Extensions'), ExtensionsType, scope=StatusResponseType))

StatusResponseType._AddElement(pyxb.binding.basis.element(pyxb.namespace.ExpandedName(Namespace, u'Status'), StatusType, scope=StatusResponseType))

StatusResponseType._AddElement(pyxb.binding.basis.element(pyxb.namespace.ExpandedName(pyxb.namespace.NamespaceForURI(u'urn:oasis:names:tc:SAML:2.0:assertion'), u'Issuer'), pyxb.bundles.saml20.assertion.NameIDType, scope=StatusResponseType))

StatusResponseType._AddElement(pyxb.binding.basis.element(pyxb.namespace.ExpandedName(pyxb.namespace.NamespaceForURI(u'http://www.w3.org/2000/09/xmldsig#'), u'Signature'), pyxb.bundles.wssplat.ds.SignatureType, scope=StatusResponseType))
StatusResponseType._GroupModel = pyxb.binding.content.GroupSequence(
    pyxb.binding.content.ParticleModel(StatusResponseType._UseForTag(pyxb.namespace.ExpandedName(pyxb.namespace.NamespaceForURI(u'urn:oasis:names:tc:SAML:2.0:assertion'), u'Issuer')), min_occurs=0L, max_occurs=1),
    pyxb.binding.content.ParticleModel(StatusResponseType._UseForTag(pyxb.namespace.ExpandedName(pyxb.namespace.NamespaceForURI(u'http://www.w3.org/2000/09/xmldsig#'), u'Signature')), min_occurs=0L, max_occurs=1),
    pyxb.binding.content.ParticleModel(StatusResponseType._UseForTag(pyxb.namespace.ExpandedName(Namespace, u'Extensions')), min_occurs=0L, max_occurs=1),
    pyxb.binding.content.ParticleModel(StatusResponseType._UseForTag(pyxb.namespace.ExpandedName(Namespace, u'Status')), min_occurs=1, max_occurs=1)
    )
StatusResponseType._ContentModel = pyxb.binding.content.ParticleModel(StatusResponseType._GroupModel, min_occurs=1, max_occurs=1)


ArtifactResponseType._GroupModel_ = pyxb.binding.content.GroupSequence(
    pyxb.binding.content.ParticleModel(ArtifactResponseType._UseForTag(pyxb.namespace.ExpandedName(pyxb.namespace.NamespaceForURI(u'urn:oasis:names:tc:SAML:2.0:assertion'), u'Issuer')), min_occurs=0L, max_occurs=1),
    pyxb.binding.content.ParticleModel(ArtifactResponseType._UseForTag(pyxb.namespace.ExpandedName(pyxb.namespace.NamespaceForURI(u'http://www.w3.org/2000/09/xmldsig#'), u'Signature')), min_occurs=0L, max_occurs=1),
    pyxb.binding.content.ParticleModel(ArtifactResponseType._UseForTag(pyxb.namespace.ExpandedName(Namespace, u'Extensions')), min_occurs=0L, max_occurs=1),
    pyxb.binding.content.ParticleModel(ArtifactResponseType._UseForTag(pyxb.namespace.ExpandedName(Namespace, u'Status')), min_occurs=1, max_occurs=1)
    )
ArtifactResponseType._GroupModel_2 = pyxb.binding.content.GroupSequence(
    pyxb.binding.content.ParticleModel(pyxb.binding.content.Wildcard(process_contents=pyxb.binding.content.Wildcard.PC_lax, namespace_constraint=pyxb.binding.content.Wildcard.NC_any), min_occurs=0L, max_occurs=1)
    )
ArtifactResponseType._GroupModel = pyxb.binding.content.GroupSequence(
    pyxb.binding.content.ParticleModel(ArtifactResponseType._GroupModel_, min_occurs=1, max_occurs=1),
    pyxb.binding.content.ParticleModel(ArtifactResponseType._GroupModel_2, min_occurs=1, max_occurs=1)
    )
ArtifactResponseType._ContentModel = pyxb.binding.content.ParticleModel(ArtifactResponseType._GroupModel, min_occurs=1, max_occurs=1)



StatusCodeType._AddElement(pyxb.binding.basis.element(pyxb.namespace.ExpandedName(Namespace, u'StatusCode'), StatusCodeType, scope=StatusCodeType))
StatusCodeType._GroupModel = pyxb.binding.content.GroupSequence(
    pyxb.binding.content.ParticleModel(StatusCodeType._UseForTag(pyxb.namespace.ExpandedName(Namespace, u'StatusCode')), min_occurs=0L, max_occurs=1)
    )
StatusCodeType._ContentModel = pyxb.binding.content.ParticleModel(StatusCodeType._GroupModel, min_occurs=1, max_occurs=1)



NameIDMappingRequestType._AddElement(pyxb.binding.basis.element(pyxb.namespace.ExpandedName(pyxb.namespace.NamespaceForURI(u'urn:oasis:names:tc:SAML:2.0:assertion'), u'BaseID'), pyxb.bundles.saml20.assertion.BaseIDAbstractType, scope=NameIDMappingRequestType))

NameIDMappingRequestType._AddElement(pyxb.binding.basis.element(pyxb.namespace.ExpandedName(pyxb.namespace.NamespaceForURI(u'urn:oasis:names:tc:SAML:2.0:assertion'), u'NameID'), pyxb.bundles.saml20.assertion.NameIDType, scope=NameIDMappingRequestType))

NameIDMappingRequestType._AddElement(pyxb.binding.basis.element(pyxb.namespace.ExpandedName(pyxb.namespace.NamespaceForURI(u'urn:oasis:names:tc:SAML:2.0:assertion'), u'EncryptedID'), pyxb.bundles.saml20.assertion.EncryptedElementType, scope=NameIDMappingRequestType))

NameIDMappingRequestType._AddElement(pyxb.binding.basis.element(pyxb.namespace.ExpandedName(Namespace, u'NameIDPolicy'), NameIDPolicyType, scope=NameIDMappingRequestType))
NameIDMappingRequestType._GroupModel_ = pyxb.binding.content.GroupSequence(
    pyxb.binding.content.ParticleModel(NameIDMappingRequestType._UseForTag(pyxb.namespace.ExpandedName(pyxb.namespace.NamespaceForURI(u'urn:oasis:names:tc:SAML:2.0:assertion'), u'Issuer')), min_occurs=0L, max_occurs=1),
    pyxb.binding.content.ParticleModel(NameIDMappingRequestType._UseForTag(pyxb.namespace.ExpandedName(pyxb.namespace.NamespaceForURI(u'http://www.w3.org/2000/09/xmldsig#'), u'Signature')), min_occurs=0L, max_occurs=1),
    pyxb.binding.content.ParticleModel(NameIDMappingRequestType._UseForTag(pyxb.namespace.ExpandedName(Namespace, u'Extensions')), min_occurs=0L, max_occurs=1)
    )
NameIDMappingRequestType._GroupModel_3 = pyxb.binding.content.GroupChoice(
    pyxb.binding.content.ParticleModel(NameIDMappingRequestType._UseForTag(pyxb.namespace.ExpandedName(pyxb.namespace.NamespaceForURI(u'urn:oasis:names:tc:SAML:2.0:assertion'), u'BaseID')), min_occurs=1, max_occurs=1),
    pyxb.binding.content.ParticleModel(NameIDMappingRequestType._UseForTag(pyxb.namespace.ExpandedName(pyxb.namespace.NamespaceForURI(u'urn:oasis:names:tc:SAML:2.0:assertion'), u'NameID')), min_occurs=1, max_occurs=1),
    pyxb.binding.content.ParticleModel(NameIDMappingRequestType._UseForTag(pyxb.namespace.ExpandedName(pyxb.namespace.NamespaceForURI(u'urn:oasis:names:tc:SAML:2.0:assertion'), u'EncryptedID')), min_occurs=1, max_occurs=1)
    )
NameIDMappingRequestType._GroupModel_2 = pyxb.binding.content.GroupSequence(
    pyxb.binding.content.ParticleModel(NameIDMappingRequestType._GroupModel_3, min_occurs=1, max_occurs=1),
    pyxb.binding.content.ParticleModel(NameIDMappingRequestType._UseForTag(pyxb.namespace.ExpandedName(Namespace, u'NameIDPolicy')), min_occurs=1, max_occurs=1)
    )
NameIDMappingRequestType._GroupModel = pyxb.binding.content.GroupSequence(
    pyxb.binding.content.ParticleModel(NameIDMappingRequestType._GroupModel_, min_occurs=1, max_occurs=1),
    pyxb.binding.content.ParticleModel(NameIDMappingRequestType._GroupModel_2, min_occurs=1, max_occurs=1)
    )
NameIDMappingRequestType._ContentModel = pyxb.binding.content.ParticleModel(NameIDMappingRequestType._GroupModel, min_occurs=1, max_occurs=1)



IDPListType._AddElement(pyxb.binding.basis.element(pyxb.namespace.ExpandedName(Namespace, u'GetComplete'), pyxb.binding.datatypes.anyURI, scope=IDPListType))

IDPListType._AddElement(pyxb.binding.basis.element(pyxb.namespace.ExpandedName(Namespace, u'IDPEntry'), IDPEntryType, scope=IDPListType))
IDPListType._GroupModel = pyxb.binding.content.GroupSequence(
    pyxb.binding.content.ParticleModel(IDPListType._UseForTag(pyxb.namespace.ExpandedName(Namespace, u'IDPEntry')), min_occurs=1, max_occurs=None),
    pyxb.binding.content.ParticleModel(IDPListType._UseForTag(pyxb.namespace.ExpandedName(Namespace, u'GetComplete')), min_occurs=0L, max_occurs=1)
    )
IDPListType._ContentModel = pyxb.binding.content.ParticleModel(IDPListType._GroupModel, min_occurs=1, max_occurs=1)


ExtensionsType._GroupModel = pyxb.binding.content.GroupSequence(
    pyxb.binding.content.ParticleModel(pyxb.binding.content.Wildcard(process_contents=pyxb.binding.content.Wildcard.PC_lax, namespace_constraint=(pyxb.binding.content.Wildcard.NC_not, u'urn:oasis:names:tc:SAML:2.0:protocol')), min_occurs=1, max_occurs=None)
    )
ExtensionsType._ContentModel = pyxb.binding.content.ParticleModel(ExtensionsType._GroupModel, min_occurs=1, max_occurs=1)



AuthnQueryType._AddElement(pyxb.binding.basis.element(pyxb.namespace.ExpandedName(Namespace, u'RequestedAuthnContext'), RequestedAuthnContextType, scope=AuthnQueryType))
AuthnQueryType._GroupModel_2 = pyxb.binding.content.GroupSequence(
    pyxb.binding.content.ParticleModel(AuthnQueryType._UseForTag(pyxb.namespace.ExpandedName(pyxb.namespace.NamespaceForURI(u'urn:oasis:names:tc:SAML:2.0:assertion'), u'Issuer')), min_occurs=0L, max_occurs=1),
    pyxb.binding.content.ParticleModel(AuthnQueryType._UseForTag(pyxb.namespace.ExpandedName(pyxb.namespace.NamespaceForURI(u'http://www.w3.org/2000/09/xmldsig#'), u'Signature')), min_occurs=0L, max_occurs=1),
    pyxb.binding.content.ParticleModel(AuthnQueryType._UseForTag(pyxb.namespace.ExpandedName(Namespace, u'Extensions')), min_occurs=0L, max_occurs=1)
    )
AuthnQueryType._GroupModel_3 = pyxb.binding.content.GroupSequence(
    pyxb.binding.content.ParticleModel(AuthnQueryType._UseForTag(pyxb.namespace.ExpandedName(pyxb.namespace.NamespaceForURI(u'urn:oasis:names:tc:SAML:2.0:assertion'), u'Subject')), min_occurs=1, max_occurs=1)
    )
AuthnQueryType._GroupModel_ = pyxb.binding.content.GroupSequence(
    pyxb.binding.content.ParticleModel(AuthnQueryType._GroupModel_2, min_occurs=1, max_occurs=1),
    pyxb.binding.content.ParticleModel(AuthnQueryType._GroupModel_3, min_occurs=1, max_occurs=1)
    )
AuthnQueryType._GroupModel_4 = pyxb.binding.content.GroupSequence(
    pyxb.binding.content.ParticleModel(AuthnQueryType._UseForTag(pyxb.namespace.ExpandedName(Namespace, u'RequestedAuthnContext')), min_occurs=0L, max_occurs=1)
    )
AuthnQueryType._GroupModel = pyxb.binding.content.GroupSequence(
    pyxb.binding.content.ParticleModel(AuthnQueryType._GroupModel_, min_occurs=1, max_occurs=1),
    pyxb.binding.content.ParticleModel(AuthnQueryType._GroupModel_4, min_occurs=1, max_occurs=1)
    )
AuthnQueryType._ContentModel = pyxb.binding.content.ParticleModel(AuthnQueryType._GroupModel, min_occurs=1, max_occurs=1)



ResponseType._AddElement(pyxb.binding.basis.element(pyxb.namespace.ExpandedName(pyxb.namespace.NamespaceForURI(u'urn:oasis:names:tc:SAML:2.0:assertion'), u'EncryptedAssertion'), pyxb.bundles.saml20.assertion.EncryptedElementType, scope=ResponseType))

ResponseType._AddElement(pyxb.binding.basis.element(pyxb.namespace.ExpandedName(pyxb.namespace.NamespaceForURI(u'urn:oasis:names:tc:SAML:2.0:assertion'), u'Assertion'), pyxb.bundles.saml20.assertion.AssertionType, scope=ResponseType))
ResponseType._GroupModel_ = pyxb.binding.content.GroupSequence(
    pyxb.binding.content.ParticleModel(ResponseType._UseForTag(pyxb.namespace.ExpandedName(pyxb.namespace.NamespaceForURI(u'urn:oasis:names:tc:SAML:2.0:assertion'), u'Issuer')), min_occurs=0L, max_occurs=1),
    pyxb.binding.content.ParticleModel(ResponseType._UseForTag(pyxb.namespace.ExpandedName(pyxb.namespace.NamespaceForURI(u'http://www.w3.org/2000/09/xmldsig#'), u'Signature')), min_occurs=0L, max_occurs=1),
    pyxb.binding.content.ParticleModel(ResponseType._UseForTag(pyxb.namespace.ExpandedName(Namespace, u'Extensions')), min_occurs=0L, max_occurs=1),
    pyxb.binding.content.ParticleModel(ResponseType._UseForTag(pyxb.namespace.ExpandedName(Namespace, u'Status')), min_occurs=1, max_occurs=1)
    )
ResponseType._GroupModel_2 = pyxb.binding.content.GroupChoice(
    pyxb.binding.content.ParticleModel(ResponseType._UseForTag(pyxb.namespace.ExpandedName(pyxb.namespace.NamespaceForURI(u'urn:oasis:names:tc:SAML:2.0:assertion'), u'Assertion')), min_occurs=1, max_occurs=1),
    pyxb.binding.content.ParticleModel(ResponseType._UseForTag(pyxb.namespace.ExpandedName(pyxb.namespace.NamespaceForURI(u'urn:oasis:names:tc:SAML:2.0:assertion'), u'EncryptedAssertion')), min_occurs=1, max_occurs=1)
    )
ResponseType._GroupModel = pyxb.binding.content.GroupSequence(
    pyxb.binding.content.ParticleModel(ResponseType._GroupModel_, min_occurs=1, max_occurs=1),
    pyxb.binding.content.ParticleModel(ResponseType._GroupModel_2, min_occurs=0L, max_occurs=None)
    )
ResponseType._ContentModel = pyxb.binding.content.ParticleModel(ResponseType._GroupModel, min_occurs=1, max_occurs=1)



ManageNameIDRequestType._AddElement(pyxb.binding.basis.element(pyxb.namespace.ExpandedName(Namespace, u'NewEncryptedID'), pyxb.bundles.saml20.assertion.EncryptedElementType, scope=ManageNameIDRequestType))

ManageNameIDRequestType._AddElement(pyxb.binding.basis.element(pyxb.namespace.ExpandedName(pyxb.namespace.NamespaceForURI(u'urn:oasis:names:tc:SAML:2.0:assertion'), u'EncryptedID'), pyxb.bundles.saml20.assertion.EncryptedElementType, scope=ManageNameIDRequestType))

ManageNameIDRequestType._AddElement(pyxb.binding.basis.element(pyxb.namespace.ExpandedName(pyxb.namespace.NamespaceForURI(u'urn:oasis:names:tc:SAML:2.0:assertion'), u'NameID'), pyxb.bundles.saml20.assertion.NameIDType, scope=ManageNameIDRequestType))

ManageNameIDRequestType._AddElement(pyxb.binding.basis.element(pyxb.namespace.ExpandedName(Namespace, u'Terminate'), TerminateType, scope=ManageNameIDRequestType))

ManageNameIDRequestType._AddElement(pyxb.binding.basis.element(pyxb.namespace.ExpandedName(Namespace, u'NewID'), pyxb.binding.datatypes.string, scope=ManageNameIDRequestType))
ManageNameIDRequestType._GroupModel_ = pyxb.binding.content.GroupSequence(
    pyxb.binding.content.ParticleModel(ManageNameIDRequestType._UseForTag(pyxb.namespace.ExpandedName(pyxb.namespace.NamespaceForURI(u'urn:oasis:names:tc:SAML:2.0:assertion'), u'Issuer')), min_occurs=0L, max_occurs=1),
    pyxb.binding.content.ParticleModel(ManageNameIDRequestType._UseForTag(pyxb.namespace.ExpandedName(pyxb.namespace.NamespaceForURI(u'http://www.w3.org/2000/09/xmldsig#'), u'Signature')), min_occurs=0L, max_occurs=1),
    pyxb.binding.content.ParticleModel(ManageNameIDRequestType._UseForTag(pyxb.namespace.ExpandedName(Namespace, u'Extensions')), min_occurs=0L, max_occurs=1)
    )
ManageNameIDRequestType._GroupModel_3 = pyxb.binding.content.GroupChoice(
    pyxb.binding.content.ParticleModel(ManageNameIDRequestType._UseForTag(pyxb.namespace.ExpandedName(pyxb.namespace.NamespaceForURI(u'urn:oasis:names:tc:SAML:2.0:assertion'), u'NameID')), min_occurs=1, max_occurs=1),
    pyxb.binding.content.ParticleModel(ManageNameIDRequestType._UseForTag(pyxb.namespace.ExpandedName(pyxb.namespace.NamespaceForURI(u'urn:oasis:names:tc:SAML:2.0:assertion'), u'EncryptedID')), min_occurs=1, max_occurs=1)
    )
ManageNameIDRequestType._GroupModel_4 = pyxb.binding.content.GroupChoice(
    pyxb.binding.content.ParticleModel(ManageNameIDRequestType._UseForTag(pyxb.namespace.ExpandedName(Namespace, u'NewID')), min_occurs=1, max_occurs=1),
    pyxb.binding.content.ParticleModel(ManageNameIDRequestType._UseForTag(pyxb.namespace.ExpandedName(Namespace, u'NewEncryptedID')), min_occurs=1, max_occurs=1),
    pyxb.binding.content.ParticleModel(ManageNameIDRequestType._UseForTag(pyxb.namespace.ExpandedName(Namespace, u'Terminate')), min_occurs=1, max_occurs=1)
    )
ManageNameIDRequestType._GroupModel_2 = pyxb.binding.content.GroupSequence(
    pyxb.binding.content.ParticleModel(ManageNameIDRequestType._GroupModel_3, min_occurs=1, max_occurs=1),
    pyxb.binding.content.ParticleModel(ManageNameIDRequestType._GroupModel_4, min_occurs=1, max_occurs=1)
    )
ManageNameIDRequestType._GroupModel = pyxb.binding.content.GroupSequence(
    pyxb.binding.content.ParticleModel(ManageNameIDRequestType._GroupModel_, min_occurs=1, max_occurs=1),
    pyxb.binding.content.ParticleModel(ManageNameIDRequestType._GroupModel_2, min_occurs=1, max_occurs=1)
    )
ManageNameIDRequestType._ContentModel = pyxb.binding.content.ParticleModel(ManageNameIDRequestType._GroupModel, min_occurs=1, max_occurs=1)


StatusDetailType._GroupModel = pyxb.binding.content.GroupSequence(
    pyxb.binding.content.ParticleModel(pyxb.binding.content.Wildcard(process_contents=pyxb.binding.content.Wildcard.PC_lax, namespace_constraint=pyxb.binding.content.Wildcard.NC_any), min_occurs=0L, max_occurs=None)
    )
StatusDetailType._ContentModel = pyxb.binding.content.ParticleModel(StatusDetailType._GroupModel, min_occurs=1, max_occurs=1)



AuthzDecisionQueryType._AddElement(pyxb.binding.basis.element(pyxb.namespace.ExpandedName(pyxb.namespace.NamespaceForURI(u'urn:oasis:names:tc:SAML:2.0:assertion'), u'Action'), pyxb.bundles.saml20.assertion.ActionType, scope=AuthzDecisionQueryType))

AuthzDecisionQueryType._AddElement(pyxb.binding.basis.element(pyxb.namespace.ExpandedName(pyxb.namespace.NamespaceForURI(u'urn:oasis:names:tc:SAML:2.0:assertion'), u'Evidence'), pyxb.bundles.saml20.assertion.EvidenceType, scope=AuthzDecisionQueryType))
AuthzDecisionQueryType._GroupModel_2 = pyxb.binding.content.GroupSequence(
    pyxb.binding.content.ParticleModel(AuthzDecisionQueryType._UseForTag(pyxb.namespace.ExpandedName(pyxb.namespace.NamespaceForURI(u'urn:oasis:names:tc:SAML:2.0:assertion'), u'Issuer')), min_occurs=0L, max_occurs=1),
    pyxb.binding.content.ParticleModel(AuthzDecisionQueryType._UseForTag(pyxb.namespace.ExpandedName(pyxb.namespace.NamespaceForURI(u'http://www.w3.org/2000/09/xmldsig#'), u'Signature')), min_occurs=0L, max_occurs=1),
    pyxb.binding.content.ParticleModel(AuthzDecisionQueryType._UseForTag(pyxb.namespace.ExpandedName(Namespace, u'Extensions')), min_occurs=0L, max_occurs=1)
    )
AuthzDecisionQueryType._GroupModel_3 = pyxb.binding.content.GroupSequence(
    pyxb.binding.content.ParticleModel(AuthzDecisionQueryType._UseForTag(pyxb.namespace.ExpandedName(pyxb.namespace.NamespaceForURI(u'urn:oasis:names:tc:SAML:2.0:assertion'), u'Subject')), min_occurs=1, max_occurs=1)
    )
AuthzDecisionQueryType._GroupModel_ = pyxb.binding.content.GroupSequence(
    pyxb.binding.content.ParticleModel(AuthzDecisionQueryType._GroupModel_2, min_occurs=1, max_occurs=1),
    pyxb.binding.content.ParticleModel(AuthzDecisionQueryType._GroupModel_3, min_occurs=1, max_occurs=1)
    )
AuthzDecisionQueryType._GroupModel_4 = pyxb.binding.content.GroupSequence(
    pyxb.binding.content.ParticleModel(AuthzDecisionQueryType._UseForTag(pyxb.namespace.ExpandedName(pyxb.namespace.NamespaceForURI(u'urn:oasis:names:tc:SAML:2.0:assertion'), u'Action')), min_occurs=1, max_occurs=None),
    pyxb.binding.content.ParticleModel(AuthzDecisionQueryType._UseForTag(pyxb.namespace.ExpandedName(pyxb.namespace.NamespaceForURI(u'urn:oasis:names:tc:SAML:2.0:assertion'), u'Evidence')), min_occurs=0L, max_occurs=1)
    )
AuthzDecisionQueryType._GroupModel = pyxb.binding.content.GroupSequence(
    pyxb.binding.content.ParticleModel(AuthzDecisionQueryType._GroupModel_, min_occurs=1, max_occurs=1),
    pyxb.binding.content.ParticleModel(AuthzDecisionQueryType._GroupModel_4, min_occurs=1, max_occurs=1)
    )
AuthzDecisionQueryType._ContentModel = pyxb.binding.content.ParticleModel(AuthzDecisionQueryType._GroupModel, min_occurs=1, max_occurs=1)



LogoutRequestType._AddElement(pyxb.binding.basis.element(pyxb.namespace.ExpandedName(pyxb.namespace.NamespaceForURI(u'urn:oasis:names:tc:SAML:2.0:assertion'), u'EncryptedID'), pyxb.bundles.saml20.assertion.EncryptedElementType, scope=LogoutRequestType))

LogoutRequestType._AddElement(pyxb.binding.basis.element(pyxb.namespace.ExpandedName(Namespace, u'SessionIndex'), pyxb.binding.datatypes.string, scope=LogoutRequestType))

LogoutRequestType._AddElement(pyxb.binding.basis.element(pyxb.namespace.ExpandedName(pyxb.namespace.NamespaceForURI(u'urn:oasis:names:tc:SAML:2.0:assertion'), u'NameID'), pyxb.bundles.saml20.assertion.NameIDType, scope=LogoutRequestType))

LogoutRequestType._AddElement(pyxb.binding.basis.element(pyxb.namespace.ExpandedName(pyxb.namespace.NamespaceForURI(u'urn:oasis:names:tc:SAML:2.0:assertion'), u'BaseID'), pyxb.bundles.saml20.assertion.BaseIDAbstractType, scope=LogoutRequestType))
LogoutRequestType._GroupModel_ = pyxb.binding.content.GroupSequence(
    pyxb.binding.content.ParticleModel(LogoutRequestType._UseForTag(pyxb.namespace.ExpandedName(pyxb.namespace.NamespaceForURI(u'urn:oasis:names:tc:SAML:2.0:assertion'), u'Issuer')), min_occurs=0L, max_occurs=1),
    pyxb.binding.content.ParticleModel(LogoutRequestType._UseForTag(pyxb.namespace.ExpandedName(pyxb.namespace.NamespaceForURI(u'http://www.w3.org/2000/09/xmldsig#'), u'Signature')), min_occurs=0L, max_occurs=1),
    pyxb.binding.content.ParticleModel(LogoutRequestType._UseForTag(pyxb.namespace.ExpandedName(Namespace, u'Extensions')), min_occurs=0L, max_occurs=1)
    )
LogoutRequestType._GroupModel_3 = pyxb.binding.content.GroupChoice(
    pyxb.binding.content.ParticleModel(LogoutRequestType._UseForTag(pyxb.namespace.ExpandedName(pyxb.namespace.NamespaceForURI(u'urn:oasis:names:tc:SAML:2.0:assertion'), u'BaseID')), min_occurs=1, max_occurs=1),
    pyxb.binding.content.ParticleModel(LogoutRequestType._UseForTag(pyxb.namespace.ExpandedName(pyxb.namespace.NamespaceForURI(u'urn:oasis:names:tc:SAML:2.0:assertion'), u'NameID')), min_occurs=1, max_occurs=1),
    pyxb.binding.content.ParticleModel(LogoutRequestType._UseForTag(pyxb.namespace.ExpandedName(pyxb.namespace.NamespaceForURI(u'urn:oasis:names:tc:SAML:2.0:assertion'), u'EncryptedID')), min_occurs=1, max_occurs=1)
    )
LogoutRequestType._GroupModel_2 = pyxb.binding.content.GroupSequence(
    pyxb.binding.content.ParticleModel(LogoutRequestType._GroupModel_3, min_occurs=1, max_occurs=1),
    pyxb.binding.content.ParticleModel(LogoutRequestType._UseForTag(pyxb.namespace.ExpandedName(Namespace, u'SessionIndex')), min_occurs=0L, max_occurs=None)
    )
LogoutRequestType._GroupModel = pyxb.binding.content.GroupSequence(
    pyxb.binding.content.ParticleModel(LogoutRequestType._GroupModel_, min_occurs=1, max_occurs=1),
    pyxb.binding.content.ParticleModel(LogoutRequestType._GroupModel_2, min_occurs=1, max_occurs=1)
    )
LogoutRequestType._ContentModel = pyxb.binding.content.ParticleModel(LogoutRequestType._GroupModel, min_occurs=1, max_occurs=1)



AssertionIDRequestType._AddElement(pyxb.binding.basis.element(pyxb.namespace.ExpandedName(pyxb.namespace.NamespaceForURI(u'urn:oasis:names:tc:SAML:2.0:assertion'), u'AssertionIDRef'), pyxb.binding.datatypes.NCName, scope=AssertionIDRequestType))
AssertionIDRequestType._GroupModel_ = pyxb.binding.content.GroupSequence(
    pyxb.binding.content.ParticleModel(AssertionIDRequestType._UseForTag(pyxb.namespace.ExpandedName(pyxb.namespace.NamespaceForURI(u'urn:oasis:names:tc:SAML:2.0:assertion'), u'Issuer')), min_occurs=0L, max_occurs=1),
    pyxb.binding.content.ParticleModel(AssertionIDRequestType._UseForTag(pyxb.namespace.ExpandedName(pyxb.namespace.NamespaceForURI(u'http://www.w3.org/2000/09/xmldsig#'), u'Signature')), min_occurs=0L, max_occurs=1),
    pyxb.binding.content.ParticleModel(AssertionIDRequestType._UseForTag(pyxb.namespace.ExpandedName(Namespace, u'Extensions')), min_occurs=0L, max_occurs=1)
    )
AssertionIDRequestType._GroupModel_2 = pyxb.binding.content.GroupSequence(
    pyxb.binding.content.ParticleModel(AssertionIDRequestType._UseForTag(pyxb.namespace.ExpandedName(pyxb.namespace.NamespaceForURI(u'urn:oasis:names:tc:SAML:2.0:assertion'), u'AssertionIDRef')), min_occurs=1, max_occurs=None)
    )
AssertionIDRequestType._GroupModel = pyxb.binding.content.GroupSequence(
    pyxb.binding.content.ParticleModel(AssertionIDRequestType._GroupModel_, min_occurs=1, max_occurs=1),
    pyxb.binding.content.ParticleModel(AssertionIDRequestType._GroupModel_2, min_occurs=1, max_occurs=1)
    )
AssertionIDRequestType._ContentModel = pyxb.binding.content.ParticleModel(AssertionIDRequestType._GroupModel, min_occurs=1, max_occurs=1)



NameIDMappingResponseType._AddElement(pyxb.binding.basis.element(pyxb.namespace.ExpandedName(pyxb.namespace.NamespaceForURI(u'urn:oasis:names:tc:SAML:2.0:assertion'), u'NameID'), pyxb.bundles.saml20.assertion.NameIDType, scope=NameIDMappingResponseType))

NameIDMappingResponseType._AddElement(pyxb.binding.basis.element(pyxb.namespace.ExpandedName(pyxb.namespace.NamespaceForURI(u'urn:oasis:names:tc:SAML:2.0:assertion'), u'EncryptedID'), pyxb.bundles.saml20.assertion.EncryptedElementType, scope=NameIDMappingResponseType))
NameIDMappingResponseType._GroupModel_ = pyxb.binding.content.GroupSequence(
    pyxb.binding.content.ParticleModel(NameIDMappingResponseType._UseForTag(pyxb.namespace.ExpandedName(pyxb.namespace.NamespaceForURI(u'urn:oasis:names:tc:SAML:2.0:assertion'), u'Issuer')), min_occurs=0L, max_occurs=1),
    pyxb.binding.content.ParticleModel(NameIDMappingResponseType._UseForTag(pyxb.namespace.ExpandedName(pyxb.namespace.NamespaceForURI(u'http://www.w3.org/2000/09/xmldsig#'), u'Signature')), min_occurs=0L, max_occurs=1),
    pyxb.binding.content.ParticleModel(NameIDMappingResponseType._UseForTag(pyxb.namespace.ExpandedName(Namespace, u'Extensions')), min_occurs=0L, max_occurs=1),
    pyxb.binding.content.ParticleModel(NameIDMappingResponseType._UseForTag(pyxb.namespace.ExpandedName(Namespace, u'Status')), min_occurs=1, max_occurs=1)
    )
NameIDMappingResponseType._GroupModel_2 = pyxb.binding.content.GroupChoice(
    pyxb.binding.content.ParticleModel(NameIDMappingResponseType._UseForTag(pyxb.namespace.ExpandedName(pyxb.namespace.NamespaceForURI(u'urn:oasis:names:tc:SAML:2.0:assertion'), u'NameID')), min_occurs=1, max_occurs=1),
    pyxb.binding.content.ParticleModel(NameIDMappingResponseType._UseForTag(pyxb.namespace.ExpandedName(pyxb.namespace.NamespaceForURI(u'urn:oasis:names:tc:SAML:2.0:assertion'), u'EncryptedID')), min_occurs=1, max_occurs=1)
    )
NameIDMappingResponseType._GroupModel = pyxb.binding.content.GroupSequence(
    pyxb.binding.content.ParticleModel(NameIDMappingResponseType._GroupModel_, min_occurs=1, max_occurs=1),
    pyxb.binding.content.ParticleModel(NameIDMappingResponseType._GroupModel_2, min_occurs=1, max_occurs=1)
    )
NameIDMappingResponseType._ContentModel = pyxb.binding.content.ParticleModel(NameIDMappingResponseType._GroupModel, min_occurs=1, max_occurs=1)



AttributeQueryType._AddElement(pyxb.binding.basis.element(pyxb.namespace.ExpandedName(pyxb.namespace.NamespaceForURI(u'urn:oasis:names:tc:SAML:2.0:assertion'), u'Attribute'), pyxb.bundles.saml20.assertion.AttributeType, scope=AttributeQueryType))
AttributeQueryType._GroupModel_2 = pyxb.binding.content.GroupSequence(
    pyxb.binding.content.ParticleModel(AttributeQueryType._UseForTag(pyxb.namespace.ExpandedName(pyxb.namespace.NamespaceForURI(u'urn:oasis:names:tc:SAML:2.0:assertion'), u'Issuer')), min_occurs=0L, max_occurs=1),
    pyxb.binding.content.ParticleModel(AttributeQueryType._UseForTag(pyxb.namespace.ExpandedName(pyxb.namespace.NamespaceForURI(u'http://www.w3.org/2000/09/xmldsig#'), u'Signature')), min_occurs=0L, max_occurs=1),
    pyxb.binding.content.ParticleModel(AttributeQueryType._UseForTag(pyxb.namespace.ExpandedName(Namespace, u'Extensions')), min_occurs=0L, max_occurs=1)
    )
AttributeQueryType._GroupModel_3 = pyxb.binding.content.GroupSequence(
    pyxb.binding.content.ParticleModel(AttributeQueryType._UseForTag(pyxb.namespace.ExpandedName(pyxb.namespace.NamespaceForURI(u'urn:oasis:names:tc:SAML:2.0:assertion'), u'Subject')), min_occurs=1, max_occurs=1)
    )
AttributeQueryType._GroupModel_ = pyxb.binding.content.GroupSequence(
    pyxb.binding.content.ParticleModel(AttributeQueryType._GroupModel_2, min_occurs=1, max_occurs=1),
    pyxb.binding.content.ParticleModel(AttributeQueryType._GroupModel_3, min_occurs=1, max_occurs=1)
    )
AttributeQueryType._GroupModel_4 = pyxb.binding.content.GroupSequence(
    pyxb.binding.content.ParticleModel(AttributeQueryType._UseForTag(pyxb.namespace.ExpandedName(pyxb.namespace.NamespaceForURI(u'urn:oasis:names:tc:SAML:2.0:assertion'), u'Attribute')), min_occurs=0L, max_occurs=None)
    )
AttributeQueryType._GroupModel = pyxb.binding.content.GroupSequence(
    pyxb.binding.content.ParticleModel(AttributeQueryType._GroupModel_, min_occurs=1, max_occurs=1),
    pyxb.binding.content.ParticleModel(AttributeQueryType._GroupModel_4, min_occurs=1, max_occurs=1)
    )
AttributeQueryType._ContentModel = pyxb.binding.content.ParticleModel(AttributeQueryType._GroupModel, min_occurs=1, max_occurs=1)
