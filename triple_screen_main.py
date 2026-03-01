"""
三重滤网选股主程序
基于亚历山大·埃尔德博士的三重滤网系统
"""
import sys
import os
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

import pandas as pd
from datetime import datetime, timedelta
from typing import List
import time

from data.data_fetcher import StockDataFetcher
from strategies.triple_screen import TripleScreenSystem, analyze_with_triple_screen


class TripleScreenSelector:
    """三重滤网选股器"""

    def __init__(self, data_source: str = "akshare"):
        self.fetcher = StockDataFetcher(data_source=data_source)
        self.results = []

    def select_stocks(self, stock_codes: List[str] = None, start_date: str = None, end_date: str = None):
        """
        使用三重滤网筛选股票

        Args:
            stock_codes: 股票代码列表
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

        print(f"\n开始三重滤网分析，日期范围: {start_date} 至 {end_date}")
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

                # 三重滤网分析
                result = analyze_with_triple_screen(data)

                if result is not None:
                    stock_name = self.fetcher.get_stock_name(code)

                    record = {
                        '股票代码': code,
                        '股票名称': stock_name,
                        '信号类型': self._get_signal_name(result['signal']),
                        '长周期趋势': result['screen1']['trend'],
                        '中周期位置': result['screen2']['position'],
                        '短周期突破': result['screen3']['breakout'],
                        'RSI': f"{result['screen2']['rsi']:.1f}",
                        '最新价格': f"{data['close'].iloc[-1]:.2f}",
                        '分析说明': result['description'],
                        '分析日期': end_date
                    }

                    self.results.append(record)

                    print(f"✓ 发现机会: {code} {stock_name} - {self._get_signal_name(result['signal'])}")

                # 避免请求过快
                time.sleep(0.1)

            except Exception as e:
                print(f"✗ 分析股票 {code} 时出错: {e}")
                continue

        print("=" * 80)
        print(f"\n分析完成！共发现 {len(self.results)} 只符合条件的股票")

    def _get_signal_name(self, signal: str) -> str:
        """获取信号名称"""
        signal_names = {
            'buy': '买入信号',
            'wait_breakout': '等待突破',
            'consider_buy': '可考虑买入',
            'sell': '卖出信号',
            'hold': '持有观望'
        }
        return signal_names.get(signal, signal)

    def export_to_csv(self, filename: str = None):
        """导出结果到CSV"""
        if len(self.results) == 0:
            print("没有符合条件的股票，无法导出")
            return

        if filename is None:
            filename = f"triple_screen_selection_{datetime.now().strftime('%Y%m%d_%H%M%S')}.csv"

        # 创建DataFrame
        df = pd.DataFrame(self.results)

        # 按信号类型排序（买入信号优先）
        signal_order = {'买入信号': 1, '等待突破': 2, '可考虑买入': 3}
        df['排序'] = df['信号类型'].map(signal_order)
        df = df.sort_values('排序')
        df = df.drop('排序', axis=1)

        # 导出CSV
        output_path = os.path.join(os.path.dirname(os.path.dirname(__file__)), filename)
        df.to_csv(output_path, index=False, encoding='utf-8-sig')

        print(f"\n结果已导出到: {output_path}")
        print(f"共 {len(df)} 条记录")

        # 显示前10条结果
        print("\n前10只股票预览:")
        print("=" * 100)
        for idx, row in df.head(10).iterrows():
            print(f"{row['股票代码']} {row['股票名称']:8s} | {row['信号类型']:8s} | "
                  f"趋势:{row['长周期趋势']:8s} RSI:{row['RSI']:5s} | {row['最新价格']}")
        print("=" * 100)

    def print_summary(self):
        """打印统计摘要"""
        if len(self.results) == 0:
            print("没有符合条件的股票")
            return

        df = pd.DataFrame(self.results)

        print("\n" + "=" * 80)
        print("三重滤网选股统计摘要")
        print("=" * 80)
        print(f"符合条件的股票总数: {len(df)}")

        # 统计各信号类型数量
        print("\n信号类型分布:")
        signal_counts = df['信号类型'].value_counts()
        for signal, count in signal_counts.items():
            print(f"  {signal}: {count}只")

        # 统计趋势分布
        print("\n长周期趋势分布:")
        trend_counts = df['长周期趋势'].value_counts()
        for trend, count in trend_counts.items():
            trend_name = {'up': '上涨', 'down': '下跌', 'neutral': '震荡'}.get(trend, trend)
            print(f"  {trend_name}: {count}只")

        print("=" * 80)


def main():
    """主函数"""
    print("=" * 80)
    print("A股三重滤网选股系统")
    print("基于亚历山大·埃尔德博士的理论")
    print("核心：顺大势，逆小势，等突破")
    print("=" * 80)

    # 创建选股器
    selector = TripleScreenSelector(data_source="akshare")

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
