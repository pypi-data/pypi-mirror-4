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

/* Subroutine */ int splicingdswap_(integer *n, doublereal *dx, integer *incx, 
	doublereal *dy, integer *incy)
{
    /* System generated locals */
    integer i__1;

    /* Local variables */
    static integer i__, m, ix, iy, mp1;
    static doublereal dtemp;


/*  Purpose   
    =======   

       interchanges two vectors.   
       uses unrolled loops for increments equal one.   

    Further Details   
    ===============   

       jack dongarra, linpack, 3/11/78.   
       modified 12/3/93, array(1) declarations changed to array(*)   

    =====================================================================   

       Parameter adjustments */
    --dy;
    --dx;

    /* Function Body */
    if (*n <= 0) {
	return 0;
    }
    if (*incx == 1 && *incy == 1) {

/*       code for both increments equal to 1   


         clean-up loop */

	m = *n % 3;
	if (m != 0) {
	    i__1 = m;
	    for (i__ = 1; i__ <= i__1; ++i__) {
		dtemp = dx[i__];
		dx[i__] = dy[i__];
		dy[i__] = dtemp;
	    }
	    if (*n < 3) {
		return 0;
	    }
	}
	mp1 = m + 1;
	i__1 = *n;
	for (i__ = mp1; i__ <= i__1; i__ += 3) {
	    dtemp = dx[i__];
	    dx[i__] = dy[i__];
	    dy[i__] = dtemp;
	    dtemp = dx[i__ + 1];
	    dx[i__ + 1] = dy[i__ + 1];
	    dy[i__ + 1] = dtemp;
	    dtemp = dx[i__ + 2];
	    dx[i__ + 2] = dy[i__ + 2];
	    dy[i__ + 2] = dtemp;
	}
    } else {

/*       code for unequal increments or equal increments not equal   
           to 1 */

	ix = 1;
	iy = 1;
	if (*incx < 0) {
	    ix = (-(*n) + 1) * *incx + 1;
	}
	if (*incy < 0) {
	    iy = (-(*n) + 1) * *incy + 1;
	}
	i__1 = *n;
	for (i__ = 1; i__ <= i__1; ++i__) {
	    dtemp = dx[ix];
	    dx[ix] = dy[iy];
	    dy[iy] = dtemp;
	    ix += *incx;
	    iy += *incy;
	}
    }
    return 0;
} /* splicingdswap_ */

