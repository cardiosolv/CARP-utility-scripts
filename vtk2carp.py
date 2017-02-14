#!/usr/bin/env python

from vtk import *
import sys, getopt
import gzip
import re

usagestring="Usage: vtk2carp.py [-h|--help] | [-i <vtkfile>|--input=<vtkfile> -m <string>|--meshname=<string> [-r <tissue region 1, 2, ..., N>|--regions=<tissue region 1, 2, ..., N>"

inputfile=''
meshname=''
regions=[]

try:
	opts, args = getopt.getopt(sys.argv[1:], "hi:m:r:", ["help", "input=", "meshname=", "regions="])
except getopt.GetoptError as err:
	print str(err)
	print usagestring
	sys.exit(2)

for opt, arg in opts:
	print "Processing option: "+opt+", argument: "+arg
	if opt in ("-h", "--help"):
		print "Help:"
		print usagestring
		sys.exit(0)
	elif opt in ("-i", "--input"):
		inputfile = arg
		print "Input: "+inputfile
	elif opt in ("-m", "--meshname"):
		meshname = arg
		print "Meshname: "+meshname
	elif opt in ("-r", "--regions"):
		regions = re.split(', *', arg)
		print "Using regions "+', '.join(map(str, regions))
	 
if not inputfile or not meshname:
	print "Invalid Input:"
	print usagestring
	sys.exit(2)

reader = vtk.vtkUnstructuredGridReader()
reader.SetFileName(inputfile)
reader.Update()

ugrid = reader.GetOutput()


points = ugrid.GetPoints()
npoints = points.GetNumberOfPoints()

ptshandle = gzip.open(meshname+'.pts.gz', 'wb')
ptshandle.write("%d\n" % npoints)
for ipoint in range(npoints):
	# print "%f %f %f" % points.GetPoint(ipoint)
	ptshandle.write("%f %f %f\n" % points.GetPoint(ipoint))
ptshandle.close()
del points

cells = ugrid.GetCells()
ncells = cells.GetNumberOfCells()

cdata = ugrid.GetCellData()
cscalars = cdata.GetScalars()

elemhandle = gzip.open(meshname+'.elem.gz', 'wb')
elemhandle.write("%d\n" % ncells)

lonhandle = gzip.open(meshname+'.lon.gz', 'wb')
lonhandle.write("1\n")

for icell in range(ncells):
	cellpointlist = []
	cell = ugrid.GetCell(icell)
	# add a check here to make sure it's a tet or hex
	ncellpoints = cell.GetNumberOfPoints()
	elementtype = "INVALID"
	if ncellpoints == 4:
		elementtype = "Tt"
	elif ncellpoints == 8:
		elementtype = "Hx"
	else:
		print "ERROR: invalid element type, exiting"
		exit(1)

	for cellpoint in range(cell.GetNumberOfPoints()):
		id = cell.GetPointId(cellpoint)
		cellpointlist.append(id)
	cregion = cscalars.GetValue(icell)

	elemhandle.write(elementtype+' '+' '.join(map(str, cellpointlist))+' '+str(cregion)+'\n')
	if regions:
		if str(cregion) in regions:
			lonhandle.write("1 0 0\n")
		else:
			lonhandle.write("0 0 0\n")
	else:
		lonhandle.write("1 0 0\n")

elemhandle.close()
lonhandle.close()
