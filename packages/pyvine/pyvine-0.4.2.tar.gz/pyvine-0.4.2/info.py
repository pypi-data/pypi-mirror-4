## AUTHOR  : Zhenfei Yuan, Taizhong Hu
## EMAIL   : zfyuan@mail.ustc.edu.cn; thu@ustc.edu.cn
## URL     : taizhonglab.ustc.edu.cn/software/pyvine.html
## DATE    : Jan, 3, 2012
## LICENCE : GPL-v3

"""
PYVINE
======


Regular vine copula provides rich models for dependence structure
modeling. It combines vine structures and families of bivariate
copulas to construct a number of multivariate distributions that can
model a wide range dependence patterns with different tail dependence
for different pairs.

We propose this package for modeling, sampling and testing a more
generalized regular vine copula (R-vine for short). R-vine modeling
algorithm searches for the R-vine structure which maximizes the vine
tree dependence, i.e., the sum of the absolute values of kendall's tau
for paired variables on edges. The maximum likelihood estimation
algorithm takes the sequential estimation as initial value and uses
L-BFGS-B algorithm for the likelihood value optimization. R-vine
sampling algorithm traverses all the edges of vine structure from the
last tree in a recursive way, and generates the marginal samples on
each edge according to some nested conditions. Goodness-of-fit testing
algorithm first generates Rosenblatt's transformed data E, then tests
the composite hypothesis H_0*: E ~ C* by using Anderson-Darling
statistic, where C* is the independence copula. Bootstrap method will
generate the empirical distribution of Anderson-Darling statistic
replications to compute an adjusted P-value.

The computing of related functions of copulas such as cumulative
distribution functions (c.d.f.), H-functions and inverse H-functions
often meets with the problem of overflow, which is a problem in the
situation when the high precision is requied. We solve this problem by
reinvestigating the following six popular families of bivariate
copulas: Normal, Student t, Clayton, Gumbel, Frank and Joe
copulas. Approximations of the above related functions of copulas are
given when the overflow occurs in the computations. All these are
implemented in a subpackage bvcopula, in which subroutines are written
in Fortran and wrapped into Python via f2py and, hence, good
performance is guaranteed.
"""



__all__=[
    'Rvine'
    ]

    
