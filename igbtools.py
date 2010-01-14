#!/usr/bin/env python
import numpy as np
import shutil
import optparse
import mmap
from scipy.io.numpyio import fwrite, fread

class IgbFile:
    "Reads the header and data from an IGB file"
    def __init__(self):
        self.filename = ""
        self.props = {}
        self.file = None
        self.dim_x = 0
        self.dim_t = 0
        self.start_time = 0
        self.fac_t = 0
        self.typecode = 'f'
        self.typesize = 4
        self.typetype = float

    def open(filename):
        self = IgbFile()
        self.filename = filename
        self.file = open(filename, "r+b")
        header = self.file.read(1024)
        tokens = header.split()
        self.props = {}
        for x in tokens:
            parameter = x.split(":")
            self.props[parameter[0]] = parameter[1]
        self.dim_x = int(self.props['x'])
        self.dim_t = int(self.props['t'])
        self.fac_t = float(self.props['fac_t'])

        if self.props['type'] == 'float':
            self.typecode = 'f'
            self.typesize = 4
            self.typetype = float
        elif self.props['type'] == 'double':
            self.typecode = 'd' 
            self.typesize = 8
            self.typetype = double
        return self
    open = staticmethod(open)

    def like(other, filename):
        #copy the other file into this filename.
        shutil.copyfile(other.filename, filename)
        #open and return the new file.
        return IgbFile.open(filename)
    like = staticmethod(like)

    def new(filename, dim_x, dim_t, fac_t=1, start_time=0):
        props = {}
        props['x'] = "%d" % dim_x
        props['t'] = "%d" % dim_t
        props['fac_t'] = "%g" % fac_t
        props['dim_t'] = "%g" % (start_time+fac_t*(dim_t-1)) 
        
        props['y'] = "1"
        props['z'] = "1"
        props['type'] = "float"
        props['systeme'] = "little_endian"
        props['unites_x'] = "cm"
        props['unites_y'] = "cm"
        props['unites_t'] = "ms"
        props['unites'] = "mV"
        props['facteur'] = "1"
        props['zero'] = "0"

        file = open(filename, 'wb')
        file.write(IgbFile.header(props))
        file.truncate(1024+4*dim_x*dim_t)
        file.close()

        return IgbFile.open(filename)
    new = staticmethod(new)
        
    def header(props):
        header_items = [key+":"+props[key]+" " for key in props.keys()]
        header = ''
        line = ''
        for item in header_items:
            if len(line)+len(item) <= 70:
                line += item
            else:
                header += line + "\r\n"
                line = item
        header += line + "\r\n"
        
        while len(header)+72 <= 1021:
            header += ' '*70 + "\r\n"
        while len(header)+71 <= 1021:
            header += ' '*70 + "\r"
        if len(header) < 1021:
            header += ' '*(1021-len(header))
        header += "\r\n\f"
        return header
    header = staticmethod(header)

    def end_time(self):
        return self.start_time+self.fac_t*(self.dim_t-1)

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
    parser = DictOptionParser(usage="Usage: %prog [options] file.igb [file2.igb [file3.igb...]]")
    parser.add_option("-d", "--compute_dvdt",
                      dest="compute_dvdt",
                      help="Compute dvdt using finite differences on the igb file",
                      default=False,
                      action="store_true",
                      )
    parser.add_option("-c", "--combine_igb_files",
                      dest="combine_igb_files",
                      help="Combine igb files written across restarts into one large igb file.  Use with arguments file1.igb file1_starttime file2.igb file2_starttime ...",
                      default=False,
                      action="store_true",
                      )
    parser.add_option("-s", "--snapshot",
                      dest="snapshot",
                      help="Take a snapshot (output a .dat file) of one timestep of an igb file.  Use with arguments file.igb snapshot_time.",
                      default=False,
                      action="store_true",
                      )

    (options, args) = parser.parse_args()
    if len(args) < 1:
        print "Need the input igb file"
        print parser.print_help()
        sys.exit(1)
    
    
    if options.has_key("compute_dvdt"):
        infile = args[0]
        igb = IgbFile.open(infile)
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
    if options.has_key("combine_igb_files"):
        # open all the files
        state = 0
        files = []
        for line in args:
            if state == 0:
                files.append(IgbFile.open(line))
                state = 1
            else:
                files[-1].start_time = float(line)
                state = 0
        #make sure they all have the same fac_t
        fac_t = files[0].fac_t
        for file in files[1:]:
            assert fac_t == file.fac_t
        #make sure they all have the same number of points
        dim_x = files[0].dim_x
        for file in files[1:]:
            assert dim_x == file.dim_x

        #sort the files by starting times
        def file_compare(a, b):
            if a.start_time < b.start_time:
                return -1
            elif a.start_time == b.start_time:
                return 0
            else:
                return 1
        files.sort(file_compare)
        
        # make sure the ending times of each file match or overlap.
        for i in xrange(0,len(files)-1):
            assert files[i+1].start_time <= files[i].end_time()

        start_time = files[0].start_time
        end_time = files[-1].end_time()

        # make a new file with the appropriate dimesions
        dim_t = (end_time-start_time)/fac_t+1
        out = IgbFile.new("combined.igb", 
                          dim_x=dim_x, 
                          fac_t=fac_t, 
                          dim_t=dim_t, 
                          start_time=start_time,
                          )
        
        file_index = 0;
        file_time = 0;
        for i in xrange(0,dim_t):
            current_time = start_time + fac_t*i
            if (file_index != len(files)-1
                and current_time >= files[file_index+1].start_time):
                file_index += 1
                file_time = 0;

            out.set_all_nodes_at_time(i, files[file_index].get_all_nodes_at_time(file_time))
            file_time += 1

    if options.has_key("snapshot"):
        infile = args[0];
        igb = IgbFile.open(infile);
        time = args[1];
        data = igb.get_all_nodes_at_time(int(time));
        filename = "vm_" + time + ".dat";
        file = open(filename, 'w');
        for i in data :            
            file.write(str(i) + "\n");
        file.close;
