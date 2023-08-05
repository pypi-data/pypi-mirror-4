###############################################################################
#
# Copyright (c) 2011 Projekt01 GmbH and Contributors.
# All Rights Reserved.
#
# This software is subject to the provisions of the Zope Public License,
# Version 2.1 (ZPL).  A copy of the ZPL should accompany this distribution.
# THIS SOFTWARE IS PROVIDED "AS IS" AND ANY AND ALL EXPRESS OR IMPLIED
# WARRANTIES ARE DISCLAIMED, INCLUDING, BUT NOT LIMITED TO, THE IMPLIED
# WARRANTIES OF TITLE, MERCHANTABILITY, AGAINST INFRINGEMENT, AND FITNESS
# FOR A PARTICULAR PURPOSE.
#
###############################################################################
"""
$Id:$
"""
__docformat__ = "reStructuredText"

import zope.interface

import s01.scrapy.item
import s01.scrapy.converter
from s01.scrapy.fieldproperty import ScrapyFieldProperty

from s01.demo import interfaces


class DemoItem(s01.scrapy.item.ScrapyItemBase):
    """DemoItem item
    
    This DemoItem uses a test exporter which is able to find the fields
    based on the given interface. see: s01.scrapy.exporter.TestExporter
    """

    zope.interface.implements(interfaces.IDemoItem)

    title = ScrapyFieldProperty(interfaces.IDemoItem['title'],
        converter=s01.scrapy.converter.textLineConverter)

    description = ScrapyFieldProperty(interfaces.IDemoItem['description'],
        converter=s01.scrapy.converter.textConverter)

    url = ScrapyFieldProperty(interfaces.IDemoItem['url'],
        converter=s01.scrapy.converter.textConverter)
