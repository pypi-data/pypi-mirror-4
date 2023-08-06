# Name:      physical_turtle/example_follow.py
# Purpose:   Reproduce all the lower level symbols for easy import
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
from physical_turtle import Turtle

def make_object(tk):
    """ Make a standard object to work around.

        For the purposes of this example, keep all angles to a right angle.

        :tk: turtle instance - used to draw the object.
    """
    tk.pendown()
    tk.pen_set_solid()
    tk.forward(100)
    tk.left(90)
    tk.forward(150)
    tk.right(90)
    tk.forward(100)
    tk.left(90)
    tk.forward(50)
    tk.left(90)
    tk.forward(300)
    tk.left(90)
    tk.forward(150)
    tk.left(90)
    tk.forward(100)
    tk.right(90)
    tk.forward(50)
    tk.left(90)
    tk.pen_unset_solid()

def walk_line_to_right(tk):
    """ Move along the line in steps and test the presence of the wall """
    while not tk.touch_right() and not tk.touch_front():
        # Find the line
        tk.forward(3)
    while tk.touch_right() and not tk.touch_front():
        # Move along the line
        tk.forward(3)

def turn_left_or_right(tk):
    """ Given a corner, decide which way to turn.

        Return the turn required in degrees to the right
    """
    if not tk.touch_right():
        turn = 90
    else:
        turn = -90
    return turn

def run_me():
    tk = Turtle()
    tk.penup()
    tk.goto(-50,100)
    make_object(tk)
    tk.penup()
    tk.goto(0,0)
    tk.left(90) # Pointing up at the object
    tk.pendown()
    tk.pencolor('blue')
    tk.forward(999) # Hit the box somewhere
    tk.left(90) # Prepare to circumnavigate

    # Loop for some arbitrary number of steps to ensure we get round
    # the object. This can be improved by using a turn invariant. See
    # Ableson and diSessa Turtle Geometry.
    for i in range(20):
        walk_line_to_right(tk)
        tk.right(turn_left_or_right(tk))
    

    # Wait for input so that the screen is left open and we can see
    # the results.
    raw_input()   

if __name__ == "__main__":
    run_me()

#-----------------------------------------------------------------------
