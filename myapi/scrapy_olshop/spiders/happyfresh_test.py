# -*- coding: utf-8 -*-
__author__ = 'dimz'

import re
import urllib.parse
import uuid
import datetime
import scrapy
import scrapy_splash
from scrapy_splash import SplashRequest


class HappyFreshSpider(scrapy.Spider):
    name = 'happyfresh'
    allowed_domains = ['happyfresh.id']
    myurl = 'https://www.happyfresh.id/hero-paskal-hypersquare/fresh-produce-2/'
    lua_script = '''
            function main(splash, args)
              splash.private_mode_enabled = false
              url = args.url
              assert(splash:go(url))
              assert(splash:wait(0.5))

              --https://stackoverflow.com/a/40366442
              local num_scrolls = 7
              local scroll_delay = 1.0

              local scroll_to = splash:jsfunc("window.scrollTo")
              local get_body_height = splash:jsfunc(
                "function() {return document.body.scrollHeight;}"
              )

              for _ = 1, num_scrolls do
                scroll_to(0, _ * get_body_height() / num_scrolls)
                splash:wait(scroll_delay)
              end
              --splash:set_viewport_full()

              return splash:html()
            end
        '''
    lua_script2 = '''
            function main(splash, args)
              splash.private_mode_enabled = false
              assert(splash:go(args.url))
              assert(splash:wait(1))
              return splash:html()
            end
        '''

    def start_requests(self):
        self.logger.info("PROSES start request")
        yield SplashRequest(url=self.myurl, callback=self.parse_link, endpoint="execute",
                            args={'wait': 2, 'lua_source': self.lua_script})

    def parse_link(self, response):
        for product in response.css('div.jsx-2542647244.root.PLP-Common-fresh-produce-2-product-container'):
            link = urllib.parse.urljoin(
                response.url.replace('www', 'm'),
                product.css("a.jsx-2542647244.jsx-717190455::attr('href')").get())
            self.logger.info("TELAH PROSES URL PRODUK: {}".format(response.url))

            yield SplashRequest(url=link, callback=self.parse_produk, endpoint="execute",
                                args={'wait': 4, 'lua_source': self.lua_script2}, meta=dict(dont_retry=False),
                                slot_policy=scrapy_splash.SlotPolicy.PER_DOMAIN, dont_process_response=True)

    @staticmethod
    def _parse_harga(string_price):
        if string_price is None:
            return None
        else:
            pattern = re.compile(r"(\d+,?.?\d*)")
            found_price = pattern.search(string_price).group(1)
            price_wo_commas = found_price.replace(".", "").replace(",", "")
            return float(price_wo_commas)

    def parse_produk(self, response):
        data = response.css("div#app")
        self.logger.info("PROSES PRODUK: {}".format(response.url))

        data_harga_awal = data.css("strike._3Ge3B::text").get()
        harga_awal = self._parse_harga(data_harga_awal) if data_harga_awal is not None else '-'

        data_harga = data.css("span._3p5jU::text").get()
        if data_harga is None:
            data_harga = data.css("span._2qwjQ::text").get()
        harga = self._parse_harga(data_harga)

        # mengambil data discount
        pattern_discount = re.compile(r"(\d+%)")
        data_discount = data.css("div._3_5A2 span::text").get()
        discount = pattern_discount.search(data_discount).group(1) if data_discount is not None else '-'

        yield {
            '_id': uuid.uuid4().hex,
            'sumber': 'happyfresh.id',
            'tgl_crawl': datetime.datetime.now().strftime("%Y-%m-%d %H:%M"),
            'nama_produk': data.css("h1._8OGam::text").get(),
            'link_produk': response.url.replace("m.happyfresh.id", "www.happyfresh.id"),
            'deskripsi': data.css("div._37miB::text").get(),
            'thumb': data.css("figure._2wUby img::attr('src')").get(),
            'harga_unit': self._parse_harga(data.css("div._3iDvw span::text").get()),
            'harga_awal': harga_awal,
            'harga': harga,
            'discount': discount,
            'qty': data.css("div._1CE2f::text").get(),
            'qty_unit': data.css("div._3iDvw span::text").get().split(" / ")[-1],
            'username': 'Hero Paskal Hypersquare',
            'link_toko': 'https://www.happyfresh.id/hero-paskal-hypersquare/',
        }
