import json
from TRecallEner import TRecallEner
#def __init__(self, limDown, limUp, ampl, fwhm):
# *******************************
def SetUpRecallEner(js, dom):
    if dom == 1:
        return TRecallEner(200, 400, 1000, 4, 100, 700)
    elif dom == 2:
        return TRecallEner(200, 400, 100, 7, 100, 700)
    elif dom == 3:
        return TRecallEner(200, 400, 1000, 15, 100, 700)
    return run20Co60source(js, dom)
# *******************************
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
                myCurrentSetting = TRecallEner(800, 1600, 1000, 4, 200, 1500)
    return myCurrentSetting

def run25Eu1252source(js, dom): #file is LUT file
    
    myCurrentSetting = TRecallEner(0,1300,100,4,0, 1500)
    for i in js:
        domainnbr=i["domain"]
        if dom==domainnbr:
            type=i["detType"]
            if type==2:
                myCurrentSetting = TRecallEner(0,1300,100,4,0, 1500)
            elif type==10:
                myCurrentSetting = TRecallEner(0,500,100,4,0, 1500)
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
