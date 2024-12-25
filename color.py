import pyqtgraph as pg
from PyQt5 import QtCore


dot_y = pg.mkPen(color='y', width=1, style=QtCore.Qt.DotLine)
dot_r = pg.mkPen(color='r', width=1, style=QtCore.Qt.DotLine)
dot_g = pg.mkPen(color='g', width=1, style=QtCore.Qt.DotLine)
dot_c = pg.mkPen(color=(0,216,255), width=1, style=QtCore.Qt.DotLine)
dot_w = pg.mkPen(color='w', width=1, style=QtCore.Qt.DotLine)

dash_r = pg.mkPen(color='r', width=1, style=QtCore.Qt.DashLine)
dash_rk = pg.mkPen(color=(204,61,61), width=1, style=QtCore.Qt.DashLine)
dash_ck = pg.mkPen(color=(61,183,204), width=1, style=QtCore.Qt.DashLine)
dash_g = pg.mkPen(color=[0, 130, 153], width=1.2, style=QtCore.Qt.DashLine)
dash_k = pg.mkPen(color=[93, 93, 93], width=1, style=QtCore.Qt.DashLine)


red = (255,0,0)
red_1 = (255,167,167)
red_2 = (204,61,61)
# red_3 = (103,0,0)
# red_2 = (255,216,216)
# red_4 = (241,95,95)
# red_6 = (152,0,0)

orange = (255,94,0)
orange_1 = (255,193,158)
orange_2 = (204,114,61)
# orange_3 = (102,37,0)
# orange_2 = (250,224,212)
# orange_4 = (242,150,97)
# orange_6 = (153,56,0)

mandarine = (255,187,0)
mandarine_1 = (255,224,140)
mandarine_2 = (204,166,61)
# mandarine_3 = (102,75,0)
# mandarine_2 = (250,236,197)
# mandarine_4 = (242,203,97)
# mandarine_6 = (153,112,0)

yellow = (255,228,0)
yellow_1 = (250,237,125)
yellow_2 = (196,183,59)
# yellow_3 = (102,92,0)
# yellow_2 = (250,244,192)
# yellow_4 = (229,216,92)
# yellow_6 = (153,138,0)

ygreen = (171,242,0)
ygreen_1 = (206,242,121)
ygreen_2 = (159,201,60)
# ygreen_3 = (71,102,0)
# ygreen_2 = (228,247,186)
# ygreen_4 = (188,229,92)
# ygreen_6 = (107,153,0)

green = (47,157,39)
green_1 = (183,240,177)
green_2 = (71,200,62)
# green_3 = (34,116,28)
# green_2 = (206,251,201)
# green_4 = (134,229,127)
# green_6 = (47,157,39)

cyan = (0,216,255)
cyan_1 = (178,235,244)
cyan_2 = (61,183,204)
# cyan_3 = (0,87,102)
# cyan_2 = (212,244,250)
# cyan_4 = (92,209,229)
# cyan_6 = (0,130,153)

yblue = (0,84,255)
yblue_1 = (178,204,255)
yblue_2 = (67,116,217)
# yblue_3 = (0,34,102)
# yblue_2 = (217,229,255)
# yblue_4 = (103,153,255)
# yblue_6 = (0,51,153)

blue = (0,0,255)
blue_1 = (181,178,255)
blue_2 = (70,65,217)
# blue_3 = (3,0,102)
# blue_2 = (218,217,255)
# blue_4 = (107,102,255)
# blue_6 = (5,0,153)

purple = (95,0,255)
purple_1 = (209,178,255)
purple_2 = (128,65,217)
# purple_3 = (42,0,102)
# purple_2 = (232,217,255)
# purple_4 = (165,102,255)
# purple_6 = (63,0,153)

pink = (255,0,221)
pink_1 = (255,178,245)
pink_2 = (217,65,197)
# pink_3 = (102,0,88)
# pink_2 = (255,217,250)
# pink_4 = (243,97,220)
# pink_6 = (153,0,133)

fiesta = (255,0,127)
fiesta_1 = (255,178,217)
fiesta_2 = (217,65,140)
# fiesta_3 = (102,0,51)
# fiesta_2 = (255,217,236)
# fiesta_4 = (243,97,166)
# fiesta_6 = (153,0,76)

white = (255,255,255)
white_1 = (189,189,189)
white_2 = (93,93,93)
# white_3 = (25,25,25)
# white_2 = (234,234,234)
# white_4 = (140,140,140)
# white_6 = (53,53,53)

li = [
      red,       red_1,       red_2,       #red_3,
      orange,    orange_1,    orange_2,    #orange_3,
      mandarine, mandarine_1, mandarine_2, #mandarine_3,
      yellow,    yellow_1,    yellow_2,    #yellow_3,
      ygreen,    ygreen_1,    ygreen_2,    #ygreen_3,
      green,     green_1,     green_2,     #green_3,
      cyan,      cyan_1,      cyan_2,      #cyan_3,
      yblue,     yblue_1,     yblue_2,     #yblue_3,
      blue,      blue_1,      blue_2,      #blue_3,
      purple,    purple_1,    purple_2,    #purple_3,
      pink,      pink_1,      pink_2,      #pink_3,
      fiesta,    fiesta_1,    fiesta_2,    #fiesta_3,
      white,     white_1,     white_2
]


