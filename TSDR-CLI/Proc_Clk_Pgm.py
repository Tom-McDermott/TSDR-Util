#
# Read Clock Synthesizer programming file from Clock Builder programming
#

import time

from wx.core import DataFormat

def ProcessClkPgm(filename):
    try:
        with open(filename, 'r') as file:
            line = next(file)
            while line != "# Part: Si5344\n":
                line = next(file)

            print("Synthesizer Part Type: ", line)
            while line != "# Start configuration preamble\n":
                line = next(file)

            line = next(file)

            while line != "# End configuration preamble\n":
                yield(line)         # generate programming line
                line = next(file)

            time.sleep(1)   # delay to allow synth to run autocalibration

            while line != "# Start configuration registers\n":
                line = next(file)

            line = next(file)

            while line != "# End configuration registers\n":
                yield(line)         # generate programming line
                line = next(file)

            while line != "# Start configuration postamble\n":
                line = next(file)

            line = next(file)

            while line != "# End configuration postamble\n":
                yield(line)         # generate programming line
                line = next(file)

    except IOError:
        print ("Error trying to open or read Clock Program File: ", filename)


def ParseClkLine(line):         # Specific to the Clock file
    address, data  = line.rstrip('\n').split(',')    
    page = '0x00' + address[2:4]
    register = '0x00' + address[4:6]
    data = '0x' + data[2:4]
    return page, register, data
