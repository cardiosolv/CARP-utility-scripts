#!/usr/bin/env python
import numpy as np
import shutil
import optparse
from scipy.io.numpyio import fwrite, fread

class IgbFile:
    "Reads the header and data from an IGB file"
    def __init__(self):
        self.filename = ""
        self.props = {}
        self.file = None
        self.dim_x = 0
        self.dim_t = 0
        self.typecode = 'f'
        self.typesize = 0

    @staticmethod
    def open(filename):
        self = IgbFile()
        self.filename = filename
        self.file = open(filename, "r+")
        header = self.file.read(1024)
        tokens = header.split()
        self.props = {}
        for x in tokens:
            parameter = x.split(":")
            self.props[parameter[0]] = parameter[1]
        self.dim_x = int(self.props['x'])
        self.dim_t = int(self.props['t'])

        if self.props['type'] == 'float':
            self.typecode = 'f'
            self.typesize = 4
            self.typetype = float
        elif self.props['type'] == 'double':
            self.typecode = 'd' 
            self.typesize = 8
            self.typetype = double
        return self

    @staticmethod
    def like(other, filename):
        #copy the other file into this filename.
        shutil.copyfile(other.filename, filename)
        #open and return the new file.
        return IgbFile.open(filename)

    def get_all_nodes_at_time(self, time):
        self.file.seek(self.dim_x*time*self.typesize+1024, 0)
        linebuffer = fread(self.file, self.dim_x, self.typecode)
        return linebuffer
        
    def set_all_nodes_at_time(self, time, buffer):
        self.file.seek(self.dim_x*time*self.typesize+1024, 0)
        fwrite(self.file, buffer.size, buffer)


# A simple class to help me parse options into a dictionary.
# Sometimes, dictionaries are easier to manipulate than objects.
class DictOptionParser(optparse.OptionParser):
    def parse_args(self, *args, **keywords):
        keywords["values"] = _blank()
        (options, args) = optparse.OptionParser.parse_args(self, *args, **keywords)
        return (options.__dict__, args)
class _blank:
    pass

if __name__=="__main__":
    import sys
    parser = DictOptionParser(usage="Usage: %prog [options] file.igb")
    parser.add_option("-d", "--compute_dvdt",
                      dest="compute_dvdt",
                      help="Compute dvdt using finite differences on the igb file",
                      default=False,
                      action="store_true",
                      )

    (options, args) = parser.parse_args()
    if len(args) != 1:
        print "Need the input igb file"
        print parser.print_help()
        sys.exit(1)
    
    infile = args[0]
    igb = IgbFile.open(infile)
    
    if options.has_key("compute_dvdt"):
        # do the computation
        if igb.dim_t < 3:
            print "We need at least three timesteps to compute derivatives"
            sys.exit(1)
        outigb = IgbFile.like(igb, "compute_dvdt.igb")

        h = float(igb.props['fac_t'])

        data = [igb.get_all_nodes_at_time(0), 
                igb.get_all_nodes_at_time(1), 
                igb.get_all_nodes_at_time(2)]
        deriv = (-3*data[0]+4*data[1]-data[2])/(2*h)
        outigb.set_all_nodes_at_time(0, deriv)

        for i in xrange(1,igb.dim_t-1):
            deriv = (data[2]-data[0])/(2*h)
            outigb.set_all_nodes_at_time(i, deriv)
            if i+2 <= igb.dim_t-1:
                data[0] = data[1]
                data[1] = data[2]
                data[2] = igb.get_all_nodes_at_time(i+2)

        deriv = (3*data[2]-4*data[1]+data[0])/(2*h)
        outigb.set_all_nodes_at_time(igb.dim_t-1, deriv)


        
