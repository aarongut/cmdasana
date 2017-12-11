all:
	git submodule init
	git submodule update

tags: ui/*.py main.py
	ctags -R ui main.py
