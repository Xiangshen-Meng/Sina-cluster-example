# -*- coding: utf-8 -*-
from weibodata import WeiboData
from weibo_analysis import WeiboAnalysis

user_name = {}
user_friend = {}
appear_list = {}
user_friend_matrix = {}

APP_KEY = '3480707696'
APP_SECRET = 'a827835fe6c714c2b57edf23532c3675'
CALL_BACK = 'http://www.baidu.com'

if __name__ == '__main__':
  #weibo = WeiboData(APP_KEY, APP_SECRET, CALL_BACK)
  #weibo.insert_user_friend(2643213241)
  #weibo.test()
  weibo = WeiboAnalysis()
  #weibo.get_top_mapreduce()
  weibo.get_top_100()
  #weibo.get_follower_mapreduce()
  weibo.init_user_list()
  weibo.init_top_matrix()
  weibo.cluster_top()

