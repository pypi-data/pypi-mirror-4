cdef extern from "rwt.h":

    void MDWT(
        double *x,
        int m,
        int n,
        double *h,
        int lh,
        int L,
        double *y
        )
        
    void MIDWT(
        double *x,
        int m,
        int n,
        double *h,
        int lh,
        int L,
        double *y
        )
        
    void MRDWT(
        double *x,
        int m,
        int n,
        double *h,
        int lh,
        int L,
        double *yl,
        double *yh
        )

    void MIRDWT(
        double *x,
        int m,
        int n,
        double *h,
        int lh,
        int L,
        double *yl,
        double *yh
        )

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
