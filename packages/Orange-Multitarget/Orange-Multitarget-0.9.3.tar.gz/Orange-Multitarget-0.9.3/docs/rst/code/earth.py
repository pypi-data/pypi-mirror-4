import Orange

l1 = Orange.multitarget.earth.EarthLearner(name="earth")
l2 = Orange.multitarget.binary.BinaryRelevanceLearner(
	learner = Orange.regression.mean.MeanLearner, name = "Majority")
learners = [l1, l2]
# PLSClassifier do not work with missing values, the missing values need to be imputed
data = Orange.data.Table('multitarget-synthetic')

results = Orange.evaluation.testing.cross_validation(learners, data, 3)

print "Regression - multitarget-synthetic.tab"
print "%18s  %6s" % ("Learner    ", "RMSE")
for i in range(len(learners)):
    print "%18s  %1.4f" % (learners[i].name,
    Orange.multitarget.scoring.mt_average_score(results, Orange.evaluation.scoring.RMSE)[i])
    