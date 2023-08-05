======
README
======

Let's do some simple test cases. First test the imports:

  >>> import pkg_resources
  >>> import scrapy.crawler
  >>> import s01.scrapy.util
  >>> import xscrapy.testing
  >>> from xscrapy.item import ScrapyItem
  >>> from xspider.coop.spiders.spider import CoopSpider


Crawler
-------

  >>> settings = s01.scrapy.util.settings
  >>> crawler = scrapy.crawler.CrawlerProcess(settings)


Spider
------

  >>> spider = CoopSpider()
  >>> spider
  <CoopSpider 'coop.ch' at ...>

  >>> spider.name
  'coop.ch'

  >>> spider._crawler = crawler


ScrapyItem
----------

  >>> response = xscrapy.testing.getTestResponse()
  >>> item = spider.getItem(response, '42', spider.name)
  >>> item
  <ScrapyItem (xspider.coop ... coop.ch) 42 for coop.ch>

  >>> item.comMarker
  u'coop.ch'

  >>> version = pkg_resources.require(item.pkgName)[0].version
  >>> version == item.pkgVersion
  True
