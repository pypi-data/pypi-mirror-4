

SOURCES=   mt64mp.h mt19937-64mp.c pymt64.c

all: build install

build: setup.py $(SOURCES) 
	python setup.py build	

install: setup.py $(SOURCES)  
	python setup.py install --home=$(HOME)

clean:
	rm -f *.o 
	rm -fr build

test:
	gcc -fopenmp  mt19937-64mp.c mt19937-64mptest.c -o mt19937-64mptest.out
	./mt19937-64mptest.out
