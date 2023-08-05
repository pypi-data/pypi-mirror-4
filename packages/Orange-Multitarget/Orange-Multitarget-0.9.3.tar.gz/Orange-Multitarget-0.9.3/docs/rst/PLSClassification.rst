PLSClassification
=========================

.. image:: ../../_multitarget/widgets/icons/PLSClassification.png
   :alt: Widget icon
   
Signals
-------

Inputs:
   - Data
   		Data to be used for learning.

Outputs:
   - Learner or Classifier

Description
-----------

.. image:: images/pls1.*
   :alt: Usage example

PLS is originally a regression technique. PLSClassification wraps Orange's implementation of PLS into a classifier. Usage is equall to all learners, settings are described below.


Settings
--------

* Num. of components to keep
  The number of components in the matrix that PLS constructs for regression and classification.