import pandas as pd
import numpy as np
from collections import Counter
import pymongo
from utils.text_process import parse_chinese

DB = "story"
COLLECTION = "acfun_user"

client = pymongo.MongoClient()


class AcfunAnalyser(object):
    def __init__(self):
        self.df = pd.DataFrame(list(client[DB][COLLECTION].find()))

    def run(self):
        name_info_df = self.df[["user_name", "user_info"]]
        word_series = name_info_df[["user_name"]].apply(lambda x: list(i for i in parse_chinese(x)))
        words = word_series["user_name"]
        print(name_info_df[name_info_df["user_name"].str.find("yksoft") > 0])
        print(Counter(words))


if __name__ == '__main__':
    ana = AcfunAnalyser()
    ana.run()
