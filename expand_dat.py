#!/usr/bin/env python
from sets import Set
import numpy as np
import optparse

def read_removed_nodes(filename):
    ''' Reads in a .rmnodes file and returns a Set of all the removed nodes.
        P: filename - filename, should end in .rmnodes
        R: Set of all the nodes in the file
    '''
    file = open(filename, 'r')
    line = file.readline()
    return Set([int(line.strip()) for line in file])

def expand_nodal_array(removed_nodes,expansion_value,short_array):
    '''Expands a data array based on removed nodes.

       P: removed_nodes - set of removed nodes in the longer array

       P: expansion_value - value that removed nodes should be set to
       when converting the short array into the longer array
       
       P: short_array - the values for the shorter array.

       R: the longer array with the nodes at removed_nodes set to
       expansion_value
    '''
    long_size = len(short_array)+len(removed_nodes)
    long_array = np.zeros([long_size],short_array.dtype)
    short_index = 0
    expand_index = 0
    for long_index in xrange(0, long_size):
        if long_index in removed_nodes:
            value = expansion_value
            expand_index += 1
        else:
            value = short_array[short_index]
            short_index += 1
        long_array[long_index] = value
    assert(short_index == len(short_array))
    return long_array

def read_in_dat_file(filename):
    return np.loadtxt(filename, 'f')

def read_in_map_file(filename):
    return np.loadtxt(filename, 'i')[:,1]

def write_out_dat_file(filename, data):
    file = open(filename, 'w')
    for i in data :            
        file.write(str(i) + "\n")


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
    parser = DictOptionParser("%prog: [options] long.rmnodes long_i2e.dat short_i2e.dat expanded_value file1.dat [file2.dat ...]")
    (options, args) = parser.parse_args()
    if len(args) < 4:
        print "Need the rmnodes file, the map file, a value to expand, and at least one dat file."
        print parser.print_help()
        sys.exit(1)

    external_removed_nodes = read_removed_nodes(args[0])
    long_i2e = read_in_map_file(args[1])
    short_i2e = read_in_map_file(args[2])
    expanded_value = float(args[3])

    removed_nodes = Set()
    rmnode_index = 0
    short_i = 0
    for long_i in xrange(0, len(long_i2e)):
        long_e = long_i2e[long_i]
        if long_e in external_removed_nodes:
            rmnode_index += 1;
            removed_nodes.add(long_i)
        else:
            short_e = long_e - rmnode_index
            if short_e == short_i2e[short_i]:
                short_i += 1
            else:
                removed_nodes.add(long_i)
    del long_i2e
    del short_i2e
    del external_removed_nodes

    for filename in args[4:]:
        short_data = read_in_dat_file(filename)
        long_data = expand_nodal_array(removed_nodes, expanded_value, short_data)
        write_out_dat_file("new."+filename, long_data)
