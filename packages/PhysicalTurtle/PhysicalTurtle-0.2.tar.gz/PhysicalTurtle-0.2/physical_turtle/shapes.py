# Name:      physical_turtle/shapes.py
# Purpose:   Basic geometric shapes used in managing collision detection.
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
from collections import namedtuple
import turtle
import math

#-----------------------------------------------------------------------

GLOBAL_PRECISION = 7

#-----------------------------------------------------------------------

class VerTex(turtle.Vec2D):
    """ Represents a point in space = vector from zero, zero to here.

        Extend the turtle version to have x, y properties and extra
        methods.
    """ 

    @property
    def x(self):
        return self[0]
    @property
    def y(self):
        return self[1]

    def round(self, precision=GLOBAL_PRECISION):
        return VerTex(round(self[0], precision),
                      round(self[1], precision))

    #-------------------------------------------------------------------
    # Stuff here uses Vec2D methods but returns a VerTex
    def rotate(self, angle):
        op = super(VerTex, self).rotate(angle)
        return VerTex(op[0], op[1])

    def __add__(self, other):
        op = super(VerTex, self).__add__(other)
        return VerTex(op[0], op[1])


    def __sub__(self, other):
        op = super(VerTex, self).__sub__(other)
        return VerTex(op[0], op[1])

    def __neg__(self, other):
        op = super(VerTex, self).__neg__(other)
        return VerTex(op[0], op[1])

    def __mul__(self, other):
        op = super(VerTex, self).__mul__(other)
        return VerTex(op[0], op[1])

    def __rmul__(self, other):
        op = super(VerTex, self).__rmul__(other)
        return VerTex(op[0], op[1])

    def distance_measure(self, other):
        return ((self.x - other.x)**2) + ((self.y - other.y)**2)

    def __str__(self):
        return "(%f, %f)" % self

#------------------------------------------------------------------------

class BBoxMixin(object):
    """ MixIn class to provide basic Bounding Box methods
    """

    @property
    def left(self):
        if self._left is None:
            self._make_box()
        return self._left
    
    @property
    def right(self):
        if self._left is None:
            self._make_box()
        return self._right

    @property
    def top(self):
        if self._left is None:
            self._make_box()
        return self._top

    @property
    def bottom(self):
        if self._left is None:
            self._make_box()
        return self._bottom

    @property
    def box_as_tuple(self):
        return self._left, self._top, self._right, self._bottom

    def box_overlap(self, other):
        """ Test if bounding box overlaps the bounding box of the
            other object.

            @param other: StraightLine

            Return True if there is an overlap
        """
        overlap_x = self.left <= other.right and other.left <= self.right
        overlap_y = self.bottom <= other.top and other.bottom <= self.top
        return overlap_x and overlap_y

    def _make_box(self):
        """ Set the values for _left, ...

            Must be provided by the outer class. This is only called
            if _left is None, so the outer class may avoid this by
            setting _left etc in its own time.
         """
        raise NotImplementedError
    
    
class BBox(BBoxMixin):
    """ Define a simple class that has left, right, top, bottom """
    
    def __init__(self, l, t, r, b):
        self._left = l
        self._right = r
        self._top = t
        self._bottom = b

class CircleEnclosure(BBoxMixin):
    """ Make a box around a circle """

    def __init__(self, centre_point, radius):
        self._left = centre_point.x - radius
        self._right = centre_point.x + radius
        self._top = centre_point.y + radius
        self._bottom = centre_point.y - radius

#-----------------------------------------------------------------------

CLIPPED = 'clipped'
NOT_CLIPPED = 'not clipped'
COINCIDENT = 'coincident'

class StraightLine(BBoxMixin):
    """ Define a straight line using a pair of either tuples, Vec2D or
        VerTex. The line provides a basic facility for detecting an
        intersection with another line.
    """

    def __init__(self, p1, p2):
        """ Define the line with these two points. The line has a
            direction, in that p1 is the start and p2 is the end. This
            is useful when clipping.

            @param p1: tuple|Vec2D|VerTex - start of line
            
            @param p2: tuple|Vec2D|VerTex - end of line
        """
        self.p1 = VerTex(p1[0], p1[1])
        self.p2 = VerTex(p2[0], p2[1])
        self._left = None
        self._right = None
        self._top = None
        self._bottom = None

    def _make_box(self):
        self._left = min(self.p1.x, self.p2.x)
        self._right = max(self.p1.x, self.p2.x)
        self._top = max(self.p1.y, self.p2.y)
        self._bottom = min(self.p1.y, self.p2.y)

    def __str__(self):
        op = ("line from %f, %f to %f, %f for %f" %
              (self.p1.x, self.p1.y, self.p2.x, self.p2.y, self.length))
        return op

    def copy(self):
        return StraightLine(self.p1, self.p2)

    def point(self, param_u):
        """ Return a VerTex calculated from p = p1 + u*(p2-p1)
        """
        diff_x = self.p2.x - self.p1.x
        diff_y = self.p2.y - self.p1.y
        new_x = self.p1.x + (param_u * diff_x)
        new_y = self.p1.y + (param_u * diff_y)
        return VerTex(new_x, new_y)

    def get_modified(self, param_u):
        """ Return a new StraightLine from p1 to p where p is
            calculated from param_u
        """
        return StraightLine(self.p1, self.point(param_u))

    @property
    def heading(self):
        """ Find the angle, in degrees, between the line and the x axis """
        p_diff = self.p2 - self.p1
        result = round(
            math.atan2(p_diff.y, p_diff.x)*180.0/math.pi, 10
            ) % 360.0
        return result

    @property
    def length(self):
        """ Length of the line """
        return math.sqrt(
            (self.p2.y - self.p1.y)**2 +
            (self.p2.x - self.p1.x)**2
            )

    def rotate(self, angle, about=None):
        """ Rotate the line in place

            @param angle: angle in degrees

            @param about: (x,y) or similar. Center of rotation. If not
                given use the line start point, p1
        """
        # Remember where we are, move to zero, rotate and move back
        if about is not None:
            first_point = VerTex(about[0], about[1])
        else:
            first_point = VerTex(self.p1.x, self.p1.y)
        self.p1 = self.p1 - first_point
        self.p2 = self.p2 - first_point
        self.p1 = self.p1.rotate(angle)
        self.p2 = self.p2.rotate(angle)
        self.p1 = self.p1 + first_point
        self.p2 = self.p2 + first_point


    def move_to(self, given_xy):
        """ Move the line to a new position """
        target_xy = VerTex(given_xy[0], given_xy[1])
        shift_xy = target_xy - self.p1
        self.p1 = target_xy
        self.p2 = self.p2 + shift_xy

    def round(self, precision=GLOBAL_PRECISION):
        """ Round all the points to something reasonable """
        self.p1 = self.p1.round(precision)
        self.p2 = self.p2.round(precision)

    def clip_to_line(self, other):
        """ Find the intersection point with the given, _other_, line.

            @param other: StraightLine

            Return u where u identifies the point of intersection _or_
            is None if the containing boxes did not overlap, the lines
            are parallel or the lines are coincident and u cannot be
            calculated.

            See
                https://en.wikipedia.org/wiki/Line-line_intersection

                and
                
                http://paulbourke.net/geometry/pointlineplane/
        """
        # Using a Bezier representation
        #
        # P = P1 + u*P2 for this line and O = O1 + t*O2 for the other
        #
        # u = ((O2.x-O1.x)(P1.y-O1.y) - (O2.y-O1.y)(P1.x-O1.x))/d
        #
        # t = ((P2.x-P1.x)(P1.y-O1.y) - (P2.y-P1.y)(P1.x-O1.x))/d
        #
        # d = (O2.y-O1.y)(P2.x-P1.x) - (O2.x-O1.x)(P2.y-P1.y)
        if not self.box_overlap(other):
            return None
        # Calculate some parts...
        s_x_diff = self.p2.x - self.p1.x
        s_y_diff = self.p2.y - self.p1.y
        o_x_diff = other.p2.x - other.p1.x
        o_y_diff = other.p2.y - other.p1.y
        param_u_numerator = (
            o_x_diff * (self.p1.y - other.p1.y) -
            o_y_diff * (self.p1.x - other.p1.x))
        param_t_numerator = (
            s_x_diff * (self.p1.y - other.p1.y) -
            s_y_diff * (self.p1.x - other.p1.x))
        denominator = (
            o_y_diff * s_x_diff -
            o_x_diff * s_y_diff)
        if (param_u_numerator == 0 and
            param_t_numerator== 0 and
            denominator == 0):
            # Coincident
            return None
        if denominator == 0:
            # Parallel
            return None
        param_u = param_u_numerator / denominator
        param_t = param_t_numerator / denominator
        # The following test allows us to skim the ends of the given
        # line. A stricter interpretation would detect the cases where
        # t == 0 or t == 1
        if 0 <= param_u <= 1 and 0 < param_t < 1:
            return param_u
        else:
            return None

    def nearest(self, given_vec):
        """ Find the nearest point on self to the given point

            :given_vec: VerTex The point in space that needs to know
                how far away frmo us it is.

            Taken from an article on http://www.gamasutra.com/ by Jeff
            Lander.

            First, create a vector, B, from the test point, t, to
            vertex p1. Dot this vector with the line segment A. This
            gives the cosine of the interior angle.  If this angle is
            90 degrees or greater, the nearest point is the vertex
            itself. If the angle is less than 90 degrees, create a
            vector C and dot it with the segment A.  If it returnes an
            angle greater than or equal to 90 degrees, point p2 would
            be the closest. If neither case is true a linear ratio of
            the two dot products will solve the problem.

        """
        # Check angle to first point
        dot_p1 = ((given_vec.x - self.p1.x)*(self.p2.x - self.p1.x) +
                  (given_vec.y - self.p1.y)*(self.p2.y - self.p1.y))
        if (dot_p1 <= 0):
            nearest_x = self.p1.x
            nearest_y = self.p1.y
            return VerTex(nearest_x, nearest_y)
        dot_p2 = ((given_vec.x - self.p2.x)*(self.p1.x - self.p2.x) +
                  (given_vec.y - self.p2.y)*(self.p1.y - self.p2.y))
        if (dot_p2 <= 0):
            nearest_x = self.p2.x
            nearest_y = self.p2.y
            return VerTex(nearest_x, nearest_y)
        nearest_x = (self.p1.x +
                     ((self.p2.x - self.p1.x) * dot_p1)/(dot_p1 + dot_p2))
        nearest_y = (self.p1.y +
                     ((self.p2.y - self.p1.y) * dot_p1)/(dot_p1 + dot_p2))
        
        return VerTex(nearest_x, nearest_y)

#-----------------------------------------------------------------------

class PolyGon(BBoxMixin):
    """ Capture the vertices of a polygon and return various things of
        interest.

        A polygon is assumed to be closed.
    """

    def __init__(self, vertices, **kwargs):
        """
            @param vertices: iterable( ... vertex-pair ... )

            @param kwargs: { ... property name:value ... }
        """
        self.vertices = [VerTex(x,y) for x,y in vertices]
        self.properties = kwargs
        # Find bounding box
        self._make_box()

    def _make_box(self):
        self._left = min([x for x,y in self.vertices])
        self._right = max([x for x,y in self.vertices])
        self._top = max([y for x,y in self.vertices])
        self._bottom = min([y for x,y in self.vertices])
        

    def __getitem__(self, k):
        return self.vertices[k]

    def __str__(self):
        op = ["%s"%str(x) for x in self.vertices]
        return ', '.join(op)

    def reduce(self):
        """ Remove redundant vertices """
        op = []
        v1 = self.vertices[0]
        op.append(v1)
        v2 = self.vertices[1]
        for v3 in self.vertices[2:]:
            # Do congruent triangles - avoiding divide by zero
            t1 = (v2.x-v1.x, v2.y-v1.y)
            t2 = (v3.x-v1.x, v3.y-v1.y)
            if t1[0] == 0 and t2[0] == 0:
                # Vertical line - v2 is redundant
                v2 = v3
            elif t1[1] == 0 and t2[1] == 0:
                # Horizontal line - v2 redundant
                v2 = v3
            elif t1[0] != 0 and t2[0] != 0 and t1[1]/t1[0] == t2[1]/t2[0]:
                # Angled line - v2 redundant
                v2 = v3
            else:
                op.append(v2)
                v1 = v2
                v2 = v3
        if v2 != self.vertices[0]:
            op.append(v2)
        self.vertices = op

    def __len__(self):
        return len(self.vertices)

    def move_to(self, given_xy):
        """ Move the current polygon to a new position """
        target_xy = VerTex(given_xy[0], given_xy[1])
        first_vertex = self.vertices[0]
        shift_xy = target_xy - first_vertex
        op = [position + shift_xy for position in self.vertices]
        self.vertices = op
        self._make_box()

    def rotate(self, angle):
        """ Rotate all the points in the polygon """
        # Remember where we are, move to zero, rotate and move back
        first_vertex = self.vertices[0]
        self.move_to((0, 0))
        op = [position.rotate(angle) for position in self.vertices]
        self.vertices = op
        self.move_to(first_vertex)
        self._make_box()

    def round(self, precision=GLOBAL_PRECISION):
        """ Round all the points to something reasonable """
        op = [position.round(precision) for position in self.vertices]
        self.vertices = op

    @property
    def lines(self):
        """ Return a list of straight lines that corresponds to this
            polygon
        """
        op = []
        p1 = self.vertices[0]
        first = p1
        for p2 in self.vertices[1:]:
            op.append(StraightLine(p1, p2))
            p1 = p2
        op.append(StraightLine(p1, first))
        return op

    @property
    def is_aligned_rectangle(self):
        """ Test to see if the polygon is actually a rectangle
            aligned with the axes.
        """
        v1 = self.vertices[0]
        for v2 in self.vertices[1:]:
            if v1.x != v2.x and v1.y != v2.y:
                return False
            v1 = v2
        if v1.x != v2.x and v1.y != v2.y:
            return False
        return True

    def clip_incomming(self, line_segment):
        """ Clip the given line segment on the assumption that the
            line starts outside the polygon.

            @param line_segment: StraightLine or similar
            
                The line segment is clipped in-place.

            Return the smallest 'u' value that was used.

        """
        line_clip = None
        for line_target in self.lines:
            param_u = line_segment.clip_to_line(line_target)
            if param_u is not None:
                if line_clip is not None:
                    line_clip = min(line_clip, param_u)
                else:
                    line_clip = param_u
        return line_clip

    def distance_measure(self, given_vec):
        """ Find the square of the shortest distance from the given
            point to the polygon.

        """
        measure = None
        for line_target in self.lines:
            nearest = line_target.nearest(given_vec)
            this_measure = given_vec.distance_measure(nearest)
            if measure is None:
                measure = this_measure
            else:
                measure = min(measure, this_measure)
        return measure

class TestVerTex(unittest.TestCase):

    def test_create_vertex(self):
        vx = VerTex(1,2)
        self.assertEqual(vx.x, 1)
        self.assertEqual(vx.y, 2)

    def test_rotate_angle(self):
        vx = VerTex(1,0)
        v90 = vx.rotate(90)
        v90 = v90.round()
        self.assertEqual(v90.x, 0)
        self.assertEqual(v90.y, 1)
        v45 = vx.rotate(45)
        v45 = v45.round()
        expected = round(math.sqrt(0.5), GLOBAL_PRECISION)
        self.assertEqual(v45.x, expected)
        self.assertEqual(v45.y, expected)

class TestBBox(unittest.TestCase):

    def testbbox(self):
        bb = BBox(0, 1, 2, 3)
        self.assertEqual(bb.left, 0)
        self.assertEqual(bb.top, 1)
        self.assertEqual(bb.right, 2)
        self.assertEqual(bb.bottom, 3)
        self.assertEqual(bb.box_as_tuple, (0, 1, 2, 3))

class TestStraightLine(unittest.TestCase):

    def test_box(self):
        ln = StraightLine((0, 1), (2, 3))
        self.assertEqual(ln.top, 3)
        self.assertEqual(ln.bottom, 1)
        self.assertEqual(ln.right, 2)
        self.assertEqual(ln.left, 0)

    def test_length(self):
        ln_1 = StraightLine((0, 0), (1, 1))
        self.assertEqual(round(ln_1.length, 7), 1.4142136)
        ln_1 = StraightLine((0, 0), (0,1))
        self.assertEqual(ln_1.length, 1)
        ln_1 = StraightLine((0, 0), (1,0))
        self.assertEqual(ln_1.length, 1)

    def test_point(self):
        ln_1 = StraightLine((2, 1), (6, 3))
        self.assertEqual(ln_1.point(0.5), VerTex(4,2))

    def test_box_overlap_ne(self):
        ln_1 = StraightLine((0, 0), (10, 20))
        ln_2 = StraightLine((5, 15), (30, -5))
        self.assertTrue(ln_1.box_overlap(ln_2))
        self.assertTrue(ln_2.box_overlap(ln_1))

    def test_clip_outside(self):
        ln_1 = StraightLine((0, 0), (10, 20))
        ln_2 = StraightLine((5, -1), (30, -21))
        self.assertEqual(ln_1.clip_to_line(ln_2), None)
        self.assertEqual(ln_2.clip_to_line(ln_1), None)

    def test_clip_inside_not(self):
        ln_1 = StraightLine((0, 0), (10, 20))
        ln_2 = StraightLine((5, 9), (30, -5))
        self.assertEqual(ln_1.clip_to_line(ln_2), None)
        self.assertEqual(ln_2.clip_to_line(ln_1), None)

    def test_clip_crossed_symmetrical(self):
        ln_1 = StraightLine((0, 0), (10, 20))
        ln_2 = StraightLine((10, 0), (0, 20))
        self.assertEqual(ln_1.clip_to_line(ln_2), 0.5)
        self.assertEqual(ln_2.clip_to_line(ln_1), 0.5)

    def test_clip_right_angle(self):
        ln_1 = StraightLine((0, 0), (30, 0))
        ln_2 = StraightLine((16, 3), (16, -5))
        self.assertEqual(ln_1.clip_to_line(ln_2), 16/30)
        self.assertEqual(ln_2.clip_to_line(ln_1), (-3)/(-8))

    def test_move_to_zero(self):
        ln_1 = StraightLine((16, 3), (16, -5))
        ln_1.move_to((0,0))
        self.assertEqual(ln_1.p1, (0, 0))
        self.assertEqual(ln_1.p2, (0, -8))
        
    def test_line_rotate_90(self):
        ln_1 = StraightLine((16, 3), (16, -5))
        ln_1.rotate(90)
        p_test = ln_1.p2
        ln_1.round()
        self.assertEqual(ln_1.p1, (16, 3))
        self.assertEqual(ln_1.p2, (24, 3))

    def test_line_rotate_center(self):
        ln_1 = StraightLine((16, 3), (16, -5))
        ln_1.rotate(90, (16, 0))
        p_test = ln_1.p2
        ln_1.round()
        self.assertEqual(ln_1.p1, (13, 0))
        self.assertEqual(ln_1.p2, (21, 0))

    def test_nearest_left(self):
        p1 = VerTex(100, 100)
        p2 = VerTex(250, -100)
        line_segment = StraightLine(p1, p2)
        p = VerTex(100, 150)
        n = line_segment.nearest(p)
        self.assertEqual(n, p1)

    def test_nearest_right_vertex(self):
        p1 = VerTex(100, 100)
        p2 = VerTex(250, -100)
        line_segment = StraightLine(p1, p2)
        p = VerTex(100, -212.5)
        n = line_segment.nearest(p)
        self.assertEqual(n, p2)

    def test_nearest_right_beyond(self):
        p1 = VerTex(100, 100)
        p2 = VerTex(250, -100)
        line_segment = StraightLine(p1, p2)
        p = VerTex(100, -213)
        n = line_segment.nearest(p)
        self.assertEqual(n, p2)

    def test_nearest_right_inside(self):
        p1 = VerTex(100, 100)
        p2 = VerTex(250, -100)
        line_segment = StraightLine(p1, p2)
        pr = VerTex(249.76, -99.68)
        p = VerTex(100, -212)
        n = line_segment.nearest(p)
        self.assertEqual(n, pr)

    def test_nearest_middle(self):
        p1 = VerTex(100, 100)
        p2 = VerTex(250, -100)
        line_segment = StraightLine(p1, p2)
        pr = VerTex(196, -28)
        p = VerTex(100, -100)
        n = line_segment.nearest(p)
        self.assertEqual(n, pr)
        
class TestPolyGon(unittest.TestCase):

    def test_create_polygon(self):
        pn = PolyGon(((0,1),(1,2),(4,3)))
        self.assertEqual(len(pn), 3)
        self.assertEqual(pn[0], VerTex(0,1))
        self.assertEqual(pn[1], VerTex(1,2))
        self.assertEqual(pn[2], VerTex(4,3))

    def test_reduce_aligned_polygon(self):
        test_poly = (
            (1, 3),
            (1, 5), # Expect removal
            (1, 10),
            (5, 10), # Expect removal
            (20, 10),
            (20, 3),
            (1, 3), # Expect removal
            )
        result_poly = (
            (1, 3),
            (1, 10),
            (20, 10),
            (20, 3),
            )
        pn_do = PolyGon(test_poly)
        pn_do.reduce()
        pn_tt = PolyGon(result_poly)
        self.assertEqual(pn_do.vertices, pn_tt.vertices)

    def test_reduce_nothing_to_do(self):
        test_poly = (
            (1, 2),
            (2, 3),
            (4, 2),
            (2, 2),
            )
        result_poly = test_poly
        pn_do = PolyGon(test_poly)
        pn_do.reduce()
        pn_tt = PolyGon(result_poly)
        self.assertEqual(pn_do.vertices, pn_tt.vertices)

    def test_reduce_angled(self):
        test_poly = (
            (0, 0),
            (1, 1), # Expect removal
            (2, 2),
            (3, 0),
            )
        result_poly = (
            (0, 0),
            (2, 2),
            (3, 0),
            )
        pn_do = PolyGon(test_poly)
        pn_do.reduce()
        pn_tt = PolyGon(result_poly)
        self.assertEqual(pn_do.vertices, pn_tt.vertices)

    def test_reduce_single_line(self):
        test_poly = (
            (1, 2),
            (2, 3),
            )
        result_poly = test_poly
        pn_do = PolyGon(test_poly)
        pn_do.reduce()
        pn_tt = PolyGon(result_poly)
        self.assertEqual(pn_do.vertices, pn_tt.vertices)

    def test_is_aligned_box(self):
        test_poly = (
            (0, 0),
            (5, 0),
            (5, 5),
            (0, 5),
            )
        pn_do = PolyGon(test_poly)
        self.assertTrue(pn_do.is_aligned_rectangle)

    def test_is_aligned_line(self):
        test_poly = (
            (0, 0),
            (5, 0),
            )
        pn_do = PolyGon(test_poly)
        self.assertTrue(pn_do.is_aligned_rectangle)

    def test_is_aligned_poly(self):
        w = 1
        h = 5
        test_poly = (
            (0, 0),
            (0, w),
            (h, w),
            (h, -w),
            (0, -w)
            )
        pn_do = PolyGon(test_poly)
        self.assertTrue(pn_do.is_aligned_rectangle)

    def test_is_aligned_not(self):
        test_poly = (
            (0, 0),
            (5, 1),
            (4, 5),
            (0, 4),
            )
        pn_do = PolyGon(test_poly)
        self.assertFalse(pn_do.is_aligned_rectangle)            

    def test_is_aligned_not_line(self):
        test_poly = (
            (0, 0),
            (5, 1),
            )
        pn_do = PolyGon(test_poly)
        self.assertFalse(pn_do.is_aligned_rectangle)

    def test_bounding_box(self):
        test_poly = (
            (0, 0),
            (6, 1),
            (4, 5),
            (0, 4),
            )
        pn_do = PolyGon(test_poly)
        self.assertEqual(pn_do.left, 0)
        self.assertEqual(pn_do.right, 6)
        self.assertEqual(pn_do.top, 5)
        self.assertEqual(pn_do.bottom, 0)

    def test_move_to_x(self):
        w = 2
        h = 5
        test_poly = (
            (0, 0),
            (0, w),
            (h, w),
            (h, -w),
            (0, -w)
            )
        result_poly = (
            (3, 0),
            (3, w),
            (h+3, w),
            (h+3, -w),
            (3, -w)
            )
        pn_do = PolyGon(test_poly)
        pn_do.move_to((3, 0))
        pn_tt = PolyGon(result_poly)
        self.assertEqual(pn_do.vertices, pn_tt.vertices)
        
    def test_rotate(self):
        w = 2
        h = 5
        test_poly = (
            (0, 0),
            (0, w),
            (h, w),
            (h, -w),
            (0, -w)
            )
        result_poly = (
            (0, 0),
            (-w, 0),
            (-w, h),
            (w, h),
            (w, 0)
            )
        pn_do = PolyGon(test_poly)
        pn_do.rotate(90)
        pn_tt = PolyGon(result_poly)
        pn_do.round()
        self.assertEqual(pn_do.vertices, pn_tt.vertices)
        
    def test_move_to_y(self):
        w = 2
        h = 5
        test_poly = (
            (0, 0),
            (0, w),
            (h, w),
            (h, -w),
            (0, -w)
            )
        result_poly = (
            (0, 3),
            (0, w+3),
            (h, w+3),
            (h, -w+3),
            (0, -w+3)
            )
        pn_do = PolyGon(test_poly)
        pn_do.move_to((0, 3))
        pn_tt = PolyGon(result_poly)
        self.assertEqual(pn_do.vertices, pn_tt.vertices)

    def test_get_lines(self):
        w = 2
        h = 5
        test_poly = (
            (0, 0),
            (0, w),
            (h, w),
            (h, -w),
            (0, -w)
            )
        expect_pairs = (
            ((0, 0),(0, w)),
            ((0, w),(h, w)),
            ((h, w),(h, -w)),
            ((h, -w),(0, -w)),
            ((0, -w), (0, 0))
            )
        pn_do = PolyGon(test_poly)
        op = pn_do.lines
        self.assertEqual(len(op), 5)
        for line_x, test_pair in zip(op, expect_pairs):
            self.assertEqual(line_x.p1.x, test_pair[0][0])
            self.assertEqual(line_x.p1.y, test_pair[0][1])
            self.assertEqual(line_x.p2.x, test_pair[1][0])
            self.assertEqual(line_x.p2.y, test_pair[1][1])

    def test_clip_not(self):
        """ Present a line segment that is not clipped """
        line_segment = StraightLine((15, 7), (11, 7))
        pn = PolyGon(
            ((5, 5), (5, 10), (10, 10), (10, 5)))
        self.assertIsNone(pn.clip_incomming(line_segment))

    def test_clip_simple(self):
        """ Present a line segment that is clipped on one edge """
        line_segment = StraightLine((15, 7), (8, 7))
        pn = PolyGon(
            ((5, 5), (5, 10), (10, 10), (10, 5)))
        self.assertEqual(pn.clip_incomming(line_segment), (10-15)/(8-15))
            
    def test_clip_double(self):
        """ Present a line segment that is clipped on two edges """
        line_segment = StraightLine((15, 8), (3, 8))
        pn = PolyGon(
            ((5, 5), (5, 10), (10, 10), (10, 5)))
        self.assertEqual(pn.clip_incomming(line_segment), (10-15)/(3-15))

#-----------------------------------------------------------------------

if __name__ == '__main__':
    unittest.main(verbosity=2)

#-----------------------------------------------------------------------
