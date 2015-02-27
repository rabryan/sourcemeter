"""
script for reading voltage values from
a keithley 2400 sourcemeter via rs-232
"""

import serial
import re
import time
SAMPLE_INT = 1

def parse_reading(readstr):
    """
    output readings look like
    \x13+2.949037E+00\x11\r

    just take the digits at index 2-6 as value

    ###assumes values in range [1-10)
    """
    if not re.match("\x13\+[0-9]+.*", readstr):
        return None

    return float(readstr[2:8])


if __name__ == "__main__":
    print(time.ctime())
    tstart = time.time()
    com = serial.Serial("/dev/ttyUSB0", 9600, timeout=1)

    """ reset and set to measure voltage """
    com.write("*rst\n")
    com.write("source:func curr\n")
    com.write("sense:func 'voltage'\n'")
    com.write("trig:count 1\n")
    com.write("form:elem volt\n")
    com.write("outp on\n")
    i = 0
    while True:
        rstart = time.time()
        com.write("read?\n")

        output = com.readall()
        value = parse_reading(output)
        if value:
            print("{}\t{}\t{}v".format(i, rstart, value))
        else:
            print("{}\t{}\tERROR".format(i, rstart))
        i+=1
        delta = time.time() - rstart
        if delta < SAMPLE_INT:
            time.sleep(SAMPLE_INT - delta)

    com.close()
