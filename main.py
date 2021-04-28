import sys
from direct.showbase.ShowBase import ShowBase
from game.editor import TextNodeEditor


class Base(ShowBase):
    def __init__(self):
        ShowBase.__init__(self)
        self.win.set_clear_color((0.1,0.1,0.1,1))
        self.accept('control-q', sys.exit)
        self.text = TextNodeEditor()

if __name__ == "__main__":
    base = Base()
    base.run()
