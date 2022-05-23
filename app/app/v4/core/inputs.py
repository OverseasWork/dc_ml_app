# -*- coding: utf-8 -*-
# @Time    : 2022/5/10 22:36
# @Author  : HuangSir
# @FileName: inputs.py
# @Software: PyCharm
# @Desc: 输入参数校验

from pydantic import BaseModel, Field
from typing import List
from enum import Enum
from .example import ex_base_info, ex_add_book, ex_app_list


class AppList(BaseModel):
    """appList"""
    appName: str = Field(title='APP名', description='app名称,原始值')
    packageName: str = Field(title='包名', description='app包名,原始值')
    firstInstallTime: int = Field(title='首次安装时间', description='首次安装时间,整型时间戳')
    lastUpdateTime: int = Field(title='最近更新时间', description='最近更新时间戳,整型时间戳')


class AddBook(BaseModel):
    """通讯录"""
    m: str = Field(title='电话号码', description='电话号码,原始值')
    # name: str = Field(title='姓名', description='姓名,原始值')
    u: str = Field(title='最近更新时间', description='%Y-%m-%d HH:MM:SS')


class ChildrenNumber(int, Enum):
    __doc__ = '孩子数量'
    THREE = 0
    ZERO = 1
    TWO = 2
    ONE = 3
    OVER_THREE = 4


class MaritalStatus(int, Enum):
    __doc__ = '婚姻枚举'
    MARRIED = 0
    SINGLE = 1
    DIVORCED = 2
    WIDOWED = 3


class BaseInfo(BaseModel):
    """基础信息"""
    age: int = Field(title='年龄', ge=18, lt=60, description='年龄,extract(year FROM age(create_time,ktp_date_of_birth))')
    final_score:int = Field(title='同盾欺诈分',default=-999, description='同盾欺诈分,直接提取原始值,缺失-999')
    marital_status: MaritalStatus = Field(title='婚姻', description="{'MARRIED': 0, 'SINGLE': 1, 'DIVORCED': 2, 'WIDOWED': 3}")
    length: float = Field(title='屏幕长度', default=-999, description='x_equipment.length')
    remaining_memory: float = Field(title='剩余可用存储,/GB', description='剩余可用存储, 单位GB,若是 MB 请预先转化成 GB,精度保留2位,'
                                                                    'round(x.remaining_memory::NUMERIC /(1024*1024*1024),2)')
    install_apply_seconds:float = Field(title='安装到申请时间差', default=-999, description="ROUND(ABS(EXTRACT(EPOCH FROM a.create_time"
                                                                                    " - x.installation_time))/3600)")
    children_number: int = Field(title='孩子数量', description="{'THREE': 0, 'ZERO': 1, 'TWO': 2, 'ONE': 3, 'OVER_THREE': 4}")

class InputData(BaseModel):
    """模型入参"""
    __doc__ = "模型接口入参"
    loan_app_id: int = Field(title='交易订单号', description='唯一标识符', example=2112222057265989)
    apply_date: str = Field(title='申请日期,需要转成 %Y-%m-%d 时间格式,精确到日', example='2021-12-22')

    base_info: BaseInfo = Field(default=..., title='基础信息', example=ex_base_info)
    app_list: List[AppList] = Field(default=..., title='app列表', example=ex_app_list)
    add_book: List[AddBook] = Field(default=..., title='通讯录', example=ex_add_book)
