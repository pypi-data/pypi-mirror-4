import cobilib
from Tkinter import *
import Tkinter
from ttk import *
import tkFileDialog
import collections
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
class cobigui:

    def callback(self):
        name = tkFileDialog.askopenfilename()
        self.fname = name
        self.fasta_filename.set(name)
        self.fasta = cobilib.load_fasta( name )
        print 'generating amino acid hist and codon hist'
        self.chist,self.ahist = cobilib.make_codon_histogram_dic(self.fasta)
        print 'codon histogram, first entry'
        print self.chist.itervalues().next()
        print 'amino histogram, first entry'
        print self.ahist.itervalues().next()

    def load_fasta_url(self):
        name = str(self.ask_entry.get())
        print name
        if name is not None:
            self.fname = name
            self.fasta_filename.set(name)
            try:
                self.fasta = cobilib.load_fasta_from_url( name )
            except Exception as e:
                print e
            else:
                print 'generating amino acid hist and codon hist'
                self.chist,self.ahist = cobilib.make_codon_histogram_dic(self.fasta)
                print 'codon histogram, first entry'
                print self.chist.itervalues().next()
                print 'amino histogram, first entry'
                print self.ahist.itervalues().next()

    def fasta_from_url(self):
        askurl = Toplevel(self.mainframe)
        ask_label = Label(askurl, text='url').pack()
        self.ask_entry = Entry(askurl)
        self.ask_entry.pack()
        ask_button = Button(askurl, text='load',command=self.load_fasta_url).pack()
        close_button = Button(askurl,text='close',command=askurl.destroy).pack()

    def load_fasta_combined(self):
        name = tkFileDialog.askopenfilename()
        self.fname = name
        self.fasta_filename.set(name)
        self.fasta = cobilib.load_fasta( name )
        print 'generating amino acid hist and codon hist'
        self.chist,self.ahist = cobilib.make_codon_histogram_dic_combined(self.fasta)
        print 'codon histogram, first entry'
        print self.chist.itervalues().next()
        print 'amino histogram, first entry'
        print self.ahist.itervalues().next()

    def reduction(self):
        try:
            n_subset = int(self.n_subset_entry.get())
        except Exception as e:
            print e
            n_subset = 100
        try:
            cobilib.plot_all_reduction_methods(self.ahist,n_subset=n_subset,is_heg=self.heg_truth)
        except Exception:
            cobilib.plot_all_reduction_methods(self.ahist,n_subset=n_subset)

    def load_heg(self):
        name = tkFileDialog.askopenfilename()
        self.heg_filename.set(name)
        self.heg_truth,heg_id = cobilib.highly_expressed_genes_by_file(name,self.chist)
        print np.arange( len(self.heg_truth)  )[np.array(self.heg_truth)==1]

    def load_fitmat(self):
        name = tkFileDialog.askopenfilename()
        self.fitmat_filename.set(name)
        self.fitmat = cobilib.init_fitnessmatrix_for_amino_acids(filenames=[name])

    def del_fitfu(self):
        idxs = self.fitfu_list.curselection()
        if len(idxs) == 1:
            idx = int(idxs[0])
            del self.fitfu_filenames[idx-1]
            self.fitfu_list.delete(idx)
        self.fitfu = cobilib.init_fitnessfunctions(filenames=self.fitfu_filenames)

    def add_fitfu(self):
        name = tkFileDialog.askopenfilename()
        self.fitfu_filenames.append(name)
        self.fitfu_list.insert(len(self.fitfu_filenames),name)
        self.fitfu = cobilib.init_fitnessfunctions(filenames=self.fitfu_filenames)

    def run(self):
        self.parameters = map(float,str(self.parameter_entry.get()).replace(',',' ').split())
        print self.parameters
        self.result = cobilib.run_model(self.parameters,self.fitfu,self.fitmat,self.ahist.itervalues().next() )
        print self.result
        print cobilib.compute_distance( self.result, self.chist.itervalues().next())
        #format for OPTIMIZER... spec is hidden in tutorials and does not work with ecai calculated rscu
        print 'for use with OPTIMIZER, using RSCU'
        rscu = cobilib.calculate_RSCU(self.result)
        for i in range(len(rscu)):
            print cobilib.codons[i].upper().replace('T','U') + ': ' + str(rscu[i]) + ';',
        print '\n'



    def evol_optimize(self):
        mymod = cobilib.Model(self.fitfu,self.fitmat,self.ahist.itervalues().next(),self.chist.itervalues().next())
        self.opt = mymod.optimize_evolutionary().candidate[:len(self.fitfu)+3]
        mymod.run(self.opt)
        self.result = mymod.results
        print self.opt
        return self.result

    def evol_optimize_two_step(self):
        mymod = cobilib.Model(self.fitfu,self.fitmat,self.ahist.itervalues().next(),self.chist.itervalues().next())
        ss = mymod.optimize_evolutionary()
        self.opt = ss.candidate[:len(self.fitfu)+3]

        print 'old fit'
        print ss.fitness
        ss = mymod.optimize_pso(old_opt=self.opt)
        self.opt = ss.candidate[:len(self.fitfu)+3]

        print 'new fit'
        print ss.fitness

        self.result = mymod.results
        print self.opt
        return self.result

    def opt_all(self):
        minlength = int( self.n_minimum_length.get() )
        cobilib.optimize_dic(self.fname,self.fitfu,self.fitmat,minlength)

    def plot(self):
        fig,axarr = p.subplots(2)
        pchist = self.chist.itervalues().next()
        axarr[0].bar( np.arange( 1.0, len( self.result ) * 2.0, 2.0 ), self.result, color = 'r' )
        axarr[0].bar( np.arange( 0.0, len( self.result ) * 2.0, 2.0 ), pchist, color = 'b' )

        pchist = np.array( self.chist.itervalues().next() )
        res = np.array(self.result)

        res[ np.abs(pchist)<1e-5  ] = 0.

        c = cobilib.calculate_RF(pchist)
        s = cobilib.calculate_RF(res)
        c = cobilib.remove_stopcodons_and_one_codon_amino_acids(c)
        s = cobilib.remove_stopcodons_and_one_codon_amino_acids(s)

        axarr[1].bar( np.arange( 1.0, len( s ) * 2.0, 2.0 ), s, color = 'r' )
        axarr[1].bar( np.arange( 0.0, len( s ) * 2.0, 2.0 ), c, color = 'b' )

        pprint.pprint( np.array(s) )
        pprint.pprint( np.array(c) )

        p.show()

    def calculate_cai(self):
        self.cai = cobilib.calculate_CAI_dic( self.fname )
        i = 0
        for gene in self.cai:
            print i, gene, self.cai[gene]
            i+=1

    def calculate_rscu(self):
        self.rscu = cobilib.calculate_RSCU_dic( self.chist )
        i = 0
        for gene in self.rscu:
            print i, gene, self.rscu[gene]
            i+=1

    def choose_genetic_code(self,event):
        new_code_idx = int(self.genetic_code_combobox.current())
        new_code = cobilib.genetic_codes.keys()[new_code_idx]
        print 'new genetic code has been chosen:'
        print new_code
        cobilib.change_amino_acid_code(new_code)
        print cobilib.amino_acids


    def __init__(self):
        pass
    def start_gui(self):
        self.root = Tk()
        self.fasta_filename = StringVar()
        self.heg_filename = StringVar()
        self.fitmat_filename = StringVar()
        self.root.title("Codon Usage/Codon Optimization Lib")
        self.mainframe = Frame(self.root)
        self.mainframe.grid( column = 0, row = 0, sticky=(N,W,E,S))
        self.mainframe.columnconfigure(0,weight=1)
        self.mainframe.rowconfigure(0,weight=1)


        self.genetic_code_combobox = Combobox(self.mainframe,width=27)
        self.genetic_code_combobox.grid(row=0,column=2)
        self.genetic_code_combobox['values'] = cobilib.genetic_codes.keys()
        self.genetic_code_combobox.bind('<<ComboboxSelected>>',self.choose_genetic_code)

        fasta_file_label = Label(self.mainframe, textvariable=self.fasta_filename,width=17).grid(row=0,column=4 )
        fasta_file_button = Button(self.mainframe,text='select fasta',command=self.callback,width=17).grid(row=0,column=0,sticky=W)
        fasta_url_button = Button(self.mainframe,text='fasta from url',command=self.fasta_from_url,width=17).grid(row=0,column=3)
        fasta_file_button = Button(self.mainframe,text='select fasta,combine all genes',command=self.load_fasta_combined,width=27).grid(row=0,column=1)

        heg_file_label = Label(self.mainframe, textvariable=self.heg_filename,width=27).grid(row=1,column=2 )
        heg_file_button = Button(self.mainframe,text='select heg list',command=self.load_heg,width=17).grid(row=1,column=0,sticky=W)
        calculate_cai = Button(self.mainframe,text='calculate cai',command=self.calculate_cai,width=17).grid(row=1,column=3)
        calculate_rscu = Button(self.mainframe,text='calculate rscu',command=self.calculate_rscu,width=17).grid(row=1,column=4)



        plot_reduction_button = Button(self.mainframe, text = 'plot reduction',command=self.reduction,width=17).grid(row=2,column=0,sticky=W)
        n_subset_label = Label(self.mainframe,text='number of genes to be analyzed',width=27).grid(row=2,column=2)
        self.n_subset_entry = Entry(self.mainframe,width=27)
        self.n_subset_entry.grid(row=2,column=1)

        fitmat_file_label = Label(self.mainframe, textvariable=self.fitmat_filename,width=17).grid(row=4,column=2 )
        fitmat_heg_file_button = Button(self.mainframe,text='select fitnessmatrix',command=self.load_fitmat,width=17).grid(row=4,column=0,sticky=W)

        self.fitfu_filenames = []


        self.fitfu_dic = collections.OrderedDict({})
        self.fitfu = self.fitfu_dic.values()

        self.fitfu_list = Listbox(self.mainframe,height=10,width=27)
        self.fitfu_list.grid(row=5,column=1,rowspan=2)

        self.fitfu_add_button = Button(self.mainframe,text='add fit',command=self.add_fitfu,width=17).grid(row=5,column=0,sticky=W)
        self.fitfu_del_button = Button(self.mainframe,text='del fit',command=self.del_fitfu,width=17).grid(row=6,column=0,sticky=W)

        self.parameter_entry = Entry(self.mainframe,width=27)
        self.parameter_entry.grid(row=7,column=1)
        self.parameters = map(float,str(self.parameter_entry.get()).split())

        self.run_button = Button(self.mainframe,text='run!',command=self.run,width=17).grid(row=7,column=0)
        run_button_label = Label(self.mainframe,text='Parameters. The ordering is\n alpha,beta,selection,strength of fitfu 1, strength of fitfu2,...').grid(row=7,column=2)

        self.opt_button = Button(self.mainframe,text='optimize first gene!',command=self.evol_optimize,width=17).grid(row=9,column=0)
        self.opt_button = Button(self.mainframe,text='optimize first gene!,twostep',command=self.evol_optimize_two_step,width=17).grid(row=10,column=0)

        self.plot_button= Button(self.mainframe,text='plot_comparison',command=self.plot,width=17).grid(row=11,column=0)

        self.opt_all_button = Button(self.mainframe,text='optimize all genes',command=self.opt_all,width=17).grid(row=12,column=0)
        self.n_minimum_length = Entry(self.mainframe,width=27)
        self.n_minimum_length.grid(row=12,column=1)

        n_minimum_length_label = Label(self.mainframe,text='minimum length of genes in #codons').grid(row=12,column=2)


        gui_doc = """
        In an example workflow you might want to select a fasta file that
        contains the genes you want use. You can either select them from a file
        or a url. In both cases a histogram of codon usage and amino acid usage
        is generated.

        You can then (optionally) load a list of highly expressed genes, we
        support the format from the HEG database.  Visualizing the codon usage
        bias for e.g. checking if the CUB as you expect can be done by plotting
        various methods of dimensionality reduction.

        If you do not want to use all the genes you can enter a
        number n. The first n genes will only be analysed.

        You now have to select a fitness matrix which gives the probability of
        one amino acid to be represented by another one.

        Additionally, you can select a number of fitnessfunctions that assign
        to each codon a fitness. These functions will be normalized!
        If you want to perform a test run you
        have to enter the parameters: alpha,beta,selection,t_i for every
        testfunction. alpha and beta are parameters for the <todo> model of
        codon substitution and are related to transition/transversion bias.
        Input is either comma or whitespace/tab separated (or a combination of
        those).

        You can compare the absolute codon usage and relative (normalized for
        each amino acid) codon usage by plot comparison.  For optimizing the
        distance you can try optimizing the first gene and again regard the
        comparison to see if the algorithm works at all.

        In a last step you can optimize all genes you have read in. Returned
        are the optimal parameters, a goodness of fit and the RSCU that you can
        use for optimizing with the help of, e.g., OPTIMIZER.
        """

        documentation_text = Label(self.mainframe,text=gui_doc).grid(row=3,column=3,rowspan=8,columnspan=2)


        for child in self.mainframe.winfo_children(): child.grid_configure(padx=5,pady=5)

        #Style().configure("TButton",padding=(0,5,0,5) )

        self.root.mainloop()

if __name__ == "__main__":
    #doctest.testmod()
    mygui = cobigui()
    mygui.start_gui()

