#!/usr/bin/env python

import sys
import os
import re

def main():
    filepath = sys.argv[1]
    basename = os.path.splitext(filepath)[0]

    if len(sys.argv) < 2 or not os.path.isfile(filepath):
        print("File path {} does not exist. Exiting...".format(filepath))
        sys.exit()
    if len(sys.argv) == 3:
        # override output name
        basename = sys.argv[2]

    with open(filepath) as fp:
            line = fp.readline()    
        # first look for nodes
            while not re.search("NODE", line):
                line = fp.readline()
                # we found the nodes
            print("Found node entry")
            with open(basename+".pts", 'w') as ptsfile:
                ptsList = []
                # throw away NODE line
                line = fp.readline()
                entries = re.findall(r"[0-9\.\-e\+]+", line)
                print("First line is %s" % line)
                print("First line length is: %d" % len(entries))
                while len(entries) == 4:
                    floats = [float(i) for i in entries]
                    ptsList.append(floats)
                    line = fp.readline()
                    entries = re.findall(r"[0-9\.\-e\+]+", line)
                ptsfile.write("%d\n" % len(ptsList))
                for point in ptsList:
                    ptsfile.write("%.6f %.6f %.6f\n" % (point[1], point[2], point[3]))
                del(ptsList)
            print("Next line is %s" % line)
            if(line.find("S3R") != -1):
                print("Found triangle entry")
                with open(basename+".tris", "w") as trisfile:
                    trisList = []
                    line = fp.readline()
                    entries = re.findall(r"[0-9]+", line)
                    print("first line is %s" % line)
                    print("first line length is %d" % len(entries))
                    while len(entries) == 4:
                        ints = [int(i) for i in entries]
                        # carp is base 0 so we subtract 1
                        trisList.append(ints)
                        line = fp.readline()
                        entries = re.findall(r"[0-9]+", line)
                    trisfile.write("%d\n" % len(trisList))
                    for tri in trisList:
                        trisfile.write("%d %d %d\n" % (tri[1], tri[2], tri[3]))
            else:
                print("Expected triangle entry, found "+str(line)+" instead, continuing though")
            print("Next line is %s" % line)
            if(line.find("C3D4") != -1):
                print("Found tets entry, FIXME this doesn't have region numbers yet")
            else:
                print("Expected tets entry, found "+str(line)+" instead, exiting")
                sys.exit(1)
                # actually we can't just write this out, we need a line count and region numbers
                # we are also writing for now just for testing purposes
                # each element will be stored as a list that starts with 'Tt' for tets
                # these lists will be stored in a list
            elementList = []
            line = fp.readline()
            entries = re.findall(r"[0-9]+", line)
            print("first line is %s" % line)
            print("first line length is %d" % len(entries))
            while len(entries) == 5:
                ints = [int(i) for i in entries]
                # carp is base 0 so we subtract 1
                #elemfile.write("%d %d %d %d\n" % (ints[1]-1, ints[2]-2, ints[3]-1, ints[4]-1))
                myElement = ['Tt', ints[1]-1, ints[2]-1, ints[3]-1, ints[4]-1, 0] # region number added later
                elementList.append(myElement)
                line = fp.readline()
                entries = re.findall(r"[0-9]+", line)
            print("Done reading tets")
                # sanity check
            # now read the volume ranges:
            # *ELSET, ELSET=ES_Volume, GENERATE
            # 1,32217021,1
            # *SOLID SECTION, ELSET=ES_Volume, MATERIAL=nma0_material0
            # *ELSET, ELSET=ES_Volume interface_SCAR_LVWALL, GENERATE
            # 32217022,33958312,1
            # *SOLID SECTION, ELSET=ES_Volume interface_SCAR_LVWALL, MATERIAL=nma0_material0
            # *ELSET, ELSET=ES_Volume interface_GZ_LVWALL, GENERATE
            # 33958313,34080458,1
            # *SOLID SECTION, ELSET=ES_Volume interface_GZ_LVWALL, MATERIAL=nma0_material0
            # *ELSET, ELSET=ES_Volume GZ, GENERATE
            # 34080459,34081997,1
            # *SOLID SECTION, ELSET=ES_Volume GZ, MATERIAL=nma0_material0
            # *ELSET, ELSET=ES_Volume LVWALL, GENERATE
            # 34081998,34081998,1
            # *SOLID SECTION, ELSET=ES_Volume LVWALL, MATERIAL=nma0_material0
            # *END PART
            
            # these appear to be written in order, so we will assume they are.

            with open(basename+".elem", "w") as elemfile:
                with open(basename+".lon", "w") as lonfile:
                    # write header for element file
                    elemfile.write("%d\n" % len(elementList))
                    # write header for lon file
                    lonfile.write("1\n")
                    
                    regions = {}
                    regions["LVWALL"] = 1
                    regions["GZ"] = 2
                    regions["SCAR"] = 3
                    regionId = 1 # default to lvwall/normal
                    
                    # to get to the region definitions, we need to skip the surfaces
                    # do this until we get to the end of the part definition
                    
                    while line and line.find("END PART") == -1:
                        while line and line.find("ELSET, ELSET=") == -1:
                            line = fp.readline()
                        line = re.sub("(\\r|)\\n$", "", line)
                        # now we should be at a volume. We are looking for ES_Volume foo
                        # the format is REGION or interface_REGIONA_REGIONB
                        # this means that it is where REGIONA intersects REGIONB
                        # We defer to REGIONA in this scheme
                        match = re.match("^.*MAT([0-9]+).*$", line)
                        if not match:
                            break
                        # now read the range
                        line = fp.readline()
                        elementRange = re.split(r',', line)
                        elementRange = elementRange[:2] # throw away the last one
                        elementRange[0] = int(elementRange[0])
                        elementRange[1] = int(elementRange[1])
                        if match.group(1) == "0":
                            # this is the main volume which is healthy tissue
                            regionId = regions["LVWALL"]
                            print("Setting region to LVWALL")
                        elif match.group(1) == "1":
                            regionId = regions["SCAR"]
                            print("Setting region to SCAR")
                        elif match.group(1) == "2":
                            regionId = regions["GZ"]
                            print("Setting region to GZ")
                        else:
                            print(words)
                            print("Shouldn't have reached this point, exiting.")
                            sys.exit(1)
                        print("Processing regionId %d from element %d to %d" % (regionId, elementRange[0], elementRange[1]))
                        for ielement in range(elementRange[0], elementRange[1]+1):
                            element = elementList[ielement-1]
                            elemfile.write("%s %d %d %d %d %d\n" % (element[0], element[1], element[2], element[3], element[4], regionId))
                            lonfile.write("1 0 0\n") # temporary file created so we can run carp and assign fibers
            print("Next line is %s" % line)

if __name__ == '__main__':
    main()
