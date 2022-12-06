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
    def __init__(self, prices: np.ndarray, assets: List[str], strategy: Callable[[np.ndarray, List[str]], np.ndarray],
                 start_date: str, end_date: str):
        self.prices = prices
        self.assets = assets
        self.strategy = strategy
        self.start_date = start_date
        self.end_date = end_date

        # 初始化统计信息
        self.statistics = {}

        # 初始化交易记录
        self.trades = []

    def run(self):
        # 调用策略函数计算交易信号
        signals = self.strategy(self.prices, self.assets)

        # 遍历所有品种
        for i in range(len(self.assets)):
            symbol = self.assets[i]
            signal = signals[:, i]

            # 计算累计收益
            returns = calculate_returns(self.prices[:, i, :], signal)
            # 计算年化收益率
            annual_return = calculate_annual_return(returns, self.start_date, self.end_date)
            # 更新统计信息
            self.statistics[symbol] = {
                "return": returns,
                "annual_return": annual_return,
            }

            # 记录交易记录
            self.trades[symbol] = signal

    def calculate_statistics(self):
        # 计算策略的年化收益率

        annual_return = (self.returns + 1).prod() ** (252 / len(self.returns)) - 1
        self.statistics['annual_return'] = annual_return

        # 计算策略的最大回撤
        max_drawdown = (self.returns + 1).cumprod().cummax().sub(self.returns.cumprod() + 1).max()
        self.statistics['max_drawdown'] = max_drawdown

        # 计算策略的夏普比率
        sharpe_ratio = self.returns.mean() / self.returns.std()
        self.statistics['sharpe_ratio'] = sharpe_ratio

        # 计算策略的风险
        risk = self.returns.std() * np.sqrt(252)
        self.statistics['risk'] = risk

    def calculate_returns(self):
        # 计算策略的收益率
        self.returns = np.diff(self.prices) / self.prices[:-1]

        # 撮合交易
        for i in range(len(self.signals)):
            if self.signals[i] == 1:
                # 买入，计算交易成本
                cost = self.prices[i] * self.commission + self.prices[i] * self.slippage
                self.returns[i] -= cost
            elif self.signals[i] == -1:
                # 卖出，计算交易成本
                cost = self.prices[i] * self.commission + self.prices[i] * self.slippage
                self.returns[i] += cost

