# -*- coding: utf-8 -*-
__author__ = 'dimz'

import re
import uuid
import datetime
import scrapy_splash
from scrapy.http import HtmlResponse
from scrapy.linkextractors.lxmlhtml import LxmlLinkExtractor
from scrapy.spiders import CrawlSpider, Rule
from scrapy_splash import SplashRequest, SplashJsonResponse, SplashTextResponse


# class HfHeropaskalSpider(scrapy.Spider):
class HfTransmartPvjSpider(CrawlSpider):
    name = 'hf-transmartpvj'
    allowed_domains = ['happyfresh.id']
    start_urls = [
        'https://www.happyfresh.id/transmart-carrefour-paris-van-java/fresh-fruits-3/',
        'https://www.happyfresh.id/transmart-carrefour-paris-van-java/fresh-vegetables-4/',
        'https://www.happyfresh.id/transmart-carrefour-paris-van-java/fresh-herbs-5/',
        'https://www.happyfresh.id/transmart-carrefour-paris-van-java/packaged-fruit-vegetables-6/',
        'https://www.happyfresh.id/transmart-carrefour-paris-van-java/organic-dairy-beverages-473/',
        'https://www.happyfresh.id/transmart-carrefour-paris-van-java/organic-pantry-supplies-476/',
        'https://www.happyfresh.id/transmart-carrefour-paris-van-java/dairy-eggs-24/',
        'https://www.happyfresh.id/transmart-carrefour-paris-van-java/pantry-48/',
        'https://www.happyfresh.id/transmart-carrefour-paris-van-java/dry-canned-goods-34/',
        'https://www.happyfresh.id/transmart-carrefour-paris-van-java/meat-seafood-7/',
        'https://www.happyfresh.id/transmart-carrefour-paris-van-java/frozen-70/',
        'https://www.happyfresh.id/transmart-carrefour-paris-van-java/deli-13/',
        'https://www.happyfresh.id/transmart-carrefour-paris-van-java/bakery-19/',
        'https://www.happyfresh.id/transmart-carrefour-paris-van-java/beverages-53/',
        'https://www.happyfresh.id/transmart-carrefour-paris-van-java/snacks-60/',
    ]

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

    rules = (
        Rule(
            link_extractor=LxmlLinkExtractor(
                restrict_xpaths="//div[contains(@class, 'jsx-4130121889 root')]/ul/li[last()]/a"),
            process_request="use_splash",
            follow=True
        ),
        Rule(
            link_extractor=LxmlLinkExtractor(
                restrict_xpaths="//div[contains(@class, 'jsx-2542647244 root')]/a"),
            process_links="process_links_produk",
            process_request="use_splash_script2",
            callback='parse_produk',
            follow=True,
        ),
    )

    def process_links_produk(self, links):
        self.logger.info("PROSES link produk")
        for link in links:
            link.url = link.url.replace('www', 'm')  # pakai versi mobile untuk scraping data produk
            yield link

    # https://github.com/scrapy-plugins/scrapy-splash/issues/92#issuecomment-487113695
    def _requests_to_follow(self, response):
        self.logger.info("PROSES request to follow")
        if not isinstance(
                response,
                (HtmlResponse, SplashJsonResponse, SplashTextResponse)):
            return
        seen = set()
        for n, rule in enumerate(self._rules):
            links = [lnk for lnk in rule.link_extractor.extract_links(response)
                     if lnk not in seen]
            if links and rule.process_links:
                links = rule.process_links(links)
            for link in links:
                seen.add(link)
                r = self._build_request(n, link)
                yield rule.process_request(r)

    def _build_request(self, rule, link):
        self.logger.info("PROSES build request {}".format(link.url))
        # parameter 'meta' is required !!!!!
        r = SplashRequest(url=link.url, callback=self._response_downloaded, endpoint="execute",
                          meta={'rule': rule, 'link_text': link.text, 'dont_retry': False},
                          args={'wait': 2, 'lua_source': self.lua_script},
                          slot_policy=scrapy_splash.SlotPolicy.PER_DOMAIN, dont_process_response=True)
        # args={'wait': 2, 'url': link.url, 'lua_source': self.lua_script})
        # Maybe you can delete it here.
        # r.meta.update(rule=rule, link_text=link.text, dont_retry=False)
        return r

    def use_splash(self, request):
        self.logger.info("PROSES use splash")
        request.meta.update(splash={
            'args': {
                'wait': 2,
                'lua_source': self.lua_script
            },
            'endpoint': 'execute',
        })
        return request

    def use_splash_script2(self, request):
        self.logger.info("PROSES use splash dgn script 2")
        request.meta.update(splash={
            'args': {
                'wait': 2,
                'lua_source': self.lua_script2
            },
            'endpoint': 'execute',
        })
        return request

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

        # mengambil data harga awal bila ada diskon
        data_harga_awal = data.css("strike._3Ge3B::text").get()
        harga_awal = self._parse_harga(data_harga_awal) if data_harga_awal is not None else '-'

        # mengambil data harga
        data_harga = data.css("span._3p5jU::text").get()
        if data_harga is None:
            data_harga = data.css("span._2qwjQ::text").get()
        harga = self._parse_harga(data_harga)

        # mengambil data discount
        pattern_discount = re.compile(r"(\d+%)")
        data_discount = data.css("div._3_5A2 span::text").get()
        discount = pattern_discount.search(data_discount).group(1) if data_discount is not None else '-'

        # mengambil data quantity per unit
        data_qty_unit = data.css("div._3iDvw span::text").get()
        qty_unit = data_qty_unit.split(" / ")[-1] if data_qty_unit is not None else '-'

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
            'qty_unit': qty_unit,
            'username': 'Transmart Carrefour Paris Van Java',
            'link_toko': 'https://www.happyfresh.id/transmart-carrefour-paris-van-java/',
        }
