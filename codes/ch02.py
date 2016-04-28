﻿#encoding:UTF-8

##########################################################################
##一、来自bit.ly的1.usa.gov数据
##1、用存Python代码对时区进行计数
##		a、数据中不完全含有tz
##		b、获取前10位时区及其计数值
##		c、fillna函数替换缺失值NA，而未知值通过布尔型数组索引加以替换
##2、统计浏览器情况；
##3、统计操作系统情况；
##4、根据时区和操作系统系统列表进行分组；
##	a、获取时区和操作系统列表分组；
##	b、获取最常出现的前10的时区；
##	c、绘制堆积条形图；

import json

path = 'D:/Desktop/Python/pydata-book-master/ch02/usagov_bitly_data2012-03-16-1331923249.txt'
open(path).readline()
records = [json.loads(line) for line in open(path)]
records[0]
records[0]['tz']

#time_zones = [rec['tz'] for rec in records]
#数据中不完全含有tz
time_zones = [rec['tz'] for rec in records if 'tz' in rec]

def get_counts(sequence):
    counts = {}
    for x in sequence:
        if x in counts:
            counts[x] += 1
        else:
            counts[x] = 1
    return counts

from collections import defaultdict
def get_counts2(sequence):
    counts = defaultdict(int) #所有的值均会被初始化为0
    for x in sequence:
        counts[x] += 1
    return counts

counts = get_counts(time_zones)

#获取前10位时区及其计数值
def top_counts(count_dict , n =10):
    value_key_pairs = [(count,tz) for tz, count in count_dict.items()]
    value_key_pairs.sort()
    return value_key_pairs[-n:]
    
top_counts(counts)


#用pandas对时区进行计数

from pandas import DataFrame, Series
import pandas as pd ; 
import numpy as np
import json

path = 'D:/Desktop/Python/pydata-book-master/ch02/usagov_bitly_data2012-03-16-1331923249.txt'
records = [json.loads(line) for line in open(path)]

frame = DataFrame(records)
tz_counts = frame['tz'].value_counts()

##fillna函数替换缺失值NA，而未知值通过布尔型数组索引加以替换
clean_tz = frame['tz'].fillna('Missing')
clean_tz[clean_tz ==''] = 'Unknown'
tz_counts = clean_tz.value_counts()
tz_counts[:10].plot(kind='barh',rot=0)

#去除缺失值NA
results = Series([x.split()[0] for x in frame.a.dropna()])
results.value_counts()[:8]

#获取非空值得数据集
cframe = frame[frame.a.notnull()]

#获取操作系统数据集
operating_system = np.where(cframe['a'].str.contains('Windows'),'Windows','Not Windows')

#根据tz对数据进行分组排序
by_tz_os = cframe.groupby(['tz',operating_system])
agg_counts = by_tz_os.size().unstack().fillna(0)

indexer = agg_counts.sum(1).argsort()
indexer[:10]

count_subset = agg_counts.take(indexer)[-10:]
count_subset

count_subset.plot(kind='barh',stacked = True)
normed_subset = count_subset.div(count_subset.sum(1),axis=0)
normed_subset.plot(kind='barh',stacked=True)

##############################################################################################
#二、MovieLens 1M数据集
#1、制作透视图，关联数据源（电影点评数据、电影数据、用户数据）；
#2、过滤评分数据不够250条的电影；
#3、统计女性观众喜欢的电影，并进行降序排序；
#4、计算评分分歧；

import pandas as pd
unames = ['user_id','gender','age','occupation','zip']
mnames = ['movie_id','title','genres']
users = pd.read_table('D:\\Desktop\\Python\\pydata-book-master\\ch02\\movielens\\users.dat',sep='::',header=None,names=unames)

rnames = ['user_id','movie_id','rating','timestamp']
ratings = pd.read_table('D:\\Desktop\\Python\\pydata-book-master\\ch02\\movielens\\ratings.dat',sep='::',header=None,names=rnames)

mnames = ['movie_id','title','genres']
movies = pd.read_table('D:\\Desktop\\Python\\pydata-book-master\\ch02\\movielens\\movies.dat',sep='::',header=None,names = mnames)

data = pd.merge(pd.merge(ratings,users),movies)

#按性别计算每部电影的平均得分
mean_ratings = data.pivot_table('rating',index='title',cols='gender',aggfunc='mean')


#2、过滤评分数据不够250条的电影
ratings_by_title = data.groupby('title').size()
active_titles = ratings_by_title.index[ratings_by_title >= 250]

mean_ratings = mean_ratings.ix[active_titles]

top_female_ratings = mean_ratings.sort_index(by='F',ascending=False)

#4、计算评分分歧；
mean_ratings['diff'] = mean_ratings['M'] - mean_ratings['F']
sorted_by_diff = mean_ratings.sort_index(by='diff')


#根据电影名称分组的得分数据的标准差
rating_std_by_title = data.groupby('title')['rating'].std()

#根据active_titles进行过滤
rating_std_by_title = rating_std_by_title.ix[active_titles]

#根据值对Series进行降序排序
rating_std_by_title.order(ascending=False)[:10]



##############################################################################################
#三、1880-2010年间全美婴儿姓名
#1、按性别和年度统计除总出生数
#	a、利用groupby或pivot_table在year和sex级别上进行数据聚合；
#	b、获取sex、year组合的前1000个名字；
#
#2、分析命名趋势
#3、评估命名多样性的增长
#	a、统计前1000个名字在总出生人数中的比例
#	b、按年度统计密度表
#	
#4、“最后一个字母”的变革
#	a、男孩女孩名字中各个末字母的比例；
#	b、各年出生的男孩中名字以d/n/y结尾的人数比例
#	c、变成女孩子名字的男孩名字