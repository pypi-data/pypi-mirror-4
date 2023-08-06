"""
Brief
-----
A library for analysing codon usage bias with the quasispecies model.

Summary
-------


Routines
--------

All included routines::
    CodonUsage
    Fitnessfunction
    Model
    __builtins__
    __doc__
    __file__
    __name__
    __package__
    c_codon_mut_dist
    calculate_CAI_dic
    calculate_NC
    calculate_RF
    calculate_RF_dic
    calculate_RSCU
    calculate_RSCU_dic
    change_amino_acid_code
    codon_hist_index
    codon_index
    codon_mut_dist
    codon_table
    codons
    compute_distance
    compute_optimum
    compute_optimum_two_step
    compute_steady_state
    config_from_file
    decomposition
    euclidean_distance
    hessian_em
    highly_expressed_genes_by_file
    highly_expressed_genes_by_id
    init_fitnessfunctions
    init_fitnessmatrix_for_amino_acids
    init_fitnessmatrix_for_codons
    init_list_of_genes
    is_ambig_codon
    kl_distance
    load_fasta
    load_fasta_from_url
    load_genbank
    load_plaintext
    make_codon_histogram
    make_codon_histogram_dic
    make_codon_histogram_dic_combined
    make_evolmatrix
    make_jc69_mutationmatrix
    make_mutationmatrix
    mds_from_fasta
    minimize
    number_of_codons
    optimize
    optimize_dic
    optimize_sequence
    parametric_run_from_config
    plot_all_reduction_methods
    plot_mds
    plot_pca
    py_codon_mut_dist
    relative_cosine_distance
    relative_euclidean_distance
    relative_hellinger_distance
    relative_jeffrey_divergence
    relative_minkowski_distance
    remove_stopcodons_and_one_codon_amino_acids
    remove_stopcodons_and_one_codon_amino_acids_dic
    run_model
    sample_run
    setup_parser
    transition

Examples
--------

"""
number_of_codons = 21

import doctest
from Bio import SeqIO
import sys
import argparse
import json
import time
import itertools
import numpy as np
import scipy as sp
import scipy.linalg
import scipy.sparse
import scipy.sparse.linalg
import scipy.spatial
from Bio import SeqIO
import pylab as p
import pprint
from sklearn import manifold
from sklearn import decomposition
import scipy
from scipy import weave
import numpy as np
import collections
import urllib2

# make a codon table
bases = ['t', 'c', 'a', 'g']
codons = [a + b + c for a in bases for b in bases for c in bases]


#from ncbi genetic codes
genetic_codes = collections.OrderedDict({})
genetic_codes['The Standard Code']                                        = 'FFLLSSSSYY**CC*WLLLLPPPPHHQQRRRRIIIMTTTTNNKKSSRRVVVVAAAADDEEGGGG'
genetic_codes['The Vertebrate Mitochondrial Code']                        = 'FFLLSSSSYY**CCWWLLLLPPPPHHQQRRRRIIMMTTTTNNKKSS**VVVVAAAADDEEGGGG'
genetic_codes['The Yeast Mitochondrial Code']                             = 'FFLLSSSSYY**CCWWTTTTPPPPHHQQRRRRIIMMTTTTNNKKSSRRVVVVAAAADDEEGGGG'
genetic_codes['The Mold, Protozoan, and Coelenterate Mitochondrial Code'] = 'FFLLSSSSYY**CCWWLLLLPPPPHHQQRRRRIIIMTTTTNNKKSSRRVVVVAAAADDEEGGGG'
genetic_codes['The Invertebrate Mitochondrial Code']                      = 'FFLLSSSSYY**CCWWLLLLPPPPHHQQRRRRIIMMTTTTNNKKSSSSVVVVAAAADDEEGGGG'
genetic_codes['The Ciliate, Dasycladacean and Hexamita Nuclear Code']     = 'FFLLSSSSYYQQCC*WLLLLPPPPHHQQRRRRIIIMTTTTNNKKSSRRVVVVAAAADDEEGGGG'
genetic_codes['The Echinoderm and Flatworm Mitochondrial Code']           = 'FFLLSSSSYY**CCWWLLLLPPPPHHQQRRRRIIIMTTTTNNNKSSSSVVVVAAAADDEEGGGG'
genetic_codes['The Euplotid Nuclear Code']                                = 'FFLLSSSSYY**CCCWLLLLPPPPHHQQRRRRIIIMTTTTNNKKSSRRVVVVAAAADDEEGGGG'
genetic_codes['The Bacterial, Archaeal and Plant Plastid Code']           = 'FFLLSSSSYY**CC*WLLLLPPPPHHQQRRRRIIIMTTTTNNKKSSRRVVVVAAAADDEEGGGG'
genetic_codes['The Alternative Yeast Nuclear Code']                       = 'FFLLSSSSYY**CC*WLLLSPPPPHHQQRRRRIIIMTTTTNNKKSSRRVVVVAAAADDEEGGGG'
genetic_codes['The Ascidian Mitochondrial Code']                          = 'FFLLSSSSYY**CCWWLLLLPPPPHHQQRRRRIIMMTTTTNNKKSSGGVVVVAAAADDEEGGGG'
genetic_codes['The Alternative Flatworm Mitochondrial Code']              = 'FFLLSSSSYYY*CCWWLLLLPPPPHHQQRRRRIIIMTTTTNNNKSSSSVVVVAAAADDEEGGGG'
genetic_codes['The Blepharisma Nuclear Code']                             = 'FFLLSSSSYY*QCC*WLLLLPPPPHHQQRRRRIIIMTTTTNNKKSSRRVVVVAAAADDEEGGGG'
genetic_codes['Chlorophycean Mitochondrial Code']                         = 'FFLLSSSSYY*LCC*WLLLLPPPPHHQQRRRRIIIMTTTTNNKKSSRRVVVVAAAADDEEGGGG'
genetic_codes['Trematode Mitochondrial Code']                             = 'FFLLSSSSYY**CCWWLLLLPPPPHHQQRRRRIIMMTTTTNNNKSSSSVVVVAAAADDEEGGGG'
genetic_codes['Scenedesmus obliquus mitochondrial Code']                  = 'FFLLSS*SYY*LCC*WLLLLPPPPHHQQRRRRIIIMTTTTNNKKSSRRVVVVAAAADDEEGGGG'
genetic_codes['Thraustochytrium Mitochondrial Code']                      = 'FF*LSSSSYY**CC*WLLLLPPPPHHQQRRRRIIIMTTTTNNKKSSRRVVVVAAAADDEEGGGG'
genetic_codes['Pterobranchia mitochondrial code']                         = 'FFLLSSSSYY**CCWWLLLLPPPPHHQQRRRRIIIMTTTTNNKKSSSKVVVVAAAADDEEGGGG'


amino_acids = genetic_codes['The Standard Code']
amino_acids_unique = ''.join( [ amino_acids[i]   for i in range(len(amino_acids)) if amino_acids.index(amino_acids[i]) == i ] )

#characters that, if the codon contains them, codes for more than one codon.
ambig_fasta_chars = list('RYKMSWBDHVNX-'.lower())

#dictionary with codons:amino_acids
codon_table = collections.OrderedDict( dict( zip( codons, amino_acids ) ) )
amino_table_index = collections.OrderedDict(dict( zip( amino_acids_unique, range( len( amino_acids_unique ) ) ) ))
# make a codon index hash
index = range( 0, 64 )
codon_hist_index = collections.OrderedDict(dict( zip( codons, index ) ))
aa_hist_index = collections.OrderedDict(dict( zip() ))
# reverse codon table
rev_codon_table = {}
for k, v in codon_table.iteritems():
        rev_codon_table[v] = rev_codon_table.get( v, [] )
        rev_codon_table[v].append( k )
codon_index = collections.OrderedDict(dict( zip( codons, range( len( codons ) ) ) ))




#if we want to change the amino acid code over different .py's we have to wrap a in [a] since
#a cannot be changed nonlocally but using lists this works. This is a horrible substitute for
#the python3 `nonlocal` statement, that is sadly not implemented in py2.7.
#looking at what I have to do to change it globally makes me sad :( ... but, yeah... it works
amino_acids_wrap = [ amino_acids ]
amino_acids = amino_acids_wrap[0]

amino_acids_unique_wrap = [ amino_acids_unique ]
codon_table_wrap = [ codon_table ]
#global amino_table_index
#global codon_hist_index
#global aa_hist_index
#global rev_codon_table
#global codon_index
#global genetic_codes


def update_tables():
    global amino_acids
    global amino_acids_wrap
    amino_acids = amino_acids_wrap[0]
    #print amino_acids_wrap[0]


def is_ambig_codon(codon):
    """
    Summary
    -------
    Tests whether the string `codon` contains an ambigous letter that is found in `ambig_fasta_chars`

    Parameters
    ---------
    codon:str
        nucleotide sequence

    Examples
    --------

    The table of codons, `codons` should not contain any ambigous codons
    >>> map(is_ambig_codon,codons)
    [False, False, False, False, False, False, False, False, False, False, False, False, False, False, False, False, False, False, False, False, False, False, False, False, False, False, False, False, False, False, False, False, False, False, False, False, False, False, False, False, False, False, False, False, False, False, False, False, False, False, False, False, False, False, False, False, False, False, False, False, False, False, False, False]

    However, the string 'aay' should
    >>> is_ambig_codon('aay')
    True
    """
    global ambig_fasta_chars

    for letter in codon:
        if letter in ambig_fasta_chars:
            return True
    return False



def change_amino_acid_code(code_name):
    """
    Summary
    -------
    Various organisms have different genetic codes. Given the `code_name` which must be a member of `genetic_codes`
    the global dictionaries for translating codons into amino acids are reset with the genetic code you want.::

        genetic_codes['The Standard Code']                                        = 'FFLLSSSSYY**CC*WLLLLPPPPHHQQRRRRIIIMTTTTNNKKSSRRVVVVAAAADDEEGGGG'
        genetic_codes['The Vertebrate Mitochondrial Code']                        = 'FFLLSSSSYY**CCWWLLLLPPPPHHQQRRRRIIMMTTTTNNKKSS**VVVVAAAADDEEGGGG'
        genetic_codes['The Yeast Mitochondrial Code']                             = 'FFLLSSSSYY**CCWWTTTTPPPPHHQQRRRRIIMMTTTTNNKKSSRRVVVVAAAADDEEGGGG'
        genetic_codes['The Mold, Protozoan, and Coelenterate Mitochondrial Code'] = 'FFLLSSSSYY**CCWWLLLLPPPPHHQQRRRRIIIMTTTTNNKKSSRRVVVVAAAADDEEGGGG'
        genetic_codes['The Invertebrate Mitochondrial Code']                      = 'FFLLSSSSYY**CCWWLLLLPPPPHHQQRRRRIIMMTTTTNNKKSSSSVVVVAAAADDEEGGGG'
        genetic_codes['The Ciliate, Dasycladacean and Hexamita Nuclear Code']     = 'FFLLSSSSYYQQCC*WLLLLPPPPHHQQRRRRIIIMTTTTNNKKSSRRVVVVAAAADDEEGGGG'
        genetic_codes['The Echinoderm and Flatworm Mitochondrial Code']           = 'FFLLSSSSYY**CCWWLLLLPPPPHHQQRRRRIIIMTTTTNNNKSSSSVVVVAAAADDEEGGGG'
        genetic_codes['The Euplotid Nuclear Code']                                = 'FFLLSSSSYY**CCCWLLLLPPPPHHQQRRRRIIIMTTTTNNKKSSRRVVVVAAAADDEEGGGG'
        genetic_codes['The Bacterial, Archaeal and Plant Plastid Code']           = 'FFLLSSSSYY**CC*WLLLLPPPPHHQQRRRRIIIMTTTTNNKKSSRRVVVVAAAADDEEGGGG'
        genetic_codes['The Alternative Yeast Nuclear Code']                       = 'FFLLSSSSYY**CC*WLLLSPPPPHHQQRRRRIIIMTTTTNNKKSSRRVVVVAAAADDEEGGGG'
        genetic_codes['The Ascidian Mitochondrial Code']                          = 'FFLLSSSSYY**CCWWLLLLPPPPHHQQRRRRIIMMTTTTNNKKSSGGVVVVAAAADDEEGGGG'
        genetic_codes['The Alternative Flatworm Mitochondrial Code']              = 'FFLLSSSSYYY*CCWWLLLLPPPPHHQQRRRRIIIMTTTTNNNKSSSSVVVVAAAADDEEGGGG'
        genetic_codes['The Blepharisma Nuclear Code']                             = 'FFLLSSSSYY*QCC*WLLLLPPPPHHQQRRRRIIIMTTTTNNKKSSRRVVVVAAAADDEEGGGG'
        genetic_codes['Chlorophycean Mitochondrial Code']                         = 'FFLLSSSSYY*LCC*WLLLLPPPPHHQQRRRRIIIMTTTTNNKKSSRRVVVVAAAADDEEGGGG'
        genetic_codes['Trematode Mitochondrial Code']                             = 'FFLLSSSSYY**CCWWLLLLPPPPHHQQRRRRIIMMTTTTNNNKSSSSVVVVAAAADDEEGGGG'
        genetic_codes['Scenedesmus obliquus mitochondrial Code']                  = 'FFLLSS*SYY*LCC*WLLLLPPPPHHQQRRRRIIIMTTTTNNKKSSRRVVVVAAAADDEEGGGG'
        genetic_codes['Thraustochytrium Mitochondrial Code']                      = 'FF*LSSSSYY**CC*WLLLLPPPPHHQQRRRRIIIMTTTTNNKKSSRRVVVVAAAADDEEGGGG'
        genetic_codes['Pterobranchia mitochondrial code']                         = 'FFLLSSSSYY**CCWWLLLLPPPPHHQQRRRRIIIMTTTTNNKKSSSKVVVVAAAADDEEGGGG'

    Parameters
    --------
    code_name:str
        the name of the code which must be a key of `genetic_codes`

    Examples
    --------

    After changing the genetic code to something different than the standard code, the global amino_acids variable should
    have changed to the new code.
    >>> _=change_amino_acid_code('The Mold, Protozoan, and Coelenterate Mitochondrial Code')
    >>> amino_acids_wrap[0]
    'FFLLSSSSYY**CCWWLLLLPPPPHHQQRRRRIIIMTTTTNNKKSSRRVVVVAAAADDEEGGGG'

    """

    global amino_acids
    global amino_acids_wrap

    #global amino_acids
    global amino_acids_unique
    global codon_table
    global amino_table_index
    global codon_hist_index
    global aa_hist_index
    global rev_codon_table
    global codon_index
    global genetic_codes
    global amino_acids_wrap

    if not genetic_codes.has_key(code_name):
        print 'genetic code not valid!'
        raise Exception('genetic code not valid')

    amino_acids_wrap[0] = genetic_codes[code_name]
    amino_acid = amino_acids_wrap[0]

    amino_acids_unique = ''.join( [ amino_acids[i]   for i in range(len(amino_acids)) if amino_acids.index(amino_acids[i]) == i ] )

    codon_table = dict( zip( codons, amino_acids ) )
    amino_table_index = dict( zip( amino_acids_unique, range( len( amino_acids_unique ) ) ) )
    # make a codon index hash
    index = range( 0, 64 )
    codon_hist_index = dict( zip( codons, index ) )
    aa_hist_index = dict( zip() )
    # reverse codon table
    rev_codon_table = {}
    for k, v in codon_table.iteritems():
            rev_codon_table[v] = rev_codon_table.get( v, [] )
            rev_codon_table[v].append( k )
    codon_index = dict( zip( codons, range( len( codons ) ) ) )

    exec "update_tables()" in globals()


def load_fasta_from_url(url):
    """
    Summary
    -------
    Load fasta from a url

    Parameters
    ----------
    url:str
        url to the fasta file

    Returns
    ------
    fasta:Bio.SeqIO
        fasta file parser object from Biopython
        None, if error has occurred

    Examples
    -------

    """

    req=urllib2.Request(url)
    try:
        f = urllib2.urlopen(req)
    except urllib2.URLError as e:
        if hasattr(e, 'reason'):
            print 'We failed to reach a server.'
            print 'Reason: ', e.reason
        elif hasattr(e, 'code'):
            print 'The server couldn\'t fulfill the request.'
            print 'Error code: ', e.code
    else:
        try:
            fi = SeqIO.parse( f, 'fasta' )
            return fi
        except Exception as error:
            print "import:", filename, " failed"
            print error
            return None




def load_fasta(filename):
    """Loads a fasta file with filename as arg. Returns generator object with list of genes

    Parameters
    ----------
    filename : str
        Path to the file to load

    Returns
    -------
    fasta : Seq
        Parser from Biopython

    Examples
    --------

    If everything is right, a generator object is returned

    >>> load_fasta("testdata.ffn") # doctest: +ELLIPSIS
    <generator object parse at ...>

    The file must exist

    >>> load_fasta("yikes")
    Open: yikes  failed
    [Errno 2] No such file or directory: 'yikes'

    However, we use Biopython and the fasta file's syntax is not checked here!

    >>> load_fasta("testdata_fail.ffn") # doctest: +ELLIPSIS
    <generator object parse at ...>

    """
    try:
        f = open(filename)
        try:
            fi = SeqIO.parse( f, 'fasta' )
            return fi
        except Exception as error:
            print "import:", filename, " failed"
            print error
            return None
    except Exception as error:
        print "Open:", filename, " failed"
        print error
        return None

def load_genbank(filename):
    """loads a genbank file with filename as arg. RReturns generator object with list of gene

    Parameters
    ----------
    filename : str
        Path to the file to load

    Returns
    -------
    genes : Seq
        Parser from Biopython

    Examples
    --------

    """
    try:
        f = open(filename)
        try:
            fi = SeqIO.parse( f, 'genbank' )
            return fi
        except Exception as error:
            print "import:", filename, " failed"
            print error
            return None
    except Exception as error:
        print "Open:", filename, " failed"
        print error
        return None

    return fi

def load_plaintext(filename):
    """loads a nucleotide file with plaintext sequence. filename as arg. Returns list of genes"""
    print 'not implemented yet'
    pass

def make_codon_histogram(gene):
    """returns codon_hist,aa_hist for one gene

    Parameters
    ----------
    gene : SeqIO
        after loading fasta

    Returns
    -------
    codon_hist : dict with each gene.id as key and num_codonsx1 np.array for each codon
    aa_hist : dict with each gene.id as key and num_aax1 np.array for each aacid


    Examples
    --------

    The histogram should reproduce what www.kazusa.org.jp/codon/cgi-bin/countcodon.cgi computes
    for the gene in testdata.ffn::

        UUU 12.6(     9)  UCU  9.8(     7)  UAU 15.4(    11)  UGU  4.2(     3)
        UUC 21.1(    15)  UCC 16.9(    12)  UAC 11.2(     8)  UGC 12.6(     9)
        UUA 15.4(    11)  UCA  8.4(     6)  UAA  0.0(     0)  UGA  1.4(     1)
        UUG 12.6(     9)  UCG 12.6(     9)  UAG  0.0(     0)  UGG  5.6(     4)
        CUU  8.4(     6)  CCU  4.2(     3)  CAU  9.8(     7)  CGU 22.5(    16)
        CUC 15.4(    11)  CCC  5.6(     4)  CAC  7.0(     5)  CGC 25.3(    18)
        CUA  4.2(     3)  CCA  1.4(     1)  CAA 11.2(     8)  CGA  2.8(     2)
        CUG 53.4(    38)  CCG 23.9(    17)  CAG 19.7(    14)  CGG  5.6(     4)
        AUU 36.5(    26)  ACU  5.6(     4)  AAU 28.1(    20)  AGU  7.0(     5)
        AUC 16.9(    12)  ACC 23.9(    17)  AAC 19.7(    14)  AGC  8.4(     6)
        AUA  0.0(     0)  ACA  0.0(     0)  AAA 26.7(    19)  AGA  0.0(     0)
        AUG 29.5(    21)  ACG  9.8(     7)  AAG 14.0(    10)  AGG  1.4(     1)
        GUU 25.3(    18)  GCU 25.3(    18)  GAU 37.9(    27)  GGU 28.1(    20)
        GUC 19.7(    14)  GCC 32.3(    23)  GAC 18.3(    13)  GGC 28.1(    20)
        GUA  8.4(     6)  GCA 12.6(     9)  GAA 47.8(    34)  GGA 12.6(     9)
        GUG 32.3(    23)  GCG 35.1(    25)  GAG 18.3(    13)  GGG  9.8(     7)

    in the first field. Remember, the order of codons in this package is given in the variable codons

    >>> make_codon_histogram( load_fasta("testdata.ffn").next() )
    ([0.012640449438202247, 0.021067415730337078, 0.015449438202247191, 0.012640449438202247, 0.0098314606741573031, 0.016853932584269662, 0.0084269662921348312, 0.012640449438202247, 0.015449438202247191, 0.011235955056179775, 0.0, 0.0, 0.0042134831460674156, 0.012640449438202247, 0.0014044943820224719, 0.0056179775280898875, 0.0084269662921348312, 0.015449438202247191, 0.0042134831460674156, 0.053370786516853931, 0.0042134831460674156, 0.0056179775280898875, 0.0014044943820224719, 0.023876404494382022, 0.0098314606741573031, 0.0070224719101123594, 0.011235955056179775, 0.019662921348314606, 0.02247191011235955, 0.025280898876404494, 0.0028089887640449437, 0.0056179775280898875, 0.036516853932584269, 0.016853932584269662, 0.0, 0.029494382022471909, 0.0056179775280898875, 0.023876404494382022, 0.0, 0.0098314606741573031, 0.028089887640449437, 0.019662921348314606, 0.026685393258426966, 0.014044943820224719, 0.0070224719101123594, 0.0084269662921348312, 0.0, 0.0014044943820224719, 0.025280898876404494, 0.019662921348314606, 0.0084269662921348312, 0.032303370786516857, 0.025280898876404494, 0.032303370786516857, 0.012640449438202247, 0.0351123595505618, 0.037921348314606744, 0.018258426966292134, 0.047752808988764044, 0.018258426966292134, 0.028089887640449437, 0.028089887640449437, 0.012640449438202247, 0.0098314606741573031], [0.033707865168539325, 0.10955056179775281, 0.063202247191011238, 0.026685393258426966, 0.0014044943820224719, 0.016853932584269662, 0.0056179775280898875, 0.0351123595505618, 0.016853932584269662, 0.030898876404494381, 0.05758426966292135, 0.053370786516853931, 0.029494382022471909, 0.039325842696629212, 0.047752808988764044, 0.040730337078651688, 0.085674157303370788, 0.10533707865168539, 0.056179775280898875, 0.066011235955056174, 0.078651685393258425])

    """


    codon_hist = np.array( [0] * 64 )
    aa_hist = np.array( [0] * 21 )

    sequence = gene.seq.tostring()

    try:
        triplets = [ sequence[start:start + 3] for start in range( 0, len( sequence ), 3 ) ]
    except Exception as error:
        print "Slicing of nucleotides into triplets failed"
        print error
        return None,None

    for codon in triplets:
        codon = codon.lower()

        if is_ambig_codon(codon):
            continue

        aa = codon_table.get( codon )

        i = codon_hist_index.get( codon )

        if i != None:
            codon_hist[codon_hist_index.get( codon )] += 1
            j = amino_table_index.get( aa )
            aa_hist[j] += 1

    codon_hist = map( lambda x:x / float( np.sum( codon_hist ) ), codon_hist)
    aa_hist = map( lambda x:x / float( np.sum( aa_hist ) ), aa_hist)

    return (codon_hist, aa_hist)

def make_codon_histogram_dic_combined(f):
    """
    Summary
    -------
    make a codon and amino acid histogram from a file parser object. But this time combine all genes so that only
    one histogram is returned.

    Parameters
    --------
    f:Bio.SeqIO
        file parser object

    Returns
    -------
    codon_hist:dict['combined genome'] :: np.array x 64
        returns codon histogram

    Examples
    --------

    """

    codon_hist = {}
    aa_hist = {}

    codon_hist['combined genome'] = np.array( [0] * 64 )
    aa_hist['combined genome'] = np.array( [0] * 21 )

    for gene in f:
        s = gene.seq.tostring()
        triplets = [ s[start:start + 3] for start in range( 0, len( s ), 3 ) ]

        for codon in triplets:
            codon = codon.lower()

            if is_ambig_codon(codon):
                continue

            aa = codon_table.get( codon )

            i = codon_hist_index.get( codon )

            if i != None:
                codon_hist['combined genome'][codon_hist_index.get( codon )] += 1
                j = amino_table_index.get( aa )
                aa_hist['combined genome'][j] += 1

    codon_hist['combined genome'] = map( lambda x:x / float( np.sum( codon_hist['combined genome'] ) ), codon_hist['combined genome'] )
    aa_hist['combined genome'] = map( lambda x:x / float( np.sum( aa_hist['combined genome'] ) ), aa_hist['combined genome'] )

    return (codon_hist, aa_hist)

def make_codon_histogram_dic(f):

    """returns codon_hist for all genes in a fasta file in form of a dictionary with fasta identifiers as keys

    The histogram should reproduce what www.kazusa.org.jp/codon/cgi-bin/countcodon.cgi for the first gene in the testdata2.ffn::

        UUU 12.6(     9)  UCU  9.8(     7)  UAU 15.4(    11)  UGU  4.2(     3)
        UUC 21.1(    15)  UCC 16.9(    12)  UAC 11.2(     8)  UGC 12.6(     9)
        UUA 15.4(    11)  UCA  8.4(     6)  UAA  0.0(     0)  UGA  1.4(     1)
        UUG 12.6(     9)  UCG 12.6(     9)  UAG  0.0(     0)  UGG  5.6(     4)
        CUU  8.4(     6)  CCU  4.2(     3)  CAU  9.8(     7)  CGU 22.5(    16)
        CUC 15.4(    11)  CCC  5.6(     4)  CAC  7.0(     5)  CGC 25.3(    18)
        CUA  4.2(     3)  CCA  1.4(     1)  CAA 11.2(     8)  CGA  2.8(     2)
        CUG 53.4(    38)  CCG 23.9(    17)  CAG 19.7(    14)  CGG  5.6(     4)
        AUU 36.5(    26)  ACU  5.6(     4)  AAU 28.1(    20)  AGU  7.0(     5)
        AUC 16.9(    12)  ACC 23.9(    17)  AAC 19.7(    14)  AGC  8.4(     6)
        AUA  0.0(     0)  ACA  0.0(     0)  AAA 26.7(    19)  AGA  0.0(     0)
        AUG 29.5(    21)  ACG  9.8(     7)  AAG 14.0(    10)  AGG  1.4(     1)
        GUU 25.3(    18)  GCU 25.3(    18)  GAU 37.9(    27)  GGU 28.1(    20)
        GUC 19.7(    14)  GCC 32.3(    23)  GAC 18.3(    13)  GGC 28.1(    20)
        GUA  8.4(     6)  GCA 12.6(     9)  GAA 47.8(    34)  GGA 12.6(     9)
        GUG 32.3(    23)  GCG 35.1(    25)  GAG 18.3(    13)  GGG  9.8(     7)

    in the first field. Remember, the order of codons in this package is given in the variable codons

    >>> make_codon_histogram_dic( load_fasta("testdata2.ffn") )[0]
    {'fid|18348942|locus|VBIEscCol44059_0001|': [0.012640449438202247, 0.021067415730337078, 0.015449438202247191, 0.012640449438202247, 0.0098314606741573031, 0.016853932584269662, 0.0084269662921348312, 0.012640449438202247, 0.015449438202247191, 0.011235955056179775, 0.0, 0.0, 0.0042134831460674156, 0.012640449438202247, 0.0014044943820224719, 0.0056179775280898875, 0.0084269662921348312, 0.015449438202247191, 0.0042134831460674156, 0.053370786516853931, 0.0042134831460674156, 0.0056179775280898875, 0.0014044943820224719, 0.023876404494382022, 0.0098314606741573031, 0.0070224719101123594, 0.011235955056179775, 0.019662921348314606, 0.02247191011235955, 0.025280898876404494, 0.0028089887640449437, 0.0056179775280898875, 0.036516853932584269, 0.016853932584269662, 0.0, 0.029494382022471909, 0.0056179775280898875, 0.023876404494382022, 0.0, 0.0098314606741573031, 0.028089887640449437, 0.019662921348314606, 0.026685393258426966, 0.014044943820224719, 0.0070224719101123594, 0.0084269662921348312, 0.0, 0.0014044943820224719, 0.025280898876404494, 0.019662921348314606, 0.0084269662921348312, 0.032303370786516857, 0.025280898876404494, 0.032303370786516857, 0.012640449438202247, 0.0351123595505618, 0.037921348314606744, 0.018258426966292134, 0.047752808988764044, 0.018258426966292134, 0.028089887640449437, 0.028089887640449437, 0.012640449438202247, 0.0098314606741573031], 'fid|129049020348348942|locus|VBIEscCol44059_0001|': [0.012640449438202247, 0.021067415730337078, 0.015449438202247191, 0.012640449438202247, 0.0098314606741573031, 0.016853932584269662, 0.0084269662921348312, 0.012640449438202247, 0.015449438202247191, 0.011235955056179775, 0.0, 0.0, 0.0042134831460674156, 0.012640449438202247, 0.0014044943820224719, 0.0056179775280898875, 0.0084269662921348312, 0.015449438202247191, 0.0042134831460674156, 0.053370786516853931, 0.0042134831460674156, 0.0056179775280898875, 0.0014044943820224719, 0.023876404494382022, 0.0098314606741573031, 0.0070224719101123594, 0.011235955056179775, 0.019662921348314606, 0.02247191011235955, 0.025280898876404494, 0.0028089887640449437, 0.0056179775280898875, 0.036516853932584269, 0.016853932584269662, 0.0, 0.029494382022471909, 0.0056179775280898875, 0.023876404494382022, 0.0, 0.0098314606741573031, 0.028089887640449437, 0.019662921348314606, 0.026685393258426966, 0.014044943820224719, 0.0070224719101123594, 0.0084269662921348312, 0.0, 0.0014044943820224719, 0.025280898876404494, 0.019662921348314606, 0.0084269662921348312, 0.032303370786516857, 0.025280898876404494, 0.032303370786516857, 0.012640449438202247, 0.0351123595505618, 0.037921348314606744, 0.018258426966292134, 0.047752808988764044, 0.018258426966292134, 0.028089887640449437, 0.028089887640449437, 0.012640449438202247, 0.0098314606741573031]}


    """
    codon_hist = {}
    aa_hist = {}

    for gene in f:
        """returns codon_hist for each gene in a file"""
        codon_hist[gene.id] = np.array( [0] * 64 )
        aa_hist[gene.id] = np.array( [0] * 21 )

        s = gene.seq.tostring()
        triplets = [ s[start:start + 3] for start in range( 0, len( s ), 3 ) ]

        for codon in triplets:
            codon = codon.lower()

            if is_ambig_codon(codon):
                continue

            aa = codon_table.get( codon )

            i = codon_hist_index.get( codon )

            if i != None:
                codon_hist[gene.id][codon_hist_index.get( codon )] += 1
                j = amino_table_index.get( aa )
                aa_hist[gene.id][j] += 1

        codon_hist[gene.id] = map( lambda x:x / float( np.sum( codon_hist[gene.id] ) ), codon_hist[gene.id] )
        aa_hist[gene.id] = map( lambda x:x / float( np.sum( aa_hist[gene.id] ) ), aa_hist[gene.id] )

    return (codon_hist, aa_hist)


def calculate_RF_dic(codon_hist):
    """Calculates relative codon frequency for each gene in codon histogram


    Test against run of testdata2.ffn and handcalculated for amino acid A (codons 52 - 55) should give 0.24,0.3066,0.12,0.33

    >>> calculate_RF_dic(  (make_codon_histogram_dic( load_fasta("testdata2.ffn")))[0] ) # doctest : +NORMALIZE_WHITESPACE
    {'fid|18348942|locus|VBIEscCol44059_0001|': array([ 0.375     ,  0.625     ,  0.14102564,  0.11538462,  0.15555556,
            0.26666667,  0.13333333,  0.2       ,  0.57894737,  0.42105263,
            0.        ,  0.        ,  0.25      ,  0.75      ,  1.        ,
            1.        ,  0.07692308,  0.14102564,  0.03846154,  0.48717949,
            0.12      ,  0.16      ,  0.04      ,  0.68      ,  0.58333333,
            0.41666667,  0.36363636,  0.63636364,  0.3902439 ,  0.43902439,
            0.04878049,  0.09756098,  0.68421053,  0.31578947,  0.        ,
            1.        ,  0.14285714,  0.60714286,  0.        ,  0.25      ,
            0.58823529,  0.41176471,  0.65517241,  0.34482759,  0.11111111,
            0.13333333,  0.        ,  0.02439024,  0.29508197,  0.2295082 ,
            0.09836066,  0.37704918,  0.24      ,  0.30666667,  0.12      ,
            0.33333333,  0.675     ,  0.325     ,  0.72340426,  0.27659574,
            0.35714286,  0.35714286,  0.16071429,  0.125     ]), 'fid|129049020348348942|locus|VBIEscCol44059_0001|': array([ 0.375     ,  0.625     ,  0.14102564,  0.11538462,  0.15555556,
            0.26666667,  0.13333333,  0.2       ,  0.57894737,  0.42105263,
            0.        ,  0.        ,  0.25      ,  0.75      ,  1.        ,
            1.        ,  0.07692308,  0.14102564,  0.03846154,  0.48717949,
            0.12      ,  0.16      ,  0.04      ,  0.68      ,  0.58333333,
            0.41666667,  0.36363636,  0.63636364,  0.3902439 ,  0.43902439,
            0.04878049,  0.09756098,  0.68421053,  0.31578947,  0.        ,
            1.        ,  0.14285714,  0.60714286,  0.        ,  0.25      ,
            0.58823529,  0.41176471,  0.65517241,  0.34482759,  0.11111111,
            0.13333333,  0.        ,  0.02439024,  0.29508197,  0.2295082 ,
            0.09836066,  0.37704918,  0.24      ,  0.30666667,  0.12      ,
            0.33333333,  0.675     ,  0.325     ,  0.72340426,  0.27659574,
            0.35714286,  0.35714286,  0.16071429,  0.125     ])}


    """
    hist_rf = {}
    for gene in codon_hist:
        hist_rf[gene] = np.array( [0.] * 64 )
        for aminoacid in rev_codon_table:
            entropy = 0
            n = 0.
            new_norm = 0.
            for codon in rev_codon_table[aminoacid]:
                new_norm += codon_hist[gene][codon_hist_index.get( codon )]

            for codon in rev_codon_table[aminoacid]:
                if new_norm > 0:
                    pi = codon_hist[gene][codon_hist_index.get( codon )] / new_norm
                    hist_rf[gene][codon_hist_index.get( codon )] = codon_hist[gene][codon_hist_index.get( codon )] / new_norm
                if pi > 0.0:
                    entropy += pi * np.log2( pi )
                    n += 1.

    return hist_rf

def calculate_RF(codon_hist):
    """Calculates relative codon frequency for a codon"""

    #lazy version until i have time... :/

    testdic = {}
    testdic['test'] = codon_hist

    results = calculate_RF_dic(testdic)['test']

    return results

def calculate_RSCU_dic(codon_hist):
    """returns codon_rscu for each gene in codon histogram

    test like calculate_rf and checked against genomes.urv.es/optimizer

    >>> calculate_RSCU_dic(  (make_codon_histogram_dic( load_fasta("testdata2.ffn")))[0] )
    {'fid|18348942|locus|VBIEscCol44059_0001|': array([ 0.75      ,  1.25      ,  0.84615385,  0.69230769,  0.93333333,
            1.6       ,  0.8       ,  1.2       ,  1.15789474,  0.84210526,
            0.        ,  0.        ,  0.5       ,  1.5       ,  3.        ,
            1.        ,  0.46153846,  0.84615385,  0.23076923,  2.92307692,
            0.48      ,  0.64      ,  0.16      ,  2.72      ,  1.16666667,
            0.83333333,  0.72727273,  1.27272727,  2.34146341,  2.63414634,
            0.29268293,  0.58536585,  2.05263158,  0.94736842,  0.        ,
            1.        ,  0.57142857,  2.42857143,  0.        ,  1.        ,
            1.17647059,  0.82352941,  1.31034483,  0.68965517,  0.66666667,
            0.8       ,  0.        ,  0.14634146,  1.18032787,  0.91803279,
            0.39344262,  1.50819672,  0.96      ,  1.22666667,  0.48      ,
            1.33333333,  1.35      ,  0.65      ,  1.44680851,  0.55319149,
            1.42857143,  1.42857143,  0.64285714,  0.5       ]), 'fid|129049020348348942|locus|VBIEscCol44059_0001|': array([ 0.75      ,  1.25      ,  0.84615385,  0.69230769,  0.93333333,
            1.6       ,  0.8       ,  1.2       ,  1.15789474,  0.84210526,
            0.        ,  0.        ,  0.5       ,  1.5       ,  3.        ,
            1.        ,  0.46153846,  0.84615385,  0.23076923,  2.92307692,
            0.48      ,  0.64      ,  0.16      ,  2.72      ,  1.16666667,
            0.83333333,  0.72727273,  1.27272727,  2.34146341,  2.63414634,
            0.29268293,  0.58536585,  2.05263158,  0.94736842,  0.        ,
            1.        ,  0.57142857,  2.42857143,  0.        ,  1.        ,
            1.17647059,  0.82352941,  1.31034483,  0.68965517,  0.66666667,
            0.8       ,  0.        ,  0.14634146,  1.18032787,  0.91803279,
            0.39344262,  1.50819672,  0.96      ,  1.22666667,  0.48      ,
            1.33333333,  1.35      ,  0.65      ,  1.44680851,  0.55319149,
            1.42857143,  1.42857143,  0.64285714,  0.5       ])}

    """
    hist_rscu = {}
    for gene in codon_hist:
        hist_rscu[gene] = np.array( [0.] * 64 )
        for aminoacid in rev_codon_table:
            entropy = 0
            n = 0.
            new_norm = 0.
            for codon in rev_codon_table[aminoacid]:
                new_norm += codon_hist[gene][codon_hist_index.get( codon )]

            for codon in rev_codon_table[aminoacid]:
                if new_norm > 0:
                    pi = codon_hist[gene][codon_hist_index.get( codon )] / new_norm
                    hist_rscu[gene][codon_hist_index.get( codon )] = len(rev_codon_table[aminoacid]) * codon_hist[gene][codon_hist_index.get( codon )] / new_norm
                if pi > 0.0:
                    entropy += pi * np.log2( pi )
                    n += 1.

    return hist_rscu

def calculate_RSCU(codon_hist):
    """returns codon_rscu for a gene

    Summary
    -------

    Parameters
    ---------
    codon_hist:np.array x 64
            codon histogram

    Returns
    ------
    hist_rscu:np.array x 64
            relative synonymous codon usage


    """

    hist_rscu = {}
    hist_rscu = np.array( [0.] * 64 )
    for aminoacid in rev_codon_table:
        entropy = 0
        n = 0.
        new_norm = 0.
        for codon in rev_codon_table[aminoacid]:
            new_norm += codon_hist[codon_hist_index.get( codon )]

        for codon in rev_codon_table[aminoacid]:
            if new_norm > 0:
                pi = codon_hist[codon_hist_index.get( codon )] / new_norm
                hist_rscu[codon_hist_index.get( codon )] = len(rev_codon_table[aminoacid])*codon_hist[codon_hist_index.get( codon )] / new_norm
            if pi > 0.0:
                entropy += pi * np.log2( pi )
                n += 1.

    return hist_rscu

from Bio.SeqUtils import CodonUsage
import Bio.SeqUtils.CodonUsageIndices
def calculate_CAI_dic(fasta_filename,heg_fasta=None,reference=Bio.SeqUtils.CodonUsageIndices.SharpEcoliIndex):

    fasta = load_fasta(fasta_filename)

    CAI = CodonUsage.CodonAdaptationIndex()

    if heg_fasta is not None:
        try:
            CAI.generate_index(heg_fasta)
        except Exception:
            CAI.set_cai_index(reference)
    else:
        CAI.set_cai_index(reference)

    cais = {}

    for gene in fasta:
        try:
            try:
                sequence = gene.seq.tostring()
                triplets = [ sequence[start:start + 3] for start in range( 0, len( sequence ), 3 ) ]
            except Exception as error:
                print "Slicing of nucleotides into triplets failed"
                print error
                return None,None

            sequence = ''.join( filter(lambda codon: not is_ambig_codon(codon.lower()) , triplets) )

            cais[gene.id] = CAI.cai_for_gene(sequence)
        except Exception as e:
            cais[gene.id] = 0.
            print e

    return cais



def calculate_NC(codon_hist):
    pass

def highly_expressed_genes_by_file(filename,hist):
    """loads a list of highly expressed genes and returns and returns an index where 0 if no heg and 1 if heg is returned.
       the format used is that from ecai/heg and it tries to find the id in the description of the histogram keys

    Example
    -------

    Load a fasta file, compute codon histogram and then read in a list of highly expressed genes from
    TODO:
    then show the first 10 gene.ids that could be found

    >>> f = load_fasta('Escherichia_coli_O157-H7_EDL933Refseq.ffn')
    >>> chist,ahist = make_codon_histogram_dic(f)
    >>> truth,ids = highly_expressed_genes_by_file('ecoli3.heg.txt',chist)
    >>> ids[1:10]
    ['fid|127177|locus|Z4698|', 'fid|130454|locus|Z0298|', 'fid|129649|locus|Z2916|', 'fid|129950|locus|Z4588|', 'fid|128046|locus|Z5060|', 'fid|128982|locus|Z4737|', 'fid|129044|locus|Z4697|', 'fid|129074|locus|Z3827|', 'fid|130382|locus|Z4114|']
 """
    #you need an ordered dictionary if you want to use is_heg
    hist = collections.OrderedDict(hist)

    is_heg = [0] * len( hist )
    is_heg_id = []
    try:
        with open( filename ) as f:
            data = [ line.split() for line in f ]
#            if not ('Synonym' in data.next()[5]):
#                raise Exception("please use file from HEG database")
            heg = [x[5] for x in ( data[3:] ) if len( x ) > 1]
            i = 0
            for gene in hist:
                for test_heg in heg:
                    if test_heg in gene:
                        is_heg_id.append(gene)
                        is_heg[i] = 1
                i += 1
    except Exception as e:
        print e

    return is_heg,is_heg_id

def highly_expressed_genes_by_id(id_list,hist):
    """not implemented right yet"""
    heg = id_list
    is_heg = [False] * len( hist )
    i = 0
    for gene in hist:
        for test_heg in heg:
            if test_heg in gene:
                is_heg[i] = True
        i += 1
    return is_heg

def remove_stopcodons_and_one_codon_amino_acids(codon_hist):
    """

    Example
    -------

    """


    codon_hist = np.array(codon_hist)

    fullrange = set( range( 64 ) )
    for x in [15, 11, 10, 14, 35]:
        fullrange.remove( x )
    cleaned_range = list( fullrange )


    return codon_hist[cleaned_range]


def remove_stopcodons_and_one_codon_amino_acids_dic(codon_hist):

    fullrange = set( range( 64 ) )
    for x in [15, 11, 10, 14, 35]:
        fullrange.remove( x )
    cleaned_range = list( fullrange )

    codon_hist_cleaned={}

    for gene in codon_hist:
        codon_hist_cleaned[gene] = np.array(codon_hist[gene])[cleaned_range]

    return codon_hist_cleaned


def mds(hist,n_components=2,max_iter=300,n_init=8,n_jobs=-1):
    X = np.array( hist.values() )
    mds = manifold.MDS( n_components, max_iter = 300, n_init = 8, n_jobs = -1 )
    Y = mds.fit_transform( X )
    return Y

def plot_mds(hist,n_components=2,max_iter=300,n_init=8,n_jobs=-1):
    X = np.array( hist.values() )
    mds = manifold.MDS( n_components, max_iter = 300, n_init = 8, n_jobs = -1 )
    Y = mds.fit_transform( X )

    p.plot( Y[:,0], Y[:,1],'.'  )
    p.show()

    return Y

def isomap(hist,n_neighbors=10,n_components=2):
    """docstring for isomap"""
    X = np.array( hist.values() )
    Y = manifold.Isomap(n_neighbors,n_components).fit_transform(X)
    return Y

def lle(hist,n_neighbors=10,n_components=2):
    """docstring for lle"""
    X = np.array( hist.values() )
    Y = manifold.LocallyLinearEmbedding(n_neighbors, n_components,
                                        eigen_solver='auto',
                                        method='standard').fit_transform(X)

    return Y

def hessian_em(hist,n_neighbors=10,n_components=2):
    """docstring for hessian_em"""
    X = np.array( hist.values() )
    Y = manifold.LocallyLinearEmbedding(n_neighbors, n_components,
                                        eigen_solver='auto',
                                        method='hessian').fit_transform(X)

    return Y

def spectral(hist,n_neighbors=10,n_components=2):
    """docstring for spectral"""
    X = np.array( hist.values() )
    se = manifold.SpectralEmbedding(n_components=n_components,
                                    n_neighbors=n_neighbors)
    Y = se.fit_transform(X)
    return Y

def pca(hist,n_components=2):
    """"""
    X = np.array( hist.values() )
    pca = decomposition.PCA()
    pca.fit(X)
    print 'explained variance'
    print pca.explained_variance_

    pca.n_components = n_components
    X_reduced = pca.fit_transform(X)

    return X_reduced

def plot_pca(hist,n_components=2,is_heg=None):
    """"""
    X = np.array( hist.values() )
    pca = decomposition.PCA()
    pca.fit(X)
    print 'explained variance'
    print pca.explained_variance_

    pca.n_components = n_components
    X_reduced = pca.fit_transform(X)

    if is_heg is None:
        p.plot( X_reduced[:,0], X_reduced[:,1],'.'  )
    elif is_heg is not None:
        color = ['b']*len(is_heg)
        i = 0
        for gene in is_heg:
            if is_heg[i] == 1:
                color[i] = 'r'
            i+=1
        fig = p.figure( figsize=(15,8)  )
        ax = fig.add_subplot()
        p.scatter( X_reduced[:,0], X_reduced[:,1],c=color  )
    p.show()

    return X_reduced

def plot_all_reduction_methods(hist,n_neighbors=10,n_components=2,is_heg=None,n_subset=None):


    X = np.array( hist.values() )
    color = ['b']*len(X[0])

    if is_heg is None:
        pass
    elif is_heg is not None:
        color = ['b']*len(is_heg)
        i = 0
        for gene in is_heg:
            if is_heg[i] == 1:
                color[i] = 'r'
            i+=1

    if n_subset is not None:
        X = X[0:n_subset,:]

    try:
        iso = manifold.Isomap(n_neighbors,n_components).fit_transform(X)
    except Exception as e:
        print e

    try:
        lle = manifold.LocallyLinearEmbedding(n_neighbors, n_components,
                                            eigen_solver='auto',
                                            method='standard').fit_transform(X)
    except Exception as e:
        print e

    hessian = None
    try:
        hessian = manifold.LocallyLinearEmbedding(n_neighbors, n_components,
                                            eigen_solver='auto',
                                            method='hessian').fit_transform(X)
    except Exception as e:
        print e
        print 'trying dense'
        hessian = manifold.LocallyLinearEmbedding(n_neighbors, n_components,
                                            eigen_solver='dense',
                                            method='hessian').fit_transform(X)

    pca = decomposition.PCA()
    pca.n_components = n_components
    pca = pca.fit_transform(X)

    mds = manifold.MDS( n_components, max_iter = 300, n_init = 8, n_jobs = -1 )
    mds = mds.fit_transform( X )

    fig = p.figure()

    ax_iso = fig.add_subplot(2,3,1 )
    ax_iso.scatter(iso[:,0],iso[:,1],c=color)


    ax_lle = fig.add_subplot(2,3,2 )
    ax_lle.scatter(lle[:,0],lle[:,1],c=color)

    if hessian is not None:
        ax_hessian = fig.add_subplot(2,3,3 )
        ax_hessian.scatter(hessian[:,0],hessian[:,1],c=color)


    ax_mds = fig.add_subplot(2,3,4 )
    ax_mds.scatter(mds[:,0],mds[:,1],c=color)

    ax_pca = fig.add_subplot(2,3,5 )
    ax_pca.scatter(pca[:,0],pca[:,1],c=color)

    p.show()

def mds_from_fasta(filename):
    fasta = load_fasta(filename)
    codon_dic,aa_dic = make_codon_histogram_dic(fasta)
    rscu = calculate_RSCU_dic(codon_dic)
    Y=mds(rscu)



def setup_parser():
    """Setting up the parser for command line usage, returns args"""
    usage = """%(prog)s <functional argument> <output target argument>"""
    description = """Codon Bias Simulation"""

    parser = argparse.ArgumentParser( usage = usage, description = description )

    parser.add_argument( '-f', '--gene', action = 'store', nargs = 1, dest = 'experimental_data_filenames', help = 'File which contains Codon sequence of Genes which are to be used for calculating the amino acid frequencies' )
    parser.add_argument( '-v', '--verbose', action = 'store_true', dest = 'verbose', default = False )
    parser.add_argument( '-s', '--fitness_matrix', action = 'store', nargs = 1, dest = 'fitness_matrix_names', help = 'Fitness matrix, e.g. amino-acid similarity' )
    parser.add_argument( '-i', '--fitness_functions', action = 'append', dest = 'fitness_functions_filenames', help = 'Fitness functions' )
    parser.add_argument( '-c', '--configfile', action = 'store', dest = 'config_filename', help = 'Configuration file' )

    #sys.argv.append( config )
    args = parser.parse_args()

    config = None

    if args.config_filename is not None:
        if "jsn" in args.config_filename:
            with json.load( open( args.config_filename )) as config:
                args.experimental_data_filenames = config["experimental_data_filenames"]
                args.fitness_functions_filenames = config["fitness_functions_filenames"]
                args.fitness_matrix_names = config["fitness_matrix_names"]
        else:
            print 'other config file formats not supported, use *.jsn ending please'
            raise Exception


    return config

def config_from_file(filename):

    config = None
    try:
        config =  json.load( open( filename ))
    except Exception as e:
        print e

    return config

def c_codon_mut_dist( a, b ):
  """ Calculates the number of transitions, transversions and staying-const when one codon mutates to another.
    and is implemented in C with scipy.weave. A pure Python version for easier readability is implemented via
    py_codon_mut_dist.

    Parameters
    ----------
    a: string with codon 1
    b: string with codon 2

    Returns
    -------
    List with three doubles `results` with `results[0]` containing the number of unchanged nucleotides,
    `results[1]` number of transitions and `results[2]` number of transversions.

    Example
    -------

    Given twice the same codon the returned distance is 3 'no-changes'

    >>> c_codon_mut_dist('aaa','aaa')
    [3, 0, 0]

    Same for 3 transversion

    >>> c_codon_mut_dist('aaa','ttt')
    [0, 0, 3]

    And for one of each

    >>> c_codon_mut_dist('aaa','atg')
    [1, 1, 1]

"""

  results = [0, 0, 0]
  support_code = r"""
  int transition(char i,char j) {
    if(  ((i=='a') && (j=='g') ) || ((i=='g') && (j=='a') )   ) return 1;
    if(  ((i=='c') && (j=='t') ) || ((i=='t') && (j=='c') )   ) return 1;
    return 0;
  }
  """

  code = """
    int ti = 0;
    int tv = 0;

    for(int ci=0; ci<3;ci++) {

        if (a[ci] == b[ci]) continue;

        if (transition((a[ci]),(b[ci]))==1) {
            ti += 1;
            continue;
        } else {
            (tv += 1);
        }
    }

    results[0] = 3-ti-tv;
    results[1] = ti;
    results[2] = tv;
  """
  vars = ['results', 'a', 'b']
  #libs = []
  headers = ['<iostream>']
  extra_compile_args = ['-O3']
  compiler = 'gcc'

  weave.inline( code, vars, headers = headers, compiler = compiler, support_code = support_code, extra_compile_args = extra_compile_args )

  return results


def transition( i, j ):
    if i == 'a' and j == 'g' or j == 'a' and i == 'g':
        return True
    if i == 'c' and j == 't' or j == 'c' and i == 't':
        return True
    return False

def py_codon_mut_dist( i, j ):
    dist = [ 0, 0, 0 ]
    for k in range( len( i ) ):
        if i[k] == j[k]:
            dist[0] += 1
        if i[k] != j[k]:
            if transition( i[k], j[k] ):
                dist[1] += 1
            else:
                dist[2] += 1
    return dist

codon_mut_dist = c_codon_mut_dist

class Fitnessfunction:
  """A Class for fitness functions!"""
  def __init__( self, description, parameter, values, interpolation,filename='' ):
    self.description = description
    #parameter = parameter
    self.parameter = parameter
    self.fitnessvalues = np.array( values )
    self.interpolation = interpolation
    self.strength = 0.0
    self.max = max( self.fitnessvalues )
    self.filename = filename


def euclidean_distance( steady_state, codon_hist ):
  aa_dist = np.linalg.norm( np.array( steady_state ) - np.array( codon_hist ) )
  return aa_dist

def kl_distance( steady_state, codon_hist ):
  aa_dist = np.dot( np.array( steady_state ), np.array( steady_state ) / np.array( codon_hist ) )
  return aa_dist

def relative_euclidean_distance( steady_state, codon_hist ):
    s = calculate_RF(steady_state)
    c = calculate_RF(codon_hist)
    c = remove_stopcodons_and_one_codon_amino_acids(c)
    s = remove_stopcodons_and_one_codon_amino_acids(s)


    aa_dist = np.linalg.norm( np.array(s) - np.array(c)   )

    return aa_dist

def relative_cosine_distance(steady_state,codon_hist):
    s = calculate_RF(steady_state)
    c = calculate_RF(codon_hist)
    c = remove_stopcodons_and_one_codon_amino_acids(c)
    s = remove_stopcodons_and_one_codon_amino_acids(s)


    aa_dist = scipy.spatial.distance.cosine(np.array(s),np.array(c))

    return aa_dist

def relative_jeffrey_divergence(steady_state,codon_hist):
    """TODO: not implemented"""
    print 'not implemented!'

    return 0

def relative_minkowski_distance(steady_state,codon_hist):
    """TODO: not implemented"""
    print 'not implemented!'

    return 0
def relative_hellinger_distance(steady_state,codon_hist):
    """TODO: not implemented"""
    print 'not implemented!'

    return 0


#compute_distance = euclidean_distance
#compute_distance = relative_euclidean_distance
compute_distance = relative_cosine_distance

def compute_steady_state( evolmatrix, aa_hist ):
  """ The steady state is the eigenvector belonging to the largest eigenvalue of the evolution matrix for a specific amino acid """

  steady_state = np.zeros( 64 )
  for A in range( 21 ):
    [eigenvalues, eigenvectors] = ( sp.linalg.eig( evolmatrix[A] , overwrite_a = True, overwrite_b = True ) )
    biggest_eigenvalue_index = list( eigenvalues ).index( max( eigenvalues ) )

    # The steady state given P(codon|amino_aicd) can be calculated as P(codon) = \sum P(Codon|amino_acid) P(amino_acid) and can be normalized additionally
    try:
        steady_state += ( abs( np.array( ( eigenvectors.T )[biggest_eigenvalue_index] / sum( eigenvectors[biggest_eigenvalue_index] ) ) ) * aa_hist[A] )
    except Exception as e:
        print 'something went wront'
        print biggest_eigenvalue_index
        print eigenvectors
        print aa_hist[A]

    return steady_state / np.sum( steady_state )


def make_jc69_mutationmatrix(mu=0,
                            alpha=0,
                            beta=0):

    """ ups, not correct! read models_of_dna_evolution on wiki  """
    if ( alpha is not 0 ) and (beta is not 0):
        mu = alpha + 2*beta

    eq = ( 1. - 3./4.*mu)
    neq = mu/4.

    for i in codons:
        for j in codons:

            if i == j:
                mutationmatrix[codon_index[ i ]][codon_index[ j ]] = eq
            else:
                mutationmatrix[codon_index[ i ]][codon_index[ j ]] = neq

    return mutationmatrix


def make_mutationmatrix_mclachlan(parameters=None,
                    alpha=0,
                    beta=0):
    mu = alpha + 2 * beta

    mutationmatrix = np.zeros( ( 64, 64 ) )

    for i in codons:
        for j in codons:
            dist = codon_mut_dist( i, j )

            mutationmatrix[codon_index[ i ]][codon_index[ j ]] = ( 1 - mu ) ** dist[0] * alpha ** dist[1] * beta ** dist[2]

    return mutationmatrix

make_mutationmatrix = make_mutationmatrix_mclachlan


def make_evolmatrix( mutationmatrix,
                    fitnessfunctions,
                    fitnessmatrices,
                    selection,
                    additive=False
):
    """Given the mutationmatrix, the fitnessfunctions, the fitnessmatrices (the amino-acid identity matrix) and the selection strength, this builds the evolutionmatrix"""
    evolmatrix = np.zeros( ( 21, 64, 64 ) )

    if additive==True:
        fit = np.array( [0.]* 64 )

    for A in range( 21 ):
        evolmatrix[A] = np.array( mutationmatrix )

        for fitnessfunction in fitnessfunctions:
            if len( fitnessfunction.fitnessvalues ) == 64:
                if additive == False:
                    evolmatrix[A] = evolmatrix[A] * (
                                                    1. - fitnessfunction.strength *
                                                    ( ( fitnessfunction.max ) - ( fitnessfunction.fitnessvalues ) )
                                                    / ( fitnessfunction.max )
                                                    )
                elif additive == True:
                    fit += (
                            1. - fitnessfunction.strength *
                            ( ( fitnessfunction.max ) - ( fitnessfunction.fitnessvalues ) )
                            / ( fitnessfunction.max )
                            )


        if additive == True:
            evolmatrix[A] = evolmatrix[A] * fit

        for fitnessmatrix in fitnessmatrices:
            Ai = codons.index( rev_codon_table[amino_acids_unique[A]][0] )
            if np.abs( fitnessmatrix[Ai][Ai] ) < np.finfo(float).eps :
                evolmatrix[A] = evolmatrix[A] * 0.
                continue
            evolmatrix[A] = evolmatrix[A] * (
                                            1. - selection *
                                            ( fitnessmatrix[Ai][Ai] - (  fitnessmatrix[Ai]  ) )
                                            / fitnessmatrix[Ai][Ai]
                                            )



    evolmatrix = np.array( evolmatrix )
    return evolmatrix


def compute_steady_state( evolmatrix, aa_hist ):
  """ The steady state is the eigenvector belonging to the largest eigenvalue of the evolution matrix for a specific amino acid """

  steady_state = np.zeros( 64 )
  for A in range( 21 ):
    [eigenvalues, eigenvectors] = ( sp.linalg.eig( evolmatrix[A] , overwrite_a = True, overwrite_b = True ) )
    # [eigenvalues, eigenvectors] = ( sp.sparse.linalg.eigs( evolmatrix[A], k = 2 ) )
    # sp.sparse
    # [eigenvalues, eigenvectors] = ( np.linalg.eig( evolmatrix[A] ) )
    biggest_eigenvalue_index = list( eigenvalues ).index( max( eigenvalues ) )
    # The steady state given P(codon|amino_aicd) can be calculated as P(codon) = \sum P(Codon|amino_acid) P(amino_acid) and can be normalized additionally
    steady_state += ( abs( np.array( ( eigenvectors.T )[biggest_eigenvalue_index] / sum( eigenvectors[biggest_eigenvalue_index] ) ) ) * aa_hist[A] )
  return steady_state / sum( steady_state )

def run_model(parameters,fitnessfunctions,fitnessmatrices,aa_hist):
    """
    parameters = alpha,beta,selection,t0,t1,t2,t3...

    """

    i = 3
    for fitnessfunction in fitnessfunctions:
        fitnessfunction.strength = parameters[i]
        i+=1

    mutationmatrix = make_mutationmatrix(alpha=parameters[0],beta=parameters[1])

    evolmatrix = make_evolmatrix( mutationmatrix, fitnessfunctions, fitnessmatrices, parameters[2] )

    result = compute_steady_state(evolmatrix,aa_hist)

    return result

import time
import inspyred
import inspyred.ec
import random
import multiprocessing as mp

class Model():
    def __init__(self, fitnessfunctions,fitnessmatrices,aa_hist,c_hist):
        self.fitnessfunctions = fitnessfunctions
        self.fitnessmatrices = fitnessmatrices
        self.aa_hist = aa_hist
        self.codon_hist = c_hist

    def run(self,parameters):
        self.results = run_model(parameters,self.fitnessfunctions,self.fitnessmatrices,self.aa_hist )
        self.distance = compute_distance( self.results, self.codon_hist )
        return self.distance

    def run_log(self,parameters):
        lparameters =  np.array( parameters) ** 10
        self.results = run_model(lparameters,self.fitnessfunctions,self.fitnessmatrices,self.aa_hist )
        self.distance = compute_distance( self.results, self.codon_hist )
        return self.distance

    def generate_quasispecies(self,random,args):
        #size = args.get()
        #alpha, beta, selection + num_fitnessfunctions
        size = 3 + len(self.fitnessfunctions)
        return [random.expovariate(1e5) for i in range(size)]
        #return [random.uniform(0.0,1.0) for i in range(size)]

    def generate_quasispecies_old_opt(self,random,args):
        opt = args['old_opt']
        #alpha, beta, selection + num_fitnessfunctions
        size = 3 + len(self.fitnessfunctions)
        return [random.expovariate(1./opt[i]) for i in range(size)]
        #return [random.uniform(0.0,1.0) for i in range(size)]

    def evaluate_quasispecies(self,candidates,args):
        fitness = []
        for candidate in candidates:
            fit = self.run(candidate)
            fitness.append(fit)
            #print candidate,fit

        return fitness

    #def optimize_evolutionary(self,pop_size=2500,max_eval=100000,mutrate=0.25):
    def optimize_evolutionary(self,pop_size=2500,max_eval=100000,mutrate=0.35):
        rand = random.Random()
        rand.seed(int(time.time()))
        es = inspyred.ec.ES(rand)
        es.terminator = inspyred.ec.terminators.evaluation_termination
        final_pop = es.evolve(generator = self.generate_quasispecies,
                              evaluator = self.evaluate_quasispecies,
                              pop_size=pop_size,
                              maximize=False,
                              bounder=inspyred.ec.Bounder(0.0,1.0),
                              max_evaluation=max_eval,
                              mutation_rate = mutrate)

        final_pop.sort(reverse=True)
        #print final_pop[0]
        return final_pop[0]


    def optimize_pso(self,pop_size=500,max_eval=100000,neighborhood_size=5,old_opt=None):
        rand = random.Random()
        rand.seed(int(time.time()))
        ea = inspyred.swarm.PSO(rand)
        ea.topology = inspyred.swarm.topologies.ring_topology
        ea.terminator = inspyred.ec.terminators.evaluation_termination
        final_pop = ea.evolve(generator = self.generate_quasispecies_old_opt,
                              evaluator = self.evaluate_quasispecies,
                              pop_size=pop_size,
                              maximize=False,
                              bounder=inspyred.ec.Bounder(0.0,1.0),
                              max_evaluation=max_eval,
                              old_opt = old_opt)

        final_pop.sort(reverse=True)
        #print final_pop[0]
        return final_pop[0]


def init_fitnessmatrix_for_codons(config=None,
                                filenames=None
                                ):
    #TODO: not implemented
    pass

def init_fitnessmatrix_for_amino_acids(config=None,
                                       filenames=None,
                                       amino_acid_order=list("ARNDCEQGHIKLMFPSTWYV")
                                       ):
    """ Load fitnessmatrix form file. Either config from file or list of filenames


    Example
    -------

    Load the mclachlan72 fitness matrix that expresses how good an amino acid i can be represented by an amino acid j.
    Then we look at which codons have nonzero fitness to code for tct which corresponds to the amino acid S. as a good test,
    all synonymous codons of S (tct,tcg,tcc,tca,agc,agt) should have nonzero fitness!

    >>> fit = init_fitnessmatrix_for_amino_acids(filenames=['mclachan72.csv'])# doctest : +NORMALIZE_WHITESPACE
    >>> np.array(codons)[fit[0][4,:]!=0] # doctest : +NORMALIZE_WHITESPACE
    array(['tct', 'tcc', 'tca', 'tcg', 'tgt', 'tgc', 'caa', 'cag', 'act',
           'acc', 'aca', 'acg', 'aat', 'aac', 'agt', 'agc', 'gct', 'gcc',
           'gca', 'gcg'],
          dtype='|S3')


    """


    if config is not None and filenames is not None:
        print 'two optional options given, I just use the config= ones...'

    if config is not None:
        filenames = config["fitness_matrix_names"]

    if config is None and filenames is None:
        print 'either config = configdict or list of filenames as filenames'


    fitnessmatrices_amino_acids = []
    fitnessmatrixparameters = []
    number_fitness_matrices = 0
    for fitness_matrix_name in filenames:
        if "jsn" in fitness_matrix_name:
            fitnessmatrixdata = json.load( open( fitness_matrix_name ) )
        if "csv" in fitness_matrix_name:
            fitnessmatrices_amino_acids.append(
                np.array(
                    [ map( float, line.split( ',' ) ) for line in open( fitness_matrix_name ) ]
                )
            )
            fitnessmatrixparameters.append( str( number_fitness_matrices ) )

    fitnessmatrices = []
    amino_acids_mc = amino_acid_order
    for fitnessmatrix_amino_acid in fitnessmatrices_amino_acids:
        fitnessmatrix = np.zeros( ( 64, 64 ) )
        for codon_index_i in range( 64 ):
            for codon_index_j in range( 64 ):
                if codons[codon_index_i] in ['tag', 'tga', 'taa'] or codons[codon_index_j] in ['tag', 'tga', 'taa']:
                    # stop codons
                    continue
                """for all codons by index, look at what codon corresponds to that index, look which amino acid corresponds to that codon,
                than look into the alphabet sorted amino acids and look at which position the amino acid can be found --- this gives the
                amino acid index for the maclachlan matrix"""
                amino_acid_i = amino_acids_mc.index( codon_table[codons[codon_index_i]] )
                amino_acid_j = amino_acids_mc.index( codon_table[codons[codon_index_j]] )

                fitnessmatrix[codon_index_i][codon_index_j] = fitnessmatrix_amino_acid[amino_acid_i][amino_acid_j]
    fitnessmatrices.append( fitnessmatrix )

    return fitnessmatrices


def init_fitnessfunctions(config=None,filenames=None):
    """ Loads fitnessfunctions from file. Either config from file oder list of filenames.


    Example
    -------

    Given an example file, `trna_pool.jsn` in which a measure for the trna pool of e.coli is given
    a list with fitnessfunctions of length 1 and a fitnessfunction with the right fitnessvalues should
    be loaded

    >>> a = init_fitnessfunctions(filenames=['trna_pool.jsn'])# doctest : +NORMALIZE_WHITESPACE
    >>> a[0].fitnessvalues
    array([  3.27,   3.27,   3.57,   9.61,   6.5 ,   2.41,   4.09,   5.18,
             6.41,   6.41,   1.  ,   1.  ,   5.01,   5.01,   1.  ,   2.98,
             2.97,   2.97,   2.1 ,  16.21,   4.1 ,   2.27,   1.83,   4.67,
             2.02,   2.02,   2.41,   2.78,  15.  ,  15.  ,  15.  ,   2.01,
            10.96,  10.96,  10.96,   8.31,   6.67,   3.78,   2.89,   4.6 ,
             3.77,   3.77,   6.08,   6.08,   4.44,   4.44,   2.74,   1.23,
            16.11,   3.99,  12.12,  12.12,  10.25,   1.95,  10.25,  10.25,
             7.56,   7.56,  14.88,  14.88,  13.76,  13.76,   6.75,   6.75])


    """

    fitnessfunctions = []

    if config is not None and filenames is not None:
        print 'two optional options given, I just use the config= ones...'

    if config is not None:
        filenames = config["fitness_functions_filenames"]

    if config is None and filenames is None:
        print 'either config = configdict or list of filenames as filenames'


    for fitness_function_filename in filenames:
        try:
            fitnessdata = json.load( open( fitness_function_filename ) )
            fitnessfunctions.append( Fitnessfunction( fitnessdata["description"], fitnessdata["parameter"], fitnessdata["fitnessvalues"], fitnessdata["interpolation"] ) )
        except Exception as e:
            print 'reading filtertnessfunction ',  fitness_function_filename, ' failed'
            print e

    if len( fitnessfunctions ) == 0:
        print "no fitnessfunctions read!"

    return fitnessfunctions

from scipy.optimize import minimize

def optimize(model,method=None):

    #alpha,beta,selection,t0,t1,t2
    x0 =  [1.0,1.0,1e-6,1e-6,1e-6,1e-6]

    res = minimize(model.run,x0,method='powell')

    return res

def sample_run():

    filename = 'Escherichia_coli_O157-H7_EDL933Refseq.ffn'
    f = load_fasta(filename)
    chist,ahist = make_codon_histogram_dic(f)
    fitmat = init_fitnessmatrix_for_amino_acids(filenames=['mclachan72.csv'])
    fitfu = init_fitnessfunctions(filenames=['trna_pool.jsn'])
    result = run_model([1.0, 1.0, 1.0,1.0],fitfu,fitmat,ahist.itervalues().next() )

    print result

    if np.abs( result[0] - 0.0114015) < 1e-5:
        print 'seems okay!'
    else:
        print 'something is wrong?'

def parametric_run_from_config(config,toolbar=False,output=True):
    # RUN
    config = config_from_file(config)
    print config['experimental_data_filenames']
    f = load_fasta(config['experimental_data_filenames'][0])
    codon_hist,aa_hist = make_codon_histogram_dic( f  )

    codon_hist = codon_hist.values()[0]
    aa_hist = aa_hist.values()[0]

    output = []
    out_config = {}
    out_config["time"] = time.time()
    out_config["aa_hist"] = aa_hist
    out_config["aa_hist_aas"] = rev_codon_table.keys()
    out_config["codon_hist"] = codon_hist
    output.append( out_config )



    fitnessmatrices =  init_fitnessmatrix_for_amino_acids(config=config)
    fitnessfunctions=  init_fitnessfunctions(config=config)

    # `toolbar` if wanted
    if toolbar:
        try:
            toolbar_width = len( np.arange( float( config["run"]["fitnessmatrix"]["selection"]["start"] ), float( config["run"]["fitnessmatrix"]["selection"]["end"] ), float( config["run"]["fitnessmatrix"]["selection"]["step"] ) ) )

            # setup toolbar
            sys.stdout.write( "[%s]" % ( " " * toolbar_width ) )
            sys.stdout.flush()
            sys.stdout.write( "\b" * ( toolbar_width + 1 ) )  # return to start of line, after '['

        except Exception:
            print "autsch"

    selection_range = []
    if config["run"]["fitnessmatrix"]["selection"]["scale"] == "linear":
        selection_range = np.arange( float( config["run"]["fitnessmatrix"]["selection"]["start"] ), float( config["run"]["fitnessmatrix"]["selection"]["end"] ), float( config["run"]["fitnessmatrix"]["selection"]["step"] ) )
    if config["run"]["fitnessmatrix"]["selection"]["scale"] == "log":
        selection_range = np.arange( float( config["run"]["fitnessmatrix"]["selection"]["start"] ), float( config["run"]["fitnessmatrix"]["selection"]["end"] ), float( config["run"]["fitnessmatrix"]["selection"]["step"] ) )
        selection_range = map( lambda x:10 ** ( -x ), selection_range )

    #WUWUWU!!!!
    fitnessfunction_strengths = list(
            itertools.product(
                        *[ np.arange( config["run"]["fitnessfunctions"][fitnessfunction_index]["start"],
                                        config["run"]["fitnessfunctions"][fitnessfunction_index]["end"],
                                        config["run"]["fitnessfunctions"][fitnessfunction_index]["step"] ) for fitnessfunction_index in range( len( fitnessfunctions ) ) ]
                        )
            )
    fitnessfunction_strengths = {}.fromkeys( fitnessfunction_strengths ).keys()

    for selection in selection_range:
        if toolbar:
            sys.stdout.write( "-" )
            sys.stdout.flush()

        alpha = config["run"]["fitnessmatrix"]["alpha"]
        beta = config["run"]["fitnessmatrix"]["beta"]
        mu = alpha + 2 * beta

        mutationmatrix = make_mutationmatrix(alpha=alpha,beta=beta)



        for fitnessfunction_strength in fitnessfunction_strengths:

            for fitnessfunction_index in range( len( fitnessfunctions ) ):
                if fitnessfunctions[fitnessfunction_index].interpolation == "linear":
                    fitnessfunctions[fitnessfunction_index].strength = fitnessfunction_strength[fitnessfunction_index]
                if fitnessfunctions[fitnessfunction_index].interpolation == "log":
                    fitnessfunctions[fitnessfunction_index].strength = 10 ** ( -fitnessfunction_strength[fitnessfunction_index] )


            #if( abs( mu - ( alpha + 2 * beta ) ) > 10e-10 ):
                #print "mu should be mu = alpha + 2beta"
                #print str( mu ) + '!=' + 'alpha+2beta=' + str( alpha + 2 * beta )
                #print abs( mu - ( alpha + 2 * beta ) )



            # Evolmatrix
            evolmatrix = make_evolmatrix( mutationmatrix, fitnessfunctions, fitnessmatrices, selection )


    #            out_sel = """ \"selection\":{0} """.format(selection)
    #            out_fitness = []
    #            for fitnessfunction_i in range(len(fitnessfunctions)):
    #              out_fitness.append( """ \"{0}\":{1} """.format(fitnessfunction_i,str(fitnessfunction[fitnessfunction_i].strength)))

            steady_state = compute_steady_state( evolmatrix, aa_hist )


            out = {}
            out["selection"] = selection
            #print [ [fitnessfunction_i, fitnessfunctions[fitnessfunction_i].strength] for fitnessfunction_i in range( len( fitnessfunctions ) ) ]
            out["fitness"] = np.array( [ [fitnessfunction_i, fitnessfunctions[fitnessfunction_i].strength] for fitnessfunction_i in range( len( fitnessfunctions ) ) ] )
            out["steady_state"] = list( map( str, steady_state ) )
            out["codon_distance"] = compute_distance( steady_state, codon_hist )
            out["mu_alpha_beta"] = [mu, alpha, beta]
            output.append( out )


            # print np.arange(config["run"]["fitnessmatrix"]["selection"]["start"],config["run"]["fitnessmatrix"]["selection"]["end"],config["run"]["fitnessmatrix"]["selection"]["step"])
            # print config["run"]["fitnessfunctions"]





    plotdata = []
    for result in output:
    # print result
    # print result
        try:
            # print result['selection'], result['aa_distance']
            plotdata.append( [result['selection']] + [ fivalue for fivalue in  result['fitness'][:, 1] ] + [result['codon_distance']] )
            #print [result['selection']] + [ fivalue for fivalue in  result['fitness'][:][1] ] + [result['codon_distance']]
        except Exception:
            pass
            #print "au"
            # print result['steady_state'][0]

    #print ( sorted( plotdata, key = lambda x:x[-1] ) ) [0:10]
    idx = plotdata.index( ( sorted( plotdata, key = lambda x:x[-1] ) ) [0] )

    #print 'done'
    #print plotdata[idx]
    print config["name"],
    for x in plotdata[idx]:
        print str( x ),

    if output:
        of = open( "results.jsn", "w+" )
        for out in output:
            try:
                out["fitness"] = list(map(list,out["fitness"]))
            except Exception:
                pass
        json.dump( output, of, indent = 2 )
        of.close()



def optimize_sequence(steady_state,target_sequence):
    """given the steady state and the target sequence, let us optimize!"""

    #translate target_sequence
    #make chist and ahist from target sequence
    #calculate relative frequency of steady state
    #formats codon in target_sequence:
    #





def compute_optimum_two_step(f,fitfu,fitmat, gene, id ):
    chist,ahist = make_codon_histogram(gene)
    mymod = Model(fitfu,fitmat,ahist,chist)
    ss = mymod.optimize_evolutionary()
    opt = ss.candidate[:len(fitfu)+3]

    #print 'old fit'
    #print ss.fitness
    ss = mymod.optimize_pso(old_opt=opt)
    opt = ss.candidate[:len(fitfu)+3]

    #print 'new fit'
    #print ss.fitness

    steady_state = mymod.run(opt)
    result = opt
    print str(id) + '\t' + gene.id + '\t',
    print ss.fitness,
    for point in result:
        print point,
    print '\n',

    f.write(id)
    for point in result:
        f.write(str(point)+'\t')

    f.write('\n')
    f.flush()

    return result

def compute_optimum(f,fitfu,fitmat, gene, id ):
    chist,ahist = make_codon_histogram(gene)
    mymod = Model(fitfu,fitmat,ahist,chist)
    opt = mymod.optimize_evolutionary().candidate[:len(fitfu)+3]
    steady_state = mymod.run(opt)
    result = opt
    print id,
    for point in result:
        print point,
    print '\n',

    f.write(id)
    for point in result:
        f.write(str(point)+'\t')

    f.write('\n')
    f.flush()

    return result



def init_list_of_genes(fasta_filename,minimal_number_of_nucleotides_per_gene):

    list_of_genes = []
    f = load_fasta(fasta_filename)
    for gene in f:
        if len(gene.seq.tostring()) > minimal_number_of_nucleotides_per_gene:
            list_of_genes.append( gene )

    return list_of_genes


def optimize_dic(fasta_filename,fitfu,fitmat,minimal_number_of_nucleotides_per_gene=500):
    """

    The probability when we  put r number of codons in a gene into n bins of different codons to find a codon with k occurences in the gene is
    ..math:
        p_k = \left( \frac{r}{k})  \right) \frac{(n-1)^{r-k}}\frac{n^r}

    hence, the probability of finding more than one occurence is

    ..math:
        p_{k>1} (63/64)^r( (64/63)^r - 1 )


    if we want to to be reasonably sure our gene contains at least one codon from every kind we have to solve the inequality
    p_{k>1} > p-value. A p-value of 0.95 implies we have to use a gene with at least 500 nucleotides

    """


    n_cpu = mp.cpu_count()
    pool = mp.Pool( 12 )

    f = open('optresuls','w+')

    list_of_genes = init_list_of_genes(fasta_filename,minimal_number_of_nucleotides_per_gene)
    for gene in list_of_genes:
        id = list_of_genes.index( gene )
        pool.apply_async( compute_optimum_two_step, ( f,fitfu,fitmat,gene, id, ) )
        #print id

    pool.close()
    pool.join()

    print 'done'
    f.close()




if __name__ == "__main__":
    doctest.testmod()
    #mygui = cobigui()
    #mygui.start_gui()





