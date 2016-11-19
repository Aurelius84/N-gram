# -*- coding:utf-8 -*-

"""
@version: 1.0
@author: kevin
@contact: liujiezhang@bupt.edu.cn
@file: oneGram.py
@time: 16/10/7 下午5:11
"""
from process import *


class Dictionary:
    '''
    Dictionary Information and mananger
    '''

    def __init__(self):

        # count train.txt words
        self.word_dict = toWordSet()

        self.N = len(self.word_dict.keys())

    def getPValue(self, word):
        '''
        计算word的频率
        :param word: 词
        :return: 频率的log值
        '''
        if not self.inDict(word):
            return 1.0 / self.N
        return self.word_dict[word] / self.N

    def inDict(self, word):
        '''
        word是否在dict中
        :param word: 词
        :return: True or False
        '''
        return word in self.word_dict

    def totalNum(self):
        return self.N

    def getDict(self):
        return self.word_dict


class DictionarySmooth:
    '''
    Dictionary Information and mananger with witten-bell smooth
    '''

    def __init__(self):

        # count train.txt words
        self.word_dict = wittenBellSmoothing(
            unknowWordsSetZero(toWordSet(), file_name='test.txt'))

        self.N = len(self.word_dict.keys())

    def getPValue(self, word):
        '''
        计算word的频率
        :param word: 词
        :return: 频率的log值
        '''
        return self.word_dict[word]

    def inDict(self, word):
        '''
        word是否在dict中
        :param word: 词
        :return: True or False
        '''
        return word in self.word_dict

    def totalNum(self):
        return self.N

    def getDict(self):
        return self.word_dict


class oneGram(DictionarySmooth):
    '''
    一元模型
    '''

    def __init__(self, split='back'):
        # 继承Dictionary类
        DictionarySmooth.__init__(self)

        self.DICT = Dictionary
        self.words = []
        self.value_dict = {}
        self.seg_dict = {}
        self.split_way = split
        self.PUNC = getPunciton()

    def backwardSplitSentence(self, sentence, word_max_len=5):
        '''
        后向切词
        :param sentence: 待切分文本
        :param word_max_len: 最大词长
        :return: 切分元组列表
        '''
        words = []
        sentence_len = len(sentence)
        range_max = [sentence_len, word_max_len][sentence_len > word_max_len]
        for i in range(range_max - 1):
            words.append((sentence[:i + 1], sentence[i + 1:]))
        return words

    def forwardSplitSentence(self, sentence, word_max_len=5):
        '''
        前向切词
        :param sentence: 待切分文本
        :param word_max_len: 最大词长
        :return: 切分元组列表
        '''
        words = []
        sentence_len = len(sentence)
        range_max = [sentence_len, word_max_len][sentence_len > word_max_len]
        for i in range(range_max - 1):
            words.append((sentence[:-(i + 1)], sentence[-(i + 1):]))
        return words

    def maxP(self, sentence):
        '''
        计算最大切分方案
        :param sentence: 待切分句子
        :return:
        '''
        # 遍历所有切分组合中，找出最大概率切分
        if len(sentence) <= 1:
            return self.DICT.getPValue(self, sentence)
        # 判断切词方向：backward 或 forward
        sentence_split_words = [self.backwardSplitSentence(
            sentence), self.forwardSplitSentence(sentence)][self.split_way != 'back']
        # 记录最大概率值
        max_p_value = 0
        # 储存最大概率下的切分组合
        word_pairs = []
        # 组合概率值
        word_p = 0

        for pair in sentence_split_words:
            p1, p2 = 0, 0

            if pair[0] in self.value_dict:
                p1 = self.value_dict[pair[0]]
            else:
                p1 = self.maxP(pair[0])

            if pair[1] in self.value_dict:
                p2 = self.value_dict[pair[1]]
            else:
                p2 = self.maxP(pair[1])

            word_p = p1 * p2

            if max_p_value < word_p:
                max_p_value = word_p
                word_pairs = pair
        # 在词典中查询当前句对应的频率，不存在时，返回 1/N
        sentence_p_value = self.DICT.getPValue(self, sentence)
        # 不切分概率最大时，更新各值
        if sentence_p_value > max_p_value and self.DICT.inDict(self, sentence):
            self.value_dict[sentence] = sentence_p_value
            self.seg_dict[sentence] = sentence
            return sentence_p_value
        # 某种切分组合概率最大时，更新sentence对应概率，避免后续切分重复计算
        else:
            self.value_dict[sentence] = max_p_value
            self.seg_dict[sentence] = word_pairs
            return max_p_value

    def getSeg(self):
        return self.seg_dict

    def segment(self, sentence):
        '''
        分词调用入口
        :param sentence: 待切分文本
        :return: 最佳切分词列表
        '''
        words = []
        sentences = []
        # 若含有标点，以标点分割
        start = -1
        for i in range(len(sentence)):
            if sentence[i] in self.PUNC and i < len(sentence):
                sentences.append(sentence[start + 1:i])
                sentences.append(sentence[i])
                start = i
        if not sentences:
            sentences.append(sentence)
        # 对每个标点分割的断句进行分词
        for sent in sentences:
            self.maxP(sent)
            words.extend(self.dumpSeg(sent))
        return words

    def dumpSeg(self, sentence):
        '''
        输出分词结果列表
        :param sentence:
        :return:
        '''
        words = []
        if sentence in self.seg_dict:
            pair = self.seg_dict[sentence]
            if isinstance(pair, tuple):
                words.extend(self.dumpSeg(pair[0]))
                words.extend(self.dumpSeg(pair[1]))
            else:
                if pair == sentence:
                    words.append(pair)
                else:
                    words.extend(self.dumpSeg(pair))
        else:
            words.append(sentence)
        return words


if __name__ == '__main__':
    OG = oneGram()
    sentence = '重症肌无力专科医院院长黄再军四川省巴中南江县高级农艺师黄恕[四川省叙永县科协主席吴兆平[四川省剑阁县新华书店农村图书发行股股长甘明[重庆市电影公司送电影下乡流动放映队队长程仕福[重庆市农业科学研究所农艺师张谊模[云南省文山壮族苗族自治州歌舞团演员陆自福[云南省江川县科协副主席罗汉江[云南省第二人民医院主治医师张灿华[贵州省农业厅直属机关党委副书记蒋德方[贵州省文化厅助理巡视员傅汝吉[贵州省委宣传部宣传处处长雷厚礼[西藏自治区话剧团演员边巴[西藏自治区歌舞团副团长顿珠次仁[西藏自治区第二人民医院妇产科主任拉布[陕西人民艺术剧院副院长刘远[西北农业大学副教授宁毓华[陕西省人民医院儿科副主任医师王可胜[甘肃省张掖地区灌溉农业科技中心高级农艺师张保善[甘肃省杂技团演员江小玉[甘肃省兰州医学院第二附属医院儿科副主任魏瑞[宁夏回族自治区银川市科协主席洪维祖[宁夏回族自治区话剧团演员黄精一[宁夏回族自治区银川市第二人民医院副院长赖嘉第[青海花儿艺术团团长马俊[青海省湟中县科技局局长霍成[青海省委宣传部副处级调研员桑映洲[青海省西宁市第一人民医院中医科副主任苟海峰[青海省海北藏族自治州藏医院医务科主任郭巴[新疆维吾尔自治区杂技团演员安尼瓦尔'
    print(OG.segment(sentence))
