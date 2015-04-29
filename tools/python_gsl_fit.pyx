cimport numpy as np
import numpy as np

cdef extern from "test.h" :
    void calculate_fit(const double *x, const double *y,int n,  double *result, int n_res)
    
cdef int fit_gsl(np.ndarray[double ,ndim=1] x, np.ndarray[double ,ndim=1] y, np.ndarray[double,ndim=1] res):
    cdef np.ndarray[np.double_t, ndim=1, mode="c"] xc, yc, resc
    xc = np.ascontiguousarray(x, dtype=np.double)
    yc = np.ascontiguousarray(y, dtype=np.double)
    resc = np.ascontiguousarray(res, dtype=np.double)
    
    calculate_fit(&xc[0], &yc[0], len(x), &resc[0], len(res))
    return 0


def python_gsl_fit(x,y,res):
    '''x, y tablice z danymi, res tablica dla wynikow zgodnie z opisem gsl \n
    res[0] - c0,\n
    res[1] = c1,\n
    res[2] = cov00, \n
    res[3] = cov01, \n
    res[4] = cov11,\n
    res[5] = chisq;
    '''
    
    fit_gsl(x,y,res)