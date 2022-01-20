# Define your item pipelines here
#
# Don't forget to add your pipeline to the ITEM_PIPELINES setting
# See: https://docs.scrapy.org/en/latest/topics/item-pipeline.html


# useful for handling different item types with a single interface
from pymongo import MongoClient
from scrapy.pipelines.images import ImagesPipeline
import scrapy

class InstaparserPipeline:

    def __init__(self):
        client = MongoClient('localhost', 27017)
        self.mongobase = client.instagram_scrapy

    def process_item(self, item, spider):
        collection = self.mongobase[spider.name]
        if not collection.find_one(item):
            collection.insert_one(item)
        return item

class InstaparserPhotosPipeline(ImagesPipeline):
    def get_media_requests(self, item, info):
        if item['friend_photo']:
            try:
                yield scrapy.Request(item['friend_photo'])
            except Exception as e:
                print(e)

    def file_path(self, request, response=None, info=None, *, item):
        folder_name = item['user_name'].replace('/', '_')
        folder_friend_type = item['friend_type']
        image = item['friend_name']
        return f'{folder_name}/{folder_friend_type}/{image}.jpg'