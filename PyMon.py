import sys
from PyQt5.QtWidgets import *
from kiwoomPytrader import Kiwoom
import time
import pandas as pd
import datetime
from datetime import *
import sqlite3
import time

MARKET_KOSPI   = 0
MARKET_KOSDAQ  = 10

class PyMon:
    def __init__(self):
        self.kiwoom = Kiwoom.Kiwoom()
        self.kiwoom.comm_connect()
        self.get_code_list()

    def get_code_list(self):
        self.kospi_codes = self.kiwoom.get_code_list_by_market(MARKET_KOSPI)
        #self.kosdaq_codes = self.kiwoom.get_code_list_by_market(MARKET_KOSDAQ)


    def get_ohlcv(self, code, start):
        self.kiwoom.ohlcv = {'date': [], 'open': [], 'high': [], 'low': [], 'close': [], 'volume': []}

        self.kiwoom.set_input_value("종목코드", code)
        self.kiwoom.set_input_value("기준일자", start)
        self.kiwoom.set_input_value("수정주가구분", 1)
        self.kiwoom.comm_rq_data("opt10081_req", "opt10081", 0, "0101")
        time.sleep(0.5)

        df = pd.DataFrame(self.kiwoom.ohlcv, columns=['open', 'high', 'low', 'close', 'volume'],
                       index = self.kiwoom.ohlcv['date'])
        # 1000원 미만 주식 제외
        global skipStock;
        if df.iloc[0]['close'] < 1000:
            skipStock=1;
        else:
            skipStock=0;
        return df

    def check_speedy_rising_volume(self, code):
        today = datetime.datetime.today().strftime("%Y%m%d")
        df = self.get_ohlcv(code, today)
        volumes = df['volume']

        if len(volumes) < 21:
            return False

        sum_vol20 = 0
        today_vol = 0

        for i, vol in enumerate(volumes):
            if i == 0:
                today_vol = vol
            elif 1 <= i <= 20:
                sum_vol20 += vol
            else:
                break

        avg_vol20 = sum_vol20 / 20
        if today_vol > avg_vol20 * 10:
            return True

    def update_buy_list(self, buy_list):
        f = open("buy_list.txt", "wt")
        for code in buy_list:
            f.writelines("매수;", code, ";시장가;10;0;매수전\n")
        f.close()

    def getCandleData(self, stockCode):
        self.kiwoom.ohlcv = {'date': [], 'open': [], 'high': [], 'low': [], 'close': [], 'volume': []}
        self.kiwoom.set_input_value("종목코드", stockCode)
        # 날짜 계산
        daynow = datetime.now()
        daynow1 = daynow.year
        daynow2 = daynow.month
        if daynow2 < 10:
            daynow2 = "0%s" % daynow2
        daynow3 = daynow.day
        if daynow3 < 10:
            daynow3 = "0%s" % daynow3
        daynow4 = "%s%s%s" % (daynow1, daynow2, daynow3)

        # opt100081 TR request
        self.kiwoom.set_input_value("종목코드", stockCode)
        self.kiwoom.set_input_value("기준일자", daynow4)
        self.kiwoom.set_input_value("수정주가구분", 1)
        self.kiwoom.comm_rq_data("opt10081_req", "opt10081", 0, "0101")
        while self.kiwoom.remained_data == True:
            time.sleep(0.2)
            self.kiwoom.set_input_value("종목코드", stockCode)
            self.kiwoom.set_input_value("기준일자", daynow4)
            self.kiwoom.set_input_value("수정주가구분", 1)
            self.kiwoom.comm_rq_data("opt10081_req","opt10081",2,"0101")

        # DB 저장
        df = pd.DataFrame(self.kiwoom.ohlcv,
                          columns=['open', 'high', 'low', 'close', 'volume'], index=self.kiwoom.ohlcv['date'])
        con = sqlite3.connect("C:/Users/***/Documents/Pycharm/kiwoomPytrader/candleData/stock.db")
        df.to_sql(stockCode, con, if_exists='replace')

    def getRealData(self, stockCode):
        self.kiwoom.set_input_value("종목코드", stockCode)
        self.kiwoom.comm_rq_data("opt10001_req","opt10001",0,"0101")


    def run(self):
        # buy_list = []
        # num = len(self.kospi_codes)
        # codes = self.kospi_codes
        # cnt = 0
        # for code in codes:
        #     print(cnt, "/", num)
        #     print("code : ", code)
        #     df = self.get_ohlcv(code, datetime.now())
        #     if skipStock == 1:
        #         continue
        #     con = sqlite3.connect("C:/Users/***/Documents/Pycharm/kiwoomPytrader/candleData/stock.db")
        #     df.to_sql(code, con, if_exists='replace')
        #     time.sleep(3.6)
        #     cnt = cnt+1

        print('end')
        # for i, code in enumerate(self.kosdaq_codes):
        #     if i == 499:
        #         time.sleep(10)
        #     elif i == 999:
        #         time.sleep(10)
        #     print(i, '/', num)
        #     if self.check_speedy_rising_volume(code):
        #         buy_list.append(code)

        # self.update_buy_list(buy_list)


if __name__ == "__main__":
    app = QApplication(sys.argv)
    pymon = PyMon()
    pymon.run()
