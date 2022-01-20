# Define here the models for your scraped items
#
# See documentation in:
# https://docs.scrapy.org/en/latest/topics/items.html

import scrapy


class InstaparserItem(scrapy.Item):
    user_id = scrapy.Field()
    user_name = scrapy.Field()
    friend_id = scrapy.Field()
    friend_name = scrapy.Field()
    friend_photo = scrapy.Field()
    friend_type = scrapy.Field()
    _id = scrapy.Field()

