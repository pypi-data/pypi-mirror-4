# Name:      physical_turtle/quadtree.py
# Purpose:   A quadtree index to speed up solid world searching
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

import unittest
import inspect

from physical_turtle.shapes import BBoxMixin, PolyGon

#-----------------------------------------------------------------------

class QuadTree(BBoxMixin):
    """ An implementation of a quad tree storing values.

        Based on http://www.pygame.org/wiki/QuadTree?parent=CookBook

        This version has been modified to store values and to support
        some extra methods.

    """

    def __init__(self, item_list=None, resolution=1, bounding_box=None, world=None):
        """ Create a quadtree node. The value to be stored is assumed
            to be '1' (one)

            @param item_list: [ ... rectangle ... ] - list of items to
                add at the start. Each item must have attributes left,
                right, top, bottom defining the bounding box. Each
                item may have a properties attribute, though this is
                not yet used.

            @param resolution: resursion stops when the box size is
                less than or equal to this.

            @param bounding_box: (l, r, t, b) - the box for this
                node. Generaly only used internally whan adding nodes,
                but it may be forced whan first called to create an
                expected space over which the quadtree will work.

            @param world: indicates the coordinate system to use.
        """
        assert (item_list is None or
                isinstance(item_list, (type(()), type([])))
                ), "item_list must be a list or a tuple"
        assert world is None, "Parameter world is not yet used"

        # The list of items that belong in this quadrant
        self.item_list = []
        self._value = None
        # The sub-quadrants are empty to start with.
        self.nw = self.ne = self.se = self.sw = None

        self.resolution = resolution

        #extract size information
        if bounding_box:
            l = self._left = bounding_box[0]
            t = self._top = bounding_box[1]
            r = self._right = bounding_box[2]
            b = self._bottom = bounding_box[3]
        elif item_list:
            # If there isn't a bounding box, then calculate it from
            # the item list.
            l = self._left = min(item.left for item in item_list)
            t = self._top = max(item.top for item in item_list)
            r = self._right = max(item.right for item in item_list)
            b = self._bottom = min(item.bottom for item in item_list)
        else:
            raise TypeError(
                "No item list and no bounding box leaves quadtree "
                "floating in space")

        # Stop if this is the end
        if abs(l - r) <= resolution or abs(t - b) <= resolution:
            if item_list is not None:
                self.item_list.extend(item_list)
                self._value = 1
            return # >>>>>>>>>>>>>>>>>>>>

        # Find this quadrant's centre
        self.cx = (l + r) * 0.5
        self.cy = (t + b) * 0.5

        self.extend(item_list)

    @property
    def value(self):
        return self._value

    def extend(self, item_list):
        """ Post the items in the given list into the quadtree
        
            @param item_list: [ ... rectangle ... ] - list of
                items to add at the start.

        """
        assert (isinstance(item_list, (type(()), type([])))
                ), "item_list must be a list or a tuple"

        nw_item_list = []
        ne_item_list = []
        se_item_list = []
        sw_item_list = []
        l, t, r, b = self.box_as_tuple
        
        if abs(l - r) <= self.resolution or abs(t - b) <= self.resolution:
            if item_list is not None:
                self.item_list.extend(item_list)
                self._value = 1
            return # >>>>>>>>>>>>>>>>>>>>

        for item in item_list:
            # Which of the sub-quadrants does the item overlap?
            #
            # The test here assumes that the item bounding box has
            # some tangible size. A box of zero size that sits at
            # the center of the quadrant will be ignored. So be
            # it.

            in_nw = item.left < self.cx and item.top > self.cy
            in_sw = item.left < self.cx and item.bottom < self.cy
            in_ne = item.right > self.cx and item.top > self.cy
            in_se = item.right > self.cx and item.bottom < self.cy
            # If it overlaps all 4 quadrants then insert it at the
            # current depth, otherwise append it to a list to be
            # inserted under every quadrant that it overlaps.
            if in_nw and in_ne and in_se and in_sw:
                self.item_list.append(item)
                self._value = 1
            else:
                if in_nw: nw_item_list.append(item)
                if in_ne: ne_item_list.append(item)
                if in_se: se_item_list.append(item)
                if in_sw: sw_item_list.append(item)
            
        # Create the sub-quadrants, recursively.
        if nw_item_list:
            try:
                self.nw.extend(nw_item_list)
            except AttributeError:
                self.nw = QuadTree(
                    nw_item_list, self.resolution, (l, t, self.cx, self.cy))
        if ne_item_list:
            try:
                self.ne.extend(ne_item_list)
            except AttributeError:
                self.ne = QuadTree(
                    ne_item_list, self.resolution, (self.cx, t, r, self.cy))
        if se_item_list:
            try:
                self.se.extend(se_item_list)
            except AttributeError:
                self.se = QuadTree(
                    se_item_list, self.resolution, (self.cx, self.cy, r, b))
        if sw_item_list:
            try:
                self.sw.extend(sw_item_list)
            except AttributeError:
                self.sw = QuadTree(
                    sw_item_list, self.resolution, (l, self.cy, self.cx, b))

    def _str_base(self):
        op = ["l %s, t %s, r %s, b %s" %(self.box_as_tuple)]
        op.append("items: %s" % str(["%s, %s, %s, %s" % x.box_as_tuple for x in self.item_list]))
        op.append("    nw")
        if self.nw:
            op_set = self.nw._str_base()
            op.extend(['    '+x for x in op_set])
        op.append("    ne")
        if self.ne:
            op_set = self.ne._str_base()
            op.extend(['    '+x for x in op_set])
        op.append("    se")
        if self.se:
            op_set = self.se._str_base()
            op.extend(['    '+x for x in op_set])
        op.append("    sw")
        if self.sw:
            op_set = self.sw._str_base()
            op.extend(['    '+x for x in op_set])
        return op

    def __str__(self):
        op = self._str_base()
        return '\n'.join(op)

    def has_value(self, rectangle):
        """ Returns True if the given rectangle contains something of
            non-zero value.
        
            @param rectangle: The bounding rectangle being tested against
                the quad-tree. This must possess left, top, right and
                bottom attributes.
        """
        if self._value is not None:
            return True

        # Recursively check the tree
        hits = False
        if (self.nw and rectangle.left < self.cx and
            rectangle.top > self.cy):
            hits = hits or self.nw.has_value(rectangle)
        if (self.sw and rectangle.left < self.cx and
            rectangle.bottom > self.cy):
            hits = hits or self.sw.has_value(rectangle)
        if (self.ne and rectangle.right > self.cx and
            rectangle.top > self.cy):
            hits = hits or  self.ne.has_value(rectangle)
        if (self.se and rectangle.right > self.cx and
            rectangle.bottom < self.cy):
            hits = hits or self.se.has_value(rectangle)
        return hits

    def hits(self, rectangle):
        """ Returns the set of all items in the quad-tree that overlap
            with a bounding rectangle.
        
            @param rectangle: The bounding rectangle being tested against
                the quad-tree. This must possess left, top, right and
                bottom attributes.
        """
        def overlaps(item):
            return (rectangle.right >= item.left and
                    item.right >= rectangle.left and
                    rectangle.top >= item.bottom and
                    item.top >= rectangle.bottom)
        
        # Find the hits at the current level.
        hits = set(item for item in self.item_list if overlaps(item))
        
        # Recursively check the lower quadrants.
        if (self.nw and rectangle.left < self.cx and
            rectangle.top > self.cy):
            hits |= self.nw.hits(rectangle)
        if (self.sw and rectangle.left < self.cx and
            rectangle.bottom < self.cy):
            hits |= self.sw.hits(rectangle)
        if (self.ne and rectangle.right > self.cx and
            rectangle.top > self.cy):
            hits |= self.ne.hits(rectangle)
        if (self.se and rectangle.right > self.cx and
            rectangle.bottom < self.cy):
            hits |= self.se.hits(rectangle)
 
        return hits

class TestQuadTree(unittest.TestCase):

    def test_qt_make_1(self):
        """ Will stop at box size 1 """
        tp = PolyGon(((0,0), (0, 1), (1, 1), (1, 0)))
        qt = QuadTree([tp])
        self.assertEqual(qt.value, 1)
        self.assertIsNone(qt.nw)
        self.assertIsNone(qt.ne)
        self.assertIsNone(qt.sw)
        self.assertIsNone(qt.se)

    def test_qt_make_2(self):
        """ Will stop because box fits this level """
        tp = PolyGon(((0,0), (0, 20), (20, 20), (20, 0)))
        qt = QuadTree([tp])
        self.assertEqual(qt.value, 1)
        self.assertIsNone(qt.nw)
        self.assertIsNone(qt.ne)
        self.assertIsNone(qt.sw)
        self.assertIsNone(qt.se)

    def test_qt_make_3(self):
        """ Polygon fits into 'ne' quadrant """
        tp = PolyGon(((0,0), (0, 20), (20, 20), (20, 0)))
        qt = QuadTree([tp], bounding_box=(-20, 20, 20, -20))
        self.assertIsNone(qt.value)
        self.assertIsNone(qt.nw)
        self.assertIsNotNone(qt.ne)
        self.assertIsNone(qt.sw)
        self.assertIsNone(qt.se)

    def test_qt_has_value_false(self):
        """ Polygon in 'ne' quadrant - look in 'se' quadrant """
        tp = PolyGon(((0,0), (0, 20), (20, 20), (20, 0)))
        qt = QuadTree([tp], bounding_box=(-20, 20, 20, -20))
        test_rect = PolyGon(((0, 0), (0, -20), (20, -20), (20, 0)))
        value_check = qt.has_value(test_rect)
        self.assertFalse(value_check)

    def test_qt_has_value_true(self):
        """ Polygon in 'ne' quadrant - look in 'ne' quadrant """
        tp = PolyGon(((0,0), (0, 20), (20, 20), (20, 0)))
        qt = QuadTree([tp], bounding_box=(-20, 20, 20, -20))
        test_rect = PolyGon(((0, 0), (0, 20), (20, 20), (20, 0)))
        value_check = qt.has_value(test_rect)
        self.assertTrue(value_check)
        
    def test_qt_hits_none(self):
        """ Polygon in 'ne' quadrant - look in 'se' quadrant """
        tp = PolyGon(((0,0), (0, 20), (20, 20), (20, 0)))
        qt = QuadTree([tp], bounding_box=(-20, 20, 20, -20))
        test_rect = PolyGon(((0, 0), (0, -20), (20, -20), (20, 0)))
        hit_list = qt.hits(test_rect)
        self.assertEqual(len(hit_list), 0)

    def test_qt_hits_found(self):
        """ Polygon in 'ne' quadrant - look in 'ne' quadrant """
        tp = PolyGon(((0,0), (0, 20), (20, 20), (20, 0)))
        qt = QuadTree([tp], bounding_box=(-20, 20, 20, -20))
        test_rect = PolyGon(((0, 0), (0, 20), (20, 20), (20, 0)))
        hit_list = qt.hits(test_rect)
        self.assertEqual(len(hit_list), 1)
        self.assertEqual(hit_list.pop().box_as_tuple, tp.box_as_tuple)
        
#-----------------------------------------------------------------------

if __name__ == '__main__':
    unittest.main(verbosity=2)

#-----------------------------------------------------------------------
