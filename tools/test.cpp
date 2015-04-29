#include "test.h"
#include <gsl/gsl_fit.h>

void calculate_fit(const double *x, const double *y, int n, double *result, int n_res)
{
//     for(int i=0; i<n;i++)
//     {
//        cout <<x[i]<<"  "<<   y[i]<<"\n";
//     }
    
    for(int i=0; i<n_res; i++)
        result[i] = i+ 10;
    
    double *c0, *c1, *cov00, *cov01, *cov11, *chisq;
    c0 = result;
    c1 = result + 1;
    cov00 = result +2;
    cov01 = result + 3;
    cov11 = result + 4;
    chisq =  result + 5;
    
    gsl_fit_linear (x, 1, y, 1,n, c0, c1, cov00, cov01, cov11, chisq);
    
//     for(int i=0; i<6;i++)
//     {
//        cout <<result[i]<<"\n";
//     }
    
    
}

