EnsembleClassifierChains
=========================

.. image:: ../../_multitarget/widgets/icons/EnsembleClassifierChain.png
   :alt: Widget icon
   
Signals
-------

Inputs:
   - Learner
   		The base learner used in the ensemble technique.

Outputs:
   - Learner or Classifier

Description
-----------

.. image:: images/ecchain1.*
   :alt: Usage example

Ensemble classifier chain learner takes a single-target learner and with it creates a number of classifier chains. Each chain is constructed on a random sample of the dataset.


Setting:
--------
- Number of chains
	Number of classifier chains that are built.
- Sample size
	The size of the random sample taken from the dataset for each chain.
- Use actual values
	If checked, the values added into features are actual values from the data. Otherwise the values predicted by the classifier are used.


