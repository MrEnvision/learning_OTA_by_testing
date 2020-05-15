import copy
from teacher import sampleGeneration, getHpyDTWsValue
from new_EQs import sampleGeneration2
import random
import math
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
    print('Start validation')
    for i in range(testNum):
        if i % 1000 == 0:
            print(i, 'of', testNum)
        # sample = sampleGeneration(learnedSys.inputs, upperGuard, stateNum, targetSys)
        l = random.randint(1, math.ceil(stateNum * 1.7))
        sample = sampleGeneration2(targetSys, upperGuard, l)
        DRTWs, value = getHpyDTWsValue(sample, learnedSys)
        realDRTWs, realValue = testDTWs(sample, targetSys)
        if (realValue == 1 and value != 1) or (realValue != 1 and value == 1):
            failNum += 1
        # if realValue != value:
        #     failNum += 1
        # else:
        #     passNum += 1
    return (testNum - failNum) / testNum
