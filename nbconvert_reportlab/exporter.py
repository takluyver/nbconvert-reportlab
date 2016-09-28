"""Helps you output colourised code snippets in ReportLab documents.

Platypus has an 'XPreformatted' flowable for handling preformatted
text, with variations in fonts and colors.   If Pygments is installed,
calling 'pygments2xpre' will return content suitable for display in
an XPreformatted object.  If it's not installed, you won't get colours.

"""
from binascii import a2b_base64
import io

from traitlets import default
from nbconvert.exporters import Exporter
from reportlab.platypus import (
    Paragraph, SimpleDocTemplate, Spacer, XPreformatted, Image
)
from reportlab.lib.styles import getSampleStyleSheet
from reportlab.lib.pygments2xpre import pygments2xpre

from .rlmarkdown import md_to_flowables

class NbPdfConverter:
    def __init__(self, nb, resources):
        self.nb = nb
        self.resources = resources
        self.stylesheet = getSampleStyleSheet()
        self.pieces = []

    def convert_markdown_cell(self, cell):
        self.pieces.extend(md_to_flowables(cell.source, self.stylesheet))

    def convert_code_cell(self, cell):
        fmt = pygments2xpre(cell.source)
        self.pieces.append(XPreformatted(fmt, style=self.stylesheet['Code']))
        
        for output in cell.outputs:
            self.convert_output(output)

    def convert_output(self, output):
        if output.output_type == 'stream':
            self.add_plain_text(''.join(output.text))
        elif output.output_type in {'display_data', 'execute_result'}:
            self.add_mimebundle(output.data, output.metadata)

    def add_plain_text(self, text):
        self.pieces.append(XPreformatted(text, style=self.stylesheet['Code']))

    def add_mimebundle(self, data, metadata=None):
        if 'image/png' in data:
            img_data = a2b_base64(data['image/png'])
            self.pieces.append(Image(io.BytesIO(img_data),
                                     height=25, width=25, kind='%'))
        elif 'text/plain' in data:
            self.add_plain_text(data['text/plain'])

    def go(self):
        for cell in self.nb.cells:
            if cell.cell_type == 'code':
                self.convert_code_cell(cell)
            elif cell.cell_type == 'markdown':
                self.convert_markdown_cell(cell)
            self.pieces.append(Spacer(1, 12))

        buffer = io.BytesIO()
        doc = SimpleDocTemplate(buffer)
        doc.build(self.pieces)
        return buffer.getvalue()

class ReportlabExporter(Exporter):
    output_mimetype = 'application/pdf'

    @default('file_extension')
    def _file_extension_default(self):
        return '.pdf'

    def from_notebook_node(self, nb, resources=None, **kw):
        nb_copy, resources = super().from_notebook_node(nb, resources)

        output = NbPdfConverter(nb_copy,  resources).go()
        return output, resources


def convertSourceFiles(filenames):
    "Helper function - makes minimal PDF document"
    styT=getSampleStyleSheet()["Title"]
    styC=getSampleStyleSheet()["Code"]
    doc = SimpleDocTemplate("pygments2xpre.pdf")
    S = [].append
    for filename in filenames:
        S(Paragraph(filename,style=styT))
        src = open(filename, 'r').read()
        fmt = pygments2xpre(src)
        S(XPreformatted(fmt, style=styC))
    doc.build(S.__self__)
    print('saved pygments2xpre.pdf')

if __name__=='__main__':
    import sys
    filename = sys.argv[1]
    ex = ReportlabExporter()
    output, resources = ex.from_filename(filename)
    with open('testnb.pdf', 'wb') as f:
        f.write(output)
    print('Written testnb.pdf')
