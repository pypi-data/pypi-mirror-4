test:
	nosetests --with-cover
	pep8 --show-source --show-pep8 .

install:
	easy_install pip
	pip install -r requirements.txt --use-mirrors

build:
	make test
	python setup.py sdist --formats=zip --dist-dir ../tictascii-dist