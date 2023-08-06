# Name:      physical_turtle/solid_world.py
# Purpose:   Provide a manager for a 2D solid world.
# Copyright: (c) 2012/2013: Mike Sandford
#
# Permission is hereby granted, free of charge, to any person obtaining 
# a copy of this software and associated documentation files (the 
# "Software"), to deal in the Software without restriction, including 
# without limitation the rights to use, copy, modify, merge, publish, 
# distribute, sublicense, and/or sell copies of the Software, and to 
# permit persons to whom the Software is furnished to do so, subject 
# to the following conditions:
# 
# The above copyright notice and this permission notice shall be 
# included in all copies or substantial portions of the Software.
# 
# THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, 
# EXPRESS OR IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF 
# MERCHANTABILITY, FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. 
# IN NO EVENT SHALL THE AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY 
# CLAIM, DAMAGES OR OTHER LIABILITY, WHETHER IN AN ACTION OF CONTRACT, 
# TORT OR OTHERWISE, ARISING FROM, OUT OF OR IN CONNECTION WITH THE 
# SOFTWARE OR THE USE OR OTHER DEALINGS IN THE SOFTWARE.

#-----------------------------------------------------------------------

from __future__ import division # Do 'proper' division
import unittest
import math

from physical_turtle.shapes import (
    BBox,
    CircleEnclosure,
    StraightLine,
    PolyGon,
    CLIPPED,
    NOT_CLIPPED,
    COINCIDENT,
    )
from quadtree import QuadTree

#-----------------------------------------------------------------------

class SolidWorld(object):
    """ This class represents a solid 2D world through which a turtle
        might navigate. The class specifically represents part of
        space that are solid, in the sense that a turtle should never
        occupy those places.

        The solid world is built up by adding polygonal items that
        define their own area of solid space.

        A list of items can be given when the world is created, and
        new items can be added.

        Items can be removed, although this may take a noticable time,
        depending on the internal implementation.
        
    """

    def __init__(self, item_list=None):
        """ Set up the solid world

            @param item_list: [ ... polygon ... ]
        """
        self.item_list = None
        if item_list:
            self.item_list = item_list

        self.index = None
        if item_list:
            self.index = QuadTree(self.item_list)

    def extend(self, item_list):
        """ Add the given items to the world.

            @param item_list: [ ... polygon ... ]
        """
        assert isinstance(item_list, (type(()), type([])))
        # Identify the bounds of the new list
        l = min(item.left for item in item_list)
        t = max(item.top for item in item_list)
        r = max(item.right for item in item_list)
        b = min(item.bottom for item in item_list)
        bounding_box = BBox(l, t, r, b)
        if self.item_list:
            self.item_list.extend(item_list)
        else:
            self.item_list = item_list
        # Compare with index
        if self.index is None:
            self.index = QuadTree(self.item_list)            
        else:
            # Check that new items are inside the existing index
            i_l, i_t, i_r, i_b = self.index.box_as_tuple
            if l >= i_l and t <= i_t and r <= i_r and b >= i_b:
                self.index.extend(item_list)
            else:
                # Rebuild to allow for extra space 
                self.index = QuadTree(self.item_list)
                # For larger worlds it _might_ be better to expand by
                # growing quadtree nodes above the existing
                # tree. This must be done carefully to avoid
                # filling the tree with empty nodes.

    def remove(self, item):
        """ Remove a single item from the world

            @param item: PolyGon or similar
        """
        self.item_list.remove(item)
        # Oops. Rebuilding quadtrees is not that easy...
        self.index = QuadTree(self.item_list)

    def has_solid(self, region):
        """ Test if the region contains any solid areas

            @param region: object where object is a rectangle with
                top, left, right and bottom attributes.
        """
        return self.index.has_value(region)

    def _initial_impact(self, line_segment, radius):

        # First pass: get a maximum line length
        angle = line_segment.heading
        half_w = radius
        rotate_center = (line_segment.p1.x, line_segment.p1.y)
        line_left = line_segment.copy()
        line_left.rotate(-angle, rotate_center)
        line_left.p1 += (0, half_w)
        line_left.p2 += (0, half_w)
        line_left.rotate(angle, rotate_center)
        line_right = line_segment.copy()
        line_right.rotate(-angle, rotate_center)
        line_right.p1 += (0, -half_w)
        line_right.p2 += (0, -half_w)
        line_right.rotate(angle, rotate_center)

        if self.index is None:
            return line_segment #>>>>>>>>>>>>>>>>>>>>
        hit_list = self.index.hits(line_segment)
        line_clip = None
        for hit in hit_list:
            try_line_clip = hit.clip_incomming(line_segment)
            if try_line_clip is not None:
                if line_clip is not None:
                    line_clip = min(line_clip, try_line_clip)
                else:
                    line_clip = try_line_clip

        hit_list = self.index.hits(line_left)
        line_left_clip = None
        for hit in hit_list:
            try_line_left_clip = hit.clip_incomming(line_left)
            if try_line_left_clip is not None:
                if line_left_clip is not None:
                    line_left_clip = min(line_left_clip, try_line_left_clip)
                else:
                    line_left_clip = try_line_left_clip

        hit_list = self.index.hits(line_right)
        line_right_clip = None
        for hit in hit_list:
            try_line_right_clip = hit.clip_incomming(line_right)
            if try_line_right_clip is not None:
                if line_right_clip is not None:
                    line_right_clip = min(line_right_clip, try_line_right_clip)
                else:
                    line_right_clip = try_line_right_clip


        if (line_clip is None and
            line_left_clip is None and
            line_right_clip is None):
            return line_segment #>>>>>>>>>>>>>>>>>>>>

        param_u = 1 if line_clip is None else line_clip
        param_left = 1 if line_left_clip is None else line_left_clip
        param_right = 1 if line_right_clip is None else line_right_clip

        effective_u = min(param_u, param_left, param_right)

        return StraightLine(line_segment.p1,
                                line_segment.point(effective_u))

    def _turtle_collision(self, try_line, radius):
        """ Check that the length of the given line allows the
            circular turtle to fit at the end.

            :try_line: StraightLine - the result of the initial impact.

            :radius: Number - the radius to be checked.

            Returns the StraightLine object that just fits.
        """
        if try_line.p1.round() == try_line.p2.round():
            # Ignore zero length line
            return try_line
        lower_step_limit = 0.00000001
        # Use a percentage margin on radius for acceptable closeness
        allowed_measure = radius**2
        allowed_measure_upper = (1.01*radius)**2
        upper_u = 1
        lower_u = 0
        try_u = 1
        while upper_u - lower_u > lower_step_limit:
            try_point = try_line.point(try_u)
            try_measure = allowed_measure_upper+1 # Reasonable maximum
            hit_list = self.index.hits(CircleEnclosure(try_point, radius))
            for hit in hit_list:
                this_measure = hit.distance_measure(try_point)
                try_measure = min(try_measure, this_measure)
            # Try the exit as soon as we can
            if try_measure < allowed_measure:
                upper_u = try_u
            elif try_measure > allowed_measure:
                lower_u = try_u
            else:
                return StraightLine(try_line.p1,
                                    try_line.point(try_u))
            try_u = lower_u + (upper_u - lower_u)/2
        #+-
        # No convergence within this limit - return the slightly shorter line
        return StraightLine(try_line.p1, try_line.point(lower_u))

    def will_impact(self, line_segment, radius):
        """ Test if the given line segment will hit a solid area, and
            return a truncated line segment that just reaches the
            solid area. If the segment does not hit a solid area,
            return the original value.

            The end of the line segment is taken to be a circle of the
            given `radius`, so the test ensures that all points along
            the resulting path are at least `radius` away.

            @param line_segment: A StraighLine object or similar.

            @param radius: a radius of safety for the line.
        """
        # Algorithm:
        #
        # Find the longest possible length of the line by clipping the
        # given line and two parallel lines either side, spaced w/2
        # away. This ensures that the deemed turtle object can pass by
        # all peaks tht might be off to one side or the other.
        #
        # The result of the first clip does not guarantee that the end
        # of the liine is w away from any obstacle, so we backtrack.
        #
        # The backtrack is a binary chop on the result segment that
        # terminates when the distance from the end of the line to the
        # nearest obstacle is just greater than `radius`.
        if not self.index:
            return line_segment
        immediate_line = self._initial_impact(line_segment, radius)
        return self._turtle_collision(immediate_line, radius)

class TestThisModule(unittest.TestCase):

    def test_create_world_and_add_something(self):
        """ Create an initial world """
        sw = SolidWorld()
        # Add a polygon
        wall_poly = PolyGon(
            ((10, -10), (10, 10), (11, 10), (11, -10)))
        sw.extend([wall_poly])
        self.assertEqual(sw.index.box_as_tuple, (10, 10, 11, -10))
        # Add another one
        roof_poly = PolyGon(
            ((10, 10), (10, 11), (20, 11), (20, 10)))
        sw.extend([roof_poly])
        self.assertEqual(sw.index.box_as_tuple, (10, 11, 20, -10))

    def test_drive_into_wall_straight(self):
        wall_poly = PolyGon(
            ((10, -10), (10, 10), (11, 10), (11, -10)))
        sw = SolidWorld([wall_poly])
        turtle_line = StraightLine((0, 0), (15, 0))
        immediate_line = sw._initial_impact(turtle_line, 2)
        new_line = sw._turtle_collision(immediate_line, 2)
        self.assertAlmostEqual(new_line.p2.x, 8)
        self.assertAlmostEqual(new_line.p2.y, 0)

    def test_drive_into_wall_45_down(self):
        wall_poly = PolyGon(
            ((10, -10), (10, 10), (11, 10), (11, -10)))
        sw = SolidWorld([wall_poly])
        turtle_line = StraightLine((0, 10), (20, -10))
        new_line = sw.will_impact(turtle_line, 2)
        self.assertAlmostEqual(new_line.p2.x, 8)
        self.assertAlmostEqual(new_line.p2.y, 2)

    def test_drive_into_wall_45_up(self):
        wall_poly = PolyGon(
            ((10, -10), (10, 10), (11, 10), (11, -10)))
        sw = SolidWorld([wall_poly])
        turtle_line = StraightLine((0, -10), (20, 10))
        new_line = sw.will_impact(turtle_line, 2)
        self.assertAlmostEqual(new_line.p2.x, 8)
        self.assertAlmostEqual(new_line.p2.y, -2)

if __name__ == '__main__':
    unittest.main(verbosity=2)
