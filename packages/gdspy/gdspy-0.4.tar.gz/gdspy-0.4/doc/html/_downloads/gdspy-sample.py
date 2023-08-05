#!/usr/bin/python

########################################################################
##                                                                    ##
##  Copyright 2009-2012 Lucas Heitzmann Gabrielli                     ##
##                                                                    ##
##  This file is part of gdspy.                                       ##
##                                                                    ##
##  gdspy is free software: you can redistribute it and/or modify it  ##
##  under the terms of the GNU General Public License as published    ##
##  by the Free Software Foundation, either version 3 of the          ##
##  License, or any later version.                                    ##
##                                                                    ##
##  gdspy is distributed in the hope that it will be useful, but      ##
##  WITHOUT ANY WARRANTY; without even the implied warranty of        ##
##  MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the     ##
##  GNU General Public License for more details.                      ##
##                                                                    ##
##  You should have received a copy of the GNU General Public         ##
##  License along with gdspy.  If not, see                            ##
##  <http://www.gnu.org/licenses/>.                                   ##
##                                                                    ##
########################################################################

import os
import numpy
import gdspy

print('Using gdspy module version ' + gdspy.__version__)


## ------------------------------------------------------------------ ##
##  POLYGONS                                                          ##
## ------------------------------------------------------------------ ##


## First we need a cell to add the polygons to.
poly_cell = gdspy.Cell('POLYGONS')

## We define the polygon through its vertices.
points = [(0, 0), (2, 2), (2, 6), (-6, 6), (-6, -6), (-4, -4), (-4, 4),
          (0, 4)]

## Create the polygon on layer 1.
poly1 = gdspy.Polygon(1, points)

## Add the new polygon to the cell.
poly_cell.add(poly1)

## Create another polygon from the same set of points, but rotate it
## 180 degrees and add it to the cell.
poly2 = gdspy.Polygon(1, points).rotate(numpy.pi)
poly_cell.add(poly2)

## To create rectangles we don't need to give the 4 corners, only 2.
## Note that we don't need to create a variable if we are not going to
## use it, just add the rectangle directly to the cell.  Create a 
## rectangle in layer 2.
poly_cell.add(gdspy.Rectangle(2, (18, 1), (22, 2)))

## There are no circles in the GDSII specification, so rounded shapes
## are actually many-sided polygons.  Create a circle in layer 2,
## centered at (27, 2), and with radius 2.
poly_cell.add(gdspy.Round(2, (27, 2), 2))

## The Round class is quite versatile: it provides circles, pie slices,
## rings and ring sections, like this one in layer 2.
poly_cell.add(gdspy.Round(2, (23.5, 7), 15, inner_radius=14,
                          initial_angle=-2.0 * numpy.pi / 3.0,
                          final_angle=-numpy.pi / 3.0))


## ------------------------------------------------------------------ ##
##  PATHS                                                             ##
## ------------------------------------------------------------------ ##


path_cell = gdspy.Cell('PATHS')

## Start a path from the origin with width 1.
path1 = gdspy.Path(1, (0, 0))

## Add a straight segment to the path in layer 1, with length 3, going
## in the '+x' direction.
path1.segment(1, 3, '+x')

## Add a curve to the path by specifying its radius as 2 and its initial
## and final angles.
path1.arc(1, 2, -numpy.pi / 2.0, numpy.pi / 6.0)

## Add another segment to the path in layer 1, with length 4 and
## pointing in the direction defined by the last piece we added above.
path1.segment(1, 4)

## Add a curve using the turn command.  We specify the radius 2 and
## turning angle. The agnle can also be specified with 'l' and 'r' for
## left and right turns of 90 degrees, or 'll' and 'rr' for 180 degrees.
path1.turn(1, 2, -2.0 * numpy.pi / 3.0)

## Final piece of the path.  Add a straight segment and tapper the path
## width from the original 1 to 0.5.
path1.segment(1, 3, final_width=0.5)
path_cell.add(path1)

## We can also create parallel paths simultaneously.  Start 2 paths with
## width 0.5 each,nd pitch 1, originating where our last path ended.
path2 = gdspy.Path(0.5, (path1.x, path1.y), number_of_paths=2,
                   distance=1)

## Add a straight segment to the paths gradually increasing their
## distance to 1.5, in the direction in which the last path ended.
path2.segment(2, 3, path1.direction, final_distance=1.5)

## Path commands can be concatenated.  Add a turn and a tapper segment
## in one expression, followed by a final turn.
path2.turn(2, 2, -2.0 * numpy.pi / 3.0).segment(2, 4, final_distance=1)
path2.turn(2, 4, numpy.pi / 6.0)
path_cell.add(path2)

## Create another single path 0.5 wide, starting where the path above
## ended, and add to it a line segment in the 3rd layer in the '-y'
## direction.
path3 = gdspy.Path(0.5, (path2.x, path2.y))
path3.segment(3, 1, '-y')

## We can create paths based on parametric curves.  First we need to
## define the curve function, with 1 argument.  This argument will vary
## from 0 to 1 and the return value should be the (x, y) coordinates of
## the path.  This could be a lambda-expression if the function is
## simple enough.  We will create a spiral path.  Note that the function
## returns (0, 0) when t=0, so that our path is connected.
def spiral(t):
    r = 4 - 3 * t
    theta = 5 * t * numpy.pi
    x = 4 - r * numpy.cos(theta)
    y = -r * numpy.sin(theta)
    return (x, y)

## We can also create the derivative of the curve to pass to out path
## path member, otherwise it will be numerically calculated.  In the
## spiral case we don't want the exact derivative, but the derivative of
## the spiral as if its radius was constant.  This will ensure that our
## path is connected at the start (geometric problem of this kind of
## spiral).
def dspiral_dt(t):
    theta = 5 * t * numpy.pi
    dx_dt = numpy.sin(theta)
    dy_dt = -numpy.cos(theta)
    return (dx_dt, dy_dt)

## Add the parametric spiral to the path in layer 3.  Note that we can
## still tapper the width.  To make the curve smoother, we increase the
## number of evaluations of the function (fracture will be performed
## automatically to ensure polygons with less than 200 points).
path3.parametric(3, spiral, dspiral_dt, final_width=0,
                 number_of_evaluations=500)
path_cell.add(path3)

## Polygonal paths are defined by the points they pass through.  The
## width of the path can be given as a number, representing the path 
## width along is whole extension, or as a list, where each element is
## the width of the path at one point.  Our path will have width 0.5 in
## all points, except the last, where it will tapper up to 1.5.  More
## than 1 path can be defined in parallel as well (useful for buses).
## The distance between the paths work the same way as the width: it's
## either a constant number, or a list.  We create 5 parallel paths that
## are larger and further apart on the last point.  The paths are put in
## layers 4 and 5.  Since we have 5 paths, the list of layers will be
## run more than once, so the 5 paths will actually be in layers 4, 5, 4,
## 5, and 4.
points = [(20, 12), (24, 8), (24, 4), (24, -2)]
widths = [0.5] * (len(points) - 1) + [1.5]
distances = [0.8] * (len(points) - 1) + [2.4]
polypath = gdspy.PolyPath([4, 5], points, widths, number_of_paths=5,
                          distance=distances)

## We can round the corners of any Polygon or PolygonSet with the fillet
## method.  Here we use a radius of 0.2.
polypath.fillet(0.2)
path_cell.add(polypath)

## L1Paths use only segments in 'x' and 'y' directions, useful for some
## lithography mask writers.  We specify a path composed of 16 segments
## of length 4.  The turns after each segment can be either 90 degrees
## CCW (positive) or CW (negative).  The absolute value of the turns
## produces a scaling of the path width and distance between paths in
## segments immediately after the turn.
lengths = [4] * 16
turns = [-1, -1, 1, 1] * 3 + [-1, -2, 1, 0.5]
l1path = gdspy.L1Path(6, (-1, -11), '+y', 0.5, lengths, turns,
                      number_of_paths=3, distance=0.7)
path_cell.add(l1path)


## ------------------------------------------------------------------ ##
##  BOOLEAN OPERATIONS                                                ##
## ------------------------------------------------------------------ ##


## Boolean operations can be executed with polygons (either gdspy
## objects or point lists).  The operands are given as a list.  In this
## example we will have 2 operands which will be 2 PolygonSet objects.
bool_cell = gdspy.Cell('BOOLEAN')
primitives = []

## Both operands are a path with a ring inside, but with different
## widths.  This is how we create them.
for width in [2, 8]:

    ## Closed path in a square shape with rounded corners.  Boolean
    ## operations become slower with the number of points involved, so
    ## it's important to keep these to a minimum.
    bool_path = gdspy.Path(width, (0, 10))
    bool_path.segment(0, 30, '+y')
    bool_path.turn(0, 10, 'r', number_of_points=64)
    bool_path.segment(0, 30, '+x')
    bool_path.turn(0, 10, 'r', number_of_points=64)
    bool_path.segment(0, 30, '-y')
    bool_path.turn(0, 10, 'r', number_of_points=64)
    bool_path.segment(0, 30, '-x')
    bool_path.turn(0, 10, 'r', number_of_points=64)

    ## Ring inside the square path.
    ring = gdspy.Round(0, (25, 25), 25 + width * 0.5,
                       inner_radius=25 - width * 0.5,
                       number_of_points=256)

    ## We create a PolygonSet that contains both our path segments and
    ## ring, and then append it to our list of operands.
    primitives.append(gdspy.PolygonSet(0, bool_path.polygons +
                                       ring.polygons))

## The list of operands contains 2 polygon sets.  We will subtract the
## 1st (narrower) from the 2nd (wider).  For that we need to define a
## function that receives 2 integers (each representing an operand) and
## returns the operation we want executed.  Here we use a lambda 
## expression to do so.
subtraction = lambda p1, p2: p2 and not p1

## We perform the operation, put the resulting polygons in layer 1, and
## add to our boolean cell.
bool_cell.add(gdspy.boolean(1, primitives, subtraction, max_points=199))


## ------------------------------------------------------------------ ##
##  SLICING POLYGONS                                                  ##
## ------------------------------------------------------------------ ##


## If there is the need to cut a polygon or set of polygons, it's better
## to use the slice function than set up a boolean operation, since it
## runs much faster.  Slices are multiple cuts perpendicular to an axis.
slice_cell = gdspy.Cell('SLICE')
original = gdspy.Round(1, (0, 0), 10, inner_radius = 5)

## Slice the original ring along x = -7 and x = 7.
result = gdspy.slice(1, original, [-7, 7], 0)

## The result is a tuple of polygon sets, one for each slice.  To keep
## add the region betwen our 2 cuts, we chose result[1].
slice_cell.add(result[1])

## If the cut needs to be at an angle we can rotate the geometry, slice
## it, and rotate back.
original = gdspy.PolyPath(2, [(12, 0), (12, 8), (28, 8), (28, -8),
                              (12, -8), (12, 0)], 1, 3, 2)
original.rotate(numpy.pi / 3, center=(20, 0))
result = gdspy.slice(2, original, 7, 1)
result[0].rotate(-numpy.pi / 3, center=(20, 0))
slice_cell.add(result[0])


## ------------------------------------------------------------------ ##
##  REFERENCES AND TEXT                                               ##
## ------------------------------------------------------------------ ##


## Cells can contain references to other cells.
ref_cell = gdspy.Cell('REFS')
ref_cell.add(gdspy.CellReference(poly_cell, (0, 30), x_reflection=True))
ref_cell.add(gdspy.CellReference(poly_cell, (25, 0), rotation=180))

## References can be whole arrays.  Add an array of the boolean cell
## with 2 lines and 3 columns and 1st element at (50, -15).
ref_cell.add(gdspy.CellArray('BOOLEAN', 3, 2, (35, 35) ,(50, -15),
                             magnification=0.5))

## Text are also sets of polygons.  They have edges parallel to 'x' and
## 'y' only.
ref_cell.add(gdspy.Text(6, 'Created with gsdpy ' + gdspy.__version__,
                        7, (-7, -35)))


## ------------------------------------------------------------------ ##
##  OUTPUT                                                            ##
## ------------------------------------------------------------------ ##


## Create the full file name to save the GDSII layout.
name = os.path.abspath(os.path.dirname(os.sys.argv[0])) + os.sep +\
       'gdspy-sample'

## Output the layout to a GDSII file (default to all created cells).
## Set the units we used to micrometers and the precision to nanometers.
gdspy.gds_print(name + '.gds', unit=1.0e-6, precision=1.0e-9)
print('Sample gds file saved: ' + name + '.gds')

## Save an image of the boolean cell in a png file.  Resolution refers
## to the number of pixels per unit in the layout.
gdspy.gds_image([bool_cell], image_name=name, resolution=4,
                antialias=4)
print('Image of the boolean cell saved: ' + name + '.png')


## ------------------------------------------------------------------ ##
##  IMPORT                                                            ##
## ------------------------------------------------------------------ ##


## Import the file we just created, and extract the cell 'POLYGONS'. To
## avoid naming conflict, we will rename all cells.
gdsii = gdspy.GdsImport(name + '.gds',
                        rename={'POLYGONS':'IMPORT_POLY',
                                'PATHS': 'IMPORT_PATHS',
                                'BOOLEAN': 'IMPORT_BOOL',
                                'SLICE': 'IMPORT_SLICE',
                                'REFS': 'IMPORT_REFS'},
                        layers={1:7,2:8,3:9})

## Now we extract the cells we want to actually include in our current
## structure. Note that the referenced cells will be automatically
## extracted as well.
gdsii.extract('IMPORT_REFS')


## ------------------------------------------------------------------ ##
##  VIEWER                                                            ##
## ------------------------------------------------------------------ ##


## View the layout using a GUI.  Full description of the controls can
## be found in the online help at http://gdspy.sourceforge.net/
gdspy.LayoutViewer()
