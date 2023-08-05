## AUTHOR  : Zhenfei Yuan, Taizhong Hu
## EMAIL   : zfyuan@mail.ustc.edu.cn; thu@ustc.edu.cn
## URL     : taizhonglab.ustc.edu.cn/software/pyvine.html
## DATE    : Dec 3, 2012
## LICENCE : GPL-V3

import numpy  as np
import pyvine as pv
import pandas as ps
import matplotlib.pyplot as plt
import time

## read in data file, and do rank transformation, either 'rankdata' or
## 'dat.rank() / (len(dat)+1)' are OK.

print "Reading dataset 'FilteredReturn.txt'...\n\n"
dat      = ps.read_csv("FilteredReturn.csv",index_col=0,parse_dates=True)
cp_dat   = pv.rankdata(dat)

## display the head of the transformed data
print "Data after rank transform looks like:\n\n"
print cp_dat.head(15).to_string(), "\n\n"


## use regular vine copulas to model the rank transformed
## data. 'structure' is used for specifying the structure, 'r' or 'R'
## for the generalized R-vine, 'd' or 'D' for the D-vine, 'c' or 'C'
## for the C-vine. 'familyset' specifies the bivariate copula families
## that could be chosen for different edges. 'threads_num' specifies
## threads number be used for the synchronous MLE for edges in the
## same vine tree.

edge_family_set = [1,2,3,4,5,6]
rvine_obj       = pv.Rvine(cp_dat)

print "Modeling the data set using D-vine"
rvine_obj.modeling(structure='d',familyset=edge_family_set,threads_num = 4)
rvine_obj.plot()
print "Modeling the data set using C-vine"
rvine_obj.modeling(structure='c',familyset=edge_family_set,threads_num = 4)
rvine_obj.plot()
print "Modeling the data set using R-vine"
tstart = time.time()
rvine_obj.modeling(structure='r',familyset=edge_family_set,threads_num = 4)
tend = time.time()
print "\n\nModeling takes time ", round(tend - tstart,2) , "s with 4 threads"

tstart = time.time()
rvine_obj.modeling(structure='r',familyset=edge_family_set,threads_num = 1)
tend = time.time()
print "Modeling takes time ", round(tend - tstart,2) , "s with 1 threads\n\n"
rvine_obj.plot()


## maximum likelihood estimation of the modeled regular vine. 'max_df'
## specifies the maximum value of degree of freedom for student
## copulas. 'threads_num' specifies how many threads be used for the
## synchronous computing of loglikelihood for edges on the same
## tree. 'factr' sets the precision for the procedure of optimization,
## also the more accury, the more time for the MLE takes, especially
## when the dimension of data set is big. We recommend the factr be
## between 1e7 and 1e12. 'disp' is a bool value that controls the
## displaying some outputs during L-BFGS-B optimization.

print "Maximum Likelihood Estimation for the Regular vine\n"
rvine_obj.mle(threads_num = 4, disp = True)
print "\n\n"



## print the result of the modeling. The method of Rvine class 'res'
## contains the result table in pandas Dataframe type.


rvine_res = rvine_obj.res().to_string()
print rvine_res, "\n\n"


## print the loglikelihood value of SQE and MLE
rvine_obj.loglik()

## testing the hypothesis H_0 : U ~ C using both limiting distribution
## and empirical distribution via parametric bootstrap replications of
## size NB.

rvine_obj.test(bootstrap=True, NB = 100, disp=True)

## sample from the modeled regular vine copulas with size 10000 and
## then model it.
print "Sample from the regular vine copulas..."
sampled_data  = rvine_obj.sim(5000)
sampled_rvine = pv.Rvine(sampled_data)
print "\n\n"

print "Model the sampled dataset"
tstart = time.time()
sampled_rvine.modeling(structure = 'r', familyset=edge_family_set, threads_num = 4)
tend = time.time()
print "sampled data modeling take ", round(tend-tstart,2), " seconds with 4 threads."

tstart = time.time()
sampled_rvine.modeling(structure = 'r', familyset=edge_family_set, threads_num = 1)
tend = time.time()
print "sampled data modeling take ", round(tend-tstart,2), " seconds with 1 threads."


print sampled_rvine.res().to_string(), "\n\n"


print "Plot sampled rvine.."
sampled_rvine.plot()

print "End..."
