from jocelyn import *

width = 400
height = 400

class Circles(Sketch):

    def setup(self):
        size(width, height)
        background(0)
        smooth()

    def mousePressed(self,e):
        circle_height = random(10,40)
        circle_width = random(10,40)
        ellipse(Q('mouseX'),Q('mouseY'),circle_height, circle_width)
        
    def draw(self):
        pass

if __name__ == '__main__':
    Circles().run_sketch()
