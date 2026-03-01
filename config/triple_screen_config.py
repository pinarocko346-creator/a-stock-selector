"""
三重滤网策略的详细参数配置
基于亚历山大·埃尔德博士的理论
核心：顺大势，逆小势，等突破
"""

# 三重滤网配置
TRIPLE_SCREEN_CONFIG = {
    # 第一层滤网：长周期趋势（周线）
    'screen1': {
        'name': '长周期趋势',
        'timeframe': 'weekly',
        'description': '判断大趋势方向，只顺势交易',

        'macd': {
            'fast': 12,
            'slow': 26,
            'signal': 9,
            'trend_bars': 3,  # 连续3周判断趋势
        },

        'moving_averages': {
            'fast_ma': 5,   # 5周均线
            'slow_ma': 20,  # 20周均线
        },

        'trend_strength': {
            'strong_up': {
                'macd_rising': True,
                'ma_bullish': True,  # 5周 > 20周
                'price_above_ma20': True,
            },
            'weak_up': {
                'macd_rising': True,
                'ma_bullish': True,
                'price_near_ma20': True,  # 在20周线附近
            },
            'sideways': {
                'macd_flat': True,
                'ma_converging': True,
            },
            'down': {
                'macd_falling': True,
                # 或均线空头
            },
        },

        'price_tolerance': 0.03,  # 价格在均线附近的容差（3%）
    },

    # 第二层滤网：中周期位置（日线）
    'screen2': {
        'name': '中周期位置',
        'timeframe': 'daily',
        'description': '寻找最佳入场位置，逆小势买入',

        'rsi': {
            'period': 14,
            'oversold': 30,      # 超卖区
            'weak': 40,          # 偏弱区
            'neutral_weak': 50,  # 中性偏弱
            'overbought': 70,    # 超买区
        },

        'rsi_status': {
            '超卖': {'min': 0, 'max': 30, 'score': 10},
            '偏弱': {'min': 30, 'max': 40, 'score': 7},
            '中性偏弱': {'min': 40, 'max': 50, 'score': 4},
            '中性': {'min': 50, 'max': 60, 'score': 2},
            '偏强': {'min': 60, 'max': 70, 'score': 0},
            '超买': {'min': 70, 'max': 100, 'score': 0},
        },

        'reversal_signals': {
            '长下影线': {'shadow_ratio': 2.0},  # 下影 > 实体2倍
            '锤子线': {'shadow_ratio': 2.0, 'upper_shadow_ratio': 0.3},
            '阳包阴': {'engulfing': True},
            '早晨之星': {'morning_star': True},
        },

        'volume': {
            'pullback_shrink': 0.8,  # 回调时缩量（<20日均量0.8倍）
            'reversal_surge': 1.2,   # 止跌时放量（>前一日1.2倍）
        },

        'support_levels': {
            'ma20': True,           # 20日均线
            'previous_platform': True,  # 前期平台
            'fibonacci': [0.382, 0.5, 0.618],  # 斐波那契回调位
        },

        'position_quality': {
            '极佳': {
                'rsi_max': 30,
                'reversal_signal': True,
                'volume_shrink': True,
                'score': 10,
            },
            '良好': {
                'rsi_max': 40,
                'reversal_signal': True,
                'support': True,
                'score': 7,
            },
            '一般': {
                'rsi_max': 50,
                'support': True,
                'score': 4,
            },
            '不佳': {
                'rsi_min': 50,
                'score': 0,
            },
        },
    },

    # 第三层滤网：短周期突破（60分钟线）
    'screen3': {
        'name': '短周期突破',
        'timeframe': '60min',  # 或30分钟
        'description': '确认入场时机，避免过早入场',

        'breakout_types': {
            '突破前高': {
                'lookback_bars': 3,  # 前3根K线
                'volume_ratio': 1.5,  # 成交量>前5根均量1.5倍
                'min_rise': 0.01,     # 阳线实体>1%
            },
            '反弹确认': {
                'rebound_pct': 0.02,  # 从日内低点反弹>2%
                'reversal_signal': True,
                'volume_ratio': 1.2,
            },
            '均线突破': {
                'fast_ma': 5,
                'slow_ma': 10,
                'macd_golden_cross': True,
            },
        },

        'confirmation': {
            'bars_after_breakout': 3,  # 突破后3根K线确认
            'volume_maintain': True,    # 成交量维持在均量以上
            'price_above_breakout': True,  # 收盘价站在突破位上方
        },

        'false_breakout_filter': {
            'quick_reversal_bars': 3,  # 3根K线内跌破
            'volume_shrink': True,
            'long_upper_shadow': True,
        },
    },

    # 三层滤网组合规则
    'combination_rules': {
        '买入信号': {
            'screen1': {
                'trend': ['up', 'weak_up'],
                'strength': ['strong', 'medium'],
            },
            'screen2': {
                'rsi_status': ['超卖', '偏弱'],
                'rsi_rising': True,
                'support': True,
            },
            'screen3': {
                'breakout_confirmed': True,
                'effectiveness': ['强', '中'],
            },
            'score': 10,
            'position_size': {'min': 0.3, 'max': 0.5},
            'stop_loss_pct': 0.03,
        },

        '等待信号': {
            'screen1': {
                'trend': ['up', 'weak_up'],
            },
            'screen2': {
                'rsi_status': ['超卖', '偏弱'],
                'reversal_sign': True,
            },
            'screen3': {
                'breakout_confirmed': False,
            },
            'score': 6,
            'position_size': {'min': 0.1, 'max': 0.2},
            'stop_loss_pct': 0.02,
        },

        '可考虑': {
            'screen1': {
                'trend': ['up'],
            },
            'screen2': {
                'rsi_status': ['中性偏弱'],
            },
            'screen3': {
                'breakout_confirmed': True,
            },
            'score': 4,
            'position_size': {'min': 0.1, 'max': 0.2},
            'stop_loss_pct': 0.02,
        },

        '观望': {
            'conditions': [
                {'screen1': {'trend': ['down', 'sideways']}},
                {'screen2': {'rsi_status': ['超买']}},
                {'screen3': {'false_breakout': True}},
            ],
            'score': 0,
            'action': '放弃',
        },
    },

    # 与13个买点的配合
    'integration_with_buy_points': {
        '最强组合': {
            'triple_screen_signal': '买入信号',
            'buy_points_score': 15,  # 总分>=15
            'key_buy_points': [1, 8],  # 有买点1或8
            'grade': 'A',
            'recommendation': '强烈推荐',
        },

        '次强组合': {
            'triple_screen_signal': '买入信号',
            'buy_points_score': 12,  # 总分>=12
            'buy_points_count': 3,   # 符合买点数>=3
            'grade': 'B',
            'recommendation': '推荐',
        },

        '一般组合': {
            'triple_screen_signal': '等待信号',
            'key_buy_points': [8],  # 有买点8(大形态突破)
            'grade': 'C',
            'recommendation': '可考虑',
        },
    },

    # 评分体系
    'scoring_system': {
        'triple_screen': {
            '买入信号': 10,
            '等待信号': 6,
            '可考虑': 4,
            '观望': 0,
        },
        'total_score_grades': {
            'A': {'min': 20, 'label': '强烈推荐'},
            'B': {'min': 15, 'max': 19, 'label': '推荐'},
            'C': {'min': 10, 'max': 14, 'label': '可考虑'},
            'D': {'max': 9, 'label': '放弃'},
        },
    },

    # 市场环境参数调整
    'market_conditions': {
        '牛市': {
            'screen1': {
                'accept_weak_up': True,
            },
            'screen2': {
                'rsi_oversold': 35,  # 放宽到35
                'rsi_weak': 45,      # 放宽到45
            },
            'screen3': {
                'lookback_bars': 2,  # 简化到2根K线
            },
        },

        '熊市': {
            'screen1': {
                'only_strong_up': True,  # 只做up，不做weak_up
            },
            'screen2': {
                'rsi_oversold': 25,  # 收紧到25
                'rsi_must_rising': True,  # 必须RSI回升
            },
            'screen3': {
                'confirmation_bars': 3,  # 需要3根K线确认
                'volume_ratio': 2.0,     # 成交量>2倍均量
            },
        },

        '震荡市': {
            'screen1': {
                'accept_sideways': True,  # 接受sideways
            },
            'screen2': {
                'rsi_buy': 30,   # RSI<30买入
                'rsi_sell': 70,  # RSI>70卖出
            },
            'screen3': {
                'lower_target': True,  # 降低预期
            },
        },
    },
}


# 全局配置
GLOBAL_CONFIG = {
    'default_market_condition': '牛市',  # 默认市场环境
    'min_data_length': 120,  # 最小数据长度（需要周线数据）
    'weekly_resample_rule': '5D',  # 周线重采样规则
}


def get_triple_screen_config() -> dict:
    """获取三重滤网配置"""
    return TRIPLE_SCREEN_CONFIG


def get_market_adjusted_config(market_condition: str = '牛市') -> dict:
    """
    获取根据市场环境调整后的配置

    Args:
        market_condition: 市场环境（牛市/熊市/震荡市）

    Returns:
        调整后的配置
    """
    base_config = TRIPLE_SCREEN_CONFIG.copy()
    adjustments = TRIPLE_SCREEN_CONFIG['market_conditions'].get(market_condition, {})

    # 应用调整
    if adjustments:
        for screen, params in adjustments.items():
            if screen in base_config:
                base_config[screen].update(params)

    return base_config


def get_signal_score(signal_type: str) -> int:
    """获取信号评分"""
    return TRIPLE_SCREEN_CONFIG['scoring_system']['triple_screen'].get(signal_type, 0)


def calculate_total_score(triple_screen_score: int, buy_points_score: int) -> tuple:
    """
    计算总评分和等级

    Args:
        triple_screen_score: 三重滤网评分
        buy_points_score: 13个买点评分

    Returns:
        (总分, 等级, 标签)
    """
    total = triple_screen_score + buy_points_score

    for grade, criteria in TRIPLE_SCREEN_CONFIG['scoring_system']['total_score_grades'].items():
        min_score = criteria.get('min', 0)
        max_score = criteria.get('max', 100)

        if min_score <= total <= max_score:
            return total, grade, criteria['label']

    return total, 'D', '放弃'
