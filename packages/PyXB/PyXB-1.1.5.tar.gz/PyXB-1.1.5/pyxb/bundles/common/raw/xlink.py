# ./pyxb/bundles/common/raw/xlink.py
# -*- coding: utf-8 -*-
# PyXB bindings for NM:b43cd366527ddb6a0e58594876e07421e0148f30
# Generated 2012-11-01 15:13:32.801093 by PyXB version 1.1.5
# Namespace http://www.w3.org/1999/xlink

import pyxb
import pyxb.binding
import pyxb.binding.saxer
import StringIO
import pyxb.utils.utility
import pyxb.utils.domutils
import sys

# Unique identifier for bindings created at the same time
_GenerationUID = pyxb.utils.utility.UniqueIdentifier('urn:uuid:9c0647da-2460-11e2-9c26-c8600024e903')

# Import bindings for namespaces imported into schema
import pyxb.binding.datatypes
import pyxb.binding.xml_

Namespace = pyxb.namespace.NamespaceForURI(u'http://www.w3.org/1999/xlink', create_if_missing=True)
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


# Atomic simple type: {http://www.w3.org/1999/xlink}labelType
class labelType (pyxb.binding.datatypes.NCName):

    """An atomic simple type."""

    _ExpandedName = pyxb.namespace.ExpandedName(Namespace, u'labelType')
    _DefinitionLocation = pyxb.utils.utility.Location('/tmp/pyxbdist.RHB65sy/PyXB-1.1.5/pyxb/bundles/common/schemas/xlink.xsd', 95, 1)
    _Documentation = None
labelType._InitializeFacetMap()
Namespace.addCategoryObject('typeBinding', u'labelType', labelType)

# Atomic simple type: {http://www.w3.org/1999/xlink}titleAttrType
class titleAttrType (pyxb.binding.datatypes.string):

    """An atomic simple type."""

    _ExpandedName = pyxb.namespace.ExpandedName(Namespace, u'titleAttrType')
    _DefinitionLocation = pyxb.utils.utility.Location('/tmp/pyxbdist.RHB65sy/PyXB-1.1.5/pyxb/bundles/common/schemas/xlink.xsd', 66, 1)
    _Documentation = None
titleAttrType._InitializeFacetMap()
Namespace.addCategoryObject('typeBinding', u'titleAttrType', titleAttrType)

# Atomic simple type: {http://www.w3.org/1999/xlink}typeType
class typeType (pyxb.binding.datatypes.token, pyxb.binding.basis.enumeration_mixin):

    """An atomic simple type."""

    _ExpandedName = pyxb.namespace.ExpandedName(Namespace, u'typeType')
    _DefinitionLocation = pyxb.utils.utility.Location('/tmp/pyxbdist.RHB65sy/PyXB-1.1.5/pyxb/bundles/common/schemas/xlink.xsd', 31, 1)
    _Documentation = None
typeType._CF_enumeration = pyxb.binding.facets.CF_enumeration(value_datatype=typeType, enum_prefix=None)
typeType.simple = typeType._CF_enumeration.addEnumeration(unicode_value=u'simple', tag=u'simple')
typeType.extended = typeType._CF_enumeration.addEnumeration(unicode_value=u'extended', tag=u'extended')
typeType.title = typeType._CF_enumeration.addEnumeration(unicode_value=u'title', tag=u'title')
typeType.resource = typeType._CF_enumeration.addEnumeration(unicode_value=u'resource', tag=u'resource')
typeType.locator = typeType._CF_enumeration.addEnumeration(unicode_value=u'locator', tag=u'locator')
typeType.arc = typeType._CF_enumeration.addEnumeration(unicode_value=u'arc', tag=u'arc')
typeType._InitializeFacetMap(typeType._CF_enumeration)
Namespace.addCategoryObject('typeBinding', u'typeType', typeType)

# Atomic simple type: {http://www.w3.org/1999/xlink}roleType
class roleType (pyxb.binding.datatypes.anyURI):

    """An atomic simple type."""

    _ExpandedName = pyxb.namespace.ExpandedName(Namespace, u'roleType')
    _DefinitionLocation = pyxb.utils.utility.Location('/tmp/pyxbdist.RHB65sy/PyXB-1.1.5/pyxb/bundles/common/schemas/xlink.xsd', 50, 1)
    _Documentation = None
roleType._CF_minLength = pyxb.binding.facets.CF_minLength(value=pyxb.binding.datatypes.nonNegativeInteger(1L))
roleType._InitializeFacetMap(roleType._CF_minLength)
Namespace.addCategoryObject('typeBinding', u'roleType', roleType)

# Atomic simple type: {http://www.w3.org/1999/xlink}hrefType
class hrefType (pyxb.binding.datatypes.anyURI):

    """An atomic simple type."""

    _ExpandedName = pyxb.namespace.ExpandedName(Namespace, u'hrefType')
    _DefinitionLocation = pyxb.utils.utility.Location('/tmp/pyxbdist.RHB65sy/PyXB-1.1.5/pyxb/bundles/common/schemas/xlink.xsd', 44, 1)
    _Documentation = None
hrefType._InitializeFacetMap()
Namespace.addCategoryObject('typeBinding', u'hrefType', hrefType)

# Atomic simple type: {http://www.w3.org/1999/xlink}arcroleType
class arcroleType (pyxb.binding.datatypes.anyURI):

    """An atomic simple type."""

    _ExpandedName = pyxb.namespace.ExpandedName(Namespace, u'arcroleType')
    _DefinitionLocation = pyxb.utils.utility.Location('/tmp/pyxbdist.RHB65sy/PyXB-1.1.5/pyxb/bundles/common/schemas/xlink.xsd', 58, 1)
    _Documentation = None
arcroleType._CF_minLength = pyxb.binding.facets.CF_minLength(value=pyxb.binding.datatypes.nonNegativeInteger(1L))
arcroleType._InitializeFacetMap(arcroleType._CF_minLength)
Namespace.addCategoryObject('typeBinding', u'arcroleType', arcroleType)

# Atomic simple type: {http://www.w3.org/1999/xlink}showType
class showType (pyxb.binding.datatypes.token, pyxb.binding.basis.enumeration_mixin):

    """An atomic simple type."""

    _ExpandedName = pyxb.namespace.ExpandedName(Namespace, u'showType')
    _DefinitionLocation = pyxb.utils.utility.Location('/tmp/pyxbdist.RHB65sy/PyXB-1.1.5/pyxb/bundles/common/schemas/xlink.xsd', 72, 1)
    _Documentation = None
showType._CF_enumeration = pyxb.binding.facets.CF_enumeration(value_datatype=showType, enum_prefix=None)
showType.new = showType._CF_enumeration.addEnumeration(unicode_value=u'new', tag=u'new')
showType.replace = showType._CF_enumeration.addEnumeration(unicode_value=u'replace', tag=u'replace')
showType.embed = showType._CF_enumeration.addEnumeration(unicode_value=u'embed', tag=u'embed')
showType.other = showType._CF_enumeration.addEnumeration(unicode_value=u'other', tag=u'other')
showType.none = showType._CF_enumeration.addEnumeration(unicode_value=u'none', tag=u'none')
showType._InitializeFacetMap(showType._CF_enumeration)
Namespace.addCategoryObject('typeBinding', u'showType', showType)

# Atomic simple type: {http://www.w3.org/1999/xlink}fromType
class fromType (pyxb.binding.datatypes.NCName):

    """An atomic simple type."""

    _ExpandedName = pyxb.namespace.ExpandedName(Namespace, u'fromType')
    _DefinitionLocation = pyxb.utils.utility.Location('/tmp/pyxbdist.RHB65sy/PyXB-1.1.5/pyxb/bundles/common/schemas/xlink.xsd', 101, 1)
    _Documentation = None
fromType._InitializeFacetMap()
Namespace.addCategoryObject('typeBinding', u'fromType', fromType)

# Atomic simple type: {http://www.w3.org/1999/xlink}toType
class toType (pyxb.binding.datatypes.NCName):

    """An atomic simple type."""

    _ExpandedName = pyxb.namespace.ExpandedName(Namespace, u'toType')
    _DefinitionLocation = pyxb.utils.utility.Location('/tmp/pyxbdist.RHB65sy/PyXB-1.1.5/pyxb/bundles/common/schemas/xlink.xsd', 107, 1)
    _Documentation = None
toType._InitializeFacetMap()
Namespace.addCategoryObject('typeBinding', u'toType', toType)

# Atomic simple type: {http://www.w3.org/1999/xlink}actuateType
class actuateType (pyxb.binding.datatypes.token, pyxb.binding.basis.enumeration_mixin):

    """An atomic simple type."""

    _ExpandedName = pyxb.namespace.ExpandedName(Namespace, u'actuateType')
    _DefinitionLocation = pyxb.utils.utility.Location('/tmp/pyxbdist.RHB65sy/PyXB-1.1.5/pyxb/bundles/common/schemas/xlink.xsd', 84, 1)
    _Documentation = None
actuateType._CF_enumeration = pyxb.binding.facets.CF_enumeration(value_datatype=actuateType, enum_prefix=None)
actuateType.onLoad = actuateType._CF_enumeration.addEnumeration(unicode_value=u'onLoad', tag=u'onLoad')
actuateType.onRequest = actuateType._CF_enumeration.addEnumeration(unicode_value=u'onRequest', tag=u'onRequest')
actuateType.other = actuateType._CF_enumeration.addEnumeration(unicode_value=u'other', tag=u'other')
actuateType.none = actuateType._CF_enumeration.addEnumeration(unicode_value=u'none', tag=u'none')
actuateType._InitializeFacetMap(actuateType._CF_enumeration)
Namespace.addCategoryObject('typeBinding', u'actuateType', actuateType)

# Complex type {http://www.w3.org/1999/xlink}locatorType with content type ELEMENT_ONLY
class locatorType (pyxb.binding.basis.complexTypeDefinition):
    _TypeDefinition = None
    _ContentTypeTag = pyxb.binding.basis.complexTypeDefinition._CT_ELEMENT_ONLY
    _Abstract = False
    _ExpandedName = pyxb.namespace.ExpandedName(Namespace, u'locatorType')
    _DefinitionLocation = pyxb.utils.utility.Location('/tmp/pyxbdist.RHB65sy/PyXB-1.1.5/pyxb/bundles/common/schemas/xlink.xsd', 236, 1)
    # Base type is pyxb.binding.datatypes.anyType
    
    # Element {http://www.w3.org/1999/xlink}title uses Python identifier title
    __title = pyxb.binding.content.ElementUse(pyxb.namespace.ExpandedName(Namespace, u'title'), 'title', '__httpwww_w3_org1999xlink_locatorType_httpwww_w3_org1999xlinktitle', True)
    __title._DeclarationLocation = pyxb.utils.utility.Location('/tmp/pyxbdist.RHB65sy/PyXB-1.1.5/pyxb/bundles/common/schemas/xlink.xsd', 167, 1)
    __title._UseLocation = pyxb.utils.utility.Location('/tmp/pyxbdist.RHB65sy/PyXB-1.1.5/pyxb/bundles/common/schemas/xlink.xsd', 237, 2)

    
    title = property(__title.value, __title.set, None, None)

    
    # Attribute {http://www.w3.org/1999/xlink}title uses Python identifier title_
    __title_ = pyxb.binding.content.AttributeUse(pyxb.namespace.ExpandedName(Namespace, u'title'), 'title_', '__httpwww_w3_org1999xlink_locatorType_httpwww_w3_org1999xlinktitle_', titleAttrType)
    __title_._DeclarationLocation = pyxb.utils.utility.Location('/tmp/pyxbdist.RHB65sy/PyXB-1.1.5/pyxb/bundles/common/schemas/xlink.xsd', 64, 1)
    __title_._UseLocation = pyxb.utils.utility.Location('/tmp/pyxbdist.RHB65sy/PyXB-1.1.5/pyxb/bundles/common/schemas/xlink.xsd', 219, 2)
    
    title_ = property(__title_.value, __title_.set, None, None)

    
    # Attribute {http://www.w3.org/1999/xlink}label uses Python identifier label
    __label = pyxb.binding.content.AttributeUse(pyxb.namespace.ExpandedName(Namespace, u'label'), 'label', '__httpwww_w3_org1999xlink_locatorType_httpwww_w3_org1999xlinklabel', labelType)
    __label._DeclarationLocation = pyxb.utils.utility.Location('/tmp/pyxbdist.RHB65sy/PyXB-1.1.5/pyxb/bundles/common/schemas/xlink.xsd', 93, 1)
    __label._UseLocation = pyxb.utils.utility.Location('/tmp/pyxbdist.RHB65sy/PyXB-1.1.5/pyxb/bundles/common/schemas/xlink.xsd', 220, 2)
    
    label = property(__label.value, __label.set, None, None)

    
    # Attribute {http://www.w3.org/1999/xlink}type uses Python identifier type
    __type = pyxb.binding.content.AttributeUse(pyxb.namespace.ExpandedName(Namespace, u'type'), 'type', '__httpwww_w3_org1999xlink_locatorType_httpwww_w3_org1999xlinktype', typeType, fixed=True, unicode_default=u'locator', required=True)
    __type._DeclarationLocation = pyxb.utils.utility.Location('/tmp/pyxbdist.RHB65sy/PyXB-1.1.5/pyxb/bundles/common/schemas/xlink.xsd', 29, 1)
    __type._UseLocation = pyxb.utils.utility.Location('/tmp/pyxbdist.RHB65sy/PyXB-1.1.5/pyxb/bundles/common/schemas/xlink.xsd', 216, 2)
    
    type = property(__type.value, __type.set, None, None)

    
    # Attribute {http://www.w3.org/1999/xlink}role uses Python identifier role
    __role = pyxb.binding.content.AttributeUse(pyxb.namespace.ExpandedName(Namespace, u'role'), 'role', '__httpwww_w3_org1999xlink_locatorType_httpwww_w3_org1999xlinkrole', roleType)
    __role._DeclarationLocation = pyxb.utils.utility.Location('/tmp/pyxbdist.RHB65sy/PyXB-1.1.5/pyxb/bundles/common/schemas/xlink.xsd', 48, 1)
    __role._UseLocation = pyxb.utils.utility.Location('/tmp/pyxbdist.RHB65sy/PyXB-1.1.5/pyxb/bundles/common/schemas/xlink.xsd', 218, 2)
    
    role = property(__role.value, __role.set, None, None)

    
    # Attribute {http://www.w3.org/1999/xlink}href uses Python identifier href
    __href = pyxb.binding.content.AttributeUse(pyxb.namespace.ExpandedName(Namespace, u'href'), 'href', '__httpwww_w3_org1999xlink_locatorType_httpwww_w3_org1999xlinkhref', hrefType, required=True)
    __href._DeclarationLocation = pyxb.utils.utility.Location('/tmp/pyxbdist.RHB65sy/PyXB-1.1.5/pyxb/bundles/common/schemas/xlink.xsd', 42, 1)
    __href._UseLocation = pyxb.utils.utility.Location('/tmp/pyxbdist.RHB65sy/PyXB-1.1.5/pyxb/bundles/common/schemas/xlink.xsd', 217, 2)
    
    href = property(__href.value, __href.set, None, None)


    _ElementMap = {
        __title.name() : __title
    }
    _AttributeMap = {
        __title_.name() : __title_,
        __label.name() : __label,
        __type.name() : __type,
        __role.name() : __role,
        __href.name() : __href
    }
Namespace.addCategoryObject('typeBinding', u'locatorType', locatorType)


# Complex type {http://www.w3.org/1999/xlink}titleEltType with content type MIXED
class titleEltType (pyxb.binding.basis.complexTypeDefinition):
    _TypeDefinition = None
    _ContentTypeTag = pyxb.binding.basis.complexTypeDefinition._CT_MIXED
    _Abstract = False
    _ExpandedName = pyxb.namespace.ExpandedName(Namespace, u'titleEltType')
    _DefinitionLocation = pyxb.utils.utility.Location('/tmp/pyxbdist.RHB65sy/PyXB-1.1.5/pyxb/bundles/common/schemas/xlink.xsd', 188, 1)
    # Base type is pyxb.binding.datatypes.anyType
    
    # Attribute {http://www.w3.org/1999/xlink}type uses Python identifier type
    __type = pyxb.binding.content.AttributeUse(pyxb.namespace.ExpandedName(Namespace, u'type'), 'type', '__httpwww_w3_org1999xlink_titleEltType_httpwww_w3_org1999xlinktype', typeType, fixed=True, unicode_default=u'title', required=True)
    __type._DeclarationLocation = pyxb.utils.utility.Location('/tmp/pyxbdist.RHB65sy/PyXB-1.1.5/pyxb/bundles/common/schemas/xlink.xsd', 29, 1)
    __type._UseLocation = pyxb.utils.utility.Location('/tmp/pyxbdist.RHB65sy/PyXB-1.1.5/pyxb/bundles/common/schemas/xlink.xsd', 170, 2)
    
    type = property(__type.value, __type.set, None, None)

    
    # Attribute {http://www.w3.org/XML/1998/namespace}lang uses Python identifier lang
    __lang = pyxb.binding.content.AttributeUse(pyxb.namespace.ExpandedName(pyxb.namespace.XML, 'lang'), 'lang', '__httpwww_w3_org1999xlink_titleEltType_httpwww_w3_orgXML1998namespacelang', pyxb.binding.xml_.STD_ANON_lang)
    __lang._DeclarationLocation = None
    __lang._UseLocation = pyxb.utils.utility.Location('/tmp/pyxbdist.RHB65sy/PyXB-1.1.5/pyxb/bundles/common/schemas/xlink.xsd', 171, 2)
    
    lang = property(__lang.value, __lang.set, None, None)

    _HasWildcardElement = True

    _ElementMap = {
        
    }
    _AttributeMap = {
        __type.name() : __type,
        __lang.name() : __lang
    }
Namespace.addCategoryObject('typeBinding', u'titleEltType', titleEltType)


# Complex type {http://www.w3.org/1999/xlink}arcType with content type ELEMENT_ONLY
class arcType (pyxb.binding.basis.complexTypeDefinition):
    _TypeDefinition = None
    _ContentTypeTag = pyxb.binding.basis.complexTypeDefinition._CT_ELEMENT_ONLY
    _Abstract = False
    _ExpandedName = pyxb.namespace.ExpandedName(Namespace, u'arcType')
    _DefinitionLocation = pyxb.utils.utility.Location('/tmp/pyxbdist.RHB65sy/PyXB-1.1.5/pyxb/bundles/common/schemas/xlink.xsd', 265, 1)
    # Base type is pyxb.binding.datatypes.anyType
    
    # Element {http://www.w3.org/1999/xlink}title uses Python identifier title
    __title = pyxb.binding.content.ElementUse(pyxb.namespace.ExpandedName(Namespace, u'title'), 'title', '__httpwww_w3_org1999xlink_arcType_httpwww_w3_org1999xlinktitle', True)
    __title._DeclarationLocation = pyxb.utils.utility.Location('/tmp/pyxbdist.RHB65sy/PyXB-1.1.5/pyxb/bundles/common/schemas/xlink.xsd', 167, 1)
    __title._UseLocation = pyxb.utils.utility.Location('/tmp/pyxbdist.RHB65sy/PyXB-1.1.5/pyxb/bundles/common/schemas/xlink.xsd', 266, 2)

    
    title = property(__title.value, __title.set, None, None)

    
    # Attribute {http://www.w3.org/1999/xlink}actuate uses Python identifier actuate
    __actuate = pyxb.binding.content.AttributeUse(pyxb.namespace.ExpandedName(Namespace, u'actuate'), 'actuate', '__httpwww_w3_org1999xlink_arcType_httpwww_w3_org1999xlinkactuate', actuateType)
    __actuate._DeclarationLocation = pyxb.utils.utility.Location('/tmp/pyxbdist.RHB65sy/PyXB-1.1.5/pyxb/bundles/common/schemas/xlink.xsd', 82, 1)
    __actuate._UseLocation = pyxb.utils.utility.Location('/tmp/pyxbdist.RHB65sy/PyXB-1.1.5/pyxb/bundles/common/schemas/xlink.xsd', 248, 2)
    
    actuate = property(__actuate.value, __actuate.set, None, None)

    
    # Attribute {http://www.w3.org/1999/xlink}show uses Python identifier show
    __show = pyxb.binding.content.AttributeUse(pyxb.namespace.ExpandedName(Namespace, u'show'), 'show', '__httpwww_w3_org1999xlink_arcType_httpwww_w3_org1999xlinkshow', showType)
    __show._DeclarationLocation = pyxb.utils.utility.Location('/tmp/pyxbdist.RHB65sy/PyXB-1.1.5/pyxb/bundles/common/schemas/xlink.xsd', 70, 1)
    __show._UseLocation = pyxb.utils.utility.Location('/tmp/pyxbdist.RHB65sy/PyXB-1.1.5/pyxb/bundles/common/schemas/xlink.xsd', 247, 2)
    
    show = property(__show.value, __show.set, None, None)

    
    # Attribute {http://www.w3.org/1999/xlink}arcrole uses Python identifier arcrole
    __arcrole = pyxb.binding.content.AttributeUse(pyxb.namespace.ExpandedName(Namespace, u'arcrole'), 'arcrole', '__httpwww_w3_org1999xlink_arcType_httpwww_w3_org1999xlinkarcrole', arcroleType)
    __arcrole._DeclarationLocation = pyxb.utils.utility.Location('/tmp/pyxbdist.RHB65sy/PyXB-1.1.5/pyxb/bundles/common/schemas/xlink.xsd', 56, 1)
    __arcrole._UseLocation = pyxb.utils.utility.Location('/tmp/pyxbdist.RHB65sy/PyXB-1.1.5/pyxb/bundles/common/schemas/xlink.xsd', 245, 2)
    
    arcrole = property(__arcrole.value, __arcrole.set, None, None)

    
    # Attribute {http://www.w3.org/1999/xlink}to uses Python identifier to
    __to = pyxb.binding.content.AttributeUse(pyxb.namespace.ExpandedName(Namespace, u'to'), 'to', '__httpwww_w3_org1999xlink_arcType_httpwww_w3_org1999xlinkto', toType)
    __to._DeclarationLocation = pyxb.utils.utility.Location('/tmp/pyxbdist.RHB65sy/PyXB-1.1.5/pyxb/bundles/common/schemas/xlink.xsd', 105, 1)
    __to._UseLocation = pyxb.utils.utility.Location('/tmp/pyxbdist.RHB65sy/PyXB-1.1.5/pyxb/bundles/common/schemas/xlink.xsd', 250, 2)
    
    to = property(__to.value, __to.set, None, None)

    
    # Attribute {http://www.w3.org/1999/xlink}type uses Python identifier type
    __type = pyxb.binding.content.AttributeUse(pyxb.namespace.ExpandedName(Namespace, u'type'), 'type', '__httpwww_w3_org1999xlink_arcType_httpwww_w3_org1999xlinktype', typeType, fixed=True, unicode_default=u'arc', required=True)
    __type._DeclarationLocation = pyxb.utils.utility.Location('/tmp/pyxbdist.RHB65sy/PyXB-1.1.5/pyxb/bundles/common/schemas/xlink.xsd', 29, 1)
    __type._UseLocation = pyxb.utils.utility.Location('/tmp/pyxbdist.RHB65sy/PyXB-1.1.5/pyxb/bundles/common/schemas/xlink.xsd', 244, 2)
    
    type = property(__type.value, __type.set, None, None)

    
    # Attribute {http://www.w3.org/1999/xlink}from uses Python identifier from_
    __from = pyxb.binding.content.AttributeUse(pyxb.namespace.ExpandedName(Namespace, u'from'), 'from_', '__httpwww_w3_org1999xlink_arcType_httpwww_w3_org1999xlinkfrom', fromType)
    __from._DeclarationLocation = pyxb.utils.utility.Location('/tmp/pyxbdist.RHB65sy/PyXB-1.1.5/pyxb/bundles/common/schemas/xlink.xsd', 99, 1)
    __from._UseLocation = pyxb.utils.utility.Location('/tmp/pyxbdist.RHB65sy/PyXB-1.1.5/pyxb/bundles/common/schemas/xlink.xsd', 249, 2)
    
    from_ = property(__from.value, __from.set, None, None)

    
    # Attribute {http://www.w3.org/1999/xlink}title uses Python identifier title_
    __title_ = pyxb.binding.content.AttributeUse(pyxb.namespace.ExpandedName(Namespace, u'title'), 'title_', '__httpwww_w3_org1999xlink_arcType_httpwww_w3_org1999xlinktitle_', titleAttrType)
    __title_._DeclarationLocation = pyxb.utils.utility.Location('/tmp/pyxbdist.RHB65sy/PyXB-1.1.5/pyxb/bundles/common/schemas/xlink.xsd', 64, 1)
    __title_._UseLocation = pyxb.utils.utility.Location('/tmp/pyxbdist.RHB65sy/PyXB-1.1.5/pyxb/bundles/common/schemas/xlink.xsd', 246, 2)
    
    title_ = property(__title_.value, __title_.set, None, None)


    _ElementMap = {
        __title.name() : __title
    }
    _AttributeMap = {
        __actuate.name() : __actuate,
        __show.name() : __show,
        __arcrole.name() : __arcrole,
        __to.name() : __to,
        __type.name() : __type,
        __from.name() : __from,
        __title_.name() : __title_
    }
Namespace.addCategoryObject('typeBinding', u'arcType', arcType)


# Complex type {http://www.w3.org/1999/xlink}resourceType with content type MIXED
class resourceType (pyxb.binding.basis.complexTypeDefinition):
    _TypeDefinition = None
    _ContentTypeTag = pyxb.binding.basis.complexTypeDefinition._CT_MIXED
    _Abstract = False
    _ExpandedName = pyxb.namespace.ExpandedName(Namespace, u'resourceType')
    _DefinitionLocation = pyxb.utils.utility.Location('/tmp/pyxbdist.RHB65sy/PyXB-1.1.5/pyxb/bundles/common/schemas/xlink.xsd', 208, 1)
    # Base type is pyxb.binding.datatypes.anyType
    
    # Attribute {http://www.w3.org/1999/xlink}type uses Python identifier type
    __type = pyxb.binding.content.AttributeUse(pyxb.namespace.ExpandedName(Namespace, u'type'), 'type', '__httpwww_w3_org1999xlink_resourceType_httpwww_w3_org1999xlinktype', typeType, fixed=True, unicode_default=u'resource', required=True)
    __type._DeclarationLocation = pyxb.utils.utility.Location('/tmp/pyxbdist.RHB65sy/PyXB-1.1.5/pyxb/bundles/common/schemas/xlink.xsd', 29, 1)
    __type._UseLocation = pyxb.utils.utility.Location('/tmp/pyxbdist.RHB65sy/PyXB-1.1.5/pyxb/bundles/common/schemas/xlink.xsd', 196, 2)
    
    type = property(__type.value, __type.set, None, None)

    
    # Attribute {http://www.w3.org/1999/xlink}title uses Python identifier title
    __title = pyxb.binding.content.AttributeUse(pyxb.namespace.ExpandedName(Namespace, u'title'), 'title', '__httpwww_w3_org1999xlink_resourceType_httpwww_w3_org1999xlinktitle', titleAttrType)
    __title._DeclarationLocation = pyxb.utils.utility.Location('/tmp/pyxbdist.RHB65sy/PyXB-1.1.5/pyxb/bundles/common/schemas/xlink.xsd', 64, 1)
    __title._UseLocation = pyxb.utils.utility.Location('/tmp/pyxbdist.RHB65sy/PyXB-1.1.5/pyxb/bundles/common/schemas/xlink.xsd', 198, 2)
    
    title = property(__title.value, __title.set, None, None)

    
    # Attribute {http://www.w3.org/1999/xlink}label uses Python identifier label
    __label = pyxb.binding.content.AttributeUse(pyxb.namespace.ExpandedName(Namespace, u'label'), 'label', '__httpwww_w3_org1999xlink_resourceType_httpwww_w3_org1999xlinklabel', labelType)
    __label._DeclarationLocation = pyxb.utils.utility.Location('/tmp/pyxbdist.RHB65sy/PyXB-1.1.5/pyxb/bundles/common/schemas/xlink.xsd', 93, 1)
    __label._UseLocation = pyxb.utils.utility.Location('/tmp/pyxbdist.RHB65sy/PyXB-1.1.5/pyxb/bundles/common/schemas/xlink.xsd', 199, 2)
    
    label = property(__label.value, __label.set, None, None)

    
    # Attribute {http://www.w3.org/1999/xlink}role uses Python identifier role
    __role = pyxb.binding.content.AttributeUse(pyxb.namespace.ExpandedName(Namespace, u'role'), 'role', '__httpwww_w3_org1999xlink_resourceType_httpwww_w3_org1999xlinkrole', roleType)
    __role._DeclarationLocation = pyxb.utils.utility.Location('/tmp/pyxbdist.RHB65sy/PyXB-1.1.5/pyxb/bundles/common/schemas/xlink.xsd', 48, 1)
    __role._UseLocation = pyxb.utils.utility.Location('/tmp/pyxbdist.RHB65sy/PyXB-1.1.5/pyxb/bundles/common/schemas/xlink.xsd', 197, 2)
    
    role = property(__role.value, __role.set, None, None)

    _HasWildcardElement = True

    _ElementMap = {
        
    }
    _AttributeMap = {
        __type.name() : __type,
        __title.name() : __title,
        __label.name() : __label,
        __role.name() : __role
    }
Namespace.addCategoryObject('typeBinding', u'resourceType', resourceType)


# Complex type {http://www.w3.org/1999/xlink}simple with content type MIXED
class simple (pyxb.binding.basis.complexTypeDefinition):
    _TypeDefinition = None
    _ContentTypeTag = pyxb.binding.basis.complexTypeDefinition._CT_MIXED
    _Abstract = False
    _ExpandedName = pyxb.namespace.ExpandedName(Namespace, u'simple')
    _DefinitionLocation = pyxb.utils.utility.Location('/tmp/pyxbdist.RHB65sy/PyXB-1.1.5/pyxb/bundles/common/schemas/xlink.xsd', 127, 1)
    # Base type is pyxb.binding.datatypes.anyType
    
    # Attribute {http://www.w3.org/1999/xlink}role uses Python identifier role
    __role = pyxb.binding.content.AttributeUse(pyxb.namespace.ExpandedName(Namespace, u'role'), 'role', '__httpwww_w3_org1999xlink_simple_httpwww_w3_org1999xlinkrole', roleType)
    __role._DeclarationLocation = pyxb.utils.utility.Location('/tmp/pyxbdist.RHB65sy/PyXB-1.1.5/pyxb/bundles/common/schemas/xlink.xsd', 48, 1)
    __role._UseLocation = pyxb.utils.utility.Location('/tmp/pyxbdist.RHB65sy/PyXB-1.1.5/pyxb/bundles/common/schemas/xlink.xsd', 114, 2)
    
    role = property(__role.value, __role.set, None, None)

    
    # Attribute {http://www.w3.org/1999/xlink}href uses Python identifier href
    __href = pyxb.binding.content.AttributeUse(pyxb.namespace.ExpandedName(Namespace, u'href'), 'href', '__httpwww_w3_org1999xlink_simple_httpwww_w3_org1999xlinkhref', hrefType)
    __href._DeclarationLocation = pyxb.utils.utility.Location('/tmp/pyxbdist.RHB65sy/PyXB-1.1.5/pyxb/bundles/common/schemas/xlink.xsd', 42, 1)
    __href._UseLocation = pyxb.utils.utility.Location('/tmp/pyxbdist.RHB65sy/PyXB-1.1.5/pyxb/bundles/common/schemas/xlink.xsd', 113, 2)
    
    href = property(__href.value, __href.set, None, None)

    
    # Attribute {http://www.w3.org/1999/xlink}arcrole uses Python identifier arcrole
    __arcrole = pyxb.binding.content.AttributeUse(pyxb.namespace.ExpandedName(Namespace, u'arcrole'), 'arcrole', '__httpwww_w3_org1999xlink_simple_httpwww_w3_org1999xlinkarcrole', arcroleType)
    __arcrole._DeclarationLocation = pyxb.utils.utility.Location('/tmp/pyxbdist.RHB65sy/PyXB-1.1.5/pyxb/bundles/common/schemas/xlink.xsd', 56, 1)
    __arcrole._UseLocation = pyxb.utils.utility.Location('/tmp/pyxbdist.RHB65sy/PyXB-1.1.5/pyxb/bundles/common/schemas/xlink.xsd', 115, 2)
    
    arcrole = property(__arcrole.value, __arcrole.set, None, None)

    
    # Attribute {http://www.w3.org/1999/xlink}title uses Python identifier title
    __title = pyxb.binding.content.AttributeUse(pyxb.namespace.ExpandedName(Namespace, u'title'), 'title', '__httpwww_w3_org1999xlink_simple_httpwww_w3_org1999xlinktitle', titleAttrType)
    __title._DeclarationLocation = pyxb.utils.utility.Location('/tmp/pyxbdist.RHB65sy/PyXB-1.1.5/pyxb/bundles/common/schemas/xlink.xsd', 64, 1)
    __title._UseLocation = pyxb.utils.utility.Location('/tmp/pyxbdist.RHB65sy/PyXB-1.1.5/pyxb/bundles/common/schemas/xlink.xsd', 116, 2)
    
    title = property(__title.value, __title.set, None, None)

    
    # Attribute {http://www.w3.org/1999/xlink}actuate uses Python identifier actuate
    __actuate = pyxb.binding.content.AttributeUse(pyxb.namespace.ExpandedName(Namespace, u'actuate'), 'actuate', '__httpwww_w3_org1999xlink_simple_httpwww_w3_org1999xlinkactuate', actuateType)
    __actuate._DeclarationLocation = pyxb.utils.utility.Location('/tmp/pyxbdist.RHB65sy/PyXB-1.1.5/pyxb/bundles/common/schemas/xlink.xsd', 82, 1)
    __actuate._UseLocation = pyxb.utils.utility.Location('/tmp/pyxbdist.RHB65sy/PyXB-1.1.5/pyxb/bundles/common/schemas/xlink.xsd', 118, 2)
    
    actuate = property(__actuate.value, __actuate.set, None, None)

    
    # Attribute {http://www.w3.org/1999/xlink}type uses Python identifier type
    __type = pyxb.binding.content.AttributeUse(pyxb.namespace.ExpandedName(Namespace, u'type'), 'type', '__httpwww_w3_org1999xlink_simple_httpwww_w3_org1999xlinktype', typeType, fixed=True, unicode_default=u'simple')
    __type._DeclarationLocation = pyxb.utils.utility.Location('/tmp/pyxbdist.RHB65sy/PyXB-1.1.5/pyxb/bundles/common/schemas/xlink.xsd', 29, 1)
    __type._UseLocation = pyxb.utils.utility.Location('/tmp/pyxbdist.RHB65sy/PyXB-1.1.5/pyxb/bundles/common/schemas/xlink.xsd', 112, 2)
    
    type = property(__type.value, __type.set, None, None)

    
    # Attribute {http://www.w3.org/1999/xlink}show uses Python identifier show
    __show = pyxb.binding.content.AttributeUse(pyxb.namespace.ExpandedName(Namespace, u'show'), 'show', '__httpwww_w3_org1999xlink_simple_httpwww_w3_org1999xlinkshow', showType)
    __show._DeclarationLocation = pyxb.utils.utility.Location('/tmp/pyxbdist.RHB65sy/PyXB-1.1.5/pyxb/bundles/common/schemas/xlink.xsd', 70, 1)
    __show._UseLocation = pyxb.utils.utility.Location('/tmp/pyxbdist.RHB65sy/PyXB-1.1.5/pyxb/bundles/common/schemas/xlink.xsd', 117, 2)
    
    show = property(__show.value, __show.set, None, None)

    _HasWildcardElement = True

    _ElementMap = {
        
    }
    _AttributeMap = {
        __role.name() : __role,
        __href.name() : __href,
        __arcrole.name() : __arcrole,
        __title.name() : __title,
        __actuate.name() : __actuate,
        __type.name() : __type,
        __show.name() : __show
    }
Namespace.addCategoryObject('typeBinding', u'simple', simple)


# Complex type {http://www.w3.org/1999/xlink}extended with content type ELEMENT_ONLY
class extended (pyxb.binding.basis.complexTypeDefinition):
    _TypeDefinition = None
    _ContentTypeTag = pyxb.binding.basis.complexTypeDefinition._CT_ELEMENT_ONLY
    _Abstract = False
    _ExpandedName = pyxb.namespace.ExpandedName(Namespace, u'extended')
    _DefinitionLocation = pyxb.utils.utility.Location('/tmp/pyxbdist.RHB65sy/PyXB-1.1.5/pyxb/bundles/common/schemas/xlink.xsd', 153, 1)
    # Base type is pyxb.binding.datatypes.anyType
    
    # Element {http://www.w3.org/1999/xlink}arc uses Python identifier arc
    __arc = pyxb.binding.content.ElementUse(pyxb.namespace.ExpandedName(Namespace, u'arc'), 'arc', '__httpwww_w3_org1999xlink_extended_httpwww_w3_org1999xlinkarc', True)
    __arc._DeclarationLocation = pyxb.utils.utility.Location('/tmp/pyxbdist.RHB65sy/PyXB-1.1.5/pyxb/bundles/common/schemas/xlink.xsd', 241, 1)
    __arc._UseLocation = pyxb.utils.utility.Location('/tmp/pyxbdist.RHB65sy/PyXB-1.1.5/pyxb/bundles/common/schemas/xlink.xsd', 163, 2)

    
    arc = property(__arc.value, __arc.set, None, None)

    
    # Element {http://www.w3.org/1999/xlink}resource uses Python identifier resource
    __resource = pyxb.binding.content.ElementUse(pyxb.namespace.ExpandedName(Namespace, u'resource'), 'resource', '__httpwww_w3_org1999xlink_extended_httpwww_w3_org1999xlinkresource', True)
    __resource._DeclarationLocation = pyxb.utils.utility.Location('/tmp/pyxbdist.RHB65sy/PyXB-1.1.5/pyxb/bundles/common/schemas/xlink.xsd', 193, 1)
    __resource._UseLocation = pyxb.utils.utility.Location('/tmp/pyxbdist.RHB65sy/PyXB-1.1.5/pyxb/bundles/common/schemas/xlink.xsd', 163, 2)

    
    resource = property(__resource.value, __resource.set, None, None)

    
    # Element {http://www.w3.org/1999/xlink}title uses Python identifier title
    __title = pyxb.binding.content.ElementUse(pyxb.namespace.ExpandedName(Namespace, u'title'), 'title', '__httpwww_w3_org1999xlink_extended_httpwww_w3_org1999xlinktitle', True)
    __title._DeclarationLocation = pyxb.utils.utility.Location('/tmp/pyxbdist.RHB65sy/PyXB-1.1.5/pyxb/bundles/common/schemas/xlink.xsd', 167, 1)
    __title._UseLocation = pyxb.utils.utility.Location('/tmp/pyxbdist.RHB65sy/PyXB-1.1.5/pyxb/bundles/common/schemas/xlink.xsd', 163, 2)

    
    title = property(__title.value, __title.set, None, None)

    
    # Element {http://www.w3.org/1999/xlink}locator uses Python identifier locator
    __locator = pyxb.binding.content.ElementUse(pyxb.namespace.ExpandedName(Namespace, u'locator'), 'locator', '__httpwww_w3_org1999xlink_extended_httpwww_w3_org1999xlinklocator', True)
    __locator._DeclarationLocation = pyxb.utils.utility.Location('/tmp/pyxbdist.RHB65sy/PyXB-1.1.5/pyxb/bundles/common/schemas/xlink.xsd', 213, 1)
    __locator._UseLocation = pyxb.utils.utility.Location('/tmp/pyxbdist.RHB65sy/PyXB-1.1.5/pyxb/bundles/common/schemas/xlink.xsd', 163, 2)

    
    locator = property(__locator.value, __locator.set, None, None)

    
    # Attribute {http://www.w3.org/1999/xlink}role uses Python identifier role
    __role = pyxb.binding.content.AttributeUse(pyxb.namespace.ExpandedName(Namespace, u'role'), 'role', '__httpwww_w3_org1999xlink_extended_httpwww_w3_org1999xlinkrole', roleType)
    __role._DeclarationLocation = pyxb.utils.utility.Location('/tmp/pyxbdist.RHB65sy/PyXB-1.1.5/pyxb/bundles/common/schemas/xlink.xsd', 48, 1)
    __role._UseLocation = pyxb.utils.utility.Location('/tmp/pyxbdist.RHB65sy/PyXB-1.1.5/pyxb/bundles/common/schemas/xlink.xsd', 140, 2)
    
    role = property(__role.value, __role.set, None, None)

    
    # Attribute {http://www.w3.org/1999/xlink}type uses Python identifier type
    __type = pyxb.binding.content.AttributeUse(pyxb.namespace.ExpandedName(Namespace, u'type'), 'type', '__httpwww_w3_org1999xlink_extended_httpwww_w3_org1999xlinktype', typeType, fixed=True, unicode_default=u'extended', required=True)
    __type._DeclarationLocation = pyxb.utils.utility.Location('/tmp/pyxbdist.RHB65sy/PyXB-1.1.5/pyxb/bundles/common/schemas/xlink.xsd', 29, 1)
    __type._UseLocation = pyxb.utils.utility.Location('/tmp/pyxbdist.RHB65sy/PyXB-1.1.5/pyxb/bundles/common/schemas/xlink.xsd', 139, 2)
    
    type = property(__type.value, __type.set, None, None)

    
    # Attribute {http://www.w3.org/1999/xlink}title uses Python identifier title_
    __title_ = pyxb.binding.content.AttributeUse(pyxb.namespace.ExpandedName(Namespace, u'title'), 'title_', '__httpwww_w3_org1999xlink_extended_httpwww_w3_org1999xlinktitle_', titleAttrType)
    __title_._DeclarationLocation = pyxb.utils.utility.Location('/tmp/pyxbdist.RHB65sy/PyXB-1.1.5/pyxb/bundles/common/schemas/xlink.xsd', 64, 1)
    __title_._UseLocation = pyxb.utils.utility.Location('/tmp/pyxbdist.RHB65sy/PyXB-1.1.5/pyxb/bundles/common/schemas/xlink.xsd', 141, 2)
    
    title_ = property(__title_.value, __title_.set, None, None)


    _ElementMap = {
        __arc.name() : __arc,
        __resource.name() : __resource,
        __title.name() : __title,
        __locator.name() : __locator
    }
    _AttributeMap = {
        __role.name() : __role,
        __type.name() : __type,
        __title_.name() : __title_
    }
Namespace.addCategoryObject('typeBinding', u'extended', extended)


locator = pyxb.binding.basis.element(pyxb.namespace.ExpandedName(Namespace, u'locator'), locatorType, abstract=pyxb.binding.datatypes.boolean(1))
Namespace.addCategoryObject('elementBinding', locator.name().localName(), locator)

arc = pyxb.binding.basis.element(pyxb.namespace.ExpandedName(Namespace, u'arc'), arcType, abstract=pyxb.binding.datatypes.boolean(1))
Namespace.addCategoryObject('elementBinding', arc.name().localName(), arc)

title = pyxb.binding.basis.element(pyxb.namespace.ExpandedName(Namespace, u'title'), titleEltType, abstract=pyxb.binding.datatypes.boolean(1))
Namespace.addCategoryObject('elementBinding', title.name().localName(), title)

resource = pyxb.binding.basis.element(pyxb.namespace.ExpandedName(Namespace, u'resource'), resourceType, abstract=pyxb.binding.datatypes.boolean(1))
Namespace.addCategoryObject('elementBinding', resource.name().localName(), resource)



locatorType._AddElement(pyxb.binding.basis.element(pyxb.namespace.ExpandedName(Namespace, u'title'), titleEltType, abstract=pyxb.binding.datatypes.boolean(1), scope=locatorType))
locatorType._GroupModel = pyxb.binding.content.GroupSequence(
    pyxb.binding.content.ParticleModel(locatorType._UseForTag(pyxb.namespace.ExpandedName(Namespace, u'title')), min_occurs=0L, max_occurs=None)
    )
locatorType._ContentModel = pyxb.binding.content.ParticleModel(locatorType._GroupModel, min_occurs=1, max_occurs=1)


titleEltType._GroupModel = pyxb.binding.content.GroupSequence(
    pyxb.binding.content.ParticleModel(pyxb.binding.content.Wildcard(process_contents=pyxb.binding.content.Wildcard.PC_lax, namespace_constraint=pyxb.binding.content.Wildcard.NC_any), min_occurs=0L, max_occurs=None)
    )
titleEltType._ContentModel = pyxb.binding.content.ParticleModel(titleEltType._GroupModel, min_occurs=1, max_occurs=1)



arcType._AddElement(pyxb.binding.basis.element(pyxb.namespace.ExpandedName(Namespace, u'title'), titleEltType, abstract=pyxb.binding.datatypes.boolean(1), scope=arcType))
arcType._GroupModel = pyxb.binding.content.GroupSequence(
    pyxb.binding.content.ParticleModel(arcType._UseForTag(pyxb.namespace.ExpandedName(Namespace, u'title')), min_occurs=0L, max_occurs=None)
    )
arcType._ContentModel = pyxb.binding.content.ParticleModel(arcType._GroupModel, min_occurs=1, max_occurs=1)


resourceType._GroupModel = pyxb.binding.content.GroupSequence(
    pyxb.binding.content.ParticleModel(pyxb.binding.content.Wildcard(process_contents=pyxb.binding.content.Wildcard.PC_lax, namespace_constraint=pyxb.binding.content.Wildcard.NC_any), min_occurs=0L, max_occurs=None)
    )
resourceType._ContentModel = pyxb.binding.content.ParticleModel(resourceType._GroupModel, min_occurs=1, max_occurs=1)


simple._GroupModel = pyxb.binding.content.GroupSequence(
    pyxb.binding.content.ParticleModel(pyxb.binding.content.Wildcard(process_contents=pyxb.binding.content.Wildcard.PC_lax, namespace_constraint=pyxb.binding.content.Wildcard.NC_any), min_occurs=0L, max_occurs=None)
    )
simple._ContentModel = pyxb.binding.content.ParticleModel(simple._GroupModel, min_occurs=1, max_occurs=1)



extended._AddElement(pyxb.binding.basis.element(pyxb.namespace.ExpandedName(Namespace, u'arc'), arcType, abstract=pyxb.binding.datatypes.boolean(1), scope=extended))

extended._AddElement(pyxb.binding.basis.element(pyxb.namespace.ExpandedName(Namespace, u'resource'), resourceType, abstract=pyxb.binding.datatypes.boolean(1), scope=extended))

extended._AddElement(pyxb.binding.basis.element(pyxb.namespace.ExpandedName(Namespace, u'title'), titleEltType, abstract=pyxb.binding.datatypes.boolean(1), scope=extended))

extended._AddElement(pyxb.binding.basis.element(pyxb.namespace.ExpandedName(Namespace, u'locator'), locatorType, abstract=pyxb.binding.datatypes.boolean(1), scope=extended))
extended._GroupModel = pyxb.binding.content.GroupChoice(
    pyxb.binding.content.ParticleModel(extended._UseForTag(pyxb.namespace.ExpandedName(Namespace, u'title')), min_occurs=1, max_occurs=1),
    pyxb.binding.content.ParticleModel(extended._UseForTag(pyxb.namespace.ExpandedName(Namespace, u'resource')), min_occurs=1, max_occurs=1),
    pyxb.binding.content.ParticleModel(extended._UseForTag(pyxb.namespace.ExpandedName(Namespace, u'locator')), min_occurs=1, max_occurs=1),
    pyxb.binding.content.ParticleModel(extended._UseForTag(pyxb.namespace.ExpandedName(Namespace, u'arc')), min_occurs=1, max_occurs=1)
    )
extended._ContentModel = pyxb.binding.content.ParticleModel(extended._GroupModel, min_occurs=0L, max_occurs=None)
