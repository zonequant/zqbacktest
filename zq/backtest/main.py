#!/usr/bin/env python
# -*- coding: utf-8 -*-
# @Time    : 2022/12/6 22:13
# @Author  : Dominolu
# @File    : main.py
# @Software: PyCharm



# 定义多品种行情数据、策略类、策略参数范围、起止日期、现金、手续费率和滑点
data = {
  'AAPL': prices_data,
  'GOOG': prices_data,
  'MSFT': prices_data
}
strategy_class = MovingAverageCrossStrategy
strategy_params = {
  'short_window': range(10, 20),
  'long_window': range(30, 40)
}
start_date = '2010-01-01'
end_date = '2018-12-31'
initial_capital = 10000.0
commission_rate = 0.001
slippage_rate = 0.001

# 使用字典来传递参数
params = {
  'data': data,
  'strategy_class': strategy_class,
  'strategy_params': strategy_params,
  'start_date': start_date,
  'end_date': end_date,
  'initial_capital': initial_capital,
  'commission_rate': commission_rate,
  'slippage_rate': slippage_rate
}

# 使用字典中的参数来构造 BacktestEngine
engine = BacktestEngine(**params)
