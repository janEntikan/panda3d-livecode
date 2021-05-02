from panda3d.core import NodePath
from panda3d.core import TextNode
from panda3d.core import TextAssembler
from panda3d.core import TextPropertiesManager
from panda3d.core import CardMaker
from direct.showbase.DirectObject import DirectObject


def fill(string, n): return "{:<{}}".format(string, n)[:n]


class TextFileNode(TextNode):
    def __init__(self, name, filename=None, **options):
        TextNode.__init__(self, name, **options)
        self.set_shadow(0.08)
        self.set_shadow_color((0,0,0,1))
        self.x = self.y = 0
        self.lines = ['']
        self.show_line_number = True
        self.line_number_width = 4
        self.max_rows = 30
        self.hidden = False
        if filename:
            self.load_file(filename)

    @property
    def line(self):
        return self.lines[self.y]

    @property
    def line_length(self):
        return len(self.line)

    @property
    def line_offset(self):
        return max(0,self.y - self.max_rows//2)

    def new_file(self):
        self.x = self.y = 0
        self.lines = ['']
        self.refresh()

    def load_file(self, filename=None):
        if filename:
            self.filename = filename
        else:
            filename = self.filename
             # TODO: Ask filename
        print('loading file {}!'.format(filename))
        self.lines = []
        self.text = ''
        with open(filename) as f:
            content = f.readlines()
        for line in content:
            line = line.strip('\n')
            self.lines.append(line)
        self.refresh()
        self.run()

    def save_file(self, filename=None):
        if filename:
            self.filename = filename
        else:
            filename = self.filename
            # TODO: Ask filename
        print('saving as {}!'.format(filename))
        self.filename = filename
        file = open(filename, 'w')
        for line in self.lines:
            file.write(line+'\n')
        file.close()

    def hide(self):
        self.hidden = not self.hidden
        self.refresh()

    def write_out(self):
        self.text = ''
        if self.hidden:
            return
        for l, line in enumerate(self.lines):
            if l >= self.line_offset:
                if self.show_line_number:
                    self.text += fill(str(l),3)+' '
                self.text += line + "\n"
            if l > self.line_offset+self.max_rows-1:
                return

    def refresh(self):
        self.write_out()


class TextFileSelectionNode(DirectObject, TextFileNode):
    def __init__(self, name, filename=None, **options):
        DirectObject.__init__(self)
        TextFileNode.__init__(self, name, None, **options)

        self.cardmaker = CardMaker('selection cards')
        self.selection_cards = []
        self.selecting = False
        self.rect_w, self.rect_h = 1, 1

        self.accept('shift', self.toggle_select, extraArgs=[True])
        self.accept('shift-up', self.toggle_select, extraArgs=[False])

    # Selection editing
    def clear_rects(self):
        for card in self.selection_cards:
            if card in list(self.children):
                self.remove_child(card)
        self.selection_cards = []

    def draw_rect(self, rect, color=(1,1,1,1)):
        rx, ry, rw, rh = rect
        l = ((rx)*self.rect_w)
        r = ((rx+rw+1)*self.rect_w)-0.2
        u = ((ry-1)*self.rect_h)+0.5
        d = ((ry+rh)*self.rect_h)+0.3
        self.cardmaker.set_frame(l,r,-u,-d)
        self.cardmaker.set_color(color)
        card = self.cardmaker.generate()
        self.add_child(card)
        return card

    def draw_line_rect(self, line_number, start, end=0):
        x = self.line_number_width+start
        y = line_number-self.line_offset
        w = len(self.lines[line_number])-start
        if end:
            w = min(w,end)
        self.selection_cards.append(self.draw_rect([x,y,w,0]))

    def remove_range(self):
        end, start = self.selection_direction()
        if start[1] == end[1]:
            a = self.lines[start[1]][:end[0]]
            b = self.lines[start[1]][start[0]:]
            self.lines[start[1]] = a + b
            self.x, self.y = end
        else:
            a = self.lines[start[1]][:start[0]]
            b = self.lines[end[1]][end[0]:]
            self.lines[start[1]] = a + b
            for i in range(1, (end[1]-start[1])+2):
                self.lines.pop(start[1]+1)
            self.x, self.y = start

    def select_range(self):
        self.clear_rects()
        self.selection_buffer = []
        start, end = self.selection_direction()
        if start[1] == end[1]:
            self.draw_line_rect(start[1], end[0], start[0]-end[0])
            self.selection_buffer.append(self.lines[start[1]][start[0]:end[0]])
        else:
            if start[0] > 0:
                self.draw_line_rect(start[1], 0, start[0])
            self.selection_buffer.append(self.lines[start[1]][:start[0]])
            for i in range(1, start[1]-end[1]):
                i = start[1] - i
                self.draw_line_rect(i,0)
                self.selection_buffer.append(self.lines[i])
            self.draw_line_rect(end[1], end[0])
            self.selection_buffer.append(self.lines[end[1]][start[0]:])

    def selection_direction(self):
        if self.y > self.selection_start[1]:
            return (self.x, self.y), self.selection_start
        else:
            return self.selection_start, (self.x, self.y)

    def toggle_select(self, on=True):
        if len(self.selection_buffer) > 0:
            already_selecting = True
        else:
            already_selecting = False
        self.selecting = on
        if self.selecting and not already_selecting:
            self.selection_start = [self.x, self.y]


