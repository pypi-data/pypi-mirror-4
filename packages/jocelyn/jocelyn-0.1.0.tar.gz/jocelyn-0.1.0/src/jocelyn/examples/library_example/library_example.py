# Example using PeasyCam extension ( adapted from processing.py examples
# ( https://github.com/jdf/processing.py )
#
# To run:
#
# - Get peasycam from http://mrfeinberg.com/peasycam/
#
# - Create a folder called 'libraries'
#
# - Unzip peasycam into 'libraries' ( directory will be recursively
#   searched for jars and they will be added to the classpath.
#
# - Run the Sketch from the directory containing this file.

from jocelyn import *
from peasy import *

class LibrarySketch(Sketch):

    def setup(self):
        size(200,200,P3D)
        cam = PeasyCam(self, 100)
        cam.setMinimumDistance(50)
        cam.setMaximumDistance(500)

    def draw(self):
        rotateX(-.5)
        rotateY(-.5)
        background(0)
        fill(255,0,0)
        box(30)
        pushMatrix()
        translate(0,0,20)
        fill(0,0,255)
        box(5)
        popMatrix()

if __name__ == '__main__':
    LibrarySketch().run_sketch()
