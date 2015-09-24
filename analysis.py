import matplotlib.pyplot as plot
import sys
import csv
import math
import scipy
import scipy.optimize
import scipy.stats as stats
import numpy

if __name__ == "__main__":

    f = open(sys.argv[1])
    reader = csv.reader(f, delimiter='\t')
    data = list(reader)
    for d in data:
        if len(d) != 3:
            print d
            data.remove(d)

    vs = []
    ts = []
    for i,t,v in data:
        try:
            v_f = float(v[0:-1])
            t_f = float(t)
            vs.append(v_f)
            ts.append(t_f)
        except:
            print("ignoring bad values: {}  {}  {}".format(i, t, v))
            pass

    tstart = ts[0]
    trels = [t - tstart for t in ts]
    thrs = [t/3600.0 for t in trels]

    n = 0.115
    tau = 1.13
    decay1 = [(3.05-n) + n*math.exp(-t/tau) for t in thrs]
    delta = [abs(v1-v2) for v1,v2 in zip(vs[:-1], vs[1:])]
    print len(delta)
    print len(thrs)
    plot.plot(thrs, vs)

    def exp_decay(t, C, A, tau):
        return C - A*numpy.exp(-t/tau)

    mean = numpy.average(vs[:5])
    vtops = []
    ttops = []
    for v, t in zip(vs, thrs):
        if v > 0.99*mean:
            vtops.append(v)
            ttops.append(t)
            mean = mean*(0.995) + v*0.005

    """
    vttops = []
    tttops = []
    mean = numpy.average()
    for v, t in zip(vtops, ttops):
        if v > mean:
            vttops.append(v)
            tttops.append(t)
    """
    N=40
    vmaxes = [max(vs[i:i+N]) for i in range((len(vs)) - N)]
    tmaxes = [thrs[i] for i in range((len(vs)) - N)]
    vs = numpy.array(vs)
    vtops = numpy.array(vtops)
    ttops = numpy.array(ttops)
    thrs = numpy.array(thrs)
    vmaxes = numpy.array(vmaxes)
    tmaxes = numpy.array(tmaxes)

    x0 = numpy.array([3.05, 0.115, 1.113])
    (C, A, tau), cov = scipy.optimize.curve_fit(exp_decay, tmaxes, vmaxes)

    print("best fit: C={}  A={}  tau={}".format(C, A, tau))
    print("{} - {}A*e^(-t/{})".format(C, A, tau))

    v_best_fit = exp_decay(tmaxes, C, A, tau)
    plot.plot(tmaxes, vmaxes, 'r')
    plot.plot(tmaxes, v_best_fit, 'b--')
    plot.show()

    #voltage drop when active
    plot.plot(thrs[:-1], delta, 'r')
    plot.show()
