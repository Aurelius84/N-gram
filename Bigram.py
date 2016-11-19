from oneGram import Dictionary, DictionarySmooth
from process import calcuBigramWordDistri, getPunciton
from collections import defaultdict
from math import log10


class BigramDictionary(Dictionary):
    """Bigram Dictionary with no smooth

    Args:
        Dictionary:class Dictionary , the dict of words

    """

    def __init__(self):
        # 继承Dictionary子类
        Dictionary.__init__(self)
        self.Bigram = calcuBigramWordDistri()

    def getCount(self, front_word, word):

        return self.Bigram[front_word][word]

    def getPValue(self, front_word, word):
        # 查询二元概率
        # 回退算法
        elpha = 0.2
        if not self.inGram(front_word, word):
            return elpha * Dictionary.getPValue(self, front_word) * Dictionary.getPValue(self, word)

        return self.getCount(front_word, word) / sum(self.Bigram[front_word].values())

    def inGram(self, front_word, word):
        if front_word in self.Bigram and word in self.Bigram[front_word]:
            return True
        return False


class BigramDictionarySmooth(DictionarySmooth):
    """Bigram Dictionary with witten-bell smooth theory

    Args:
        Dictionary:class Dictionary , the dict of words

    """

    def __init__(self):
        # 继承Dictionary子类
        DictionarySmooth.__init__(self)
        self.Bigram = calcuBigramWordDistri()
        self.unknowWordsSetZero()
        self.alpha = self.wittenBellSmoothing()

    def getPValue(self, front_word, word):
        '''
        查询二元概率
        :param front_word: 前向词
        :param word: 当前词
        :return: P(Wi|Wi-1)
        '''
        if not self.inGram(front_word, word):
            return self.alpha
        return self.Bigram[front_word][word]

    def inGram(self, front_word, word):
        '''
        P(Wi|Wi-1)是否存在
        :param front_word: 前向词
        :param word: 后向词
        :return:True or False
        '''
        if front_word in self.Bigram and word in self.Bigram[front_word]:
            return True
        return False

    def unknowWordsSetZero(self, file_name='test.txt'):
        '''
        统计未登录词，放入word_dict中，value = 0
        :param file_name: 测试文件路径
        :return:
        '''
        test_word_dict = calcuBigramWordDistri(file_name)
        unknow_word_cnt = 0
        for front_word in test_word_dict:
            for word in test_word_dict[front_word]:
                if not self.inGram(front_word, word):
                    self.Bigram[front_word][word] = 0.
                    unknow_word_cnt += 1

        print('unknow words count number: {0}, set unknow word value = {1}'.format(
            unknow_word_cnt, 0.0))

    def wittenBellSmoothing(self):
        '''
        witten-Bell平滑
        Pi =
             T/{(N+T)Z}  if Ci == 0
             Ci/(N+T)    if Ci != 0
        :return:
        '''

        # 未登录词数，词量计数，单词数
        Z, N, T = 0, 0, 0
        for front_word in self.Bigram.keys():
            for word in self.Bigram[front_word]:
                if self.Bigram[front_word][word] == 0.:
                    Z += 1
                else:
                    N += self.Bigram[front_word][word]
                    T += 1
        # 平滑处理
        for front_word in self.Bigram.keys():
            for word in self.Bigram[front_word]:
                if self.Bigram[front_word][word] == 0.:
                    self.Bigram[front_word][word] = T / ((N + T) * Z)
                else:
                    self.Bigram[front_word][word] = self.Bigram[
                        front_word][word] / (N + T)
                    T += 1
        print(
            'successfully witten-Bell smoothing! smooth_value:{0}'.format(T / ((N + T) * Z)))
        return (T / ((N + T) * Z))**4


class Bigram(BigramDictionarySmooth):

    '''
    Bigram 类方法
    '''

    def __init__(self):
        BigramDictionarySmooth.__init__(self)
        self.DICT = BigramDictionarySmooth
        self.PUNC = getPunciton()

    def _forwardSplitSentence(self, sentence, word_max_len=5):
        '''
        前向切分
        :param sentence:待切分文本
        :param word_max_len:最大词长
        :return:切分方案列表
        '''
        # 所有可能的切分方案
        split_groups = []
        # 去除空格
        sentence = sentence.strip()
        sentence_len = len(sentence)
        if sentence_len < 2:
            return [[sentence]]
        range_max = [sentence_len,
                     word_max_len][sentence_len > word_max_len]
        # 保存当前二切分结果
        current_groups = []
        single_cut = True
        for i in range(1, range_max)[::-1]:
            # 词典存在子词串，二分切分
            if self.DICT.inDict(self, sentence[:i]) and i != 1:
                current_groups.append([sentence[:i], sentence[i:]])
                single_cut = False
        if single_cut or self.DICT.inDict(self, sentence[1:3]):
            current_groups.append([sentence[:1], sentence[1:]])
        # 词长为2时，为未登录词的概率较大，保留“为词”的可能性
        if sentence_len <= 3:
            current_groups.append([sentence])
        # 对每一个切分，递归组合
        # print(current_groups)
        for one_group in current_groups:
            if len(one_group) == 1:
                split_groups.append(one_group)
                continue
            for child_group in self._forwardSplitSentence(one_group[1]):
                child_group.insert(0, one_group[0])
                # print(child_group)
                split_groups.append(child_group)
        # print(split_groups)
        return split_groups

    def backwardSplitSentence(self, sentence):
        # Todo
        '''
        后向切分
        :param sentence:待切分文本
        :return:切分方案列表
        '''
        pass

    def queryBigram(self, split_words_group):
        '''
        查询各个gram的概率
        :param split_words_group:gram列表
        :return:gram对应概率值key-value
        '''
        gram_p = {}
        gram_p[u'<start>'] = defaultdict(float)
        for split_words in split_words_group[::-1]:
            try:
                for i in range(len(split_words)):
                    if i == 0:
                        gram_p[u'<start>'][split_words[0]] = self.DICT.getPValue(
                            self, u'<start>', split_words[0])
                        continue
                    front_word = split_words[i - 1]
                    word = split_words[i]
                    if front_word not in gram_p:
                        gram_p[front_word] = defaultdict(float)
                    gram_p[front_word][word] = self.DICT.getPValue(self,
                                                                   front_word, word)
            except ValueError:
                print('Failed to query Bigram.')
        return gram_p

    def _maxP(self, sentence, word_max_len=5):
        '''
        计算最大概率的切分组合
        :param sentence: 待切分句子
        :param word_max_len: 最大词长
        :return:最优切分
        '''
       # 获取切分组合
        split_words_group = self._forwardSplitSentence(
            sentence, word_max_len=word_max_len)
        max_p = -99999
        best_split = []
        # 存放已经计算过概率的子序列
        value_dict = {}
        value_dict[u'<start>'] = defaultdict(float)
        for split_words in split_words_group[::-1]:
            words_p = 0
            try:
                for i in range(len(split_words)):
                    word = split_words[i]
                    if i == 0:
                        if word not in value_dict[u'<start>']:
                            value_dict[u'<start>'][word] = log10(
                                self.DICT.getPValue(self, u'<start>', word))
                        words_p += value_dict[u'<start>'][word]
                        # print("<start> {0}: {1}".format(word,value_dict[u'<start>'][word]))
                        continue

                    front_word = split_words[i - 1]
                    if front_word not in value_dict:
                        value_dict[front_word] = defaultdict(float)
                    if word not in value_dict[front_word]:
                        value_dict[front_word][word] = log10(
                            self.DICT.getPValue(self, front_word, word))

                    words_p += value_dict[front_word][word]
                    # print("{0} {1}: {2}".format(front_word,word,value_dict[front_word][word]))
                    if words_p < max_p:
                        break
            except ValueError:
                print("Failed to calculate maxP.")
            if words_p > max_p:
                max_p = words_p
                best_split = split_words
        return best_split

    def segment(self, sentence):
        '''
        分词调用入口
        :param sentence:待切分句子
        :return:切分词序列
        '''
        words = []
        sentences = []
        # 若含有标点，以标点分割
        start = -1
        for i in range(len(sentence)):
            if sentence[i] in self.PUNC:
                sentences.append(sentence[start + 1:i])
                sentences.append(sentence[i])
                start = i
        if not sentences:
            sentences.append(sentence)
        for sent in sentences:
            # print(sent)
            words.extend(self._maxP(sent))
        return words


if __name__ == '__main__':

    bigram = Bigram()
    s = '党的十五大依据邓小平理论和党的基本路线提出的党在社会主义初级阶段经济'
    # s = u'不能结婚的和尚啊'
    print(bigram.segment(s))
