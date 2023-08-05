/* \file pymt64.c
 * \author R. Samadi
 * 
 * PyMT64 : 64-bit and thread safe version of the Mersenne Twister pseudorandom number generator
 * 
 * It is a C - Python interface based on the original C source code (mt19937-64.c)
 * by Takuji Nishimura and Makoto Matsumoto 
 *
 *
 * This is a free software: you can redistribute it and/or modify
 * it under the terms of the GNU General Public License as published by
 * the Free Software Foundation, either version 3 of the License, or
 * (at your option) any later version.
 *
 * This software is distributed in the hope that it will be useful,
 * but WITHOUT ANY WARRANTY; without even the implied warranty of
 * MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
 * GNU General Public License for more details.
 *
 * You should have received a copy of the GNU General Public License
 * along with this code.  If not, see <http://www.gnu.org/licenses/>.
 *
 * Copyright (C) 2012 by R. Samadi
 */
#include <Python.h>
#include <stdio.h>
#include <math.h>
#include <stdlib.h>
#include <numpy/arrayobject.h>
#include <time.h>
#include "mt64mp.h"

#define PI acos(-1.)

const char * doc_string = "\t\t\tPyMT64\n\nPyMT64 is a Python version of the Mersenne Twister (MT) 64-bit pseudorandom number generator by Takuji Nishimura and Makoto Matsumoto (see http://www.math.sci.hiroshima-u.ac.jp/~m-mat/MT/emt64.html and the references below).\n\n\
This customised version is thread safe and was interfaced from C to Python (see pymt64.c)\n\n\
This module provides the following methods:\n\
- init : initialisation of the state vector used by the pseudorandom number generator (PNG)\n\
- uniform : generation of an uniform distribution\n\
- normal : generation of two Normal distributions\n\
- poisson : generation of a Poisson distribution\n\
\n\
The period of the PNG is 2**19937-1.\n\
\n\
Example:\n\
\timport time\n\
\timport pymt64\n\
\tseed = int(time.time()) # the initial seed\n\
\tmt = pymt64.init(seed) # initialisation of the state vector of MT\n\
\tu = pymt64.uniform(mt,10) # generation of an uniform distribution\n\
\tprint u\n\
\t[ 0.94295421  0.47222327  0.634552    0.26012686  0.38431784  0.23995444\n\
\t 0.02175826  0.8209848   0.79266556  0.8638286 ]\n\
\n\
\n\
For a complete example, see pymt64_test.py\n\
\n\
Note: the state vector 'mt' returned by pymt64.init has 313 elements instead of the 312 elements of the original C code. This is because the 313th element stores the associated counter (mti).\n\
\n\nR. Samadi (LESIA, Observatoire de Paris), 22 Dec. 2012\n\nReferences:\n- T. Nishimura, ``Tables of 64-bit Mersenne Twisters'', ACM Transactions on Modeling and  Computer Simulation 10. (2000) 348--357.\n- M. Matsumoto and T. Nishimura, ``Mersenne Twister: a 623-dimensionally equidistributed uniform pseudorandom number generator'', ACM Transactions on Modeling and Computer Simulation 8. (Jan. 1998) 3--30. " ;





double gammln(double xx)
{
	double x,y,tmp,ser;
	static double cof[6]={76.18009172947146,-86.50532032941677,
		24.01409824083091,-1.231739572450155,
		0.1208650973866179e-2,-0.5395239384953e-5};
	int j;

	y=x=xx;
	tmp=x+5.5;
	tmp -= (x+0.5)*log(tmp);
	ser=1.000000000190015;
	for (j=0;j<=5;j++) ser += cof[j]/++y;
	return -tmp+log(2.5066282746310005*ser/x);
}


double poisson(UL64 * mt , int * mti , double xm )
{
	double gammln(double xx);
	static double sq,alxm,g,oldm=(-1.0);
	double em,t,y;

	if (xm < 12.0) {
		if (xm != oldm) {
			oldm=xm;
			g=exp(-xm);
		}
		em = -1;
		t=1.0;
		do {
			++em;
			t *= genrand64_real1(mt,mti) ;
		} while (t > g);
	} else {
		if (xm != oldm) {
			oldm=xm;
			sq=sqrt(2.0*xm);
			alxm=log(xm);
			g=xm*alxm-gammln(xm+1.0);
		}
		do {
			do {
				y=tan(PI*genrand64_real1(mt,mti));
				em=sq*y+xm;
			} while (em < 0.0);
			em=floor(em);
			t=0.9*(1.0+y*y)*exp(em*alxm-gammln(em+1.0)-g);
		} while (genrand64_real1(mt,mti)  > t);
	}
	return em;
}


void uniformn(UL64 * mt , int * mti, double * x , long n )

{
  long i ;
  for (i=0l;i<n;i++)     x[i] =  genrand64_real1(mt,mti) ;
  
}

void poissonn(UL64 * mt , int * mti , double xm, double * x , long n )

{
  long i ;
  for (i=0l;i<n;i++)     x[i] = poisson(mt,mti,xm);
  
}

void normaln(UL64 * mt, int * mti , double * x , double * y, long n )
{
  long i ; 
  double  r1 , r2 , u ;
  for (i=0l;i<n;i++) {
    r1 =  genrand64_real1(mt,mti) ; 
    r2 =  genrand64_real1(mt,mti) ;
    u = sqrt(-2.*log(r1)) ;
    x[i] = u * cos(2.*PI * r2) ;
    y[i] = u * sin(2.*PI * r2) ;
  }
}

int check_valid_mt_object (PyObject * Omt ) {
  
  char msg[512];
  
   int nd = PyArray_NDIM(Omt) ;

    if ((nd !=1)) 
    {
      sprintf(msg,"PyMT64: the input array must be a 1D array)");
      PyErr_SetString(PyExc_ValueError,msg);
      return 0;
    }

    int n = PyArray_DIM(Omt,0) ;

    if ((n <MTSIZE+1 )) 
    {
      sprintf(msg,"PyMT64: the input array must have a size >=%d",MTSIZE);
      PyErr_SetString(PyExc_ValueError,msg);
      return 0;
    }

    if (PyArray_TYPE (Omt) != NPY_UINT64) 
    {
      sprintf(msg,"PyMT64: the input array must an unsigned int64");
      PyErr_SetString(PyExc_ValueError,msg);
      return 0;

    }

    return 1 ; 

}

static PyObject* init(PyObject *self, PyObject *args)
{
  /* buffer for return messages */

  char msg[512];

  /* 
    First we need to get references for the objects
    passed as the argument
  */

   PyObject * Omt = NULL ; 
   UL64 seed ;

   if (!PyArg_ParseTuple(args,"K",&Omt,&seed )) 
    return NULL;

   int nd = 1 ;
   npy_intp dims [1] = {MTSIZE+1} ;
   Omt = PyArray_SimpleNew(nd, dims, NPY_UINT64 ) ;
   UL64 * mt  = (UL64 *)  PyArray_DATA(Omt) ;
   init_genrand64(seed , mt , mt + MTSIZE  ) ; 

   //    the state vector 'mt'  has MTSIZE+1  elements 
   //    instead of the MTSIZE  elements of the original C code. 
   ///   This is because the last element stores the associated counter (mti).

   return  Py_BuildValue("N",  Omt ) ;
}


static PyObject* uniform_wrap(PyObject *self, PyObject *args)
{
  /* buffer for return messages */

  char msg[512];

  /* 
    First we need to get references for the objects
    passed as the argument
  */

  PyObject  * Omt , * Ox ; 
  Ox = NULL;
  Omt = NULL;
  long int n ; 

  if (!PyArg_ParseTuple(args,"Ol",&Omt,&n))
    return NULL;



  if ( check_valid_mt_object (Omt) == 1) {
    UL64 * mt  = (UL64 *)  PyArray_DATA(Omt) ;
    int nd = 1 ;
    npy_intp dims [1] = {n} ;
    Ox = PyArray_SimpleNew(nd, dims, NPY_DOUBLE ) ;
    uniformn( mt  , mt + MTSIZE , (double *)  PyArray_DATA(Ox),n) ;
  }
	   

  return  Py_BuildValue("N",  Ox  ) ;
}

static PyObject* poisson_wrap(PyObject *self, PyObject *args)
{
  /* buffer for return messages */

  char msg[512];

  /* 
    First we need to get references for the objects
    passed as the argument
  */

  PyObject * Ox , * Omt  ; 
  double xm ; 
  Ox = NULL;
  Omt = NULL;
  long int n ; 

  if (!PyArg_ParseTuple(args,"Odl",&Omt, &xm , &n ))
    return NULL;

  if ( check_valid_mt_object (Omt) == 1) {
    UL64 * mt  = (UL64 *)  PyArray_DATA(Omt) ;
    int nd = 1 ;
    npy_intp dims [1] = {n} ;
    Ox = PyArray_SimpleNew(nd, dims, NPY_DOUBLE ) ;
    poissonn( mt , mt + MTSIZE ,xm,(double *)  PyArray_DATA(Ox),n) ;
  }

  return  Py_BuildValue("N",  Ox  ) ;
}




static PyObject* normal_wrap(PyObject *self, PyObject *args)
{
  /* buffer for return messages */

  char msg[512];

  /* 
    First we need to get references for the objects
    passed as the argument
  */

  PyObject * Ox , * Oy , * Omt ; 
  Ox = NULL;
  Oy = NULL;
  Omt = NULL;
  long int n ; 

  if (!PyArg_ParseTuple(args,"Ol", &Omt , &n))
    return NULL;

  if ( check_valid_mt_object (Omt) == 1) {
    UL64 * mt  = (UL64 *)  PyArray_DATA(Omt) ;
    int nd = 1 ;
    npy_intp dims [1] = {n} ;
    Ox = PyArray_SimpleNew(nd, dims, NPY_DOUBLE ) ;
    Oy = PyArray_SimpleNew(nd, dims, NPY_DOUBLE ) ;

   normaln( mt  , mt + MTSIZE , (double *)  PyArray_DATA(Ox),(double *)  PyArray_DATA(Oy) , n) ;

  }
  

  return   Py_BuildValue("NN",  Ox , Oy ) ;
}


static PyMethodDef pymt64Methods[] = 
  {
    {"uniform",uniform_wrap, METH_VARARGS,"x = uniform(mt,n)\n\nGenerates n random numbers on [0,1]-real-interval"},
    {"normal",normal_wrap, METH_VARARGS,"(x,y) = normal(mt,n)\n\nGenerates two random series of size n Normally distributed with zero mean and variance one. "},
    {"poisson",poisson_wrap, METH_VARARGS,"x = poisson(mt,mu,n)\n\nGenerates a Poisson distribution of mean mu."},
    {"init",init, METH_VARARGS,"mt = init(seed)\n\nFunction used to initialise the state vector mt used by the pseudorandom number generator. "},
    {NULL, NULL, 0, NULL}
  };


PyMODINIT_FUNC initpymt64(void)
{
  //  (void)Py_InitModule("pymt64", pymt64Methods);
  (void) Py_InitModule3("pymt64",pymt64Methods  , doc_string  ) ; 
  import_array();
  
}
 

