from .text import TextFileSelectionNode
from .highlight import Highlight
from .repl import Repl


NUMBERS = '0123456789'
SYMBOLS = ' `~!@#$%^&*()_+|-=\\[];,./{}:"<>?'+"'"
LETTERS = 'ABCDEFGHIJKLMNOPQRSTUVWXYZ'
LETTERS = LETTERS + LETTERS.lower()
LEGAL_CHARACTERS = LETTERS + NUMBERS + SYMBOLS

def split(l, n): return l[:n], l[n:]
def clamp(n, low, high): return max(low, min(n, high))


class TextEditorNode(TextFileSelectionNode):
    def __init__(self, name, filename=None, **options):
        TextFileSelectionNode.__init__(self, name, filename, **options)
        # Only works with monospaces fonts at this time.
        self.font = loader.load_font("fifteen.ttf")
        self.set_font(self.font)
        self.rect_w = self.calc_width(" ")
        self.rect_h = self.get_line_height()
        self.tab_size = 4

        self.highlight = Highlight()
        self.repl = Repl()
        self.setup_input()

        self.cursor_card = None
        self.paste_buffer = []

        self.history = []
        self.history_index = 0

        if filename:
            self.load_file(filename)

        self.add_history() # Make initial state a snapshot.

    def add_history(self):
        self.history.insert(0, ((self.x, self.y), self.lines[:]))
        self.history = self.history[self.history_index:]
        self.history_index = 0

    def undo_redo(self, direction=1):
        self.history_index += direction
        self.history_index = clamp(
            self.history_index, 0, len(self.history)-1
        )
        history = self.history[self.history_index]
        self.x, self.y = history[0]
        self.lines = history[1][:]
        self.refresh()

    def copy(self):
        self.paste_buffer = self.selection_buffer[:]

    def cut(self):
        self.copy()
        self.remove_range()
        self.add_history()
        self.refresh()

    def paste(self):
        if len(self.paste_buffer) <= 0:
            return
        if len(self.selection_buffer) > 0:
            self.remove_range()

        a, b = split(self.line, self.x)

        to_paste = self.paste_buffer[:]
        self.lines[self.y] = a + to_paste[-1]
        for l, line in enumerate(to_paste[1:-1]):
            self.lines.insert(self.y+1, line)
        self.y += l+1
        self.lines[self.y] += b
        self.move_char(-1)
        self.add_history()
        self.refresh()

    def draw_cursor(self):
        new_card = self.draw_rect([self.x+self.line_number_width, self.y-self.line_offset, 0.0001, 0])
        if self.cursor_card:
            new_card.replace_node(self.cursor_card)
        self.cursor_card = new_card

    def move_char(self, amount, refresh=True):
        self.x += amount
        if self.x < 0:
            self.move_line(-1)
            self.x = self.line_length
        elif self.x > self.line_length:
            self.move_line(1)
            self.x = 0
        if refresh:
            self.refresh()

    def move_word(self, amount, refresh=True):
        try:
            check = " " if self.line[self.x] == " " else LETTERS
            self.move_char(amount, refresh=False)
            while True:
                if self.line[self.x] in check:
                    self.move_char(amount, refresh=False)
                else:
                    break
        except IndexError:
            self.move_char(amount, refresh=False)
        if refresh:
            self.refresh()

    def move_line(self, amount, refresh=True):
        self.y += amount
        self.y = clamp(self.y, 0, len(self.lines)-1)
        if self.x > self.line_length:
            self.x = self.line_length
        if refresh:
            self.refresh()

    def scroll(self, amount):
        for i in range(self.max_rows-1):
            self.move_line(amount, refresh=False)
        self.refresh()

    def scroll_max(self, line=True, end=True):
        if line:
            self.x = self.line_length if end else 0
        else:
            self.y = len(self.lines) if end else 0
        self.refresh()

    def remove(self, backwards=True, refresh=True):
        if len(self.selection_buffer) > 0:
            self.remove_range()
            self.add_history()
            self.refresh()
            return

        if not backwards:
            self.move_char(1)
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
        if refresh:
            self.add_history()
            self.refresh()

    def add(self, keyname):
        if keyname in LEGAL_CHARACTERS:
            a,b = split(self.line, self.x)
            self.lines[self.y] = a+keyname+b
            self.x += 1
            self.add_history()
            self.refresh()

    def enter(self):
        string_a, string_b = split(self.line, self.x)
        self.lines.pop(self.y)
        lines_a, lines_b = split(self.lines, self.y)
        self.lines = lines_a + [string_a] + [string_b] + lines_b
        self.x = 0
        self.y += 1
        self.add_history()
        self.refresh()
        self.run()

    def tab(self, backwards=False):
        if backwards:
            # HACK: selecting is on when holding shift
            # so let's force it off for shift-tab untill another key pops up
            self.selecting = False
            if self.line[:self.tab_size] == '    ':
                self.lines[self.y] = self.line[self.tab_size:]
                self.x -= self.tab_size
                self.add_history()
                self.refresh()
        else:
            for i in range(self.tab_size):
                self.add(" ")

    # Input
    def key(self, key, func, extra_args=[]):
        self.accept(key, func, extraArgs=extra_args)
        self.accept('shift-'+key, func, extraArgs=extra_args)
        self.accept(key+'-repeat', func, extraArgs=extra_args)
        self.accept('shift-'+key+'-repeat', func, extraArgs=extra_args)

    def setup_input(self):
        base.buttonThrowers[0].node().setKeystrokeEvent('keystroke')
        self.key('keystroke', self.add)
        self.key('enter', self.enter)
        self.key('shift-enter', self.run)

        self.key('arrow_left', self.move_char, [-1])
        self.key('arrow_right', self.move_char, [1])
        self.key('arrow_up', self.move_line, [-1])
        self.key('arrow_down', self.move_line, [1])
        self.key("control-arrow_left", self.move_word, [-1])
        self.key("control-arrow_right", self.move_word, [1])

        self.key('tab', self.tab)
        self.key('shift-tab', self.tab, extra_args=[True])
        self.key('control-tab', self.hide)

        self.key('backspace', self.remove)
        self.key('delete', self.remove, extra_args=[False])

        self.key('end', self.scroll_max, extra_args=[True, True])
        self.key('home', self.scroll_max, extra_args=[True, False])
        self.key('control-end', self.scroll_max, extra_args=[False, True])
        self.key('control-home', self.scroll_max, extra_args=[False, False])
        self.key('page_down', self.scroll, extra_args=[1])
        self.key('page_up', self.scroll, extra_args=[-1])

        self.key('control-n', self.new_file)
        self.key('control-s', self.save_file)
        self.key('control-o', self.load_file)

        self.key('control-c', self.copy)
        self.key('control-x', self.cut)
        self.key('control-v', self.paste)

        self.key('control-z', self.undo_redo, extra_args=[1])
        self.key('control-y', self.undo_redo, extra_args=[-1])

    def refresh(self):
        if self.selecting:
            self.select_range()
        else:
            self.clear_rects()
            self.selection_buffer = []
        self.draw_cursor()
        self.write_out()
        self.text = self.highlight.highlight(self.text)

    def run(self):
        self.repl.repl(self.lines)
