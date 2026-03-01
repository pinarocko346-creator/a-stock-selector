"""
13个买点策略的详细参数配置
根据你提供的完整规范整理
"""

# 13个买点的详细参数配置
BUY_POINTS_CONFIG = {
    1: {
        'name': '2B结构',
        'weight': 10,
        'timeframe': 'daily',
        'description': '完整5浪下跌后的恐慌性反转',
        'min_data_length': 30,
        'conditions': {
            # 条件3: 第5浪以恐慌性下跌结束
            'bearish_candle': {
                'min_drop_pct': 0.03,  # 跌幅 > 3%
                'volume_ratio': 1.5,  # 成交量 > 20日均量1.5倍
            },
            # 条件4: 立即反转
            'bullish_candle': {
                'min_rise_pct': 0.03,  # 涨幅 > 3%
                'body_ratio': 0.7,  # 阳线实体 > 阴线实体70%
                'volume_ratio': 1.2,  # 成交量 > 前一日1.2倍
            },
            # 条件5: 位置确认
            'confirmation_days': 3,  # 3日内不创新低
        },
        'stop_loss_pct': 0.03,  # 止损: 反转前低点下方3%
    },

    2: {
        'name': '底部头肩右肩',
        'weight': 8,
        'timeframe': 'daily',
        'description': '头肩底形态的右肩50%位置',
        'min_data_length': 60,
        'conditions': {
            # 条件2: 回落到50%位置
            'retracement_level': 0.5,  # 斐波那契0.5
            'price_tolerance': 0.02,  # 价格容差±2%
            # 条件3: 不创新低
            'new_low_threshold': 0.02,  # 右肩低点 > 头部低点2%
            # 条件4: 成交量特征
            'volume_shrink': True,  # 右肩成交量 < 头部成交量
            # 条件5: K线信号
            'reversal_signals': ['长下影线', '阳包阴', '早晨之星'],
            'shadow_ratio': 2.0,  # 下影 > 实体2倍
        },
        'stop_loss_pct': 0.02,  # 止损: 头部低点下方2%
    },

    3: {
        'name': '二次测试',
        'weight': 8,
        'timeframe': 'daily',
        'description': '刺破前低但快速收回',
        'min_data_length': 30,
        'conditions': {
            # 条件2: 刺破前低
            'pierce_depth_max': 0.03,  # 跌破幅度 < 3%
            'pierce_days_max': 3,  # 时间 < 3个交易日
            # 条件3: 快速收回
            'recovery_volume_ratio': 1.3,  # 收回时成交量 > 跌破时1.3倍
            # 条件4: K线确认
            'reversal_signals': ['长下影线', '锤子线', '阳包阴'],
            'shadow_ratio': 1.5,  # 下影 > 实体1.5倍
        },
        'stop_loss_pct': 0.02,  # 止损: 刺破最低点下方2%
    },

    4: {
        'name': '强势出现',
        'weight': 6,
        'timeframe': 'daily',
        'description': '底部形态中轴以上的放量阳线',
        'min_data_length': 40,
        'conditions': {
            # 条件1: 底部形态清晰
            'pattern_min_days': 20,  # 形态持续时间 >= 20个交易日
            'pattern_types': ['箱体', '三角形', '圆弧底'],
            # 条件2: 位置在形态中轴以上
            'above_midline': True,
            'midline_days': 2,  # 站稳中轴 >= 2个交易日
            # 条件3: 放量阳线
            'min_rise_pct': 0.03,  # 涨幅 > 3%
            'volume_ratio': 1.5,  # 成交量 > 20日均量1.5倍
            'upper_shadow_ratio': 0.2,  # 上影线 < 实体20%
            # 条件5: 后续确认
            'confirmation_days': 3,
        },
        'stop_loss_pct': 0.02,  # 止损: 中轴位置下方2%
    },

    5: {
        'name': '趋势线+量能密集区突破',
        'weight': 7,
        'timeframe': 'daily',
        'description': '双突破：趋势线和量能密集区',
        'min_data_length': 60,
        'conditions': {
            # 条件1: 下降趋势线清晰
            'trendline_min_touches': 2,  # 至少2个触点
            'trendline_angle_min': 30,  # 角度30-60度
            'trendline_angle_max': 60,
            # 条件2: 量能密集区明确
            'consolidation_min_days': 15,  # 整理时间 >= 15个交易日
            # 条件3: 同时突破
            'breakout_min_rise': 0.02,  # 突破时涨幅 > 2%
            # 条件4: 成交量配合
            'volume_ratio': 2.0,  # 突破日成交量 > 20日均量2倍
            'consolidation_volume_ratio': 1.5,  # 或 > 整理期均量1.5倍
        },
        'stop_loss_pct': 0.03,  # 止损: 突破位下方3%
    },

    6: {
        'name': '趋势线+关键点位突破',
        'weight': 7,
        'timeframe': 'daily',
        'description': '双突破：趋势线和关键点位',
        'min_data_length': 60,
        'conditions': {
            # 条件2: 关键点位明确
            'key_levels': ['前高', '前低', '斐波那契0.382', '斐波那契0.5', '斐波那契0.618'],
            # 条件4: 成交量
            'volume_ratio': 1.5,  # 突破日成交量 > 前5日均量1.5倍
        },
        'stop_loss_pct': 0.02,  # 止损: 关键点位下方2%
    },

    7: {
        'name': '趋势线+形态突破',
        'weight': 7,
        'timeframe': 'daily',
        'description': '双突破：趋势线和形态',
        'min_data_length': 60,
        'conditions': {
            # 条件2: 底部形态
            'pattern_types': ['三角形', '楔形', '旗形'],
            'pattern_min_days': 10,  # 形态时间 >= 10个交易日
            # 条件3: 共振突破
            'breakout_min_rise': 0.02,  # 突破时阳线实体 > 2%
            # 条件4: 形态特征
            'volume_decreasing': True,  # 形态内成交量递减
            'breakout_volume_surge': True,  # 突破时成交量突增
        },
        'stop_loss_pct': 0.02,  # 止损: 形态下沿下方2%
    },

    8: {
        'name': '大形态突破',
        'weight': 9,
        'timeframe': 'daily',
        'description': '长期盘整后的突破',
        'min_data_length': 120,
        'conditions': {
            # 条件1: 长期盘整
            'consolidation_min_days': 60,  # 盘整时间 >= 3个月
            'consolidation_max_range': 0.30,  # 盘整幅度 < 30%
            # 条件2: 形态规整
            'pattern_types': ['箱体', '圆弧底', '大三角形'],
            'min_touches': 4,  # 至少2次触及上沿，2次触及下沿
            # 条件3: 放量突破
            'volume_ratio': 2.5,  # 突破日成交量 > 20日均量2.5倍
            'min_rise_pct': 0.03,  # 阳线实体 > 3%
            # 条件4: 回抽确认
            'pullback_days_min': 3,
            'pullback_days_max': 5,
            'pullback_volume_shrink': True,  # 回抽时缩量
        },
        'stop_loss_pct': 0.05,  # 止损: 突破位下方5%
    },

    9: {
        'name': '斐波那契回调',
        'weight': 6,
        'timeframe': 'daily',
        'description': '上涨波段的回调买点',
        'min_data_length': 60,
        'conditions': {
            # 条件1: 明确的上涨波段
            'min_rise_pct': 0.20,  # 涨幅 > 20%
            'min_rise_days': 10,  # 上涨时间 >= 10个交易日
            # 条件2: 回调到关键位
            'fib_levels': [0.382, 0.5, 0.618],
            'price_tolerance': 0.01,  # 价格容差±1%
            # 条件3: 止跌信号
            'reversal_signals': ['长下影线', '十字星', '阳包阴', '锤子线'],
            # 条件4: 成交量
            'pullback_volume_shrink': True,  # 回调过程中缩量
            # 条件5: 趋势保持
            'ma20_uptrend': True,  # 20日均线仍然向上
        },
        'stop_loss_pct': 0.02,  # 止损: 回调低点下方2%
    },

    10: {
        'name': '箱体弹簧',
        'weight': 7,
        'timeframe': 'daily',
        'description': '跌破箱体后快速拉回',
        'min_data_length': 40,
        'conditions': {
            # 条件1: 箱体形态清晰
            'box_min_days': 15,  # 盘整时间 >= 15个交易日
            'box_min_touches': 4,  # 至少2次触及上沿，2次触及下沿
            'box_range_min': 0.10,  # 箱体幅度10-20%
            'box_range_max': 0.20,
            # 条件2: 跌破箱体下沿
            'pierce_depth_max': 0.05,  # 跌破幅度 < 5%
            'pierce_days_max': 3,  # 跌破时间 < 3个交易日
            # 条件3: 快速拉回
            'recovery_min_rise': 0.02,  # 拉回时涨幅 > 2%
            'recovery_volume_ratio': 1.5,  # 拉回时成交量 > 跌破时1.5倍
            # 条件4: K线特征
            'shadow_ratio': 2.0,  # 长下影线：下影 > 实体2倍
            # 条件5: 假突破确认
            'confirmation_days': 3,
        },
        'stop_loss_pct': 0.02,  # 止损: 跌破最低点下方2%
    },

    11: {
        'name': '多周期共振',
        'weight': 5,
        'timeframe': 'multi',  # 日线、周线、月线
        'description': '多个周期都呈现上涨趋势',
        'min_data_length': 60,
        'conditions': {
            # 条件1: 均线多头排列
            'daily_ma': [5, 20, 60],  # 日线: 5日 > 20日 > 60日
            'weekly_ma': [5, 20],  # 周线: 5周 > 20周
            # 条件2: MACD共振
            'daily_macd_above_zero': True,  # 日线MACD在零轴上方
            'weekly_macd_uptrend': True,  # 周线MACD向上或金叉
            # 条件3: 趋势一致性
            'monthly_uptrend': True,  # 月线趋势向上
            # 条件4: 成交量配合
            'volume_ratio': 1.0,  # 近期成交量 > 20日均量
            # 条件5: 买入时机
            'entry_points': ['回调到5日线', '回调到20日线', '突破前高'],
        },
        'stop_loss_pct': 0.03,  # 止损: 20日均线下方3%
    },

    12: {
        'name': '支撑压力互换',
        'weight': 6,
        'timeframe': 'daily',
        'description': '前期压力变成支撑',
        'min_data_length': 60,
        'conditions': {
            # 条件1: 前期压力明确
            'resistance_types': ['历史高点', '前期平台', '密集成交区'],
            'min_touches': 2,  # 至少2次触及后回落
            # 条件2: 突破确认
            'breakout_min_rise': 0.03,  # 突破涨幅 > 3%
            'breakout_volume_ratio': 2.0,  # 成交量 > 20日均量2倍
            'breakout_hold_days': 3,  # 收盘价站在压力位上方 >= 3日
            # 条件3: 回抽确认
            'pullback_volume_shrink': True,  # 回抽时缩量
            # 条件4: 再次向上
            'rebound_volume_ratio': 1.0,  # 成交量温和放大
            # 条件5: 买入点
            'entry_points': ['回抽到支撑位', '再次向上突破'],
        },
        'stop_loss_pct': 0.03,  # 止损: 原压力位下方3%
    },

    13: {
        'name': '趋势急跌',
        'weight': 4,
        'timeframe': 'daily',
        'description': '上涨趋势中的首次急跌',
        'min_data_length': 60,
        'conditions': {
            # 条件1: 明确的上升趋势
            'ma20_uptrend': True,  # 20日均线向上
            'above_ma20_days': 20,  # 价格运行在20日均线上方 >= 20日
            'weekly_uptrend': True,  # 周线趋势向上
            # 条件2: 首次急跌
            'single_day_drop': 0.05,  # 单日跌幅 > 5%
            'three_day_drop': 0.08,  # 或3日累计跌幅 > 8%
            'first_drop': True,  # 这是上涨以来的第一次急跌
            # 条件3: 跌到关键位
            'key_levels': ['50%位置', '20日均线', '前期平台'],
            # 条件4: 快速反弹
            'rebound_min_ratio': 0.30,  # 反弹幅度 > 跌幅的30%
            # 条件5: 成交量
            'drop_volume_surge': True,  # 急跌时放量（恐慌盘）
            'rebound_volume_normal': True,  # 反弹时缩量或平量
        },
        'stop_loss_pct': 0.02,  # 止损: 急跌最低点下方2%
    },
}


# 全局配置
GLOBAL_CONFIG = {
    'min_data_length': 60,  # 最小数据长度
    'volume_ma_period': 20,  # 成交量均线周期
    'price_ma_periods': [5, 10, 20, 60],  # 价格均线周期
    'macd_params': {
        'fast': 12,
        'slow': 26,
        'signal': 9,
    },
    'rsi_period': 14,
}


def get_buy_point_config(buy_point_number: int) -> dict:
    """获取指定买点的配置"""
    return BUY_POINTS_CONFIG.get(buy_point_number, {})


def get_all_weights() -> dict:
    """获取所有买点的权重"""
    return {k: v['weight'] for k, v in BUY_POINTS_CONFIG.items()}


def get_buy_points_by_weight(min_weight: int = 0) -> list:
    """按权重筛选买点"""
    return [k for k, v in BUY_POINTS_CONFIG.items() if v['weight'] >= min_weight]
