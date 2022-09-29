# -*- coding: utf-8 -*-
# @Time    : 2020/10/29 5:08 下午
# @Author  : HuangSir
# @FileName: utils.py
# @Software: PyCharm
# @Desc:

import sys

sys.path.append('..')

import warnings

warnings.filterwarnings('ignore')

import numpy as np
import pandas as pd
import joblib
import json


def prob2score(prob, basePoint=600, PDO=50, odds0=20):
    """
    将概率转化成分数且为正整数
    :param prob: 违约概率
    :param basePoint: 基础评分
    :param PDO:评分倍率
    :param odds0:真实样本好坏比
    :return:
    """
    # 倍率
    factor = PDO / np.log(2)
    # 真实好坏比
    odds = np.log((1 - prob) / prob)
    # 基础分校准
    offset = basePoint - factor * np.log(odds0)
    # 最终得分
    score = factor * odds + offset
    score = score.astype('int')
    return score


def load_data(filename: str):
    if '.txt' in filename:
        with open(filename, 'r') as f:
            dt = f.read().split('\n')
            dt = [i for i in dt if i]
        return dt
    elif '.pkl' in filename:
        dt = joblib.load(filename)
        return dt
    elif '.xlsx' in filename:
        dt = pd.read_excel(filename)
        return dt
    elif '.csv' in filename:
        dt = pd.read_csv(filename)
        return dt
    elif '.json' in filename:
        with open(filename, 'r') as f:
            dt = json.load(f)
        return dt
    else:
        raise ValueError(f'{filename} fail identify filename types')
