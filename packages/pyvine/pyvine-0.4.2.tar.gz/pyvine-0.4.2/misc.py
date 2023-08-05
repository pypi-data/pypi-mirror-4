## AUTHOR  : Taizhong Hu, Zhenfei Yuan
## EMAIL   : zfyuan@mail.ustc.edu.cn; thu@ustc.edu.cn
## URL     : taizhonglab.ustc.edu.cn/software/pyvine.html
## DATE    : Jan, 3, 2012
## LICENCE : GPL-v3

## This file is devoted for some miscellaneous and auxiliary
## functions.


import pandas

def rankdata(data):
    """
    The input data variable may be some kind of raw data before rank
    transformation, for example the daily-return dataset of several
    financial assets. This function apply the rank transformation to
    each column (axis=0) of the raw data to get just what copula
    modeling and hypothesis work needs. The rank transformation method
    for abtaining the dataset with U(0,1) margins is prefered by
    C. Genest, see [1], while Joe prefers his 'Inference Functions for
    Margins' (IFM) method, see [2].

    Parameters
    ----------
    
    data : pandas DataFrame or Series type. Data before rank transformation for each column.

    Return
    -------
    x : pandas DataFrame or Series.
    """
    return data.dropna().rank()/(len(data)+1)



