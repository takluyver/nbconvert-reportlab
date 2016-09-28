"""Markdown to reportlab conversion.
"""
from io import BytesIO
from reportlab.platypus import Paragraph, XPreformatted, Image
from reportlab.platypus.flowables import HRFlowable
from reportlab.lib.pygments2xpre import pygments2xpre
from html import escape
import mistune

from nbconvert.filters.markdown_mistune import MarkdownWithMath
from IPython.lib.latextools import latex_to_png
from matplotlib import mathtext

class InlineRenderer(mistune.Renderer):
    # autolink: rely on default implementation
        
    def inline_html(self, html):
        # RL throws an error on HTML that's not valid XML (e.g. <br>), so for
        # now, skip this.
        return ''
        
    def footnote_ref(self, key, footnote_idx):
        return ''  # TODO
    
    def image(self, link, title, text):
        src = mistune.escape_link(src, quote=True)
        return '<img src="%s" />' % src

    def link(self, link, title, text):
        # The HTML works, but there's no title attribute
        return super().link(link, '', text)
    
    def double_emphasis(self, text):  # bold
        return '<b>%s</b>' % text
    
    def emphasis(self, text):  # italic
        return '<i>%s</i>' % text
    
    def codespan(self, text):
        return text  # TODO
        
    def linebreak(self):
        return ''  # TODO
    
    def strikethrough(self, text):
        return '<strike>%s</strike>' % text
    
    def text(self, text):
        return escape(text)
    
    def inline_math(self, content):
        return '$%s$' % escape(content)  # TODO

    def block_math(self, content):
        return ''  # TODO


class BlockRenderer(mistune.Renderer):
    def get_style(self, name):
        return self.options['stylesheet'][name]

    def placeholder(self):
        return []
    
    def footnotes(self, body):
        return []  # TODO

    def newline(self):
        return []
    
    def hrule(self):
        return [HRFlowable()]
        
    def header(self, text, level, raw=None):
        style = self.get_style('Heading%d' % level)
        return [Paragraph(text, style=style)]
    
    def block_code(self, code, lang=None):
        if lang:
            code = pygments2xpre(code, language=lang)
        return [XPreformatted(code, style=self.get_style('Code'))]
        
    def table(self, header, body):
        return []  # TODO
        
    def table_row(self, content):
        return []  # TODO
    def table_cell(self, content, **flags):
        return []  # TODO
    
    def block_quote(self, content):
        return []  # TODO

    def list(self, content, ordered):
        return []  # TODO
        
    def list_item(self, body):
        return []  # TODO
        
    def block_html(self, html):
        return []  # TODO
        
    def paragraph(self, text):
        return [Paragraph(text, style=self.get_style('Normal'))]
    
    def latex_environment(name, text):
        return []  # TODO
    
    def block_math(name, text):
        # print(repr(text))
        text = '$%s$' % text.strip()
        mt = mathtext.MathTextParser('bitmap')
        f = BytesIO()
        mt.to_png(f, text, fontsize=16, dpi=120)
        return [Image(f, width=50, height=50, kind='%')]

def md_to_flowables(src, stylesheet):
    inliner_lexer = mistune.InlineLexer(InlineRenderer())
    converter = MarkdownWithMath(renderer=BlockRenderer(stylesheet=stylesheet), 
                                 inline=inliner_lexer)
    return converter.render(src)