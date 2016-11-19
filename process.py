# !--*-- coding:utf-8 --*--
"""
@version: 1.0
@author: kevin
@contact: liujiezhang@bupt.edu.cn
@file: oneGram.py
@time: 16/10/7 下午4:21
"""

from __future__ import absolute_import, division, print_function
from collections import defaultdict
from sklearn.externals import joblib
from random import random


def splitCorpus(train=0.9, fileName='199801.txt'):
    '''
    随机切分语料
    :param train: 训练集比率
    :param fileName: 原始语料路径
    :return:
    '''
    train_file = open('train.txt', 'wb')
    test_file = open('test.txt', 'wb')

    with open(fileName, 'rb') as f:
        for line in f:
            if random() <= train:
                train_file.write(line)
            else:
                test_file.write(line)
    train_file.close()
    test_file.close()
    print('successfully to split corpus by train = %f test = %f' %
          (train, 1 - train))


def toWordSet(file_name='train.txt', is_save=False, save_file='wordSet.pkl'):
    '''
    获取词典
    :param file_name: 文本路径
    :param is_save: 是否保存
    :param save_file: 保存路径
    :return:
    '''
    word_dict = defaultdict(float)

    with open(file_name, 'rb') as f:
        for line in f:
            content = line.decode('gbk').strip().split()
            # 去掉第一个词“19980101-01-001-001/m”
            for word in content[1:]:
                word_dict[word.split(u'/')[0]] += 1
    if is_save:
        # 保存wordSet以复用
        joblib.dump(word_dict, save_file)

    print("successfully get word dictionary!")
    print("the total number of words is:{0}".format(len(word_dict.keys())))
    return word_dict


def getPunciton(file_name='199801.txt', is_save=False, save_file='punction.pkl'):
    '''
    获取标点
    :param file_name: 文本路径
    :param is_save: 是否保存
    :param save_file: 保存路径
    :return:
    '''

    punction = set(['[', ']'])
    with open(file_name, 'rb') as f:
        for line in f:
            content = line.decode('gbk').strip().split()
            # 去掉第一个词“19980101-01-001-001/m”
            for word in content[1:]:
                if word.split(u'/')[1] == u'w':
                    punction.add(word.split(u'/')[0])
    if is_save:
        # punction
        joblib.dump(punction, save_file)
    print("the total number of punction is:{0}".format(len(punction)))
    return punction


def unknowWordsSetZero(word_dict, file_name='test.txt'):
    '''
    统计未登录词，放入word_dict中，value = 0
    :param word_dict:
    :param file_name:
    :return:
    '''
    test_word_dict = toWordSet(file_name)
    unknow_word_cnt = 0
    for test_word in test_word_dict:
        if test_word not in word_dict:
            word_dict[test_word] = 0.
            unknow_word_cnt += 1

    print('unknow words count number: {0}, set unknow word value = {1}'.format(
        unknow_word_cnt, 0.0))
    return word_dict


def plusOneSmoothing(word_dict):
    '''
    加一平滑
    :param word_dict:
    :return:
    '''
    total_cnt = sum(word_dict.values())
    words_cnt = len(word_dict.keys())
    re_word_dict = word_dict.copy()
    print('words number: {0}, words total count: {1}'.format(
        words_cnt, total_cnt))

    for word in word_dict:
        re_word_dict[word] = (word_dict[word] + 1.0) / (total_cnt + words_cnt)

    print('successfully plus one smoothing!')

    return re_word_dict


def wittenBellSmoothing(word_dict):
    '''
    witten-Bell平滑
    Pi =
         T/{(N+T)Z}  if Ci == 0
         Ci/(N+T)    if Ci != 0
    :param word_dict:
    :return:
    '''

    # 未登录词数，词量计数，单词数
    Z, N, T = 0, 0, 0
    for key in word_dict:
        if word_dict[key] == 0.:
            Z += 1
        else:
            N += word_dict[key]
            T += 1
    # 平滑处理
    re_word_dict = word_dict.copy()
    for key in word_dict:
        if word_dict[key] == 0.:
            re_word_dict[key] = T / ((N + T) * Z)
        else:
            re_word_dict[key] = word_dict[key] / (N + T)
    print('successfully witten-Bell smoothing!')

    return re_word_dict


def calcuBigramWordDistri(file_name='train.txt', is_save=False, sava_file='BigramWordDistri.pkl'):
    '''
    计算2-gram分布
    :param file_name:
    :param is_save:
    :param sava_file:
    :return:
    '''

    wordDistri = defaultdict(dict)
    wordDistri[u'<start>'] = defaultdict(float)

    with open(file_name, 'rb') as f:
        for line in f:

            content = line.decode('gbk').strip().split()
            if not content or len(content) == 1:
                continue
            # 删除'19980101-01-001-001/m'
            del content[0]
            word_len = len(content)

            # 不用标记是否为句尾词
            for i in range(word_len - 1):
                word_pos = content[i].split(u'/')
                # 判断当前词是否第一次出现
                if not wordDistri[word_pos[0]]:
                    wordDistri[word_pos[0]] = defaultdict(float)
                # 标点后的第一词也算做句首词
                back_word_pos = ['', content[i + 1].split(u'/')][i != 0]
                if i == 0 or back_word_pos[1] == u'w':
                    wordDistri[u'<start>'][word_pos[0]] += 1
                else:
                    wordDistri[word_pos[0]][back_word_pos[0]] += 1
    # gram计数
    N = 0
    for key in wordDistri:
        N += len(wordDistri[key].keys())
    if is_save:
        joblib.dump(wordDistri, sava_file)

    print("The total number of bigram is : {0}.".format(N))
    return wordDistri


def forwardMaxCut(ustring, word_set, word_max_len=5):
    '''
    前向最大切词
    :param ustring: 待切词文本
    :param word_set: 词典
    :param word_max_len: 最大词长
    :return: 词列表
    '''
    wordList = []
    if not ustring:
        return wordList

    while ustring:
        sentence_len = len(ustring)
        if sentence_len < word_max_len:
            word_max_len = sentence_len

        for i in range(word_max_len, 0, -1):
            if ustring[:i] in word_set or i == 1:
                wordList.append(ustring[:i])
                ustring = ustring[i:]
                break
            else:
                i -= 1

    return wordList


def backwardMaxCut(ustring, word_set, word_max_len=5):
    '''
    后向最大切词
    :param ustring: 待切分文本
    :param word_set: 词典
    :param word_max_len: 最大词长
    :return: 词切分列表
    '''

    wordList = []
    if not ustring:
        return wordList

    while ustring:
        sentence_len = len(ustring)
        if sentence_len < word_max_len:
            word_max_len = sentence_len

        for i in range(word_max_len, 0, -1):
            if ustring[-i:] in word_set or i == 1:
                wordList.append(ustring[-i:])
                ustring = ustring[:-i]
                break
            else:
                i -= 1

    return wordList[::-1]


# if __name__ == '__main__':
#     splitCorpus(train=0.9)
    # punc = getPunciton()
    # print(punc)
#     train_word_dict = __toWordSet()
#     word_dict = __unknowWordsSetZero(train_word_dict)
#     word_dict_by_plusOne = plusOneSmoothing(word_dict)
#     word_dict_by_wittenBell = wittenBellSmoothing(word_dict)
#     print('origin\t plus One\t WittenBell\t')
#     for word in word_dict:
#         print('{0}: {1}\t {2}\t {3}'.format(
#             word, word_dict[word], word_dict_by_plusOne[word], word_dict_by_wittenBell[word]))
    # __splitCorpus()
    # __toWordSet()
    # calcuBigramWordDistri()
    # calcuTriramWordDistri()
    # 词典
    # WORDSET = joblib.load('wordSet.pkl')

    # Bigram
    # BIGRAMWORDDISTRI = joblib.load('BigramWordDistri.pkl')

    # ustring = u"我是北京邮电大学的一名研究生，喜欢编程，生于1993年，毕业于2016年！！"
    # for word in forwardMaxCut(ustring):
    #     print(word)
    # for word in backwardMaxCut(ustring):
    #     print(word)
