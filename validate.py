import copy
from teacher import sampleGeneration, getHpyDTWsValue
from tester import testDTWs
from equiv.equiv_wrapper import buildCanonicalOTA, transform_system
from equiv.equivalence import equivalence_query_normal


def validate(learnedSys, targetSys, upperGuard, stateNum, testNum):
    A = copy.deepcopy(targetSys)
    AA = buildCanonicalOTA(A)
    sys = transform_system(AA, "A", "s")
    HH = copy.deepcopy(learnedSys)
    sys2 = transform_system(HH, "B", "q")

    equivalent, _ = equivalence_query_normal(AA.max_time_value(), sys, sys2)
    if equivalent:
        print("Completely correct!")
        return 1.0


    failNum = 0
    for i in range(testNum):
        sample = sampleGeneration(learnedSys.inputs, upperGuard, stateNum, targetSys)
        DRTWs, value = getHpyDTWsValue(sample, learnedSys)
        realDRTWs, realValue = testDTWs(sample, targetSys)
        if (realValue == 1 and value != 1) or (realValue != 1 and value == 1):
            failNum += 1
        # if realValue != value:
        #     failNum += 1
        # else:
        #     passNum += 1
    return (testNum - failNum) / testNum
