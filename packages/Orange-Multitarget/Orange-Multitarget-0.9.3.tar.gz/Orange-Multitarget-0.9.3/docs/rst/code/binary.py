import Orange

data = Orange.data.Table('multitarget:bridges.tab')

cl1 = Orange.multitarget.binary.BinaryRelevanceLearner( \
	learner = Orange.classification.majority.MajorityLearner, name="Binary - Maj")
cl2 = Orange.multitarget.binary.BinaryRelevanceLearner( \
	learner = Orange.classification.tree.SimpleTreeLearner, name="Binary - Tree")

learners = [cl1,cl2]

results = Orange.evaluation.testing.cross_validation(learners, data)

print "Classification - bridges.tab"
print "%18s  %6s  %8s  %8s" % ("Learner    ", "LogLoss", "Mean Acc", "Glob Acc")
for i in range(len(learners)):
    print "%18s  %1.4f    %1.4f    %1.4f" % (learners[i].name,
    Orange.multitarget.scoring.mt_average_score(results, Orange.evaluation.scoring.logloss)[i],
    Orange.multitarget.scoring.mt_mean_accuracy(results)[i],
    Orange.multitarget.scoring.mt_global_accuracy(results)[i])
