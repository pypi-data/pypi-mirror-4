#!/usr/bin/env python

NAME                  = "pyvine"
MAINTAINER            = "Zhenfei Yuan, Taizhong Hu"
MAINTAINER_EMAIL      = "zfyuan@mail.ustc.edu.cn, thu@ustc.edu.cn"
URL                   = "taizhonglab.ustc.edu.cn/software/pyvine.html"
DOWNLOAD_URL          = "taizhonglab.ustc.edu.cn/software/pyvine/pyvine-0.4.2.tar.gz"
LICENSE               = "GPL-v3"
PLATFORMS             = ["Windows","Linux"]
MAJOR                 = 0
MINOR                 = 4
MICRO                 = 2
VERSION               = "%d.%d.%d" % (MAJOR,MINOR,MICRO)

DESCRIPTION           = """
This package provides regular vine modeling, sampling and testing
algorithms. Also some popular bivariate copulas routines which are
optimized for wider range of parameters, high precision and good
performances.
"""
LONG_DESCRIPTION      = """
Regular vine copula provides rich models for dependence structure
modeling. It combines vine structures and families of bivariate
copulas to construct a number of multivariate distributions that can
model a wide range dependence patterns with different tail dependence
for different pairs. Two special cases of regular vine copulas, C-vine
and D-vine copulas, have been deeply investigated.

We propose the Python package, pyvine, for modeling, sampling and
testing a more generalized regular vine copula (R-vine for
short). R-vine modeling algorithm searches for the R-vine structure
which maximizes the vine tree dependence, i.e., the sum of the
absolute values of kendall's tau for paired variables on edges using
PRIM algorithm of minimum-spanning-tree in a sequential way. The
maximum likelihood estimation algorithm takes the sequential
estimation as initial value and uses L-BFGS-B algorithm for the
likelihood value optimization. R-vine sampling algorithm traverses all
the edges of vine structure from the last tree in a recursive way, and
generates the marginal samples on each edge according to some nested
conditions. Goodness-of-fit testing algorithm first generates
Rosenblatt's transformed data E, then tests the composite hypothesis
H_0*: E ~ C* by using Anderson-Darling statistic, where C* is the
independence copula. Bootstrap method will generate the empirical
distribution of Anderson-Darling statistic replications to compute an
adjusted P-value.

The computing of related functions of copulas such as cumulative
distribution functions often meets with the problem of overflow. We
solve this problem by reinvestigating the following six popular
families of bivariate opulas: Normal, Student t, Clayton, Gumbel,
Frank and Joe copulas. Approximations of the above related functions
of copulas are given when the overflow occurs in the computations. All
these are implemented in a subpackage bvcopula of pyvine, in which
subroutines are written in Fortran and wrapped into Python via f2py
and good performance and high precision are both guaranteed.
"""


def configuration(parent_package='',top_path=None):
    from numpy.distutils.misc_util import Configuration
    config = Configuration(NAME,parent_package,top_path)
    config.add_subpackage('bvcopula','bvcopula')
    config.add_data_files('test/FilteredReturn.csv')
    config.add_extension(
        name="mpmle",
        sources=['src/blas.f',
                 'src/lbfgsb.f',
                 'src/timer.f',
                 'src/linpack.f',
                 'src/prob.f90',
                 'src/lmin.f90',
                 'src/ktau.f',
                 'mpmle.f90',                 
                 'mpmle.pyf'],
        libraries=['gomp'],
        )
    return config


if __name__=='__main__':
    
    from numpy.distutils.core import setup
    setup(
        maintainer       = MAINTAINER,
        maintainer_email = MAINTAINER_EMAIL,
        description      = DESCRIPTION,
        long_description = LONG_DESCRIPTION,
        url              = URL,
        download_url     = DOWNLOAD_URL,
        license          = LICENSE,
        platforms        = PLATFORMS,
        version          = VERSION,
        configuration    = configuration
        )
    
