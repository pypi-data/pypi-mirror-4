WINPYTHON=/cygdrive/c/Python25/python

all:  exe

exe: pyomo.exe pysos.exe

pyomo.exe:
	(cd pyomo; $(WINPYTHON) setup.py py2exe)
	rm -Rf pyomo/build

pysos.exe:
	(cd pysos; $(WINPYTHON) setup.py py2exe)
	rm -Rf pysos/build

