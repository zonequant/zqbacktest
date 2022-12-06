#!/usr/bin/env python
# -*- coding: utf-8 -*-
# @Time    : 2022/12/6 22:13
# @Author  : Dominolu
# @File    : Strategy.py
# @Software: PyCharm


class Strategy:
    def __init__(self, *args, **kwargs):
        self.params = args
        self.kwparams = kwargs

    def factors(self, prices: np.ndarray) -> np.ndarray:
        # 解析策略参数
        window = self.params[0]
        threshold = self.params[1]

        # 计算移动平均线
        ma = np.mean(prices, axis=0)

        # 计算交易信号，当价格上穿移动平均线时买入，下穿时卖出
        signals = np.zeros(ma.shape)
        signals[ma > ma[0] * (1 + threshold)] = 1
        signals[ma < ma[0] * (1 - threshold)] = -1

        return signals