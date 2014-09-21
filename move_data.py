#-*- coding: utf-8 -*-
import MySQLdb

if __name__ == '__main__':
  user_lines = [line for line in file('user_name.txt')]
  friend_lines = [line for line in file('friend_list.txt')]

  conn = MySQLdb.connect(user='shinn',db='weibodata', charset='utf8')
  curs = conn.cursor()
  #curs.execute("SET NAMES utf8")
  #curs.execute("SET CHARACTER_SET_CLIENT=utf8")
  #curs.execute("SET CHARACTER_SET_RESULTS=utf8")
  #conn.commit()



  #curs.execute("SELECT u_name FROM userlist WHERE u_id = %d" % 2089092945)
  #s = curs.fetchall()[0][0]
  #s = s.decode('utf-8')
  #print s

  for u_line in user_lines:
    user = u_line.strip().split('\t')
    u_id = int(user[0])
    u_name = user[1].decode('utf-8')

    curs.execute("SELECT u_id FROM userlist WHERE u_id = %d" % u_id)

    if len(curs.fetchall()) != 0:
      continue
    curs.execute("INSERT INTO userlist(u_id, u_name) VALUES ( %d, '%s' )" % (u_id, u_name.encode('utf-8')))
    print u_id, '  ', u_name, '    Done !'
    conn.commit()

  for f_line in friend_lines:
    friend = f_line.strip().split('\t')
    u_id = int(friend[0])
    friend_list = friend[1:]
    curs.execute("SELECT u_id FROM friendlist WHERE u_id = %d" % u_id)
    if len(curs.fetchall()) != 0:
      continue
    print u_id, '    begin to write'
    for f_id in friend_list:
      f_id = int(f_id)
      curs.execute("INSERT INTO friendlist(u_id, f_id) VALUES(%d, %d)" % (u_id, f_id))
    print u_id, '    Done! '
    conn.commit()
      
  conn.close()
