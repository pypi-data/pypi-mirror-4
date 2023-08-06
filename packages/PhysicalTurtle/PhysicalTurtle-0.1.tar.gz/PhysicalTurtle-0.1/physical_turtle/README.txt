Physical Turtle
===============

This is an extension for the Python turtle module that provides a
physical space for a turtle to inhabit. The initial aim is to provide
areas of solid space that the turtle cannot move into.

The Turtle class is extended with the following methods and
attributes.  This list may change as the first version of this package
is developed.

Attributes:

* `touch_left`, `touch_right`, `touch_front`, `touch_back`

  Each one returns True if the Turtle would not be able to move in
  that direction.

* `last_distance`

  The distance travelled in the preceding forward or backward
  movement. Since the turtle is not able to move through a solid area
  this distance may be less than the distance originally called for.

Methods:

* `pen_set_solid()`

  Set a pen property so that any movement of the turtle with the pen
  down creates a solid area. The pen colour is not affected, so that
  the lines shown on the screen correspond to lines of solidity in
  the physical space.

  The solid area created by the turtle move is a rectangle
  corresponding to the length of the move and the width of the pen.

  No solid area is drawn in the pen is up.

  The action of filling a polygon with a colour does not create solid
  space.

* `pen_unset_solid()`

  Reverses the action of pen_set_solid so that turtle movement does
  not create solid areas.

The extension provides a new rule that says a turtle cannot cross a
line that has been drawn with `pen_set_solid`. The turtle is allowed
to move up to the soild line and the attribute `last_distance`
gives the distance actually moved.

There are two exceptions to this rule:

- A turtle with pen `up` is allowed to move anywhere. This is allows
  the turtle to move to any place on the screen and is required for
  placing the turtle into an enclosed space.

- A turtle with pen `solid` is allowed to move anywhere. This is
  specifically designed to allow drawing a solid shape where one edge
  must be drawn contiguously with another. (If this was not allowed,
  the second line would not be drawn because it would be trapped by at
  the end of the first line.)

Installation
============

Get the version straight from the Python Package Index::

  pip install physical_turtle

Or Get the latest version from Bit Bucket::

    https://bitbucket.org/mikedeplume/physical-turtle

If you do download the repository, don't forget to put the
physical_turtle package on your PYTHON_PATH. The easiest way to do
this is to go into the directory and type::

    python setup.py install


License
=======

The package uses the MIT license:


    Permission is hereby granted, free of charge, to any person
    obtaining a copy of this software and associated documentation
    files (the "Software"), to deal in the Software without
    restriction, including without limitation the rights to use, copy,
    modify, merge, publish, distribute, sublicense, and/or sell copies
    of the Software, and to permit persons to whom the Software is
    furnished to do so, subject to the following conditions:

    The above copyright notice and this permission notice shall be
    included in all copies or substantial portions of the Software.

    THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND,
    EXPRESS OR IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF
    MERCHANTABILITY, FITNESS FOR A PARTICULAR PURPOSE AND
    NONINFRINGEMENT. IN NO EVENT SHALL THE AUTHORS OR COPYRIGHT
    HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER LIABILITY,
    WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING FROM,
    OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER
    DEALINGS IN THE SOFTWARE.

Use
===

The package is intended as a one for one replacement for the builtin
turtle module. Any existing turtle software that you have should work
just as before if you replace::

    from trurtle import ...

with::

    from physical_turtle import ...

From that perspective, there is nothing much new to learn.

Example
=======

At the Python prompt:

   >>> from physical_turtle.example_random import run_me
   >>> run_me()

And watch the turtle bounce randomly around an enclosed space. 
