# -*- coding: utf-8 -*-
# @Time    : 2022/5/11 11:49
# @Author  : HuangSir
# @FileName: test.py
# @Software: PyCharm
# @Desc:

import requests
import json
import pandas as pd
import numpy as np
from datetime import datetime


url = 'http://0.0.0.0:8004/app/v1/score'
headers = {'Content-Type': 'application/json','accept':'application/json'}

mlfeat = ['busi_id','apply_date','sex','age','brands','marry','usable_ram','usable_memory','resolution',
          'add_book','app_list']

result_list  = []
# test = pd.read_excel('valid_data.xlsx')
test = pd.read_csv('valid_data.csv')
test['apply_date'] = test['apply_date'].astype('str')

t0,n = datetime.now(),len(test)

for busi_id in test['busi_id'].tolist():
    n-=1
    dt = test[test.busi_id==busi_id][mlfeat].to_dict(orient='index')
    dt = list(dt.values())[0]
    apply_date = dt['apply_date']
    base_info = {k:dt[k] for k in ['sex','age','brands','marry','usable_ram','usable_memory','resolution']}
    add_book = eval(dt['add_book'])
    app_list = eval(dt['app_list'])
    request_data = {'busi_id':busi_id,'apply_date':apply_date,
                    'base_info':base_info,'add_book':add_book,'app_list':app_list}

    # if busi_id == '1020220409101331000163821':
    #     print(json.dumps(request_data,ensure_ascii=False))
    #     break

    res = requests.post(url=url, data = json.dumps(request_data), headers=headers).json()
    if n%500==0:
        print(f'cost time is {(datetime.now()-t0).seconds},ramain request {n}')
        t0 = datetime.now()
    col = ['CUST_ID','ID_TYPE','CUSTOMER_NO','apply_date','PLAN_STATUS','PENALTY_DAYS','TARGET']
    result = test[test.busi_id==busi_id][col].to_dict(orient='index')
    result = list(result.values())[0]

    result = {**res,**result}
    result_list.append(result)

pd.DataFrame(result_list).to_excel('valid_result.xlsx',index=False)

