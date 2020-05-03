#
# Makefile
# Martin Užák, 2020-05-03 19:09
#

.PHONY:
test:
	pytest -v

db.json: 
	./dump.py -j > db.json

clean:
	rm -v db.json
