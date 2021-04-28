import sys
import builtins
from direct.showbase.ShowBase import ShowBase
from panda3d.core import NodePath
from game.text import TextNodeEditor


class Base(ShowBase):
    def __init__(self):
        ShowBase.__init__(self)
        self.font = loader.load_font("fifteen.ttf")
        self.win.set_clear_color((0.1,0.1,0.1,1))
        self.text = TextNodeEditor()
        base.accept('control-q', sys.exit)

    def reset(self):
        self.render = NodePath("new render!")
        base.camera.reparent_to(self.render)
        builtins.render = self.render


if __name__ == "__main__":
    base = Base()
    base.run()
