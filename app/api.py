# -*- coding: utf-8 -*-
# @Time    : 2020/10/29 8:49 下午
# @Author  : HuangSir
# @FileName: api.py
# @Software: PyCharm
# @Desc:

import warnings
warnings.filterwarnings('ignore')

from .routers import risk_router_init
from fastapi import FastAPI


description = """
* 客户评分越高风险越低,评分范围:\t300~850, \t **999**:\t表示评分异常  \t 模型接口入参详情:\t**ReqData**<br>

|  **返回码**   | **说明**  |
|  :---  | :---  |
| 200 | 处理成功 |
| 201 | 查无此订单 |
| 202 | 基础数据获取失败 |
| 203 | 通讯录获取失败 |
| 204 | appList获取失败 |
| 205 | 模型预测失败 |
| 206 | 未知错误 |

"""


def create_app():
    app = FastAPI(title='新客风险评分评级模型',
                  description=description)
    risk_router_init(app)
    return app
