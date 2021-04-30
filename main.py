import sys
from direct.showbase.ShowBase import ShowBase
from livecode.editor import TextNodeEditor


class Base(ShowBase):
    def __init__(self):
        ShowBase.__init__(self)
        self.win.set_clear_color((0.1,0.1,0.1,1))
        self.accept('control-q', sys.exit)
        self.text = TextNodeEditor("Editor", "example/__init__.py")
        self.text_np= render2d.attach_new_node(self.text)
        self.text_np.set_scale(0.045)
        self.text_np.set_pos((-0.95,0,0.9))

if __name__ == "__main__":
    base = Base()
    base.run()
