## AUTHOR  : Zhenfei Yuan, Taizhong Hu
## EMAIL   : zfyuan@mail.ustc.edu.cn; thu@ustc.edu.cn
## URL     : taizhonglab.ustc.edu.cn/software/pyvine.html
## DATE    : Jan, 3, 2012
## LICENCE : GPL-v3

__doc__="""
BVCOPULA
========

This module mainly contains routines of probability distribution
functions, density functions, random sample generating functions,
H-functions and Inverse H-functions for six (and it will become more
than ten in the coming version, includes BB1, BB6, BB7, BB8 etc
families) bivariate copulas families. These ten bivariate copula has
been deeply looked into by acamedic fields also own some popularity in
industry fields. The names of these ten copula families are listed
below each with an integer label.

        0 ~ Independent
        1 ~ Normal 
        2 ~ Student t 
        3 ~ Clayton
        4 ~ Gumbel
        5 ~ Frank
        6 ~ Joe
        7 ~ BB1 (coming soon)
        8 ~ BB6 (coming soon)
        9 ~ BB7 (coming soon)
       10 ~ BB8 (coming soon)



This package implementing these common seen bivariate copula here
mainly serves as a toolbox for the package 'pyvine', in which these
bivariate copula play a role of building block to construct regular
vine copulas. We don't think our work for this package is recreate tie
because we focus on the precision, range of parameters and
performances of those routines related to these copula. All these
advantages is attributed to optimized algorithm and approximation when
overflow occurs, which are implemented in fortran and wrapped via
f2py.
"""



__all__ = [
    'bv_cop_mle',
    'bv_cop_cdf',
    'bv_cop_pdf',
    'bv_cop_loglik',
    'bv_cop_sim',
    'bv_cop_hfunc',
    'bv_cop_inv_hfunc',
    'bv_cop_model_selection'
    ]

