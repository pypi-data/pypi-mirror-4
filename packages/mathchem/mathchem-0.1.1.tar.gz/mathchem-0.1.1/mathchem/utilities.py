from mathchem import *

          
def batch_process(infile, file_format, outfile, function, hydrogens=False) :
    """ Read file molecule-by-molecule and apply a <function> to each molecule
    Good for large files containing thousands of molecules
    """
    
    f_out = open(outfile, 'w')
    f_in = open(infile, 'r')
    
    if file_format == 'g6':
        for line in f_in:
            #line = f_in.readline()
            m = Mol(line)
            f_out.write(str(function(m))+"\n")
            
    elif file_format =='sdf':
        while True:
            m = _read_sdf_molecule(f_in, hydrogens)
            if m == False: break
            f_out.write(str(function(m))+"\n")
    
    elif file_format =='mol2':
        while True:
            m = _read_mol2_molecule(f_in, hydrogens)
            if m == False: break
            f_out.write(str(function(m))+"\n")
            
    # TODO: read the directory because mol file contain only one molecule
    elif file_format =='mol':
        m = read_from_mol(f_in, hydrogens)
        if m != False:
            f_out.write(str(function(m))+"\n")
        
    
    f_in.close()
    f_out.close()



# functions which read all the file and return list of Mol instances

def read_from_sdf(fname, hydrogens = False):
    """
    Read the whole .sdf file and return list of Mol instances
    """

    f_in = open(fname, 'r')
    mols = []

    while True:
        m = _read_sdf_molecule(f_in, hydrogens)
        if m == False: break
        mols.append(m)
    
    f_in.close()
    return mols

def read_from_mol(fname, hydrogens = False):
    """
    Read the whole .mol file and return Mol instance
    """

    f_in = open(fname, 'r')

    m = _read_sdf_molecule(f_in, hydrogens)
    
    f_in.close()
    return m

def read_from_mol2(fname, hydrogens = False):
    """
    Read the whole .mol2 file and return list of Mol instances
    """
    
    f_in = open(fname, 'r')
    mols = []

    while True:
        m = _read_mol2_molecule(f_in, hydrogens)
        if m == False: break
        mols.append(m)
    
    f_in.close()
    return mols
    
def read_from_g6(fname):
    """
    Read the whole .g6 file and return list of Mol instances
    """
    
    f_in = open(fname, 'r')
    mols = []

    for line in f_in:
        mols.append(Mol(line))

    f_in.close()
    return mols   


def read_from_NCI_by_name(name, hydrogens = False):
    import urllib
    url = 'http://cactus.nci.nih.gov/cgi-bin/nci2.1.tcl?op1=name&data1='+name+'&method1=substring&output=sdf&nomsg=1&maxhits=1000000'
    f = urllib.urlretrieve(url)
    return read_from_sdf(f[0], hydrogens)

def read_from_NCI_by_NSC(num, hydrogens = False):
    import urllib
    url = 'http://cactus.nci.nih.gov/cgi-bin/nci2.1.tcl?op1=nsc&data1='+num+'&output=sdf&nomsg=1&maxhits=1000000'
    f = urllib.urlretrieve(url)
    return read_from_sdf(f[0], hydrogens)

def read_from_NCI_by_CAS(num, hydrogens = False):
    import urllib
    url = 'http://cactus.nci.nih.gov/cgi-bin/nci2.1.tcl?op1=cas&data1='+num+'&output=sdf&nomsg=1&maxhits=1000000'
    f = urllib.urlretrieve(url)
    return read_from_sdf(f[0], hydrogens)

    
# functions which parse a fragment of file and initialize Mol instance

# read a single molecule from file
def _read_sdf_molecule(file, hydrogens = False):
    # read the header 3 lines
    for i in range(3):
        file.readline()
    line = file.readline()
    
    if line == '': return False
    
    # this does not work for 123456 which must be 123 and 456
    #(atoms, bonds) = [t(s) for t,s in zip((int,int),line.split())]
    atoms = int(line[:3])
    bonds = int(line[3:6])
    
    order = atoms
    
    v = [];
    
    for i in range( atoms ):
        line = file.readline()
        symbol = line.split()[3]
        
        if hydrogens == False and (symbol == 'H' or symbol == 'h'):
            order = order - 1
        else:
            v.append(i+1);
            
    
    # fill the matrix A zeros
    A = [[0 for col in range(order)] for row in range(order)]
    edges = []
    
    for i in range( bonds ):
        line = file.readline()
        #(a1, a2) = [t(s) for t,s in zip((int,int),line.split())]
        a1 = int(line[:3])
        a2 = int(line[3:6])

        if a1 in v and a2 in v:
            # add edge here!
            k = v.index(a1)
            j = v.index(a2)
            A[k][j] = 1
            A[j][k] = 1
            edges.append((k,j))
    
    
    while line !='':
        line = file.readline()
        if line[:4] == "$$$$": break
        
    m = Mol()
    m._set_A(A)
    m._set_Order(order)
    m._set_Edges(edges)
    
    return m
    
    
# read a single molecule from file
def _read_mol2_molecule(file, hydrogens = False):

    # seek for MOLECULE tag
    line = file.readline()
    
    while line != '':
        if line.strip() == '@<TRIPOS>MOLECULE': break
        line = file.readline()


    if line == '': return False
    #skip molecule name
    file.readline()

    # read
    line = file.readline()

    
    atoms = int(line.split()[0])
    # TODO: number of bonds may not be present
    bonds = int(line.split()[1])
    
    #print atoms, bonds
        
    order = atoms
    
    v = [];
    
    # seek for ATOM tag
    line = file.readline()
    while line != '':
        if line.strip() == '@<TRIPOS>ATOM': break
        line = file.readline()
       
    for i in range( atoms ):
        line = file.readline()
        arr = line.split()
        id = int(arr[0])
        symbol = arr[4]
        
        if hydrogens == False and (symbol == 'H' or symbol == 'h'):
            order = order - 1
        else:
            v.append(id);
            
    
    # fill the matrix A zeros
    A = [[0 for col in range(order)] for row in range(order)]
    edges = []
    
    #seek for bonds tag @<TRIPOS>BOND
    line = file.readline()
    while line !='':
        if line.strip() == '@<TRIPOS>BOND': break
        line = file.readline()
        
    if line == '': return False
    
    
    for i in range( bonds ):
        line = file.readline()
        (bid, a1, a2) = [t(s) for t,s in zip((int, int,int),line.split())]


        if a1 in v and a2 in v:
            # add edge here!
            k = v.index(a1)
            j = v.index(a2)
            A[k][j] = 1
            A[j][k] = 1
            edges.append((k,j))
        
    m = Mol()
    m._set_A(A)
    m._set_Order(order)
    m._set_Edges(edges)
    
    return m

    