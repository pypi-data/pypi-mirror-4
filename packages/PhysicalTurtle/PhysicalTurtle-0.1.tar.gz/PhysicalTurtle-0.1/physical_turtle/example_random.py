# Name:      physical_turtle/example_random.py
# Purpose:   Demonstrate constraint by solid lines using random lines.
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

import random
from physical_turtle import Turtle
from physical_turtle.shapes import VerTex

#-----------------------------------------------------------------------

def poly2(tx, length, breadth, angle):
    """ Define a polygon with adjacent sides of unequal length. Used
        to draw rectangles.
    """
    rotation = 0
    while True:
        tx.forward(length)
        tx.right(angle)
        rotation += angle
        tx.forward(breadth)
        tx.right(angle)
        rotation += angle
        if rotation%360 == 0:
            break

#-----------------------------------------------------------------------
# Set up some driving parameters

# Define two boxes so that one fits inside the other. The two boxes
# are drawn solid and the space between the boxes is the test space.
INNER_BOX_SIZE = (200, 75)
OUTER_BOX_SIZE = (600, 350)

# This must be greater than possible travel in the test space so that all
# lines are clipped.
LARGE_NUMBER = 3000 

# Allow lines drawn in the test space to cycle through these colours,
# just for fun.
COLOR_SET = ['red', 'green', 'blue', 'yellow']

def draw_test_space(tx):
    """ Using the given tutle object, draw a test space """
    inner = VerTex(*INNER_BOX_SIZE)
    outer = VerTex(*OUTER_BOX_SIZE)
    tx.penup()
    tx.goto(-inner.x/2, inner.y/2)
    tx.pendown()
    tx.pen_set_solid()
    poly2(tx, inner.x, inner.y, 90)
    tx.penup()
    tx.pen_unset_solid()
    tx.goto(-outer.x/2, outer.y/2)
    tx.pendown()
    tx.pen_set_solid()
    poly2(tx, outer.x, outer.y, 90)
    tx.penup()
    tx.pen_unset_solid()
    
    tx.goto(0,0)

def escape_attempt(tx):
    """ Using the given turtle, attempt to escape from the test space """
    # Draw lines one after the other with a random heading.
    for i in range(1000):
        tx.pencolor(COLOR_SET[i/10%len(COLOR_SET)])
        tx.setheading(360*random.random())
        tx.forward(LARGE_NUMBER)
    
def run_me():
    # We will use this turtle to draw everything.
    tx = Turtle()

    # Grab sizes in a way that can be used more easily
    inner = VerTex(*INNER_BOX_SIZE)
    outer = VerTex(*OUTER_BOX_SIZE)
    
    # Start with the test space
    draw_test_space(tx)

    # Choose a random starting point
    while True:
        # random point inside the outer box
        u_x = random.random()
        x = -((outer.x/2)-1) + outer.x*u_x
        u_y = random.random()
        y = -((outer.y/2)-1) + outer.y*u_x
        # test and reject if inside the inner box
        if (-(inner.x/2+1) < x < inner.x/2+1 and
            -(inner.y/2+1) < y < inner.y/2+1):
            continue
        # This is inside the envelope
        break
    tx.goto(x, y)
    tx.pendown()

    # Now try to escape
    escape_attempt(tx)

    # Wait for input so that the screen is left open and we can see
    # the results.
    raw_input()
    
if __name__ == '__main__':
    run_me()

#-----------------------------------------------------------------------
