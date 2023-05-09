all: buildmo

buildmo:
	# WARNING: the second sed below will only works correctly with the languages that don't contain "-"
	for file in `ls po/*.po`; do \
		lang=`echo $$file | sed 's@po/@@' | sed 's/\.po//' | sed 's/kotori-//'`; \
		install -d mo/$$lang/LC_MESSAGES/; \
		msgfmt -o mo/$$lang/LC_MESSAGES/kotori.mo $$file; \
	done \

clean:
	rm -rf mo

lint:
	black --check --diff kotori kotori.py
	flake8 .

black:
	black kotori kotori.py

test:
	mkdir -p "/tmp/kotori-py"
	PYTHONPYCACHEPREFIX="/tmp/kotori-py" python3 -m pytest tests
	rm -rf "/tmp/kotori-py"
