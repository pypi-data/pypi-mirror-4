#-*- coding:utf-8 -*-

import unittest

from sphinx_amazonjp_embed import url


class TestURL(unittest.TestCase):


    def test_parse_db_from_url(self):
        u'''
        dp 取ってくるテスト
        '''

        u = 'http://www.amazon.co.jp/%E3%83%91%E3%83%BC%E3%83%95%E3%82%A7%E3%82%AF%E3%83%88Python-PERFECT-SERIES-5-Python%E3%82%B5%E3%83%9D%E3%83%BC%E3%82%BF%E3%83%BC%E3%82%BA/dp/477415539X/ref=sr_1_1?ie=UTF8&qid=1364021936&sr=8-1'

        self.assertEquals('477415539X', url.parse_dp_from_url(u))



    def test_parse_db_from_url_fail(self):
        u'''
        dp 取れないテスト
        '''

        u = 'http://google.com/'

        self.assertEquals(None, url.parse_dp_from_url(u))
