
class Mol ():
    r"""
    Molecule.
    """
    # Adjacency matrix
    __A = []
    # Incidence matrix
    __B = []
    # Laplacian matrix
    __L = []
    # Normalized laplacian matrix
    __NL = []
    # Signless laplacian matrix
    __Q = []
    # Distance matrix
    __D = []
    # Resistance Distance matrix
    __RD = []

    __Order = 0
    __Edges = []
    
    __Sage_graph = None
    __NX_graph = None
    
    __Degrees = []
    
    
    __Spectrum = []
    __Laplacian_spectrum = []
    __Distance_spectrum = []
    __Norm_laplacian_spectrum = []
    __Signless_laplacian_spectrum = []
    __RD_spectrum = []
    
    __Is_connected = None
    
    def _reset_(self):
        """ Reset all attributes """
        # Adjacency matrix
        self.__A = []
        # Incidence matrix
        self.__B = []
        # Laplacian matrix
        self.__L = []
        # Normalized laplacian matrix
        self.__NL = []
        # Signless laplacian matrix
        self.__Q = []
        # Distance matrix
        self.__D = []
        # Resistance Distance matrix
        self.__RD = []
    
        self.__Order = 0
        self.__Edges = []
        
        self.__Sage_graph = None
        self.__NX_graph = None
        
        self.__Degrees = []
        
        
        self.__Spectrum = []
        self.__Laplacian_spectrum = []
        self.__Distance_spectrum = []
        self.__Norm_laplacian_spectrum = []
        self.__Signless_laplacian_spectrum = []
        self.__RD_spectrum = []
        
        self.__Is_connected = None
    
    # allow to set structure from somewhere
    # used in utilites
    
    def _set_A(self, A):
        self.__A = A
        
    def _set_Edges(self, edges):
        self.__Edges = edges
        
    def _set_Order(self, order):
        self.__Order = order
    
    # native method to initialize Mol class is to provide g6 string
    def __init__(self, g6str=None):
        """ Molecular graph class """
        if g6str != None:
            self.read_g6(g6str)
        
          
    def __repr__(self):
        if self.__A != None: return  'Molecular graph on '+ str(self.__Order)+' vertices'
        return 'Empty Molecular graph'
        
    def __len__(self):
        if self.__A != None: return len(self.__A)
        else: return 0
            
      
    def order(self):
        """ Return number of vertices """
        return self.__Order
    
    def edges(self):
        """ Return list of Edges """    
        return self.__Edges
    
    def vertices(self):
        """ Return list of vertices """
        return range(self.__Order)
           
    def sage_graph(self):
        """ Return Sage Graph object """
        #if not self._is_sage_graph(): self._init_sage_graph_()
        if self.__Sage_graph is None: self._init_sage_graph_()
        return self.__Sage_graph
         
            
    def NX_graph(self):
        """ Return NetworkX graph object """
        if self.__NX_graph is None:
            import networkx as nx
            self.__NX_graph = nx.Graph(self.__Edges)
        return self.__NX_graph
        
        
    def _init_sage_graph_(self):
        """ Initialize SAGE graph from Adjacency matrix"""
        from sage.graphs.graph import Graph
        self.__Sage_graph = Graph(self.__Edges)
            
            
    def read_g6(self, s):
        """ Initialize graph from graph6 string """
        def graph_bit(pos,off):
            return ( (ord(s[off + 1+ pos/6]) - 63) & (2**(5-pos%6)) ) != 0
        
        # reset all the attributes before changing the structure    
        self._reset_()
        
        n = ord(s[0]) - 63
        off = 0
        if n==63:
            if not ord(s[1]) - 63 == 63:
                n = sum(map(lambda i: (ord(s[i]) - 63) << (6*(3-i)),range(1,3)))
                off = 3
            else:
                n = sum(map(lambda i: (ord(s[i]) - 63) << (6*(7-i)),range(2,7)))
                off = 7
        self.__Order = n     
    
        self.__A = [[0 for col in range(n)] for row in range(n)]
    
        i=0; j=1
        
        self.__Edges = [];
        for x in range(n*(n-1)/2):
            if graph_bit(x, off):
                self.__A[i][j] = 1
                self.__A[j][i] = 1
                self.__Edges.append((i,j))
            if j-i == 1:
                i=0
                j+=1
            else:
                i+=1
    
    
    def write_dot_file(self, filename):
    
        f_out = open(filename, 'w')
        f_out.writelines('graph Mol {\n')
        for (i,j) in self.edges():
            f_out.writelines( '    ' + str(i) + ' -- ' + str(j) +';\n')
        f_out.writelines('}')    
        f_out.close()
                    
    #
    #
    # matrices
    #
    #
    
    def adjacency_matrix(self):
        """ Return Adjacency matrix
        
        Alias : A
        """    
        return self.__A
        
    A = adjacency_matrix
    
    def incidence_matrix(self):
        """ Return Incidence matrix 
        
        Alias: B
        """
        if self.__B == []:
            def func((u,v)):
                col = [0] * self.__Order
                col[u] = 1
                col[v] = 1
                return col
            # apply func to each edge
            b = map(lambda e: func(e), self.edges())
            # transpose the result
            self.__B = map(list, zip(*b)) 
        return self.__B
        
    B = incidence_matrix


    def laplacian_matrix(self):
        """ Return Laplacian matrix
        
        L = D-A
        where  D - matrix whose diagonal elements are the degrees of the corresponding vertices
               A - adjacency matrix
                
        Alias : L
        """
        if self.__L == []:
            import numpy as np;
            self.__L = np.diag(self.degrees()) - np.matrix(self.__A);
        return self.__L
        
    L = laplacian_matrix
    
    
    def signless_laplacian_matrix(self):
        """ Return Signless Laplacian matrix
        
        Q = D+A
        Alias : Q
        """
        if self.__Q == []:
            import numpy as np;
            self.__Q = np.diag(self.degrees()) + np.matrix(self.__A);
        return self.__Q
        
    Q = signless_laplacian_matrix
    
    
    def normalized_laplacian_matrix(self):
        """ Return Normalized Laplacian matrix
        
        NL = deg^(-1/2) * L * deg(1/2)
        Alias : NL
        """
        ## TODO: check if we have zeros in degrees()
        if self.__NL  == []:
            import numpy as np;
            d1 = np.diag( np.power( self.degrees(), -.5 ))
            d2 = np.diag( np.power( self.degrees(),  .5 ))
            self.__NL = d1 * self.laplacian_matrix() * d2
        return self.__NL
        
    NL = normalized_laplacian_matrix


    def distance_matrix(self):
        """ Return Distance matrix
        
        Alias : D
        """    
        if self.__Order == 0: return []
        
        if self.__D == [] :
            import numpy as np;
            # use here float only for using np.inf - infinity
            A = np.matrix(self.__A, dtype=float)
            n,m = A.shape
            I=np.identity(n)
            A[A==0]=np.inf # set zero entries to inf
            A[I==1]=0 # except diagonal which should be zero
            for i in range(n):
                r = A[i,:]
                A = np.minimum(A, r + r.T)
            self.__D = np.matrix(A,dtype=int)
            
        return self.__D  
        
    D = distance_matrix
    
    def reciprocal_distance_matrix(self):
        """ Return Reciprocal Distance matrix """

        import numpy as np;

        rd = np.matrix(self.distance_matrix(),dtype=float)
        # probably there exists more python way to apply a function to each element of matrix
        for i in range(self.__Order):
            for j in range(self.__Order):
                if not rd[i,j] == 0: rd[i,j] = 1 / rd[i,j]
        
        return rd

    
    def resistance_distance_matrix(self):
        """ Return Resistance Distance matrix """
        
        if not self.is_connected() or self.__Order == 0:
            return False
            
        if self.__RD == []:
            import numpy as np
            #from numpy import linalg as la
            n = self.__Order
            s = n*self.laplacian_matrix() + 1
            sn = n* np.linalg.inv(s)
            RD = np.ndarray((n,n))
            for i in range(n):
                for j in range(n):
                    RD[i,j] = sn[i,i] + sn[j,j] - 2*sn[i,j]
            self.__RD = RD
            
        return self.__RD
    #
    #
    # Graph invariants
    #
    #
    
    def diameter(self):
        """ Return diameter of the graph
        
        Diameter is the maximum value of distance matrix
        """
        return self.distance_matrix().max()
        
    
        
    def degrees(self):
        """ Return degree of the vertex
        
        Alias : deg
        """
        if self.__Degrees == []:
            self.__Degrees = map(lambda r: sum(r) , self.__A)
        ## calcuate degrees for all vertices
        return self.__Degrees
        
    deg = degrees
                
                
    def eccentricity(self):
        """ Eccentricity of the graph for all its vertices"""
        if self.__Order == 0: return None
        
        return self.distance_matrix().max(axis=0).tolist()[0]
        
        
        
    def distances_from_vertex(self, v):
        """ Return list of all distances from a given vertex to all others"""
        # used to test graph where it is connected or not
        seen={}  
        level=0  
        nextlevel=[v]
        while nextlevel:
            thislevel=nextlevel 
            nextlevel=[] 
            for v in thislevel:
                if v not in seen: 
                    seen[v]=level 
                    nb = [i for (i,j) in zip(range(len(self.__A[v])), self.__A[v]) if j!=0]
                    nextlevel.extend(nb)
            #if (cutoff is not None and cutoff <= level):  break
            level=level+1
        return seen
        
        
        
    def is_connected(self):
        """ Return True/False depends on the graph is connected or not """ 
        if self.__Order == 0: return False
         
        if self.__Is_connected is None:
            # we take vertex 0 and check whether we can reach all other vertices 
            self.__Is_connected = len(self.distances_from_vertex(0)) == self.order()
        return self.__Is_connected
        
        
            
    #
    #
    # Graph spectra
    #
    #
    
    def spectrum(self, matrix="adjacency"):
        r""" Calculates spectrum of the graph
    
        args:
            matrix (str)
                'adjacency'             or 'A' : default
                'laplacian'             or 'L'
                'distance'              or 'D'
                'signless_laplacian'    or 'Q'
                'normalized_laplacian'  or 'NL'
                'resistance_distance'   or 'RD'
                'reciprocal_distance'
                
        """
        if self.__Order == 0: return []
        
        if matrix == "adjacency" or matrix == "A":
            if self.__Spectrum == []:
                from numpy import linalg as la
                s = la.eigvalsh(self.__A).tolist()
                s.sort(reverse=True)
                self.__Spectrum = s
            return self.__Spectrum
                
        elif matrix == "laplacian" or matrix == "L":
            if self.__Laplacian_spectrum == []:
                from numpy import linalg as la
                s = la.eigvalsh(self.laplacian_matrix()).tolist()
                s.sort(reverse=True)
                self.__Laplacian_spectrum = map(lambda x: x if x>0 else 0,s)
            return self.__Laplacian_spectrum
            
        elif matrix == "distance" or matrix == "D":
            if self.__Distance_spectrum == []:
                from numpy import linalg as la
                s = la.eigvalsh(self.distance_matrix()).tolist()
                s.sort(reverse=True)
                self.__Distance_spectrum = s
            return self.__Distance_spectrum  
        
        elif matrix == "signless_laplacian" or matrix == "Q":
            if self.__Signless_laplacian_spectrum == []:
                ## TODO: check if we have zeros in degrees()
                from numpy import linalg as la
                s = la.eigvalsh(self.signless_laplacian_matrix()).tolist()
                s.sort(reverse=True)
                self.__Signless_laplacian_spectrum = map(lambda x: x if x>0 else 0,s)
            return self.__Signless_laplacian_spectrum  

        elif matrix == "normalized_laplacian" or matrix == "NL":
            if self.__Norm_laplacian_spectrum == []:
                ## TODO: check if we have zeros in degrees()
                from numpy import linalg as la
                s = la.eigvalsh(self.normalized_laplacian_matrix()).tolist()
                s.sort(reverse=True)
                self.__Norm_laplacian_spectrum = s
            return self.__Norm_laplacian_spectrum  

        elif matrix == "resistance_distance" or matrix == "RD":
            if self.__RD_spectrum == []:
                from numpy import linalg as la
                s = la.eigvalsh(self.resistance_distance_matrix()).tolist()
                s.sort(reverse=True)
                self.__RD_spectrum = s
            return self.__RD_spectrum
        # NO CACHE
        elif matrix == "reciprocal_distance" :
            s = la.eigvalsh(self.reciprocal_distance_matrix()).tolist()
            s.sort(reverse=True)
            return s
       
        else:
            return False        
    
    
    def spectral_moment(self, k, matrix="adjacency"):
        """ Return k-th spectral moment
        
        parameters: matrix - see spectrum help
        """
        from numpy import power
        return power(self.spectrum(matrix),k).tolist()
    
        
    def energy(self, matrix="adjacency"):
        """ Return energy of the graph 
        
        parameters: matrix - see spectrum help
        """
        return sum( map( lambda x: abs(x) ,self.spectrum(matrix)))
                
                
    def incidence_energy(self):
        """ Return incidence energy (IE)
            
        Incidence energy is the sum of singular values of incidence matrix
        """
        if self.__Order == 0: return []
        from numpy.linalg import svd
        return sum(svd(self.incidence_matrix(), compute_uv=False))

    #
    #
    # Chemical indices
    #
    #
    
    def zagreb_m1_index(self):
        """ Calculates Zagreb M1 Index """    
        return sum(map(lambda d: d**2, self.degrees()))
        
    
    def zagreb_m2_index(self):
        """ Calculates Zagreb M2 Index 
        
        The molecular graph must contain at least one edge, otherwise the function Return False
        Zagreb M2 Index is a special case of Connectivity Index with power = 1"""
        return sum( map(lambda (e1, e2): self.degrees()[e1]*self.degrees()[e2] , self.edges()) )    

    
    def connectivity_index(self, power):
        """ Calculates Connectivity index (R)"""
        E = self.edges() # E - all edges
        if len(E) == 0: return 0
        return sum( map(lambda (e1 ,e2): ( self.degrees()[e1]*self.degrees()[e2] ) ** power , E) )

    
    def eccentric_connectivity_index(self):
        """ Calculates Eccentric Connectivity Index 
        
        The molecuar graph must be connected, otherwise the function Return False"""
        if not self.is_connected():
            return False 
        max_dist = map(lambda row: row.max() , self.distance_matrix())
        return sum( map( lambda a,b: a*b, self.degrees(), max_dist ) )
        
    
    def randic_index(self):
        """ Calculates Randic Index 
        
        The molecular graph must contain at least one edge, otherwise the function Return False
        Randic Index is a special case of Connectivity Index with power = -1/2"""
        return self.connectivity_index(-0.5)
                        
    
    def atom_bond_connectivity_index(self):
        """ Calculates Atom-Bond Connectivity Index (ABC) """
        s = 0.0 # summator
        for (u,v) in self.edges():
            d1 = self.degrees()[u]
            d2 = self.degrees()[v]
            s += ( 1.0* (d1 + d2 - 2 ) / (d1 * d2)) ** .5
        return s   
    
    
    def estrada_index(self, matrix = "adjacency"):
        """ Calculates Estrada Index (EE)  
        
        args:
            matrix -- see spectrum for help, default value is 'adjacency'
            
        There is an alias 'distance_estrada_index' for distance matrix
        """
        from numpy import exp        
        return sum( map( lambda x: exp( x.real ) , self.spectrum(matrix) ) ) 
        
        
    def distance_estrada_index(self):
        """ Calculates Distance Estrada Index (DEE) 
        
        Special case of Estrada index with distance matrix
        """
        return self.estrada_index('distance')
    
    
    
    def degree_distance(self):
        """ Calculates Degree Distance (DD)
        
        The molecuar graph must be connected, otherwise the function Return False"""
        if not self.is_connected():
            return False      
        from numpy import matrix
        dd = matrix(self.degrees()) * self.distance_matrix().sum(axis=1)
        return dd[0,0]
        
    def reverse_degree_distance(self):
        """ Calculates Reverse Distance Degree (rDD)
        
        The molecuar graph must be connected, otherwise the function Return False"""
        if not self.is_connected():
            return False 
        return 2*( self.order()-1 ) * len(self.edges()) * self.diameter() - self.degree_distance()
    
    
    def molecular_topological_index(self):
        """ Calculates (Schultz) Molecular Topological Index (MTI)
        
        The molecuar graph must be connected, otherwise the function Return False"""
        if not self.is_connected():
            return False 
        # (A+D)*d
        from numpy import matrix
        A = matrix(self.__A)
        d = matrix(self.degrees())
        return ( (A + self.distance_matrix()) * d.T ).sum()
    
        
    def eccentric_distance_sum(self):
        """ Calculates Distance Sum
        
        The molecuar graph must be connected, otherwise the function Return False"""
        if not self.is_connected():
            return False 
        return (self.eccentricity() * self.distance_matrix().sum(axis=1))[0,0]
    
    
    # strange - it is slow ((
    def balaban_j_index(self):
        """ Calculates Balaban J index 
        
        The molecuar graph must be connected, otherwise the function Return False"""
        if not self.is_connected():
            return False 
        from numpy import sqrt
        ds = self.distance_matrix().sum(axis=1)
        m = len(self.edges())
        k = (m / ( m - self.__Order +2.0 ))
        return k * sum( map(lambda (u ,v): 1 / sqrt((ds[u][0,0]*ds[v][0,0])), self.edges() ))
        
    def kirchhoff_index(self):
        """ Calculates Kirchhoff Index (Kf)
        
        Kf = 1/2 * sum_i sum_j RD[i,j]
        Based on resistance distance matrix RD
        
        Alias: resistance
        
        The molecuar graph must be connected, otherwise the function Return False
        """
        if not self.is_connected():
            return False 
        return self.resistance_distance_matrix().sum() / 2
        
    resistance = kirchhoff_index
    
    def wiener_index(self):
        """ Calculates Wiener Index (W)
        
        W = 1/2 * sum_i sum_j D[i,j]
        where D is distance matrix
        The molecuar graph must be connected, otherwise the function Return False
        """
        if not self.is_connected():
            return False 
        return self.distance_matrix().sum() / 2
        
    def terminal_wiener_index(self):
        """ Calculate Terminal Wiener Index (TW)
        
        TW = Sum of all distances between pendent vertices (with degree = 1)
        """
        if not self.is_connected(): return False
        s = 0
        for u in range(self.order()):
            if self.degrees()[u] != 1: continue
            for v in range(u+1, self.order()):
                if self.degrees()[v] == 1:
                    s = s + self.distance_matrix()[u,v]
        return s

    def reverse_wiener_index(self):
        """ Calculates Reverse Wiener Index (RW)
        
        RW = 1/2 * sum_i!=j ( d - D[i,j] )
        where D is distance matrix and d is diameter
        
        The molecuar graph must be connected, otherwise the function Return False
        """
        if not self.is_connected():
            return False 
        # here we use formula: RW = 1/2 * n * (n-1) * d - W
        return  self.diameter() * (self.__Order * (self.__Order - 1)) / 2 - self.wiener_index()
        
    def hyper_wiener_index(self):
        """ Calculates Hyper-Wiener Index (WW)
        
        WW = 1/2 * ( sum_ij d(i,j)^2 + sum_i_j d(i,j) )
        where D is distance matrix

        The molecuar graph must be connected, otherwise the function Return False
        """
        if not self.is_connected():
            return False         
        from numpy import power
        return ( power(self.distance_matrix(),2).sum() + self.distance_matrix().sum() ) / 4 # since we have symmetric matrix
        
        
    def harary_index(self):
        """ Calculates Harary Index (H)
        
        H = sum_i sum_j Rd[i,j]
        where Rd is reciprocal distance matrix 
        Rd[i,j] = 1 / D[i,j] for D[i,j] != 0
        Rd[i,j] = 0 otherwise

        The molecuar graph must be connected, otherwise the function Return False
        """
        if not self.is_connected():
            return False         
        return self.reciprocal_distance_matrix().sum()
        
    def LEL(self):
        """ Return Laplacian-like energy (LEL) """
        from numpy import sqrt
        return sum( map( lambda x: sqrt(x) ,self.spectrum('laplacian')))


    # Adriatic indices
    
    def adriatic_index(self, func, inv):
        """ Adriatic index """
        if inv == 'degree': d = self.degrees()
        elif inv == 'distance': d = self.distance_matrix().sum(axis=0).tolist()[0]
        
        return sum( map( lambda (u,v): func(d[u],d[v]), self.edges()) )

            
    def randic_type_lodeg_index (self):
        """ Adriatic index: Randic-type lodeg index"""
        from numpy import log
        
        def func(du, dv):
            return log(du)*log(dv)
            
        return self.adriatic_index(func,'degree')

        
    def randic_type_sdi_index (self):
        """ Adriatic index: Randic-type sdi index"""
        
        def func(du, dv):
            return du*du*dv*dv
            
        return self.adriatic_index(func,'distance')


    def randic_type_hadi_index (self):
        """ Adriatic index: Randic-type hadi index"""
        
        def func(du, dv):
            return .5**(du+dv)
            
        return self.adriatic_index(func,'distance')
                
        
    def sum_lordeg_index (self):
        """ Adriatic index: sum lordeg index"""
        from numpy import log
        # here we use more easy for calculations formula
        return sum(map( lambda d: d*(log(d)**.5)  , self.degrees() ))
    
    
    def inverse_sum_lordeg_index(self):
        """ Adriatic index: inverse sum lordeg index"""
        from numpy import log
        
        def func(du, dv):
            return 1.0 / (log(du)**.5 + log(dv)**.5)
            
        return self.adriatic_index(func,'degree')
    
        
    def inverse_sum_indeg_index(self):
        """ Adriatic index: inverse sum indeg index"""
        
        def func(du, dv):
            return du*dv / (du + dv)
            
        return self.adriatic_index(func,'degree')
    
        
    def misbalance_lodeg_index(self):
        """ Adriatic index: misbalance lodeg index"""
        from numpy import log
        
        def func(du, dv):
            return abs( log(du) - log(dv) )
            
        return self.adriatic_index(func,'degree')
    
        
    def misbalance_losdeg_index(self):
        """ Adriatic index: misbalance losdeg index"""
        from numpy import log
        
        def func(du, dv):
            return abs( log(du)**2 - log(dv)**2 )
            
        return self.adriatic_index(func,'degree')
    
        
    def misbalance_indeg_index(self):
        """ Adriatic index: misbalance indeg index"""
        
        def func(du, dv):
            return abs( 1.0/du - 1.0/dv)
            
        return self.adriatic_index(func,'degree')
    
    
    def misbalance_irdeg_index(self):
        """ Adriatic index: misbalance irdeg index"""
        
        def func(du, dv):
            return abs( 1.0/du**.5 - 1.0/dv**.5)
            
        return self.adriatic_index(func,'degree')
        
        
    def misbalance_rodeg_index(self):
        """ Adriatic index: misbalance rodeg index"""
        
        def func(du, dv):
            return abs( du**.5 - dv**.5)
            
        return self.adriatic_index(func,'degree')
            
            
    def misbalance_deg_index(self):
        """ Adriatic index: misbalance deg index"""
        
        def func(du, dv):
            return abs( du - dv)
            
        return self.adriatic_index(func,'degree')
            
    
    def misbalance_hadeg_index(self):
        """ Adriatic index: misbalance hadeg index"""
        
        def func(du, dv):
            return abs( 2**(-du) - 2**(-dv))
            
        return self.adriatic_index(func,'degree')
                    
    
    def misbalance_indi_index(self):
        """ Adriatic index: misbalance indi index"""
        
        def func(du, dv):
            return abs( 1.0/du - 1.0/dv)
            
        return self.adriatic_index(func,'distance')
            
            
    def min_max_rodeg_index(self):
        """ Adriatic index: min-max rodeg index"""
        
        def func(du, dv):
            return ( min(dv,du) / max(dv,du) )**.5
            
        return self.adriatic_index(func,'degree')        
                
        
    def min_max_sdi_index(self):
        """ Adriatic index: min-max sdi index"""
        
        def func(du, dv):
            return ( min(dv,du) / max(dv,du) )**2
            
        return self.adriatic_index(func,'distance')  
    
    
    def max_min_deg_index(self):
        """ Adriatic index: max-min deg index"""
        
        def func(du, dv):
            return max(dv,du) / min(dv,du)
            
        return self.adriatic_index(func,'degree')
    
    
    def max_min_sdeg_index(self):
        """ Adriatic index: max-min sdeg index"""
        
        def func(du, dv):
            return ( max(dv,du) / min(dv,du) )**2
            
        return self.adriatic_index(func,'degree')
    
    
    def symmetric_division_deg_index(self):
        """ Adriatic index: symmetric division deg index"""
        
        def func(du, dv):
            # it is faster then min / max + max / min
            return  float(du + dv)**2 / du*dv - 2

        return self.adriatic_index(func,'degree')
        
        
        
    