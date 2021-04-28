import sys
import builtins
from direct.showbase.ShowBase import ShowBase
from panda3d.core import NodePath
from game.text import TextNodeEditor


class Base(ShowBase):
    def __init__(self):
        ShowBase.__init__(self)
        self.base_tasks = []
        for task in base.task_mgr.getTasks():
            self.base_tasks.append(task)
        self.font = loader.load_font("fifteen.ttf")
        self.win.set_clear_color((0.1,0.1,0.1,1))
        self.text = TextNodeEditor()
        self.accept('control-q', sys.exit)

    def reset(self):
        self.render = NodePath("new render!")
        for task in base.task_mgr.getTasks():
            if not task in self.base_tasks:
                print(dir(task))
                task.remove()
        base.camera.reparent_to(self.render)
        builtins.render = self.render

if __name__ == "__main__":
    base = Base()
    base.run()
