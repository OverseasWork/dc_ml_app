# -*- coding: utf-8 -*-
# @Time    : 2022/9/29 01:38
# @Author  : HuangSir
# @FileName: dt_pre.py
# @Software: PyCharm
# @Desc: 数据预处理

import warnings
warnings.filterwarnings('ignore')
import sys
sys.path.append('..')

import json
import re
import pandas as pd
import numpy as np
from typing import List
import copy

class TongDun:
    '''同盾数据预处理'''
    def __cure_eval(self,x):
        try:
            x = json.loads(x)
        except:
            # print(x)
            x = np.nan
        return x

    def __info_analysis(self,x):
        res = {}
        # IP地址检测
        res['true_ip_address'] = x.get('address_detect', {}).get('true_ip_address', np.nan)
        # 设备信息
        device_info = x.get('device_info', {})
        # cpu
        res['cpu_frequency'] = device_info.get('cpuFrequency', np.nan) / 1000
        # 当地信息
        res['allow_mock_location'] = device_info.get('allowMockLocation', np.nan)
        # 电池温度
        res['battery_temp'] = device_info.get('batteryTemp', np.nan)
        # 网络环境
        res['network_type'] = device_info.get('networkType', np.nan)
        # 屏幕亮度
        res['brightness'] = device_info.get('brightness', np.nan)
        # 手机信息
        telephonyInfos = device_info.get('telephonyInfos', [])
        # 手机卡数
        res['telephony_infos'] = len(telephonyInfos)
        # 运营商
        res['phone_type'], res['sim_operator'] = np.nan, np.nan
        for tl in telephonyInfos:
            if 'phoneType' in list(tl.keys()):
                res['phone_type'] = str(tl.get('phoneType')).lower().replace(' ', '')
                res['sim_operator'] = str(tl.get('simOperator')).lower().replace(' ', '')
                break
        return res

    def __antifraud(self,x):
        res = {}
        res['final_score'] = x.get('final_score', np.nan)
        res['final_decision'] = x.get('final_decision', np.nan)
        risk_items = x.get('risk_items', [])
        if risk_items:
            pattern = r'[\u4e00-\u9fa5]'
            items_score = {re.sub(pattern, '', i.get('risk_name', 'nan')): i.get('score', np.nan) for i in risk_items}

            items_len = {re.sub(pattern, '', i.get('risk_name', 'nan')) + '_len': len(i.get('risk_detail', [])) for i in
                         risk_items}

            res = {**res, **items_score, **items_len}
        return res

    def __td_analyze(self,x):
        x = self.__cure_eval(x)
        if str(x) != 'nan':
            INFOANALYSIS = x.get('INFOANALYSIS', {})
            ANTIFRAUD = x.get('ANTIFRAUD', {})
            info_anl_dt = self.__info_analysis(INFOANALYSIS)
            anti_dt = self.__antifraud(ANTIFRAUD)
            result = {**info_anl_dt, **anti_dt}
        else:
            result = {}
        return result

    def td_analyze(self,dt:pd.DataFrame):
        res = self.__td_analyze(dt['result'].values[0])
        res['customer_id'] = dt['customer_id'].values[0]
        res['loan_app_id'] = dt['loan_app_id'].values[0]
        res = pd.DataFrame([res])
        return res

class AddSelfFeat:
    '''通讯录衍生变量'''

    def self_cal(self,df: pd.DataFrame, seq_bins: List[int], seq_var: str, seq_group: str = None):
        """
        时间切片及类型
        df: 数据框
        seq_bins:序列切片，[0,1,5,15,30,60,120,180,360,np.inf]
        seq_var:序列变量,必须是数值类型
        seq_group:分组变量， 类别变量，能穷举
        """
        if df.empty:
            return pd.DataFrame()
        labels = seq_bins[1:]
        # total 每个切片
        total_cut = pd.cut(x=df[seq_var], bins=seq_bins, include_lowest=True, labels=labels)

        total_df = pd.value_counts(total_cut)  # 每个切片总数
        cols = ['total']
        if seq_group:
            # 序列组别
            df[seq_group] = df[seq_group].astype('str')
            for seq_type in df[seq_group].unique():
                cols.append(seq_type)
                tmp_df = df.loc[df[seq_group] == seq_type, seq_var]
                tmp_cut = pd.cut(x=tmp_df, bins=seq_bins, include_lowest=True, labels=labels)
                tmp_df = pd.value_counts(tmp_cut)  # 统计每个组别的样本量
                total_df = pd.concat([total_df, tmp_df], axis=1)
            # 重置表头
            total_df.columns = cols
        else:
            total_df = pd.DataFrame(total_df)
            total_df.columns = ['total']
        # 索引并排序
        total_df.sort_index(inplace=True)
        # 累计求和
        total_cumsum = total_df.cumsum()
        total_cumsum.columns = ['sum_' + str(i) for i in total_df.columns]

        result_df = pd.concat([total_df, total_cumsum], axis=1)
        # 总占比,累计占比
        cols = copy.deepcopy(result_df.columns.tolist())
        for col in cols:
            if col == 'sum_total':
                result_df['sum_total_rate'] = round(result_df['sum_total'] / max(result_df['sum_total']), 2)
            elif col != 'total' and 'sum' not in str(col):
                #             组别切片与总切片比
                result_df[col + '_rate'] = result_df.apply(lambda row: -999 if row['total'] == 0
                else round(row[col] / row['total'], 2), axis=1)
                #             组别切片比率 与 组别平均比率 比
                avg_rate = max(result_df['sum_' + col]) / max(result_df['sum_total']) if max(
                    result_df['sum_total']) != 0 else 0
                avg_rate = avg_rate if avg_rate != 0 else avg_rate + 0.001
                result_df[col + '_lift'] = result_df.apply(lambda row: round(row[col + '_rate'] / avg_rate, 2
                                                                             ) if row[col + '_rate'] != -999 else -999,
                                                           axis=1)

            elif 'sum' in str(col) and col != 'sum_total':
                #             组别累计增率与总增率 比
                result_df[col + '_total_rate'] = result_df.apply(lambda row: -999 if row['sum_total'] == 0
                else round(row[col] / row['sum_total'], 2), axis=1)
                #             组别增率
                result_df[col + '_rate'] = result_df.apply(lambda row: -999 if max(result_df[col]) == 0
                else round(row[col] / max(result_df[col]), 2), axis=1)
                # 组别增率 与 总增率差异
                result_df[col + '_ks'] = result_df.apply(
                    lambda row: round(row[col + '_rate'] - row['sum_total_rate'], 2)
                    if row[col + '_rate'] != -999 else -999, axis=1)
                # 拉平宽表 -------------------------------
        result_df.index = [str(i) + 'D' for i in result_df.index]
        res = result_df.stack().reset_index()
        res['cols'] = seq_var + '_' + seq_group + '_' + res['level_0'].astype('str') + '_' + res['level_1'].astype(
            'str')
        res = res[['cols', 0]].T
        res.columns = [i.replace('.0', '').replace('inf', 'all') for i in res[res.index == 'cols'].values.tolist()[0]]
        res = res[res.index == 0]
        return res

    def self_add_feat(self,add_df,customer_id,loan_app_id):
        add_df = add_df[add_df.validADD == 'ef']
        res = pd.DataFrame()
        res['customer_id'] = customer_id
        res['loan_app_id'] = loan_app_id
        df2 = self.self_cal(df=add_df, seq_bins=[0, 3, 5, 7, 30, np.inf],
                            seq_var='updateADD_tday', seq_group='validADD')
        res = pd.concat([res, df2], axis=1)
        return res


class DtPre:
    '''数据预处理'''
    def td_pre(self,base_dt:pd.DataFrame):
        '''同盾数据解析'''
        td_df = TongDun().td_analyze(base_dt)
        # base_dt = pd.concat([base_dt,td_df],axis=1)
        base_dt = pd.merge(base_dt,td_df,how='left',on=['customer_id','loan_app_id'])
        return base_dt

    def get_all_dt(self,base_dt,add_df,customer_id,loan_app_id):
        base_dt = self.td_pre(base_dt)
        if not add_df.empty:
            add_dt = AddSelfFeat().self_add_feat(add_df,customer_id,loan_app_id)
            # dt = pd.concat([base_dt,add_dt],axis=1)
            dt = pd.merge(base_dt,add_dt,how='left',on=['customer_id','loan_app_id'])
            # print(dt)
        else:
            dt = base_dt
        return dt

    def fill_feat(self,ml_feat:list,dt:pd.DataFrame):
        # 入模特征填充
        fil_cols = list(set(ml_feat)-set(dt.columns))
        for col in fil_cols:
            dt[col] = -999
        dt = dt.fillna(-999)
        return dt

    def cat_code_map(self,dt:pd.DataFrame,catCodeMap:dict):
        # 入模变量编码
        for col in catCodeMap.keys():
            dt[col] = dt[col].apply(lambda x:catCodeMap[col].get(x,-999))
        return dt