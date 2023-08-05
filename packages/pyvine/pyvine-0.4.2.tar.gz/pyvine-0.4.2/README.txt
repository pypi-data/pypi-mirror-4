PYVINE PACKAGE
==============

pyvine is an python package for regular vine copulas modeling.

MAINTAINER            : Zhenfei Yuan, Taizhong Hu
MAINTAINER_EMAIL      : zfyuan@mail.ustc.edu.cn, thu@ustc.edu.cn
URL                   : taizhonglab.ustc.edu.cn/software/pyvine.html
DOWNLOAD_URL          : taizhonglab.ustc.edu.cn/software/pyvine/pyvine-0.4.2.tar.gz
LICENSE               : GPL-v3
PLATFORMS             : Linux, Windows


1. INTRODUCTION
===============


pyvine is a Python package used for modeling, sampling and testing a
more generalized regular vine copula (R-vine for short). It provides
'Rvine' class with its member functions implementing algorithms as
below.

    [SQE]    sequential estimation of an R-vine object.
    
    [MLE]    maximum likelihood estimation of an R-vine object after SQE.
    
    [SIM]    simulation of an R-vine object after sequential estimation
             after SQE or MLE.
    
    [TEST]   test the hypothesis that H_0 : U ~ C*, U standing for
    	     observations of variable, C* standing for the R-vine
    	     copula after SQE or MLE.
    
    [PLOT]   plot the regular vine structure finded for R-vine object
             after SQE.
    
    [LOGLIK] print the loglikelihood value of R-vine object after SQE or MLE.
    
    [RES]    return the parameters for each edge in pandas dataframe
    	     class after SQE or MLE.  Some parallel techniques are
    	     included into package pyvine via Fortran and fopenmp to
    	     accelerate SQE and MLE since version 0.3.0.

The computing of related functions of copulas such as cumulative
distribution functions often meets with the problem of overflow. We
solve this problem by reinvestigating the following six popular
families of bivariate opulas: Normal, Student t, Clayton, Gumbel,
Frank and Joe copulas. Approximations of the above related functions
of copulas are given when the overflow occurs in the computations. All
these are implemented in a subpackage bvcopula of pyvine, in which
subroutines are written in Fortran and wrapped into Python via f2py
and good performance and high precision are both guaranteed. Functions
for the six bivariate copula are listed below:

        * cumulative distribution function
        * probability density function
    	* simulation function
	* H-function
	* inverse H-function
	* maximum likelihood estimation function


2. DEPENDENCE
=============

pyvine depends on either Python 2.6 or 2.7. The latest version does
not support Python 3.x, however it will come in near future. It also
depends on some other python packages as listed below:

	* scipy & numpy
	* pandas
	* matplotlib
	
		We will say thanks to John D. Hunter (1968-2012), the
		creator of matplotlib. He died from complications
		arising from cancer treatment, after a brief but
		intense battle with this terrible illness. Thanks for
		this excellent library and bless. We remember him.'

	* networkx



3. LICENCE
==========

pyvine follows the GPL-v3 Licence.

	

4. BUILD & INSTALL
==================

For compiling the source code, Fortran compiler is needed. We
recommend the GNU95 fortran compiler. To build and install pyvine to
default directory on your machine, just type the following command (on
windows machine, you probably needs mingw32 installed and replace
"fcompiler=gnu95" with "compiler=mingw32") :

	$ python setup.py config_fc --opt="-fopenmp" build --fcompiler=gnu95
	$ python setup.py install


For the windows users, we provide binary files that can be installed
directly.

Old versions of pyvine package can be download in our homepage:
http://taizhonglab.ustc.edu.cn/software/old_versions.html


5. RELEASE NOTES
================


	(1) Revise docstrings to code files and functions;
	
	(2) Set the optional argument factr of RvineMLE from default
            1e7 to 1e9 for quick result (but low precision);
	
	(3) Rename the function 'ad_test_chisq' to a clear name
 	    'ad_statistic';
	
	(4) Omit the argument 'max_df' of function 'RvineMLE', put
	    these kind of bound limits as local variables of function
	    'RvineMLE'.
	
	(5) Add argument 'filename' to the member function plot for
   	    output the R-vine structure to files.
	
	(6) Change the default value of argument 'N' specifying the
	    resampling size to zero so as to use the same sample size
	    with dataset.
	
	(7) Fix BUG of resampling in function
	    'sample_with_replacement'. Fix BUG in function 'RvineTest'
	    so as to generate the true empirical distribution of
	    bootstrap replications.

