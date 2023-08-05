"""
Jocelyn - a shim to make Processing easier from jython.
"""

# Imports to do more importing
import os
import sys
import fnmatch
from java.net import URL, URLClassLoader
from java.lang import ClassLoader
from java.io import File

# Add Java Libraries to classpath
try:
    import processing
except ImportError:
    # Import framework libs
    libsdir = os.path.abspath(os.path.join(os.path.dirname(__file__),
                                           'java_libs'))

    libs = [os.path.join(libsdir, lib) for lib in os.listdir(libsdir)]

    # Import user libraries
    for root, dirnames, filenames in os.walk('libraries'):
        for libfile in fnmatch.filter(filenames, '*.jar'):
            libs.append(os.path.join(root, libfile))

    for lib in libs:
        sys.path.append(lib)
        m = URLClassLoader.getDeclaredMethod("addURL", [URL])
        m.accessible = 1
        m.invoke(ClassLoader.getSystemClassLoader(), [File(lib).toURL()])

# Python imports
import __builtin__

# Java imports
from java.lang import Class
from java.lang.reflect import Modifier
from javax.swing import JFrame
from processing.core import PApplet


class Sketch(PApplet):
    """
    A subclass of processing's ``PApplet`` that provides convenience methods
    for running and displaying Applets.

    Keeps a reference to the currently running ``Sketch`` as a static member
    which is subsequently used by sketch delegate methods to avoid
    requiring an explicit self ( which makes it easier to translate
    Processing code )

    """
    instance = None

    def __init__(self):
        super(Sketch, self).__init__()


    def create_frame(self):
        """
        Returns a ``JFrame`` to which the applet will be added. Can be
        overridden by subclasses to provide something more suitable ( or
        nothing in the case of ``SketchedImage`` )

        """
        return JFrame(resizable=0,
                           defaultCloseOperation=JFrame.EXIT_ON_CLOSE)

    def run_sketch(self):
        """
        Initialises the underlying PApplet and creates a frame ( using ``create_frame`` if
        required ) to display it in.

        """
        Sketch.instance = self
        self.init()
        frame = self.create_frame()
        if frame:
            frame.add(self)
            frame.pack()
            frame.visible = 1


    @staticmethod
    def get_instance():
        """
        Returns an instance of the currently running sketch or throws a
        ``ValueError`` if none exists.

        """
        if Sketch.instance is None:
            raise ValueError("Sketch has not been started yet"
                             ", required for delgated methods to work!")
        else:
            return Sketch.instance


class SketchedImage(Sketch):
    """
    Convenience subclass of Sketch for creating static images.

    Expects subclasses to implement 'draw_image' method which is called
    once and the results saved to the file given inthe costructor.
    """
    def __init__(self, img_width, img_height, filename):
        super(SketchedImage, self).__init__()
        self.img_width = img_width
        self.img_height = img_height
        self.filename = filename

    def setup(self):
        size(self.img_width, self.img_height)
        smooth()

    def draw(self):
        self.draw_image()
        save(self.filename)
        self.exit()

    def draw_image(self):
        """
        Override this method to draw in PApplet, results will be saved
        to filename given in the constructor.

        """

        print "Override me to draw image."


class SketchDelegate(object):
    """
    Used to wrap methods exposed by the module to use the singleton
    ``Sketch`` as first argument.

    """
    def __init__(self, name):
        self.name = name

    def _get_named_sketch_attr(self):
        if(not hasattr(self, "attr")):
            self.attr = getattr(Sketch.get_instance(), self.name)
        return self.attr

    def __call__(self, *args, **kwargs):
        return apply(self._get_named_sketch_attr(), args, kwargs)


def Q(name):
    """Gets a variable from the current sketch. Processing has a number
    of methods and variables with the same name, 'mousePressed' for
    example. This allows us to disambiguate.

    Also casts numeric values as floats to make it easier to translate
    code from pde to python.

    """
    retval = PApplet.getDeclaredField(name).get(Sketch.get_instance())
    if isinstance(retval, (long, int)):
        return float(retval)
    else:
        return retval


def dimensions():
    """Convenience function to get both width and height, returned as a
    tuple.
    """
    return (Q('width'), Q('height'))


# Namespace munging
module = sys.modules[__name__]
papplet_class = Class.forName("processing.core.PApplet")
pconstants_class = Class.forName("processing.core.PConstants")
visible_members = set(dir(PApplet))
builtins = set(dir(__builtin__))

# Er...
members_to_expose = []

# Find PApplet methods and make them work as delegates.
declared_methods = set([m.name for m in
                        papplet_class.getDeclaredMethods()])

for m in (declared_methods & visible_members) - builtins:
    setattr(module, m, SketchDelegate(m))
    members_to_expose.append(m)

# Expose constants directly in the module
#
# These will be cached by the Python import mechanism but it doesn't
# matter - because they're constant.
def expose_constants(cls):
    fields = set([f.name for f in cls.getDeclaredFields() if
                  Modifier.isStatic(f.getModifiers())])

    for f in (fields & visible_members) - builtins:
        setattr(module, f, getattr(cls, f))
        members_to_expose.append(f)


expose_constants(papplet_class)
expose_constants(pconstants_class)

__all__ = members_to_expose + ["Sketch",
                               "SketchedImage",
                               "Q",
                               "dimensions"
                               ]
