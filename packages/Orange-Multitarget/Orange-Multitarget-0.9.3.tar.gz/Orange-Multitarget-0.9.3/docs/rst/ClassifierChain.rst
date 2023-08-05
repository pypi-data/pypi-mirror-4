ClassifierChain
================

.. image:: ../../_multitarget/widgets/icons/ClassifierChain.png
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

.. image:: images/cchain1.*
   :alt: Usage example

Classifier chain learner takes a single-target learner and with it creates a classifier for every class variable in the data. Every time a classifier is created, the values of that class variable are added to features. The order in which the class variables are chosen is random.


Setting:
--------
- Use actual values
	If checked, the values added into features are actual values from the data. Otherwise the values predicted by the classifier are used.


