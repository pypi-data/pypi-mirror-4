ClusteringTree
=========================

.. image:: ../../_multitarget/widgets/icons/ClusteringTree.png
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

.. image:: images/ct1.*
   :alt: Usage example

Clustering trees are similiar to classic decision trees, to select features they measure the distance between clusters the featers would create by splitting the dataset. Usage is simple, the settings are described below.


Settings
--------

* Stop splitting nodes at depth

    Maximal depth of tree.
	
* Minimal majority class proportion

    Minimal proportion of the majority class value each of the class variables has to reach
    to stop induction (only used for classification). 


* Min mean squared error

    Minimal mean squared error each of the class variables has to reach
    to stop induction (only used for regression). 

* Min. instances in leaves

    Minimal number of instances in leaves. Instance count is weighed.

* Feature scorer

        * Inter dist (default) - Euclidean distance between centroids of clusters
        * Intra dist - average Euclidean distance of each member of a cluster to the centroid of that cluster
        * Silhouette - silhouette (http://en.wikipedia.org/wiki/Silhouette_(clustering)) measure calculated with euclidean distances between clusters instead of elements of a cluster.
        * Gini-index - calculates the Gini-gain index, should be used with class variables with nominal values