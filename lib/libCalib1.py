# necessary classes, functions to calculate activity
import sys
from datetime import datetime
import numpy as np
import math
from scipy.integrate import quad


time_format = "%Y-%m-%d %H:%M:%S"

class TIsotope:
    def __init__(self, name, t12, date0, a0):
        self.name = name
        # self.t12 = t12*365*24*3600
        self.t12 = t12
        self.date0 = date0
        self.a0 = a0

    def __post_init__(self):
        if self.name is None:
            self.name = 0
        if self.t12 is None:
            self.t12 = 0
        if self.date0 is None:
            self.date0 = '60Co'
        if self.a0 is None:
            self.a0 = a0

    def setup_source_from_json(self, data, source_name):
        self.found = False
        if source_name in data:
            self.name = source_name
            self.date0 = datetime.strptime(data[source_name]['t0'], time_format)
            self.a0 = data[source_name]['a0']
            self.t12 = data[source_name]['t12']
            self.found = True
        else:
            print('source in not found in the source file')
            sys.exit()

    def decay_constant(self):
        return math.log(2, math.e)/self.t12

    def __repr__(self):
        return print('Isotope: {}, T12= {} s, Date {}, A0 = {}'.format(self.name, self.t12, self.date0, self.a0))

    def __str__(self):
        return print('Isotope: {}, T12= {} s, Date {}, A0 = {}'.format(self.name, self.t12, self.date0, self.a0))

    def Activity(self, time1):
        t = time1 - self.date0
        # print('Activity after {} s is {} Bq'.format(t.total_seconds(), self.a0*np.exp(-1*self.decay_constant()*t.total_seconds())))
        return self.a0 * np.exp(-1 * self.decay_constant() * t.total_seconds())

    def GetNdecays(self, start, stop):
        return(1 / 2 * (self.Activity(start) + self.Activity(stop)) * (stop - start).total_seconds())

    def GetNdecaysIntegral(self, start, stop):
        t1 = (start - self.date0).total_seconds()
        t2 = (stop - self.date0).total_seconds()
        ndecays = lambda t, a0, decay_constant: a0 * np.exp(-1 * decay_constant * t)
        nn, err = quad(ndecays, t1, t2, args=(self.a0, self.decay_constant()))
        print("Error from the quad integral is {}".format(err))
        return nn, err

class TMeasurement:
    def __init__(self, server, run, source, tstart, tstop, distance):
        self.run = run
        self.source = source
        self.tstart = tstart
        self.tstop = tstop
        self.server = server
        self.distance = distance
        self.found = True

    default_time =  datetime.strptime('2022-08-08 12:00:00', time_format)

    def __post_init__(self):
        if self.server is None:
            self.server = 0
        if self.run is None:
            self.run = 0
        if self.source is None:
            self.source = '60Co'
        if self.tstart is None:
            self.tstart = default_time
        if self.tstop is None:
            self.tstop = default_time
        if self.distance is None:
            self.distance = 0
        if self.found is None:
            self.found = False

    def setup_run_from_json(self, data, val, server):
        self.found = False
        for runnbr in data['measurements']:
            if ((int(runnbr['run']) == val) and (int(runnbr['server']) == server)):
                # self.source = runnbr['source']
                if (self.found):
                    print('Multiple occurrence in run {} and server {}'.format(runnbr, server))
                    sys.exit()
                self.run = runnbr['run']
                self.tstart = datetime.strptime(runnbr['tstart'],time_format)
                self.tstop = datetime.strptime(runnbr['tstop'],time_format)
                self.found = True
                self.server = server
                self.run = val
                self.distance = runnbr['distance']
            if runnbr['source'] is None:
               runnbr['source'] = '60Co'
            else:
                self.source = runnbr['source']
                # print("{}, YES".format(val))

    def __str__(self):
        return print('Run: {}, Server: {}, Source: {}, Time Start: {}, Time Stop: {}, Distance {}, Found {}'.format(self.run, self.server, self.source, self.tstart, self.tstop, self.distance, self.found))
