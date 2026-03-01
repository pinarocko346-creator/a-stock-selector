#!/usr/bin/env python3
"""
快速测试脚本 - 使用示例数据测试13个买点策略
"""
import sys
import os
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

import pandas as pd
from datetime import datetime
from data.data_fetcher import StockDataFetcher
from strategies.buy_points import BuyPointAnalyzer


def test_buy_points():
    """测试13个买点策略"""
    print("=" * 80)
    print("A股选股系统 - 快速测试")
    print("=" * 80)

    # 创建数据获取器（使用示例数据）
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

        # 分析买点
        analyzer = BuyPointAnalyzer(data)
        buy_points = analyzer.analyze_all_buy_points()

        if len(buy_points) > 0:
            print(f"  ✓ 发现 {len(buy_points)} 个买点:")
            for bp in buy_points:
                print(f"    - {bp}")

            results.append({
                '股票代码': code,
                '股票名称': name,
                '符合买点数量': len(buy_points),
                '选股原因': '; '.join(buy_points),
                '最新价格': f"{data['close'].iloc[-1]:.2f}",
                '分析日期': datetime.now().strftime('%Y-%m-%d')
            })
        else:
            print(f"  - 未发现符合条件的买点")

    print("\n" + "=" * 80)
    print("测试完成")
    print("=" * 80)

    if len(results) > 0:
        # 导出CSV
        df = pd.DataFrame(results)
        output_file = 'test_results.csv'
        df.to_csv(output_file, index=False, encoding='utf-8-sig')

        print(f"\n结果已导出到: {output_file}")
        print(f"\n结果预览:")
        print(df.to_string(index=False))
    else:
        print("\n未发现符合条件的股票")

    print("\n提示: 这是使用示例数据的测试。")
    print("要分析真实A股数据，请运行: python main.py")


if __name__ == "__main__":
    test_buy_points()
