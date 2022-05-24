# -*- coding: utf-8 -*-
# @Time    : 2022/5/13 11:34
# @Author  : HuangSir
# @FileName: pre_utils.py
# @Software: PyCharm
# @Desc: 数据预处理
import warnings

warnings.filterwarnings('ignore')
import numpy as np
from conf.log_config import log
import time
import pandas as pd

def split_rom_ram(x: str):
    # 设备存储字段拆分
    x_new = str(x).replace('GB', '').replace('MB', '').replace(' ', '').replace(',', '')
    xl = x_new.split('/')
    try:
        x1, x2 = float(xl[0]), float(xl[1])
        if 'MB' in str(x):
            x1, x2 = round(x1 / 1024, 4), round(x2 / 1024, 4)
    except ValueError as val:
        # print(f'when split {x} happen {str(val)}')
        log.logger.warning(msg=f'when split {x} happen {str(val)}')
        x1, x2 = np.nan, np.nan
    return x1, x2


def split_screen(x: str):
    # 分辨率
    xl = x.split(' ')[0]
    if '_' in xl:
        res = xl.split('_')
    elif '×' in xl:
        res = xl.split('×')
    else:
        res = []
    x1, x2 = np.nan, np.nan
    if res:
        try:
            x1, x2 = int(float(res[0])), int(float(res[1]))
        except ValueError as val:
            # print(res)
            log.logger.warning(msg=f'when split {x} happen {str(val)}')
    else:
        log.logger.warning(msg=f'{x} is empty')
    return x1, x2


def timestamp_datetime(value):
    # 时间格式转化
#     format = '%Y-%m-%d %H:%M:%S'
    format = '%Y-%m-%d'
    value = int(float(value))
    value = time.localtime(value/1000)
    t = time.strftime(format, value)
    t= pd.to_datetime(t)
    return t


def get_lower_case_name(text):
    # 峰坨转换为下划线
    lst = []
    for index, char in enumerate(text):
        if char.isupper() and index != 0:
            lst.append("_")
        lst.append(char)
    return "".join(lst).lower()
