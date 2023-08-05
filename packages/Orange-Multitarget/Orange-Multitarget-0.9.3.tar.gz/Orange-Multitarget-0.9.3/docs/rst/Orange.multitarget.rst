###########################################
Multi-target prediction (``multitarget``)
###########################################

.. toctree::
   :maxdepth: 1
   :hidden:

   Orange.multitarget.tree
   Orange.multitarget.binary
   Orange.multitarget.chain
   Orange.multitarget.neural
   Orange.multitarget.pls
   Orange.regression.earth
   Orange.multitarget.scoring


Multi-target prediction tries to achieve better prediction accuracy or speed
through prediction of multiple dependent variables at once. It works on
multi-target data, which is also supported by
Orange's tab file format using multiclass directive.

List of supported  learners: 

* :doc:`Orange.multitarget.tree`
* :doc:`Orange.multitarget.binary`
* :doc:`Orange.multitarget.chain`
* :doc:`Orange.multitarget.neural`
* :doc:`Orange.multitarget.pls`
* :doc:`Orange.regression.earth`

For evaluation of multi-target methods, see the corresponding section in 
:doc:`Orange.multitarget.scoring`.


The addon also includes three sample datasets:

* **bridges.tab** - dataset with 5 multi-class class variables
* **flare.tab** - dataset with 3 multi-class class variables
* **emotions.tab** - dataset with 6 binary class variables (a multi-label dataset)

Example of loading an included dataset:

.. literalinclude:: code/multitarget.py
    :lines: 1-2


.. automodule:: Orange.multitarget