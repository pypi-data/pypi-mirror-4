all: _sql.pyd _sql_d.pyd
	
_sql.pyd _sql_d.pyd: sql_wrap.c
	../../Scripts/Python setup.py build --debug
	../../Scripts/Python setup.py build
	cp None ../../Binaries/_sql.pdb
	cp build/lib.*/*.pyd .

sql_wrap.c: sql.i  sqldefs.i  sqlutil.i sqlext.h
	swig -threads -python sql.i	

test: test.py
	../../Scripts/Python test.py


