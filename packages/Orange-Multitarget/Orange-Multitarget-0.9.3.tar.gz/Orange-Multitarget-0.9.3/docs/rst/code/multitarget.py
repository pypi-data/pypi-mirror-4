import Orange
data = Orange.data.Table('multitarget:bridges.tab')
print 'Features:', data.domain.features
print 'Classes:', data.domain.class_vars
print 'First instance:', data[0]
print 'Actual classes:', data[0].get_classes()

majority = Orange.classification.majority.MajorityLearner()
mt_majority = Orange.multitarget.binary.BinaryRelevanceLearner(learner = majority)
c_majority = mt_majority(data)
print 'Majority predictions:\n', c_majority(data[0])

mt_majority = Orange.multitarget.chain.ClassifierChainLearner(learner = majority)
c_majority = mt_majority(data)
print 'Chain Majority predictions:\n', c_majority(data[0])

pls = Orange.multitarget.pls.PLSClassificationLearner()
c_pls = pls(data)
print 'PLS predictions:\n', c_pls(data[0])

clust_tree = Orange.multitarget.tree.ClusteringTreeLearner()
c_clust_tree = clust_tree(data)
print 'Clustering Tree predictions: \n', c_clust_tree(data[0])