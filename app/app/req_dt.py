# -*- coding: utf-8 -*-
# @Time    : 2022/9/28 16:25
# @Author  : HuangSir
# @FileName: req_dt.py
# @Software: PyCharm
# @Desc: 数据请求
import sys

sys.path.append('..')
import warnings
from utils.log import log
from utils.pre import timestamp_datetime
from datetime import datetime

warnings.filterwarnings('ignore')
import pandas as pd
import numpy as np
import requests
from sqlalchemy import create_engine
import json
import re
from app.app.req_sql import QuerySql


class QueryDt(QuerySql):

    def __init__(self, db_url: str):
        '''数据库实例'''
        self.engine = create_engine(db_url)

    def query_dt(self, sql: str):
        """批数据查询,返回dataFrame"""
        with self.engine.connect() as conn:
            dt = pd.read_sql_query(sql=sql, con=conn)
        return dt

    def download_s3(self, s3_url):
        # try:
        text = requests.get(s3_url).text
        dt = pd.DataFrame(json.loads(text))
        return dt
        # except Exception as error:
        #     log.logger.warning(f"下载S3数据失败:{s3_url},详情:{str(error)}")
        #     return pd.DataFrame()

    def base_info(self, customer_id, loan_app_id):
        '''基础数据'''
        base_dt = self.query_dt(self.base_sql(customer_id, loan_app_id))
        lbs_dt = self.query_dt(self.lbs_sql(customer_id, loan_app_id))
        td_dt = self.query_dt(self.td_sql(customer_id, loan_app_id))
        equip_dt = self.query_dt(self.equip_sql(customer_id, loan_app_id))
        # 表关联
        joins = ['customer_id', 'loan_app_id']
        dt = pd.merge(base_dt, lbs_dt, how='left', on=joins)
        dt = pd.merge(dt, td_dt, how='left', on=joins)
        dt = pd.merge(dt, equip_dt, how='left', on=joins)
        dt = dt.fillna(-999)
        return dt

    def add_info(self, add_s3: str):
        dt = self.download_s3(add_s3)
        if not dt.empty:
            # 剔除无用字段
            dt = dt.drop(columns=['r', 'l', 'r', 'd', 'nn', 'c', 'email', 'n'])
            # 去重
            dt = dt.dropna(subset=['m', 'u'], axis=0)
            # 时间计算
            dt['updateADD_tday'] = (datetime.today() - pd.to_datetime(dt['u'])).dt.days
            # 有效验证
            dt['validADD'] = dt.apply(self.__add_valid, axis=1)
            # 剔除时间异常
            dt = dt[dt.validADD != 'ot']
            # 提取变量
            cols = ['updateADD_tday', 'validADD']
            dt = dt[cols]
            # 空行
            dt = dt.dropna(axis=0)
        else:
            dt = pd.DataFrame()
        return dt

    def __add_valid(self,row):
        # 通讯录号码清洗
        phone, updateADD_tday = row['m'], row['updateADD_tday']
        phone = ''.join(filter(str.isdigit, phone.lstrip('+20|0')))
        # 号码为空 或长度不为10
        if not phone or len(phone) != 10:
            return 'lh'  # 长度不符
        # 创建时间
        elif updateADD_tday > 1080 or updateADD_tday < 0:
            return 'ot'  # 时间不符
        # 号码不符合运营商
        elif not bool(re.search('10|11|12|15', phone[:2])):
            return 'op'  # 运营商不符
        else:
            return 'ef'  # 有效号码