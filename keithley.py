"""
script for reading voltage values from
a keithley 2400 sourcemeter via rs-232
"""

import serial
import re
import time
import logging as log

from drift.model.core import Source, Attr, register_source_class
from drift.model.projects.project import ProjectScript, register_project_script

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


class Keithley( Source ):
    sampleint = Attr("Sample Interval (s)", float, default=1, min=0.2, max=100000)
    port = Attr("Serial Port", str, readonly=True, default="/dev/ttyUSB0")
    
    def __init__(self, **kwargs):
        super().__init__(name="Sourcemeter", **kwargs)
        self.com = serial.Serial(self.port, 9600, timeout=1)
        self.newDatum("Voltage", units="v")
        self._last_read = 0
    
    def start(self):
        """ reset and set to measure voltage """
        self.com.write("*rst\n".encode())
        self.com.write("source:func curr\n".encode())
        self.com.write("sense:func 'voltage'\n'".encode())
        self.com.write("trig:count 1\n".encode())
        self.com.write("form:elem volt\n".encode())
        self.com.write("outp on\n".encode())
        self.read()

    def tic(self):
        if time.time() - self._last_read >= self.sampleint:
            self.read()
            self._last_read = time.time()

    def read(self):
        self.com.write("read?\n".encode())

        output = self.com.readall()
        value = parse_reading(output.decode())
        if value:
            self.broadcast( "Voltage", time.time(), value )
            log.debug("Voltage: {}".format(value))
        else:
            log.warning("Invalid sourcemeter response \'{}\'".format( output.decode()))



@register_project_script("Keithley")
class KeithleyScript(ProjectScript):
    def __init__( self, project):
        super().__init__()
        self.sourcemeter = Keithley() 
        self.connectJobTimer(project)
        project.add(self.sourcemeter)

    def start(self):
        self.sourcemeter.start()
    
    def stop(self):
        self.sourcemeter.stop()
        self.removeJobs()

if __name__ == "__main__":
    print(time.ctime())
    SAMPLE_INT = 1
    tstart = time.time()
    com = serial.Serial("/dev/ttyUSB0", 9600, timeout=1)

    """ reset and set to measure voltage """
    com.write("*rst\n".encode())
    com.write("source:func curr\n".encode())
    com.write("sense:func 'voltage'\n'".encode())
    com.write("trig:count 1\n".encode())
    com.write("form:elem volt\n".encode())
    com.write("outp on\n".encode())
    i = 0
    while True:
        rstart = time.time()
        com.write("read?\n".encode())

        output = com.readall()
        value = parse_reading(output.decode())
        if value:
            print("{}\t{}\t{}v".format(i, rstart, value))
        else:
            print("{}\t{}\tERROR".format(i, rstart))
        i+=1
        delta = time.time() - rstart
        if delta < SAMPLE_INT:
            time.sleep(SAMPLE_INT - delta)

    com.close()
