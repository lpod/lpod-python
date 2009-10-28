VER = $(shell git describe)
DEST = lpod-$(VER)
PYTHON = $(shell cat python/python_path.txt)

all:
	@echo "Usage:"
	@echo "  dist   generate the distribution tarball"

dist:
	$(shell [[ -d $(DEST) ]] && rm $(DEST) -rf)
	@mkdir -p $(DEST)/python
	# Copy licenses
	@cp gpl-3.0.txt $(DEST)
	@cp apacheLICENSE-2.0.txt $(DEST)
	# Copy documentation
	@(cd doc && make clean > /dev/null)
	@cp -r doc $(DEST)
	# Copy Python
	@(cd python && rm dist -rf && $(PYTHON) setup.py sdist > /dev/null)
	@(cd $(DEST)/python && tar --strip-components 1 -xf ../../python/dist/*.tar.gz)
	# Copy Perl
	@cp -r perl $(DEST)
	# Copy Ruby
	@cp -r ruby $(DEST)
	@tar cf $(DEST).tar.gz $(DEST)
	@rm $(DEST) -rf
	@echo
	@echo "  $(DEST).tar.gz generated."
	@echo

.PHONY: dist
