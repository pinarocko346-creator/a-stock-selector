"""
A股选股主程序
基于13个买点策略筛选股票并输出CSV
"""
import sys
import os
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

import pandas as pd
from datetime import datetime, timedelta
from typing import List, Dict
import time

from data.data_fetcher import StockDataFetcher
from strategies.buy_points import BuyPointAnalyzer


class StockSelector:
    """A股选股器"""

    def __init__(self, data_source: str = "akshare"):
        self.fetcher = StockDataFetcher(data_source=data_source)
        self.results = []

    def select_stocks(self, stock_codes: List[str] = None, start_date: str = None, end_date: str = None):
        """
        筛选股票

        Args:
            stock_codes: 股票代码列表，如果为None则获取所有A股
            start_date: 开始日期
            end_date: 结束日期
        """
        # 获取股票代码列表
        if stock_codes is None:
            print("正在获取所有A股代码...")
            stock_codes = self.fetcher.get_all_stock_codes()
            print(f"共获取 {len(stock_codes)} 只股票")

        # 设置日期范围
        if end_date is None:
            end_date = datetime.now().strftime('%Y-%m-%d')
        if start_date is None:
            start_date = (datetime.now() - timedelta(days=365)).strftime('%Y-%m-%d')

        print(f"\n开始分析股票，日期范围: {start_date} 至 {end_date}")
        print("=" * 80)

        # 分析每只股票
        total = len(stock_codes)
        for idx, code in enumerate(stock_codes, 1):
            try:
                # 显示进度
                if idx % 10 == 0 or idx == total:
                    print(f"进度: {idx}/{total} ({idx/total*100:.1f}%)")

                # 获取股票数据
                data = self.fetcher.get_stock_data(code, start_date, end_date)

                if data is None or len(data) < 60:
                    continue

                # 分析买点
                analyzer = BuyPointAnalyzer(data)
                buy_points = analyzer.analyze_all_buy_points()

                # 如果有符合条件的买点，记录结果
                if len(buy_points) > 0:
                    stock_name = self.fetcher.get_stock_name(code)

                    result = {
                        '股票代码': code,
                        '股票名称': stock_name,
                        '符合买点数量': len(buy_points),
                        '选股原因': '; '.join(buy_points),
                        '最新价格': f"{data['close'].iloc[-1]:.2f}",
                        '分析日期': end_date
                    }

                    self.results.append(result)

                    print(f"✓ 发现机会: {code} {stock_name} - {len(buy_points)}个买点")

                # 避免请求过快
                time.sleep(0.1)

            except Exception as e:
                print(f"✗ 分析股票 {code} 时出错: {e}")
                continue

        print("=" * 80)
        print(f"\n分析完成！共发现 {len(self.results)} 只符合条件的股票")

    def export_to_csv(self, filename: str = None):
        """
        导出结果到CSV文件

        Args:
            filename: 输出文件名
        """
        if len(self.results) == 0:
            print("没有符合条件的股票，无法导出")
            return

        if filename is None:
            filename = f"a_stock_selection_{datetime.now().strftime('%Y%m%d_%H%M%S')}.csv"

        # 创建DataFrame
        df = pd.DataFrame(self.results)

        # 按符合买点数量排序
        df = df.sort_values('符合买点数量', ascending=False)

        # 导出CSV
        output_path = os.path.join(os.path.dirname(os.path.dirname(__file__)), filename)
        df.to_csv(output_path, index=False, encoding='utf-8-sig')

        print(f"\n结果已导出到: {output_path}")
        print(f"共 {len(df)} 条记录")

        # 显示前10条结果
        print("\n前10只股票预览:")
        print("=" * 100)
        for idx, row in df.head(10).iterrows():
            print(f"{row['股票代码']} {row['股票名称']:8s} | 买点数: {row['符合买点数量']} | {row['选股原因']}")
        print("=" * 100)

    def print_summary(self):
        """打印统计摘要"""
        if len(self.results) == 0:
            print("没有符合条件的股票")
            return

        df = pd.DataFrame(self.results)

        print("\n" + "=" * 80)
        print("选股统计摘要")
        print("=" * 80)
        print(f"符合条件的股票总数: {len(df)}")
        print(f"平均符合买点数量: {df['符合买点数量'].mean():.2f}")
        print(f"最多符合买点数量: {df['符合买点数量'].max()}")

        # 统计各买点出现频率
        print("\n各买点出现频率:")
        buy_point_counts = {}
        for reasons in df['选股原因']:
            for reason in reasons.split('; '):
                buy_point_counts[reason] = buy_point_counts.get(reason, 0) + 1

        for buy_point, count in sorted(buy_point_counts.items(), key=lambda x: x[1], reverse=True):
            print(f"  {buy_point}: {count}次")

        print("=" * 80)


def main():
    """主函数"""
    print("=" * 80)
    print("A股选股系统 - 基于13个买点策略")
    print("=" * 80)

    # 创建选股器
    selector = StockSelector(data_source="akshare")

    # 选择模式
    print("\n请选择运行模式:")
    print("1. 快速测试模式（分析10只示例股票）")
    print("2. 完整模式（分析所有A股，需要较长时间）")

    choice = input("\n请输入选择 (1/2，默认1): ").strip() or "1"

    if choice == "1":
        # 快速测试模式
        print("\n使用快速测试模式...")
        test_codes = [
            '000001', '000002', '000333', '000651', '000858',
            '600000', '600036', '600519', '600887', '601318'
        ]
        selector.select_stocks(stock_codes=test_codes)

    else:
        # 完整模式
        print("\n使用完整模式，这可能需要较长时间...")
        confirm = input("确认继续？(y/n): ").strip().lower()
        if confirm == 'y':
            selector.select_stocks()
        else:
            print("已取消")
            return

    # 打印摘要
    selector.print_summary()

    # 导出CSV
    selector.export_to_csv()

    print("\n选股完成！")


if __name__ == "__main__":
    main()
