#!/usr/bin/env python

import sys
import os
import re

def main():

    if (len(sys.argv) < 2):
	print("Usage: carp2vtk <meshname>")
	sys.exit()

    meshname = sys.argv[1]

    with open(meshname+".vtk", "w") as vtkfile:
	    vtkfile.write("# vtk DataFile Version 2.0\n")
	    vtkfile.write("Mesh "+meshname+"\n")
	    vtkfile.write("ASCII\nDATASET UNSTRUCTURED_GRID\n")
	    ptswritten = 0
	    with open(meshname+".pts") as ptsfile:
		    line = ptsfile.readline()    
		    numpts = int(line)
		    # print("Header indicates %d points" % numpts)
		    vtkfile.write("POINTS {} float\n".format(numpts))
		    line = ptsfile.readline()    
		    while line:
			    # we can just copy the points over
			    #result = re.findall(r'[e\d\.-]+', foo)
			    vtkfile.write(line)
			    ptswritten+=1
			    line = ptsfile.readline()
            if(ptswritten != numpts):
		    print("%d points written doesn't match header value of %, exiting" % (ptswritten, numpts))
		    sys.exit(1)
	    # now we have to read the whole elem file unfortunately to find out some header info
	    with open(meshname+".elem") as elemfile:
		            elements = []
			    elementTypes = []
			    regions = []
			    line = elemfile.readline()
			    numelem = int(line)
			    # print("Header indicates %d elements" % numelem)
			    line = elemfile.readline()
			    integerCount = 0
			    while line:
			            result = line.split()
				    elementType = result[0]
				    if(elementType == "Tt"):
					    integerCount+=4
					    # store indices for this element
					    elements.append([result[1], result[2], result[3], result[4]])
					    # 10 = tet
					    elementTypes.append(10)
					    regions.append(result[-1])
		                    elif(elementType == "Hx"):
					    integerCount+=8
					    elements.append([result[1], result[2], result[3], result[4], result[5], result[6], result[7], result[8]])
					    # 12 = hexahedron
					    elementTypes.append(12)
					    regions.append(result[-1])
		                    elif(elementType == "Py"):
					    integerCount+=5
					    elements.append([result[1], result[2], result[3], result[4], result[5]])
					    # 14 = pyramid
					    elementTypes.append(14)
					    regions.append(result[-1])
		                    elif(elementType == "Pr"):
					    integerCount+=6
					    elements.append([result[1], result[2], result[3], result[4], result[5], result[6]])
					    # 13 = triangular prism/wedge
					    elementTypes.append(13)
					    regions.append(result[-1])
                                    else:
					    print "Element type %s not recognized" % elementType
					    sys.exit(1)
                                    
			            line = elemfile.readline()

   	    # sanity checks
   	    if ( len(elements) != int(numelem) ):
   	       	   print ("%d elements not equal to header value of %d" % (len(elements), int(numelem)))
   		   sys.exit(1)
            if ( len(elementTypes) != len(elements) ):
   	           print("%d elementTypes not equal to %d elements, exiting" % (len(elementTypes), len(elements)))
   	           sys.exit(1)
   	    if ( len(regions) != len(elements) ):
   	           print("%d regions not equal to %d elements, exiting" % (len(regions), len(elements)))
   	           sys.exit(1)
   
            # now print out the headers and the data
	    # print("Printing cells with {} points and size {}".format(numelem, (numelem+integerCount)))
	    sizeTally = 0
            vtkfile.write("CELLS %d %d\n" % (numelem, numelem+integerCount))
   	    for element in elements:
		   vtkfile.write("{} ".format(len(element)))
		   sizeTally += 1
   	           for point in element[:-1]:
   	               vtkfile.write("{} ".format(point))
		       sizeTally += 1
   		   vtkfile.write("{}\n".format(element[-1]))
		   sizeTally += 1
            # print("size {}, size tally {}".format(numelem+integerCount, sizeTally))
   	    # cell types / element types
   	    vtkfile.write("CELL_TYPES %d\n" % numelem)
   	    for etype in elementTypes:
   	           vtkfile.write("{}\n".format(etype))
   		           
            # regions as cell data
   	    vtkfile.write("CELL_DATA %d\nSCALARS region_numbers int 1\nLOOKUP_TABLE default\n" % numelem)
   	    for region in regions:
   	           vtkfile.write("{}\n".format(region))
 
				   

if __name__ == '__main__':
    main()
