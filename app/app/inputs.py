# -*- coding: utf-8 -*-
# @Time    : 2022/9/27 22:31
# @Author  : HuangSir
# @FileName: inputs.py
# @Software: PyCharm
# @Desc:

from pydantic import BaseModel, Field
from datetime import datetime


class ReqData(BaseModel):
    __doc__ = "模型接口请求参数"
    customerId: str = Field(title='客户号',default='123445', description='真实客户号', example='428935')

    loanAppId: str = Field(title='交易订单号',default='202021139494', description='订单号,唯一标识符', example='2207261521389370')

    addURL: str = Field(title='通讯录地址', default=None, description='通讯录S3存储地址',
                        example='https://madfoo3a-prod.s3.eu-central-1.amazonaws.com/CONTACT/1891/202208230128/681891.json')

    appURL: str = Field(title='appList地址', default=None, description='appList S3存储地址',
                        example='https://madfoo3a-prod.s3.eu-central-1.amazonaws.com/INSTALLED_APP/3438/202207261925/673438.json')

    applyTime: str = Field(title='申请时间', default=str(datetime.now()).split('.')[0],
                           description='时间格式,YY-mm-dd HH24:MM:SS 精确到秒', example='2022-09-10 12:30:00')
