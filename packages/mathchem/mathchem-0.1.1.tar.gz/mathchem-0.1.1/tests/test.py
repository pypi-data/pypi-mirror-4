import mathchem as mc
import mathchem.utilities as u

infile = '/Users/Hamster3d/Documents/PhD/Data/graph7c.g6'
outfile = '/Users/Hamster3d/Documents/PhD/Data/graph7c_result.txt'
#u.batch_process(infile, 'g6', outfile, lambda x: x.wiener_index())


ms = u.read_from_g6(infile)

print [(x.energy(), x.energy('laplacian')) for x in ms]






from mathchem import *
# retreive compounds with NSC number from 1 to 10000
>>> mols = read_from_NCI_by_NSC('1-10000')
>>> len(mols)
9787
# some of the numbers does not refer to any compound

# some of the compounds are not connected
# let's filter them by calling is_connected method of each instance
>>> mols_c = filter(lambda x: x.is_connected(), mols)
>>> len(mols_c)
9496
# all theses compounds will not contain infinity in their distance matrix



sage: import mathchem as mc
sage: mols = mc.read_from_NCI_by_NSC('1-1000')
sage: len(mols)
993
sage: mols_c = filter(lambda m: m.is_connected(), mols)
sage: len(mols_c)
980
sage: bj = [m.balaban_j_index() for m in mols_c]
sage: bj = map(lambda m: m.balaban_j_index(), mols_c)

sage: bar_chart(bj)
sage: m1 = [m.zagreb_m1_index() for m in mols_c]
sage: m2 = [m.zagreb_m2_index() for m in mols_c]
sage: scatter_plot(zip(m1,m2))
sage: scatter_plot(zip(m1,m2), markersize=1).show(figsize=[8,4], dpi=300)

......image here .....





import mathchem as mc
mols = mc.read_from_NCI_by_NSC('1-5000')
mols_c = filter(lambda m: m.is_connected(), mols)

print 'Test set of ', len(mols_c), 'compounds'
orders = [m.order() for m in mols_c]
hist_data = [0]*max(orders)
for i in orders:
    hist_data[i-1] = hist_data[i-1]+1
bar_chart(hist_data).show(figsize=[10,2])

methods = ['order','diameter', 'energy', 'incidence_energy', 'zagreb_m1_index', 'zagreb_m2_index', 'eccentric_connectivity_index', 'randic_index', 'atom_bond_connectivity_index', 'estrada_index', 'degree_distance', 'reverse_degree_distance', 'molecular_topological_index', 'eccentric_distance_sum', 'balaban_j_index', 'kirchhoff_index', 'wiener_index', 'terminal_wiener_index', 'reverse_wiener_index', 'hyper_wiener_index', 'harary_index', 'LEL', 'randic_type_lodeg_index', 'randic_type_sdi_index', 'randic_type_hadi_index', 'sum_lordeg_index', 'inverse_sum_lordeg_index', 'inverse_sum_indeg_index', 'misbalance_lodeg_index', 'misbalance_losdeg_index', 'misbalance_irdeg_index', 'misbalance_rodeg_index', 'misbalance_deg_index', 'misbalance_hadeg_index','misbalance_indi_index', 'min_max_rodeg_index', 'min_max_sdi_index', 'max_min_deg_index', 'max_min_sdeg_index', 'symmetric_division_deg_index']



import scipy.stats as stats
@interact
def index_correlations(index_A = selector(methods,label="Index A"), index_B = selector(methods,label="Index B")):
    data_A = [getattr(m, index_A)() for m in mols_c]
    data_B = [getattr(m, index_B)() for m in mols_c]
    data = zip(data_A, data_B)
    slope, intercept, r, ttprob, stderr = stats.linregress(data)
    
    print 'Correlation coefficient: ', r
    canvas = scatter_plot(data) + plot(slope*x+intercept,min(data_A),max(data_A))
    canvas.show(figsize=[10,4], axes_labels=[index_A, index_B])

