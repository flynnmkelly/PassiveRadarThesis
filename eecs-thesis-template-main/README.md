# EECS Thesis Template
This repository contains a template for the UQ EECS thesis proposal and thesis
documents.  The LaTeX source files are adapted from [Nick Lambourne's EECS
Thesis Template][1].

## Building
I'm currently using the Code-OSS Extension [LaTeX Workshop][2] to generate PDFs
from the TeX source. First, ensure you have working installation of `TeXLive`
on your computer. `biber` should also be installed, as this package is used as
the `BibTeX` backend.

Now, assuming the root folder is opened in the Code workspace, simply open the
`main.tex` file for either `thesis` or `proposal` and trigger a build. The
resulting PDF will be called `main.pdf`.

[1]:https://github.com/nicklambourne/eecs-thesis-template
[2]:https://github.com/James-Yu/LaTeX-Workshop
