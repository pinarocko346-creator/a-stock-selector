"""
数据获取模块
支持从多个数据源获取A股数据
"""
import pandas as pd
import numpy as np
from datetime import datetime, timedelta
from typing import List, Optional


class StockDataFetcher:
    """A股数据获取器"""

    def __init__(self, data_source: str = "akshare"):
        """
        初始化数据获取器

        Args:
            data_source: 数据源，支持 'akshare', 'tushare', 'baostock'
        """
        self.data_source = data_source

    def get_all_stock_codes(self) -> List[str]:
        """
        获取所有A股股票代码

        Returns:
            股票代码列表
        """
        try:
            if self.data_source == "akshare":
                return self._get_codes_from_akshare()
            else:
                # 如果没有安装数据源，返回示例数据
                return self._get_sample_codes()
        except Exception as e:
            print(f"获取股票代码失败: {e}")
            return self._get_sample_codes()

    def _get_codes_from_akshare(self) -> List[str]:
        """从akshare获取股票代码"""
        try:
            import akshare as ak
            stock_info = ak.stock_info_a_code_name()
            # 过滤掉ST、退市股票
            stock_info = stock_info[~stock_info['name'].str.contains('ST|退')]
            return stock_info['code'].tolist()
        except ImportError:
            print("未安装akshare，使用示例数据")
            return self._get_sample_codes()
        except Exception as e:
            print(f"akshare获取数据失败: {e}")
            return self._get_sample_codes()

    def _get_sample_codes(self) -> List[str]:
        """返回示例股票代码（用于测试）"""
        return [
            '000001',  # 平安银行
            '000002',  # 万科A
            '000333',  # 美的集团
            '000651',  # 格力电器
            '000858',  # 五粮液
            '600000',  # 浦发银行
            '600036',  # 招商银行
            '600519',  # 贵州茅台
            '600887',  # 伊利股份
            '601318',  # 中国平安
        ]

    def get_stock_data(self, code: str, start_date: str = None, end_date: str = None) -> Optional[pd.DataFrame]:
        """
        获取单只股票的历史数据

        Args:
            code: 股票代码
            start_date: 开始日期，格式'YYYY-MM-DD'
            end_date: 结束日期，格式'YYYY-MM-DD'

        Returns:
            包含OHLCV数据的DataFrame
        """
        if start_date is None:
            start_date = (datetime.now() - timedelta(days=365)).strftime('%Y-%m-%d')
        if end_date is None:
            end_date = datetime.now().strftime('%Y-%m-%d')

        try:
            if self.data_source == "akshare":
                return self._get_data_from_akshare(code, start_date, end_date)
            else:
                return self._generate_sample_data(code, start_date, end_date)
        except Exception as e:
            print(f"获取股票 {code} 数据失败: {e}")
            return None

    def _get_data_from_akshare(self, code: str, start_date: str, end_date: str) -> Optional[pd.DataFrame]:
        """从akshare获取股票数据"""
        try:
            import akshare as ak

            # 根据代码判断市场
            if code.startswith('6'):
                symbol = f"sh{code}"
            else:
                symbol = f"sz{code}"

            # 获取日线数据
            df = ak.stock_zh_a_hist(symbol=code, period="daily", start_date=start_date.replace('-', ''),
                                     end_date=end_date.replace('-', ''), adjust="qfq")

            if df is None or len(df) == 0:
                return None

            # 重命名列
            df = df.rename(columns={
                '日期': 'date',
                '开盘': 'open',
                '最高': 'high',
                '最低': 'low',
                '收盘': 'close',
                '成交量': 'volume',
                '成交额': 'amount'
            })

            # 选择需要的列
            df = df[['date', 'open', 'high', 'low', 'close', 'volume']]
            df['date'] = pd.to_datetime(df['date'])
            df = df.set_index('date')

            # 转换数据类型
            for col in ['open', 'high', 'low', 'close', 'volume']:
                df[col] = pd.to_numeric(df[col], errors='coerce')

            return df

        except ImportError:
            print(f"未安装akshare，为股票 {code} 生成示例数据")
            return self._generate_sample_data(code, start_date, end_date)
        except Exception as e:
            print(f"akshare获取股票 {code} 数据失败: {e}")
            return None

    def _generate_sample_data(self, code: str, start_date: str, end_date: str) -> pd.DataFrame:
        """生成示例数据（用于测试）"""
        dates = pd.date_range(start=start_date, end=end_date, freq='D')
        dates = dates[dates.dayofweek < 5]  # 只保留工作日

        np.random.seed(int(code))  # 使用股票代码作为随机种子

        # 生成随机价格数据
        base_price = 10 + np.random.rand() * 90
        prices = [base_price]

        for _ in range(len(dates) - 1):
            change = np.random.randn() * 0.02  # 2%的日波动
            new_price = prices[-1] * (1 + change)
            prices.append(new_price)

        prices = np.array(prices)

        # 生成OHLC数据
        data = {
            'open': prices * (1 + np.random.randn(len(prices)) * 0.01),
            'high': prices * (1 + abs(np.random.randn(len(prices))) * 0.02),
            'low': prices * (1 - abs(np.random.randn(len(prices))) * 0.02),
            'close': prices,
            'volume': np.random.randint(1000000, 10000000, len(prices))
        }

        df = pd.DataFrame(data, index=dates)
        return df

    def get_stock_name(self, code: str) -> str:
        """
        获取股票名称

        Args:
            code: 股票代码

        Returns:
            股票名称
        """
        try:
            if self.data_source == "akshare":
                import akshare as ak
                stock_info = ak.stock_info_a_code_name()
                name = stock_info[stock_info['code'] == code]['name'].values
                if len(name) > 0:
                    return name[0]
        except:
            pass

        # 返回默认名称
        return f"股票{code}"
