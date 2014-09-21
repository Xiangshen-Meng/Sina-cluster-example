# -*- coding: utf-8 -*-
from pymongo import Connection
from pymongo.code import Code
from cluster import Cluster
import pymongo

class WeiboAnalysis:
  '''
  微博信息分析类
  '''
  def __init__(self, connectDB = True):
    '''
    初始化相关变量及连接数据库
    '''
    self.top_hundred = {}
    self.top_hundred_list = []
    self.user_list = []
    self.top_hundred_matrix = []
    self.clus = Cluster()
    if connectDB == True:
      self.connection = Connection()
      self.db = self.connection.weibo
      self.user_collection = self.db.user_info
      self.friend_collection = self.db.user_friend
      self.follower_collection = self.db.user_follower
      self.top_rank = self.db.top_rank

  def __def__(self):
    pass

  def init_user_list(self):
    '''
    读取数据库填充user_list数组内容
    '''
    results = self.friend_collection.find()
    for result in results:
      self.user_list.append(int(result['id']));
    print "INFO\t: Inital user_list done. %d ids has been found." % len(self.user_list)

  def init_top_matrix(self):
    '''
    通过top 和 user_list进行生成关注关系的矩阵,形式如下:
    用户id在user_list中的位置--> 1   2   3   4   5   6  7  ...
    1                            0   1   0   1   1   0  1
    2                            1   0   1   0   0   0  0
    3                            0   0   0   0   0   1  1
    关注用1表示,不关注用0
    ^
    |
    被关注者id在top_hundred_list中的位置（top中的用户)
    '''
    top_num = len(self.top_hundred_list)
    user_num = len(self.user_list)

    #初始化相关变量,并将top_hundred_matrix矩阵全部填充为0
    self.top_hundred_matrix = [[] for i in range(top_num)]
    for i in range(top_num):
      self.top_hundred_matrix[i] = [0 for j in range(user_num)]

    print "INFO\t: Begin to inital top 100 matrix."
    for j in range(user_num):
      id = self.user_list[j]
      res = self.friend_collection.find_one({"id":id})
      friends =  res["friend_ids"]
      for i in range(top_num):
        if self.top_hundred_list[i] in friends:
          self.top_hundred_matrix[i][j] = 1
    print "INFO\t: Top matrix done. Top number : %5d\t\tUser number : %5d" % (top_num, user_num)

  def get_top_mapreduce(self):
    '''
    使用MongoDB中的mapreduce功能自动生成关于所有用户关注对象的频度统计写入top_rank集合中
    '''
    map = Code(open('gettopMap.js','r').read())
    reduce = Code(open('gettopReduce.js','r').read())
    
    print "INFO\t: Begin to MapReduce ..."
    results = self.friend_collection.map_reduce(map, reduce, "top_rank")
    print "INFO\t: Has been written to ", results.full_name

  def get_follower_mapreduce(self):
    '''
    不使用，意义不大
    '''
    map = Code(open('getfollowerMap.js','r').read())
    reduce = Code(open('getfollowerReduce.js','r').read())
  
    print "INFO\t: Begin to MapReduce ..."
    results = self.friend_collection.map_reduce(map, reduce, "top_follower", scope = {'idList':self.top_hundred.keys()})
    print "INFO\t: Has been written to ", results.full_name

  def get_top_100(self):
    '''
    查询并排序得出前100用户的信息,同时写入top_hundred字典中,字典以id作为键
    '''
    results = self.top_rank.find().sort('value', direction = pymongo.DESCENDING)

    for result in results[:100]:
      id = int(result['_id'])
      name = self.user_collection.find_one({'id':id},fields = {'screen_name':1})['screen_name']
      
      self.top_hundred[id] = {}
      self.top_hundred[id]['name'] = name
      self.top_hundred[id]['follower_num'] = int(result['value']['count'])
    self.top_hundred_list = list(self.top_hundred.keys())
    print "INFO\t: Get top 100 Done."

    for (id,info) in sorted(self.top_hundred.items(), key = lambda x:x[1],reverse = True):
      print "%-15s \t Count: %d" % (info['name'],info['follower_num'])

  def cluster_top(self):
    '''
    对top_hundred_matrix矩阵所得到的信息进行聚类分析
    '''
    res = self.clus.k_cluster(self.top_hundred_matrix, k = 5)
    for i in range(len(res)):
      clus = res[i]
      print "Group %d \t" % i
      print "#"*50
      for id in clus:
        print self.top_hundred[self.top_hundred_list[id]]['name']


