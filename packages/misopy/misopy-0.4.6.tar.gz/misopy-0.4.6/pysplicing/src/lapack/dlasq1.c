/*  -- translated by f2c (version 20100827).
   You must link the resulting object file with libf2c:
	on Microsoft Windows system, link with libf2c.lib;
	on Linux or Unix systems, link with .../path/to/libf2c.a -lm
	or, if you install libf2c.a in a standard place, with -lf2c -lm
	-- in that order, at the end of the command line, as in
		cc *.o -lf2c -lm
	Source for libf2c is in /netlib/f2c/libf2c.zip, e.g.,

		http://www.netlib.org/f2c/libf2c.zip
*/

#include "f2c.h"

/* Table of constant values */

static integer c__1 = 1;
static integer c__2 = 2;
static integer c__0 = 0;

/* Subroutine */ int splicingdlasq1_(integer *n, doublereal *d__, doublereal *e, 
	doublereal *work, integer *info)
{
    /* System generated locals */
    integer i__1, i__2;
    doublereal d__1, d__2, d__3;

    /* Builtin functions */
    double sqrt(doublereal);

    /* Local variables */
    static integer i__;
    static doublereal eps;
    extern /* Subroutine */ int splicingdlas2_(doublereal *, doublereal *, doublereal 
	    *, doublereal *, doublereal *);
    static doublereal scale;
    static integer iinfo;
    static doublereal sigmn;
    extern /* Subroutine */ int splicingdcopy_(integer *, doublereal *, integer *, 
	    doublereal *, integer *);
    static doublereal sigmx;
    extern /* Subroutine */ int splicingdlasq2_(integer *, doublereal *, integer *);
    extern doublereal splicingdlamch_(char *);
    extern /* Subroutine */ int splicingdlascl_(char *, integer *, integer *, 
	    doublereal *, doublereal *, integer *, integer *, doublereal *, 
	    integer *, integer *);
    static doublereal safmin;
    extern /* Subroutine */ int splicingxerbla_(char *, integer *, ftnlen), splicingdlasrt_(
	    char *, integer *, doublereal *, integer *);


/*  -- LAPACK routine (version 3.2)                                    --   

    -- Contributed by Osni Marques of the Lawrence Berkeley National   --   
    -- Laboratory and Beresford Parlett of the Univ. of California at  --   
    -- Berkeley                                                        --   
    -- November 2008                                                   --   

    -- LAPACK is a software package provided by Univ. of Tennessee,    --   
    -- Univ. of California Berkeley, Univ. of Colorado Denver and NAG Ltd..--   


    Purpose   
    =======   

    DLASQ1 computes the singular values of a real N-by-N bidiagonal   
    matrix with diagonal D and off-diagonal E. The singular values   
    are computed to high relative accuracy, in the absence of   
    denormalization, underflow and overflow. The algorithm was first   
    presented in   

    "Accurate singular values and differential qd algorithms" by K. V.   
    Fernando and B. N. Parlett, Numer. Math., Vol-67, No. 2, pp. 191-230,   
    1994,   

    and the present implementation is described in "An implementation of   
    the dqds Algorithm (Positive Case)", LAPACK Working Note.   

    Arguments   
    =========   

    N     (input) INTEGER   
          The number of rows and columns in the matrix. N >= 0.   

    D     (input/output) DOUBLE PRECISION array, dimension (N)   
          On entry, D contains the diagonal elements of the   
          bidiagonal matrix whose SVD is desired. On normal exit,   
          D contains the singular values in decreasing order.   

    E     (input/output) DOUBLE PRECISION array, dimension (N)   
          On entry, elements E(1:N-1) contain the off-diagonal elements   
          of the bidiagonal matrix whose SVD is desired.   
          On exit, E is overwritten.   

    WORK  (workspace) DOUBLE PRECISION array, dimension (4*N)   

    INFO  (output) INTEGER   
          = 0: successful exit   
          < 0: if INFO = -i, the i-th argument had an illegal value   
          > 0: the algorithm failed   
               = 1, a split was marked by a positive value in E   
               = 2, current block of Z not diagonalized after 30*N   
                    iterations (in inner while loop)   
               = 3, termination criterion of outer while loop not met   
                    (program created more than N unreduced blocks)   

    =====================================================================   


       Parameter adjustments */
    --work;
    --e;
    --d__;

    /* Function Body */
    *info = 0;
    if (*n < 0) {
	*info = -2;
	i__1 = -(*info);
	splicingxerbla_("DLASQ1", &i__1, (ftnlen)6);
	return 0;
    } else if (*n == 0) {
	return 0;
    } else if (*n == 1) {
	d__[1] = abs(d__[1]);
	return 0;
    } else if (*n == 2) {
	splicingdlas2_(&d__[1], &e[1], &d__[2], &sigmn, &sigmx);
	d__[1] = sigmx;
	d__[2] = sigmn;
	return 0;
    }

/*     Estimate the largest singular value. */

    sigmx = 0.;
    i__1 = *n - 1;
    for (i__ = 1; i__ <= i__1; ++i__) {
	d__[i__] = (d__1 = d__[i__], abs(d__1));
/* Computing MAX */
	d__2 = sigmx, d__3 = (d__1 = e[i__], abs(d__1));
	sigmx = max(d__2,d__3);
/* L10: */
    }
    d__[*n] = (d__1 = d__[*n], abs(d__1));

/*     Early return if SIGMX is zero (matrix is already diagonal). */

    if (sigmx == 0.) {
	splicingdlasrt_("D", n, &d__[1], &iinfo);
	return 0;
    }

    i__1 = *n;
    for (i__ = 1; i__ <= i__1; ++i__) {
/* Computing MAX */
	d__1 = sigmx, d__2 = d__[i__];
	sigmx = max(d__1,d__2);
/* L20: */
    }

/*     Copy D and E into WORK (in the Z format) and scale (squaring the   
       input data makes scaling by a power of the radix pointless). */

    eps = splicingdlamch_("Precision");
    safmin = splicingdlamch_("Safe minimum");
    scale = sqrt(eps / safmin);
    splicingdcopy_(n, &d__[1], &c__1, &work[1], &c__2);
    i__1 = *n - 1;
    splicingdcopy_(&i__1, &e[1], &c__1, &work[2], &c__2);
    i__1 = (*n << 1) - 1;
    i__2 = (*n << 1) - 1;
    splicingdlascl_("G", &c__0, &c__0, &sigmx, &scale, &i__1, &c__1, &work[1], &i__2, 
	    &iinfo);

/*     Compute the q's and e's. */

    i__1 = (*n << 1) - 1;
    for (i__ = 1; i__ <= i__1; ++i__) {
/* Computing 2nd power */
	d__1 = work[i__];
	work[i__] = d__1 * d__1;
/* L30: */
    }
    work[*n * 2] = 0.;

    splicingdlasq2_(n, &work[1], info);

    if (*info == 0) {
	i__1 = *n;
	for (i__ = 1; i__ <= i__1; ++i__) {
	    d__[i__] = sqrt(work[i__]);
/* L40: */
	}
	splicingdlascl_("G", &c__0, &c__0, &scale, &sigmx, n, &c__1, &d__[1], n, &
		iinfo);
    }

    return 0;

/*     End of DLASQ1 */

} /* splicingdlasq1_ */

