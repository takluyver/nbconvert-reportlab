An experimental tool to convert Jupyter notebooks to PDFs using
`Reportlab <https://pypi.python.org/pypi/reportlab/>`__.

Install:

    pip install nbconvert_reportlab

Use:

    jupyter nbconvert --to pdf-rl MyNotebook.ipynb

Jupyter comes with support for generating PDFs by filling a template to
make a Latex file, and then running Latex to convert that to PDF. This is a
powerful approach, but Latex code is not a great intermediate format for
automatic generation, and that can lead to a variety of problems.

This package uses the open source Reportlab Toolkit to convert notebooks
directly to PDFs. This avoids a lot of complexity, but at least for now there
are many things that it cannot handle and will simply skip over.
