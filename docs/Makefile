# Minimal makefile for Sphinx documentation
SPHINXOPTS     ?= -j auto
SPHINXBUILD    ?= sphinx-build
AUTOOPTS       = --ignore '*.csv' --port 8181
SOURCEDIR      = .
AUTOSOURCEDIRS = $(SOURCEDIR)/api $(SOURCEDIR)/models $(SOURCEDIR)/modules
BUILDDIR       = _build

# Put it first so that "make" without argument is like "make help".
help:
	@$(SPHINXBUILD) -M help "$(SOURCEDIR)" "$(BUILDDIR)" $(SPHINXOPTS) $(O)

.PHONY: help all clean-apidoc Makefile

all: clean clean-apidoc html

clean-apidoc:
	rm -rf $(AUTOSOURCEDIRS)

livehtml:
	sphinx-autobuild "$(SOURCEDIR)" "$(BUILDDIR)"/html $(SPHINXOPTS) $(AUTOOPTS) $(O) 

# Catch-all target: route all unknown targets to Sphinx builder
%: Makefile
	@$(SPHINXBUILD) -M $@ "$(SOURCEDIR)" "$(BUILDDIR)" $(SPHINXOPTS) $(O)
	# E.g: sphinx-build -M html . _build
