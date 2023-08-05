#include <math.h>
#include <stdio.h>
#include <stdlib.h>

#include "rwt.h"


void DWTAXIS(
    double *x,
    int n,
    int prod_h,
    int stride,
    double *h,
    int lh,
    int L,
    double *y
    )
{
    double *h0;
    double *h1;
    double *ydummyl;
    double *ydummyh;
    double *xdummy;
    int i;
    int j;
    int actual_L;
    int actual_n;
    int c_o_a;
    int ir;
    int lhm1;
    int ind;
    int base_ind;

    xdummy = (double *)calloc(n+lh-1, sizeof(double));
    ydummyl = (double *)calloc(n, sizeof(double));
    ydummyh = (double *)calloc(n, sizeof(double));

    //
    // Low and high filters.
    //
    h0 = (double *)calloc(lh, sizeof(double));
    h1 = (double *)calloc(lh, sizeof(double));
    for (i=0; i<lh; i++){
        h0[i] = h[lh-i-1];
        h1[i] = h[i];
    }   
    for (i=0; i<lh; i+=2)
        h1[i] = -h1[i];

    lhm1 = lh - 1;
    actual_n = 2*n;

    //
    // Loop on all scales
    //
    for (actual_L=1; actual_L <= L; actual_L++){
        base_ind = 0;
        actual_n = actual_n/2;
        c_o_a = actual_n/2;

        //
        // Loop over outer axes
        //
        for (ir=0; ir<prod_h; ir++)
        {
            //
            // Loop over inner axes
            //
            for (j=0; j<stride; j++)
            {
                //
                // store in dummy variable
                //
                ind = base_ind+j;
                for (i=0; i<actual_n; i++)
                {
                    if (actual_L==1)  
                        xdummy[i] = x[ind];  
                    else 
                        xdummy[i] = y[ind];
    
                    ind += stride;
                }
    
                //
                // perform filtering lowpass and highpass
                //
                fpsconv(xdummy, actual_n, h0, h1, lhm1, ydummyl, ydummyh); 
            
                //
                // restore dummy variables in matrices
                //
                ind = base_ind+j;
                for (i=0; i<c_o_a; i++){    
                    y[ind] = ydummyl[i];
                    y[ind+c_o_a*stride] = ydummyh[i];
                    ind += stride;
                } 
            }
            base_ind += stride * n;
        }  
    }

    free((void *)xdummy);
    free((void *)ydummyl);
    free((void *)ydummyh);
    free((void *)h0);
    free((void *)h1);
}


void IDWTAXIS(
    double *x,
    int n,
    int prod_h,
    int stride,
    double *h,
    int lh,
    int L,
    double *y
    )
{
    double *g0;
    double *g1;
    double *ydummyl;
    double *ydummyh;
    double *xdummy;
    int i;
    int j;
    int actual_L;
    int actual_n;
    int r_o_a;
    int ir;
    int lhm1;
    int lhhm1;
    int ind;
    int base_ind;

    lhm1 = lh - 1;
    lhhm1 = lh/2 - 1;

    //
    // Relocate space for vector copies
    //
    xdummy = (double *)calloc(n, sizeof(double));
    ydummyl = (double *)calloc(n+lhhm1, sizeof(double));
    ydummyh = (double *)calloc(n+lhhm1, sizeof(double));

    //
    // Low and high filters.
    //
    g0 = (double *)calloc(lh, sizeof(double));
    g1 = (double *)calloc(lh, sizeof(double));
    for (i=0; i<lh; i++){
        g0[i] = h[i];
        g1[i] = h[lh-i-1];
    }
    for (i=1; i<=lh; i+=2)
        g1[i] = -g1[i];

    actual_n = n/(1<<(L-1));

    //
    // Copy input signal to output
    //
    for (i=0; i<(stride*n*prod_h); i++)
        x[i] = y[i];

    //
    // Loop on all scales
    //
    for (actual_L=L; actual_L >= 1; actual_L--){
        base_ind = 0;
        r_o_a = actual_n/2;
    
        //
        // Loop on outer axes
        //
        for (ir=0; ir<prod_h; ir++)
        {
            //
            // Loop over inner axes
            //
            for (j=0; j<stride; j++)
            {
                //
                // store in dummy variable
                //
                ind = base_ind+j;
                for (i=0; i<r_o_a; i++)
                {    
                    ydummyl[i+lhhm1] = x[ind];  
                    ydummyh[i+lhhm1] = x[ind+r_o_a*stride];
                    ind += stride;
                }
                
                //
                // perform filtering lowpass and highpass
                //
                bpsconv(xdummy, r_o_a, g0, g1, lhm1, lhhm1, ydummyl, ydummyh);
                
                //
                // restore dummy variables in matrix
                //
                ind = base_ind+j;
                for (i=0; i<actual_n; i++)
                {
                    x[ind] = xdummy[i];  
                    ind += stride;
                }
            }
            base_ind += stride * n;
        }
        actual_n = actual_n*2;
    }

    free((void *)xdummy);
    free((void *)ydummyl);
    free((void *)ydummyh);
    free((void *)g0);
    free((void *)g1);
}
