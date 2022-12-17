#!/usr/bin/env python
# -*- coding: utf-8 -*-
# @Time    : 2022/12/12 20:09
# @Author  : Dominolu
# @File    : futurebroker.py
# @Software: PyCharm

import numpy as np


class FutureBroker():

    def __init__(self, symbols, data, initial_capital, commission_rate, slippage_rate):
        self._symbols = symbols
        self._data = data
        data_length = self._data.shape()[0]
        self._commission_rate = commission_rate
        self._cash = initial_capital
        self._slippage_rate = slippage_rate
        self._positions = np.zeros((data_length, len(self._symbols), 5))  # 仓位 [[[持仓均价,持仓数量,当前价格]]]
        self._trades = None  # 已成交订单 [[[成交时间，成交品种序号，订单价格，订单数量,手续费]]]
        self._equity = np.zeros((data_length,))  # 资产[[资产价值]]
        self._orders = None  # 未成交订单[[品种序号，订单价格，订单数量]]
        self._cash = np.zeros((data_length,))
        self._fees = np.zeros((data_length,))

    @property
    def time(self):
        return self._data[0][0][self._index]

    @property
    def equitys(self):
        """
        :return: 返回当前账户资产价值
        """
        return self.equity

    @property
    def equity(self):
        """
        :return: 返回当前账户资产价值
        """
        return self._equity[self._index]

    @equity.setter
    def equity(self, value):
        self._equity[self._index:] = value

    @property
    def cash(self):
        """
        :return: 返回当前账户现金可用余额
        """
        return self._cash[self._index]

    @cash.setter
    def cash(self, value):
        self._cash[self._index:] = value

    @property
    def fee(self):
        return self._fees[self._index]

    @fee.setter
    def fee(self, value):
        self._fees[self._index] = value

    def results(self):
        return

    # @property
    # def result(self):
    #     return self._retuns[self._index]
    #
    # @result.setter
    # def result(self, value):
    #     self._retuns[self._index:] = value

    @property
    def orders(self):
        if self._orders:
            return self._orders
        else:
            return []

    def add_order(self, *args):
        if self._orders:
            self._orders = np.append(self._orders, args, axis=0)
        else:
            self._orders = np.array([args])

    def del_order(self, index):
        self._orders = np.delete(self._orders, index, axis=0)

    def add_trade(self, *args):
        if self._trades:
            self._trades = np.append(self._trades, args, axis=0)
        else:
            self._trades = np.array([args])

    def get_data(self, symbol: None):
        if symbol:
            return self._data[symbol, self._index, :]
        else:
            return self._data[:, self._index, :]

    def get_posistion_value(self, pos, bar):
        """
        获取当前所有的持仓价值
        （现价-开仓价）*持仓数量
        [交易对,持仓数量,开仓价格,当前价格，持仓价值]
        持仓价值=持仓数量*(当前价格-开仓价格)+abs(数量)*开仓价格
        """

        pos[3] = bar[pos[0], 1]
        pos[4] = pos[1] * (pos[3] - pos[2]) + abs(pos[1]) * pos[2]
        return pos[4].sum()

    def match(self, index, data):
        """
        1.根据收盘价计算持仓价值，
        2.卖单价<high，or 买单价>low 即为撮合成功。
        3.判断是否超卖
        撮合顺序 价格优先
        [交易对，订单价格,订单数量]
        """
        self._index = index
        # 根据上一次的持仓记录和当前的开盘价计算持仓价值
        pos = self._positions[self._index - 1]
        pos_value = self.get_posistion_value(pos, data)
        self.equity = pos_value + self._cash[self._index - 1]
        if self.equity <= 0:
            "持仓亏损大于现金，说明已经爆仓"
            #
            self._positions = self._positions * 0
            self._orders = None
            self.equity = 0
            self._cash = 0
        else:
            orders = list()
            fee = 0
            for i in self.orders:
                s, p, v = i[1]
                t, o, h, l, c, v = data[s, :]
                if (v > 0 and p > l) or (v < 0 and p < h):
                    # 重新计算持仓均价
                    f = abs(p * v) * self._commission_rate
                    pos[s, 2] = (pos[s, 1] * pos[s, 2] + p * v * (1 + self._commission_rate)) / (pos[s, 1] + v)
                    # 更新持仓数量
                    pos[s, 1] = pos[s, 1] + v
                    fee = fee + f
                    self.add_trade(t, s, p, v, f)
                else:
                    # 未撮合成交的放在list中
                    orders.append(i)
            # 订单撮合后重新计算持仓价格
            pos_value = self.get_posistion_value(pos, data)
            #
            if self.equity - pos_value >= 0:
                self._positions = pos
                self._orders = np.array(orders)
                self.cash = self.equity - pos_value
                self.fee = fee
            else:
                self._orders = None
                self.log("余额不足，订单取消")

    def buy(self, **kwargs):
        symbol = kwargs["symbol"]
        price = kwargs["price"]
        volume = kwargs["volume"]
        self.add_order(self._symbols.index(symbol), price, volume)

    def sell(self, **kwargs):
        symbol = kwargs["symbol"]
        price = kwargs["price"]
        volume = kwargs["volume"]
        self.add_order(self._symbols.index(symbol), price, -volume)

    def log(self, msg):
        print(msg)
