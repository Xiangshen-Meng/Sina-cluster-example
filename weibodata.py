# -*- coding: utf-8 -*-
from weibo import APIClient
from pymongo import Connection
import json
import webbrowser
import time
import os

class WeiboData:
  '''
  '''
  def __init__(self, app_key, app_secret, call_back):
    '''
    ��ʼ���������
    '''
    # ����api��֤
    self.client = APIClient(app_key = app_key, app_secret=app_secret, redirect_uri = call_back)
    auth_url = self.client.get_authorize_url()
    webbrowser.open(auth_url)

    code = raw_input('Please input the code: ').strip()
    r = self.client.request_access_token(code)
    access_token = r.access_token
    expires_in = r.expires_in

    self.client.set_access_token(access_token, expires_in)

    print 'INFO\t:Login success!'

    # MongoDB ���ݿ�����
    self.connection = Connection()
    self.db = self.connection.weibo
    self.user_collection = self.db.user_info
    self.friend_collection = self.db.user_friend
    self.follower_collection = self.db.user_follower
    print 'INFO\t:Connect to MongoDB  success!'
    

  def __del__(self):
    pass

  def inital_download_list(self, id, down_list_name = 'download_list.txt'):
    '''
    ��ʼ�������б�ͨ������id�ķ�˿���ɼ������ص�id�б�
    '''
    cursor = self.follower_collection.find({'id': id},{'follower_ids':1})
    id_list = cursor[0]['follower_ids']
    out = open(down_list_name, 'a+')
    for id in id_list:
      out.write('%d\n' % id)
    out.close()

  def load_and_down_list(self, down_list_name = 'download_list.txt'):
    '''
    ���������б��������,��д���ļ�
    '''
    lines = [int(line.strip()) for line in file(down_list_name)]
    user_ids = []
    user_ids.extend(lines)
    for i in range(len(user_ids)):
      id = user_ids[i]
      
      try:
        self.down_user_friend_to_file(id)
      except:
        print 'ERROR\t: Download fail! ID %d' % id
        out = open(down_list_name, 'w')
        for u_id in user_ids[i:]:
          out.write('%d\n' % u_id)
        out.close()
        return
      print 'INFO\t: Done ! ID : %d' % id
    
    
  def down_user_friend_to_file(self, id, insert_type = 'friend', user_file_name = 'user_list.txt', friend_file_name = 'user_friend.txt'):
    '''
    ͨ������id,�������ע�б�,��д��user_file_name��friend_file_name�ļ���,
    ��ʽΪjson��ʽ
    '''
    (user_info_list, user_friend) = self.download_user_friend(id, insert_type)
    out = open(user_file_name, 'a+')
    
    for user in user_info_list:
      user_info = self.change_data(user)
      u_info_str = json.dumps(user_info)
      out.write(u_info_str)
      out.write('\n')
    out.close()

    out = open(friend_file_name, 'a+')
    u_frind_str = json.dumps(user_friend)
    out.write(u_frind_str)
    out.write('\n')
    out.close()

  def insert_user_friend_from_file(self, user_file_name = 'user_list.txt', friend_file_name = 'user_friend.txt'):
    '''
    ͨ����ȡuser_file_name��friend_file_name�ļ�����,
    ����json��ʽ���ݲ�д��mongoDB
    '''
    lines = [line for line in file(user_file_name)]
    for line in lines:
      user_info = json.loads(line)
      user_info = self.change_data(user_info)
      self.insert_user(user_info)

    lines = [line for line in file(friend_file_name)]
    for line in lines:
      user_friend = json.loads(line)
      user_friend = self.change_friend_data(user_friend)
      self.insert_friend(user_friend)

  def change_friend_data(self, friend):
    '''
    ����ֵ�е�Unicode��ʽתΪutf-8
    '''
    if 'friend_ids' in friend:
      ids_str = 'friend_ids'
    elif 'follower_ids' in friend:
      ids_str = 'follower_ids'
    else: return
    user_friend = {'id': friend['id'], ids_str:friend[ids_str]}
    return user_friend

  def download_user_friend(self, id, insert_type = 'friend'):
    '''
    ͨ������id�õ���ע�б�ͷ�˿�б�
    '''
    user_info_list = []
    str_ids = '%s_ids' % insert_type
    user_friend = {'id':id, str_ids :[]}

    next_cur = 0
    j = {}
    while 1:

      if insert_type == 'friend':
        j = self.client.get.friendships__friends(uid = id, cursor=next_cur, count = 200)
      elif insert_type == 'follower':
        j = self.client.get.friendships__followers(uid = id, cursor=next_cur, count = 200)
      else:
        return

      next_cur = int(j['next_cursor'])

      for friend_info in j['users']:
	friend_id = friend_info['id']
	user_friend[str_ids].append(friend_id)
	user_info_list.append(friend_info)
      if next_cur == 0: break

    return user_info_list, user_friend

  def insert_user_friend(self, id, insert_type = 'friend'):
    '''
    ͨ������id�õ���ע�б�ͷ�˿�б�ͬʱ�����û�,�û���ע,�û���˿����
    '''
    (user_info_list, user_friend) = self.download_user_friend(id, insert_type)
    for user_info in user_info_list:
      self.insert_user(user_info)
    self.insert_friend(user_friend, insert_type)
    


  def insert_friend(self, user_friend,insert_type = 'friend'):
    '''
    ��JSON�ṹ��ע���˿��ϵд�����ݿ�
    �ṹ����
    {
       'id': xxxxxxxxxxxxx,
       'friend_ids' or 'follower_ids' : [xxxxxxxxxx, xxxxxxxxxx, xxxxxxxxxxx,...]
    }
    '''
    collection = None
    if insert_type == 'friend':
      collection = self.friend_collection
    else:
      collection = self.follower_collection

    cursor = collection.find_one({'id':user_friend['id']})
    if cursor == None:
      collection.insert(user_friend)
      print "INFO\t:Insert ",user_friend['id'], ' to DB!\tType : %s' % insert_type
    else:
      print "INFO\t:Skip by ",user_friend['id'], '\tType : %s' % insert_type

  def insert_user(self,user_info):
    '''
    ��JSON�ṹ�û���Ϣд�����ݿ�
    �ṹ����
    {
        'id' 			: xxxxxxxxxxxx,
        'screen_name' 		: "xxxxxxxxxxxxx",
        'province' 		: "xxxxx",
        'city' 			: "xx",
        'gender' 		: "m" or "f" or "n",
        'location' 		: "xxxxxxx",
        'followers_count' 	: xxxx,
        'friends_count' 	: xxx,
        'bi_followers_count' 	: xxx
    }
    '''
    cursor = self.user_collection.find_one({'id':user_info['id']})
    if cursor == None:
      print "INFO\t:Insert ",user_info['screen_name'], ' to DB!'
      self.user_collection.insert(user_info)
    #else:
      #print "INFO\t:Skip by ",user_info['screen_name']

  def change_data(self, user):
    '''
    ת������,תΪutf-8����
    '''
    user_info={}
    user_info['id'] = user['id']
    user_info['screen_name'] = user['screen_name'].encode('utf-8')
    user_info['province'] = user['province'].encode('utf-8')
    user_info['city'] = user['city'].encode('utf-8')
    user_info['gender'] = user['gender'].encode('utf-8')
    user_info['location'] = user['location'].encode('utf-8')
    user_info['followers_count'] = user['followers_count']
    user_info['friends_count'] = user['friends_count']
    user_info['bi_followers_count'] = user['bi_followers_count']
    return user_info

  def test(self):
    #self.insert_user_friend(1400220917, insert_type = 'follower')
    #self.inital_download_list(1400220917)
    #self.down_user_friend_to_file(2580858435)
    self.insert_user_friend_from_file()
    #self.load_and_down_list()


