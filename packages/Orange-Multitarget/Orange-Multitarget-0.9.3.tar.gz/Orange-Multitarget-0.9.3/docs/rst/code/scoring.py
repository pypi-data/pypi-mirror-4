import Orange

data = Orange.data.Table('multitarget:bridges.tab')

cl1 = Orange.multitarget.binary.BinaryRelevanceLearner( \
    learner = Orange.classification.majority.MajorityLearner, name="Majority")
cl2 = Orange.multitarget.tree.ClusteringTreeLearner(name="CTree")

learners = [cl1,cl2]

results = Orange.evaluation.testing.cross_validation(learners, data)

print "%18s  %7s    %6s  %10s   %8s  %8s" % \
("Learner    ", "LogLoss", "Brier", "Inf. Score", "Mean Acc", "Glob Acc")
for i in range(len(learners)):
    print "%18s   %1.4f    %1.4f     %+2.4f     %1.4f    %1.4f" % (learners[i].name,

    # Calculate average logloss
    Orange.multitarget.scoring.mt_average_score(results, \
        Orange.evaluation.scoring.logloss)[i],
    # Calculate average Brier score
    Orange.multitarget.scoring.mt_average_score(results, \
        Orange.evaluation.scoring.Brier_score)[i],
    # Calculate average Information Score
    Orange.multitarget.scoring.mt_average_score(results, \
        Orange.evaluation.scoring.IS)[i],
    # Calculate mean accuracy
    Orange.multitarget.scoring.mt_mean_accuracy(results)[i],
    # Calculate global accuracy
    Orange.multitarget.scoring.mt_global_accuracy(results)[i])
