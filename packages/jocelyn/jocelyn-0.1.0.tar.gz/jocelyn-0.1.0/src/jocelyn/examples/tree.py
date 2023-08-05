# Recursive Tree
# by Daniel Shiffman.

# Adapted for jocelyn by Danny O'Connor

# Renders a simple tree-like structure via recursion.
# The branching angle is calculated as a function of
# the horizontal mouse location. Move the mouse left
# and right to change the angle.

from jocelyn import *

class mem:
    theta = None

class TreeSketch(Sketch):

    def setup(self):
        size(640, 360)

    def draw(self):
        background(0)
        frameRate(30)
        stroke(255)
        a = Q('mouseX') / Q('width') * 90
        mem.theta = float(radians(a))

        translate(Q('width')/2,Q('height'))
        line(0,0,0,-120)
        translate(0,-120)
        # Start the recursive branching!
        branch(120)

def branch(h):
    #Each branch will be 2/3rds the size of the previous one
    h = h *0.66

    # All recursive functions must have an exit condition!!!!
    # Here, ours is when the length of the branch is 2 pixels or less
    if (h > 2):
        pushMatrix() # Save the current state of transformation (i.e. where are we now)
        rotate(mem.theta) # Rotate by theta
        line(0, 0, 0, -h) # Draw the branch
        translate(0, -h) # Move to the end of the branch
        branch(h) # Ok, now call myself to draw two new branches!!
        popMatrix() # Whenever we get back here, we "pop" in order to restore the previous matrix state

        #Repeat the same thing, only branch off to the "left" this time!
        pushMatrix()
        rotate(-mem.theta)
        line(0, 0, 0, -h)
        translate(0, -h)
        branch(h)
        popMatrix()

if __name__ == '__main__':
    TreeSketch().run_sketch()
