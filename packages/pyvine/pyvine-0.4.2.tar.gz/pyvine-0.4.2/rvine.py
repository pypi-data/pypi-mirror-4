## AUTHOR  : Zhenfei Yuan, Taizhong Hu
## EMAIL   : zfyuan@mail.ustc.edu.cn; thu@ustc.edu.cn
## URL     : taizhonglab.ustc.edu.cn/software/pyvine.html
## DATE    : Jan, 3, 2012
## LICENCE : GPL-v3


import pandas
import numpy             as np
import networkx          as nx
import matplotlib.pyplot as plt
import bvcopula          as bvcop
from scipy.optimize import fmin_l_bfgs_b as fmin
from scipy.stats    import norm,chi2
from itertools      import combinations
from mpmle          import multi_process_mle
from mpmle          import multi_process_loglik
from mpmle          import ad_stat, adinf, kendalltau




def gen_node(a,b):
    """
    Generate one node name in next regular vine tree by two neighbor
    nodes named 'a' and 'b' in current tree.

    Parameter
    ---------

    a, b : string. The format of 'a' and 'b' follows Bedford and Cook
           2001,2002 composed by conditioned set and conditioning set
           seperated by '|'.

    Return
    ------

    x : string. The generated node name for the next regular vine
        tree.

    """
    set_a = set(a.replace('|',''))-set(',')
    set_b = set(b.replace('|',''))-set(',')
    
    conditioning_set = set.intersection(set_a,set_b)
    conditioned_set = set.union(set_a,set_b)-conditioning_set
    
    conditioning_lst = list(conditioning_set)
    conditioned_lst = list(conditioned_set)
    
    conditioning_lst.sort()
    conditioned_lst.sort()
    
    if conditioning_lst:
        return ','.join(conditioned_lst)+ \
            '|'+','.join(conditioning_lst)
    else:
        return ','.join(conditioned_lst)


def model_next_tree(current_tree,familyset,threads_num = 1):
    """
    Function for generating and modeling the next tree given current
    tree.

    Parameter
    ---------

    current_tree : vine tree with class networkx.Graph() like.

    familyset : list of integers. familyset provides a set of
                bivariate copula families for edges of vine trees to
                choose from. Available families are listed below.

        1 : Normal copula
        2 : t copula
        3 : Clayton copula
        4 : Gumbel copula
        5 : Frank copula
        6 : Joe copula

    threads_num : int. The number of threads using for simultaneously
                  mle on edges of vine tree. Real cpu core number will
                  be used if threads_num is larger. Default is 1.
        

    Return
    ------

    x : a tuple of two networkx.Graph() elements. The next graph and
        the next tree of regular vine generated from current tree.
    """
    # create next graph
    next_graph = nx.Graph()

    def gen_edge(neighbor_nodes_pair,node):
        old_n0,old_n1 = neighbor_nodes_pair

        ## n0 and n1 are two new nodes of next graph
        n0 = gen_node(old_n0,node)
        n1 = gen_node(old_n1,node)
        next_graph.add_edge(n0,n1)

        ## figure out a new edge data via H-function

        ## the edge data with label n0
        edge_data = {}
        v1 = current_tree[old_n0][node]['edge_data'][old_n0]
        v2 = current_tree[old_n0][node]['edge_data'][node]
        edge_par = current_tree[old_n0][node]['par']
        edge_family = current_tree[old_n0][node]['family']
        edge_data[n0] = bvcop.bv_cop_hfunc(
            v1,
            v2,
            edge_par,            
            edge_family
            )

        ## the edge data with label n1
        v1 = current_tree[old_n1][node]['edge_data'][old_n1]
        v2 = current_tree[old_n1][node]['edge_data'][node]
        edge_par = current_tree[old_n1][node]['par']
        edge_family = current_tree[old_n1][node]['family']
        edge_data[n1] = bvcop.bv_cop_hfunc(
            v1,
            v2,
            edge_par,
            edge_family
            )

        ## compute kendall tau and weight = 1 - |tau| for the new edge
        next_graph[n0][n1]['edge_data' ] = edge_data
        ktau = kendalltau(edge_data[n0],edge_data[n1])        
        next_graph[n0][n1]['kendalltau'] = ktau
        next_graph[n0][n1]['weight'    ] = 1-np.abs(ktau)
        next_graph[n0][n1]['one_fold'  ] = [old_n0,old_n1,node]
        return

    for node in current_tree.nodes():
        neighbor_list = current_tree.neighbors(node)
        if len(neighbor_list) >= 2:

            ## first generate all of the 2-combination of neighbor
            ## nodes of the current node
            neighbor_nodes_comb = combinations(neighbor_list,2)

            ## then for each element of the 2-combination (n0,n1),
            ## generate the new edge (n0|node,n1|node) for the next
            ## graph
            for neighbor_nodes_pair in neighbor_nodes_comb:
                gen_edge(neighbor_nodes_pair,node)

    ## after generate all the possible new edges for the next graph,
    ## we use prim algorithm to generate the next tree with maximum
    ## summation of weight
    next_tree = nx.minimum_spanning_tree(next_graph)

    ##  parallel mle for every edge of next_tree via realization of
    ##  fortran and openmp. 

    ## collect edge data into a matrix named paired_data.
    paired_data = []
    
    for edge in next_tree.edges():
        n0,n1 = edge
        v0 = next_tree[n0][n1]['edge_data'][n0]
        v1 = next_tree[n0][n1]['edge_data'][n1]
        paired_data.append( np.array([v0,v1]).transpose() )
        
    paired_data = np.concatenate(paired_data,1)

    ## parallel mle for the (2i-1,2i) column of the paired_data
    par_mat,fml_vec,ll_vec = \
        multi_process_mle(paired_data,
                          familyset,
                          len(next_tree.edges()),
                          threads_num)

    ## return the result back to next_tree
    pnum = 0
    for edge in next_tree.edges():
        n0,n1 = edge
        next_tree[n0][n1]['par'] = par_mat[:,pnum]
        next_tree[n0][n1]['family'] = fml_vec[pnum]
        next_tree[n0][n1]['loglik'] = ll_vec[pnum]        
        pnum += 1
        
    return next_tree,next_graph


def RvineModeling(rvine,familyset = [1,2,3,4,5,6], threads_num = 1):
    """
    Fit the Regular vine model to data. This function is called by the
    Rvine class member function 'modeling', and generate vine trees
    for the Rvine object.

    Parameter
    ---------

    rvine : RVine Class object.

    familyset : list of integers. familyset provides a set of
                bivariate copula families for edges of vine trees to
                choose from. Available families are listed below.
    
        1 : Normal copula
        2 : t copula
        3 : Clayton copula
        4 : Gumbel copula
        5 : Frank copula
        6 : Joe copula

    threads_num : int. The number of threads using for simultaneously
                  mle on edges of vine tree. Real cpu core number will
                  be used if threads_num is larger. Default is 1.

    """
    copula_data = rvine.copula_data
    var_num = rvine.var_num

    ## initialization of the rvine structure via tree_list
    tree_list  = []
    graph_list = []

    ## initialization of the first tree
    current_graph = nx.Graph()

    ## generate the 2-combinations of all nodes of the first tree.
    node_list = [str(i) for i in range(1,var_num+1)]
    paired_nodes = combinations(node_list,2)
    
    for e in paired_nodes:
        current_graph.add_edge(*e)

    ## distribute data pairs onto edges of the first tree, compute tau
    ## and weights for each edge
    for edge in current_graph.edges():
        n0,n1 = edge    
        edge_data = {n0:copula_data[n0],n1:copula_data[n1]}
        
        current_graph[n0][n1]['edge_data' ] = edge_data
        ktau = kendalltau(edge_data[n0],edge_data[n1]) 
        current_graph[n0][n1]['kendalltau'] = ktau
        current_graph[n0][n1]['weight'    ] = 1-np.abs(ktau)
        
    graph_list.append(current_graph)
    current_tree = nx.minimum_spanning_tree(current_graph)

    ##  parallel mle of every edge of next_tree via realization of
    ##  fortran and openmp.

    ## collect data for mle into a matrix named paired_data 
    paired_data = []
    
    for edge in current_tree.edges():
        n0,n1 = edge
        v0 = current_tree[n0][n1]['edge_data'][n0]
        v1 = current_tree[n0][n1]['edge_data'][n1]
        paired_data.append( np.array([v0,v1]).transpose() )

    paired_data = np.concatenate(paired_data,1)

    ## parallel mle
    par_mat,fml_vec,ll_vec = \
        multi_process_mle(paired_data,
                          familyset,
                          len(current_tree.edges()),
                          threads_num
                          )
    ## return the result of mle back to the first tree
    pnum = 0
    for edge in current_tree.edges():
        n0,n1 = edge
        current_tree[n0][n1]['par'] = par_mat[:,pnum]
        current_tree[n0][n1]['family'] = fml_vec[pnum]
        current_tree[n0][n1]['loglik'] = ll_vec[pnum]
        pnum +=  1

    tree_list.append(current_tree)
    
    while( len(current_tree.nodes()) >= 3 ):
        next_tree,next_graph = model_next_tree(current_tree,
                                               familyset,
                                               threads_num)
        tree_list.append(  next_tree  )
        graph_list.append( next_graph )
        current_tree = next_tree
        
    # when MLE carries, all the values in 'par' will be covered, hence
    # a new key for storing sequential estimation result is created
    # and named 'par_sqe'. Same as attribute 'loglik'.
    for tree in tree_list:
        for edge in tree.edges():
            n0,n1 = edge
            tree[n0][n1]['par_sqe'   ] = tree[n0][n1]['par']
            tree[n0][n1]['loglik_seq'] = tree[n0][n1]['loglik']
            
    ## compute for the loglikelihood value of the whole regular vine
    init_loglik = 0
    for tree in tree_list:
        for edge in tree.edges():
            n0,n1 = edge
            edge_info = tree[n0][n1]
            init_loglik += edge_info['loglik_seq']

    rvine.tree_list  = tree_list
    rvine.graph_list = graph_list
    rvine.sqe_ll     = init_loglik
    return



def cvine_model_next_tree(current_tree,familyset,threads_num = 1):
    """
    Function for generating and modeling the next tree given current
    tree for C-vine.

    Parameter
    ---------

    current_tree : vine tree with class networkx.Graph() like.

    familyset : list of integers. familyset provides a set of
                bivariate copula families for edges of vine trees to
                choose from. Available families are listed below.

        1 : Normal copula
        2 : t copula
        3 : Clayton copula
        4 : Gumbel copula
        5 : Frank copula
        6 : Joe copula

    threads_num : int. The number of threads using for simultaneously
                  mle on edges of vine tree. Real cpu core number will
                  be used if threads_num is larger. Default is 1.
        

    Return
    ------

    x : a tuple of two networkx.Graph() elements. The next graph and
        the next tree of C-vine generated from current tree.
    """
    # create an empty graph for next graph
    next_graph = nx.Graph()

    def gen_edge(neighbor_nodes_pair,node):
        old_n0,old_n1 = neighbor_nodes_pair

        ## n0 and n1 are two new nodes of next graph
        n0 = gen_node(old_n0,node)
        n1 = gen_node(old_n1,node)
        next_graph.add_edge(n0,n1)

        
        ## figure out edge data of the new edge of next graph

        ## the edge data with label n0
        edge_data = {}
        v1 = current_tree[old_n0][node]['edge_data'][old_n0]
        v2 = current_tree[old_n0][node]['edge_data'][node]
        edge_par      = current_tree[old_n0][node]['par'   ]
        edge_family   = current_tree[old_n0][node]['family']
        edge_data[n0] = bvcop.bv_cop_hfunc(
            v1,
            v2,
            edge_par,            
            edge_family
            )

        ## the edge data with label n1
        v1 = current_tree[old_n1][node]['edge_data'][old_n1]
        v2 = current_tree[old_n1][node]['edge_data'][node]
        edge_par      = current_tree[old_n1][node]['par'   ]
        edge_family   = current_tree[old_n1][node]['family']
        edge_data[n1] = bvcop.bv_cop_hfunc(
            v1,
            v2,
            edge_par,
            edge_family
            )

        ## compute kendall tau and weight = 1 - |tau| for the new edge
        next_graph[n0][n1]['edge_data' ] = edge_data
        ktau = kendalltau(edge_data[n0],edge_data[n1])
        next_graph[n0][n1]['kendalltau'] = ktau
        next_graph[n0][n1]['weight'    ] = 1-np.abs(ktau)
        next_graph[n0][n1]['one_fold'  ] = [old_n0,old_n1,node]
        return

    for node in current_tree.nodes():
        
        neighbor_list = current_tree.neighbors(node)
        if len(neighbor_list) >= 2:

            ## first generate all of the 2-combination of neighbor
            ## nodes of the current node
            neighbor_nodes_comb = combinations(neighbor_list,2)

            ## then for each element of the 2-combination (n0,n1),
            ## generate the new edge (n0|node,n1|node) for the next
            ## graph
            for neighbor_nodes_pair in neighbor_nodes_comb:
                gen_edge(neighbor_nodes_pair,node)

    next_tree = next_graph.copy()

    ## node_weight_sum is a dictionary that contains the weight
    ## summation of every node of the first graph.
    node_weight_sum = {}
    
    for node in next_tree.nodes():
        neighbor_list = next_tree.neighbors(node)
        w_sum = 0
        
        for neighbor_node in neighbor_list:
            w_sum += next_tree[node][neighbor_node]['weight']

        node_weight_sum[node] = w_sum

    ## pick up the node with the highest summation of weights to be
    ## the star node, and delete edges to modify the graph into a star
    ## tree
    star_node = max(node_weight_sum,key=node_weight_sum.get)
    star_node_neighbors = next_tree.neighbors(star_node)
    paired_nodes = combinations(star_node_neighbors,2)

    for e in paired_nodes:
        next_tree.remove_edge(*e)
    
    ##  parallel mle for every edge of next_tree via realization of
    ##  fortran and openmp. 

    ## collect edge data into a matrix named paired_data
    paired_data = []
    
    for edge in next_tree.edges():
        n0,n1 = edge
        v0 = next_tree[n0][n1]['edge_data'][n0]
        v1 = next_tree[n0][n1]['edge_data'][n1]
        paired_data.append( np.array([v0,v1]).transpose() )
        
    paired_data = np.concatenate(paired_data,1)

    ## parallel mle for the (2i-1,2i) column of the paired_data
    par_mat,fml_vec,ll_vec = \
        multi_process_mle(paired_data,
                          familyset,
                          len(next_tree.edges()),
                          threads_num)

    ## return the result back to next_tree
    pnum = 0
    for edge in next_tree.edges():
        n0,n1 = edge
        next_tree[n0][n1]['par'   ] = par_mat[:,pnum]
        next_tree[n0][n1]['family'] = fml_vec[pnum]
        next_tree[n0][n1]['loglik'] = ll_vec[pnum]        
        pnum += 1
        
    return next_tree,next_graph



def CvineModeling(rvine,familyset=[1,2,3,4,5,6],threads_num = 1):
    """
    C-Vine modeling function.  C-Vine is a special structure of
    regular vine, with each tree having a star like structure. The
    star nodes of each tree is chosen as the most influential,
    i.e. having the highest summation of absolute value of kendall tau
    with its neighbors.

    Parameter
    ---------

    rvine : RVine Class object.

    familyset : list of integers. familyset provides a set of
                bivariate copula families for edges of vine trees to
                choose from. Available families are listed below.

        1 : Normal copula
        2 : t copula
        3 : Clayton copula
        4 : Gumbel copula
        5 : Frank copula
        6 : Joe copula

    threads_num : int. The number of threads using for simultaneously
                  mle on edges of vine tree. Real cpu core number will
                  be used if threads_num is larger. Default is 1.
    """
    copula_data = rvine.copula_data
    var_num = rvine.var_num

    ## initialization of the rvine structure via tree_list
    tree_list  = []
    graph_list = []

    ## initialization of the first tree
    current_graph = nx.Graph()

    ## generate the 2-combinations of all nodes of the first tree.
    node_list = [str(i) for i in range(1,var_num+1)]
    paired_nodes = combinations(node_list,2)
    
    for e in paired_nodes:
        current_graph.add_edge(*e)
        
    for edge in current_graph.edges():
        n0,n1 = edge    
        edge_data = {n0:copula_data[n0],n1:copula_data[n1]}
        
        current_graph[n0][n1]['edge_data' ] = edge_data
        ktau = kendalltau(edge_data[n0],edge_data[n1])
        current_graph[n0][n1]['kendalltau'] = ktau
        current_graph[n0][n1]['weight'    ] = 1-np.abs(ktau)

    graph_list.append(current_graph)
    current_tree = current_graph.copy()

    ## node_weight_sum is a dictionary that contains the weight
    ## summation of every node of the first graph.
    node_weight_sum = {}
    
    for node in current_tree.nodes():
        neighbor_list = current_tree.neighbors(node)
        w_sum = 0
        
        for neighbor_node in neighbor_list:
            w_sum += current_tree[node][neighbor_node]['weight']

        node_weight_sum[node] = w_sum

    ## pick up the node with the highest summation of weights to be
    ## the star node, and delete edges to modify the graph into a star
    ## tree
    star_node = max(node_weight_sum,key=node_weight_sum.get)
    star_node_neighbors = current_tree.neighbors(star_node)
    paired_nodes = combinations(star_node_neighbors,2)

    for e in paired_nodes:
        current_tree.remove_edge(*e)

    ##  parallel mle of every edge of next_tree via realization of
    ##  fortran and openmp.

    ## collect data for mle into a matrix named paired_data 
    paired_data = []
    
    for edge in current_tree.edges():
        n0,n1 = edge
        v0 = current_tree[n0][n1]['edge_data'][n0]
        v1 = current_tree[n0][n1]['edge_data'][n1]
        paired_data.append( np.array([v0,v1]).transpose() )

    paired_data = np.concatenate(paired_data,1)

    ## parallel mle
    par_mat,fml_vec,ll_vec = \
        multi_process_mle(paired_data,
                          familyset,
                          len(current_tree.edges()),
                          threads_num
                          )
    ## return the result of mle back to the first tree
    pnum = 0
    for edge in current_tree.edges():
        n0,n1 = edge
        current_tree[n0][n1]['par'   ] = par_mat[:,pnum]
        current_tree[n0][n1]['family'] = fml_vec[pnum]
        current_tree[n0][n1]['loglik'] = ll_vec[pnum]
        pnum +=  1

    tree_list.append(current_tree)
            
        
    while( len(current_tree.nodes()) >= 3 ):
        next_tree,next_graph = \
            cvine_model_next_tree(current_tree,
                                  familyset,
                                  threads_num
                                  )
        tree_list.append(next_tree)
        graph_list.append(next_graph)
        current_tree = next_tree
        
    # when MLE carries, all the values in 'par' will be covered, hence
    # a new key for storing sequential estimation result is created
    # and named 'par_sqe'. Same as attribute 'loglik'.
    for tree in tree_list:
        for edge in tree.edges():
            n0,n1 = edge
            tree[n0][n1]['par_sqe'   ] = tree[n0][n1]['par'   ]
            tree[n0][n1]['loglik_seq'] = tree[n0][n1]['loglik']
            
    ## compute for the loglikelihood value of the whole regular vine
    init_loglik = 0
    for tree in tree_list:
        for edge in tree.edges():
            n0,n1 = edge
            edge_info = tree[n0][n1]
            init_loglik += edge_info['loglik_seq']


    rvine.tree_list  = tree_list
    rvine.graph_list = graph_list
    rvine.sqe_ll     = init_loglik
    return


def dvine_model_next_tree(current_tree,familyset,threads_num = 1):
    """
    Function for generating and modeling the next tree given current
    tree for D-vine.

    Parameter
    ---------

    current_tree : vine tree with class networkx.Graph() like.

    familyset : list of integers. familyset provides a set of
                bivariate copula families for edges of vine trees to
                choose from. Available families are listed below.

        1 : Normal copula
        2 : t copula
        3 : Clayton copula
        4 : Gumbel copula
        5 : Frank copula
        6 : Joe copula

    threads_num : int. The number of threads using for simultaneously
                  mle on edges of vine tree. Real cpu core number will
                  be used if threads_num is larger. Default is 1.
        

    Return
    ------

    x : a tuple of two networkx.Graph() elements. The next graph and
        the next tree of C-vine generated from current tree.
    """
    # create an empty graph for next graph
    next_graph = nx.Graph()

    def gen_edge(neighbor_nodes_pair,node):
        old_n0,old_n1 = neighbor_nodes_pair

        ## n0 and n1 are two new nodes of next graph
        n0 = gen_node(old_n0,node)
        n1 = gen_node(old_n1,node)
        next_graph.add_edge(n0,n1)

        ## figure out edge data of the new edge of next graph

        ## the edge data with label n0
        edge_data = {}
        v1 = current_tree[old_n0][node]['edge_data'][old_n0]
        v2 = current_tree[old_n0][node]['edge_data'][node]
        edge_par = current_tree[old_n0][node]['par']
        edge_family = current_tree[old_n0][node]['family']
        edge_data[n0] = bvcop.bv_cop_hfunc(
            v1,
            v2,
            edge_par,            
            edge_family
            )

        ## the edge data with label n1
        v1 = current_tree[old_n1][node]['edge_data'][old_n1]
        v2 = current_tree[old_n1][node]['edge_data'][node]
        edge_par = current_tree[old_n1][node]['par']
        edge_family = current_tree[old_n1][node]['family']
        edge_data[n1] = bvcop.bv_cop_hfunc(
            v1,
            v2,
            edge_par,
            edge_family
            )

        ## compute kendall tau and weight = 1 - |tau| for the new edge
        next_graph[n0][n1]['edge_data' ] = edge_data
        ktau = kendalltau(edge_data[n0],edge_data[n1])
        next_graph[n0][n1]['kendalltau'] = ktau
        next_graph[n0][n1]['weight'    ] = 1-np.abs(ktau)
        next_graph[n0][n1]['one_fold'  ] = [old_n0,old_n1,node]
        return

    for node in current_tree.nodes():
        
        neighbor_list = current_tree.neighbors(node)
        if len(neighbor_list) >= 2:

            ## first generate all of the 2-combination of neighbor
            ## nodes of the current node
            neighbor_nodes_comb = combinations(neighbor_list,2)

            ## then for each element of the 2-combination (n0,n1),
            ## generate the new edge (n0|node,n1|node) for the next
            ## graph
            for neighbor_nodes_pair in neighbor_nodes_comb:
                gen_edge(neighbor_nodes_pair,node)


    next_tree = next_graph.copy()

    ##  parallel mle for every edge of next_tree via realization of
    ##  fortran and openmp. 

    ## collect edge data into a matrix named paired_data
    paired_data = []
    
    for edge in next_tree.edges():
        n0,n1 = edge
        v0 = next_tree[n0][n1]['edge_data'][n0]
        v1 = next_tree[n0][n1]['edge_data'][n1]
        paired_data.append( np.array([v0,v1]).transpose() )
        
    paired_data = np.concatenate(paired_data,1)

    ## parallel mle for the (2i-1,2i) column of the paired_data
    par_mat,fml_vec,ll_vec = \
        multi_process_mle(paired_data,
                          familyset,
                          len(next_tree.edges()),
                          threads_num)

    ## return the result back to next_tree
    pnum = 0
    for edge in next_tree.edges():
        n0,n1 = edge
        next_tree[n0][n1]['par'   ] = par_mat[:,pnum]
        next_tree[n0][n1]['family'] = fml_vec[pnum]
        next_tree[n0][n1]['loglik'] = ll_vec[pnum]        
        pnum += 1
        
    return next_tree,next_graph


def DvineModeling(rvine,familyset=[1,2,3,4,5,6],threads_num = 1):
    """
    D-Vine modeling function.  D-Vine is a special structure of
    regular vine, with each tree having a linear structure. Nodes in
    first tree should be ordered manually.

    Parameter
    ---------

    rvine : RVine Class object.

    familyset : list of integers. familyset provides a set of
                bivariate copula families for edges of vine trees to
                choose from. Available families are listed below.

        1 : Normal copula
        2 : t copula
        3 : Clayton copula
        4 : Gumbel copula
        5 : Frank copula
        6 : Joe copula

    threads_num : int. The number of threads using for simultaneously
                  mle on edges of vine tree. Real cpu core number will
                  be used if threads_num is larger. Default is 1.
    
    """
    copula_data = rvine.copula_data
    var_num = rvine.var_num

    ## initialization of the rvine structure via tree_list
    tree_list  = []
    graph_list = []

    ## initialization of the first tree
    current_graph = nx.Graph()

    ## generate the 2-combinations of all nodes of the first tree.
    node_list = [str(i) for i in range(1,var_num+1)]

    for i in range(1,var_num):
        current_graph.add_edge(str(i),str(i+1))
        
    for edge in current_graph.edges():
        n0, n1 = edge    
        edge_data = {n0:copula_data[n0],n1:copula_data[n1]}
        
        current_graph[n0][n1]['edge_data' ] = edge_data
        ktau = kendalltau(edge_data[n0],edge_data[n1])            
        current_graph[n0][n1]['kendalltau'] = ktau
        current_graph[n0][n1]['weight'    ] = 1-np.abs(ktau)

    graph_list.append(current_graph)
    current_tree = current_graph.copy()

    ##  parallel mle of every edge of next_tree via realization of
    ##  fortran and openmp.

    ## collect data for mle into a matrix named paired_data 
    paired_data = []
    
    for edge in current_tree.edges():
        n0,n1 = edge
        v0 = current_tree[n0][n1]['edge_data'][n0]
        v1 = current_tree[n0][n1]['edge_data'][n1]
        paired_data.append( np.array([v0,v1]).transpose() )

    paired_data = np.concatenate(paired_data,1)

    ## parallel mle
    par_mat,fml_vec,ll_vec = \
        multi_process_mle(paired_data,
                          familyset,
                          len(current_tree.edges()),
                          threads_num
                          )
    ## return the result of mle back to the first tree
    pnum = 0
    for edge in current_tree.edges():
        n0,n1 = edge
        current_tree[n0][n1]['par'   ] = par_mat[:,pnum]
        current_tree[n0][n1]['family'] = fml_vec[pnum]
        current_tree[n0][n1]['loglik'] = ll_vec[pnum]
        pnum +=  1

    tree_list.append(current_tree)
            
        
    while( len(current_tree.nodes()) >= 3 ):
        next_tree,next_graph = dvine_model_next_tree(current_tree,
                                                     familyset,
                                                     threads_num)
        tree_list.append(next_tree)
        graph_list.append(next_graph)
        current_tree = next_tree
        
    # when MLE carries, all the values in 'par' will be covered, hence
    # a new key for storing sequential estimation result is created
    # and named 'par_sqe'. Same as attribute 'loglik'.
    for tree in tree_list:
        for edge in tree.edges():
            n0,n1 = edge
            tree[n0][n1]['par_sqe'   ] = tree[n0][n1]['par']
            tree[n0][n1]['loglik_seq'] = tree[n0][n1]['loglik']
            
    ## compute for the loglikelihood value of the whole regular vine
    init_loglik = 0
    for tree in tree_list:
        for edge in tree.edges():
            n0,n1 = edge
            edge_info = tree[n0][n1]
            init_loglik += edge_info['loglik_seq']

    rvine.tree_list  = tree_list
    rvine.graph_list = graph_list
    rvine.sqe_ll     = init_loglik
    return
    


def RvineMLE(rvine, threads_num=1, factr = 1e9, disp=False):
    """
    Maximum likelihood estimation after sequential estimation for a
    larger likelihood value.

    Parameter
    ---------
    
    rvine : RVine class object.

    disp : bool, optional. If 'True', the optimization ratio of
           progress will be shown. Default is 'False'.

    factr: float, optional. The machine precision multiplying the
           factor value is the iteration stopping condition
           value. Typical values for factr are: 1e12 for low accuracy,
           1e7 for moderate accuracy, and 10.0 for extremely high
           accuracy. Default is 1e9.

    threads_num : int. Number of threads are used for the multi
                  processing computing of loglikelihood value of each
                  vine tree. The real cpu cores number will be used if
                  threads_num is larger. Default is 1.

    """
    min_df    = 2.0
    max_df    = 1e2
    max_delta = 1e3
    max_rho   = 0.999

    tree_list = rvine.tree_list

    ## generate initial value vector, bounds vector and family vector
    para_init   = []
    para_bounds = []

    ## don't worry the orders of parametre initial vector, bounds
    ## vector and family vector, because each time walk through each
    ## tree of tree_list and each edge of each tree, the order doesn't
    ## change.

    ## the nested for loop below just pack the parameter initial
    ## value, the parameter bound and family of each edge on each tree
    ## into the three vectors, which is a necessary for the l-bfgs-b
    ## algorithm.

    for tree in tree_list:
        for edge in tree.edges():
            n0,n1 = edge
            edge_para = tree[n0][n1]['par_sqe']
            edge_fami = tree[n0][n1]["family" ]
            par_one,par_two = edge_para

            if edge_fami == 1:
                
                para_bounds.append(
                        (
                        max(par_one - 0.05 , -max_rho),
                        min(par_one + 0.05 , +max_rho)
                        )
                        )
                para_init.append(par_one)

            elif edge_fami == 2:
                
                para_bounds.extend(
                    [
                        (
                            max(par_one - 0.05, -max_rho),
                            min(par_one + 0.05, +max_rho)
                            )
                        ,
                        (
                            max(par_two - 5.00, min_df),
                            min(par_two + 5.00, max_df)
                            )
                        ]
                    )
                para_init.extend(edge_para) # add both rho and nu into
                                            # the parameter initial
                                            # vector
                
            elif edge_fami == 3:
                
                para_bounds.append(
                        (
                        max(par_one - 5.00, 0.00),
                        min(par_one + 5.00, max_delta)
                        )
                        )
                para_init.append(par_one)
                
            elif edge_fami == 4:
                
                para_bounds.append(
                        (
                        max(par_one - 5.00, +1.00),
                        min(par_one + 5.00, +max_delta)
                        )
                        )
                para_init.append(par_one)


            elif edge_fami == 5:
                
                para_bounds.append(
                        (
                        max(par_one - 5.00, -max_delta),
                        min(par_one + 5.00, +max_delta)
                        )
                        )
                para_init.append(par_one)
    
            elif edge_fami == 6:
                
                para_bounds.append(
                        (
                        max(par_one - 5.00, +1.00),
                        min(par_one + 5.00, +max_delta)
                        )
                        )

                para_init.append(par_one)

                
    def rvine_loglik(par):
        """
        This function computes the total loglikelihood value of the
        regular vine given par vector.
        """
        ## unpack the par vector onto edges

        i = 0
        
        for tree in tree_list:
            for edge in tree.edges():
                n0, n1 = edge
                edge_info = tree[n0][n1]
                edge_fami = edge_info['family']

                if edge_fami == 2:
                    
                    tree[n0][n1]['par'] = par[i:i+2]
                    i += 2
                    
                else:

                    par_one = par[i]
                    edge_par = np.array([par_one,0.0])
                    tree[n0][n1]['par'] = edge_par
                    i += 1
        
        ## RvineFixModel will compute edge data for edges on the
        ## second till last vine trees through H functions with fixed
        ## edges parameters
                    
        RvineFixModel(rvine,fix_par = True)

        ## collect the paired edge data, the parameter vector, the
        ## family vector for parallel computing of the loglikelihood
        ## value of the vine copulas given parameter vector

        paired_data = []
        para_vec = []
        fami_vec = []

        for tree in tree_list:
            for edge in tree.edges():
                
                n0 , n1 = edge
                edge_info = tree[n0][n1]
                edge_fami = edge_info['family']
                edge_para = edge_info['par'   ]
                u1 = edge_info['edge_data'][n0]
                u2 = edge_info['edge_data'][n1]

                paired_data.append( np.array([u1,u2]).transpose() )
                para_vec.append( edge_para )
                fami_vec.append( edge_fami )

        paired_data = np.concatenate( paired_data, 1 )
        para_vec    = np.array(para_vec).transpose()
        fami_vec    = np.array(fami_vec,dtype=int)

        ## using multi_process_loglik to computer the total
        ## loglikelihood value of the entire regular vine
        return multi_process_loglik(paired_data,
                                    para_vec,
                                    fami_vec,
                                    threads_num
                                    )

    def optim_fun(par):
        ## target function for fmin_lbfgsb
        return -rvine_loglik(par)

    optim_res = fmin(optim_fun,
                     para_init,
                     approx_grad = True,
                     bounds = para_bounds,
                     disp = disp,
                     factr = factr
                     )
    
    par_res      =  optim_res[0]
    rvine.mle_ll = -optim_res[1]

    ## unpack and distribute the mle result to each edge
    i = 0
    
    for tree in tree_list:
        for edge in tree.edges():
            n0,n1 = edge
            edge_info = tree[n0][n1]
            edge_fami = edge_info['family']

            if edge_fami == 2:
                tree[n0][n1]['par_mle'] = par_res[i:i+2]
                i += 2
                
            else:
                par_one = par_res[i]
                edge_par_mle = np.array([par_one,0.0])
                tree[n0][n1]['par_mle'] = edge_par_mle
                i += 1

    return



def RvineSim(rvine,size):
    """
    Sample from a regular vine object 'RVine' which is after
    modeling.

    Parameter
    ---------

    rvine : Rvine class object.

    size : int.

    Return
    ------

    x : pandas DataFrame like.
    """
    tree_list = rvine.tree_list
    tree_num = rvine.var_num - 2
    
    # firstly sample for the edge of the last tree
    current_tree = tree_list[tree_num]
    n0,n1        = current_tree.edges()[0]
    edge_info    = current_tree[n0][n1]
    
    u_n0 = np.random.rand( size )
    u_n1 = np.random.rand( size )
    
    edge_par    = edge_info['par'   ]
    edge_family = edge_info['family']
    
    u_n1 = bvcop.bv_cop_inv_hfunc(u_n1,
                                  u_n0,
                                  edge_par,
                                  edge_family
                                  )
    
    edge_sample = {n0:u_n0,n1:u_n1}
    current_tree[n0][n1]['sample'] = edge_sample
    
    def Sample_Edge(n0,n1,old_n0,old_n1):

        ## determine the current tree number from node name
        tree_num = len(n0.replace('|','').replace(',',''))-1
        
        current_tree = tree_list[tree_num]
        next_tree    = tree_list[tree_num+1]
        edge_info    = current_tree[n0][n1]

        ## if marginal samples both exists on this edge (n0, n1), just
        ## return
        if edge_info.has_key('sample') and \
                len(edge_info['sample']) == 2:
            return

        ## if u_n0 and u_n1 both don't exist, or only u_n0 exists
        if not edge_info.has_key('sample') or not \
                edge_info['sample'].has_key(n1):
            ## if current tree is the first tree, just sample u_n1
            ## from uniform distribution
            if tree_num == 0:
                u_n1 = np.random.rand( size )
            ## if not the first tree, consider whether u_n1 could be
            ## figured out via H-function from marginal samples on the
            ## edge corresponding to its one-fold triple in the
            ## previous tree. if the two marginal samples doesn't both
            ## exist, just sample u_n1 from uniform distribution
            else:
                prev_n0,prev_n1,prev_n2 = edge_info['one_fold']
                prev_tree = tree_list[tree_num-1]
                if not gen_node(prev_n0,prev_n2) == n1:
                    prev_n0 = prev_n1
                prev_edge_info = prev_tree[prev_n0][prev_n2]
                if prev_edge_info.has_key('sample') and \
                        len(prev_edge_info['sample']) == 2:
                    u_prev_n0 = prev_edge_info['sample'][prev_n0]
                    u_prev_n2 = prev_edge_info['sample'][prev_n2]
                    u_n1 = bvcop.bv_cop_hfunc(u_prev_n0,u_prev_n2,
                                              prev_edge_info['par'],                        
                                              prev_edge_info['family']
                                              )
                else:
                    u_n1 = np.random.rand( size )

        else:
            u_n1 = edge_info['sample'][n1]

        ## figure out u_n0 via the inverse H-function via marginal
        ## sample on edge (old_n0,old_n1)
        next_tree_info = next_tree[old_n0][old_n1]
        u_n0 = bvcop.bv_cop_inv_hfunc(next_tree_info['sample'][gen_node(n0,n1)],
                                  u_n1,
                                  edge_info['par'],
                                  edge_info['family']
                                  )

        ## put the sampled dict of edge_sample on edge (n0,n1)
        edge_sample = {n0:u_n0,n1:u_n1}
        current_tree[n0][n1]['sample'] = edge_sample

        ## if the current tree is the first one, copy the marginal
        ## sample to the neighbor edge as soon as it is generated.
        if tree_num == 0:
            for one_node in current_tree.neighbors(n0):
                if not current_tree[n0][one_node].has_key('sample'):
                    edge_sample = {n0:u_n0}
                    current_tree[n0][one_node]['sample'] = edge_sample
                else:
                    if not current_tree[n0][one_node]['sample'].has_key(n0):
                        current_tree[n0][one_node]['sample'][n0] = u_n0
            for one_node in current_tree.neighbors(n1):
                
                if not current_tree[n1][one_node].has_key('sample'):
                    edge_sample = {n1:u_n1}
                    current_tree[n1][one_node]['sample'] = edge_sample
                else:
                    if not current_tree[n1][one_node]['sample'].has_key(n1):
                        current_tree[n1][one_node]['sample'][n1] = u_n1
            return

        ## recover the three node of one-fold triple of current edge
        prev_n0,prev_n1,prev_n2 = edge_info['one_fold']

        ## call 'Sample_Edge' itself recursively
        Sample_Edge(prev_n0,prev_n2,n0,n1)
        Sample_Edge(prev_n1,prev_n2,n0,n1)
        return 
    
    prev_n0,prev_n1,prev_n2 = edge_info['one_fold']

    # recursive sampling entrance
    Sample_Edge(prev_n0,prev_n2,n0,n1)
    Sample_Edge(prev_n1,prev_n2,n0,n1)
    
    sample_result = {}
    tree_1 = tree_list[0]
    
    for edge in tree_1.edges():
        
        n0,n1 = edge
        edge_info = tree_1[n0][n1]
        
        if not sample_result.has_key(n0):
            sample_result[n0] = edge_info['sample'][n0]
        if not sample_result.has_key(n1):
            sample_result[n1] = edge_info['sample'][n1]
            
    for tree in tree_list:
        for edge in tree.edges():
            n0,n1 = edge
            tree[n0][n1].pop('sample')
            
    return sample_result
        



def RvineFixModel(rvine,fix_par = False):
    """
    Model R-vine copula with fixed structure. Fixing parameters is
    optional.

    Parameter
    ---------

    rvine : RVine Class object.

    fix_par : bool, optional. If 'True', both the structure and the
              already existed parameters will be fixed.
    """
    tree_list = rvine.tree_list
    if fix_par ==  True:
        tree_num = 0
        while tree_num !=  rvine.var_num-2:
            tree_num +=  1
            current_tree = tree_list[tree_num]
            prev_tree = tree_list[tree_num-1]
            for edge in current_tree.edges():
                n0,n1 = edge
                edge_info = current_tree[n0][n1]
                prev_n1,prev_n2,prev_n0 = edge_info['one_fold']
                edge_data = {}
                prev_edge_info = prev_tree[prev_n1][prev_n0]
                prev_edge_data = prev_edge_info['edge_data']
                prev_edge_fami = prev_edge_info['family'   ]
                prev_edge_para = prev_edge_info['par'      ]
                v1 = prev_edge_data[prev_n1]
                v0 = prev_edge_data[prev_n0]
                edge_data[gen_node(prev_n1,prev_n0)] = \
                    bvcop.bv_cop_hfunc(v1,v0,
                                       prev_edge_para,                                       
                                       prev_edge_fami
                                     )
                prev_edge_info = prev_tree[prev_n2][prev_n0]
                prev_edge_data = prev_edge_info['edge_data']
                prev_edge_fami = prev_edge_info['family'   ]
                prev_edge_para = prev_edge_info['par'      ]
                v1 = prev_edge_data[prev_n2]
                v0 = prev_edge_data[prev_n0]
                edge_data[gen_node(prev_n2,prev_n0)] = \
                    bvcop.bv_cop_hfunc(v1,v0,
                                       prev_edge_para,                                       
                                       prev_edge_fami,
                                       )
                current_tree[n0][n1]['edge_data'] = edge_data
    else:
        tree_num = 0
        while tree_num !=  rvine.var_num - 2:
            tree_num +=  1
            current_tree = tree_list[tree_num]
            prev_tree = tree_list[tree_num-1]
            for edge in current_tree.edges():
                n0,n1 = edge
                edge_info = current_tree[n0][n1]
                prev_n1, prev_n2, prev_n0 = edge_info['one_fold']
                edge_data = {}
                prev_edge_info = prev_tree[prev_n1][prev_n0]
                prev_edge_data = prev_edge_info['edge_data']
                prev_edge_fami = prev_edge_info['family'   ]
                v1 = prev_edge_data[prev_n1]
                v0 = prev_edge_data[prev_n0]
                prev_edge_info['par'] = bvcop.bv_cop_mle(v1,
                                                         v0,
                                                         prev_edge_fami,
                                                         )[0]
                prev_edge_para = prev_edge_info['par']
                edge_data[gen_node(prev_n1,prev_n0)] = \
                    bvcop.bv_cop_hfunc(v1,v0,
                                       prev_edge_para,                                       
                                       prev_edge_fami
                                       )
                    
                prev_edge_info = prev_tree[prev_n2][prev_n0]
                prev_edge_data = prev_edge_info['edge_data']
                prev_edge_fami = prev_edge_info['family'   ]
                v1 = prev_edge_data[prev_n2]
                v0 = prev_edge_data[prev_n0]
                prev_edge_info['par'] = bvcop.bv_cop_mle(v1,
                                                         v0,
                                                         prev_edge_fami
                                                         )[0]
                prev_edge_para = prev_edge_info['par']
                edge_data[gen_node(prev_n2,prev_n0)] = \
                    bvcop.bv_cop_hfunc(v1,v0,
                                       prev_edge_para,                                      
                                       prev_edge_fami
                                       )
                current_tree[n0][n1]['edge_data'] = edge_data
                    


def rsblt_trans(rvine):
    """
    Compute data after Rosenblatt probability integral transformation
    of R-vine copula.

    Parameter
    ---------

    rvine : RVine Class object.

    Return
    ------

    x : array with shape N x P.
    """
    tree_list = rvine.tree_list
    tree_num = rvine.var_num - 2
    
    current_tree = tree_list[tree_num]
    n0,n1        = current_tree.edges()[0]
    edge_info    = current_tree[n0][n1]
    e0           = edge_info['edge_data'][n0]
    e1           = edge_info['edge_data'][n1]
    edge_fami    = edge_info['family']
    edge_para    = edge_info['par']
    e1           = bvcop.bv_cop_hfunc(e1,
                                      e0,
                                      edge_para,
                                      edge_fami
                                      )
    rsblt_trans_data = [e0,e1]
    while tree_num !=  0:
        prev_n0,prev_n1,prev_n2 = current_tree[n0][n1]['one_fold']
        tree_num    -=  1
        current_tree = tree_list[tree_num]
        n1, n0       = prev_n0, prev_n2
        edge_info    = current_tree[n0][n1]
        e            = edge_info['edge_data'][n0]
        rsblt_trans_data.append(e)
        
    rsblt_trans_data = np.array(rsblt_trans_data).transpose() # amend .T -> .transpose()
    return rsblt_trans_data


def ad_statistic(data):
    """
    Anderson-Darling test for the hypothesis that data are
    observations from independent copula.

    Parameter
    ---------

    data : array with shape N x P.

    Return
    ------

    x : float. The AD-test Statistic.
    """
    chisq_data = (norm.ppf(data)**2).sum(1) # sum along row axis
    chisq_data.sort()
    sample_num, var_num = data.shape
    g_chi = chi2.cdf(chisq_data,var_num)
    return ad_stat(g_chi)


def sample_with_replace(copula_data,N):
    """
    N size sample with replacement.

    Parameter
    ---------

    copula_data : dict of array.

    N : int. Resample size.

    Return
    ------

    x : list of array.
    """
    copied = copula_data.copy() # the argument 'copula_data' refers to
                                # the original dataset. Copy for not
                                # recover.
    index = np.random.randint(low = 0,high = len(copied[copied.keys()[0]]),size = N) # [FIXED]
    print index
    for i in copied.keys():
        copied[i] = copied[i][index]
    return copied
    

def RvineTest(rvine, bootstrap = False, N = 0, NB = 1000, disp = False):
    """
    Test the hypothesis H0: U ~ C where C stands for the R-vine
    copula.

    Firstly map (u_1,...,u_d) into (e_1,...,e_d) by applying
    Rosenblatt probability transform (function 'rsblt_trans'). The
    transformed random vector (e_1,...,e_d) will follow an independent
    copulas C*, hence the hypothesis H0 : U ~ C will be approximately
    equal to the new hypothesis H0* : E ~ C*. Bootstrap method is
    utilized for the empirical distribution of Anderson-Darling
    statistics for an adjusted P-value.

    Parameter
    ---------

    rvine : RVine class object. At least the sequential estimation for
            rvine should be taken.

    bootstrap : bool, optional. Flag controling the bootstrap version
                of Anderson-Darling test. Default is False.

    N : int, optional. Resample size. Default is 0 indicating the
        same size with dataset.

    NB : int, optional. The number of replications. Default is 1000.

    disp : bool, optional. Flag controling the displaying of rate of
           progress.
    """
    if rvine.mle_flag ==  True:
        rvine.gen_par('mle')
    else:
        rvine.gen_par('sqe')

    # The necessity of 'RvineFixModel' sentence below comes from the
    # reason that conditional marginal data from second to last vine
    # trees is overwritten after mle. Hence its safe to re-generate
    # them.
    RvineFixModel(rvine,fix_par = True) 
    rsblt_trans_data = rsblt_trans(rvine)
    rvine.ad_stat    = ad_statistic(rsblt_trans_data)
    rvine.pvalue     = 1.0 - adinf(rvine.ad_stat)

    if not bootstrap:
        return
    
    ## create the empirical distribution using bootstrap method.
    bootstrap_reps = np.zeros(NB)

    if disp == True:
        print "\n\tBootstrap version of AD-Test:\n"

    import copy                 # used for deep copy of rvine object
    
    for i in range(NB):

        bst_rvine   = copy.deepcopy(rvine)
        # cp_data_rep = sample_with_replace(rvine.copula_data, N)
        sim_dat = rvine.sim( N ).values

        cp_data_rep = {}
        for j in range(rvine.var_num):
            cp_data_rep[str(j+1)] = sim_dat[:,j]

        tree_one    = bst_rvine.tree_list[0]
        
        for edge in tree_one.edges():
            n0, n1 = edge
            edge_data = {
                n0:cp_data_rep[n0],
                n1:cp_data_rep[n1]
                }
            tree_one[n0][n1]['edge_data'] = edge_data

        # calling RvineFixModel here so as to model the resampled data
        # with fixed R-vine structure and bivariate families on each
        # edge
        RvineFixModel(bst_rvine, fix_par = True)
        rsblt_trans_data = rsblt_trans(bst_rvine)

        tmp = pandas.DataFrame(rsblt_trans_data)

        bootstrap_reps[i] = ad_statistic(rsblt_trans_data)

        if disp == True:
            print "\t\t replication ", i+1, " completed.."
            
    rvine.bootstrap_reps = bootstrap_reps
    rvine.bpvalue     = 1.0 - \
        np.mean(np.array(bootstrap_reps < rvine.ad_stat,dtype = float))

    return





# def RvineTest(rvine, bootstrap = False, N = 0, NB = 1000, disp = False):
#     """
#     Test the hypothesis H0: U ~ C where C stands for the R-vine
#     copula.

#     Firstly map (u_1,...,u_d) into (e_1,...,e_d) by applying
#     Rosenblatt probability transform (function 'rsblt_trans'). The
#     transformed random vector (e_1,...,e_d) will follow an independent
#     copulas C*, hence the hypothesis H0 : U ~ C will be approximately
#     equal to the new hypothesis H0* : E ~ C*. Bootstrap method is
#     utilized for the empirical distribution of Anderson-Darling
#     statistics for an adjusted P-value.

#     Parameter
#     ---------

#     rvine : RVine class object. At least the sequential estimation for
#             rvine should be taken.

#     bootstrap : bool, optional. Flag controling the bootstrap version
#                 of Anderson-Darling test. Default is False.

#     N : int, optional. Resample size. Default is 0 indicating the
#         same size with dataset.

#     NB : int, optional. The number of replications. Default is 1000.

#     disp : bool, optional. Flag controling the displaying of rate of
#            progress.
#     """
#     if rvine.mle_flag ==  True:
#         rvine.gen_par('mle')
#     else:
#         rvine.gen_par('sqe')

#     # The necessity of 'RvineFixModel' sentence below comes from the
#     # reason that conditional marginal data from second to last vine
#     # trees is overwritten after mle. Hence its safe to re-generate
#     # them.
#     RvineFixModel(rvine,fix_par = True) 
#     rsblt_trans_data = rsblt_trans(rvine)
#     rvine.ad_stat    = ad_statistic(rsblt_trans_data)
#     rvine.pvalue     = 1.0 - adinf(rvine.ad_stat)

#     if not bootstrap:
#         return
    
#     ## create the empirical distribution using bootstrap method.
#     bootstrap_reps = np.zeros(NB)

#     if disp == True:
#         print "\n\tBootstrap version of AD-Test:\n"

#     import copy                 # used for deep copy of rvine object
    
#     for i in range(NB):

#         bst_rvine   = copy.deepcopy(rvine)
#         cp_data_rep = sample_with_replace(rvine.copula_data, N)

#         tree_one    = bst_rvine.tree_list[0]
        
#         for edge in tree_one.edges():
#             n0, n1 = edge
#             edge_data = {
#                 n0:cp_data_rep[n0],
#                 n1:cp_data_rep[n1]
#                 }
#             tree_one[n0][n1]['edge_data'] = edge_data

#         # calling RvineFixModel here so as to model the resampled data
#         # with fixed R-vine structure and bivariate families on each
#         # edge
#         RvineFixModel(bst_rvine, fix_par = True)
#         rsblt_trans_data = rsblt_trans(bst_rvine)

#         tmp = pandas.DataFrame(rsblt_trans_data)

#         bootstrap_reps[i] = ad_statistic(rsblt_trans_data)

#         if disp == True:
#             print "\t\t replication ", i+1, " completed.."
            
#     rvine.bootstrap_reps = bootstrap_reps
#     rvine.bpvalue     = 1.0 - \
#         np.mean(np.array(bootstrap_reps < rvine.ad_stat,dtype = float))

#     return






def DataCheck(cp_data):
    """
    Check the low and upp bounds for rank transformed dataset.

    Parameter
    ---------

    cp_data : array with shape N x P.

    Return
    ------

    x : tuple of a bool value and a string.
    """
    if np.min( cp_data ) <= 0.0:
        bval = False
        bstr = "Values equal or small than zero."
    elif np.max( cp_data ) >= 1.0:
        bval = False
        bstr = "Values equal or large than one."
    elif cp_data.shape[0] < 10:
        bval = False
        bstr = "Sample size smaller than ten."
    elif cp_data.shape[1] < 3:
        bval = False
        bstr = "Dimension < 3."
    else:
        bval = True
        bstr = "OK."
    return (bval, bstr)


class Rvine:
    def __init__(self,dataframe):
        """
        Initialization function for an Rvine class object using data
        after rank transformation.

        Parameter
        ---------

        dataframe : pandas DataFrame.
        """
        if type(dataframe) != pandas.core.frame.DataFrame:
            raise TypeError("data must be pandas DataFrame type.")
        self.dataframe = dataframe
        
        bval, bstr = DataCheck(dataframe.values)
        if not bval:
            raise Exception(bstr)
        del bval, bstr

        self.data        = dataframe.values
        self.var_name    = dataframe.columns.tolist()
        self.sample_num, self.var_num = dataframe.shape
        
        copula_data = {}
        for i in range(self.var_num):
            copula_data[str(i+1)] = self.data[:,i]
            
        self.copula_data = copula_data
        self.mle_flag    = False
        self.sqe_flag    = False
        self.sqe_ll      = 0
        self.mle_ll      = 0
        
    def modeling(self,structure = 'r', familyset = [1,2,3,4,5,6], threads_num = 1):
        """
        Sequential estimation of R-vine copulas. R-vine structure,
        families and parameters for edges are determined.

        Parameter
        ---------

        structure : flag specifying the structure of vine. Only 'r',
                    'c' and 'd' and there capital letters are
                    acceptable. 'r' stands for generalized regular
                    vine; 'c' stands for C-vine, with star like trees;
                    'd' stands for D-vine, with linear structure
                    trees.

        familyset : list of integers. familyset provides a set of
                    bivariate copula families for edges of vine trees
                    to choose from. Available families are listed
                    below.

        threads_num : int. Number of threads are used for the multi
                      processing mle work. The real cpu cores number
                      will be used if threads_num is larger. Default
                      is 1.
        """
        structure = structure.upper()

        if structure == 'R':
            RvineModeling(self, familyset = familyset, threads_num = threads_num)
        elif structure == 'C':
            CvineModeling(self, familyset = familyset, threads_num = threads_num)
        elif structure == 'D':
            DvineModeling(self, familyset = familyset, threads_num = threads_num)
            
        self.sqe_flag = True

        
    def mle(self, threads_num = 1, factr = 1e9, disp = False):
        """
        ML estimation for R-vine copula.

        Parameter
        ---------
        
        disp : bool, optional. If 'True', the optimization output
               would be printed. Default is 'False'.

        factr : float, optional. The machine precision multiplying the
                factr value is the iteration stopping condition
                value. Typical values for factr are: 1e12 for low
                accuracy, 1e7 for moderate accuracy, and 10.0 for
                extremely high accuracy. Default is 1e7. The smaller,
                the more time optimization would take. Default is 1e9.

        threads_num : int. Number of threads are used for the multi
                      processing computing of loglikelihood value of
                      each vine tree. The real cpu cores number will
                      be used if threads_num is larger. Default is 1.
        """
        if not self.sqe_flag:
            raise Exception(
                "MLE should take after sequential estimation via function 'modeling'."
                )
        if self.mle_flag:
            raise Warning("MLE has been taken.\n")
        RvineMLE(self, threads_num = threads_num, factr = factr, disp = disp)
        self.mle_flag = True
        
    def plot(self,ntrees = 0, filename = ""):
        """
        Plot the regular vine structure after sequential estimation
        via function 'modeling'.

        Parameter
        ---------

        ntrees : int, optional. The first ntrees of all the vine trees
                 will be plotted. Default is `0', meaning plotting all
                 the vine trees.
                 
        filename : string, optional. Default is an empty string
                   indicating direct output to screen. The plot will
                   output to the specified directory if a file name
                   with extension is given.
        """
        if not self.sqe_flag:
            raise Exception("Plot should be taken after regular vine modeling.")

        if ntrees == 0:
            ntrees = self.var_num -1
        elif ntrees > self.var_num -1:
            ntrees = self.var_num -1
            
        mf_row = (ntrees + 1) / 2

        if ntrees == 1:

            plt.title("Tree_1")
            nx.draw(self.tree_list[0])
            if filename:
                plt.savefig(filename)                
            else:
                plt.show()

        else:

            mfrow = (ntrees+1) /2
            mfcol = 2

            for i in range(ntrees):
                plt.subplot(mfrow, mfcol, i+1)
                plt.title("Tree_"+str(i+1))
                nx.draw(self.tree_list[i])

            if filename:
                plt.savefig(filename)                
            else:
                plt.show()
        
        plt.clf()
        
        
    def res(self,ndigits=2):
        """
        Return the result of regular vine copula modeling.

        Parameter
        ---------

        ndigits : int. Control the number of decimal digits of result
                  that will be printed.
        """
        BVCOPULA_FAMILY = {
            1:"Normal",
            2:"Student",
            3:"Clayton",
            4:"Gumbel",
            5:"Frank",
            6:"Joe",
            }
        
        if not self.sqe_flag:
            raise Exception(
                "Sequential estimation isn't taken."
                )
        if self.mle_flag == True:
            res_columns = pandas.MultiIndex.from_tuples([('Edge','Node1'),
                                                       ('Edge','Node2'),
                                                       ('SQ Est','Par1'),
                                                       ('SQ Est','Par2'),
                                                       ('ML Est','Par1'),
                                                       ('ML Est','Par2'),
                                                       ('Family','')])
            node_1_list   = []
            node_2_list   = []
            sq_par_1_list = []
            sq_par_2_list = []
            ml_par_1_list = []
            ml_par_2_list = []
            family_list   = []
            for tree in self.tree_list:
                for edge in tree.edges():
                    n0,n1        = edge
                    edge_family  = tree[n0][n1]['family' ]
                    edge_par     = tree[n0][n1]['par_sqe']
                    edge_par_mle = tree[n0][n1]['par_mle']
                    node_1_list.append(n0)
                    node_2_list.append(n1)
                    family_list.append(BVCOPULA_FAMILY[edge_family])                    
                    sq_par_1_list.append(round(edge_par[0],ndigits))
                    sq_par_2_list.append(round(edge_par[1],ndigits))
                    ml_par_1_list.append(round(edge_par_mle[0],ndigits))
                    ml_par_2_list.append(round(edge_par_mle[1],ndigits))
            self.res_df = pandas.DataFrame(zip(*[node_1_list,
                                               node_2_list,
                                               sq_par_1_list,
                                               sq_par_2_list,
                                               ml_par_1_list,
                                               ml_par_2_list,
                                               family_list]),
                                           columns = res_columns)
        else:
            res_columns = pandas.MultiIndex.from_tuples([('Edge','Node1'),
                                                       ('Edge','Node2'),
                                                       ('SQ Est','Par1'),
                                                       ('SQ Est','Par2'),
                                                       ('Family','')])
            node_1_list   = []
            node_2_list   = []
            sq_par_1_list = []
            sq_par_2_list = []
            family_list   = []
            for tree in self.tree_list:
                for edge in tree.edges():
                    n0,n1       = edge
                    edge_family = tree[n0][n1]['family' ]
                    edge_par    = tree[n0][n1]['par_sqe']
                    node_1_list.append(n0)
                    node_2_list.append(n1)
                    family_list.append(BVCOPULA_FAMILY[edge_family])                    
                    sq_par_1_list.append(round(edge_par[0],ndigits))
                    sq_par_2_list.append(round(edge_par[1],ndigits))
            self.res_df = pandas.DataFrame(zip(*[node_1_list,
                                               node_2_list,
                                               sq_par_1_list,
                                               sq_par_2_list,
                                               family_list]),
                                           columns = res_columns)
        return self.res_df

    def loglik(self):
        """
        Display the loglikelihood value of sequential estimation (and
        maximum likelihood estimation if it has been taken) of the
        regular vine copula.
        """
        if not self.sqe_flag:
            raise Exception("Sequential estimation isn't taken.")
        
        print "Loglikelihood for SQ Estimation is %.4f " % self.sqe_ll
        if self.mle_flag:
            print "Loglikelihood for ML Estimation is %.4f " % self.mle_ll

    def sim(self,size):
        """
        Sample from an R-vine copulas. Sequential estimation should be
        taken before sampling.

        Parameter
        ---------

        size : int. Sample size.

        Return
        ------

        x : pandas DataFrame.
        """
        if not self.sqe_flag:
            raise Exception("Sequential estimation isn't taken!")
        sampled = pandas.DataFrame(RvineSim(self,size))
        sampled.columns = self.var_name
        return sampled

    def gen_par(self,par_flag):
        """
        Each edge has three members related to parameter information,
        'par', 'par_mle' and 'par_sqe'. This routine substitute 'par'
        either by 'par_mle' or 'par_sqe', depending on the par_flag.

        Parameter
        ---------

        par_flag : string. Either 'mle' or 'sqe' is acceptable.
        """
        if self.sqe_flag ==  False:
            raise Exception("SQ Estimation isn't taken.")
        
        if par_flag ==  'mle':
            if self.mle_flag ==  False:
                raise Exception("ML Estimation isn't taken.")
            else:
                for tree in self.tree_list:
                    for edge in tree.edges():
                        n0,n1 = edge
                        tree[n0][n1]['par'] = tree[n0][n1]['par_mle']
                        
        elif par_flag ==  'sqe':
            for tree in self.tree_list:
                for edge in tree.edges():
                    n0,n1 = edge
                    tree[n0][n1]['par'] = tree[n0][n1]['par_sqe']
        else:
            
            raise ValueError("Wrong input in 'gen_par'!")
        
        return

    
    def test(self,bootstrap = False, N = 0, NB = 1000, disp = False, hist = True):
        """
        Test the hypothesis H_0 : U ~ C.

        Firstly map (u_1,...,u_d) into (e_1,...,e_d) by Rosenblatt
        probability transform (abbrev. RTT), the random vector
        (e_1,...,e_d) will follow an independent copulas C*.  The
        Anderson-Darling test which has good power properties will be
        applied on the data set (e_1,...,e_d). For a more corrected
        value of the crytical value due to AD-test, bootstrap method
        is utilized.

        Parameter
        ---------

        bootstrap : bool, optional. Flag controling the bootstrap
                    version of Anderson-Darling test. Default is
                    False.

        N : int, optional. Resample size. Default is 0 indicating the
            same size with dataset.

        NB : int, optional. The number of replication for
             bootstrap. Default 1000.

        disp : bool, optional. Flag controling the displaying of the
               testing procedure.

        hist : bool, optional. Control the plotting of histogram of
               empirical distribution of bootstrap statistics for
               AD-test.
        """
        if N == 0:
            N = self.sample_num
        RvineTest(self, bootstrap, N = N, NB = NB, disp = disp)
        if bootstrap:
            print """
Testing Hypothesis H0 : U ~ C
-----------------------------

%d parametric bootstrap replications of %d resampling are generated

Statistic          = %.4f
P-value            = %.4f
Adjusted P-value   = %.4f
""" % (NB, N, self.ad_stat, self.pvalue, self.bpvalue)
            if hist:

                dx   = 0.001
                mx   = max(max(self.bootstrap_reps), 4.5)
                x    = np.linspace(0, mx, mx / dx)
                y    = adinf(x)
                dy   = (y[1:] - y[:-1]) / dx

                fig  = plt.figure()
                ax   = fig.add_subplot(111)
                
                bins = max(10, NB / 50)

                ax.hist(self.bootstrap_reps, bins, normed = True)
                ax.plot(x[1:], dy, color = 'red')

                ax.xaxis.set_label_text('AD-statistic')
                ax.yaxis.set_label_text('Distribution')

                plt.show()

        else:
            print """
Testing Hypothesis H0 : U ~ C
-----------------------------

Statistic          = %.4f
P-value            = %.4f
""" % (self.ad_stat, self.pvalue)
    
