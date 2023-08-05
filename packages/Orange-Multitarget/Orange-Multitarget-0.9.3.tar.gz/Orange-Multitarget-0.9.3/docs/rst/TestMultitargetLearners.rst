TestMultitargetLearners
=========================

.. image:: ../../_multitarget/widgets/icons/TestMTLearners.png
   :alt: Widget icon
   
Signals
-------

Inputs:
  - Data
  	Data to be used for testing.

  - Seoerate Test Data
    Separate data for testing

  - Learner
    One or more learning algorithms

Outputs:
   - Evaluation results
      Results of testing the algorithms

Description
-----------

.. image:: images/test1.*
   :alt: Usage example

This widget is used for testing built learners. We provide the data and a number of learners we want to compare to the inputs of this wiget. Inside the widget we then select the method of testing and the scores we wish to measure. Results are displayed on the table to the right.


.. image:: images/test2.*
   :alt: Settings example

Settings
--------

* Sampling

    Here we can choose the method of sampling for testing the learners. Available methods are cross-validation, leave-one-out testing, random sampling, test on train data and test on test data (this requires additional test data on input)
	
* Performance Scorers

    A list of scorers is available, by clicking on one of them we either add or remove a scorer from the table of results.