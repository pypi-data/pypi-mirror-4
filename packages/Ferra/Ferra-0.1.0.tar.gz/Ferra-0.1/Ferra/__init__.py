#TODO: fix clear_color_buffer
import pyglet
from pyglet import media
from pyglet import image
from .errors import *
from . import sprite
from . import resource
from . import gl
from pyglet.window import key
from pyglet.window import mouse
__all__ = ["Window",
            "sprite",
            "resource",
            "KeyHandler",
            "schedule",
            "schedule_interval",
            "Batch",
            "run",
            "gl",
            ]
class Window(pyglet.window.Window):
    """ This updated Window class' clear method allows you to specify your own color e.g:
        #[OMMITTED: Creation of window]
        window.clear(1, 1, 1, 1) # white
        window.clear(1, 0, 1, 0) # pink
        window.clear() # for default black color
        you can use others.
    """
    def clear(self, *args):
        super(Window, self).clear()
        if args:
            try:
                pyglet.gl.glClearColor(*args)
            except:
                raise ClearException("Invalid color: %s" % args)
class KeyHandler(pyglet.window.key.KeyStateHandler):
    """ Simple key handler with the use:
        class MyKeyHandler(Ferra.KeyHandler):
            pass
        keys = MyKeyHandler()
        if keys[Ferra.keys.LEFT]:
            ......
    """
    pass
            
####class Image(image.ImageData): # Error: Please Don't UNCOMMENT!
####    """ loads an image and gets it ready for displaying """
####    def __init__(self, filename, flip_x=False, flip_y=False, rotate=0):
####        self.__image = image.load(filename, flip_x=flip_x, flip_y=flip_y, rotate=rotate)
####    def blit(self, pos):
####        self.__image.blit(pos)
####def clear_color_buffer(): # value unknown please do not UNCOMMENT! if you know what to do please send an email to Victor8334@ovi.com
####    """ clears the color buffer """
####    pyglet.gl.glClear(GL_COLOR_CLEAR_VALUE)
def schedule(func):
    """ clall func every frame """
    return pyglet.clock.schedule(func)
def schedule_interval(func, interval):
    """ call func at interval frames """
    return pyglet.clock.schedule_interval(func, interval)
def Batch(*args, **kwargs):
    """ return pyglet.graphics.Batch(*args, **kwargs) """
    return pyglet.graphics.Batch(*args, **kwargs)
def run():
    pyglet.app.run()
