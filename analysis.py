import matplotlib.pyplot as plot
import sys
import csv


if __name__ == "__main__":

    f = open(sys.argv[1])
    reader = csv.reader(f, delimiter='\t')
    data = list(reader)
    vs = [float(v[0:-1]) for i,t,v in data]
    ts = [float(t) for i,t,v in data]
    tstart = ts[0]
    trels = [t - tstart for t in ts]
    thrs = [t/3600.0 for t in trels]

    plot.plot(thrs, vs)
    plot.show()
