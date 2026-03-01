#!/usr/bin/env python3
"""
三重滤网系统快速测试
"""
import sys
import os
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

import pandas as pd
from datetime import datetime
from data.data_fetcher import StockDataFetcher
from strategies.triple_screen import TripleScreenSystem


def test_triple_screen():
    """测试三重滤网系统"""
    print("=" * 80)
    print("三重滤网系统 - 快速测试")
    print("=" * 80)

    # 创建数据获取器
    fetcher = StockDataFetcher(data_source="sample")

    # 测试股票列表
    test_stocks = [
        ('000001', '平安银行'),
        ('600519', '贵州茅台'),
        ('000333', '美的集团'),
    ]

    print("\n开始测试...")
    print("-" * 80)

    results = []

    for code, name in test_stocks:
        print(f"\n分析股票: {code} {name}")

        # 获取数据
        data = fetcher.get_stock_data(code, start_date='2023-01-01', end_date='2024-12-31')

        if data is None:
            print(f"  ✗ 无法获取数据")
            continue

        print(f"  数据量: {len(data)} 天")

        # 创建三重滤网系统
        system = TripleScreenSystem(data)

        # 执行分析
        result = system.analyze()

        print(f"\n  三重滤网分析结果:")
        print(f"  {'-' * 60}")
        print(f"  {result['description']}")
        print(f"  {'-' * 60}")

        # 详细信息
        print(f"\n  详细数据:")
        print(f"    第一层滤网（长周期趋势）:")
        print(f"      - 趋势: {result['screen1']['trend']}")
        print(f"      - MACD: {result['screen1']['macd']:.4f}")
        print(f"      - 信号线: {result['screen1']['signal']:.4f}")

        print(f"\n    第二层滤网（中周期震荡）:")
        print(f"      - 位置: {result['screen2']['position']}")
        print(f"      - RSI: {result['screen2']['rsi']:.2f}")

        print(f"\n    第三层滤网（短周期突破）:")
        print(f"      - 突破: {result['screen3']['breakout']}")
        print(f"      - 当前价: {result['screen3']['price']:.2f}")

        # 如果有信号，记录结果
        if result['signal'] in ['buy', 'wait_breakout', 'consider_buy']:
            results.append({
                '股票代码': code,
                '股票名称': name,
                '信号': result['signal'],
                '长周期趋势': result['screen1']['trend'],
                'RSI': f"{result['screen2']['rsi']:.1f}",
                '最新价格': f"{data['close'].iloc[-1]:.2f}",
                '说明': result['description'].replace('\n', ' | ')
            })

    print("\n" + "=" * 80)
    print("测试完成")
    print("=" * 80)

    if len(results) > 0:
        # 导出CSV
        df = pd.DataFrame(results)
        output_file = 'triple_screen_test_results.csv'
        df.to_csv(output_file, index=False, encoding='utf-8-sig')

        print(f"\n结果已导出到: {output_file}")
        print(f"\n结果预览:")
        for _, row in df.iterrows():
            print(f"\n{row['股票代码']} {row['股票名称']}")
            print(f"  信号: {row['信号']}")
            print(f"  趋势: {row['长周期趋势']}, RSI: {row['RSI']}")
            print(f"  价格: {row['最新价格']}")
    else:
        print("\n未发现符合条件的股票")

    print("\n提示: 这是使用示例数据的测试。")
    print("要分析真实A股数据，请运行: python triple_screen_main.py")


if __name__ == "__main__":
    test_triple_screen()
