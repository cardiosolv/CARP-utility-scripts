#!/usr/bin/env python

import sys
import re
import os
import optparse
import shutil


from numpy import *
from scipy import sparse
import scipy as Sci
import numpy.linalg


# A simple class to help me parse options into a dictionary.
# Sometimes, dictionaries are easier to manipulate than objects.
class DictOptionParser(optparse.OptionParser):
   def parse_args(self, *args, **keywords):
      keywords["values"] = _blank()
      (options, args) = optparse.OptionParser.parse_args(self, *args, **keywords)
      return (options.__dict__, args)
class _blank:
   pass


def strip_header(file):
    return int(file.readline().strip())


if __name__=="__main__":
   parser = DictOptionParser(usage="Usage: %prog [options] meshname t-files")

   (options, args) = parser.parse_args()
   if len(args) < 1:
      parser.print_help()
      sys.exit(1)
   name = args[0]

   print "Reading in the pts file"
   pts_file = open(name+".pts", "r")
   num_points = strip_header(pts_file)
   pts = [[float(coord) 
           for coord 
           in re.split(r'\s+', line.strip())
           ]
          for line
          in pts_file
          ]
   del pts_file
   

   grad_mat = [sparse.lil_matrix((num_points, num_points))
               for i
               in range(0,3)
               ]
   pt_area = zeros((num_points, 1))

   print "Reading in the tetras file"
   elem_file = open(name+".tetras", "r")
   num_elem = strip_header(elem_file)
   for line in elem_file:
       elem = [int(point)-1
               for point
               in re.split(r'\s+', line.strip())[0:4]
               ]
       shape = zeros((4,4))
       shape[3,:] = 1
       for i in range(0,4):
           shape[0:3, i] = pts[elem[i]]
       elem_grad = linalg.inv(shape)[:,0:3]
       elem_area = abs(linalg.det(shape))
       for pt in elem:
           pt_area[pt] += elem_area
           for dim in range(0,3):
               grad_mat[dim][pt, elem] += elem_area*elem_grad[:,dim]

   del elem_file
   del pts


   for g in grad_mat:
       for i in xrange(0,num_points):
           g[i,:] *= float(1/pt_area[i]*10) # convert to V/cm
   del pt_area

   grad_mat = [g.tocsr() for g in grad_mat]

   phi_e = zeros((num_points))
   for filename in args[1:]:
       m = re.match(name+r'\.t(\d+)',filename)
       if not m:
           print "Skipping "+filename
       print "Processing "+filename
       file_number = m.group(1)

       in_file = open(filename, "r")
       time = in_file.readline()
       for i in xrange(0, num_points):
           line = in_file.readline().strip()
           phi_e[i] = float(line.split(" ")[0]) # Read Phi_e
       in_file.close()

       grad_mag = zeros((num_points))
       for g in grad_mat:
           grad_mag += g.matvec(phi_e)**2
       grad_mag = sqrt(grad_mag)

       out_file = open(name+".gm"+file_number, "w")
       print >>out_file, time,
       for g in grad_mag:
           print >>out_file, g
       out_file.close()
