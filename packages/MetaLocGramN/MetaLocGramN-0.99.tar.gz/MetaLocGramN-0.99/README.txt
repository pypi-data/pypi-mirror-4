Welcome to MetaLocGramN
---------------

The MetaLocGramN is a method for subcellular localization prediction of Gram-negative proteins. 
Read more: http://iimcb.genesilico.pl/MetaLocGramN/home

How does MetaLocGramN work?
==================================================

The MetaLocGramN is a gateway to a number of primary prediction methods (various types: signal peptide, beta-barrel, transmembrane helices and subcellular localization predictors).

The MetaLocGramN integrates the primary methods and based on their outputs provides overall consensus prediction. 

Requirements
============

* suds = 0.4

Installation
============

Install it with pip (or easy_install)::

	pip install MetaLocGramN

How to start?
==================================================
If you are really lazy try:
       
        $ ipython
        
	In [1]: from MetaLocGramN import *
	In [2]: run_example()
	# job_id: 1X820N
	# status: queue
	# status: primary prediction::in progress
	# status: primary prediction::in progress
	# status: primary prediction::done
	# status: consenus::done
	# status: done
	extracellular,47.541,0.0,0.0,0.0,52.459,
	primary methods: CELLO,cytoplasmic,0.6138,0.036,0.1346,0.0612,0.1546,PSLpred,extracellular,0.2,0.531,PSORTb3,unknown,0.2,0.2,0.2,0.2,0.2,SosuiGramN,cytoplasmic
	In [3]: run_example?
	# to get help!
	In [4]: run_example??
	# to get even bigger help!

if you want to find out more, see test.py inside the pkg.

	import MetaLocGramN
	import time

	if __name__ == "__main__":
	    mlgn = MetaLocGramN.MLGN()

	    seq = """>fasta
	    MKLSINKNTLESAVILCNAYVEKKDSSTITSHLFFHADEDKLLIKASDYEIGI
	    NYKIKKIRVESSGFATANAKSIADVIKSLNNEEVVLETIDNFLFVRQKNTKYK
	    """
	    mlgn.predict(seq)
	    print '# job_id:', mlgn.get_job_id()
	    status = ''
	    while True:
	        status = mlgn.get_status()
	        print '# status:', status
	        if status == 'done':
	            break
	        time.sleep(5)
	    print mlgn.get_result()

You should get something like:

	python test.py
	# job_id: K6Q10Q
	# status: queue
	# status: queue
	# status: primary prediction::in progress
	# status: primary prediction::in progress
	# status: primary prediction::done
	# status: done
	extracellular,47.541,0.0,0.0,0.0,52.459,
	primary methods: CELLO,cytoplasmic,0.6138,0.036,0.1346,0.0612,0.1546,PSLpred,extracellular,0.2,0.531,PSORTb3,unknown,0.2,0.2,0.2,0.2,0.2,SosuiGramN,cytoplasmic

Authors
==================================================

Marcin Magnus,
Marcin Pawlowski,
Janusz M. Bujnicki

http://iimcb.genesilico.pl/


Happy predictions!
==================================================

Marcin Magnus magnus@genesilico.pl

