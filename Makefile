all: buildmo

buildmo:
	# WARNING: the second sed below will only works correctly with the languages that don't contain "-"
	for file in `ls po/*.po`; do \
		lang=`echo $$file | sed 's@po/@@' | sed 's/\.po//' | sed 's/kotori-//'`; \
		install -d usr/share/locale/$$lang/LC_MESSAGES/; \
		msgfmt -o usr/share/locale/$$lang/LC_MESSAGES/kotori.mo $$file; \
	done \

clean:
	rm -rf usr/share/locale

lint:
	black --check --diff usr/lib/kotori/kotori usr/lib/kotori/kotori.py
	flake8 .

black:
	black usr/lib/kotori/kotori usr/lib/kotori/kotori.py

test:
	mkdir -p "/tmp/kotori-py"
	PYTHONPYCACHEPREFIX="/tmp/kotori-py" python3 -m pytest tests
	rm -rf "/tmp/kotori-py"
