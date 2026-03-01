"""
13个买点策略实现
基于道氏理论、威科夫理论、波浪理论的技术分析
"""
import pandas as pd
import numpy as np
from typing import List, Dict, Tuple


class BuyPointAnalyzer:
    """13个买点分析器"""

    def __init__(self, data: pd.DataFrame):
        """
        初始化分析器

        Args:
            data: 包含OHLCV数据的DataFrame，列名为['open', 'high', 'low', 'close', 'volume']
        """
        self.data = data
        self.signals = []

    def analyze_all_buy_points(self) -> List[str]:
        """分析所有13个买点，返回符合条件的买点列表"""
        buy_points = []

        # 底部反转结构的买点（1-4）
        if self.check_2b_structure():
            buy_points.append("买点1: 2B结构")

        if self.check_head_shoulder_right():
            buy_points.append("买点2: 底部头肩右肩")

        if self.check_second_test():
            buy_points.append("买点3: 二次测试")

        if self.check_strength_appear():
            buy_points.append("买点4: 强势出现")

        # 形态突破和中继的买点（5-8）
        if self.check_trendline_volume_breakout():
            buy_points.append("买点5: 趋势线+量能密集区突破")

        if self.check_trendline_keypoint_breakout():
            buy_points.append("买点6: 趋势线+关键点位突破")

        if self.check_trendline_pattern_breakout():
            buy_points.append("买点7: 趋势线+形态突破")

        if self.check_major_pattern_breakout():
            buy_points.append("买点8: 大形态突破")

        # 上涨趋势中的买点（9-13）
        if self.check_fibonacci_pullback():
            buy_points.append("买点9: 波段回踩(斐波那契)")

        if self.check_spring_in_box():
            buy_points.append("买点10: 箱体弹簧")

        if self.check_multi_timeframe_resonance():
            buy_points.append("买点11: 多周期共振")

        if self.check_support_resistance_swap():
            buy_points.append("买点12: 支撑压力互换")

        if self.check_trend_sharp_drop():
            buy_points.append("买点13: 趋势急跌")

        return buy_points

    # ==================== 底部反转结构的买点（1-4）====================

    def check_2b_structure(self) -> bool:
        """
        买点1: 2B结构（云聪版）
        条件：
        1. 有完整的五浪下跌
        2. 在第四浪或第五浪有小形态（平台/三角形）
        3. 最后一跌是大阴线跌破平台
        4. 第二根K线是大阳线马上拉起
        """
        if len(self.data) < 30:
            return False

        recent = self.data.tail(10)

        # 检查最后两根K线
        if len(recent) < 2:
            return False

        last_2 = recent.tail(2)
        k1 = last_2.iloc[0]  # 倒数第二根
        k2 = last_2.iloc[1]  # 最后一根

        # 倒数第二根是大阴线（跌幅>3%）
        k1_drop = (k1['close'] - k1['open']) / k1['open']
        is_big_bearish = k1_drop < -0.03

        # 最后一根是大阳线（涨幅>3%）
        k2_rise = (k2['close'] - k2['open']) / k2['open']
        is_big_bullish = k2_rise > 0.03

        # 最后一根收盘价高于倒数第二根开盘价（快速拉起）
        quick_recovery = k2['close'] > k1['open']

        # 检查前期是否有下跌趋势
        ma20 = recent['close'].rolling(20).mean()
        has_downtrend = ma20.iloc[-1] < ma20.iloc[0] if len(ma20) > 1 else False

        return is_big_bearish and is_big_bullish and quick_recovery and has_downtrend

    def check_head_shoulder_right(self) -> bool:
        """
        买点2: 底部头肩的右肩（50%位置）
        条件：价格回调到前一个下跌波段的50%位置
        """
        if len(self.data) < 60:
            return False

        recent = self.data.tail(60)

        # 找到最近的低点
        low_idx = recent['low'].idxmin()
        low_price = recent.loc[low_idx, 'low']

        # 找到低点之前的高点
        before_low = recent.loc[:low_idx]
        if len(before_low) < 10:
            return False

        high_price = before_low['high'].max()

        # 计算50%回调位
        retracement_50 = low_price + (high_price - low_price) * 0.5

        # 当前价格在50%回调位附近（±2%）
        current_price = recent['close'].iloc[-1]
        near_50_percent = abs(current_price - retracement_50) / retracement_50 < 0.02

        # 检查是否有反转K线信号（如长下影线）
        last_k = recent.iloc[-1]
        lower_shadow = last_k['close'] - last_k['low']
        body = abs(last_k['close'] - last_k['open'])
        has_reversal_signal = lower_shadow > body * 2

        return near_50_percent and has_reversal_signal

    def check_second_test(self) -> bool:
        """
        买点3: 二次测试
        条件：刺破前低但很快收回，伴有明确K线信号
        """
        if len(self.data) < 30:
            return False

        recent = self.data.tail(30)

        # 找到前期低点
        lows = recent['low'].rolling(5).min()

        # 检查最后几根K线
        last_5 = recent.tail(5)

        # 是否刺破前低
        prev_low = lows.iloc[-6] if len(lows) > 6 else lows.min()
        pierced_low = last_5['low'].min() < prev_low

        # 是否快速收回（最后一根收盘价高于前低）
        recovered = last_5['close'].iloc[-1] > prev_low

        # 是否有长下影线或反包
        last_k = last_5.iloc[-1]
        lower_shadow = last_k['close'] - last_k['low']
        body = abs(last_k['close'] - last_k['open'])
        has_signal = lower_shadow > body * 1.5

        return pierced_low and recovered and has_signal

    def check_strength_appear(self) -> bool:
        """
        买点4: 强势出现（威科夫概念）
        条件：在底部形态中轴以上，出现带量阳K线
        """
        if len(self.data) < 40:
            return False

        recent = self.data.tail(40)

        # 计算底部形态的中轴（最近20天的中位价）
        box_high = recent['high'].tail(20).max()
        box_low = recent['low'].tail(20).min()
        mid_line = (box_high + box_low) / 2

        # 最后一根K线
        last_k = recent.iloc[-1]

        # 在中轴以上
        above_midline = last_k['close'] > mid_line

        # 是阳线
        is_bullish = last_k['close'] > last_k['open']

        # 涨幅>2%
        rise_pct = (last_k['close'] - last_k['open']) / last_k['open']
        strong_rise = rise_pct > 0.02

        # 成交量放大（大于前5天平均的1.5倍）
        avg_volume = recent['volume'].tail(6).iloc[:-1].mean()
        volume_surge = last_k['volume'] > avg_volume * 1.5

        return above_midline and is_bullish and strong_rise and volume_surge

    # ==================== 形态突破和中继的买点（5-8）====================

    def check_trendline_volume_breakout(self) -> bool:
        """
        买点5: 趋势线 + 量能密集区的突破
        """
        if len(self.data) < 60:
            return False

        recent = self.data.tail(60)

        # 简化判断：检查是否突破前期高点且成交量放大
        high_20 = recent['high'].tail(21).iloc[:-1].max()
        current_close = recent['close'].iloc[-1]

        # 突破前期高点
        breakout = current_close > high_20

        # 成交量放大
        avg_volume = recent['volume'].tail(21).iloc[:-1].mean()
        volume_surge = recent['volume'].iloc[-1] > avg_volume * 1.8

        return breakout and volume_surge

    def check_trendline_keypoint_breakout(self) -> bool:
        """
        买点6: 趋势线 + 关键点位的突破
        """
        if len(self.data) < 60:
            return False

        recent = self.data.tail(60)

        # 检查是否突破重要压力位（如前期高点）
        key_resistance = recent['high'].tail(30).max()
        current_close = recent['close'].iloc[-1]

        # 突破关键点位
        breakout = current_close > key_resistance * 1.01  # 突破1%以上

        # 有明显的上涨趋势
        ma5 = recent['close'].rolling(5).mean()
        ma20 = recent['close'].rolling(20).mean()
        uptrend = ma5.iloc[-1] > ma20.iloc[-1]

        return breakout and uptrend

    def check_trendline_pattern_breakout(self) -> bool:
        """
        买点7: 趋势线 + 形态的突破
        """
        if len(self.data) < 60:
            return False

        recent = self.data.tail(60)

        # 检查是否有箱体整理后的突破
        # 计算最近20天的波动范围
        box_period = recent.tail(20)
        box_high = box_period['high'].max()
        box_low = box_period['low'].min()
        box_range = (box_high - box_low) / box_low

        # 箱体整理（波动范围<15%）
        is_consolidation = box_range < 0.15

        # 突破箱体上轨
        current_close = recent['close'].iloc[-1]
        breakout = current_close > box_high

        return is_consolidation and breakout

    def check_major_pattern_breakout(self) -> bool:
        """
        买点8: 大形态突破
        条件：长期底部盘整后的突破
        """
        if len(self.data) < 120:
            return False

        # 检查长期盘整（60天以上）
        long_term = self.data.tail(120)
        consolidation_period = long_term.tail(60)

        # 计算盘整区间
        cons_high = consolidation_period['high'].max()
        cons_low = consolidation_period['low'].min()
        cons_range = (cons_high - cons_low) / cons_low

        # 长期盘整（波动<20%）
        is_long_consolidation = cons_range < 0.20

        # 最近突破
        current_close = self.data['close'].iloc[-1]
        recent_breakout = current_close > cons_high * 1.02

        # 成交量放大
        avg_volume = consolidation_period['volume'].mean()
        volume_surge = self.data['volume'].iloc[-1] > avg_volume * 2

        return is_long_consolidation and recent_breakout and volume_surge

    # ==================== 上涨趋势中的买点（9-13）====================

    def check_fibonacci_pullback(self) -> bool:
        """
        买点9: 波段的回踩（斐波那契回调）
        条件：回调到0.382、0.5或0.618位置
        """
        if len(self.data) < 60:
            return False

        recent = self.data.tail(60)

        # 找到最近的上涨波段
        # 找低点
        low_idx = recent['low'].idxmin()
        low_price = recent.loc[low_idx, 'low']

        # 找低点之后的高点
        after_low = recent.loc[low_idx:]
        if len(after_low) < 10:
            return False

        high_price = after_low['high'].max()

        # 计算斐波那契回调位
        fib_382 = high_price - (high_price - low_price) * 0.382
        fib_500 = high_price - (high_price - low_price) * 0.500
        fib_618 = high_price - (high_price - low_price) * 0.618

        # 当前价格
        current_price = recent['close'].iloc[-1]

        # 检查是否在回调位附近（±3%）
        near_fib = (
            abs(current_price - fib_382) / fib_382 < 0.03 or
            abs(current_price - fib_500) / fib_500 < 0.03 or
            abs(current_price - fib_618) / fib_618 < 0.03
        )

        # 检查是否有反转信号
        last_k = recent.iloc[-1]
        is_bullish = last_k['close'] > last_k['open']

        return near_fib and is_bullish

    def check_spring_in_box(self) -> bool:
        """
        买点10: 箱体/形态内的弹簧
        条件：跌破箱体底部但快速拉回
        """
        if len(self.data) < 40:
            return False

        recent = self.data.tail(40)

        # 定义箱体（最近20天）
        box_period = recent.tail(21).iloc[:-1]
        box_low = box_period['low'].min()

        # 最后一根K线
        last_k = recent.iloc[-1]

        # 跌破箱体底部
        pierced = last_k['low'] < box_low

        # 快速拉回（收盘价回到箱体内）
        recovered = last_k['close'] > box_low

        # 有长下影线
        lower_shadow = last_k['close'] - last_k['low']
        body = abs(last_k['close'] - last_k['open'])
        has_long_shadow = lower_shadow > body * 2

        return pierced and recovered and has_long_shadow

    def check_multi_timeframe_resonance(self) -> bool:
        """
        买点11: 多周期共振
        条件：多个周期都呈现上涨趋势
        """
        if len(self.data) < 60:
            return False

        recent = self.data.tail(60)

        # 计算不同周期的均线
        ma5 = recent['close'].rolling(5).mean()
        ma10 = recent['close'].rolling(10).mean()
        ma20 = recent['close'].rolling(20).mean()
        ma60 = recent['close'].rolling(60).mean()

        # 多头排列（短期均线在长期均线之上）
        if len(ma5) < 1 or len(ma10) < 1 or len(ma20) < 1 or len(ma60) < 1:
            return False

        bullish_alignment = (
            ma5.iloc[-1] > ma10.iloc[-1] and
            ma10.iloc[-1] > ma20.iloc[-1] and
            ma20.iloc[-1] > ma60.iloc[-1]
        )

        # 当前价格在所有均线之上
        current_price = recent['close'].iloc[-1]
        above_all_ma = current_price > ma60.iloc[-1]

        return bullish_alignment and above_all_ma

    def check_support_resistance_swap(self) -> bool:
        """
        买点12: 支撑压力互换
        条件：回调到前期压力转支撑的位置
        """
        if len(self.data) < 60:
            return False

        recent = self.data.tail(60)

        # 找到前期的压力位（前30天的高点）
        resistance_period = recent.tail(31).iloc[:-1]
        resistance_level = resistance_period['high'].max()

        # 检查是否已经突破该压力位
        breakthrough_period = recent.tail(10)
        has_breakthrough = breakthrough_period['close'].max() > resistance_level

        # 当前价格回调到该位置附近（±3%）
        current_price = recent['close'].iloc[-1]
        near_support = abs(current_price - resistance_level) / resistance_level < 0.03

        # 价格在该位置之上（支撑有效）
        above_support = current_price > resistance_level * 0.97

        return has_breakthrough and near_support and above_support

    def check_trend_sharp_drop(self) -> bool:
        """
        买点13: 趋势急跌（首次急跌到50%）
        条件：上涨趋势中第一次快速暴跌到50%位置
        """
        if len(self.data) < 60:
            return False

        recent = self.data.tail(60)

        # 检查是否有上涨趋势
        ma20 = recent['close'].rolling(20).mean()
        has_uptrend = ma20.iloc[-1] > ma20.iloc[-20] if len(ma20) >= 20 else False

        if not has_uptrend:
            return False

        # 找到最近的高点
        high_idx = recent['high'].tail(20).idxmax()
        high_price = recent.loc[high_idx, 'high']

        # 找到高点之前的低点
        before_high = recent.loc[:high_idx]
        if len(before_high) < 10:
            return False

        low_price = before_high['low'].min()

        # 计算50%回调位
        retracement_50 = high_price - (high_price - low_price) * 0.5

        # 当前价格在50%回调位附近（±3%）
        current_price = recent['close'].iloc[-1]
        near_50_percent = abs(current_price - retracement_50) / retracement_50 < 0.03

        # 检查是否是快速下跌（最近5天跌幅>10%）
        recent_5 = recent.tail(5)
        drop_pct = (recent_5['close'].iloc[-1] - recent_5['close'].iloc[0]) / recent_5['close'].iloc[0]
        is_sharp_drop = drop_pct < -0.10

        return near_50_percent and is_sharp_drop
