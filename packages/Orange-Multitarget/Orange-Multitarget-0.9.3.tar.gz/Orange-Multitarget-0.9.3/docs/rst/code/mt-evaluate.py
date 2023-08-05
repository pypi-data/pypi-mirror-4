import Orange

data = Orange.data.Table('multitarget-synthetic')

majority = Orange.multitarget.binary.BinaryRelevanceLearner( \
	learner=Orange.classification.majority.MajorityLearner(), name='Majority')
tree = Orange.multitarget.tree.ClusteringTreeLearner(min_MSE=1e-10, min_instances=3, name='Clust Tree')
pls = Orange.multitarget.pls.PLSRegressionLearner(name='PLS')
earth = Orange.multitarget.earth.EarthLearner(name='Earth')

learners = [majority, tree, pls, earth]
res = Orange.evaluation.testing.cross_validation(learners, data)
rmse = Orange.evaluation.scoring.RMSE
scores = Orange.multitarget.scoring.mt_average_score(
            res, rmse, weights=[5,2,2,1])
print 'Weighted RMSE scores:'
print '\n'.join('%12s\t%.4f' % r for r in zip(res.classifier_names, scores))
