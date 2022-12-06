#!/usr/bin/env python
# -*- coding: utf-8 -*-
# @Time    : 2022/12/6 22:13
# @Author  : Dominolu
# @File    : main.py
# @Software: PyCharm



strategy = Strategy(10, 0.01)

# 运行回测引擎
backtest = Backtest(prices, assets, strategy.factors, start_date, end_date)
results = backtest.run()