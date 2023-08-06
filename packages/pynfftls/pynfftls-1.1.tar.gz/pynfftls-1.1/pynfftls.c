#include <Python.h>
#include <stdio.h>
#include <math.h>
#include <stdlib.h>
#include <numpy/arrayobject.h>
#include <time.h>
#include <complex.h>
#include <nfft/nfft3.h>
#include "utils.h"
#include "ls.h"

#ifndef PI
#define PI acos(-1.)
#endif



const char* ProgName = "PyNFFTls";
const char* VersionStr = "1.0";


const char * doc_string = "\t\tPyNFFTls\n\
\n\
This Python module provides the Fast Lomb-Scargle periodogram developed by B. Leroy (2012, Astron. Astrophys. 545, A50)\n\
It is based on the Non-equispaced Fast Fourier Transform (NFFTn http://www-user.tu-chemnitz.de/~potts/nfft/download.php)\n\
Both librairies must be installed.\n\
as well as the FFTW3 library (http://www.fftw.org/)\n\
\n\
Calling sequence:\n\
\t(f,p) = period(t,y,ofac,hifac)\n\
For more details, see the associated documentation\n\
For a complete example, see nfftls_test.py\n\
\n\
This Python module also provides the following methods:\n\
- the Non-equidistant Fast Fourier Transform (NFFT, see http://www-user.tu-chemnitz.de/~potts/nfft/) of a time series:\n\
(f,A) = nfft(t,y,p,d)\n\
For more details, see the associated documentation\n\
- the Discrete  Fourier Transform  (DFT) of a time series:\n\
A = dft(t,y,f)\n\
For more details, see the associated documentation\n\
\n\
For a complete example, see nfftls_test2.py\n\
\n\
R. Samadi, LESIA (http://lesia.obspm.fr), Observatoire de Paris\n22 Dec. 2012\n\
";

static  void allocation_error(char * routine) 
{
  char msg[512];
  sprintf(msg,"%s: memory allocation error",routine);    
  PyErr_SetString(PyExc_MemoryError,msg);
}


/* Computation of the /full/ Non-equidistant Fast Fourier Transform (NFFT) of a real time-series y(t).
*
* Inputs:
* t the times reduced to [1/2 , 1/2)
* y the measurements (NULL , for computing the FT of the window )
* n the number of measurements
* m the number of positive frequencies (null frequency included)

* Output :
* d the Fourier coefficients ( preallocated array of (2*m) elements )
* associated with  m negative frequencies, and m positive frequencies. 
*
*/
static void rnfft(const double* t, const double* y, int n, int m,  double complex * d )
{
  nfft_plan p;
  nfft_init_1d(&p, 2 * m, n);

  if (y)			/* spectrum */
  {
    for (int i = 0; i < n; i++)
    {
      p.x[i] = t[i];
      p.f[i] = y[i];
    }
  }
  else				/* window */
  {
    for (int i = 0; i < n; i++)
    {
      p.x[i] = t[i];
      p.f[i] = 1.0;
    }
  }
  
  if (p.nfft_flags & PRE_ONE_PSI)
    nfft_precompute_one_psi(&p);

  nfft_adjoint(&p);
  /*
   * NFFT plan produces Fourier components for
   * frequencies in an open interval [-m, m[;
   */


  for (int i = 0; i < m; i++)// negative frequencies (m)
    d[i+m] = conj(p.f_hat[i]);

  for (int i = 0; i < m; i++) // positive frequencies (m) , null frequency included
    d[i] = conj(p.f_hat[ i+m]);

  
  nfft_finalize(&p);
}



/* Computation of the /full/ Non-equidistant Fast Fourier Transform (NFFT) of a complex time-series y(t).
*
* Inputs:
* t the times reduced to [1/2 , 1/2)
* y the measurements (NULL , for computing the FT of the window )
* n the number of measurements
* m the number of positive frequencies (null frequency included)

* Output :
* d the Fourier coefficients ( preallocated array of (2*m) elements )
* associated with  m negative frequencies, and m positive frequencies. 
*
*/
static void nfft(const double* t, const double complex * y, int n, int m,  double complex * d )
{
  nfft_plan p;

  nfft_init_1d(&p, 2 * m, n);

  if (y)			/* spectrum */
  {
    for (int i = 0; i < n; i++)
    {
      p.x[i] = t[i];
      p.f[i] = y[i];
    }
  }
  else				/* window */
  {
    for (int i = 0; i < n; i++)
    {
      p.x[i] = t[i];
      p.f[i] = 1.0;
    }
  }
  
  if (p.nfft_flags & PRE_ONE_PSI)
    nfft_precompute_one_psi(&p);

   nfft_adjoint(&p);
  
  /*
   * NFFT plan produces Fourier components for
   * frequencies in an open interval [-m, m[;
   */


  for (int i = 0; i < m; i++)// negative frequencies (m)
    d[i+m] = conj(p.f_hat[i]);

  for (int i = 0; i < m; i++) // positive frequencies (m) , null frequency included
    d[i] = conj(p.f_hat[ i+m]);


 

  nfft_finalize(&p);
}




/* Computation of the Discrete Fast Fourier Transform (NFFT) of a real time-series y(t).
*
* Inputs:
* t the times
* y the measurements
* n the number of measurements
* f the frequencies for which we want to compute the DFT
* m the number of frequencies 
* dir the direction of the trasnform (dir>= for the forward transform, and dir<0 for the inverse transform)

* Output :
* d the Fourier coefficients ( preallocated array of m elements )
* associated with  the frequencie f 
*
*/
static void rdft(const double* t, const double* y,  int n, const double *f, int m, int dir ,  double complex * d )
{
  double dirf = (dir >=0) ? 1. : -1. ;
  double twopi = 2.*PI ;
  double complex sum ;
  double  w , a ;
  for (int i=0 ; i < m; i++) {
    sum = 0. ;
    a = twopi*f[i] ; 
    for (int j=0 ; j <n ; j++)
      {
	w = a*t[j] ; 
	sum = sum + y[j] * cos(w) - _Complex_I * (y[j] * dirf * sin(w) ) ;
      }
    d[i] = sum ;
  }
    
}



/* Computation of the Discrete Fast Fourier Transform (NFFT) of a complex time-series y(t).
*
* Inputs:
* t the times
* y the measurements
* n the number of measurements
* f the frequencies for which we want to compute the DFT
* m the number of frequencies 
* dir the direction of the trasnform (dir>= for the forward transform, and dir<0 for the inverse transform)

* Output :
* d the Fourier coefficients ( preallocated array of m elements )
* associated with  the frequencie f 
*
*/
static void dft(const double* t, const double complex * y,  int n, const double *f, int m, int dir ,  double complex * d )
{
  double dirf = (dir >=0) ? 1. : -1. ;
  double twopi = 2.*PI ;
  double complex sum ; 
  double c , s , w , a ;
  for (int i=0 ; i < m; i++) {
    sum = 0. ;
    a = twopi*f[i] ; 
    for (int j=0 ; j <n ; j++) {
      w = a*t[j] ; 
      c = cos(w); 
      s = dirf * sin(w);
      sum = sum +  ( creal(y[j]) *  c +  cimag(y[j]) * s )  
	+ _Complex_I * ( cimag(y[j]) *  c  - creal(y[j]) * s ) ;
    }
    d[i] = sum ;
  }
    
}



static PyObject* nfft_wrap(PyObject *self, PyObject *args, PyObject *kwds)
{

  /* 
     First we need to get references for the objects
     passed as the argument
  */
  // inputs:
  PyObject * Ot , * Oy ; 
  int m = 0; //  number of positive frequencies
  double dt = 1. ; // sampling time
  Ot = NULL;
  Oy = NULL;
  static char *kwlist[] = {"","","","dt", NULL};

  if (!PyArg_ParseTupleAndKeywords(args,kwds,"OOi|d",kwlist , &Ot, &Oy , &m , &dt  ))
    return NULL;
  
  int n = PyArray_DIM(Ot,0) ; // number elements in t[] and y[]

  if  ( (Oy != Py_None) && (PyArray_DIM(Oy,0) != n) ) 
    {
      PyErr_SetString(PyExc_ValueError,"nfft: t and y must have the same size");
      return 0;
    }

  if  ( m <= 0) 
    {
      PyErr_SetString(PyExc_ValueError,"nfft: the number of positive frequencies must be > 0");
      return 0;
    }


  if ( PyArray_TYPE (Ot) != NPY_DOUBLE   ) 
    {
      PyErr_SetString(PyExc_ValueError,"nfft: t must be an array of double (64 bits)");
      return 0;
    }
  
  if ( (Oy != Py_None) && PyArray_TYPE (Oy) != NPY_DOUBLE && PyArray_TYPE (Oy) != NPY_CDOUBLE  ) 
    {
      PyErr_SetString(PyExc_ValueError,"nfft: y must be an array of double (64 bits) or complex double");
      return 0;
    }
  

  if( PyArray_NDIM(Ot) !=1   )
    {
      PyErr_SetString(PyExc_ValueError,"nfft: t must be an 1D array");
      return 0;
    }


 if(  (Oy != Py_None) && ( PyArray_NDIM(Oy) !=1)   )
    {
      PyErr_SetString(PyExc_ValueError,"nfft: y must be an 1D array");
      return 0;
    }

  double complex * A = NULL ;
  A = malloc( (2*m) *sizeof(double complex ));

  if(!A) {
    allocation_error("nfft");
    return 0 ; 
  }

  double * tn  = malloc( n *sizeof(double complex ));
  double * t = (double *)  PyArray_DATA(Ot) ;
  if(!tn) {  
    free(tn) ;
    allocation_error("nfft");
    return 0 ; 
  }
  memcpy(tn, t  , n * sizeof(double));

  reduce(tn , n, 1.);
   
  if( (Oy != Py_None) && (PyArray_TYPE (Oy) == NPY_DOUBLE) )   rnfft( tn   ,  (double *)  PyArray_DATA(Oy) , n , m ,    A  ) ;
  else {
    if (Oy != Py_None) nfft( tn   ,  (double complex *)  PyArray_DATA(Oy) , n , m ,    A  ) ;
    else rnfft( tn   ,  NULL , n , m ,    A  ) ;
      }

  free(tn) ;

  int nd = 1 ;
  npy_intp dims [1] = {2*m} ;
 
  PyArrayObject * OA = (PyArrayObject *) PyArray_SimpleNewFromData(nd, dims, NPY_CDOUBLE,A) ;
  PyArrayObject * Of = (PyArrayObject *) PyArray_SimpleNew(nd, dims, NPY_DOUBLE) ; 
  
  //  free(d) ; 

  if(OA && Of) {
    OA->flags |= NPY_OWNDATA;
    Of->flags |= NPY_OWNDATA;
    double df = 1./(n*dt) ; 
    double * f = (double *)  PyArray_DATA(Of) ; 
    for (int i=0; i<m ; i++) f[i] = i*df ; // positive frequencies (m) , null frequency included
    for (int i=m; i<2*m ; i++) f[i] = -(2*m - i)*df ; // negative frequencies (m)
    return  Py_BuildValue("NN",  Of , OA );
  }

  free(A) ;
  allocation_error("nfft");
  return 0;



}

static PyObject* dft_wrap(PyObject *self, PyObject *args, PyObject *kwds)
{

  /* 
     First we need to get references for the objects
     passed as the argument
  */
  // inputs:
  PyObject * Ot , * Oy , * Of ; 
  Ot = NULL;
  Oy = NULL;
  Of = NULL;
  int dir  = 1 ; 
  static char *kwlist[] = {"","","","dir", NULL};

  if (!PyArg_ParseTupleAndKeywords(args,kwds,"OOO|i",kwlist,&Ot, &Oy , &Of  , &dir ))
    return NULL;
  
  int n = PyArray_DIM(Ot,0) ; // number elements in t[] and y[]
  int m = PyArray_DIM(Of,0) ; // number elements in f[]

  if  ( PyArray_DIM(Oy,0) != n) 
    {
      PyErr_SetString(PyExc_ValueError,"dft: t and y must have the same size");
      return 0;
    }

  if  ( m <= 0) 
    {
      PyErr_SetString(PyExc_ValueError,"dft: the number of frequencies must be > 0");
      return 0;
    }

  if ( PyArray_TYPE (Ot) != NPY_DOUBLE   ) 
    {
      PyErr_SetString(PyExc_ValueError,"dfft: t must be an array of double (64 bits)");
      return 0;
    }
  
   if ( PyArray_TYPE (Oy) != NPY_DOUBLE && PyArray_TYPE (Oy) != NPY_CDOUBLE  ) 
    {
      PyErr_SetString(PyExc_ValueError,"dft: y must be an array of double (64 bits) or complex double");
      return 0;
    }

  if( PyArray_NDIM(Ot) !=1 || PyArray_NDIM(Oy) !=1  || PyArray_NDIM(Of) !=1 )
    {
      PyErr_SetString(PyExc_ValueError,"dft: t,y, and d must be 1D arrays");
      return 0;
    }


  double complex * A = malloc( m *sizeof(double complex ));

  if(!A) {
    allocation_error("rdft");
    return 0 ; 
  }

  if(PyArray_TYPE (Oy) == NPY_DOUBLE)    rdft( (double *)  PyArray_DATA(Ot)   ,  (double *)  PyArray_DATA(Oy) , n , (double *)  PyArray_DATA(Of)  , m ,  dir , A  ) ;
  else dft( (double *)  PyArray_DATA(Ot)   ,  (double complex *)  PyArray_DATA(Oy) , n , (double *)  PyArray_DATA(Of)  , m ,  dir , A  ) ;

  int nd = 1 ;
  npy_intp dims [1] = {m} ;
 
  PyArrayObject * OA = (PyArrayObject *) PyArray_SimpleNewFromData(nd, dims, NPY_CDOUBLE,A) ;

  if(OA ) {
    OA->flags |= NPY_OWNDATA;
    return  Py_BuildValue("N",  OA );
  }

  free(A) ;
  allocation_error("rdft");
  return 0;



}

static PyObject* period_wrap(PyObject *self, PyObject *args)
{

  /* 
     First we need to get references for the objects
     passed as the argument
  */
  // inputs:
  PyObject * Ot , * Oy ; 
  double ofac , hifac  ;


  Ot = NULL;
  Oy = NULL;

  if (!PyArg_ParseTuple(args,"OOdd",&Ot, &Oy , &ofac , &hifac  ))
    return NULL;
  
  long n = PyArray_DIM(Ot,0) ; // number elements in t[] and y[]

  if  ( PyArray_DIM(Oy,0) != n) 
    {
      PyErr_SetString(PyExc_ValueError,"nfftls: t and y must have the same size");
      return 0;
    }

  if ( PyArray_TYPE (Ot) != NPY_DOUBLE || PyArray_TYPE (Oy) != NPY_DOUBLE  ) 
    {
      PyErr_SetString(PyExc_ValueError,"nfftls: t and y   must be arrays of double (64 bits)");
      return 0;
    }
  

  if( PyArray_NDIM(Ot) !=1 || PyArray_NDIM(Oy) !=1  )
    {
      PyErr_SetString(PyExc_ValueError,"nfftls: t and y  must be 1D arrays");
      return 0;
    }


  double * f = NULL , * p = NULL ;
 
  int  nfreqs = periodogram_simple((double *)  PyArray_DATA(Ot) , (double *)  PyArray_DATA(Oy) , n, ofac, hifac , &f , &p);
  
  if( (f == NULL) || (p == NULL) ) {
    if(f) free(f) ;
    if(p) free(p) ;
    PyErr_SetString(PyExc_MemoryError,"nfftls: unable to allocate the required memory space");
    return 0;
  }

  int nd = 1 ; 
  npy_intp dims [1] = {nfreqs} ;

  PyArrayObject * Of  = (PyArrayObject *) PyArray_SimpleNewFromData(nd, dims, NPY_DOUBLE, f ) ; 
  PyArrayObject * Op  = (PyArrayObject *) PyArray_SimpleNewFromData(nd, dims, NPY_DOUBLE, p ) ; 
  Of->flags |= NPY_OWNDATA; 
  Op->flags |= NPY_OWNDATA; 

  return  Py_BuildValue("NN",  Of , Op );
}

static PyMethodDef nfftlsMethods[] = 
  {
    {"nfft",(PyCFunction) nfft_wrap, METH_VARARGS | METH_KEYWORDS,"Computes the Non-equidistant Fast Fourier Transform (NFFT, see http://www-user.tu-chemnitz.de/~potts/nfft/) of a time series\n\n(f,A) = nfft(t,y,p,dt=1)\n\
Inputs:\n\
t: times\n\
y: signal (real or complex). None for computing the FT of the window. \n\
p: number of positives frequencies\n\
dt: sampling time (default: 1)\n\
Outputs\n\
f: the frequencies ( 2*p elements)\n\
A: the Fourier spectrum (complex numbers) with 2p elements\n\
A[1:p] contains the positive-frequency terms, and A[p:] contains the negative-frequency terms, in order of decreasingly negative frequency.\n\
"},  
    {"dft",(PyCFunction) dft_wrap, METH_VARARGS | METH_KEYWORDS,"Computes the Discrete Fourier Transform (DFT) of a time series\n\nA = dft(t,y,f,dir=1)\n\
Inputs:\n\
t: times\n\
y: signal (real or complex)\n\
f: the frequencies for which we want the Fourier component\n\
dir (keyword): direction of the transform: dir >= 0 for a forward transform and dir < 0 for an inverse transform\n\
Outputs\n\
A: the Fourier components (complex numbers) as many as frequncies\n\
"},
    {"period",period_wrap, METH_VARARGS,"Computes the Lomb-Scargle normalised periodogram of a time series\n\n (f,p) = period(t,y,ofac,hifac)\n\nt: times\ny: signal\nofac: oversampling factor\nhifac: highest frequency in units of the Nyquist frequency\n\nReturn: a tuple (f,p) where: \n\tp: normalised periodogram\n\tf: frequencies\n\nFor more details see Leroy (2012, Astron. Astrophys. 545, A50)\n\n"},
    {NULL, NULL, 0, NULL},
 };


PyMODINIT_FUNC initpynfftls(void)
{
  //  (void)Py_InitModule("nfftls", nfftlsMethods);
  (void) Py_InitModule3("pynfftls", nfftlsMethods , doc_string  ) ; 
 import_array();

}
 

