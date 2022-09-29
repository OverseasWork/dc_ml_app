# -*- coding: utf-8 -*-
# @Time    : 2022/9/27 23:51
# @Author  : HuangSir
# @FileName: api.py
# @Software: PyCharm
# @Desc:

'''
200 处理成功
201 查无此订单
202 基础数据获取失败
203 通讯录获取失败
204 appList获取失败
205 模型预测失败
206 未知错误
'''

import warnings

warnings.filterwarnings('ignore')
import sys

sys.path.append('..')
import pandas as pd
import lightgbm as lgb
from utils.log import log
from utils.properties import Properties
from utils.utils import load_data
from utils.pre import get_lower_case_name
from app.app.req_dt import QueryDt
from app.app.dt_pre import DtPre
from utils.utils import prob2score

# 读取资源
dbUrl = Properties('conf/dburl.properties').getProperties().get('db_url')
file = 'app/app/data/'
feat = load_data(file + 'feat.txt')
cat_feat = load_data(file + 'cat_feat.txt')
catCodeMap = load_data(file + 'catCodeMap.json')
lgbModel = load_data(file + 'lgbModel.pkl')


def predict(data: dict):
    '''预测结果'''
    # data = {get_lower_case_name(k):v for k,v in data.items()}
    # 获取基础数据
    qd = QueryDt(dbUrl)
    try:
        base_info = qd.base_info(data['customerId'], data['loanAppId'])
    except Exception as error:
        details = f"基础数据获取失败, {data['customerId'], data['loanAppId']},{str(error)}"
        log.logger.warning(details)
        res = {'score': 999,
               'code': 202,
               'msg': '失败',
               "details": details}
        return res

    if base_info.empty:
        res = {
            'score': 999,
            'code': 201,
            'msg': '失败',
            'details': f"无订单记录,查询订单:'{data['loanAppId']}'"
        }
        return res
    else:
        # 同盾数据解析
        base_info = DtPre().td_pre(base_info)
        if data.get('addURL') is None:
            add_info = pd.DataFrame()
        else:
            try:
                add_info = qd.add_info(data['addURL'])
            except Exception as error:
                details = f"下载通讯录信息失败, {data['addURL']},{str(error)}"
                log.logger.warning(details)
                res = {'score': 999,
                       'code': 203,
                       'msg': '失败',
                       "details": details}
                return res
        # --------------------------------------------
        # 获取所有入模数据
        dt = DtPre().get_all_dt(base_info, add_info, data['customerId'], data['loanAppId'])
        # 填充特征
        dt = DtPre().fill_feat(feat, dt)
        # 类别特征编码
        dt = DtPre().cat_code_map(dt, catCodeMap)
        # 预测概率
        # print(dt[feat].dtypes)
        dt[feat] = dt[feat].astype(float)
        prob = lgbModel.predict(dt[feat])
        # 转化分数
        score = prob2score(prob, basePoint=600, PDO=100, odds0=2)
        res = {
            'score': int(score),
            'code': 200,
            'msg': '成功'}
        return res
