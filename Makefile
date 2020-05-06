#
# Makefile
# Martin Užák, 2020-05-03 19:09
#

DB := db
PILLS := $(shell find $(DB) -name "*.pill") 

.PHONY: test clean

test:
	pytest -v

db.json: $(PILLS)
	./dump.py -j > db.json

clean:
	rm -v db.json
