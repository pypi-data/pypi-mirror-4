import Orange

l1 = Orange.multitarget.neural.NeuralNetworkLearner(n_mid=15, reg_fact=0.1, max_iter=100, name="Neural Network")
l2 = Orange.multitarget.binary.BinaryRelevanceLearner(
	learner = Orange.classification.majority.MajorityLearner, name = "Majority")
learners = [l1, l2]

data = Orange.data.Table('multitarget:flare.tab')

results = Orange.evaluation.testing.cross_validation(learners, data, 3)

print "Classification - flare.tab"
print "%18s  %6s  %8s  %8s" % ("Learner    ", "LogLoss", "Mean Acc", "Glob Acc")
for i in range(len(learners)):
    print "%18s  %1.4f    %1.4f    %1.4f" % (learners[i].name,
    Orange.multitarget.scoring.mt_average_score(results, Orange.evaluation.scoring.logloss)[i],
    Orange.multitarget.scoring.mt_mean_accuracy(results)[i],
    Orange.multitarget.scoring.mt_global_accuracy(results)[i])


# Neural Networks do not work with missing values, the missing values need to be imputed
data = Orange.data.Table('multitarget:bridges.tab')
imputer = Orange.feature.imputation.AverageConstructor()
imputer = imputer(data)
imp_data = imputer(data)

results = Orange.evaluation.testing.cross_validation(learners, imp_data, 3)

print "Classification - imputed bridges.tab"
print "%18s  %6s  %8s  %8s" % ("Learner    ", "LogLoss", "Mean Acc", "Glob Acc")
for i in range(len(learners)):
    print "%18s  %1.4f    %1.4f    %1.4f" % (learners[i].name,
    Orange.multitarget.scoring.mt_average_score(results, Orange.evaluation.scoring.logloss)[i],
    Orange.multitarget.scoring.mt_mean_accuracy(results)[i],
    Orange.multitarget.scoring.mt_global_accuracy(results)[i])
