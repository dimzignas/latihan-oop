# -*- coding: utf-8 -*-

# Define your item pipelines here
#
# Don't forget to add your pipeline to the ITEM_PIPELINES setting
# See: https://docs.scrapy.org/en/latest/topics/item-pipeline.html
from common.database import Database


class MongodbPipeline(object):
    collection_name = 'products'

    def close_spider(self, spider):
        Database.CLIENT.close()

    def process_item(self, item, spider):
        if item['nama_produk'] is not None:
            query_result = Database.find_one(self.collection_name, {'link_produk': item['link_produk']}, {'_id': 1})
            if query_result is not None:
                item['_id'] = query_result['_id']
            Database.update(self.collection_name, {'link_produk': item['link_produk']}, item)
        return item


class ScrapyOlshopPipeline(object):
    def process_item(self, item, spider):
        return item
