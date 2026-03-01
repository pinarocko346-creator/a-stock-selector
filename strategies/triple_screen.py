"""
三重滤网交易系统
基于亚历山大·埃尔德博士的理论
核心：顺大势，逆小势，等突破
"""
import pandas as pd
import numpy as np
from typing import Dict, Optional, Tuple


class TripleScreenSystem:
    """三重滤网交易系统"""

    def __init__(self, data: pd.DataFrame, long_period: int = 5, mid_period: int = 1):
        """
        初始化三重滤网系统

        Args:
            data: 包含OHLCV数据的DataFrame
            long_period: 长周期倍数（相对于中周期），默认5（如果中周期是日线，长周期就是周线）
            mid_period: 中周期倍数，默认1
        """
        self.data = data
        self.long_period = long_period
        self.mid_period = mid_period

    def analyze(self) -> Dict:
        """
        执行三重滤网分析

        Returns:
            包含三层滤网结果的字典
        """
        # 第一层滤网：长周期趋势
        screen1_result = self.first_screen()

        # 第二层滤网：中周期震荡
        screen2_result = self.second_screen()

        # 第三层滤网：短周期突破
        screen3_result = self.third_screen()

        # 综合判断
        signal = self.generate_signal(screen1_result, screen2_result, screen3_result)

        return {
            'screen1': screen1_result,
            'screen2': screen2_result,
            'screen3': screen3_result,
            'signal': signal,
            'description': self.get_description(screen1_result, screen2_result, screen3_result, signal)
        }

    def first_screen(self) -> Dict:
        """
        第一层滤网：长周期趋势判断
        使用MACD斜率判断趋势方向

        Returns:
            {'trend': 'up'/'down'/'neutral', 'macd': float, 'signal': float}
        """
        if len(self.data) < 60:
            return {'trend': 'neutral', 'macd': 0, 'signal': 0, 'reason': '数据不足'}

        # 计算MACD（使用长周期数据）
        # 对数据进行重采样，模拟长周期
        long_data = self._resample_data(self.data, self.long_period)

        if len(long_data) < 30:
            return {'trend': 'neutral', 'macd': 0, 'signal': 0, 'reason': '长周期数据不足'}

        # 计算MACD
        macd_line, signal_line = self._calculate_macd(long_data['close'])

        if len(macd_line) < 2:
            return {'trend': 'neutral', 'macd': 0, 'signal': 0, 'reason': 'MACD计算失败'}

        # 判断MACD斜率
        macd_current = macd_line.iloc[-1]
        macd_prev = macd_line.iloc[-2]
        macd_slope = macd_current - macd_prev

        # 判断趋势
        if macd_slope > 0 and macd_current > signal_line.iloc[-1]:
            trend = 'up'
        elif macd_slope < 0 and macd_current < signal_line.iloc[-1]:
            trend = 'down'
        else:
            trend = 'neutral'

        return {
            'trend': trend,
            'macd': macd_current,
            'signal': signal_line.iloc[-1],
            'slope': macd_slope,
            'reason': f'MACD斜率{"向上" if macd_slope > 0 else "向下"}'
        }

    def second_screen(self) -> Dict:
        """
        第二层滤网：中周期震荡指标
        寻找与长周期趋势相反的入场时机

        Returns:
            {'position': 'oversold'/'overbought'/'neutral', 'rsi': float}
        """
        if len(self.data) < 30:
            return {'position': 'neutral', 'rsi': 50, 'reason': '数据不足'}

        # 计算RSI
        rsi = self._calculate_rsi(self.data['close'], period=14)

        if len(rsi) == 0:
            return {'position': 'neutral', 'rsi': 50, 'reason': 'RSI计算失败'}

        rsi_current = rsi.iloc[-1]

        # 判断超买超卖
        if rsi_current < 30:
            position = 'oversold'  # 超卖
        elif rsi_current > 70:
            position = 'overbought'  # 超买
        else:
            position = 'neutral'

        return {
            'position': position,
            'rsi': rsi_current,
            'reason': f'RSI={rsi_current:.1f}'
        }

    def third_screen(self) -> Dict:
        """
        第三层滤网：短周期突破
        看盘中价格突破

        Returns:
            {'breakout': 'up'/'down'/'none', 'price': float}
        """
        if len(self.data) < 5:
            return {'breakout': 'none', 'price': 0, 'reason': '数据不足'}

        recent = self.data.tail(5)

        # 获取当前价格和前期高低点
        current_price = recent['close'].iloc[-1]
        prev_high = recent['high'].iloc[:-1].max()
        prev_low = recent['low'].iloc[:-1].min()

        # 判断突破
        if current_price > prev_high * 1.005:  # 突破前高0.5%以上
            breakout = 'up'
            reason = f'向上突破前高{prev_high:.2f}'
        elif current_price < prev_low * 0.995:  # 跌破前低0.5%以上
            breakout = 'down'
            reason = f'向下跌破前低{prev_low:.2f}'
        else:
            breakout = 'none'
            reason = '未突破'

        return {
            'breakout': breakout,
            'price': current_price,
            'prev_high': prev_high,
            'prev_low': prev_low,
            'reason': reason
        }

    def generate_signal(self, screen1: Dict, screen2: Dict, screen3: Dict) -> str:
        """
        综合三层滤网，生成交易信号

        核心逻辑：顺大势，逆小势，等突破
        - 做多：长周期上涨 + 中周期超卖 + 短周期向上突破
        - 做空：长周期下跌 + 中周期超买 + 短周期向下突破

        Returns:
            'buy' / 'sell' / 'hold'
        """
        # 做多信号
        if (screen1['trend'] == 'up' and
            screen2['position'] == 'oversold' and
            screen3['breakout'] == 'up'):
            return 'buy'

        # 做空信号（A股不常用，但保留逻辑）
        if (screen1['trend'] == 'down' and
            screen2['position'] == 'overbought' and
            screen3['breakout'] == 'down'):
            return 'sell'

        # 部分满足的情况
        if screen1['trend'] == 'up' and screen2['position'] == 'oversold':
            return 'wait_breakout'  # 等待突破

        if screen1['trend'] == 'up' and screen3['breakout'] == 'up':
            return 'consider_buy'  # 可以考虑买入

        return 'hold'

    def get_description(self, screen1: Dict, screen2: Dict, screen3: Dict, signal: str) -> str:
        """生成描述性文字"""
        desc = []

        # 第一层滤网
        if screen1['trend'] == 'up':
            desc.append("✓ 长周期趋势向上")
        elif screen1['trend'] == 'down':
            desc.append("✗ 长周期趋势向下")
        else:
            desc.append("- 长周期趋势不明")

        # 第二层滤网
        if screen2['position'] == 'oversold':
            desc.append("✓ 中周期超卖")
        elif screen2['position'] == 'overbought':
            desc.append("✗ 中周期超买")
        else:
            desc.append("- 中周期震荡")

        # 第三层滤网
        if screen3['breakout'] == 'up':
            desc.append("✓ 短周期向上突破")
        elif screen3['breakout'] == 'down':
            desc.append("✗ 短周期向下突破")
        else:
            desc.append("- 短周期未突破")

        # 信号
        signal_desc = {
            'buy': '【买入信号】三层滤网全部满足',
            'sell': '【卖出信号】三层滤网全部满足',
            'wait_breakout': '【等待突破】趋势和位置都好，等待突破确认',
            'consider_buy': '【可考虑】趋势向上且已突破，但位置不是最佳',
            'hold': '【持有/观望】条件不满足'
        }

        desc.append(f"\n{signal_desc.get(signal, '观望')}")

        return '\n'.join(desc)

    # ==================== 辅助计算方法 ====================

    def _resample_data(self, data: pd.DataFrame, period: int) -> pd.DataFrame:
        """
        重采样数据，模拟长周期

        Args:
            data: 原始数据
            period: 周期倍数

        Returns:
            重采样后的数据
        """
        if period == 1:
            return data

        # 每period天取一次数据
        resampled = data.iloc[::period].copy()
        return resampled

    def _calculate_macd(self, prices: pd.Series, fast: int = 12, slow: int = 26, signal: int = 9) -> Tuple[pd.Series, pd.Series]:
        """
        计算MACD

        Args:
            prices: 价格序列
            fast: 快线周期
            slow: 慢线周期
            signal: 信号线周期

        Returns:
            (MACD线, 信号线)
        """
        # 计算EMA
        ema_fast = prices.ewm(span=fast, adjust=False).mean()
        ema_slow = prices.ewm(span=slow, adjust=False).mean()

        # MACD线
        macd_line = ema_fast - ema_slow

        # 信号线
        signal_line = macd_line.ewm(span=signal, adjust=False).mean()

        return macd_line, signal_line

    def _calculate_rsi(self, prices: pd.Series, period: int = 14) -> pd.Series:
        """
        计算RSI

        Args:
            prices: 价格序列
            period: 周期

        Returns:
            RSI序列
        """
        delta = prices.diff()
        gain = (delta.where(delta > 0, 0)).rolling(window=period).mean()
        loss = (-delta.where(delta < 0, 0)).rolling(window=period).mean()

        rs = gain / loss
        rsi = 100 - (100 / (1 + rs))

        return rsi


def analyze_with_triple_screen(data: pd.DataFrame) -> Optional[Dict]:
    """
    使用三重滤网系统分析股票

    Args:
        data: 股票数据

    Returns:
        分析结果字典，如果不符合条件返回None
    """
    if len(data) < 60:
        return None

    # 创建三重滤网系统
    system = TripleScreenSystem(data)

    # 执行分析
    result = system.analyze()

    # 只返回有买入信号的结果
    if result['signal'] in ['buy', 'wait_breakout', 'consider_buy']:
        return result

    return None
