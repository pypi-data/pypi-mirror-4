pholcidae - Tiny python web crawler library
=========

Pholcidae
------------

Pholcidae, commonly known as cellar spiders, are a spider family in the suborder Araneomorphae.

About
------------

Pholcidae is a tiny Python module allows you to write your own crawl spider fast and easy.

Dependencies
------------

* python >= 2.6.x

Basic example
------------

    from pholcidae import Pholcidae

    class MySpider(Pholcidae):

        settings = {'domain': 'www.test.com', 'start_page': '/sitemap/'}

        def crawl(self, data):
            print(data.url)

    spider = MySpider()
    spider.start()
