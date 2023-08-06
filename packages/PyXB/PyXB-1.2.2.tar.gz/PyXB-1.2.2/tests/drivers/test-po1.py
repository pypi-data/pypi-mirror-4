# -*- coding: utf-8 -*-
import logging
if __name__ == '__main__':
    logging.basicConfig()
_log = logging.getLogger(__name__)
import pyxb.binding.generate
import pyxb.utils.domutils
from xml.dom import Node

import os.path
schema_path = os.path.abspath(os.path.join(os.path.dirname(__file__), '../schemas/po1.xsd'))
code = pyxb.binding.generate.GeneratePython(schema_location=schema_path)

#file('code.py', 'w').write(code)
rv = compile(code, 'test', 'exec')
eval(rv)

from pyxb.exceptions_ import *

from pyxb.utils import domutils

def ToDOM (instance, tag=None, dom_support=None):
    return instance.toDOM(dom_support).documentElement

import unittest

class TestPO1 (unittest.TestCase):
    street_content = '''95 Main St.
Anytown, AS  12345-6789'''
    street_xml = '<street>%s</street>' % (street_content,)
    street_dom = pyxb.utils.domutils.StringToDOM(street_xml).documentElement

    address1_xml = '<name>Customer</name><street>95 Main St</street>'
    address2_xml = '<name>Sugar Mama</name><street>24 E. Dearling Ave.</street>'

    def tearDown (self):
        pyxb.RequireValidWhenGenerating(True)
        pyxb.RequireValidWhenParsing(True)

    def testPythonElementSimpleContent (self):
        elt = USAddress._ElementMap['street'].elementBinding()(self.street_content)
        self.assertEqual(self.street_content, elt)
        self.assertEqual(ToDOM(elt).toxml("utf-8"), self.street_xml)

    def testDOMElementSimpleContent (self):
        elt = USAddress._ElementMap['street'].elementBinding().createFromDOM(self.street_dom)
        self.assertEqual(ToDOM(elt).toxml("utf-8"), self.street_xml)

    def testPythonElementComplexContent_Element (self):
        addr = USAddress(name='Customer', street='95 Main St')
        self.assertEqual('95 Main St', addr.street)
        addr = USAddress('Customer', '95 Main St')
        self.assertEqual('95 Main St', addr.street)
        addr.street = '43 West Oak'
        self.assertEqual('43 West Oak', addr.street)
        #self.assertEqual('<s>%s</s>' % (self.address1_xml,), ToDOM(addr, tag='s').toxml("utf-8"))

    def testDOM_CTD_element (self):
        # NB: USAddress is a CTD, not an element.
        xml = '<shipTo>%s</shipTo>' % (self.address1_xml,)
        dom = pyxb.utils.domutils.StringToDOM(xml)
        addr2 = USAddress.Factory(_dom_node=dom.documentElement)
        #self.assertEqual(xml, ToDOM(addr2, tag='shipTo').toxml("utf-8"))

    def testPurchaseOrder (self):
        po = purchaseOrder(shipTo=USAddress(name='Customer', street='95 Main St'),
                           billTo=USAddress(name='Sugar Mama', street='24 E. Dearling Ave'),
                           comment='Thanks!')
        xml = ToDOM(po).toxml("utf-8")
        xml1 = '<ns1:purchaseOrder xmlns:ns1="http://www.example.com/PO1"><shipTo><name>Customer</name><street>95 Main St</street></shipTo><billTo><name>Sugar Mama</name><street>24 E. Dearling Ave</street></billTo><ns1:comment>Thanks!</ns1:comment></ns1:purchaseOrder>'
        self.assertEqual(xml, xml1)

        dom = pyxb.utils.domutils.StringToDOM(xml)
        po2 = purchaseOrder.createFromDOM(dom.documentElement)
        self.assertEqual(xml1, ToDOM(po2).toxml("utf-8"))
        loc = po2.shipTo._location()
        self.assertTrue((not isinstance(loc, pyxb.utils.utility.Locatable_mixin)) or (58 == loc.columnNumber))
        loc = po2.billTo.name._location()
        self.assertTrue((not isinstance(loc, pyxb.utils.utility.Locatable_mixin)) or (131 == loc.columnNumber))

        po2 = CreateFromDocument(xml)
        self.assertEqual(xml1, ToDOM(po2).toxml("utf-8"))
        loc = po2.shipTo._location()
        self.assertTrue((not isinstance(loc, pyxb.utils.utility.Locatable_mixin)) or (58 == loc.columnNumber))
        loc = po2.billTo.name._location()
        self.assertTrue((not isinstance(loc, pyxb.utils.utility.Locatable_mixin)) or (131 == loc.columnNumber))


        xml2 = '<purchaseOrder xmlns="http://www.example.com/PO1"><shipTo><name>Customer</name><street>95 Main St</street></shipTo><billTo><name>Sugar Mama</name><street>24 E. Dearling Ave</street></billTo><comment>Thanks!</comment></purchaseOrder>'
        bds = pyxb.utils.domutils.BindingDOMSupport()
        bds.setDefaultNamespace(Namespace)
        self.assertEqual(xml2, ToDOM(po2, dom_support=bds).toxml("utf-8"))

    def testGenerationValidation (self):
        ship_to = USAddress('Robert Smith', 'General Delivery')
        po = purchaseOrder(ship_to)
        self.assertEqual('General Delivery', po.shipTo.street)
        self.assertTrue(po.billTo is None)

        self.assertTrue(pyxb.RequireValidWhenGenerating())
        self.assertRaises(pyxb.IncompleteElementContentError, po.toxml)
        try:
            pyxb.RequireValidWhenGenerating(False)
            self.assertFalse(pyxb.RequireValidWhenGenerating())
            xmls = po.toxml("utf-8", root_only=True)
            self.assertEqual('<ns1:purchaseOrder xmlns:ns1="http://www.example.com/PO1"><shipTo><street>General Delivery</street><name>Robert Smith</name></shipTo></ns1:purchaseOrder>', xmls)
        finally:
            pyxb.RequireValidWhenGenerating(True)
        self.assertRaises(pyxb.UnrecognizedContentError, CreateFromDocument, xmls)
        self.assertTrue(pyxb.RequireValidWhenParsing())
        try:
            pyxb.RequireValidWhenParsing(False)
            self.assertFalse(pyxb.RequireValidWhenParsing())
            po2 = CreateFromDocument(xmls)
        finally:
            pyxb.RequireValidWhenParsing(True)
        self.assertEqual('General Delivery', po2.shipTo.street)
        self.assertTrue(po2.billTo is None)

if __name__ == '__main__':
    unittest.main()
    
        
