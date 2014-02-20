test:
	nosetests

coverage:
	nosetests --with-coverage --cover-html --cover-package=square_words


all: test

.PHONY = coverage test
