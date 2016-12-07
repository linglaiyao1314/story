# coding=utf-8
import re
import pynlpir
from contextlib import contextmanager

# 通用正则表达式
CHINESE_PATTERN = re.compile(u"[\u4e00-\u9fa5]")
NOT_CHINESE_PATTERN = re.compile(u"[^\u4e00-\u9fa5]")
NUMBER_PATTERN = re.compile(u"[\d]")
UNICODE_PATTERN = re.compile(u"[\u4e00-\u9fa5|\w\W]")


# 过滤出字符串的中文
def parse_chinese(s, to_str):
    filter_list = filter(lambda x: re.match(CHINESE_PATTERN, x), s)
    if to_str:
        return "".join(filter_list)
    return filter_list


# 过滤字符串中非中文串
def parse_others(s, to_str=True):
    filter_list = filter(lambda x: re.match(NOT_CHINESE_PATTERN, x), s)
    if to_str:
        return "".join(filter_list)
    return filter_list


# 过滤字符串中的数字
def get_number(s, to_str=True):
    filter_list = filter(lambda x: re.match(NUMBER_PATTERN, x), s)
    if to_str:
        return "".join(filter_list)
    return filter_list


# 过滤出字符串中所有unicode编码的内容
def parse_unicodestr(s, to_str=True):
    filter_list = filter(lambda x: re.match(UNICODE_PATTERN, x), s)
    if to_str:
        return "".join(filter_list)
    return filter_list


# ===========================
# 分词工具
# ===========================
@contextmanager
def nlpserver():
    pynlpir.open()
    try:
        yield pynlpir
    finally:
        pynlpir.close()


def get_key_words(content, max_words=50, weighted=False):
    """
    :param content: 文本
    :param max_words: 返回关键字数量
    :param weighted: 是否标记每个关键字的权重
    :return: list
    """
    with nlpserver() as keyword_nlp:
        result = keyword_nlp.get_key_words(content, max_words, weighted)
        return result


def segment(content, pos_tagging=True, pos_names='parent', pos_english=True):
    """
    :param content: 文本
    :param pos_tagging:
    :param pos_names:
    :param pos_english:
    :return: list
    """
    with nlpserver() as segment_nlp:
        result = segment_nlp.segment(content,
                                     pos_tagging,
                                     pos_names,
                                     pos_english)
        return result


if __name__ == '__main__':
    print("".join(get_number("'/member/user.aspx?uid=126155'")))
    print("".join(parse_others("2016-12-07 12:58 来源：澎湃新闻")))