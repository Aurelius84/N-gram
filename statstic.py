#-*- coding:utf-8 -*-

"""
@version: 1.0
@author: kevin
@contact: liujiezhang@bupt.edu.cn
@file: stastic.py
@time: 16/11/5 下午5:10
"""
from __future__ import division
from oneGram import oneGram
import sys
from Bigram import Bigram
from process import splitCorpus, forwardMaxCut, backwardMaxCut, toWordSet


class statstic(oneGram, Bigram):
    '''
    calculate the accuracy of the model
    '''

    def __init__(self, Ngram='oneGram', test_file='test.txt', encode_type='gbk'):
        # 继承分词方法类
        if Ngram.lower() == 'onegram':
            oneGram.__init__(self)
            self.Ngram = oneGram
        else:
            Bigram.__init__(self)
            self.Ngram = Bigram

        self.test_file = test_file
        self.encode_type = encode_type
        # 原始词量
        self.origin_total_count = 0.
        # 正确分词量
        self.segmen_true_count = 0.
        # 错误分词量
        self.segmen_false_count = 0.
        # 总分词量
        self.segmen_total_count = 0.
        self.word_set = toWordSet()
        self.n = 0.

    def recall(self):
        # 召回率
        return self.segmen_true_count / self.origin_total_count

    def accuracy(self):
        # 准确率
        return self.segmen_true_count / self.segmen_total_count

    def run(self):

        with open(self.test_file, 'rb') as f:
            total_lines = len(f.readlines())
            process_tag = '#'
            line_num = 0
            process = 0.
        sys.stdout.write(str(int(process * 100)) +
                         '% ||' + process_tag + '->' + "\r")
        with open(self.test_file, 'rb') as f:
            for line in f:
                line_num += 1
                # 去除pos后的词列表
                words = []
                sentence = u''
                line_cont = line.decode(self.encode_type).strip().split()
                # 去除句首标记
                if len(line_cont) < 2:
                    continue
                del line_cont[0]
                for word_pos in line_cont:
                    word = word_pos.split(u'/')[0]
                    if word[0] == '[':
                        words.append(word[0])
                        words.append(word[1:])
                    elif word[-1] == ']':
                        words.append(word[-1])
                        words.append(word[:-1])
                    else:
                        words.append(word)
                    sentence += word
                # 分词，统计
                # print(sentence)
                self.count(words, sentence)

                if line_num / total_lines - 0.014 > process:
                    process = line_num / total_lines
                    process_tag += '#'
                    sys.stdout.write(str(int(process * 100)) +
                                     '% ||' + process_tag + '->' + "\r")
                    sys.stdout.flush()
        print(self.segmen_false_count)
        print(self.segmen_true_count)
        print(self.segmen_total_count)
        print(self.origin_total_count)
        assert self.segmen_total_count == self.segmen_false_count + self.segmen_true_count

    def count(self, words, sentence):
        assert len(words) >= 1
        # 调用分词器
        segment_words = self.Ngram.segment(self, sentence)
        self.segmen_total_count += len(segment_words)
        self.origin_total_count += len(words)
        # 正确分词个数
        true_cnt = 0
        for word in segment_words:
            if word == '':
                continue
            if word in words:
                true_cnt += 1
        self.segmen_true_count += true_cnt
        self.segmen_false_count += (len(segment_words) - true_cnt)

if __name__ == '__main__':
    splitCorpus()
    one_stt = statstic(Ngram='biGram')
    one_stt.run()
    print('召回率为:{0}'.format(one_stt.recall()))
    print('准确率为:{0}'.format(one_stt.accuracy()))
    print('F值为:{0}'.format(2 * one_stt.accuracy() *
                           one_stt.recall() / (one_stt.accuracy() + one_stt.recall())))

    # bi_stt = statstic(Ngram='Bigram')
    # bi_stt.run()
    # print(bi_stt.recall())
    # print(bi_stt.accuracy())
