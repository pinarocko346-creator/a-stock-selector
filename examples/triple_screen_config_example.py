"""
三重滤网配置文件使用示例
"""
import sys
import os
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from config.triple_screen_config import (
    TRIPLE_SCREEN_CONFIG,
    get_triple_screen_config,
    get_market_adjusted_config,
    get_signal_score,
    calculate_total_score
)


def show_triple_screen_config():
    """展示三重滤网配置"""

    print("=" * 80)
    print("三重滤网系统配置详解")
    print("=" * 80)

    config = get_triple_screen_config()

    # 第一层滤网
    print("\n【第一层滤网】长周期趋势（周线）")
    print("-" * 80)
    screen1 = config['screen1']
    print(f"名称: {screen1['name']}")
    print(f"时间框架: {screen1['timeframe']}")
    print(f"描述: {screen1['description']}")

    print("\nMACD参数:")
    macd = screen1['macd']
    print(f"  快线: {macd['fast']}, 慢线: {macd['slow']}, 信号线: {macd['signal']}")
    print(f"  趋势判断: 连续{macd['trend_bars']}周")

    print("\n均线参数:")
    ma = screen1['moving_averages']
    print(f"  快线: {ma['fast_ma']}周, 慢线: {ma['slow_ma']}周")

    print("\n趋势强度判断:")
    for strength, criteria in screen1['trend_strength'].items():
        print(f"  {strength}: {criteria}")

    # 第二层滤网
    print("\n【第二层滤网】中周期位置（日线）")
    print("-" * 80)
    screen2 = config['screen2']
    print(f"名称: {screen2['name']}")
    print(f"时间框架: {screen2['timeframe']}")
    print(f"描述: {screen2['description']}")

    print("\nRSI参数:")
    rsi = screen2['rsi']
    print(f"  周期: {rsi['period']}")
    print(f"  超卖: <{rsi['oversold']}")
    print(f"  偏弱: {rsi['oversold']}-{rsi['weak']}")
    print(f"  中性偏弱: {rsi['weak']}-{rsi['neutral_weak']}")
    print(f"  超买: >{rsi['overbought']}")

    print("\nRSI状态评分:")
    for status, params in screen2['rsi_status'].items():
        print(f"  {status}: {params['min']}-{params['max']}, 得分{params['score']}")

    print("\n反转信号:")
    for signal, params in screen2['reversal_signals'].items():
        print(f"  {signal}: {params}")

    print("\n位置质量评估:")
    for quality, criteria in screen2['position_quality'].items():
        print(f"  {quality}: {criteria}")

    # 第三层滤网
    print("\n【第三层滤网】短周期突破（60分钟线）")
    print("-" * 80)
    screen3 = config['screen3']
    print(f"名称: {screen3['name']}")
    print(f"时间框架: {screen3['timeframe']}")
    print(f"描述: {screen3['description']}")

    print("\n突破类型:")
    for breakout_type, params in screen3['breakout_types'].items():
        print(f"  {breakout_type}: {params}")

    print("\n确认条件:")
    confirmation = screen3['confirmation']
    print(f"  突破后确认K线数: {confirmation['bars_after_breakout']}")
    print(f"  成交量维持: {confirmation['volume_maintain']}")
    print(f"  价格站稳: {confirmation['price_above_breakout']}")

    # 组合规则
    print("\n【三层滤网组合规则】")
    print("-" * 80)
    for signal_type, rules in config['combination_rules'].items():
        if signal_type == '观望':
            continue
        print(f"\n{signal_type}:")
        print(f"  评分: {rules['score']}")
        print(f"  仓位: {rules['position_size']['min']:.0%}-{rules['position_size']['max']:.0%}")
        print(f"  止损: {rules['stop_loss_pct']:.1%}")
        print(f"  条件:")
        for screen, criteria in rules.items():
            if screen.startswith('screen'):
                print(f"    {screen}: {criteria}")

    # 评分体系
    print("\n【评分体系】")
    print("-" * 80)
    print("三重滤网评分:")
    for signal, score in config['scoring_system']['triple_screen'].items():
        print(f"  {signal}: {score}分")

    print("\n总评分等级:")
    for grade, criteria in config['scoring_system']['total_score_grades'].items():
        min_score = criteria.get('min', 0)
        max_score = criteria.get('max', '∞')
        print(f"  {grade}级 ({criteria['label']}): {min_score}-{max_score}分")

    # 与13个买点的配合
    print("\n【与13个买点的配合】")
    print("-" * 80)
    for combo_type, criteria in config['integration_with_buy_points'].items():
        print(f"\n{combo_type}:")
        for key, value in criteria.items():
            print(f"  {key}: {value}")

    # 市场环境调整
    print("\n【市场环境参数调整】")
    print("-" * 80)
    for market, adjustments in config['market_conditions'].items():
        print(f"\n{market}:")
        for screen, params in adjustments.items():
            print(f"  {screen}: {params}")

    # 示例：计算总评分
    print("\n【评分计算示例】")
    print("-" * 80)
    examples = [
        ('买入信号', 15, '有买点1'),
        ('买入信号', 12, '符合3个买点'),
        ('等待信号', 8, '有买点8'),
        ('可考虑', 5, '符合1个买点'),
    ]

    for ts_signal, bp_score, desc in examples:
        ts_score = get_signal_score(ts_signal)
        total, grade, label = calculate_total_score(ts_score, bp_score)
        print(f"\n三重滤网: {ts_signal}({ts_score}分) + 13个买点: {bp_score}分 ({desc})")
        print(f"  总分: {total}分, 等级: {grade}级, 评价: {label}")

    # 示例：不同市场环境的配置
    print("\n【不同市场环境配置示例】")
    print("-" * 80)
    for market in ['牛市', '熊市', '震荡市']:
        print(f"\n{market}配置:")
        adjusted_config = get_market_adjusted_config(market)
        screen2 = adjusted_config['screen2']
        if 'rsi_oversold' in screen2:
            print(f"  RSI超卖阈值: {screen2['rsi_oversold']}")
        if 'rsi_weak' in screen2:
            print(f"  RSI偏弱阈值: {screen2['rsi_weak']}")

    print("\n" + "=" * 80)


if __name__ == "__main__":
    show_triple_screen_config()
