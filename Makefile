#
# Makefile
# Martin Užák, 2020-05-03 19:09
#

DB := db
PILLS := $(shell find $(DB) -name "*.pill") 
UI_DIR ?= ../etymolog-ui

.PHONY: test coverage clean

test:
	pytest -v

coverage:
	coverage run  --source . --omit test\*,parsetab.py --branch -m pytest
	coverage report

db.json: $(PILLS)
	./dump.py -j > db.json
	cp db.json ${UI_DIR}/public/

count_slovak_words:
	grep -c 'sk:' db/rendlich_franco/* | cut -d':' -f2 | paste -sd+ - | bc


clean:
	rm -fv db.json
