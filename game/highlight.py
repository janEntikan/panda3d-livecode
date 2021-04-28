from pygments import highlight
from pygments.styles import STYLE_MAP
from pygments.formatter import Formatter
from pygments.lexers import PythonLexer
from panda3d.core import TextPropertiesManager, TextProperties


class TextNodeFormatter(Formatter):
    def __init__(self, **options):
        Formatter.__init__(self, **options)
        self.styles = {}
        manager = TextPropertiesManager.getGlobalPtr()
        n = 1/255
        for token, style in self.style:
            start = end = ''
            if style['color']:
                color = tuple(int(style['color'][i:i+2], 16) for i in (0, 2, 4))
                color = (n*color[0],n*color[1],n*color[2],1)
                start += '\1%s\1' % str(color)
                end = str('\2' + end)
                tp = TextProperties()
                tp.setTextColor(color)
                manager.setProperties(str(color), tp)
            self.styles[token] = (start, end)

    def format(self, tokensource, outfile):
        lastval = ''
        lasttype = None
        for ttype, value in tokensource:
            while ttype not in self.styles:
                ttype = ttype.parent
            if ttype == lasttype:
                lastval += value
            else:
                if lastval:
                    stylebegin, styleend = self.styles[lasttype]
                    outfile.write(stylebegin + lastval + styleend)
                lastval = value
                lasttype = ttype
        if lastval:
            stylebegin, styleend = self.styles[lasttype]
            outfile.write(stylebegin + lastval + styleend)

class Highlight():
    def __init__(self):
        self.styles = STYLE_MAP.keys()
        self.formatter = TextNodeFormatter(style="paraiso-dark")
        self.lexer = PythonLexer()

    def highlight(self, code):
        return highlight(code, self.lexer, self.formatter)
