#!/usr/bin/env python

from vtk import *
import sys

x=vtkUnstructuredGridReader()
x.SetFileName(sys.argv[1])
x.Update()
print("Loaded")
