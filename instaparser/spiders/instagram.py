import json
import re

import scrapy
from scrapy.http import HtmlResponse
from instaparser.items import InstaparserItem


class InstaSpider(scrapy.Spider):
    name = 'instagram'
    allowed_domains = ['instagram.com']
    start_urls = ['https://www.instagram.com/']
    inst_login_link = 'https://www.instagram.com/accounts/login/ajax/'
    inst_login_name = 'user'
    inst_login_pwd = 'password'
    parse_users = ['shdvor_vbg', 'sdfg.trr']
    friends_url = 'https://i.instagram.com/api/v1/friendships/'

    def parse(self, response: HtmlResponse):
        csrf = self.fetch_csrf_token(response.text)
        yield scrapy.FormRequest(
            self.inst_login_link,
            method='POST',
            callback=self.login,
            formdata={'username': self.inst_login_name, 'enc_password': self.inst_login_pwd},
            headers={'X-CSRFToken': csrf}
        )

    def login(self, response: HtmlResponse):
        j_body = response.json()
        if j_body.get('authenticated'):
            for parse_user in self.parse_users:
                yield response.follow(f'/{parse_user}',
                                      callback=self.user_data_parse,
                                      cb_kwargs={'username': parse_user}
                                      )

    def user_data_parse(self, response: HtmlResponse, username):

        user_id = self.fetch_user_id(response.text, username)
        url_followers = f'{self.friends_url}{user_id}/followers/?count=12&search_surface=follow_list_page'
        url_following = f'{self.friends_url}{user_id}/following/?count=12'

        yield response.follow(url_followers,
                              callback=self.user_followers_parse,
                              headers={'User-Agent': 'Instagram 155.0.0.37.107'},
                              cb_kwargs={'username': username, 'user_id': user_id})

        yield response.follow(url_following,
                              callback=self.user_following_parse,
                              headers={'User-Agent': 'Instagram 155.0.0.37.107'},
                              cb_kwargs={'username': username, 'user_id': user_id})

    def user_followers_parse(self, response: HtmlResponse, username, user_id):
        j_data = response.json()
        next_max_id = j_data.get('next_max_id')
        if next_max_id:
            url_followers = f'{self.friends_url}{user_id}/followers/?count=12&max_id={next_max_id}&search_surface=follow_list_page'
            yield response.follow(url_followers,
                                  callback=self.user_followers_parse,
                                  headers={'User-Agent': 'Instagram 155.0.0.37.107'},
                                  cb_kwargs={'username': username, 'user_id': user_id})

        users = j_data.get('users')
        for user in users:
            item = InstaparserItem(
                user_id=user_id,
                user_name=username,
                friend_id=user.get('pk'),
                friend_name=user.get('username'),
                friend_photo=user.get('profile_pic_url'),
                friend_type='follower'

            )
            yield item

    def user_following_parse(self, response: HtmlResponse, username, user_id):
        j_data = response.json()
        next_max_id = j_data.get('next_max_id')
        if next_max_id:
            url_following = f'{self.friends_url}{user_id}/following/?count=12&max_id={next_max_id}'
            yield response.follow(url_following,
                                  callback=self.user_following_parse,
                                  headers={'User-Agent': 'Instagram 155.0.0.37.107'},
                                  cb_kwargs={'username': username, 'user_id': user_id})

        users = j_data.get('users')
        for user in users:
            item = InstaparserItem(
                user_id=user_id,
                user_name=username,
                friend_id=user.get('pk'),
                friend_name=user.get('username'),
                friend_photo=user.get('profile_pic_url'),
                friend_type='following'

            )
            yield item

    def fetch_csrf_token(self, text):
        ''' Get csrf-token for auth '''
        matched = re.search('\"csrf_token\":\"\\w+\"', text).group()
        return matched.split(':').pop().replace(r'"', '')

    def fetch_user_id(self, text, username):
        try:
            matched = re.search(
                '{\"id\":\"\\d+\",\"username\":\"%s\"}' % username, text
            ).group()
            return json.loads(matched).get('id')
        except:
            return re.findall('\"id\":\"\\d+\"', text)[-1].split('"')[-2]
