# -*- coding: utf-8 -*-
import random

def tanimoto(v1, v2):
  '''
  tanimoto系数表示距离,'与'除以'或'
  '''
  c1, c2, shr = 0, 0, 0
  for i in range(len(v1)):
    if v1[i] != 0: c1+=1
    if v2[i] != 0: c2+=1
    if v1[i] != 0 and v2[i] != 0: shr+=1
  return 1.0-(float(shr)/(c1+c2-shr))

class Cluster:
  '''
  聚类算法类
  '''
  def __init__(self):
    pass

  def k_cluster(self,rows, distance=tanimoto, k = 4):
    '''
    K 均值聚类算法,算法主要来源于 集体智慧编程,做了关于tanimoto系数的相关调整
    '''
    if distance == tanimoto:
      #如果是tanimoto表示聚类生成的中心点应只有0,1两种
      clusters = [[int(random.random()+0.5) for i in range(len(rows[0]))] for j in range(k)]
    else:
      #非tanimoto型表距离,可使用小数表中心点
      ranges = [(min([row[i] for row in rows]), max([row[i] for row in rows])) for i in range(len(rows[0]))]
      clusters = [[random.random()*(ranges[i][1]-ranges[i][0])-ranges[i][0] for i in range(len(rows[0]))] for j in range(k)]

    lastmatches = None
    for t in range(50):
      bestmatches = [[] for i in range(k)]

      for j in range(len(rows)):
        row = rows[j]
        bestmatch=0
        for i in range(k):
          d1 = distance(clusters[i], row)
          d2 = distance(clusters[bestmatch], row)
          if d1 < d2: bestmatch = i
        bestmatches[bestmatch].append(j)

      if bestmatches == lastmatches: break
      lastmatches = bestmatches

      #重新计算中心点的位置,并注意tanimoto系数时距离只为1,0的情况
      for i in range(k):
        avgs = [0.0]*len(rows[0])
        if len(bestmatches[i]) > 0:
          for rowid in bestmatches[i]:
            for m in range(len(rows[rowid])):
              avgs[m]+=rows[rowid][m]
          for j in range(len(avgs)):
            if distance == tanimoto:
              avgs[j] = int((avgs[j]/len(bestmatches[i]))+0.5)
            else:
              avgs[j]/= len(bestmatches[i])
          clusters[i] = avgs
    print "Iteration times\t: %d" % t
    return bestmatches
