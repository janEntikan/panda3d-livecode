import builtins
from panda3d.core import NodePath


class Repl():
    def __init__(self):
        self.base_tasks = []
        for task in base.task_mgr.getTasks():
            self.base_tasks.append(task)

    def reset_showbase(self):
        base.render = NodePath("new render!")
        for task in base.task_mgr.getTasks():
            if not task in self.base_tasks:
                task.remove()
        base.camera.reparent_to(base.render)
        builtins.render = base.render

    def repl(self, code):
        compiled = ""
        for l, line in enumerate(code):
            compiled += line + '\n'
        self.reset_showbase()
        try:
            exec(compiled)
        except:
            print("error")
