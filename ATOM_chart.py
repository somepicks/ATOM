import pandas as pd
from PyQt5.QtWidgets import *
from PyQt5.QtCore import *
from PyQt5.QtGui import *
import numpy as np
import pyqtgraph as pg
import chart_real
import random
import os
import sys
sys.path.append(os.path.dirname(os.path.abspath(os.path.dirname(__file__))))
import color as cl
from pprint import pprint
class Window(QWidget):
    def __init__(self,df,dict_plot,market,ticker):
        super().__init__()
        # self.sub_chart = graph_real.Graph()
        # xValue = 0
        # dict_plot = 0
        QW_main = QWidget()
        QVB_main = QVBoxLayout()
        # self.setCentralWidget(QW_main)

        pg_graph = pg.GraphicsLayoutWidget(self)
        # splitter.addWidget(QPB2)
        QVB_main.addWidget(pg_graph)
        self.setLayout(QVB_main)
        # print(df)
        # print(dict_plot)
        # bottomAxis_0 = pg.AxisItem(orientation='bottom')
        # bottomAxis_1 = pg.AxisItem(orientation='bottom')
        # bottomAxis_2 = pg.AxisItem(orientation='bottom')
        # bottomAxis_3 = pg.AxisItem(orientation='bottom')
        # bottomAxis_4 = pg.AxisItem(orientation='bottom')
        global p0_0
        global p1_0
        global p2_0
        global p3_0
        global p0_1
        global p1_1
        global p2_1
        global p3_1
        global p0_2
        global p1_2
        global p2_2
        global p3_2
        global p0_3
        global p1_3
        global p2_3
        global p3_3
        global p0_4
        global p1_4
        global p2_4
        global p3_4

        # p0_0 = pg_graph.addPlot(row=0, col=0, title='p0_0', axisItems={bottomAxis_0})
        if market == '코인':
            p0_0 = pg_graph.addPlot(row=0, col=0, title='p0_0', axisItems={'bottom': pg.DateAxisItem()})
            p1_0 = pg_graph.addPlot(row=1, col=0, title='p1_0', axisItems={'bottom': pg.DateAxisItem()})
            p2_0 = pg_graph.addPlot(row=2, col=0, title='p2_0', axisItems={'bottom': pg.DateAxisItem()})
            p3_0 = pg_graph.addPlot(row=3, col=0, title='p3_0', axisItems={'bottom': pg.DateAxisItem()})
            p0_1 = pg_graph.addPlot(row=0, col=1, title='p0_1', axisItems={'bottom': pg.DateAxisItem()})
            p1_1 = pg_graph.addPlot(row=1, col=1, title='p1_1', axisItems={'bottom': pg.DateAxisItem()})
            p2_1 = pg_graph.addPlot(row=2, col=1, title='p2_1', axisItems={'bottom': pg.DateAxisItem()})
            p3_1 = pg_graph.addPlot(row=3, col=1, title='p3_1', axisItems={'bottom': pg.DateAxisItem()})
            p0_2 = pg_graph.addPlot(row=0, col=2, title='p0_2', axisItems={'bottom': pg.DateAxisItem()})
            p1_2 = pg_graph.addPlot(row=1, col=2, title='p1_2', axisItems={'bottom': pg.DateAxisItem()})
            p2_2 = pg_graph.addPlot(row=2, col=2, title='p2_2', axisItems={'bottom': pg.DateAxisItem()})
            p3_2 = pg_graph.addPlot(row=3, col=2, title='p3_2', axisItems={'bottom': pg.DateAxisItem()})
            p0_3 = pg_graph.addPlot(row=0, col=3, title='p0_3', axisItems={'bottom': pg.DateAxisItem()})
            p1_3 = pg_graph.addPlot(row=1, col=3, title='p1_3', axisItems={'bottom': pg.DateAxisItem()})
            p2_3 = pg_graph.addPlot(row=2, col=3, title='p2_3', axisItems={'bottom': pg.DateAxisItem()})
            p3_3 = pg_graph.addPlot(row=3, col=3, title='p3_3', axisItems={'bottom': pg.DateAxisItem()})
            p0_4 = pg_graph.addPlot(row=0, col=4, title='p0_4', axisItems={'bottom': pg.DateAxisItem()})
            p1_4 = pg_graph.addPlot(row=1, col=4, title='p1_4', axisItems={'bottom': pg.DateAxisItem()})
            p2_4 = pg_graph.addPlot(row=2, col=4, title='p2_4', axisItems={'bottom': pg.DateAxisItem()})
            p3_4 = pg_graph.addPlot(row=3, col=4, title='p3_4', axisItems={'bottom': pg.DateAxisItem()})


        elif market == '국내주식' or market == '국내선옵':
            self.bottomAxis0_0 = pg.AxisItem(orientation='bottom')
            p0_0 = pg_graph.addPlot(row=0, col=0, title='p0_0', axisItems={'bottom':self.bottomAxis0_0})
            # p0_0 = pg_graph.addPlot(row=0, col=0, title='p0_0', axisItems={'bottom': pg.DateAxisItem()})#기준
            p1_0 = pg_graph.addPlot(row=1, col=0, title='p1_0', axisItems={'bottom': pg.AxisItem(orientation='bottom')})
            p2_0 = pg_graph.addPlot(row=2, col=0, title='p2_0', axisItems={'bottom': pg.AxisItem(orientation='bottom')})
            p3_0 = pg_graph.addPlot(row=3, col=0, title='p3_0', axisItems={'bottom': pg.AxisItem(orientation='bottom')})
            p0_1 = pg_graph.addPlot(row=0, col=1, title='p0_1', axisItems={'bottom': pg.AxisItem(orientation='bottom')})
            p1_1 = pg_graph.addPlot(row=1, col=1, title='p1_1', axisItems={'bottom': pg.AxisItem(orientation='bottom')})
            p2_1 = pg_graph.addPlot(row=2, col=1, title='p2_1', axisItems={'bottom': pg.AxisItem(orientation='bottom')})
            p3_1 = pg_graph.addPlot(row=3, col=1, title='p3_1', axisItems={'bottom': pg.AxisItem(orientation='bottom')})
            p0_2 = pg_graph.addPlot(row=0, col=2, title='p0_2', axisItems={'bottom': pg.AxisItem(orientation='bottom')})
            p1_2 = pg_graph.addPlot(row=1, col=2, title='p1_2', axisItems={'bottom': pg.AxisItem(orientation='bottom')})
            p2_2 = pg_graph.addPlot(row=2, col=2, title='p2_2', axisItems={'bottom': pg.AxisItem(orientation='bottom')})
            p3_2 = pg_graph.addPlot(row=3, col=2, title='p3_2', axisItems={'bottom': pg.AxisItem(orientation='bottom')})
            p0_3 = pg_graph.addPlot(row=0, col=3, title='p0_3', axisItems={'bottom': pg.AxisItem(orientation='bottom')})
            p1_3 = pg_graph.addPlot(row=1, col=3, title='p1_3', axisItems={'bottom': pg.AxisItem(orientation='bottom')})
            p2_3 = pg_graph.addPlot(row=2, col=3, title='p2_3', axisItems={'bottom': pg.AxisItem(orientation='bottom')})
            p3_3 = pg_graph.addPlot(row=3, col=3, title='p3_3', axisItems={'bottom': pg.AxisItem(orientation='bottom')})
            p0_4 = pg_graph.addPlot(row=0, col=4, title='p0_4', axisItems={'bottom': pg.AxisItem(orientation='bottom')})
            p1_4 = pg_graph.addPlot(row=1, col=4, title='p1_4', axisItems={'bottom': pg.AxisItem(orientation='bottom')})
            p2_4 = pg_graph.addPlot(row=2, col=4, title='p2_4', axisItems={'bottom': pg.AxisItem(orientation='bottom')})
            p3_4 = pg_graph.addPlot(row=3, col=4, title='p3_4', axisItems={'bottom': pg.AxisItem(orientation='bottom')})

        p0_0.addLegend()
        p1_0.addLegend()
        p2_0.addLegend()
        p3_0.addLegend()
        p0_1.addLegend()
        p1_1.addLegend()
        p2_1.addLegend()
        p3_1.addLegend()
        p0_2.addLegend()
        p1_2.addLegend()
        p2_2.addLegend()
        p3_2.addLegend()
        p0_3.addLegend()
        p1_3.addLegend()
        p2_3.addLegend()
        p3_3.addLegend()
        p0_4.addLegend()
        p1_4.addLegend()
        p2_4.addLegend()
        p3_4.addLegend()


        p0_0.showGrid(x=True, y=True)
        p1_0.showGrid(x=True, y=True)
        p2_0.showGrid(x=True, y=True)
        p3_0.showGrid(x=True, y=True)
        p0_1.showGrid(x=True, y=True)
        p1_1.showGrid(x=True, y=True)
        p2_1.showGrid(x=True, y=True)
        p3_1.showGrid(x=True, y=True)
        p0_2.showGrid(x=True, y=True)
        p1_2.showGrid(x=True, y=True)
        p2_2.showGrid(x=True, y=True)
        p3_2.showGrid(x=True, y=True)
        p0_3.showGrid(x=True, y=True)
        p1_3.showGrid(x=True, y=True)
        p2_3.showGrid(x=True, y=True)
        p3_3.showGrid(x=True, y=True)
        p0_4.showGrid(x=True, y=True)
        p1_4.showGrid(x=True, y=True)
        p2_4.showGrid(x=True, y=True)
        p3_4.showGrid(x=True, y=True)
        p0_0.setXLink(p0_0)
        p1_0.setXLink(p0_0)
        p2_0.setXLink(p0_0)
        p3_0.setXLink(p0_0)
        p0_1.setXLink(p0_0)
        p1_1.setXLink(p0_0)
        p2_1.setXLink(p0_0)
        p3_1.setXLink(p0_0)
        p0_2.setXLink(p0_0)
        p1_2.setXLink(p0_0)
        p2_2.setXLink(p0_0)
        p3_2.setXLink(p0_0)
        p0_3.setXLink(p0_0)
        p1_3.setXLink(p0_0)
        p2_3.setXLink(p0_0)
        p3_3.setXLink(p0_0)
        p0_4.setXLink(p0_0)
        p1_4.setXLink(p0_0)
        p2_4.setXLink(p0_0)
        p3_4.setXLink(p0_0)

        pg.setConfigOptions(antialias=True)
        # bottomAxis_0.setTicks(xtickts)
        # bottomAxis_1.setTicks(xtickts)
        # bottomAxis_2.setTicks(xtickts)
        # bottomAxis_3.setTicks(xtickts)
        # bottomAxis_4.setTicks(xtickts)
        #     self.crosshair8()
        #

        # xValue = df.index.tolist()
        # x_dict = dict(enumerate(xValue))
        # ticks = list(zip(x_dict.keys(), x_dict.values()))
        # xax = pg.getAxis('bottom')
        # xax.setTicks(ticks)
        # df.index = pd.to_datetime(df.index)
        if market == '코인':
            unix_ts = [x.timestamp() for x in pd.to_datetime(df.index)]
        elif market == '국내주식' or market == '국내선옵':
            # unix_ts = [x.timestamp() for x in pd.to_datetime(df.index)]  #기준

            list_x = [dt.strftime('%H:%M') if dt.minute % 60 == 0 else '' for dt in df.index]
            # print(f"{len(df)=}")
            # list_num = np.arange(len(df))
            # unix_ts = dict(zip(list_num,list_x))
            unix_ts = dict(enumerate(list_x))
            self.bottomAxis0_0.setTicks([unix_ts.items()])
            unix_ts=list(unix_ts.keys())
            # list_x = [dt.strftime('%H:%M') if dt.minute % 60 == 0 else '' for dt in df.index]
            # list_num = np.arange(len(df))
            # unix_ts = dict(zip(list_num,list_x))
            # unix_ts = dict(enumerate(list_x))
            # self.bottomAxis0_0.setTicks([unix_ts.items()])
        # xValue = np.arange(len(df.index.tolist()))
        for plot_num in dict_plot.keys():  # {'p1_0_0':{'현재가':array([26600.,26600.,]))}, 'p1_0_1':.......}
            # if plot_num == 'p0_0':
            #     x_axis = unix_ts
            #     print('unix_ts',unix_ts)
            #     print('axis_change',plot_num)
            #
            # else:
            #     x_axis = xValue
            for factor, data in dict_plot[plot_num].items():
                # try:
                    # if not data.size == np.count_nonzero(np.isnan(data)):  # data가 전부 nan으로 되어있지 않을 경우만
                    # #     print('is not nan')
                        if factor == '매수가' or factor == '매도가' or factor == '전략매수' or factor == '전략매도' \
                                or factor == '진입신호' or factor == '청산신호':
                            if '매수가' in factor:
                                globals()[plot_num].plot(x=unix_ts, y=data, pen=None, symbolBrush=(200, 0, 0),
                                                         symbolPen=(51, 255, 51), symbol='t1', symbolSize=10,
                                                         name="진입")  # 마커
                            elif '매도가' in factor:
                                globals()[plot_num].plot(x=unix_ts, y=data, pen=None, symbolBrush=(0, 0, 200),
                                                         symbolPen=(51, 255, 51), symbol='t', symbolSize=10, name="청산")
                            elif '진입신호' in factor:
                                globals()[plot_num].plot(x=unix_ts, y=data, pen=None, symbolBrush=cl.pink, symbolPen='w',
                                                         symbol='t2', symbolSize=10, name="진입신호")
                            elif '청산신호' in factor:
                                globals()[plot_num].plot(x=unix_ts, y=data, pen=None, symbolBrush=cl.cyan,
                                                         symbolPen=(51, 255, 51), symbol='t3', symbolSize=10,
                                                         name="청산신호")
                            elif '전략매수' in factor:
                                globals()[plot_num].plot(x=unix_ts, y=data, pen=None, symbolBrush=cl.red_1,
                                                         symbolPen=cl.red_1, symbol='d', symbolSize=10, name="전략매수")
                            elif '전략매도' in factor:
                                globals()[plot_num].plot(x=unix_ts, y=data, pen=None, symbolBrush=cl.ygreen_2,
                                                         symbolPen=cl.ygreen_2, symbol='d', symbolSize=10, name="전략매도")
                        # elif '_' in factor: #언더바 색깔 다르게
                        #     globals()[plot_num].plot(x=unix_ts, y=data, pen=cl.dash_k,
                        #                              name=factor.replace('<', "＜"))  # 마커

                        else:
                            # try:
                                if '.cl' in factor:
                                    colors = 'cl=' + factor[factor.rindex('.cl') + 1:]  # cl.red 를 cl=cl.red 로 바꿈
                                    locals_dict_vars = {}
                                    exec(colors, None,
                                         locals_dict_vars)  # 그냥 exec로 하면 안됨 #https://jvvp.tistory.com/1162
                                    globals()[plot_num].plot(x=unix_ts, y=data, pen=locals_dict_vars.get('cl'),
                                                             name=factor[:factor.index('.cl')])  # 마커
                                elif '.fill' in factor:
                                    level = int(factor[factor.index('.fill') + 6:-1])
                                    globals()[plot_num].plot(x=unix_ts, y=data, pen=cl.cyan, fillLevel=level,
                                                             brush=(50, 50, 200, 200),
                                                             name=factor.replace('<', "＜"))  # 마커
                                else:
                                    globals()[plot_num].plot(x=unix_ts, y=data, pen=random.choice(cl.li),
                                                             name=factor.replace('<', "＜"))  # 마커 < 로 할 경우 짤림
                                    #
                            # except:
                            #     print(f'에러 - {factor}')
                            #     pass
                    # else:
                        # print(f'data 전부 nan = {factor}')
                        # pass
                # except:
                #     print(f'에러 - {plot_num}')
            globals()[plot_num].enableAutoRange() #실행 시 차트의 전체가 보여지도록
            p0_0.setTitle(f"{ticker}")

        # def crosshair8(self):
        self.vLine_p0_0 = pg.InfiniteLine()
        self.vLine_p1_0 = pg.InfiniteLine()
        self.vLine_p2_0 = pg.InfiniteLine()
        self.vLine_p3_0 = pg.InfiniteLine()
        self.vLine_p0_1 = pg.InfiniteLine()
        self.vLine_p1_1 = pg.InfiniteLine()
        self.vLine_p2_1 = pg.InfiniteLine()
        self.vLine_p3_1 = pg.InfiniteLine()
        self.vLine_p0_2 = pg.InfiniteLine()
        self.vLine_p1_2 = pg.InfiniteLine()
        self.vLine_p2_2 = pg.InfiniteLine()
        self.vLine_p3_2 = pg.InfiniteLine()
        self.vLine_p0_3 = pg.InfiniteLine()
        self.vLine_p1_3 = pg.InfiniteLine()
        self.vLine_p2_3 = pg.InfiniteLine()
        self.vLine_p3_3 = pg.InfiniteLine()
        self.vLine_p0_4 = pg.InfiniteLine()
        self.vLine_p1_4 = pg.InfiniteLine()
        self.vLine_p2_4 = pg.InfiniteLine()
        self.vLine_p3_4 = pg.InfiniteLine()

        self.vLine_p0_0.setPen(pg.mkPen(QColor(230, 230, 0), width=1))
        self.vLine_p1_0.setPen(pg.mkPen(QColor(230, 230, 0), width=1))
        self.vLine_p2_0.setPen(pg.mkPen(QColor(230, 230, 0), width=1))
        self.vLine_p3_0.setPen(pg.mkPen(QColor(230, 230, 0), width=1))
        self.vLine_p0_1.setPen(pg.mkPen(QColor(230, 230, 0), width=1))
        self.vLine_p1_1.setPen(pg.mkPen(QColor(230, 230, 0), width=1))
        self.vLine_p2_1.setPen(pg.mkPen(QColor(230, 230, 0), width=1))
        self.vLine_p3_1.setPen(pg.mkPen(QColor(230, 230, 0), width=1))
        self.vLine_p0_2.setPen(pg.mkPen(QColor(230, 230, 0), width=1))
        self.vLine_p1_2.setPen(pg.mkPen(QColor(230, 230, 0), width=1))
        self.vLine_p2_2.setPen(pg.mkPen(QColor(230, 230, 0), width=1))
        self.vLine_p3_2.setPen(pg.mkPen(QColor(230, 230, 0), width=1))
        self.vLine_p0_3.setPen(pg.mkPen(QColor(230, 230, 0), width=1))
        self.vLine_p1_3.setPen(pg.mkPen(QColor(230, 230, 0), width=1))
        self.vLine_p2_3.setPen(pg.mkPen(QColor(230, 230, 0), width=1))
        self.vLine_p3_3.setPen(pg.mkPen(QColor(230, 230, 0), width=1))
        self.vLine_p0_4.setPen(pg.mkPen(QColor(230, 230, 0), width=1))
        self.vLine_p1_4.setPen(pg.mkPen(QColor(230, 230, 0), width=1))
        self.vLine_p2_4.setPen(pg.mkPen(QColor(230, 230, 0), width=1))
        self.vLine_p3_4.setPen(pg.mkPen(QColor(230, 230, 0), width=1))


        self.hLine_p0_0 = pg.InfiniteLine(angle=0)
        self.hLine_p1_0 = pg.InfiniteLine(angle=0)
        self.hLine_p2_0 = pg.InfiniteLine(angle=0)
        self.hLine_p3_0 = pg.InfiniteLine(angle=0)
        self.hLine_p0_1 = pg.InfiniteLine(angle=0)
        self.hLine_p1_1 = pg.InfiniteLine(angle=0)
        self.hLine_p2_1 = pg.InfiniteLine(angle=0)
        self.hLine_p3_1 = pg.InfiniteLine(angle=0)
        self.hLine_p0_2 = pg.InfiniteLine(angle=0)
        self.hLine_p1_2 = pg.InfiniteLine(angle=0)
        self.hLine_p2_2 = pg.InfiniteLine(angle=0)
        self.hLine_p3_2 = pg.InfiniteLine(angle=0)
        self.hLine_p0_3 = pg.InfiniteLine(angle=0)
        self.hLine_p1_3 = pg.InfiniteLine(angle=0)
        self.hLine_p2_3 = pg.InfiniteLine(angle=0)
        self.hLine_p3_3 = pg.InfiniteLine(angle=0)
        self.hLine_p0_4 = pg.InfiniteLine(angle=0)
        self.hLine_p1_4 = pg.InfiniteLine(angle=0)
        self.hLine_p2_4 = pg.InfiniteLine(angle=0)
        self.hLine_p3_4 = pg.InfiniteLine(angle=0)
        self.hLine_p0_0.setPen(pg.mkPen(QColor(230, 230, 0), width=1))
        self.hLine_p1_0.setPen(pg.mkPen(QColor(230, 230, 0), width=1))
        self.hLine_p2_0.setPen(pg.mkPen(QColor(230, 230, 0), width=1))
        self.hLine_p3_0.setPen(pg.mkPen(QColor(230, 230, 0), width=1))
        self.hLine_p0_1.setPen(pg.mkPen(QColor(230, 230, 0), width=1))
        self.hLine_p1_1.setPen(pg.mkPen(QColor(230, 230, 0), width=1))
        self.hLine_p2_1.setPen(pg.mkPen(QColor(230, 230, 0), width=1))
        self.hLine_p3_1.setPen(pg.mkPen(QColor(230, 230, 0), width=1))
        self.hLine_p0_2.setPen(pg.mkPen(QColor(230, 230, 0), width=1))
        self.hLine_p1_2.setPen(pg.mkPen(QColor(230, 230, 0), width=1))
        self.hLine_p2_2.setPen(pg.mkPen(QColor(230, 230, 0), width=1))
        self.hLine_p3_2.setPen(pg.mkPen(QColor(230, 230, 0), width=1))
        self.hLine_p0_3.setPen(pg.mkPen(QColor(230, 230, 0), width=1))
        self.hLine_p1_3.setPen(pg.mkPen(QColor(230, 230, 0), width=1))
        self.hLine_p2_3.setPen(pg.mkPen(QColor(230, 230, 0), width=1))
        self.hLine_p3_3.setPen(pg.mkPen(QColor(230, 230, 0), width=1))
        self.hLine_p0_4.setPen(pg.mkPen(QColor(230, 230, 0), width=1))
        self.hLine_p1_4.setPen(pg.mkPen(QColor(230, 230, 0), width=1))
        self.hLine_p2_4.setPen(pg.mkPen(QColor(230, 230, 0), width=1))
        self.hLine_p3_4.setPen(pg.mkPen(QColor(230, 230, 0), width=1))


        p0_0.addItem(self.vLine_p0_0, ignoreBounds=True)
        p1_0.addItem(self.vLine_p1_0, ignoreBounds=True)
        p2_0.addItem(self.vLine_p2_0, ignoreBounds=True)
        p3_0.addItem(self.vLine_p3_0, ignoreBounds=True)
        p0_1.addItem(self.vLine_p0_1, ignoreBounds=True)
        p1_1.addItem(self.vLine_p1_1, ignoreBounds=True)
        p2_1.addItem(self.vLine_p2_1, ignoreBounds=True)
        p3_1.addItem(self.vLine_p3_1, ignoreBounds=True)
        p0_2.addItem(self.vLine_p0_2, ignoreBounds=True)
        p1_2.addItem(self.vLine_p1_2, ignoreBounds=True)
        p2_2.addItem(self.vLine_p2_2, ignoreBounds=True)
        p3_2.addItem(self.vLine_p3_2, ignoreBounds=True)
        p0_3.addItem(self.vLine_p0_3, ignoreBounds=True)
        p1_3.addItem(self.vLine_p1_3, ignoreBounds=True)
        p2_3.addItem(self.vLine_p2_3, ignoreBounds=True)
        p3_3.addItem(self.vLine_p3_3, ignoreBounds=True)
        p0_4.addItem(self.vLine_p0_4, ignoreBounds=True)
        p1_4.addItem(self.vLine_p1_4, ignoreBounds=True)
        p2_4.addItem(self.vLine_p2_4, ignoreBounds=True)
        p3_4.addItem(self.vLine_p3_4, ignoreBounds=True)
        p0_0.addItem(self.hLine_p0_0, ignoreBounds=True)
        p1_0.addItem(self.hLine_p1_0, ignoreBounds=True)
        p2_0.addItem(self.hLine_p2_0, ignoreBounds=True)
        p3_0.addItem(self.hLine_p3_0, ignoreBounds=True)
        p0_1.addItem(self.hLine_p0_1, ignoreBounds=True)
        p1_1.addItem(self.hLine_p1_1, ignoreBounds=True)
        p2_1.addItem(self.hLine_p2_1, ignoreBounds=True)
        p3_1.addItem(self.hLine_p3_1, ignoreBounds=True)
        p0_2.addItem(self.hLine_p0_2, ignoreBounds=True)
        p1_2.addItem(self.hLine_p1_2, ignoreBounds=True)
        p2_2.addItem(self.hLine_p2_2, ignoreBounds=True)
        p3_2.addItem(self.hLine_p3_2, ignoreBounds=True)
        p0_3.addItem(self.hLine_p0_3, ignoreBounds=True)
        p1_3.addItem(self.hLine_p1_3, ignoreBounds=True)
        p2_3.addItem(self.hLine_p2_3, ignoreBounds=True)
        p3_3.addItem(self.hLine_p3_3, ignoreBounds=True)
        p0_4.addItem(self.hLine_p0_4, ignoreBounds=True)
        p1_4.addItem(self.hLine_p1_4, ignoreBounds=True)
        p2_4.addItem(self.hLine_p2_4, ignoreBounds=True)
        p3_4.addItem(self.hLine_p3_4, ignoreBounds=True)
        self.VB_p0_0 = p0_0.getViewBox()
        self.VB_p1_0 = p1_0.getViewBox()
        self.VB_p2_0 = p2_0.getViewBox()
        self.VB_p3_0 = p3_0.getViewBox()
        self.VB_p0_1 = p0_1.getViewBox()
        self.VB_p1_1 = p1_1.getViewBox()
        self.VB_p2_1 = p2_1.getViewBox()
        self.VB_p3_1 = p3_1.getViewBox()
        self.VB_p0_2 = p0_2.getViewBox()
        self.VB_p1_2 = p1_2.getViewBox()
        self.VB_p2_2 = p2_2.getViewBox()
        self.VB_p3_2 = p3_2.getViewBox()
        self.VB_p0_3 = p0_3.getViewBox()
        self.VB_p1_3 = p1_3.getViewBox()
        self.VB_p2_3 = p2_3.getViewBox()
        self.VB_p3_3 = p3_3.getViewBox()
        self.VB_p0_4 = p0_4.getViewBox()
        self.VB_p1_4 = p1_4.getViewBox()
        self.VB_p2_4 = p2_4.getViewBox()
        self.VB_p3_4 = p3_4.getViewBox()
        p0_0.proxy = pg.SignalProxy(p0_0.scene().sigMouseMoved, rateLimit=20, slot=self.mouseMoved)
        p1_0.proxy = pg.SignalProxy(p1_0.scene().sigMouseMoved, rateLimit=20, slot=self.mouseMoved)
        p2_0.proxy = pg.SignalProxy(p1_0.scene().sigMouseMoved, rateLimit=20, slot=self.mouseMoved)
        p3_0.proxy = pg.SignalProxy(p1_0.scene().sigMouseMoved, rateLimit=20, slot=self.mouseMoved)
        p0_1.proxy = pg.SignalProxy(p1_0.scene().sigMouseMoved, rateLimit=20, slot=self.mouseMoved)
        p1_1.proxy = pg.SignalProxy(p1_0.scene().sigMouseMoved, rateLimit=20, slot=self.mouseMoved)
        p2_1.proxy = pg.SignalProxy(p1_0.scene().sigMouseMoved, rateLimit=20, slot=self.mouseMoved)
        p3_1.proxy = pg.SignalProxy(p1_0.scene().sigMouseMoved, rateLimit=20, slot=self.mouseMoved)
        p0_2.proxy = pg.SignalProxy(p1_0.scene().sigMouseMoved, rateLimit=20, slot=self.mouseMoved)
        p1_2.proxy = pg.SignalProxy(p1_0.scene().sigMouseMoved, rateLimit=20, slot=self.mouseMoved)
        p2_2.proxy = pg.SignalProxy(p1_0.scene().sigMouseMoved, rateLimit=20, slot=self.mouseMoved)
        p3_2.proxy = pg.SignalProxy(p1_0.scene().sigMouseMoved, rateLimit=20, slot=self.mouseMoved)
        p0_3.proxy = pg.SignalProxy(p1_0.scene().sigMouseMoved, rateLimit=20, slot=self.mouseMoved)
        p1_3.proxy = pg.SignalProxy(p1_0.scene().sigMouseMoved, rateLimit=20, slot=self.mouseMoved)
        p2_3.proxy = pg.SignalProxy(p1_0.scene().sigMouseMoved, rateLimit=20, slot=self.mouseMoved)
        p3_3.proxy = pg.SignalProxy(p1_0.scene().sigMouseMoved, rateLimit=20, slot=self.mouseMoved)

    def setPos_vline(self,mousePoint):
        self.vLine_p0_0.setPos(mousePoint.x())
        self.vLine_p1_0.setPos(mousePoint.x())
        self.vLine_p2_0.setPos(mousePoint.x())
        self.vLine_p3_0.setPos(mousePoint.x())
        self.vLine_p0_1.setPos(mousePoint.x())
        self.vLine_p1_1.setPos(mousePoint.x())
        self.vLine_p2_1.setPos(mousePoint.x())
        self.vLine_p3_1.setPos(mousePoint.x())
        self.vLine_p0_2.setPos(mousePoint.x())
        self.vLine_p1_2.setPos(mousePoint.x())
        self.vLine_p2_2.setPos(mousePoint.x())
        self.vLine_p3_2.setPos(mousePoint.x())
        self.vLine_p0_3.setPos(mousePoint.x())
        self.vLine_p1_3.setPos(mousePoint.x())
        self.vLine_p2_3.setPos(mousePoint.x())
        self.vLine_p3_3.setPos(mousePoint.x())
        self.vLine_p0_4.setPos(mousePoint.x())
        self.vLine_p1_4.setPos(mousePoint.x())
        self.vLine_p2_4.setPos(mousePoint.x())
        self.vLine_p3_4.setPos(mousePoint.x())
    def mouseMoved(self, evt):
        pos = evt[0]
        # self.TG.mouseMoved(evt)
        if p0_0.sceneBoundingRect().contains(pos):
            mousePoint = self.VB_p0_0.mapSceneToView(pos)
            self.hLine_p0_0.setPos(mousePoint.y())  # 주석처리하면 세로만 나옴
            self.setPos_vline(mousePoint)
        elif p1_0.sceneBoundingRect().contains(pos):
            mousePoint = self.VB_p1_0.mapSceneToView(pos)
            self.hLine_p1_0.setPos(mousePoint.y())  # 주석처리하면 세로만 나옴
            self.setPos_vline(mousePoint)
        elif p2_0.sceneBoundingRect().contains(pos):
            mousePoint = self.VB_p2_0.mapSceneToView(pos)
            self.hLine_p2_0.setPos(mousePoint.y())  # 주석처리하면 세로만 나옴
            self.setPos_vline(mousePoint)
        elif p3_0.sceneBoundingRect().contains(pos):
            mousePoint = self.VB_p3_0.mapSceneToView(pos)
            self.hLine_p3_0.setPos(mousePoint.y())  # 주석처리하면 세로만 나옴
            self.setPos_vline(mousePoint)
        elif p0_1.sceneBoundingRect().contains(pos):
            mousePoint = self.VB_p0_1.mapSceneToView(pos)
            self.hLine_p0_1.setPos(mousePoint.y())  # 주석처리하면 세로만 나옴
            self.setPos_vline(mousePoint)
        elif p1_1.sceneBoundingRect().contains(pos):
            mousePoint = self.VB_p1_1.mapSceneToView(pos)
            self.hLine_p1_1.setPos(mousePoint.y())  # 주석처리하면 세로만 나옴
            self.setPos_vline(mousePoint)
        elif p2_1.sceneBoundingRect().contains(pos):
            mousePoint = self.VB_p2_1.mapSceneToView(pos)
            self.hLine_p2_1.setPos(mousePoint.y())  # 주석처리하면 세로만 나옴
            self.setPos_vline(mousePoint)
        elif p3_1.sceneBoundingRect().contains(pos):
            mousePoint = self.VB_p3_1.mapSceneToView(pos)
            self.hLine_p3_1.setPos(mousePoint.y())  # 주석처리하면 세로만 나옴
            self.setPos_vline(mousePoint)
        elif p0_2.sceneBoundingRect().contains(pos):
            mousePoint = self.VB_p0_2.mapSceneToView(pos)
            self.hLine_p0_2.setPos(mousePoint.y())  # 주석처리하면 세로만 나옴
            self.setPos_vline(mousePoint)
        elif p1_2.sceneBoundingRect().contains(pos):
            mousePoint = self.VB_p1_2.mapSceneToView(pos)
            self.hLine_p1_2.setPos(mousePoint.y())  # 주석처리하면 세로만 나옴
            self.setPos_vline(mousePoint)
        elif p2_2.sceneBoundingRect().contains(pos):
            mousePoint = self.VB_p2_2.mapSceneToView(pos)
            self.hLine_p2_2.setPos(mousePoint.y())  # 주석처리하면 세로만 나옴
            self.setPos_vline(mousePoint)
        elif p3_2.sceneBoundingRect().contains(pos):
            mousePoint = self.VB_p3_2.mapSceneToView(pos)
            self.hLine_p3_2.setPos(mousePoint.y())  # 주석처리하면 세로만 나옴
            self.setPos_vline(mousePoint)
        elif p0_3.sceneBoundingRect().contains(pos):
            mousePoint = self.VB_p0_3.mapSceneToView(pos)
            self.hLine_p0_3.setPos(mousePoint.y())  # 주석처리하면 세로만 나옴
            self.setPos_vline(mousePoint)
        elif p1_3.sceneBoundingRect().contains(pos):
            mousePoint = self.VB_p1_3.mapSceneToView(pos)
            self.hLine_p1_3.setPos(mousePoint.y())  # 주석처리하면 세로만 나옴
            self.setPos_vline(mousePoint)
        elif p2_3.sceneBoundingRect().contains(pos):
            mousePoint = self.VB_p2_3.mapSceneToView(pos)
            self.hLine_p2_3.setPos(mousePoint.y())  # 주석처리하면 세로만 나옴
            self.setPos_vline(mousePoint)
        elif p3_3.sceneBoundingRect().contains(pos):
            mousePoint = self.VB_p3_3.mapSceneToView(pos)
            self.hLine_p3_3.setPos(mousePoint.y())  # 주석처리하면 세로만 나옴
            self.setPos_vline(mousePoint)
        elif p0_4.sceneBoundingRect().contains(pos):
            mousePoint = self.VB_p0_4.mapSceneToView(pos)
            self.hLine_p0_4.setPos(mousePoint.y())  # 주석처리하면 세로만 나옴
            self.setPos_vline(mousePoint)
        elif p1_4.sceneBoundingRect().contains(pos):
            mousePoint = self.VB_p1_4.mapSceneToView(pos)
            self.hLine_p1_4.setPos(mousePoint.y())  # 주석처리하면 세로만 나옴
            self.setPos_vline(mousePoint)
        elif p2_4.sceneBoundingRect().contains(pos):
            mousePoint = self.VB_p2_4.mapSceneToView(pos)
            self.hLine_p2_4.setPos(mousePoint.y())  # 주석처리하면 세로만 나옴
            self.setPos_vline(mousePoint)
        elif p3_4.sceneBoundingRect().contains(pos):
            mousePoint = self.VB_p3_4.mapSceneToView(pos)
            self.hLine_p3_4.setPos(mousePoint.y())  # 주석처리하면 세로만 나옴
            self.setPos_vline(mousePoint)


def main():
    pg.setConfigOption('background', 'k')
    pg.setConfigOption('foreground', 'w')
    app = QApplication([])
    import sqlite3
    conn = sqlite3.connect('DB/bt.db')
    df = pd.read_sql(f"SELECT * FROM 'bt'", conn).set_index('날짜')
    print(df['종가'].isna().any())  # True, NaN이 포함되어 있으면 True 반환
    print(df['종가'].apply(lambda x: pd.isna(x) or isinstance(x, str)).any())  # True

    conn = sqlite3.connect('DB/chart_table.db')
    df_chart_table = pd.read_sql(f"SELECT * FROM '국내주식'", conn).set_index('index')

    import ATOM_chart_numpy
    dict_plot = ATOM_chart_numpy.chart_np(df, df_chart_table)

    print(dict_plot)
    print(df)
    window = Window(df, dict_plot, 'stock_name', 'stock_code')
    window.setMinimumSize(600, 400)
    window.show()
    app.exec()


if __name__ == "__main__":
    main()
