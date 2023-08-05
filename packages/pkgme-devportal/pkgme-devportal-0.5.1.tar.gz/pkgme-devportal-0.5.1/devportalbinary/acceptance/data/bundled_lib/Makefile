
all: libtest.so uselib

uselib: libtest.so
	gcc -o $@ $@.c -m32 -L. -ltest

libtest.so: libtest.c
	gcc -shared -m32 -fPIC -o $@ $<

clean:
	rm *~ *.o *.so uselib
