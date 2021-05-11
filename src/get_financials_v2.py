import yfinance as yf
import yahoo_fin.stock_info as si
import pandas as pd
import requests
from math import isnan
from bs4 import BeautifulSoup


class Financials:
    def __init__(self, stock_batch):
        self.stock_batch = []
        self.batch_earnings = []
        self.batch_stats = []
        self.batch_info = []
        self.yf_tickers = []
        for s in stock_batch:
            def init_filter(stock_name):
                try:
                    self.batch_info.append(si.get_quote_table(s))
                    df = pd.DataFrame(si.get_earnings_history(s))
                    if not df.empty:
                        self.batch_earnings.append(df)
                        self.batch_stats.append(si.get_stats(s))
                        self.stock_batch.append(s)
                    else:
                        pass
                except (KeyError, IndexError, ValueError, TypeError) as e:
                    #Skip stocks that return missing information
                    pass
            try:
                try:
                    init_filter(s + '.TO')
                except:
                    init_filter(s + '.V')
            except:
                init_filter(s)

        self.financials_dict = {}
        self.m = {'K': 3, 'M': 6, 'B': 9, 'T': 12}
        pass

    def __repr__(self):
        return f'<class Financials imported {len(self.stock_batch)} tickers.>'

    def get_financial_data(self):
        len_batch = self._filter_tickers()
        print(f'<Value Invest found {len_batch} useable tickers.>')
        for idx, ft in enumerate(self.stock_batch):
            try:
                self.financials_dict[ft] = {}
                p2b = self._get_price2book(self.yf_tickers[idx])
                pe = self._get_peRatio(self.batch_info[idx])
                self.financials_dict[ft]['priceToBook'] = p2b
                self.financials_dict[ft]['PEratio_TTM'] = pe
                self.financials_dict[ft]['blended_mult'] = round(p2b * pe, 2)
                self.financials_dict[ft]['currentRatio'] = self._get_currentRatio(self.batch_stats[idx])
                self.financials_dict[ft]['debt2assets'] = self._debt2assets(ft)
                self.financials_dict[ft]['dividendYield'] = round(self._divYield(self.yf_tickers[idx]), 2)
            except TypeError:
                pass

        for name in self.stock_batch:
            print(f'{name.upper()}:\n{self.financials_dict[name]}')

    def value_screener(self):
        self.get_financial_data()

        def rules(stock):
            sf = self.financials_dict[stock]

            # try:
            if sf['currentRatio'] > 1.5 \
                    and sf['debt2assets'] <= 1.0 \
                    and sf['PEratio_TTM'] <= 15 \
                    and sf['priceToBook'] <= 1.5 \
                    and sf['dividendYield'] > 1.0 \
                    and sf['blended_mult'] <= 22.5:
                return True
            # except KeyError:
            #     return False
            else:
                return False

        s = [b for idx, b in enumerate(self.stock_batch)
             if rules(list(self.financials_dict.keys())[idx])]

        output_dict = {}
        for gs in s:
            output_dict[gs] = self.financials_dict[gs]
        return output_dict

    def _filter_tickers(self):
        """
         - Verify stocks have P/E ratios
         - Verify company isn't too young & has no neg earnings in last year
        """
        # self.stock_batch = [b for idx, b in enumerate(self.stock_batch)
        #                     if self.batch_info[idx]]

        sb = []
        bi = []
        be = []
        b_st = []
        for idx, b in enumerate(self.stock_batch):
            try:
                if self.batch_info[idx]:
                    if self.batch_info[idx]['PE Ratio (TTM)'] is not None:
                        be_df = pd.DataFrame(si.get_earnings_history(b))
                        if len(be_df['epsactual'].tolist()) > 8:
                            df_batch = [be.dropna(subset=['epsactual']).iloc[:4] for be in self.batch_earnings]
                            if not (df_batch[idx]['epsactual'] < 0).values.any():
                                sb.append(b)
                                bi.append(self.batch_info[idx])
                                be.append(self.batch_earnings[idx])
                                b_st.append(self.batch_stats[idx])
                            else:
                                pass
                        else:
                            pass
                    else:
                        pass
                else:
                    pass
            except KeyError:
                pass
        self.stock_batch = sb
        self.batch_info = bi
        self.batch_earnings = be
        self.batch_stats = b_st
        self.yf_tickers = [yf.Ticker(x) for x in sb]
        return len(sb)

    def _get_price2book(self, yft):
        return round(yft.info['priceToBook'], 2)

    def _get_currentRatio(self, bs):
        return float(bs.loc[bs['Attribute'] == 'Current Ratio (mrq)']['Value'].values)

    def _debt2assets(self, stock):
        try:
            def get_debt(s):
                page = requests.get(f"https://ca.finance.yahoo.com/quote/{s}/key-statistics?p={s}")
                soup = BeautifulSoup(page.content, "html.parser")
                stock_stats = soup.find_all('tr')
                total_debt = [x.text for x in stock_stats if 'Total Debt' in str(x)][0]
                total_debt = total_debt.split(')')[1]
                return int(float(total_debt[:-1]) * 10 ** self.m[total_debt[-1]] / 1000)

            def get_assets(s):
                page = requests.get(f"https://ca.finance.yahoo.com/quote/{s}/balance-sheet?p={s}")
                soup = BeautifulSoup(page.content, "html.parser")
                stock_stats = soup.find_all(class_='D(tbr) fi-row Bgc($hoverBgColor):h')
                total_assets = list([x for x in stock_stats if 'Total Assets' in str(x)][0])[1].text
                return int(total_assets.replace(',', ''))
            return round(get_debt(stock) / get_assets(stock), 2)
        except (IndexError, ValueError) as e:
            return 9999

    def _get_peRatio(self, stock):
        return stock['PE Ratio (TTM)']

    def _divYield(self, yft):
        return yft.info['dividendYield'] * 100
