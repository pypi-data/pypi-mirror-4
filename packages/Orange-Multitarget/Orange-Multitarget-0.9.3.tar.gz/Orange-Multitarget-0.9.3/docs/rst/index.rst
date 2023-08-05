Orange Multitarget documentation
================================

Orange Multitarget is an add-on for Orange_ data mining software package. It
extends Orange by providing methods that allow for classification of datasets
with multiple classes.

.. _Orange: http://orange.biolab.si/

 
Scripting Reference
-------------------
   
.. toctree::
   :maxdepth: 1

   Orange.multitarget


Widgets
----------------------

.. toctree::
   :maxdepth: 1

   BinaryRelevance
   ClassifierChain
   EnsembleClassifierChains
   PLSClassification
   ClusteringTree
   ClusteringRandomForest
   NeuralNetwork
   TestMultitargetLearners


Installation
------------

To install Multitarget add-on for Orange from PyPi_ run::

    pip install Orange-Multitarget

To install it from source code run::

    python setup.py install

To build Python egg run::

    python setup.py bdist_egg

To install add-on in `development mode`_ run::

    python setup.py develop

.. _development mode: http://packages.python.org/distribute/setuptools.html#development-mode
.. _PyPi: http://pypi.python.org/pypi

Source Code and Issue Tracker
-----------------------------

Source code is available on Bitbucket_. For issues and wiki we use Trac_.

.. _Bitbucket: https://bitbucket.org/biolab/orange-multitarget
.. _Trac: http://orange.biolab.si/trac/

Indices and tables
==================

* :ref:`genindex`
* :ref:`modindex`
* :ref:`search`
