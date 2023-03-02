import json

class TRecallEner:
    def __init__(self, limDown, limUp, fwhm, ampl):
        self.limDown = limDown
        self.limUp = limUp
        self.fwhm = fwhm
        self.ampl = ampl

global myCurrentSetting

def run20Co60source(dom): #file is LUT file
    with open('LUT_ELIADE_S9_run20_raluca.json', 'r') as js_file:
        file=json.load(js_file)

    for i in file:
        domainnbr=i["domain"]
        if dom==domainnbr:
            type=i["detType"]
            if type==2:
                myCurrentSetting = TRecallEner(700, 1200, 7, 100)
            elif type==10:
                myCurrentSetting = TRecallEner(200, 600, 4, 1000)
            elif type==1:
                myCurrentSetting = TRecallEner(800, 1600, 4, 1000)
    return myCurrentSetting


def run25Eu152source(dom):
    pass
