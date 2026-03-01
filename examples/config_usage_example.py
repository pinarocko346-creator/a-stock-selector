"""
使用配置文件的示例
展示如何使用buy_points_config.py中的参数
"""
import sys
import os
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from config.buy_points_config import (
    BUY_POINTS_CONFIG,
    get_buy_point_config,
    get_all_weights,
    get_buy_points_by_weight
)


def show_config_examples():
    """展示配置文件的使用方法"""

    print("=" * 80)
    print("13个买点配置文件使用示例")
    print("=" * 80)

    # 示例1: 查看所有买点的权重
    print("\n【示例1】所有买点的权重:")
    weights = get_all_weights()
    for bp_num, weight in sorted(weights.items(), key=lambda x: x[1], reverse=True):
        config = BUY_POINTS_CONFIG[bp_num]
        print(f"  买点{bp_num:2d}: {config['name']:15s} - 权重{weight:2d}")

    # 示例2: 查看高权重买点（权重>=8）
    print("\n【示例2】高权重买点（权重>=8）:")
    high_weight_points = get_buy_points_by_weight(min_weight=8)
    for bp_num in high_weight_points:
        config = BUY_POINTS_CONFIG[bp_num]
        print(f"  买点{bp_num}: {config['name']} (权重{config['weight']})")
        print(f"    描述: {config['description']}")

    # 示例3: 查看特定买点的详细配置
    print("\n【示例3】买点1（2B结构）的详细配置:")
    bp1_config = get_buy_point_config(1)
    print(f"  名称: {bp1_config['name']}")
    print(f"  权重: {bp1_config['weight']}")
    print(f"  时间框架: {bp1_config['timeframe']}")
    print(f"  描述: {bp1_config['description']}")
    print(f"  最小数据长度: {bp1_config['min_data_length']}")
    print(f"  止损百分比: {bp1_config['stop_loss_pct']:.1%}")

    print("\n  判断条件:")
    conditions = bp1_config['conditions']
    print(f"    大阴线最小跌幅: {conditions['bearish_candle']['min_drop_pct']:.1%}")
    print(f"    大阴线成交量比: {conditions['bearish_candle']['volume_ratio']:.1f}倍")
    print(f"    大阳线最小涨幅: {conditions['bullish_candle']['min_rise_pct']:.1%}")
    print(f"    大阳线实体比例: {conditions['bullish_candle']['body_ratio']:.1%}")
    print(f"    大阳线成交量比: {conditions['bullish_candle']['volume_ratio']:.1f}倍")
    print(f"    确认天数: {conditions['confirmation_days']}天")

    # 示例4: 按时间框架分类
    print("\n【示例4】按时间框架分类:")
    timeframes = {}
    for bp_num, config in BUY_POINTS_CONFIG.items():
        tf = config['timeframe']
        if tf not in timeframes:
            timeframes[tf] = []
        timeframes[tf].append((bp_num, config['name']))

    for tf, points in timeframes.items():
        print(f"\n  {tf}:")
        for bp_num, name in points:
            print(f"    买点{bp_num}: {name}")

    # 示例5: 查看所有止损设置
    print("\n【示例5】所有买点的止损设置:")
    for bp_num in sorted(BUY_POINTS_CONFIG.keys()):
        config = BUY_POINTS_CONFIG[bp_num]
        print(f"  买点{bp_num:2d} {config['name']:15s}: {config['stop_loss_pct']:.1%}")

    # 示例6: 如何在代码中使用这些参数
    print("\n【示例6】在代码中使用参数的示例:")
    print("""
    # 获取买点1的配置
    config = get_buy_point_config(1)

    # 使用配置参数进行判断
    k1_drop = (k1['close'] - k1['open']) / k1['open']
    is_big_bearish = k1_drop < -config['conditions']['bearish_candle']['min_drop_pct']

    avg_volume = data['volume'].tail(20).mean()
    k1_volume_surge = k1['volume'] > avg_volume * config['conditions']['bearish_candle']['volume_ratio']

    # 计算止损价格
    stop_loss = k1['low'] * (1 - config['stop_loss_pct'])
    """)

    print("\n" + "=" * 80)


if __name__ == "__main__":
    show_config_examples()
