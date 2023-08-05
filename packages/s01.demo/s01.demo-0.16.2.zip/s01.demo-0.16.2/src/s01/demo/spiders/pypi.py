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
"""demo scrapy spider
$Id:$
"""
__docformat__ = "reStructuredText"

from scrapy.selector import HtmlXPathSelector
from scrapy.spider import BaseSpider

from s01.demo.item import DemoItem


class DemoSpider(BaseSpider):
    """Demo spider package

    You can install such buildout based packages with the spider processor 
    located in s01.worker.
    """

    name = "python.org"

    allowed_domains = ["python.org"]

    start_urls = [
        "http://pypi.python.org/pypi"
    ]

    def parse(self, response):
        hxs = HtmlXPathSelector(response)
        baseURL = 'http://pypi.python.org/pypi/'
        xPath = "//table[@class='list']/tr"
        rows = hxs.select(xPath)
        for row in rows:
            try:
                url = row.select('*/a/@href').extract()
                if not url:
                    # this is the table header
                    continue
                item = DemoItem(self)
                item.title = row.select('*/a/text()').extract()[0]
                item.description = row.select('td[3]/text()').extract()[0]
                item.url = baseURL + url[0]
                yield item
            except IndexError, e:
                # skip row
                pass
