# -*- coding: utf-8 -*-
# @Time    : 2022/5/14 15:16
# @Author  : HuangSir
# @FileName: dfs_feat.py
# @Software: PyCharm
# @Desc:

import sys

sys.path.append('..')

import warnings

warnings.filterwarnings('ignore')
import uuid


import pandas as pd
from conf.log_config import log
from utils.load_utils import load_data
from utils.decorator import log_run_time

import featuretools as ft

class DFSFeat:
    def __init__(self):
        super(DFSFeat, self).__init__()
        self.path_data = 'app/app/v4/data/'
        self.MlFeat = load_data(f'{self.path_data}feat.txt')
        # 通讯录
        self.feat_add = ft.load_features(f'{self.path_data}dfs_add_feat.json')
        self.feat_add = [i for i in self.feat_add if i.get_name() in self.MlFeat]
        # appList
        self.feat_app = ft.load_features((f'{self.path_data}dfs_app_feat.json'))
        self.feat_app = [i for i in self.feat_app if i.get_name() in self.MlFeat]

        # 实体配置
        self.base_config = {
            'entity_id': 'base',
            'index': 'loan_app_id',
            'make_index': False,
            'time_index': None
        }

        self.add_config = {
            'entity_id': 'add',
            'index': 'add_id',
            'variable_types': {
                'validADD': ft.variable_types.Categorical,
                'updateADD_tday': ft.variable_types.Numeric,
            },
            'make_index': False,
            'time_index': None
        }

        self.app_config = {
            'entity_id': 'app',
            'index': 'app_id',
            'variable_types': {
                'appName': ft.variable_types.NaturalLanguage,
                'packageName': ft.variable_types.NaturalLanguage,
                'type': ft.variable_types.Categorical,
                'updateAPP_tday': ft.variable_types.Numeric,
                'install_updateday': ft.variable_types.Numeric,
                'installAPP_tday': ft.variable_types.Numeric
            },
            'make_index': False,
            'time_index': None
        }

    @log_run_time
    def dfs_feat(self, add_df: pd.DataFrame, app_df: pd.DataFrame, base_df: pd.DataFrame):
        # 剔除无效app,检查是否删除
        log.logger.info(f'appList of origin size {app_df.shape}')
        app_df = app_df[app_df.validAPP == 1]
        log.logger.info(f'drop invalid appList of size {app_df.shape}')

        log.logger.info(f'addbook of origin size {add_df.shape}')
        add_df = add_df[add_df.validADD != 'ot']
        log.logger.info(f'drop outerline datetime addbook of size {add_df.shape}')

        # 删除无用变量
        add_df = add_df[['loan_app_id', 'updateADD_tday','validADD']]

        app_df = app_df[['loan_app_id','appName','packageName', 'type', 'updateAPP_tday', 'installAPP_tday', 'install_updateday']]

        # 初始化实体集
        es_add = ft.EntitySet(id=str(uuid.uuid1()))
        es_app = ft.EntitySet(id=str(uuid.uuid1()))

        base_cols = ['loan_app_id']
        es_add = es_add.entity_from_dataframe(dataframe=base_df[base_cols], **self.base_config)
        es_app = es_app.entity_from_dataframe(dataframe=base_df[base_cols], **self.base_config)

        es_add = es_add.entity_from_dataframe(dataframe=add_df, **self.add_config)
        es_app = es_app.entity_from_dataframe(dataframe=app_df, **self.app_config)

        # Adding a Relationship
        relat_add = ft.Relationship(es_add['base']['loan_app_id'], es_add['add']['loan_app_id'])
        relat_app = ft.Relationship(es_app['base']['loan_app_id'], es_app['app']['loan_app_id'])
        # -----------------------
        es_add = es_add.add_relationship(relat_add)
        es_app = es_app.add_relationship(relat_app)
        # 衍生变量加工
        matrix_add = ft.calculate_feature_matrix(features = self.feat_add, entityset=es_add,n_jobs=1)
        matrix_add = matrix_add.reset_index()
        # print(list(matrix_add[[i.get_name() for i in self.feat_add]].to_dict(orient='index').values())[0])

        matrix_app = ft.calculate_feature_matrix(features=self.feat_app, entityset=es_app,n_jobs=1)
        matrix_app = matrix_app.reset_index()
        # print(list(matrix_app[[i.get_name() for i in self.feat_app]].to_dict(orient='index').values())[0])

        matrix = pd.concat([matrix_add, matrix_app], axis=1)
        return matrix
