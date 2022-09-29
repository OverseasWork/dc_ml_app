# -*- coding: utf-8 -*-
# @Time    : 2021/11/6 11:35 下午
# @Author  : HuangSir
# @FileName: ml_router.py
# @Software: PyCharm
# @Desc: 模型路由

from fastapi import APIRouter

from app.app.api import predict
from app.app.inputs import ReqData

ml_router = APIRouter()

@ml_router.post('/app/v5/score',tags=['v5.0'])
async def score(data:ReqData):
    data = data.dict()
    res = predict(data)
    return res
