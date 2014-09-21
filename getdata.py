# -*- coding: utf-8 -*-
from weibo import APIClient
import urllib2
import urllib
import httplib
import webbrowser
import time
import os

# 新浪提供 app-key
APP_KEY = '3480707696'
# 新浪提供 app-secret
APP_SECRET = 'a827835fe6c714c2b57edf23532c3675'
# 回调网址用于取code
CALL_BACK = 'http://www.baidu.com'

login_id = '13555992603'
login_psw= 'shinn4135'

# 新浪提供SDK 调用
client = APIClient(app_key = APP_KEY, app_secret=APP_SECRET, redirect_uri = CALL_BACK)

# 用户名和ID字典
user_name = {}

#用户ID和关注用户的ID字典
user_friend = {}

def get_auth():
  '''
  获得认证函数
  以后调用使用:
  client.get.xxx__xx()
  By : Shinn
  '''
  auth_url = client.get_authorize_url()
  webbrowser.open(auth_url)

  code = raw_input('Please input the code: ').strip()
  r = client.request_access_token(code)
  access_token = r.access_token
  expires_in = r.expires_in

  client.set_access_token(access_token, expires_in)

def down_uinfo_from_public():
  '''
  下载用户信息函数
  调用SDK得到当前公共主页发表微薄的信息，得到发表用户的信息，
  并通过用户ID得到其关注的用户的ID
  填充user_name 和user_friend字典
  By : Shinn
  '''
  # 用户名和ID字典
  user_name = {}

  #用户ID和关注用户的ID字典
  user_friend = {}

  js = client.get.statuses__public_timeline()
  for blog_info in js['statuses']:

    u_name = blog_info['user']['screen_name']
    u_id = blog_info['user']['id']

    user_name[u_id] = u_name
    user_friend.setdefault(u_id, [])
    next_cur = 0
    while 1:
      j = client.get.friendships__friends(uid = u_id, cursor = next_cur, count = 200)
      next_cur = int(j['next_cursor'])

      for friend in j['users']:
        friend_id = friend['id']
        user_friend[u_id].append(friend_id)
        user_name[friend_id] = friend['screen_name']

      print next_cur, '\t'
      if next_cur == 0:
        break
    print '######%d#####' % u_id
    print user_friend[u_id]
  print user_name
  return user_name,user_friend

def down_user_follower(u_id):
  u_id = int(u_id)
  user_name = {}
  user_friend = {}

  next_cur = 0
  while 1:
    j = client.get.friendships__followers(uid = u_id, cursor=next_cur, count = 200)
    next_cur = int(j['next_cursor'])

    for friend in j['users']:
      friend_id = friend['id']
      user_friend.setdefault(u_id,[])
      user_friend[u_id].append(friend_id)
      user_name[friend_id] = friend['screen_name']
    if next_cur == 0: break
  write_friend_to_file(user_friend)
  write_user_to_file(user_name)
  print u_id, '   Done'

def down_follower(user_friend):
  down_list = []
  if not os.path.isfile('down_list.txt'):
    down_set = set()
    for (u_id,friend_list) in user_friend.items():
      friend_set = set(friend_list)
      down_set.update(friend_set)
    down_file = open('down_list.txt','w')
    for i in range(len(down_set)):
      down_file.write(down_set.pop())
      down_file.write('\n')
    down_file.close()

  lines = [line for line in file('down_list.txt')]
  down_list.extend([line.strip() for line in lines])

  for i in range(len(down_list)):
    print 'ID : ',down_list[i]
    try:
      down_user_follower(down_list[i])
    except:
      print 'ERROR : Down load ID : %s error' % down_list[i]
      down_file = open('down_list.txt','w')
      for u_id in down_list[i:]:
        down_file.write(u_id)
        down_file.write('\n')
      down_file.close()
      return
    print 'Done One'


def write_user_to_file(user_name, user_file_name = 'user_name.txt'):
  '''
  将user_name字典写入文件
  写入格式:
  user_name:
    UserID \t  Username \n
    xxx    \t  xxx      \n
  By : Shinn
  '''
  user_file = open(user_file_name,'a+')

  for (u_id,u_name) in user_name.items():
    user_file.write(str(u_id))
    user_file.write('\t')
    user_file.write(u_name.encode('utf-8'))
    user_file.write('\n')

  user_file.close()

def write_friend_to_file(user_friend, friend_file_name = 'friend_list.txt'):
  '''
  将user_friend字典写入文件
  写入格式:
  user_friend:
    UserID \n
    xxx    \t  xxx(关注用户的ID) \t  xxx(同上)\n
  By : Shinn
  '''
  friend_file = open(friend_file_name,'a+')

  for (u_id,friends) in user_friend.items():
    friend_file.write(str(u_id))
    for friend in friends:
      friend_file.write('\t')
      friend_file.write(str(friend))
    friend_file.write('\n')

  friend_file.close()


def load_from_file(user_file_name = 'user_name.txt', friend_file_name = 'friend_list.txt'):
  '''
  通过所给文件加载user_name 和user_friend字典
  文件格式件 write_to_file函数描述
  *注* 在数据下载后, 所有的ID 均是数字
  *注* 但写入文件后再次加载则为字符串类型(ID不会进行加减操作所以采用字符串较好,可省去转化操作)
  By : Shinn
  '''
  user_lines = [line for line in file(user_file_name)]
  friend_lines = [line for line in file(friend_file_name)]

  for u_line in user_lines:
    u_line_list = u_line.strip().split('\t')
    user_name[u_line_list[0]] = u_line_list[1].decode('utf-8')

  for f_line in friend_lines:
    f_line_list = f_line.strip().split('\t')
    u_id = f_line_list[0]
    user_friend.setdefault(u_id , [])
    user_friend[u_id].extend(f_line_list[1:])

  return user_name, user_friend

if __name__ == '__main__':
  get_auth()
  #(user_name, user_friend) = down_uinfo_from_public()

  #user_name = {1:u'Ring\u8a69\u5152',2:u'\u9ece\u4e0d\u79bb'}
  #user_friend = {'1':['2','3','4'],'2':['3','4','5']}
  #write_user_to_file(user_name)
  #write_friend_to_file(user_friend)
  #(user_name,user_friend) = load_from_file()
  #down_follower(user_friend)
