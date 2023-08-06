# Name:      physical_turtle/turtle_main.py
# Purpose:   
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

import turtle as _original_turtle_module

from physical_turtle.solid_world import SolidWorld
from physical_turtle.shapes import VerTex, StraightLine, PolyGon

#-----------------------------------------------------------------------

# Import the remainder of the turtle module to retain
# compatability. Leave out the turtle functions that have been
# generated automatically from the original turtle.

# Classes (except Turtle)
from turtle import (
    ScrolledCanvas, TurtleScreen, Screen,
    RawTurtle, RawPen, Pen, Shape, Vec2D,)

# Screen Functions
from turtle import (
    addshape, bgcolor, bgpic, bye,
    clearscreen, colormode, delay, exitonclick, getcanvas,
    getshapes, listen, mode, onkey, onscreenclick, ontimer,
    register_shape, resetscreen, screensize, setup,
    setworldcoordinates, title, tracer, turtles, update,
    window_height, window_width,)

# turtle functions
from turtle import (
    back, backward, begin_fill, begin_poly, bk,
    circle, clear, clearstamp, clearstamps, clone, color,
    degrees, distance, dot, down, end_fill, end_poly, fd,
    fill, fillcolor, forward, get_poly, getpen, getscreen,
    getturtle, goto, heading, hideturtle, home, ht, isdown,
    isvisible, left, lt, onclick, ondrag, onrelease, pd,
    pen, pencolor, pendown, pensize, penup, pos, position,
    pu, radians, right, reset, resizemode, rt,
    seth, setheading, setpos, setposition, settiltangle,
    setundobuffer, setx, sety, shape, shapesize, showturtle,
    speed, st, stamp, tilt, tiltangle, towards, tracer,
    turtlesize, undo, undobufferentries, up, width,
    window_height, window_width, write, xcor, ycor,)

# Utilities
from turtle import (
    write_docstringdict, done, mainloop,)

# Math functions
from turtle import (
    acos, asin, atan, atan2, ceil, cos, cosh,
    e, exp, fabs, floor, fmod, frexp, hypot, ldexp, log,
    log10, modf, pi, pow, sin, sinh, sqrt, tan, tanh,
    )

_tg_turtle_functions = [
    # Start with genuine Turtle functions
    'back', 'backward', 'begin_fill', 'begin_poly', 'bk',
    'circle', 'clear', 'clearstamp', 'clearstamps', 'clone', 'color',
    'degrees', 'distance', 'dot', 'down', 'end_fill', 'end_poly', 'fd',
    'fill', 'fillcolor', 'forward', 'get_poly', 'getpen', 'getscreen',
    'getturtle', 'goto', 'heading', 'hideturtle', 'home', 'ht', 'isdown',
    'isvisible', 'left', 'lt', 'onclick', 'ondrag', 'onrelease', 'pd',
    'pen', 'pencolor', 'pendown', 'pensize', 'penup', 'pos', 'position',
    'pu', 'radians', 'right', 'reset', 'resizemode', 'rt',
    'seth', 'setheading', 'setpos', 'setposition', 'settiltangle',
    'setundobuffer', 'setx', 'sety', 'shape', 'shapesize', 'showturtle',
    'speed', 'st', 'stamp', 'tilt', 'tiltangle', 'towards', 'tracer',
    'turtlesize', 'undo', 'undobufferentries', 'up', 'width',
    'window_height', 'window_width', 'write', 'xcor', 'ycor',
    # Add in the ones we define here
    'last_distance', 'touch_left', 'touch_right', 'touch_front',
    'touch_back', 'pen_set_solid', 'pen_unset_solid',
    ]

#-----------------------------------------------------------------------

__all__ = ['Turtle'] +  _tg_turtle_functions + _original_turtle_module._tg_classes + _original_turtle_module._tg_screen_functions + _original_turtle_module._tg_utilities

#-----------------------------------------------------------------------

solid_world = SolidWorld()

def clear_solid_world():
    global solid_world
    solid_world = SolidWorld()

#-----------------------------------------------------------------------

class Turtle(_original_turtle_module.Turtle):
    """ A new Turtle class that can detect things in its surroundings.

        This is an extension for the Python turtle module that
        provides a physical space for a turtle to inhabit. The initial
        aim is to provide areas of solid space that the turtle cannot
        move into.

        The Turtle class is extended with the following methods and
        attributes.  This list may change as the first version of this
        package is developed.

        Attributes:

        * touch_left, touch_right, touch_front, touch_back

          Each one returns True if the Turtle would not be able to move in
          that direction.

        * last_distance

          The distance travelled in the preceding forward or backward
          movement. Since the turtle is not able to move through a solid area
          this distance may be less than the distance originally called for.

        Methods:

        * pen_set_solid()

          Set a pen property so that any movement of the turtle with the pen
          down creates a solid area. The pen colour is not affected, so that
          the lines shown on the screen correspond to lines of solidity in
          the physical space.

          The solid area created by the turtle move is a rectangle
          corresponding to the length of the move and the width of the pen.

          No solid area is drawn in the pen is up.

          The action of filling a polygon with a colour does not create solid
          space.

        * pen_unset_solid()

          Reverses the action of pen_set_solid so that turtle movement does
          not create solid areas.        
    """

    def __init__(self, *args, **kwargs):
        super(Turtle, self).__init__(*args, **kwargs)
        self._last_distance = 0
        self._is_solid = False
        self._safety_radius = 3
        self._stick_length = self._safety_radius

    def last_distance(self):
        return self._last_distance

    def touch_left(self):
        """ True if the turtle is less than a skip distance away from
            solid space
        """
        is_down = self.isdown()
        if not is_down:
            # Must be pendown to be able to bump into things
            return False
        this_screen = self.getscreen()
        this_tracer = this_screen.tracer()
        this_screen.tracer(0)
        self.left(90)
        self.forward(self._stick_length)
        if round(self.last_distance(),7) < self._stick_length:
            op = True
        else:
            op = False
        self.undo() # forward motion
        self.undo() # rotate
        this_screen.tracer(this_tracer)
        return op

    def touch_right(self):
        """ True if the turtle is less than a skip distance away from
            solid space
        """
        is_down = self.isdown()
        if not is_down:
            # Must be pendown to be able to bump into things
            return False
        this_screen = self.getscreen()
        this_tracer = this_screen.tracer()
        this_screen.tracer(0)
        self.right(90)
        self.forward(self._stick_length)
        if round(self.last_distance(),7) < self._stick_length:
            op = True
        else:
            op = False
        self.undo() # forward motion
        self.undo() # rotate
        this_screen.tracer(this_tracer)
        return op

    def touch_front(self):
        """ True if the turtle is less than a skip distance away from
            solid space
        """
        is_down = self.isdown()
        if not is_down:
            # Must be pendown to be able to bump into things
            return False
        this_screen = self.getscreen()
        this_tracer = this_screen.tracer()
        this_screen.tracer(0)
        self.forward(self._stick_length)
        if round(self.last_distance(),7) < self._stick_length:
            op = True
        else:
            op = False
        self.undo() # forward motion
        this_screen.tracer(this_tracer)
        return op

    def touch_back(self):
        """ True if the turtle is less than a skip distance away from
            solid space
        """
        is_down = self.isdown()
        if not is_down:
            # Must be pendown to be able to bump into things
            return False
        this_screen = self.getscreen()
        this_tracer = this_screen.tracer()
        this_screen.tracer(0)
        self.forward(-self._stick_length)
        if round(self.last_distance(),7) < self._stick_length:
            op = True
        else:
            op = False
        self.undo()
        this_screen.tracer(this_tracer)
        return op

    def pen_set_solid(self):
        """ Set the turtle to be able to draw shapes in solid space """
        self._is_solid = True

    def pen_unset_solid(self):
        """ Set the turtle back to normal """
        self._is_solid = False

    #-------------------------------------------------------------------
    # Internals...
    def _goto(self, given_place):
        """ Move the pen a given distance, thereby drawing a line if
            pen is down. All other methods for turtle movement depend
            on this one.

            If the turtle would impact solid space, reduce the target
            distance so that the movement stops short of impact.

            @param given_place: number - the distance to be drawn in the
                current direction.

            Do not check if the pen is up: The live turtle must be
            able toget to wherever it has to to start drawinf in the
            solid world.

            Do not check if the pen is solid. This allows the free
            drawing of initial conditions.
        """
        if not self.isdown() or self._is_solid:
            target_place = given_place
        else:
            target_place = self.check_ahead(given_place)
        self._last_distance = self.distance(target_place)
        self.draw_solid(self._last_distance)
        super(Turtle, self)._goto(target_place)

    def check_ahead(self, given_place):
        """ Look ahead along the line to be drawn to see if the turtle
            will hit anything solid.

            Return the new position it is safe for the turtle to travel to.

            @param given_place: Vec2D - the end position of the line
                to be drawn.
            
        """
        line_segment = StraightLine(self._position, given_place)
        new_line_segment = solid_world.will_impact(line_segment,
                                                   self._safety_radius)
        return new_line_segment.p2

    def draw_solid(self, given_distance):
        """ Check if the movement is supposed to create a solid area.

            If so, define the appropriate rectangle and add it to the
            solid world.

            @param given_distance: number - the distance to be drawn in the
                current direction.
        """
        if not self._is_solid:
            return
        # Create a polygon of correspondng to line width and distance,
        # where the start point is (0, 0).
        w = self._pensize/2
        solid = PolyGon(
            ((0, 0), (0, w),
             (given_distance, w), (given_distance, -w),
             (0, -w))
            )
        # Rotate the polygon to the current heading
        solid.rotate(self.heading())
        # Now shift it to the actual current position
        solid.move_to(self._position)
        solid_world.extend([solid])

#-----------------------------------------------------------------------

## Use our new turtle for the anonymous turtle
Pen = Turtle

def _getpen():
    """Create the 'anonymous' turtle if not already present."""
    if Turtle._pen is None:
        Turtle._pen = Turtle()
    return Turtle._pen

#-----------------------------------------------------------------------

## The following mechanism makes all methods of RawTurtle and Turtle
## available as functions. So we can enhance, change, add, delete
## methods to these classes and do not need to change anything
## here.

## We have to do this here because some of them may have been
## redefined in our new Turtle
        
## Copied from original turtle.

for methodname in _tg_turtle_functions:
    pl1, pl2 = _original_turtle_module.getmethparlist(
        eval('Turtle.' + methodname))
    if pl1 == "":
        continue
    defstr = ("def %(key)s%(pl1)s: return _getpen().%(key)s%(pl2)s" %
                                   {'key':methodname, 'pl1':pl1, 'pl2':pl2})
    exec defstr
    eval(methodname).__doc__ = _original_turtle_module._turtle_docrevise(
        eval('Turtle.'+methodname).__doc__)

del pl1, pl2, defstr

## Now for some tests

class TestThisModule(unittest.TestCase):

    def setUp(self):
        clear_solid_world()

    def test_create_turtle(self):
        """ Create a turtle and check key attribute """
        pt = Turtle()
        # Confirm it is one of ours
        self.assertTrue(hasattr(pt, 'touch_front'))

    def test_make_wall(self):
        """ Make a wall and confirm it is in solid world """
        pt = Turtle()
        pt.pensize(0)
        pt.pen_set_solid()
        pt.forward(20)
        self.assertEqual(pt.pos(), (20, 0))
        pt.left(90)
        pt.forward(10)
        self.assertEqual(pt.pos(), (20, 10))
        pt.left(90)
        pt.forward(20)
        self.assertEqual(VerTex(pt.pos()[0], pt.pos()[1]).round(), VerTex(0, 10))
        pt.left(90)
        pt.forward(10)
        self.assertEqual(VerTex(pt.pos()[0], pt.pos()[1]).round(), (0, 0))
        pt.left(90)
        pt.pen_unset_solid()
        poly_set = solid_world.item_list
        # 4 'forward' moves
        self.assertEqual(len(poly_set), 4)

    def test_blocked_by_line(self):
        """ Draw a solid line and drive headlong at it """
        # Draw the target line
        pt = Turtle()
        pt.penup()
        pt.goto(20, -10)
        pt.left(90)
        pt.pendown()
        #pt.pensize(0)
        pt.pen_set_solid()
        pt.forward(20)
        # Start a new Turtle
        ln = Turtle()
        ln.forward(50)
        self.assertTrue(ln.last_distance() <
                        20-(pt.pensize()/2)-ln._safety_radius)

    def test_jump_line_fails(self):
        """ Draw a wall at zero and try to cross it """
        # Draw the target line
        pt = Turtle()
        pt.penup()
        pt.goto(0, -10)
        pt.left(90)
        pt.pendown()
        pt.pen_set_solid()
        pt.forward(20)
        # Start a new Turtle
        ln = Turtle()
        ln.forward(50)
        self.assertEqual(round(ln.last_distance(), 7), 0)

    def test_cross_a_box_fails(self):
        """ Draw a box and attempt to cross it """
        pt = Turtle()
        pt.pensize(0)
        pt.forward(20)
        pt.pen_set_solid()
        pt.left(90)
        pt.forward(10)
        pt.left(90)
        pt.forward(10)
        pt.left(90)
        pt.forward(10)
        pt.left(90)
        pt.pen_unset_solid()
        # Draw a line
        ln = Turtle()
        ln.goto(-5, 0) # orthogonal to something.
        ln.goto(-5, 5)
        ln.forward(100)
        self.assertEqual(round(ln.last_distance()),
                         15-(pt.pensize()/2)-ln._safety_radius)

    def test_start_angled_from_coincident_place(self):
        """ Start at zero, with a line through it - cannot escape"""
        pt = Turtle()
        pt.left(90)
        pt.pen_set_solid()
        pt.pensize(0)
        pt.forward(20) # 20 up.
        pt.pen_unset_solid()
        # Draw a line
        ln = Turtle()
        ln.goto(-5, 5)
        pos = ln.position()
        pos = (round(pos[0], 7), round(pos[1], 7))
        self.assertEqual(pos, (0,0))

    def test_start_ortho_from_coincident_place(self):
        """ Start at zero, with a line through it - cannot escape"""
        pt = Turtle()
        pt.left(90)
        pt.pen_set_solid()
        pt.pensize(0)
        pt.forward(20) # 20 up.
        pt.pen_unset_solid()
        # Draw a line
        ln = Turtle()
        ln.goto(-5, 0)
        pos = ln.position()
        pos = (round(pos[0], 7), round(pos[1], 7))
        self.assertEqual(pos, (0,0))

    def test_touch_front(self):
        pt = Turtle()
        # Draw a line to bump into
        pt.penup()
        pt.goto(-10, 10)
        pt.pendown()
        pt.pen_set_solid()
        pt.forward(20)
        pt.pen_unset_solid()
        ln = Turtle()
        ln.left(90) # Point to the line
        pos_before = ln.position()
        self.assertFalse(ln.touch_front())
        pos_after = ln.position()
        self.assertEqual(pos_before, pos_after)
        ln.forward(10)
        pos_before = ln.position()
        self.assertEqual(round(ln.last_distance(), 7),
                         10-(pt.pensize()/2)-ln._safety_radius)
        self.assertTrue(ln.touch_front())
        pos_after = ln.position()
        self.assertEqual(pos_before, pos_after)

    def test_touch_back(self):
        pt = Turtle()
        # Draw a line to bump into
        pt.penup()
        pt.goto(-10, 10)
        pt.pendown()
        pt.pen_set_solid()
        pt.forward(20)
        pt.pen_unset_solid()
        ln = Turtle()        
        ln.left(90) # Point to the line
        # Trivial test when out in the open
        pos_before = ln.position()
        head_before = ln.heading()
        self.assertFalse(ln.touch_back()) # Trivial
        pos_after = ln.position()
        head_after = ln.heading()
        self.assertEqual(pos_before, pos_after)
        self.assertEqual(head_before, head_after)
        # Move as close to the wall as we are allowed
        ln.forward(10)
        self.assertEqual(round(ln.last_distance(), 7),
                         10-(pt.pensize()/2)-ln._safety_radius)
        ln.left(180) # Turn the turtle's back to the wall
        pos_before = ln.position()
        head_before = ln.heading()
        self.assertTrue(ln.touch_back())
        pos_after = ln.position()
        head_after = ln.heading()
        self.assertEqual(pos_before, pos_after)
        self.assertEqual(head_before, head_after)
        # Move a step away from the wall
        ln.forward(1)
        pos_before = ln.position()
        head_before = ln.heading()
        self.assertTrue(ln.touch_back())
        pos_after = ln.position()
        head_after = ln.heading()
        self.assertEqual(pos_before, pos_after)
        self.assertEqual(head_before, head_after)
        # Move stick length away from  the wall
        ln.forward(ln._stick_length-1)
        self.assertFalse(ln.touch_back())
        # and back a bit
        ln.forward(-0.01)
        self.assertTrue(ln.touch_back())
        
    def test_touch_right(self):
        pt = Turtle()
        # Draw a line to bump into
        pt.penup()
        pt.goto(-10, 10)
        pt.pendown()
        pt.pen_set_solid()
        pt.forward(20)
        pt.pen_unset_solid()
        ln = Turtle()        
        ln.left(90) # Point to the line
        # Trivial test when out in the open
        pos_before = ln.position()
        head_before = ln.heading()
        self.assertFalse(ln.touch_back()) # Trivial
        pos_after = ln.position()
        head_after = ln.heading()
        self.assertEqual(pos_before, pos_after)
        self.assertEqual(head_before, head_after)
        # Move as close to the wall as we are allowed
        ln.forward(10)
        self.assertEqual(round(ln.last_distance(), 7),
                         10-(pt.pensize()/2)-ln._safety_radius)
        ln.left(90) # Turn the turtle left (the wall on the right)
        pos_before = ln.position()
        head_before = ln.heading()
        self.assertTrue(ln.touch_right())
        pos_after = ln.position()
        head_after = ln.heading()
        self.assertEqual(pos_before, pos_after)
        self.assertEqual(head_before, head_after)
        # Move a step away from the wall
        ln.left(90)
        ln.forward(1)
        ln.left(-90)
        pos_before = ln.position()
        head_before = ln.heading()
        self.assertTrue(ln.touch_right())
        pos_after = ln.position()
        head_after = ln.heading()
        self.assertEqual(pos_before, pos_after)
        self.assertEqual(head_before, head_after)
        # Move stick length away from  the wall
        ln.left(90)
        ln.forward(ln._stick_length-1)
        ln.left(-90)
        self.assertFalse(ln.touch_right())
        # and back a bit
        ln.left(90)
        ln.forward(-0.01)
        ln.left(-90)
        self.assertTrue(ln.touch_right())
        
    def test_touch_left(self):
        pt = Turtle()
        # Draw a line to bump into
        pt.penup()
        pt.goto(-10, 10)
        pt.pendown()
        pt.pen_set_solid()
        pt.forward(20)
        pt.pen_unset_solid()
        ln = Turtle()        
        ln.left(90) # Point to the line
        # Trivial test when out in the open
        pos_before = ln.position()
        head_before = ln.heading()
        self.assertFalse(ln.touch_back()) # Trivial
        pos_after = ln.position()
        head_after = ln.heading()
        self.assertEqual(pos_before, pos_after)
        self.assertEqual(head_before, head_after)
        # Move as close to the wall as we are allowed
        ln.forward(10)
        self.assertEqual(round(ln.last_distance(), 7),
                         10-(pt.pensize()/2)-ln._safety_radius)
        ln.left(-90) # Turn the turtle right (the wall on the left)
        pos_before = ln.position()
        head_before = ln.heading()
        self.assertTrue(ln.touch_left())
        pos_after = ln.position()
        head_after = ln.heading()
        self.assertEqual(pos_before, pos_after)
        self.assertEqual(head_before, head_after)
        # Move a step away from the wall
        ln.left(-90)
        ln.forward(1)
        ln.left(90)
        pos_before = ln.position()
        head_before = ln.heading()
        self.assertTrue(ln.touch_left())
        pos_after = ln.position()
        head_after = ln.heading()
        self.assertEqual(pos_before, pos_after)
        self.assertEqual(head_before, head_after)
        # Move stick length away from  the wall
        ln.left(-90)
        ln.forward(ln._stick_length-1)
        ln.left(90)
        self.assertFalse(ln.touch_left())
        # and back a bit
        ln.left(-90)
        ln.forward(-0.01)
        ln.left(90)
        self.assertTrue(ln.touch_left())

    def test_touch_sequence(self):
        # Apparent special case when stepping alongside a line. Test
        # for touch is fuzzy due to floating point operations.
        pt = Turtle()
        # Draw a line to bump into
        pt.penup()
        pt.goto(-10, 10)
        pt.pendown()
        pt.pen_set_solid()
        pt.forward(20)
        pt.pen_unset_solid()
        ln = Turtle()        
        ln.left(90) # Point to the line
        ln.forward(20) # Hit the line
        ln.left(90)
        self.assertTrue(ln.touch_right())
        self.assertFalse(ln.touch_front())
        # Step ahead
        ln.forward(3)
        self.assertTrue(ln.touch_right())
        self.assertFalse(ln.touch_front())
        # Step ahead
        ln.forward(3)
        self.assertTrue(ln.touch_right())
        self.assertFalse(ln.touch_front())
        
if __name__ == '__main__':
    unittest.main(verbosity=2)
