#!/usr/bin/env python

import sys
import re
import os
import optparse
import shutil
from sets import Set

try:
   from numpy import *
   import scipy as Sci
   import scipy.linalg
   _have_scipy = True
except (ImportError), e:
   print """
Scipy not installed.  Run the following command to install it. 
sudo yum install scipy
Without scipy, I can't convert .spec files to .lon files.
"""
   _have_scipy = False


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
   if not _have_scipy:
      sys.exit(1)

   parser = DictOptionParser(usage="Usage: %prog meshname surface")
   (options, args) = parser.parse_args()
   if len(args) != 2:
      print "Need the input meshname followed by a surface"
      parser.print_help()
      sys.exit(1)
   mesh_name = args[0]
   surface_name = args[1]

   #read in the surface
   surface_file = open(surface_name,"r")
   numtriangles = int(surface_file.readline())
   triangles = zeros((numtriangles, 3), 'i')
   for ii in xrange(0,numtriangles):
      triangle = [int(num) for num in surface_file.readline().split(" ")]
      triangles[ii,0] = triangle[0]
      triangles[ii,1] = triangle[1]
      triangles[ii,2] = triangle[2]
   
   #get the nearest neighbors for each point on the surface.
   original_neighbors = {}
   for ii in xrange(0,numtriangles):
      for jj in range(0,3):
         node = triangles[ii,jj]
         if not original_neighbors.has_key(node):
            original_neighbors[node] = Set()
         for kk in range(0,3):
            if not node == triangles[ii,kk]:
               original_neighbors[node].add(triangles[ii,kk])

   #enlarge the nearest neighbor network so we have enough points to solve the
   #quadratic system.
   neighbors = {}
   for node in original_neighbors.keys():
      if len(original_neighbors[node]) >= 5:
         neighbors[node] = original_neighbors[node]
      else:
         neighbors[node] = Set(original_neighbors[node])
         for neighbor in original_neighbors[node]:
            neighbors[node] |= original_neighbors[neighbor] - Set([node])

   #compute the mapping between the node number to the subset pts.
   ii=0
   index = {}
   for node in neighbors.keys():
      index[node] = ii
      ii += 1

   #read in the point data for the surface nodes.
   relevant_points = zeros((len(neighbors),3),'f')
   ptsfile = open(mesh_name+".pts","r")
   numpoints = int(ptsfile.readline())
   for ii in xrange(0,numpoints):
      line = ptsfile.readline()
      if neighbors.has_key(ii):
         a = [float(num) for num in line.split(" ")]
         for jj in range(0,3):
            relevant_points[index[ii],jj] = a[jj]

   gaussian_curv = {}
   mean_curv = {}
   #for each surface node
   for node in neighbors.keys():
      #compute a rotation matrix for each point to convert it into x,y,and z coordinates.
      center = relevant_points[index[node],:]
      shifted_points = zeros((len(neighbors[node]),3),'f')
      ii=0
      for neighbor in neighbors[node]:
         shifted_points[ii,:] = relevant_points[index[neighbor],:] - center
         ii += 1

      M = zeros((3,3),'f')
      for ii in range(0,len(neighbors[node])):
         for jj in range(0,3):
            for kk in range(0,3):
               M[jj,kk] += shifted_points[ii,jj]*shifted_points[ii,kk]
      (D,V) = linalg.eig(M)
      #print D
      #print V
      
      #find the minimum eigenvalue: this is the normal plane.
      min_index = 0
      for ii in range(1,3):
         if D[ii] < D[min_index]:
            min_index = ii

      #fit a least squares quadratic to the point
      A = zeros((len(neighbors[node]),5),'f')
      b = zeros((len(neighbors[node]),),'f')
      for ii in range(0,len(neighbors[node])):
         x = dot(V[:,(min_index+1)%3],shifted_points[ii,:])
         y = dot(V[:,(min_index+2)%3],shifted_points[ii,:])
         z = dot(V[:,min_index],shifted_points[ii,:])
         A[ii,0] = x*x
         A[ii,1] = x*y
         A[ii,2] = y*y
         A[ii,3] = x
         A[ii,4] = y
         b[ii] = z
      #print linalg.lstsq(A,b)
      x = linalg.lstsq(A,b)[0]
      a = x[0]
      b = x[1]
      c = x[2]
      d = x[3]
      e = x[4]
      
      #use these values to find the curvature
      #if not abs(d)+abs(e) < 1e-5:
      #   print "ERROR: ",a,b,c,d,e
      # this assertion should hold if my calculations are correct.
      denom = (1+d*d+e*e)
      gaussian_curv[node] = (4*a*c - b*b)/denom/denom
      mean_curv[node] = (a + c + a*e*e + c*d*d - b*d*e)/denom/sqrt(denom)

   for node in neighbors.keys():
      print node,gaussian_curv[node],mean_curv[node]
