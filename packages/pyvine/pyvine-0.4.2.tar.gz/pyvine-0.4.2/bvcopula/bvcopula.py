## AUTHOR  : Zhenfei Yuan, Taizhong Hu
## EMAIL   : zfyuan@mail.ustc.edu.cn; thu@ustc.edu.cn
## URL     : taizhonglab.ustc.edu.cn/software/pyvine.html
## DATE    : Jan, 3, 2012
## LICENCE : GPL-v3


import numpy as np
import bvnorm
import bvt
import bvclayton
import bvgumbel
import bvfrank
import bvjoe



def bv_cop_mle(u1,u2,family):
    """
    Estimate the copula model parameters with specified family.

    Parameter
    ---------

    u1, u2 : array-like

    family : int

        Integer represents the 2-D Copula family. The mapping is below.

        0 ~ Independent
        1 ~ Gaussian
        2 ~ Student's T
        3 ~ Clayton
        4 ~ Gumbel
        5 ~ Frank
        6 ~ Joe
       
    Return
    ------

    x : List containing the mle result and the negative loglikelihood.
    """
    if family == 1:
        return bvnorm.bv_norm_mle(u1,u2)
    elif family == 2:
        return bvt.bv_t_mle(u1,u2)
    elif family == 3:
        return bvclayton.bv_clayton_mle(u1,u2)
    elif family == 4:
        return bvgumbel.bv_gumbel_mle(u1,u2)
    elif family == 5:
        return bvfrank.bv_frank_mle(u1,u2)
    elif family == 6:
        return bvjoe.bv_joe_mle(u1,u2)


def bv_cop_cdf(u1,u2,par,family):
    """
    Cumulative density function with copula family specified.

    Parameter
    ---------

    u1, u2 : array-like

    par : array with length 2.

    family : int

        Integer represents the bivariate Copula family:

        0 ~ Independent
        1 ~ Gaussian
        2 ~ Student's T
        3 ~ Clayton
        4 ~ Gumbel
        5 ~ Frank
        6 ~ Joe

    Return
    ------

    x : array-like.
    """
    if family==1:

        rho = par[0]
        if np.abs(rho) > 1.:
            raise ValueError("In: 'pbv_norm': |rho| > 1.")
        
        return bvnorm.pbv_norm_f( u1 , u2 , rho )
    
    elif family==2:

        rho, nu = par
        if np.abs(rho) > 1.:
            raise ValueError("In 'pbv_t': |rho| > 1.")
        
        if nu < 2.:
            raise ValueError("In 'pbv_t': nu < 2.")
        
        return bvt.pbv_t_f(u1,u2,rho,nu)

    elif family==3:

        delta = par[0]
        if delta < 0.:
            raise ValueError("In 'pbv_clayton': delta <= 0.")
        return bvclayton.pbv_clayton_f(u1,u2,delta)
        
    elif family==4:

        delta = par[0]
        if delta < 1.:
            raise ValueError("In 'pbv_gumbel': delta < 1.")
        return bvgumbel.pbv_gumbel_f(u1,u2,delta)
        
    elif family==5:

        delta = par[0]
        # if delta == 0.0:
        #     raise ValueError("In 'pbv_frank': delta == 0.0")
        return bvfrank.pbv_frank_f(u1,u2,delta)        

    elif family==6:

        delta = par[0]
        if delta < 1.:
            raise ValueError("In 'pbv_joe': delta < 1.")
        return bvjoe.pbv_joe_f(u1,u2,delta)


def bv_cop_pdf(u1,u2,par,family):
    """
    Probability density function with copula family specified.

    Parameter
    ---------

    u1, u2 : array-like

    par : array with length 2.

    family : int

        Integer represents the bivariate Copula family:

        0 ~ Independent
        1 ~ Gaussian
        2 ~ Student's T
        3 ~ Clayton
        4 ~ Gumbel
        5 ~ Frank
        6 ~ Joe

    Return
    ------

    x : array-like.
    """
    if family == 1:

        rho = par[0]
        if np.abs(rho) >= 1.:
            raise ValueError("In 'dbv_norm': |rho| >= 1.")
        return bvnorm.dbv_norm_f(u1,u2,rho)
        
    elif family == 2:

        rho, nu = par
        if np.abs(rho) >= 1.:
            raise ValueError("In dbv_t: |rho| >= 1.")
        if nu < 2.:
            raise ValueError("In dbv_t: nu < 2.")
        return bvt.dbv_t_f(u1,u2,rho,nu)
        
    elif family == 3:

        delta = par[0]
        if delta < 0:
            raise ValueError("In 'dbv_clayton': delta <= 0.")
        return bvclayton.dbv_clayton_f(u1,u2,delta)
        
    elif family == 4:

        delta = par[0]
        if delta < 1.:
            raise ValueError("In 'dbv_gumbel': delta < 1")
        return bvgumbel.dbv_gumbel_f(u1,u2,delta)

    elif family == 5:

        delta = par[0]
        if delta == 0.0:
            raise ValueError("In 'dbv_frank': delta == 0")
        return bvfrank.dbv_frank_f(u1,u2,delta)

    elif family == 6:

        delta = par[0]
        if delta < 1.:
            raise ValueError("In 'dbv_joe': delta < 1.")
        return bvjoe.dbv_joe_f(u1,u2,delta)



def bv_cop_loglik(u1,u2,par,family):
    """
    Log-Likelihood value of specified copula family.

    Parameter
    ---------

    u1, u2 : array-like

    par : array with length 2.    

    family : int

        Integer represents the bivariate Copula family:

        0 ~ Independent
        1 ~ Gaussian
        2 ~ Student's T
        3 ~ Clayton
        4 ~ Gumbel
        5 ~ Frank
        6 ~ Joe

    Return
    ------

    x : float.
    """
    if family == 1:

        rho = par[0]
        if np.abs(rho)>= 1.:
            raise ValueError("In 'bv_norm_loglik': |rho| >= 1.")
        return bvnorm.bv_norm_loglik_f(u1,u2,rho)

    elif family == 2:

        rho, nu = par
        if np.abs(rho) >= 1.:
            raise ValueError("In 'bv_t_loglik': |rho| >= 1")
        if nu < 2.:
            raise ValueError("In 'bv_t_loglik': nu < 2.")
        return bvt.bv_t_loglik_f(u1,u2,rho,nu)
        
    elif family == 3:

        delta = par[0]
        if delta < 0.:
            raise ValueError("In 'bv_clayton_loglik': theta < 0.")
        return bvclayton.bv_clayton_loglik_f(u1,u2,delta)

    elif family == 4:

        delta = par[0]
        if delta < 0.:
            raise ValueError("In 'bv_clayton_loglik': theta < 0.")
        return bvgumbel.bv_gumbel_loglik_f(u1,u2,delta)

    elif family == 5:

        delta = par[0]
        if delta == 0.:
            raise ValueError("In 'bv_frank_loglik': theta == 0.")
        return bvfrank.bv_frank_loglik_f(u1,u2,delta)

    elif family == 6:

        delta = par[0]
        if delta < 1.:
            raise ValueError("In 'bv_joe_loglik': delta < 1.")
        return bvjoe.bv_joe_loglik_f(u1,u2,delta)
    


def bv_cop_sim(par,family,size=1):
    """
    Sampling function with copula family specified.

    Parameter
    ---------

    par : array with length 2.    

    family : int

        Integer represents the bivariate Copula family:

        0 ~ Independent
        1 ~ Gaussian
        2 ~ Student's T
        3 ~ Clayton
        4 ~ Gumbel
        5 ~ Frank
        6 ~ Joe

    size : int, optional. Sample size. Default value is '1'.

    Return
    ------

    x : array-like with shape (size,2).
    """
    if family == 1:

        rho = par[0]
        if np.abs( rho ) > 1.:
            raise ValueError("In 'rbv_norm': |rho| > 1.")
        u1, u2 = bvnorm.rbv_norm_f( rho , size )
        return np.array([u1,u2]).transpose()

    elif family == 2:

        rho, nu = par
        if np.abs(rho) > 1.:
            raise ValueError("In 'rbv_t': |rho| > 1.")
        if nu < 2.:
            raise ValueError("In 'rbv_t': nu < 2.")

        rho, nu = par
        if rho == 1.:
            u1 = np.random.rand(size)
            u2 = u1
            return np.array([u1,u2]).transpose()
        if rho == -1.:
            u1 = np.random.rand(size)
            u2 = 1.-u1
            return np.array([u1,u2]).transpose()
        u1,u2 = bvt.rbv_t_f(rho,nu,size)
        return np.array([u1,u2]).transpose()
        

    elif family == 3:

        delta = par[0]
        if delta < 0:
            raise ValueError("In 'rbv_clayton': theta <= 0.")
        if delta == 0.:
            return np.random.rand(size,2)
        u1,u2 = bvclayton.rbv_clayton_f(delta,size)
        return np.array([u1,u2]).transpose()

    elif family == 4:

        delta = par[0]
        if delta < 1.:
            raise ValueError("In 'rbv_gumbel': delta < 1.")
        if delta == 1.:
            res = np.random.rand(size,2)
            return res
        u1, u2 = bvgumbel.rbv_gumbel_f(delta,size)
        return np.array([u1,u2]).transpose()
        
    elif family == 5:

        delta = par[0]
        if delta == 0.:
            return np.random.rand(size,2)
        u1, u2 = bvfrank.rbv_frank_f(delta,size)
        return np.array([u1,u2]).transpose()
        

    elif family == 6:

        delta = par[0]
        if delta < 1.:
            raise ValueError("In 'rbv_joe': delta < 1.")
        u1,u2 = bvjoe.rbv_joe_f(delta,size)
        return np.array([u1,u2]).transpose()
        

def bv_cop_hfunc(u1,u2,par,family):
    """
    H-function for Copulas with specified family. The definition of
    H-func is the partial derivative of C(u1,u2,par) with respect to
    'u2', for more details, see [1].

    Parameter
    ---------

    u1, u2 : array-like.

    par : array with length 2.        

    family : int.

        Integer represents the bivariate copula family:

        0 ~ Independent
        1 ~ Gaussian
        2 ~ Student's T
        3 ~ Clayton
        4 ~ Gumbel
        5 ~ Frank
        6 ~ Joe

    Return
    ------

    x : array-like.

    Reference
    ---------

    [1] K. Aas, C. Czado, A. Frigessi, H. Bakken. Pair-copula
    constructions of multiple dependence. Insurance: Mathematics and
    Economics. 2009.
    """
    if family == 1:

        rho = par[0]
        if np.abs(rho) > 1.:
            raise ValueError("In 'bv_norm_hfunc': |rho| > 1.")
        return bvnorm.bv_norm_hfunc_f(u1,u2,rho)
        
    elif family == 2:

        rho, nu = par
        if np.abs(rho) > 1.:
            raise ValueError("In 'bv_t_hfunc': |rho| > 1.")
        if nu < 2.:
            raise ValueError("In 'bv_t_hfunc': nu < 2.")
        return bvt.bv_t_hfunc_f(u1,u2,rho,nu)

    elif family == 3:

        delta = par[0]
        if delta < 0.:
            raise ValueError("In 'bv_clayton_hfunc': delta < 0.")
        return bvclayton.bv_clayton_hfunc_f(u1,u2,delta)

    elif family == 4:

        delta = par[0]
        if delta < 1.:
            raise ValueError("In 'bv_gumbel_hfunc': delta < 1.")
        return bvgumbel.bv_gumbel_hfunc_f(u1,u2,delta)

    elif family == 5:

        delta = par[0]
        return bvfrank.bv_frank_hfunc_f(u1,u2,delta)        

    elif family == 6:

        delta = par[0]
        if delta < 1.:
            raise ValueError("In 'bv_joe_hfunc': delta < 1.")
        return bvjoe.bv_joe_hfunc_f(u1,u2,delta)

    
def bv_cop_inv_hfunc(u1,u2,par,family):
    """
    Inverse of H-function for specified copula family.

    Parameter
    ---------

    u1, u2 : array-like.

    par : array with length 2.

    family : int.

        Integer represents the bivariate copula family:

        0 ~ Independent
        1 ~ Gaussian
        2 ~ Student's T
        3 ~ Clayton
        4 ~ Gumbel
        5 ~ Frank
        6 ~ Joe

    Return
    ------

    x : array-like.

    Reference
    ---------

    [1] K. Aas, C. Czado, A. Frigessi, H. Bakken. Pair-copula
    constructions of multiple dependence. Insurance: Mathematics and
    Economics. 2009.
    """
    if family == 1:

        rho = par[0]
        if np.abs(rho) > 1.:
            raise ValueError("In 'bv_norm_inv_hfunc': |rho| > 1.")
        return bvnorm.bv_norm_inv_hfunc_f(u1,u2,rho)

    elif family == 2:

        rho, nu = par
        if np.abs(rho) > 1.:
            raise ValueError("In 'bv_t_inv_hfunc': |rho| > 1.")
        if nu < 2.:
            raise ValueError("In 'bv_t_inv_hfunc': nu < 2.")
        return bvt.bv_t_inv_hfunc_f(u1,u2,rho,nu)
        
    elif family == 3:

        delta = par[0]

        if delta < 0.:
            raise ValueError("In 'bv_clayton_inv_hfunc': delta < 0.")
        return bvclayton.bv_clayton_inv_hfunc_f(u1,u2,delta)

    elif family == 4:

        delta = par[0]

        if delta < 1.:
            raise ValueError("In 'bv_gumbel_inv_hfunc': delta < 1.")
        return bvgumbel.bv_gumbel_inv_hfunc_f(u1,u2,delta)
        
    elif family == 5:

        delta = par[0]

        if delta == 0.0:
            raise ValueError("In 'bv_frank_inv_hfunc:' delta == 0")
        return bvfrank.bv_frank_inv_hfunc_f(u1,u2,delta)        

    elif family == 6:

        delta = par[0]

        if delta < 1.:
            raise ValueError("In 'bv_joe_inv_hfunc': delta < 1.")
        return bvjoe.bv_joe_inv_hfunc_f(u1,u2,delta)

    

def bv_cop_model_selection(u1,u2,familyset=[1,2,3,4,5,6]):
    """
    Bivariate copulas model selection for given data set with shape
    Nx2.

    AIC is used to choose the better model. AIC provieds a means for
    model selection, and does not provide a test of a model, i.e. AIC
    can tell nothing about how well a model fits the data in an
    absolute sense.

    Parameter
    ---------
    u1,u2 : array-like

    Return
    ------
    x : list
    
        The first element of return x is the number representing for
        the family, while the second element is the parameter
        estimation for the dataset with family specified.
    """
    aic_lst = []

    par_lst = []

    for fml in familyset:

        par, loglik = bv_cop_mle(u1,u2,fml)
        par_lst.append(par)

        if fml == 2:
            aic_lst.append( -2 * loglik + 4.)
        else:
            aic_lst.append( -2 * loglik + 2.)

    pos = 0
    for i in range(len(aic_lst)):
        if aic_lst[i] < aic_lst[pos]:
            pos = i
        
    res=(familyset[pos],par_lst[pos])
    
    return res
    
