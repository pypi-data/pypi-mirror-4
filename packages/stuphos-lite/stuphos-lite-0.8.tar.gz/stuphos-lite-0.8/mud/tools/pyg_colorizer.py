# Stuph Color Code formatter.
 #-
 # Copyright (c) 2013 Clint Banis (hereby known as "The Author")
 # All rights reserved.
 #
 # Redistribution and use in source and binary forms, with or without
 # modification, are permitted provided that the following conditions
 # are met:
 # 1. Redistributions of source code must retain the above copyright
 #    notice, this list of conditions and the following disclaimer.
 # 2. Redistributions in binary form must reproduce the above copyright
 #    notice, this list of conditions and the following disclaimer in the
 #    documentation and/or other materials provided with the distribution.
 # 3. All advertising materials mentioning features or use of this software
 #    must display the following acknowledgement:
 #        This product includes software developed by The Author, Clint Banis.
 # 4. The name of The Author may not be used to endorse or promote products
 #    derived from this software without specific prior written permission.
 #
 # THIS SOFTWARE IS PROVIDED BY THE AUTHOR AND CONTRIBUTORS
 # ``AS IS'' AND ANY EXPRESS OR IMPLIED WARRANTIES, INCLUDING, BUT NOT LIMITED
 # TO, THE IMPLIED WARRANTIES OF MERCHANTABILITY AND FITNESS FOR A PARTICULAR
 # PURPOSE ARE DISCLAIMED.  IN NO EVENT SHALL THE AUTHOR OR CONTRIBUTORS
 # BE LIABLE FOR ANY DIRECT, INDIRECT, INCIDENTAL, SPECIAL, EXEMPLARY, OR
 # CONSEQUENTIAL DAMAGES (INCLUDING, BUT NOT LIMITED TO, PROCUREMENT OF
 # SUBSTITUTE GOODS OR SERVICES; LOSS OF USE, DATA, OR PROFITS; OR BUSINESS
 # INTERRUPTION) HOWEVER CAUSED AND ON ANY THEORY OF LIABILITY, WHETHER IN
 # CONTRACT, STRICT LIABILITY, OR TORT (INCLUDING NEGLIGENCE OR OTHERWISE)
 # ARISING IN ANY WAY OUT OF THE USE OF THIS SOFTWARE, EVEN IF ADVISED OF THE
 # POSSIBILITY OF SUCH DAMAGE.
 #
from pygments.formatter import Formatter

class StuphColorFormatter(Formatter):
    def __init__(self, **options):
        Formatter.__init__(self, **options)

        # create a dict of (start, end) tuples that wrap the
        # value of a token so that we can use it in the format
        # method later
        self.styles = {}

        # we iterate over the `_styles` attribute of a style item
        # that contains the parsed style values.
        for token, style in self.style:
            start = end = ''
            # a style item is a tuple in the following form:
            # colors are readily specified in hex: 'RRGGBB'
            color = style['color']
            if color:
                if style['bold']:
                    color = self.getColorCodeFromHex(color)
                else:
                    color = self.getColorCodeFromHex(color, bold = True)

                # italic, underline, bgcolor, border

                start += '&%s' % color
                end = '&N' + end

            self.styles[token] = (start, end)

    def getColorCodeFromHex(self, hex, bold = False):
        c = COLOR_CODES.get(hex, 'N')
        if bold:
            c = c.upper()

        return c

    def format(self, tokensource, outfile):
        # lastval is a string we use for caching
        # because it's possible that an lexer yields a number
        # of consecutive tokens with the same token type.
        # to minimize the size of the generated html markup we
        # try to join the values of same-type tokens here
        lastval = ''
        lasttype = None

        # wrap the whole output with <pre>
        # outfile.write('<pre>')

        for ttype, value in tokensource:
            # if the token type doesn't exist in the stylemap
            # we try it with the parent of the token type
            # eg: parent of Token.Literal.String.Double is
            # Token.Literal.String
            while ttype not in self.styles:
                ttype = ttype.parent
            if ttype == lasttype:
                # the current token type is the same of the last
                # iteration. cache it
                lastval += value
            else:
                # not the same token as last iteration, but we
                # have some data in the buffer. wrap it with the
                # defined style and write it to the output file
                if lastval:
                    stylebegin, styleend = self.styles[lasttype]
                    outfile.write(stylebegin + lastval + styleend)
                # set lastval/lasttype to current values
                lastval = value
                lasttype = ttype

        # if something is left in the buffer, write it to the
        # output file, then close the opened <pre> tag
        if lastval:
            stylebegin, styleend = self.styles[lasttype]
            outfile.write(stylebegin + lastval + styleend)
        # outfile.write('</pre>\n')

##    COLORS = ['B00040', '880000', 'FF0000', 'BB6622', '800080', '408080', '00A000',
##              '19177C', 'A0A000', 'A00000', 'BA2121', '0000FF', '0040D0', 'BC7A00',
##              '666666', '000080', 'D2413A', 'AA22FF', '7D9029', 'bbbbbb', 'BB6688',
##              '999999', '808080', '008000']

COLORS = {'B00040': 'red',
          '880000': 'red',
          'FF0000': 'red',
          'BB6622': 'red',
          '800080': 'purple',
          '408080': 'cyan',
          '00A000': 'green',
          '19177C': 'blue',
          'A0A000': 'yellow',
          'A00000': 'red',
          'BA2121': 'red',
          '0000FF': 'blue',
          '0040D0': 'blue',
          'BC7A00': 'yellow',
          '666666': 'grey',
          '000080': 'blue',
          'D2413A': 'red',
          'AA22FF': 'purple',
          '7D9029': 'green',
          'bbbbbb': 'grey',
          'BB6688': 'pink',
          '999999': 'grey',
          '808080': 'grey',
          '008000': 'green'}

COLOR_MAP = dict(red = 'r', purple = 'm', cyan = 'c',
                 green = 'g', blue = 'b', yellow = 'y',
                 grey = 'w', pink = 'm')

COLOR_CODES = dict((n, COLOR_MAP[v]) for (n, v) in COLORS.iteritems())

from pygments import highlight
from pygments.lexers import get_lexer_by_name

python = get_lexer_by_name('python')

def stuphColorFormat(code):
    return highlight(code, python, StuphColorFormatter())

##    def getFileName():
##        if __file__.endswith('.pyc'):
##            return __file__[:-1]
##
##        return __file__
##
##    def thisCode():
##        return stuphFormat('''
##        # Stuph Color Code formatter.
##        from pygments.formatter import Formatter
##
##        class StuphColorFormatter(Formatter):
##
##            def __init__(self, **options):
##                Formatter.__init__(self, **options)
##
##                # create a dict of (start, end) tuples that wrap the
##                # value of a token so that we can use it in the format
##                # method later
##                self.styles = {}
##
##                # we iterate over the `_styles` attribute of a style item
##                # that contains the parsed style values.
##                for token, style in self.style:
##                    start = end = ''
##                    # a style item is a tuple in the following form:
##                    # colors are readily specified in hex: 'RRGGBB'
##                    color = style['color']
##        ''')
##
##    def colorTable():
##        def _():
##            yield '<table><tr>'
##            yield '<td>'
##            yield '<ul>'
##            for c in COLORS:
##                yield '<li style="background: #%s">&nbsp;</li>' % c
##
##            yield '</ul>'
##            yield '</td>'
##
##            yield '<td>'
##            yield '<textarea>'
##            for c in COLORS:
##                yield "'%s': ''," % c
##
##            yield '</textarea>'
##            yield '</td></tr></table>'
##
##        return '\n'.join(_())

# print thisCode()

##    class WizControl:
##        def view_code(self, peer, moduleName):
##            try: x
##            else:
##                if x:
##                    code = open(f).read()
##
##                    try: from pyg_colorizer import stuphFormat
##                    except ImportError: pass
##                    else: code = stuphFormat(code)
##
##                    peer.page_string(code)
