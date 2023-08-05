import Orange
data = Orange.data.Table('multitarget:bridges.tab')

majority = Orange.multitarget.binary.BinaryRelevanceLearner(
	learner = Orange.classification.majority.MajorityLearner, name = "Majority")

clust_tree = Orange.multitarget.tree.ClusteringTreeLearner(
	max_depth = 50, min_majority = 0.6, min_instances = 5, 
	method = Orange.multitarget.tree.inter_distance, name = "CT inter dist")

# we can use different distance measuring methods
ct2 = Orange.multitarget.tree.ClusteringTreeLearner(
	max_depth = 50, min_majority = 0.6, min_instances = 5, 
	method = Orange.multitarget.tree.intra_distance, name = "CT intra dist")

ct3 = Orange.multitarget.tree.ClusteringTreeLearner(
	max_depth = 50, min_majority = 0.6, min_instances = 5, 
	method = Orange.multitarget.tree.silhouette, name = "CT silhouette")

# Gini index should be used when working with nominal class variables
ct4 = Orange.multitarget.tree.ClusteringTreeLearner(
	max_depth = 50, min_majority = 0.6, min_instances = 5, 
	method = Orange.multitarget.tree.gini_index, name = "CT gini index")


# forests work better if trees are pruned less
forest_tree = Orange.multitarget.tree.ClusteringTreeLearner(
	max_depth = 50, min_majority = 1.0, min_instances = 3)
clust_forest = Orange.ensemble.forest.RandomForestLearner(
	base_learner = forest_tree, trees = 50, name = "Clustering Forest")

learners = [ majority, clust_tree, ct2, ct3, ct4, clust_forest ]

results = Orange.evaluation.testing.cross_validation(learners, data, folds=5)

print "Classification - bridges.tab"
print "%17s  %6s  %8s  %8s" % ("Learner", "LogLoss", "Mean Acc", "Glob Acc")
for i in range(len(learners)):
    print "%17s  %1.4f    %1.4f    %1.4f" % (learners[i].name,
    Orange.multitarget.scoring.mt_average_score(results, Orange.evaluation.scoring.logloss)[i],
    Orange.multitarget.scoring.mt_mean_accuracy(results)[i],
    Orange.multitarget.scoring.mt_global_accuracy(results)[i])

# regression uses a different parameter for pruning - min_MSE instead of min_majority
clust_tree = Orange.multitarget.tree.ClusteringTreeLearner(
	max_depth = 50, min_MSE = 0.05, min_instances = 5, name = "Clustering Tree")

forest_tree = Orange.multitarget.tree.ClusteringTreeLearner(
	max_depth = 50, min_MSE = 0.06, min_instances = 3)
clust_forest = Orange.ensemble.forest.RandomForestLearner(
	base_learner = forest_tree, trees = 50, name = "Clustering Forest")

learners = [ majority, clust_tree, clust_forest ]

data = Orange.data.Table('multitarget-synthetic.tab')
results = Orange.evaluation.testing.cross_validation(learners, data, folds=5)

print "Regression - multitarget-synthetic.tab"
print "%17s  %6s " % ("Learner", "RMSE")
for i in range(len(learners)):
    print "%17s  %1.4f  " % (learners[i].name,
    Orange.multitarget.scoring.mt_average_score(results, Orange.evaluation.scoring.RMSE)[i])

