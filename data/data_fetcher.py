"""
数据获取模块
支持从多个数据源获取A股数据 - 优先akshare，失败自动切换到baostock
"""
import pandas as pd
import numpy as np
from datetime import datetime, timedelta
from typing import List, Optional


class StockDataFetcher:
    """A股数据获取器 - 自动切换数据源"""

    def __init__(self, data_source: str = "auto"):
        self.data_source = data_source
        self._baostock_logged_in = False

    def _baostock_login(self):
        if not self._baostock_logged_in:
            try:
                import baostock as bs
                result = bs.login()
                if result.error_code == '0':
                    self._baostock_logged_in = True
                    return True
            except:
                pass
        return self._baostock_logged_in

    def get_all_stock_codes(self) -> List[str]:
        try:
            codes = self._get_codes_from_akshare()
            if codes and len(codes) > 100:
                return codes
        except Exception as e:
            print(f"akshare获取失败，尝试baostock: {e}")

        try:
            codes = self._get_codes_from_baostock()
            if codes and len(codes) > 100:
                return codes
        except Exception as e:
            print(f"baostock获取失败，使用示例数据: {e}")

        return self._get_sample_codes()

    def _get_codes_from_akshare(self) -> List[str]:
        import akshare as ak
        stock_info = ak.stock_info_a_code_name()
        stock_info = stock_info[~stock_info['name'].str.contains('ST|退', na=False)]
        return stock_info['code'].tolist()

    def _get_codes_from_baostock(self) -> List[str]:
        if not self._baostock_login():
            return []
        import baostock as bs
        rs = bs.query_all_stock(day=datetime.now().strftime('%Y-%m-%d'))
        codes = []
        while (rs.error_code == '0') & rs.next():
            code = rs.get_row_data()[0]
            if '.' in code:
                code = code.split('.')[-1]
            codes.append(code)
        return codes

    def _get_sample_codes(self) -> List[str]:
        return ['000001', '000002', '000333', '000651', '000858', '600000', '600036', '600519', '600887', '601318']

    def get_stock_data(self, code: str, start_date: str = None, end_date: str = None) -> Optional[pd.DataFrame]:
        if start_date is None:
            start_date = (datetime.now() - timedelta(days=365)).strftime('%Y-%m-%d')
        if end_date is None:
            end_date = datetime.now().strftime('%Y-%m-%d')

        if self.data_source == "akshare":
            return self._get_data_from_akshare(code, start_date, end_date)
        elif self.data_source == "baostock":
            return self._get_data_from_baostock(code, start_date, end_date)
        elif self.data_source == "sample":
            return self._generate_sample_data(code, start_date, end_date)
        else:  # auto模式
            try:
                df = self._get_data_from_akshare(code, start_date, end_date)
                if df is not None and len(df) > 0:
                    return df
            except Exception as e:
                print(f"akshare获取{code}失败，尝试baostock")

            try:
                df = self._get_data_from_baostock(code, start_date, end_date)
                if df is not None and len(df) > 0:
                    return df
            except Exception as e:
                print(f"baostock获取{code}失败，使用示例数据")

            return self._generate_sample_data(code, start_date, end_date)

    def _get_data_from_akshare(self, code: str, start_date: str, end_date: str) -> Optional[pd.DataFrame]:
        import akshare as ak
        df = ak.stock_zh_a_hist(symbol=code, period="daily",
                                start_date=start_date.replace('-', ''),
                                end_date=end_date.replace('-', ''),
                                adjust="qfq")
        if df is None or len(df) == 0:
            return None
        df = df.rename(columns={
            '日期': 'date', '开盘': 'open', '最高': 'high', '最低': 'low', '收盘': 'close', '成交量': 'volume'
        })
        df = df[['date', 'open', 'high', 'low', 'close', 'volume']]
        df['date'] = pd.to_datetime(df['date'])
        df = df.set_index('date')
        for col in ['open', 'high', 'low', 'close', 'volume']:
            df[col] = pd.to_numeric(df[col], errors='coerce')
        return df

    def _get_data_from_baostock(self, code: str, start_date: str, end_date: str) -> Optional[pd.DataFrame]:
        if not self._baostock_login():
            return None
        import baostock as bs
        bs_code = f"sh.{code}" if code.startswith('6') else f"sz.{code}"
        rs = bs.query_history_k_data_plus(bs_code, "date,open,high,low,close,volume",
                                          start_date=start_date, end_date=end_date, frequency="d", adjustflag="3")
        data_list = []
        while (rs.error_code == '0') & rs.next():
            data_list.append(rs.get_row_data())
        if len(data_list) == 0:
            return None
        df = pd.DataFrame(data_list, columns=['date', 'open', 'high', 'low', 'close', 'volume'])
        for col in ['open', 'high', 'low', 'close', 'volume']:
            df[col] = pd.to_numeric(df[col], errors='coerce')
        df['date'] = pd.to_datetime(df['date'])
        df = df.set_index('date')
        return df

    def _generate_sample_data(self, code: str, start_date: str, end_date: str) -> pd.DataFrame:
        dates = pd.date_range(start=start_date, end=end_date, freq='D')
        dates = dates[dates.dayofweek < 5]
        np.random.seed(int(code))
        base_price = 10 + np.random.rand() * 90
        prices = [base_price]
        for _ in range(len(dates) - 1):
            prices.append(prices[-1] * (1 + np.random.randn() * 0.02))
        prices = np.array(prices)
        data = {
            'open': prices * (1 + np.random.randn(len(prices)) * 0.01),
            'high': prices * (1 + abs(np.random.randn(len(prices))) * 0.02),
            'low': prices * (1 - abs(np.random.randn(len(prices))) * 0.02),
            'close': prices,
            'volume': np.random.randint(1000000, 10000000, len(prices))
        }
        return pd.DataFrame(data, index=dates)

    def get_stock_name(self, code: str) -> str:
        try:
            import akshare as ak
            stock_info = ak.stock_info_a_code_name()
            name = stock_info[stock_info['code'] == code]['name'].values
            if len(name) > 0:
                return name[0]
        except:
            pass
        return f"股票{code}"
