#------------------------------------------------------------------------------
# file: $Id: Makefile 58 2012-09-06 03:46:56Z griff1n $
# desc: pysyncml Makefile. the pysyncml process:
#
#         1) create unit test that tests the change to be made
#         2) make changes to the source code & update documentation
#         3) verify that nothing broke and the coverage % is *increased*:
#              $ make test-all
#              $ make cover
#         4) commit the change to the repository
#         5) test package creation
#              $ make pkg
#         6) deploy package and documentation to pypi and sourceforge
#              $ make deploy
#         7) add the new package to the repository and commit
#              $ svn add dist/*
#              $ svn commit
#         8) ...
#         9) be happy
#
# auth: griffin <griffin@uberdev.org>
# date: 2012/06/30
# copy: (C) CopyLoose 2012 UberDev <hardcore@uberdev.org>, No Rights Reserved.
#------------------------------------------------------------------------------

# PYVER          := $(shell python -V 2>&1)

NOSE            = nosetests
SPHINX          = sphinx-build
RSYNC           = rsync
RSYNCUSER       = griff1n
PY264           = . ~/virtualenv/pysyncml-2.6.4/bin/activate
PY266           = . ~/virtualenv/pysyncml-2.6.6/bin/activate
PY272           = . ~/virtualenv/pysyncml-2.7.2/bin/activate

# NOTE: virtualenv prepared with:
#  $ ./configure '--prefix=/usr/local/contrib/app/python/VERSION' '--enable-ipv6' '--enable-unicode=ucs4' '--with-dbmliborder=bdb:gdbm' '--with-system-expat' '--with-system-ffi' '--with-fpectl' 'CC=gcc' 'CFLAGS=-g -fstack-protector --param=ssp-buffer-size=4 -Wformat -Wformat-security -Werror=format-security ' 'LDFLAGS=-Wl,-Bsymbolic-functions -Wl,-z,relro -L/usr/lib/i386-linux-gnu'
#  $ make && make install
#  $ /usr/local/contrib/app/python/VERSION/bin/python setuptools-0.6c11/setup.py install
#  $ /usr/local/contrib/app/python/VERSION/bin/easy_install virtualenv
#  $ /usr/local/contrib/app/python/VERSION/bin/virtualenv ~/virtualenv/pysyncml-VERSION
#  $ . ~/virtualenv/pysyncml-VERSION/bin/activate
#  (pysyncml-VERSION)$ pip install distribute
#  (pysyncml-VERSION)$ pip install nose==1.1.2 coverage==3.5.2 sphinx==1.1.3 SQLAlchemy==0.7.7
# NOTE: on ubuntu-12, SSLv2 is disabled in openssl... so a patch as described in:
#  http://blog.schmichael.com/2012/05/29/building-python-2-6-8-on-ubuntu-12-04/
#  (this was fixed in python 2.7, but not back-ported)

test:
	@echo "[  ] running test in active python version..."
	python setup.py test

test-all:
	@echo "[  ] running test in all defined python versions..."
	$(PY264) && python setup.py test
	$(PY266) && python setup.py test
	$(PY272) && python setup.py test

nose:
	@echo "[  ] running nosetest (without coverage)..."
	$(NOSE) --verbose --where src

cover:
	@echo "[  ] running nosetest with coverage..."
	$(NOSE) --with-coverage \
	  --cover-erase \
	  --cover-package=pysyncml \
	  --verbose --where src

#	  --cover-html --cover-html-dir=coverage \
#	  --cover-branches

pkg:
	@echo "[  ] building python distribution egg..."
	$(PY264) && python setup.py bdist_egg
	$(PY272) && python setup.py bdist_egg
	$(PY272) && python setup.py sdist

# pkg-prod:
# 	@echo "[  ] building python production distribution egg..."
# 	# NOTE: this does not seem to work with setuptools 0.6c12
# 	python setup.py --no-svn-revision --no-date --tag-build-name "" bdist_egg

upload: upload-pypi upload-sf upload-docs

upload-pypi:
	@echo "[  ] building and uploading python distribution egg..."
	$(PY264) && python setup.py bdist_egg upload
	$(PY272) && python setup.py bdist_egg upload
	$(PY272) && python setup.py sdist upload

upload-sf:
	@echo "[  ] uploading distributions to sourceforge..."
	$(RSYNC) -avz --rsh ssh --filter '- .svn' \
	  dist/ $(RSYNCUSER)@frs.sourceforge.net:/home/frs/project/pysyncml/trunk

docs:
	@echo "[  ] building HTML documentation..."
	mkdir -p sphinx/build
	$(SPHINX) -b html -c sphinx -d sphinx/build src doc
# TODO: perhaps convert to using setup.py for this?
#       the problem that i had was that i was getting a very confusing
#         error: sphinx/conf.py: No such file or directory
#       (but the file clearly existed)
#	python setup.py build_sphinx

upload-docs:
	@echo "[  ] uploading HTML documentation..."
	python setup.py upload_docs

deploy: docs upload

# cheesecake:
# 	@echo "[  ] testing the kwalitee of pysyncml..."
# 	cheesecake_index --name=svnpublish

clean-docs:
	find doc -type f -a '!' -path '*/.svn/*' -delete

clean:
	find src/pysyncml -iname '*.pyc' -exec rm {} \;
	rm -fr sphinx/build/* build/*

#------------------------------------------------------------------------------
# end of $Id: Makefile 58 2012-09-06 03:46:56Z griff1n $
#------------------------------------------------------------------------------
