from panda3d.core import TextNode, TextPropertiesManager
from panda3d.core import CardMaker
from direct.showbase.DirectObject import DirectObject

from .highlight import Highlight
from .repl import Repl


NUMBERS = '0123456789'
LETTERS = 'ABCDEFGHIJKLMNOPQRSTUVWXYZ'
SYMBOLS = ' `~!@#$%^&*()_+|-=\\[];,./{}:"<>?'+"'"
LEGAL_CHARACTERS = LETTERS + LETTERS.lower() + NUMBERS + SYMBOLS

def split(l, n): return l[:n], l[n:]
def fill(string, n): return "{:<{}}".format(string, n)[:n]


class TextNodeEditor(DirectObject, TextNode):
    def __init__(self, name, filename=None, **options):
        DirectObject.__init__(self)
        TextNode.__init__(self, name, **options)
        self.highlight = Highlight()
        self.repl = Repl()
        self.font = loader.load_font("fifteen.ttf")
        self.set_font(self.font)
        self.set_shadow(0.08)
        self.set_shadow_color((0,0,0,1))

        self.lines = ['']
        self.scroll_start = 15
        self.max_lines = 30
        self.x = self.y = 0

        self.cardmaker = CardMaker("select")
        self.select_start = [0,0]
        self.select_cards = []

        self.show_line_number = True
        self.hidden = False
        self.setup_input()
        self.load_file(filename)

    @property
    def line(self):
        return self.lines[self.y]

    @property
    def line_length(self):
        return len(self.line)

    def run(self):
        self.repl.repl(self.lines)

    def new_file(self):
        self.x = self.y = 0
        self.lines = ['']
        self.refresh()

    def load_file(self, filename=None):
        if filename:
            self.filename = filename
        else:
            pass # TODO: Ask filename
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

    def save_file(self, filename):
        if filename:
            self.filename = filename
        else:
            pass # TODO: Ask filename
        print('saving as {}!'.format(filename))
        self.filename = filename
        file = open(filename, 'w')
        for line in self.lines:
            file.write(line+'\n')
        file.close()

    def key(self, key, func, extra_args=[]):
        self.accept(key, func, extraArgs=extra_args)
        self.accept(key+'-repeat', func, extraArgs=extra_args)

    def setup_input(self):
        base.buttonThrowers[0].node().setKeystrokeEvent('keystroke')
        self.key('keystroke', self.add)
        self.key('enter', self.enter)
        self.key('shift-enter', self.run)

        self.key('arrow_left', self.move_char, [-1])
        self.key('arrow_right', self.move_char, [1])
        self.key('arrow_up', self.move_line, [-1])
        self.key('arrow_down', self.move_line, [1])

        self.key('tab', self.tab)
        self.key('shift-tab', self.tab, extra_args=[True])
        self.key('control-tab', self.hide)

        self.key('backspace', self.remove)
        self.key('delete', self.remove, extra_args=[False])

        self.key('end', self.scroll_max, extra_args=[True, True])
        self.key('home', self.scroll_max, extra_args=[True, False])
        self.key('control-end', self.scroll_max, extra_args=[False, True])
        self.key('control-home', self.scroll_max, extra_args=[False, False])
        self.key('page_down', self.scroll, extra_args=[-1])
        self.key('page_up', self.scroll, extra_args=[1])

        self.key('control-n', self.new_file)
        self.key('control-s', self.save_file, extra_args=['example/__init__.py'])
        self.key('control-l', self.load_file)

    def hide(self):
        self.hidden = not self.hidden
        self.refresh()

    def refresh(self):
        self.text = ''
        if not self.hidden:
            for l, line in enumerate(self.lines):
                line_offset = max(0,self.y - self.scroll_start)
                if l >= line_offset:
                    if self.y == l:
                        a,b = split(line, self.x)
                        line = a+"|"+b
                    line = self.highlight.highlight(line)
                    if self.show_line_number:
                        self.text += fill(str(l),3)+' '
                    self.text += line
                if l > line_offset+self.max_lines-1:
                    return

    def move_char(self, amount, refresh=True):
        self.x += amount
        if self.x < 0:
            self.move_line(-1)
            self.x = self.line_length
        elif self.x > self.line_length:
            self.move_line(1)
            self.x = 0
        if refresh: self.refresh()

    def move_line(self, amount, refresh=True):
        self.y += amount
        if self.y >= len(self.lines)-1:
            self.y = len(self.lines)-1
        if self.y < 0:
            self.y = 0
        if self.x > self.line_length:
            self.x = self.line_length
        if refresh: self.refresh()

    def scroll(self, amount):
        for i in range(self.max_lines-1):
            self.move_line(amount, refresh=False)
        self.refresh()

    def scroll_max(self, line=True, end=True):
        if line:
            self.x = self.line_length if end else 0
        else:
            self.y = len(self.lines) if end else 0
        self.refresh()

    def tab(self, backwards=False):
        if backwards:
            if self.line[:4] == '    ':
                self.lines[self.y] = self.line[4:]
                self.x -= 4
                self.refresh()
        else:
            for i in range(4):
                self.add(" ")

    def remove(self, backwards=True):
        if not backwards: self.move_char(1)
        a, b = split(self.line, self.x)
        if len(a) == 0:
            if len(self.lines)-1 == 0:
                return
            self.lines.pop(self.y)
            self.y -= 1
            self.x = self.line_length
            self.lines[self.y] += b
        else:
            a = a[:-1]
            self.x -= 1
            self.lines[self.y] = a + b
        self.refresh()

    def add(self, keyname):
        if keyname in LEGAL_CHARACTERS:
            a,b = split(self.line, self.x)
            self.lines[self.y] = a+keyname+b
            self.x += 1
            self.refresh()

    def enter(self):
        string_a, string_b = split(self.line, self.x)
        self.lines.pop(self.y)
        lines_a, lines_b = split(self.lines, self.y)
        self.lines = lines_a + [string_a] + [string_b] + lines_b
        self.x = 0
        self.y += 1
        self.refresh()
        self.run()
