#!/usr/bin/env python
# -*- coding: utf-8 -*-
# @Time    : 2022/12/6 22:07
# @Author  : Dominolu
# @File    : BacktestEngine.py
# @Software: PyCharm

import numpy as np
from typing import Callable, Dict


# 定义BacktestEngine类
class BacktestEngine:
    def __init__(self, data, strategy_class, strategy_params, start_date, end_date,
                 initial_capital, commission_rate, slippage_rate):
        """
        :param data: {"symbol1":ndarray,"symbol2":ndarray}
        :param strategy_class:
        :param strategy_params:
        :param start_date:
        :param end_date:
        :param initial_capital:
        :param commission_rate:
        :param slippage_rate:
        """

        self.data = data
        self.strategy_class = strategy_class
        self.strategy_params = strategy_params
        self.start_date = start_date
        self.end_date = end_date
        self.initial_capital = initial_capital
        self.commission_rate = commission_rate
        self.slippage_rate = slippage_rate

        self.symbols = list(data.keys())
        # 转存行情数据为 numpy 三维数组
        self.data_matrix = np.array([data[symbol] for symbol in self.symbols])
        # 根据参数初始化策略
        self.strategy = self.strategy_class(**self.strategy_params)

        # 初始化撮合过程中的数据
        data_length = self.data_matrix[0].shape[0]


    def run_strategy(self, strategy, initial_capital, commission_rate, slippage_rate):
        # 计算因子
        factors = strategy.factors(self.data_matrix)
        # 循环遍历数据
        for i in range(data_length):
            # 获取当前时间的行情数据和因子信号
            klines = self.data_matrix[:, i, :]
            signals = factors[:, i]
            # 根据行情数据和因子信号，生成交易订单
            order = strategy.run(klines, signals)
            # 将交易订单写入到 trades 数组中
            self.trades[i] = order
            # 撮合交易订单
            trade = self.match_order(order)
            # 更新持仓数据
            self.positions[i] = self.positions[i - 1] + trade
            # 计算当前时间的账户权益
            # equity_change代表每次交易的收益，也就是成交量 * (成交价 - 持仓均价)
            equity_change = trade * (klines[-1] - self.positions[i - 1] * klines[-1])
            # 账户权益变化 = 每次交易的收益 + 手续费
            equity_change -= trade * commission_rate
            # 账户权益变化 = 账户权益变化 - 滑点损耗
            equity_change -= trade * slippage_rate
            # 更新权益数组
            self.equity[i] = self.equity[i - 1] + equity_change

    def run(self):
        # 根据策略参数，循环实例化策略
        for strategy_params in self.strategy_params:
            # 实例化策略
            strategy = self.strategy_class(**strategy_params)
            # 调用 run_strategy 函数，计算收益率
            performance = self.run_strategy(strategy, self.initial_capital, self.commission_rate, self.slippage_rate)
            # 将收益率数据保存起来
            self.performances.append(performance)
        # 根据收益率，夏普，最大回撤排序
        sorted_performances = sorted(self.performances, key=lambda x: x[1], reverse=True)
        # 输出每个策略参数与相应收益率数据
        for p in sorted_performances:
            print(p[0], p[1])

    def calculate_statistics(self, equity):
        # 计算收益率
        returns = (equity[-1] - equity[0]) / equity[0]
        # 计算夏普比率
        sharpe_ratio = returns / equity.std()
        # 计算最大回撤
        max_drawdown = (equity.cummax() - equity) / equity.cummax()
        # 计算年化收益率
        annualized_return = returns / len(equity) * 252
        # 计算盈利天数
        win_days = equity[equity > equity.shift(1)].count()
        # 计算亏损天数
        lose_days = equity[equity < equity.shift(1)].count()
        # 计算平均盈利
        average_win = equity[equity > equity.shift(1)].mean()
        # 计算平均亏损
        average_lose = equity[equity < equity.shift(1)].mean()
        # 计算盈亏比
        win_loss_ratio = average_win / abs(average_lose)

        return [returns,sharpe_ratio,max_drawdown,annualized_return,win_days,lose_days,average_win,average_lose,win_loss_ratio]

    def match_order(self, orders, high, low):
        # Calculate the value of the current position.
        position_value = (self.positions * (self.data[-1] - self.data[0]) +
                          abs(self.positions) * self.data[0])

        # Combine any unfulfilled orders.
        orders = orders.groupby(["side"]).sum()

        # Loop through all orders.
        for i, row in orders.iterrows():
            # If the order is a buy order and the price is above the high price
            # or if the order is a sell order and the price is below the low
            # price, the order is executed successfully.
            if ((row["side"] == "BUY" and row["price"] > high) or
                    (row["side"] == "SELL" and row["price"] < low)):
                # Update the average price of the position.
                self.position_avg_price = (self.position_avg_price * self.positions +
                                           row["price"] * row["quantity"]) / (self.positions + row["quantity"])

                # Update the number of shares held.
                self.positions += row["quantity"]

        # Update the available cash.
        self.cash = position_value - (self.positions * (self.data[-1] - self.position_avg_price) +
                                      abs(self.positions) * self.position_avg_price)




# def calculate_statistics(self):
#     # 计算策略的年化收益率
#
#     annual_return = (self.returns + 1).prod() ** (252 / len(self.returns)) - 1
#     self.statistics['annual_return'] = annual_return
#
#     # 计算策略的最大回撤
#     max_drawdown = (self.returns + 1).cumprod().cummax().sub(self.returns.cumprod() + 1).max()
#     self.statistics['max_drawdown'] = max_drawdown
#
#     # 计算策略的夏普比率
#     sharpe_ratio = self.returns.mean() / self.returns.std()
#     self.statistics['sharpe_ratio'] = sharpe_ratio
#
#     # 计算策略的风险
#     risk = self.returns.std() * np.sqrt(252)
#     self.statistics['risk'] = risk
#
#
# def calculate_returns(self):
#     # 计算策略的收益率
#     self.returns = np.diff(self.prices) / self.prices[:-1]
#
#     # 撮合交易
#     for i in range(len(self.signals)):
#         if self.signals[i] == 1:
#             # 买入，计算交易成本
#             cost = self.prices[i] * self.commission + self.prices[i] * self.slippage
#             self.returns[i] -= cost
#         elif self.signals[i] == -1:
#             # 卖出，计算交易成本
#             cost = self.prices[i] * self.commission + self.prices[i] * self.slippage
#             self.returns[i] += cost
