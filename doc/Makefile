# Makefile for Sphinx documentation
#

# Git repository
GIT_VERSION = $(shell ../bin/release.py)

# You can set these variables from the command line.
SPHINXOPTS    =
SPHINXBUILD   = sphinx-build
PAPER         =

# Internal variables.
PAPEROPT_a4     = -D latex_paper_size=a4
PAPEROPT_letter = -D latex_paper_size=letter
ALLSPHINXOPTS   = -d .build/doctrees $(PAPEROPT_$(PAPER)) $(SPHINXOPTS) .

.PHONY: help clean html latex pdf changes linkcheck release

help:
	@echo "Please use \`make <target>' where <target> is one of"
	@echo "  html      to make standalone HTML files"
	@echo "  latex     to make LaTeX files, you can set PAPER=a4 or PAPER=letter"
	@echo "  pdf       to make PDF files, you can set PAPER=a4 or PAPER=letter"
	@echo "  changes   to make an overview over all changed/added/deprecated items"
	@echo "  linkcheck to check all external links for integrity"

clean:
	-rm -rf .build
	-rm -rf lpod-docs-*.tgz

html:
	mkdir -p .build/html .build/doctrees
	$(SPHINXBUILD) -b html $(ALLSPHINXOPTS) .build/html
	@echo
	@echo "Build finished. The HTML pages are in .build/html."

latex:
	mkdir -p .build/latex .build/doctrees
	$(SPHINXBUILD) -b latex $(ALLSPHINXOPTS) .build/latex
	@echo
	@echo "Build finished; the LaTeX files are in .build/latex."
	@echo "Run \`make all-pdf' or \`make all-ps' in that directory to" \
	      "run these through (pdf)latex."

pdf: latex
	cd .build/latex && make all-pdf
	@echo
	@echo "Your PDF is available in .build/latex"

changes:
	mkdir -p .build/changes .build/doctrees
	$(SPHINXBUILD) -b changes $(ALLSPHINXOPTS) .build/changes
	@echo
	@echo "The overview file is in .build/changes."

linkcheck:
	mkdir -p .build/linkcheck .build/doctrees
	$(SPHINXBUILD) -b linkcheck $(ALLSPHINXOPTS) .build/linkcheck
	@echo
	@echo "Link check complete; look for any errors in the above output " \
	      "or in .build/linkcheck/output.txt."

release: html pdf
	cd .build/html && tar czf ../../lpod-docs-html-$(GIT_VERSION).tgz *
	cd .build/latex && tar czf ../../lpod-docs-pdf-$(GIT_VERSION).tgz lpod.pdf
	@echo
	@echo "html doc is available ./lpod-docs-html-$(GIT_VERSION).tgz and"
	@echo "pdf doc is available ./lpod-docs-pdf-$(GIT_VERSION).tgz"



