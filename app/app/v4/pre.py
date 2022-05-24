# -*- coding: utf-8 -*-
# @Time    : 2022/5/13 11:28
# @Author  : HuangSir
# @FileName: pre.py
# @Software: PyCharm
# @Desc:数据预处理

import warnings

warnings.filterwarnings('ignore')

import sys

sys.path.append('..')

import re
import pandas as pd
import numpy as np

from conf.log_config import log
from utils.load_utils import load_data
from utils.decorator import log_run_time
from typing import List
from datetime import datetime

from utils.pre_utils import split_rom_ram, split_screen, timestamp_datetime,get_lower_case_name


class BaseInfoPre:
    def __init__(self):
        super().__init__()
        pass

    def base_info_pre(self,base_info:dict):
        # 可用内存
        res = {get_lower_case_name(k):v for k,v in base_info.items()}
        return res


class AddPre:
    def __init__(self):
        """通讯录预处理"""
        super().__init__()
        pass

    def __add_valid(self, row):
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
        elif not bool(re.search(r'10|11|12|15', phone[:2])):
            return 'op'  # 运营商不符

        else:
            return 'ef'  # 有效号码

    def __add_pre(self, addBook: List[dict], apply_date: str):
        '''
        通讯录预处理
        Args:
            addBook: addbook origin
            apply_date: str

        Returns: addbook clear

        '''
        try:
            apply_date = pd.to_datetime(apply_date)
        except:
            apply_date = pd.to_datetime(datetime.now()).date()

        if addBook:
            try:
                add_df = pd.DataFrame(addBook)
            except Exception as err:
                raise_str = f'when {addBook} convert to dataframe happen {err}'
                log.logger.error(raise_str)
                raise ValueError(raise_str)

            # 剔除缺失
            add_df = add_df.dropna(subset=['m', 'u'], axis=0)
            # 去重
            add_df = add_df.drop_duplicates(subset='m')
            # 时间计算
            add_df['updateADD_tday'] = (apply_date - pd.to_datetime(add_df['u'])).dt.days
            # 有效验证
            add_df['validADD'] = add_df.apply(self.__add_valid, axis=1)
            # print(add_df['validADD'].value_counts())
            # 提取变量
            cols = ['updateADD_tday', 'validADD']
            add_df = add_df[cols]
            # 空行
            add_df = add_df.dropna(axis=0)
            return add_df
        else:
            log.logger.warning(f'{addBook} is empty')
            return pd.DataFrame()

    # def __drop_invalid(self,add_df:pd.DataFrame):
    #     '''
    #     删除无效通讯录
    #     Args:
    #         add_df:
    #
    #     Returns:
    #
    #     '''
    #     # 剔除无效通讯录
    #     log.logger.info(f'addBook of origin size {add_df.shape}')
    #     add_df = add_df[add_df.validADD == 1]
    #     log.logger.info(f'drop invalid addBook of size {add_df.shape}')
    #
    #     add_df = add_df[add_df.name.notnull()]
    #     # log.logger.info(f'drop empty name of size {add_df.shape}')
    #
    #     add_df = add_df[add_df.updateADD_tday.notnull()]
    #     # log.logger.info(f'drop empty updateADD_tday of size {add_df.shape}')
    #     return add_df

    @log_run_time
    def add_pre(self, addBook: List[dict], apply_date: str):
        '''
        通讯录预处理
        Args:
            addBook:
            apply_date:

        Returns:

        '''
        add_df = self.__add_pre(addBook, apply_date)
        # add_df = self.__drop_invalid(add_df)
        return add_df


class AppPre:
    def __init__(self):
        """appList 预处理"""
        super().__init__()

        self.path_db = 'app/app/v4/db/'
        self.app_type_base = load_data(f'{self.path_db}applist_type.xlsx')

    # def __search_loans(self, row):
    #     # 关键词APP标签
    #     name, package = row['app_name'], row['app_pack_name']
    #     t1 = re.search(self.loan_app_keys, name.lower().replace(' ', ''))
    #     t2 = re.search(self.loan_app_keys, package.lower().replace(' ', ''))
    #     if bool(t1) or bool(t2):
    #         return 'Kloan'
    #     else:
    #         return 'other'

    def __app_valid(self, row):
        # 有效app验证
        if str(row['updateAPP_tday']) == 'nan' or str(row['install_updateday']) == 'nan':
            return 0
        elif row['updateAPP_tday'] < 0 or row['updateAPP_tday'] > 720 or \
                row['installAPP_tday'] < 0 or row['installAPP_tday'] > 1800:
            return 0
        elif (row['appName'] == row['packageName']
        ) or (str(row['appName']) == 'nan'
        ) or (str(row['packageName']) == 'nan'
        ) or (str(row['appName']).replace(' ', '') == ''):
            return 0
        elif bool(re.search(r'([\u4e00-\u9fa5]+)', row['appName'])):
            return 0
        elif bool(re.search(r'^com\.|^android\.|\.com$|\.product$', row['appName'])):
            return 0
        elif str(row['appName']).count('.') >= 2:
            return 0
        else:
            return 1

    def __app_pre(self, appList: List[dict], apply_date: str):
        '''
        appList预处理
        Args:
            app_df:appList origin

        Returns: app_clear_df

        '''
        try:
            apply_date = pd.to_datetime(apply_date)
        except:
            apply_date = pd.to_datetime(datetime.now()).date()

        if appList:
            try:
                app_df = pd.DataFrame(appList)
            except Exception as err:
                raise_str = f'when {appList} convert to dataframe happen {err}'
                log.logger.error(raise_str)
                raise ValueError(raise_str)

            # 去重
            app_df = app_df.drop_duplicates(subset='packageName')
            # 删除缺失
            app_df = app_df.dropna(subset=['firstInstallTime', 'lastUpdateTime'], axis=0)
            # 日期格式转化
            app_df['firstInstallTime'] = app_df['firstInstallTime'].apply(timestamp_datetime)
            app_df['lastUpdateTime'] = app_df['lastUpdateTime'].apply(timestamp_datetime)
            # 日期差 ---------------
            # 更新距今天数
            app_df['updateAPP_tday'] = (apply_date - app_df['lastUpdateTime']).dt.days
            # 安装距今天数
            app_df['installAPP_tday'] = (
                    apply_date - app_df['firstInstallTime']).dt.days
            # 安装到更新日期差
            app_df['install_updateday'] = (app_df['lastUpdateTime'] - app_df['firstInstallTime']).dt.days
            # 有效性验证
            app_df['validAPP'] = app_df.apply(self.__app_valid, axis=1)
            # 特征筛选
            cols = ['appName', 'packageName', 'updateAPP_tday', 'installAPP_tday', 'install_updateday', 'validAPP']
            app_df = app_df[cols]
            # 匹配类型
            app_df = pd.merge(app_df, self.app_type_base, on='packageName', how='left')
            # 去重
            app_df = app_df.drop_duplicates(subset=['packageName'], ignore_index=True)
            # 填充
            app_df['type'] = app_df['type'].fillna('other')
            return app_df
        else:
            log.logger.error(f'{appList} is empty')
            return pd.DataFrame()

    def __drop_invalid(self, app_df: pd.DataFrame):
        '''
        删除无效applist
        Args:
            app_df:

        Returns:

        '''
        # 剔除无效app
        log.logger.info(f'appList of origin size {app_df.shape}')
        app_df = app_df[app_df['validAPP'] == 1]
        app_df = app_df.dropna(axis=0)
        log.logger.info(f'drop empty  of size  {app_df.shape}')
        return app_df

    @log_run_time
    def app_pre(self, appList: List[dict], apply_date: str):
        '''
        appList 预处理
        Args:
            appList:
            apply_date:

        Returns:

        '''
        app_df = self.__app_pre(appList, apply_date)
        app_df = self.__drop_invalid(app_df)
        return app_df
