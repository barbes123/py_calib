import json
from TRecallEner import TRecallEner
#def __init__(self, limDown, limUp, ampl, fwhm):
############################
#limDown, limUp, ampl, fwhm, limStart, limStop
# *******************************
def SetUpRecallEner(js, dom, source):
    if source == "60Co":
        if dom == 1:
            return TRecallEner(200, 400, 10000, 15, 200, 400)
        elif dom == 2:
            return TRecallEner(200, 400, 1000, 10, 200, 700)
        elif dom == 3:
            return TRecallEner(200, 400, 1000, 15, 100, 700)
        return run20Co60andbackground(js, dom)
    elif source=="152Eu":
        if dom == 1:
            return TRecallEner(0, 500, 10000, 4, 0, 500)
        elif dom == 2:
            return TRecallEner(0, 500, 1000, 10, 200, 700)
        elif dom == 3:
            return TRecallEner(0, 500, 1000, 15, 100, 700)
        return run68Eu152source(js, dom)
# *******************************
def run20Co60andbackground(js, dom): #file is LUT file
    myCurrentSetting = TRecallEner(800,1200,100,4,200, 1500)
    for i in js:
        domainnbr=i["domain"]
        if dom==domainnbr:
            type=i["detType"]
            if type==2:
                myCurrentSetting = TRecallEner(800, 2100, 100, 7, 200, 1500)
            elif type==10:
                myCurrentSetting = TRecallEner(200, 600, 1000, 4, 100, 800)
            elif type==1:
                myCurrentSetting = TRecallEner(800, 2100, 100, 4, 200, 1500)
    return myCurrentSetting
def run20Co60source(js, dom): #file is LUT file
    myCurrentSetting = TRecallEner(800,1200,100,4,200, 1500)
    for i in js:
        domainnbr=i["domain"]
        if dom==domainnbr:
            type=i["detType"]
            if type==2:
                myCurrentSetting = TRecallEner(800, 1400, 100, 7, 200, 1500)
            elif type==10:
                myCurrentSetting = TRecallEner(200, 600, 1000, 4, 100, 800)
            elif type==1:
                myCurrentSetting = TRecallEner(800, 1600, 100, 4, 200, 1500)
    return myCurrentSetting

def run68Eu152source(js, dom): #file is LUT file
    
    myCurrentSetting = TRecallEner(0,1300,100,4,0, 1500)
    for i in js:
        domainnbr=i["domain"]
        if dom==domainnbr:
            type=i["detType"]
            if type==2:
                myCurrentSetting = TRecallEner(50,1300,10,3,100,1500)
            elif type==10:
                myCurrentSetting = TRecallEner(0,500,100,4,0, 500)
            elif type==1:
                myCurrentSetting = TRecallEner(0,1300,100,4,0, 1500)
    return myCurrentSetting


# class TRecallEner:
#     def __init__(self, limDown, limUp, fwhm, ampl):
#         self.limDown = limDown
#         self.limUp = limUp
#         self.fwhm = fwhm
#         self.ampl = ampl
#
# global myCurrentSetting
#
# def run20Co60source(dom): #file is LUT file
#     with open('LUT_ELIADE_S9_run20_raluca.json', 'r') as js_file:
#         file=json.load(js_file)
#
#     for i in file:
#         domainnbr=i["domain"]
#         if dom==domainnbr:
#             type=i["detType"]
#             if type==2:
#                 myCurrentSetting = TRecallEner(700, 1200, 7, 100)
#             elif type==10:
#                 myCurrentSetting = TRecallEner(200, 600, 4, 1000)
#             elif type==1:
#                 myCurrentSetting = TRecallEner(800, 1600, 4, 1000)
#     return myCurrentSetting
#
#
def run25Eu152source(dom):
    pass
#################################################
#   OLD 152EU INFORMATION IN GAMMA_SOURCES.JSON
#  "152Eu": {
#       "t12": 426902832.0,
#       "a0": 543500.0,
#       "t0": "2021-03-21 12:00:00",
#       "comment": "",
#       "gammas": {
#          "121.779": 0.2858,
#          "244.693": 0.7583,
#          "344.272": 0.265,
#          "411.111": 0.02234,
#          "443.979": 0.3148,
#          "778.890": 0.12942,
#          "964.014": 0.14605,
#          "1085.793": 0.10207,
#          "1112.070": 0.13644,
#          "1407.993": 0.21005
#       }
#    }
#################################################